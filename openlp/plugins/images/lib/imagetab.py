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

from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.common.enum import ImageThemeMode
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.lib.ui import find_and_set_in_combo_box


class ImageTab(SettingsTab):
    """
    ImageTab is the images settings tab in the settings dialog.
    """
    def setup_ui(self):
        self.setObjectName('ImagesTab')
        super(ImageTab, self).setup_ui()
        self.image_theme_group_box = QtWidgets.QGroupBox(self.left_column)
        self.image_theme_group_box.setObjectName('image_theme_group_box')
        self.image_theme_group_box_layout = QtWidgets.QFormLayout(self.image_theme_group_box)
        self.image_theme_group_box_layout.setObjectName('image_theme_group_box_layout')
        # Theme mode radios
        self.radio_group = QtWidgets.QButtonGroup(self)
        self.use_black_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.use_black_radio, ImageThemeMode.Black)
        self.image_theme_group_box_layout.setWidget(0, QtWidgets.QFormLayout.ItemRole.SpanningRole,
                                                    self.use_black_radio)
        self.custom_theme_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.custom_theme_radio, ImageThemeMode.CustomTheme)
        self.image_theme_group_box_layout.setWidget(2, QtWidgets.QFormLayout.ItemRole.SpanningRole,
                                                    self.custom_theme_radio)
        # Theme selection
        self.theme_combo_box = QtWidgets.QComboBox(self.image_theme_group_box)
        self.theme_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.theme_combo_box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.theme_combo_box.setObjectName('theme_combo_box')
        self.image_theme_label = QtWidgets.QLabel(self.theme_combo_box)
        self.image_theme_label.setObjectName('image_theme_label')
        self.image_theme_group_box_layout.addRow(self.image_theme_label, self.theme_combo_box)
        # Add all to layout
        self.left_layout.addWidget(self.image_theme_group_box)
        self.left_layout.addStretch()
        self.right_column.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.right_layout.addStretch()
        # Signals and slots
        self.radio_group.buttonToggled.connect(self.on_radio_group_button_toggled)
        self.theme_combo_box.activated.connect(self.on_image_theme_changed)
        Registry().register_function('theme_update_list', self.update_theme_list)

    def retranslate_ui(self):
        self.image_theme_group_box.setTitle(translate('ImagesPlugin.ImageTab', 'Image Background'))
        self.use_black_radio.setText(translate('ImagesPlugin.ImageTab', 'Use blank theme'))
        self.custom_theme_radio.setText(translate('ImagesPlugin.ImageTab', 'Custom theme'))
        self.image_theme_label.setText(translate('ImagesPlugin.ImageTab', 'Theme:'))

    def on_radio_group_button_toggled(self, button, checked):
        """
        Handles the toggled signal on the radio buttons. The signal is emitted twice if a radio butting being toggled on
        causes another radio button in the group to be toggled off.

        En/Disables the `Custom Theme` line edits depending on the currently selected radio button

        :param QtWidgets.QRadioButton button: The button that has toggled
        :param bool checked: The buttons new state
        """
        group_id = self.radio_group.id(button)  # The work around (see above comment)
        enable_manual_edits = group_id == ImageThemeMode.CustomTheme and checked
        if checked:
            self.background_mode = group_id
        self.theme_combo_box.setEnabled(enable_manual_edits)

    def on_image_theme_changed(self):
        self.image_theme = self.theme_combo_box.currentText()

    def update_theme_list(self, theme_list):
        """
        Called from ThemeManager when the Themes have changed.

        :param theme_list: The list of available themes::

                ['Bible Theme', 'Song Theme']
        """
        # Reload as may have been triggered by the ThemeManager.
        self.image_theme = self.settings.value('images/theme')
        self.theme_combo_box.clear()
        self.theme_combo_box.addItems(theme_list)
        find_and_set_in_combo_box(self.theme_combo_box, self.image_theme)

    def load(self):
        self.background_mode = self.settings.value('images/background mode')
        self.initial_mode = self.background_mode
        checked_radio = self.radio_group.button(self.background_mode)
        checked_radio.setChecked(True)
        self.image_theme = self.settings.value('images/theme')
        self.initial_theme = self.image_theme

    def save(self):
        self.settings.setValue('images/background mode', self.radio_group.checkedId())
        self.settings.setValue('images/theme', self.image_theme)
        if self.initial_theme != self.image_theme or self.initial_mode != self.background_mode:
            self.settings_form.register_post_process('images_config_updated')
