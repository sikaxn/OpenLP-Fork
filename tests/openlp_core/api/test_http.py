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
import pytest
from flask import Response

from openlp.core.api.http import check_auth, authenticate


@pytest.mark.parametrize('auth,result', [((None, 'b3BlbmxwOnBhc3N3b3Jk'), True),
                                         ((None, 'b3BlbmxwMTpwYXNzd29yZDE='), False)])
def test_check_auth(auth: str, result: bool, mock_settings):
    """Test the check_auth() method"""
    mock_settings.value.side_effect = ['openlp', 'password']
    assert check_auth(auth) == result


def test_authenticate():
    """Test the authenticate() method"""
    result = authenticate()
    assert isinstance(result, Response)
    assert result.status_code == 401
    assert result.www_authenticate.realm == 'OpenLP Login Required'
