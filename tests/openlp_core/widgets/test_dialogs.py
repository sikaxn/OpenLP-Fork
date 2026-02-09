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
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6 import QtWidgets

from openlp.core.widgets.dialogs import FileDialog


def test_file_dialog(mock_settings: MagicMock):
    """
    Test that the :class:`FileDialog` instantiates correctly
    """
    # GIVEN: The FileDialog class
    # WHEN: Creating an instance
    instance = FileDialog()

    # THEN: The instance should be an instance of QFileDialog
    assert isinstance(instance, QtWidgets.QFileDialog)


def test_get_existing_directory_user_abort():
    """
    Test that `getExistingDirectory` handles the case when the user cancels the dialog
    """
    # GIVEN: FileDialog with a mocked QDialog.getExistingDirectory method
    # WHEN: Calling FileDialog.getExistingDirectory and the user cancels the dialog returns a empty string
    with patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory', return_value=''):
        result = FileDialog.getExistingDirectory()

        # THEN: The result should be None
        assert result is None


def test_get_existing_directory_user_accepts():
    """
    Test that `getExistingDirectory` handles the case when the user accepts the dialog
    """
    # GIVEN: FileDialog with a mocked QDialog.getExistingDirectory method
    # WHEN: Calling FileDialog.getExistingDirectory, the user chooses a file and accepts the dialog (it returns a
    #       string pointing to the directory)
    with patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory', return_value=os.path.join('test', 'dir')):
        result = FileDialog.getExistingDirectory()

        # THEN: getExistingDirectory() should return a Path object pointing to the chosen file
        assert result == Path('test', 'dir')


def test_get_existing_directory_param_order():
    """
    Test that `getExistingDirectory` passes the parameters to `QFileDialog.getExistingDirectory` in the correct
    order
    """
    # GIVEN: FileDialog
    with patch('openlp.core.widgets.dialogs.QtWidgets.QFileDialog.getExistingDirectory', return_value='') \
            as mocked_get_existing_directory:

        # WHEN: Calling the getExistingDirectory method with all parameters set
        FileDialog.getExistingDirectory('Parent', 'Caption', Path('test', 'dir'), 'Options')

        # THEN: The `QFileDialog.getExistingDirectory` should have been called with the parameters in the correct
        #       order
        mocked_get_existing_directory.assert_called_once_with('Parent', 'Caption', os.path.join('test', 'dir'),
                                                              'Options')


def test_get_open_file_name_user_abort():
    """
    Test that `getOpenFileName` handles the case when the user cancels the dialog
    """
    # GIVEN: FileDialog with a mocked QDialog.getOpenFileName method
    # WHEN: Calling FileDialog.getOpenFileName and the user cancels the dialog (it returns a tuple with the first
    #       value set as an empty string)
    with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=('', '')):
        result = FileDialog.getOpenFileName()

        # THEN: First value should be None
        assert result[0] is None


def test_get_open_file_name_user_accepts():
    """
    Test that `getOpenFileName` handles the case when the user accepts the dialog
    """
    # GIVEN: FileDialog with a mocked QDialog.getOpenFileName method
    # WHEN: Calling FileDialog.getOpenFileName, the user chooses a file and accepts the dialog (it returns a
    #       tuple with the first value set as an string pointing to the file)
    with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName',
               return_value=(os.path.join('test', 'chosen.file'), '')):
        result = FileDialog.getOpenFileName()

        # THEN: getOpenFileName() should return a tuple with the first value set to a Path object pointing to the
        #       chosen file
        assert result[0] == Path('test', 'chosen.file')


def test_get_open_file_name_selected_filter():
    """
    Test that `getOpenFileName` does not modify the selectedFilter as returned by `QFileDialog.getOpenFileName`
    """
    # GIVEN: FileDialog with a mocked QDialog.get_save_file_name method
    # WHEN: Calling FileDialog.getOpenFileName, and `QFileDialog.getOpenFileName` returns a known `selectedFilter`
    with patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', return_value=('', 'selected filter')):
        result = FileDialog.getOpenFileName()

        # THEN: getOpenFileName() should return a tuple with the second value set to a the selected filter
        assert result[1] == 'selected filter'


def test_get_open_file_names_user_abort():
    """
    Test that `getOpenFileNames` handles the case when the user cancels the dialog
    """
    # GIVEN: FileDialog with a mocked QDialog.getOpenFileNames method
    # WHEN: Calling FileDialog.getOpenFileNames and the user cancels the dialog (it returns a tuple with the first
    #       value set as an empty list)
    with patch('PySide6.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], '')):
        result = FileDialog.getOpenFileNames()

        # THEN: First value should be an empty list
        assert result[0] == []


def test_get_open_file_names_user_accepts():
    """
    Test that `getOpenFileNames` handles the case when the user accepts the dialog
    """
    # GIVEN: FileDialog with a mocked QDialog.getOpenFileNames method
    # WHEN: Calling FileDialog.getOpenFileNames, the user chooses some files and accepts the dialog (it returns a
    #       tuple with the first value set as a list of strings pointing to the file)
    with patch('PySide6.QtWidgets.QFileDialog.getOpenFileNames',
               return_value=([os.path.join('test', 'chosen.file1'), os.path.join('test', 'chosen.file2')], '')):
        result = FileDialog.getOpenFileNames()

        # THEN: getOpenFileNames() should return a tuple with the first value set to a list of Path objects pointing
        #       to the chosen file
        assert result[0] == [Path('test', 'chosen.file1'), Path('test', 'chosen.file2')]


def test_get_open_file_names_selected_filter():
    """
    Test that `getOpenFileNames` does not modify the selectedFilter as returned by `QFileDialog.getOpenFileNames`
    """
    # GIVEN: FileDialog with a mocked QDialog.getOpenFileNames method
    # WHEN: Calling FileDialog.getOpenFileNames, and `QFileDialog.getOpenFileNames` returns a known
    #       `selectedFilter`
    with patch('PySide6.QtWidgets.QFileDialog.getOpenFileNames', return_value=([], 'selected filter')):
        result = FileDialog.getOpenFileNames()

        # THEN: getOpenFileNames() should return a tuple with the second value set to a the selected filter
        assert result[1] == 'selected filter'


def test_get_save_file_name_user_abort():
    """
    Test that `getSaveFileName` handles the case when the user cancels the dialog
    """
    # GIVEN: FileDialog with a mocked QDialog.get_save_file_name method
    # WHEN: Calling FileDialog.getSaveFileName and the user cancels the dialog (it returns a tuple with the first
    #       value set as an empty string)
    with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName', return_value=('', '')):
        result = FileDialog.getSaveFileName()

        # THEN: First value should be None
        assert result[0] is None


def test_get_save_file_name_user_accepts():
    """
    Test that `getSaveFileName` handles the case when the user accepts the dialog
    """
    # GIVEN: FileDialog with a mocked QDialog.getSaveFileName method
    # WHEN: Calling FileDialog.getSaveFileName, the user chooses a file and accepts the dialog (it returns a
    #       tuple with the first value set as an string pointing to the file)
    with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName',
               return_value=(os.path.join('test', 'chosen.file'), '')):
        result = FileDialog.getSaveFileName()

        # THEN: getSaveFileName() should return a tuple with the first value set to a Path object pointing to the
        #       chosen file
        assert result[0] == Path('test', 'chosen.file')


def test_get_save_file_name_selected_filter():
    """
    Test that `getSaveFileName` does not modify the selectedFilter as returned by `QFileDialog.getSaveFileName`
    """
    # GIVEN: FileDialog with a mocked QDialog.get_save_file_name method
    # WHEN: Calling FileDialog.getSaveFileName, and `QFileDialog.getSaveFileName` returns a known `selectedFilter`
    with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName', return_value=('', 'selected filter')):
        result = FileDialog.getSaveFileName()

        # THEN: getSaveFileName() should return a tuple with the second value set to a the selected filter
        assert result[1] == 'selected filter'
