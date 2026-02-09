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
Package to test the openlp.core.common.json package.
"""
import json
import os
from pathlib import Path
from unittest.mock import patch

from openlp.core.common.json import JSONMixin, OpenLPJSONDecoder, OpenLPJSONEncoder, PathSerializer, _registered_classes
from openlp.core.common.platform import is_win


class BaseTestClass(object):
    """
    Simple class to avoid repetition
    """
    def __init__(self, a=None, b=None, c=None):
        self.a = a
        self.b = b
        self.c = c


@patch.dict(_registered_classes, clear=True)
def test_subclass_json_mixin():
    """
    Test that a class is `registered` when subclassing JSONMixin
    """
    # GIVEN: The JSONMixin class
    # WHEN: Subclassing it
    class TestClass(JSONMixin):
        pass

    # THEN: The TestClass should have been `registered`
    assert _registered_classes['TestClass'] == TestClass


@patch.dict(_registered_classes, clear=True)
def test_subclass_json_mixin_alt_names():
    """
    Test that a class is `registered` using the specified names when subclassing JSONMixin
    """
    # GIVEN: The JSONMixin class
    # WHEN: Subclassing it with custom names
    class TestClass(JSONMixin, register_names=('AltName1', 'AltName2')):
        pass

    # THEN: The TestClass should have been registered with only those names
    assert 'TestClass' not in _registered_classes
    assert _registered_classes['AltName1'] == TestClass
    assert _registered_classes['AltName2'] == TestClass


@patch.dict(_registered_classes, clear=True)
def test_encoding_json_mixin_subclass():
    """
    Test that an instance of a JSONMixin subclass is properly serialized to a JSON string
    """
    # GIVEN: A instance of a subclass of the JSONMixin class
    class TestClass(BaseTestClass, JSONMixin):
        _json_keys = ['a', 'b']

    instance = TestClass(a=1, c=2)

    # WHEN: Serializing the instance
    json_string = json.dumps(instance, cls=OpenLPJSONEncoder)

    # THEN: Only the attributes specified by `_json_keys` should be serialized, and only if they have been set
    assert json_string == '{"a": 1, "json_meta": {"class": "TestClass", "version": 1}}'


@patch.dict(_registered_classes, clear=True)
def test_decoding_json_mixin_subclass():
    """
    Test that an instance of a JSONMixin subclass is properly deserialized from a JSON string
    """
    # GIVEN: A subclass of the JSONMixin class
    class TestClass(BaseTestClass, JSONMixin):
        _json_keys = ['a', 'b']

    # WHEN: Deserializing a JSON representation of the TestClass
    instance = json.loads(
        '{"a": 1, "c": 2, "json_meta": {"class": "TestClass", "version": 1}}', cls=OpenLPJSONDecoder)

    # THEN: Only the attributes specified by `_json_keys` should have been set
    assert instance.__class__ == TestClass
    assert instance.a == 1
    assert instance.b is None
    assert instance.c is None


@patch.dict(_registered_classes, clear=True)
def test_encoding_json_mixin_subclass_custom_name():
    """
    Test that an instance of a JSONMixin subclass is properly serialized to a JSON string when using a custom name
    """
    # GIVEN: A instance of a subclass of the JSONMixin class with a custom name
    class TestClass(BaseTestClass, JSONMixin, register_names=('AltName', )):
        _json_keys = ['a', 'b']
        _name = 'AltName'
        _version = 2

    instance = TestClass(a=1, c=2)

    # WHEN: Serializing the instance
    json_string = json.dumps(instance, cls=OpenLPJSONEncoder)

    # THEN: Only the attributes specified by `_json_keys` should be serialized, and only if they have been set
    assert json_string == '{"a": 1, "json_meta": {"class": "AltName", "version": 2}}'


@patch.dict(_registered_classes, clear=True)
def test_decoding_json_mixin_subclass_custom_name():
    """
    Test that an instance of a JSONMixin subclass is properly deserialized from a JSON string when using a custom
    name
    """
    # GIVEN: A instance of a subclass of the JSONMixin class with a custom name
    class TestClass(BaseTestClass, JSONMixin, register_names=('AltName', )):
        _json_keys = ['a', 'b']
        _name = 'AltName'
        _version = 2

    # WHEN: Deserializing a JSON representation of the TestClass
    instance = json.loads(
        '{"a": 1, "c": 2, "json_meta": {"class": "AltName", "version": 2}}', cls=OpenLPJSONDecoder)

    # THEN: Only the attributes specified by `_json_keys` should have been set
    assert instance.__class__ == TestClass
    assert instance.a == 1
    assert instance.b is None
    assert instance.c is None


def test_object_hook_path_object():
    """
    Test the object_hook method when called with a decoded Path JSON object
    """
    # GIVEN: An instance of OpenLPJsonDecoder
    instance = OpenLPJSONDecoder()

    # WHEN: Calling the object_hook method with a decoded JSON object which contains a Path
    result = instance.object_hook({'parts': ['test', 'path'], "json_meta": {"class": "Path", "version": 1}})

    # THEN: A Path object should be returned
    assert result == Path('test', 'path')


def test_object_hook_non_path_object():
    """
    Test the object_hook method when called with a decoded JSON object
    """
    # GIVEN: An instance of OpenLPJsonDecoder
    instance = OpenLPJSONDecoder()

    # WHEN: Calling the object_hook method with a decoded JSON object which contains a Path
    with patch('openlp.core.common.json.Path') as mocked_path:
        result = instance.object_hook({'key': 'value'})

        # THEN: The object should be returned unchanged and a Path object should not have been initiated
        assert result == {'key': 'value'}
        assert mocked_path.called is False


def test_json_decode():
    """
    Test the OpenLPJsonDecoder when decoding a JSON string
    """
    # GIVEN: A JSON encoded string
    json_string = '[{"parts": ["test", "path1"], "json_meta": {"class": "Path", "version": 1}}, ' \
                  '{"parts": ["test", "path2"], "json_meta": {"class": "Path", "version": 1}}, ' \
                  '{"key": "value", "json_meta": {"class": "Object"}}]'

    # WHEN: Decoding the string using the OpenLPJsonDecoder class
    obj = json.loads(json_string, cls=OpenLPJSONDecoder)

    # THEN: The object returned should be a python version of the JSON string
    assert obj == [Path('test', 'path1'), Path('test', 'path2'), {'key': 'value', 'json_meta': {'class': 'Object'}}]


def test_json_decode_old_style():
    """
    Test the OpenLPJsonDecoder when decoding a JSON string with an old-style Path object
    """
    # GIVEN: A JSON encoded string
    json_string = '[{"__Path__": ["test", "path1"]}, ' \
                  '{"__Path__": ["test", "path2"]}]'

    # WHEN: Decoding the string using the OpenLPJsonDecoder class
    obj = json.loads(json_string, cls=OpenLPJSONDecoder)

    # THEN: The object returned should be a python version of the JSON string
    assert obj == [Path('test', 'path1'), Path('test', 'path2')]


def test_default_path_object():
    """
    Test the default method when called with a Path object
    """
    # GIVEN: An instance of OpenLPJSONEncoder
    instance = OpenLPJSONEncoder()

    # WHEN: Calling the default method with a Path object
    result = instance.default(Path('test', 'path'))

    # THEN: A dictionary object that can be JSON encoded should be returned
    assert result == {'parts': ('test', 'path'), "json_meta": {"class": "Path", "version": 1}}


def test_default_non_path_object():
    """
    Test the default method when called with a object other than a Path object
    """
    with patch('openlp.core.common.json.JSONEncoder.default') as mocked_super_default:

        # GIVEN: An instance of OpenLPJSONEncoder
        instance = OpenLPJSONEncoder()

        # WHEN: Calling the default method with a object other than a Path object
        instance.default('invalid object')

        # THEN: default method of the super class should have been called
        mocked_super_default.assert_called_once_with('invalid object')


def test_json_encode():
    """
    Test the OpenLPJsonDEncoder when encoding an object conatining Path objects
    """
    # GIVEN: A list of Path objects
    obj = [Path('test', 'path1'), Path('test', 'path2')]

    # WHEN: Encoding the object using the OpenLPJSONEncoder class
    json_string = json.dumps(obj, cls=OpenLPJSONEncoder)

    # THEN: The JSON string return should be a representation of the object encoded
    assert json_string == '[{"parts": ["test", "path1"], "json_meta": {"class": "Path", "version": 1}}, ' \
                          '{"parts": ["test", "path2"], "json_meta": {"class": "Path", "version": 1}}]'


def test_path_encode_json():
    """
    Test that `Path.encode_json` returns a Path object from a dictionary representation of a Path object decoded
    from JSON
    """
    # GIVEN: A Path object from openlp.core.common.path
    # WHEN: Calling encode_json, with a dictionary representation
    path = PathSerializer.encode_json(
        {'parts': ['path', 'to', 'fi.le'], "json_meta": {"class": "Path", "version": 1}}, extra=1, args=2)

    # THEN: A Path object should have been returned
    assert path == Path('path', 'to', 'fi.le')


def test_path_encode_json_base_path():
    """
    Test that `Path.encode_json` returns a Path object from a dictionary representation of a Path object decoded
    from JSON when the base_path arg is supplied.
    """
    # GIVEN: A Path object from openlp.core.common.path
    # WHEN: Calling encode_json, with a dictionary representation
    path = PathSerializer.encode_json(
        {'parts': ['path', 'to', 'fi.le'], "json_meta": {"class": "Path", "version": 1}}, base_path=Path('/base'))

    # THEN: A Path object should have been returned with an absolute path
    assert path == Path('/', 'base', 'path', 'to', 'fi.le')


def test_path_json_object():
    """
    Test that `Path.json_object` creates a JSON decode-able object from a Path object
    """
    # GIVEN: A Path object from openlp.core.common.path
    path = Path('/base', 'path', 'to', 'fi.le')

    # WHEN: Calling json_object
    obj = PathSerializer().json_object(path, extra=1, args=2)

    # THEN: A JSON decodeable object should have been returned.
    assert obj == {'parts': (os.sep, 'base', 'path', 'to', 'fi.le'), "json_meta": {"class": "Path", "version": 1}}


def test_path_json_object_is_js():
    """
    Test that `Path.json_object` creates a JSON decode-able object from a Path object
    """
    # GIVEN: A Path object from openlp.core.common.path
    if is_win():
        path = Path('c:\\', 'base', 'path', 'to', 'fi.le')
    else:
        path = Path('/base', 'path', 'to', 'fi.le')

    # WHEN: Calling json_object
    obj = PathSerializer().json_object(path, is_js=True, extra=1, args=2)

    # THEN: A URI should be returned
    if is_win():
        assert obj == 'file:///c:/base/path/to/fi.le'
    else:
        assert obj == 'file:///base/path/to/fi.le'


def test_path_json_object_base_path():
    """
    Test that `Path.json_object` creates a JSON decode-able object from a Path object, that is relative to the
    base_path
    """
    # GIVEN: A Path object from openlp.core.common.path
    path = Path('/base', 'path', 'to', 'fi.le')

    # WHEN: Calling json_object with a base_path
    obj = PathSerializer().json_object(path, base_path=Path('/', 'base'))

    # THEN: A JSON decodable object should have been returned.
    assert obj == {'parts': ('path', 'to', 'fi.le'), "json_meta": {"class": "Path", "version": 1}}
