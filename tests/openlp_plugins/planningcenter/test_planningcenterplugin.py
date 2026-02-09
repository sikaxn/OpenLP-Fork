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
Package to test the openlp.plugins.planningcenter.planningcenterplugin package.
"""
import pytest
from unittest.mock import MagicMock, patch

from PySide6 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.plugins.planningcenter.planningcenterplugin import PlanningCenterPlugin


@pytest.fixture
def plugin(qapp, settings: Settings, state: State, registry: Registry):
    """An instance of the PlanningcenterPlugin"""
    registry.register('main_window', None)
    plugin = PlanningCenterPlugin()
    return plugin


def test_class_init_defaults(plugin: PlanningCenterPlugin):
    """
    Test that the plugin class is instantiated with the correct defaults
    """
    # GIVEN: A PlanningcenterPlugin Class
    # WHEN:  the class has been through __init__
    # THEN:
    # planningcenter form is set to None
    assert plugin.planningcenter_form is None, "Init plugin set to None"
    # icon is set correctly
    assert plugin.icon == UiIcons().planning_center, "Init icon set to planning_center icon"
    # weight is -1
    assert plugin.weight == -1, "Init weight set to -1"
    # the planning_center module is registered active
    assert State().is_module_active('planning_center') is True, "Init State() is active"


def test_initialise(plugin: PlanningCenterPlugin):
    """
    Test that the initialise function can be called and it passes a call along
    to its parent class
    """
    # GIVEN: A PlanningcenterPlugin Class
    # WHEN:  initialise has been called on the class
    with patch('openlp.plugins.planningcenter.planningcenterplugin.PlanningCenterPlugin.import_planning_center',
               create=True):
        return_value = plugin.initialise()
    # THEN:
    # the function returns and does not fail... it doesn't do much at this point, so this
    # is mainly to improve test coverage
    assert return_value is None, "Initialise was called on the class and it didn't crash"


def test_import_menu_item_added(plugin: PlanningCenterPlugin):
    """
    Test that the add_import_menu_item function adds the menu item
    """
    # GIVEN: A PlanningcenterPlugin Class
    # WHEN:  add_import_menu_item is called
    import_menu = QtWidgets.QMenu()
    plugin.add_import_menu_item(import_menu)
    plugin.import_planning_center.setVisible(True)
    # THEN:
    # the menu should not be empty
    assert import_menu.isEmpty() is False, "Menu Item is populated"


@patch('openlp.plugins.planningcenter.planningcenterplugin.SelectPlanForm')
def test_on_import_planning_center_triggered_with_auth_settings(MockSelectPlanForm: MagicMock,
                                                                plugin: PlanningCenterPlugin,
                                                                registry: Registry, settings: Settings):
    """
    Test that the on_import_planning_center_triggered function correctly returns
    the correct form to display.
    """
    # GIVEN: A PlanningCenterPlugin Class with mocked exec calls on both
    # PlanningCenter forms and settings set
    mocked_select_plan_form = MagicMock()
    MockSelectPlanForm.return_value = mocked_select_plan_form
    mocked_settings_form = MagicMock()
    registry.register('settings_form', mocked_settings_form)
    settings.setValue('planningcenter/application_id', 'test-application-id')
    settings.setValue('planningcenter/secret', 'test-secret')
    # init the planning center plugin so we have default values defined for Settings()
    # WHEN:  on_import_planning_center_triggered is called
    plugin.on_import_planning_center_triggered()
    # THEN:
    assert mocked_select_plan_form.exec.call_count == 1, 'Select Plan Form was shown'
    assert mocked_settings_form.exec.call_count == 0, 'Settings Form was not shown'


@patch('openlp.plugins.planningcenter.forms.selectplanform.SelectPlanForm.exec')
def test_on_import_planning_center_triggered_without_auth_settings(mocked_selectplan_exec: MagicMock,
                                                                   plugin: PlanningCenterPlugin,
                                                                   registry: Registry, settings: Settings):
    """
    Test that the on_import_planning_center_triggered function correctly returns
    the correct form to display.
    """
    # GIVEN: A PlanningCenterPlugin Class with mocked exec calls on both
    mocked_settings_form = MagicMock()
    registry.register('settings_form', mocked_settings_form)
    # PlanningCenter forms and settings set
    # application_id = ''
    # secret = ''
    # settings.setValue('planningcenter/application_id', application_id)
    # settings.setValue('planningcenter/secret', secret)
    # init the planning center plugin so we have default values defined for Settings()
    # WHEN:  on_import_planning_center_triggered is called
    plugin.on_import_planning_center_triggered()
    # THEN:
    assert mocked_selectplan_exec.call_count == 0, "Select Plan Form was not shown"
    assert mocked_settings_form.exec.call_count == 1, "Edit Auth Form was shown"


def test_finalise(plugin: PlanningCenterPlugin):
    """
    Test that the finalise function cleans up after the plugin
    """
    # GIVEN: A PlanningcenterPlugin Class with a bunch of mocks
    plugin.import_planning_center = MagicMock()

    # WHEN: finalise has been called on the class
    plugin.finalise()

    # THEN: it cleans up after itself
    plugin.import_planning_center.setVisible.assert_called_once_with(False)


def test_about(plugin: PlanningCenterPlugin):
    result = plugin.about()

    assert result == (
        '<strong>PlanningCenter Plugin</strong>'
        '<br />The planningcenter plugin provides an interface to import '
        'service plans from the Planning Center Online v2 API.'
    )
