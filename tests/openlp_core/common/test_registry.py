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
Package to test the openlp.core.lib package.
"""
import logging
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry, RegistryBase


def dummy_function_1():
    return "function_1"


def dummy_function_2():
    return "function_2"


def test_registry_service(registry: Registry):
    """
    Test the registry creation and its usage
    """
    # GIVEN: A new registry
    # WHEN: I add a component it should save it
    mock_1 = MagicMock()
    Registry().register('test1', mock_1)

    # THEN: we should be able retrieve the saved component
    assert Registry().get('test1') == mock_1, 'The saved service can be retrieved and matches'

    # WHEN: I add a component for the second time I am mad.
    # THEN  and I will get an exception
    with pytest.raises(KeyError) as context:
        Registry().register('test1', mock_1)
    assert context.value != KeyError('Duplicate service exception test1'), \
        'KeyError exception should have been thrown for duplicate service'

    # WHEN I try to get back a non existent component
    # THEN I will get None
    assert Registry().get('test2') is None

    # WHEN I try to replace a component I should be allowed
    Registry().remove('test1')
    # THEN I will get an exception
    assert Registry().get('test1') is None


def test_registry_function(registry: Registry):
    """
    Test the registry function creation and their usages
    """
    # GIVEN: An existing registry register a function
    Registry().register_function('test1', dummy_function_1)

    # WHEN: I execute the function
    return_value = Registry().execute('test1')

    # THEN: I expect then function to have been called and a return given
    assert return_value[0] == 'function_1', 'A return value is provided and matches'

    # WHEN: I execute the a function with the same reference and execute the function
    Registry().register_function('test1', dummy_function_1)
    return_value = Registry().execute('test1')

    # THEN: I expect then function to have been called and a return given
    assert return_value == ['function_1', 'function_1'], 'A return value list is provided and matches'

    # WHEN: I execute the a 2nd function with the different reference and execute the function
    Registry().register_function('test2', dummy_function_2)
    return_value = Registry().execute('test2')

    # THEN: I expect then function to have been called and a return given
    assert return_value[0] == 'function_2', 'A return value is provided and matches'


@patch('openlp.core.common.registry.log')
@patch('openlp.core.common.registry.trace_error_handler')
def test_registry_function_type_error(mocked_trace_error: MagicMock, mocked_log: MagicMock, registry: Registry):
    """Test that a TypeError is logged"""
    # GIVEN: A registry, some mocks, and a rigged function
    mock_function = MagicMock()
    mock_function.side_effect = TypeError
    registry.register_function('mock', mock_function)

    # WHEN: execute is called
    result = registry.execute('mock', 'arg', kwarg='kwarg')

    # THEN: result should be an empty list, and the correct functions should have been called
    assert result == []
    mock_function.assert_called_with('arg', kwarg='kwarg')
    mocked_trace_error.assert_called_once_with(mocked_log)
    mocked_log.exception.assert_called_once_with(f'Exception for function {mock_function}')


@patch('openlp.core.common.registry.log')
@patch('openlp.core.common.registry.trace_error_handler')
def test_registry_function_does_not_exist(mocked_trace_error: MagicMock, mocked_log: MagicMock,
                                          registry: Registry):
    """Test that a TypeError is logged"""
    # GIVEN: A registry, some mocks, and a rigged function
    mocked_log.getEffectiveLevel.return_value = logging.DEBUG

    # WHEN: execute is called
    result = registry.execute('mock')

    # THEN: result should be an empty list, and the correct functions should have been called
    assert result == []
    mocked_trace_error.assert_called_once_with(mocked_log)
    mocked_log.error.assert_called_once_with('Event mock called but not registered')


def test_registry_working_flags(registry: Registry):
    """
    Test the registry working flags creation and its usage
    """
    # GIVEN: A new registry
    # WHEN: I add a working flag it should save it
    my_data = 'Lamas'
    my_data2 = 'More Lamas'
    Registry().set_flag('test1', my_data)

    # THEN: we should be able retrieve the saved component
    temp = Registry().get_flag('test1')
    assert temp == my_data, 'The value should have been saved'

    # WHEN: I add a component for the second time I am not mad.
    # THEN  and I will not get an exception
    Registry().set_flag('test1', my_data2)
    temp = Registry().get_flag('test1')
    assert temp == my_data2, 'The value should have been updated'

    # WHEN I try to get back a non existent Working Flag
    # THEN I will get an exception
    with pytest.raises(KeyError) as context1:
        Registry().get_flag('test2')
    assert context1.value != KeyError('Working Flag test2 not found in list'), \
        'KeyError exception should have been thrown for missing working flag'

    # WHEN I try to replace a working flag I should be allowed
    Registry().remove_flag('test1')
    # THEN I will get an exception
    with pytest.raises(KeyError) as context:
        Registry().get_flag('test1')
    assert context.value != 'Working Flag test1 not found in list', \
        'KeyError exception should have been thrown for duplicate working flag'


def test_remove_function(registry: Registry):
    """
    Test the remove_function() method
    """
    # GIVEN: An existing registry register a function
    Registry().register_function('test1', dummy_function_1)

    # WHEN: Remove the function.
    Registry().remove_function('test1', dummy_function_1)

    # THEN: The method should not be available.
    assert Registry().functions_list['test1'] == [], 'The function should not be in the dict anymore.'


class PlainStub(object):
    def __init__(self):
        pass


class RegistryStub(RegistryBase):
    def __init__(self):
        super().__init__()


def test_registry_mixin_missing(registry: Registry):
    """
    Test the registry creation and its usage
    """
    # GIVEN: A new registry
    # WHEN: I create an instance of a class that doesn't inherit from RegistryMixin
    PlainStub()

    # THEN: Nothing is registered with the registry
    assert len(Registry().functions_list) == 0, 'The function should not be in the dict anymore.'


def test_registry_mixin_present(registry: Registry):
    """
    Test the registry creation and its usage
    """
    # GIVEN: A new registry
    # WHEN: I create an instance of a class that inherits from RegistryMixin
    RegistryStub()

    # THEN: The bootstrap methods should be registered
    assert len(Registry().functions_list) == 3, 'The bootstrap functions should be in the dict.'


def test_registry_base_empty_methods(registry: Registry):
    """Test the RegistryBase class, just to increase coverage"""
    base = RegistryStub()
    base.bootstrap_initialise()
    base.bootstrap_post_set_up()
    base.bootstrap_completion()
