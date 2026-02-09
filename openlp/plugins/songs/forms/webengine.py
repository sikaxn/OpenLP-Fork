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
Subclass of QWebEngineView used to block js messages; Useful for public sites
where we have no control on the code run in the webpage, and do not want to
see the error messages.
"""
from PySide6 import QtWebEngineWidgets, QtWebEngineCore


class WebEnginePage(QtWebEngineCore.QWebEnginePage):
    """
    A custom WebEngine page to capture Javascript console logging
    """
    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        """
        Override the parent method in order to hide the ccli site messages
        """
        pass


class WebEngineView(QtWebEngineWidgets.QWebEngineView):
    """
    A sub-classed QWebEngineView
    """

    def __init__(self, parent=None):
        """
        Constructor
        """
        super(WebEngineView, self).__init__(parent)
        self.setPage(WebEnginePage(self))
