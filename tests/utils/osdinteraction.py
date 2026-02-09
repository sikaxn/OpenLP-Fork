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
The :mod:`osdinteraction` provides miscellaneous functions for interacting with
OSD files.
"""
import json
import os

from tests.utils.constants import TEST_RESOURCES_PATH


def read_service_from_file(file_name):
    """
    Reads an OSD file and returns the first service item found therein.
    @param file_name: File name of an OSD file residing in the tests/resources folder.
    @return: The service contained in the file.
    """
    service_file = os.path.join(TEST_RESOURCES_PATH, 'service', file_name)
    with open(service_file, 'r') as open_file:
        service = json.load(open_file)
    return service
