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
Module to test the StreamSelectorForm.
"""
import pytest

from unittest.mock import MagicMock, patch

from PySide6 import QtCore, QtTest, QtWidgets

from openlp.plugins.media.forms.streamselectorform import StreamSelectorForm


# This mocks the callback function BackgroundPage.set_stream() in core/pages/background.py
# This function is used to set the device stream text in the theme wizard
setstream = MagicMock()


@pytest.fixture()
def stream_selector_form(settings):
    '''
    Fixture for setting up a StreamSelectorForm with dummy video and audio devices
    '''
    main_window = QtWidgets.QMainWindow()

    camera1 = MagicMock()
    camera1.description.return_value = "Camera 1"
    camera1.deviceName.return_value = "Camera 1 device"
    camera2 = MagicMock()
    camera2.description.return_value = "Camera 2"
    camera2.deviceName.return_value = "Camera 2 device"

    audio1 = MagicMock()
    audio1.description.return_value = "Audio 1"
    audio1.deviceName.return_value = "Audio 1 device"
    audio2 = MagicMock()
    audio2.description.return_value = "Audio 2"
    audio2.deviceName.return_value = "Audio 2 device"

    with patch('openlp.plugins.media.forms.streamselectordialog.QMediaDevices.videoInputs',
               return_value=[camera1, camera2]), \
            patch('openlp.plugins.media.forms.streamselectordialog.QMediaDevices.audioInputs',
                  return_value=[audio1, audio2]):
        form = StreamSelectorForm(main_window, setstream)

    yield form
    del form
    del main_window


def test_set_mrl(stream_selector_form):
    '''
    Test that the UI components are prefilled correctly
    '''
    # GIVEN: A fixture for a StreamSelectorForm on a windows computer with dummy devices

    # WHEN: The stream selector form is prefilled

    live_stream_text = 'devicestream:streamtest&&qt6video=Camera 2;qt6audio=Audio 2&&'
    stream_selector_form.set_mrl(live_stream_text)

    # THEN: The form should contain the prefilled values
    stream_selector_form.stream_name_edit.text() == "streamtest"
    assert stream_selector_form.capture_widget.video_devices_combo_box.currentText() == 'Camera 2'
    assert stream_selector_form.capture_widget.video_devices_combo_box.currentIndex() == 2


def test_set_stream_call(stream_selector_form):
    '''
    Test that when a stream selector form is run and filled in then set_stream() is called correctly
    '''
    # GIVEN: A fixture for a StreamSelectorForm on a windows computer with dummy devices

    # WHEN: The form is executed and filled in with values

    stream_selector_form.stream_name_edit.setText('test')
    # choose camera 2
    stream_selector_form.capture_widget.video_devices_combo_box.setCurrentIndex(2)
    # click on Save
    QtTest.QTest.mouseClick(stream_selector_form.save_button, QtCore.Qt.MouseButton.LeftButton)

    # THEN: The callback function should be called with the correct values
    setstream.assert_called_with('devicestream:test&&qt6video=Camera 2;qt6audio=&&')
