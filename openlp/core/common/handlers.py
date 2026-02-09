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
Some exception handling functions
"""
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from PySide6 import QtWidgets

from openlp.core.common.i18n import translate


log = logging.getLogger(__name__)


@contextmanager
def handle_permission_error(filepath: Path, parent: Optional[QtWidgets.QWidget] = None):
    try:
        yield
    except PermissionError:
        log.exception(f'Permission denied when accessing {filepath}')
        QtWidgets.QMessageBox.critical(
            parent,
            translate('OpenLP.Handlers', 'Permission Error'),
            translate('OpenLP.Handlers', 'There was a permissions error when trying to access '
                      '{filename}').format(filename=filepath)
        )
