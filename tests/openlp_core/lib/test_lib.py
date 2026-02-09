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
Package to test the openlp.core.lib package.
"""
import io
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtGui

from openlp.core.lib import DataType, build_icon, check_item_selected, create_separated_list, create_thumb, \
    get_text_file_string, image_to_byte, read_or_fail, read_int, resize_image, seek_or_fail, str_to_bool, \
    validate_thumb
from openlp.core.common.registry import Registry
from tests.utils.constants import RESOURCE_PATH


def test_str_to_bool_with_bool_true():
    """
    Test the str_to_bool function with boolean input of True
    """
    # GIVEN: A boolean value set to true
    true_boolean = True

    # WHEN: We "convert" it to a bool
    true_result = str_to_bool(true_boolean)

    # THEN: We should get back a True bool
    assert isinstance(true_result, bool), 'The result should be a boolean'
    assert true_result is True, 'The result should be True'


def test_str_to_bool_with_bool_false():
    """
    Test the str_to_bool function with boolean input of False
    """
    # GIVEN: A boolean value set to false
    false_boolean = False

    # WHEN: We "convert" it to a bool
    false_result = str_to_bool(false_boolean)

    # THEN: We should get back a True bool
    assert isinstance(false_result, bool), 'The result should be a boolean'
    assert false_result is False, 'The result should be True'


def test_str_to_bool_with_integer():
    """
    Test the str_to_bool function with an integer input
    """
    # GIVEN: An integer value
    int_string = 1

    # WHEN: we convert it to a bool
    int_result = str_to_bool(int_string)

    # THEN: we should get back a false
    assert int_result is False, 'The result should be False'


def test_str_to_bool_with_invalid_string():
    """
    Test the str_to_bool function with an invalid string
    """
    # GIVEN: An string value with completely invalid input
    invalid_string = 'my feet are wet'

    # WHEN: we convert it to a bool
    str_result = str_to_bool(invalid_string)

    # THEN: we should get back a false
    assert str_result is False, 'The result should be False'


def test_str_to_bool_with_string_false():
    """
    Test the str_to_bool function with a string saying "false"
    """
    # GIVEN: A string set to "false"
    false_string = 'false'

    # WHEN: we convert it to a bool
    false_result = str_to_bool(false_string)

    # THEN: we should get back a false
    assert false_result is False, 'The result should be False'


def test_str_to_bool_with_string_no():
    """
    Test the str_to_bool function with a string saying "NO"
    """
    # GIVEN: An string set to "NO"
    no_string = 'NO'

    # WHEN: we convert it to a bool
    str_result = str_to_bool(no_string)

    # THEN: we should get back a false
    assert str_result is False, 'The result should be False'


def test_str_to_bool_with_true_string_value():
    """
    Test the str_to_bool function with a string set to "True"
    """
    # GIVEN: A string set to "True"
    true_string = 'True'

    # WHEN: we convert it to a bool
    true_result = str_to_bool(true_string)

    # THEN: we should get back a true
    assert true_result is True, 'The result should be True'


def test_str_to_bool_with_yes_string_value():
    """
    Test the str_to_bool function with a string set to "yes"
    """
    # GIVEN: An string set to "yes"
    yes_string = 'yes'

    # WHEN: we convert it to a bool
    str_result = str_to_bool(yes_string)

    # THEN: we should get back a true
    assert str_result is True, 'The result should be True'


def test_get_text_file_string_no_file():
    """
    Test the get_text_file_string() function when a file does not exist
    """
    # GIVEN: A patched is_file which returns False, and a file path
    with patch.object(Path, 'is_file', return_value=False):
        file_path = Path('testfile.txt')

        # WHEN: get_text_file_string is called
        result = get_text_file_string(file_path)

        # THEN: The result should be False
        file_path.is_file.assert_called_with()
        assert result is False, 'False should be returned if no file exists'


def test_get_text_file_string_read_error():
    """
    Test the get_text_file_string() method when a read error happens
    """
    # GIVEN: A patched open which raises an exception and is_file which returns True
    with patch.object(Path, 'is_file'), \
            patch.object(Path, 'open'):
        file_path = Path('testfile.txt')
        file_path.is_file.return_value = True
        file_path.open.side_effect = OSError()

        # WHEN: get_text_file_string is called
        result = get_text_file_string(file_path)

        # THEN: None should be returned
        file_path.is_file.assert_called_once_with()
        file_path.open.assert_called_once_with('r', encoding='utf-8')
        assert result is None, 'None should be returned if the file cannot be opened'


def test_build_icon_with_qicon():
    """
    Test the build_icon() function with a QIcon instance
    """
    # GIVEN: An icon QIcon
    icon = QtGui.QIcon()

    # WHEN: We pass a QIcon instance in
    result = build_icon(icon)

    # THEN: The result should be the same icon as we passed in
    assert icon is result, 'The result should be the same icon as we passed in'


def test_build_icon_with_resource():
    """
    Test the build_icon() function with a resource URI
    """
    with patch('openlp.core.lib.QtGui') as MockedQtGui, \
            patch('openlp.core.lib.QtGui.QPixmap') as MockedQPixmap:
        # GIVEN: A mocked QIcon and a mocked QPixmap
        MockedQtGui.QIcon = MagicMock
        MockedQtGui.QIcon.Mode = MagicMock
        MockedQtGui.QIcon.State = MagicMock
        MockedQtGui.QIcon.Mode.Normal = 1
        MockedQtGui.QIcon.State.Off = 2
        MockedQPixmap.return_value = 'mocked_pixmap'
        resource_uri = ':/resource/uri'

        # WHEN: We pass a QIcon instance in
        result = build_icon(resource_uri)

        # THEN: The result should be our mocked QIcon
        MockedQPixmap.assert_called_with(resource_uri)
        # There really should be more assert statements here but due to type checking and things they all break. The
        # best we can do is to assert that we get back a MagicMock object.
        assert isinstance(result, MagicMock), 'The result should be a MagicMock, because we mocked it out'


def test_image_to_byte():
    """
    Test the image_to_byte() function
    """
    with patch('openlp.core.lib.QtCore') as MockedQtCore:
        # GIVEN: A set of mocked-out Qt classes
        mocked_byte_array = MagicMock()
        MockedQtCore.QByteArray.return_value = mocked_byte_array
        mocked_buffer = MagicMock()
        MockedQtCore.QBuffer.return_value = mocked_buffer
        MockedQtCore.QIODevice.WriteOnly = 'writeonly'
        mocked_image = MagicMock()

        # WHEN: We convert an image to a byte array
        result = image_to_byte(mocked_image, base_64=False)

        # THEN: We should receive the mocked_buffer
        MockedQtCore.QByteArray.assert_called_with()
        MockedQtCore.QBuffer.assert_called_with(mocked_byte_array)
        mocked_buffer.open.assert_called_with('writeonly')
        mocked_image.save.assert_called_with(mocked_buffer, "JPEG")
        assert mocked_byte_array.toBase64.called is False
        assert mocked_byte_array == result, 'The mocked out byte array should be returned'


def test_image_to_byte_base_64():
    """
    Test the image_to_byte() function
    """
    with patch('openlp.core.lib.QtCore') as MockedQtCore, \
            patch('openlp.core.lib.base64.b64encode') as mocked_b64encode:
        # GIVEN: A set of mocked-out Qt classes
        mocked_b64encode.side_effect = lambda x: MagicMock(decode=MagicMock(return_value='{} base64ified'.format(x)))
        mocked_byte_array = "byte_array"
        MockedQtCore.QByteArray.return_value = mocked_byte_array
        mocked_buffer = MagicMock()
        MockedQtCore.QBuffer.return_value = mocked_buffer
        MockedQtCore.QIODevice.WriteOnly = 'writeonly'
        mocked_image = MagicMock()

        # WHEN: We convert an image to a byte array
        result = image_to_byte(mocked_image)

        # THEN: We should receive a value of 'base64mock'
        MockedQtCore.QByteArray.assert_called_with()
        MockedQtCore.QBuffer.assert_called_with(mocked_byte_array)
        mocked_buffer.open.assert_called_with('writeonly')
        mocked_image.save.assert_called_with(mocked_buffer, "JPEG")
        mocked_b64encode.assert_called_with(mocked_byte_array)
        assert 'byte_array base64ified' == result, 'The result should be the return value of the mocked base64 method'


def test_create_thumb_with_size(registry: Registry):
    """
    Test the create_thumb() function with a given size.
    """
    # GIVEN: An image to create a thumb of.
    image_path = RESOURCE_PATH / 'church.jpg'
    thumb_path = RESOURCE_PATH / 'church_thumb.jpg'
    thumb_size = QtCore.QSize(10, 20)

    # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
    # last test.
    try:
        thumb_path.unlink()
    except Exception:
        pass

    # Only continue when the thumb does not exist.
    assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

    # WHEN: Create the thumb.
    icon = create_thumb(image_path, thumb_path, size=thumb_size)

    # THEN: Check if the thumb was created and scaled to the given size.
    assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
    assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
    assert icon.isNull() is False, 'The icon should not be null'
    assert thumb_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

    # Remove the thumb so that the test actually tests if the thumb will be created.
    try:
        thumb_path.unlink()
    except Exception:
        pass


def test_create_thumb_no_size(registry: Registry):
    """
    Test the create_thumb() function with no size specified.
    """
    # GIVEN: An image to create a thumb of.
    image_path = RESOURCE_PATH / 'church.jpg'
    thumb_path = RESOURCE_PATH / 'church_thumb.jpg'
    expected_size = QtCore.QSize(63, 88)

    # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
    # last test.
    try:
        thumb_path.unlink()
    except Exception:
        pass

    # Only continue when the thumb does not exist.
    assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

    # WHEN: Create the thumb.
    icon = create_thumb(image_path, thumb_path)

    # THEN: Check if the thumb was created, retaining its aspect ratio.
    assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
    assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
    assert icon.isNull() is False, 'The icon should not be null'
    assert expected_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

    # Remove the thumb so that the test actually tests if the thumb will be created.
    try:
        thumb_path.unlink()
    except Exception:
        pass


def test_create_thumb_invalid_size(registry: Registry):
    """
    Test the create_thumb() function with invalid size specified.
    """
    # GIVEN: An image to create a thumb of.
    image_path = RESOURCE_PATH / 'church.jpg'
    thumb_path = RESOURCE_PATH / 'church_thumb.jpg'
    thumb_size = QtCore.QSize(-1, -1)
    expected_size = QtCore.QSize(63, 88)

    # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
    # last test.
    try:
        thumb_path.unlink()
    except Exception:
        pass

    # Only continue when the thumb does not exist.
    assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

    # WHEN: Create the thumb.
    icon = create_thumb(image_path, thumb_path, size=thumb_size)

    # THEN: Check if the thumb was created, retaining its aspect ratio.
    assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
    assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
    assert icon.isNull() is False, 'The icon should not be null'
    assert expected_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

    # Remove the thumb so that the test actually tests if the thumb will be created.
    try:
        thumb_path.unlink()
    except Exception:
        pass


def test_create_thumb_width_only(registry: Registry):
    """
    Test the create_thumb() function with a size of only width specified.
    """
    # GIVEN: An image to create a thumb of.
    image_path = RESOURCE_PATH / 'church.jpg'
    thumb_path = RESOURCE_PATH / 'church_thumb.jpg'
    thumb_size = QtCore.QSize(100, -1)
    expected_size = QtCore.QSize(100, 137)

    # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
    # last test.
    try:
        thumb_path.unlink()
    except Exception:
        pass

    # Only continue when the thumb does not exist.
    assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

    # WHEN: Create the thumb.
    icon = create_thumb(image_path, thumb_path, size=thumb_size)

    # THEN: Check if the thumb was created, retaining its aspect ratio.
    assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
    assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
    assert icon.isNull() is False, 'The icon should not be null'
    assert expected_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

    # Remove the thumb so that the test actually tests if the thumb will be created.
    try:
        thumb_path.unlink()
    except Exception:
        pass


def test_create_thumb_height_only(registry: Registry):
    """
    Test the create_thumb() function with a size of only height specified.
    """
    # GIVEN: An image to create a thumb of.
    image_path = RESOURCE_PATH / 'church.jpg'
    thumb_path = RESOURCE_PATH / 'church_thumb.jpg'
    thumb_size = QtCore.QSize(-1, 100)
    expected_size = QtCore.QSize(72, 100)

    # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
    # last test.
    try:
        thumb_path.unlink()
    except Exception:
        pass

    # Only continue when the thumb does not exist.
    assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

    # WHEN: Create the thumb.
    icon = create_thumb(image_path, thumb_path, size=thumb_size)

    # THEN: Check if the thumb was created, retaining its aspect ratio.
    assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
    assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
    assert icon.isNull() is False, 'The icon should not be null'
    assert expected_size == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

    # Remove the thumb so that the test actually tests if the thumb will be created.
    try:
        thumb_path.unlink()
    except Exception:
        pass


def test_create_thumb_empty_img(registry: Registry):
    """
    Test the create_thumb() function with a size of only height specified.
    """
    # GIVEN: An image to create a thumb of.
    image_path = RESOURCE_PATH / 'church.jpg'
    thumb_path = RESOURCE_PATH / 'church_thumb.jpg'
    thumb_size = QtCore.QSize(-1, 100)
    expected_size_1 = QtCore.QSize(88, 88)
    expected_size_2 = QtCore.QSize(100, 100)

    # Remove the thumb so that the test actually tests if the thumb will be created. Maybe it was not deleted in the
    # last test.
    try:
        thumb_path.unlink()
    except Exception:
        pass

    # Only continue when the thumb does not exist.
    assert thumb_path.exists() is False, 'Test was not run, because the thumb already exists.'

    # WHEN: Create the thumb.
    with patch('openlp.core.lib.QtGui.QImageReader.size') as mocked_size:
        mocked_size.return_value = QtCore.QSize(0, 0)
        icon = create_thumb(image_path, thumb_path, size=None)

    # THEN: Check if the thumb was created with aspect ratio of 1.
    assert thumb_path.exists() is True, 'Test was not ran, because the thumb already exists'
    assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
    assert icon.isNull() is False, 'The icon should not be null'
    assert expected_size_1 == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

    # WHEN: Create the thumb.
    with patch('openlp.core.lib.QtGui.QImageReader.size') as mocked_size:
        mocked_size.return_value = QtCore.QSize(0, 0)
        icon = create_thumb(image_path, thumb_path, size=thumb_size)

    # THEN: Check if the thumb was created with aspect ratio of 1.
    assert isinstance(icon, QtGui.QIcon), 'The icon should be a QIcon'
    assert icon.isNull() is False, 'The icon should not be null'
    assert expected_size_2 == QtGui.QImageReader(str(thumb_path)).size(), 'The thumb should have the given size'

    # Remove the thumb so that the test actually tests if the thumb will be created.
    try:
        thumb_path.unlink()
    except Exception:
        pass


@patch('openlp.core.lib.QtGui.QImageReader')
@patch('openlp.core.lib.build_icon')
def test_create_thumb_path_fails(mocked_build_icon: MagicMock, MockQImageReader: MagicMock, registry: Registry):
    """
    Test that build_icon() is run against the image_path when the thumbnail fails to be created
    """
    # GIVEN: A bunch of mocks
    image_path = RESOURCE_PATH / 'church.jpg'
    thumb_path = Path('doesnotexist')
    mocked_image_reader = MagicMock()
    mocked_image_reader.size.return_value.isEmpty.return_value = True

    # WHEN: Create the thumb
    create_thumb(image_path, thumb_path)

    # THEN: The image path should have been used
    mocked_build_icon.assert_called_once_with(image_path)


@patch('openlp.core.lib.QtWidgets', MagicMock())
def test_check_item_selected_true():
    """
    Test that the check_item_selected() function returns True when there are selected indexes
    """
    # GIVEN: A mocked out QtWidgets module and a list widget with selected indexes
    mocked_list_widget = MagicMock()
    mocked_list_widget.selectedIndexes.return_value = True
    message = 'message'

    # WHEN: We check if there are selected items
    result = check_item_selected(mocked_list_widget, message)

    # THEN: The selectedIndexes function should have been called and the result should be true
    mocked_list_widget.selectedIndexes.assert_called_with()
    assert result is True, 'The result should be True'


def test_check_item_selected_false(registry: Registry):
    """
    Test that the check_item_selected() function returns False when there are no selected indexes.
    """
    # GIVEN: A mocked out QtWidgets module and a list widget with selected indexes
    with patch('openlp.core.lib.QtWidgets') as MockedQtWidgets, \
            patch('openlp.core.lib.translate') as mocked_translate:
        mocked_translate.return_value = 'mocked translate'
        mocked_list_widget = MagicMock()
        mocked_list_widget.selectedIndexes.return_value = False
        mocked_list_widget.parent.return_value = 'parent'
        message = 'message'

        # WHEN: We check if there are selected items
        result = check_item_selected(mocked_list_widget, message)

        # THEN: The selectedIndexes function should have been called and the result should be true
        mocked_list_widget.selectedIndexes.assert_called_with()
        MockedQtWidgets.QMessageBox.information.assert_called_with('parent', 'mocked translate', 'message')
        assert result is False, 'The result should be False'


def test_validate_thumb_file_does_not_exist():
    """
    Test the validate_thumb() function when the thumbnail does not exist
    """
    # GIVEN: A mocked out os module, with path.exists returning False, and fake paths to a file and a thumb
    with patch.object(Path, 'exists', return_value=False):
        file_path = Path('path', 'to', 'file')
        thumb_path = Path('path', 'to', 'thumb')

        # WHEN: we run the validate_thumb() function
        result = validate_thumb(file_path, thumb_path)

        # THEN: we should have called a few functions, and the result should be False
        thumb_path.exists.assert_called_once_with()
        assert result is False, 'The result should be False'


def test_validate_thumb_file_exists_and_newer():
    """
    Test the validate_thumb() function when the thumbnail exists and has a newer timestamp than the file
    """
    with patch.object(Path, 'exists'), patch.object(Path, 'stat'):
        # GIVEN: Mocked file_path and thumb_path which return different values fo the modified times
        file_path = MagicMock(**{'stat.return_value': MagicMock(st_mtime=10)})
        thumb_path = MagicMock(**{'exists.return_value': True, 'stat.return_value': MagicMock(st_mtime=11)})

        # WHEN: we run the validate_thumb() function
        result = validate_thumb(file_path, thumb_path)

        # THEN: `validate_thumb` should return True
        assert result is True


def test_validate_thumb_file_exists_and_older():
    """
    Test the validate_thumb() function when the thumbnail exists but is older than the file
    """
    # GIVEN: Mocked file_path and thumb_path which return different values fo the modified times
    file_path = MagicMock(**{'stat.return_value': MagicMock(st_mtime=10)})
    thumb_path = MagicMock(**{'exists.return_value': True, 'stat.return_value': MagicMock(st_mtime=9)})

    # WHEN: we run the validate_thumb() function
    result = validate_thumb(file_path, thumb_path)

    # THEN: `validate_thumb` should return False
    thumb_path.stat.assert_called_once_with()
    assert result is False, 'The result should be False'


def test_resize_thumb(registry: Registry):
    """
    Test the resize_thumb() function
    """
    # GIVEN: A path to an image.
    image_path = str(RESOURCE_PATH / 'church.jpg')
    wanted_width = 777
    wanted_height = 72
    # We want the background to be white.
    wanted_background_hex = '#FFFFFF'
    wanted_background_rgb = QtGui.QColor(wanted_background_hex).rgb()

    # WHEN: Resize the image and add a background.
    image = resize_image(image_path, wanted_width, wanted_height, wanted_background_hex)

    # THEN: Check if the size is correct and the background was set.
    result_size = image.size()
    assert wanted_height == result_size.height(), 'The image should have the requested height.'
    assert wanted_width == result_size.width(), 'The image should have the requested width.'
    assert image.pixel(0, 0) == wanted_background_rgb, 'The background should be white.'


def test_resize_thumb_ignoring_aspect_ratio(registry: Registry):
    """
    Test the resize_thumb() function ignoring aspect ratio
    """
    # GIVEN: A path to an image.
    image_path = str(RESOURCE_PATH / 'church.jpg')
    wanted_width = 1000
    wanted_height = 1000
    # We want the background to be white.
    wanted_background_hex = '#FFFFFF'
    wanted_background_rgb = QtGui.QColor(wanted_background_hex).rgb()

    # WHEN: Resize the image and add a background.
    image = resize_image(image_path, wanted_width, wanted_height, wanted_background_hex, True)

    # THEN: Check if the size is correct and the background was set.
    result_size = image.size()
    assert wanted_height == result_size.height(), 'The image should have the requested height.'
    assert wanted_width == result_size.width(), 'The image should have the requested width.'
    assert image.pixel(0, 0) == wanted_background_rgb, 'The background should be white.'


def test_resize_thumb_width_aspect_ratio(registry: Registry):
    """
    Test the resize_thumb() function using the image's width as the reference
    """
    # GIVEN: A path to an image.
    image_path = str(RESOURCE_PATH / 'church.jpg')
    wanted_width = 10
    wanted_height = 1000

    # WHEN: Resize the image and add a background.
    image = resize_image(image_path, wanted_width, wanted_height)

    # THEN: Check if the size is correct and the background was set.
    result_size = image.size()
    assert wanted_height == result_size.height(), 'The image should have the requested height.'
    assert wanted_width == result_size.width(), 'The image should have the requested width.'


def test_resize_thumb_same_aspect_ratio(registry: Registry):
    """
    Test the resize_thumb() function when the image and the wanted aspect ratio are the same
    """
    # GIVEN: A path to an image.
    image_path = str(RESOURCE_PATH / 'church.jpg')
    wanted_width = 1122
    wanted_height = 1544

    # WHEN: Resize the image and add a background.
    image = resize_image(image_path, wanted_width, wanted_height)

    # THEN: Check if the size is correct and the background was set.
    result_size = image.size()
    assert wanted_height == result_size.height(), 'The image should have the requested height.'
    assert wanted_width == result_size.width(), 'The image should have the requested width.'


@patch('openlp.core.lib.QtCore.QLocale.createSeparatedList')
def test_create_separated_list_qlocate(mocked_createSeparatedList: MagicMock):
    """
    Test the create_separated_list function using the Qt provided method
    """
    # GIVEN: A list of strings and the mocked Qt module.
    mocked_createSeparatedList.return_value = 'Author 1, Author 2, and Author 3'
    string_list = ['Author 1', 'Author 2', 'Author 3']

    # WHEN: We get a string build from the entries it the list and a separator.
    string_result = create_separated_list(string_list)

    # THEN: We should have "Author 1, Author 2, and Author 3"
    assert string_result == 'Author 1, Author 2 and Author 3', \
        'The string should be "Author 1, Author 2, and Author 3".'


def test_create_separated_list_empty_list():
    """
    Test the create_separated_list function with an empty list
    """
    # GIVEN: An empty list
    string_list = []

    # WHEN: We get a string build from the entries it the list and a separator.
    string_result = create_separated_list(string_list)

    # THEN: We shoud have an emptry string.
    assert string_result == '', 'The string sould be empty.'


def test_create_separated_list_with_one_item():
    """
    Test the create_separated_list function with a list consisting of only one entry
    """
    # GIVEN: A list with a string.
    string_list = ['Author 1']

    # WHEN: We get a string build from the entries it the list and a separator.
    string_result = create_separated_list(string_list)

    # THEN: We should have "Author 1"
    assert string_result == 'Author 1', 'The string should be "Author 1".'


def test_create_separated_list_with_two_items():
    """
    Test the create_separated_list function with a list of two entries
    """
    # GIVEN: A list with two strings.
    string_list = ['Author 1', 'Author 2']

    # WHEN: We get a string build from the entries it the list and a seperator.
    string_result = create_separated_list(string_list)

    # THEN: We should have "Author 1 and Author 2"
    assert string_result == 'Author 1 and Author 2', 'The string should be "Author 1 and Author 2".'


def test_create_separated_list_with_three_items():
    """
    Test the create_separated_list function with a list of three items
    """
    # GIVEN: A list with three strings.
    string_list = ['Author 1', 'Author 2', 'Author 3']

    # WHEN: We get a string build from the entries it the list and a seperator.
    string_result = create_separated_list(string_list)

    # THEN: We should have "Author 1, Author 2 and Author 3"
    assert string_result == 'Author 1, Author 2 and Author 3', \
        'The string should be "Author 1, Author 2, and Author 3".'


def test_read_or_fail_fail():
    """
    Test the :func:`read_or_fail` function when attempting to read more data than the buffer contains.
    """
    # GIVEN: Some test data
    test_data = io.BytesIO(b'test data')

    # WHEN: Attempting to read past the end of the buffer
    # THEN: An OSError should be raised.
    with pytest.raises(OSError):
        read_or_fail(test_data, 15)


def test_read_or_fail_success():
    """
    Test the :func:`read_or_fail` function when reading data that is in the buffer.
    """
    # GIVEN: Some test data
    test_data = io.BytesIO(b'test data')

    # WHEN: Attempting to read data that should exist.
    result = read_or_fail(test_data, 4)

    # THEN: The data of the requested length should be returned
    assert result == b'test'


def test_read_int_u8_big():
    """
    Test the :func:`read_int` function when reading an unsigned 8-bit int using 'big' endianness.
    """
    # GIVEN: Some test data
    test_data = io.BytesIO(b'\x0f\xf0\x0f\xf0')

    # WHEN: Reading a an unsigned 8-bit int
    result = read_int(test_data, DataType.U8, 'big')

    # THEN: The an int should have been returned of the expected value
    assert result == 15


def test_read_int_u8_little():
    """
    Test the :func:`read_int` function when reading an unsigned 8-bit int using 'little' endianness.
    """
    # GIVEN: Some test data
    test_data = io.BytesIO(b'\x0f\xf0\x0f\xf0')

    # WHEN: Reading a an unsigned 8-bit int
    result = read_int(test_data, DataType.U8, 'little')

    # THEN: The an int should have been returned of the expected value
    assert result == 15


def test_read_int_u16_big():
    """
    Test the :func:`read_int` function when reading an unsigned 16-bit int using 'big' endianness.
    """
    # GIVEN: Some test data
    test_data = io.BytesIO(b'\x0f\xf0\x0f\xf0')

    # WHEN: Reading a an unsigned 16-bit int
    result = read_int(test_data, DataType.U16, 'big')

    # THEN: The an int should have been returned of the expected value
    assert result == 4080


def test_read_int_u16_little():
    """
    Test the :func:`read_int` function when reading an unsigned 16-bit int using 'little' endianness.
    """
    # GIVEN: Some test data
    test_data = io.BytesIO(b'\x0f\xf0\x0f\xf0')

    # WHEN: Reading a an unsigned 16-bit int
    result = read_int(test_data, DataType.U16, 'little')

    # THEN: The an int should have been returned of the expected value
    assert result == 61455


def test_read_int_u32_big():
    """
    Test the :func:`read_int` function when reading an unsigned 32-bit int using 'big' endianness.
    """
    # GIVEN: Some test data
    test_data = io.BytesIO(b'\x0f\xf0\x0f\xf0')

    # WHEN: Reading a an unsigned 32-bit int
    result = read_int(test_data, DataType.U32, 'big')

    # THEN: The an int should have been returned of the expected value
    assert result == 267390960


def test_read_int_u32_little():
    """
    Test the :func:`read_int` function when reading an unsigned 32-bit int using 'little' endianness.
    """
    # GIVEN: Some test data
    test_data = io.BytesIO(b'\x0f\xf0\x0f\xf0')

    # WHEN: Reading a an unsigned 32-bit int
    result = read_int(test_data, DataType.U32, 'little')

    # THEN: The an int should have been returned of the expected value
    assert result == 4027576335


def test_seek_or_fail_default_method():
    """
    Test the :func:`seek_or_fail` function when using the default value for the :arg:`how`
    """
    # GIVEN: A mocked_file_like_object
    mocked_file_like_object = MagicMock(**{'seek.return_value': 5, 'tell.return_value': 0})

    # WHEN: Calling seek_or_fail with out the how arg set
    seek_or_fail(mocked_file_like_object, 5)

    # THEN: seek should be called using the os.SEEK_SET constant
    mocked_file_like_object.seek.assert_called_once_with(5, os.SEEK_SET)


def test_seek_or_fail_os_end():
    """
    Test the :func:`seek_or_fail` function when called with an unsupported seek operation.
    """
    # GIVEN: A Mocked object
    # WHEN: Attempting to seek relative to the end
    # THEN: An NotImplementedError should have been raised
    with pytest.raises(NotImplementedError):
        seek_or_fail(MagicMock(), 1, os.SEEK_END)


def test_seek_or_fail_valid_seek_set():
    """
    Test that :func:`seek_or_fail` successfully seeks to the correct position.
    """
    # GIVEN: A mocked file-like object
    mocked_file_like_object = MagicMock(**{'tell.return_value': 3, 'seek.return_value': 5})

    # WHEN: Attempting to seek from the beginning
    result = seek_or_fail(mocked_file_like_object, 5, os.SEEK_SET)

    # THEN: The new position should be 5 from the beginning
    assert result == 5


def test_seek_or_fail_invalid_seek_set():
    """
    Test that :func:`seek_or_fail` raises an exception when seeking past the end.
    """
    # GIVEN: A Mocked file-like object
    mocked_file_like_object = MagicMock(**{'tell.return_value': 3, 'seek.return_value': 10})

    # WHEN: Attempting to seek from the beginning past the end
    # THEN: An OSError should have been raised
    with pytest.raises(OSError):
        seek_or_fail(mocked_file_like_object, 15, os.SEEK_SET)


def test_seek_or_fail_valid_seek_cur():
    """
    Test that :func:`seek_or_fail` successfully seeks to the correct position.
    """
    # GIVEN: A mocked file_like object
    mocked_file_like_object = MagicMock(**{'tell.return_value': 3, 'seek.return_value': 8})

    # WHEN: Attempting to seek from the current position
    result = seek_or_fail(mocked_file_like_object, 5, os.SEEK_CUR)

    # THEN: The new position should be 8 (5 from its starting position)
    assert result == 8


def test_seek_or_fail_invalid_seek_cur():
    """
    Test that :func:`seek_or_fail` raises an exception when seeking past the end.
    """
    # GIVEN: A mocked file_like object
    mocked_file_like_object = MagicMock(**{'tell.return_value': 3, 'seek.return_value': 10})

    # WHEN: Attempting to seek from the current position pas the end.
    # THEN: An OSError should have been raised
    with pytest.raises(OSError):
        seek_or_fail(mocked_file_like_object, 15, os.SEEK_CUR)
