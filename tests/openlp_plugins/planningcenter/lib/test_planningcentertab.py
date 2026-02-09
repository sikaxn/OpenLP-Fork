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
Package to test the openlp.plugins.planningcenter.lib.planningcentertab package.
"""
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore, QtTest, QtWidgets

from openlp.core.state import State
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.planningcenter.lib.planningcentertab import PlanningCenterTab
from openlp.plugins.planningcenter.planningcenterplugin import PlanningCenterPlugin


@pytest.fixture
def plugin(registry: Registry, settings: Settings, state: State) -> PlanningCenterPlugin:
    settings.setValue('planningcenter/application_id', 'abc')
    settings.setValue('planningcenter/secret', '123')
    return PlanningCenterPlugin()


@pytest.fixture
def tab(plugin: PlanningCenterPlugin) -> PlanningCenterTab:
    dialog = QtWidgets.QDialog()
    tab = PlanningCenterTab(dialog, 'PlanningCenter')
    tab.setup_ui()
    tab.retranslate_ui()
    tab.load()
    tab.resizeEvent()
    yield tab
    del tab
    del dialog


@patch('openlp.plugins.planningcenter.lib.planningcentertab.PlanningCenterAPI.check_credentials')
@patch('openlp.plugins.planningcenter.lib.planningcentertab.QtWidgets.QMessageBox.warning')
def test_bad_authentication_credentials(mocked_warning: MagicMock, mocked_check_credentials: MagicMock,
                                        tab: PlanningCenterTab):
    """
    Test that the tab can be created and Test authentication clicked for bad application id and secret
    """
    # GIVEN: A PlanningCenterTab Class with bad credentials
    # WHEN: The test button is clicked
    mocked_check_credentials.return_value = ''
    QtTest.QTest.mouseClick(tab.test_credentials_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN: The warning messagebox should be called
    mocked_warning.assert_called_once()


@patch('openlp.plugins.planningcenter.lib.planningcentertab.QtWidgets.QMessageBox.warning')
def test_empty_authentication_credentials(mocked_warning: MagicMock, tab: PlanningCenterTab):
    """
    Test that the tab can be created and Test authentication clicked for missing application id and secret
    """
    # GIVEN: A PlanningCenterTab Class with empty credentials
    # WHEN: The test button is clicked
    tab.application_id_line_edit.setText('')
    tab.secret_line_edit.setText('')
    QtTest.QTest.mouseClick(tab.test_credentials_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN: The warning messagebox should be called
    mocked_warning.assert_called_once()


@patch('openlp.plugins.planningcenter.lib.planningcentertab.PlanningCenterAPI.check_credentials')
@patch('openlp.plugins.planningcenter.lib.planningcentertab.QtWidgets.QMessageBox.information')
def test_good_authentication_credentials(mocked_information: MagicMock, mocked_check_credentials: MagicMock,
                                         tab: PlanningCenterTab):
    """
    Test that the tab can be created and Test authentication clicked for good application id and secret
    """
    # GIVEN: A PlanningCenterTab Class and good credentials
    # WHEN: The test button is clicked
    mocked_check_credentials.return_value = 'good'
    QtTest.QTest.mouseClick(tab.test_credentials_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN: The information messagebox should be called
    mocked_information.assert_called_once()


@patch('openlp.plugins.planningcenter.lib.planningcentertab.PlanningCenterAPI.get_service_type_list')
def test_load_service_type_combobox_items(mocked_get_service_type_list: MagicMock, tab: PlanningCenterTab):
    """
    Test that clicking default service type combo box loads the service types
    """

    # GIVEN: a PlanningCenterTab with a default selected service type and a PlanningCenterAPI
    # that returns three service types
    tab.def_service_type_combobox.clear()
    tab.def_service_type_combobox.addItem("Service Type 2", "2")
    tab.def_service_type_combobox.setCurrentIndex(0)

    mocked_get_service_type_list.return_value = [
        {
            "id": "1",
            "attributes": {"name": "Service Type 1"}
        },
        {
            "id": "2",
            "attributes": {"name": "Service Type 2"}
        },
        {
            "id": "3",
            "attributes": {"name": "Service Type 3"}
        },
    ]

    # WHEN: the service types are loaded
    success = tab.on_load_def_service_type_combobox_items()

    # THEN: the service types should be added to the combo box and the current selected
    # service type should be preserved
    assert success is True
    assert tab.def_service_type_combobox.count() == 4
    assert tab.def_service_type_combobox.currentIndex() == 2
    assert tab.def_service_type_combobox.itemData(tab.def_service_type_combobox.currentIndex()) == "2"


@patch('openlp.plugins.planningcenter.lib.planningcentertab.PlanningCenterAPI.get_service_type_list')
@patch('openlp.plugins.planningcenter.lib.planningcentertab.QtWidgets.QMessageBox.warning')
def test_load_service_type_combobox_items_bad_auth(
    mocked_warning: MagicMock,
    mocked_get_service_type_list: MagicMock,
    tab: PlanningCenterTab
):
    """
    Test that clicking default service type combo box with bad credentials causes warning
    """

    # GIVEN: A PlanningCenterTab and bad credentials
    mocked_get_service_type_list.side_effect = Exception("test exception")

    # WHEN: service types for the default service type combo box are loading
    success = tab.on_load_def_service_type_combobox_items()

    # THEN: a warning should be issued and the function should return False so we
    # can retry loading
    mocked_warning.assert_called_once()
    assert success is False


def test_load_when_service_type_combobox_loaded(settings: Settings, tab: PlanningCenterTab):
    """
    Test that the configured default service type is added to the default service type
    combobox when the tab is loading for the first time.
    """

    # GIVEN: a configured default service type and an empty combo box
    settings.setValue('planningcenter/default_service_type_id', '123')
    settings.setValue('planningcenter/default_service_type_name', 'Test Service Type')

    tab.def_service_type_combobox.clear()

    # WHEN: the settings tab is loaded
    tab.load()

    # THEN: the combo box should have one item with the configured default service type
    assert tab.def_service_type_combobox.count() == 1
    assert tab.def_service_type_combobox.itemData(tab.def_service_type_combobox.currentIndex()) == '123'
    assert tab.def_service_type_combobox.itemText(tab.def_service_type_combobox.currentIndex()) == 'Test Service Type'


def test_load_when_service_type_combobox_not_loaded(settings: Settings, tab: PlanningCenterTab):
    """
    Test that the correct service type is selected when the tab is loading and the
    default service type combobox has previously been loaded.
    """

    # GIVEN: a configured default service type and a loaded combo box
    tab.def_service_type_combobox.clear()
    tab.def_service_type_combobox.addItem('-- none --', '')
    tab.def_service_type_combobox.addItem('ServiceType1', '1')
    tab.def_service_type_combobox.addItem('ServiceType2', '2')
    tab.def_service_type_combobox.addItem('ServiceType3', '3')

    settings.setValue('planningcenter/default_service_type_id', '2')
    settings.setValue('planningcenter/default_service_type_name', 'ServiceType2')

    # WHEN: the settings tab is loaded
    tab.load()

    # THEN: the configured default service type should be selected
    assert tab.def_service_type_combobox.count() == 4
    assert tab.def_service_type_combobox.currentIndex() == 2
    assert tab.def_service_type_combobox.itemData(tab.def_service_type_combobox.currentIndex()) == '2'
    assert tab.def_service_type_combobox.itemText(tab.def_service_type_combobox.currentIndex()) == 'ServiceType2'


def test_save(settings: Settings, tab: PlanningCenterTab):
    """
    Test that credentials are saved in settings when the save function is called
    """
    # GIVEN: A PlanningCenterTab Class
    # WHEN: fields are set to something and the save function is called
    tab.application_id_line_edit.setText('planningcenter')
    tab.secret_line_edit.setText('woohoo')

    tab.def_service_type_combobox.clear()
    tab.def_service_type_combobox.addItem('Service Type', '1234')
    tab.def_service_type_combobox.setCurrentIndex(0)

    tab.save()

    # THEN: The settings version of application_id and secret should reflect the new values
    assert settings.value('planningcenter/application_id') == 'planningcenter'
    assert settings.value('planningcenter/secret') == 'woohoo'
    assert settings.value('planningcenter/default_service_type_name') == 'Service Type'
    assert settings.value('planningcenter/default_service_type_id') == '1234'
