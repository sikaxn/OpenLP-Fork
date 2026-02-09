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
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore, QtWidgets

from openlp.core.common.platform import is_win
from openlp.core.ui.library import FolderLibraryItem


class MockItem:
    id = 1
    name = 'video.mp4'
    file_path = 'path/to/video.mp4'
    folder_id = None

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockFolder:
    id = 1
    name = 'folder'
    parent_id = None

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.fixture
def folder_library_item(registry, settings):
    registry.register('main_window', MagicMock())
    mocked_manager = MagicMock()
    with patch('openlp.core.lib.mediamanageritem.MediaManagerItem._setup'), \
            patch('openlp.core.lib.mediamanageritem.MediaManagerItem.setup_item'):
        library_item = FolderLibraryItem(None, MagicMock(manager=mocked_manager), MockFolder, MockItem)
        library_item.list_view = MagicMock(**{'selectedItems.return_value': []})
    return library_item


def test_folderlibrary_retranslate_ui(folder_library_item):
    """Test the retranslate_ui() method"""
    # GIVEN: A FolderLibraryItem object with mocks
    folder_library_item.add_folder_action = MagicMock()

    # WHEN: retranslate_ui() is called
    folder_library_item.retranslate_ui()

    # THEN: there should be no errors and the text should be correct
    folder_library_item.add_folder_action.setText.assert_called_once_with('Add folder')
    folder_library_item.add_folder_action.setToolTip.assert_called_once_with('Add folder.')


def test_folderlibrary_add_custom_context_actions(folder_library_item):
    """Test that the folder_library_item.add_custom_context_actions does nothing"""
    folder_library_item.add_custom_context_actions()


def test_folderlibrary_load_item(folder_library_item):
    """Test that the load_item() method raises a NotImplementedError"""
    with pytest.raises(NotImplementedError):
        folder_library_item.load_item(MockItem())


def test_folderlibrary_delete_item(folder_library_item):
    """Test that the delete_item() method raises a NotImplementedError"""
    with pytest.raises(NotImplementedError):
        folder_library_item.delete_item(MockItem())


def test_folderlibrary_add_middle_header_bar(folder_library_item):
    """Test that an action is created for the header bar"""
    # GIVEN: A mocked action and toolbar
    mocked_action = MagicMock()
    folder_library_item.toolbar = MagicMock(**{'add_toolbar_action.return_value': mocked_action})

    # WHEN: add_middle_header_bar() is called
    folder_library_item.add_middle_header_bar()

    # THEN: The action should have been created
    assert folder_library_item.add_folder_action is mocked_action


def test_folderlibrary_create_item_from_id_path(folder_library_item):
    """Test the create_item_from_id method"""
    # GIVEN: An instance of the FolderLibraryItem
    mocked_item = MockItem()
    folder_library_item.manager.get_object_filtered.return_value = mocked_item

    # WHEN: create_item_from_id is called
    result = folder_library_item.create_item_from_id('path/to/video.mp4')

    # THEN: The result should be a QTreeWidgetItem with a mocked object as data
    assert isinstance(result, QtWidgets.QTreeWidgetItem)
    assert result.data(0, QtCore.Qt.ItemDataRole.UserRole) is mocked_item


def test_folderlibrary_create_item_from_id_object(folder_library_item):
    """Test the create_item_from_id method"""
    # GIVEN: An instance of the FolderLibraryItem
    mocked_item = MockItem()
    folder_library_item.manager.get_object_filtered.return_value = mocked_item

    # WHEN: create_item_from_id is called
    result = folder_library_item.create_item_from_id(mocked_item)

    # THEN: The result should be a QTreeWidgetItem with a mocked object as data
    assert isinstance(result, QtWidgets.QTreeWidgetItem)
    assert result.data(0, QtCore.Qt.ItemDataRole.UserRole) is mocked_item


def test_folderlibrary_current_folder(folder_library_item):
    """Test that the current_folder property returns the correct folder"""
    # GIVEN: A whole buncha mocks
    mocked_folder = MockFolder()
    mocked_item = MockItem()
    mocked_list_folder = MagicMock(**{'data.return_value': mocked_folder}, spec=QtWidgets.QTreeWidgetItem)
    mocked_list_item = MagicMock(**{'data.return_value': mocked_item, 'parent.return_value': mocked_list_folder})
    folder_library_item.list_view.selectedItems.return_value = [mocked_list_item]

    # WHEN: We access the property
    folder = folder_library_item.current_folder

    # THEN: The current folder should be the mocked folder
    assert folder is mocked_folder


def test_file_to_item_as_path(folder_library_item):
    """Test the file_to_item() method returns an Item from the filename as a Path"""
    # GIVEN: A FolderLibraryItem
    folder_library_item.manager.save_object = MagicMock()

    # WHEN: A Path object is passed to file_to_item()
    result = folder_library_item.file_to_item(Path('path/to/file.mp4'))

    # THEN: An Item should be returned
    assert isinstance(result, MockItem)
    assert result.name == 'file.mp4'
    if is_win():
        assert result.file_path == 'path\\to\\file.mp4'
    else:
        assert result.file_path == 'path/to/file.mp4'


def test_file_to_item_as_str(folder_library_item):
    """Test the file_to_item() method returns an Item from the filename as a str"""
    # GIVEN: A FolderLibraryItem
    folder_library_item.manager.save_object = MagicMock()

    # WHEN: A Path object is passed to file_to_item()
    result = folder_library_item.file_to_item('path/to/file.mp4')

    # THEN: An Item should be returned
    assert isinstance(result, MockItem)
    assert result.name == 'file.mp4'
    assert result.file_path == 'path/to/file.mp4'


def test_validate_and_load(folder_library_item):
    """
    Test that the validate_and_load() method when called with a folder
    """
    # GIVEN: A list of files, and a mocked out load_list
    file_list = ['path1/image1.jpg', 'path2/image2.jpg']
    expected_list = [MagicMock(file_path=fp) for fp in file_list]
    folder_library_item.manager.get_all_objects.return_value = expected_list
    folder_library_item.load_list = MagicMock()
    folder_library_item.list_view.selectedItems.return_value = None
    folder_library_item.settings_section = 'tests'
    folder_library_item.choose_folder_form = MagicMock(**{'exec.return_value': QtWidgets.QDialog.Accepted,
                                                          'folder': None})

    # WHEN: Calling validate_and_load with the list of files and a group
    folder_library_item.validate_and_load(file_list)

    # THEN: load_list should have been called with the file list and the group name,
    #       the directory should have been saved to the settings
    folder_library_item.load_list.assert_called_once_with(expected_list, target_folder=None)


@patch('openlp.core.ui.library.sha256_file_hash')
def test_recursively_delete_folder(mocked_sha256_file_hash, folder_library_item):
    """
    Test that recursively_delete_folder() works
    """
    # GIVEN: A Folder object and mocked functions
    folder_library_item.manager.get_all_objects.side_effect = [
        [MockItem(), MockItem(), MockItem()],
        [MockFolder()],
        [MockItem(), MockItem()],
        []
    ]
    folder_library_item.service_path = Path()
    folder_library_item.manager.delete_object = MagicMock()
    folder_library_item.delete_item = MagicMock()
    mocked_folder = MockFolder()
    mocked_folder.id = 1
    mocked_folder.parent_id = None
    mocked_sha256_file_hash.return_value = 'abcd'

    # WHEN: recursively_delete_group() is called
    folder_library_item.recursively_delete_folder(mocked_folder)

    # THEN: delete_file() should have been called 12 times and manager.delete_object() 7 times.
    assert folder_library_item.manager.delete_object.call_count == 6, \
        'delete_object() should be called 6 times, called {} times'.format(
            folder_library_item.manager.delete_object.call_count)
    assert folder_library_item.delete_item.call_count == 5, 'delete_item() should have been called 5 times'


@patch('openlp.core.ui.library.sha256_file_hash')
def test_on_delete_click(mocked_sha256_file_hash, folder_library_item):
    """
    Test that on_delete_click() works
    """
    # GIVEN: An ImageGroups object and mocked functions
    folder_library_item.check_item_selected = MagicMock(return_value=True)
    folder_library_item.delete_item = MagicMock()
    mocked_item = MockItem()
    mocked_item.id = 1
    mocked_item.file_path = 'imagefile.png'
    mocked_item.file_hash = 'abcd'
    folder_library_item.service_path = Path()
    mocked_row_item = MagicMock()
    mocked_row_item.data.return_value = mocked_item
    mocked_row_item.text.return_value = ''
    folder_library_item.list_view.selectedItems.return_value = [None, mocked_row_item]
    mocked_sha256_file_hash.return_value = 'abcd'

    # WHEN: Calling on_delete_click
    folder_library_item.on_delete_click()

    # THEN: delete_file should have been called twice
    assert folder_library_item.delete_item.call_count == 1, 'delete_item() should have been called once'


@patch('openlp.core.ui.library.sha256_file_hash')
def test_on_delete_click_with_parent(mocked_sha256_file_hash, folder_library_item):
    """
    Test that on_delete_click() works
    """
    # GIVEN: An ImageGroups object and mocked functions
    folder_library_item.check_item_selected = MagicMock(return_value=True)
    folder_library_item.delete_item = MagicMock()
    mocked_item = MockItem()
    mocked_item.id = 1
    mocked_item.folder_id = 1
    mocked_item.file_path = 'imagefile.png'
    mocked_item.file_hash = 'abcd'
    folder_library_item.service_path = Path()
    mocked_row_item = MagicMock()
    mocked_row_item.data.return_value = mocked_item
    mocked_row_item.text.return_value = ''
    folder_library_item.list_view.selectedItems.return_value = [mocked_row_item]
    mocked_sha256_file_hash.return_value = 'abcd'

    # WHEN: Calling on_delete_click
    folder_library_item.on_delete_click()

    # THEN: delete_file should have been called twice
    assert folder_library_item.delete_item.call_count == 1, 'delete_item() should have been called once'


@patch('openlp.core.ui.library.sha256_file_hash')
@patch('openlp.core.ui.library.QtWidgets.QMessageBox.question')
def test_on_delete_click_as_folder(mocked_question, mocked_sha256_file_hash, folder_library_item):
    """
    Test that on_delete_click() works
    """
    # GIVEN: An ImageGroups object and mocked functions
    folder_library_item.check_item_selected = MagicMock(return_value=True)
    folder_library_item.delete_item = MagicMock()
    folder_library_item.recursively_delete_folder = MagicMock()
    mocked_folder = MockFolder()
    mocked_folder.id = 1
    folder_library_item.service_path = Path()
    mocked_row_item = MagicMock()
    mocked_row_item.data.return_value = mocked_folder
    mocked_row_item.text.return_value = ''
    folder_library_item.list_view.selectedItems.return_value = [mocked_row_item]
    mocked_sha256_file_hash.return_value = 'abcd'
    mocked_question.return_value = QtWidgets.QMessageBox.Yes

    # WHEN: Calling on_delete_click
    folder_library_item.on_delete_click()

    # THEN: delete_file should have been called twice
    assert folder_library_item.recursively_delete_folder.call_count == 1, \
        'recursively_delete_folder() should have been called once'


@patch('openlp.core.ui.library.sha256_file_hash')
@patch('openlp.core.ui.library.QtWidgets.QMessageBox.question')
def test_on_delete_click_as_folder_with_parent(mocked_question, mocked_sha256_file_hash, folder_library_item):
    """
    Test that on_delete_click() works
    """
    # GIVEN: An ImageGroups object and mocked functions
    folder_library_item.check_item_selected = MagicMock(return_value=True)
    folder_library_item.delete_item = MagicMock()
    folder_library_item.recursively_delete_folder = MagicMock()
    mocked_folder = MockFolder()
    mocked_folder.id = 1
    mocked_folder.parent_id = 1
    folder_library_item.service_path = Path()
    mocked_row_item = MagicMock()
    mocked_row_item.data.return_value = mocked_folder
    mocked_row_item.text.return_value = ''
    folder_library_item.list_view.selectedItems.return_value = [mocked_row_item]
    mocked_sha256_file_hash.return_value = 'abcd'
    mocked_question.return_value = QtWidgets.QMessageBox.Yes

    # WHEN: Calling on_delete_click
    folder_library_item.on_delete_click()

    # THEN: delete_file should have been called twice
    assert folder_library_item.recursively_delete_folder.call_count == 1, \
        'recursively_delete_folder() should have been called once'


def test_on_add_folder_click(folder_library_item):
    """Test that the on_add_folder_click adds a folder to the list"""
    # GIVEN: A folder library item and some mocks
    mocked_folder = MockFolder()
    mocked_folder.id = 1
    mocked_item = MockItem()
    folder_library_item.add_folder_form = MagicMock(**{'exec.return_value': True, 'new_folder': mocked_folder})
    folder_library_item.manager.save_object = MagicMock(return_value=True)
    folder_library_item.manager.get_all_objects = MagicMock(return_value=[mocked_item])
    folder_library_item.load_list = MagicMock()
    folder_library_item.expand_folder = MagicMock()

    # WHEN: on_add_folder_click() is called
    folder_library_item.on_add_folder_click()

    # THEN: Things should happen
    folder_library_item.manager.save_object.assert_called_once_with(mocked_folder)
    folder_library_item.manager.get_all_objects.assert_called_once()
    folder_library_item.load_list.assert_called_once_with([mocked_item])
    folder_library_item.expand_folder.assert_called_once_with(1)


@patch('openlp.core.ui.library.critical_error_message_box')
def test_on_add_folder_click_fails(mocked_critical_error_message_box, folder_library_item):
    """Test that the on_add_folder_click adds a folder to the list"""
    # GIVEN: A folder library item and some mocks
    mocked_folder = MockFolder()
    mocked_folder.id = 1
    folder_library_item.add_folder_form = MagicMock(**{'exec.return_value': True, 'new_folder': mocked_folder})
    folder_library_item.manager.save_object = MagicMock(return_value=False)
    folder_library_item.manager.get_all_objects = MagicMock()
    folder_library_item.load_list = MagicMock()
    folder_library_item.expand_folder = MagicMock()

    # WHEN: on_add_folder_click() is called
    folder_library_item.on_add_folder_click()

    # THEN: Things should happen
    folder_library_item.manager.save_object.assert_called_once_with(mocked_folder)
    folder_library_item.manager.get_all_objects.assert_not_called()
    folder_library_item.load_list.assert_not_called()
    folder_library_item.expand_folder.assert_not_called()
    mocked_critical_error_message_box.assert_called_once_with(message='Could not add the new folder.')
