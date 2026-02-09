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
"""
This module is a base to be used for Mac OS X presentation modules using applescript
to control presentation application, such as keynote and powerpoint for mac
"""
import logging
try:
    import applescript
    APPLESCRIPT_AVAILABLE = True
except ImportError:
    APPLESCRIPT_AVAILABLE = False


from openlp.core.common.platform import is_macosx
from openlp.core.display.screens import ScreenList
from openlp.plugins.presentations.lib.presentationcontroller import PresentationController, PresentationDocument


log = logging.getLogger(__name__)

DEFAULT_APPLESCRIPT = """
on check_available()
    return false
end check_available
"""


class AppleScriptBaseController(PresentationController):
    """
    Class to control interactions with a Presentation program like Keynote or Powerpoint.
    It uses py-applescript to compile and execute applescript to Load and Close the Presentation.
    As well as triggering the correct activities based on the users input.
    """
    log.info('ApplescriptController loaded')

    base_class = True

    def __init__(self, plugin, name, doc):
        """
        Initialise the class
        """
        super(AppleScriptBaseController, self).__init__(plugin, name, doc)
        # Script expected to be overwritten by subclasses
        if APPLESCRIPT_AVAILABLE:
            self.applescript = applescript.AppleScript(DEFAULT_APPLESCRIPT)

    def check_available(self):
        """
        Program is able to run on this machine.
        """
        log.debug('check_available')
        if not is_macosx():
            return False
        try:
            return self.applescript.call('check_available')
        except Exception:
            log.exception('script execution failed')
        return False

    def start_process(self):
        """
        Loads the presentation application
        """
        log.debug('start_process')
        try:
            self.applescript.call('start_application')
        except Exception:
            log.exception('script execution failed')

    def kill(self):
        """
        Called at system exit to clean up any running presentations.
        """
        log.debug('Kill presentation program')
        while self.docs:
            self.docs[0].close_presentation()
        try:
            self.applescript.call('stop_application')
        except Exception:
            log.exception('script execution failed')


class AppleScriptBaseDocument(PresentationDocument):
    """
    Class which holds information and controls a single presentation.
    """

    def __init__(self, controller, document_path):
        """
        Constructor, store information about the file and initialise.

        :param controller:
        :param pathlib.Path document_path: Path to the document to load
        :rtype: None
        """
        log.debug('Init Presentation Applescript')
        super().__init__(controller, document_path)
        self.presentation_loaded = False
        self.is_blanked = False
        self.slide_count = 0

    def load_presentation(self):
        """
        Called when a presentation is added to the SlideController. Opens the presentation file.
        """
        log.debug('load_presentation')
        # check if there already exists thumbnails etc. If so skip loading the presentation.
        files = self.get_thumbnail_folder().glob('*')
        if len(list(files)) > 0:
            self.presentation_loaded = True
            return self.presentation_loaded
        try:
            self.controller.applescript.call('create_thumbs', str(self.file_path), str(self.get_thumbnail_folder()))
            self.presentation_loaded = True
        except Exception:
            log.exception('script execution failed')
            self.presentation_loaded = False
        return self.presentation_loaded

    def create_thumbnails(self):
        """
        Create the thumbnail images for the current presentation.
        """
        log.debug('create_thumbnails')
        # No need to do anything, already created thumbs in load_presentation

    def close_presentation(self):
        """
        Close presentation and clean up objects. This is triggered by a new object being added to SlideController or
        OpenLP being shut down.
        """
        log.debug('close_presentation')
        if self.presentation_loaded:
            try:
                self.controller.applescript.call('close_presentation')
            except Exception:
                log.exception('script execution failed')
        self.presentation_loaded = False
        self.controller.remove_doc(self)

    def is_loaded(self):
        """
        Returns ``True`` if a presentation is loaded.
        """
        self.presentation_loaded = False
        log.debug('is_loaded')
        try:
            self.presentation_loaded = self.controller.applescript.call('is_loaded', str(self.file_path))
        except Exception:
            log.exception('script execution failed')
        return self.presentation_loaded

    def is_active(self):
        """
        Returns ``True`` if a presentation is currently active.
        """
        log.debug('is_active')
        if not self.is_loaded():
            return False
        try:
            return self.controller.applescript.call('is_active')
        except Exception:
            log.exception('script execution failed')
        return False

    def unblank_screen(self):
        """
        Unblanks (restores) the presentation.
        """
        log.debug('unblank_screen')
        try:
            self.controller.applescript.call('unblank')
        except Exception:
            log.exception('script execution failed')
        self.is_blanked = False

    def blank_screen(self):
        """
        Blanks the screen.
        """
        log.debug('blank_screen')
        try:
            self.controller.applescript.call('blank')
        except Exception:
            log.exception('script execution failed')

    def is_blank(self):
        """
        Returns ``True`` if screen is blank.
        """
        log.debug('is_blank')
        return self.is_blanked

    def stop_presentation(self):
        """
        Stops the current presentation and hides the output. Used when blanking to desktop.
        """
        try:
            self.controller.applescript.call('stop_presentation')
        except Exception:
            log.exception('script execution failed')

    def start_presentation(self):
        """
        Starts a presentation from the beginning.
        """
        log.debug('start_presentation')
        try:
            fullscreen = (ScreenList().current.custom_geometry is None)
            size = ScreenList().current.display_geometry
            self.controller.applescript.call('start_presentation', str(self.file_path), size.top(), size.left(),
                                             size.width(), size.height(), fullscreen)
        except Exception:
            log.exception('script execution failed')

    def get_slide_number(self):
        """
        Returns the current slide number.
        """
        log.debug('get_slide_number')
        ret = 0
        try:
            ret = int(self.controller.applescript.call('get_current_slide'))
        except Exception:
            log.exception('script execution failed')
        return ret

    def get_slide_count(self):
        """
        Returns total number of slides.
        """
        log.debug('get_slide_count')
        return self.slide_count

    def goto_slide(self, slide_no):
        """
        Moves to a specific slide in the presentation.

        :param slide_no: The slide the text is required for, starting at 1
        """
        log.debug('goto_slide')
        try:
            self.controller.applescript.call('goto_slide', slide_no)
        except Exception:
            log.exception('script execution failed')

    def next_step(self):
        """
        Triggers the next effect of slide on the running presentation.
        """
        log.debug('next_step')
        past_end = False
        try:
            self.controller.applescript.call('next_slide')
            # TODO: detect past end
        except Exception:
            log.exception('script execution failed')
        return past_end

    def previous_step(self):
        """
        Triggers the previous slide on the running presentation.
        """
        log.debug('previous_step')
        before_start = False
        try:
            self.controller.applescript.call('previous_slide')
            # TODO: detect before start
        except Exception:
            log.exception('script execution failed')
        return before_start

    def get_slide_text(self, slide_no):
        """
        Returns the text on the slide.

        :param slide_no: The slide the text is required for, starting at 1
        """
        return ''

    def get_slide_notes(self, slide_no):
        """
        Returns the text on the slide.

        :param slide_no: The slide the text is required for, starting at 1
        """
        return ''

    def create_titles_and_notes(self):
        """
        Writes the list of titles (one per slide)
        to 'titles.txt'
        and the notes to 'slideNotes[x].txt'
        in the thumbnails directory
        """
        # Already done in create thumbs
        pass
