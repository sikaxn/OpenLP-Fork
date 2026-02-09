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
The :mod:`songfileimporthelper` modules provides a helper class and methods to easily enable testing the import of
song files from third party applications.
"""
import json
import logging
from unittest.mock import MagicMock, call, patch

log = logging.getLogger(__name__)


class SongImportTestHelper(object):
    """
    This class is designed to be a helper class to reduce repetition when testing the import of song files.
    """
    def __init__(self, *args, **kwargs):
        self.importer_class_name = args[0]
        self.importer_module_name = args[1]
        self.importer_module = __import__('openlp.plugins.songs.lib.importers.%s' %
                                          self.importer_module_name, fromlist=[self.importer_class_name])
        self.importer_class = getattr(self.importer_module, self.importer_class_name)

    def setUp(self):
        """
        Patch and set up the mocks required.
        """
        self.add_copyright_patcher = patch('openlp.plugins.songs.lib.importers.%s.%s.add_copyright' %
                                           (self.importer_module_name, self.importer_class_name))
        self.add_verse_patcher = patch('openlp.plugins.songs.lib.importers.%s.%s.add_verse' %
                                       (self.importer_module_name, self.importer_class_name))
        self.finish_patcher = patch('openlp.plugins.songs.lib.importers.%s.%s.finish' %
                                    (self.importer_module_name, self.importer_class_name))
        self.add_author_patcher = patch('openlp.plugins.songs.lib.importers.%s.%s.add_author' %
                                        (self.importer_module_name, self.importer_class_name))
        self.song_import_patcher = patch('openlp.plugins.songs.lib.importers.%s.SongImport' %
                                         self.importer_module_name)
        self.mocked_add_copyright = self.add_copyright_patcher.start()
        self.mocked_add_verse = self.add_verse_patcher.start()
        self.mocked_finish = self.finish_patcher.start()
        self.mocked_add_author = self.add_author_patcher.start()
        self.mocked_song_importer = self.song_import_patcher.start()
        self.mocked_manager = MagicMock()
        self.mocked_import_wizard = MagicMock()
        self.mocked_finish.return_value = True

    def tearDown(self):
        """
        Clean up
        """
        self.add_copyright_patcher.stop()
        self.add_verse_patcher.stop()
        self.finish_patcher.stop()
        self.add_author_patcher.stop()
        self.song_import_patcher.stop()

    def __enter__(self):
        """Make this class into a context manager"""
        self.setUp()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Make this class into a context manager"""
        self.tearDown

    def load_external_result_data(self, file_path):
        """
        A method to load and return an object containing the song data from an external file.

        :param pathlib.Path file_path: The path of the file to load
        """
        return json.loads(file_path.read_bytes().decode())

    def file_import(self, source_file_name, result_data):
        """
        Import the given file and check that it has imported correctly
        """
        importer = self.importer_class(self.mocked_manager, file_paths=[source_file_name])
        importer.import_wizard = self.mocked_import_wizard
        importer.stop_import_flag = False
        importer.topics = []

        # WHEN: Importing the source file
        importer.import_source = source_file_name
        add_verse_calls = self._get_data(result_data, 'verses')
        author_calls = self._get_data(result_data, 'authors')
        ccli_number = self._get_data(result_data, 'ccli_number')
        comments = self._get_data(result_data, 'comments')
        song_book_name = self._get_data(result_data, 'song_book_name')
        song_copyright = self._get_data(result_data, 'copyright')
        song_number = self._get_data(result_data, 'song_number')
        title = self._get_data(result_data, 'title')
        topics = self._get_data(result_data, 'topics')
        verse_order_list = self._get_data(result_data, 'verse_order_list')

        # THEN: do_import should return none, the song data should be as expected, and finish should have been called.
        assert importer.do_import() is None, 'do_import should return None when it has completed'

        # Debug information - will be displayed when the test fails
        log.debug("Title imported: %s" % importer.title)
        log.debug("Verses imported: %s" % self.mocked_add_verse.mock_calls)
        log.debug("Verse order imported: %s" % importer.verse_order_list)
        log.debug("Authors imported: %s" % self.mocked_add_author.mock_calls)
        log.debug("CCLI No. imported: %s" % importer.ccli_number)
        log.debug("Comments imported: %s" % importer.comments)
        log.debug("Songbook imported: %s" % importer.song_book_name)
        log.debug("Song number imported: %s" % importer.song_number)
        log.debug("Song copyright imported: %s" % importer.song_number)
        log.debug("Topics imported: %s" % importer.topics)

        assert importer.title == title, \
            'title for %s should be "%s" and is "%s"' % (source_file_name, title, importer.title)
        for author in author_calls:
            if isinstance(author, str):
                self.mocked_add_author.assert_any_call(author)
            else:
                self.mocked_add_author.assert_any_call(*author)
        if song_copyright:
            self.mocked_add_copyright.assert_called_with(song_copyright)
        if ccli_number:
            assert importer.ccli_number == ccli_number, \
                'ccli_number for %s should be %s' % (source_file_name, ccli_number)
        expected_calls = []
        for verse_text, verse_tag in add_verse_calls:
            self.mocked_add_verse.assert_any_call(verse_text, verse_tag)
            expected_calls.append(call(verse_text, verse_tag))
        self.mocked_add_verse.assert_has_calls(expected_calls, any_order=False)
        if topics:
            assert importer.topics == topics, 'topics for %s should be %s' % (source_file_name, topics)
        if comments:
            assert importer.comments == comments, \
                'comments for %s should be "%s"' % (source_file_name, comments)
        if song_book_name:
            assert importer.song_book_name == song_book_name, \
                'song_book_name for %s should be "%s"' % (source_file_name, song_book_name)
        if song_number:
            assert importer.song_number == song_number, \
                'song_number for %s should be %s' % (source_file_name, song_number)
        if verse_order_list:
            assert importer.verse_order_list == verse_order_list, \
                'verse_order_list for %s should be %s and is %s' % (source_file_name,
                                                                    verse_order_list, importer.verse_order_list)
        self.mocked_finish.assert_called_with()

    def _get_data(self, data, key):
        if key in data:
            return data[key]
        return ''
