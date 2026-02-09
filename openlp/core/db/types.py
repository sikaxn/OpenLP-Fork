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
The :mod:`~openlp.core.db.types` module provides additional database column types
"""
import json
from pathlib import Path

from sqlalchemy.types import TypeDecorator, Unicode, UnicodeText

from openlp.core.common.applocation import AppLocation
from openlp.core.common.json import OpenLPJSONDecoder, OpenLPJSONEncoder


class PathType(TypeDecorator):
    """
    Create a PathType for storing Path objects with SQLAlchemy. Behind the scenes we convert the Path object to a JSON
    representation and store it as a Unicode type
    """
    impl = Unicode
    cache_ok = True

    def coerce_compared_value(self, op, value):
        """
        Some times it make sense to compare a PathType with a string. In the case a string is used coerce the
        PathType to a UnicodeText type.

        :param op: The operation being carried out. Not used, as we only care about the type that is being used with the
            operation.
        :param pathlib.Path | str value: The value being used for the comparison. Most likely a Path Object or str.
        :return PathType | UnicodeText: The coerced value stored in the db
        """
        if isinstance(value, str):
            return UnicodeText()
        else:
            return self

    def process_bind_param(self, value: Path, dialect) -> str:
        """
        Convert the Path object to a JSON representation

        :param pathlib.Path value: The value to convert
        :param dialect: Not used
        :return str: The Path object as a JSON string
        """
        data_path = AppLocation.get_data_path()
        return json.dumps(value, cls=OpenLPJSONEncoder, base_path=data_path)

    def process_result_value(self, value: str, dialect) -> Path:
        """
        Convert the JSON representation back

        :param types.UnicodeText value: The value to convert
        :param dialect: Not used
        :return: The JSON object converted Python object (in this case it should be a Path object)
        :rtype: pathlib.Path
        """
        data_path = AppLocation.get_data_path()
        return json.loads(value, cls=OpenLPJSONDecoder, base_path=data_path)
