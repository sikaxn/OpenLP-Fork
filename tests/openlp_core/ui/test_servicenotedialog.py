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
from unittest.mock import patch

from PySide6 import QtCore, QtTest

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.ui.servicenoteform import ServiceNoteForm


@pytest.fixture
def form(registry: Registry, settings: Settings):
    Registry().register('main_window', None)
    frm = ServiceNoteForm()
    return frm


def test_basic_display(form: ServiceNoteForm):
    """
    Test Service Note form functionality
    """
    # GIVEN: A dialog with an empty text box
    form.text_edit.setPlainText('')

    # WHEN displaying the UI and pressing enter
    with patch('openlp.core.ui.servicenoteform.QtWidgets.QDialog.exec'):
        form.exec()
    ok_widget = form.button_box.button(form.button_box.StandardButton.Save)
    QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.MouseButton.LeftButton)

    # THEN the following input text is returned
    assert form.text_edit.toPlainText() == '', 'The returned text should be empty'

    # WHEN displaying the UI, having set the text and pressing enter
    text = 'OpenLP is the best worship software'
    form.text_edit.setPlainText(text)
    with patch('openlp.core.ui.servicenoteform.QtWidgets.QDialog.exec'):
        form.exec()
    ok_widget = form.button_box.button(form.button_box.StandardButton.Save)
    QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.MouseButton.LeftButton)

    # THEN the following text is returned
    assert form.text_edit.toPlainText() == text, 'The text originally entered should still be there'

    # WHEN displaying the UI, having set the text and pressing enter
    form.text_edit.setPlainText('')
    with patch('openlp.core.ui.servicenoteform.QtWidgets.QDialog.exec'):
        form.exec()
        form.text_edit.setPlainText(text)
    ok_widget = form.button_box.button(form.button_box.StandardButton.Save)
    QtTest.QTest.mouseClick(ok_widget, QtCore.Qt.MouseButton.LeftButton)

    # THEN the following text is returned
    assert form.text_edit.toPlainText() == text, 'The new text should be returned'
