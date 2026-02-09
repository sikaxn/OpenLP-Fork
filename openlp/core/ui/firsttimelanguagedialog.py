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
The UI widgets of the language selection dialog.
"""
from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_FirstTimeLanguageDialog(object):
    """
    The UI widgets of the language selection dialog.
    """
    def setup_ui(self, language_dialog):
        """
        Set up the UI.
        """
        language_dialog.setObjectName('language_dialog')
        language_dialog.setWindowIcon(UiIcons().main_icon)
        language_dialog.resize(300, 50)
        self.dialog_layout = QtWidgets.QVBoxLayout(language_dialog)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setObjectName('dialog_layout')
        self.info_label = QtWidgets.QLabel(language_dialog)
        self.info_label.setObjectName('info_label')
        self.dialog_layout.addWidget(self.info_label)
        self.language_layout = QtWidgets.QHBoxLayout()
        self.language_layout.setObjectName('language_layout')
        self.language_label = QtWidgets.QLabel(language_dialog)
        self.language_label.setObjectName('language_label')
        self.language_layout.addWidget(self.language_label)
        self.language_combo_box = QtWidgets.QComboBox(language_dialog)
        self.language_combo_box.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.language_combo_box.setObjectName("language_combo_box")
        self.language_layout.addWidget(self.language_combo_box)
        self.dialog_layout.addLayout(self.language_layout)
        self.button_box = create_button_box(language_dialog, 'button_box', ['cancel', 'ok'])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui(language_dialog)
        self.setMaximumHeight(self.sizeHint().height())

    def retranslate_ui(self, language_dialog):
        """
        Translate the UI on the fly.
        """
        self.setWindowTitle(translate('OpenLP.FirstTimeLanguageForm', 'Select Translation'))
        self.info_label.setText(
            translate('OpenLP.FirstTimeLanguageForm', 'Choose the translation you\'d like to use in OpenLP.'))
        self.language_label.setText(translate('OpenLP.FirstTimeLanguageForm', 'Translation:'))
