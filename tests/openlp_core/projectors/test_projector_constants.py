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
Package to test the openlp.core.projectors.constants module.
"""
from openlp.core.projectors import constants
from openlp.core.projectors.constants import STATUS_CODE, STATUS_MSG


def test_defined_codes_in_status_code():
    """
    Test defined status/error codes have equivalent strings
    """
    check = []
    missing_str = []

    # GIVEN: List of defined E_* and S_* items defined in constants

    for item in constants.__dict__:
        if item.startswith('E_') or item.startswith('S_'):
            check.append(item)

    # WHEN: Verify items were addeded to check
    for item in check:
        if constants.__dict__[item] not in STATUS_CODE:
            missing_str.append(item)

    # THEN: There should be no missing items
    assert 0 == len(missing_str), 'Status string missing: {msg}'.format(msg=missing_str)


def test_status_code_in_status_message():
    """
    Test if entries in STATUS_CODE have equivalent descriptions in STATUS_MSG
    """
    missing_msg = []

    # GIVEN: Test items
    check = STATUS_CODE

    # WHEN: Verify each entry in STATUS_MSG against STATUS_CODE
    for item in check:
        if item not in STATUS_MSG:
            missing_msg.append(item)

    # THEN: There should be no missing items
    assert 0 == len(missing_msg), 'Status message missing: {msg}'.format(msg=missing_msg)


def test_build_pjlink_video_label():
    """
    Test building PJLINK_DEFAULT_CODES dictionary
    """
    # GIVEN: Test data
    from tests.resources.projector.data import TEST_VIDEO_CODES

    # WHEN: Import projector PJLINK_DEFAULT_CODES
    from openlp.core.projectors.constants import PJLINK_DEFAULT_CODES

    # THEN: Verify dictionary was build correctly
    assert PJLINK_DEFAULT_CODES == TEST_VIDEO_CODES, 'PJLink video strings should match'
