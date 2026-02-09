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

import logging
import re
from shutil import copyfile

from PySide6 import QtCore

from openlp.core.common import normalize_str
from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import translate
from openlp.core.common.path import create_paths
from openlp.core.common.registry import Registry
from openlp.core.widgets.wizard import WizardStrings
from openlp.plugins.songs.lib import VerseType, clean_song
from openlp.plugins.songs.lib.db import Author, AuthorType, SongBook, MediaFile, Song, Topic
from openlp.plugins.songs.lib.openlyricsxml import SongXML
from openlp.plugins.songs.lib.ui import SongStrings


log = logging.getLogger(__name__)


class SongImport(QtCore.QObject):
    """
    Helper class for import a song from a third party source into OpenLP

    This class just takes the raw strings, and will work out for itself
    whether the authors etc already exist and add them or refer to them
    as necessary
    """
    @staticmethod
    def is_valid_source(import_source):
        """
        Override this method to validate the source prior to import.
        """
        return True

    def __init__(self, manager, **kwargs):
        """
        Initialise and create defaults for properties

        :param manager: An instance of a SongManager, through which all database access is performed.
        :param kwargs:
        """
        self.manager = manager
        QtCore.QObject.__init__(self)
        if 'file_path' in kwargs:
            self.import_source = kwargs['file_path']
        elif 'file_paths' in kwargs:
            self.import_source = kwargs['file_paths']
        elif 'folder_path' in kwargs:
            self.import_source = kwargs['folder_path']
        else:
            raise KeyError('Keyword arguments "file_path[s]" or "folder_path" not supplied.')
        log.debug(self.import_source)
        self.import_wizard = None
        self.song = None
        self.stop_import_flag = False
        self.set_defaults()
        Registry().register_function('openlp_stop_wizard', self.stop_import)
        self.settings = Registry().get('settings')

    def set_defaults(self):
        """
        Create defaults for properties - call this before each song
        if importing many songs at once to ensure a clean beginning
        """
        self.title = ''
        self.song_number = ''
        self.alternate_title = ''
        self.copyright = ''
        self.comments = ''
        self.theme_name = ''
        self.ccli_number = ''
        self.authors = []
        self.topics = []
        self.media_files = []
        self.song_book_name = ''
        self.song_book_pub = ''
        self.verse_order_list_generated_useful = False
        self.verse_order_list_generated = []
        self.verse_order_list = []
        self.verses = []
        self.verse_counts = {}
        self.copyright_string = translate('SongsPlugin.SongImport', 'copyright')

    def log_error(self, file_path, reason=SongStrings().SongIncomplete):
        """
        This should be called, when a song could not be imported.

        :param file_path: This should be the file path if ``self.import_source`` is a list with different files. If it
            is not a list, but a single file (for instance a database), then this should be the song's title.
        :param reason: The reason why the import failed. The string should be as informative as possible.
        """
        self.set_defaults()
        if self.import_wizard is None:
            return
        if self.import_wizard.error_report_text_edit.isHidden():
            self.import_wizard.error_report_text_edit.setText(
                translate('SongsPlugin.SongImport', 'The following songs could not be imported:'))
            self.import_wizard.error_report_text_edit.setVisible(True)
            self.import_wizard.error_copy_to_button.setVisible(True)
            self.import_wizard.error_save_to_button.setVisible(True)
        self.import_wizard.error_report_text_edit.append('- {path} ({error})'.format(path=file_path, error=reason))

    def stop_import(self):
        """
        Sets the flag for importers to stop their import
        """
        log.debug('Stopping songs import')
        self.stop_import_flag = True

    def register(self, import_wizard):
        self.import_wizard = import_wizard

    def process_song_text(self, text):
        """
        Process the song text from import

        :param text: Some text
        """
        verse_texts = text.split('\n\n')
        for verse_text in verse_texts:
            if verse_text.strip() != '':
                self.process_verse_text(verse_text.strip())

    def process_verse_text(self, text):
        """
        Process the song verse text from import

        :param text: Some text
        """
        lines = text.split('\n')
        if text.lower().find(self.copyright_string) >= 0 or text.find(str(SongStrings().CopyrightSymbol)) >= 0:
            copyright_found = False
            for line in lines:
                if (copyright_found or line.lower().find(self.copyright_string) >= 0 or
                        line.find(str(SongStrings().CopyrightSymbol)) >= 0):
                    copyright_found = True
                    self.add_copyright(line)
                else:
                    self.parse_author(line)
            return
        if len(lines) == 1:
            self.parse_author(lines[0])
            return
        if not self.title:
            self.title = lines[0]
        self.add_verse(text)

    def parse_song_book_name_and_number(self, book_and_number):
        """
        Build the book name and song number from a single string
        """
        # Turn 'Spring Harvest 1997 No. 34' or
        # 'Spring Harvest 1997 (34)' or
        # 'Spring Harvest 1997 34' into
        # Book name:'Spring Harvest 1997' and
        # Song number: 34
        #
        # Also, turn 'NRH231.' into
        # Book name:'NRH' and
        # Song number: 231
        book_and_number = book_and_number.strip()
        if not book_and_number:
            return
        book_and_number = book_and_number.replace('No.', ' ')
        if ' ' in book_and_number:
            parts = book_and_number.split(' ')
            self.song_book_name = ' '.join(parts[:-1])
            self.song_number = parts[-1].strip('()')
        else:
            # Something like 'ABC123.'
            match = re.match(r'(.*\D)(\d+)', book_and_number)
            match_num = re.match(r'(\d+)', book_and_number)
            if match:
                # Name and number
                self.song_book_name = match.group(1)
                self.song_number = match.group(2)
            # These last two cases aren't tested yet, but
            # are here in an attempt to do something vaguely
            # sensible if we get a string in a different format
            elif match_num:
                # Number only
                self.song_number = match_num.group(1)
            else:
                # Name only
                self.song_book_name = book_and_number

    def add_comment(self, comment):
        """
        Build the comments field
        """
        if self.comments.find(comment) >= 0:
            return
        if comment:
            self.comments += comment.strip() + '\n'

    def add_copyright(self, copyright):
        """
        Build the copyright field
        """
        if self.copyright.find(copyright) >= 0:
            return
        if self.copyright:
            self.copyright += ' '
        self.copyright += copyright

    def _check_for_author_prefix(self, author, default_type):
        """
        Detect if the author type is prefixed the author name. Looks for the prefix in entire string, in case multiple
        authors are listed, each prefixed with a type.
        :param author: String with author(s) to search for predefined prefixes
        :param default_type: The default or expected author type to use
        :return: True if a prefix was found, meaning the author will be added from this method. Else False is returned,
                 and the caller must add the author.
        """
        author_low = author.lower()
        music_prefixes = ['music by', translate('SongsPlugin.SongImport', 'music by').lower(),
                          'music:', translate('SongsPlugin.SongImport', 'music:').lower(),
                          'arranged by', translate('SongsPlugin.SongImport', 'arranged by').lower(),
                          'arranged:', translate('SongsPlugin.SongImport', 'arranged:').lower(),
                          'composed by', translate('SongsPlugin.SongImport', 'composed by').lower(),
                          'composer:', translate('SongsPlugin.SongImport', 'composer:').lower()]
        words_prefixes = ['words by', translate('SongsPlugin.SongImport', 'words by').lower(),
                          'words:', translate('SongsPlugin.SongImport', 'words:').lower(),
                          'lyrics by', translate('SongsPlugin.SongImport', 'lyrics by').lower(),
                          'lyrics:', translate('SongsPlugin.SongImport', 'lyrics:').lower(),
                          'written by', translate('SongsPlugin.SongImport', 'written by').lower(),
                          'writer:', translate('SongsPlugin.SongImport', 'writer:').lower(),
                          'authored by', translate('SongsPlugin.SongImport', 'authored by').lower(),
                          'author:', translate('SongsPlugin.SongImport', 'author:').lower()]
        translation_prefixes = ['translated by', translate('SongsPlugin.SongImport', 'translated by').lower(),
                                'translation:', translate('SongsPlugin.SongImport', 'translation:').lower()]
        prefix_map = [(music_prefixes, AuthorType.Music), (words_prefixes, AuthorType.Words),
                      (translation_prefixes, AuthorType.Translation)]
        for prefixes, prefix_type in prefix_map:
            for prefix in prefixes:
                idx = author_low.find(prefix)
                if idx == -1:
                    pass  # no hit
                elif idx == 0:
                    # found the prefix right at the start
                    author_without_prefix = author[len(prefix):].strip()
                    self.parse_author(author_without_prefix, prefix_type)
                    return True
                else:
                    # found the prefix "inside" the string
                    author_before_prefix = author[0:idx].strip()
                    author_after_prefix = author[idx + len(prefix):].strip()
                    # the type of the authors before the "prefix" must be of the type provided in the method parameter
                    self.parse_author(author_before_prefix, default_type)
                    self.parse_author(author_after_prefix, prefix_type)
                    return True
        return False

    def parse_author(self, text, type=None):
        """
        Add the author. OpenLP stores them individually so split by 'and', '&' comma and semicolon.
        TODO: check for 'Mr and Mrs Smith' and turn it to 'Mr Smith' and 'Mrs Smith'.
        """
        # check if the given text is prefixed with the author type, in which case the adding of the author will
        # be done in _check_for_author_prefix
        if self._check_for_author_prefix(text, type):
            return
        for author in text.split(','):
            authors = re.split(r';|&| and |/|\|', author)
            for i in range(len(authors)):
                author2 = authors[i].strip()
                if author2.find(' ') == -1 and i < len(authors) - 1:
                    author2 = author2 + ' ' + authors[i + 1].strip().split(' ')[-1]
                if author2.endswith('.'):
                    author2 = author2[:-1]
                if author2:
                    if type:
                        self.add_author(author2, type)
                    else:
                        self.add_author(author2)

    def add_author(self, author, type=None):
        """
        Add an author to the list
        """
        if (author, type) in self.authors:
            return
        self.authors.append((author, type))

    def add_media_file(self, file_path, weight=0):
        """
        Add a media file to the list
        """
        if file_path in [x[0] for x in self.media_files]:
            return
        self.media_files.append((file_path, weight))

    def add_verse(self, verse_text, verse_def='v', lang=None):
        """
        Add a verse. This is the whole verse, lines split by \\n. It will also
        attempt to detect duplicates. In this case it will just add to the verse
        order.

        :param verse_text:  The text of the verse.
        :param verse_def: The verse tag can be v1/c1/b etc, or 'v' and 'c' (will count the
            verses/choruses itself) or None, where it will assume verse.
        :param lang: The language code (ISO-639) of the verse, for example *en* or *de*.
        """
        for (old_verse_def, old_verse, old_lang) in self.verses:
            if old_verse.strip() == verse_text.strip():
                self.verse_order_list_generated.append(old_verse_def)
                self.verse_order_list_generated_useful = True
                return
        if verse_def[0] in self.verse_counts:
            self.verse_counts[verse_def[0]] += 1
        else:
            self.verse_counts[verse_def[0]] = 1
        if len(verse_def) == 1:
            verse_def += str(self.verse_counts[verse_def[0]])
        elif int(verse_def[1:]) > self.verse_counts[verse_def[0]]:
            self.verse_counts[verse_def[0]] = int(verse_def[1:])
        self.verses.append([verse_def, verse_text.rstrip(), lang])
        # A verse_def refers to all verses with that name, adding it once adds every instance, so do not add if already
        # used.
        if verse_def not in self.verse_order_list_generated:
            self.verse_order_list_generated.append(verse_def)

    def repeat_verse(self, verse_def=None):
        """
        Repeat the verse with the given verse_def or default to repeating the previous verse in the verse order

        :param verse_def: verse_def of the verse to be repeated
        """
        if self.verse_order_list_generated:
            if verse_def:
                # If the given verse_def is only one char (like 'v' or 'c'), postfix it with '1'
                if len(verse_def) == 1:
                    verse_def += '1'
                if verse_def in self.verse_order_list_generated:
                    self.verse_order_list_generated.append(verse_def)
                else:
                    log.warning('Trying to add unknown verse_def "%s"' % verse_def)
            else:
                self.verse_order_list_generated.append(self.verse_order_list_generated[-1])
            self.verse_order_list_generated_useful = True

    def check_complete(self):
        """
        Check the mandatory fields are entered (i.e. title and a verse)
        Author not checked here, if no author then "Author unknown" is automatically added
        """
        if not self.title or not self.verses:
            return False
        else:
            return True

    def finish(self, temporary_flag=False):
        """
        All fields have been set to this song. Write the song to disk.

        :param temporary_flag: should this song be marked as temporary in the db (default=False)
        """
        if not self.check_complete():
            self.set_defaults()
            return False
        log.info('committing song {title} to database'.format(title=self.title))
        song = Song()
        song.title = self.title
        if self.import_wizard is not None:
            self.import_wizard.increment_progress_bar(WizardStrings.ImportingType.format(source=song.title))
        song.alternate_title = self.alternate_title
        # Values will be set when cleaning the song.
        song.search_title = ''
        song.search_lyrics = ''
        song.verse_order = ''
        song.song_number = self.song_number
        verses_changed_to_other = {}
        sxml = SongXML()
        other_count = 1
        for (verse_def, verse_text, lang) in self.verses:
            if verse_def[0].lower() in VerseType.tags:
                verse_tag = verse_def[0].lower()
            else:
                new_verse_def = '{tag}{count:d}'.format(tag=VerseType.tags[VerseType.Other], count=other_count)
                verses_changed_to_other[verse_def] = new_verse_def
                other_count += 1
                verse_tag = VerseType.tags[VerseType.Other]
                log.info('Versetype {old} changing to {new}'.format(old=verse_def, new=new_verse_def))
                verse_def = new_verse_def
            sxml.add_verse_to_lyrics(verse_tag, verse_def[1:], normalize_str(verse_text), lang)
        song.lyrics = str(sxml.extract_xml(), 'utf-8')
        if not self.verse_order_list and self.verse_order_list_generated_useful:
            self.verse_order_list = self.verse_order_list_generated
        self.verse_order_list = [verses_changed_to_other.get(v, v) for v in self.verse_order_list]
        song.verse_order = ' '.join(self.verse_order_list)
        song.copyright = self.copyright
        song.comments = self.comments
        song.theme_name = self.theme_name
        song.ccli_number = self.ccli_number
        for author_text, author_type in self.authors:
            author = self.manager.get_object_filtered(Author, Author.display_name == author_text)
            if not author:
                author = Author(display_name=author_text,
                                last_name=author_text.split(' ')[-1],
                                first_name=' '.join(author_text.split(' ')[:-1]))
            song.add_author(author, author_type)
        if self.song_book_name:
            song_book = self.manager.get_object_filtered(SongBook, SongBook.name == self.song_book_name)
            if song_book is None:
                song_book = SongBook(name=self.song_book_name, publisher=self.song_book_pub)
            song.add_songbook_entry(song_book, song.song_number)
        for topic_text in self.topics:
            if not topic_text:
                continue
            topic = self.manager.get_object_filtered(Topic, Topic.name == topic_text)
            if topic is None:
                topic = Topic(name=topic_text)
            song.topics.append(topic)
        song.temporary = temporary_flag
        # We need to save the song now, before adding the media files, so that
        # we know where to save the media files to.
        clean_song(self.manager, song)
        self.manager.save_object(song)
        # Now loop through the media files, copy them to the correct location,
        # and save the song again.
        for file_path, weight in self.media_files:
            media_file = self.manager.get_object_filtered(MediaFile, MediaFile.file_path == file_path)
            if not media_file:
                if file_path.parent:
                    file_path = self.copy_media_file(song.id, file_path)
                song.media_files.append(MediaFile(file_path=file_path, weight=weight))
        self.manager.save_object(song)
        self.set_defaults()
        return song.id

    def copy_media_file(self, song_id, file_path):
        """
        This method copies the media file to the correct location and returns
        the new file location.

        :param song_id:
        :param pathlib.Path file_path: The file to copy.
        :return: The new location of the file
        :rtype: pathlib.Path
        """
        if not hasattr(self, 'save_path'):
            self.save_path = AppLocation.get_section_data_path(self.import_wizard.plugin.name) / 'audio' / str(song_id)
        create_paths(self.save_path)
        if self.save_path not in file_path.parents:
            old_path, file_path = file_path, self.save_path / file_path.name
            copyfile(old_path, file_path)
        return file_path
