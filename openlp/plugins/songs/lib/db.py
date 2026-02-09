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
The :mod:`db` module provides the database and schema that is the backend for
the Songs plugin


The song database contains the following tables:

    * authors
    * authors_songs
    * media_files
    * media_files_songs
    * song_books
    * songs
    * songs_songbooks
    * songs_topics
    * topics

**authors** Table
    This table holds the names of all the authors. It has the following
    columns:

    * id
    * first_name
    * last_name
    * display_name

**authors_songs Table**
    This is a bridging table between the *authors* and *songs* tables, which
    serves to create a many-to-many relationship between the two tables. It
    has the following columns:

    * author_id
    * song_id
    * author_type

**media_files Table**
    * id
    * file_path
    * file_hash
    * type
    * weight

**song_books Table**
    The *song_books* table holds a list of books that a congregation gets
    their songs from, or old hymnals now no longer used. This table has the
    following columns:

    * id
    * name
    * publisher

**songs Table**
    This table contains the songs, and each song has a list of attributes.
    The *songs* table has the following columns:

    * id
    * title
    * alternate_title
    * lyrics
    * verse_order
    * copyright
    * comments
    * ccli_number
    * theme_name
    * search_title
    * search_lyrics

**songs_songsbooks Table**
    This is a mapping table between the *songs* and the *song_books* tables. It has the following columns:

    * songbook_id
    * song_id
    * entry  # The song number, like 120 or 550A

**songs_topics Table**
    This is a bridging table between the *songs* and *topics* tables, which
    serves to create a many-to-many relationship between the two tables. It
    has the following columns:

    * song_id
    * topic_id

**topics Table**
    The topics table holds a selection of topics that songs can cover. This
    is useful when a worship leader wants to select songs with a certain
    theme. This table has the following columns:

    * id
    * name
"""
from typing import Optional

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, declarative_base, reconstructor, relationship
from sqlalchemy.sql.expression import func, text
from sqlalchemy.types import Boolean, DateTime, Integer, Unicode, UnicodeText

from openlp.core.common.i18n import get_natural_key, translate
from openlp.core.db.types import PathType
from openlp.core.db.helpers import init_db
from openlp.core.lib import create_separated_list


Base = declarative_base()


songs_topics_table = Table(
    'songs_topics', Base.metadata,
    Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id'), primary_key=True)
)


sort_key_cache = {}
song_detail_cache = {}


class AuthorType(object):
    """
    Enumeration for Author
    They are defined by OpenLyrics: http://openlyrics.info/dataformat.html#authors

    The 'words+music' type is not an official type, but is provided for convenience.
    """
    NoType = ''
    Words = 'words'
    Music = 'music'
    WordsAndMusic = 'words+music'
    Translation = 'translation'
    SortedTypes = [
        NoType,
        Words,
        Music,
        WordsAndMusic,
        Translation
    ]

    @classmethod
    def get_translated_type(cls, author_type: str) -> str:
        if author_type == cls.NoType:
            return ''
        elif author_type == cls.Words:
            return translate('SongsPlugin.AuthorType', 'Words',
                             'Author who wrote the lyrics of a song')
        elif author_type == cls.Music:
            return translate('SongsPlugin.AuthorType', 'Music',
                             'Author who wrote the music of a song')
        elif author_type == cls.WordsAndMusic:
            return translate('SongsPlugin.AuthorType', 'Words and Music',
                             'Author who wrote both lyrics and music of a song')
        elif author_type == cls.Translation:
            return translate('SongsPlugin.AuthorType', 'Translation',
                             'Author who translated the song')

        raise ValueError(f'Unknown author type: {author_type}')

    @classmethod
    def get_translated_types(cls):
        return {
            cls.NoType: cls.get_translated_type(cls.NoType),
            cls.Words: cls.get_translated_type(cls.Words),
            cls.Music: cls.get_translated_type(cls.Music),
            cls.WordsAndMusic: cls.get_translated_type(cls.WordsAndMusic),
            cls.Translation: cls.get_translated_type(cls.Translation)
        }

    @classmethod
    def get_translated_types_list(cls):
        return [
            cls.get_translated_type(cls.NoType),
            cls.get_translated_type(cls.Words),
            cls.get_translated_type(cls.Music),
            cls.get_translated_type(cls.WordsAndMusic),
            cls.get_translated_type(cls.Translation)
        ]

    @staticmethod
    def from_translated_text(translated_type):
        """
        Get the AuthorType from a translated string.
        :param translated_type: Translated Author type.
        """
        for key, value in AuthorType.get_translated_types().items():
            if value == translated_type:
                return key
        return AuthorType.NoType


class Author(Base):
    """
    Author model
    """
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    first_name = Column(Unicode(128))
    last_name = Column(Unicode(128))
    display_name = Column(Unicode(255), index=True, nullable=False)

    authors_songs = relationship('AuthorSong', back_populates='author')

    def __init__(self, **kwargs):
        if 'first_name' in kwargs and isinstance(kwargs['first_name'], str):
            kwargs['first_name'] = self._normalize_name(kwargs['first_name'])

        if 'last_name' in kwargs and isinstance(kwargs['last_name'], str):
            kwargs['last_name'] = self._normalize_name(kwargs['last_name'])

        if 'display_name' in kwargs and isinstance(kwargs['display_name'], str):
            kwargs['display_name'] = self._normalize_name(kwargs['display_name'])

        super().__init__(**kwargs)

    def _normalize_name(self, name):
        """Remove all newline characters and carriage return characters"""
        normalized_name = name.replace('\n', ' ').replace('\r', '')
        return normalized_name

    def get_display_name(self, author_type: Optional[str] = None) -> str:
        """Determine the display name"""
        if author_type:
            return "{name} ({author})".format(name=self.display_name,
                                              author=AuthorType.get_translated_type(author_type))
        return self.display_name

    @property
    def songs(self):
        """All the songs associated with this author"""
        return [author_song.song for author_song in self.authors_songs]


class AuthorSong(Base):
    """
    Relationship between Authors and Songs (many to many).
    Need to define this relationship table explicit to get access to the
    Association Object (author_type).
    http://docs.sqlalchemy.org/en/latest/orm/relationships.html#association-object
    """
    __tablename__ = 'authors_songs'

    author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.id'), primary_key=True)
    author_type = Column(Unicode(255), primary_key=True, nullable=False, server_default=text('""'))

    author = relationship('Author', back_populates='authors_songs')
    song = relationship('Song', back_populates='authors_songs')


class SongBook(Base):
    """
    SongBook model
    """
    __tablename__ = 'song_books'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), nullable=False)
    publisher = Column(Unicode(128))

    songbook_entries = relationship('SongBookEntry', back_populates='songbook')

    @property
    def songs(self):
        """
        A property to return the songs associated with this book.
        """
        return [sbe.song for sbe in self.songbook_entries]

    def __repr__(self):
        return f'<SongBook id="{self.id}" name="{self.name}" publisher="{self.publisher}">'


class MediaFile(Base):
    """
    MediaFile model
    """
    __tablename__ = 'media_files'

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.id'), default=None)
    file_path = Column(PathType, nullable=False)
    file_hash = Column(Unicode(128), nullable=False)
    type = Column(Unicode(64), nullable=False, default='audio')
    weight = Column(Integer, default=0)

    songs = relationship('Song', back_populates='media_files')


class Song(Base):
    """
    Song model
    """
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(255), nullable=False)
    alternate_title = Column(Unicode(255))
    lyrics = Column(UnicodeText, nullable=False)
    verse_order = Column(Unicode(128))
    copyright = Column(Unicode(255))
    comments = Column(UnicodeText)
    ccli_number = Column(Unicode(64))
    theme_name = Column(Unicode(128))
    search_title = Column(Unicode(255), index=True, nullable=False)
    search_lyrics = Column(UnicodeText, nullable=False)
    create_date = Column(DateTime, default=func.now())
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now())
    temporary = Column(Boolean, default=False)
    is_favourite = Column(Boolean, default=False)

    authors_songs = relationship('AuthorSong', back_populates='song', cascade='all, delete-orphan')
    media_files = relationship('MediaFile', back_populates='songs', order_by='MediaFile.weight')
    songbook_entries = relationship('SongBookEntry', back_populates='song', cascade='all, delete-orphan')
    topics = relationship('Topic', back_populates='songs', secondary=songs_topics_table)

    @hybrid_property
    def authors(self):
        return [author_song.author for author_song in self.authors_songs]

    @reconstructor
    def init_on_load(self, force_song_detail_recalculation=False):
        """
        Precompute and cache performance-sensitive values:
        - A locale-aware natural sort key based on the song title.
        - A display text for the song list, composed of author names or the title.

        This avoids repeated computation during sorting and rendering.
        """
        sort_key = sort_key_cache.get(self.title)
        if sort_key is None:
            sort_key = get_natural_key(self.title)
            sort_key_cache[self.title] = sort_key
        self.sort_key = sort_key

        key = f'{self.id}-{self.last_modified}'
        song_detail = song_detail_cache.get(key)
        if song_detail is None or force_song_detail_recalculation:
            author_list = [author.display_name for author in self.authors]
            text = create_separated_list(author_list) if author_list else self.title
            if len(self.media_files) > 0:
                song_detail = f'{self.title} (A) ({text})'
            else:
                song_detail = '{title} ({author})'.format(title=self.title, author=text)
            song_detail_cache[key] = song_detail
        self.song_detail = song_detail

    def add_author(self, author, author_type=None):
        """
        Add an author to the song if it not yet exists

        :param author: Author object
        :param author_type: AuthorType constant or None
        """
        for author_song in self.authors_songs:
            if author_song.author == author and author_song.author_type == author_type:
                return
        new_author_song = AuthorSong(author=author, author_type=author_type)
        new_author_song.author = author
        new_author_song.author_type = author_type
        self.authors_songs.append(new_author_song)

    def remove_author(self, author, author_type=None):
        """
        Remove an existing author from the song

        :param author: Author object
        :param author_type: AuthorType constant or None
        """
        for author_song in self.authors_songs:
            if author_song.author == author and author_song.author_type == author_type:
                self.authors_songs.remove(author_song)
                return

    def add_songbook_entry(self, songbook, entry):
        """
        Add a Songbook Entry to the song if it not yet exists

        :param songbook: Name of the Songbook.
        :param entry: Entry in the Songbook (usually a number)
        """
        for songbook_entry in self.songbook_entries:
            if songbook_entry.songbook.name == songbook.name and songbook_entry.entry == entry:
                return

        new_songbook_entry = SongBookEntry()
        if session := Session.object_session(self):
            # Session is None in the tests
            session.add(songbook)

        new_songbook_entry.songbook = songbook
        new_songbook_entry.entry = entry
        self.songbook_entries.append(new_songbook_entry)


class SongBookEntry(Base):
    """
    SongBookEntry model
    """
    __tablename__ = 'songs_songbooks'

    songbook_id = Column(Integer, ForeignKey('song_books.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('songs.id'), primary_key=True)
    entry = Column(Unicode(255), primary_key=True, nullable=False)

    songbook = relationship('SongBook', back_populates='songbook_entries')
    song = relationship('Song', back_populates='songbook_entries')

    def __repr__(self):
        return SongBookEntry.get_display_name(self.songbook.name, self.entry)

    @staticmethod
    def get_display_name(songbook_name, entry):
        if entry:
            return "{name} #{entry}".format(name=songbook_name, entry=entry)
        return songbook_name


class Topic(Base):
    """
    Topic model
    """
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), index=True, nullable=False)

    songs = relationship('Song', back_populates='topics', secondary=songs_topics_table)


def init_schema(url):
    """
    Setup the songs database connection and initialise the database schema.

    :param url: The database to setup

    """
    session, metadata = init_db(url, base=Base)
    metadata.create_all(bind=metadata.bind, checkfirst=True)
    return session
