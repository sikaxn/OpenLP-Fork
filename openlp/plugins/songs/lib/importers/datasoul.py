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
The :mod:`datasoul` module provides the functionality for importing Datasoul songs into the OpenLP database.
"""
import logging

from lxml import etree, objectify

from openlp.core.common.i18n import translate
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.ui import SongStrings


log = logging.getLogger(__name__)


class DatasoulImport(SongImport):
    """
    The :class:`DatasoulImport` class provides the ability to import song files from
    Datasoul .song XML format. The only tag that is taken into consideration for a
    song's lyrics is <Text/>. There can also be <ChordsComplete/> and
    <ChordsSimplified/>, which can contain lyrics but are ignored.
    """

    def do_import(self):
        """
        Receive a single file_path or a list of files to import.
        """
        if isinstance(self.import_source, list):
            self.import_wizard.progress_bar.setMaximum(len(self.import_source))
            for file_path in self.import_source:
                if self.stop_import_flag:
                    return
                self.set_defaults()
                parser = objectify.makeparser(recover=True)
                try:
                    tree = objectify.parse(str(file_path), parser)
                except etree.XMLSyntaxError:
                    log.exception('XML syntax error in file {name}'.format(name=file_path))
                    self.log_error(file_path, SongStrings().XMLSyntaxError)
                    continue
                song_xml = tree.getroot()
                if song_xml.tag != 'Song':
                    self.log_error(
                        file_path,
                        translate('SongsPlugin.DatasoulImport',
                                  'Invalid Datasoul song file. Missing Song tag.'))
                    continue
                if hasattr(song_xml, 'Title') and song_xml.Title.text:
                    self.title = str(song_xml.Title.text)
                if hasattr(song_xml, 'SongAuthor') and song_xml.SongAuthor.text:
                    self.parse_author(str(song_xml.SongAuthor.text))
                if hasattr(song_xml, 'Text') and song_xml.Text.text:
                    for verse in str(song_xml.Text.text).split('\n===\n'):
                        self.add_verse(verse.replace('\n==\n', '\n[--}{--]\n'), 'v')
                if hasattr(song_xml, 'SongSource') and song_xml.SongSource.text:
                    self.parse_song_book_name_and_number(str(song_xml.SongSource.text))
                if hasattr(song_xml, 'Notes') and song_xml.Notes.text:
                    self.add_comment(str(song_xml.Notes.text))
                if hasattr(song_xml, 'Copyright') and song_xml.Copyright.text:
                    self.add_copyright(str(song_xml.Copyright.text))
                if not self.finish():
                    self.log_error(file_path)
