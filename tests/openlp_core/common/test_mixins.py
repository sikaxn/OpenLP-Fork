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
Package to test the openlp.core.common.mixins package.
"""
import pytest
from unittest.mock import MagicMock, patch

from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry


@pytest.fixture
def registry_env():
    """An instance of the Registry"""
    Registry.create()

    class Test(RegistryProperties):
        pass
    return Test()


def test_no_application(registry_env):
    """
    Test property if no registry value assigned
    """
    # GIVEN an Empty Registry
    # WHEN there is no Application
    # THEN the application should be none
    assert registry_env.application is None, 'The application value should be None'


def test_application(registry_env):
    """
    Test property if registry value assigned
    """
    # GIVEN an Empty Registry
    application = MagicMock()

    # WHEN the application is registered
    Registry().register('application', application)

    # THEN the application should be none
    assert registry_env.application == application, 'The application value should match'


@patch('openlp.core.common.mixins.is_win')
def test_application_on_windows(mocked_is_win, registry_env):
    """
    Test property if registry value assigned on Windows
    """
    # GIVEN an Empty Registry and we're on Windows
    application = MagicMock()
    mocked_is_win.return_value = True

    # WHEN the application is registered
    Registry().register('application', application)

    # THEN the application should be none
    assert registry_env.application == application, 'The application value should match'


@patch('openlp.core.common.mixins.is_win')
def test_get_application_on_windows(mocked_is_win):
    """
    Set that getting the application object on Windows happens dynamically
    """
    # GIVEN an Empty Registry and we're on Windows
    mocked_is_win.return_value = True
    mock_application = MagicMock()
    reg_props = RegistryProperties()
    registry = Registry()

    # WHEN the application is accessed
    with patch.object(registry, 'get') as mocked_get:
        mocked_get.return_value = mock_application
        actual_application = reg_props.application

    # THEN the application should be the mock object, and the correct function should have been called
    assert mock_application == actual_application, 'The application value should match'
    mocked_is_win.assert_called_with()
    mocked_get.assert_called_with('application')
