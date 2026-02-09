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
The :mod:`upgrade` module provides a way for the database and schema that is the
backend for the projector setup.
"""
import logging

from sqlalchemy import Column, Table, types
from sqlalchemy.sql.expression import null

from openlp.core.db.upgrades import get_upgrade_op


log = logging.getLogger(__name__)

# Initial projector DB was unversioned
__version__ = 3

log.debug('Projector DB upgrade module loading')


def upgrade_1(session, metadata):
    """
    Version 1 upgrade - old db might/might not be versioned.
    """
    log.debug('Skipping projector DB upgrade to version 1 - not used')


def upgrade_2(session, metadata):
    """
    Version 2 upgrade.

    Update Projector() table to include new data defined in PJLink version 2 changes

    mac_adx:        Column(String(18))
    serial_no:      Column(String(30))
    sw_version:     Column(String(30))
    model_filter:   Column(String(30))
    model_lamp:     Column(String(30))

    :param session: DB session instance
    :param metadata: Metadata of current DB
    """
    log.debug('Checking projector DB upgrade to version 2')
    projector_table = Table('projector', metadata, autoload_with=metadata.bind)
    upgrade_db = 'mac_adx' not in [col.name for col in projector_table.c.values()]
    if upgrade_db:
        new_op = get_upgrade_op(session)
        new_op.add_column('projector', Column('mac_adx', types.String(18), server_default=null()))
        new_op.add_column('projector', Column('serial_no', types.String(30), server_default=null()))
        new_op.add_column('projector', Column('sw_version', types.String(30), server_default=null()))
        new_op.add_column('projector', Column('model_filter', types.String(30), server_default=null()))
        new_op.add_column('projector', Column('model_lamp', types.String(30), server_default=null()))
    log.debug('{status} projector DB upgrade to version 2'.format(status='Updated' if upgrade_db else 'Skipping'))


def upgrade_3(session, metadata):
    """
    Version 3 upgrade.

    Update Projector() table to inlcude PJLink class as part of record.

    pjlink_version:     Column(String(1))

    :param session: DB Session instance
    :param metadata: Metadata of current DB
    """
    log.debug('Checking projector DB upgrade to version 3')
    projector_table = Table('projector', metadata, autoload_with=metadata.bind)
    upgrade_db = 'pjlink_class' not in [col.name for col in projector_table.c.values()]
    if upgrade_db:
        new_op = get_upgrade_op(session)
        new_op.add_column('projector', Column('pjlink_class', types.String(5), server_default=null()))
    log.debug('{status} projector DB upgrade to version 3'.format(status='Updated' if upgrade_db else 'Skipping'))
