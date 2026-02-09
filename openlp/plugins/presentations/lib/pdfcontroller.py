# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008 OpenLP Developers                                   #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
import logging

from pathlib import Path

from PySide6 import QtWidgets
from PySide6.QtPdf import QPdfDocument
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter

from openlp.core.common.registry import Registry
from openlp.core.display.screens import ScreenList
from openlp.plugins.presentations.lib.presentationcontroller import PresentationController, PresentationDocument


log = logging.getLogger(__name__)

PDF_CONTROLLER_FILETYPES = ['pdf']


class PdfController(PresentationController):
    """
    Class to control PDF presentations
    """
    log.info('PdfController loaded')

    def __init__(self, plugin):
        """
        Initialise the class

        :param plugin: The plugin that creates the controller.
        """
        log.debug('Initialising')
        super(PdfController, self).__init__(plugin, 'Pdf', PdfDocument)
        self.process = None
        self.supports = ['pdf']
        self.also_supports = []

    def check_available(self):
        """
        PdfController is able to run on this machine.

        :return: Always returns true since QtPdf seems to be required for Qt.
        """
        log.debug('check_available Pdf')
        return True

    def kill(self):
        """
        Called at system exit to clean up any running presentations
        """
        log.debug('Kill pdfviewer')
        while self.docs:
            self.docs[0].close_presentation()


class PdfDocument(PresentationDocument):
    """
    Class which holds information of a single presentation.
    This class is not actually used to present the PDF, instead we convert to
    image-serviceitem on the fly and present as such. Therefore some of the 'playback'
    functions is not implemented.
    """
    def __init__(self, controller, document_path):
        """
        Constructor, store information about the file and initialise.

        :param pathlib.Path document_path: Path to the document to load
        :rtype: None
        """
        log.debug('Init Presentation Pdf')
        super().__init__(controller, document_path)
        self.presentation = None
        self.blanked = False
        self.hidden = False
        self.image_files = []
        self.num_pages = -1

    def load_presentation(self):
        """
        Called when a presentation is added to the SlideController. It generates images from the PDF.

        :return: True is loading succeeded, otherwise False.
        """
        log.debug('load_presentation pdf')
        temp_dir_path = self.get_temp_folder()
        # Check if the images has already been created, and if yes load them
        if (temp_dir_path / 'mainslide001.png').is_file():
            created_files = sorted(temp_dir_path.glob('*'))
            for image_path in created_files:
                if image_path.is_file():
                    self.image_files.append(image_path)
            self.num_pages = len(self.image_files)
            return True
        size = ScreenList().current.display_geometry
        # load pdf
        self.presentation = QPdfDocument(Registry().get('application'))
        self.presentation.load(str(self.file_path))
        # wait for loading to complete
        while self.presentation.status() != QPdfDocument.Status.Ready:
            QtWidgets.QApplication.processEvents()
        # Generate images from PDF that will fit the frame.
        if not temp_dir_path.is_dir():
            temp_dir_path.mkdir(parents=True)
        log.debug('loading presentation using QPdfDocument')
        painter = QPainter()
        for i in range(0, self.presentation.pageCount()):
            page_size = self.presentation.pagePointSize(i).toSize()
            scaled_page_size = page_size.scaled(size.width(), size.height(), Qt.AspectRatioMode.KeepAspectRatio)
            image = self.presentation.render(i, scaled_page_size)
            png_filename = str(temp_dir_path / 'mainslide{:03d}.png'.format(i + 1))
            # due to the background not being set to white by default, it needs to be done manually
            image_redraw = QImage(image.size(), QImage.Format_ARGB32)
            image_redraw.fill(QColor(Qt.white).rgb())
            painter.begin(image_redraw)
            painter.drawImage(0, 0, image)
            image_redraw.save(png_filename, 'png')
            painter.end()
            png_path = Path(png_filename)
            self.image_files.append(Path(png_path))
        # Create thumbnails
        self.create_thumbnails()
        self.create_titles_and_notes()
        return True

    def create_thumbnails(self):
        """
        Generates thumbnails
        """
        log.debug('create_thumbnails pdf')
        if self.check_thumbnails():
            return
        # use builtin function to create thumbnails from generated images
        index = 1
        for image in self.image_files:
            self.convert_thumbnail(image, index)
            index += 1

    def close_presentation(self):
        """
        Close presentation and clean up objects. Triggered by new object being added to SlideController or OpenLP being
        shut down.
        """
        log.debug('close_presentation pdf')
        self.controller.remove_doc(self)

    def is_loaded(self):
        """
        Returns true if a presentation is loaded.

        :return: True if loaded, False if not.
        """
        log.debug('is_loaded pdf')
        if self.presentation:
            return True
        return False

    def is_active(self):
        """
        Returns true if a presentation is currently active.

        :return: True if active, False if not.
        """
        log.debug('is_active pdf')
        return self.is_loaded() and not self.hidden

    def get_slide_count(self):
        """
        Returns total number of slides

        :return: The number of pages in the presentation..
        """
        return self.presentation.pageCount()

    def create_titles_and_notes(self):
        """
        Writes the list of titles - usually page number - (one per slide)
        to 'titles.txt' and the notes to 'slideNotes[x].txt'
        in the thumbnails directory
        """
        titles = []
        notes = []
        for i in range(0, self.presentation.pageCount()):
            titles.append(self.presentation.pageLabel(i))
        self.save_titles_and_notes(titles, notes)
