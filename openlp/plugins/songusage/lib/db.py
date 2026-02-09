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
The :mod:`db` module provides the database and schema that is the backend for
the SongUsage plugin
"""

from sqlalchemy import Column
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.types import Integer, Date, Time, Unicode

from openlp.core.db.helpers import init_db


Base = declarative_base()


class SongUsageItem(Base):
    """
    SongUsageItem model
    """
    __tablename__ = 'songusage_data'

    id = Column(Integer, primary_key=True)
    usagedate = Column(Date, index=True, nullable=False)
    usagetime = Column(Time, index=True, nullable=False)
    title = Column(Unicode(255), nullable=False)
    authors = Column(Unicode(255), nullable=False)
    copyright = Column(Unicode(255))
    ccl_number = Column(Unicode(65))
    plugin_name = Column(Unicode(20))
    source = Column(Unicode(10))


def init_schema(url: str) -> Session:
    """
    Setup the songusage database connection and initialise the database schema

    :param url: The database to setup
    """
    session, metadata = init_db(url, base=Base)
    metadata.create_all(bind=metadata.bind, checkfirst=True)
    return session
