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
Package to test the openlp.plugins.planningcenter.lib.planningcenter_api package.
"""
import os
from urllib.error import HTTPError
from unittest.mock import MagicMock, patch

import pytest

from openlp.plugins.planningcenter.lib.planningcenter_api import PlanningCenterAPI

TEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'resources', 'planningcenter'))


@pytest.fixture
def api() -> PlanningCenterAPI:
    yield PlanningCenterAPI('application_id', 'secret')


def test_init():
    """
    Test that the api class can be instantiated with an application_id and secret
    """
    # GIVEN: A PlanningCenterAPI Class
    # WHEN:  __init__ is called with an application id and secret
    api = PlanningCenterAPI('application_id', 'secret')
    # THEN: airplane mode should be false
    assert api.airplane_mode is False, 'Class init without airplane mode'


@patch('openlp.plugins.planningcenter.lib.planningcenter_api.os.path.isdir')
def test_init_with_airplane_mode(mocked_isdir: MagicMock):
    """
    Test that the api class can be instantiated with an application_id and secret
    """
    # GIVEN: A PlanningCenterAPI Class
    mocked_isdir.return_value = True
    # WHEN:  __init__ is called with an application id and secret and airplane_dir mocked
    api = PlanningCenterAPI('application_id', 'secret')
    # THEN: airplane mode should be true
    assert api.airplane_mode is True, 'Class init with airplane mode'


@patch('openlp.plugins.planningcenter.lib.planningcenter_api.os.path.isdir')
@patch('openlp.plugins.planningcenter.lib.planningcenter_api.urllib.request.build_opener')
@patch('openlp.plugins.planningcenter.lib.planningcenter_api.open')
def test_get_from_services_api(mocked_open: MagicMock, mocked_opener: MagicMock, mocked_isdir: MagicMock,
                               api: PlanningCenterAPI):
    """
    Test that the get_from_services_api can be called in airplane mode
    """
    # GIVEN: A PlanningCenterAPI Class
    mocked_isdir.return_value = True
    mocked_opener.return_value.open.return_value.read.return_value = '{"foo" : "bar"}'.encode(encoding='utf8')
    # WHEN:  get_from_services_api is called with empty string as input ('') and airplane mode enabled
    result = api.get_from_services_api('test')
    # THEN: we should get back the return value we mocked
    assert result['foo'] == 'bar', 'get_from_services_api returns correct value'


def test_check_credentials_returns_empty_string_for_bad_credentials(api: PlanningCenterAPI):
    """
    Test that check_credentials returns an empty string if authentication fails
    """
    # GIVEN: A PlanningCenterAPI Class with mocked out get_from_services_api that returns a 401 (http auth) error
    with patch.object(api, 'get_from_services_api') as mocked_get_services:
        mocked_get_services.side_effect = HTTPError(None, 401, None, None, None)
        # WHEN: check_credentials is called
        result = api.check_credentials()
    # THEN: we have an empty string returns
    assert result == '', 'return string is empty for bad authentication'


def test_check_credentials_raises_other_exceptions(api: PlanningCenterAPI):
    # GIVEN: A PlanningCenterAPI Class with mocked out get_from_services_api that returns a 400 error
    with patch.object(api, 'get_from_services_api') as mocked_get_services:
        mocked_get_services.side_effect = HTTPError(None, 300, None, None, None)
        # WHEN: check_credentials is called in a try block
        with pytest.raises(HTTPError) as exc:
            api.check_credentials()
    # THEN: we received an exception with code of 300
    assert exc.value.code == 300, 'correct exception is raised from check_credentials'


@patch('openlp.plugins.planningcenter.lib.planningcenter_api.os.path.isdir')
@patch('openlp.plugins.planningcenter.lib.planningcenter_api.urllib.request.build_opener')
@patch('openlp.plugins.planningcenter.lib.planningcenter_api.open')
def test_check_credentials_pass(mocked_open: MagicMock, mocked_opener: MagicMock, mocked_isdir: MagicMock,
                                api: PlanningCenterAPI):
    """
    Test that check_credentials can be called in airplane mode
    """
    # GIVEN: A PlanningCenterAPI Class
    mocked_isdir.return_value = True
    mocked_opener.return_value.open.return_value.read.return_value = \
        '{"data": {"attributes": {"name": "jpk"}}}'.encode(encoding='utf8')
    # WHEN:  get_from_services_api is called with empty string as input ('') and airplane mode enabled
    result = api.check_credentials()
    # THEN: Check credentials returns our mocked value
    assert result == 'jpk', 'check_credentials returns correct value for pass'
