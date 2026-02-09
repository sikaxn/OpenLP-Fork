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
The :mod:`lyrix` module provides the functionality for importing songs which are
exported from Lyrix."""
import json
import logging
import re
from pathlib import Path

from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib.db import AuthorType
from openlp.plugins.songs.lib.importers.songimport import SongImport


log = logging.getLogger(__name__)


class VideoPsalmImport(SongImport):
    """
    Import songs exported from Lyrix
    """

    def __init__(self, manager, **kwargs):
        """
        Initialise the class.
        """
        super(VideoPsalmImport, self).__init__(manager, **kwargs)

    def do_import(self):
        """
        Process the VideoPsalm file - pass in a file-like object, not a file path.
        """
        self.import_source = Path(self.import_source)
        self.set_defaults()
        try:
            file_content = self.import_source.read_text(encoding='utf-8-sig')
            processed_content = ''
            inside_quotes = False
            # The VideoPsalm format is not valid json, it uses illegal line breaks and unquoted keys, this must be fixed
            file_content_it = iter(file_content)
            for c in file_content_it:
                if c == '"':
                    inside_quotes = not inside_quotes
                # Detect invalid linebreak
                if c == '\n':
                    if inside_quotes:
                        processed_content += '\\n'
                # Put keys in quotes. The '-' is for handling nagative numbers
                elif (c.isalnum() or c == '-') and not inside_quotes:
                    processed_content += '"' + c
                    c = next(file_content_it)
                    while c.isalnum():
                        processed_content += c
                        c = next(file_content_it)
                    processed_content += '"' + c
                # Remove control characters
                elif c < chr(32):
                    processed_content += ' '
                # Handle escaped characters
                elif c == '\\':
                    processed_content += c
                    c = next(file_content_it)
                    processed_content += c
                else:
                    processed_content += c
            songbook = json.loads(processed_content.strip())
            # Get song array
            songs = songbook['Songs']
            self.import_wizard.progress_bar.setMaximum(len(songs))
            songbook_name = songbook['Text']
            media_path = Path('..', 'Audio')
            for song in songs:
                self.song_book_name = songbook_name
                if 'Text' in song:
                    self.title = song['Text']
                composer = None
                author = None
                if 'Composer' in song:
                    composer = song['Composer']
                if 'Author' in song:
                    author = song['Author']
                if author and composer == author:
                    self.add_author(author, AuthorType.WordsAndMusic)
                else:
                    if author:
                        self.add_author(author, AuthorType.Words)
                    if composer:
                        self.add_author(composer, AuthorType.Music)
                if 'Copyright' in song:
                    self.add_copyright(song['Copyright'].replace('\n', ' ').strip())
                if 'CCLI' in song:
                    self.ccli_number = song['CCLI']
                if 'Theme' in song:
                    self.topics = song['Theme'].splitlines()
                if 'AudioFile' in song:
                    self.add_media_file(media_path / song['AudioFile'])
                if 'Memo1' in song:
                    self.add_comment(song['Memo1'])
                if 'Memo2' in song:
                    self.add_comment(song['Memo2'])
                if 'Memo3' in song:
                    self.add_comment(song['Memo3'])
                for verse in song['Verses']:
                    if 'Text' not in verse:
                        continue
                    verse_text = verse['Text']
                    # Strip out chords if set up to
                    if not self.settings.value('songs/enable chords') or \
                            self.settings.value('songs/disable chords import'):
                        verse_text = re.sub(r'\[.*?\]', '', verse_text)
                    self.add_verse(verse_text, 'v')
                if not self.finish():
                    self.log_error('Could not import {title}'.format(title=self.title))
        except Exception as e:
            self.log_error(self.import_source.name,
                           translate('SongsPlugin.VideoPsalmImport', 'Error: {error}').format(error=e))
