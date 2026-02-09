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
import time

from PySide6 import QtCore

from openlp.core.common import get_uno_command, get_uno_instance, normalize_str
from openlp.core.common.i18n import translate
from openlp.core.common.platform import is_win

from .songimport import SongImport


log = logging.getLogger(__name__)

if is_win():
    from win32com.client import Dispatch
    NoConnectException = Exception
else:
    import uno
    from com.sun.star.connection import NoConnectException
    from com.sun.star.beans import PropertyValue
try:
    from com.sun.star.style.BreakType import PAGE_BEFORE, PAGE_AFTER, PAGE_BOTH
except ImportError:
    PAGE_BEFORE = 4
    PAGE_AFTER = 5
    PAGE_BOTH = 6


class OpenOfficeImport(SongImport):
    """
    Import songs from Impress/Powerpoint docs using Impress
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the class. Requires a songmanager class which is passed to SongImport for writing song to disk
        """
        super(OpenOfficeImport, self).__init__(manager, **kwargs)
        self.document = None
        self.process_started = False

    def do_import(self):
        if not isinstance(self.import_source, list):
            return
        try:
            self.start_ooo()
        except NoConnectException as exc:
            self.log_error(
                self.import_source[0],
                translate('SongsPlugin.SongImport', 'Cannot access OpenOffice or LibreOffice'))
            log.error(exc)
            return
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                break
            if file_path.is_file():
                self.open_ooo_file(file_path)
                if self.document:
                    self.process_ooo_document()
                    self.close_ooo_file()
                else:
                    self.log_error(self.file_path, translate('SongsPlugin.SongImport', 'Unable to open file'))
            else:
                self.log_error(self.file_path, translate('SongsPlugin.SongImport', 'File not found'))
        self.close_ooo()

    def process_ooo_document(self):
        """
        Handle the import process for OpenOffice files. This method facilitates
        allowing subclasses to handle specific types of OpenOffice files.
        """
        if self.document.supportsService("com.sun.star.presentation.PresentationDocument"):
            self.process_presentation()
        if self.document.supportsService("com.sun.star.text.TextDocument"):
            self.process_doc()

    def start_ooo(self):
        """
        Start OpenOffice.org process
        TODO: The presentation/Impress plugin may already have it running
        """
        if is_win():
            self.start_ooo_process()
            self.desktop = self.ooo_manager.createInstance('com.sun.star.frame.Desktop')
        else:
            context = uno.getComponentContext()
            resolver = context.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', context)
            uno_instance = None
            loop = 0
            while uno_instance is None and loop < 5:
                try:
                    uno_instance = get_uno_instance(resolver)
                except NoConnectException:
                    time.sleep(0.1)
                    log.exception("Failed to resolve uno connection")
                    self.start_ooo_process()
                    loop += 1
                else:
                    manager = uno_instance.ServiceManager
                    self.desktop = manager.createInstanceWithContext("com.sun.star.frame.Desktop", uno_instance)
                    return
            raise Exception('Unable to start LibreOffice')

    def start_ooo_process(self):
        """
        Start the OO Process
        """
        try:
            if is_win():
                self.ooo_manager = Dispatch('com.sun.star.ServiceManager')
                self.ooo_manager._FlagAsMethod('Bridge_GetStruct')
                self.ooo_manager._FlagAsMethod('Bridge_GetValueObject')
            else:
                cmd = get_uno_command()
                process = QtCore.QProcess()
                process.startDetached(cmd)
            self.process_started = True
        except Exception:
            log.exception("start_ooo_process failed")

    def open_ooo_file(self, file_path):
        """
        Open the passed file in OpenOffice.org Impress
        """
        self.file_path = file_path
        url = file_path.as_uri()
        properties = (self.create_property('Hidden', True),)
        try:
            self.document = self.desktop.loadComponentFromURL(url, '_blank', 0, properties)
            if not self.document.supportsService("com.sun.star.presentation.PresentationDocument") and not \
                    self.document.supportsService("com.sun.star.text.TextDocument"):
                self.close_ooo_file()
            else:
                self.import_wizard.increment_progress_bar('Processing file {file_path}'.format(file_path=file_path), 0)
        except AttributeError:
            log.exception("open_ooo_file failed: {url}".format(url=url))
        return

    def create_property(self, name, value):
        """
        Create an OOo style property object which are passed into some Uno methods.
        """
        log.debug('create property OpenOffice')
        if is_win():
            property_object = self.ooo_manager.Bridge_GetStruct('com.sun.star.beans.PropertyValue')
        else:
            property_object = PropertyValue()
        property_object.Name = name
        property_object.Value = value
        return property_object

    def close_ooo_file(self):
        """
        Close file.
        """
        try:
            self.document.close(True)
        except Exception:
            log.exception('Exception in close_ooo_file - trying to ignore it.')
        self.document = None

    def close_ooo(self):
        """
        Close OOo. But only if we started it and not on windows
        """
        if self.process_started:
            try:
                self.desktop.terminate()
            except Exception:
                log.exception('Exception in close_ooo - trying to ignore it.')

    def process_presentation(self):
        """
        Process the file
        """
        doc = self.document
        slides = doc.getDrawPages()
        text = ''
        for slide_no in range(slides.getCount()):
            if self.stop_import_flag:
                self.import_wizard.increment_progress_bar('Import cancelled', 0)
                return
            slide = slides.getByIndex(slide_no)
            slide_text = ''
            for idx in range(slide.getCount()):
                shape = slide.getByIndex(idx)
                if shape.supportsService("com.sun.star.drawing.Text"):
                    if shape.getString().strip() != '':
                        slide_text += shape.getString().strip() + '\n\n'
            if slide_text.strip() == '':
                slide_text = '\f'
            text += slide_text
        self.process_songs_text(text)
        return

    def process_doc(self):
        """
        Process the doc file, a paragraph at a time
        """
        text = ''
        paragraphs = self.document.getText().createEnumeration()
        while paragraphs.hasMoreElements():
            para_text = ''
            paragraph = paragraphs.nextElement()
            if paragraph.supportsService("com.sun.star.text.Paragraph"):
                text_portions = paragraph.createEnumeration()
                while text_portions.hasMoreElements():
                    text_portion = text_portions.nextElement()
                    if text_portion.BreakType in (PAGE_BEFORE, PAGE_BOTH):
                        para_text += '\f'
                    para_text += text_portion.getString()
                    if text_portion.BreakType in (PAGE_AFTER, PAGE_BOTH):
                        para_text += '\f'
            text += para_text + '\n'
        self.process_songs_text(text)

    def process_songs_text(self, text):
        """
        Process the songs text

        :param text: The text.
        """
        song_texts = normalize_str(text).split('\f')
        self.set_defaults()
        for song_text in song_texts:
            if song_text.strip():
                self.process_song_text(song_text.strip())
                if self.check_complete():
                    self.finish()
                    self.set_defaults()
        if self.check_complete():
            self.finish()
