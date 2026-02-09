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
The :mod:`chordpro` module provides the functionality for importing
ChordPro files into the current database.
"""
import logging
import re

from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.db import AuthorType


log = logging.getLogger(__name__)


class ChordProImport(SongImport):
    """
    The :class:`ChordProImport` class provides OpenLP with the ability to import ChordPro files.

    This importer is based on the information available on these webpages:

    - https://www.chordpro.org
    - http://webchord.sourceforge.net/tech.html
    - http://www.vromans.org/johan/projects/Chordii/chordpro/
    - http://www.tenbyten.com/software/songsgen/help/HtmlHelp/files_reference.htm
    - http://linkesoft.com/songbook/chordproformat.html
    """
    def do_import(self):
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            with file_path.open('rt', encoding='utf8') as song_file:
                self.do_import_file(song_file)

    def do_import_file(self, song_file):
        """
        Imports the songs in the given file
        :param song_file: The file object to be imported from.
        """
        self.set_defaults()
        # Loop over the lines of the file
        try:
            file_content = song_file.read()
        except UnicodeDecodeError:
            self.log_error(song_file.name, translate('SongsPlugin.ChordProFileImport',
                                                     'The file contains unreadable characters.'))
            return
        current_verse = ''
        current_verse_type = 'v'
        skip_block = False
        chorus_added = []
        for line in file_content.splitlines():
            line = line.rstrip()
            # Detect tags
            if line.startswith('{'):
                tag_name, tag_value = self.parse_tag(line)
                # Detect which tag
                if tag_name in ['title', 't']:
                    self.title = tag_value
                elif tag_name in ['subtitle', 'su', 'st']:
                    self.alternate_title = tag_value
                elif tag_name == 'composer':
                    self.parse_author(tag_value, AuthorType.Music)
                elif tag_name in ['lyricist', 'author']:  # author is not an official directive
                    self.parse_author(tag_value, AuthorType.Words)
                elif tag_name == 'artist':
                    self.parse_author(tag_value)
                elif tag_name == 'meta':
                    meta_tag_name, meta_tag_value = tag_value.split(' ', 1)
                    # Skip, if no value
                    if not meta_tag_value:
                        continue
                    # The meta-tag can contain anything. We check for the ones above and a few more
                    if meta_tag_name in ['title', 't']:
                        self.title = meta_tag_value
                    elif meta_tag_name in ['subtitle', 'su', 'st']:
                        self.alternate_title = meta_tag_value
                    elif meta_tag_name == 'composer':
                        self.parse_author(meta_tag_value, AuthorType.Music)
                    elif meta_tag_name in ['lyricist', 'author']:
                        self.parse_author(meta_tag_value, AuthorType.Words)
                    elif meta_tag_name == 'artist':
                        self.parse_author(meta_tag_value)
                    elif meta_tag_name in ['topic', 'topics']:
                        for topic in meta_tag_value.split(','):
                            self.topics.append(topic.strip())
                    elif 'ccli' in meta_tag_name:
                        self.ccli_number = meta_tag_value
                elif tag_name == 'ccli':
                    self.ccli_number = tag_value
                elif tag_name == 'copyright':
                    self.add_copyright(tag_value)
                elif tag_name in ['comment', 'c', 'comment_italic', 'ci', 'comment_box', 'cb']:
                    # Detect if the comment is used as a verse type marker
                    lower_tag_value = tag_value.lower()
                    if lower_tag_value.startswith(('chorus', 'verse', 'bridge', 'ending')):
                        if current_verse.strip():
                            self.add_chordpro_verse(current_verse.rstrip(), current_verse_type)
                            current_verse_type = 'v'
                            current_verse = ''
                        # Detect if the comment is used as a chorus repeat marker
                        if lower_tag_value.startswith('chorus'):
                            if lower_tag_value in chorus_added:
                                self.repeat_verse('c%d' % (chorus_added.index(lower_tag_value) + 1))
                            else:
                                chorus_added.append(lower_tag_value)
                                current_verse_type = 'c'
                        elif lower_tag_value.startswith('verse'):
                            current_verse_type = 'v'
                        elif lower_tag_value.startswith('bridge'):
                            current_verse_type = 'b'
                        elif lower_tag_value.startswith('ending'):
                            current_verse_type = 'e'
                    else:
                        self.add_comment(tag_value)
                elif tag_name in ['start_of_chorus', 'soc']:
                    current_verse_type = 'c'
                elif tag_name in ['end_of_chorus', 'eoc']:
                    self.add_chordpro_verse(current_verse.rstrip(), current_verse_type)
                    chorus_added.append('chorus')
                    current_verse_type = 'v'
                    current_verse = ''
                elif tag_name in ['start_of_tab', 'sot']:
                    if current_verse.strip():
                        self.add_chordpro_verse(current_verse.rstrip(), current_verse_type)
                        current_verse_type = 'v'
                        current_verse = ''
                    skip_block = True
                elif tag_name in ['end_of_tab', 'eot']:
                    skip_block = False
                elif tag_name in ['new_song', 'ns']:
                    # A new song starts below this tag
                    if self.verses and self.title:
                        if current_verse.strip():
                            self.add_chordpro_verse(current_verse.rstrip(), current_verse_type)
                        if not self.finish():
                            self.log_error(song_file.name)
                    self.set_defaults()
                    current_verse_type = 'v'
                    current_verse = ''
                else:
                    # Unsupported tag
                    log.debug('unsupported tag: %s' % line)
            elif line.startswith('#'):
                # Found a comment line, which is ignored...
                continue
            elif line == "['|]":
                # Found a vertical bar
                continue
            elif line.startswith('CCLI') or line.startswith('©'):
                # Found the CCLI footer or a copyright footer, stop here.
                break
            else:
                if skip_block:
                    continue
                elif line == '' and current_verse.strip() and current_verse_type != 'c':
                    self.add_chordpro_verse(current_verse.rstrip(), current_verse_type)
                    current_verse_type = 'v'
                    current_verse = ''
                else:
                    if current_verse.strip() == '':
                        current_verse = line + '\n'
                    else:
                        current_verse += line + '\n'
        if current_verse.strip():
            self.add_chordpro_verse(current_verse.rstrip(), current_verse_type)
        # if no title was in directives, get it from the first line
        if not self.title and self.verses:
            (verse_def, verse_text, lang) = self.verses[0]
            # strip any chords from the title
            self.title = re.sub(r'\[.*?\]', '', verse_text.split('\n')[0])
            # strip the last char if it a punctuation
            self.title = re.sub(r'[^\w\s]$', '', self.title)
        if not self.finish():
            self.log_error(song_file.name)

    def parse_tag(self, line):
        """
        :param line: Line with the tag to be parsed
        :return: A tuple with tag name and tag value (if any)
        """
        # Strip the first '}'
        line = line[1:].strip()
        colon_idx = line.find(':')
        # check if this is a tag without value
        if colon_idx < 0:
            # strip the final '}' and return the tag name
            return line[:-1], None
        tag_name = line[:colon_idx]
        tag_value = line[colon_idx + 1:-1].strip()
        return tag_name, tag_value

    def add_chordpro_verse(self, verse_text, verse_type):
        """
        Strip out chords if set up to.
        In some cases (noteably CCLI) spaces and dashes are inserted for readability,
        but they do not look good on display so remove them
        :param verse_text:
        :param verse_type:
        """
        if not self.settings.value('songs/enable chords') or self.settings.value('songs/disable chords import'):
            verse_text = re.sub(r'( +- +)?\[.*?\]( +- +)?', '', verse_text)
        else:
            verse_text = re.sub(r' +- +\[', '[', verse_text)
            verse_text = re.sub(r'\] +- +', ']', verse_text)
        self.add_verse(verse_text.rstrip(), verse_type)
