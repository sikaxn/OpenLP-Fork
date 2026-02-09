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
from contextlib import suppress
from json import JSONDecoder, JSONEncoder
from pathlib import Path

_registered_classes = {}


class JSONMixin(object):
    """
    :class:`JSONMixin` is a mixin class to simplify the serialization of a subclass to JSON.

    :cvar:`_json_keys` is used to specify the attributes of the subclass that you wish to serialize.
    :vartype _json_keys: list[str]
    :cvar:`_name` set to override the subclass name, useful if using a `proxy` class
    :vartype _name: str
    """
    _json_keys = []
    _name = None
    _version = 1

    def __init_subclass__(cls, register_names=None, **kwargs):
        """
        Register the subclass.

        :param collections.Iterable[str] register_names: Alternative names to register instead of the class name
        :param kwargs: Other args to pass to the super method
        :return None:
        """
        super().__init_subclass__(**kwargs)
        for key in register_names or [cls.__name__]:
            _registered_classes[key] = cls

    @classmethod
    def encode_json(cls, obj, **kwargs):
        """
        Create a instance of the subclass from the dictionary that has been constructed by the JSON representation.
        Only use the keys specified in :cvar:`_json_keys`.

        :param dict[str] obj: The dictionary representation of the subclass (deserailized from the JSON)
        :param kwargs: Contains any extra parameters. Not used!
        :return: The desrialized object
        """
        return cls(**{key: obj[key] for key in cls._json_keys if obj.get(key) is not None})

    @classmethod
    def attach_meta(cls, j_dict):
        """
        Attach meta data to the serialized dictionary.

        :param dict[str] j_dict: The dictionary to update with the meta data
        :return None:
        """
        j_dict.update({'json_meta': {'class': cls._name or cls.__name__, 'version': cls._version}})

    def json_object(self, **kwargs):
        """
        Create a dictionary that can be JSON decoded.

        :param kwargs: Contains any extra parameters. Not used!
        :return dict[str]: The dictionary representation of this Path object.
        """
        j_dict = {key: self.__dict__[key] for key in self._json_keys if self.__dict__.get(key) is not None}
        self.attach_meta(j_dict)
        return j_dict


class OpenLPJSONDecoder(JSONDecoder):
    """
    Implement a custom JSONDecoder to extend compatibility to custom objects

    Example Usage:
        object = json.loads(json_string, cls=OpenLPJsonDecoder)
    """
    def __init__(self, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, strict=True,
                 object_pairs_hook=None, **kwargs):
        """
        Re-implement __init__ so that we can pass in our object_hook method. Any additional kwargs, are stored in the
        instance and are passed to custom objects upon encoding or decoding.
        """
        self.kwargs = kwargs
        if object_hook is None:
            object_hook = self.custom_object_hook
        super().__init__(object_hook=object_hook, parse_float=parse_float, parse_int=parse_int,
                         parse_constant=parse_constant, strict=strict, object_pairs_hook=object_pairs_hook)

    def custom_object_hook(self, obj):
        """
        Implement a custom object decoder.

        :param dict obj: A decoded JSON object
        :return: The custom object from the serialized data if the custom object is registered, else obj
        """
        if '__Path__' in obj:
            return PathSerializer.encode_json(obj, **self.kwargs)
        try:
            key = obj['json_meta']['class']
        except KeyError:
            return obj
        if key in _registered_classes:
            return _registered_classes[key].encode_json(obj, **self.kwargs)
        return obj


class OpenLPJSONEncoder(JSONEncoder):
    """
    Implement a custom JSONEncoder to handle to extend compatibility to custom objects

    Example Usage:
        json_string = json.dumps(object, cls=OpenLPJSONEncoder)
    """
    def __init__(self, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, default=None, **kwargs):
        """
        Re-implement __init__ so that we can pass in additional kwargs, which are stored in the instance and are passed
        to custom objects upon encoding or decoding.
        """
        self.kwargs = kwargs
        if default is None:
            default = self.custom_default
        super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                         allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators,
                         default=default)

    def custom_default(self, obj):
        """
        Convert any registered objects into a dictionary object which can be serialized.

        :param object obj: The object to convert
        :return dict: The serializable object
        """
        if isinstance(obj, JSONMixin):
            return obj.json_object()
        elif obj.__class__.__name__ in _registered_classes:
            return _registered_classes[obj.__class__.__name__].json_object(obj, **self.kwargs)
        return super().default(obj, **self.kwargs)


def is_serializable(obj):
    return obj.__class__.__name__ in _registered_classes


class PathSerializer(JSONMixin, register_names=('Path', 'PosixPath', 'WindowsPath')):
    """
    Implement a de/serializer for pathlib.Path objects
    """
    _name = 'Path'

    @staticmethod
    def encode_json(obj, base_path=None, **kwargs):
        """
        Reimplement encode_json to create a Path object from a dictionary representation.

        :param dict[str] obj: The dictionary representation
        :param Path base_path: If specified, an absolute path to base the relative path off of.
        :param kwargs: Contains any extra parameters. Not used!
        :return Path: The deserialized Path object
        """
        if '__Path__' in obj:
            parts = obj['__Path__']
        else:
            parts = obj['parts']
        path = Path(*parts)
        if base_path and not path.is_absolute():
            return base_path / path
        return path

    @classmethod
    def json_object(cls, obj, base_path=None, is_js=False, **kwargs):
        """
        Create a dictionary that can be JSON decoded.

        :param Path base_path: If specified, an absolute path to make a relative path from.
        :param bool is_js: Encode the path as a uri. For example for use in the js rendering code.
        :param kwargs: Contains any extra parameters. Not used!
        :return: The dictionary representation of this Path object.
        :rtype: dict[tuple]
        """
        path = obj
        if base_path:
            with suppress(ValueError):
                path = path.relative_to(base_path)
        if is_js is True:
            return path.as_uri()
        json_dict = {'parts': path.parts}
        cls.attach_meta(json_dict)
        return json_dict
