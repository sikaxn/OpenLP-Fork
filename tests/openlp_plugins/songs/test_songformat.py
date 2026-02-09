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
This module contains tests for the SongFormat class
"""
from openlp.plugins.songs.lib.importer import SongFormat


def test_get_format_list():
    """
    Test that get_format_list() returns all available formats
    """
    # GIVEN: The SongFormat class
    # WHEN: Retrieving the format list
    # THEN: All SongFormats should be returned
    assert len(SongFormat.get_format_list()) == len(SongFormat.__attributes__), \
        "The returned SongFormats don't match the stored ones"


def test_get_attributed_no_attributes():
    """
    Test that SongFormat.get(song_format) returns all attributes associated with the given song_format
    """
    # GIVEN: A SongFormat
    # WHEN: Retrieving all attributes of a SongFormat
    for song_format in SongFormat.get_format_list():
        # THEN: All attributes associated with the SongFormat should be returned
        assert SongFormat.get(song_format) == SongFormat.__attributes__[song_format], \
            "The returned attributes don't match the stored ones"


def test_get_attributed_single_attribute():
    """
    Test that SongFormat.get(song_format, attribute) returns only one -and the correct- attribute
    """
    # GIVEN: A SongFormat
    for song_format in SongFormat.get_format_list():
        # WHEN: Retrieving an attribute that overrides the default values
        for attribute in SongFormat.get(song_format).keys():
            # THEN: Return the attribute
            assert SongFormat.get(song_format, attribute) == SongFormat.get(song_format)[attribute], \
                "The returned attribute doesn't match the stored one"
        # WHEN: Retrieving an attribute that was not overridden
        for attribute in SongFormat.__defaults__.keys():
            if attribute not in SongFormat.get(song_format).keys():
                # THEN: Return the default value
                assert SongFormat.get(song_format, attribute) == SongFormat.__defaults__[attribute], \
                    "The returned attribute does not match the default values stored"


def test_get_attributed_multiple_attributes():
    """
    Test that multiple attributes can be retrieved for a song_format
    """
    # GIVEN: A SongFormat
    # WHEN: Retrieving multiple attributes at the same time
    for song_format in SongFormat.get_format_list():
        # THEN: Return all attributes that were specified
        assert len(SongFormat.get(song_format, 'canDisable', 'availability')) == 2, \
            "Did not return the correct number of attributes when retrieving multiple attributes at once"


def test_get_format_list_returns_ordered_list():
    """
    Test that get_format_list() returns a list that is ordered
    according to the order specified in SongFormat
    """
    # GIVEN: The SongFormat class
    # WHEN: Retrieving all formats
    # THEN: The returned list should be sorted according to the ordering defined in SongFormat
    assert sorted(SongFormat.get_format_list()) == SongFormat.get_format_list(), \
        "The list returned should be sorted according to the ordering in SongFormat"
