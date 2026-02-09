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
The :mod:`~openlp.plugins.planningcenter.lib.songimport` module provides
2 classes that are used to import Planning Center Online Service Songs into
an OpenLP Service.
"""
import re

from openlp.core.common.registry import Registry
from openlp.plugins.songs.lib.db import Song
from openlp.plugins.songs.lib.importers.songimport import SongImport


class PlanningCenterSongImport(SongImport):
    """
    The :class:`PlanningCenterSongImport` class subclasses SongImport
    and provides interfaces for parsing lyrics and adding songs from a
    Planning Center Service into an OpenLP Service.
    """
    def __init__(self):
        """
        Initialize
        """
        songs = Registry().get('songs')
        manager = songs.plugin.manager
        SongImport.__init__(self, manager, file_path=None)

    def add_song(self, item_title, author, lyrics, theme_name, last_modified, copyright="", ccli_number="",
                 verse_order=""):
        """
        Builds and adds song to the database and returns the Song ID
        :param item_title: The song title.
        :param author: Author String from Planning Center
        :param lyrics: Lyrics String from Planning Center
        :param theme_name: Theme String to use for this song
        :param last_modified: DateTime of last modified date for this song
        :param copyright: Copyright statement for this song
        :param ccli_no: CCLI number for this song
        :param verse_order: Verse Order for this song
        """
        self.set_defaults()
        self.title = item_title
        self.theme_name = theme_name
        if author:
            self.parse_author(author)
        self.ccli_number = ccli_number
        self.copyright = copyright
        # handle edge condition where a song has no lyrics set
        if lyrics is None:
            self.add_verse(item_title)
        else:
            verses = self._split_lyrics_into_verses(lyrics)
            for verse in verses:
                if len(verse['verse_type']):
                    verse_def = verse['verse_type'] + verse['verse_number']
                    self.add_verse(verse_text=verse['verse_text'], verse_def=verse_def)
                else:
                    self.add_verse(verse_text=verse['verse_text'])
        openlp_id = self.finish(temporary_flag=True)
        # set the last_updated date/time based on the PCO date/time so I can look for updates
        song = self.manager.get_object(Song, openlp_id)
        song.last_modified = last_modified
        song.verse_order = verse_order
        self.manager.save_object(song)
        return openlp_id

    def _split_lyrics_into_verses(self, lyrics):
        """
        Parses Planning Center Lyrics and returns an list of verses, where each
        verse is a dictionary that looks like:
            verse['verse_type']
            verse['verse_number']
            verse['verse_text']
        :param lyrics: Lyrics String from Planning Center
        """
        # create a regular expression for potential VERSE,CHORUS tags included inline inside the lyrics...
        verse_marker_pattern = re.compile(r'^(v|verse|c|chorus|bridge|prechorus|instrumental|intro|outro|vamp|breakdown|ending|interlude|tag|misc)\s*(\d*)$', re.IGNORECASE)  # noqa: E501
        # create regex for an END marker.  content after this marker will be ignored
        end_marker_pattern = re.compile('^{(<.*?>)?END(<.*?>)?}$')
        verse_type = ''
        verse_number = ''
        verse_text = ''
        is_end_marker = False
        output_verses = []
        input_verses = lyrics.split("\n\n")
        for verse in input_verses:
            for line in verse.split("\n"):
                if end_marker_pattern.search(line):
                    # see if this is the end marker (stop parsing verses if it is)
                    is_end_marker = True
                # strip out curly braces and the content inside {}
                line = re.sub('{.*?}+', '', line)
                # strip out any extraneous tags <...>
                line = re.sub('<.*?>', '', line)
                # remove beginning/trailing whitespace and line breaks
                line = line.rstrip()
                line = line.lstrip()
                regex_match = verse_marker_pattern.search(line)
                if regex_match:
                    if len(verse_text):
                        # if we have verse_text from the previous verse, submit it now
                        self._add_verse(output_verses, verse_type, verse_number, verse_text)
                        verse_text = ''
                    verse_type = self._lookup_openlp_verse_type(regex_match.group(1))
                    # if we have a number after the verse marker, capture it here
                    if regex_match.group(2):
                        verse_number = regex_match.group(2)
                    else:
                        # if empty, let openlp auto-create it for us
                        verse_number = ''
                    continue
                else:
                    if len(verse_text):
                        verse_text += "\n{0}".format(line)
                    else:
                        verse_text = line
            if len(verse_text):
                self._add_verse(output_verses, verse_type, verse_number, verse_text)
                verse_text = ''
            if is_end_marker:
                return output_verses
        return output_verses

    def _lookup_openlp_verse_type(self, pco_verse_type):
        """
        Provides a lookup table to map from a Planning Center Verse Type
        to an OpenLP verse type.
        :param pco_verse_type: Planning Center Verse Type String
        """
        pco_verse_type_to_openlp = {}
        pco_verse_type_to_openlp['VERSE'] = 'v'
        pco_verse_type_to_openlp['V'] = 'v'
        pco_verse_type_to_openlp['C'] = 'c'
        pco_verse_type_to_openlp['CHORUS'] = 'c'
        pco_verse_type_to_openlp['PRECHORUS'] = 'p'
        pco_verse_type_to_openlp['INTRO'] = 'i'
        pco_verse_type_to_openlp['ENDING'] = 'e'
        pco_verse_type_to_openlp['BRIDGE'] = 'b'
        pco_verse_type_to_openlp['OTHER'] = 'o'
        openlp_verse_type = pco_verse_type_to_openlp['OTHER']
        if pco_verse_type.upper() in pco_verse_type_to_openlp:
            openlp_verse_type = pco_verse_type_to_openlp[pco_verse_type.upper()]
        return openlp_verse_type

    def _add_verse(self, output_verses, verse_type, verse_number, verse_text):
        """
        Simple utility function that takes verse attributes and adds the verse
        to the output_verses list.
        :param output_verses: The list of verses that will ultimately be returned by
        the _split_lyrics_into_verses function
        :param verse_type: The OpenLP Verse Type, like v,c,e, etc...
        :param verse_number: The verse number, if known, like 1, 2, 3, etc.
        :param verse_text: The parsed verse text returned from _split_lyrics_into_verses
        """
        new_verse = {}
        new_verse['verse_type'] = verse_type
        new_verse['verse_number'] = verse_number
        new_verse['verse_text'] = verse_text
        output_verses.append(new_verse)
