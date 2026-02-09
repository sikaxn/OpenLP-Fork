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
Test aspects of the song export wizard.
"""

import pytest
from unittest.mock import MagicMock
from PySide6 import QtCore, QtWidgets

from openlp.plugins.songs.lib.db import Song
from openlp.plugins.songs.forms.songexportform import SongExportForm


@pytest.fixture()
def form(settings):
    """Create song export wizard form"""

    mocked_plugin = MagicMock()
    frm = SongExportForm(None, mocked_plugin)

    yield frm
    del frm


def make_list_item_from_song(song):
    """Prepare a QListWidgetItem to be added to the list of available songs."""

    item = QtWidgets.QListWidgetItem(song.title)
    item.setData(QtCore.Qt.ItemDataRole.UserRole, song)
    item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
                  QtCore.Qt.ItemFlag.ItemIsUserCheckable |
                  QtCore.Qt.ItemFlag.ItemIsEnabled)
    item.setCheckState(QtCore.Qt.CheckState.Unchecked)

    return item


def test_export_checked(form):
    """
    Test whether only the songs checked in the list of available songs actually end up
    in in the list of songs to be exported.
    """

    song1 = Song()
    song1.title = 'test song1'

    # the second song shall not be selected for export
    title_unchecked = 'test song2'
    song2 = Song()
    song2.title = title_unchecked

    song3 = Song()
    song3.title = 'test song3'

    item1 = make_list_item_from_song(song1)
    item2 = make_list_item_from_song(song2)
    item3 = make_list_item_from_song(song3)

    # select only songs 1 and 3
    form.available_list_widget.itemActivated.emit(item1)
    form.available_list_widget.itemActivated.emit(item3)

    form.available_list_widget.addItem(item1)
    form.available_list_widget.addItem(item2)
    form.available_list_widget.addItem(item3)

    form.show()

    # id not stored upon addition, so assume it's the first page after the welcome
    # page in the wizard and change to that page to validate it
    available_songs_page_id = 1
    form.setCurrentId(available_songs_page_id)
    form.validateCurrentPage()

    # we checked only two of the three available items, so only these should be selected:
    number_selected = form.selected_list_widget.count()
    assert number_selected == 2, 'Only two of the songs in the list should be selected.'

    # none of the two selected songs must contain the title of song #2:
    selected_songs = [
        form.selected_list_widget.item(i).data(QtCore.Qt.ItemDataRole.UserRole)
        for i in range(number_selected)
    ]
    assert not any([song.title == title_unchecked for song in selected_songs]), \
        f'"{title_unchecked}" is expected not to be selected.'
