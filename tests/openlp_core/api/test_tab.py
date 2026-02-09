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
This module contains tests for the lib submodule of the Remotes plugin.
"""
import hashlib
import pytest
import re
from unittest.mock import MagicMock, patch

from PySide6 import QtWidgets

from openlp.core.api.tab import ApiTab
from openlp.core.common import get_network_interfaces
from openlp.core.common.registry import Registry

ZERO_URL = '0.0.0.0'


@pytest.fixture(scope="module")
def mocked_get_installed_version():
    setup_patcher = patch('openlp.core.api.tab.get_installed_version')
    mocked_setup_patcher = setup_patcher.start()
    mocked_setup_patcher.return_value = None
    yield mocked_setup_patcher
    setup_patcher.stop()


@pytest.fixture
def api_tab_instantiate(mocked_get_installed_version, settings):
    forms = []
    parent = QtWidgets.QMainWindow()

    def _create_api_tab():
        nonlocal forms, parent  # noqa: F824
        Registry().set_flag('website_version', '00-00-0000')
        Registry().set_flag('no_web_server', False)
        form = ApiTab(parent)
        forms.append(form)
        return form

    yield _create_api_tab
    del parent
    for form in forms:
        del form
    mocked_get_installed_version.return_value = None


@pytest.fixture
def api_tab(api_tab_instantiate):
    yield api_tab_instantiate()


def test_get_ip_address_default(api_tab):
    """
    Test the get_ip_address function with ZERO_URL
    """
    # GIVEN: list of local IP addresses for this machine
    ip_addresses = []
    interfaces = get_network_interfaces()
    for _, interface in interfaces.items():
        ip_addresses.append(interface['ip'])

    # WHEN: the default ip address is given
    ip_address = api_tab.get_ip_address(ZERO_URL)

    # THEN: the default ip address will be returned
    assert re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_address), \
        'The return value should be a valid ip address'
    assert ip_address in ip_addresses, 'The return address should be in the list of local IP addresses'


def test_get_ip_address_with_ip(api_tab):
    """
    Test the get_ip_address function with given ip address
    """
    # GIVEN: An ip address
    given_ip = '192.168.1.1'

    # WHEN: the default ip address is given
    ip_address = api_tab.get_ip_address(given_ip)

    # THEN: the default ip address will be returned
    assert ip_address == given_ip, 'The return value should be %s' % given_ip


def test_set_urls(api_tab):
    """
    Test the set_url function to generate correct url links
    """
    # GIVEN: An ip address
    api_tab.address_edit.setText('192.168.1.1')
    # WHEN: the urls are generated
    api_tab.set_urls()
    # THEN: the following links are returned
    assert api_tab.remote_url.text() == "<a href=\"http://192.168.1.1:4316/\">http://192.168.1.1:4316/</a>", \
        'The return value should be a fully formed link'
    assert api_tab.stage_url.text() == \
        "<a href=\"http://192.168.1.1:4316/stage\">http://192.168.1.1:4316/stage</a>", \
        'The return value should be a fully formed stage link'
    assert api_tab.live_url.text() == \
        "<a href=\"http://192.168.1.1:4316/main\">http://192.168.1.1:4316/main</a>", \
        'The return value should be a fully formed main link'
    assert api_tab.chords_url.text() == \
        "<a href=\"http://192.168.1.1:4316/chords\">http://192.168.1.1:4316/chords</a>", \
        'The return value should be a fully formed chords link'
    assert hashlib.sha256(api_tab.app_qr_code_label.text().encode()).hexdigest() \
           == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Incorrect QR Code generated'


def test_address_revert_button_clicked(api_tab, settings):
    """
    Test the IP revert function works
    """
    # GIVEN: The ip address text set to a non default value
    api_tab.address_edit.setText('not the default')
    # WHEN: address_revert_button_clicked is called
    api_tab.address_revert_button_clicked()
    # THEN: The text should have been changed to the default value
    assert api_tab.address_edit.text() == settings.get_default_value('api/ip address')


@patch('openlp.core.api.tab.QtWidgets.QMessageBox.information')
def test_save(mocked_information, api_tab, registry, settings):
    """
    Test the save method works correctly
    """
    # GIVEN: Various settings are set on the form and a mocked settings form
    mocked_settings_form = MagicMock()
    registry.remove('settings_form')
    registry.register('settings_form', mocked_settings_form)
    settings.setValue('api/ip address', '0.0.0.0')
    api_tab.address_edit.setText('192.168.1.1')
    api_tab.twelve_hour = True
    api_tab.thumbnails = True
    api_tab.user_login_group_box.setChecked(True)
    api_tab.user_id.setText('user id thing')
    api_tab.password.setText('user password thing')

    # WHEN: save is called
    api_tab.save()

    # THEN: The text should have been changed to the default value
    mocked_information.assert_called_once_with(api_tab, 'Restart Required',
                                               'This change will only take effect once OpenLP has been restarted.')
    mocked_settings_form.register_post_process.assert_called_once_with('remotes_config_updated')
    assert settings.value('api/twelve hour') is True
    assert settings.value('api/thumbnails') is True
    assert settings.value('api/authentication enabled') is True
    assert settings.value('api/user id') == 'user id thing'
    assert settings.value('api/password') == 'user password thing'


def test_available_version_property_get_none(api_tab):
    """Test that the available version property is None on init"""
    # GIVEN: An uninitialised API tab

    # WHEN: the available version is GET'ed
    result = api_tab.available_version

    # THEN: The result is None
    assert result is None


def test_available_version_property_set(api_tab):
    """Test that the available version property is set correctly"""
    # GIVEN: An uninitialised API tab
    available_version = '0.9.7'

    # WHEN: the available version is SET
    api_tab.available_version = available_version

    # THEN: The internal value should be set, and the right methods should have been called
    assert api_tab._available_version == available_version
    assert api_tab.available_version_value.text() == available_version


def test_available_version_property_set_none(api_tab):
    """Test that the available version property is set correctly"""
    # GIVEN: An uninitialised API tab
    available_version = None

    # WHEN: the available version is SET
    api_tab.available_version = available_version

    # THEN: The internal value should be set, and the right methods should have been called
    assert api_tab._available_version == available_version
    assert api_tab.available_version_value.text() == '(unknown)'


def test_installed_version_property_get_none(mocked_get_installed_version, api_tab_instantiate, settings):
    """Test that the installed version property is None on init"""
    # GIVEN: An uninitialised API tab
    mocked_get_installed_version.return_value = None
    settings.setValue('api/download_version', None)
    api_tab = api_tab_instantiate()

    # WHEN: the installed version is GET'ed
    result = api_tab.installed_version

    # THEN: The result is None
    assert result is None


def test_installed_version_property_set(api_tab):
    """Test that the installed version property is set correctly"""
    # GIVEN: An uninitialised API tab
    installed_version = '0.9.7'

    # WHEN: the installed version is SET
    api_tab.installed_version = installed_version

    # THEN: The internal value should be set, and the right methods should have been called
    assert api_tab._installed_version == installed_version
    assert api_tab.installed_version_value.text() == installed_version


def test_installed_version_property_set_none(api_tab):
    """Test that the installed version property is set correctly"""
    # GIVEN: An uninitialised API tab
    installed_version = None

    # WHEN: the installed version is SET
    api_tab.installed_version = installed_version

    # THEN: The internal value should be set, and the right methods should have been called
    assert api_tab._installed_version == installed_version
    assert api_tab.installed_version_value.text() == '(not installed)'


def test_validate_available_version(api_tab):
    """Test that the validate_available_version() method sets the label correctly"""
    # GIVEN: An uninitialised API tab

    # WHEN: validate_available_version() is run
    api_tab.validate_available_version()

    # THEN: The label should say "(unknown)"
    assert api_tab.available_version_value.text() == '(unknown)'


@patch('openlp.core.api.tab.is_thread_finished')
def test_set_server_states_up(mock_is_thread_finished, registry, settings, api_tab):
    """Test getting the server states when the servers are up"""
    # GIVEN: An API tab and some mocks
    mock_is_thread_finished.return_value = False

    # WHEN: set_server_states() is called
    api_tab.set_server_states()

    # THEN: The servers should all be "up"
    assert api_tab.server_http_state.text() == 'Active'
    assert api_tab.server_websocket_state.text() == 'Active'


@patch('openlp.core.api.tab.is_thread_finished')
def test_set_server_states_disabled(mock_is_thread_finished, registry, settings, api_tab):
    """Test getting the server states when the servers are disabled"""
    # GIVEN: An API tab and some mocks
    mock_is_thread_finished.return_value = True
    registry.set_flag('no_web_server', True)

    # WHEN: set_server_states() is called
    api_tab.set_server_states()

    # THEN: The servers should all be "up"
    assert api_tab.server_http_state.text() == 'Disabled'
    assert api_tab.server_websocket_state.text() == 'Disabled'


@patch('openlp.core.api.tab.is_thread_finished')
def test_set_server_states_down(mock_is_thread_finished, registry, settings, api_tab):
    """Test getting the server states when the servers are down"""
    # GIVEN: An API tab and some mocks
    mock_is_thread_finished.return_value = True
    registry.set_flag('no_web_server', False)

    # WHEN: set_server_states() is called
    api_tab.set_server_states()

    # THEN: The servers should all be "up"
    assert api_tab.server_http_state.text() == 'Failed'
    assert api_tab.server_websocket_state.text() == 'Failed'


@patch('openlp.core.api.tab.download_version_info')
def test_on_check_for_updates_button_clicked(mocked_download_version_info, mocked_qapp, registry, settings, api_tab):
    """Test that the correct methods are called when the Check for Updates button is clicked"""
    # GIVEN: An API tab and a couple of mocks
    mocked_download_version_info.return_value = {'latest': {'version': '0.9.5'}}
    mocked_main_window = MagicMock()
    registry.register('main_window', mocked_main_window)
    registry.remove('application')
    registry.register('application', mocked_qapp)

    # WHEN: The Check for Updates button is clicked
    with patch.object(api_tab, 'can_enable_install_button') as mocked_can_enable_install_button:
        mocked_can_enable_install_button.return_value = True
        api_tab.on_check_for_updates_button_clicked()
        assert mocked_can_enable_install_button.call_count == 2

    # THEN: The correct methods were called
    mocked_qapp.set_busy_cursor.assert_called_once()
    assert mocked_qapp.process_events.call_count == 4
    mocked_qapp.set_normal_cursor.assert_called_once()
    mocked_download_version_info.assert_called_once()
    mocked_main_window.information_message.assert_called_once_with(
        'New version available!', 'There\'s a new version of the web remote available.'
    )
    assert api_tab.available_version == '0.9.5'


@patch('openlp.core.api.tab.download_version_info')
def test_on_check_for_updates_error(mocked_download_version_info, mocked_qapp, registry, settings, api_tab):
    """Test that an error message is shown when the remote version cannot be downloaded"""
    # GIVEN: An API tab and a couple of mocks
    mocked_download_version_info.return_value = None
    mocked_main_window = MagicMock()
    registry.register('main_window', mocked_main_window)
    registry.remove('application')
    registry.register('application', mocked_qapp)

    # WHEN: The Check for Updates button is clicked
    with patch.object(api_tab, 'can_enable_install_button') as mocked_can_enable_install_button:
        mocked_can_enable_install_button.return_value = False
        api_tab.on_check_for_updates_button_clicked()
        assert mocked_can_enable_install_button.call_count == 1

    # THEN: The correct methods were called
    mocked_qapp.set_busy_cursor.assert_called_once()
    assert mocked_qapp.process_events.call_count == 4
    mocked_qapp.set_normal_cursor.assert_called_once()
    mocked_download_version_info.assert_called_once()
    mocked_main_window.error_message.assert_called_once_with(
        'Error fetching version', 'There was a problem fetching the latest version of the remote'
    )
    mocked_main_window.information_message.assert_not_called()
    assert api_tab.available_version is None


@patch('openlp.core.api.tab.DownloadProgressDialog')
@patch('openlp.core.api.tab.download_and_install')
@patch('openlp.core.api.tab.sleep')
def test_on_install_button_clicked(mocked_sleep, mocked_download_and_install, MockDownloadProgressDialog,
                                   mocked_qapp, registry, settings, api_tab):
    """Test that the correct methods are called when the Check for Updates button is clicked"""
    # GIVEN: An API tab and a couple of mocks
    mocked_download_and_install.return_value = '0.9.6'
    mocked_progress = MagicMock()
    MockDownloadProgressDialog.return_value = mocked_progress
    registry.remove('application')
    registry.register('application', mocked_qapp)

    # WHEN: The Check for Updates button is clicked
    api_tab.on_install_button_clicked()

    # THEN: The correct methods were called
    assert mocked_qapp.process_events.call_count == 3
    MockDownloadProgressDialog.assert_called_once_with(api_tab, mocked_qapp)
    mocked_progress.show.assert_called_once()
    mocked_progress.close.assert_called_once()
    mocked_download_and_install.assert_called_once_with(mocked_progress)
    assert api_tab.installed_version == '0.9.6'
    assert settings.value('api/download version') == '0.9.6'
