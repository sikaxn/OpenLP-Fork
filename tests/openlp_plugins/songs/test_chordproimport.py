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
This module contains tests for the OpenSong song importer.
"""
from openlp.core.common.registry import Registry
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'chordpro'


def test_chordpro(mock_settings):

    test_file_import = SongImportTestHelper('ChordProImport', 'chordpro')
    test_file_import.setUp()
    Registry().get('settings').value.side_effect = lambda value: True if value == 'songs/enable chords' else False
    # Do the test import
    test_file_import.file_import([TEST_PATH / 'swing-low.chordpro'],
                                 test_file_import.load_external_result_data(TEST_PATH / 'swing-low.json'))
    test_file_import.tearDown()
