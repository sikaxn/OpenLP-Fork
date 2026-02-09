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
Functional tests to test the PresentationController and PresentationDocument
classes and related methods.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from openlp.plugins.presentations.lib.presentationcontroller import PresentationController, PresentationDocument, \
    PresentationList


FOLDER_TO_PATCH = 'openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument.get_thumbnail_folder'


@pytest.fixture()
def get_thumbnail_folder(settings):
    gtf = patch('openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument.get_thumbnail_folder',
                return_value=Path())
    yield gtf.start()
    gtf.stop()


@pytest.fixture()
def create_paths(settings):
    c_paths = patch('openlp.plugins.presentations.lib.presentationcontroller.create_paths')
    yield c_paths.start()
    c_paths.stop()


@pytest.fixture()
def setup(settings):
    s_up = patch('openlp.plugins.presentations.lib.presentationcontroller.PresentationDocument._setup')
    yield s_up.start()
    s_up.stop()


@pytest.fixture()
def presentation(settings, get_thumbnail_folder):
    mocked_plugin = MagicMock()
    mocked_plugin.settings_section = 'presentations'
    return PresentationController(mocked_plugin)


@pytest.fixture()
def document(presentation):
    return PresentationDocument(presentation, Path(''))


def test_constructor(presentation):
    """
    Test the Constructor
    """
    # GIVEN: A mocked plugin

    # WHEN: The PresentationController is created

    # THEN: The name of the presentation controller should be correct
    assert 'PresentationController' == presentation.name, \
        'The name of the presentation controller should be correct'


def test_save_titles_and_notes(document):
    """
    Test PresentationDocument.save_titles_and_notes method with two valid lists
    """
    # GIVEN: two lists of length==2 and a mocked open and get_thumbnail_folder
    with patch('openlp.plugins.presentations.lib.presentationcontroller.Path.write_text') as mocked_write_text, \
            patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
        titles = ['uno', 'dos']
        notes = ['one', 'two']

        # WHEN: calling save_titles_and_notes
        mocked_get_thumbnail_folder.return_value = Path('test')
        document.save_titles_and_notes(titles, notes)

        # THEN: the last call to open should have been for slideNotes2.txt
        assert mocked_write_text.call_count == 3, 'There should be exactly three files written'
        mocked_write_text.assert_has_calls([call('uno\ndos', encoding='utf-8'), call('one', encoding='utf-8'),
                                            call('two', encoding='utf-8')])


def test_save_titles_and_notes_with_none(document):
    """
    Test PresentationDocument.save_titles_and_notes method with no data
    """
    # GIVEN: None and an empty list and a mocked open and get_thumbnail_folder
    with patch('builtins.open') as mocked_open, patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
        titles = None
        notes = None

        # WHEN: calling save_titles_and_notes
        mocked_get_thumbnail_folder.return_value = 'test'
        document.save_titles_and_notes(titles, notes)

        # THEN: No file should have been created
        assert mocked_open.call_count == 0, 'No file should be created'


def test_get_titles_and_notes(document):
    """
    Test PresentationDocument.get_titles_and_notes method
    """
    # GIVEN: A mocked open, get_thumbnail_folder and exists

    with patch('openlp.plugins.presentations.lib.presentationcontroller.Path.read_text',
               return_value='uno\ndos\n') as mocked_read_text, \
            patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder, \
            patch('openlp.plugins.presentations.lib.presentationcontroller.Path.exists') as mocked_exists:
        mocked_get_thumbnail_folder.return_value = Path('test')
        mocked_exists.return_value = True

        # WHEN: calling get_titles_and_notes
        result_titles, result_notes = document.get_titles_and_notes()

        # THEN: it should return two items for the titles and two empty strings for the notes
        assert type(result_titles) is list, 'result_titles should be of type list'
        assert len(result_titles) == 2, 'There should be two items in the titles'
        assert type(result_notes) is list, 'result_notes should be of type list'
        assert len(result_notes) == 2, 'There should be two items in the notes'
        assert mocked_read_text.call_count == 3, 'Three files should be read'


def test_get_titles_and_notes_with_file_not_found(document):
    """
    Test PresentationDocument.get_titles_and_notes method with file not found
    """
    # GIVEN: A mocked open, get_thumbnail_folder and exists
    with patch('openlp.plugins.presentations.lib.presentationcontroller.Path.read_text') as mocked_read_text, \
            patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
        mocked_read_text.side_effect = FileNotFoundError()
        mocked_get_thumbnail_folder.return_value = Path('test')

        # WHEN: calling get_titles_and_notes
        result_titles, result_notes = document.get_titles_and_notes()

        # THEN: it should return two empty lists
        assert isinstance(result_titles, list), 'result_titles should be of type list'
        assert len(result_titles) == 0, 'there be no titles'
        assert isinstance(result_notes, list), 'result_notes should be a list'
        assert len(result_notes) == 0, 'but the list should be empty'


def test_get_titles_and_notes_with_file_error(document):
    """
    Test PresentationDocument.get_titles_and_notes method with file errors
    """
    # GIVEN: A mocked open, get_thumbnail_folder and exists
    with patch('openlp.plugins.presentations.lib.presentationcontroller.Path.read_text') as mocked_read_text, \
            patch(FOLDER_TO_PATCH) as mocked_get_thumbnail_folder:
        mocked_read_text.side_effect = OSError()
        mocked_get_thumbnail_folder.return_value = Path('test')

        # WHEN: calling get_titles_and_notes
        result_titles, result_notes = document.get_titles_and_notes()

        # THEN: it should return two empty lists
        assert type(result_titles) is list, 'result_titles should be a list'


def test_initialise_presentation_document(setup):
    """
    Test the PresentationDocument __init__ method when initialising the PresentationDocument Class
    """
    # GIVEN: A mocked setup method and mocked controller
    # WHEN: Creating an instance of PresentationDocument
    PresentationDocument(MagicMock(), 'Name')

    # THEN: PresentationDocument._setup should have been called with the argument 'Name'
    setup.assert_called_once_with('Name')


def test_presentation_document_setup(create_paths, get_thumbnail_folder):
    """
    Test the PresentationDocument _setup method when initialising the PresentationDocument Class
    """
    # GIVEN: A mocked controller, patched create_paths and get_thumbnail_folder methods
    get_thumbnail_folder.return_value = Path('returned/path/')

    # WHEN: Creating an instance of PresentationDocument
    PresentationDocument(MagicMock(), 'Name')

    # THEN: create_paths should have been called with 'returned/path/'
    create_paths.assert_called_once_with(Path('returned', 'path/'))


def test_load_presentation(get_thumbnail_folder):
    """
    Test the PresentationDocument.load_presentation method.
    """

    # GIVEN: An instance of PresentationDocument
    instance = PresentationDocument(MagicMock(), 'Name')

    # WHEN: Calling load_presentation()
    result = instance.load_presentation()

    # THEN: load_presentation should return false
    assert result is False, "PresentationDocument.load_presentation should return false."


def test_presentation_list_is_singleton():
    """
    Test PresentationList is a singleton class
    """
    # GIVEN: a PresentationList
    presentation_list = PresentationList()

    # WHEN: I try to create another instance
    presentation_list_2 = PresentationList()

    # THEN: I get the same instance returned
    assert presentation_list_2 is presentation_list


def test_presentation_list_add_and_retrieve(document):
    """
    Test adding a presentation document and later retrieving it
    """
    # GIVEN: a fixture with a mocked document which is added to the PresentationList
    PresentationList().add(document, "unique id")

    # WHEN: I retrieve the presentation document
    retrieved_presentation = PresentationList().get_presentation_by_id("unique id")

    # THEN: I get the same instance returned
    retrieved_presentation is document


def test_presentation_list_remove(document):
    """
    Test removing a presentation document from the list
    """
    # GIVEN: a fixture with a mocked document which is added to the PresentationList
    PresentationList().add(document, "unique id")

    # WHEN: I remove the presentation document
    PresentationList().remove("unique id")

    # THEN: That document shouldn't be in the list
    PresentationList().get_presentation_by_id("unique id") is None
