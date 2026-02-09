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
The layout of the theme
"""
from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons


class Ui_ThemeLayoutDialog(object):
    """
    The layout of the theme
    """
    def setup_ui(self, themeLayoutDialog):
        """
        Set up the UI
        """
        themeLayoutDialog.setObjectName('themeLayoutDialogDialog')
        themeLayoutDialog.setWindowIcon(UiIcons().main_icon)
        self.preview_layout = QtWidgets.QVBoxLayout(themeLayoutDialog)
        self.preview_layout.setObjectName('preview_layout')
        self.preview_area = QtWidgets.QWidget(themeLayoutDialog)
        self.preview_area.setObjectName('preview_area')
        self.preview_area_layout = QtWidgets.QGridLayout(self.preview_area)
        self.preview_area_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_area_layout.setColumnStretch(0, 1)
        self.preview_area_layout.setRowStretch(0, 1)
        self.preview_area_layout.setObjectName('preview_area_layout')
        self.theme_display_label = QtWidgets.QLabel(self.preview_area)
        self.theme_display_label.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.theme_display_label.setScaledContents(True)
        self.theme_display_label.setObjectName('theme_display_label')
        self.preview_area_layout.addWidget(self.theme_display_label)
        self.preview_layout.addWidget(self.preview_area)
        self.main_colour_label = QtWidgets.QLabel(self.preview_area)
        self.main_colour_label.setObjectName('main_colour_label')
        self.preview_layout.addWidget(self.main_colour_label)
        self.footer_colour_label = QtWidgets.QLabel(self.preview_area)
        self.footer_colour_label.setObjectName('footer_colour_label')
        self.preview_layout.addWidget(self.footer_colour_label)
        self.button_box = create_button_box(themeLayoutDialog, 'button_box', ['ok'])
        self.preview_layout.addWidget(self.button_box)
        self.retranslate_ui(themeLayoutDialog)

    def retranslate_ui(self, themeLayoutDialog):
        """
        Translate the UI on the fly
        """
        themeLayoutDialog.setWindowTitle(translate('OpenLP.StartTimeForm', 'Theme Layout'))
        self.main_colour_label.setText(translate('OpenLP.StartTimeForm', 'The blue box shows the main area.'))
        self.footer_colour_label.setText(translate('OpenLP.StartTimeForm', 'The red box shows the footer.'))
