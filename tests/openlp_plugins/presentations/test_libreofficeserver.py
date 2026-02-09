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
Functional tests to test the LibreOffice Pyro server
"""
from unittest.mock import MagicMock, patch, call

import pytest

from openlp.core.common.platform import is_macosx

try:
    import Pyro5    # noqa: F401
    has_pyro5 = True
except ImportError:
    has_pyro5 = False

if has_pyro5:
    from openlp.plugins.presentations.lib.libreofficeserver import LibreOfficeServer, TextType, main


pytestmark = [
    pytest.mark.skipif(not has_pyro5, reason='Pyro5 is not installed, skipping testing the LibreOffice server'),
    pytest.mark.skipif(not is_macosx(), reason='Not on macOS, skipping testing the LibreOffice server')
]


def test_constructor():
    """
    Test the Constructor from the server
    """
    # GIVEN: No server
    # WHEN: The server object is created
    server = LibreOfficeServer()

    # THEN: The server should have been set up correctly
    assert server._control is None
    # assert server._desktop is None
    assert server._document is None
    assert server._presentation is None
    assert server._process is None


@patch('openlp.plugins.presentations.lib.libreofficeserver.Popen')
def test_start_process(MockedPopen):
    """
    Test that the correct command is issued to run LibreOffice
    """
    # GIVEN: A LOServer
    mocked_process = MagicMock()
    MockedPopen.return_value = mocked_process
    server = LibreOfficeServer()

    # WHEN: The start_process() method is run
    server.start_process()

    # THEN: The correct command line should run and the process should have started
    MockedPopen.assert_called_with([
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
        '--nologo',
        '--norestore',
        '--minimized',
        '--nodefault',
        '--nofirststartwizard',
        '--accept=pipe,name=openlp_maclo;urp;StarOffice.ServiceManager'
    ])
    assert server._process is mocked_process


@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
def test_desktop_already_has_desktop(mocked_uno):
    """
    Test that setup_desktop() exits early when there's already a desktop
    """
    # GIVEN: A LibreOfficeServer instance
    server = LibreOfficeServer()
    server._desktop = MagicMock()

    # WHEN: the desktop property is called
    desktop = server.desktop

    # THEN: setup_desktop() exits early
    assert desktop is server._desktop
    assert server._manager is None


@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
def test_desktop_exception(mocked_uno):
    """
    Test that setting up the desktop works correctly when an exception occurs
    """
    # GIVEN: A LibreOfficeServer instance
    server = LibreOfficeServer()
    mocked_context = MagicMock()
    mocked_resolver = MagicMock()
    mocked_uno_instance = MagicMock()
    MockedServiceManager = MagicMock()
    mocked_uno.getComponentContext.return_value = mocked_context
    mocked_context.ServiceManager.createInstanceWithContext.return_value = mocked_resolver
    mocked_resolver.resolve.side_effect = [Exception, mocked_uno_instance]
    mocked_uno_instance.ServiceManager = MockedServiceManager
    MockedServiceManager.createInstanceWithContext.side_effect = Exception()

    # WHEN: the desktop property is called
    server.desktop

    # THEN: A desktop object was created
    mocked_uno.getComponentContext.assert_called_once_with()
    mocked_context.ServiceManager.createInstanceWithContext.assert_called_once_with(
        'com.sun.star.bridge.UnoUrlResolver', mocked_context)
    expected_calls = [
        call('uno:pipe,name=openlp_maclo;urp;StarOffice.ComponentContext'),
        call('uno:pipe,name=openlp_maclo;urp;StarOffice.ComponentContext')
    ]
    assert mocked_resolver.resolve.call_args_list == expected_calls
    MockedServiceManager.createInstanceWithContext.assert_called_once_with(
        'com.sun.star.frame.Desktop', mocked_uno_instance)
    assert server._manager is MockedServiceManager
    assert server._desktop is None


@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
def test_desktop(mocked_uno):
    """
    Test that setting up the desktop works correctly
    """
    # GIVEN: A LibreOfficeServer instance
    server = LibreOfficeServer()
    mocked_context = MagicMock()
    mocked_resolver = MagicMock()
    mocked_uno_instance = MagicMock()
    MockedServiceManager = MagicMock()
    mocked_desktop = MagicMock()
    mocked_uno.getComponentContext.return_value = mocked_context
    mocked_context.ServiceManager.createInstanceWithContext.return_value = mocked_resolver
    mocked_resolver.resolve.side_effect = [Exception, mocked_uno_instance]
    mocked_uno_instance.ServiceManager = MockedServiceManager
    MockedServiceManager.createInstanceWithContext.return_value = mocked_desktop

    # WHEN: the desktop property is called
    server.desktop

    # THEN: A desktop object was created
    mocked_uno.getComponentContext.assert_called_once_with()
    mocked_context.ServiceManager.createInstanceWithContext.assert_called_once_with(
        'com.sun.star.bridge.UnoUrlResolver', mocked_context)
    expected_calls = [
        call('uno:pipe,name=openlp_maclo;urp;StarOffice.ComponentContext'),
        call('uno:pipe,name=openlp_maclo;urp;StarOffice.ComponentContext')
    ]
    assert mocked_resolver.resolve.call_args_list == expected_calls
    MockedServiceManager.createInstanceWithContext.assert_called_once_with(
        'com.sun.star.frame.Desktop', mocked_uno_instance)
    assert server._manager is MockedServiceManager
    assert server._desktop is mocked_desktop


@patch('openlp.plugins.presentations.lib.libreofficeserver.PropertyValue')
def test_create_property(MockedPropertyValue):
    """
    Test that the _create_property() method works correctly
    """
    # GIVEN: A server amnd property to set
    server = LibreOfficeServer()
    name = 'Hidden'
    value = True

    # WHEN: The _create_property() method is called
    prop = server._create_property(name, value)

    # THEN: The property should have the correct attributes
    assert prop.Name == name
    assert prop.Value == value


def test_get_text_from_page_slide_text():
    """
    Test that the _get_text_from_page() method gives us nothing for slide text
    """
    # GIVEN: A LibreOfficeServer object and some mocked objects
    text_type = TextType.SlideText
    slide_no = 1
    server = LibreOfficeServer()
    server._document = MagicMock()
    mocked_pages = MagicMock()
    mocked_page = MagicMock()
    mocked_shape = MagicMock()
    server._document.getDrawPages.return_value = mocked_pages
    mocked_pages.getCount.return_value = 1
    mocked_pages.getByIndex.return_value = mocked_page
    mocked_page.getByIndex.return_value = mocked_shape
    mocked_shape.getShapeType.return_value = 'com.sun.star.presentation.TitleTextShape'
    mocked_shape.supportsService.return_value = True
    mocked_shape.getString.return_value = 'Page Text'

    # WHEN: _get_text_from_page() is run for slide text
    text = server._get_text_from_page(slide_no, text_type)

    # THE: The text is correct
    assert text == 'Page Text\n'


def test_get_text_from_page_title():
    """
    Test that the _get_text_from_page() method gives us the text from the titles
    """
    # GIVEN: A LibreOfficeServer object and some mocked objects
    text_type = TextType.Title
    slide_no = 1
    server = LibreOfficeServer()
    server._document = MagicMock()
    mocked_pages = MagicMock()
    mocked_page = MagicMock()
    mocked_shape = MagicMock()
    server._document.getDrawPages.return_value = mocked_pages
    mocked_pages.getCount.return_value = 1
    mocked_pages.getByIndex.return_value = mocked_page
    mocked_page.getByIndex.return_value = mocked_shape
    mocked_shape.getShapeType.return_value = 'com.sun.star.presentation.TitleTextShape'
    mocked_shape.supportsService.return_value = True
    mocked_shape.getString.return_value = 'Page Title'

    # WHEN: _get_text_from_page() is run for titles
    text = server._get_text_from_page(slide_no, text_type)

    # THEN: The text should be correct
    assert text == 'Page Title\n'


def test_get_text_from_page_notes():
    """
    Test that the _get_text_from_page() method gives us the text from the notes
    """
    # GIVEN: A LibreOfficeServer object and some mocked objects
    text_type = TextType.Notes
    slide_no = 1
    server = LibreOfficeServer()
    server._document = MagicMock()
    mocked_pages = MagicMock()
    mocked_page = MagicMock()
    mocked_notes_page = MagicMock()
    mocked_shape = MagicMock()
    server._document.getDrawPages.return_value = mocked_pages
    mocked_pages.getCount.return_value = 1
    mocked_pages.getByIndex.return_value = mocked_page
    mocked_page.getNotesPage.return_value = mocked_notes_page
    mocked_notes_page.getByIndex.return_value = mocked_shape
    mocked_shape.getShapeType.return_value = 'com.sun.star.presentation.TitleTextShape'
    mocked_shape.supportsService.return_value = True
    mocked_shape.getString.return_value = 'Page Notes'

    # WHEN: _get_text_from_page() is run for titles
    text = server._get_text_from_page(slide_no, text_type)

    # THEN: The text should be correct
    assert text == 'Page Notes\n'


def test_shutdown_other_docs():
    """
    Test the shutdown method while other documents are open in LibreOffice
    """
    def close_docs():
        server._docs = []

    # GIVEN: An up an running LibreOfficeServer
    server = LibreOfficeServer()
    mocked_doc = MagicMock()
    mocked_desktop = MagicMock()
    mocked_docs = MagicMock()
    mocked_list = MagicMock()
    mocked_element_doc = MagicMock()
    server._docs = [mocked_doc]
    server._desktop = mocked_desktop
    server._process = MagicMock()
    mocked_doc.close_presentation.side_effect = close_docs
    mocked_desktop.getComponents.return_value = mocked_docs
    mocked_docs.hasElements.return_value = True
    mocked_docs.createEnumeration.return_value = mocked_list
    mocked_list.hasMoreElements.side_effect = [True, False]
    mocked_list.nextElement.return_value = mocked_element_doc
    mocked_element_doc.getImplementationName.side_effect = [
        'org.openlp.Nothing',
        'com.sun.star.comp.framework.BackingComp'
    ]

    # WHEN: shutdown() is called
    server.shutdown()

    # THEN: The right methods are called and everything works
    mocked_doc.close_presentation.assert_called_once_with()
    mocked_desktop.getComponents.assert_called_once_with()
    mocked_docs.hasElements.assert_called_once_with()
    mocked_docs.createEnumeration.assert_called_once_with()
    assert mocked_list.hasMoreElements.call_count == 2
    mocked_list.nextElement.assert_called_once_with()
    mocked_element_doc.getImplementationName.assert_called_once_with()
    assert mocked_desktop.terminate.call_count == 0
    assert server._process.kill.call_count == 0


def test_shutdown():
    """
    Test the shutdown method
    """
    def close_docs():
        server._docs = []

    # GIVEN: An up an running LibreOfficeServer
    server = LibreOfficeServer()
    mocked_doc = MagicMock()
    mocked_desktop = MagicMock()
    mocked_docs = MagicMock()
    mocked_list = MagicMock()
    mocked_element_doc = MagicMock()
    server._docs = [mocked_doc]
    server._desktop = mocked_desktop
    server._process = MagicMock()
    mocked_doc.close_presentation.side_effect = close_docs
    mocked_desktop.getComponents.return_value = mocked_docs
    mocked_docs.hasElements.return_value = True
    mocked_docs.createEnumeration.return_value = mocked_list
    mocked_list.hasMoreElements.side_effect = [True, False]
    mocked_list.nextElement.return_value = mocked_element_doc
    mocked_element_doc.getImplementationName.return_value = 'com.sun.star.comp.framework.BackingComp'

    # WHEN: shutdown() is called
    server.shutdown()

    # THEN: The right methods are called and everything works
    mocked_doc.close_presentation.assert_called_once_with()
    mocked_desktop.getComponents.assert_called_once_with()
    mocked_docs.hasElements.assert_called_once_with()
    mocked_docs.createEnumeration.assert_called_once_with()
    assert mocked_list.hasMoreElements.call_count == 2
    mocked_list.nextElement.assert_called_once_with()
    mocked_element_doc.getImplementationName.assert_called_once_with()
    mocked_desktop.terminate.assert_called_once_with()
    server._process.kill.assert_called_once_with()


@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
def test_load_presentation_exception(mocked_uno):
    """
    Test the load_presentation() method when an exception occurs
    """
    # GIVEN: A LibreOfficeServer object
    presentation_file = '/path/to/presentation.odp'
    screen_number = 1
    server = LibreOfficeServer()
    mocked_desktop = MagicMock()
    mocked_uno.systemPathToFileUrl.side_effect = lambda x: x
    server._desktop = mocked_desktop
    mocked_desktop.loadComponentFromURL.side_effect = Exception()

    # WHEN: load_presentation() is called
    with patch.object(server, '_create_property') as mocked_create_property:
        mocked_create_property.side_effect = lambda x, y: {x: y}
        result = server.load_presentation(presentation_file, screen_number)

    # THEN: A presentation is loaded
    assert result is False


@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
def test_load_presentation(mocked_uno):
    """
    Test the load_presentation() method
    """
    # GIVEN: A LibreOfficeServer object
    presentation_file = '/path/to/presentation.odp'
    screen_number = 1
    server = LibreOfficeServer()
    mocked_desktop = MagicMock()
    mocked_document = MagicMock()
    mocked_presentation = MagicMock()
    mocked_uno.systemPathToFileUrl.side_effect = lambda x: x
    server._desktop = mocked_desktop
    mocked_desktop.loadComponentFromURL.return_value = mocked_document
    mocked_document.getPresentation.return_value = mocked_presentation

    # WHEN: load_presentation() is called
    with patch.object(server, '_create_property') as mocked_create_property:
        mocked_create_property.side_effect = lambda x, y: {x: y}
        result = server.load_presentation(presentation_file, screen_number)

    # THEN: A presentation is loaded
    assert result is True
    mocked_uno.systemPathToFileUrl.assert_called_once_with(presentation_file)
    mocked_create_property.assert_called_once_with('Hidden', True)
    mocked_desktop.loadComponentFromURL.assert_called_once_with(
        presentation_file, '_blank', 0, ({'Hidden': True},))
    assert server._document is mocked_document
    mocked_document.getPresentation.assert_called_once_with()
    assert server._presentation is mocked_presentation
    assert server._presentation.Display == screen_number
    assert server._control is None


@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
def test_extract_thumbnails_no_pages(mocked_uno):
    """
    Test the extract_thumbnails() method when there are no pages
    """
    # GIVEN: A LibreOfficeServer instance
    temp_folder = '/tmp'
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    server._document = mocked_document
    mocked_uno.systemPathToFileUrl.side_effect = lambda x: x
    mocked_document.getDrawPages.return_value = None

    # WHEN: The extract_thumbnails() method is called
    with patch.object(server, '_create_property') as mocked_create_property:
        mocked_create_property.side_effect = lambda x, y: {x: y}
        thumbnails = server.extract_thumbnails(temp_folder)

    # THEN: Thumbnails have been extracted
    mocked_uno.systemPathToFileUrl.assert_called_once_with(temp_folder)
    mocked_create_property.assert_called_once_with('FilterName', 'impress_png_Export')
    mocked_document.getDrawPages.assert_called_once_with()
    assert thumbnails == []


@patch('openlp.plugins.presentations.lib.libreofficeserver.uno')
@patch('openlp.plugins.presentations.lib.libreofficeserver.os')
def test_extract_thumbnails(mocked_os, mocked_uno):
    """
    Test the extract_thumbnails() method
    """
    # GIVEN: A LibreOfficeServer instance
    temp_folder = '/tmp'
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    mocked_pages = MagicMock()
    mocked_page_1 = MagicMock()
    mocked_page_2 = MagicMock()
    mocked_controller = MagicMock()
    server._document = mocked_document
    mocked_uno.systemPathToFileUrl.side_effect = lambda x: x
    mocked_document.getDrawPages.return_value = mocked_pages
    mocked_os.path.isdir.return_value = False
    mocked_pages.getCount.return_value = 2
    mocked_pages.getByIndex.side_effect = [mocked_page_1, mocked_page_2]
    mocked_document.getCurrentController.return_value = mocked_controller
    mocked_os.path.join.side_effect = lambda *x: '/'.join(x)

    # WHEN: The extract_thumbnails() method is called
    with patch.object(server, '_create_property') as mocked_create_property:
        mocked_create_property.side_effect = lambda x, y: {x: y}
        thumbnails = server.extract_thumbnails(temp_folder)

    # THEN: Thumbnails have been extracted
    mocked_uno.systemPathToFileUrl.assert_called_once_with(temp_folder)
    mocked_create_property.assert_called_once_with('FilterName', 'impress_png_Export')
    mocked_document.getDrawPages.assert_called_once_with()
    mocked_pages.getCount.assert_called_once_with()
    assert mocked_pages.getByIndex.call_args_list == [call(0), call(1)]
    assert mocked_controller.setCurrentPage.call_args_list == \
        [call(mocked_page_1), call(mocked_page_2)]
    assert mocked_document.storeToURL.call_args_list == \
        [call('/tmp/1.png', ({'FilterName': 'impress_png_Export'},)),
         call('/tmp/2.png', ({'FilterName': 'impress_png_Export'},))]
    assert thumbnails == ['/tmp/1.png', '/tmp/2.png']


def test_get_titles_and_notes():
    """
    Test the get_titles_and_notes() method
    """
    # GIVEN: A LibreOfficeServer object and a bunch of mocks
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    mocked_pages = MagicMock()
    server._document = mocked_document
    mocked_document.getDrawPages.return_value = mocked_pages
    mocked_pages.getCount.return_value = 2

    # WHEN: get_titles_and_notes() is called
    with patch.object(server, '_get_text_from_page') as mocked_get_text_from_page:
        mocked_get_text_from_page.side_effect = [
            'OpenLP on Mac OS X',
            '',
            '',
            'Installing is a drag-and-drop affair'
        ]
        titles, notes = server.get_titles_and_notes()

    # THEN: The right calls are made and the right stuff returned
    mocked_document.getDrawPages.assert_called_once_with()
    mocked_pages.getCount.assert_called_once_with()
    assert mocked_get_text_from_page.call_count == 4
    expected_calls = [
        call(1, TextType.Title), call(1, TextType.Notes),
        call(2, TextType.Title), call(2, TextType.Notes),
    ]
    assert mocked_get_text_from_page.call_args_list == expected_calls
    assert titles == ['OpenLP on Mac OS X\n', '\n'], titles
    assert notes == [' ', 'Installing is a drag-and-drop affair'], notes


def test_close_presentation():
    """
    Test that closing the presentation cleans things up correctly
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    mocked_presentation = MagicMock()
    server._document = mocked_document
    server._presentation = mocked_presentation

    # WHEN: close_presentation() is called
    server.close_presentation()

    # THEN: The presentation and document should be closed
    mocked_presentation.end.assert_called_once_with()
    mocked_document.dispose.assert_called_once_with()
    assert server._document is None
    assert server._presentation is None


def test_is_loaded_no_objects():
    """
    Test the is_loaded() method when there's no document or presentation
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()

    # WHEN: The is_loaded() method is called
    result = server.is_loaded()

    # THEN: The result should be false
    assert result is False


def test_is_loaded_no_presentation():
    """
    Test the is_loaded() method when there's no presentation
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    server._document = mocked_document
    server._presentation = MagicMock()
    mocked_document.getPresentation.return_value = None

    # WHEN: The is_loaded() method is called
    result = server.is_loaded()

    # THEN: The result should be false
    assert result is False
    mocked_document.getPresentation.assert_called_once_with()


def test_is_loaded_exception():
    """
    Test the is_loaded() method when an exception is thrown
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    server._document = mocked_document
    server._presentation = MagicMock()
    mocked_document.getPresentation.side_effect = Exception()

    # WHEN: The is_loaded() method is called
    result = server.is_loaded()

    # THEN: The result should be false
    assert result is False
    mocked_document.getPresentation.assert_called_once_with()


def test_is_loaded():
    """
    Test the is_loaded() method
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    mocked_presentation = MagicMock()
    server._document = mocked_document
    server._presentation = mocked_presentation
    mocked_document.getPresentation.return_value = mocked_presentation

    # WHEN: The is_loaded() method is called
    result = server.is_loaded()

    # THEN: The result should be false
    assert result is True
    mocked_document.getPresentation.assert_called_once_with()


def test_is_active_not_loaded():
    """
    Test is_active() when is_loaded() returns False
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()

    # WHEN: is_active() is called with is_loaded() returns False
    with patch.object(server, 'is_loaded') as mocked_is_loaded:
        mocked_is_loaded.return_value = False
        result = server.is_active()

    # THEN: It should have returned False
    assert result is False


def test_is_active_no_control():
    """
    Test is_active() when is_loaded() returns True but there's no control
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()

    # WHEN: is_active() is called with is_loaded() returns False
    with patch.object(server, 'is_loaded') as mocked_is_loaded:
        mocked_is_loaded.return_value = True
        result = server.is_active()

    # THEN: The result should be False
    assert result is False
    mocked_is_loaded.assert_called_once_with()


def test_is_active():
    """
    Test is_active()
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control
    mocked_control.isRunning.return_value = True

    # WHEN: is_active() is called with is_loaded() returns False
    with patch.object(server, 'is_loaded') as mocked_is_loaded:
        mocked_is_loaded.return_value = True
        result = server.is_active()

    # THEN: The result should be False
    assert result is True
    mocked_is_loaded.assert_called_once_with()
    mocked_control.isRunning.assert_called_once_with()


def test_unblank_screen():
    """
    Test the unblank_screen() method
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control

    # WHEN: unblank_screen() is run
    server.unblank_screen()

    # THEN: The resume method should have been called
    mocked_control.resume.assert_called_once_with()


def test_blank_screen():
    """
    Test the blank_screen() method
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control

    # WHEN: blank_screen() is run
    server.blank_screen()

    # THEN: The resume method should have been called
    mocked_control.blankScreen.assert_called_once_with(0)


def test_is_blank_no_control():
    """
    Test the is_blank() method when there's no control
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()

    # WHEN: is_blank() is called
    result = server.is_blank()

    # THEN: It should have returned False
    assert result is False


def test_is_blank_control_is_running():
    """
    Test the is_blank() method when the control is running
    """
    # GIVEN: A LibreOfficeServer instance and a bunch of mocks
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control
    mocked_control.isRunning.return_value = True
    mocked_control.isPaused.return_value = True

    # WHEN: is_blank() is called
    result = server.is_blank()

    # THEN: It should have returned False
    assert result is True
    mocked_control.isRunning.assert_called_once_with()
    mocked_control.isPaused.assert_called_once_with()


def test_stop_presentation():
    """
    Test the stop_presentation() method
    """
    # GIVEN: A LibreOfficeServer instance and a mocked presentation
    server = LibreOfficeServer()
    mocked_presentation = MagicMock()
    mocked_control = MagicMock()
    server._presentation = mocked_presentation
    server._control = mocked_control

    # WHEN: stop_presentation() is called
    server.stop_presentation()

    # THEN: The presentation is ended and the control is removed
    mocked_presentation.end.assert_called_once_with()
    assert server._control is None


@patch('openlp.plugins.presentations.lib.libreofficeserver.time.sleep')
def test_start_presentation_no_control(mocked_sleep):
    """
    Test the start_presentation() method when there's no control
    """
    # GIVEN: A LibreOfficeServer instance and some mocks
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    mocked_document = MagicMock()
    mocked_presentation = MagicMock()
    mocked_controller = MagicMock()
    mocked_frame = MagicMock()
    mocked_window = MagicMock()
    server._document = mocked_document
    server._presentation = mocked_presentation
    mocked_document.getCurrentController.return_value = mocked_controller
    mocked_controller.getFrame.return_value = mocked_frame
    mocked_frame.getContainerWindow.return_value = mocked_window
    mocked_presentation.getController.side_effect = [None, mocked_control]

    # WHEN: start_presentation() is called
    server.start_presentation()

    # THEN: The slide number should be correct
    mocked_document.getCurrentController.assert_called_once_with()
    mocked_controller.getFrame.assert_called_once_with()
    mocked_frame.getContainerWindow.assert_called_once_with()
    mocked_presentation.start.assert_called_once_with()
    assert mocked_presentation.getController.call_count == 2
    mocked_sleep.assert_called_once_with(0.1)
    assert mocked_window.setVisible.call_args_list == [call(True), call(False)]
    assert server._control is mocked_control


def test_start_presentation():
    """
    Test the start_presentation() method when there's a control
    """
    # GIVEN: A LibreOfficeServer instance and some mocks
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control

    # WHEN: start_presentation() is called
    with patch.object(server, 'goto_slide') as mocked_goto_slide:
        server.start_presentation()

    # THEN: The control should have been activated and the first slide selected
    mocked_control.activate.assert_called_once_with()
    mocked_goto_slide.assert_called_once_with(1)


def test_get_slide_number():
    """
    Test the get_slide_number() method
    """
    # GIVEN: A LibreOfficeServer instance and some mocks
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    mocked_control.getCurrentSlideIndex.return_value = 3
    server._control = mocked_control

    # WHEN: get_slide_number() is called
    result = server.get_slide_number()

    # THEN: The slide number should be correct
    assert result == 4


def test_get_slide_count():
    """
    Test the get_slide_count() method
    """
    # GIVEN: A LibreOfficeServer instance and some mocks
    server = LibreOfficeServer()
    mocked_document = MagicMock()
    mocked_pages = MagicMock()
    server._document = mocked_document
    mocked_document.getDrawPages.return_value = mocked_pages
    mocked_pages.getCount.return_value = 2

    # WHEN: get_slide_count() is called
    result = server.get_slide_count()

    # THEN: The slide count should be correct
    assert result == 2


def test_goto_slide():
    """
    Test the goto_slide() method
    """
    # GIVEN: A LibreOfficeServer instance and some mocks
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control

    # WHEN: goto_slide() is called
    server.goto_slide(1)

    # THEN: The slide number should be correct
    mocked_control.gotoSlideIndex.assert_called_once_with(0)


@patch('openlp.plugins.presentations.lib.libreofficeserver.time.sleep')
def test_next_step_when_paused(mocked_sleep):
    """
    Test the next_step() method when paused
    """
    # GIVEN: A LibreOfficeServer instance and a mocked control
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control
    mocked_control.isPaused.side_effect = [False, True]

    # WHEN: next_step() is called
    server.next_step()

    # THEN: The correct call should be made
    mocked_control.gotoNextEffect.assert_called_once_with()
    mocked_sleep.assert_called_once_with(0.1)
    assert mocked_control.isPaused.call_count == 2
    mocked_control.gotoPreviousEffect.assert_called_once_with()


@patch('openlp.plugins.presentations.lib.libreofficeserver.time.sleep')
def test_next_step(mocked_sleep):
    """
    Test the next_step() method when paused
    """
    # GIVEN: A LibreOfficeServer instance and a mocked control
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control
    mocked_control.isPaused.side_effect = [True, True]

    # WHEN: next_step() is called
    server.next_step()

    # THEN: The correct call should be made
    mocked_control.gotoNextEffect.assert_called_once_with()
    mocked_sleep.assert_called_once_with(0.1)
    assert mocked_control.isPaused.call_count == 1
    assert mocked_control.gotoPreviousEffect.call_count == 0


def test_previous_step():
    """
    Test the previous_step() method
    """
    # GIVEN: A LibreOfficeServer instance and a mocked control
    server = LibreOfficeServer()
    mocked_control = MagicMock()
    server._control = mocked_control

    # WHEN: previous_step() is called
    server.previous_step()

    # THEN: The correct call should be made
    mocked_control.gotoPreviousEffect.assert_called_once_with()


def test_get_slide_text():
    """
    Test the get_slide_text() method
    """
    # GIVEN: A LibreOfficeServer instance
    server = LibreOfficeServer()

    # WHEN: get_slide_text() is called for a particular slide
    with patch.object(server, '_get_text_from_page') as mocked_get_text_from_page:
        mocked_get_text_from_page.return_value = 'OpenLP on Mac OS X'
        result = server.get_slide_text(5)

    # THEN: The text should be returned
    mocked_get_text_from_page.assert_called_once_with(5)
    assert result == 'OpenLP on Mac OS X'


def test_get_slide_notes():
    """
    Test the get_slide_notes() method
    """
    # GIVEN: A LibreOfficeServer instance
    server = LibreOfficeServer()

    # WHEN: get_slide_notes() is called for a particular slide
    with patch.object(server, '_get_text_from_page') as mocked_get_text_from_page:
        mocked_get_text_from_page.return_value = 'Installing is a drag-and-drop affair'
        result = server.get_slide_notes(3)

    # THEN: The text should be returned
    mocked_get_text_from_page.assert_called_once_with(3, TextType.Notes)
    assert result == 'Installing is a drag-and-drop affair'


@patch('openlp.plugins.presentations.lib.libreofficeserver.Daemon')
def test_main(MockedDaemon):
    """
    Test the main() function
    """
    # GIVEN: Mocked out Pyro objects
    mocked_daemon = MagicMock()
    MockedDaemon.return_value = mocked_daemon

    # WHEN: main() is run
    main()

    # THEN: The correct calls are made
    MockedDaemon.assert_called_once_with(host='localhost', port=4310)
    mocked_daemon.register.assert_called_once_with(LibreOfficeServer, 'openlp.libreofficeserver')
    mocked_daemon.requestLoop.assert_called_once_with()
    mocked_daemon.close.assert_called_once_with()
