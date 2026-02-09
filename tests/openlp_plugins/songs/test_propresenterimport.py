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
The :mod:`propresenterimport` module provides the functionality for importing
ProPresenter song files into the current installation database.
"""
from tests.helpers.songfileimport import SongImportTestHelper
from tests.utils.constants import RESOURCE_PATH

TEST_PATH = RESOURCE_PATH / 'songs' / 'propresenter'


def test_pro4_song_import(settings):
    """
    Test that loading a ProPresenter 4 file works correctly
    """
    with SongImportTestHelper('ProPresenterImport', 'propresenter') as helper:
        helper.file_import([TEST_PATH / 'Amazing Grace.pro4'],
                           helper.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))


def test_pro5_song_import(settings):
    """
    Test that loading a ProPresenter 5 file works correctly
    """
    with SongImportTestHelper('ProPresenterImport', 'propresenter') as helper:
        helper.file_import([TEST_PATH / 'Amazing Grace.pro5'],
                           helper.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))


def test_pro6_song_import(settings):
    """
    Test that loading a ProPresenter 6 file works correctly
    """
    with SongImportTestHelper('ProPresenterImport', 'propresenter') as helper:
        helper.file_import([TEST_PATH / 'Amazing Grace.pro6'],
                           helper.load_external_result_data(TEST_PATH / 'Amazing Grace.json'))
