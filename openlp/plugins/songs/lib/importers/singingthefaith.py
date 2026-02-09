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
The :mod:`singingthefaith` module provides the functionality for importing songs which are
exported from Singing The Faith - an Authorised songbook for the Methodist Church of
Great Britain."""

import logging
import re
from pathlib import Path

from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.core.common.applocation import AppLocation


log = logging.getLogger(__name__)


class SingingTheFaithImport(SongImport):
    """
    Import songs exported from SingingTheFaith
    """

    def __init__(self, manager, **kwargs):
        """
        Initialise the class.
        """
        super(SingingTheFaithImport, self).__init__(manager, **kwargs)
        self.hints_available = False
        self.checks_needed = True
        self.hint_line = {}
        self.hint_file_version = '0'
        self.hint_verse_order = ''
        self.hint_song_title = ''
        self.hint_comments = ''
        self.hint_ccli = ''
        self.hint_ignore_indent = False
        self.hint_songbook_number_in_title = False

    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        if not isinstance(self.import_source, list):
            return
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            # If this is backported to version 2.4 then do_import is called with a filename
            #  rather than a path object if called from the development version.
            # Check here to minimise differences between versions.
            if isinstance(file_path, str):
                song_file = open(file_path, 'rt', encoding='cp1251')
                self.do_import_file(song_file)
                song_file.close()
            else:
                with file_path.open('rt', encoding='cp1251') as song_file:
                    self.do_import_file(song_file)

    def do_import_file(self, file):
        """
        Process the SingingTheFaith file - pass in a file-like object, not a file path.
        """
        hints_file_name = 'singingthefaith-hints.tag'
        singing_the_faith_version = 1
        self.set_defaults()
        # Setup variables
        line_number = 0
        old_indent = 0
        # The chorus indent is how many spaces the chorus is indented - it might be 6,
        # but we test for >= and I do not know how consistent to formatting of the
        # exported songs is.
        chorus_indent = 5
        # Initialise the song title - the format of the title finally produced can be affected
        #  by the SongbookNumberInTitle option in the hints file
        song_title = 'STF000 -'
        song_number = '0'
        ccli = '0'
        current_verse = ''
        current_verse_type = 'v'
        current_verse_number = 1
        # Potentially we could try to track current chorus number to automatically handle
        # more than 1 chorus, currently unused.
        # current_chorus_number = 1
        has_chorus = False
        chorus_written = False
        auto_verse_order_ok = False
        copyright = ''
        # the check_flag is prepended to the title, removed if the import should be OK
        # all the songs which need manual editing should sort below all the OK songs
        check_flag = 'z'

        self.add_comment(
            'Imported with Singing The Faith Importer  v{no}'.format(no=singing_the_faith_version))

        # Get the file_song_number - so we can use it for hints
        filename = Path(file.name)
        song_number_file = filename.stem
        song_number_match = re.search(r'\d+', song_number_file)
        if song_number_match:
            song_number_file = song_number_match.group()

        # See if there is a hints file in the same location as the file
        dir_path = filename.parent
        hints_file_path = dir_path / hints_file_name
        try:
            with hints_file_path.open('r') as hints_file:
                hints_available = self.read_hints(hints_file, song_number_file)
        except FileNotFoundError:
            # Look for the hints file in the Plugins directory
            hints_file_path = AppLocation.get_directory(AppLocation.PluginsDir) / 'songs' / 'lib' / \
                'importers' / hints_file_name
            try:
                with hints_file_path.open('r') as hints_file:
                    hints_available = self.read_hints(hints_file, song_number_file)
            except FileNotFoundError:
                hints_available = False

        try:
            for line in file:
                line_number += 1
                # Strip out leftover formatting (\i and \b)
                line = line.replace('\\i', '')
                line = line.replace('\\b', '')
                if hints_available and str(line_number) in self.hint_line:
                    hint = self.hint_line[str(line_number)]
                    # Set to false if this hint does not replace the line
                    line_replaced = True
                    if hint == 'Comment':
                        line.strip()
                        self.add_comment(line)
                        continue
                    elif hint == 'Ignore':
                        continue
                    elif hint == 'Author':
                        # add as a raw author - do not split
                        line.strip()
                        self.add_author(line)
                        line_number += 1
                        next(file)
                        continue
                    elif hint.startswith('VariantVerse'):
                        vv, hintverse, replace = hint.split(' ', 2)
                        this_verse = self.verses[int(hintverse) - 1]
                        this_verse_str = this_verse[1]
                        new_verse = this_verse_str
                        # There might be multiple replace pairs separated by |
                        replaces = replace.split('|')
                        for rep in replaces:
                            source_str, dest_str = rep.split('/')
                            new_verse = new_verse.replace(source_str, dest_str)
                        self.add_verse(new_verse, 'v')
                        self.verse_order_list.append('v{}'.format(str(current_verse_number)))
                        current_verse_number += 1
                        line_number += 1
                        next(file)
                        continue
                    elif hint == 'AddSpaceAfterSemi':
                        line = line.replace(';', '; ')
                        line_replaced = False
                        # note - do not use contine here as the line should now be processed as normal.
                    elif hint == 'AddSpaceAfterColon':
                        line = line.replace(':', ': ')
                        line_replaced = False
                    elif hint == 'BlankLine':
                        line = ' *Blank*'
                        line_replaced = False
                    elif hint == 'BoldLine':
                        # processing of the hint is deferred, but pick it up as a known hint here
                        line_replaced = False
                    else:
                        self.log_error(translate('SongsPlugin.SingingTheFaithImport',
                                       'File {file})'.format(file=file.name)),
                                       translate('SongsPlugin.SingingTheFaithImport',
                                       'Unknown hint {hint}').format(hint=hint))
                    if line_replaced:
                        return
                # STF exported lines have a leading verse number at the start of each verse.
                #  remove them - note that we want to track the indent as that shows a chorus
                # so will deal with that before stripping all leading spaces.
                indent = 0
                if line.strip():
                    # One hymn has one line which starts '* 6' at the start of a verse
                    # Strip this out
                    if line.startswith('* 6'):
                        line = line.lstrip('* ')
                    verse_num_match = re.search(r'^\d+', line)
                    if verse_num_match:
                        # Could extract the verse number and check it against the calculated
                        # verse number - TODO
                        # verse_num = verse_num_match.group()
                        line = line.lstrip('0123456789')
                    indent_match = re.search(r'^\s+', line)
                    if indent_match:
                        indent = len(indent_match.group())
                # Assuming we have sorted out what is verse and what is chorus, strip lines,
                # unless ignoreIndent
                if self.hint_ignore_indent:
                    line = line.rstrip()
                else:
                    line = line.strip()
                if line_number == 2:
                    # note that songs seem to start with a blank line so the title is line 2
                    # Also we strip blanks from the title, even if ignoring indent.
                    song_title = line.strip()
                # Process possible line formatting hints after the verse number has been removed
                if hints_available and str(line_number) in self.hint_line and hint == 'BoldLine':
                    line = '{{st}}{0}{{/st}}'.format(line)
                # Detect the 'Reproduced from Singing the Faith Electronic Words Edition' line
                if line.startswith('Reproduced from Singing the Faith Electronic Words Edition'):
                    song_number_match = re.search(r'\d+', line)
                    if song_number_match:
                        song_number = song_number_match.group()
                        continue
                elif indent == 0:
                    # If the indent is 0 and it contains '(c)' then it is a Copyright line
                    if '(c)' in line:
                        copyright = line
                        continue
                    elif (line.startswith('Liturgical ') or line.startswith('From The ') or
                          line.startswith('From Common ') or line.startswith('Based on Psalm ')):
                        self.add_comment(line)
                        continue
                    # If indent is 0 it may be the author, unless it was one of the cases covered above
                    elif len(line) > 0:
                        # May have more than one author, separated by ' and '
                        authors = line.split(' and ')
                        for a in authors:
                            self.parse_author(a)
                        continue
                # If a blank line has bee replaced by *Blank* then put it back to being
                # a simple space since this is past stripping blanks
                if '*Blank*' in line:
                    line = ' '
                if line == '':
                    if current_verse != '':
                        self.add_verse(current_verse, current_verse_type)
                        self.verse_order_list.append(current_verse_type + str(current_verse_number))
                        if current_verse_type == 'c':
                            chorus_written = True
                        else:
                            current_verse_number += 1
                    current_verse = ''
                    if chorus_written:
                        current_verse_type = 'v'
                else:
                    # If the line is indented more than or equal chorus_indent then assume it is a chorus
                    # If the indent has just changed then start a new verse just like hitting a blank line
                    if not self.hint_ignore_indent and ((indent >= chorus_indent) and (old_indent < indent)):
                        if current_verse != '':
                            self.add_verse(current_verse, current_verse_type)
                            self.verse_order_list.append(current_verse_type + str(current_verse_number))
                            if current_verse_type == 'v':
                                current_verse_number += 1
                        current_verse = line
                        current_verse_type = 'c'
                        old_indent = indent
                        chorus_written = False
                        has_chorus = True
                        continue
                    if current_verse == '':
                        current_verse += line
                    else:
                        current_verse += '\n' + line
                old_indent = indent
        except Exception as e:
            self.log_error(translate('SongsPlugin.SingingTheFaithImport', 'File {file}').format(file=file.name),
                           translate('SongsPlugin.SingingTheFaithImport', 'Error: {error}').format(error=e))
            return

        if self.hint_song_title:
            song_title = self.hint_song_title
        self.title = '{}STF{} - {title}'.format(check_flag, song_number.zfill(3), title=song_title)
        self.song_book_name = 'Singing The Faith'
        self.song_number = song_number
        self.ccli_number = ccli
        self.add_copyright(copyright)
        # If we have a chorus then the generated Verse order can not be used directly, but we can generate
        #  one for two special cases - Verse followed by one chorus (to be repeated after every verse)
        #  of Chorus, followed by verses. If hints for ManualCheck or VerseOrder are supplied ignore this
        if has_chorus and not self.hint_verse_order and not self.checks_needed:
            auto_verse_order_ok = False
            # Popular case V1 C2 V2 ...
            if self.verse_order_list:         # protect against odd cases
                if self.verse_order_list[0] == 'v1' and self.verse_order_list[1] == 'c2':
                    new_verse_order_list = ['v1', 'c1']
                    i = 2
                    auto_verse_order_ok = True
                elif self.verse_order_list[0] == 'c1' and self.verse_order_list[1] == 'v1':
                    new_verse_order_list = ['c1', 'v1', 'c1']
                    i = 2
                    auto_verse_order_ok = True
                # if we are in a case we can deal with
                if auto_verse_order_ok:
                    while i < len(self.verse_order_list):
                        if self.verse_order_list[i].startswith('v'):
                            new_verse_order_list.append(self.verse_order_list[i])
                            new_verse_order_list.append('c1')
                        else:
                            auto_verse_order_ok = False
                            self.add_comment('Importer detected unexpected verse order entry {}'.format(
                                self.verse_order_list[i]))
                        i += 1
                    self.verse_order_list = new_verse_order_list
            else:
                if not auto_verse_order_ok:
                    self.verse_order_list = []
        if self.hint_verse_order:
            self.verse_order_list = self.hint_verse_order.split(',')
        if self.hint_comments:
            self.add_comment(self.hint_comments)
        if self.hint_ccli:
            self.ccli_number = self.hint_ccli
        # Write the title last as by now we will know if we need checks
        if hints_available and not self.checks_needed:
            check_flag = ''
        elif not hints_available and not has_chorus:
            check_flag = ''
        elif not hints_available and has_chorus and auto_verse_order_ok:
            check_flag = ''
        if self.hint_songbook_number_in_title:
            self.title = '{}STF{} - {title}'.format(check_flag, song_number.zfill(3), title=song_title)
        else:
            self.title = '{}{title}'.format(check_flag, title=song_title)
        if not self.finish():
            self.log_error(file.name)

    def read_hints(self, file, song_number):
        """
        Read the hints used to transform a particular song into version which can be projected,
        or improve the transformation process beyond the standard heuristics. Not every song will
        have, or need, hints.
        """
        hintfound = False
        self.hint_verse_order = ''
        self.hint_line.clear()
        self.hint_comments = ''
        self.hint_song_title = ''
        self.hint_ignore_indent = False
        self.hint_ccli = ''
        for tl in file:
            if not tl.strip():
                return hintfound
            tagval = tl.split(':')
            tag = tagval[0].strip()
            val = tagval[1].strip()
            if tag == 'Version':
                self.hint_file_version = val
                continue
            elif tag == 'SongbookNumberInTitle':
                if val == 'False':
                    self.hint_songbook_number_in_title = False
                else:
                    self.hint_songbook_number_in_title = True
                continue
            elif tag == 'Comment':
                continue
            if (tag == 'Hymn') and (val == song_number):
                self.add_comment('Using hints version {}'.format(str(self.hint_file_version)))
                hintfound = True
                # Assume, unless the hints has ManualCheck that if hinted all will be OK
                self.checks_needed = False
                for tl in file:
                    tagval = tl.split(':')
                    tag = tagval[0].strip()
                    val = tagval[1].strip()
                    if tag == 'End':
                        return hintfound
                    elif tag == 'CommentsLine':
                        vals = val.split(',')
                        for v in vals:
                            self.hint_line[v] = 'Comment'
                    elif tag == 'IgnoreLine':
                        vals = val.split(',')
                        for v in vals:
                            self.hint_line[v] = 'Ignore'
                    elif tag == 'AuthorLine':
                        vals = val.split(',')
                        for v in vals:
                            self.hint_line[v] = 'Author'
                    elif tag == 'AddSpaceAfterSemi':
                        vals = val.split(',')
                        for v in vals:
                            self.hint_line[v] = 'AddSpaceAfterSemi'
                    elif tag == 'AddSpaceAfterColon':
                        vals = val.split(',')
                        for v in vals:
                            self.hint_line[v] = 'AddSpaceAfterColon'
                    elif tag == 'BlankLine':
                        vals = val.split(',')
                        for v in vals:
                            self.hint_line[v] = 'BlankLine'
                    elif tag == 'BoldLine':
                        vals = val.split(',')
                        for v in vals:
                            self.hint_line[v] = 'BoldLine'
                    elif tag == 'VerseOrder':
                        self.hint_verse_order = val
                    elif tag == 'ManualCheck':
                        self.checks_needed = True
                    elif tag == 'IgnoreIndent':
                        self.hint_ignore_indent = True
                    elif tag == 'VariantVerse':
                        vvline = val.split(' ', 1)
                        self.hint_line[vvline[0].strip()] = 'VariantVerse {}'.format(vvline[1].strip())
                    elif tag == 'SongTitle':
                        self.hint_song_title = val
                    elif tag == 'AddComment':
                        self.hint_comments += '\n' + val
                    elif tag == 'CCLI':
                        self.hint_ccli = val
                    elif tag == 'Hymn':
                        self.log_error(file.name, 'Missing End tag in hint for Hymn: {}'.format(song_number))
                    else:
                        self.log_error(file.name, 'Unknown tag {} value {}'.format(tag, val))
        return hintfound
