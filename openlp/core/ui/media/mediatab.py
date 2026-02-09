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
The :mod:`~openlp.core.ui.media.mediatab` module holds the configuration tab for the media stuff.
"""
import logging

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.ui.icons import UiIcons


log = logging.getLogger(__name__)


class MediaTab(SettingsTab):
    """
    MediaTab is the Media settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        self.icon_path = UiIcons().video
        player_translated = translate('OpenLP.MediaTab', 'Media')
        super(MediaTab, self).__init__(parent, 'Media', player_translated)

    def setup_ui(self):
        """
        Set up the UI
        """
        self.setObjectName('MediaTab')
        super(MediaTab, self).setup_ui()
        self.live_media_group_box = QtWidgets.QGroupBox(self.left_column)
        self.live_media_group_box.setObjectName('live_media_group_box')
        self.media_layout = QtWidgets.QVBoxLayout(self.live_media_group_box)
        self.media_layout.setObjectName('live_media_layout')
        self.auto_start_check_box = QtWidgets.QCheckBox(self.live_media_group_box)
        self.auto_start_check_box.setObjectName('auto_start_check_box')
        self.media_layout.addWidget(self.auto_start_check_box)
        self.left_layout.addWidget(self.live_media_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()

    def retranslate_ui(self):
        """
        Translate the UI on the fly
        """
        self.live_media_group_box.setTitle(translate('MediaPlugin.MediaTab', 'Live Media'))
        self.auto_start_check_box.setText(translate('MediaPlugin.MediaTab', 'Start Live items automatically'))

    def load(self):
        """
        Load the settings
        """
        self.auto_start_check_box.setChecked(self.settings.value('media/media auto start') ==
                                             QtCore.Qt.CheckState.Checked)

    def save(self):
        """
        Save the settings
        """
        setting_key = 'media/media auto start'
        if self.settings.value(setting_key) != self.auto_start_check_box.checkState():
            self.settings.setValue(setting_key, self.auto_start_check_box.checkState())

    def post_set_up(self, post_update=False):
        """
        Late setup for players as the MediaController has to be initialised first.

        :param post_update: Indicates if called before or after updates.
        """
        pass

    def on_revert(self):
        pass
