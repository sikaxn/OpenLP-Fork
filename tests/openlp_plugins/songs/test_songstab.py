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
This module contains tests for the lib submodule of the Songs plugin.
"""
import pytest
from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtWidgets
from openlp.core.common.enum import SongFirstSlideMode

from openlp.core.common.registry import Registry
from openlp.plugins.songs.lib.songstab import SongsTab

__default_settings__ = {
    'songs/footer template': """${title}""",
    'songs/chord notation': 'english'
}


@pytest.fixture()
def form(settings):
    Registry().register('settings_form', MagicMock())
    Registry().get('settings').extend_default_settings(__default_settings__)
    frm = SongsTab(None, 'Songs', None, None)
    frm.settings_form.register_post_process = MagicMock()
    return frm


def test_german_notation_on_load(form):
    """
    Test the corrent notation is selected on load
    """
    # GIVEN: German notation in the settings
    form.settings.setValue('songs/chord notation', 'german')
    # WHEN: Load is invoked
    form.load()
    # THEN: The german radio button should be checked
    assert form.german_notation_radio_button.isChecked() is True


def test_neolatin_notation_on_load(form):
    """
    Test the corrent notation is selected on load
    """
    # GIVEN: neo-latin notation in the settings
    form.settings.setValue('songs/chord notation', 'neo-latin')
    # WHEN: Load is invoked
    form.load()
    # THEN: The neo-latin radio button should be checked
    assert form.neolatin_notation_radio_button.isChecked() is True


def test_invalid_notation_on_load(form):
    """
    Test the invalid notation in settings reverts to english
    """
    # GIVEN: gibberish notation in the settings
    form.settings.setValue('songs/chord notation', 'gibberish')
    # WHEN: Load is invoked
    form.load()
    # THEN: The english radio button should be checked
    assert form.english_notation_radio_button.isChecked() is True


def test_save_check_box_settings(form):
    """
    Test check box options are correctly saved
    """
    # GIVEN: A arrangement of enabled/disabled check boxes
    form.on_search_as_type_check_box_changed(QtCore.Qt.CheckState.Unchecked)
    form.on_tool_bar_active_check_box_changed(QtCore.Qt.CheckState.Checked)
    form.on_update_on_edit_check_box_changed(QtCore.Qt.CheckState.Unchecked)
    form.on_add_from_service_check_box_changed(QtCore.Qt.CheckState.Checked)
    form.on_disable_chords_import_check_box_changed(QtCore.Qt.CheckState.Unchecked)
    form.on_auto_play_check_box_changed(QtCore.Qt.CheckState.Checked)
    form.on_uppercase_check_box_changed(QtCore.Qt.CheckState.Checked)
    # Preview group
    form.preview_group_box.setChecked(True)
    form.on_preview_intro_check_box_changed(QtCore.Qt.CheckState.Checked)
    form.on_preview_verse_check_box_changed(QtCore.Qt.CheckState.Unchecked)
    form.on_preview_chorus_check_box_changed(QtCore.Qt.CheckState.Checked)
    form.on_preview_bridge_check_box_changed(QtCore.Qt.CheckState.Unchecked)
    form.on_preview_pre_chorus_check_box_changed(QtCore.Qt.CheckState.Checked)
    form.on_preview_ending_check_box_changed(QtCore.Qt.CheckState.Unchecked)
    form.on_preview_other_check_box_changed(QtCore.Qt.CheckState.Checked)

    # WHEN: Save is invoked
    form.save()
    # THEN: The correct values should be stored in the settings
    # song_search is currently unused
    assert form.settings.value('songs/display songbar') is True
    assert form.settings.value('songs/update service on edit') is False
    assert form.settings.value('songs/add song from service') is True
    assert form.settings.value('songs/disable chords import') is False
    assert form.settings.value('songs/auto play audio') is True
    assert form.settings.value('songs/uppercase songs') is True
    # Preview group
    assert form.settings.value('songs/preview_enabled') is True
    assert form.settings.value('songs/preview_intro') is True
    assert form.settings.value('songs/preview_verse') is False
    assert form.settings.value('songs/preview_chorus') is True
    assert form.settings.value('songs/preview_bridge') is False
    assert form.settings.value('songs/preview_pre_chorus') is True
    assert form.settings.value('songs/preview_ending') is False
    assert form.settings.value('songs/preview_other') is True


def test_english_notation_button(form):
    """
    Test notation button clicked handler
    """
    # GIVEN: A normal song form
    # WHEN: english notation clicked
    form.on_english_notation_button_clicked()
    # THEN: Chord notation should be correct
    assert form.chord_notation == 'english'


def test_german_notation_button(form):
    """
    Test notation button clicked handler
    """
    # GIVEN: A normal song form
    # WHEN: german notation clicked
    form.on_german_notation_button_clicked()
    # THEN: Chord notation should be correct
    assert form.chord_notation == 'german'


def test_neolatin_notation_button(form):
    """
    Test notation button clicked handler
    """
    # GIVEN: A normal song form
    # WHEN: neolatin notation clicked
    form.on_neolatin_notation_button_clicked()
    # THEN: Chord notation should be correct
    assert form.chord_notation == 'neo-latin'


@patch('openlp.plugins.songs.lib.songstab.QtWidgets.QMessageBox.question')
@patch('openlp.core.common.settings.Settings.setValue')
def test_password_change(mocked_settings_set_val, mocked_question, form):
    """
    Test the ccli password sends a warning when changed, and saves when accepted
    """
    # GIVEN: Warning is accepted and new password set
    form.ccli_password.setText('new_password')
    mocked_question.return_value = QtWidgets.QMessageBox.StandardButton.Yes
    # WHEN: save is invoked
    form.save()
    # THEN: footer should not have been saved (one less call than the change test below)
    mocked_question.assert_called_once()
    assert mocked_settings_set_val.call_count == 20


@patch('openlp.plugins.songs.lib.songstab.QtWidgets.QMessageBox.question')
@patch('openlp.core.common.settings.Settings.setValue')
def test_password_change_cancelled(mocked_settings_set_val, mocked_question, form):
    """
    Test the ccli password sends a warning when changed and does not save when cancelled
    """
    # GIVEN: Warning is not accepted and new password set
    form.ccli_password.setText('new_password')
    mocked_question.return_value = QtWidgets.QMessageBox.StandardButton.No
    # WHEN: save is invoked
    form.save()
    # THEN: footer should not have been saved (one less call than the change test below)
    mocked_question.assert_called_once()
    assert mocked_settings_set_val.call_count == 19


@patch('openlp.core.common.settings.Settings.setValue')
def test_footer_nochange(mocked_settings_set_val, form):
    """
    Test the footer is not saved when not changed
    """
    # GIVEN: A normal song form
    # WHEN: save is invoked
    form.save()
    # THEN: footer should not have been saved (one less call than the change test below)
    assert mocked_settings_set_val.call_count == 20


@patch('openlp.core.common.settings.Settings.setValue')
def test_footer_change(mocked_settings_set_val, form):
    """
    Test the footer is saved when changed
    """
    # GIVEN: Footer has changed
    form.footer_edit_box.setPlainText('A new footer')
    # WHEN: save is invoked
    form.save()
    # THEN: footer should have been saved (one more call to setValue than the nochange test)
    assert mocked_settings_set_val.call_count == 21
    assert form.footer_edit_box.toPlainText() == 'A new footer'


def test_footer_reset(form):
    """
    Test the footer is reset when reset clicked
    """
    # GIVEN: A default footer and different content in the edit box
    form.settings.setValue('songs/footer template', 'hello')
    form.footer_edit_box.setPlainText('A different footer')
    # WHEN: reset is invoked
    form.on_footer_reset_button_clicked()
    # THEN: footer edit box should have been reset to the settings value
    assert form.footer_edit_box.toPlainText() == form.settings.get_default_value('songs/footer template')


def test_footer_reset_save(form):
    """
    Test the footer can be saved as the default value
    """
    # GIVEN: A non default footer template and the default template in the edit box
    form.settings.setValue('songs/footer template', 'hello')
    default_footer = form.settings.get_default_value('songs/footer template')
    form.footer_edit_box.setPlainText(default_footer)
    # WHEN: save is invoked
    form.save()
    # THEN: footer template should have been reset to the default_footer value
    assert form.settings.value('songs/footer template') == form.settings.get_default_value('songs/footer template')


def test_save_tab_nochange(form):
    """
    Test no changes does not trigger post processing
    """
    # GIVEN: No changes on the form.
    # WHEN: the save is invoked
    form.save()
    # THEN: the post process should not be requested
    assert 0 == form.settings_form.register_post_process.call_count, \
        'Songs Post processing should not have been requested'


def test_save_tab_change(form):
    """
    Test save after visiting the page triggers post processing.
    """
    # GIVEN: Form has been visited.
    form.tab_visited = True
    # WHEN: the save is invoked
    form.save()
    # THEN: the post process should be requested
    assert 1 == form.settings_form.register_post_process.call_count, \
        'Songs Post processing should have been requested'


def test_save_first_slide_settings(form):
    """
    Tests that "Add First Slide" setting is saved correctly.
    """
    # GIVEN: "Add First Slide" has been changed
    form.on_first_slide_mode_combo_box_changed(2)

    # WHEN: save() is invoked
    form.save()

    # THEN: The correct values should be stored in the settings
    assert form.settings.value('songs/first slide mode') is SongFirstSlideMode.Footer.value
