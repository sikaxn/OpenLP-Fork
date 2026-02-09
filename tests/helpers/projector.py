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
Help classes/functions for PJLink Projector tests
"""

from unittest.mock import MagicMock
from PySide6 import QtNetwork

from openlp.core.projectors.constants import S_NOT_CONNECTED, S_OFF, S_OK
from openlp.core.projectors.db import Projector
from tests.resources.projector.data import TEST1_DATA


class FakeProjector(object):
    """
    Helper test class
    """
    def __init__(self, port=4352, name="Faker"):
        self.link = self
        self.entry = self
        self.name = name
        self.pin = None
        self.port = port


class FakePJLinkUDP(object):
    """
    Helper test class
    """
    def __init__(self, *args, **kwargs):
        pass

    def check_settings(self, *args, **kwargs):
        pass


class FakePJLink(object):
    """
    Helper class with signals and methods mocked
    """
    def __init__(self, projector=Projector(**TEST1_DATA), *args, **kwargs):
        # Signal mocks
        self.changeStatus = MagicMock()  # Deprecated use projectorChangeStatus
        self.projectorChangeStatus = MagicMock()
        self.projectorStatus = MagicMock()
        self.projectorAuthentication = MagicMock()
        self.projectorNoAuthentication = MagicMock()
        self.projectorReceivedData = MagicMock()
        self.projectorUpdateIcons = MagicMock()

        # Method mocks
        self.change_status = MagicMock()
        self.connect_to_host = MagicMock()
        self.disconnect_from_host = MagicMock()
        self.poll_timer = MagicMock()
        self.set_power_off = MagicMock()
        self.set_power_on = MagicMock()
        self.set_shutter_closed = MagicMock()
        self.set_shutter_open = MagicMock()
        self.socket_timer = MagicMock()
        self.state = MagicMock()
        self.status_timer = MagicMock()
        self.status_timer_add = MagicMock()
        self.status_timer_delete = MagicMock()

        # Some tests that may include what it thinks are ProjectorItem()
        # If ProjectorItem() is called, will probably overwrite these - OK
        self.link = self
        self.pjlink = self

        # Normal entries from PJLink
        self.db = projector
        self.entry = self.db  # Deprecated use self.db
        self.ip = self.db.ip
        self.qhost = QtNetwork.QHostAddress(self.ip)
        self.location = self.db.location
        self.mac_adx = self.db.mac_adx
        self.name = self.db.name
        self.notes = self.db.notes
        self.pin = self.db.pin
        self.port = int(self.db.port)
        self.pjlink_class = "1" if self.db.pjlink_class is None else self.db.pjlink_class
        self.poll_time = 20000
        self.socket_timeout = 5000
        self.no_poll = True
        self.status_connect = S_NOT_CONNECTED
        self.last_command = ''
        self.projector_status = S_NOT_CONNECTED
        self.error_status = S_OK
        self.send_queue = []
        self.priority_queue = []
        self.send_busy = False
        self.status_timer_checks = {}  # Keep track of events for the status timer

        # reset_information attributes
        self.fan = None  # ERST
        self.filter_time = None  # FILT
        self.lamp = None  # LAMP
        self.mac_adx_received = None  # ACKN
        self.manufacturer = None  # INF1
        self.model = None  # INF2
        self.model_filter = None  # RFIL
        self.model_lamp = None  # RLMP
        self.mute = None  # AVMT
        self.other_info = None  # INFO
        self.pjlink_name = None  # NAME
        self.power = S_OFF  # POWR
        self.projector_errors = {}  # Full ERST errors
        self.serial_no = None  # SNUM
        self.serial_no_received = None
        self.sw_version = None  # SVER
        self.sw_version_received = None
        self.shutter = None  # AVMT
        self.source_available = None  # INST
        self.source = None  # INPT
