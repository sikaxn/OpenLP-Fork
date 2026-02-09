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
###########################################################################
"""
Package to test the openlp.core.ui.media package.
"""
import pytest

from unittest.mock import MagicMock


from openlp.core.common.registry import Registry
from openlp.core.ui.media import MediaPlayItem, media_state, MediaState, MediaType


@pytest.mark.parametrize("theme, type, playing, result", [
    (True, MediaType.Audio, MediaState.Paused, MediaState.Off),
    (True, MediaType.Dual, MediaState.Paused, MediaState.Paused),
    (False, MediaType.Dual, MediaState.Playing, MediaState.Playing),
    (False, MediaType.Audio, MediaState.Paused, MediaState.Paused),
    (False, MediaType.Video, MediaState.Playing, MediaState.Playing)
])
def test_media_state(registry: Registry, theme: bool, type: MediaType, playing: MediaState, result: MediaState):
    live = MagicMock()
    live.media_play_item = MediaPlayItem()
    live.media_play_item.is_theme_background = theme
    live.media_play_item.media_type = type
    live.media_play_item.is_playing = playing
    Registry().register("live_controller", live)
    Registry().register_function("media_state", media_state)
    ans = registry.execute("media_state")[0]
    assert ans == result
