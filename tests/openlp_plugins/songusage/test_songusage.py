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
This module contains tests for the Songusage plugin.
"""
from unittest.mock import MagicMock, patch

from openlp.plugins.songusage.lib import upgrade
from openlp.plugins.songusage.lib.db import init_schema
from openlp.plugins.songusage.songusageplugin import SongUsagePlugin


def test_about_text(state, mock_settings):
    """
    Test the about text of the song usage plugin
    """
    # GIVEN: The SongUsagePlugin
    # WHEN: Retrieving the about text
    # THEN: about() should return a string object
    assert isinstance(SongUsagePlugin.about(), str)
    # THEN: about() should return a non-empty string
    assert len(SongUsagePlugin.about()) != 0
    assert len(SongUsagePlugin.about()) != 0


@patch('openlp.plugins.songusage.songusageplugin.DBManager')
def test_song_usage_init(MockedManager, settings, state):
    """
    Test the initialisation of the SongUsagePlugin class
    """
    # GIVEN: A mocked database manager
    mocked_manager = MagicMock()
    MockedManager.return_value = mocked_manager

    # WHEN: The SongUsagePlugin class is instantiated
    song_usage = SongUsagePlugin()

    # THEN: It should be initialised correctly
    MockedManager.assert_called_with('songusage', init_schema, upgrade_mod=upgrade)
    assert mocked_manager == song_usage.manager
    assert song_usage.song_usage_active is False


@patch('openlp.plugins.songusage.songusageplugin.DBManager')
def test_check_pre_conditions(MockedManager, settings, state):
    """
    Test that check_pre_condition returns true for valid manager session
    """
    # GIVEN: A mocked database manager
    mocked_manager = MagicMock()
    mocked_manager.session = MagicMock()
    MockedManager.return_value = mocked_manager
    song_usage = SongUsagePlugin()

    # WHEN: The calling check_pre_conditions
    ret = song_usage.check_pre_conditions()

    # THEN: It should return True
    assert ret is True


@patch('openlp.plugins.songusage.songusageplugin.DBManager')
def test_toggle_song_usage_state(MockedManager, settings, state):
    """
    Test that toggle_song_usage_state does toggle song_usage_state
    """
    # GIVEN: A SongUsagePlugin
    song_usage = SongUsagePlugin()
    song_usage.set_button_state = MagicMock()
    song_usage.song_usage_active = True

    # WHEN: calling toggle_song_usage_state
    song_usage.toggle_song_usage_state()

    # THEN: song_usage_state should have been toggled
    assert song_usage.song_usage_active is False
