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
The :mod:`~openlp.core.db.mixins` module provides some database mixins for OpenLP
"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship


class CommonMixin(object):
    """
    Base class to automate table name and ID column.
    """
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)


class FolderMixin(CommonMixin):
    """
    A mixin to provide most of the fields needed for folder support
    """
    name = Column(Unicode(255), nullable=False, index=True)

    @declared_attr
    def parent_id(self):
        return Column(Integer, ForeignKey('folder.id'))

    @declared_attr
    def folders(self):
        return relationship('Folder', backref=backref('parent', remote_side='Folder.id'), order_by='Folder.name')

    @declared_attr
    def items(self):
        return relationship('Item', backref='folder', order_by='Item.name')


class ItemMixin(CommonMixin):
    """
    A mixin to provide most of the fields needed for folder support
    """
    name = Column(Unicode(255), nullable=False, index=True)
    file_path = Column(Unicode(255))
    file_hash = Column(Unicode(255))

    @declared_attr
    def folder_id(self):
        return Column(Integer, ForeignKey('folder.id'))
