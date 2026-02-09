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
This module is for controlling keynote.
"""
import logging
import shutil
try:
    import applescript
    APPLESCRIPT_AVAILABLE = True
except ImportError:
    APPLESCRIPT_AVAILABLE = False

from openlp.plugins.presentations.lib.applescriptbasecontroller import AppleScriptBaseController, \
    AppleScriptBaseDocument


log = logging.getLogger(__name__)

KEYNOTE_APPLESCRIPT = """
on check_available()
    try
        set appID to "com.apple.iWork.Keynote"
        if exists application id appID then
            return true
        end if
        return false
    on error
        return false
    end try
end check_available

on get_version()
    return (version of application "Keynote")
end get_version

on start_application()
    tell application "Keynote"
        launch
    end tell
end start_application

on close_presentation()
    try
        tell application "Keynote"
            -- close presentation
            close front document
            end tell
    end try
end close_presentation

on create_thumbs(documentName, outputPath)
    set outputPathHfs to POSIX file outputPath
    tell application "Keynote"
        if playing is true then tell the front document to stop
        -- Open document
        open documentName
        -- hide keynote
        tell application "System Events"
            set visible of application process "Keynote" to false
        end tell
        -- Export slides to png
        export front document as slide images to file outputPathHfs with properties ¬
            {image format:PNG, skipped slides:false}
        -- Get the Presentation Notes and slide title
        set the slideTitles to ""
        tell the front document
            repeat with i from 1 to the count of slides
                tell slide i
                    set noteFilename to outputPath & "/slideNotes" & (slide number as string) & ".txt"
                    if skipped is false then
                        -- Save the notes to file
                        set noteText to presenter notes of it
                        set noteFile to open for access noteFilename with write permission
                        write noteText to noteFile
                        close access noteFile
                        -- if title is available, save it
                        if title showing is true then
                            set the slideTitle to object text of default title item
                            set the slideTitles to slideTitles & slideTitle & return
                        else
                            set the slideTitles to "slide " & (slide number as string) & return
                        end if
                    end if
                end tell
            end repeat
        end tell
        -- Save the titles to file
        set titlesFilename to outputPath & "/titles.txt"
        set titlesFile to open for access titlesFilename with write permission
        write slideTitles to titlesFile
        close access titlesFile
        -- close presentation
        close front document
    end tell
end create_thumbs
--create_thumbs("/Users/tgc/Downloads/keynote-pres.key", "/Users/tgc/Downloads/tmp/")

on start_presentation(documentName, new_top, new_left_pos, new_width, new_height, fullscreen)
    tell application "Keynote"
        if playing is true then tell the front document to stop
        -- Open document
        open documentName
        --start front document from the first slide of front document
        --activate
    end tell
    -- There seems to be no applescript command to start presentation in window mode
    -- so we that by faking mouse clicks (requires accessability rights)
    tell application "System Events"
        tell process "Keynote"
            click (menu bar item 10 of menu bar 1)
            click menu item 2 of menu 1 of menu bar item 10 of menu bar 1
        end tell
    end tell
    tell application "Keynote"
    -- set the size and postion on presentation window
        if fullscreen is true then
            -- move window to right screen
            set bounds of front window to {new_top, new_left_pos, new_width, new_height}
            -- put it in fullscreen mode
            tell application "System Events" to tell process "Keynote"
                set value of attribute "AXFullScreen" of front window to true
            end tell
        else
            set bounds of front window to {new_top, new_left_pos, new_width, new_height}
        end if
        activate
    end tell
end start_presentation
--start_presentation("Users:solva_a:Downloads:tomas:applescript:keynote-pres.key", 10, 10, 640, 480, false)

on stop_presentation()
    tell application "Keynote"
        --activate
        -- stop presenting
        if playing is true then tell the front document to stop
        -- close presentation
        close front document
        -- hide keynote
        tell application "System Events"
            set visible of application process "Keynote" to false
        end tell
    end tell
end stop_presentation

on is_loaded(documentPath)
    set documentOldStylePath to POSIX file documentPath as alias
    tell application "Keynote"
        return (file of front document as string is (documentOldStylePath as string))
    end tell
end is_loaded

on is_active()
    tell application "Keynote"
        -- print(?) true/false playing state
        return playing
    end tell
end is_active


on next_slide()
    tell application "Keynote"
        --activate
        if playing is false then start front document from the first slide of front document
        show next
        -- Print(?) slide number
        slide number
    end tell
end next_slide

on previous_slide()
    tell application "Keynote"
        if playing is false then start front document from the first slide of front document
        show previous
        -- Print(?) slide number
        slide number
    end tell
end previous_slide

on goto_slide(slideNumber)
    tell application "Keynote"
        if playing is false then
            start front document from slide slideNumber of front document
        else
            set the current slide to the first slide whose slide number is slideNumber
        end if
    end tell
end goto_slide

on get_current_slide()
    tell application "Keynote"
        -- Print(?) slide number
        slide number
    end tell
end get_current_slide

on blank()
    tell application "Keynote"
        tell application "System Events" to keystroke "b"
    end tell
end blank

on unblank()
    tell application "Keynote"
        tell application "System Events" to keystroke "b"
    end tell
end blank
"""


class KeynoteController(AppleScriptBaseController):
    """
    Class to control interactions with Keynote.
    As well as triggering the correct activities based on the users input.
    """
    log.info('KeynoteController loaded')
    base_class = False

    def __init__(self, plugin):
        """
        Initialise the class
        """
        log.debug('Initialising')
        super(KeynoteController, self).__init__(plugin, 'Keynote', KeynoteDocument)
        if APPLESCRIPT_AVAILABLE:
            # Compiled script expected to be set by subclasses
            try:
                self.applescript = applescript.AppleScript(KEYNOTE_APPLESCRIPT)
            except applescript.ScriptError:
                log.exception('Compilation of Keynote applescript failed')
            self.supports = ['key']
            self.also_supports = ['ppt', 'pps', 'pptx', 'ppsx', 'pptm']

    def check_available(self):
        """
        Program is able to run on this machine.
        """
        ret = super().check_available()
        if ret:
            # Powerpoint is available! now check if the version is 10.1 or above
            try:
                version = self.applescript.call('get_version')
            except Exception:
                log.exception('script execution failed')
                return False
            try:
                versions = version.split('.')
                major_version = int(versions[0])
                if major_version == 10:
                    minor_version = int(versions[1])
                    if minor_version >= 1:
                        return True
                elif major_version > 10:
                    return True
            except ValueError:
                pass
        return False


class KeynoteDocument(AppleScriptBaseDocument):
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
        log.debug('Init Presentation KeynoteDocument')
        super().__init__(controller, document_path)
        self.presentation_loaded = False
        self.is_blank = False

    def load_presentation(self):
        ret = super().load_presentation()
        if ret:
            # Keynote will name the thumbnails in the format: <sha256>.001.png, we need to convert to slide1.png
            old_images = list(self.get_thumbnail_folder().glob('*.png'))
            # if the convertion was already done, don't do it again
            if self.get_thumbnail_folder() / 'slide1.png' in old_images:
                return True
            self.slide_count = len(old_images)
            for old_image in old_images:
                # get the image name in format 001.png
                number_name = old_image.name.split('.', 1)[1]
                # get the image name in format 1.png
                number_name = number_name.lstrip('0')
                new_name = 'slide' + number_name
                shutil.move(old_image, self.get_thumbnail_folder() / new_name)
        return ret
