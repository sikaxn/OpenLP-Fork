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
from subprocess import Popen

from openlp.core.common import delete_file
from openlp.core.common.applocation import AppLocation
from openlp.core.common.mixins import LogMixin
from openlp.core.common.path import Path
from openlp.core.common.platform import is_macosx
from openlp.core.common.registry import Registry
from openlp.core.display.screens import ScreenList
from openlp.plugins.presentations.lib.presentationcontroller import PresentationController, PresentationDocument


LIBREOFFICE_PATH = Path('/Applications/LibreOffice.app')
LIBREOFFICE_PYTHON = LIBREOFFICE_PATH / 'Contents' / 'Resources' / 'python'

try:
    from Pyro5.client import Proxy
    if is_macosx() and LIBREOFFICE_PATH.exists():
        macuno_available = True
    else:
        macuno_available = False
except ImportError:
    macuno_available = False


if macuno_available:
    # If this controller is good to go, register the serializer classes with Pyro5
    from openlp.plugins.presentations.lib.serializers import register_classes
    register_classes()


log = logging.getLogger(__name__)


class MacLOController(PresentationController, LogMixin):
    """
    Class to control interactions with MacLO presentations on Mac OS X via Pyro5. It starts the Pyro5 nameserver,
    starts the LibreOfficeServer, and then controls MacLO via Pyro5.
    """
    log.info('MacLOController loaded')

    def __init__(self, plugin):
        """
        Initialise the class
        """
        log.debug('Initialising')
        super(MacLOController, self).__init__(plugin, 'maclo', MacLODocument, 'Impress on macOS')
        self.supports = ['odp']
        self.also_supports = ['ppt', 'pps', 'pptx', 'ppsx', 'pptm']
        self.server_process = None
        self._client = None
        self._start_server()

    def _start_server(self):
        """
        Start a LibreOfficeServer
        """
        libreoffice_python = Path('/Applications/LibreOffice.app/Contents/Resources/python')
        libreoffice_server = AppLocation.get_directory(AppLocation.PluginsDir).joinpath('presentations', 'lib',
                                                                                        'libreofficeserver.py')
        if libreoffice_python.exists():
            self.server_process = Popen([str(libreoffice_python), str(libreoffice_server)])

    @property
    def client(self):
        """
        Set up a Pyro5 client so that we can talk to the LibreOfficeServer
        """
        if not self._client:
            self._client = Proxy('PYRO:openlp.libreofficeserver@localhost:4310')
        if not self._client._pyroConnection:
            self._client._pyroReconnect()
        return self._client

    def check_available(self):
        """
        MacLO is able to run on this machine.
        """
        log.debug('check_available')
        return macuno_available

    def start_process(self):
        """
        Loads a running version of LibreOffice in the background. It is not displayed to the user but is available to
        the UNO interface when required.
        """
        log.debug('Started automatically by the Pyro server')
        self.client.start_process()

    def kill(self):
        """
        Called at system exit to clean up any running presentations.
        """
        log.debug('Kill LibreOffice')
        try:
            # Some people like to close LibreOffice themselves, let's just catch any errors so that OpenLP fails
            # silently
            self.client.shutdown()
        except Exception:
            pass
        self.server_process.kill()


class MacLODocument(PresentationDocument):
    """
    Class which holds information and controls a single presentation.
    """

    def __init__(self, controller, presentation):
        """
        Constructor, store information about the file and initialise.
        """
        log.debug('Init Presentation LibreOffice')
        super(MacLODocument, self).__init__(controller, presentation)
        self.client = controller.client

    def load_presentation(self):
        """
        Tell the LibreOfficeServer to start the presentation.
        """
        log.debug('Load Presentation LibreOffice')
        if not self.client.load_presentation(str(self.file_path), ScreenList().current.number + 1):
            return False
        self.create_thumbnails()
        self.create_titles_and_notes()
        return True

    def create_thumbnails(self):
        """
        Create thumbnail images for presentation.
        """
        log.debug('create thumbnails LibreOffice')
        if self.check_thumbnails():
            return
        temp_thumbnails = self.client.extract_thumbnails(str(self.get_temp_folder()))
        for index, temp_thumb in enumerate(temp_thumbnails):
            temp_thumb = Path(temp_thumb)
            self.convert_thumbnail(temp_thumb, index + 1)
            delete_file(temp_thumb)

    def create_titles_and_notes(self):
        """
        Writes the list of titles (one per slide) to 'titles.txt' and the notes to 'slideNotes[x].txt'
        in the thumbnails directory
        """
        titles, notes = self.client.get_titles_and_notes()
        self.save_titles_and_notes(titles, notes)

    def close_presentation(self):
        """
        Close presentation and clean up objects. Triggered by new object being added to SlideController or OpenLP being
        shutdown.
        """
        log.debug('close Presentation LibreOffice')
        self.client.close_presentation()
        self.controller.remove_doc(self)

    def is_loaded(self):
        """
        Returns true if a presentation is loaded.
        """
        log.debug('is loaded LibreOffice')
        return self.client.is_loaded()

    def is_active(self):
        """
        Returns true if a presentation is active and running.
        """
        log.debug('is active LibreOffice')
        return self.client.is_active()

    def unblank_screen(self):
        """
        Unblanks the screen.
        """
        log.debug('unblank screen LibreOffice')
        return self.client.unblank_screen()

    def blank_screen(self):
        """
        Blanks the screen.
        """
        log.debug('blank screen LibreOffice')
        self.client.blank_screen()

    def is_blank(self):
        """
        Returns true if screen is blank.
        """
        log.debug('is blank LibreOffice')
        return self.client.is_blank()

    def stop_presentation(self):
        """
        Stop the presentation, remove from screen.
        """
        log.debug('stop presentation LibreOffice')
        self.client.stop_presentation()

    def start_presentation(self):
        """
        Start the presentation from the beginning.
        """
        log.debug('start presentation LibreOffice')
        self.client.start_presentation()
        # Make sure impress doesn't steal focus, unless we're on a single screen setup
        if len(ScreenList()) > 1:
            Registry().get('main_window').activateWindow()

    def get_slide_number(self):
        """
        Return the current slide number on the screen, from 1.
        """
        return self.client.get_slide_number()

    def get_slide_count(self):
        """
        Return the total number of slides.
        """
        return self.client.get_slide_count()

    def goto_slide(self, slide_no):
        """
        Go to a specific slide (from 1).

        :param slide_no: The slide the text is required for, starting at 1
        """
        self.client.goto_slide(slide_no)

    def next_step(self):
        """
        Triggers the next effect of slide on the running presentation.
        """
        self.client.next_step()

    def previous_step(self):
        """
        Triggers the previous slide on the running presentation.
        """
        self.client.previous_step()

    def get_slide_text(self, slide_no):
        """
        Returns the text on the slide.

        :param slide_no: The slide the text is required for, starting at 1
        """
        return self.client.get_slide_text(slide_no)

    def get_slide_notes(self, slide_no):
        """
        Returns the text in the slide notes.

        :param slide_no: The slide the notes are required for, starting at 1
        """
        return self.client.get_slide_notes(slide_no)
