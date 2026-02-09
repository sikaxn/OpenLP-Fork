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
from unittest.mock import MagicMock

from openlp.core.state import State, MessageType
from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import PluginStatus


"""
Test the States class.
"""


def test_load_settings(state):
    # GIVEN: Some modules
    State().modules = {'mock': MagicMock}

    # WHEN: load_settings() is run
    State().load_settings()

    # THEN: the modules should be empty
    assert State().modules == {}, 'There should be no modules in the State object'


def test_save_settings(state):
    # GIVEN: Niks
    # WHEN: save_settings() is run
    State().save_settings()

    # THEN: Nothing should happen
    assert True, 'There should be no exceptions'


def test_add_service(state):
    # GIVEN a new state
    # WHEN I add a new service
    State().add_service("test", 1, PluginStatus.Active)

    # THEN I have a saved service
    assert len(State().modules) == 1


def test_add_service_multiple(state):
    # GIVEN a new state
    # WHEN I add a new service twice
    State().add_service("test", 1, PluginStatus.Active)
    State().add_service("test", 1, PluginStatus.Active)

    # THEN I have a single saved service
    assert len(State().modules) == 1


def test_add_service_multiple_depend(state):
    # GIVEN a new state
    # WHEN I add a new service twice
    State().add_service("test", 1, 1, PluginStatus.Active)
    State().add_service("test1", 1, 1, PluginStatus.Active, "test")
    State().add_service("test1", 1, 1, PluginStatus.Active, "test")

    # THEN I have still have a single saved service and one dependency
    assert len(State().modules) == 2
    assert len(State().modules['test'].required_by) == 1


def test_add_service_multiple_depends(state):
    # GIVEN a new state
    # WHEN I add a new service twice
    State().add_service("test", 1, 1, PluginStatus.Active)
    State().add_service("test1", 1, 1, PluginStatus.Active, "test")
    State().add_service("test2", 1, 1, PluginStatus.Active, "test")

    # THEN I have a 3 modules and 2 dependencies
    assert len(State().modules) == 3
    assert len(State().modules['test'].required_by) == 2


def test_active_service(state):
    # GIVEN a new state
    # WHEN I add a new service which is Active
    State().add_service("test", 1, 1, PluginStatus.Active)

    # THEN I have a single saved service
    assert State().is_module_active('test') is True


def test_inactive_service(state):
    # GIVEN a new state
    # WHEN I add a new service which is Inactive
    State().add_service("test", 1, 1, PluginStatus.Inactive)

    # THEN I have a single saved service
    assert State().is_module_active('test') is False


def test_basic_preconditions_fail(state, registry):
    # GIVEN a new state
    Registry().register('test_plugin', MagicMock())

    # WHEN I add a new services with dependencies and a failed pre condition
    State().add_service("test", 1, 1, PluginStatus.Inactive)
    State().add_service("test2", 1, 1, PluginStatus.Inactive)
    State().add_service("test1", 1, 1, PluginStatus.Inactive, 'test')
    State().update_pre_conditions('test', False)

    # THEN correct the state when I flush the preconditions
    assert State().modules['test'].pass_preconditions is False
    assert State().modules['test2'].pass_preconditions is False
    assert State().modules['test1'].pass_preconditions is False
    State().flush_preconditions()
    assert State().modules['test'].pass_preconditions is False
    assert State().modules['test2'].pass_preconditions is False
    assert State().modules['test1'].pass_preconditions is False


def test_basic_preconditions_pass(state, registry):
    # GIVEN a new state
    Registry().register('test_plugin', MagicMock())

    # WHEN I add a new services with dependencies and a failed pre condition
    State().add_service("test", 1, 1, PluginStatus.Inactive)
    State().add_service("test2", 1, 1, PluginStatus.Inactive)
    State().add_service("test1", 1, 1, PluginStatus.Inactive, 'test')
    State().update_pre_conditions('test', True)

    # THEN correct the state when I flush the preconditions
    assert State().modules['test'].pass_preconditions is True
    assert State().modules['test2'].pass_preconditions is False
    assert State().modules['test1'].pass_preconditions is False
    State().flush_preconditions()
    assert State().modules['test'].pass_preconditions is True
    assert State().modules['test2'].pass_preconditions is False
    assert State().modules['test1'].pass_preconditions is True


def test_missing_text(state):
    """
    Test that settings the missing text in a module works
    """
    # GIVEN: A state with a module
    State().modules['test'] = MagicMock()

    # WHEN: missing_text() is called
    State().missing_text('test', 'Test test', MessageType.Information)

    # THEN: The text is set
    assert State().modules['test'].text == 'Test test', 'The text on the module should have been set'
    assert State().modules['test'].message_type == MessageType.Information, \
        'The message type on the module should have been set'


def test_get_text(state):
    """
    Test that the get_text() method returns the text of all the states
    """
    # GIVEN: Some states with text
    State().modules.update({'test1': MagicMock(text='Test 1', message_type=MessageType.Error),
                            'test2': MagicMock(text='Test 2', message_type=MessageType.Information)})

    # WHEN: get_text() is called
    result = State().get_text()

    # THEN: The correct text is returned
    assert result == 'Test 1\nTest 2\n', 'The full text is returned'


def test_get_text_single_type(state):
    """
    Test that the get_text() method returns the text of only that particular message type
    """
    # GIVEN: Some states with text
    State().modules.update({'test1': MagicMock(text='Test 1', message_type=MessageType.Error),
                            'test2': MagicMock(text='Test 2', message_type=MessageType.Information)})

    # WHEN: get_text() is called
    result = State().get_text(MessageType.Information)

    # THEN: The correct text is returned
    assert result == 'Test 2\n', 'Only the information text is returned'


def test_check_preconditions_no_required(state):
    """
    Test that the check_preconditions() method returns the correct attribute when there are no requirements
    """
    # GIVEN: A State with no requires
    State().modules.update({'test_pre1': MagicMock(requires=None, pass_preconditions=True)})

    # WHEN: check_preconditions() is called
    result = State().check_preconditions('test_pre1')

    # THEN: The correct result should be returned
    assert result is True


def test_check_preconditions_required_module(state):
    """
    Test that the check_preconditions() method returns the correct attribute when there is another required module
    """
    # GIVEN: A State with two modules
    State().modules.update({
        'test_pre2': MagicMock(requires='test_pre3', pass_preconditions=True),
        'test_pre3': MagicMock(requires=None, pass_preconditions=False)
    })

    # WHEN: check_preconditions() is called
    result = State().check_preconditions('test_pre2')

    # THEN: The correct result should be returned
    assert result is False


def test_check_preconditions_missing_module(state):
    """
    Test that the check_preconditions() method returns the correct attribute when the module is missing
    """
    # GIVEN: A State with two modules
    State().modules.update({
        'test_pre2': MagicMock(requires='test_pre3', pass_preconditions=True),
        'test_pre3': MagicMock(requires=None, pass_preconditions=False)
    })

    # WHEN: check_preconditions() is called
    result = State().check_preconditions('test_pre1')

    # THEN: The correct result should be returned
    assert result is False
