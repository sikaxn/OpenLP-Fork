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
The :mod:`openlp` module provides the functionality for importing OpenLP
song databases into the current installation database.
"""
import logging
from pathlib import Path
from sqlite3 import Row, connect as sqlite3_connect

from openlp.core.common import sha256_file_hash
from openlp.core.common.i18n import translate
from openlp.core.widgets.wizard import WizardStrings
from openlp.plugins.songs.lib import clean_song
from openlp.plugins.songs.lib.db import Author, SongBook, MediaFile, Song, Topic

from .songimport import SongImport

log = logging.getLogger(__name__)


SONG_AUTHORS = 'SELECT * FROM authors AS a JOIN authors_songs AS s ON a.id = s.author_id WHERE s.song_id = ?'
SONG_TOPICS = 'SELECT t.name AS name FROM topics AS t JOIN songs_topics AS st ON t.id = st.topic_id ' \
              'WHERE st.song_id = ?'
SONG_BOOKS = 'SELECT b.name, b.publisher, e.entry FROM song_books AS b ' \
             'JOIN songs_songbooks AS e ON b.id = e.songbook_id WHERE e.song_id = ?'
SONG_MEDIA = 'SELECT * FROM media_files WHERE song_id = ?'


def does_table_exist(conn, table_name: str) -> bool:
    """Check if a table exists in the database"""
    res = conn.execute('SELECT name FROM sqlite_master WHERE type = "table" AND name = ?', (table_name,))
    return res.fetchone() is not None


def does_column_exist(conn, table_name: str, column_name: str) -> bool:
    """Check if a table exists in the database"""
    res = conn.execute(f'SELECT * FROM {table_name} LIMIT 1')
    return column_name in res.fetchone().keys()


class OpenLPSongImport(SongImport):
    """
    The :class:`OpenLPSongImport` class provides OpenLP with the ability to
    import song databases from other installations of OpenLP.
    """
    def __init__(self, manager, **kwargs):
        """
        Initialise the import.

        :param manager: The song manager for the running OpenLP installation.
        :param kwargs: The database providing the data to import.
        """
        super(OpenLPSongImport, self).__init__(manager, **kwargs)
        self.source_session = None

    def do_import(self, progress_dialog=None):
        """
        Run the import for an OpenLP version 2 song database.

        :param progress_dialog: The QProgressDialog used when importing songs from the FRW.
        """
        # Check the file type
        if self.import_source.suffix != '.sqlite':
            self.log_error(self.import_source, translate('SongsPlugin.OpenLPSongImport',
                                                         'Not a valid OpenLP 2 song database.'))
            return
        # Connect to the database
        conn = sqlite3_connect(self.import_source)
        conn.row_factory = Row
        # Check that we have some of the mandatory tables
        if not any([does_table_exist(conn, 'songs'), does_table_exist(conn, 'authors'),
                    does_table_exist(conn, 'topics'), does_table_exist(conn, 'song_books')]):
            self.log_error(self.import_source, translate('SongsPlugin.OpenLPSongImport',
                                                         'Not a valid OpenLP 2 song database.'))
            return
        # Determine the database structure
        has_media_files = does_table_exist(conn, 'media_files')
        has_songs_books = does_table_exist(conn, 'songs_songbooks')
        # has_authors_songs = does_table_exist(conn, 'authors_songs')
        # has_author_type = has_authors_songs and does_column_exist(conn, 'authors_songs', 'author_type')
        # Set up wizard
        if self.import_wizard:
            song_count = conn.execute('SELECT COUNT(id) AS song_count FROM songs').fetchone()
            self.import_wizard.progress_bar.setMaximum(song_count['song_count'])
        for song in conn.execute('SELECT * FROM songs'):
            new_song = Song()
            new_song.title = song['title']
            if 'alternate_title' in song.keys():
                new_song.alternate_title = song['alternate_title']
            else:
                old_titles = song['search_title'].split('@')
                if len(old_titles) > 1:
                    new_song.alternate_title = old_titles[1]
            # Transfer the values to the new song object
            new_song.search_title = ''
            new_song.search_lyrics = ''
            new_song.lyrics = song['lyrics']
            new_song.verse_order = song['verse_order']
            new_song.copyright = song['copyright']
            new_song.comments = song['comments']
            new_song.theme_name = song['theme_name']
            new_song.ccli_number = song['ccli_number']
            if 'song_number' in song.keys():
                new_song.song_number = song['song_number']
            # Find or create all the authors and add them to the new song object
            song_authors = conn.execute(SONG_AUTHORS, (song['id'],))
            for author in song_authors:
                existing_author = self.manager.get_object_filtered(Author,
                                                                   Author.display_name == author['display_name'])
                if not existing_author:
                    existing_author = Author(
                        first_name=author['first_name'],
                        last_name=author['last_name'],
                        display_name=author['display_name']
                    )
                # If this is a new database, we need to import the author_type too
                try:
                    author_type = author['author_type']
                except IndexError:
                    author_type = ''
                new_song.add_author(existing_author, author_type)
            # Find or create all the topics and add them to the new song object
            for topic in conn.execute(SONG_TOPICS, (song['id'],)):
                existing_topic = self.manager.get_object_filtered(Topic, Topic.name == topic['name'])
                if not existing_topic:
                    existing_topic = Topic(name=topic['name'])
                new_song.topics.append(existing_topic)
            # Find or create all the songbooks and add them to the new song object
            if has_songs_books:
                for entry in conn.execute(SONG_BOOKS, (song['id'],)):
                    existing_book = self.manager.get_object_filtered(SongBook, SongBook.name == entry['name'])
                    if not existing_book:
                        existing_book = SongBook(name=entry['name'], publisher=entry['publisher'])
                    new_song.add_songbook_entry(existing_book, entry['entry'])
            elif does_column_exist(conn, 'songs', 'book_id'):
                book = conn.execute('SELECT name, publisher FROM song_books WHERE id = ?', (song['book_id'],))
                existing_book = self.manager.get_object_filtered(SongBook, SongBook.name == book['name'])
                if not existing_book:
                    existing_book = SongBook(name=book['name'], publisher=book['publisher'])
                # Get the song_number from "songs" table "song_number" field. (This is db structure from 2.2.1)
                # If there's a number, add it to the song, otherwise it will be "".
                if 'song_number' in song.keys():
                    new_song.add_songbook_entry(existing_book, song['song_number'])
                else:
                    new_song.add_songbook_entry(existing_book, '')
            # Find or create all the media files and add them to the new song object
            if has_media_files:
                for media_file in conn.execute(SONG_MEDIA, (song['id'],)):
                    # Database now uses paths rather than strings for media files, and the key name has
                    # changed appropriately. This catches any databases using the old key name.
                    try:
                        media_path = media_file['file_path']
                    except (IndexError, KeyError):
                        media_path = Path(media_file['file_name'])
                    existing_media_file = self.manager.get_object_filtered(MediaFile,
                                                                           MediaFile.file_path == media_path)
                    if existing_media_file:
                        new_song.media_files.append(existing_media_file)
                    else:
                        if 'file_hash' in media_file.keys():
                            file_hash = media_file['file_hash']
                        else:
                            file_hash = sha256_file_hash(media_path)
                        new_song.media_files.append(MediaFile(file_path=media_path, file_hash=file_hash))
            clean_song(self.manager, new_song)
            self.manager.save_object(new_song)
            if progress_dialog:
                progress_dialog.setValue(progress_dialog.value() + 1)
                progress_dialog.setLabelText(WizardStrings.ImportingType.format(source=new_song.title))
            else:
                self.import_wizard.increment_progress_bar(WizardStrings.ImportingType.format(source=new_song.title))
            if self.stop_import_flag:
                break
        conn.close()
