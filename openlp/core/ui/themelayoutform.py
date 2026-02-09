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
The form layout
"""
from PySide6 import QtCore, QtWidgets

from .themelayoutdialog import Ui_ThemeLayoutDialog


class ThemeLayoutForm(QtWidgets.QDialog, Ui_ThemeLayoutDialog):
    """
    The exception dialog
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super(ThemeLayoutForm, self).__init__(parent)
        self.setup_ui(self)

    def exec(self, image):
        """
        Run the Dialog with correct heading.
        """
        pixmap = image.scaledToHeight(400, QtCore.Qt.TransformationMode.SmoothTransformation)
        pixmap.setDevicePixelRatio(self.theme_display_label.devicePixelRatio())
        self.theme_display_label.setPixmap(pixmap)
        display_aspect_ratio = float(image.width()) / image.height()
        self.theme_display_label.setFixedSize(400, int(400 / display_aspect_ratio))
        return QtWidgets.QDialog.exec(self)
