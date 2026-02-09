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
Package to test the openlp.core.ui.formattingtagscontroller package.
"""
import pytest

from openlp.core.ui.formattingtagcontroller import FormattingTagController


@pytest.fixture()
def services(registry, qapp):
    return FormattingTagController()


def test_strip(services):
    """
    Test that the _strip strips the correct chars
    """
    # GIVEN: An instance of the Formatting Tag Form and a string containing a tag
    tag = '{tag}'

    # WHEN: Calling _strip
    result = services._strip(tag)

    # THEN: The tag should be returned with the wrappers removed.
    assert result == 'tag', 'FormattingTagForm._strip should return u\'tag\' when called with u\'{tag}\''


def test_end_tag_changed_processes_correctly(services):
    """
    Test that the end html tags are generated correctly
    """
    # GIVEN: A list of start , end tags and error messages
    tests = []
    test = {'start': '<b>', 'end': None, 'gen': '</b>', 'valid': None}
    tests.append(test)
    test = {'start': '<i>', 'end': '</i>', 'gen': None, 'valid': None}
    tests.append(test)
    test = {'start': '<b>', 'end': '</i>', 'gen': None,
            'valid': 'End tag </b> does not match end tag for start tag <b>'}
    tests.append(test)

    # WHEN: Testing each one of them in turn
    for test in tests:
        error, result = services.end_tag_changed(test['start'], test['end'])

        # THEN: The result should match the predetermined value.
        assert result == test['gen'], \
            'Function should handle end tag correctly : %s and %s for %s ' % (test['gen'], result, test['start'])
        assert error == test['valid'], 'Function should not generate unexpected error messages : %s ' % error


def test_start_tag_changed_processes_correctly(services):
    """
    Test that the end html tags are generated correctly
    """
    # GIVEN: A list of start , end tags and error messages
    tests = []
    test = {'start': '<b>', 'end': '', 'gen': '</b>', 'valid': None}
    tests.append(test)
    test = {'start': '<i>', 'end': '</i>', 'gen': None, 'valid': None}
    tests.append(test)
    test = {'start': 'superfly', 'end': '', 'gen': None, 'valid': 'Start tag superfly is not valid HTML'}
    tests.append(test)

    # WHEN: Testing each one of them in turn
    for test in tests:
        error, result = services.start_tag_changed(test['start'], test['end'])

        # THEN: The result should match the predetermined value.
        assert result == test['gen'], \
            'Function should handle end tag correctly : %s and %s ' % (test['gen'], result)
        assert error == test['valid'], 'Function should not generate unexpected error messages : %s ' % error


def test_start_html_to_end_html(services):
    """
    Test that the end html tags are generated correctly
    """
    # GIVEN: A list of valid and invalid tags
    tests = {'<b>': '</b>', '<i>': '</i>', 'superfly': '', '<HTML START>': None,
             '<span style="-webkit-text-fill-color:red">': '</span>'}

    # WHEN: Testing each one of them
    for test1, test2 in tests.items():
        result = services.start_html_to_end_html(test1)

        # THEN: The result should match the predetermined value.
        assert result == test2, 'Calculated end tag should be valid: %s and %s = %s' % (test1, test2, result)
