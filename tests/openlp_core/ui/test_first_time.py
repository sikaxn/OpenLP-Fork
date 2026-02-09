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
Package to test the openlp.core.utils.__init__ package.
"""
from unittest.mock import patch

from openlp.core.common.httputils import CONNECTION_RETRIES, get_web_page


@patch('openlp.core.common.httputils.requests')
def test_webpage_connection_retry(mocked_requests, mock_settings):
    """
    Test get_web_page will attempt CONNECTION_RETRIES+1 connections - bug 1409031
    """
    # GIVEN: Initial settings and mocks
    mocked_requests.get.side_effect = OSError('Unable to connect')

    # WHEN: A webpage is requested
    try:
        get_web_page('http://localhost')
    except Exception as e:
        assert isinstance(e, ConnectionError)

    # THEN: urlopen should have been called CONNECTION_RETRIES + 1 count
    assert mocked_requests.get.call_count == CONNECTION_RETRIES, \
        'get should have been called {} times, but was only called {} times'.format(
            CONNECTION_RETRIES, mocked_requests.get.call_count)
