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
backend for the SongsUsage plugin
"""
import logging

from sqlalchemy import Column, Table, types

from openlp.core.db.upgrades import get_upgrade_op


log = logging.getLogger(__name__)
__version__ = 2


def upgrade_1(session, metadata):
    """
    Version 1 upgrade

    Skip due to possible missed update from a 2.4-2.6 upgrade
    """
    pass


def upgrade_2(session, metadata):
    """
    Version 2 upgrade.

    This upgrade adds two new fields to the songusage database

    :param session: SQLAlchemy Session object
    :param metadata: SQLAlchemy MetaData object
    """
    op = get_upgrade_op(session)
    songusage_table = Table('songusage_data', metadata, autoload_with=metadata.bind)
    if 'plugin_name' not in [col.name for col in songusage_table.c.values()]:
        op.add_column('songusage_data', Column('plugin_name', types.Unicode(20), server_default=''))
        op.add_column('songusage_data', Column('source', types.Unicode(10), server_default=''))
