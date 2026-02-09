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
The :mod:`powerpraiseimport` module provides the functionality for importing
ProPresenter song files into the current installation database.
"""
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH


TEST_PATH = RESOURCE_PATH / 'songs' / 'powerpraise'


def test_power_praise(mock_settings):

    test_file_import = SongImportTestHelper('PowerPraiseImport', 'powerpraise')
    test_file_import.setUp()
    test_file_import.file_import([TEST_PATH / 'Naher, mein Gott zu Dir.ppl'],
                                 test_file_import.load_external_result_data(TEST_PATH / 'Naher, mein Gott zu Dir.json'))
    test_file_import.file_import([TEST_PATH / 'You are so faithful.ppl'],
                                 test_file_import.load_external_result_data(TEST_PATH / 'You are so faithful.json'))
    test_file_import.tearDown()
