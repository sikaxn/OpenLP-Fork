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
The :mod:`~openlp.plugins.songs.lib.songselect` module contains the SongSelect importer itself.
"""
import logging
import re
from PySide6 import QtCore

from openlp.plugins.songs.lib import VerseType, clean_song
from openlp.plugins.songs.lib.db import Song, Author, Topic
from openlp.plugins.songs.lib.openlyricsxml import SongXML
from openlp.core.common.utils import wait_for


BASE_URL = 'https://songselect.ccli.com'
LOGIN_PAGE = 'https://profile.ccli.com/account/signin?appContext=SongSelect&returnUrl='\
    'https%3a%2f%2fsongselect.ccli.com%2f'
LOGIN_URL = 'https://profile.ccli.com'
LOGOUT_URL = BASE_URL + '/account/logout'
SEARCH_URL = BASE_URL + '/search/results'
SONG_PAGE = BASE_URL + '/Songs/'

log = logging.getLogger(__name__)


class Pages(object):
    """
    Songselect web page types.
    """
    Login = 0
    Home = 1
    Search = 2
    Song = 3
    Other = 4


class SongSelectImport(object):
    """
    The :class:`~openlp.plugins.songs.lib.songselect.SongSelectImport` class contains all the code which interfaces
    with CCLI's SongSelect service and downloads the songs.
    """
    def __init__(self, db_manager, webview):
        """
        Set up the song select importer

        :param db_manager: The song database manager
        """
        self.db_manager = db_manager
        self.webview = webview

    def get_page_type(self):
        """
        Get the type of page the user is currently ono

        :return: The page the user is on
        """
        current_url_host = self.webview.page().url().host()
        current_url_path = self.webview.page().url().path()
        if current_url_host == QtCore.QUrl(LOGIN_URL).host() and current_url_path == QtCore.QUrl(LOGIN_PAGE).path():
            return Pages.Login
        elif current_url_host == QtCore.QUrl(BASE_URL).host():
            if current_url_path == '/' or current_url_path == '':
                return Pages.Home
            elif current_url_path == QtCore.QUrl(SEARCH_URL).path():
                return Pages.Search
            elif self.get_song_number_from_url(current_url_path) is not None:
                return Pages.Song
        return Pages.Other

    def _run_javascript(self, script):
        """
        Run a script and returns the result

        :param script: The javascript to be run
        :return: The evaluated result
        """
        self.web_stuff = ""
        self.got_web_stuff = False

        def handle_result(result):
            """
            Handle the result from the asynchronous call
            """
            self.got_web_stuff = True
            self.web_stuff = result
        self.webview.page().runJavaScript(script, handle_result)
        wait_for(lambda: self.got_web_stuff)
        return self.web_stuff

    def reset_webview(self):
        """
        Sets the webview back to the login page using the Qt setUrl method
        """
        url = QtCore.QUrl(LOGIN_PAGE)
        self.webview.setUrl(url)

    def set_home_page(self):
        """
        Sets the webview to the search page
        """
        self.set_page(BASE_URL)

    def set_page(self, url):
        """
        Sets the active page in the webview

        :param url: The new page location
        """
        script = 'document.location = "{}"'.format(url)
        self._run_javascript(script)

    def set_login_fields(self, username, password):
        script_set_login_fields = ('document.getElementById("EmailAddress").value = "{email}";'
                                   'document.getElementById("Password").value = "{password}";'
                                   ).format(email=username, password=password)
        self._run_javascript(script_set_login_fields)

    def get_page(self, url):
        """
        Gets the html for the url through the active webview

        :return: String containing a html document
        """
        script_get_page = ('var openlp_page_data = null;'
                           'fetch("{}").then(data => {{return data.text()}})'
                           '           .then(data => {{openlp_page_data = data}})').format(url)
        self._run_javascript(script_get_page)
        wait_for(lambda: self._run_javascript('openlp_page_data != null'))
        return self._run_javascript('openlp_page_data')

    def get_song_number_from_url(self, url):
        """
        Gets the ccli song number for a song from the url

        :return: String containg ccli song number, None is returned if not found
        """
        ccli_number_regex = re.compile(r'.*?Songs\/([0-9]+).*', re.IGNORECASE)
        regex_matches = ccli_number_regex.match(url)
        if regex_matches:
            return regex_matches.group(1)
        return None

    def save_song(self, song):
        """
        Save a song to the database, using the db_manager

        :param song: Dictionary of the song to save
        :return:
        """
        db_song = Song(title=song['title'], copyright=song['copyright'], ccli_number=song['ccli_number'])
        song_xml = SongXML()
        verse_order = []
        for verse in song['verses']:
            if ' ' in verse['label']:
                verse_type, verse_number = verse['label'].split(' ', 1)
            else:
                verse_type = verse['label']
                verse_number = 1
            verse_type = VerseType.from_loose_input(verse_type)
            try:
                verse_number = int(verse_number)
            except ValueError:
                # Some custom verse types contain multiple words, and this messes with the verse number,
                # so just default to 1 on ValueError. See https://gitlab.com/openlp/openlp/-/issues/937
                verse_number = 1
            song_xml.add_verse_to_lyrics(VerseType.tags[verse_type], verse_number, verse['lyrics'])
            verse_order.append('{tag}{number}'.format(tag=VerseType.tags[verse_type], number=verse_number))
        db_song.verse_order = ' '.join(verse_order)
        db_song.lyrics = song_xml.extract_xml()
        clean_song(self.db_manager, db_song)
        self.db_manager.save_object(db_song)
        db_song.authors_songs = []
        for author_name in song['authors']:
            author = self.db_manager.get_object_filtered(Author, Author.display_name == author_name)
            if not author:
                name_parts = author_name.rsplit(' ', 1)
                first_name = name_parts[0]
                if len(name_parts) == 1:
                    last_name = ''
                else:
                    last_name = name_parts[1]
                author = Author(first_name=first_name, last_name=last_name, display_name=author_name)
            db_song.add_author(author)
        for topic_name in song.get('topics', []):
            topic = self.db_manager.get_object_filtered(Topic, Topic.name == topic_name)
            if not topic:
                topic = Topic(name=topic_name)
            db_song.topics.append(topic)
        self.db_manager.save_object(db_song)
        return db_song
