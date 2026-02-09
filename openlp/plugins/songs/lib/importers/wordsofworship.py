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
The :mod:`wordsofworship` module provides the functionality for importing Words of
Worship songs into the OpenLP database.
"""
import logging
import os

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.lib import DataType, read_int, read_or_fail, seek_or_fail
from openlp.plugins.songs.lib.importers.songimport import SongImport


BLOCK_TYPES = ('V', 'C', 'B')

log = logging.getLogger(__name__)


class WordsOfWorshipImport(SongImport):
    """
    The :class:`WordsOfWorshipImport` class provides the ability to import song files from Words of Worship.

    **Words Of Worship Song File Format:**

    The Words Of Worship song file format is as follows:

    * The song title is the file name minus the extension.
    * The song has a header, a number of blocks, followed by footer containing
      the author and the copyright.
    * A block can be a verse, chorus or bridge.

    Little endian is used.

    File Header:
        Bytes are counted from one, i.e. the first byte is byte 1.

        0x00 - 0x13 Should be "WoW File \nSong Words\n"
        0x14 - 0x1F Minimum version of Words Of Worship required to open this file
        0x20 - 0x2B Minimum version of Words Of Worship required to save this file without data loss
        0x2C - 0x37 The version of Words of Worship that this file is from. From test data, it looks like this might be
                    the version that originally created this file, not the last version to save it.

        The Words Of Worship versioning system seems to be in the format:
            ``Major.Minor.Patch``

        Where each part of the version number is stored by a 32-bit int

        0x38 - 0x3B Specifies how many blocks there are.

        0x42 - 0x51 Should be "CSongDoc::CBlock"

        0x52 The first song blocks start from here.

    Blocks:
        Each block starts with a 32-bit int which specifies how many lines are in that block.

        Then there are a number of lines corresponding to the value above.

        Each block ends with a 32 bit number, which defines what type of
        block it is:

        * 0x00000000 = Verse
        * 0x01000000 = Chorus
        * 0x02000000 = Bridge

        Blocks are separated by two bytes. The first byte is 0x01, and the
        second byte is 0x80.

    Lines:
        Each line consists of a "Pascal" string.
        In later versions, a byte follows which denotes the formatting of the line:

        * 0x00 = Normal
        * 0x01 = Minor

        It looks like this may have been introduced in Words of Worship song version 2.1.0, though this is an educated
        guess.

    Footer:
        The footer follows on after the last block. Its format is as follows:

        Author String (as a 'Pascal' string)
        Copyright String (as a 'Pascal' string)

        Finally in newer versions of Word Of Worship song files there is a 32 bit int describing the copyright.

            0x00000000 = Covered by CCL
            0x01000000 = Authors explicit permission
            0x02000000 = Public Domain
            0x03000000 = Copyright expired
            0x04000000 = Other

    Pascal Strings:
        Strings are preceded by a variable length integer which specifies how many bytes are in the string. An example
        of the variable length integer is below.

            Lentgh bytes 'Little'| Str len
            -------------------------------
            01                   |       01
            02                   |       02
            ....                 |
            FD                   |       FD
            FE                   |       FE
            FF FF 00             |       FF
            FF 00 01             |    01 00
            FF 01 01             |    01 01
            FF 02 01             |    01 02
            ....                 |
            FF FC FF             |    FF FC
            FF FD FF             |    FF FD
            FF FF FF FE FF       |    FF FE
            FF FF FF FF FF 00 00 |    FF FF
            FF FF FF 00 00 01 00 | 01 00 00
            FF FF FF 01 00 01 00 | 01 00 01
            FF FF FF 02 00 02 00 | 01 00 02

    Valid extensions for a Words of Worship song file are:

    * .wsg
    * .wow-song
    """
    @staticmethod
    def parse_string(song_data):
        length_bytes = song_data.read(DataType.U8)
        if length_bytes == b'\xff':
            length_bytes = song_data.read(DataType.U16)
        length = int.from_bytes(length_bytes, 'little')
        return read_or_fail(song_data, length).decode('cp1252')

    def parse_lines(self, song_data):
        lines = []
        lines_to_read = read_int(song_data, DataType.U32, 'little')
        for line_no in range(0, lines_to_read):
            line_text = self.parse_string(song_data)
            if self.read_version >= (2, 1, 0):
                if read_or_fail(song_data, DataType.U8) == b'\x01':
                    line_text = '{{minor}}{text}{{/minor}}'.format(text=line_text)
            lines.append(line_text)
        return '\n'.join(lines)

    @staticmethod
    def parse_version(song_data):
        return (read_int(song_data, DataType.U32, 'little'),
                read_int(song_data, DataType.U32, 'little'),
                read_int(song_data, DataType.U32, 'little'))

    def vaildate(self, file_path, song_data):
        seek_or_fail(song_data, 0x00)
        err_text = b''
        data = read_or_fail(song_data, 20)
        if data != b'WoW File\nSong Words\n':
            err_text = data
        seek_or_fail(song_data, 0x42)
        data = read_or_fail(song_data, 16)
        if data != b'CSongDoc::CBlock':
            err_text = data
        if err_text:
            self.log_error(file_path,
                           translate('SongsPlugin.WordsofWorshipSongImport',
                                     'Invalid Words of Worship song file. Missing {text!r} header.'
                                     ).format(text=err_text))
            return False
        return True

    def do_import(self):
        """
        Receive a single file or a list of files to import.
        """
        if isinstance(self.import_source, list):
            self.import_wizard.progress_bar.setMaximum(len(self.import_source))
            for file_path in self.import_source:
                if self.stop_import_flag:
                    return
                log.debug('Importing %s', file_path)
                try:
                    self.set_defaults()
                    # Get the song title
                    self.title = file_path.stem
                    with file_path.open('rb') as song_data:
                        if not self.vaildate(file_path, song_data):
                            continue
                        seek_or_fail(song_data, 20)
                        self.read_version = self.parse_version(song_data)
                        # Seek to byte which stores number of blocks in the song
                        seek_or_fail(song_data, 56)
                        no_of_blocks = read_int(song_data, DataType.U8)

                        # Seek to the beginning of the first block
                        seek_or_fail(song_data, 82)
                        for block_no in range(no_of_blocks):
                            # Blocks are separated by 2 bytes, skip them, but not if this is the last block!
                            if block_no != 0:
                                seek_or_fail(song_data, 2, os.SEEK_CUR)
                            text = self.parse_lines(song_data)
                            block_type = BLOCK_TYPES[read_int(song_data, DataType.U32, 'little')]
                            self.add_verse(text, block_type)

                        # Now to extract the author
                        self.parse_author(self.parse_string(song_data))
                        # Finally the copyright
                        self.add_copyright(self.parse_string(song_data))
                        if not self.finish():
                            self.log_error(file_path)
                except IndexError:
                    self.log_error(file_path, UiStrings().FileCorrupt)
                except Exception as e:
                    self.log_error(file_path, e)
