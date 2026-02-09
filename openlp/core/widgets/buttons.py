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
Provide a custom widget based on QPushButton for the selection of colors
"""
from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import translate


class ColorButton(QtWidgets.QPushButton):
    """
    Subclasses QPushbutton to create a "Color Chooser" button
    """

    colorChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        """
        Initialise the ColorButton
        """
        super().__init__(parent)
        self.parent = parent
        self._setup()

    def _setup(self):
        """Set up the object. This method is used to make the class easily tested"""
        self.change_color('#ffffff')
        self.setToolTip(translate('OpenLP.ColorButton', 'Click to select a color.'))
        self.clicked.connect(self.on_clicked)

    def change_color(self, color):
        """
        Sets the _color variable and the background color.

        :param color:  String representation of a hexadecimal color
        """
        self._color = color
        self.setStyleSheet('background-color: %s' % color)

    @property
    def color(self):
        """
        Property method to return the color variable

        :return:  String representation of a hexadecimal color
        """
        return self._color

    @color.setter
    def color(self, color):
        """
        Property setter to change the instance color

        :param color:  String representation of a hexadecimal color
        """
        self.change_color(color)

    def on_clicked(self):
        """
        Handle the PushButton clicked signal, showing the ColorDialog and validating the input
        """
        new_color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._color), self.parent)
        if new_color.isValid() and self._color != new_color.name():
            self.change_color(new_color.name())
            self.colorChanged.emit(new_color.name())
