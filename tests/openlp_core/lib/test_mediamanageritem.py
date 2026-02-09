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
Package to test the openlp.core.lib.mediamanageritem package.
"""
import pytest
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.lib.mediamanageritem import MediaManagerItem


@pytest.fixture
def media_env():
    setup_patcher = patch('openlp.core.lib.mediamanageritem.MediaManagerItem._setup')
    setup_patcher.start()
    yield
    setup_patcher.stop


@patch('openlp.core.lib.mediamanageritem.MediaManagerItem.on_preview_click')
def test_on_double_clicked(mocked_on_preview_click, media_env, registry):
    """
    Test that when an item is double-clicked then the item is previewed
    """
    # GIVEN: A setting to enable "Double-click to go live" and a media manager item
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = False
    Registry().register('settings', mocked_settings)
    mmi = MediaManagerItem(None)
    mmi.can_preview = True
    mmi.can_make_live = True
    mmi.can_add_to_service = True

    # WHEN: on_double_clicked() is called
    mmi.on_double_clicked()

    # THEN: on_preview_click() should have been called
    mocked_on_preview_click.assert_called_with()


def test_required_icons(media_env):
    """
    Test the default icons for plugins
    """
    # GIVEN: A MediaManagerItem
    mmi = MediaManagerItem(None)
    # WHEN: Object is created
    mmi.required_icons()
    # THEN: Default icons should be populated
    assert mmi.has_import_icon is False, 'There should be no import icon by default'
    assert mmi.has_new_icon is True, 'By default a new icon should be present'
    assert mmi.has_file_icon is False, 'There should be no file icon by default'
    assert mmi.has_delete_icon is True, 'By default a delete icon should be present'
    assert mmi.add_to_service_item is False, 'There should be no add_to_service icon by default'
    assert mmi.can_preview is True, 'There should be a preview icon by default'
    assert mmi.can_make_live is True, 'There should be a make live by default'
    assert mmi.can_add_to_service is True, 'There should be a add to service icon by default'


@patch('openlp.core.lib.mediamanageritem.MediaManagerItem.on_live_click')
def test_on_double_clicked_go_live(mocked_on_live_click, media_env, registry):
    """
    Test that when "Double-click to go live" is enabled that the item goes live
    """
    # GIVEN: A setting to enable "Double-click to go live" and a media manager item
    mocked_settings = MagicMock()
    mocked_settings.value.side_effect = lambda x: x == 'advanced/double click live'
    Registry().register('settings', mocked_settings)
    mmi = MediaManagerItem(None)
    mmi.can_preview = True
    mmi.can_make_live = True
    mmi.can_add_to_service = True

    # WHEN: on_double_clicked() is called
    mmi.on_double_clicked()

    # THEN: on_live_click() should have been called
    mocked_on_live_click.assert_called_with()


@patch('openlp.core.lib.mediamanageritem.MediaManagerItem.on_live_click')
@patch('openlp.core.lib.mediamanageritem.MediaManagerItem.on_preview_click')
def test_on_double_clicked_single_click_preview(mocked_on_preview_click, mocked_on_live_click, media_env, registry):
    """
    Test that when "Single-click preview" is enabled then nothing happens on double-click
    """
    # GIVEN: A setting to enable "Double-click to go live" and a media manager item
    mocked_settings = MagicMock()
    mocked_settings.value.side_effect = lambda x: x == 'advanced/single click preview'
    Registry().register('settings', mocked_settings)
    mmi = MediaManagerItem(None)
    mmi.can_preview = True
    mmi.can_make_live = True
    mmi.can_add_to_service = True

    # WHEN: on_double_clicked() is called
    mmi.on_double_clicked()

    # THEN: on_live_click() should have been called
    assert 0 == mocked_on_live_click.call_count, 'on_live_click() should not have been called'
    assert 0 == mocked_on_preview_click.call_count, 'on_preview_click() should not have been called'


def test_search_options(media_env):
    """
    Test that the default search options return a empty list
    """
    # GIVEN: A media manager item
    mmi = MediaManagerItem(None)

    # WHEN: The search options are requested
    result = mmi.search_options()

    # THEN: should return a empty list
    assert result == []


def test_set_search_option(media_env):
    """
    Test that the default set search option return false because it's setting a non existant setting
    """
    # GIVEN: A media manager item
    mmi = MediaManagerItem(None)

    # WHEN: The a search option is set
    result = mmi.set_search_option('my option', 'my value')

    # THEN: should return false
    assert result is False
