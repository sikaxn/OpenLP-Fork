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
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from openlp.core.api.deploy import REMOTE_URL, deploy_zipfile, download_version_info, download_and_install, \
    get_installed_version


CONFIG_FILE = '{"latest": {"version": "0.1", "filename": "remote-0.1.zip", "sha256": "", "size": 854039}}'
CONFIG_DICT = json.loads(CONFIG_FILE)


@patch('openlp.core.api.deploy.ZipFile')
def test_deploy_zipfile(MockZipFile):
    """
    Remote Deploy tests - test the dummy zip file is processed correctly
    """
    # GIVEN: A new downloaded zip file
    mocked_zipfile = MagicMock()
    MockZipFile.return_value = mocked_zipfile
    root_path = Path('/') / 'tmp' / 'remotes'

    # WHEN: deploy_zipfile() is called
    deploy_zipfile(root_path, 'site.zip')

    # THEN: the zip file should have been extracted to the right location
    MockZipFile.assert_called_once_with(Path('/tmp/remotes/site.zip'))
    mocked_zipfile.extractall.assert_called_once_with(Path('/tmp/remotes'))


@patch('openlp.core.api.deploy.get_openlp_user_agent')
@patch('openlp.core.api.deploy.get_web_page')
def test_download_version_info_connection_error(mocked_get_web_page, mocked_get_openlp_user_agent):
    """
    Test that if a ConnectionError occurs while downloading a sha256 False is returned
    """
    # GIVEN: A bunch of mocks
    mocked_get_web_page.side_effect = ConnectionError()
    mocked_get_openlp_user_agent.return_value = 'OpenLP'

    # WHEN: download_sha256() is called
    result = download_version_info()

    # THEN: The result should be False
    assert result is False, 'download_version_info() should return False when encountering ConnectionError'


@patch('openlp.core.api.deploy.get_openlp_user_agent')
@patch('openlp.core.api.deploy.get_web_page')
def test_download_version_info_empty_file(mocked_get_web_page, mocked_get_openlp_user_agent):
    """
    Test that if there's no config when downloading a sha256 None is returned
    """
    # GIVEN: A bunch of mocks
    mocked_get_web_page.return_value = None
    mocked_get_openlp_user_agent.return_value = 'OpenLP'

    # WHEN: download_sha256() is called
    result = download_version_info()

    # THEN: The result should be Nonw
    assert result is None, 'download_version_info() should return None when there is a problem downloading the page'


@patch('openlp.core.api.deploy.get_openlp_user_agent')
@patch('openlp.core.api.deploy.get_web_page')
def test_download_version_info(mocked_get_web_page, mocked_get_openlp_user_agent):
    """
    Test that the sha256 and the version are returned
    """
    # GIVEN: A bunch of mocks
    mocked_get_web_page.return_value = CONFIG_FILE
    mocked_get_openlp_user_agent.return_value = 'OpenLP'

    # WHEN: download_sha256() is called
    result = download_version_info()

    # THEN: The result should be Nonw
    assert result == CONFIG_DICT, 'download_version_info() should return a dictionary of version information'


@patch('openlp.core.api.deploy.log.warning')
@patch('openlp.core.api.deploy.download_version_info')
def test_download_and_install_log_warning(mocked_download_version_info, mocked_warning):
    """
    Test that when the version info fails, a warning is logged
    """
    # GIVEN: A few mocks, and a version info of None
    mocked_download_version_info.return_value = None

    # WHEN: download_and_install is run
    result = download_and_install(None)

    # THEN: None is returned and a warning is logged
    assert result is None, 'The result should be None'
    mocked_warning.assert_called_once_with('Unable to access the version information, abandoning download')


@patch('openlp.core.api.deploy.AppLocation.get_section_data_path')
@patch('openlp.core.api.deploy.download_file')
@patch('openlp.core.api.deploy.download_version_info')
def test_download_and_install_download_fails(mocked_download_version_info, mocked_download_file,
                                             mocked_get_section_data_path):
    """
    Test that when the version info fails, a warning is logged
    """
    # GIVEN: A few mocks
    mocked_callback = MagicMock()
    mocked_download_version_info.return_value = CONFIG_DICT
    mocked_download_file.return_value = False
    mocked_get_section_data_path.return_value = Path('.')

    # WHEN: download_and_install is run
    result = download_and_install(mocked_callback)

    # THEN: None is returned and a warning is logged
    assert result is None, 'The result should be None'


@patch('openlp.core.api.deploy.AppLocation.get_section_data_path')
@patch('openlp.core.api.deploy.deploy_zipfile')
@patch('openlp.core.api.deploy.download_file')
@patch('openlp.core.api.deploy.download_version_info')
def test_download_and_install(mocked_download_version_info, mocked_download_file, mocked_deploy_zipfile,
                              mocked_get_section_data_path):
    # GIVEN: A bunch of mocks
    mocked_callback = MagicMock()
    mocked_download_version_info.return_value = CONFIG_DICT
    mocked_download_file.return_value = True
    mocked_remote_path = Path('/') / 'tmp' / 'remotes'
    mocked_remote_zip = mocked_remote_path / 'remote.zip'
    mocked_get_section_data_path.return_value = mocked_remote_path

    # WHEN: download_and_install() is called
    result = download_and_install(mocked_callback)

    # THEN: The correct things should have been done
    assert result == CONFIG_DICT['latest']['version'], 'The correct version is returned'
    mocked_download_file.assert_called_once_with(mocked_callback, REMOTE_URL + '0.1/remote-0.1.zip', mocked_remote_zip)
    mocked_deploy_zipfile.assert_called_once_with(mocked_remote_path, 'remote.zip')


@patch('openlp.core.api.deploy.AppLocation.get_section_data_path')
def test_get_installed_version_not_installed(mocked_get_section_data_path):
    """Test that if there is no remote installed, None is returned"""
    # GIVEN: A mocked AppLocation and no file installed
    mocked_version_file = MagicMock()
    mocked_version_file.__truediv__.return_value = mocked_version_file
    mocked_version_file.exists.return_value = False
    mocked_get_section_data_path.return_value = mocked_version_file

    # WHEN: get_installed_version() is called but there is no version file
    result = get_installed_version()

    # THEN: The result should be None
    assert result is None


@patch('openlp.core.api.deploy.AppLocation.get_section_data_path')
def test_get_installed_version_no_valid_version(mocked_get_section_data_path):
    """Test that if there is no valid version number, None is returned"""
    # GIVEN: A mocked AppLocation and no file installed
    mocked_version_file = MagicMock()
    mocked_version_file.__truediv__.return_value = mocked_version_file
    mocked_version_file.exists.return_value = True
    mocked_version_file.read_text.return_value = 'let app_version = 0.9.7;'
    mocked_get_section_data_path.return_value = mocked_version_file

    # WHEN: get_installed_version() is called but there is no version in the file
    result = get_installed_version()

    # THEN: The result should be None
    assert result is None


@patch('openlp.core.api.deploy.AppLocation.get_section_data_path')
def test_get_installed_version(mocked_get_section_data_path):
    """Test that get_installed_version returns the version number"""
    # GIVEN: A mocked AppLocation and no file installed
    mocked_version_file = MagicMock()
    mocked_version_file.__truediv__.return_value = mocked_version_file
    mocked_version_file.exists.return_value = True
    mocked_version_file.read_text.return_value = 'let appVersion = \'0.9.7\';'
    mocked_get_section_data_path.return_value = mocked_version_file

    # WHEN: get_installed_version() is called
    result = get_installed_version()

    # THEN: The result should be 0.9.7
    assert result == '0.9.7'


@patch('openlp.core.api.deploy.AppLocation.get_section_data_path')
def test_get_installed_version_nondefault_syntax(mocked_get_section_data_path):
    """Test that get_installed_version accepts double quotes and no trailing semicolon in version file"""
    # GIVEN: A mocked AppLocation and no file installed
    mocked_version_file = MagicMock()
    mocked_version_file.__truediv__.return_value = mocked_version_file
    mocked_version_file.exists.return_value = True
    mocked_version_file.read_text.return_value = 'let appVersion = "0.9.7"'
    mocked_get_section_data_path.return_value = mocked_version_file

    # WHEN: get_installed_version() is called
    result = get_installed_version()

    # THEN: The result should be 0.9.7
    assert result == '0.9.7'
