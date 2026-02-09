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
Package to test the openlp.core.ui.servicetab package.
"""
from openlp.core.ui.servicetab import ServiceTab
from openlp.core.ui.settingsform import SettingsForm


def test_creation(settings):
    """
    Test that Service Tab is created.
    """
    # GIVEN: A new Service Tab
    settings_form = SettingsForm(None)

    # WHEN: I create an service tab
    service_tab = ServiceTab(settings_form)

    # THEN:
    assert "Service" == service_tab.tab_title, 'The tab title should be Service'
