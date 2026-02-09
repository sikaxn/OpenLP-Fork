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
the Custom plugin
"""
from sqlalchemy import Column
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import Integer, Unicode, UnicodeText

from openlp.core.common.i18n import get_natural_key
from openlp.core.db.helpers import init_db


Base = declarative_base()


class CustomSlide(Base):
    """
    CustomSlide model
    """
    __tablename__ = 'custom_slide'

    id = Column(Integer, primary_key=True)
    title = Column(Unicode(255), nullable=False)
    text = Column(UnicodeText, nullable=False)
    credits = Column(UnicodeText)
    theme_name = Column(Unicode(128))

    # By default sort the customs by its title considering language specific characters.
    def __lt__(self, other):
        return get_natural_key(self.title) < get_natural_key(other.title)

    def __eq__(self, other):
        return get_natural_key(self.title) == get_natural_key(other.title)

    def __hash__(self):
        """
        Return the hash for a custom slide.
        """
        return self.id


def init_schema(url):
    """
    Setup the custom database connection and initialise the database schema

    :param url:  The database to setup
    """
    session, metadata = init_db(url, base=Base)
    metadata.create_all(bind=metadata.bind, checkfirst=True)
    return session
