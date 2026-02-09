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
The :mod:`~openlp.core.ui.media.mediabase` module contains the MediaBase class.
"""
from openlp.core.common.mixins import RegistryProperties
from openlp.core.display.screens import ScreenList


class MediaBase(RegistryProperties):
    """
    This is the base class media Player class to provide OpenLP with a pluggable media display framework.
    """

    def __init__(self, parent, name="media_player"):
        """
        Constructor
        """
        self.parent = parent
        self.name = name
        self.controller = None

    def setup(self, controller, display):
        """
        Create the related widgets for the current display

        :param controller: Which Controller is running the show.
        :param display: The display to be updated.
        """
        pass

    def load(self) -> bool:
        """
        Load a new media file and check if it is valid
        :param controller: Which Controller is running the show.
        :param display: The display to be updated.
        :param file: The file to be loaded
        """
        return True

    def resize(self) -> None:
        """
        Resize the player

        :return:
        """
        if self.controller.is_live:
            self.controller.media_widget.setGeometry(ScreenList().current.display_geometry)
        else:
            self.controller.media_widget.resize(self.controller.preview_display.size())

    def play(self):
        """
        Starts playing of current Media File, media player is expected to loop automatically

        """
        pass

    def pause(self):
        """
        Pause of current Media File

        """
        pass

    def stop(self):
        """
        Stop playing of current Media File

        """
        pass

    def volume(self, vol: int) -> None:
        """
        Set the volume

        :param vol: The volume to be sets
        :return:
        """
        self.audio_output.setVolume(float(vol / 100))

    def seek(self, seek_value: int) -> None:
        """
        Go to a particular position

        :param seek_value: The position of where a seek goes to
        """
        if self.media_player.isSeekable():
            self.media_player.setPosition(seek_value)

    def reset(self) -> None:
        """
        Reset the player

        """
        self.media_player.stop()

    def set_visible(self, status: bool) -> None:
        """
        Set the visibility

        :param status: The visibility status
        """
        self.controller.media_widget.setVisible(status)

    def update_ui(self) -> None:
        """
        Update the UI

        """
        if not self.controller.mediabar.seek_slider.isSliderDown():
            self.controller.mediabar.seek_slider.blockSignals(True)
            self.controller.mediabar.seek_slider.setSliderPosition(self.media_player.position())
            self.controller.mediabar.seek_slider.blockSignals(False)

    def toggle_loop(self, controller, loop_required: bool) -> None:
        """
        Changes the looping style
        :param controller: Which Controller is running the show.
        :param loop_required: Are we to be toggled or not
        :return: none
        """
        pass

    def get_time(self) -> int:
        """Returns the position of the playing media"""
        return self.media_player.position()

    def status(self) -> int:
        """Returns the status of the media"""
        return self.media_player.mediaStatus()
