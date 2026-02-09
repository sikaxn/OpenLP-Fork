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
Package to test the openlp.core.version package.
"""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import ConnectionError

from openlp.core.version import VersionWorker, check_for_update, get_version, update_check_date


def test_worker_init():
    """
    Test the VersionWorker constructor
    """
    # GIVEN: A last check date and a current version
    last_check_date = '1970-01-01'
    current_version = '2.0'

    # WHEN: A worker is created
    worker = VersionWorker(last_check_date, current_version)

    # THEN: The correct attributes should have been set
    assert worker.last_check_date == last_check_date
    assert worker.current_version == current_version


@patch('openlp.core.version.platform')
@patch('openlp.core.version.get_web_page')
def test_worker_start(mock_get_web_page, mock_platform):
    """
    Test the VersionWorkder.start() method
    """
    # GIVEN: A last check date, current version, and an instance of worker
    last_check_date = '1970-01-01'
    current_version = {'full': '2.0', 'version': '2.0', 'build': None}
    mock_platform.system.return_value = 'Linux'
    mock_platform.release.return_value = '4.12.0-1-amd64'
    mock_get_web_page.return_value = '2.4.6'
    worker = VersionWorker(last_check_date, current_version)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: The check completes and the signal is emitted
    expected_download_url = 'https://get.openlp.org/versions/version.txt'
    expected_headers = {'User-Agent': 'OpenLP/2.0 Linux/4.12.0-1-amd64; '}
    mock_get_web_page.assert_called_once_with(expected_download_url, headers=expected_headers)
    mock_new_version.emit.assert_called_once_with('2.4.6')
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.platform')
@patch('openlp.core.version.get_web_page')
def test_worker_start_fail(mock_get_web_page, mock_platform):
    """
    Test the Version Workder.start() method with no response
    """
    # GIVEN: A last check date, current version, and an instance of worker
    last_check_date = '1970-01-01'
    current_version = {'full': '2.0', 'version': '2.0', 'build': None}
    mock_platform.system.return_value = 'Linux'
    mock_platform.release.return_value = '4.12.0-1-amd64'
    mock_get_web_page.return_value = None
    worker = VersionWorker(last_check_date, current_version)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: The check completes and the signal is emitted
    expected_download_url = 'https://get.openlp.org/versions/version.txt'
    expected_headers = {'User-Agent': 'OpenLP/2.0 Linux/4.12.0-1-amd64; '}
    mock_get_web_page.assert_called_once_with(expected_download_url, headers=expected_headers)
    mock_new_version.emit.assert_not_called()
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.platform')
@patch('openlp.core.version.get_web_page')
def test_worker_start_dev_version(mock_get_web_page, mock_platform):
    """
    Test the VersionWorkder.start() method for dev versions
    """
    # GIVEN: A last check date, current version, and an instance of worker
    last_check_date = '1970-01-01'
    current_version = {'full': '2.1.3', 'version': '2.1.3', 'build': None}
    mock_platform.system.return_value = 'Linux'
    mock_platform.release.return_value = '4.12.0-1-amd64'
    mock_get_web_page.return_value = '2.4.6'
    worker = VersionWorker(last_check_date, current_version)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: The check completes and the signal is emitted
    expected_download_url = 'https://get.openlp.org/versions/dev_version.txt'
    expected_headers = {'User-Agent': 'OpenLP/2.1.3 Linux/4.12.0-1-amd64; '}
    mock_get_web_page.assert_called_once_with(expected_download_url, headers=expected_headers)
    mock_new_version.emit.assert_called_once_with('2.4.6')
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.platform')
@patch('openlp.core.version.get_web_page')
def test_worker_start_nightly_version(mock_get_web_page, mock_platform):
    """
    Test the VersionWorkder.start() method for nightlies
    """
    # GIVEN: A last check date, current version, and an instance of worker
    last_check_date = '1970-01-01'
    current_version = {'full': '2.1.0+git2345', 'version': '2.1', 'build': '2345'}
    mock_platform.system.return_value = 'Linux'
    mock_platform.release.return_value = '4.12.0-1-amd64'
    mock_get_web_page.return_value = '2.4.6'
    worker = VersionWorker(last_check_date, current_version)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: The check completes and the signal is emitted
    expected_download_url = 'https://get.openlp.org/versions/nightly_version.txt'
    expected_headers = {'User-Agent': 'OpenLP/2.1.0+git2345 Linux/4.12.0-1-amd64; '}
    mock_get_web_page.assert_called_once_with(expected_download_url, headers=expected_headers)
    mock_new_version.emit.assert_called_once_with('2.4.6')
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.platform')
@patch('openlp.core.version.get_web_page')
def test_worker_empty_response(mock_get_web_page, mock_platform):
    """
    Test the VersionWorkder.start() method for empty responses
    """
    # GIVEN: A last check date, current version, and an instance of worker
    last_check_date = '1970-01-01'
    current_version = {'full': '2.1+git2345', 'version': '2.1', 'build': '2345'}
    mock_platform.system.return_value = 'Linux'
    mock_platform.release.return_value = '4.12.0-1-amd64'
    mock_get_web_page.return_value = '\n'
    worker = VersionWorker(last_check_date, current_version)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: The check completes and the signal is emitted
    expected_download_url = 'https://get.openlp.org/versions/nightly_version.txt'
    expected_headers = {'User-Agent': 'OpenLP/2.1+git2345 Linux/4.12.0-1-amd64; '}
    mock_get_web_page.assert_called_once_with(expected_download_url, headers=expected_headers)
    assert mock_new_version.emit.call_count == 0
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.platform')
@patch('openlp.core.version.get_web_page')
def test_worker_start_connection_error(mock_get_web_page, mock_platform):
    """
    Test the VersionWorkder.start() method when a ConnectionError happens
    """
    # GIVEN: A last check date, current version, and an instance of worker
    last_check_date = '1970-01-01'
    current_version = {'full': '2.0', 'version': '2.0', 'build': None}
    mock_platform.system.return_value = 'Linux'
    mock_platform.release.return_value = '4.12.0-1-amd64'
    mock_get_web_page.side_effect = ConnectionError('Could not connect')
    worker = VersionWorker(last_check_date, current_version)

    # WHEN: The worker is run
    with patch.object(worker, 'no_internet') as mocked_no_internet, \
            patch.object(worker, 'quit') as mocked_quit:
        worker.start()

    # THEN: The check completes and the signal is emitted
    expected_download_url = 'https://get.openlp.org/versions/version.txt'
    expected_headers = {'User-Agent': 'OpenLP/2.0 Linux/4.12.0-1-amd64; '}
    mock_get_web_page.assert_called_with(expected_download_url, headers=expected_headers)
    assert mock_get_web_page.call_count == 3
    mocked_no_internet.emit.assert_called_once_with()
    mocked_quit.emit.assert_called_once_with()


def test_update_check_date(mock_settings):
    """
    Test that the update_check_date() function writes the correct date
    """
    # GIVEN: A mocked Settings object
    # WHEN: update_check_date() is called
    update_check_date()

    # THEN: The correct date should have been saved
    mock_settings.setValue.assert_called_once_with('core/last version test', date.today().strftime('%Y-%m-%d'))


@patch('openlp.core.version.run_thread')
def test_check_for_update(mocked_run_thread, mock_settings):
    """
    Test the check_for_update() function
    """
    # GIVEN: A mocked settings object
    mock_settings.value.return_value = '1970-01-01'

    # WHEN: check_for_update() is called
    check_for_update(MagicMock())

    # THEN: The right things should have been called and a thread set in motion
    assert mocked_run_thread.call_count == 1


@patch('openlp.core.version.run_thread')
def test_check_for_update_skipped(mocked_run_thread, mock_settings):
    """
    Test that the check_for_update() function skips running if it already ran today
    """
    # GIVEN: A mocked settings object
    mock_settings.value.return_value = date.today().strftime('%Y-%m-%d')

    # WHEN: check_for_update() is called
    check_for_update(MagicMock())

    # THEN: The right things should have been called and a thread set in motion
    assert mocked_run_thread.call_count == 0


@pytest.mark.parametrize('in_version, out_version', [
    ('3.1.1', {'full': '3.1.1', 'version': '3.1.1', 'build': None}),
    ('3.0.2+git.cb1db9f43', {'full': '3.0.2+git.cb1db9f43', 'version': '3.0.2', 'build': 'git.cb1db9f43'}),
    ('3.1.2.dev15+gff6b05ed3', {'full': '3.1.2.dev15+gff6b05ed3', 'version': '3.1.2', 'build': 'gff6b05ed3'})
])
@patch('openlp.core.version.AppLocation.get_directory')
def test_get_version(mocked_get_directory: MagicMock, in_version: str, out_version: dict):
    """
    Test the get_version() function
    """
    # GIVEN: Some mocks and predefined versions
    mocked_path = MagicMock()
    mocked_path.__truediv__.return_value = mocked_path
    mocked_path.read_text.return_value = in_version
    mocked_get_directory.return_value = mocked_path

    # WHEN: get_version() is run
    with patch('openlp.core.version.APPLICATION_VERSION', None):
        version = get_version()

    # THEN: version is something
    assert version == out_version
