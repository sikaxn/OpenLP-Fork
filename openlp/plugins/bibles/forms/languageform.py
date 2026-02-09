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
Module implementing LanguageForm.
"""
import logging

from PySide6 import QtCore
from PySide6.QtWidgets import QDialog

from openlp.core.common.i18n import LANGUAGES, translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.bibles.forms.languagedialog import Ui_LanguageDialog


log = logging.getLogger(__name__)


class LanguageForm(QDialog, Ui_LanguageDialog):
    """
    Class to manage a dialog which ask the user for a language.
    """
    log.info('LanguageForm loaded')

    def __init__(self, parent=None):
        """
        Constructor
        """
        super(LanguageForm, self).__init__(parent,
                                           QtCore.Qt.WindowType.WindowSystemMenuHint |
                                           QtCore.Qt.WindowType.WindowTitleHint |
                                           QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)

    def exec(self, bible_name):
        if bible_name:
            self.bible_label.setText(bible_name)
        self.language_combo_box.addItem('')
        for language in LANGUAGES:
            self.language_combo_box.addItem(language.name, language.id)
        return QDialog.exec(self)

    def accept(self):
        if not self.language_combo_box.currentText():
            critical_error_message_box(message=translate('BiblesPlugin.LanguageForm', 'You need to choose a language.'))
            self.language_combo_box.setFocus()
            return False
        else:
            return QDialog.accept(self)
