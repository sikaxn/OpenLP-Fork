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
The :mod:`~openlp.core.display.window` module contains the display window
"""
import logging
import re
import time

from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)


def wait_for(check_func, error_message='Timed out waiting for completion', timeout=10):
    """
    Wait until web engine page loaded
    :return boolean: True on success, False on timeout
    """
    # Timeout in 10 seconds
    end_time = time.time() + timeout
    app = Registry().get('application')
    success = True
    while not check_func():
        now = time.time()
        if now > end_time:
            log.error(error_message)
            success = False
            break
        time.sleep(0.001)
        app.process_events()
    return success


def is_uuid(uuid):
    if not isinstance(uuid, (str, bytes)):
        return False
    return (
        re.match(r'^[0-9A-F]{8}-[0-9A-F]{4}-[14][0-9A-F]{3}-[0-9A-F]{4}-[0-9A-F]{12}$', uuid, re.IGNORECASE) is not None
    )
