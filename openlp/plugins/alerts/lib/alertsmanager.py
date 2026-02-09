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
The :mod:`~openlp.plugins.alerts.lib.alertsmanager` module contains the part of the plugin which manages storing and
displaying of alerts.
"""
import json

from PySide6 import QtCore, QtGui

from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import Registry, RegistryBase
from openlp.core.display.screens import ScreenList


class AlertsManager(QtCore.QObject, RegistryBase, LogMixin, RegistryProperties):
    """
    AlertsManager manages the settings of Alerts.
    """
    alerts_text = QtCore.Signal(list)

    def __init__(self, parent):
        super(AlertsManager, self).__init__()
        Registry().register_function('alerts_text', self.alert_text)
        self.alerts_text.connect(self.alert_text)

    def alert_text(self, message):
        """
        Called via a alerts_text event. Message is single element array containing text.

        :param message: The message text to be displayed
        """
        if message:
            text = message[0]
            # remove line breaks as these crash javascript code on display
            while '\n' in text:
                text = text.replace('\n', ' ')
            self.display_alert(text)

    def display_alert(self, text=''):
        """
        Called from the Alert Tab to display an alert.

        :param text: The text to display
        """
        self.log_debug(f'display alert called "{text}"')
        if not text:
            return
        if len(ScreenList()) == 1 and not self.settings.value('core/display on monitor'):
            return
        # Put alert settings together in dict that will be passed to Display in Javascript
        alert_settings = {
            'backgroundColor': self._hex_to_rgb(QtGui.QColor(self.settings.value('alerts/background color'))),
            'location': self.settings.value('alerts/location'),
            'fontFace': self.settings.value('alerts/font face'),
            'fontSize': self.settings.value('alerts/font size'),
            'fontColor': self._hex_to_rgb(QtGui.QColor(self.settings.value('alerts/font color'))),
            'timeout': self.settings.value('alerts/timeout'),
            'repeat': self.settings.value('alerts/repeat'),
            'scroll': self.settings.value('alerts/scroll')
        }
        self.live_controller.display.alert(text, json.dumps(alert_settings))

    def _hex_to_rgb(self, rgb_values):
        """
        Converts rgb color values from QColor to rgb string

        :param rgb_values:
        :return: rgb color string
        :rtype: string
        """
        return "rgb(" + str(rgb_values.red()) + ", " + str(rgb_values.green()) + ", " + str(rgb_values.blue()) + ")"
