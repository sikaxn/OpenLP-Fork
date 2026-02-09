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
Functional tests to test the :mod:`~openlp.core.common.platform` module.
"""
from unittest.mock import patch

import pytest

from openlp.core.common.platform import is_win, is_macosx, is_linux, is_64bit_instance


def test_is_win():
    """
    Test the is_win() function
    """
    # GIVEN: Mocked out objects
    with patch('openlp.core.common.platform.os') as mocked_os, \
            patch('openlp.core.common.platform.sys') as mocked_sys:

        # WHEN: The mocked os.name and sys.platform are set to 'nt' and 'win32' repectivly
        mocked_os.name = 'nt'
        mocked_sys.platform = 'win32'

        # THEN: The three platform functions should perform properly
        assert is_win() is True, 'is_win() should return True'
        assert is_macosx() is False, 'is_macosx() should return False'
        assert is_linux() is False, 'is_linux() should return False'


def test_is_macosx():
    """
    Test the is_macosx() function
    """
    # GIVEN: Mocked out objects
    with patch('openlp.core.common.platform.os') as mocked_os, \
            patch('openlp.core.common.platform.sys') as mocked_sys:

        # WHEN: The mocked os.name and sys.platform are set to 'posix' and 'darwin' repectivly
        mocked_os.name = 'posix'
        mocked_sys.platform = 'darwin'

        # THEN: The three platform functions should perform properly
        assert is_macosx() is True, 'is_macosx() should return True'
        assert is_win() is False, 'is_win() should return False'
        assert is_linux() is False, 'is_linux() should return False'


def test_is_linux():
    """
    Test the is_linux() function
    """
    # GIVEN: Mocked out objects
    with patch('openlp.core.common.platform.os') as mocked_os, \
            patch('openlp.core.common.platform.sys') as mocked_sys:

        # WHEN: The mocked os.name and sys.platform are set to 'posix' and 'linux3' repectively
        mocked_os.name = 'posix'
        mocked_sys.platform = 'linux3'

        # THEN: The three platform functions should perform properly
        assert is_linux() is True, 'is_linux() should return True'
        assert is_win() is False, 'is_win() should return False'
        assert is_macosx() is False, 'is_macosx() should return False'


@pytest.mark.skipif(not is_linux(), reason='This can only run on Linux')
def test_is_linux_distro():
    """
    Test the is_linux() function for a particular Linux distribution
    """
    # GIVEN: Mocked out objects
    with patch('openlp.core.common.platform.os') as mocked_os, \
            patch('openlp.core.common.platform.sys') as mocked_sys, \
            patch('openlp.core.common.platform.distro_id') as mocked_distro_id:

        # WHEN: The mocked os.name and sys.platform are set to 'posix' and 'linux3' repectively
        #       and the distro is Fedora
        mocked_os.name = 'posix'
        mocked_sys.platform = 'linux3'
        mocked_distro_id.return_value = 'fedora'

        # THEN: The three platform functions should perform properly
        assert is_linux(distro='fedora') is True, 'is_linux(distro="fedora") should return True'
        assert is_win() is False, 'is_win() should return False'
        assert is_macosx() is False, 'is_macosx() should return False'


def test_is_64bit_instance():
    """
    Test the is_64bit_instance() function
    """
    # GIVEN: Mocked out objects
    with patch('openlp.core.common.platform.sys') as mocked_sys:

        # WHEN: The mocked sys.maxsize is set to 32-bit
        mocked_sys.maxsize = 2**32

        # THEN: The result should be False
        assert is_64bit_instance() is False, 'is_64bit_instance() should return False'
