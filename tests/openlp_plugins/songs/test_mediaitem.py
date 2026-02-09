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
This module contains tests for the lib submodule of the Songs plugin.
"""
import pytest
from unittest.mock import MagicMock, patch, call

from PySide6 import QtCore, QtWidgets

from openlp.core.common.enum import SongFirstSlideMode, SongSearch
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib.serviceitem import ServiceItem
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.plugins.songs.lib.db import AuthorType, Song
from openlp.plugins.songs.lib.mediaitem import SongMediaItem
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics


__default_settings__ = {
    'songs/footer template': """
${title}<br/>

%if authors_none:
  <%
    authors = ", ".join(authors_none)
  %>
  ${authors_none_label}:&nbsp;${authors}<br/>
%endif

%if authors_words_music:
  <%
    authors = ", ".join(authors_words_music)
  %>
  ${authors_words_music_label}:&nbsp;${authors}<br/>
%endif

%if authors_words:
  <%
    authors = ", ".join(authors_words)
  %>
  ${authors_words_label}:&nbsp;${authors}<br/>
%endif

%if authors_music:
  <%
    authors = ", ".join(authors_music)
  %>
  ${authors_music_label}:&nbsp;${authors}<br/>
%endif

%if authors_translation:
  <%
    authors = ", ".join(authors_translation)
  %>
  ${authors_translation_label}:&nbsp;${authors}<br/>
%endif

%if copyright:
  &copy;&nbsp;${copyright}<br/>
%endif

%if songbook_entries:
  <%
    entries = ", ".join(songbook_entries)
  %>
  ${entries}<br/>
%endif

%if ccli_license:
  ${ccli_license_label}&nbsp;${ccli_license}<br/>
%endif
"""
}


SONG_VERSES_TEST_LYRICS = [[{'type': 'v', 'label': '1'}, 'Test text']]
SONG_VERSES_TEST_VERSE_ORDER = 'v1'


@pytest.fixture
def media_item(registry: Registry, settings: Settings):
    registry.register('service_list', MagicMock())
    registry.register('main_window', MagicMock())
    registry.register('media_controller', MagicMock())
    mocked_plugin = MagicMock()
    with patch('openlp.core.lib.mediamanageritem.MediaManagerItem._setup'), \
            patch('openlp.plugins.songs.forms.editsongform.EditSongForm.__init__'):
        media_item = SongMediaItem(None, mocked_plugin)
        media_item.save_auto_select_id = MagicMock()
        media_item.list_view = MagicMock()
        media_item.list_view.save_auto_select_id = MagicMock()
        media_item.list_view.clear = MagicMock()
        media_item.list_view.addItem = MagicMock()
        media_item.list_view.setCurrentItem = MagicMock()
        media_item.auto_select_id = -1
        media_item.display_songbook = False
        media_item.display_copyright_symbol = False
    settings = registry.get('settings')
    settings.extend_default_settings(__default_settings__)
    QtCore.QLocale.setDefault(QtCore.QLocale('en_GB'))
    yield media_item


def test_add_middle_header_bar(media_item: SongMediaItem):
    """Test the add_middle_header_bar() function, that it sets up the search interface"""
    # GIVEN: A mocked out toolbar and other methods
    with patch.object(media_item, 'add_search_to_toolbar') as mocked_add_search:
        media_item.toolbar = MagicMock()
        media_item.search_button_layout = MagicMock()
        media_item.search_text_edit = MagicMock()

        # WHEN: add_middle_header_bar() is called
        media_item.add_middle_header_bar()

    # THEN: The favourite toggle button should have been added to the
    media_item.toolbar.addSeparator.assert_called_once_with()
    mocked_add_search.assert_called_once_with()
    assert hasattr(media_item, 'favourite_toggle_button')
    assert isinstance(media_item.favourite_toggle_button, QtWidgets.QPushButton)
    media_item.search_button_layout.insertWidget.assert_called_once_with(1, media_item.favourite_toggle_button)


@patch('openlp.plugins.songs.lib.mediaitem.create_widget_action')
def test_add_custom_context_actions(mocked_create_action: MagicMock, media_item: SongMediaItem):
    """Test that adding extra context menu items works"""
    # GIVEN: A pre-mocked media item
    # WHEN: add_custom_context_actions() is called
    media_item.add_custom_context_actions()

    # THEN: Custom actions are added to the context menu
    assert mocked_create_action.call_args_list == [
        call(media_item.list_view, separator=True),
        call(media_item.list_view, text='&Clone', icon=UiIcons().clone, triggers=media_item.on_clone_click),
        call(media_item.list_view, text='Toggle Favourite', icon=UiIcons().favourite,
             triggers=media_item.on_favourite_click)
    ]


def test_on_focus(media_item: SongMediaItem):
    """Test that the on_focus() handler does the correct actions"""
    # GIVEN: A mocked out search_text_edit widget
    mocked_edit = MagicMock()
    media_item.search_text_edit = mocked_edit

    # WHEN: on_focus() is called
    media_item.on_focus()

    # THEN: The search text edit should be focused and all the text selected
    mocked_edit.setFocus.assert_called_once_with()
    mocked_edit.selectAll.assert_called_once_with()


def test_config_update(settings: Settings, media_item: SongMediaItem):
    """Test that the local configuration is updated from the settings"""
    # GIVEN: A settings object and a SongMediaItem
    media_item.is_search_as_you_type_enabled = False
    media_item.update_service_on_edit = True
    media_item.add_song_from_service = True

    settings.setValue('advanced/search as type', True)
    settings.setValue('songs/update service on edit', False)
    settings.setValue('songs/add song from service', False)

    # WHEN: config_update() is called
    media_item.config_update()

    # THEN: The set values should be correct
    assert media_item.is_search_as_you_type_enabled is True
    assert media_item.update_service_on_edit is False
    assert media_item.add_song_from_service is False


def test_retranslate_ui(media_item: SongMediaItem):
    """Test that the labels are all set correctly when calling retranslate_ui()"""
    # GIVEN: A song media item with a number of mocked out attributes
    media_item.search_text_label = MagicMock()
    media_item.search_text_button = MagicMock()
    media_item.maintenance_action = MagicMock()
    media_item.favourite_toggle_button = MagicMock()

    # WHEN: retranslate_ui() is called
    media_item.retranslate_ui()

    # THEN: The correct strings should be set
    media_item.search_text_label.setText.assert_called_once_with('Search:')
    media_item.search_text_button.setText.assert_called_once_with('Search')
    media_item.maintenance_action.setText.assert_called_once_with('Song Maintenance')
    media_item.maintenance_action.setToolTip.assert_called_once_with(
        'Maintain the lists of authors, topics and books.'
    )
    media_item.favourite_toggle_button.setToolTip.assert_called_once_with('Show only favourites')


@pytest.mark.parametrize('is_checked', (True, False))
def test_on_favourite_toggle_button_clicked(settings: Settings, media_item: SongMediaItem, is_checked: bool):
    """Test the on_favourite_toggle_button_clicked() method"""
    # GIVEN: A mocked out on_search_text_button_clicked
    with patch.object(media_item, 'on_search_text_button_clicked') as mocked_clicked:
        # WHEN: on_favourite_toggle_button_clicked() is called after toggling
        media_item.on_favourite_toggle_button_clicked(is_checked)

    # THEN: The setting should be correct, and the method should have been called
    assert settings.value('songs/favourites_toggled') is is_checked
    mocked_clicked.assert_called_once_with()


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.Song')
def test_on_search_text_button_clicked_entire(MockSong: MagicMock, fav_filter: bool, media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockSong.is_favourite.is_.return_value = 'is_true'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'Amazing grace'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.Entire
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item, 'search_entire') as mocked_search_entire, \
            patch.object(media_item, 'display_results_song') as mocked_display_results:
        mocked_search_entire.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    if fav_filter:
        mocked_search_entire.assert_called_once_with('Amazing grace', 'is_true')
    else:
        mocked_search_entire.assert_called_once_with('Amazing grace')
    mocked_display_results.assert_called_once_with(['Amazing Grace'])


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.Song')
def test_on_search_text_button_clicked_titles(MockSong: MagicMock, fav_filter: bool, media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockSong.is_favourite.is_.return_value = 'is_true'
    MockSong.search_title.like.return_value = 'like Amazing Grace'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'Amazing grace'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.Titles
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item.plugin.manager, 'get_all_objects') as mocked_get_all_objects, \
            patch.object(media_item, 'display_results_song') as mocked_display_results:
        mocked_get_all_objects.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    if fav_filter:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'is_true', 'like Amazing Grace')
    else:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'like Amazing Grace')
    mocked_display_results.assert_called_once_with(['Amazing Grace'])


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.Song')
def test_on_search_text_button_clicked_lyrics(MockSong: MagicMock, fav_filter: bool, media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockSong.is_favourite.is_.return_value = 'is_true'
    MockSong.search_lyrics.like.return_value = 'lyrics Amazing Grace'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'Amazing grace'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.Lyrics
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item.plugin.manager, 'get_all_objects') as mocked_get_all_objects, \
            patch.object(media_item, 'display_results_song') as mocked_display_results:
        mocked_get_all_objects.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    if fav_filter:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'is_true', 'lyrics Amazing Grace')
    else:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'lyrics Amazing Grace')
    mocked_display_results.assert_called_once_with(['Amazing Grace'])


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.Author')
def test_on_search_text_button_clicked_authors(MockAuthor: MagicMock, fav_filter: bool,
                                               media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockAuthor.display_name.like.return_value = 'like John Newton'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'John Newton'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.Authors
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item.plugin.manager, 'get_all_objects') as mocked_get_all_objects, \
            patch.object(media_item, 'display_results_author') as mocked_display_results:
        mocked_get_all_objects.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    mocked_get_all_objects.assert_called_once_with(MockAuthor, 'like John Newton')
    mocked_display_results.assert_called_once_with(['Amazing Grace'], fav_filter)


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.Topic')
def test_on_search_text_button_clicked_topics(MockTopic: MagicMock, fav_filter: bool,
                                              media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockTopic.name.like.return_value = 'like Salvation'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'Salvation'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.Topics
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item.plugin.manager, 'get_all_objects') as mocked_get_all_objects, \
            patch.object(media_item, 'display_results_topic') as mocked_display_results:
        mocked_get_all_objects.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    mocked_get_all_objects.assert_called_once_with(MockTopic, 'like Salvation')
    mocked_display_results.assert_called_once_with(['Amazing Grace'], fav_filter)


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.SongBookEntry')
@patch('openlp.plugins.songs.lib.mediaitem.SongBook')
@patch('openlp.plugins.songs.lib.mediaitem.Song')
def test_on_search_text_button_clicked_songbooks(MockSong: MagicMock, MockSongBook: MagicMock,
                                                 MockSongBookEntry: MagicMock, fav_filter: bool,
                                                 media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockSong.is_favourite.is_.return_value = 'is_true'
    MockSongBook.name.like.return_value = 'like Trinity Hymnal'
    MockSongBookEntry.entry.like.return_value = 'like 451'
    MockSong.temporary.is_.return_value = 'is False'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'Salvation'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.Books
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item.plugin.manager.session, 'query') as mocked_query, \
            patch.object(media_item, 'display_results_book') as mocked_display_results:
        mocked_song_join = MagicMock()
        mocked_songbook_join = MagicMock()
        mocked_filter = MagicMock()
        mocked_query.return_value = mocked_song_join
        mocked_song_join.join.return_value = mocked_songbook_join
        mocked_songbook_join.join.return_value = mocked_filter
        mocked_filter.filter.return_value.all.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    mocked_query.assert_called_once_with(MockSongBookEntry.entry, MockSongBook.name, MockSong.title, MockSong.id)
    mocked_song_join.join.assert_called_once_with(MockSong)
    mocked_songbook_join.join.assert_called_once_with(MockSongBook)
    if fav_filter:
        mocked_filter.filter.assert_called_once_with('is_true', 'like Trinity Hymnal', 'like 451', 'is False')
    else:
        mocked_filter.filter.assert_called_once_with('like Trinity Hymnal', 'like 451', 'is False')
    mocked_display_results.assert_called_once_with(['Amazing Grace'])


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.Song')
def test_on_search_text_button_clicked_themes(MockSong: MagicMock, fav_filter: bool, media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockSong.is_favourite.is_.return_value = 'is_true'
    MockSong.theme_name.like.return_value = 'like sunrise'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'sunrise'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.Themes
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item.plugin.manager, 'get_all_objects') as mocked_get_all_objects, \
            patch.object(media_item, 'display_results_themes') as mocked_display_results:
        mocked_get_all_objects.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    if fav_filter:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'is_true', 'like sunrise')
    else:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'like sunrise')
    mocked_display_results.assert_called_once_with(['Amazing Grace'])


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.Song')
def test_on_search_text_button_clicked_copyright(MockSong: MagicMock, fav_filter: bool,
                                                 media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockSong.is_favourite.is_.return_value = 'is_true'
    MockSong.copyright.like.return_value = 'like public domain'
    MockSong.copyright.__ne__.return_value = 'ne ""'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'public domain'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.Copyright
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item.plugin.manager, 'get_all_objects') as mocked_get_all_objects, \
            patch.object(media_item, 'display_results_song') as mocked_display_results:
        mocked_get_all_objects.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    if fav_filter:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'is_true', 'like public domain', 'ne ""')
    else:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'like public domain', 'ne ""')
    mocked_display_results.assert_called_once_with(['Amazing Grace'])


@pytest.mark.parametrize('fav_filter', (False, True))
@patch('openlp.plugins.songs.lib.mediaitem.Song')
def test_on_search_text_button_clicked_cclinumber(MockSong: MagicMock, fav_filter: bool,
                                                  media_item: SongMediaItem):
    """Test the search button handler"""
    # GIVEN: A media item with some mocked stuff
    MockSong.is_favourite.is_.return_value = 'is_true'
    MockSong.ccli_number.like.return_value = 'like 12345'
    MockSong.ccli_number.__ne__.return_value = 'ne ""'
    media_item.search_text_edit = MagicMock()
    media_item.search_text_edit.displayText.return_value = 'public domain'
    media_item.search_text_edit.current_search_type.return_value = SongSearch.CCLInumber
    media_item.favourite_toggle_button = MagicMock()
    media_item.favourite_toggle_button.isChecked.return_value = fav_filter
    with patch.object(media_item.plugin.manager, 'get_all_objects') as mocked_get_all_objects, \
            patch.object(media_item, 'display_results_cclinumber') as mocked_display_results:
        mocked_get_all_objects.return_value = ['Amazing Grace']

        # WHEN: on_search_text_button_clicked() is called
        media_item.on_search_text_button_clicked()

    # THEN: The correct calls should have been made
    if fav_filter:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'is_true', 'like 12345', 'ne ""')
    else:
        mocked_get_all_objects.assert_called_once_with(MockSong, 'like 12345', 'ne ""')
    mocked_display_results.assert_called_once_with(['Amazing Grace'])


def test_display_results_song(media_item):
    """
    Test displaying song search results with basic song
    """
    # GIVEN: Search results, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem:
        mocked_song = MagicMock(id=1, sort_key='My Song', song_detail='My Song (My Author)', temporary=False)
        mocked_song_temp = MagicMock(id=2, sort_key='My Temporary', song_detail='My Temporary (Skipped)',
                                     temporary=True)
        mock_search_results = [mocked_song, mocked_song_temp]
        mocked_list_item = MagicMock()
        MockedQListWidgetItem.return_value = mocked_list_item
        media_item.auto_select_id = 1

        # WHEN: I display song search results
        media_item.display_results_song(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        media_item.save_auto_select_id.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with(mocked_song.song_detail)
        mocked_list_item.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole, mocked_song.id)
        media_item.list_view.addItem.assert_called_once_with(mocked_list_item)
        media_item.list_view.setCurrentItem.assert_called_with(mocked_list_item)


@pytest.mark.parametrize('is_fav', [True, False])
def test_display_results_author(is_fav: bool, media_item: SongMediaItem):
    """
    Test displaying song search results grouped by author with basic song
    """
    # GIVEN: Search results grouped by author, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem:
        mocked_author = MagicMock(display_name='My Author')
        mocked_song_regular = MagicMock(id=1, title='My Song', sort_key='1',
                                        temporary=False, is_favourite=False)
        mocked_song_temp = MagicMock(id=2, title='My Song Temp', sort_key='2',
                                     temporary=True, is_favourite=False)
        mocked_song_fav = MagicMock(id=3, title='My Song Favourite', sort_key='3',
                                    temporary=False, is_favourite=True)
        mocked_author_song_regular = MagicMock(author=mocked_author, song=mocked_song_regular)
        mocked_author_song_temp = MagicMock(author=mocked_author, song=mocked_song_temp)
        mocked_author_song_fav = MagicMock(author=mocked_author, song=mocked_song_fav)
        mocked_author.authors_songs = [mocked_author_song_regular, mocked_author_song_temp,
                                       mocked_author_song_fav]
        mocked_search_results = [mocked_author]
        mocked_list_item_regular = MagicMock()
        mocked_list_item_favourite = MagicMock()
        if is_fav:
            MockedQListWidgetItem.side_effect = [mocked_list_item_favourite]
        else:
            MockedQListWidgetItem.side_effect = [mocked_list_item_regular, mocked_list_item_favourite]

        # WHEN: I display song search results grouped by author
        media_item.display_results_author(mocked_search_results, is_fav)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        if is_fav:
            MockedQListWidgetItem.assert_called_once_with('My Author (My Song Favourite)')
        else:
            assert MockedQListWidgetItem.call_args_list == [
                call('My Author (My Song)'),
                call('My Author (My Song Favourite)')
            ]
        if not is_fav:
            mocked_list_item_regular.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole,
                                                                     mocked_song_regular.id)
            assert call(mocked_list_item_regular) in media_item.list_view.addItem.call_args_list
        mocked_list_item_favourite.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole,
                                                                   mocked_song_fav.id)
        assert call(mocked_list_item_favourite) in media_item.list_view.addItem.call_args_list


def test_display_results_book(media_item: SongMediaItem):
    """
    Test displaying song search results grouped by book and entry with basic song
    """
    # GIVEN: Search results grouped by book and entry, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem:
        mock_search_results = [('1', 'My Book', 'My Song', 1)]
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget

        # WHEN: I display song search results grouped by book
        media_item.display_results_book(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('My Book #1: My Song')
        mock_qlist_widget.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole, 1)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)


def test_songbook_natural_sorting(media_item: SongMediaItem):
    """
    Test that songbooks are sorted naturally
    """
    # GIVEN: Search results grouped by book and entry
    search_results = [('2', 'Thy Book', 'Thy Song', 50),
                      ('2', 'My Book', 'Your Song', 7),
                      ('10', 'My Book', 'Our Song', 12),
                      ('1', 'My Book', 'My Song', 1),
                      ('2', 'Thy Book', 'A Song', 8)]

    # WHEN: I display song search results grouped by book
    media_item.display_results_book(search_results)

    # THEN: The songbooks are sorted inplace in the right (natural) order,
    #       grouped first by book, then by number, then by song title
    assert search_results == [('1', 'My Book', 'My Song', 1),
                              ('2', 'My Book', 'Your Song', 7),
                              ('10', 'My Book', 'Our Song', 12),
                              ('2', 'Thy Book', 'A Song', 8),
                              ('2', 'Thy Book', 'Thy Song', 50)]


@pytest.mark.parametrize('is_fav', [True, False])
def test_display_results_topic(is_fav: bool, media_item: SongMediaItem):
    """
    Test displaying song search results grouped by topic with basic song
    """
    # GIVEN: Search results grouped by topic, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem:
        mocked_song_regular = MagicMock(id=1, title='My Song', sort_key='1',
                                        temporary=False, is_favourite=False)
        mocked_song_temp = MagicMock(id=2, title='My Song Temp', sort_key='2',
                                     temporary=True, is_favourite=False)
        mocked_song_fav = MagicMock(id=3, title='My Song Favourite', sort_key='3',
                                    temporary=False, is_favourite=True)
        mocked_topic = MagicMock()
        # See https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
        mocked_topic.name = 'My Topic'
        mocked_topic.songs = [mocked_song_regular, mocked_song_temp, mocked_song_fav]
        mocked_search_results = [mocked_topic]
        mocked_list_item_regular = MagicMock()
        mocked_list_item_favourite = MagicMock()
        if is_fav:
            MockedQListWidgetItem.side_effect = [mocked_list_item_favourite]
        else:
            MockedQListWidgetItem.side_effect = [mocked_list_item_regular, mocked_list_item_favourite]

        # WHEN: I display song search results grouped by topic
        media_item.display_results_topic(mocked_search_results, is_fav)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        if is_fav:
            assert MockedQListWidgetItem.call_args_list == [
                call('My Topic (My Song Favourite)')
            ]
        else:
            assert MockedQListWidgetItem.call_args_list == [
                call('My Topic (My Song)'),
                call('My Topic (My Song Favourite)')
            ]
        if not is_fav:
            mocked_list_item_regular.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole,
                                                                     mocked_song_regular.id)
            assert call(mocked_list_item_regular) in media_item.list_view.addItem.call_args_list
        mocked_list_item_favourite.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole,
                                                                   mocked_song_fav.id)
        assert call(mocked_list_item_favourite) in media_item.list_view.addItem.call_args_list


def test_display_results_themes(media_item: SongMediaItem):
    """
    Test displaying song search results sorted by theme with basic song
    """
    # GIVEN: Search results sorted by theme, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem:
        mock_search_results = []
        mock_song = MagicMock()
        mock_song_temp = MagicMock()
        mock_song.id = 1
        mock_song.title = 'My Song'
        mock_song.sort_key = 'My Song'
        mock_song.theme_name = 'My Theme'
        mock_song.temporary = False
        mock_song_temp.id = 2
        mock_song_temp.title = 'My Temporary'
        mock_song_temp.sort_key = 'My Temporary'
        mock_song_temp.theme_name = 'My Theme'
        mock_song_temp.temporary = True
        mock_search_results.append(mock_song)
        mock_search_results.append(mock_song_temp)
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget

        # WHEN: I display song search results sorted by theme
        media_item.display_results_themes(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('My Theme (My Song)')
        mock_qlist_widget.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole, mock_song.id)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)


def test_display_results_cclinumber(media_item: SongMediaItem):
    """
    Test displaying song search results sorted by CCLI number with basic song
    """
    # GIVEN: Search results sorted by CCLI number, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem:
        mock_search_results = []
        mock_song = MagicMock()
        mock_song_temp = MagicMock()
        mock_song.id = 1
        mock_song.title = 'My Song'
        mock_song.sort_key = 'My Song'
        mock_song.ccli_number = '12345'
        mock_song.temporary = False
        mock_song_temp.id = 2
        mock_song_temp.title = 'My Temporary'
        mock_song_temp.sort_key = 'My Temporary'
        mock_song_temp.ccli_number = '12346'
        mock_song_temp.temporary = True
        mock_search_results.append(mock_song)
        mock_search_results.append(mock_song_temp)
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget

        # WHEN: I display song search results sorted by CCLI number
        media_item.display_results_cclinumber(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('12345 (My Song)')
        mock_qlist_widget.setData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole, mock_song.id)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)


def test_build_song_footer_two_authors(media_item: SongMediaItem):
    """
    Test build songs footer with basic song and two authors
    """
    # GIVEN: A Song and a Service Item
    mock_song = MagicMock()
    mock_song.title = 'My Song'
    mock_song.authors_songs = []
    mock_author = MagicMock()
    mock_author.display_name = 'my author'
    mock_author_song = MagicMock()
    mock_author_song.author = mock_author
    mock_author_song.author_type = AuthorType.Music
    mock_song.authors_songs.append(mock_author_song)
    mock_author = MagicMock()
    mock_author.display_name = 'another author'
    mock_author_song = MagicMock()
    mock_author_song.author = mock_author
    mock_author_song.author_type = AuthorType.Words
    mock_song.authors_songs.append(mock_author_song)
    mock_author = MagicMock()
    mock_author.display_name = 'translator'
    mock_author_song = MagicMock()
    mock_author_song.author = mock_author
    mock_author_song.author_type = AuthorType.Translation
    mock_song.authors_songs.append(mock_author_song)
    mock_song.copyright = 'My copyright'
    mock_song.songbook_entries = []
    service_item = ServiceItem(None)
    songbooks_str = []
    authors = media_item._get_music_authors(mock_song)
    mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    author_list = media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: I get the following Array returned
    assert service_item.raw_footer == ['My Song', 'Words: another author', 'Music: my author',
                                       'Translation: translator', '© My copyright'], \
        'The array should be returned correctly with a song, two authors and copyright'
    assert author_list == ['another author', 'my author', 'translator'], \
        'The author list should be returned correctly with two authors'


def test_build_song_footer_base_ccli(media_item: SongMediaItem):
    """
    Test build songs footer with basic song and a CCLI number
    """
    # GIVEN: A Song and a Service Item and a configured CCLI license
    mock_song = MagicMock()
    mock_song.title = 'My Song'
    mock_song.copyright = 'My copyright'
    mock_song.songbook_entries = []
    service_item = ServiceItem(None)
    media_item.settings.setValue('core/ccli number', '1234')
    songbooks_str = []
    authors = media_item._get_music_authors(mock_song)
    mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: I get the following Array returned
    assert service_item.raw_footer == ['My Song', '© My copyright', 'CCLI License: 1234'], \
        'The array should be returned correctly with a song, an author, copyright and ccli'

    # WHEN: I amend the CCLI value
    media_item.settings.setValue('core/ccli number', '4321')
    media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: I would get an amended footer string
    assert service_item.raw_footer == ['My Song', '© My copyright', 'CCLI License: 4321'], \
        'The array should be returned correctly with a song, an author, copyright and amended ccli'


def test_build_song_footer_base_songbook(media_item: SongMediaItem):
    """
    Test build songs footer with basic song and multiple songbooks
    """
    # GIVEN: A Song and a Service Item
    song = Song()
    song.title = 'My Song'
    song.alternate_title = ''
    song.copyright = 'My copyright'
    song.authors_songs = []
    song.songbook_entries = []
    song.alternate_title = ''
    song.topics = []
    song.ccli_number = ''
    book1 = MagicMock()
    book1.name = 'My songbook'
    book2 = MagicMock()
    book2.name = 'Thy songbook'
    song.songbook_entries = []
    song.add_songbook_entry(book1, '12')
    song.add_songbook_entry(book2, '502A')
    service_item = ServiceItem(None)
    songbooks_str = [str(songbook) for songbook in song.songbook_entries]
    authors = media_item._get_music_authors(song)
    mako_vars = media_item._get_mako_vars(song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    media_item.generate_footer(service_item, song, authors, songbooks_str, mako_vars)

    # THEN: The songbook should be in the footer
    assert service_item.raw_footer == ['My Song', '© My copyright', 'My songbook #12, Thy songbook #502A']


def test_build_song_footer_copyright_enabled(media_item: SongMediaItem):
    """
    Test building song footer with displaying the copyright symbol
    """
    # GIVEN: A Song and a Service Item; displaying the copyright symbol is enabled
    media_item.display_copyright_symbol = True
    mock_song = MagicMock()
    mock_song.title = 'My Song'
    mock_song.copyright = 'My copyright'
    mock_song.songbook_entries = []
    service_item = ServiceItem(None)
    songbooks_str = []
    authors = media_item._get_music_authors(mock_song)
    mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: The copyright symbol should be in the footer
    assert service_item.raw_footer == ['My Song', '© My copyright']


def test_build_song_footer_copyright_disabled(media_item: SongMediaItem):
    """
    Test building song footer without displaying the copyright symbol
    """
    # GIVEN: A Song and a Service Item; displaying the copyright symbol should be disabled by default
    mock_song = MagicMock()
    mock_song.title = 'My Song'
    mock_song.copyright = 'My copyright'
    mock_song.songbook_entries = []
    service_item = ServiceItem(None)
    songbooks_str = []
    authors = media_item._get_music_authors(mock_song)
    mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: The copyright symbol should not be in the footer
    assert service_item.raw_footer == ['My Song', '© My copyright']


def test_authors_match(media_item: SongMediaItem):
    """
    Test the author matching when importing a song from a service
    """
    # GIVEN: A song and a string with authors
    song = MagicMock()
    song.authors = []
    author = MagicMock()
    author.display_name = "Hans Wurst"
    song.authors.append(author)
    author2 = MagicMock()
    author2.display_name = "Max Mustermann"
    song.authors.append(author2)
    # There are occasions where an author appears twice in a song (with different types).
    # We need to make sure that this case works (lp#1313538)
    author3 = MagicMock()
    author3.display_name = "Max Mustermann"
    song.authors.append(author3)
    authors_str = "Hans Wurst, Max Mustermann, Max Mustermann"

    # WHEN: Checking for matching
    result = media_item._authors_match(song, authors_str)

    # THEN: They should match
    assert result is True, "Authors should match"


def test_authors_dont_match(media_item: SongMediaItem):
    # GIVEN: A song and a string with authors
    song = MagicMock()
    song.authors = []
    author = MagicMock()
    author.display_name = "Hans Wurst"
    song.authors.append(author)
    author2 = MagicMock()
    author2.display_name = "Max Mustermann"
    song.authors.append(author2)
    # There are occasions where an author appears twice in a song (with different types).
    # We need to make sure that this case works (lp#1313538)
    author3 = MagicMock()
    author3.display_name = "Max Mustermann"
    song.authors.append(author3)

    # WHEN: An author is missing in the string
    authors_str = "Hans Wurst, Max Mustermann"
    result = media_item._authors_match(song, authors_str)

    # THEN: They should not match
    assert result is False, "Authors should not match"


def test_build_remote_search(media_item: SongMediaItem):
    """
    Test results for the remote search api
    """
    # GIVEN: A Song and a search a JSON array should be returned.
    mock_song = MagicMock()
    mock_song.id = 123
    mock_song.title = 'My Song'
    mock_song.search_title = 'My Song'
    mock_song.alternate_title = 'My alternative'
    media_item.search_entire = MagicMock()
    media_item.search_entire.return_value = [mock_song]

    # WHEN: I process a search
    search_results = media_item.search('My Song', False)

    # THEN: The correct formatted results are returned
    assert search_results == [[123, 'My Song', 'My alternative']]


@patch('openlp.plugins.songs.lib.mediaitem.SongBook')
@patch('openlp.plugins.songs.lib.mediaitem.SongBookEntry')
@patch('openlp.plugins.songs.lib.mediaitem.Song')
@patch('openlp.plugins.songs.lib.mediaitem.or_')
def test_entire_song_search(mocked_or: MagicMock, MockedSong: MagicMock, MockedSongBookEntry: MagicMock,
                            MockedBook: MagicMock, media_item: SongMediaItem):
    """
    Test that searching the entire song does the right queries
    """
    # GIVEN: A song media item, a keyword and some mocks
    keyword = 'Jesus'
    mocked_or.side_effect = lambda a, b, c, d, e: ' '.join([a, b, c, d, e])
    MockedSong.search_title.like.side_effect = lambda a: a
    MockedSong.search_lyrics.like.side_effect = lambda a: a
    MockedSong.comments.like.side_effect = lambda a: a
    MockedSongBookEntry.entry.like.side_effect = lambda a: a
    MockedBook.name.like.side_effect = lambda a: a

    # WHEN: search_entire_song() is called with the keyword
    media_item.search_entire(keyword)

    # THEN: The correct calls were made
    MockedSong.search_title.like.assert_called_once_with('%jesus%')
    MockedSong.search_lyrics.like.assert_called_once_with('%jesus%')
    MockedSong.comments.like.assert_called_once_with('%jesus%')
    MockedSongBookEntry.entry.like.assert_called_once_with('%jesus%')
    MockedBook.name.like.assert_called_once_with('%jesus%')
    mocked_or.assert_called_once_with('%jesus%', '%jesus%', '%jesus%', '%jesus%', '%jesus%')
    media_item.plugin.manager.session.query.assert_called_once_with(MockedSong)

    assert media_item.plugin.manager.session.query.mock_calls[4][0] == '().join().join().filter().all'


def test_build_song_footer_one_author_show_written_by(media_item: SongMediaItem):
    """
    Test build songs footer with basic song and one author
    """
    # GIVEN: A Song and a Service Item, mocked settings
    media_item.settings.setValue('core/ccli number', "0")
    media_item.settings.setValue('songs/footer template', "")
    with patch('mako.template.Template.render_unicode') as MockedRenderer:
        mock_song = MagicMock()
        mock_song.title = 'My Song'
        mock_song.alternate_title = ''
        mock_song.ccli_number = ''
        mock_song.authors_songs = []
        mock_author = MagicMock()
        mock_author.display_name = 'my author'
        mock_author_song = MagicMock()
        mock_author_song.author = mock_author
        mock_song.authors_songs.append(mock_author_song)
        mock_song.copyright = 'My copyright'
        mock_song.songbook_entries = []
        service_item = ServiceItem(None)
        songbooks_str = []
        authors = media_item._get_music_authors(mock_song)
        mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

        # WHEN: I generate the Footer with default settings
        author_list = media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

        # THEN: The mako function was called with the following arguments
        args = {'authors_translation': [], 'authors_music_label': 'Music',
                'copyright': 'My copyright', 'songbook_entries': [],
                'alternate_title': '', 'topics': [], 'authors_music_all': [],
                'authors_words_label': 'Words', 'authors_music': [],
                'authors_words_music': [], 'ccli_number': '',
                'authors_none_label': 'Written by', 'title': 'My Song',
                'authors_words_music_label': 'Words and Music',
                'authors_none': ['my author'],
                'ccli_license_label': 'CCLI License', 'authors_words': [],
                'ccli_license': '0', 'authors_translation_label': 'Translation',
                'authors_words_all': [], 'first_slide': False}
        MockedRenderer.assert_called_once_with(**args)
        assert author_list == ['my author'], 'The author list should be returned correctly with one author'


@patch('openlp.plugins.songs.lib.mediaitem.SongMediaItem._get_id_of_item_to_generate')
@patch('openlp.plugins.songs.lib.mediaitem.SongXML.get_verses')
@pytest.mark.parametrize('first_slide_mode', SongFirstSlideMode)
def test_song_first_slide_creation_works(mocked_get_verses: MagicMock,
                                         mocked__get_id_of_item_to_generate: MagicMock,
                                         media_item: SongMediaItem,
                                         first_slide_mode: SongFirstSlideMode,
                                         settings: Settings):
    """
    Test building song with SongFirstSlideMode = Songbook works
    """
    # GIVEN: A Song and a Service Item
    mocked__get_id_of_item_to_generate.return_value = '00000000-0000-0000-0000-000000000000'
    settings.setValue('songs/first slide mode', first_slide_mode)
    mocked_get_verses.return_value = SONG_VERSES_TEST_LYRICS
    media_item.plugin = MagicMock()
    media_item.open_lyrics = OpenLyrics(media_item.plugin.manager)
    song = Song()
    song.title = 'My Song'
    song.alternate_title = ''
    song.copyright = 'My copyright'
    song.authors_songs = []
    song.songbook_entries = []
    song.alternate_title = ''
    song.lyrics = 'Teste'
    song.theme_name = 'Default'
    song.topics = []
    song.ccli_number = ''
    song.lyrics = '<fake xml>'  # Mocked by mocked_get_verses
    song.verse_order = SONG_VERSES_TEST_VERSE_ORDER
    song.search_title = 'my song@'
    song.last_modified = '2023-02-20T00:00:00Z'
    song.media_files = []
    song.comments = ''
    book1 = MagicMock()
    book1.name = 'My songbook'
    book1.publisher = None
    book2 = MagicMock()
    book2.name = 'Thy songbook'
    book2.publisher = 'Publisher'
    song.songbook_entries = []
    song.add_songbook_entry(book1, '12')
    song.add_songbook_entry(book2, '502A')
    service_item = ServiceItem(None)
    media_item.plugin.manager.get_object.return_value = song

    # WHEN: I generate the Footer with default settings
    media_item.generate_slide_data(service_item, item=song)

    # THEN: The copyright symbol should not be in the footer
    if first_slide_mode == SongFirstSlideMode.Default:
        # No metadata is needed on default slide mode (at least for now)
        assert 'metadata' not in service_item.slides[0]
    else:
        assert service_item.slides[0]['metadata']['songs_first_slide_type'] == first_slide_mode
    if first_slide_mode == SongFirstSlideMode.Songbook:
        assert service_item.slides[0]['text'] == '\nMy songbook #12\n\nThy songbook #502A (Publisher)\n\n'
    if first_slide_mode == SongFirstSlideMode.Footer:
        assert service_item.slides[0]['text'] == service_item.footer_html
        # It needs to have empty footer as it's already shown on text
        assert service_item.slides[0]['footer_html'] == ''


@patch('openlp.plugins.songs.lib.mediaitem.SongMediaItem._get_id_of_item_to_generate')
@patch('openlp.plugins.songs.lib.mediaitem.SongXML.get_verses')
def test_generate_slide_data_adds_preview_for_next_verse(mocked_get_verses: MagicMock,
                                                         mocked__get_id_of_item_to_generate: MagicMock,
                                                         media_item: SongMediaItem,
                                                         settings: Settings):
    """
    Simple test to check that previews are added for the next verse.
    When preview is enabled for verses, generate_slide_data should append the
    first line of the next verse wrapped in {preview}...{/preview}.
    """

    # GIVEN: A Song which has multiple verses and a preview setting enabled for verses
    mocked__get_id_of_item_to_generate.return_value = '00000000-0000-0000-0000-000000000000'
    settings.setValue('songs/preview_enabled', True)
    settings.setValue('songs/preview_verse', True)

    preview_verses = [
        [{'type': 'v', 'label': '1'}, 'Line 1 of the verse 1\nLine 2 of the verse 1'],
        [{'type': 'v', 'label': '2'}, 'Line 1 of the verse 2\nLine 2 of the verse 2']
    ]
    preview_order = 'v1 v2'

    mocked_get_verses.return_value = preview_verses
    media_item.plugin = MagicMock()
    media_item.open_lyrics = OpenLyrics(media_item.plugin.manager)

    # Build a Song instance
    song = Song()
    song.title = 'My Song'
    song.lyrics = '<fake xml>'  # Mocked by mocked_get_verses
    song.theme_name = 'Default'
    song.verse_order = preview_order
    media_item.plugin.manager.get_object.return_value = song
    service_item = ServiceItem(None)

    # The expected first slide text should contain the preview tag with the first line of the next verse
    expected_first_slide = (
        "Line 1 of the verse 1\n"
        "Line 2 of the verse 1\n"
        "{preview}Line 1 of the verse 2{/preview}"
    )

    # WHEN: I generate the slides
    media_item.generate_slide_data(service_item, item=song)

    # THEN: The first slide should contain the preview tag with the first line of the next verse
    slide_texts = [s['text'] for s in service_item.slides]
    assert slide_texts[0] == expected_first_slide, \
        f"Expected {expected_first_slide}, but got {slide_texts[0]}"


@patch('openlp.plugins.songs.lib.mediaitem.SongMediaItem._get_id_of_item_to_generate')
@patch('openlp.plugins.songs.lib.mediaitem.SongXML.get_verses')
def test_generate_slide_data_forced_split_previews_next_split(mocked_get_verses: MagicMock,
                                                              mocked__get_id_of_item_to_generate: MagicMock,
                                                              media_item: SongMediaItem,
                                                              settings: Settings):
    """
    If a verse contains a forced split [--}{--] the preview for the last split
    should be the first line of the next split (within the same verse),
    and the last split should preview the first line of the next verse.
    """

    #  GIVEN: A Song which has multiple verses with a split and a preview setting enabled for verses
    mocked__get_id_of_item_to_generate.return_value = '00000000-0000-0000-0000-000000000000'
    settings.setValue('songs/preview_enabled', True)
    settings.setValue('songs/preview_verse', True)

    preview_verses = [
        [{'type': 'v', 'label': '1'}, "Line 1 of the verse 1\n[--}{--]\nLine 2 of the verse 1\nLine 3 of the verse 1"],
        [{'type': 'v', 'label': '2'}, "Line 1 of the verse 2\nLine 2 of the verse 2"]
    ]

    preview_order = 'v1 v2'

    mocked_get_verses.return_value = preview_verses
    media_item.plugin = MagicMock()
    media_item.open_lyrics = OpenLyrics(media_item.plugin.manager)

    song = Song()
    song.title = 'Split Song'
    song.lyrics = '<fake xml>'
    song.theme_name = 'Default'
    song.verse_order = preview_order
    media_item.plugin.manager.get_object.return_value = song
    service_item = ServiceItem(None)

    # WHEN: I generate the slides
    media_item.generate_slide_data(service_item, item=song)

    # THEN: the preview for the last split should be the first line of the next split (within the same verse)
    # and the last split should preview the first line of the next verse.
    slide_texts = [s['text'] for s in service_item.slides]

    expected_slides = [
        "Line 1 of the verse 1\n{preview}Line 2 of the verse 1{/preview}",
        "Line 2 of the verse 1\nLine 3 of the verse 1\n{preview}Line 1 of the verse 2{/preview}"
    ]

    assert slide_texts[:2] == expected_slides, \
        f"Expected {expected_slides}, but got {slide_texts[:2]}"


@patch('openlp.plugins.songs.lib.mediaitem.SongMediaItem._get_id_of_item_to_generate')
@patch('openlp.plugins.songs.lib.mediaitem.SongXML.get_verses')
def test_generate_slide_data_adds_preview_for_selected_verses(mocked_get_verses: MagicMock,
                                                              mocked__get_id_of_item_to_generate: MagicMock,
                                                              media_item: SongMediaItem,
                                                              settings: Settings):
    """
    When preview is enabled for selected verses, generate_slide_data
    should append only for those in which were selected in the settings
    """

    # GIVEN: A Song which has multiple verses and a preview setting enabled for verses and bridge
    mocked__get_id_of_item_to_generate.return_value = '00000000-0000-0000-0000-000000000000'
    settings.setValue('songs/preview_enabled', True)
    settings.setValue('songs/preview_verse', True)
    settings.setValue('songs/preview_chorus', False)
    settings.setValue('songs/preview_bridge', True)

    preview_verses = [
        [{'type': 'v', 'label': '1'}, 'Line 1 of the verse 1\nLine 2 of the verse 1'],
        [{'type': 'v', 'label': '2'}, 'Line 1 of the verse 2\nLine 2 of the verse 2'],
        [{'type': 'c', 'label': '1'}, 'Line 1 of the chorus 1\nLine 2 of the chorus 1'],
        [{'type': 'b', 'label': '1'}, 'Line 1 of the bridge 1\nLine 2 of the bridge 1'],
    ]
    preview_order = 'v1 v2 c1 b1 v2'

    mocked_get_verses.return_value = preview_verses
    media_item.plugin = MagicMock()
    media_item.open_lyrics = OpenLyrics(media_item.plugin.manager)

    # Build a Song instance
    song = Song()
    song.title = 'My Song'
    song.lyrics = '<fake xml>'  # Mocked by mocked_get_verses
    song.theme_name = 'Default'
    song.verse_order = preview_order
    media_item.plugin.manager.get_object.return_value = song
    service_item = ServiceItem(None)

    # The expected slides should contain:
    # 1. V1 with preview for first line of verse 2 (enabled)
    # 2. V2 with no preview for chorus 1 (disabled)
    # 3. C1 with no preview for bridge 1 (disabled chorus)
    # 4. B1 with preview for verse 2 (enabled)
    expected_slides = [
        (
            "Line 1 of the verse 1\n"
            "Line 2 of the verse 1\n"
            "{preview}Line 1 of the verse 2{/preview}"
        ),
        (
            "Line 1 of the verse 2\n"
            "Line 2 of the verse 2"
        ),
        (
            "Line 1 of the chorus 1\n"
            "Line 2 of the chorus 1"
        ),
        (
            "Line 1 of the bridge 1\n"
            "Line 2 of the bridge 1\n"
            "{preview}Line 1 of the verse 2{/preview}"
        ),
        (
            "Line 1 of the verse 2\n"
            "Line 2 of the verse 2"
        )
    ]

    # WHEN: I generate the slides
    media_item.generate_slide_data(service_item, item=song)

    # THEN: The first slide should contain the preview tag with the first line of the next verse
    slide_texts = [s['text'] for s in service_item.slides]

    assert slide_texts == expected_slides, \
        f"Expected {expected_slides}, but got {slide_texts[0]}"


@patch('openlp.plugins.songs.lib.mediaitem.SongMediaItem._get_id_of_item_to_generate')
@patch('openlp.plugins.songs.lib.mediaitem.SongXML.get_verses')
@patch('openlp.plugins.songs.lib.mediaitem.Path')
def test_generate_slide_data_with_media_files_as_strings(MockPath: MagicMock, mocked_get_verses: MagicMock,
                                                         mocked__get_id_of_item_to_generate: MagicMock,
                                                         media_item: SongMediaItem, registry: Registry,
                                                         settings: Settings):
    """Test that generate_slide_data() correctly handles media files as strings"""
    # GIVEN: A Song which has multiple verses and a media file attached
    mocked__get_id_of_item_to_generate.return_value = '00000000-0000-0000-0000-000000000000'
    mocked_verses = [
        [{'type': 'v', 'label': '1'}, 'Line 1 of the verse 1\nLine 2 of the verse 1'],
        [{'type': 'v', 'label': '2'}, 'Line 1 of the verse 2\nLine 2 of the verse 2'],
        [{'type': 'c', 'label': '1'}, 'Line 1 of the chorus 1\nLine 2 of the chorus 1'],
        [{'type': 'b', 'label': '1'}, 'Line 1 of the bridge 1\nLine 2 of the bridge 1'],
    ]
    mocked_order = 'v1 v2 c1 b1 v2'
    mocked_get_verses.return_value = mocked_verses
    media_item.plugin = MagicMock()
    media_item.open_lyrics = OpenLyrics(media_item.plugin.manager)
    registry.register('media_plugin', MagicMock())
    State().load_settings()
    State().add_service('media', 1, True)
    State().update_pre_conditions('media', True)
    mocked_path = MagicMock()
    mocked_path.is_file.return_value = True
    MockPath.return_value = mocked_path

    # Build a Song instance
    song = Song()
    song.title = 'My Song'
    song.lyrics = '<fake xml>'  # Mocked by mocked_get_verses
    song.theme_name = 'Default'
    song.verse_order = mocked_order
    song.media_files = [MagicMock(file_path='/path/to/media-file.mp3', file_hash='1234567890')]
    media_item.plugin.manager.get_object.return_value = song
    service_item = ServiceItem(None)
    media_item.media_controller.media_length.return_value = 120

    # WHEN: I generate the slides
    # import pudb
    # pudb.set_trace()
    media_item.generate_slide_data(service_item, item=song)

    # THEN: The media file should have been added to the service item
    assert service_item.background_audio == [(mocked_path, '1234567890')]
    assert service_item.media_length == 120
