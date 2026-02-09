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
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_LanguageDialog(object):
    def setup_ui(self, language_dialog):
        language_dialog.setObjectName('language_dialog')
        language_dialog.setWindowIcon(UiIcons().main_icon)
        language_dialog.resize(400, 165)
        self.language_layout = QtWidgets.QVBoxLayout(language_dialog)
        self.language_layout.setSpacing(8)
        self.language_layout.setContentsMargins(8, 8, 8, 8)
        self.language_layout.setObjectName('language_layout')
        self.bible_label = QtWidgets.QLabel(language_dialog)
        self.bible_label.setObjectName('bible_label')
        self.language_layout.addWidget(self.bible_label)
        self.info_label = QtWidgets.QLabel(language_dialog)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName('info_label')
        self.language_layout.addWidget(self.info_label)
        self.language_h_box_layout = QtWidgets.QHBoxLayout()
        self.language_h_box_layout.setSpacing(8)
        self.language_h_box_layout.setObjectName('language_h_box_layout')
        self.language_label = QtWidgets.QLabel(language_dialog)
        self.language_label.setObjectName('language_label')
        self.language_h_box_layout.addWidget(self.language_label)
        self.language_combo_box = QtWidgets.QComboBox(language_dialog)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                            QtWidgets.QSizePolicy.Policy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.language_combo_box.sizePolicy().hasHeightForWidth())
        self.language_combo_box.setSizePolicy(size_policy)
        self.language_combo_box.setObjectName('language_combo_box')
        self.language_h_box_layout.addWidget(self.language_combo_box)
        self.language_layout.addLayout(self.language_h_box_layout)
        self.button_box = create_button_box(language_dialog, 'button_box', ['cancel', 'ok'])
        self.language_layout.addWidget(self.button_box)

        self.retranslate_ui(language_dialog)

    def retranslate_ui(self, language_dialog):
        language_dialog.setWindowTitle(translate('BiblesPlugin.LanguageDialog', 'Select Language'))
        self.bible_label.setText(translate('BiblesPlugin.LanguageDialog', ''))
        self.info_label.setText(
            translate('BiblesPlugin.LanguageDialog',
                      'OpenLP is unable to determine the language of this translation of the Bible. Please select '
                      'the language from the list below.'))
        self.language_label.setText(translate('BiblesPlugin.LanguageDialog', 'Language:'))
