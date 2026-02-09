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
Test projector settings tab UI
"""

import logging

import openlp.core.projectors.tab

from PySide6 import QtWidgets  # noqa
from unittest.mock import MagicMock

from openlp.core.projectors.tab import ProjectorTab
from tests.resources.projector.data import TEST1_DATA, TEST2_DATA

test_module = openlp.core.projectors.tab.__name__


def test_load_settings(settings):
    """
    Test ProjectorTab loads settings
    """
    # GIVEN: Test environmnet
    # Test settings
    t_connect_on_start = not settings.get_default_value('projector/connect on start')
    t_socket_timeout = 10  # Range 2-10 default 5
    t_poll_time = 60  # Range 5-60 default 20
    t_source_dialog_type = 1
    t_udp_broadcast_listen = not settings.get_default_value('projector/udp broadcast listen')
    t_lkup = not settings.get_default_value('projector/connect when LKUP received')

    # Ensure default settings loaded before we change them
    t_tab = ProjectorTab(parent=None)
    t_tab.connect_on_startup.setChecked(settings.get_default_value('projector/connect on start'))
    t_tab.socket_timeout_spin_box.setValue(settings.get_default_value('projector/socket timeout'))
    t_tab.socket_poll_spin_box.setValue(settings.get_default_value('projector/poll time'))
    t_tab.dialog_type_combo_box.setCurrentIndex(settings.get_default_value('projector/source dialog type'))
    t_tab.udp_broadcast_listen.setChecked(settings.get_default_value('projector/udp broadcast listen'))
    t_tab.connect_on_linkup.setChecked(settings.get_default_value('projector/connect when LKUP received'))

    # WHEN: Settings changed
    settings.setValue('projector/connect on start', t_connect_on_start)
    settings.setValue('projector/socket timeout', t_socket_timeout)
    settings.setValue('projector/poll time', t_poll_time)
    settings.setValue('projector/source dialog type', t_source_dialog_type)
    settings.setValue('projector/udp broadcast listen', t_udp_broadcast_listen)
    settings.setValue('projector/connect when LKUP received', t_lkup)
    t_tab.load()

    # THEN: new values should reflect changed settings
    assert t_tab.connect_on_startup.isChecked() == t_connect_on_start, 'connect on start should have changed'
    assert t_tab.socket_timeout_spin_box.value() == t_socket_timeout, 'socket timeout should have changed'
    assert t_tab.socket_poll_spin_box.value() == t_poll_time, 'poll time should have changed'
    assert t_tab.dialog_type_combo_box.currentIndex() == t_source_dialog_type, 'source dialog should have changed'
    assert t_tab.connect_on_linkup.isChecked() == t_lkup, 'LKUP should have changed'
    assert t_tab.udp_broadcast_listen.isChecked() == t_udp_broadcast_listen, 'broadcast listen should have changed'


def test_save_settings(settings):
    """
    Test ProjectorTab saves settings
    """
    # GIVEN: Test environmnet
    # Test settings
    t_connect_on_start = not settings.get_default_value('projector/connect on start')
    t_socket_timeout = 10  # Range 2-10 default 5
    t_poll_time = 60  # Range 5-60 default 20
    t_source_dialog_type = 1
    t_udp_broadcast_listen = not settings.get_default_value('projector/udp broadcast listen')
    t_lkup = not settings.get_default_value('projector/connect when LKUP received')

    t_tab = ProjectorTab(parent=None)
    t_tab.connect_on_startup.setChecked(t_connect_on_start)
    t_tab.socket_timeout_spin_box.setValue(t_socket_timeout)
    t_tab.socket_poll_spin_box.setValue(t_poll_time)
    t_tab.dialog_type_combo_box.setCurrentIndex(t_source_dialog_type)
    t_tab.udp_broadcast_listen.setChecked(t_udp_broadcast_listen)
    t_tab.connect_on_linkup.setChecked(t_lkup)

    # WHEN: save settings called
    t_tab.save()

    # THEN: Saved settings should match the new values
    assert settings.value('projector/connect on start') == t_connect_on_start, 'connect on start should have changed'
    assert settings.value('projector/socket timeout') == t_socket_timeout, 'socket timeout should have changed'
    assert settings.value('projector/poll time') == t_poll_time, 'poll time should have changed'
    assert settings.value('projector/source dialog type') == t_source_dialog_type, 'dialog type should have changed'
    assert settings.value('projector/udp broadcast listen') == t_udp_broadcast_listen, \
        'udp broadcast listen should have changed'
    assert settings.value('projector/connect when LKUP received') == t_lkup, 'LKUP should have changed'


def test_dialog_type_changed(settings):
    """
    Test dialog_type is updated by dialog_type_combo_box
    """
    # TODO: Check if ProjectorTab.dialog_type attribute is actually used anywhere
    # GIVEN: Test setup
    t_tab = ProjectorTab(parent=None)

    # WHEN: Index changed
    t_tab.dialog_type_combo_box.setCurrentIndex(1)
    t_tab.on_dialog_type_combo_box_changed()

    # THEN: dialog_type should be changed
    assert t_tab.dialog_type == 1, 'dialog_type should have changed'


def test_add_udp_listener(settings, caplog):
    """
    Test UDP callback registered
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_mock1 = MagicMock()
    t_udp1 = {'port': TEST1_DATA['port'],
              'callback': t_mock1}
    logs = [(test_module, logging.DEBUG,
             f'PJLinkSettings: new callback list: dict_keys([\'{t_udp1["port"]}\'])')]

    t_tab = ProjectorTab(parent=None)
    assert t_tab.udp_listeners == {}

    # WHEN: Called
    caplog.clear()
    t_tab.add_udp_listener(**t_udp1)

    # THEN: Callback registered
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert t_udp1['port'] in t_tab.udp_listeners, 'Listener port not added'
    assert t_tab.udp_listeners[t_udp1['port']] == t_mock1, 'Callback not registered properly'


def test_add_udp_listener_existing(settings, caplog):
    """
    Test UDP callback registered
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_mock1 = MagicMock()
    t_udp1 = {'port': TEST1_DATA['port'],
              'callback': t_mock1}
    logs = [(test_module, logging.WARNING,
             f'Port {t_udp1["port"]} already in list - not adding')]
    t_tab = ProjectorTab(parent=None)
    assert t_tab.udp_listeners == {}
    t_tab.add_udp_listener(**t_udp1)

    # WHEN: Called
    caplog.clear()
    t_tab.add_udp_listener(**t_udp1)

    # THEN: Callback registered
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_tab.udp_listeners) == 1, 'Listeners dictionary changed'


def test_remove_udp_listener(settings, caplog):
    """
    Test udp listener callback removed
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_mock1 = MagicMock()
    t_mock2 = MagicMock()
    t_udp1 = {'port': TEST1_DATA['port'],
              'callback': t_mock1}
    t_udp2 = {'port': TEST2_DATA['port'],
              'callback': t_mock2}
    logs = [(test_module, logging.DEBUG,
             f'PJLinkSettings: new callback list: dict_keys([\'{t_udp1["port"]}\'])')]

    t_tab = ProjectorTab(parent=None)
    assert t_tab.udp_listeners == {}
    t_tab.add_udp_listener(**t_udp1)
    t_tab.add_udp_listener(**t_udp2)

    # WHEN: Called
    caplog.clear()
    t_tab.remove_udp_listener(port=t_udp2['port'])

    # THEN: Listener removed and log entry made
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_tab.udp_listeners) == 1, 'Listener not removed'


def test_remove_udp_listener_not_there(settings, caplog):
    """
    Test udp listener callback removed
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_mock1 = MagicMock()
    t_mock2 = MagicMock()
    t_udp1 = {'port': TEST1_DATA['port'],
              'callback': t_mock1}
    t_udp2 = {'port': TEST2_DATA['port'],
              'callback': t_mock2}
    logs = [(test_module, logging.WARNING,
             f'Port {t_udp2["port"]} not in list - ignoring')]

    t_tab = ProjectorTab(parent=None)
    assert t_tab.udp_listeners == {}
    t_tab.add_udp_listener(**t_udp1)

    # WHEN: Called
    caplog.clear()
    t_tab.remove_udp_listener(port=t_udp2['port'])

    # THEN: Listener removed and log entry made
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_tab.udp_listeners) == 1, 'Listener not removed'
