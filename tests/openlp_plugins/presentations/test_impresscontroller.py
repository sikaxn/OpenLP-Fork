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
Functional tests to test the Impress class and related methods.
"""
import pytest
from unittest.mock import MagicMock, call, patch

from openlp.plugins.presentations.lib.impresscontroller import ImpressController, ImpressDocument, TextType
from tests.utils.constants import RESOURCE_PATH


@pytest.fixture()
def doc(settings):
    mocked_plugin = MagicMock()
    mocked_plugin.settings_section = 'presentations'
    file_name = RESOURCE_PATH / 'presentations' / 'test.pptx'
    ppc = ImpressController(mocked_plugin)
    return ImpressDocument(ppc, file_name)


def test_constructor(settings, mock_plugin):
    """
    Test the Constructor from the ImpressController
    """
    # GIVEN: No presentation controller
    controller = None

    # WHEN: The presentation controller object is created
    controller = ImpressController(plugin=mock_plugin)

    # THEN: The name of the presentation controller should be correct
    assert 'Impress' == controller.name, 'The name of the presentation controller should be correct'


@patch('openlp.plugins.presentations.lib.impresscontroller.log')
def test_check_available(mocked_log, settings, mock_plugin):
    """
    Test `ImpressController.check_available` on Windows
    """
    # GIVEN: An instance of :class:`ImpressController`
    controller = ImpressController(plugin=mock_plugin)

    # WHEN: `check_available` is called on Windows and `get_com_servicemanager` returns None
    with patch('openlp.plugins.presentations.lib.impresscontroller.is_win', return_value=True), \
            patch.object(controller, 'get_com_servicemanager', return_value=None) as mocked_get_com_servicemanager:
        result = controller.check_available()

        # THEN: `check_available` should return False
        assert mocked_get_com_servicemanager.called is True
        assert result is False


@patch('openlp.plugins.presentations.lib.impresscontroller.log')
def test_check_available_on_windows(mocked_log, settings, mock_plugin):
    """
    Test `ImpressController.check_available` on Windows
    """
    # GIVEN: An instance of :class:`ImpressController`
    controller = ImpressController(plugin=mock_plugin)

    # WHEN: `check_available` is called on Windows and `get_com_servicemanager` returns an object
    mocked_com_object = MagicMock()
    with patch('openlp.plugins.presentations.lib.impresscontroller.is_win', return_value=True), \
            patch.object(controller, 'get_com_servicemanager', return_value=mocked_com_object) \
            as mocked_get_com_servicemanager:
        result = controller.check_available()

        # THEN: `check_available` should return True
        assert mocked_get_com_servicemanager.called is True
        assert result is True


@patch('openlp.plugins.presentations.lib.impresscontroller.log')
@patch('openlp.plugins.presentations.lib.impresscontroller.is_win', return_value=False)
def test_check_available_on_linux(mocked_is_win, mocked_log, settings, mock_plugin):
    """
    Test `ImpressController.check_available` when not on Windows
    """
    # GIVEN: An instance of :class:`ImpressController`
    controller = ImpressController(plugin=mock_plugin)

    # WHEN: `check_available` is called on Windows and `uno_available` is True
    with patch('openlp.plugins.presentations.lib.impresscontroller.uno_available', True), \
            patch.object(controller, 'get_com_servicemanager') as mocked_get_com_servicemanager:
        result = controller.check_available()

        # THEN: `check_available` should return True
        assert mocked_get_com_servicemanager.called is False
        assert result is True


@patch('openlp.plugins.presentations.lib.impresscontroller.is_win', return_value=True)
def test_start_process_on_windows(mocked_is_win, settings, mock_plugin):
    """
    Test that start_process() on Windows starts the process
    """
    # GIVEN: An ImpressController object
    controller = ImpressController(plugin=mock_plugin)
    controller.get_com_servicemanager = MagicMock(return_value=MagicMock())

    # WHEN: start_process() is called
    controller.start_process()

    # THEN: The correct methods should have been called
    controller.get_com_servicemanager.assert_called_once()
    assert controller.manager._FlagAsMethod.call_args_list == [call('Bridge_GetStruct'),
                                                               call('Bridge_GetValueObject')]


@patch('openlp.plugins.presentations.lib.impresscontroller.is_win', return_value=False)
@patch('openlp.plugins.presentations.lib.impresscontroller.get_uno_command', return_value='libreoffice')
@patch('openlp.plugins.presentations.lib.impresscontroller.QtCore.QProcess')
def test_start_process_on_linux(MockQProcess, mocked_get_uno_command, mocked_is_win, settings, mock_plugin):
    """
    Test that start_process() on Linux starts the process
    """
    # GIVEN: An ImpressController object
    mocked_process = MagicMock()
    MockQProcess.return_value = mocked_process
    controller = ImpressController(plugin=mock_plugin)

    # WHEN: start_process() is called
    controller.start_process()

    # THEN: The correct methods should have been called
    mocked_get_uno_command.assert_called_once()
    MockQProcess.assert_called_once()
    assert controller.process is mocked_process
    mocked_process.startDetached.assert_called_once_with('libreoffice')


def test_create_titles_and_notes(doc):
    """
    Test ImpressDocument.create_titles_and_notes
    """
    # GIVEN: mocked PresentationController.save_titles_and_notes with
    # 0 pages and the LibreOffice Document
    doc.save_titles_and_notes = MagicMock()
    doc.document = MagicMock()
    doc.document.getDrawPages.return_value = MagicMock()
    doc.document.getDrawPages().getCount.return_value = 0

    # WHEN reading the titles and notes
    doc.create_titles_and_notes()

    # THEN save_titles_and_notes should have been called with empty arrays
    doc.save_titles_and_notes.assert_called_once_with([], [])

    # GIVEN: reset mock and set it to 2 pages
    doc.save_titles_and_notes.reset_mock()
    doc.document.getDrawPages().getCount.return_value = 2

    # WHEN: a new call to create_titles_and_notes
    doc.create_titles_and_notes()

    # THEN: save_titles_and_notes should have been called once with
    # two arrays of two elements
    # self.doc.save_titles_and_notes.assert_called_once_with(['\n', '\n'], [' ', ' '])
    doc.save_titles_and_notes.assert_called_once_with(['', ''], [' ', ' '])


def test_get_text_from_page_out_of_bound(doc):
    """
    Test ImpressDocument.__get_text_from_page with out-of-bounds index
    """
    # GIVEN: mocked LibreOffice Document with one slide,
    # two notes and three texts
    doc.document = _mock_a_LibreOffice_document(1, 2, 3)

    # WHEN: __get_text_from_page is called with an index of 0x00
    result = doc._ImpressDocument__get_text_from_page(0, TextType.Notes)

    # THEN: the result should be an empty string
    assert result == '', 'Result should be an empty string'

    # WHEN: regardless of the type of text, index 0x00 is out of bounds
    result = doc._ImpressDocument__get_text_from_page(0, TextType.Title)

    # THEN: result should be an empty string
    assert result == '', 'Result should be an empty string'

    # WHEN: when called with 2, it should also be out of bounds
    result = doc._ImpressDocument__get_text_from_page(2, TextType.SlideText)

    # THEN: result should be an empty string ... and, getByIndex should
    # have never been called
    assert result == '', 'Result should be an empty string'
    assert doc.document.getDrawPages().getByIndex.call_count == 0, 'There should be no call to getByIndex'


def test_get_text_from_page_wrong_type(doc):
    """
    Test ImpressDocument.__get_text_from_page with wrong TextType
    """
    # GIVEN: mocked LibreOffice Document with one slide, two notes and
    # three texts
    doc.document = _mock_a_LibreOffice_document(1, 2, 3)

    # WHEN: called with TextType 3
    result = doc._ImpressDocument__get_text_from_page(1, 3)

    # THEN: result should be an empty string
    assert result == '', 'Result should be and empty string'
    assert doc.document.getDrawPages().getByIndex.call_count == 0, 'There should be no call to getByIndex'


def test_get_text_from_page_valid_params(doc):
    """
    Test ImpressDocument.__get_text_from_page with valid parameters
    """
    # GIVEN: mocked LibreOffice Document with one slide,
    # two notes and three texts
    doc.document = _mock_a_LibreOffice_document(1, 2, 3)

    # WHEN: __get_text_from_page is called to get the Notes
    result = doc._ImpressDocument__get_text_from_page(1, TextType.Notes)

    # THEN: result should be 'Note\nNote\n'
    assert result == 'Note\nNote\n', 'Result should be \'Note\\n\' times the count of notes in the page'

    # WHEN: get the Title
    result = doc._ImpressDocument__get_text_from_page(1, TextType.Title)

    # THEN: result should be 'Title\n'
    assert result == 'Title\n', 'Result should be exactly \'Title\\n\''

    # WHEN: get all text
    result = doc._ImpressDocument__get_text_from_page(1, TextType.SlideText)

    # THEN: result should be 'Title\nString\nString\n'
    assert result == 'Title\nString\nString\n', 'Result should be exactly \'Title\\nString\\nString\\n\''


def _mock_a_LibreOffice_document(page_count, note_count, text_count):
    """
    Helper function, creates a mock libreoffice document.

    :param page_count: Number of pages in the document
    :param note_count: Number of note pages in the document
    :param text_count: Number of text pages in the document
    """
    pages = MagicMock()
    page = MagicMock()
    pages.getByIndex.return_value = page
    notes_page = MagicMock()
    notes_page.getCount.return_value = note_count
    shape = MagicMock()
    shape.supportsService.return_value = True
    shape.getString.return_value = 'Note'
    notes_page.getByIndex.return_value = shape
    page.getNotesPage.return_value = notes_page
    page.getCount.return_value = text_count
    page.getByIndex.side_effect = _get_page_shape_side_effect
    pages.getCount.return_value = page_count
    document = MagicMock()
    document.getDrawPages.return_value = pages
    document.getByIndex.return_value = page
    return document


def _get_page_shape_side_effect(*args):
    """
    Helper function.
    """
    page_shape = MagicMock()
    page_shape.supportsService.return_value = True
    if args[0] == 0:
        page_shape.getShapeType.return_value = 'com.sun.star.presentation.TitleTextShape'
        page_shape.getString.return_value = 'Title'
    else:
        page_shape.getString.return_value = 'String'
    return page_shape
