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
try:
    import applescript
    APPLESCRIPT_AVAILABLE = True
except ImportError:
    APPLESCRIPT_AVAILABLE = False

from openlp.plugins.presentations.lib.applescriptbasecontroller import AppleScriptBaseController, \
    AppleScriptBaseDocument

from PySide6 import QtWidgets
from PySide6.QtPdf import QPdfDocument
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter

from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)


POWERPOINT_MAC_APPLESCRIPT = """
on check_available()
    set appID to "com.microsoft.PowerPoint"
    set doesExist to false
    try
        tell application "Finder" to get application file id appID
        set doesExist to true
    end try
    return doesExist
end check_available

on get_version()
    return (version of application "Microsoft PowerPoint")
end get_version

on start_application()
    tell application "Microsoft PowerPoint"
        launch
        -- Wait for powerpoint to start
        tell application "System Events"
            repeat while true
                set PowerPointUp to (count of (every process whose name is "Microsoft PowerPoint")) > 0
                if PowerPointUp then
                    exit repeat
                else
                    delay 0.2
                end if
            end repeat
        end tell
    end tell
end start_application

-- helper function to write text to files
on write_file(fileName, theData)
    set fileDescriptor to open for access the fileName with write permission
    write theData to fileDescriptor as «class utf8»
    close access fileDescriptor
end write_file

-- helper function to create empty file
on create_empty_file(f)
    write_file(f, "")
    return (POSIX path of f) as POSIX file
end create_empty_file

on create_thumbs(documentName, outputPath)
    tell application "Microsoft PowerPoint"
        -- Open document
        open documentName
        -- wait for document to load
        repeat until document window 1 exists
            delay 0.2
        end repeat
        -- Export slides to jpg
        --save active presentation in outputPath as save as PNG
        -- Export slides to pdf
        save active presentation in my create_empty_file(outputPath & "/tmp.pdf") as save as PDF
        -- Get the Presentation Notes and slide title
        set the slideTitles to ""
        set titleTypes to {placeholder type title placeholder, placeholder type center title placeholder, ¬
            placeholder type vertical title placeholder}
        repeat with tSlide in (get slides of active presentation)
            -- Only handle non-hidden slides
            if hidden of slide show transition of tSlide is false then
                --text = slide.Shapes.Title.TextFrame.TextRange.Text
                -- Get the title of the current slide
                repeat with currentShape in (get shapes of tSlide)
                    tell currentShape to if has text frame then tell its text frame to if has text then
                        set aType to placeholder type of currentShape
                        if aType is not missing value and aType is in titleTypes then
                            set slideTitles to slideTitles & (content of its text range) & return
                            exit repeat
                        end if
                    end if
                end repeat
                set the noteText to ""
                repeat with t_shape in (get shapes of notes page of tSlide)
                    tell t_shape to if has text frame then tell its text frame to if has text then
                        -- get the note of this slide
                        set the noteText to (content of its text range)
                        exit repeat
                    end if
                end repeat
                -- Save note to file
                set noteFilename to outputPath & "/slideNotes" & (slide index of tSlide as string) & ".txt"
                my write_file(noteFilename, noteText)
            end if
        end repeat
        -- Save the titles to file
        set titlesFilename to outputPath & "/titles.txt"
        my write_file(titlesFilename, slideTitles)
        close active presentation
    end tell
end create_thumbs

on close_presentation()
    tell application "Microsoft PowerPoint"
        -- close presentation
        close active presentation
        -- Hide powerpoint
        tell application "System Events"
            set visible of application process "Microsoft PowerPoint" to false
        end tell
    end tell
end close_presentation

on start_presentation(documentName, new_top, new_left_pos, new_width, new_height, fullscreen)
    tell application "Microsoft PowerPoint"
        -- Open document
        open documentName
        -- wait for document to load
        repeat until document window 1 exists
            delay 0.2
        end repeat
        -- disable presenter console
        set showpresenterview of slide show settings of active presentation to 0
        -- set presentation to show presentation in window
        set show type of slide show settings of active presentation to slide show type window
        -- start presentation
        run slide show slide show settings of active presentation
        -- set the size and postion on presentation window
        set top of slide show window of active presentation to new_top
        set left position of slide show window of active presentation to new_left_pos
        if fullscreen is true then
            -- put it in fullscreen mode
            tell application "System Events" to tell process "Microsoft PowerPoint"
                set value of attribute "AXFullScreen" of front window to true
            end tell
        else
            set height of slide show window of active presentation to new_height
            set width of slide show window of active presentation to new_width
        end if
        -- move to the front
        activate
    end tell
end start_presentation

on stop_presentation()
    tell application "Microsoft PowerPoint"
        -- stop presenting - self.presentation.SlideShowWindow.View.Exit()
        exit slide show slide show view of slide show window 1
        -- close presentation
        close active presentation
        -- Hide powerpoint
        tell application "System Events"
            set visible of application process "Microsoft PowerPoint" to false
        end tell
    end tell
end stop_presentation

on is_loaded(documentPath)
    tell application "Microsoft PowerPoint"
        return (full name of active presentation is (documentPath as string))
    end tell
end is_loaded

on is_active()
    tell application "Microsoft PowerPoint"
        -- when the presentation window is out of focus it is paused, so check for both paused and running
        return (slide state of slide show view of slide show window of active presentation is ¬
            slide show state running) ¬
            or (slide state of slide show view of slide show window of active presentation is ¬
            slide show state paused)
    end tell
end is_active

on next_slide()
    tell application "Microsoft PowerPoint"
        --activate
        -- self.presentation.SlideShowWindow.View.Next()
        go to next slide slide show view of slide show window 1
        -- Print(?) slide number
        -- slide number of slide of slideshow view of slide show window of active presentation
    end tell
end next_slide

on previous_slide()
    tell application "Microsoft PowerPoint"
        --activate
        go to previous slide slide show view of slide show window 1
        -- Print(?) slide number
        -- self.presentation.SlideShowWindow.View.Slide.SlideNumber
        -- slide number of slide of view of slide show window of active presentation
    end tell
end previous_slide

on goto_slide(slideNumber)
    tell application "Microsoft PowerPoint"
        activate
        -- self.presentation.SlideShowWindow.View.GotoSlide(slideNumber)
        --go to slide slideNumber of slide show window of active presentation
        -- there seems to be no applescipt-way of going to a specific slide, so send keystroke
        tell application "System Events"
            keystroke (slideNumber as string)
            key code 36
        end tell
    end tell
end goto_slide

on get_current_slide()
    tell application "Microsoft PowerPoint"
        --activate
        -- Print(?) slide number
        return slide number of slide of slide show view of slide show window of active presentation
    end tell
end get_current_slide

on blank()
    tell application "Microsoft PowerPoint"
        --activate
        -- self.presentation.SlideShowWindow.View.State = 3
        --set state of slide of view of slide show window of active presentation to 3
        set slide state of slide show view of slide show window 1 to slide show state black screen
    end tell
end blank

on unblank()
    tell application "Microsoft PowerPoint"
        --activate
        -- self.presentation.SlideShowWindow.View.State = 1
        set slide state of slide show view of slide show window 1 to slide show state running
    end tell
end unblank
"""


class PowerPointMacController(AppleScriptBaseController):
    """
    Class to control interactions with a Powerpoint for Mac.
    As well as triggering the correct activities based on the users input.
    """
    log.info('PowerPointMacController loaded')
    base_class = False

    def __init__(self, plugin):
        """
        Initialise the class
        """
        log.debug('Initialising')
        super(PowerPointMacController, self).__init__(plugin, 'PowerPointMac', PowerPointMacDocument)
        if APPLESCRIPT_AVAILABLE:
            # Compiled script expected to be set by subclasses
            try:
                self.applescript = applescript.AppleScript(POWERPOINT_MAC_APPLESCRIPT)
            except applescript.ScriptError:
                log.exception('Compilation of Powerpoint applescript failed')
            self.supports = ['ppt', 'pps', 'pptx', 'ppsx', 'pptm']
            self.also_supports = ['odp']

    def check_available(self):
        """
        Program is able to run on this machine.
        """
        ret = super().check_available()
        if ret:
            # Powerpoint is available! now check if the version is 15 (Powerpoint 2016) or above
            try:
                version = self.applescript.call('get_version')
            except Exception:
                log.exception('script execution failed')
                return False
            try:
                major_version = int(version.split('.')[0])
            except ValueError:
                return False
            if major_version >= 15:
                return True
        return False


class PowerPointMacDocument(AppleScriptBaseDocument):
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
        self.is_blank = False

    def load_presentation(self):
        ret = super().load_presentation()
        if ret:
            # we make powerpoint export to PDF and then convert the pdf to thumbnails
            pdf_file = self.get_thumbnail_folder() / 'tmp.pdf'
            # if the pdf file does not exists anymore it is assume the convertion has been done
            if not pdf_file.exists():
                return True
            log.debug('converting pdf to png thumbnails using QPdf')
            pdf_doc = QPdfDocument(Registry().get('application'))
            pdf_doc.load(str(pdf_file))
            # wait for loading to complete
            while pdf_doc.status() != QPdfDocument.Status.Ready:
                QtWidgets.QApplication.processEvents()
            # Generate images from PDF
            log.debug('loading presentation using QPdfDocument')
            painter = QPainter()
            for i in range(0, pdf_doc.pageCount()):
                page_size = pdf_doc.pagePointSize(i).toSize()
                scaled_page_size = page_size.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
                image = pdf_doc.render(i, scaled_page_size)
                png_filename = str(self.get_thumbnail_folder() / 'slide{num}.png'.format(num=i + 1))
                # due to the background not being set to white by default, it needs to be done manually
                image_redraw = QImage(image.size(), QImage.Format_ARGB32)
                image_redraw.fill(QColor(Qt.white).rgb())
                painter.begin(image_redraw)
                painter.drawImage(0, 0, image)
                image_redraw.save(png_filename, 'png')
                painter.end()
            # delete pdf
            pdf_file.unlink()
        return ret
