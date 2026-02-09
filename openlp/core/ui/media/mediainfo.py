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
The :mod:`~openlp.core.ui.media.mediainfo` module for media meta data.
"""
import logging

from time import sleep

from PySide6 import QtWidgets
from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QMediaPlayer

log = logging.getLogger(__name__)


class media_info(QObject):

    def get_media_duration(self, media_file: str) -> int:
        """
        Set up a headless media player to parse the mediafile and get duration.

        :param controller: The controller where the media is
        :param display: The display where the media is.
        :return:
        """
        self.got_duration = False
        self.error_occurred = False
        self.duration = 0
        self.media_player = QMediaPlayer(None)
        self.media_player.errorOccurred.connect(self.error_event)
        self.media_player.durationChanged.connect(self.duration_changed_event)
        self.media_player.setSource(QUrl.fromLocalFile(str(media_file)))
        loops = 0
        while not self.got_duration and not self.error_occurred and loops < 100:
            loops += 1
            sleep(0.01)
            QtWidgets.QApplication.instance().processEvents()
        return self.duration

    def duration_changed_event(self, duration: int):
        self.got_duration = True
        self.duration = duration

    def error_event(self, error_text) -> None:
        self.error_occurred = True
