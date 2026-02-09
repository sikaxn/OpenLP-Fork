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
This module contains tests for the SingingTheFaith song importer.
"""
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'singingthefaith'


def test_singingthefaith_file_import(registry: Registry, settings: Settings):
    """
    Test that loading a Singing The Faith file works correctly on various files
    """
    with SongImportTestHelper('SingingTheFaithImport', 'singingthefaith') as helper:
        # Note that the previous tests without hints no longer apply as there is always a
        # hints file, which contains the hints for the real Singing The Faith Songs.
        # Unhinted songs here must be numbered above any real Singing The Faith Song
        # Single verse
        helper.file_import([TEST_PATH / 'H901.txt'],
                           helper.load_external_result_data(TEST_PATH / 'STF901.json'))
        # Whole song
        helper.file_import([TEST_PATH / 'H902.txt'],
                           helper.load_external_result_data(TEST_PATH / 'STF902.json'))

        # Tests with hints - note that the hints directory has a hints.tag which specifies
        # SongbookNumberInTitle: True
        # The default is false, so the unhinted tests will not have the title, but the hinted
        # song tests will need it

        # Single verse
        helper.file_import([TEST_PATH / 'hints' / 'H1.txt'],
                           helper.load_external_result_data(TEST_PATH / 'hints' / 'STF001.json'))
        # Whole song
        helper.file_import([TEST_PATH / 'hints' / 'H2.txt'],
                           helper.load_external_result_data(TEST_PATH / 'hints' / 'STF002.json'))
