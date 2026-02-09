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
from pathlib import Path
from unittest.mock import patch

try:
    import Pyro5    # noqa
    from openlp.plugins.presentations.lib.serializers import path_class_to_dict, path_dict_to_class, register_classes
except ImportError:
    import pytest
    pytestmark = pytest.mark.skip('Pyro5 not installed')


def test_path_class_to_dict():
    """Test that the path_class_to_dict() method returns a correctly formatted dictionary"""
    # GIVEN: A Path object
    path = Path('openlp/core/ui/aboutform.py')

    # WHEN: path_class_to_dict() is called with the given Path object
    result = path_class_to_dict(path)

    # THEN: The dictionary should be formatted correctly
    assert result == {'__class__': 'Path', 'parts': ('openlp', 'core', 'ui', 'aboutform.py')}


def test_path_dict_to_class():
    """Test that the path_dict_to_class() method returns the right object"""
    # GIVEN: A dictionary that was created from a Path object
    path_dict = {'__class__': 'Path', 'parts': ('openlp', 'core', 'app.py')}

    # WHEN: path_dict_to_class() is called with the given dictionary
    result = path_dict_to_class('Path', path_dict)

    # THEN: The correct Path object should have been created
    assert isinstance(result, Path)
    assert result == Path('openlp/core/app.py')


@patch('openlp.plugins.presentations.lib.serializers.SerializerBase')
def test_register_classes(MockSerializerBase):
    """Test that the register_classes() method registers the two functions"""
    # GIVEN: A mocked out SerializerBase

    # WHEN: register_classes() is run
    register_classes()

    # THEN: The functions should have been registered
    MockSerializerBase.register_class_to_dict.assert_called_once_with(Path, path_class_to_dict)
    MockSerializerBase.register_dict_to_class.assert_called_once_with('Path', path_dict_to_class)
