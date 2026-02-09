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
The :mod:`~openlp.plugins.presentations.lib.db` module contains the database layer for the presentations plugin
"""
from sqlalchemy.orm import declarative_base

from openlp.core.db.helpers import init_db, init_url
from openlp.core.db.mixins import FolderMixin, ItemMixin

Base = declarative_base()


class Folder(Base, FolderMixin):
    """A folder holds items or other folders"""


class Item(Base, ItemMixin):
    """An item is something that can be contained within a folder"""


def init_schema(*args, **kwargs):
    """
    Set up the media database and initialise the schema
    """
    session, metadata = init_db(init_url('presentations'), base=Base)
    metadata.create_all(bind=metadata.bind, checkfirst=True)
    return session
