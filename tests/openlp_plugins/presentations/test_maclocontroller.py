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
Functional tests to test the Mac LibreOffice class and related methods.
"""
from unittest.mock import MagicMock, patch, call

import pytest

from openlp.core.common.path import Path
from openlp.core.common.platform import is_macosx
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.presentations.lib.maclocontroller import MacLOController, MacLODocument

from tests.utils.constants import TEST_RESOURCES_PATH

try:
    import Pyro5    # noqa: F401
    has_pyro5 = True
except ImportError:
    has_pyro5 = False

pytestmark = [
    pytest.mark.skipif(not has_pyro5, reason='Pyro5 is not installed, skipping testing the Mac LibreOffice controller'),
    pytest.mark.skipif(not is_macosx(), reason='Not on macOS, skipping testing the Mac LibreOffice controller'),
]
TEST_FILE = Path(TEST_RESOURCES_PATH) / 'presentations' / 'test.odp'

# @pytest.mark.skipif(is_macosx(), reason='Skip on macOS until we can figure out what the problem is')


@pytest.fixture
def controller(registry: Registry, settings: Settings):
    with patch('openlp.plugins.presentations.lib.maclocontroller.MacLOController._start_server'):
        _controller = MacLOController(MagicMock(settings_section='presentations'))
    _controller._client = MagicMock()
    return _controller


@pytest.fixture
def document(controller: MacLOController):
    return MacLODocument(controller, TEST_FILE)


@patch('openlp.plugins.presentations.lib.maclocontroller.MacLOController._start_server')
def test_constructor(mocked_start_server: MagicMock, registry: Registry, settings: Settings):
    """
    Test the Constructor from the MacLOController
    """
    # GIVEN: No presentation controller
    controller = None

    # WHEN: The presentation controller object is created
    controller = MacLOController(plugin=MagicMock(settings_section='presentations'))

    # THEN: The name of the presentation controller should be correct
    assert controller.name == 'maclo', \
        'The name of the presentation controller should be correct'
    assert controller.display_name == 'Impress on macOS', \
        'The display name of the presentation controller should be correct'
    mocked_start_server.assert_called_once_with()


@patch('openlp.plugins.presentations.lib.maclocontroller.MacLOController._start_server')
@patch('openlp.plugins.presentations.lib.maclocontroller.Proxy')
def test_client(MockedProxy: MagicMock, mocked_start_server: MagicMock, registry: Registry, settings: Settings):
    """
    Test the client property of the Controller
    """
    # GIVEN: A controller without a client and a mocked out Pyro
    controller = MacLOController(plugin=MagicMock(settings_section='presentations'))
    mocked_client = MagicMock()
    MockedProxy.return_value = mocked_client
    mocked_client._pyroConnection = None

    # WHEN: the client property is called the first time
    client = controller.client

    # THEN: a client is created
    assert client == mocked_client
    MockedProxy.assert_called_once_with('PYRO:openlp.libreofficeserver@localhost:4310')
    mocked_client._pyroReconnect.assert_called_once_with()


@patch('openlp.plugins.presentations.lib.maclocontroller.MacLOController._start_server')
def test_check_available(mocked_start_server: MagicMock, controller: MacLOController):
    """
    Test the check_available() method
    """
    from openlp.plugins.presentations.lib.maclocontroller import macuno_available

    # GIVEN: A controller
    # WHEN: check_available() is run
    result = controller.check_available()

    # THEN: it should return false
    assert result == macuno_available


@patch('openlp.plugins.presentations.lib.maclocontroller.MacLOController._start_server')
def test_start_process(mocked_start_server: MagicMock, controller: MacLOController):
    """
    Test the start_process() method
    """
    # GIVEN: A controller and a client
    # WHEN: start_process() is called
    controller.start_process()

    # THEN: The client's start_process() should have been called
    controller._client.start_process.assert_called_once_with()


@patch('openlp.plugins.presentations.lib.maclocontroller.MacLOController._start_server')
def test_kill(mocked_start_server: MagicMock, controller: MacLOController):
    """
    Test the kill() method
    """
    # GIVEN: A controller and a client
    controller.server_process = MagicMock()

    # WHEN: start_process() is called
    controller.kill()

    # THEN: The client's start_process() should have been called
    controller._client.shutdown.assert_called_once_with()
    controller.server_process.kill.assert_called_once_with()


@patch('openlp.plugins.presentations.lib.maclocontroller.MacLOController._start_server')
def test_kill_client_already_closed(mocked_start_server: MagicMock, controller: MacLOController):
    """
    Test the kill() method when the client is already closed
    """
    # GIVEN: A controller and a client
    controller._client.shutdown.side_effect = Exception
    controller.server_process = MagicMock()

    # WHEN: start_process() is called
    controller.kill()

    # THEN: The client's start_process() should have been called
    controller._client.shutdown.assert_called_once_with()
    controller.server_process.kill.assert_called_once_with()


@patch('openlp.plugins.presentations.lib.maclocontroller.ScreenList')
def test_load_presentation_cannot_load(MockedScreenList: MagicMock, controller: MacLOController,
                                       document: MacLODocument):
    """
    Test the load_presentation() method when the server can't load the presentation
    """
    # GIVEN: A document and a mocked client
    mocked_screen_list = MagicMock()
    MockedScreenList.return_value = mocked_screen_list
    mocked_screen_list.current.number = 0
    controller._client.load_presentation.return_value = False

    # WHEN: load_presentation() is called
    result = document.load_presentation()

    # THEN: Stuff should work right
    controller._client.load_presentation.assert_called_once_with(str(TEST_FILE), 1)
    assert result is False


@patch('openlp.plugins.presentations.lib.maclocontroller.ScreenList')
def test_load_presentation(MockedScreenList: MagicMock, controller: MacLOController, document: MacLODocument):
    """
    Test the load_presentation() method
    """
    # GIVEN: A document and a mocked client
    mocked_screen_list = MagicMock()
    MockedScreenList.return_value = mocked_screen_list
    mocked_screen_list.current.number = 0
    controller._client.load_presentation.return_value = True

    # WHEN: load_presentation() is called
    with patch.object(document, 'create_thumbnails') as mocked_create_thumbnails, \
            patch.object(document, 'create_titles_and_notes') as mocked_create_titles_and_notes:
        result = document.load_presentation()

    # THEN: Stuff should work right
    controller._client.load_presentation.assert_called_once_with(str(TEST_FILE), 1)
    mocked_create_thumbnails.assert_called_once_with()
    mocked_create_titles_and_notes.assert_called_once_with()
    assert result is True


def test_create_thumbnails_already_exist(controller: MacLOController, document: MacLODocument):
    """
    Test the create_thumbnails() method when thumbnails already exist
    """
    # GIVEN: thumbnails that exist and a mocked client
    document.check_thumbnails = MagicMock(return_value=True)

    # WHEN: create_thumbnails() is called
    document.create_thumbnails()

    # THEN: The method should exit early
    assert controller._client.extract_thumbnails.call_count == 0


@patch('openlp.plugins.presentations.lib.maclocontroller.delete_file')
def test_create_thumbnails(mocked_delete_file: MagicMock, controller: MacLOController, document: MacLODocument):
    """
    Test the create_thumbnails() method
    """
    # GIVEN: thumbnails that don't exist and a mocked client
    document.check_thumbnails = MagicMock(return_value=False)
    controller._client.extract_thumbnails.return_value = ['thumb1.png', 'thumb2.png']

    # WHEN: create_thumbnails() is called
    with patch.object(document, 'convert_thumbnail') as mocked_convert_thumbnail, \
            patch.object(document, 'get_temp_folder') as mocked_get_temp_folder:
        mocked_get_temp_folder.return_value = 'temp'
        document.create_thumbnails()

    # THEN: The method should complete successfully
    controller._client.extract_thumbnails.assert_called_once_with('temp')
    assert mocked_convert_thumbnail.call_args_list == [
        call(Path('thumb1.png'), 1), call(Path('thumb2.png'), 2)]
    assert mocked_delete_file.call_args_list == [call(Path('thumb1.png')), call(Path('thumb2.png'))]


def test_create_titles_and_notes(controller: MacLOController, document: MacLODocument):
    """
    Test create_titles_and_notes() method
    """
    # GIVEN: mocked client and mocked save_titles_and_notes() method
    controller._client.get_titles_and_notes.return_value = ('OpenLP', 'This is a note')

    # WHEN: create_titles_and_notes() is called
    with patch.object(document, 'save_titles_and_notes') as mocked_save_titles_and_notes:
        document.create_titles_and_notes()

    # THEN save_titles_and_notes should have been called
    controller._client.get_titles_and_notes.assert_called_once_with()
    mocked_save_titles_and_notes.assert_called_once_with('OpenLP', 'This is a note')


def test_close_presentation(controller: MacLOController, document: MacLODocument):
    """
    Test the close_presentation() method
    """
    # GIVEN: A mocked client and mocked remove_doc() method
    # WHEN: close_presentation() is called
    with patch.object(controller, 'remove_doc') as mocked_remove_doc:
        document.close_presentation()

    # THEN: The presentation should have been closed
    controller._client.close_presentation.assert_called_once_with()
    mocked_remove_doc.assert_called_once_with(document)


def test_is_loaded(controller: MacLOController, document: MacLODocument):
    """
    Test the is_loaded() method
    """
    # GIVEN: A mocked client
    controller._client.is_loaded.return_value = True

    # WHEN: is_loaded() is called
    result = document.is_loaded()

    # THEN: Then the result should be correct
    assert result is True


def test_is_active(controller: MacLOController, document: MacLODocument):
    """
    Test the is_active() method
    """
    # GIVEN: A mocked client
    controller._client.is_active.return_value = True

    # WHEN: is_active() is called
    result = document.is_active()

    # THEN: Then the result should be correct
    assert result is True


def test_unblank_screen(controller: MacLOController, document: MacLODocument):
    """
    Test the unblank_screen() method
    """
    # GIVEN: A mocked client
    controller._client.unblank_screen.return_value = True

    # WHEN: unblank_screen() is called
    result = document.unblank_screen()

    # THEN: Then the result should be correct
    controller._client.unblank_screen.assert_called_once_with()
    assert result is True


def test_blank_screen(controller: MacLOController, document: MacLODocument):
    """
    Test the blank_screen() method
    """
    # GIVEN: A mocked client
    controller._client.blank_screen.return_value = True

    # WHEN: blank_screen() is called
    document.blank_screen()

    # THEN: Then the result should be correct
    controller._client.blank_screen.assert_called_once_with()


def test_is_blank(controller: MacLOController, document: MacLODocument):
    """
    Test the is_blank() method
    """
    # GIVEN: A mocked client
    controller._client.is_blank.return_value = True

    # WHEN: is_blank() is called
    result = document.is_blank()

    # THEN: Then the result should be correct
    assert result is True


def test_stop_presentation(controller: MacLOController, document: MacLODocument):
    """
    Test the stop_presentation() method
    """
    # GIVEN: A mocked client
    controller._client.stop_presentation.return_value = True

    # WHEN: stop_presentation() is called
    document.stop_presentation()

    # THEN: Then the result should be correct
    controller._client.stop_presentation.assert_called_once_with()


@patch('openlp.plugins.presentations.lib.maclocontroller.ScreenList')
@patch('openlp.plugins.presentations.lib.maclocontroller.Registry')
def test_start_presentation(MockedRegistry: MagicMock, MockedScreenList: MagicMock, controller: MacLOController,
                            document: MacLODocument):
    """
    Test the start_presentation() method
    """
    # GIVEN: a mocked client, and multiple screens
    mocked_screen_list = MagicMock()
    mocked_screen_list.__len__.return_value = 2
    mocked_registry = MagicMock()
    mocked_main_window = MagicMock()
    MockedScreenList.return_value = mocked_screen_list
    MockedRegistry.return_value = mocked_registry
    mocked_screen_list.screen_list = [0, 1]
    mocked_registry.get.return_value = mocked_main_window

    # WHEN: start_presentation() is called
    document.start_presentation()

    # THEN: The presentation should be started
    controller._client.start_presentation.assert_called_once_with()
    mocked_registry.get.assert_called_once_with('main_window')
    mocked_main_window.activateWindow.assert_called_once_with()


def test_get_slide_number(controller: MacLOController, document: MacLODocument):
    """
    Test the get_slide_number() method
    """
    # GIVEN: A mocked client
    controller._client.get_slide_number.return_value = 5

    # WHEN: get_slide_number() is called
    result = document.get_slide_number()

    # THEN: Then the result should be correct
    assert result == 5


def test_get_slide_count(controller: MacLOController, document: MacLODocument):
    """
    Test the get_slide_count() method
    """
    # GIVEN: A mocked client
    controller._client.get_slide_count.return_value = 8

    # WHEN: get_slide_count() is called
    result = document.get_slide_count()

    # THEN: Then the result should be correct
    assert result == 8


def test_goto_slide(controller: MacLOController, document: MacLODocument):
    """
    Test the goto_slide() method
    """
    # GIVEN: A mocked client
    # WHEN: goto_slide() is called
    document.goto_slide(3)

    # THEN: Then the result should be correct
    controller._client.goto_slide.assert_called_once_with(3)


def test_next_step(controller: MacLOController, document: MacLODocument):
    """
    Test the next_step() method
    """
    # GIVEN: A mocked client
    # WHEN: next_step() is called
    document.next_step()

    # THEN: Then the result should be correct
    controller._client.next_step.assert_called_once_with()


def test_previous_step(controller: MacLOController, document: MacLODocument):
    """
    Test the previous_step() method
    """
    # GIVEN: A mocked client
    # WHEN: previous_step() is called
    document.previous_step()

    # THEN: Then the result should be correct
    controller._client.previous_step.assert_called_once_with()


def test_get_slide_text(controller: MacLOController, document: MacLODocument):
    """
    Test the get_slide_text() method
    """
    # GIVEN: A mocked client
    controller._client.get_slide_text.return_value = 'Some slide text'

    # WHEN: get_slide_text() is called
    result = document.get_slide_text(1)

    # THEN: Then the result should be correct
    controller._client.get_slide_text.assert_called_once_with(1)
    assert result == 'Some slide text'


def test_get_slide_notes(controller: MacLOController, document: MacLODocument):
    """
    Test the get_slide_notes() method
    """
    # GIVEN: A mocked client
    controller._client.get_slide_notes.return_value = 'This is a note'

    # WHEN: get_slide_notes() is called
    result = document.get_slide_notes(2)

    # THEN: Then the result should be correct
    controller._client.get_slide_notes.assert_called_once_with(2)
    assert result == 'This is a note'
