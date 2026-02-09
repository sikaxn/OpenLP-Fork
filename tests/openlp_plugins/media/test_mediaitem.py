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
Test the media plugin
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from openlp.core.common.registry import Registry
from openlp.core.ui.media import MediaType, get_supported_media_suffix
from openlp.plugins.media.lib.mediaitem import MediaMediaItem


@pytest.fixture
def media_item(settings):
    """Local test setup"""
    mocked_main_window = MagicMock()
    Registry().register('service_list', MagicMock())
    Registry().register('main_window', mocked_main_window)
    Registry().register('live_controller', MagicMock())
    mocked_plugin = MagicMock()
    with patch('openlp.plugins.media.lib.mediaitem.FolderLibraryItem._setup'), \
            patch('openlp.plugins.media.lib.mediaitem.MediaMediaItem.setup_item'):
        m_item = MediaMediaItem(None, mocked_plugin)
        m_item.manager = MagicMock()
    return m_item


def test_search_found(media_item):
    """
    Media Remote Search Successful find
    """
    # GIVEN: The Mediaitem set up a list of media
    media_item.manager.get_all_objects.return_value = [MagicMock(file_path='test.mp4')]

    # WHEN: Retrieving the test file
    result = media_item.search('test.mp4', False)

    # THEN: a file should be found
    assert result == [['test.mp4', 'test.mp4']], 'The result file contain the file name'


def test_search_not_found(media_item):
    """
    Media Remote Search not find
    """
    # GIVEN: The Mediaitem set up a list of media
    media_item.manager.get_all_objects.return_value = []

    # WHEN: Retrieving the test file
    result = media_item.search('test.mpx', False)

    # THEN: a file should be found
    assert result == [], 'The result file should be empty'


@patch('openlp.plugins.media.lib.mediaitem.or_')
@patch('openlp.plugins.media.lib.mediaitem.Item')
def test_get_list_audio(MockItem, mocked_or, media_item):
    """
    Test the ``MediaMediaItem.get_list()`` method to return all audio items
    """
    # GIVEN: A mocked Item class and some mocked items to return
    media_item.manager.get_all_objects.return_value = [MagicMock(file_path='test1.mp3'),
                                                       MagicMock(file_path='test2.ogg')]
    MockItem.file_path.endswith.side_effect = lambda ext: ext
    mocked_or.side_effect = lambda *ext: list(ext)

    # WHEN: get_list() is called
    media_list = media_item.get_list(MediaType.Audio)

    # THEN: All the clauses should have been created, and the right extensions used
    a_suffixes, _ = get_supported_media_suffix()
    expected_extensions = [ext[1:] for ext in a_suffixes]
    expected_calls = [call(ext) for ext in expected_extensions]
    MockItem.file_path.endswith.assert_has_calls(expected_calls)
    mocked_or.assert_called_once_with(*expected_extensions)
    media_item.manager.get_all_objects.assert_called_once_with(MockItem, expected_extensions)
    assert media_list == [Path('test1.mp3'), Path('test2.ogg')]


@patch('openlp.plugins.media.lib.mediaitem.or_')
@patch('openlp.plugins.media.lib.mediaitem.Item')
def test_get_list_video(MockItem, mocked_or, media_item):
    """
    Test the ``MediaMediaItem.get_list()`` method to return all audio items
    """
    # GIVEN: A mocked Item class and some mocked items to return
    media_item.manager.get_all_objects.return_value = [MagicMock(file_path='test1.mp4'),
                                                       MagicMock(file_path='test2.ogv')]
    MockItem.file_path.endswith.side_effect = lambda ext: ext
    mocked_or.side_effect = lambda *ext: list(ext)

    # WHEN: get_list() is called
    media_list = media_item.get_list(MediaType.Video)

    # THEN: All the clauses should have been created, and the right extensions used
    _, v_suffixes = get_supported_media_suffix()
    expected_extensions = [ext[1:] for ext in v_suffixes]
    expected_calls = [call(ext) for ext in expected_extensions]
    MockItem.file_path.endswith.assert_has_calls(expected_calls)
    mocked_or.assert_called_once_with(*expected_extensions)
    media_item.manager.get_all_objects.assert_called_once_with(MockItem, expected_extensions)
    assert media_list == [Path('test1.mp4'), Path('test2.ogv')]


def test_add_device_stream(media_item):
    """Test that the ``MediaMediaItem.add_device_stream()`` method calls validate_and_load()"""
    # GIVEN: A MediaMediaItem object, with a mocked out `validate_and_load` method
    with patch.object(media_item, 'validate_and_load') as mocked_validate_and_load:
        # WHEN: add_device_stream is called
        media_item.add_device_stream('devicestream:/dev/v4l')

        # THEN: The mocked method should have been called
        mocked_validate_and_load.assert_called_once_with(['devicestream:/dev/v4l'])


def test_add_network_stream(media_item):
    """Test that the ``MediaMediaItem.add_network_stream()`` method calls validate_and_load()"""
    # GIVEN: A MediaMediaItem object, with a mocked out `validate_and_load` method
    with patch.object(media_item, 'validate_and_load') as mocked_validate_and_load:
        # WHEN: add_network_stream is called
        media_item.add_network_stream('networkstream:rmtp://localhost')

        # THEN: The mocked method should have been called
        mocked_validate_and_load.assert_called_once_with(['networkstream:rmtp://localhost'])
