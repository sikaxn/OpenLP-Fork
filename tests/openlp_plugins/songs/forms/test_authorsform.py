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
Package to test the openlp.plugins.songs.forms.authorsform package.
"""
import pytest
from unittest.mock import patch

from PySide6 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.songs.forms.authorsform import AuthorsForm


@pytest.fixture()
def form(settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    frm = AuthorsForm()
    yield frm
    del frm
    del main_window


def test_ui_defaults(form):
    """
    Test the AuthorForm defaults are correct
    """
    assert form.first_name_edit.text() == '', 'The first name edit should be empty'
    assert form.last_name_edit.text() == '', 'The last name edit should be empty'
    assert form.display_edit.text() == '', 'The display name edit should be empty'


def test_get_first_name_property(form):
    """
    Test that getting the first name property on the AuthorForm works correctly
    """
    # GIVEN: A first name to set
    first_name = 'John'

    # WHEN: The first_name_edit's text is set
    form.first_name_edit.setText(first_name)

    # THEN: The first_name property should have the correct value
    assert form.first_name == first_name, 'The first name property should be correct'


def test_set_first_name_property(form):
    """
    Test that setting the first name property on the AuthorForm works correctly
    """
    # GIVEN: A first name to set
    first_name = 'James'

    # WHEN: The first_name property is set
    form.first_name = first_name

    # THEN: The first_name_edit should have the correct value
    assert form.first_name_edit.text() == first_name, 'The first name should be set correctly'


def test_get_last_name_property(form):
    """
    Test that getting the last name property on the AuthorForm works correctly
    """
    # GIVEN: A last name to set
    last_name = 'Smith'

    # WHEN: The last_name_edit's text is set
    form.last_name_edit.setText(last_name)

    # THEN: The last_name property should have the correct value
    assert form.last_name == last_name, 'The last name property should be correct'


def test_set_last_name_property(form):
    """
    Test that setting the last name property on the AuthorForm works correctly
    """
    # GIVEN: A last name to set
    last_name = 'Potter'

    # WHEN: The last_name property is set
    form.last_name = last_name

    # THEN: The last_name_edit should have the correct value
    assert form.last_name_edit.text() == last_name, 'The last name should be set correctly'


def test_get_display_name_property(form):
    """
    Test that getting the display name property on the AuthorForm works correctly
    """
    # GIVEN: A display name to set
    display_name = 'John'

    # WHEN: The display_name_edit's text is set
    form.display_edit.setText(display_name)

    # THEN: The display_name property should have the correct value
    assert form.display_name == display_name, 'The display name property should be correct'


def test_set_display_name_property(form):
    """
    Test that setting the display name property on the AuthorForm works correctly
    """
    # GIVEN: A display name to set
    display_name = 'John'

    # WHEN: The display_name property is set
    form.display_name = display_name

    # THEN: The display_name_edit should have the correct value
    assert form.display_edit.text() == display_name, 'The display name should be set correctly'


@patch('openlp.plugins.songs.forms.authorsform.QtWidgets.QDialog.exec')
def test_exec(mocked_exec, form):
    """
    Test the exec() method
    """
    # GIVEN: An authors for and various mocked objects
    with patch.object(form.first_name_edit, 'clear') as mocked_first_name_edit_clear, \
            patch.object(form.last_name_edit, 'clear') as mocked_last_name_edit_clear, \
            patch.object(form.display_edit, 'clear') as mocked_display_edit_clear, \
            patch.object(form.first_name_edit, 'setFocus') as mocked_first_name_edit_setFocus:
        # WHEN: The exec() method is called
        form.exec(clear=True)

        # THEN: The clear and exec() methods should have been called
    mocked_first_name_edit_clear.assert_called_once_with()
    mocked_last_name_edit_clear.assert_called_once_with()
    mocked_display_edit_clear.assert_called_once_with()
    mocked_first_name_edit_setFocus.assert_called_once_with()
    mocked_exec.assert_called_once_with(form)


def test_first_name_edited(form):
    """
    Test the on_first_name_edited() method
    """
    # GIVEN: An author form
    form.auto_display_name = True

    with patch.object(form.last_name_edit, 'text') as mocked_last_name_edit_text, \
            patch.object(form.display_edit, 'setText') as mocked_display_edit_setText:
        mocked_last_name_edit_text.return_value = 'Newton'

        # WHEN: on_first_name_edited() is called
        form.on_first_name_edited('John')

    # THEN: The display name should be updated
    assert mocked_last_name_edit_text.call_count == 2
    mocked_display_edit_setText.assert_called_once_with('John Newton')


def test_first_name_edited_no_auto(form):
    """
    Test the on_first_name_edited() method without auto_display_name
    """
    # GIVEN: An author form
    form.auto_display_name = False

    with patch.object(form.last_name_edit, 'text') as mocked_last_name_edit_text, \
            patch.object(form.display_edit, 'setText') as mocked_display_edit_setText:

        # WHEN: on_first_name_edited() is called
        form.on_first_name_edited('John')

    # THEN: The display name should not be updated
    assert mocked_last_name_edit_text.call_count == 0
    assert mocked_display_edit_setText.call_count == 0


def test_last_name_edited(form):
    """
    Test the on_last_name_edited() method
    """
    # GIVEN: An author form
    form.auto_display_name = True

    with patch.object(form.first_name_edit, 'text') as mocked_first_name_edit_text, \
            patch.object(form.display_edit, 'setText') as mocked_display_edit_setText:
        mocked_first_name_edit_text.return_value = 'John'

        # WHEN: on_last_name_edited() is called
        form.on_last_name_edited('Newton')

    # THEN: The display name should be updated
    assert mocked_first_name_edit_text.call_count == 2
    mocked_display_edit_setText.assert_called_once_with('John Newton')


def test_last_name_edited_no_auto(form):
    """
    Test the on_last_name_edited() method without auto_display_name
    """
    # GIVEN: An author form
    form.auto_display_name = False

    with patch.object(form.first_name_edit, 'text') as mocked_first_name_edit_text, \
            patch.object(form.display_edit, 'setText') as mocked_display_edit_setText:

        # WHEN: on_last_name_edited() is called
        form.on_last_name_edited('Newton')

    # THEN: The display name should not be updated
    assert mocked_first_name_edit_text.call_count == 0
    assert mocked_display_edit_setText.call_count == 0


@patch('openlp.plugins.songs.forms.authorsform.critical_error_message_box')
def test_accept_no_first_name(mocked_critical_error, form):
    """
    Test the accept() method with no first name
    """
    # GIVEN: A form and no text in thefirst name edit
    with patch.object(form.first_name_edit, 'text') as mocked_first_name_edit_text, \
            patch.object(form.first_name_edit, 'setFocus') as mocked_first_name_edit_setFocus:
        mocked_first_name_edit_text.return_value = ''

        # WHEN: accept() is called
        result = form.accept()

    # THEN: The result should be false and a critical error displayed
    assert result is False
    mocked_critical_error.assert_called_once_with(message='You need to type in the first name of the author.')
    mocked_first_name_edit_text.assert_called_once_with()
    mocked_first_name_edit_setFocus.assert_called_once_with()


@patch('openlp.plugins.songs.forms.authorsform.critical_error_message_box')
def test_accept_no_last_name(mocked_critical_error, form):
    """
    Test the accept() method with no last name
    """
    # GIVEN: A form and no text in the last name edit
    with patch.object(form.first_name_edit, 'text') as mocked_first_name_edit_text, \
            patch.object(form.last_name_edit, 'text') as mocked_last_name_edit_text, \
            patch.object(form.last_name_edit, 'setFocus') as mocked_last_name_edit_setFocus:
        mocked_first_name_edit_text.return_value = 'John'
        mocked_last_name_edit_text.return_value = ''

        # WHEN: accept() is called
        result = form.accept()

    # THEN: The result should be false and a critical error displayed
    assert result is False
    mocked_critical_error.assert_called_once_with(message='You need to type in the last name of the author.')
    mocked_first_name_edit_text.assert_called_once_with()
    mocked_last_name_edit_text.assert_called_once_with()
    mocked_last_name_edit_setFocus.assert_called_once_with()


@patch('openlp.plugins.songs.forms.authorsform.critical_error_message_box')
def test_accept_no_display_name_no_combine(mocked_critical_error, form):
    """
    Test the accept() method with no display name and no combining
    """
    # GIVEN: A form and no text in the display name edit
    mocked_critical_error.return_value = QtWidgets.QMessageBox.StandardButton.No
    with patch.object(form.first_name_edit, 'text') as mocked_first_name_edit_text, \
            patch.object(form.last_name_edit, 'text') as mocked_last_name_edit_text, \
            patch.object(form.display_edit, 'text') as mocked_display_edit_text, \
            patch.object(form.display_edit, 'setFocus') as mocked_display_edit_setFocus:
        mocked_first_name_edit_text.return_value = 'John'
        mocked_last_name_edit_text.return_value = 'Newton'
        mocked_display_edit_text.return_value = ''

        # WHEN: accept() is called
        result = form.accept()

    # THEN: The result should be false and a critical error displayed
    assert result is False
    mocked_critical_error.assert_called_once_with(
        message='You have not set a display name for the author, combine the first and last names?',
        parent=form, question=True)
    mocked_first_name_edit_text.assert_called_once_with()
    mocked_last_name_edit_text.assert_called_once_with()
    mocked_display_edit_text.assert_called_once_with()
    mocked_display_edit_setFocus.assert_called_once_with()


@patch('openlp.plugins.songs.forms.authorsform.critical_error_message_box')
@patch('openlp.plugins.songs.forms.authorsform.QtWidgets.QDialog.accept')
def test_accept_no_display_name(mocked_accept, mocked_critical_error, form):
    """
    Test the accept() method with no display name and auto-combine
    """
    # GIVEN: A form and no text in the display name edit
    mocked_accept.return_value = True
    mocked_critical_error.return_value = QtWidgets.QMessageBox.StandardButton.Yes
    with patch.object(form.first_name_edit, 'text') as mocked_first_name_edit_text, \
            patch.object(form.last_name_edit, 'text') as mocked_last_name_edit_text, \
            patch.object(form.display_edit, 'text') as mocked_display_edit_text, \
            patch.object(form.display_edit, 'setText') as mocked_display_edit_setText:
        mocked_first_name_edit_text.return_value = 'John'
        mocked_last_name_edit_text.return_value = 'Newton'
        mocked_display_edit_text.return_value = ''

        # WHEN: accept() is called
        result = form.accept()

    # THEN: The result should be false and a critical error displayed
    assert result is True
    mocked_critical_error.assert_called_once_with(
        message='You have not set a display name for the author, combine the first and last names?',
        parent=form, question=True)
    assert mocked_first_name_edit_text.call_count == 2
    assert mocked_last_name_edit_text.call_count == 2
    mocked_display_edit_text.assert_called_once_with()
    mocked_display_edit_setText.assert_called_once_with('John Newton')
    mocked_accept.assert_called_once_with(form)


@patch('openlp.plugins.songs.forms.authorsform.QtWidgets.QDialog.accept')
def test_accept(mocked_accept, form):
    """
    Test the accept() method
    """
    # GIVEN: A form and text in the right places
    mocked_accept.return_value = True
    with patch.object(form.first_name_edit, 'text') as mocked_first_name_edit_text, \
            patch.object(form.last_name_edit, 'text') as mocked_last_name_edit_text, \
            patch.object(form.display_edit, 'text') as mocked_display_edit_text:
        mocked_first_name_edit_text.return_value = 'John'
        mocked_last_name_edit_text.return_value = 'Newton'
        mocked_display_edit_text.return_value = 'John Newton'

        # WHEN: accept() is called
        result = form.accept()

    # THEN: The result should be false and a critical error displayed
    assert result is True
    mocked_first_name_edit_text.assert_called_once_with()
    mocked_last_name_edit_text.assert_called_once_with()
    mocked_display_edit_text.assert_called_once_with()
    mocked_accept.assert_called_once_with(form)
