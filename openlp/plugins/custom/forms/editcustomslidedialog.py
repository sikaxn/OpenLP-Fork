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

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib.ui import create_button, create_button_box
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.edits import SpellTextEdit


class Ui_CustomSlideEditDialog(object):
    def setup_ui(self, custom_slide_edit_dialog):
        custom_slide_edit_dialog.setObjectName('custom_slide_edit_dialog')
        custom_slide_edit_dialog.setWindowIcon(UiIcons().main_icon)
        custom_slide_edit_dialog.resize(350, 300)
        self.dialog_layout = QtWidgets.QVBoxLayout(custom_slide_edit_dialog)
        self.slide_text_edit = SpellTextEdit(self)
        self.slide_text_edit.setObjectName('slide_text_edit')
        self.dialog_layout.addWidget(self.slide_text_edit)
        self.split_button = create_button(custom_slide_edit_dialog, 'splitButton', icon=UiIcons().add)
        self.insert_button = create_button(custom_slide_edit_dialog, 'insertButton', icon=UiIcons().add)
        self.button_box = create_button_box(custom_slide_edit_dialog, 'button_box', ['cancel', 'save'],
                                            [self.split_button, self.insert_button])
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui(custom_slide_edit_dialog)

    def retranslate_ui(self, custom_slide_edit_dialog):
        custom_slide_edit_dialog.setWindowTitle(translate('CustomPlugin.EditVerseForm', 'Edit Slide'))
        self.split_button.setText(UiStrings().Split)
        self.split_button.setToolTip(UiStrings().SplitToolTip)
        self.insert_button.setText(translate('CustomPlugin.EditCustomForm', 'Insert Slide'))
        self.insert_button.setToolTip(translate('CustomPlugin.EditCustomForm',
                                                'Split a slide into two by inserting a slide splitter.'))
