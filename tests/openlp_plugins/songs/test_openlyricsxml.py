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
This module contains tests for the OpenLyrics song importer.
"""
import json
from unittest.mock import MagicMock, patch

import pytest
from lxml import etree, objectify

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics, SongXML
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'songs' / 'openlyrics'
START_TAGS = [{"protected": False, "desc": "z", "start tag": "{z}", "end html": "</strong>", "temporary": False,
               "end tag": "{/z}", "start html": "strong>", "hidden": False}]
RESULT_TAGS = [{"temporary": False, "protected": False, "desc": "z", "start tag": "{z}", "start html": "strong>",
                "end html": "</strong>", "end tag": "{/z}", "hidden": False},
               {"temporary": False, "end tag": "{/c}", "desc": "c", "start tag": "{c}",
                "start html": "<span class=\"chord\" style=\"display:none\"><strong>", "end html": "</strong></span>",
                "protected": False, "hidden": False}]
VERSE_LINES_07_XML = '<lines>\
                        <line>Amazing grace, how sweet the sound</line>\
                        <line>That saved a wretch like me</line>\
                      </lines>'
VERSE_LINES_08_XML = '<lines>\
                        Amazing grace, how sweet the sound<br/>\
                        That saved a wretch like me\
                      </lines>'
VERSE_LINES_EMPTY_XML = '<lines/>'
AUTHOR_XML = '<properties>\
                  <authors>\
                      <author type="words">Test Author1</author>\
                      <author type="music">Test Author1</author>\
                      <author type="words">Test Author2</author>\
                  </authors>\
            </properties>'
SONGBOOK_XML = '<properties>\
                    <songbooks>\
                        <songbook name="Collection 1" entry="48"/>\
                        <songbook name="Collection 2" entry="445 A"/>\
                    </songbooks>\
                </properties>'


@pytest.fixture
def song_xml(registry: Registry, settings: Settings):
    return SongXML()


@pytest.fixture
def open_lyrics(registry: Registry, settings: Settings):
    return OpenLyrics(MagicMock())


def test_songxml_get_verses_invalid_xml(song_xml: SongXML):
    """Test that invalid XML for a song is ignored"""
    # GIVEN: Invalid XML and a SongXML object
    invalid_xml = 'this is not xml'

    # WHEN: get_verses is called with invalid XML
    result = song_xml.get_verses(invalid_xml)

    # THEN: An empty list is returned
    assert result == []


def test_process_verse_lines_v07(open_lyrics: OpenLyrics):
    """
    Test that the _process_verse_lines method correctly processes the verse lines with v0.7 OpenLyrics
    """
    # GIVEN: Some lyrics XML and version 0.7 of OpenLyrics
    lines = objectify.fromstring(VERSE_LINES_07_XML)

    # WHEN: The lyrics of a verse are processed
    result = open_lyrics._process_verse_lines(lines, '0.7')

    # THEN: The results should be correct
    assert result == 'Amazing grace, how sweet the sound\nThat saved a wretch like me'


def test_process_verse_lines_v08(open_lyrics: OpenLyrics):
    """
    Test that the _process_verse_lines method correctly processes the verse lines with v0.8 OpenLyrics
    """
    # GIVEN: Some lyrics XML and version 0.8 of OpenLyrics
    lines = objectify.fromstring(VERSE_LINES_08_XML)

    # WHEN: The lyrics of a verse are processed
    result = open_lyrics._process_verse_lines(lines, '0.8')

    # THEN: The results should be correct
    assert result == '                        Amazing grace, how sweet the sound'\
                     '                        That saved a wretch like me                      '


def test_process_empty_verse_lines(open_lyrics: OpenLyrics):
    """
    Test that _process_verse_lines() correctly handles empty verse lines
    """
    # GIVEN: An empty lines object with additional content
    lines = objectify.fromstring(VERSE_LINES_EMPTY_XML)

    # WHEN: The lyrics of a verse are processed
    result = open_lyrics._process_verse_lines(lines, '0.8')

    # THEN: The results should be correct
    assert result == ''


def test_process_formatting_tags(settings: Settings, open_lyrics: OpenLyrics):
    """
    Test that _process_formatting_tags works
    """
    # GIVEN: A OpenLyric XML with formatting tags and a mocked out manager
    settings.setValue('formattingTags/html_tags', json.dumps(START_TAGS))
    parser = etree.XMLParser(remove_blank_text=True)
    parsed_file = etree.parse((TEST_PATH / 'duchu-tags.xml').open('rb'), parser)
    xml = etree.tostring(parsed_file).decode()
    song_xml = objectify.fromstring(xml)

    # WHEN: processing the formatting tags
    open_lyrics._process_formatting_tags(song_xml, False)

    # THEN: New tags should have been saved
    assert json.loads(settings.value('formattingTags/html_tags')) == RESULT_TAGS, \
        'The formatting tags should contain both the old and the new'


@patch('openlp.plugins.songs.lib.openlyricsxml.Author')
def test_process_author(MockAuthor: MagicMock, open_lyrics: OpenLyrics):
    """
    Test that _process_authors works
    """
    # GIVEN: A OpenLyric XML with authors and a mocked out manager
    open_lyrics.manager.get_object_filtered.return_value = None
    properties_xml = objectify.fromstring(AUTHOR_XML)
    mocked_song = MagicMock()

    # WHEN: processing the author xml
    open_lyrics._process_authors(properties_xml, mocked_song)

    # THEN: add_author should have been called twice
    assert mocked_song.method_calls[0][1][1] == 'words+music'
    assert mocked_song.method_calls[1][1][1] == 'words'


@patch('openlp.plugins.songs.lib.openlyricsxml.SongBook')
def test_process_songbooks(MockSongBook: MagicMock, open_lyrics: OpenLyrics):
    """
    Test that _process_songbooks works
    """
    # GIVEN: A OpenLyric XML with songbooks and a mocked out manager
    open_lyrics.manager.get_object_filtered.return_value = None
    properties_xml = objectify.fromstring(SONGBOOK_XML)
    mocked_song = MagicMock()

    # WHEN: processing the songbook xml
    open_lyrics._process_songbooks(properties_xml, mocked_song)

    # THEN: add_songbook_entry should have been called twice
    assert mocked_song.method_calls[0][1][1] == '48'
    assert mocked_song.method_calls[1][1][1] == '445 A'
