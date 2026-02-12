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
Settings tab for the LRC Player plugin.
"""
from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.settingstab import SettingsTab


class LrcPlayerTab(SettingsTab):
    """
    LRC Player settings.
    """
    def setup_ui(self):
        self.setObjectName('LrcPlayerTab')
        super(LrcPlayerTab, self).setup_ui()
        self.behavior_group_box = QtWidgets.QGroupBox(self.left_column)
        self.behavior_group_box.setObjectName('behavior_group_box')
        self.behavior_layout = QtWidgets.QFormLayout(self.behavior_group_box)
        self.behavior_layout.setObjectName('behavior_layout')

        self.end_behavior_combo_box = QtWidgets.QComboBox(self.behavior_group_box)
        self.end_behavior_combo_box.setObjectName('end_behavior_combo_box')
        self.behavior_layout.addRow(self.end_behavior_combo_box)

        self.add_empty_start_line_check_box = QtWidgets.QCheckBox(self.behavior_group_box)
        self.add_empty_start_line_check_box.setObjectName('add_empty_start_line_check_box')
        self.behavior_layout.addRow(self.add_empty_start_line_check_box)
        self.timecode_note_label = QtWidgets.QLabel(self.behavior_group_box)
        self.timecode_note_label.setObjectName('timecode_note_label')
        self.timecode_note_label.setWordWrap(True)
        self.behavior_layout.addRow(self.timecode_note_label)

        self.left_layout.addWidget(self.behavior_group_box)
        self.left_layout.addStretch()
        self.right_layout.addStretch()

    def retranslate_ui(self):
        self.behavior_group_box.setTitle(translate('LrcPlayerPlugin.LrcPlayerTab', 'LRC Playback'))
        self.end_behavior_combo_box.clear()
        self.end_behavior_combo_box.addItem(
            translate('LrcPlayerPlugin.LrcPlayerTab', 'When done playing: Go back to first line'),
            'reset_to_start'
        )
        self.end_behavior_combo_box.addItem(
            translate('LrcPlayerPlugin.LrcPlayerTab', 'When done playing: Stay at last line'),
            'stay_on_last'
        )
        self.add_empty_start_line_check_box.setText(
            translate('LrcPlayerPlugin.LrcPlayerTab', 'Add empty first line at 0:00 when importing LRC')
        )
        self.timecode_note_label.setText(
            translate(
                'LrcPlayerPlugin.LrcPlayerTab',
                'Note: If Timecode is active and "Go back to first line" is selected, timecode will also return to '
                '00:00. To reduce visible jumps during resets, consider keeping an empty lyric line in your LRC for '
                'blank screen, or use Companion automation to handle the timecode change before the lyric reset.'
            )
        )

    def load(self):
        saved_behavior = self.settings.value('lrcplayer/end behavior')
        saved_behavior_index = self.end_behavior_combo_box.findData(saved_behavior)
        if saved_behavior_index < 0:
            saved_behavior_index = 0
        self.end_behavior_combo_box.setCurrentIndex(saved_behavior_index)
        self.add_empty_start_line_check_box.setChecked(bool(self.settings.value('lrcplayer/add empty line on import')))

    def save(self):
        self.settings.setValue('lrcplayer/end behavior', self.end_behavior_combo_box.currentData())
        self.settings.setValue('lrcplayer/add empty line on import', self.add_empty_start_line_check_box.isChecked())
