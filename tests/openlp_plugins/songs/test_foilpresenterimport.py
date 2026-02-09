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
This module contains tests for the SongShow Plus song importer.
"""
from unittest.mock import MagicMock, patch

import pytest

from openlp.plugins.songs.lib.importers.foilpresenter import FoilPresenter


@pytest.fixture
def foil_presenter():
    mocked_manager = MagicMock()
    mocked_song_import = MagicMock()
    return FoilPresenter(mocked_manager, mocked_song_import)


def test_create_foil_presenter(foil_presenter: FoilPresenter):
    """
    Test creating an instance of the foil_presenter class
    """
    # GIVEN: A mocked out "manager" and "SongImport" instance
    # WHEN: An foil_presenter instance is created
    # THEN: The instance should not be None
    assert foil_presenter is not None, 'foil_presenter instance should not be none'


@pytest.mark.parametrize('arg', [None, False, 0, ''])
def test_no_xml(foil_presenter: FoilPresenter, arg: None | bool | int | str):
    """
    Test calling xml_to_song with out the xml argument
    """
    # GIVEN: A mocked out "manager" and "SongImport" as well as an foil_presenter instance
    # WHEN: xml_to_song is called without valid an argument
    result = foil_presenter.xml_to_song(arg)

    # Then: xml_to_song should return False
    assert result is None, 'xml_to_song should return None when called with %s' % arg


def test_encoding_declaration_removal(foil_presenter: FoilPresenter):
    """
    Test that the encoding declaration is removed
    """
    # GIVEN: A reset mocked out re and an instance of foil_presenter
    # WHEN: xml_to_song is called with a string with an xml encoding declaration
    result = foil_presenter._remove_declaration('<?xml version="1.0" encoding="UTF-8"?>\n<foilpresenterfolie>')

    # THEN: the xml encoding declaration should have been stripped
    assert result == '\n<foilpresenterfolie>'


def test_no_encoding_declaration(foil_presenter: FoilPresenter):
    """
    Check that the xml sting is left intact when no encoding declaration is made
    """
    # GIVEN: A reset mocked out re and an instance of foil_presenter
    # WHEN: xml_to_song is called with a string without an xml encoding declaration
    result = foil_presenter._remove_declaration('<foilpresenterfolie>')

    # THEN: the string should have been left intact
    assert result == '<foilpresenterfolie>'


@patch('openlp.plugins.songs.lib.importers.foilpresenter.SongXML')
def test_process_lyrics_no_verses(MockSongXML: MagicMock, foil_presenter: FoilPresenter):
    """
    Test that _process_lyrics handles song files that have no verses.
    """
    # GIVEN: A mocked foilpresenterfolie with no attribute strophe, a mocked song and a
    #       foil presenter instance
    class FakeFoilPresenterFolie:
        strophen: None = None
        titel: str = 'Lied'

    fake_foilpresenterfolie = FakeFoilPresenterFolie()

    # del mock_foilpresenterfolie.strophen.strophe
    mocked_song = MagicMock()

    # WHEN: _process_lyrics is called
    result = foil_presenter._process_lyrics(fake_foilpresenterfolie, mocked_song)

    # THEN: _process_lyrics should return None and the song_import log_error method should have been called once
    assert result is None
    foil_presenter.importer.log_error.assert_called_once_with('Lied',
                                                              'Invalid Foilpresenter song file. No verses found.')
