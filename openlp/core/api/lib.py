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
The OpenLP API library.
"""

from functools import wraps
import xml.etree.ElementTree as ElementTree

from flask import Response, request
from openlp.core.common.registry import Registry


def login_required(f):
    """
    Checks if a login is required.

    :param: f: The function to call.
    :type f: function
    :return: The decorated function.
    :rtype: function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not Registry().get('settings_thread').value('api/authentication enabled'):
            return f(*args, **kwargs)
        token = request.headers.get('Authorization', '')
        if token == Registry().get('authentication_token'):
            return f(*args, **kwargs)
        return '', 401
    return decorated


def _serialise_xml_value(parent, value, element_name='item'):
    """
    Serialise a Python value into XML child elements under ``parent``.

    :param parent: The parent XML element.
    :type parent: xml.etree.ElementTree.Element
    :param value: The value to serialise.
    :type value: Any
    :param element_name: Element name used for list items.
    :type element_name: str
    """
    if isinstance(value, dict):
        for key, child_value in value.items():
            child = ElementTree.SubElement(parent, str(key))
            _serialise_xml_value(child, child_value, element_name='item')
    elif isinstance(value, list):
        for list_value in value:
            child = ElementTree.SubElement(parent, element_name)
            _serialise_xml_value(child, list_value, element_name='item')
    elif isinstance(value, bool):
        parent.text = str(value).lower()
    elif value is None:
        parent.text = ''
    else:
        parent.text = str(value)


def xml_response(data, root_name='response'):
    """
    Convert Python data to XML and return it as a Flask response.

    :param data: The data to serialise.
    :type data: Any
    :param root_name: The name for the root XML element.
    :type root_name: str
    :return: XML flask response.
    :rtype: flask.Response
    """
    root = ElementTree.Element(root_name)
    _serialise_xml_value(root, data)
    xml_string = ElementTree.tostring(root, encoding='unicode')
    xml_payload = '<?xml version="1.0" encoding="UTF-8"?>\n{xml}'.format(xml=xml_string)
    return Response(xml_payload, mimetype='application/xml')
