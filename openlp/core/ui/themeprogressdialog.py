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
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.display.render import ThemePreviewRenderer
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.layouts import AspectRatioLayout


class UiThemeProgressDialog(object):
    """
    The GUI widgets for the ThemeProgressDialog
    """

    def setup_ui(self, theme_progress_dialog):
        """
        Set up the UI for the dialog.

        :param theme_progress_dialog: The QDialog object to set up.
        """
        theme_progress_dialog.setObjectName('theme_progress_dialog')
        theme_progress_dialog.setWindowIcon(UiIcons().main_icon)
        theme_progress_dialog.resize(400, 306)
        self.theme_progress_layout = QtWidgets.QVBoxLayout(theme_progress_dialog)
        self.theme_progress_layout.setObjectName('theme_progress_layout')
        self.preview_area = QtWidgets.QWidget(theme_progress_dialog)
        self.preview_area.setObjectName('PreviewArea')
        self.theme_preview_layout = AspectRatioLayout(self.preview_area, 0.75)  # Dummy ratio, will be update
        self.theme_preview_layout.margin = 8
        self.theme_preview_layout.setSpacing(0)
        self.theme_preview_layout.setObjectName('preview_web_layout')
        self.theme_display = ThemePreviewRenderer(theme_progress_dialog, can_show_startup_screen=False,
                                                  window_title='Theme Progress Dialog')
        self.theme_display.setObjectName('theme_display')
        self.theme_preview_layout.addWidget(self.theme_display)
        self.theme_progress_layout.addWidget(self.preview_area)
        self.label = QtWidgets.QLabel(theme_progress_dialog)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName('label')
        self.theme_progress_layout.addWidget(self.label)
        self.progress_bar = QtWidgets.QProgressBar(theme_progress_dialog)
        self.progress_bar.setProperty('value', 24)
        self.progress_bar.setObjectName('progress_bar')
        self.theme_progress_layout.addWidget(self.progress_bar)
        self.theme_display.show()

        self.retranslate_ui(theme_progress_dialog)
        QtCore.QMetaObject.connectSlotsByName(theme_progress_dialog)

    def retranslate_ui(self, theme_progress_dialog):
        """
        Dynamically translate the UI.

        :param about_dialog: The QDialog object to translate
        """
        theme_progress_dialog.setWindowTitle(translate('OpenLP.Themes', 'Recreating Theme Thumbnails'))
