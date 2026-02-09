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
Test the exception handling functions
"""
from unittest.mock import patch

from openlp.core.common.handlers import handle_permission_error


@patch('openlp.core.common.handlers.QtWidgets.QMessageBox')
def test_handle_permission_error(MockQMessageBox):
    """Test the handle_permission_error() function to make sure it catches PermissionError"""
    # GIVEN: A mocked QMessageBox class and a file path
    file_path = 'mocked_file_path'

    # WHEN: the handle_permission_error() context manager is used
    try:
        with handle_permission_error(file_path):
            raise PermissionError('Bad mojo')
    except PermissionError:
        assert False, 'PermissionError was not caught'

    MockQMessageBox.critical.assert_called_once_with(
        None, 'Permission Error',
        'There was a permissions error when trying to access mocked_file_path'
    )
