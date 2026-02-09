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
Package to test the openlp.core.ui.media package.
"""

import pytest

from unittest.mock import MagicMock, ANY

from openlp.core.ui.media import get_volume, save_volume, toggle_looping_playback, saved_looping_playback
from openlp.core.ui.media import format_milliseconds, get_supported_media_suffix


def test_media_suffix():
    """ Test the generation of media suffixex"""
    # GIVEN: A default set of suffixes
    # WHEN:I request them
    aud, vid = get_supported_media_suffix()
    # THEN: the following Codecs will be returned
    assert "mp3" not in aud
    assert "mp4" not in vid


def test_format_milliseconds():
    """
    Test that format_milliseconds(...) makes an expected human readable time string
    """

    # GIVEN: 200 million milliseconds (Revelation 9:16)
    num_soldiers_on_horses_as_milliseconds = 200 * 1000 * 1000

    # WHEN: converting milliseconds to human readable string
    num_soldiers_on_horses_as_formatted_time_string = format_milliseconds(num_soldiers_on_horses_as_milliseconds)

    # THEN: The formatted time string should be 55 hours, 33 minutes, 20 seconds, and 000 milliseconds
    assert num_soldiers_on_horses_as_formatted_time_string == "55:33:20,000"


@pytest.mark.parametrize("live, result", [(False, 'media/preview volume'), (True, 'media/live volume')])
def test_get_volume(mock_settings, live, result):
    controller = MagicMock()
    controller.is_live = live
    get_volume(controller)
    mock_settings.value.assert_called_with(result)


@pytest.mark.parametrize("live, result", [(False, 'media/preview volume'), (True, 'media/live volume')])
def test_save_volume(mock_settings, live, result):
    controller = MagicMock()
    controller.is_live = live
    save_volume(controller, 5)
    mock_settings.setValue.assert_called_with(result, ANY)


@pytest.mark.parametrize("live, result", [(False, 'media/preview loop'), (True, 'media/live loop')])
def test_toggle_looping_playback(mock_settings, live, result):
    controller = MagicMock()
    controller.is_live = live
    toggle_looping_playback(controller)
    mock_settings.value.assert_called_with(result)
    mock_settings.setValue.assert_called_with(result, ANY)


@pytest.mark.parametrize("live, result", [(False, 'media/preview loop'), (True, 'media/live loop')])
def test_is_looping_playback(mock_settings, live, result):
    controller = MagicMock()
    controller.is_live = live
    saved_looping_playback(controller)
    mock_settings.value.assert_called_with(result)
