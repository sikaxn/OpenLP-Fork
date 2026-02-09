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

from PySide6 import QtGui, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.lib.ui import create_valign_selection_widgets
from openlp.core.widgets.buttons import ColorButton


class AlertsTab(SettingsTab):
    """
    AlertsTab is the alerts settings tab in the settings dialog.
    """
    def setup_ui(self):
        self.setObjectName('AlertsTab')
        super(AlertsTab, self).setup_ui()
        self.font_group_box = QtWidgets.QGroupBox(self.left_column)
        self.font_group_box.setObjectName('font_group_box')
        self.font_layout = QtWidgets.QFormLayout(self.font_group_box)
        self.font_layout.setObjectName('font_layout')
        self.font_label = QtWidgets.QLabel(self.font_group_box)
        self.font_label.setObjectName('font_label')
        self.font_combo_box = QtWidgets.QFontComboBox(self.font_group_box)
        self.font_combo_box.setObjectName('font_combo_box')
        self.font_layout.addRow(self.font_label, self.font_combo_box)
        self.font_color_label = QtWidgets.QLabel(self.font_group_box)
        self.font_color_label.setObjectName('font_color_label')
        self.font_color_button = ColorButton(self.font_group_box)
        self.font_color_button.setObjectName('font_color_button')
        self.font_layout.addRow(self.font_color_label, self.font_color_button)
        self.font_size_label = QtWidgets.QLabel(self.font_group_box)
        self.font_size_label.setObjectName('font_size_label')
        self.font_size_spin_box = QtWidgets.QSpinBox(self.font_group_box)
        self.font_size_spin_box.setObjectName('font_size_spin_box')
        self.font_layout.addRow(self.font_size_label, self.font_size_spin_box)
        self.left_layout.addWidget(self.font_group_box)
        # Background Settings
        self.background_group_box = QtWidgets.QGroupBox(self.left_column)
        self.background_group_box.setObjectName('background_group_box')
        self.background_layout = QtWidgets.QFormLayout(self.background_group_box)
        self.background_layout.setObjectName('background_settings_layout')
        self.background_color_label = QtWidgets.QLabel(self.background_group_box)
        self.background_color_label.setObjectName('background_color_label')
        self.background_color_button = ColorButton(self.background_group_box)
        self.background_color_button.setObjectName('background_color_button')
        self.background_layout.addRow(self.background_color_label, self.background_color_button)
        self.left_layout.addWidget(self.background_group_box)
        # Scroll Settings
        self.scroll_group_box = QtWidgets.QGroupBox(self.left_column)
        self.scroll_group_box.setObjectName('scroll_group_box')
        self.scroll_group_layout = QtWidgets.QFormLayout(self.scroll_group_box)
        self.scroll_group_layout.setObjectName('scroll_group_layout')
        self.scroll_check_box = QtWidgets.QCheckBox(self.scroll_group_box)
        self.scroll_check_box.setObjectName('scroll_check_box')
        self.scroll_group_layout.addRow(self.scroll_check_box)
        self.repeat_label = QtWidgets.QLabel(self.scroll_group_box)
        self.repeat_label.setObjectName('repeat_label')
        self.repeat_spin_box = QtWidgets.QSpinBox(self.scroll_group_box)
        self.repeat_spin_box.setObjectName('repeat_spin_box')
        self.scroll_group_layout.addRow(self.repeat_label, self.repeat_spin_box)
        self.left_layout.addWidget(self.scroll_group_box)
        # Other Settings
        self.settings_group_box = QtWidgets.QGroupBox(self.left_column)
        self.settings_group_box.setObjectName('settings_group_box')
        self.settings_layout = QtWidgets.QFormLayout(self.settings_group_box)
        self.settings_layout.setObjectName('settings_layout')
        self.timeout_label = QtWidgets.QLabel(self.settings_group_box)
        self.timeout_label.setObjectName('timeout_label')
        self.timeout_spin_box = QtWidgets.QSpinBox(self.settings_group_box)
        self.timeout_spin_box.setMaximum(180)
        self.timeout_spin_box.setObjectName('timeout_spin_box')
        self.settings_layout.addRow(self.timeout_label, self.timeout_spin_box)
        self.vertical_label, self.vertical_combo_box = create_valign_selection_widgets(self.font_group_box)
        self.vertical_label.setObjectName('vertical_label')
        self.vertical_combo_box.setObjectName('vertical_combo_box')
        self.settings_layout.addRow(self.vertical_label, self.vertical_combo_box)
        self.left_layout.addWidget(self.settings_group_box)
        self.left_layout.addStretch()
        self.preview_group_box = QtWidgets.QGroupBox(self.right_column)
        self.preview_group_box.setObjectName('preview_group_box')
        self.preview_layout = QtWidgets.QVBoxLayout(self.preview_group_box)
        self.preview_layout.setObjectName('preview_layout')
        self.font_preview = QtWidgets.QLineEdit(self.preview_group_box)
        self.font_preview.setObjectName('font_preview')
        self.preview_layout.addWidget(self.font_preview)
        self.right_layout.addWidget(self.preview_group_box)
        self.right_layout.addStretch()
        # Signals and slots
        self.background_color_button.colorChanged.connect(self.on_background_color_changed)
        self.font_color_button.colorChanged.connect(self.on_font_color_changed)
        self.font_combo_box.activated.connect(self.on_font_combo_box_clicked)
        self.timeout_spin_box.valueChanged.connect(self.on_timeout_spin_box_changed)
        self.font_size_spin_box.valueChanged.connect(self.on_font_size_spin_box_changed)
        self.repeat_spin_box.valueChanged.connect(self.on_repeat_spin_box_changed)
        self.scroll_check_box.toggled.connect(self.scroll_check_box_toggled)

    def retranslate_ui(self):
        self.font_group_box.setTitle(translate('AlertsPlugin.AlertsTab', 'Font Settings'))
        self.font_label.setText(translate('AlertsPlugin.AlertsTab', 'Font name:'))
        self.font_color_label.setText(translate('AlertsPlugin.AlertsTab', 'Font color:'))
        self.background_color_label.setText(UiStrings().BackgroundColorColon)
        self.font_size_label.setText(translate('AlertsPlugin.AlertsTab', 'Font size:'))
        self.font_size_spin_box.setSuffix(' {unit}'.format(unit=UiStrings().FontSizePtUnit))
        self.background_group_box.setTitle(translate('AlertsPlugin.AlertsTab', 'Background Settings'))
        self.settings_group_box.setTitle(translate('AlertsPlugin.AlertsTab', 'Other Settings'))
        self.timeout_label.setText(translate('AlertsPlugin.AlertsTab', 'Alert timeout:'))
        self.timeout_spin_box.setSuffix(' {unit}'.format(unit=UiStrings().Seconds))
        self.repeat_label.setText(translate('AlertsPlugin.AlertsTab', 'Repeat (no. of times):'))
        self.scroll_check_box.setText(translate('AlertsPlugin.AlertsTab', 'Enable Scrolling'))
        self.preview_group_box.setTitle(UiStrings().Preview)
        self.font_preview.setText(UiStrings().OpenLP)

    def on_background_color_changed(self, color):
        """
        The background color has been changed.
        """
        self.background_color = color
        self.update_display()

    def on_font_combo_box_clicked(self):
        """
        The Font Combo was changed.
        """
        self.update_display()

    def on_font_color_changed(self, color):
        """
        The Font Color button has clicked.
        """
        self.font_color = color
        self.update_display()

    def on_timeout_spin_box_changed(self):
        """
        The Time out spin box has changed.

        """
        self.timeout = self.timeout_spin_box.value()
        self.changed = True

    def on_font_size_spin_box_changed(self):
        """
        The font size spin box has changed.
        """
        self.font_size = self.font_size_spin_box.value()
        self.update_display()

    def on_repeat_spin_box_changed(self):
        """
        The repeat spin box has changed
        """
        self.repeat = self.repeat_spin_box.value()
        self.changed = True

    def scroll_check_box_toggled(self):
        """
        The scrolling checkbox has been toggled
        """
        if self.scroll_check_box.isChecked():
            self.repeat_spin_box.setEnabled(True)
        else:
            self.repeat_spin_box.setEnabled(False)
        self.scroll = self.scroll_check_box.isChecked()
        self.changed = True

    def load(self):
        """
        Load the settings into the UI.
        """
        self.timeout = self.settings.value('alerts/timeout')
        self.font_color = self.settings.value('alerts/font color')
        self.font_size = self.settings.value('alerts/font size')
        self.background_color = self.settings.value('alerts/background color')
        self.font_face = self.settings.value('alerts/font face')
        self.location = self.settings.value('alerts/location')
        self.repeat = self.settings.value('alerts/repeat')
        self.scroll = self.settings.value('alerts/scroll')
        self.font_size_spin_box.setValue(self.font_size)
        self.timeout_spin_box.setValue(self.timeout)
        self.font_color_button.color = self.font_color
        self.background_color_button.color = self.background_color
        self.repeat_spin_box.setValue(self.repeat)
        self.repeat_spin_box.setEnabled(self.scroll)
        self.vertical_combo_box.setCurrentIndex(self.location)
        self.scroll_check_box.setChecked(self.scroll)
        font = QtGui.QFont()
        font.setFamily(self.font_face)
        self.font_combo_box.setCurrentFont(font)
        self.update_display()
        self.changed = False

    def save(self):
        """
        Save the changes on exit of the Settings dialog.
        """
        # Check value has changed as no event handles this field
        if self.settings.value('alerts/location') != self.vertical_combo_box.currentIndex():
            self.changed = True
        self.settings.setValue('alerts/background color', self.background_color)
        self.settings.setValue('alerts/font color', self.font_color)
        self.settings.setValue('alerts/font size', self.font_size)
        self.font_face = self.font_combo_box.currentFont().family()
        self.settings.setValue('alerts/font face', self.font_face)
        self.settings.setValue('alerts/timeout', self.timeout)
        self.location = self.vertical_combo_box.currentIndex()
        self.settings.setValue('alerts/location', self.location)
        self.settings.setValue('alerts/repeat', self.repeat)
        self.settings.setValue('alerts/scroll', self.scroll_check_box.isChecked())
        if self.changed:
            self.settings_form.register_post_process('update_display_css')
        self.changed = False

    def update_display(self):
        """
        Update the preview display after changes have been made,
        """
        font = QtGui.QFont()
        font.setFamily(self.font_combo_box.currentFont().family())
        font.setBold(True)
        font.setPointSize(self.font_size)
        self.font_preview.setFont(font)
        self.font_preview.setStyleSheet('background-color: {back}; color: {front}'.format(back=self.background_color,
                                                                                          front=self.font_color))
        self.changed = True
