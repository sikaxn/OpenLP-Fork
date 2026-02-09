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
Package to test the openlp.core.ui package.
"""
import pytest
from unittest.mock import MagicMock, patch

from PySide6 import QtTest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.ui.filerenameform import FileRenameForm


@pytest.fixture()
def form(registry: Registry, settings: Settings):
    Registry().register('main_window', None)
    frm = FileRenameForm()
    return frm


def test_window_title(form: FileRenameForm):
    """
    Test the windowTitle of the FileRenameDialog
    """
    # GIVEN: A mocked QDialog.exec() method
    with patch('PySide6.QtWidgets.QDialog.exec'):

        # WHEN: The form is executed with no args
        form.exec()

        # THEN: the window title is set correctly
        assert form.windowTitle() == 'File Rename', 'The window title should be "File Rename"'

        # WHEN: The form is executed with False arg
        form.exec(False)

        # THEN: the window title is set correctly
        assert form.windowTitle() == 'File Rename', 'The window title should be "File Rename"'

        # WHEN: The form is executed with True arg
        form.exec(True)

        # THEN: the window title is set correctly
        assert form.windowTitle() == 'File Copy', 'The window title should be "File Copy"'


def test_line_edit_focus(form: FileRenameForm):
    """
    Regression test for bug1067251
    Test that the file_name_edit setFocus has called with True when executed
    """
    # GIVEN: A mocked QDialog.exec() method and mocked file_name_edit.setFocus() method.
    with patch('PySide6.QtWidgets.QDialog.exec'):
        mocked_set_focus = MagicMock()
        form.file_name_edit.setFocus = mocked_set_focus

        # WHEN: The form is executed
        form.exec()

        # THEN: the setFocus method of the file_name_edit has been called with True
        mocked_set_focus.assert_called_with()


def test_file_name_validation(form: FileRenameForm):
    """
    Test the file_name_edit validation
    """
    # GIVEN: QLineEdit with a validator set with illegal file name characters.

    # WHEN: 'Typing' a string containing invalid file characters.
    QtTest.QTest.keyClicks(form.file_name_edit, r'I/n\\v?a*l|i<d> \F[i\l]e" :N+a%me')

    # THEN: The text in the QLineEdit should be the same as the input string with the invalid characters filtered
    # out.
    assert form.file_name_edit.text() == 'Invalid File Name'
