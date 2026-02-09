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
Module to test the EditCustomSlideForm.
"""
import pytest
from unittest.mock import MagicMock, patch

from PySide6 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.custom.forms.editcustomslideform import EditCustomSlideForm


@pytest.fixture()
def form(settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    frm = EditCustomSlideForm()
    yield frm
    del frm
    del main_window


def test_basic(form):
    """
    Test if the dialog is correctly set up.
    """
    # GIVEN: A mocked QDialog.exec() method
    with patch('PySide6.QtWidgets.QDialog.exec'):
        # WHEN: Show the dialog.
        form.exec()

        # THEN: The dialog should be empty.
        assert form.slide_text_edit.toPlainText() == '', 'There should not be any text in the text editor.'


def test_set_text(form):
    """
    Test the set_text() method.
    """
    # GIVEN: A mocked QDialog.exec() method
    with patch('PySide6.QtWidgets.QDialog.exec'):
        mocked_set_focus = MagicMock()
        form.slide_text_edit.setFocus = mocked_set_focus
        wanted_text = 'THIS TEXT SHOULD BE SHOWN.'

        # WHEN: Show the dialog and set the text.
        form.exec()
        form.set_text(wanted_text)

        # THEN: The dialog should show the text.
        assert form.slide_text_edit.toPlainText() == wanted_text, \
            'The text editor should show the correct text.'

        # THEN: The dialog should have focus.
        mocked_set_focus.assert_called_with()
