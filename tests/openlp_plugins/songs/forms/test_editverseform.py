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
This module contains tests for the editverseform of the Songs plugin.
"""
from unittest.mock import MagicMock, call, patch

import pytest
from PySide6 import QtCore, QtTest, QtGui, QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.songs.forms.editverseform import EditVerseForm


@pytest.fixture()
def edit_verse_form(registry: Registry, settings: Settings) -> EditVerseForm:
    main_window = QtWidgets.QMainWindow()
    registry.register('main_window', main_window)
    frm = EditVerseForm()
    yield frm
    del frm
    del main_window


@patch('openlp.plugins.songs.forms.editverseform.QtWidgets.QDialog')
def test_exec(MockQDialog: MagicMock, edit_verse_form: EditVerseForm):
    """Test the Exec method of the form"""
    # GIVEN: An EditVerseForm with the QDialog mocked out
    MockQDialog.exec.return_value = 1

    # WHEN: exec() is called
    result = edit_verse_form.exec()

    # THEN: The result should be Accepted
    assert result == 1


@pytest.mark.parametrize('chords_enabled', [True, False])
@patch('openlp.plugins.songs.forms.editverseform.QtWidgets.QDialog')
@patch('openlp.plugins.songs.forms.editverseform.transpose_lyrics')
def test_accept(mocked_transpose_lyrics: MagicMock, MockQDialog: MagicMock, chords_enabled: bool, settings: Settings,
                edit_verse_form: EditVerseForm):
    """Test the accept method of the form"""
    # GIVEN: An EditVerseForm with the QDialog mocked out and the chords enabled or disabled
    settings.setValue('songs/enable chords', chords_enabled)

    # WHEN: accept() is called
    edit_verse_form.accept()

    # THEN: The result should be Accepted
    if chords_enabled:
        mocked_transpose_lyrics.assert_called()
    else:
        mocked_transpose_lyrics.assert_not_called()


@patch('openlp.plugins.songs.forms.editverseform.QtWidgets.QDialog')
@patch('openlp.plugins.songs.forms.editverseform.transpose_lyrics')
@patch('openlp.plugins.songs.forms.editverseform.critical_error_message_box')
def test_accept_exception(mocked_critical_error: MagicMock, mocked_transpose_lyrics: MagicMock, MockQDialog: MagicMock,
                          settings: Settings, edit_verse_form: EditVerseForm):
    """Test the accept method of the form correctly handles the KeyError exception"""
    # GIVEN: An EditVerseForm with the QDialog mocked out and the chords enabled
    settings.setValue('songs/enable chords', True)
    mocked_transpose_lyrics.side_effect = KeyError('test')

    # WHEN: accept() is called
    edit_verse_form.accept()

    # THEN: The result should be Accepted
    mocked_critical_error.assert_called()


def test_ui_defaults(edit_verse_form: EditVerseForm):
    """
    Test the EditVerseForm defaults are correct
    """
    # GIVEN: An EditVerseForm instance
    # WHEN: The form is shown
    # THEN: The default value is correct
    assert edit_verse_form.verse_text_edit.toPlainText() == '', 'The verse edit box is empty.'


def test_type_verse_text(edit_verse_form: EditVerseForm):
    """
    Test that typing into the verse text edit box returns the correct text
    """
    # GIVEN: An instance of the EditVerseForm and some text to type
    text = 'Amazing Grace, how sweet the sound!'

    # WHEN: Some verse text is typed into the text edit
    QtTest.QTest.keyClicks(edit_verse_form.verse_text_edit, text)

    # THEN: The verse text edit should have the verse text in it
    assert text == edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse text edit should have the typed out verse'


def test_insert_verse(edit_verse_form: EditVerseForm):
    """
    Test the insert_verse() method
    """
    # GIVEN: An EditVerseForm instance, with stuff mocked out
    with patch.object(edit_verse_form, 'verse_text_edit') as mocked_verse_text_edit:
        mocked_verse_text_edit.textCursor.return_value.columnNumber.return_value = 1
        # WHEN: insert_verse() is called
        edit_verse_form.insert_verse('V')
        # THEN: The verse is inserted
        assert mocked_verse_text_edit.insertPlainText.call_args_list == [call('\n'), call('---[Verse:1]---\n')]
        mocked_verse_text_edit.setFocus()


def test_insert_verse_insert_click(edit_verse_form: EditVerseForm):
    """
    Test that clicking the insert button inserts the correct verse marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The Insert button is clicked
    QtTest.QTest.mouseClick(edit_verse_form.insert_button, QtCore.Qt.MouseButton.LeftButton)

    # THEN: The verse text edit should have a Verse:1 in it
    assert '---[Verse:1]---' in edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a verse marker'


def test_insert_verse_up_click(edit_verse_form: EditVerseForm):
    """
    Test that clicking the up button on the spin box and then clicking the insert button inserts the correct marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The spin button and then the Insert button are clicked
    QtTest.QTest.keyClick(edit_verse_form.verse_number_box, QtCore.Qt.Key.Key_Up)
    QtTest.QTest.mouseClick(edit_verse_form.insert_button, QtCore.Qt.MouseButton.LeftButton)

    # THEN: The verse text edit should have a Verse:1 in it
    assert '---[Verse:2]---' in edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a "Verse 2" marker'


def test_insert_chorus(edit_verse_form: EditVerseForm):
    """
    Test that clicking the verse type combo box and then clicking the insert button inserts the correct marker
    """
    # GIVEN: An instance of the EditVerseForm
    # WHEN: The verse type combo box and then the Insert button are clicked
    QtTest.QTest.keyClick(edit_verse_form.verse_type_combo_box, QtCore.Qt.Key.Key_Down)
    QtTest.QTest.mouseClick(edit_verse_form.insert_button, QtCore.Qt.MouseButton.LeftButton)

    # THEN: The verse text edit should have a Chorus:1 in it
    assert '---[Chorus:1]---' in edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse text edit should have a "Chorus 1" marker'


def test_update_suggested_verse_number_has_no_effect(edit_verse_form: EditVerseForm):
    """
    Test that update_suggested_verse_number() has no effect when editing a single verse
    """
    # GIVEN some input values
    edit_verse_form.has_single_verse = True
    edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=0)
    edit_verse_form.verse_text_edit.toPlainText = MagicMock(return_value='Text')
    edit_verse_form.verse_number_box.setValue(3)

    # WHEN the method is called
    edit_verse_form.update_suggested_verse_number()

    # THEN the verse number must not be changed
    assert 3 == edit_verse_form.verse_number_box.value(), 'The verse number should be 3'


def test_update_suggested_verse_number_different_type(edit_verse_form: EditVerseForm):
    """
    Test that update_suggested_verse_number() returns 0 when editing a second verse of a different type
    """
    # GIVEN some input values
    edit_verse_form.has_single_verse = False
    edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=2)
    edit_verse_form.verse_text_edit.toPlainText = MagicMock(return_value='Text')
    edit_verse_form.verse_number_box.setValue(3)

    # WHEN the method is called
    edit_verse_form.update_suggested_verse_number()

    # THEN the verse number must be changed to 1
    assert 1 == edit_verse_form.verse_number_box.value(), 'The verse number should be 1'


def test_on_divide_split_button_clicked(edit_verse_form: EditVerseForm):
    """
    Test that divide adds text at the correct position
    """
    # GIVEN some input values
    edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=4)
    edit_verse_form.verse_text_edit.setPlainText('Text\n')

    # WHEN the method is called
    edit_verse_form.on_forced_split_button_clicked()
    # THEN the verse number must not be changed
    assert '[--}{--]\nText\n' == edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse number should be [--}{--]\nText\n'


def test_on_split_button_clicked(edit_verse_form: EditVerseForm):
    """
    Test that divide adds text at the correct position
    """
    # GIVEN some input values
    edit_verse_form.verse_type_combo_box.currentIndex = MagicMock(return_value=4)
    edit_verse_form.verse_text_edit.setPlainText('Text\n')

    # WHEN the method is called
    edit_verse_form.on_overflow_split_button_clicked()
    # THEN the verse number must not be changed
    assert '[---]\nText\n' == edit_verse_form.verse_text_edit.toPlainText(), \
        'The verse number should be [---]\nText\n'


@patch('openlp.plugins.songs.forms.editverseform.show_key_warning')
def test_on_transpose_up_button_clicked_key_warning(mocked_show_key_warning: MagicMock, edit_verse_form: EditVerseForm):
    """
    Test that transpose button will transpose the chords and warn about missing song key
    """
    # GIVEN some input values
    edit_verse_form.verse_text_edit.setPlainText('Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')

    # WHEN the method is called
    edit_verse_form.on_transpose_up_button_clicked()

    # THEN chords should be transposed up
    mocked_show_key_warning.assert_called_once_with(edit_verse_form)
    assert 'Am[Ab]azing gr[Ab/C]ace, how sw[C#]eet the s[Ab]ound' == edit_verse_form.verse_text_edit.toPlainText()


@patch('openlp.plugins.songs.forms.editverseform.show_key_warning')
def test_on_transpose_up_button_clicked_no_key_warning(mocked_show_key_warning: MagicMock,
                                                       edit_verse_form: EditVerseForm):
    """
    Test that transpose button will transpose the chords but won't show a key error
    """
    # GIVEN some input values
    edit_verse_form.verse_text_edit.setPlainText('[=G]Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')

    # WHEN the method is called
    edit_verse_form.on_transpose_up_button_clicked()

    # THEN chords should be transposed up
    mocked_show_key_warning.assert_not_called()
    assert '[=Ab]Am[Ab]azing gr[Ab/C]ace, how sw[Db]eet the s[Ab]ound' == edit_verse_form.verse_text_edit.toPlainText()


@patch('openlp.plugins.songs.forms.editverseform.show_key_warning')
@patch('openlp.plugins.songs.forms.editverseform.critical_error_message_box')
def test_on_transpose_up_button_clicked_with_keyerror(mocked_critical_error: MagicMock,
                                                      mocked_show_key_warning: MagicMock,
                                                      edit_verse_form: EditVerseForm):
    """
    Test that transpose button will transpose the chords and warn about missing song key
    """
    # GIVEN some input values annd a hacked show_key_warning to throw an exception
    edit_verse_form.verse_text_edit.setPlainText('Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')
    mocked_show_key_warning.side_effect = KeyError('"A" not found in "chords"')

    # WHEN the method is called
    edit_verse_form.on_transpose_up_button_clicked()

    # THEN An error message should have been shown
    mocked_critical_error.assert_called_once_with(title='Transposing failed', message='Transposing failed because of '
                                                  'invalid chord:\n\'"A" not found in "chords"\'')


@patch('openlp.plugins.songs.forms.editverseform.show_key_warning')
def test_on_transpose_down_button_clicked_key_warning(mocked_show_key_warning: MagicMock,
                                                      edit_verse_form: EditVerseForm):
    """
    Test that transpose button will transpose the chords and warn about missing song key
    """
    # GIVEN some input values
    edit_verse_form.verse_text_edit.setPlainText('Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')

    # WHEN the method is called
    edit_verse_form.on_transpose_down_button_clicked()

    # THEN chords should be transposed up
    mocked_show_key_warning.assert_called_once_with(edit_verse_form)
    assert 'Am[F#]azing gr[F#/A#]ace, how sw[B]eet the s[F#]ound' == edit_verse_form.verse_text_edit.toPlainText()


@patch('openlp.plugins.songs.forms.editverseform.show_key_warning')
def test_on_transpose_down_button_clicked_no_key_warning(mocked_show_key_warning: MagicMock,
                                                         edit_verse_form: EditVerseForm):
    """
    Test that transpose button will transpose the chords but won't show a message about the key
    """
    # GIVEN some input values
    edit_verse_form.verse_text_edit.setPlainText('[=G]Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')

    # WHEN the method is called
    edit_verse_form.on_transpose_down_button_clicked()

    # THEN chords should be transposed up
    mocked_show_key_warning.assert_not_called()
    assert '[=F#]Am[F#]azing gr[F#/A#]ace, how sw[B]eet the s[F#]ound' == edit_verse_form.verse_text_edit.toPlainText()


@patch('openlp.plugins.songs.forms.editverseform.show_key_warning')
@patch('openlp.plugins.songs.forms.editverseform.critical_error_message_box')
def test_on_transpose_down_button_clicked_keyerror(mocked_critical_error: MagicMock, mocked_show_key_warning: MagicMock,
                                                   edit_verse_form: EditVerseForm):
    """
    Test that transpose button shows an error message when there is an invalid chord
    """
    # GIVEN some input values
    edit_verse_form.verse_text_edit.setPlainText('Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')
    mocked_show_key_warning.side_effect = KeyError('"A" not found in "chords"')

    # WHEN the method is called
    edit_verse_form.on_transpose_down_button_clicked()

    # THEN An error message should have been shown
    mocked_critical_error.assert_called_once_with(title='Transposing failed', message='Transposing failed because of '
                                                  'invalid chord:\n\'"A" not found in "chords"\'')


def test_set_verse_single(settings: Settings, edit_verse_form: EditVerseForm):
    """
    Test the set_verse() method of the EditVerseForm for single verses
    """
    # GIVEN: An EditVerseForm instance, with some stuff mocked out, and chords enabled
    settings.setValue('songs/enable chords', True)

    with patch.object(edit_verse_form, 'verse_type_combo_box') as mocked_verse_type_combo, \
            patch.object(edit_verse_form, 'verse_number_box') as mocked_verse_number_box, \
            patch.object(edit_verse_form, 'insert_button') as mocked_insert_button, \
            patch.object(edit_verse_form, 'transpose_widget') as mocked_transpose_widget, \
            patch.object(edit_verse_form, 'verse_text_edit') as mocked_verse_text_edit:
        # WHEN: set_verse() is called
        edit_verse_form.set_verse('Amazing grace, how sweet the sound', single=True)

        # THEN: The right things should have been done
        mocked_verse_type_combo.setCurrentIndex.assert_called_once_with(0)
        mocked_verse_number_box.setValue.assert_called_once_with(1)
        mocked_insert_button.setVisible.assert_called_once_with(False)
        mocked_transpose_widget.setVisible.assert_called_once_with(False)
        mocked_verse_text_edit.setPlainText.assert_called_once_with('Amazing grace, how sweet the sound')
        mocked_verse_text_edit.setFocus.assert_called_once_with()
        mocked_verse_text_edit.moveCursor.assert_called_once_with(QtGui.QTextCursor.MoveOperation.End)


def test_set_verse_multiple(settings: Settings, edit_verse_form: EditVerseForm):
    """
    Test the set_verse() method of the EditVerseForm for multiple verses
    """
    # GIVEN: An EditVerseForm instance, with some stuff mocked out, and chords enabled
    settings.setValue('songs/enable chords', True)

    with patch.object(edit_verse_form, 'verse_type_combo_box') as mocked_verse_type_combo, \
            patch.object(edit_verse_form, 'verse_number_box') as mocked_verse_number_box, \
            patch.object(edit_verse_form, 'insert_button') as mocked_insert_button, \
            patch.object(edit_verse_form, 'transpose_widget') as mocked_transpose_widget, \
            patch.object(edit_verse_form, 'verse_text_edit') as mocked_verse_text_edit:
        # WHEN: set_verse() is called
        edit_verse_form.set_verse(None)

        # THEN: The right things should have been done
        mocked_verse_type_combo.setCurrentIndex.assert_called_once_with(0)
        mocked_verse_number_box.setValue.assert_called_once_with(1)
        mocked_insert_button.setVisible.assert_called_once_with(True)
        mocked_transpose_widget.setVisible.assert_called_once_with(True)
        mocked_verse_text_edit.setPlainText.assert_called_once_with('---[Verse:1]---\n')
        mocked_verse_text_edit.setFocus.assert_called_once_with()
        mocked_verse_text_edit.moveCursor.assert_called_once_with(QtGui.QTextCursor.MoveOperation.End)


def test_set_verse_multiple_chords_disabled(settings: Settings, edit_verse_form: EditVerseForm):
    """
    Test the set_verse() method of the EditVerseForm for multiple verses when chords are disabled
    """
    # GIVEN: An EditVerseForm instance, with some stuff mocked out, and chords enabled
    settings.setValue('songs/enable chords', False)

    with patch.object(edit_verse_form, 'verse_type_combo_box') as mocked_verse_type_combo, \
            patch.object(edit_verse_form, 'verse_number_box') as mocked_verse_number_box, \
            patch.object(edit_verse_form, 'insert_button') as mocked_insert_button, \
            patch.object(edit_verse_form, 'transpose_widget') as mocked_transpose_widget, \
            patch.object(edit_verse_form, 'verse_text_edit') as mocked_verse_text_edit:
        # WHEN: set_verse() is called
        edit_verse_form.set_verse(None)

        # THEN: The right things should have been done
        mocked_verse_type_combo.setCurrentIndex.assert_called_once_with(0)
        mocked_verse_number_box.setValue.assert_called_once_with(1)
        mocked_insert_button.setVisible.assert_called_once_with(True)
        mocked_transpose_widget.setVisible.assert_not_called()
        mocked_verse_text_edit.setPlainText.assert_called_once_with('---[Verse:1]---\n')
        mocked_verse_text_edit.setFocus.assert_called_once_with()
        mocked_verse_text_edit.moveCursor.assert_called_once_with(QtGui.QTextCursor.MoveOperation.End)


def test_add_splitter_to_text(edit_verse_form: EditVerseForm):
    """
    Test the _add_splitter_to_text() method
    """
    # GIVEN: An EditVerseForm instance, with some stuff mocked out
    with patch.object(edit_verse_form, 'verse_text_edit') as mocked_verse_text_edit:
        mocked_verse_text_edit.toPlainText.return_value = 'this is a verse'
        mocked_verse_text_edit.textCursor.return_value.position.return_value = 1

        # WHEN: _add_splitter_to_text() is called
        edit_verse_form._add_splitter_to_text('another line to add')

        # THEN: The correct things should have been done
        mocked_verse_text_edit.insertPlainText.assert_called_once_with('\nanother line to add\n')
        mocked_verse_text_edit.setFocus.assert_called_once_with()


def test_get_verse(edit_verse_form: EditVerseForm):
    """
    Test getting the verse via get_verse()
    """
    # GIVEN: An EditVerseForm with some text
    edit_verse_form.verse_text_edit.setPlainText('[=G]Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')
    edit_verse_form.verse_type_combo_box.setCurrentIndex(0)
    edit_verse_form.verse_number_box.setValue(2)

    # WHEN: get_verse() is called
    result = edit_verse_form.get_verse()

    # THEN: We should get the right verse back
    assert result == ('[=G]Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound', 'v', '2')


def test_get_all_verses(edit_verse_form: EditVerseForm):
    """
    Test getting all the verses via get_all_verses()
    """
    # GIVEN: An EditVerseForm with some text
    edit_verse_form.verse_text_edit.setPlainText('[=G]Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound')
    edit_verse_form.verse_type_combo_box.setCurrentIndex(0)
    edit_verse_form.verse_number_box.setValue(1)

    # WHEN: get_verse() is called
    result = edit_verse_form.get_all_verses()

    # THEN: We should get the right verse back
    assert result == '---[Verse:1]---\n[=G]Am[G]azing gr[G/B]ace, how sw[C]eet the s[G]ound'


@patch('openlp.plugins.songs.forms.editverseform.VERSE_REGEX')
def test_update_suggested_verse_number_no_end_part(mocked_verse_regex: MagicMock, edit_verse_form: EditVerseForm):
    """
    Test the update_suggested_verse_number() method when a verse tag doesn't  contain its end
    """
    # GIVEN: An EditVerseForm with a malformed "--[Verse:1]---" separator
    verse_text = '---[Verse:1\nAmazing grace, how sweet the sound'
    edit_verse_form.verse_text_edit.setPlainText(verse_text)

    with patch.object(edit_verse_form.verse_text_edit, 'textCursor') as mocked_text_cursor:
        mocked_text_cursor.return_value.position.return_value = len(verse_text)

        # WHEN: update_suggested_verse_number() is called
        edit_verse_form.update_suggested_verse_number()

        # THEN: The method should have exited early
        mocked_verse_regex.match.assert_not_called()


def test_update_suggested_verse_number_no_match(edit_verse_form: EditVerseForm):
    """
    Test the update_suggested_verse_number() method when a verse tag doesn't  contain its end
    """
    # GIVEN: An EditVerseForm with a malformed "--[Verse:1]---" separator
    verse_text = '---[Verse:X]---\nAmazing grace, how sweet the sound'
    edit_verse_form.verse_text_edit.setPlainText(verse_text)

    with patch.object(edit_verse_form.verse_text_edit, 'textCursor') as mocked_text_cursor, \
            patch.object(edit_verse_form, 'verse_number_box') as mocked_verse_number_box:
        mocked_text_cursor.return_value.position.return_value = len(verse_text)

        # WHEN: update_suggested_verse_number() is called
        edit_verse_form.update_suggested_verse_number()

        # THEN: The method should have exited early
        mocked_verse_number_box.setValue.assert_called_once_with(1)
