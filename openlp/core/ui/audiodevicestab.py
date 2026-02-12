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
from openlp.core.timecode.midi import MIDI_OUTPUT_DEVICE_NONE, get_midi_output_devices
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media import (
    AUDIO_OUTPUT_DEVICE_DEFAULT,
    AUDIO_OUTPUT_DEVICE_FOLLOW_PLAYBACK,
    AUDIO_OUTPUT_DEVICE_NONE,
    get_audio_output_devices
)


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
        self.timecode_output_label = QtWidgets.QLabel(self.audio_device_group_box)
        self.timecode_output_label.setObjectName('timecode_output_label')
        self.audio_device_layout.addWidget(self.timecode_output_label)
        self.timecode_output_combo_box = QtWidgets.QComboBox(self.audio_device_group_box)
        self.timecode_output_combo_box.setObjectName('timecode_output_combo_box')
        self.audio_device_layout.addWidget(self.timecode_output_combo_box)
        self.timecode_midi_output_label = QtWidgets.QLabel(self.audio_device_group_box)
        self.timecode_midi_output_label.setObjectName('timecode_midi_output_label')
        self.audio_device_layout.addWidget(self.timecode_midi_output_label)
        self.timecode_midi_output_combo_box = QtWidgets.QComboBox(self.audio_device_group_box)
        self.timecode_midi_output_combo_box.setObjectName('timecode_midi_output_combo_box')
        self.audio_device_layout.addWidget(self.timecode_midi_output_combo_box)
        self.timecode_frame_rate_label = QtWidgets.QLabel(self.audio_device_group_box)
        self.timecode_frame_rate_label.setObjectName('timecode_frame_rate_label')
        self.audio_device_layout.addWidget(self.timecode_frame_rate_label)
        self.timecode_frame_rate_combo_box = QtWidgets.QComboBox(self.audio_device_group_box)
        self.timecode_frame_rate_combo_box.setObjectName('timecode_frame_rate_combo_box')
        self.audio_device_layout.addWidget(self.timecode_frame_rate_combo_box)
        self.timecode_mtc_frame_rate_label = QtWidgets.QLabel(self.audio_device_group_box)
        self.timecode_mtc_frame_rate_label.setObjectName('timecode_mtc_frame_rate_label')
        self.audio_device_layout.addWidget(self.timecode_mtc_frame_rate_label)
        self.timecode_mtc_frame_rate_combo_box = QtWidgets.QComboBox(self.audio_device_group_box)
        self.timecode_mtc_frame_rate_combo_box.setObjectName('timecode_mtc_frame_rate_combo_box')
        self.audio_device_layout.addWidget(self.timecode_mtc_frame_rate_combo_box)
        self.timecode_sample_rate_label = QtWidgets.QLabel(self.audio_device_group_box)
        self.timecode_sample_rate_label.setObjectName('timecode_sample_rate_label')
        self.audio_device_layout.addWidget(self.timecode_sample_rate_label)
        self.timecode_sample_rate_combo_box = QtWidgets.QComboBox(self.audio_device_group_box)
        self.timecode_sample_rate_combo_box.setObjectName('timecode_sample_rate_combo_box')
        self.audio_device_layout.addWidget(self.timecode_sample_rate_combo_box)
        self.timecode_bit_depth_label = QtWidgets.QLabel(self.audio_device_group_box)
        self.timecode_bit_depth_label.setObjectName('timecode_bit_depth_label')
        self.audio_device_layout.addWidget(self.timecode_bit_depth_label)
        self.timecode_bit_depth_combo_box = QtWidgets.QComboBox(self.audio_device_group_box)
        self.timecode_bit_depth_combo_box.setObjectName('timecode_bit_depth_combo_box')
        self.audio_device_layout.addWidget(self.timecode_bit_depth_combo_box)
        self.left_layout.addWidget(self.audio_device_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()

    def retranslate_ui(self):
        """
        Translate the UI on the fly
        """
        self.audio_device_group_box.setTitle(translate('OpenLP.AudioDevicesTab', 'Playback'))
        self.audio_output_label.setText(translate('OpenLP.AudioDevicesTab', 'Playback Device'))
        self.timecode_output_label.setText(translate('OpenLP.AudioDevicesTab', 'Timecode Output Device'))
        self.timecode_midi_output_label.setText(translate('OpenLP.AudioDevicesTab', 'Timecode MIDI Output Device'))
        self.timecode_frame_rate_label.setText(translate('OpenLP.AudioDevicesTab', 'Timecode SMPTE/LTC Frame Rate'))
        self.timecode_mtc_frame_rate_label.setText(translate('OpenLP.AudioDevicesTab', 'Timecode MIDI (MTC) Frame Rate'))
        self.timecode_sample_rate_label.setText(translate('OpenLP.AudioDevicesTab', 'Timecode Sample Rate'))
        self.timecode_bit_depth_label.setText(translate('OpenLP.AudioDevicesTab', 'Timecode Bit Depth'))

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
        self.timecode_output_combo_box.clear()
        self.timecode_output_combo_box.addItem(
            translate('OpenLP.AudioDevicesTab', 'Follow playback device setting'),
            AUDIO_OUTPUT_DEVICE_FOLLOW_PLAYBACK
        )
        self.timecode_output_combo_box.addItem(
            translate('OpenLP.AudioDevicesTab', 'Use system default'),
            AUDIO_OUTPUT_DEVICE_DEFAULT
        )
        self.timecode_output_combo_box.addItem(
            translate('OpenLP.AudioDevicesTab', 'None (mute output)'),
            AUDIO_OUTPUT_DEVICE_NONE
        )
        for device_id, device_description in get_audio_output_devices():
            self.timecode_output_combo_box.addItem(device_description, device_id)
        self.timecode_midi_output_combo_box.clear()
        self.timecode_midi_output_combo_box.addItem(
            translate('OpenLP.AudioDevicesTab', 'None (disabled)'),
            MIDI_OUTPUT_DEVICE_NONE
        )
        for device_id, device_description in get_midi_output_devices():
            self.timecode_midi_output_combo_box.addItem(device_description, device_id)
        self.timecode_frame_rate_combo_box.clear()
        for fps in [23.976, 24.0, 25.0, 29.97, 30.0, 48.0, 50.0, 59.94, 60.0]:
            self.timecode_frame_rate_combo_box.addItem(f'{fps:g} fps', fps)
        self.timecode_mtc_frame_rate_combo_box.clear()
        for fps in [24.0, 25.0, 29.97, 30.0]:
            self.timecode_mtc_frame_rate_combo_box.addItem(f'{fps:g} fps', fps)
        self.timecode_sample_rate_combo_box.clear()
        for sample_rate in [44100, 48000, 96000]:
            self.timecode_sample_rate_combo_box.addItem(f'{sample_rate} Hz', sample_rate)
        self.timecode_bit_depth_combo_box.clear()
        self.timecode_bit_depth_combo_box.addItem('8-bit', 8)
        self.timecode_bit_depth_combo_box.addItem('16-bit', 16)
        self.timecode_bit_depth_combo_box.addItem('32-bit', 32)

    def _find_approx_data_index(self, combo_box, value, epsilon=0.002):
        for index in range(combo_box.count()):
            data = combo_box.itemData(index)
            try:
                if abs(float(data) - float(value)) <= epsilon:
                    return index
            except (TypeError, ValueError):
                continue
        return -1

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
        saved_timecode_device = self.settings.value('timecode/audio output device')
        saved_timecode_index = self.timecode_output_combo_box.findData(saved_timecode_device)
        if saved_timecode_index < 0:
            saved_timecode_index = 0
        self.timecode_output_combo_box.setCurrentIndex(saved_timecode_index)
        saved_timecode_midi_device = self.settings.value('timecode/midi output device')
        saved_timecode_midi_index = self.timecode_midi_output_combo_box.findData(saved_timecode_midi_device)
        if saved_timecode_midi_index < 0:
            saved_timecode_midi_index = 0
        self.timecode_midi_output_combo_box.setCurrentIndex(saved_timecode_midi_index)
        saved_frame_rate = float(self.settings.value('timecode/frame rate') or self.settings.value('timecode/fps') or 30.0)
        frame_rate_index = self._find_approx_data_index(self.timecode_frame_rate_combo_box, saved_frame_rate)
        if frame_rate_index < 0:
            frame_rate_index = self._find_approx_data_index(self.timecode_frame_rate_combo_box, 30.0)
        self.timecode_frame_rate_combo_box.setCurrentIndex(frame_rate_index)
        saved_mtc_frame_rate = float(self.settings.value('timecode/mtc frame rate') or saved_frame_rate)
        mtc_frame_rate_index = self._find_approx_data_index(self.timecode_mtc_frame_rate_combo_box, saved_mtc_frame_rate)
        if mtc_frame_rate_index < 0:
            mtc_frame_rate_index = self._find_approx_data_index(self.timecode_mtc_frame_rate_combo_box, 30.0)
        self.timecode_mtc_frame_rate_combo_box.setCurrentIndex(mtc_frame_rate_index)
        saved_sample_rate = int(self.settings.value('timecode/sample rate') or 48000)
        sample_rate_index = self.timecode_sample_rate_combo_box.findData(saved_sample_rate)
        if sample_rate_index < 0:
            sample_rate_index = self.timecode_sample_rate_combo_box.findData(48000)
        self.timecode_sample_rate_combo_box.setCurrentIndex(sample_rate_index)
        saved_bit_depth = int(self.settings.value('timecode/bit depth') or 16)
        bit_depth_index = self.timecode_bit_depth_combo_box.findData(saved_bit_depth)
        if bit_depth_index < 0:
            bit_depth_index = self.timecode_bit_depth_combo_box.findData(16)
        self.timecode_bit_depth_combo_box.setCurrentIndex(bit_depth_index)

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
        selected_timecode_device = self.timecode_output_combo_box.currentData()
        selected_timecode_midi_device = self.timecode_midi_output_combo_box.currentData()
        selected_frame_rate = float(self.timecode_frame_rate_combo_box.currentData())
        selected_mtc_frame_rate = float(self.timecode_mtc_frame_rate_combo_box.currentData())
        selected_sample_rate = int(self.timecode_sample_rate_combo_box.currentData())
        selected_bit_depth = int(self.timecode_bit_depth_combo_box.currentData())
        timecode_changed = False
        if self.settings.value('timecode/audio output device') != selected_timecode_device:
            self.settings.setValue('timecode/audio output device', selected_timecode_device)
            timecode_changed = True
        if self.settings.value('timecode/midi output device') != selected_timecode_midi_device:
            self.settings.setValue('timecode/midi output device', selected_timecode_midi_device)
            timecode_changed = True
        if abs(float(self.settings.value('timecode/frame rate') or 30.0) - selected_frame_rate) > 0.0001:
            self.settings.setValue('timecode/frame rate', selected_frame_rate)
            self.settings.setValue('timecode/fps', selected_frame_rate)
            timecode_changed = True
        if abs(float(self.settings.value('timecode/mtc frame rate') or 30.0) - selected_mtc_frame_rate) > 0.0001:
            self.settings.setValue('timecode/mtc frame rate', selected_mtc_frame_rate)
            timecode_changed = True
        if int(self.settings.value('timecode/sample rate') or 48000) != selected_sample_rate:
            self.settings.setValue('timecode/sample rate', selected_sample_rate)
            timecode_changed = True
        if int(self.settings.value('timecode/bit depth') or 16) != selected_bit_depth:
            self.settings.setValue('timecode/bit depth', selected_bit_depth)
            timecode_changed = True
        if timecode_changed:
            timecode_manager = getattr(Registry().get('main_window'), 'timecode_manager_contents', None)
            if timecode_manager and hasattr(timecode_manager, 'apply_audio_output_device'):
                timecode_manager.apply_audio_output_device()

    def post_set_up(self, post_update=False):
        """
        Late setup for players as the MediaController has to be initialised first.

        :param post_update: Indicates if called before or after updates.
        """
        pass

    def on_revert(self):
        pass
