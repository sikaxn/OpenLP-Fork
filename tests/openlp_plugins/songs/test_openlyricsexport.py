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
import shutil
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import MagicMock, patch

import pytest

from openlp.plugins.songs.lib.openlyricsexport import OpenLyricsExport


@pytest.fixture
def temp_folder():
    temp_path = Path(mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


def test_export_same_filename(registry, settings, temp_folder):
    """
    Test that files is not overwritten if songs has same title and author
    """
    # GIVEN: A mocked song_to_xml, 2 mocked songs, a mocked application and an OpenLyricsExport instance
    with patch('openlp.plugins.songs.lib.openlyricsexport.OpenLyrics.song_to_xml') as mocked_song_to_xml:
        mocked_song_to_xml.return_value = '<?xml version="1.0" encoding="UTF-8"?>\n<empty/>'
        author = MagicMock()
        author.display_name = 'Test Author'
        song = MagicMock()
        song.authors = [author]
        song.title = 'Test Title'
        parent = MagicMock()
        parent.stop_export_flag = False
        # mocked_application_object = MagicMock()
        # Registry().register('application', mocked_application_object)
        ol_export = OpenLyricsExport(parent, [song, song], temp_folder)

        # WHEN: Doing the export
        ol_export.do_export()

        # THEN: The exporter should have created 2 files
        assert (temp_folder / '{title} ({display_name}).xml'.format(
            title=song.title, display_name=author.display_name)).exists() is True
        assert (temp_folder / '{title} ({display_name})-1.xml'.format(
            title=song.title, display_name=author.display_name)).exists() is True


def test_export_sort_of_authers_filename(registry, settings, temp_folder):
    """
    Test that files is not overwritten if songs has same title and author
    """
    # GIVEN: A mocked song_to_xml, 1 mocked songs, a mocked application and an OpenLyricsExport instance
    with patch('openlp.plugins.songs.lib.openlyricsexport.OpenLyrics.song_to_xml') as mocked_song_to_xml:
        mocked_song_to_xml.return_value = '<?xml version="1.0" encoding="UTF-8"?>\n<empty/>'
        authorA = MagicMock()
        authorA.display_name = 'a Author'
        authorB = MagicMock()
        authorB.display_name = 'b Author'
        songA = MagicMock()
        songA.authors = [authorA, authorB]
        songA.title = 'Test Title'
        songB = MagicMock()
        songB.authors = [authorB, authorA]
        songB.title = 'Test Title'

        parent = MagicMock()
        parent.stop_export_flag = False
        # mocked_application_object = MagicMock()
        # Registry().register('application', mocked_application_object)
        ol_export = OpenLyricsExport(parent, [songA, songB], temp_folder)

        # WHEN: Doing the export
        ol_export.do_export()

        # THEN: The exporter orders authers
        assert (temp_folder / '{title} ({display_name}).xml'.format(
            title=songA.title,
            display_name=", ".join([authorA.display_name, authorB.display_name])
        )).exists() is True
        assert (temp_folder / '{title} ({display_name})-1.xml'.format(
            title=songB.title,
            display_name=", ".join([authorA.display_name, authorB.display_name])
        )).exists() is True


def test_export_is_stopped(registry, settings, temp_folder):
    """
    Test that the exporter stops when the flag is set
    """
    # GIVEN: A mocked song_to_xml, a mocked song, a mocked application and an OpenLyricsExport instance
    with patch('openlp.plugins.songs.lib.openlyricsexport.OpenLyrics.song_to_xml') as mocked_song_to_xml:
        mocked_song_to_xml.return_value = '<?xml version="1.0" encoding="UTF-8"?>\n<empty/>'
        author = MagicMock()
        author.display_name = 'Test Author'
        song = MagicMock()
        song.authors = [author]
        song.title = 'Test Title'
        parent = MagicMock()
        parent.stop_export_flag = True
        # mocked_application_object = MagicMock()
        # Registry().register('application', mocked_application_object)
        ol_export = OpenLyricsExport(parent, [song, song], temp_folder)

        # WHEN: Doing the export
        ol_export.do_export()

        # THEN: The exporter should not have created any files
        assert (temp_folder / '{title} ({display_name}).xml'.format(
            title=song.title, display_name=author.display_name)).exists() is False
