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
Package to test the openlp.core.ui.formattingtagsform package.
"""
import pytest
from unittest.mock import MagicMock, call, patch

from openlp.core.ui.formattingtagform import FormattingTagForm


@pytest.fixture()
def tagform_env(registry):
    setup_patcher = patch('openlp.core.ui.formattingtagform.FormattingTagForm._setup')
    mocked_setup_patcher = setup_patcher.start()
    yield mocked_setup_patcher
    setup_patcher.stop()


def test_on_row_selected(tagform_env, mock_settings):
    """
    Test that the appropriate actions are preformed when on_row_selected is called
    """
    # GIVEN: An instance of the Formatting Tag Form and a mocked delete_button
    form = FormattingTagForm(None)
    form.delete_button = MagicMock()

    # WHEN: on_row_selected is called
    form.on_row_selected()

    # THEN: setEnabled and should have been called on delete_button
    form.delete_button.setEnabled.assert_called_with(True)


def test_on_new_clicked(tagform_env, mock_settings):
    """
    Test that clicking the Add a new tag button does the right thing
    """

    # GIVEN: A formatting tag form and a mocked out tag table widget
    form = FormattingTagForm(None)
    form.tag_table_widget = MagicMock()
    row_count = 5
    form.tag_table_widget.rowCount.return_value = row_count

    # WHEN: on_new_clicked is run (i.e. the Add new button was clicked)
    with patch('openlp.core.ui.formattingtagform.QtWidgets.QTableWidgetItem') as MockedQTableWidgetItem:
        mockedwidget = patch('openlp.core.ui.formattingtagform.QtWidgets.QWidget')
        mocked_table_widget = MagicMock()
        mocked_widget = MagicMock()
        MockedQTableWidgetItem.return_value = mocked_table_widget
        mockedwidget.return_value = mocked_widget
        form.on_new_clicked()

        # THEN: A new row should be added to the table
        form.tag_table_widget.rowCount.assert_called_with()
        form.tag_table_widget.insertRow.assert_called_with(row_count)
        expected_set_item_calls = [
            call(row_count, 0, mocked_table_widget),
            call(row_count, 1, mocked_table_widget),
            call(row_count, 2, mocked_table_widget),
            call(row_count, 3, mocked_table_widget)
        ]
        assert expected_set_item_calls == form.tag_table_widget.setItem.call_args_list, \
            'setItem should have been called correctly'
        form.tag_table_widget.resizeRowsToContents.assert_called_with()
        form.tag_table_widget.scrollToBottom.assert_called_with()
        form.tag_table_widget.selectRow.assert_called_with(row_count)
