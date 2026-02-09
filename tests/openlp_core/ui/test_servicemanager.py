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
Package to test the openlp.core.ui.slidecontroller package.
"""
import json
import threading
from functools import partial
from pathlib import Path
from time import sleep
from unittest.mock import Mock, MagicMock, call, patch
from zipfile import BadZipFile

import pytest
from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common import ThemeLevel
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.state import State
from openlp.core.common.enum import ServiceItemType
from openlp.core.lib.exceptions import ValidationError
from openlp.core.lib.serviceitem import ItemCapabilities, ServiceItem
from openlp.core.ui.servicemanager import ServiceManager, ServiceManagerList
from openlp.core.widgets.toolbar import OpenLPToolbar

from tests.utils.constants import RESOURCE_PATH

BIBLE_VERSES = (
    'In the beginning, God created the heavens and the earth. The earth was formless and empty. Darkness '
    'was on the surface of the deep and God\'s Spirit was hovering over the surface of the waters.'
)


def _create_mock_action(s_manager: ServiceManager, name: str, **kwargs):
    """
    Create a fake action with some "real" attributes
    """
    action = QtGui.QAction(s_manager.toolbar)
    action.setObjectName(name)
    if kwargs.get('triggers'):
        action.triggered.connect(kwargs.pop('triggers'))
    s_manager.toolbar.actions_map[name] = action
    return action


def _add_song_service_item(s_manager: ServiceManager):
    """Add a mocked songs service item to the passed service manager"""
    mocked_plugin = MagicMock()
    mocked_plugin.name = 'songs'
    service_item = ServiceItem(mocked_plugin)
    service_item.add_icon()
    slide = 'Test slide'
    service_item.add_from_text(slide)
    service_item.title = 'Test item'
    service_item.service_item_type = ServiceItemType.Text
    service_item.background_audio = [(Path('myfile.mp3'), None), (Path('myfile.mp3'), None)]
    s_manager.add_service_item(service_item, rebuild=True, repaint=False, selected=True)
    return service_item


def _add_bible_service_item(s_manager: ServiceManager):
    """Add a mocked Bible service item to the passed service manager"""
    mocked_plugin = MagicMock()
    mocked_plugin.name = 'bibles'
    service_item = ServiceItem(mocked_plugin)
    service_item.add_icon()
    service_item.add_from_text(BIBLE_VERSES)
    service_item.title = 'Genesis 1:1-2'
    service_item.add_capability(ItemCapabilities.CanWordSplit)
    service_item.add_capability(ItemCapabilities.CanPreview)
    service_item.add_capability(ItemCapabilities.CanLoop)
    service_item.add_capability(ItemCapabilities.CanEditTitle)
    service_item.service_item_type = ServiceItemType.Text
    s_manager.add_service_item(service_item, rebuild=True, repaint=False, selected=False)
    return service_item


def _add_presentation_service_item(s_manager: ServiceManager, has_valid_thumb: bool = True):
    """Add a mocked Presentation service item to the passed service manager"""
    mocked_plugin = MagicMock()
    mocked_plugin.name = 'presentations'
    service_item = ServiceItem(mocked_plugin)
    service_item.add_icon()
    if has_valid_thumb:
        service_item.slides = [
            {
                'title': 'test.ppt',
                'image': str(RESOURCE_PATH / 'presentations' / 'img0.jpg'),
                'path': RESOURCE_PATH / 'presentations',
                'display_title': 'Slide 1',
                'notes': '',
                'thumbnail': str(RESOURCE_PATH / 'presentations' / 'img0.jpg')
            }
        ]
    else:
        service_item.slides = [
            {
                'title': 'test.ppt',
                'image': 'fake/path/img0.jpg',
                'path': '',
                'display_title': 'Slide 1',
                'notes': '',
                'thumbnail': 'fake/path/img0.jpg'
            }
        ]
    service_item.title = 'TestPresentation.odp'
    service_item.add_capability(ItemCapabilities.CanEditTitle)
    service_item.add_capability(ItemCapabilities.ProvidesOwnDisplay)
    service_item.add_capability(ItemCapabilities.HasDisplayTitle)
    service_item.add_capability(ItemCapabilities.HasThumbnails)
    service_item.service_item_type = ServiceItemType.Command
    s_manager.add_service_item(service_item, rebuild=True, repaint=False, selected=False)
    return service_item


def _add_image_service_item(s_manager: ServiceManager, has_valid_image: bool = True):
    """Add a mocked songs service item to the passed service manager"""
    mocked_plugin = MagicMock()
    mocked_plugin.name = 'images'
    service_item = ServiceItem(mocked_plugin)
    service_item.add_icon()
    service_item.title = 'Images'
    service_item.service_item_type = ServiceItemType.Image
    service_item.add_capability(ItemCapabilities.CanMaintain)
    service_item.add_capability(ItemCapabilities.CanPreview)
    service_item.add_capability(ItemCapabilities.CanLoop)
    service_item.add_capability(ItemCapabilities.CanAppend)
    service_item.add_capability(ItemCapabilities.CanEditTitle)
    service_item.add_capability(ItemCapabilities.HasThumbnails)
    service_item.add_capability(ItemCapabilities.ProvidesOwnTheme)
    if has_valid_image:
        service_item.add_from_image(RESOURCE_PATH / 'church.jpg', 'church.jpg')
    else:
        service_item.add_from_image(Path('fake/path/church.jpg'), 'church.jpg')
    s_manager.add_service_item(service_item, rebuild=True, repaint=False, selected=True)
    return service_item


@pytest.fixture()
def service_manager(registry: Registry, settings: Settings):
    """Setup a service manager with a service item and a few mocked registry entries"""
    # Mocked registry entries
    registry.register('main_window', MagicMock())
    registry.register('live_controller', MagicMock())
    registry.register('renderer', MagicMock())
    registry.register('plugin_manager', MagicMock())
    settings.setValue('advanced/new service message', False)

    # Service manager
    svc_manager = ServiceManager()
    _add_toolbar_action = partial(_create_mock_action, svc_manager)
    add_toolbar_action_patcher = patch('openlp.core.ui.servicemanager.OpenLPToolbar.add_toolbar_action')
    mocked_add_toolbar_action = add_toolbar_action_patcher.start()
    mocked_add_toolbar_action.side_effect = _add_toolbar_action
    svc_manager.setup_ui(svc_manager)

    yield svc_manager
    del svc_manager

    add_toolbar_action_patcher.stop()


def _setup_service_manager_list(service_manager: ServiceManager):
    service_manager.expanded = MagicMock()
    service_manager.collapsed = MagicMock()
    verse_1 = QtWidgets.QTreeWidgetItem(0)
    verse_2 = QtWidgets.QTreeWidgetItem(0)
    song_item = QtWidgets.QTreeWidgetItem(0)
    song_item.addChild(verse_1)
    song_item.addChild(verse_2)
    service_manager.setup_ui(service_manager)
    service_manager.service_manager_list.addTopLevelItem(song_item)
    return verse_1, verse_2, song_item


def test_initial_service_manager(mock_settings: MagicMock):
    """
    Test the initial of service manager.
    """
    # GIVEN: A new service manager instance.
    ServiceManager(None)
    # WHEN: the default service manager is built.
    # THEN: The the controller should be registered in the registry.
    assert Registry().get('service_manager') is not None, 'The base service manager should be registered'


def test_new_file(registry: Registry):
    """Test the new_file() method"""
    # GIVEN: A service manager
    mocked_settings = MagicMock()
    mocked_plugin_manager = MagicMock()
    mocked_main_window = MagicMock()
    mocked_slide_controller = MagicMock()
    registry.register('settings', mocked_settings)
    registry.register('plugin_manager', mocked_plugin_manager)
    registry.register('main_window', mocked_main_window)
    registry.register('live_controller', mocked_slide_controller)
    service_manager = ServiceManager(None)
    service_manager.service_items = [MagicMock(), MagicMock()]
    service_manager.service_id = 5
    service_manager._service_path = 'service.osz'
    service_manager._modified = True
    service_manager.service_manager_list = MagicMock()
    service_manager.plugin_manager.new_service_created = MagicMock()

    # WHEN: new_file() is called
    service_manager.new_file()

    # THEN: Everything should be correct
    service_manager.service_manager_list.clear.assert_called_once_with()
    assert service_manager.service_items == [], 'The list of service items should be blank'
    assert service_manager._service_path is None, 'The file_name should be None'
    assert service_manager.service_id == 7, 'The service id should be 6'
    mocked_settings.setValue.assert_called_with('servicemanager/last file', None)
    mocked_plugin_manager.new_service_created.assert_called_once_with()
    assert mocked_slide_controller.slide_count == 0, 'Slide count should be zero'


def test_create_basic_service(settings: Settings):
    """
    Test the create basic service array
    """
    # GIVEN: A new service manager instance.
    service_manager = ServiceManager(None)
    # WHEN: when the basic service array is created.
    service_manager._save_lite = False
    service_manager.service_theme = 'test_theme'
    service = service_manager.create_basic_service()[0]
    # THEN: The controller should be registered in the registry.
    assert service is not None, 'The base service should be created'
    assert service['openlp_core']['service-theme'] == 'test_theme', 'The test theme should be saved'
    assert service['openlp_core']['lite-service'] is False, 'The lite service should be saved'


def test_is_modified(settings: Settings):
    """
    Test the is_modified() method
    """
    # GIVEN: A service manager with the self._modified set
    service_manager = ServiceManager(None)
    service_manager._modified = True

    # WHEN: is_modified is called
    result = service_manager.is_modified()

    # THEN: The result should be True
    assert result is True, 'is_modified should return True'


def test_build_context_menu(settings: Settings):
    """
    Test the creation of a context menu from a null service item.
    """
    # GIVEN: A new service manager instance and a default service item.
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have been called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have been called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have been called once'


def test_build_song_context_menu(settings: Settings, state: State):
    """
    Test the creation of a context menu from service item of type text from Songs.
    """
    # GIVEN: A new service manager instance and a default service item.
    mocked_renderer = MagicMock()
    mocked_renderer.theme_level = ThemeLevel.Song
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', mocked_renderer)
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    for capability in [ItemCapabilities.CanEdit, ItemCapabilities.CanPreview, ItemCapabilities.CanLoop,
                       ItemCapabilities.OnLoadUpdate, ItemCapabilities.AddIfNewItem,
                       ItemCapabilities.CanSoftBreak]:
        service_item.add_capability(capability)
    service_item.service_item_type = ServiceItemType.Text
    service_item.edit_id = 1
    service_item._display_slides = []
    service_item._display_slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    # THEN we add a 2nd display frame
    service_item._display_slides.append(MagicMock())
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.timed_slide_interval.setChecked.call_count == 1, 'Should have be called once'


def test_build_bible_context_menu(settings: Settings, state: State):
    """
    Test the creation of a context menu from service item of type text from Bibles.
    """
    # GIVEN: A new service manager instance and a default service item.
    mocked_renderer = MagicMock()
    mocked_renderer.theme_level = ThemeLevel.Song
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', mocked_renderer)
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    for capability in [ItemCapabilities.NoLineBreaks, ItemCapabilities.CanPreview,
                       ItemCapabilities.CanLoop, ItemCapabilities.CanWordSplit,
                       ItemCapabilities.CanEditTitle]:
        service_item.add_capability(capability)
    service_item.service_item_type = ServiceItemType.Text
    service_item.edit_id = 1
    service_item._display_slides = []
    service_item._display_slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    # THEN we add a 2nd display frame
    service_item._display_slides.append(MagicMock())
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.timed_slide_interval.setChecked.call_count == 1, 'Should have be called once'


def test_build_custom_context_menu(settings: Settings, state: State):
    """
    Test the creation of a context menu from service item of type text from Custom.
    """
    # GIVEN: A new service manager instance and a default service item.
    mocked_renderer = MagicMock()
    mocked_renderer.theme_level = ThemeLevel.Song
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', mocked_renderer)
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.CanEdit)
    service_item.add_capability(ItemCapabilities.CanPreview)
    service_item.add_capability(ItemCapabilities.CanLoop)
    service_item.add_capability(ItemCapabilities.CanSoftBreak)
    service_item.add_capability(ItemCapabilities.OnLoadUpdate)
    service_item.service_item_type = ServiceItemType.Text
    service_item.edit_id = 1
    service_item._display_slides = []
    service_item._display_slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    # THEN we add a 2nd display frame
    service_item._display_slides.append(MagicMock())
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.timed_slide_interval.setChecked.call_count == 1, 'Should have be called once'


def test_build_image_context_menu(settings: Settings):
    """
    Test the creation of a context menu from service item of type Image from Image.
    """
    # GIVEN: A new service manager instance and a default service item.
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.CanMaintain)
    service_item.add_capability(ItemCapabilities.CanPreview)
    service_item.add_capability(ItemCapabilities.CanLoop)
    service_item.add_capability(ItemCapabilities.CanAppend)
    service_item.add_capability(ItemCapabilities.CanEditTitle)
    service_item.service_item_type = ServiceItemType.Image
    service_item.edit_id = 1
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    # THEN we add a 2nd display frame and regenerate the menu.
    service_item.slides.append(MagicMock())
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 2, \
        'Should have be called twice'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 1, 'Should have be called once'
    assert service_manager.timed_slide_interval.setChecked.call_count == 1, 'Should have be called once'


def test_build_media_context_menu(settings: Settings):
    """
    Test the creation of a context menu from service item of type Command from Media.
    """
    # GIVEN: A new service manager instance and a default service item.
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.CanAutoStartForLive)
    service_item.add_capability(ItemCapabilities.CanEditTitle)
    service_item.add_capability(ItemCapabilities.RequiresMedia)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    # THEN I change the length of the media and regenerate the menu.
    service_item.set_media_length(5)
    service_manager.context_menu(1)
    # THEN the following additional calls should have occurred.
    assert service_manager.time_action.setVisible.call_count == 3, 'Should have be called three times'


def test_build_presentation_pdf_context_menu(settings: Settings):
    """
    Test the creation of a context menu from service item of type Command with PDF from Presentation.
    """
    # GIVEN: A new service manager instance and a default service item.
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.CanMaintain)
    service_item.add_capability(ItemCapabilities.CanPreview)
    service_item.add_capability(ItemCapabilities.CanLoop)
    service_item.add_capability(ItemCapabilities.CanAppend)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 2, 'Should have be called twice'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'


def test_build_presentation_non_pdf_context_menu(settings: Settings):
    """
    Test the creation of a context menu from service item of type Command with Impress from Presentation.
    """
    # GIVEN: A new service manager instance and a default service item.
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    service_manager = ServiceManager(None)
    item = MagicMock()
    item.parent.return_value = False
    item.data.return_value = 0
    service_manager.service_manager_list = MagicMock()
    service_manager.service_manager_list.itemAt.return_value = item
    service_item = ServiceItem(None)
    service_item.add_capability(ItemCapabilities.ProvidesOwnDisplay)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item})
    service_manager.edit_action = MagicMock()
    service_manager.rename_action = MagicMock()
    service_manager.create_custom_action = MagicMock()
    service_manager.maintain_action = MagicMock()
    service_manager.notes_action = MagicMock()
    service_manager.time_action = MagicMock()
    service_manager.auto_start_action = MagicMock()
    service_manager.auto_play_slides_menu = MagicMock()
    service_manager.auto_play_slides_once = MagicMock()
    service_manager.auto_play_slides_loop = MagicMock()
    service_manager.timed_slide_interval = MagicMock()
    service_manager.theme_menu = MagicMock()
    service_manager.menu = MagicMock()
    # WHEN I define a context menu
    service_manager.context_menu(1)
    # THEN the following calls should have occurred.
    assert service_manager.edit_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.rename_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.create_custom_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.maintain_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.notes_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.time_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_start_action.setVisible.call_count == 1, 'Should have be called once'
    assert service_manager.auto_play_slides_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'
    assert service_manager.auto_play_slides_once.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.auto_play_slides_loop.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.timed_slide_interval.setChecked.call_count == 0, 'Should not be called'
    assert service_manager.theme_menu.menuAction().setVisible.call_count == 1, \
        'Should have be called once'


@patch('openlp.core.ui.servicemanager.QtCore.QTimer.singleShot')
def test_single_click_preview_true(mocked_singleShot: MagicMock, settings: Settings):
    """
    Test that when "Preview items when clicked in Service Manager" enabled the preview timer starts
    """
    # GIVEN: A setting to enable "Preview items when clicked in Service Manager" and a service manager.
    settings.setValue('advanced/single click service preview', True)
    service_manager = ServiceManager(None)
    # WHEN: on_single_click_preview() is called
    service_manager.on_single_click_preview()
    # THEN: timer should have been started
    mocked_singleShot.assert_called_with(QtWidgets.QApplication.instance().doubleClickInterval(),
                                         service_manager.on_single_click_preview_timeout)


@patch('openlp.core.ui.servicemanager.QtCore.QTimer.singleShot')
def test_single_click_preview_false(mocked_singleShot: MagicMock, settings: Settings):
    """
    Test that when "Preview items when clicked in Service Manager" disabled the preview timer doesn't start
    """
    # GIVEN: A setting to enable "Preview items when clicked in Service Manager" and a service manager.
    settings.setValue('advanced/single click service preview', False)
    service_manager = ServiceManager(None)
    # WHEN: on_single_click_preview() is called
    service_manager.on_single_click_preview()
    # THEN: timer should not be started
    assert mocked_singleShot.call_count == 0, 'Should not be called'


@patch('openlp.core.ui.servicemanager.QtCore.QTimer.singleShot')
def test_single_click_preview_double(mocked_singleShot: MagicMock, settings: Settings):
    """
    Test that when a double click has registered the preview timer doesn't start
    """
    # GIVEN: A setting to enable "Preview items when clicked in Service Manager" and a service manager.
    settings.setValue('advanced/single click service preview', True)
    service_manager = ServiceManager(None)

    # WHEN: on_single_click_preview() is called following a double click
    with patch.object(service_manager, 'make_live') as mocked_make_live:
        service_manager.on_double_click_live()
        service_manager.on_single_click_preview()

    # THEN: timer should not be started
    mocked_make_live.assert_called_with()
    assert mocked_singleShot.call_count == 0, 'Should not be called'


def test_single_click_timeout_single(settings: Settings):
    """
    Test that when a single click has been registered, the item is sent to preview
    """
    # GIVEN: A service manager.
    service_manager = ServiceManager(None)

    # WHEN: on_single_click_preview() is called
    with patch.object(service_manager, 'make_preview') as mocked_make_preview:
        service_manager.on_single_click_preview_timeout()

    # THEN: make_preview() should have been called
    assert mocked_make_preview.call_count == 1, 'ServiceManager.make_preview() should have been called once'


def test_single_click_timeout_double(settings: Settings):
    """
    Test that when a double click has been registered, the item does not goes to preview
    """
    # GIVEN: A service manager.
    service_manager = ServiceManager(None)

    # WHEN: on_single_click_preview() is called after a double click
    with patch.object(service_manager, 'make_preview') as mocked_make_preview, \
            patch.object(service_manager, 'make_live') as mocked_make_live:
        service_manager.on_double_click_live()
        service_manager.on_single_click_preview_timeout()

    # THEN: make_preview() should not have been called
    assert mocked_make_preview.call_count == 0, 'ServiceManager.make_preview() should not be called'
    assert mocked_make_live.call_count == 1, 'ServiceManager.make_live() should have been called once'


@patch('openlp.core.ui.servicemanager.zipfile')
@patch('openlp.core.ui.servicemanager.shutil')
def test_save_file_raises_permission_error(mocked_shutil: MagicMock, mocked_zipfile: MagicMock,
                                           settings: Settings):
    """
    Test that when a PermissionError is raised when trying to save a file, it is handled correctly
    """
    # GIVEN: A service manager, a service to save
    mocked_main_window = MagicMock()
    Registry().register('main_window', mocked_main_window)
    service_manager = ServiceManager(None)
    service_manager._service_path = MagicMock()
    service_manager._save_lite = False
    service_manager.service_items = []
    service_manager.service_theme = 'Default'
    service_manager.service_manager_list = MagicMock()
    mocked_zipfile.ZipFile.return_value = MagicMock()
    mocked_shutil.move.side_effect = PermissionError

    # WHEN: The service is saved and a PermissionError is raised
    with patch.object(service_manager, 'save_file_as') as mocked_save_file_as:
        mocked_save_file_as.return_value = False
        result = service_manager.save_file()

    # THEN: The "save_as" method is called to save the service
    assert result is False
    mocked_save_file_as.assert_called_with()


@patch('openlp.core.ui.servicemanager.zipfile')
@patch('openlp.core.ui.servicemanager.os')
@patch('openlp.core.ui.servicemanager.shutil')
@patch('openlp.core.ui.servicemanager.len')
def test_save_file_large_file(mocked_len: MagicMock, mocked_shutil: MagicMock, mocked_os: MagicMock,
                              mocked_zipfile: MagicMock, registry: Registry):
    """
    Test that when a file size size larger than a 32bit signed int is attempted to save, the progress bar
    should be provided a value that fits in a 32bit int (because it's passed to C++ as a 32bit unsigned int)
    """
    # GIVEN: A service manager, a service to save, and len() returns a huge value (file size)
    def check_for_i32_overflow(val):
        if val > 2147483647:
            raise OverflowError
    mocked_main_window = MagicMock()
    mocked_main_window.display_progress_bar.side_effect = check_for_i32_overflow
    Registry().register('main_window', mocked_main_window)
    Registry().register('application', MagicMock())
    Registry().register('settings', MagicMock())
    service_manager = ServiceManager(None)
    service_manager._service_path = MagicMock()
    service_manager._save_lite = False
    service_manager.service_items = []
    service_manager.service_theme = 'Default'
    service_manager.service_manager_list = MagicMock()
    mocked_zipfile.ZipFile.return_value = MagicMock()
    mocked_len.return_value = 10000000000000

    # WHEN: The service is saved and no error is raised
    with patch.object(service_manager, 'save_file_as') as mocked_save_file_as:
        mocked_save_file_as.return_value = False
        result = service_manager.save_file()

    # THEN: The "save_as" method is called to save the service
    assert result is True
    mocked_save_file_as.assert_not_called()


def test_theme_change_global(settings: Settings):
    """
    Test that when a Toolbar theme combobox displays correctly when the theme is set to Global
    """
    # GIVEN: A service manager, settings set to Global theme
    service_manager = ServiceManager(None)
    service_manager.toolbar = OpenLPToolbar(None)
    service_manager.toolbar.add_toolbar_action('theme_combo_box', triggers=MagicMock())
    service_manager.toolbar.add_toolbar_action('theme_label', triggers=MagicMock())
    settings.setValue('themes/theme level', ThemeLevel.Global)

    # WHEN: theme_change is called
    with patch.object(service_manager, 'regenerate_service_items'):
        service_manager.on_theme_level_changed()

    # THEN: The the theme toolbar should not be visible
    assert service_manager.toolbar.actions_map['theme_combo_box'].isVisible() is False, \
        'The visibility should be False'


def test_theme_change_service(settings: Settings):
    """
    Test that when a Toolbar theme combobox displays correctly when the theme is set to Theme
    """
    # GIVEN: A service manager, settings set to Service theme
    service_manager = ServiceManager(None)
    service_manager.toolbar = OpenLPToolbar(None)
    service_manager.toolbar.add_toolbar_action('theme_combo_box', triggers=MagicMock())
    service_manager.toolbar.add_toolbar_action('theme_label', triggers=MagicMock())
    settings.setValue('themes/theme level', ThemeLevel.Service)

    # WHEN: theme_change is called
    with patch.object(service_manager, 'regenerate_service_items'):
        service_manager.on_theme_level_changed()

    # THEN: The the theme toolbar should be visible
    assert service_manager.toolbar.actions_map['theme_combo_box'].isVisible() is True, \
        'The visibility should be True'


def test_theme_change_song(settings: Settings):
    """
    Test that when a Toolbar theme combobox displays correctly when the theme is set to Song
    """
    # GIVEN: A service manager, settings set to Song theme
    service_manager = ServiceManager(None)
    service_manager.toolbar = OpenLPToolbar(None)
    service_manager.toolbar.add_toolbar_action('theme_combo_box', triggers=MagicMock())
    service_manager.toolbar.add_toolbar_action('theme_label', triggers=MagicMock())
    settings.setValue('themes/theme level', ThemeLevel.Song)

    # WHEN: theme_change is called
    with patch.object(service_manager, 'regenerate_service_items'):
        service_manager.on_theme_level_changed()

    # THEN: The the theme toolbar should be visible
    assert service_manager.toolbar.actions_map['theme_combo_box'].isVisible() is True, \
        'The visibility should be True'


@patch('PySide6.QtWidgets.QTreeWidgetItemIterator')
def test_regenerate_service_items(mocked_tree: MagicMock, settings: Settings):
    """
    test that an unmodified service item that is regenerated is still unmodified
    """
    # GIVEN: A service manager and a service item
    mocked_main_window = MagicMock()
    Registry().register('main_window', mocked_main_window)
    service_manager = ServiceManager(None)
    service_item = ServiceItem(None)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.icon = MagicMock(pixmap=MagicMock())
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item, 'expanded': False})
    service_manager._modified = False
    service_manager.service_manager_list = MagicMock()
    service_manager.repaint_service_list = MagicMock()
    mocked_tree.return_value = MagicMock(value=MagicMock(return_value=None))

    # WHEN: regenerate_service_items is called
    service_manager.regenerate_service_items()

    # THEN: The the service should be repainted and not be marked as modified
    assert service_manager.is_modified() is False
    service_manager.repaint_service_list.assert_called_once()


@patch('PySide6.QtWidgets.QTreeWidgetItemIterator')
def test_regenerate_service_items_modified(mocked_tree: MagicMock, settings: Settings):
    """
    test that an unmodified service item that is regenerated is still unmodified
    """
    # GIVEN: A service manager and a service item
    mocked_main_window = MagicMock()
    Registry().register('main_window', mocked_main_window)
    service_manager = ServiceManager(None)
    service_item = ServiceItem(None)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.icon = MagicMock(pixmap=MagicMock())
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item, 'expanded': False})
    service_manager._modified = True
    service_manager.service_manager_list = MagicMock()
    service_manager.repaint_service_list = MagicMock()
    mocked_tree.return_value = MagicMock(value=MagicMock(return_value=None))

    # WHEN: regenerate_service_items is called
    service_manager.regenerate_service_items()

    # THEN: The the service should be repainted and still be marked as modified
    assert service_manager.is_modified() is True
    service_manager.repaint_service_list.assert_called_once()


@patch('PySide6.QtWidgets.QTreeWidgetItemIterator')
def test_regenerate_service_items_set_modified(mocked_tree: MagicMock, settings: Settings):
    """
    test that a service item that is regenerated with the modified argument becomes modified
    """
    # GIVEN: A service manager and a service item
    mocked_main_window = MagicMock()
    Registry().register('main_window', mocked_main_window)
    service_manager = ServiceManager(None)
    service_item = ServiceItem(None)
    service_item.service_item_type = ServiceItemType.Command
    service_item.edit_id = 1
    service_item.icon = MagicMock(pixmap=MagicMock())
    service_item.slides.append(MagicMock())
    service_manager.service_items.insert(1, {'service_item': service_item, 'expanded': False})
    service_manager._modified = False
    service_manager.service_manager_list = MagicMock()
    service_manager.repaint_service_list = MagicMock()
    mocked_tree.return_value = MagicMock(value=MagicMock(return_value=None))

    # WHEN: regenerate_service_items is called
    service_manager.regenerate_service_items(True)

    # THEN: The the service should be repainted and now be marked as modified
    assert service_manager.is_modified() is True
    service_manager.repaint_service_list.assert_called_once()


def test_service_manager_list_drag_enter_event():
    """
    Test that the ServiceManagerList.dragEnterEvent slot accepts the event
    """
    # GIVEN: A service manager and a mocked event
    service_manager_list = ServiceManagerList(None)
    mocked_event = MagicMock()

    # WHEN: The dragEnterEvent method is called
    service_manager_list.dragEnterEvent(mocked_event)

    # THEN: The accept() method on the event is called
    mocked_event.accept.assert_called_once_with()


def test_service_manager_list_drag_move_event():
    """
    Test that the ServiceManagerList.dragMoveEvent slot accepts the event
    """
    # GIVEN: A service manager and a mocked event
    service_manager_list = ServiceManagerList(None)
    mocked_event = MagicMock()

    # WHEN: The dragMoveEvent method is called
    service_manager_list.dragMoveEvent(mocked_event)

    # THEN: The accept() method on the event is called
    mocked_event.accept.assert_called_once_with()


def test_service_manager_list_key_press_event():
    """
    Test that the ServiceManagerList.keyPressEvent slot ignores the event
    """
    # GIVEN: A service manager and a mocked event
    service_manager_list = ServiceManagerList(None)
    mocked_event = MagicMock()

    # WHEN: The keyPressEvent method is called
    service_manager_list.keyPressEvent(mocked_event)

    # THEN: The ignore() method on the event is called
    mocked_event.ignore.assert_called_once_with()


def test_service_manager_list_mouse_move_event_not_left_button():
    """
    Test that the ServiceManagerList.mouseMoveEvent slot ignores the event if it's not a left-click
    """
    # GIVEN: A service manager and a mocked event
    service_manager_list = ServiceManagerList(None)
    mocked_event = MagicMock()
    mocked_event.buttons.return_value = QtCore.Qt.MouseButton.RightButton

    # WHEN: The mouseMoveEvent method is called
    service_manager_list.mouseMoveEvent(mocked_event)

    # THEN: The ignore() method on the event is called
    mocked_event.ignore.assert_called_once_with()


@patch('openlp.core.ui.servicemanager.QtGui.QCursor')
def test_service_manager_list_mouse_move_event_no_item(MockQCursor: MagicMock):
    """
    Test that the ServiceManagerList.mouseMoveEvent slot ignores the event if it's not over an item
    """
    # GIVEN: A service manager and a mocked event
    service_manager_list = ServiceManagerList(None)
    service_manager_list.itemAt = MagicMock(return_value=None)
    service_manager_list.mapFromGlobal = MagicMock()
    mocked_event = MagicMock()
    mocked_event.buttons.return_value = QtCore.Qt.MouseButton.LeftButton

    # WHEN: The mouseMoveEvent method is called
    service_manager_list.mouseMoveEvent(mocked_event)

    # THEN: The ignore() method on the event is called
    mocked_event.ignore.assert_called_once_with()


@patch('openlp.core.ui.servicemanager.QtGui.QCursor')
@patch('openlp.core.ui.servicemanager.QtGui.QDrag')
@patch('openlp.core.ui.servicemanager.QtCore.QMimeData')
def test_service_manager_list_mouse_move_event(MockQMimeData: MagicMock, MockQDrag: MagicMock,
                                               MockQCursor: MagicMock):
    """
    Test that the ServiceManagerList.mouseMoveEvent slot ignores the event if it's not over an item
    """
    # GIVEN: A service manager and a mocked event
    service_manager_list = ServiceManagerList(None)
    service_manager_list.itemAt = MagicMock(return_value=True)
    service_manager_list.mapFromGlobal = MagicMock()
    mocked_event = MagicMock()
    mocked_event.buttons.return_value = QtCore.Qt.MouseButton.LeftButton
    mocked_drag = MagicMock()
    MockQDrag.return_value = mocked_drag
    mocked_mime_data = MagicMock()
    MockQMimeData.return_value = mocked_mime_data

    # WHEN: The mouseMoveEvent method is called
    service_manager_list.mouseMoveEvent(mocked_event)

    # THEN: The ignore() method on the event is called
    mocked_drag.setMimeData.assert_called_once_with(mocked_mime_data)
    mocked_mime_data.setText.assert_called_once_with('ServiceManager')
    mocked_drag.exec.assert_called_once_with(QtCore.Qt.DropAction.CopyAction)


def test_on_new_service_clicked_not_saved_cancel(registry: Registry):
    """Test that when you click on the new service button, you're asked to save any modified documents"""
    # GIVEN: A Service manager and some mocks
    service_manager = ServiceManager(None)
    service_manager.is_modified = MagicMock(return_value=True)
    service_manager.save_modified_service = MagicMock(return_value=QtWidgets.QMessageBox.StandardButton.Cancel)

    # WHEN: on_new_service_clicked() is called
    result = service_manager.on_new_service_clicked()

    # THEN: The method should have exited early (hence the False return)
    assert result is False, 'The method should have returned early'


def test_on_new_service_clicked_not_saved_false_save(registry: Registry):
    """Test that when you click on the new service button, you're asked to save any modified documents"""
    # GIVEN: A Service manager and some mocks
    service_manager = ServiceManager(None)
    service_manager.is_modified = MagicMock(return_value=True)
    service_manager.save_modified_service = MagicMock(return_value=QtWidgets.QMessageBox.StandardButton.Save)
    service_manager.decide_save_method = MagicMock(return_value=False)

    # WHEN: on_new_service_clicked() is called
    result = service_manager.on_new_service_clicked()

    # THEN: The method should have exited early (hence the False return)
    assert result is False, 'The method should have returned early'


@patch('openlp.core.ui.servicemanager.QtWidgets.QMessageBox')
def test_on_new_service_clicked_unmodified_blank_service(MockQMessageBox: MagicMock, registry: Registry):
    """Test that when the click the new button with an unmodified service, it shows you a message"""
    # GIVEN: A service manager with no service items and a bunch of mocks
    mocked_message_box = MagicMock()
    mocked_message_box.checkbox.return_value.isChecked.return_value = True
    MockQMessageBox.return_value = mocked_message_box
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = True
    registry.register('settings', mocked_settings)
    service_manager = ServiceManager(None)
    service_manager.is_modified = MagicMock(return_value=False)
    service_manager.service_items = []
    service_manager.new_file = MagicMock()

    # WHEN: on_new_service_clicked() is called
    service_manager.on_new_service_clicked()

    # THEN: The message box should have been shown, and the message supressed
    mocked_settings.value.assert_called_once_with('advanced/new service message')
    assert mocked_message_box.setCheckBox.call_count == 1, 'setCheckBox was called to place the checkbox'
    mocked_message_box.exec.assert_called_once_with()
    mocked_settings.setValue.assert_called_once_with('advanced/new service message', False)
    service_manager.new_file.assert_called_once_with()


def test_on_delete_from_service_confirmation_disabled(settings: Settings, service_manager: ServiceManager):
    """
    Test that when the on_delete_from_service function is called and
    confirmation for deleting items is disabled, the currently selected
    item is removed.
    """
    # GIVEN delete item confirmation is disabled and a mock service item
    settings.setValue('advanced/delete service item confirmation', False)
    _add_song_service_item(service_manager)
    service_manager.find_service_item = MagicMock()
    service_manager.find_service_item.return_value = (0, MagicMock())

    # WHEN the on_delete_from_service function is called
    service_manager.on_delete_from_service()

    # THEN the service_items list should be empty
    assert len(service_manager.service_items) == 0


def test_on_delete_from_service_confirmation_enabled_choose_delete(settings: Settings,
                                                                   service_manager: ServiceManager):
    """
    Test that when the on_delete_from_service function is called and
    confirmation for deleting items is enabled, and the user confirms
    deletion, the currently selected item is removed from the service.
    """
    # GIVEN delete item confirmation is enabled and a mock service item
    settings.setValue('advanced/delete service item confirmation', True)
    _add_song_service_item(service_manager)
    service_manager.find_service_item = MagicMock()
    service_manager.find_service_item.return_value = (0, MagicMock())

    # WHEN the on_delete_from_service function is called and the user chooses to delete
    service_manager._delete_confirmation_dialog = MagicMock(return_value=QtWidgets.QMessageBox.StandardButton.Close)
    service_manager.on_delete_from_service()

    # THEN the service_items list should be empty
    assert len(service_manager.service_items) == 0


def test_on_delete_from_service_confirmation_enabled_choose_cancel(settings: Settings,
                                                                   service_manager: ServiceManager):
    """
    Test that when the on_delete_from_service function is called and
    confirmation for deleting items is enabled, and the user confirms
    deletion, the service remains unchanged.
    """
    # GIVEN delete item confirmation is enabled a mock service item
    settings.setValue('advanced/delete service item confirmation', True)
    _add_song_service_item(service_manager)
    service_items_copy = service_manager.service_items.copy()

    # WHEN the on_delete_from_service function is called and the user cancels
    service_manager._delete_confirmation_dialog = MagicMock(return_value=QtWidgets.QMessageBox.StandardButton.Cancel)
    service_manager.on_delete_from_service()

    # THEN the service_items list should be unchanged
    assert service_manager.service_items == service_items_copy


def test_on_load_service_clicked(registry: Registry):
    """Test that a service is loaded when you click the button"""
    # GIVEN: A service manager
    service_manager = ServiceManager(None)

    # THEN: Check that we have a load_service method first, before mocking it
    assert hasattr(service_manager, 'load_service'), 'ServiceManager.load_service() should exist'

    # GIVEN: A mocked out load_service() method
    service_manager.load_service = MagicMock()

    # WHEN: The load button is clicked
    service_manager.on_load_service_clicked(False)

    # THEN: load_service() should have been called
    service_manager.load_service.assert_called_once_with()


def test_load_service_modified_cancel_save(registry: Registry):
    """Test that the load_service() method exits early when the service is modified, but the save is canceled"""
    # GIVEN: A modified ServiceManager
    service_manager = ServiceManager(None)
    service_manager.is_modified = MagicMock(return_value=True)
    service_manager.save_modified_service = MagicMock(return_value=QtWidgets.QMessageBox.StandardButton.Cancel)

    # WHEN: A service is loaded
    result = service_manager.load_service()

    # THEN: The result should be False because of an early exit
    assert result is False, 'The method did not exit early'


@patch('openlp.core.ui.servicemanager.FileDialog.getOpenFileName')
def test_load_service_without_file_path_canceled(mocked_get_open_file_name: MagicMock, registry: Registry):
    """Test that the load_service() method does nothing when no file is loaded and the load dialog is canceled"""
    # GIVEN: A modified ServiceManager
    mocked_settings = MagicMock()
    registry.register('settings', mocked_settings)
    registry.register('main_window', None)
    service_manager = ServiceManager(None)
    service_manager.is_modified = MagicMock(return_value=False)
    mocked_get_open_file_name.return_value = None, None

    # WHEN: A service is loaded but not path specified, and the load dialog is canceled
    result = service_manager.load_service(file_path=None)

    # THEN: The result should be False
    mocked_get_open_file_name.assert_called_once()
    assert result is False


def test_load_service_modified_saved_with_file_path(registry: Registry):
    """Test that the load_service() method saves the file and loads the specified file"""
    # GIVEN: A modified ServiceManager
    mocked_settings = MagicMock()
    registry.register('settings', mocked_settings)
    service_manager = ServiceManager(None)
    service_manager.is_modified = MagicMock(return_value=True)
    service_manager.save_modified_service = MagicMock(return_value=QtWidgets.QMessageBox.StandardButton.Save)
    service_manager.decide_save_method = MagicMock()
    service_manager.load_file = MagicMock()

    # WHEN: A service is loaded
    service_manager.load_service(Path.home() / 'service.osz')

    # THEN: The service should be loaded
    service_manager.decide_save_method.assert_called_once_with()
    mocked_settings.setValue.assert_called_once_with('servicemanager/last directory', Path.home())
    service_manager.load_file.assert_called_once_with(Path.home() / 'service.osz')


@patch('openlp.core.ui.servicemanager.FileDialog.getOpenFileName')
def test_load_service_no_file_path_passed_or_selected(mocked_get_open_file_name: MagicMock,
                                                      mock_settings: MagicMock, registry: Registry):
    """Test that the load_service() method exits early when no file is passed and no file is selected in the dialog"""
    # GIVEN: A modified ServiceManager
    registry.register('main_window', None)
    service_manager = ServiceManager(None)
    mocked_get_open_file_name.return_value = (None, None)

    # WHEN: A service is loaded
    result = service_manager.load_service()

    # THEN: The result should be False because of an early exit
    assert result is False, 'The method did not exit early'


@patch('openlp.core.ui.servicemanager.FileDialog.getOpenFileName')
def test_load_service_no_file_path_passed_file_selected(mocked_get_open_file_name: MagicMock,
                                                        mock_settings: MagicMock, registry: Registry):
    """Test that the load_service() method loads a file chosen in the dialog when no file is passed"""
    # GIVEN: A modified ServiceManager
    registry.register('main_window', None)
    service_manager = ServiceManager(None)
    mocked_get_open_file_name.return_value = (Path.home() / 'service.osz', None)
    service_manager.load_file = MagicMock()

    # WHEN: A service is loaded
    service_manager.load_service()

    # THEN: The service should be loaded
    service_manager.load_file.assert_called_once_with(Path.home() / 'service.osz')


def test_on_recent_service_clicked_modified_cancel_save(registry: Registry):
    """Test that the on_recent_service_clicked() method exits early when the service is modified,
    but the save is canceled"""
    # GIVEN: A modified ServiceManager
    registry.register('main_window', None)
    service_manager = ServiceManager(None)
    service_manager.is_modified = MagicMock(return_value=True)
    service_manager.save_modified_service = MagicMock(return_value=QtWidgets.QMessageBox.StandardButton.Cancel)

    # WHEN: on_recent_service_clicked is called
    result = service_manager.on_recent_service_clicked(True)

    # THEN: The result should be False because of an early exit
    assert result is False, 'The method did not exit early'


def test_on_recent_service_clicked_modified_saved_with_file_path(registry: Registry):
    """Test that the on_recent_service_clicked() method saves the file and loads the file"""
    # GIVEN: A modified ServiceManager
    mocked_settings = MagicMock()
    registry.register('settings', mocked_settings)
    registry.register('main_window', None)
    service_manager = ServiceManager(None)
    service_manager.is_modified = MagicMock(return_value=True)
    service_manager.save_modified_service = MagicMock(return_value=QtWidgets.QMessageBox.StandardButton.Save)
    service_manager.decide_save_method = MagicMock()
    service_manager.load_file = MagicMock()
    service_manager.sender = MagicMock(return_value=MagicMock())

    # WHEN: on_recent_service_clicked is called
    service_manager.on_recent_service_clicked(True)

    # THEN: The recent service should be loaded
    service_manager.decide_save_method.assert_called_once_with()
    service_manager.load_file.assert_called_once()


def test_on_recent_service_clicked_unmodified(registry: Registry):
    # GIVEN: A modified ServiceManager
    registry.register('main_window', None)
    service_manager = ServiceManager(None)
    service_manager.load_file = MagicMock()
    service_manager.sender = MagicMock(return_value=MagicMock())

    # WHEN: on_recent_service_clicked is called
    service_manager.on_recent_service_clicked(True)

    # THEN: The recent service should be loaded
    service_manager.load_file.assert_called_once()


@patch('openlp.core.ui.servicemanager.Path', autospec=True)
def test_service_manager_load_file_str(MockPath: MagicMock, registry: Registry):
    """Test the service manager's load_file method when it is given a str"""
    # GIVEN: A service manager and a mocked path object
    service_manager = ServiceManager(None)
    MockPath.__class__ = Path.__class__
    MockPath.return_value.exists.return_value = False

    # WHEN: A str filename is passed to load_file
    result = service_manager.load_file('service.osz')

    # THEN: False should be returned, but a valid Path object created
    assert result is False, 'ServiceManager.load_file should return false for a non-existant file'
    MockPath.assert_called_once_with('service.osz')
    MockPath.return_value.exists.assert_called_once()


@patch('openlp.core.ui.servicemanager.QtWidgets.QMessageBox')
def test_service_manager_delete_confirmation_dialog(MockMessageBox: MagicMock, registry: Registry):
    """Test the _delete_confirmation_dialog() method"""
    # GIVEN: A service manager and a mocked QMessageBox class
    service_manager = ServiceManager(None)
    mocked_message_box = MagicMock()
    MockMessageBox.return_value = mocked_message_box
    # Restore a couple of items for a more realistic situation
    MockMessageBox.Question = QtWidgets.QMessageBox.Icon.Question
    MockMessageBox.Close = QtWidgets.QMessageBox.StandardButton.Close
    MockMessageBox.Cancel = QtWidgets.QMessageBox.StandardButton.Cancel
    MockMessageBox.StandardButton = QtWidgets.QMessageBox.StandardButton

    # WHEN: _delete_confirmation_dialog() is called
    service_manager._delete_confirmation_dialog()

    # THEN: All the correct things should have been called
    MockMessageBox.assert_called_once_with(QtWidgets.QMessageBox.Icon.Question, 'Delete item from service',
                                           'Are you sure you want to delete this item from the service?',
                                           QtWidgets.QMessageBox.StandardButton(
                                               QtWidgets.QMessageBox.StandardButton.Close |
                                               QtWidgets.QMessageBox.StandardButton.Cancel),
                                           service_manager)
    mocked_message_box.button.assert_called_once_with(QtWidgets.QMessageBox.StandardButton.Close)
    mocked_message_box.setDefaultButton.assert_called_once_with(QtWidgets.QMessageBox.StandardButton.Close)
    mocked_message_box.exec.assert_called_once()


@patch('openlp.core.ui.servicemanager.QtWidgets.QMessageBox.question')
def test_service_manager_save_modified_service(mocked_question: MagicMock, registry: Registry):
    """Test the save_modified_service() method"""
    # GIVEN: A service manager and a mocked main window
    mocked_main_window = MagicMock()
    registry.register('main_window', mocked_main_window)
    service_manager = ServiceManager(None)

    # WHEN: save_modified_service() is called
    service_manager.save_modified_service()

    # THEN: All the correct things should have been called
    mocked_question.assert_called_once_with(mocked_main_window, 'Modified Service',
                                            'The current service has been modified. '
                                            'Would you like to save this service?',
                                            QtWidgets.QMessageBox.StandardButton.Save |
                                            QtWidgets.QMessageBox.StandardButton.Discard |
                                            QtWidgets.QMessageBox.StandardButton.Cancel,
                                            QtWidgets.QMessageBox.StandardButton.Save)


def test_service_manager_on_recent_service_clicked_cancel(registry: Registry):
    """Test the on_recent_service_clicked() method"""
    # GIVEN: A service manager with some methods mocked out
    service_manager = ServiceManager(None)
    service_manager.is_modified = lambda: True
    service_manager.save_modified_service = lambda: QtWidgets.QMessageBox.StandardButton.Cancel

    # WHEN: on_recent_service_clicked() is called
    result = service_manager.on_recent_service_clicked(True)

    # THEN: The result should be False
    assert result is False, 'on_recent_service_clicked() should have returned False'


def test_service_manager_on_recent_service_clicked_save(registry: Registry):
    """Test the on_recent_service_clicked() method"""
    # GIVEN: A service manager with some methods mocked out
    service_manager = ServiceManager(None)
    service_manager.is_modified = lambda: True
    service_manager.save_modified_service = lambda: QtWidgets.QMessageBox.StandardButton.Save
    service_manager.decide_save_method = lambda: None
    service_manager.sender = lambda: MagicMock(**{'data.return_value': '/path/to/service'})
    service_manager.load_file = MagicMock()

    # WHEN: on_recent_service_clicked() is called
    result = service_manager.on_recent_service_clicked(True)

    # THEN: The result should be None
    assert result is None, 'on_recent_service_clicked() should have returned None'
    service_manager.load_file.assert_called_once_with(Path('/path/to/service'))


def test_service_manager_decide_save_method_save(registry: Registry):
    """Test the decide_save_method() method"""
    # GIVEN: A service manager with some methods mocked out
    service_manager = ServiceManager(None)
    service_manager.file_name = lambda: 'filename.osz'
    service_manager.save_file = MagicMock()
    service_manager.save_file_as = MagicMock()

    # WHEN: decide_save_method() is called
    service_manager.decide_save_method()

    # THEN: The correct methods should have been called
    service_manager.save_file.assert_called_once()
    assert service_manager.save_file_as.call_count == 0, 'The save_file_as method should not have been called'


def test_service_manager_decide_save_method_save_as(registry: Registry):
    """Test the decide_save_method() method"""
    # GIVEN: A service manager with some methods mocked out
    service_manager = ServiceManager(None)
    service_manager.file_name = lambda: None
    service_manager.save_file = MagicMock()
    service_manager.save_file_as = MagicMock()

    # WHEN: decide_save_method() is called
    service_manager.decide_save_method()

    # THEN: The correct methods should have been called
    service_manager.save_file_as.assert_called_once()
    assert service_manager.save_file.call_count == 0, 'The save_file method should not have been called'


def test_load_last_file(registry: Registry):
    """Test the load_last_file() method"""
    # GIVEN: Mocked out settings and a ServiceManager
    mocked_settings = MagicMock()
    mocked_settings.value.return_value = Path('filename.osz')
    registry.register('settings', mocked_settings)
    service_manager = ServiceManager(None)
    service_manager.load_file = MagicMock()

    # WHEN: load_last_file() is called
    service_manager.load_last_file()

    # THEN: The file should have been loaded
    service_manager.load_file.assert_called_once_with(Path('filename.osz'))


@patch('openlp.core.ui.servicemanager.Path')
def test_load_file_not_exists(MockPath: MagicMock, registry: Registry):
    """Test the load_file() method when the file does not exist"""
    # GIVEN: A mocked path object, and a service manager
    MockPath.return_value.exists.return_value = False
    service_manager = ServiceManager(None)

    # WHEN: load_file() is called
    is_loaded = service_manager.load_file('fake/path.osz')

    # THEN: load_file() should exit early and return False
    assert is_loaded is False, 'is_loaded should have been False'
    MockPath.assert_called_once_with('fake/path.osz')


@patch('openlp.core.ui.servicemanager.Path')
def test_load_file_os_error(MockPath: MagicMock, registry: Registry):
    """Test the load_file() method when the path object raises an OSError exception"""
    # GIVEN: A mocked path object, and a service manager
    MockPath.return_value.exists.side_effect = OSError
    service_manager = ServiceManager(None)

    # WHEN: load_file() is called
    is_loaded = service_manager.load_file('fake/path.osz')

    # THEN: load_file() should exit early and return False
    assert is_loaded is False, 'is_loaded should have been False'
    MockPath.assert_called_once_with('fake/path.osz')


@patch('openlp.core.ui.servicemanager.critical_error_message_box')
@patch('openlp.core.ui.servicemanager.zipfile.ZipFile')
@patch('openlp.core.ui.servicemanager.Path')
@pytest.mark.parametrize('error', [NameError, OSError, ValidationError, BadZipFile])
def test_load_file_zipfile_exception(MockPath: MagicMock, MockZipFile: MagicMock,
                                     mocked_critical_error_message_box: MagicMock, registry: Registry,
                                     service_manager: ServiceManager, error: Exception):
    """Test that OpenLP handles various exceptions correctly when trying to load a service file"""
    # GIVEN: A mocked path object, and a service manager
    MockZipFile.return_value.__enter__.side_effect = error
    MockPath.return_value.exists.return_value = True
    MockPath.return_value.__str__.return_value = 'fake/path.osz'

    # WHEN: load_file() is called
    service_manager.load_file('fake/path.osz')

    # THEN: load_file() should handle the exception correct and show a message to the user
    MockPath.assert_called_once_with('fake/path.osz')
    mocked_critical_error_message_box.assert_called_once_with(message='The service file fake/path.osz could not be '
                                                              'loaded because it is either corrupt, inaccessible, '
                                                              'or not a valid OpenLP 2 or OpenLP 3 service file.')


@patch('openlp.core.ui.servicemanager.zipfile.ZipFile')
@patch('openlp.core.ui.servicemanager.Path')
def test_load_file_extract_and_fix(MockPath: MagicMock, MockZipFile: MagicMock, mock_settings: MagicMock,
                                   request: pytest.FixtureRequest):
    """Test that OpenLP correctly reads the files in a service file, and fixes a corrupted file"""
    actual_service = [
        {
            'openlp_core': {
                'lite-service': False,
                'service-theme': None,
                'openlp-servicefile-version': 3
            }
        },
        {
            'serviceitem': {
                'header': {
                    'name': 'images',
                    'plugin': 'images',
                    'theme': -1,
                    'title': 'First Baptist Church.jpg',
                    'footer': [],
                    'type': 2,
                    'audit': '',
                    'notes': '',
                    'from_plugin': False,
                    'capabilities': [3, 1, 5, 6, 17, 21, 26],
                    'search': '',
                    'data': '',
                    'xml_version': None,
                    'auto_play_slides_once': False,
                    'auto_play_slides_loop': False,
                    'timed_slide_interval': 0,
                    'start_time': 0,
                    'end_time': 0,
                    'media_length': 0,
                    'background_audio': [],
                    'theme_overwritten': False,
                    'will_auto_start': False,
                    'processor': None,
                    'metadata': [],
                    'sha256_file_hash': None,
                    'stored_filename': None
                },
                'data': [
                    {
                        'title': 'First Baptist Church.jpg',
                        'image': {
                            'parts': [
                                'images',
                                'thumbnails',
                                '7213e6a21ae0a45ceef509a2d107d0bd7d8a4aff2cef9bc94cc3ebd2a40ab352.jpg'
                            ],
                            'json_meta': {
                                'class': 'Path',
                                'version': 1
                            }
                        },
                        'file_hash': '7213e6a21ae0a45ceef509a2d107d0bd7d8a4aff2cef9bc94cc3ebd2a40ab352'
                    }
                ]
            }
        },
        {
            'serviceitem': {
                'header': {
                    'name': 'images',
                    'plugin': 'images',
                    'theme': -1,
                    'title': 'Announcements-12-16-21.jpg',
                    'footer': [],
                    'type': 2,
                    'audit': '',
                    'notes': '',
                    'from_plugin': False,
                    'capabilities': [3, 1, 5, 6, 17, 21, 26],
                    'search': '',
                    'data': '',
                    'xml_version': None,
                    'auto_play_slides_once': False,
                    'auto_play_slides_loop': False,
                    'timed_slide_interval': 0,
                    'start_time': 0,
                    'end_time': 0,
                    'media_length': 0,
                    'background_audio': [],
                    'theme_overwritten': False,
                    'will_auto_start': False,
                    'processor': None,
                    'metadata': [],
                    'sha256_file_hash': None,
                    'stored_filename': None
                },
                'data': [
                    {
                        'title': 'Announcements-12-16-21.jpg',
                        'image': {
                            'parts': [
                                'images',
                                'thumbnails',
                                'df665978e046ac45e0e638dd85f533d52cce2e6d4de33e6628f9b4c4ee57b09f.jpg'
                            ],
                            'json_meta': {
                                'class': 'Path',
                                'version': 1
                            }
                        },
                        'file_hash': 'df665978e046ac45e0e638dd85f533d52cce2e6d4de33e6628f9b4c4ee57b09f'
                    }
                ]
            }
        }
    ]
    expected_service = [
        {
            'openlp_core': {
                'lite-service': False,
                'service-theme': None,
                'openlp-servicefile-version': 3
            }
        },
        {
            'serviceitem': {
                'header': {
                    'name': 'images',
                    'plugin': 'images',
                    'theme': -1,
                    'title': 'First Baptist Church.jpg',
                    'footer': [],
                    'type': 2,
                    'audit': '',
                    'notes': '',
                    'from_plugin': False,
                    'capabilities': [3, 1, 5, 6, 17, 21, 26],
                    'search': '',
                    'data': '',
                    'xml_version': None,
                    'auto_play_slides_once': False,
                    'auto_play_slides_loop': False,
                    'timed_slide_interval': 0,
                    'start_time': 0,
                    'end_time': 0,
                    'media_length': 0,
                    'background_audio': [],
                    'theme_overwritten': False,
                    'will_auto_start': False,
                    'processor': None,
                    'metadata': [],
                    'sha256_file_hash': None,
                    'stored_filename': None
                },
                'data': [
                    {
                        'title': 'First Baptist Church.jpg',
                        'image': Path(
                            'images',
                            'thumbnails',
                            '7213e6a21ae0a45ceef509a2d107d0bd7d8a4aff2cef9bc94cc3ebd2a40ab352.jpg'
                        ),
                        'file_hash': '7213e6a21ae0a45ceef509a2d107d0bd7d8a4aff2cef9bc94cc3ebd2a40ab352'
                    }
                ]
            }
        },
        {
            'serviceitem': {
                'header': {
                    'name': 'images',
                    'plugin': 'images',
                    'theme': -1,
                    'title': 'Announcements-12-16-21.jpg',
                    'footer': [],
                    'type': 2,
                    'audit': '',
                    'notes': '',
                    'from_plugin': False,
                    'capabilities': [3, 1, 5, 6, 17, 21, 26],
                    'search': '',
                    'data': '',
                    'xml_version': None,
                    'auto_play_slides_once': False,
                    'auto_play_slides_loop': False,
                    'timed_slide_interval': 0,
                    'start_time': 0,
                    'end_time': 0,
                    'media_length': 0,
                    'background_audio': [],
                    'theme_overwritten': False,
                    'will_auto_start': False,
                    'processor': None,
                    'metadata': [],
                    'sha256_file_hash': None,
                    'stored_filename': None
                },
                'data': [
                    {
                        'title': 'Announcements-12-16-21.jpg',
                        'image': Path(
                            'images',
                            'thumbnails',
                            'df665978e046ac45e0e638dd85f533d52cce2e6d4de33e6628f9b4c4ee57b09f.jpg'
                        ),
                        'file_hash': 'df665978e046ac45e0e638dd85f533d52cce2e6d4de33e6628f9b4c4ee57b09f'
                    }
                ]
            }
        }
    ]
    service_json = json.dumps(actual_service)
    Registry().register('main_window', MagicMock())
    mocked_zip_file = MagicMock()
    mocked_zip_file.infolist.return_value = [
        MagicMock(compress_size=100, filename='service_data.osj'),
        MagicMock(compress_size=156, filename='7213e6a21ae0a45ceef509a2d107d0bd7d8a4aff2cef9bc94cc3ebd2a40ab352/.jpg'),
        MagicMock(compress_size=149, filename='df665978e046ac45e0e638dd85f533d52cce2e6d4de33e6628f9b4c4ee57b09f/.jpg'),
    ]
    mocked_zip_file.open.return_value.__enter__.return_value.read.return_value = service_json
    MockZipFile.return_value.__enter__.return_value = mocked_zip_file
    service_manager = ServiceManager(None)

    _add_toolbar_action = partial(_create_mock_action, service_manager)
    add_toolbar_action_patcher = patch('openlp.core.ui.servicemanager.OpenLPToolbar.add_toolbar_action')
    mocked_add_toolbar_action = add_toolbar_action_patcher.start()
    mocked_add_toolbar_action.side_effect = _add_toolbar_action
    request.addfinalizer(add_toolbar_action_patcher.stop)

    service_manager.setup_ui(service_manager)
    service_manager.new_file = MagicMock()
    service_manager.process_service_items = MagicMock()
    service_manager.set_file_name = MagicMock()
    service_manager.set_modified = MagicMock()
    service_manager.save_file = MagicMock()
    service_manager.repaint_service_list = MagicMock()

    # WHEN: load_file() is called
    service_manager.load_file('fake/path.osz')

    # THEN: The files should have been loaded
    service_manager.new_file.assert_called_once_with()
    service_manager.process_service_items.assert_called_once_with(expected_service)
    service_manager.set_file_name.assert_called_once()
    service_manager.set_modified.assert_called_once_with(False)
    service_manager.save_file.assert_called_once_with()


def test_bootstrap_initialise(service_manager: ServiceManager):
    """
    Test the bootstrap_initialise method
    """
    # GIVEN: Mocked out stuff
    service_manager.setup_ui = MagicMock()
    service_manager.servicemanager_set_item = MagicMock()
    service_manager.servicemanager_set_item_by_uuid = MagicMock()
    service_manager.servicemanager_next_item = MagicMock()
    service_manager.servicemanager_previous_item = MagicMock()
    service_manager.servicemanager_new_file = MagicMock()
    service_manager.theme_update_service = MagicMock()

    # WHEN: bootstrap_initialise is called
    service_manager.bootstrap_initialise()

    # THEN: The correct calls should have been made
    service_manager.setup_ui.assert_called_once_with(service_manager)
    service_manager.servicemanager_set_item.connect.assert_called_once_with(service_manager.on_set_item)
    service_manager.servicemanager_set_item_by_uuid.connect.assert_called_once_with(service_manager.set_item_by_uuid)
    service_manager.servicemanager_next_item.connect.assert_called_once_with(service_manager.next_item)
    service_manager.servicemanager_previous_item.connect.assert_called_once_with(service_manager.previous_item)
    service_manager.servicemanager_new_file.connect.assert_called_once_with(service_manager.new_file)
    service_manager.theme_update_service.connect.assert_called_once_with(service_manager.on_service_theme_change)


@patch('openlp.core.ui.servicemanager.ServiceNoteForm')
@patch('openlp.core.ui.servicemanager.ServiceItemEditForm')
@patch('openlp.core.ui.servicemanager.StartTimeForm')
def test_bootstrap_post_set_up(MockStartTimeForm: MagicMock, MockServiceItemEditForm: MagicMock,
                               MockServiceNoteForm: MagicMock, service_manager: ServiceManager):
    """
    Test the post bootstrap setup
    """
    # GIVEN: Mocked forms and a ServiceManager object
    mocked_service_note_form = MagicMock()
    MockServiceNoteForm.return_value = mocked_service_note_form
    mocked_service_item_edit_form = MagicMock()
    MockServiceItemEditForm.return_value = mocked_service_item_edit_form
    mocked_start_time_form = MagicMock()
    MockStartTimeForm.return_value = mocked_start_time_form

    # WHEN: bootstrap_post_set_up is run
    service_manager.bootstrap_post_set_up()

    # THEN: The forms should have been created
    assert service_manager.service_note_form == mocked_service_note_form
    assert service_manager.service_item_edit_form == mocked_service_item_edit_form
    assert service_manager.start_time_form == mocked_start_time_form


def test_set_file_name_osz(service_manager: ServiceManager):
    """
    Test setting the file name
    """
    # GIVEN: A service manager, some mocks and a file name
    service_manager.set_modified = MagicMock()
    service_manager.settings.setValue = MagicMock()
    file_path = Path('servicefile.osz')

    # WHEN: The filename is set
    service_manager.set_file_name(file_path)

    # THEN: Various things should have been called and set
    assert service_manager._service_path == file_path
    service_manager.set_modified.assert_called_once_with(False)
    service_manager.settings.setValue.assert_called_once_with('servicemanager/last file', file_path)
    assert service_manager._save_lite is False


def test_set_file_name_oszl(service_manager: ServiceManager):
    """
    Test setting the file name
    """
    # GIVEN: A service manager, some mocks and a file name
    service_manager.set_modified = MagicMock()
    service_manager.settings.setValue = MagicMock()
    file_path = Path('servicefile.oszl')

    # WHEN: The filename is set
    service_manager.set_file_name(file_path)

    # THEN: Various things should have been called and set
    assert service_manager._service_path == file_path
    service_manager.set_modified.assert_called_once_with(False)
    service_manager.settings.setValue.assert_called_once_with('servicemanager/last file', file_path)
    assert service_manager._save_lite is True


def test_short_file_name(service_manager: ServiceManager):
    """
    Test the short_file_name method
    """
    # GIVEN: A service manager and a file name
    service_manager._service_path = Path('/home/user/service.osz')

    # WHEN: short_file_name is called
    result = service_manager.short_file_name()

    # THEN: The result should be correct
    assert result == 'service.osz'


def test_basic_service_manager(service_manager: ServiceManager):
    """
    Test the Service Manager UI Functionality
    """
    # GIVEN: A New Service Manager instance
    # WHEN I have set up the display
    service_manager.setup_ui(service_manager)

    # THEN the count of items should be zero
    assert service_manager.service_manager_list.topLevelItemCount() == 0, \
        'The service manager list should be empty '


@patch('openlp.core.ui.servicemanager.QtWidgets.QTreeWidget.itemAt')
@patch('openlp.core.ui.servicemanager.QtWidgets.QWidget.mapToGlobal')
def test_default_context_menu(mocked_mapToGlobal, mocked_item_at_method, service_manager: ServiceManager):
    """
    Test the context_menu() method with a default service item
    """
    # GIVEN: A service item added
    mocked_item = MagicMock()
    mocked_item.parent.return_value = None
    mocked_item_at_method.return_value = mocked_item
    mocked_item.data.return_value = 1
    service_manager.setup_ui(service_manager)
    # A service item without capabilities.
    service_item = ServiceItem()
    service_manager.service_items = [{'service_item': service_item}]
    q_point = None
    # Mocked actions.
    service_manager.edit_action.setVisible = MagicMock()
    service_manager.create_custom_action.setVisible = MagicMock()
    service_manager.maintain_action.setVisible = MagicMock()
    service_manager.notes_action.setVisible = MagicMock()
    service_manager.time_action.setVisible = MagicMock()
    service_manager.auto_start_action.setVisible = MagicMock()
    service_manager.menu.exec = MagicMock()

    # WHEN: Show the context menu.
    service_manager.context_menu(q_point)

    # THEN: The following actions should be not visible.
    service_manager.edit_action.setVisible.assert_called_once_with(False), \
        'The action should be set invisible.'
    service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
        'The action should be set invisible.'
    service_manager.maintain_action.setVisible.assert_called_once_with(False), \
        'The action should be set invisible.'
    service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
    service_manager.time_action.setVisible.assert_called_once_with(False), \
        'The action should be set invisible.'
    service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
        'The action should be set invisible.'


def test_edit_context_menu(service_manager: ServiceManager):
    """
    Test the context_menu() method with a edit service item
    """
    # GIVEN: A service item added
    service_manager.setup_ui(service_manager)
    with patch('openlp.core.ui.servicemanager.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
            patch('openlp.core.ui.servicemanager.QtWidgets.QWidget.mapToGlobal'):
        mocked_item = MagicMock()
        mocked_item.parent.return_value = None
        mocked_item_at_method.return_value = mocked_item
        # We want 1 to be returned for the position
        mocked_item.data.return_value = 1
        # A service item without capabilities.
        service_item = ServiceItem()
        service_item.add_capability(ItemCapabilities.CanEdit)
        service_item.edit_id = 1
        service_manager.service_items = [{'service_item': service_item}]
        q_point = None
        # Mocked actions.
        service_manager.edit_action.setVisible = MagicMock()
        service_manager.create_custom_action.setVisible = MagicMock()
        service_manager.maintain_action.setVisible = MagicMock()
        service_manager.notes_action.setVisible = MagicMock()
        service_manager.time_action.setVisible = MagicMock()
        service_manager.auto_start_action.setVisible = MagicMock()
        service_manager.menu.exec = MagicMock()

        # WHEN: Show the context menu.
        service_manager.context_menu(q_point)

        # THEN: The following actions should be not visible.
        service_manager.edit_action.setVisible.assert_called_with(True), \
            'The action should be set visible.'
        service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.maintain_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
        service_manager.time_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'


def test_maintain_context_menu(service_manager: ServiceManager):
    """
    Test the context_menu() method with a maintain
    """
    # GIVEN: A service item added
    service_manager.setup_ui(service_manager)
    with patch('openlp.core.ui.servicemanager.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
            patch('openlp.core.ui.servicemanager.QtWidgets.QWidget.mapToGlobal'):
        mocked_item = MagicMock()
        mocked_item.parent.return_value = None
        mocked_item_at_method.return_value = mocked_item
        # We want 1 to be returned for the position
        mocked_item.data.return_value = 1
        # A service item without capabilities.
        service_item = ServiceItem()
        service_item.add_capability(ItemCapabilities.CanMaintain)
        service_manager.service_items = [{'service_item': service_item}]
        q_point = None
        # Mocked actions.
        service_manager.edit_action.setVisible = MagicMock()
        service_manager.create_custom_action.setVisible = MagicMock()
        service_manager.maintain_action.setVisible = MagicMock()
        service_manager.notes_action.setVisible = MagicMock()
        service_manager.time_action.setVisible = MagicMock()
        service_manager.auto_start_action.setVisible = MagicMock()
        service_manager.menu.exec = MagicMock()

        # WHEN: Show the context menu.
        service_manager.context_menu(q_point)

        # THEN: The following actions should be not visible.
        service_manager.edit_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.maintain_action.setVisible.assert_called_with(True), \
            'The action should be set visible.'
        service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
        service_manager.time_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'


def test_loopy_context_menu(service_manager: ServiceManager):
    """
    Test the context_menu() method with a loop
    """
    # GIVEN: A service item added
    service_manager.setup_ui(service_manager)
    with patch('openlp.core.ui.servicemanager.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
            patch('openlp.core.ui.servicemanager.QtWidgets.QWidget.mapToGlobal'):
        mocked_item = MagicMock()
        mocked_item.parent.return_value = None
        mocked_item_at_method.return_value = mocked_item
        # We want 1 to be returned for the position
        mocked_item.data.return_value = 1
        # A service item without capabilities.
        service_item = ServiceItem()
        service_item.add_capability(ItemCapabilities.CanLoop)
        service_item.slides.append("One")
        service_item.slides.append("Two")
        service_manager.service_items = [{'service_item': service_item}]
        q_point = None
        # Mocked actions.
        service_manager.edit_action.setVisible = MagicMock()
        service_manager.create_custom_action.setVisible = MagicMock()
        service_manager.maintain_action.setVisible = MagicMock()
        service_manager.notes_action.setVisible = MagicMock()
        service_manager.time_action.setVisible = MagicMock()
        service_manager.auto_start_action.setVisible = MagicMock()
        service_manager.menu.exec = MagicMock()

        # WHEN: Show the context menu.
        service_manager.context_menu(q_point)

        # THEN: The following actions should be not visible.
        service_manager.edit_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.maintain_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
        service_manager.time_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'


def test_start_time_context_menu(service_manager: ServiceManager):
    """
    Test the context_menu() method with a start time
    """
    # GIVEN: A service item added
    service_manager.setup_ui(service_manager)
    with patch('openlp.core.ui.servicemanager.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
            patch('openlp.core.ui.servicemanager.QtWidgets.QWidget.mapToGlobal'):
        mocked_item = MagicMock()
        mocked_item.parent.return_value = None
        mocked_item_at_method.return_value = mocked_item
        # We want 1 to be returned for the position
        mocked_item.data.return_value = 1
        # A service item without capabilities.
        service_item = ServiceItem()
        service_item.add_capability(ItemCapabilities.HasVariableStartTime)
        service_manager.service_items = [{'service_item': service_item}]
        q_point = None
        # Mocked actions.
        service_manager.edit_action.setVisible = MagicMock()
        service_manager.create_custom_action.setVisible = MagicMock()
        service_manager.maintain_action.setVisible = MagicMock()
        service_manager.notes_action.setVisible = MagicMock()
        service_manager.time_action.setVisible = MagicMock()
        service_manager.auto_start_action.setVisible = MagicMock()
        service_manager.menu.exec = MagicMock()

        # WHEN: Show the context menu.
        service_manager.context_menu(q_point)

        # THEN: The following actions should be not visible.
        service_manager.edit_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.maintain_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
        service_manager.time_action.setVisible.assert_called_with(True), \
            'The action should be set visible.'
        service_manager.auto_start_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'


def test_auto_start_context_menu(service_manager: ServiceManager):
    """
    Test the context_menu() method with can auto start
    """
    # GIVEN: A service item added
    service_manager.setup_ui(service_manager)
    with patch('openlp.core.ui.servicemanager.QtWidgets.QTreeWidget.itemAt') as mocked_item_at_method, \
            patch('openlp.core.ui.servicemanager.QtWidgets.QWidget.mapToGlobal'):
        mocked_item = MagicMock()
        mocked_item.parent.return_value = None
        mocked_item_at_method.return_value = mocked_item
        # We want 1 to be returned for the position
        mocked_item.data.return_value = 1
        # A service item without capabilities.
        service_item = ServiceItem()
        service_item.add_capability(ItemCapabilities.CanAutoStartForLive)
        service_manager.service_items = [{'service_item': service_item}]
        q_point = None
        # Mocked actions.
        service_manager.edit_action.setVisible = MagicMock()
        service_manager.create_custom_action.setVisible = MagicMock()
        service_manager.maintain_action.setVisible = MagicMock()
        service_manager.notes_action.setVisible = MagicMock()
        service_manager.time_action.setVisible = MagicMock()
        service_manager.auto_start_action.setVisible = MagicMock()
        service_manager.rename_action.setVisible = MagicMock()
        service_manager.menu.exec = MagicMock()

        # WHEN: Show the context menu.
        service_manager.context_menu(q_point)

        # THEN: The following actions should be not visible.
        service_manager.edit_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.create_custom_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.maintain_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.notes_action.setVisible.assert_called_with(True), 'The action should be set visible.'
        service_manager.time_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'
        service_manager.auto_start_action.setVisible.assert_called_with(True), \
            'The action should be set visible.'
        service_manager.rename_action.setVisible.assert_called_once_with(False), \
            'The action should be set invisible.'


def test_click_on_new_service(service_manager: ServiceManager):
    """
    Test the on_new_service event handler is called by the UI
    """
    # GIVEN: An initial form
    with patch.object(service_manager, 'new_file') as mocked_new_file:

        # WHEN displaying the UI and pressing cancel
        new_service = service_manager.toolbar.actions_map['newService']
        new_service.trigger()

        assert mocked_new_file.call_count == 1, \
            'The on_new_service_clicked method should have been called once'


def test_expand_selection_on_right_arrow(service_manager: ServiceManager):
    """
    Test that a right arrow key press event calls the on_expand_selection function
    """
    # GIVEN a mocked expand function
    service_manager.on_expand_selection = MagicMock()

    # WHEN the right arrow key event is called
    service_manager.setup_ui(service_manager)
    event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_Right, QtCore.Qt.KeyboardModifier.NoModifier)
    service_manager.service_manager_list.keyPressEvent(event)

    # THEN the on_expand_selection function should have been called.
    service_manager.on_expand_selection.assert_called_once_with()


def test_on_expand_selection_item_none(service_manager: ServiceManager):
    """
    Test that on_expand_selection exits early when there is no item selected.
    """
    # GIVEN a mocked expand function
    service_manager.service_manager_list = MagicMock(**{'currentItem.return_value': None})

    # WHEN on_expand_selection is called
    service_manager.on_expand_selection()

    # THEN on_expand_selection should have exited early
    service_manager.service_manager_list.isExpanded.assert_not_called()


def test_collapse_selection_on_left_arrow(service_manager: ServiceManager):
    """
    Test that a left arrow key press event calls the on_collapse_selection function
    """
    # GIVEN a mocked collapse function
    service_manager.on_collapse_selection = MagicMock()

    # WHEN the left arrow key event is called
    service_manager.setup_ui(service_manager)
    event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_Left, QtCore.Qt.KeyboardModifier.NoModifier)
    service_manager.service_manager_list.keyPressEvent(event)

    # THEN the on_collapse_selection function should have been called.
    service_manager.on_collapse_selection.assert_called_once_with()


def test_move_selection_down_on_down_arrow(service_manager: ServiceManager):
    """
    Test that a down arrow key press event calls the on_move_selection_down function
    """
    # GIVEN a mocked move down function
    service_manager.on_move_selection_down = MagicMock()

    # WHEN the down arrow key event is called
    service_manager.setup_ui(service_manager)
    event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_Down, QtCore.Qt.KeyboardModifier.NoModifier)
    service_manager.service_manager_list.keyPressEvent(event)

    # THEN the on_move_selection_down function should have been called.
    service_manager.on_move_selection_down.assert_called_once_with()


def test_move_selection_up_on_up_arrow(service_manager: ServiceManager):
    """
    Test that an up arrow key press event calls the on_move_selection_up function
    """
    # GIVEN a mocked move up function
    service_manager.on_move_selection_up = MagicMock()

    # WHEN the up arrow key event is called
    service_manager.setup_ui(service_manager)
    event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress, QtCore.Qt.Key.Key_Up, QtCore.Qt.KeyboardModifier.NoModifier)
    service_manager.service_manager_list.keyPressEvent(event)

    # THEN the on_move_selection_up function should have been called.
    service_manager.on_move_selection_up.assert_called_once_with()


def test_delete_selection_on_delete_key(service_manager: ServiceManager):
    """
    Test that a delete key press event calls the on_delete_from_service function
    """
    # GIVEN a mocked on_delete_from_service function
    service_manager.on_delete_from_service = MagicMock()

    # WHEN the delete key event is called
    service_manager.setup_ui(service_manager)
    event = QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress,
                            QtCore.Qt.Key.Key_Delete,
                            QtCore.Qt.KeyboardModifier.NoModifier)
    service_manager.service_manager_list.keyPressEvent(event)

    # THEN the on_delete_from_service function should have been called.
    service_manager.on_delete_from_service.assert_called_once_with()


def test_on_expand_selection(service_manager: ServiceManager):
    """
    Test that the on_expand_selection function successfully expands an item and moves to its first child
    """
    # GIVEN a mocked servicemanager list
    verse_1, verse_2, song_item = _setup_service_manager_list(service_manager)
    service_manager.service_manager_list.setCurrentItem(song_item)
    # Reset expanded function in case it has been called and/or changed in initialisation of the service manager.
    service_manager.expanded = MagicMock()

    # WHEN on_expand_selection is called
    service_manager.on_expand_selection()

    # THEN selection should be expanded
    selected_index = service_manager.service_manager_list.currentIndex()
    above_selected_index = service_manager.service_manager_list.indexAbove(selected_index)
    assert service_manager.service_manager_list.isExpanded(above_selected_index) is True, \
        'Item should have been expanded'
    service_manager.expanded.assert_called_once_with(song_item)


def test_on_collapse_selection_with_parent_selected(service_manager: ServiceManager):
    """
    Test that the on_collapse_selection function successfully collapses an item
    """
    # GIVEN a mocked servicemanager list
    verse_1, verse_2, song_item = _setup_service_manager_list(service_manager)
    service_manager.service_manager_list.setCurrentItem(song_item)
    service_manager.service_manager_list.expandItem(song_item)

    # Reset collapsed function in case it has been called and/or changed in initialisation of the service manager.
    service_manager.collapsed = MagicMock()

    # WHEN on_expand_selection is called
    service_manager.on_collapse_selection()

    # THEN selection should be expanded
    selected_index = service_manager.service_manager_list.currentIndex()
    assert service_manager.service_manager_list.isExpanded(selected_index) is False, \
        'Item should have been collapsed'
    assert service_manager.service_manager_list.currentItem() == song_item, \
        'Top item should have been selected'
    service_manager.collapsed.assert_called_once_with(song_item)


def test_on_collapse_selection_with_child_selected(service_manager: ServiceManager):
    """
    Test that the on_collapse_selection function successfully collapses child's parent item
    and moves selection to its parent.
    """
    # GIVEN a mocked servicemanager list
    verse_1, verse_2, song_item = _setup_service_manager_list(service_manager)
    service_manager.service_manager_list.setCurrentItem(verse_2)
    service_manager.service_manager_list.expandItem(song_item)
    # Reset collapsed function in case it has been called and/or changed in initialisation of the service manager.
    service_manager.collapsed = MagicMock()

    # WHEN on_expand_selection is called
    service_manager.on_collapse_selection()

    # THEN selection should be expanded
    selected_index = service_manager.service_manager_list.currentIndex()
    assert service_manager.service_manager_list.isExpanded(selected_index) is False, \
        'Item should have been collapsed'
    assert service_manager.service_manager_list.currentItem() == song_item, \
        'Top item should have been selected'
    service_manager.collapsed.assert_called_once_with(song_item)


def test_replace_service_item(registry: Registry, service_manager: ServiceManager):
    """
    Tests that the replace_service_item function replaces items as expected
    """
    # GIVEN a service item list and a new item which name and edit_id match a service item
    service_manager.repaint_service_list = MagicMock()
    # registry.remove('live_controller')
    # Registry().register('live_controller', MagicMock())
    item1 = MagicMock()
    item1.edit_id = 'abcd'
    item1.name = 'itemA'
    item2 = MagicMock()
    item2.edit_id = 'abcd'
    item2.name = 'itemB'
    item3 = MagicMock()
    item3.edit_id = 'cfgh'
    item3.name = 'itemA'
    service_manager.service_items = [
        {'service_item': item1},
        {'service_item': item2},
        {'service_item': item3}
    ]
    new_item = MagicMock()
    new_item.edit_id = 'abcd'
    new_item.name = 'itemA'

    # WHEN replace_service_item is called
    service_manager.replace_service_item(new_item)

    # THEN new_item should replace item1, and only replaces that one item
    assert service_manager.service_items[0]['service_item'] == new_item
    new_item.merge.assert_called_once_with(item1)


def test_replace_service_list_call_not_parallel(registry: Registry, service_manager: ServiceManager):
    """
    Tests if _replace_service_list calls are not done in parallel
    """
    # GIVEN a service manager and a mocked repaint
    def mock_repaint():
        service_manager.is_running_repaint = True
        sleep(0.25)
        service_manager.is_running_repaint = False

    service_manager._repaint_service_list = MagicMock(side_effect=mock_repaint)

    # WHEN repaint_service_list is called from different threads
    thread_1 = threading.Thread(target=lambda: service_manager.repaint_service_list(-1, -1))
    thread_2 = threading.Thread(target=lambda: service_manager.repaint_service_list(-1, -1))
    thread_1.start()
    thread_2.start()

    # THEN the _repaint_service_list call must be called only once
    thread_1.join()
    thread_2.join()
    service_manager._repaint_service_list.assert_called_once()


@patch('openlp.core.ui.servicemanager.sha256_file_hash')
def test_get_write_file_list(mocked_sha256_file_hash: MagicMock, registry: Registry,
                             service_manager: ServiceManager):
    """Test that the get_write_file_list() works properly"""
    # GIVEN: A whole bunch of items in the service, of various types and with various problems
    mocked_sha256_file_hash.return_value = '91f95ec0c802da3b5867c5ca25a258955380fcf93e42006ba5988da5ed236287'
    _add_song_service_item(service_manager)
    _add_bible_service_item(service_manager)
    _add_presentation_service_item(service_manager, has_valid_thumb=False)
    _add_presentation_service_item(service_manager, has_valid_thumb=True)
    _add_image_service_item(service_manager, has_valid_image=False)
    _add_image_service_item(service_manager, has_valid_image=True)
    presentation_item = _add_presentation_service_item(service_manager)
    presentation_item.stored_filename = RESOURCE_PATH / 'presentations' / 'test.pptx'

    # WHEN the on_delete_from_service function is called
    write_list, missing_list = service_manager.get_write_file_list()

    # THEN the service_items list should be empty
    assert len(write_list) == 6


@patch('openlp.core.ui.servicemanager.ServiceItem')
@patch('openlp.core.ui.servicemanager.find_and_set_in_combo_box')
def test_process_service_items(mocked_fns_combo: Mock, MockServiceItem: Mock, service_manager: ServiceManager,
                               registry: Registry):
    """Test the process_service_items() method"""
    # GIVEN: A mocked ServiceItem and a ServiceManager
    mocked_service = MagicMock()
    mocked_service.service_load.side_effect = lambda x: x
    registry.register('test', mocked_service)
    mocked_service_item = MagicMock()
    # This line below is because Mock has an internal "name" attr that is set via the constructor
    # See https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    mocked_service_item.name = 'test'
    MockServiceItem.return_value = mocked_service_item
    service_items = [
        {
        },
        {
            'openlp_core': {
                'lite-service': True,
                'service-theme': 'Blue'
            }
        },
        {
        }
    ]
    service_manager.theme_combo_box = MagicMock(**{'currentText.return_value': 'Blue'})
    service_manager.add_service_item = MagicMock()

    # WHEN: process_service_items() is called
    service_manager.process_service_items(service_items)

    # THEN: The correct calls should have been made
    mocked_fns_combo.assert_called_once_with(service_manager.theme_combo_box, 'Blue', set_missing=False)
    assert service_manager.service_theme == 'Blue'
    assert service_manager._save_lite is True
    assert mocked_service_item.set_from_service.call_args_list == [
        call({}, service_manager.service_path, service_manager.servicefile_version),
        call({}, version=service_manager.servicefile_version)
    ]


def test_on_theme_combo_box_selected(service_manager: ServiceManager, registry: Registry, settings: Settings):
    """Test the on_theme_combo_box_selected() method"""
    # GIVEN: A ServiceManager
    # Need this to get around globals/locals
    results = {}

    def theme_changed():
        results['theme_changed'] = True

    if registry.has_function('theme_change_service'):
        registry.remove_function('theme_change_service')
    registry.register_function('theme_change_service', theme_changed)
    service_manager.theme_combo_box = MagicMock(**{'currentText.return_value': 'Blue'})

    # WHEN: on_theme_combo_box_selected() is called
    service_manager.on_theme_combo_box_selected(0)

    # THEN: The correct calls should have been made
    assert service_manager.service_theme == 'Blue'
    assert results.get('theme_changed') is True
    assert settings.value('servicemanager/service theme') == 'Blue'


@patch('openlp.core.ui.servicemanager.find_and_set_in_combo_box')
def test_on_service_theme_change(mocked_find: MagicMock, service_manager: ServiceManager, registry: Registry,
                                 settings: Settings):
    """Test the on_service_theme_change() method"""
    # GIVEN: A ServiceManager
    # Need this to get around globals/locals
    results = {}

    def theme_changed():
        results['theme_changed'] = True

    if registry.has_function('theme_change_service'):
        registry.remove_function('theme_change_service')
    registry.register_function('theme_change_service', theme_changed)
    settings.setValue('servicemanager/service theme', 'Red')

    # WHEN: on_service_theme_change() is called
    service_manager.on_service_theme_change()

    # THEN: The correct calls should have been made
    assert service_manager.service_theme == 'Red'
    assert results.get('theme_changed') is True
    mocked_find.assert_called_once_with(service_manager.theme_combo_box, 'Red')


def test_regenerate_changed_service_items(service_manager: ServiceManager):
    """Test the regenerate_changed_service_items() method"""
    # GIVEN: A ServiceManager, with a patched regenerate_service_items()
    service_manager.regenerate_service_items = MagicMock()

    # WHEN: regenerate_changed_service_items() is called
    service_manager.regenerate_changed_service_items()

    # THEN: regenerate_service_items() should have been called with the changed parameter
    service_manager.regenerate_service_items.assert_called_once_with(changed=True)
