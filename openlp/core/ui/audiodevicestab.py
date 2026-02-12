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
The :mod:`~openlp.core.ui.audiodevicestab` module holds the configuration tab for audio output devices.
"""
import logging

from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media import AUDIO_OUTPUT_DEVICE_DEFAULT, AUDIO_OUTPUT_DEVICE_NONE, get_audio_output_devices


log = logging.getLogger(__name__)


class AudioDevicesTab(SettingsTab):
    """
    AudioDevicesTab is the Audio Devices settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        self.icon_path = UiIcons().audio
        audio_devices_translated = translate('OpenLP.AudioDevicesTab', 'Audio Devices')
        super(AudioDevicesTab, self).__init__(parent, 'Audio Devices', audio_devices_translated)

    def setup_ui(self):
        """
        Set up the UI
        """
        self.setObjectName('AudioDevicesTab')
        super(AudioDevicesTab, self).setup_ui()
        self.audio_device_group_box = QtWidgets.QGroupBox(self.left_column)
        self.audio_device_group_box.setObjectName('audio_device_group_box')
        self.audio_device_layout = QtWidgets.QVBoxLayout(self.audio_device_group_box)
        self.audio_device_layout.setObjectName('audio_device_layout')
        self.audio_output_label = QtWidgets.QLabel(self.audio_device_group_box)
        self.audio_output_label.setObjectName('audio_output_label')
        self.audio_device_layout.addWidget(self.audio_output_label)
        self.audio_output_combo_box = QtWidgets.QComboBox(self.audio_device_group_box)
        self.audio_output_combo_box.setObjectName('audio_output_combo_box')
        self.audio_device_layout.addWidget(self.audio_output_combo_box)
        self.left_layout.addWidget(self.audio_device_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()

    def retranslate_ui(self):
        """
        Translate the UI on the fly
        """
        self.audio_device_group_box.setTitle(translate('OpenLP.AudioDevicesTab', 'Playback'))
        self.audio_output_label.setText(translate('OpenLP.AudioDevicesTab', 'Playback Device'))

    def _load_audio_outputs(self):
        self.audio_output_combo_box.clear()
        self.audio_output_combo_box.addItem(
            translate('OpenLP.AudioDevicesTab', 'Use system default'),
            AUDIO_OUTPUT_DEVICE_DEFAULT
        )
        self.audio_output_combo_box.addItem(
            translate('OpenLP.AudioDevicesTab', 'None (mute output)'),
            AUDIO_OUTPUT_DEVICE_NONE
        )
        for device_id, device_description in get_audio_output_devices():
            self.audio_output_combo_box.addItem(device_description, device_id)

    def load(self):
        """
        Load the settings
        """
        self._load_audio_outputs()
        saved_device = self.settings.value('media/audio output device')
        saved_index = self.audio_output_combo_box.findData(saved_device)
        if saved_index < 0:
            saved_index = 0
        self.audio_output_combo_box.setCurrentIndex(saved_index)

    def save(self):
        """
        Save the settings
        """
        selected_device = self.audio_output_combo_box.currentData()
        if self.settings.value('media/audio output device') != selected_device:
            self.settings.setValue('media/audio output device', selected_device)
            media_controller = Registry().get('media_controller')
            if media_controller:
                media_controller.apply_audio_output_device(check_saved_device=False)

    def post_set_up(self, post_update=False):
        """
        Late setup for players as the MediaController has to be initialised first.

        :param post_update: Indicates if called before or after updates.
        """
        pass

    def on_revert(self):
        pass
