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
The :mod:`openlp.plugins.songs.lib.ui` module provides standard UI components
for the songs plugin.
"""
from PySide6 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry


class SongStrings(object):
    """
    Provide standard strings for use throughout the songs plugin.
    """
    def __init__(self):
        # These strings should need a good reason to be retranslated elsewhere.
        self.Author = translate('OpenLP.Ui', 'Author', 'Singular')
        self.Authors = translate('OpenLP.Ui', 'Authors', 'Plural')
        self.AuthorUnknown = translate('OpenLP.Ui', 'Author Unknown')  # Used to populate the database.
        self.CopyrightSymbol = '\xa9'
        self.SongBook = translate('OpenLP.Ui', 'Songbook', 'Singular')
        self.SongBooks = translate('OpenLP.Ui', 'Songbooks', 'Plural')
        self.SongIncomplete = translate('OpenLP.Ui', 'Title and/or verses not found')
        self.SongMaintenance = translate('OpenLP.Ui', 'Song Maintenance')
        self.Topic = translate('OpenLP.Ui', 'Topic', 'Singular')
        self.Topics = translate('OpenLP.Ui', 'Topics', 'Plural')
        self.XMLSyntaxError = translate('OpenLP.Ui', 'XML syntax error')


def show_key_warning(parent):
    """
    Check the settings to see if we need to show the warning message, and then show a warning about the key of the song
    """
    if Registry().get('settings').value('songs/enable chords') and \
            Registry().get('settings').value('songs/warn about missing song key'):
        QtWidgets.QMessageBox.warning(
            parent,
            translate('SongsPlugin.UI', 'Song key warning'),
            translate('SongsPlugin.UI', 'No musical key has been detected for this song, it should be placed before '
                      'the first chord.\nFor an optimal chord experience, please include a song key at the beginning '
                      'of the song. For example: [=G]\n\nYou can disable this warning message in songs settings.')
        )
