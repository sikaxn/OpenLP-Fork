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
Package to test the openlp.core.ui.ThemeTab package.
"""
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry
from openlp.core.ui.settingsform import SettingsForm
from openlp.core.ui.themestab import ThemesTab


def test_save_triggers_processes_true(mock_settings):
    """
    Test that the global theme event is triggered when the tab is visited.
    """
    # GIVEN: A new Advanced Tab
    settings_form = SettingsForm(None)
    themes_tab = ThemesTab(settings_form)
    Registry().register('renderer', MagicMock())
    themes_tab.tab_visited = True
    # WHEN: I change search as type check box
    themes_tab.save()

    # THEN: we should have two post save processed to run
    assert 1 == len(settings_form.processes), 'One post save processes should be created'


def test_save_triggers_processes_false(mock_settings):
    """
    Test that the global theme event is not triggered when the tab is not visited.
    """
    # GIVEN: A new Advanced Tab
    settings_form = SettingsForm(None)
    themes_tab = ThemesTab(settings_form)
    Registry().register('renderer', MagicMock())
    themes_tab.tab_visited = False
    # WHEN: I change search as type check box
    themes_tab.save()

    # THEN: we should have two post save processed to run
    assert 0 == len(settings_form.processes), 'No post save processes should be created'
