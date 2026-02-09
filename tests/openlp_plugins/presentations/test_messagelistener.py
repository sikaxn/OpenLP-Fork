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
This module contains tests for the lib submodule of the Presentations plugin.
"""
from unittest.mock import MagicMock, patch

from openlp.core.ui import HideMode
from openlp.plugins.presentations.lib.mediaitem import MessageListener
from openlp.plugins.presentations.lib.messagelistener import Controller


@patch('openlp.plugins.presentations.lib.mediaitem.MessageListener._setup')
def test_start_presentation(media_mock, media_item):
    """
    Find and chose a controller to play a presentations.
    """
    # GIVEN: A single controller and service item wanting to use the controller
    mock_item = MagicMock()
    mock_item.processor = 'Powerpoint'
    mock_item.get_frame_path.return_value = "test.ppt"
    media_item.automatic = False
    mocked_controller = MagicMock()
    mocked_controller.available = True
    mocked_controller.supports = ['ppt']
    controllers = {
        'Powerpoint': mocked_controller
    }
    ml = MessageListener(media_item)
    ml.media_item = media_item
    ml.controllers = controllers
    ml.preview_handler = MagicMock()
    ml.timer = MagicMock()

    # WHEN: request the presentation to start
    ml.startup([mock_item, False, False, False])

    # THEN: The controllers will be setup.
    assert len(controllers) > 0, 'We have loaded a controller'


@patch('openlp.plugins.presentations.lib.mediaitem.MessageListener._setup')
def test_start_presentation_with_no_player(media_mock, media_item):
    """
    Find and chose a controller to play a presentations when the player is not available.
    """
    # GIVEN: A single controller and service item wanting to use the controller
    mock_item = MagicMock()
    mock_item.processor = 'Powerpoint'
    mock_item.get_frame_path.return_value = "test.ppt"
    media_item.automatic = False
    mocked_controller = MagicMock()
    mocked_controller.available = True
    mocked_controller.supports = ['ppt']
    mocked_controller1 = MagicMock()
    mocked_controller1.available = False
    mocked_controller1.supports = ['ppt']
    controllers = {
        'Impress': mocked_controller,
        'Powerpoint': mocked_controller1
    }
    ml = MessageListener(media_item)
    ml.media_item = media_item
    ml.controllers = controllers
    ml.preview_handler = MagicMock()
    ml.timer = MagicMock()

    # WHEN: request the presentation to start
    ml.startup([mock_item, False, False, False])

    # THEN: The controllers will be setup.
    assert len(controllers) > 0, 'We have loaded a controller'


@patch('openlp.plugins.presentations.lib.mediaitem.MessageListener._setup')
def test_start_pdf_presentation(media_mock, media_item):
    """
    Test the startup of pdf presentation succeed.
    """
    # GIVEN: A sservice item with a pdf
    mock_item = MagicMock()
    mock_item.processor = 'Pdf'
    mock_item.get_frame_path.return_value = "test.pdf"
    expected_identifier = mock_item.unique_identifier
    media_item.generate_slide_data = MagicMock()
    ml = MessageListener(media_item)
    ml.media_item = media_item
    ml.preview_handler = MagicMock()

    # WHEN: request the presentation to start
    ml.startup([mock_item, False, False, False])

    # THEN: The handler should be set to None
    assert ml.handler is None, 'The handler should be None'

    # THEN: unique_identifier should still be the same.
    assert mock_item.unique_identifier == expected_identifier, 'unique_identifier should not be changed'


def test_add_handler_failure():
    """
    Test that add_handler does set doc.slidenumber to 0 in case filed loading
    """
    # GIVEN: A Controller, a mocked doc-controller
    controller = Controller(True)
    mocked_doc_controller = MagicMock()
    mocked_doc = MagicMock()
    mocked_doc.load_presentation.return_value = False
    mocked_doc_controller.add_document.return_value = mocked_doc

    # WHEN: calling add_handler that fails
    controller.add_handler(mocked_doc_controller, MagicMock(), True, 0, "uuid")

    # THEN: ui_slidenumber should be 0
    assert controller.doc.ui_slidenumber == 0, 'doc.ui_slidenumber should be 0'


@patch('openlp.plugins.presentations.lib.messagelistener.PresentationList')
@patch('openlp.plugins.presentations.lib.messagelistener.Registry')
def test_add_handler_hide_mode_screen_and_slidenumber_zero(
        mocked_registry: MagicMock, mocked_presentation_list: MagicMock):
    """
    Test that add_handler calls stop() and Registry().execute() when hide_mode is HideMode.Screen.
    Also, verify that ui_slidenumber is set to 1 when slide_no = 0.
    """
    # GIVEN: A Controller, a mocked document controller, and dependencies
    controller = Controller(True)
    mocked_doc_controller = MagicMock()
    mocked_doc = MagicMock()
    mocked_doc.load_presentation.return_value = True
    mocked_doc_controller.add_document.return_value = mocked_doc
    mocked_registry_instance = mocked_registry.return_value

    # WHEN: Calling add_handler with hide_mode = HideMode.Screen and slide_no = 0
    with patch.object(controller, 'stop') as mocked_stop:
        controller.add_handler(mocked_doc_controller, MagicMock(), HideMode.Screen, 0, "uuid")

    # THEN: stop() and Registry.execute() should have been called, and ui_slidenumber should be set to 1
    mocked_registry_instance.execute.assert_called_with('live_display_hide', HideMode.Screen)
    mocked_stop.assert_called_once()
    assert controller.doc.ui_slidenumber == 1, 'doc.ui_slidenumber should be 1'


@patch('openlp.plugins.presentations.lib.messagelistener.PresentationList')
def test_add_handler_hide_mode_theme(mocked_presentation_list: MagicMock):
    """
    Test that add_handler calls blank() when hide_mode is HideMode.Theme.
    """
    # GIVEN: A Controller and a mocked document controller
    controller = Controller(True)
    mocked_doc_controller = MagicMock()
    mocked_doc = MagicMock()
    mocked_doc.load_presentation.return_value = True
    mocked_doc_controller.add_document.return_value = mocked_doc

    # WHEN: Calling add_handler with hide_mode = HideMode.Theme
    with patch.object(controller, 'blank') as mocked_blank:
        controller.add_handler(mocked_doc_controller, MagicMock(), HideMode.Theme, 1, "uuid")

    # THEN: blank() should have been called with HideMode.Theme
    mocked_blank.assert_called_once_with(HideMode.Theme)


@patch('openlp.plugins.presentations.lib.messagelistener.PresentationList')
def test_add_handler_hide_mode_blank(mocked_presentation_list: MagicMock):
    """
    Test that add_handler calls blank() when hide_mode is HideMode.Blank.
    """
    # GIVEN: A Controller and a mocked document controller
    controller = Controller(True)
    mocked_doc_controller = MagicMock()
    mocked_doc = MagicMock()
    mocked_doc.load_presentation.return_value = True
    mocked_doc_controller.add_document.return_value = mocked_doc

    # WHEN: Calling add_handler with hide_mode = HideMode.Blank
    with patch.object(controller, 'blank') as mocked_blank:
        controller.add_handler(mocked_doc_controller, MagicMock(), HideMode.Blank, 1, "uuid")

    # THEN: blank() should have been called with HideMode.Blank
    mocked_blank.assert_called_once_with(HideMode.Blank)


@patch('openlp.plugins.presentations.lib.messagelistener.PresentationList')
@patch('openlp.plugins.presentations.lib.messagelistener.Registry')
def test_add_handler_slidenumber_one(mocked_registry: MagicMock, mocked_presentation_list: MagicMock):
    """
    Test that add_handler calls slide(), start_presentation(), and Registry().execute() when slide_no = 1.
    """
    # GIVEN: A Controller, a mocked document controller, and dependencies
    controller = Controller(True)
    mocked_doc_controller = MagicMock()
    mocked_doc = MagicMock()
    mocked_doc.load_presentation.return_value = True
    mocked_doc.start_presentation = MagicMock()
    mocked_doc_controller.add_document.return_value = mocked_doc
    mocked_registry_instance = mocked_registry.return_value

    # WHEN: Calling add_handler with slide_no = 1
    with patch.object(controller, 'slide') as mocked_slide:
        controller.add_handler(mocked_doc_controller, MagicMock(), None, 1, "uuid")

    # THEN: slide(), start_presentation(), and Registry.execute() should have been called
    mocked_slide.assert_called_once_with(1)
    mocked_doc.start_presentation.assert_called_once()
    mocked_registry_instance.execute.assert_called_with('live_display_hide', HideMode.Screen)
