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
Package to test the openlp.core.lib.exceptions package.
"""
from openlp.core.lib.exceptions import ValidationError


def test_validation_error():
    """
    Test the creation of a ValidationError
    """
    # GIVEN: The ValidationError class

    # WHEN: Creating an instance of ValidationError
    error = ValidationError('Test ValidationError')

    # THEN: Then calling str on the error should return the correct text and it should be an instance of `Exception`
    assert str(error) == 'Test ValidationError'
    assert isinstance(error, Exception)
