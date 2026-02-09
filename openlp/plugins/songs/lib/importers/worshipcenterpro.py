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
The :mod:`worshipcenterpro` module provides the functionality for importing
a WorshipCenter Pro database into the OpenLP database.
"""
import logging
import re

import pyodbc

from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport


log = logging.getLogger(__name__)


class WorshipCenterProImport(SongImport):
    """
    The :class:`WorshipCenterProImport` class provides the ability to import the
    WorshipCenter Pro Access Database
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the WorshipCenter Pro importer.
        """
        super(WorshipCenterProImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Receive a single file to import.
        """
        try:
            conn = pyodbc.connect('DRIVER={{Microsoft Access Driver (*.mdb)}};'
                                  'DBQ={source}'.format(source=self.import_source))
        except Exception as e:
            log.warning('Unable to connect the WorshipCenter Pro '
                        'database {source}. {error}'.format(source=self.import_source, error=str(e)))
            # Unfortunately no specific exception type
            self.log_error(self.import_source, translate('SongsPlugin.WorshipCenterProImport',
                                                         'Unable to connect the WorshipCenter Pro database.'))
            return
        cursor = conn.cursor()
        cursor.execute('SELECT ID, Field, Value FROM __SONGDATA')
        records = cursor.fetchall()
        songs = {}
        for record in records:
            record_id = record.ID
            if record_id not in songs:
                songs[record_id] = {}
            songs[record_id][record.Field] = record.Value
        self.import_wizard.progress_bar.setMaximum(len(songs))
        for song in songs:
            if self.stop_import_flag:
                break
            self.set_defaults()
            self.title = songs[song]['TITLE']
            if 'AUTHOR' in songs[song]:
                self.parse_author(songs[song]['AUTHOR'])
            if 'CCLISONGID' in songs[song]:
                self.ccli_number = songs[song]['CCLISONGID']
            if 'COMMENTS' in songs[song]:
                self.add_comment(songs[song]['COMMENTS'])
            if 'COPY' in songs[song]:
                self.add_copyright(songs[song]['COPY'])
            if 'SUBJECT' in songs[song]:
                self.topics.append(songs[song]['SUBJECT'])
            lyrics = songs[song]['LYRICS'].strip('&crlf;&crlf;')
            for verse in lyrics.split('&crlf;&crlf;'):
                verse = verse.replace('&crlf;', '\n')
                marker_type = 'v'
                # Find verse markers if any
                marker_start = verse.find('<')
                if marker_start > -1:
                    marker_end = verse.find('>')
                    marker = verse[marker_start + 1:marker_end]
                    # Identify the marker type
                    if marker in ['REFRAIN', 'CHORUS']:
                        marker_type = 'c'
                    elif marker == 'BRIDGE':
                        marker_type = 'b'
                    elif marker == 'PRECHORUS':
                        marker_type = 'p'
                    elif marker == 'END':
                        marker_type = 'e'
                    elif marker == 'INTRO':
                        marker_type = 'i'
                    elif marker == 'TAG':
                        marker_type = 'o'
                    # Strip tags from text
                    verse = re.sub('<[^<]+?>', '', verse)
                self.add_verse(verse.strip(), marker_type)
            self.finish()
