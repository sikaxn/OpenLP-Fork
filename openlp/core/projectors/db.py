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
:mod:`openlp.core.lib.projector.db` module

Provides the database functions for the Projector module.

The Manufacturer, Model, Source tables keep track of the video source
strings used for display of input sources. The Source table maps
manufacturer-defined or user-defined strings from PJLink default strings
to end-user readable strings; ex: PJLink code 11 would map "RGB 1"
default string to "RGB PC (analog)" string.
(Future feature).

The Projector table keeps track of entries for controlled projectors.
"""

import logging

from sqlalchemy import Column, ForeignKey, Integer, String, and_
from sqlalchemy.orm import declarative_base, relationship

from openlp.core.db.helpers import init_db, init_url
from openlp.core.db.manager import DBManager
from openlp.core.db.mixins import CommonMixin
from openlp.core.projectors import upgrade
from openlp.core.projectors.constants import PJLINK_DEFAULT_CODES


log = logging.getLogger(__name__)
log.debug('projector.lib.db module loaded')


Base = declarative_base()


class Manufacturer(Base, CommonMixin):
    """
    Projector manufacturer table.

    Manufacturer:
        name:   Column(String(30))
        models: Relationship(Model.id)

    Model table is related.
    """
    def __repr__(self):
        """
        Returns a basic representation of a Manufacturer table entry.
        """
        return '<Manufacturer(name="{name}")>'.format(name=self.name)

    name = Column(String(30))
    models = relationship('Model',
                          order_by='Model.name',
                          backref='manufacturer',
                          cascade='all, delete-orphan',
                          primaryjoin='Manufacturer.id==Model.manufacturer_id',
                          lazy='joined')


class Model(Base, CommonMixin):
    """
    Projector model table.

    Model:
        name:               Column(String(20))
        sources:            Relationship(Source.id)
        manufacturer_id:    Foreign_key(Manufacturer.id)

    Manufacturer table links here.
    Source table is related.
    """
    def __repr__(self):
        """
        Returns a basic representation of a Model table entry.
        """
        return '<Model(name={name})>'.format(name=self.name)

    manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
    name = Column(String(20))
    sources = relationship('Source',
                           order_by='Source.pjlink_name',
                           backref='model',
                           cascade='all, delete-orphan',
                           primaryjoin='Model.id==Source.model_id',
                           lazy='joined')


class Source(Base, CommonMixin):
    """
    Projector video source table.

    Source:
        pjlink_name:    Column(String(15))
        pjlink_code:    Column(String(2))
        text:           Column(String(30))
        model_id:       Foreign_key(Model.id)

    Model table links here.

    These entries map PJLink input video source codes to text strings.
    """
    def __repr__(self):
        """
        Return basic representation of Source table entry.
        """
        return '<Source(pjlink_name="{name}", pjlink_code="{code}", text="{text}")>'.format(name=self.pjlink_name,
                                                                                            code=self.pjlink_code,
                                                                                            text=self.text)
    model_id = Column(Integer, ForeignKey('model.id'))
    pjlink_name = Column(String(15))
    pjlink_code = Column(String(2))
    text = Column(String(30))


class Projector(Base, CommonMixin):
    """
    Projector table.

    Projector:
        ip:             Column(String(100))  # Allow for IPv6 or FQDN
        port:           Column(String(8))
        pin:            Column(String(20))   # Allow for test strings
        name:           Column(String(20))
        location:       Column(String(30))
        notes:          Column(String(200))
        pjlink_name:    Column(String(128))  # From projector
        pjlink_class    Column(String(5))    # From projector
        manufacturer:   Column(String(128))  # From projector
        model:          Column(String(128))  # From projector
        other:          Column(String(128))  # From projector
        sources:        Column(String(128))  # From projector
        serial_no:      Column(String(30))   # From projector (Class 2)
        sw_version:     Column(String(30))   # From projector (Class 2)
        model_filter:   Column(String(30))   # From projector (Class 2)
        model_lamp:     Column(String(30))   # From projector (Class 2)

        ProjectorSource relates
    """
    def __repr__(self):
        """
        Return basic representation of Source table entry.
        """
        return f'< Projector(id="{self.id}", ip="{self.ip}", port="{self.port}", mac_adx="{self.mac_adx}", ' \
            f'pin="{self.pin}", name="{self.name}", location="{self.location}", notes="{self.notes}", ' \
            f'pjlink_name="{self.pjlink_name}", pjlink_class="{self.pjlink_class}", ' \
            f'manufacturer="{self.manufacturer}", model="{self.model}", serial_no="{self.serial_no}", ' \
            f'other="{self.other}", sources="{self.sources}", source_list="{self.source_list}", ' \
            f'model_filter="{self.model_filter}", model_lamp="{self.model_lamp}", ' \
            f'sw_version="{self.sw_version}") >'

    def __eq__(self, other):
        if not isinstance(other, Projector):
            return False
        # Does not check self.id == other.id
        return \
            self.ip == other.ip and \
            self.port == other.port and \
            self.mac_adx == other.mac_adx and \
            self.pin == other.pin and \
            self.name == other.name and \
            self.location == other.location and \
            self.notes == other.notes and \
            self.pjlink_name == other.pjlink_name and \
            self.pjlink_class == other.pjlink_class and \
            self.manufacturer == other.manufacturer and \
            self.model == other.model and \
            self.other == other.other and \
            self.serial_no == other.serial_no and \
            self.sw_version == other.sw_version and \
            self.model_filter == other.model_filter and \
            self.model_lamp == other.model_lamp

    ip = Column(String(100))
    port = Column(String(8))
    mac_adx = Column(String(18))
    pin = Column(String(20))
    name = Column(String(20))
    location = Column(String(30))
    notes = Column(String(200))
    pjlink_name = Column(String(128))
    pjlink_class = Column(String(5))
    manufacturer = Column(String(128))
    model = Column(String(128))
    other = Column(String(128))
    sources = Column(String(128))
    serial_no = Column(String(30))
    sw_version = Column(String(30))
    model_filter = Column(String(30))
    model_lamp = Column(String(30))
    source_list = relationship('ProjectorSource', order_by='ProjectorSource.code', back_populates='projector',
                               cascade='all, delete-orphan')


class ProjectorSource(Base, CommonMixin):
    """
    Projector local source table
    This table allows mapping specific projector source input to a local
    connection; i.e., '11': 'DVD Player'

    Projector Source:
        projector_id:   Foreign_key(Column(Projector.id))
        code:           Column(String(3)) #  PJLink source code
        text:           Column(String(20))  # Text to display

    Projector table links here
    """
    def __repr__(self):
        """
        Return basic representation of Source table entry.
        """
        return '<ProjectorSource(id="{data}", code="{code}", text="{text}", ' \
            'projector_id="{projector_id}")>'.format(data=self.id,
                                                     code=self.code,
                                                     text=self.text,
                                                     projector_id=self.projector_id)
    code = Column(String(3))
    text = Column(String(20))
    projector_id = Column(Integer, ForeignKey('projector.id'))

    projector = relationship('Projector', back_populates='source_list')


class ProjectorDB(DBManager):
    """
    Class to access the projector database.
    """
    def __init__(self, *args, **kwargs):
        log.debug('ProjectorDB().__init__(args="{arg}", kwargs="{kwarg}")'.format(arg=args, kwarg=kwargs))
        super().__init__(plugin_name='projector',
                         init_schema=self.init_schema,
                         upgrade_mod=upgrade)
        log.debug('ProjectorDB() Initialized using db url {db}'.format(db=self.db_url))
        log.debug('Session: {session}'.format(session=self.session))

    def init_schema(self, *args, **kwargs):
        """
        Setup the projector database and initialize the schema.

        Declarative uses table classes to define schema.
        """
        self.db_url = init_url('projector')
        session, metadata = init_db(self.db_url, base=Base)
        metadata.create_all(bind=metadata.bind, checkfirst=True)
        return session

    def get_projector(self, *args, **kwargs):
        """
        Get projector instance(s) in database

        If projector=Projector() instance, use projector as filter object.

        id=<int> or projector.id is not None: Filter by record.id
        name=<str> or projector.name is not None: Filter by record.name
        ip=<str> or projector.ip is not None: Filter by record.ip
        port=<str> or projector.port is not None: Filter by record.port

        Any other options ignored

        In order:
            id returns 1 record - all other following options ignored
            name returns 1 record - all other following options ignored
            ip AND port returns 1 record
            ip only may return 1+ records
            port only may return 1+ records

        :returns: None if no record found, otherwise list
        """
        db_filter = []
        projector = Projector() if 'projector' not in kwargs else kwargs['projector']
        if projector.id is None and 'id' in kwargs:
            projector.id = int(kwargs['id'])
        if projector.name is None and 'name' in kwargs:
            projector.name = kwargs['name']
        if projector.ip is None and 'ip' in kwargs:
            projector.ip = kwargs['ip']
        if projector.port is None and 'port' in kwargs:
            projector.port = kwargs['port']

        if projector.id is not None:
            log.debug('Filter by ID')
            db_filter.append(Projector.id == projector.id)
        elif projector.name is not None:
            log.debug('Filter by Name')
            db_filter.append(Projector.name == projector.name)
        else:
            p = ''
            if projector.ip is not None:
                db_filter.append(Projector.ip == projector.ip)
                p += " IP"
            if projector.port is not None:
                db_filter.append(Projector.port == projector.port)
                p += " Port"
            if len(p) > 0:
                log.debug(f'Filter by{p}')

        if len(db_filter) < 1:
            log.warning('get_projector(): No valid query found - cancelled')
            return None

        return self.get_all_objects(Projector, db_filter)

    def get_projector_by_id(self, dbid):
        """
        Locate a DB record by record ID.

        :param dbid: DB record id
        :returns: Projector() instance
        """
        log.debug('get_projector_by_id(id="{data}")'.format(data=dbid))
        projector = self.get_object(Projector, dbid)
        if projector is None:
            # Not found
            log.warning('get_projector_by_id() did not find {data}'.format(data=id))
            return None
        log.debug('get_projectorby_id() returning 1 entry for "{entry}" id="{data}"'.format(entry=dbid,
                                                                                            data=projector.id))
        return projector

    def get_projector_all(self):
        """
        Retrieve all projector entries.

        :returns: List with Projector() instances used in Manager() QListWidget.
        """
        log.debug('get_all() called')
        return_list = []
        new_list = self.get_all_objects(Projector)
        if new_list is None or new_list.count == 0:
            return return_list
        for new_projector in new_list:
            return_list.append(new_projector)
        log.debug('get_all() returning {items} item(s)'.format(items=len(return_list)))
        return return_list

    def get_projector_by_ip(self, ip):
        """
        Locate a projector by host IP/Name.

        :param ip: Host IP/Name
        :returns: Projector() instance
        """
        log.debug('get_projector_by_ip(ip="{ip}")'.format(ip=ip))
        projector = self.get_object_filtered(Projector, Projector.ip == ip)
        if projector is None:
            # Not found
            log.warning('get_projector_by_ip() did not find {ip}'.format(ip=ip))
            return None
        log.debug('get_projectorby_ip() returning 1 entry for "{ip}" id="{data}"'.format(ip=ip,
                                                                                         data=projector.id))
        return projector

    def get_projector_by_name(self, name):
        """
        Locate a projector by name field

        :param name: Name of projector
        :returns: Projector() instance
        """
        log.debug('get_projector_by_name(name="{name}")'.format(name=name))
        projector = self.get_object_filtered(Projector, Projector.name == name)
        if projector is None:
            # Not found
            log.warning('get_projector_by_name() did not find "{name}"'.format(name=name))
            return None
        log.debug('get_projector_by_name() returning one entry for "{name}" id="{data}"'.format(name=name,
                                                                                                data=projector.id))
        return projector

    def add_projector(self, projector):
        """
        Add a new projector entry

        :param projector: Projector() instance to add
        :returns: bool
                  True if entry added
                  False if entry already in DB or db error
        """
        old_projector = self.get_object_filtered(Projector,
                                                 Projector.ip == projector.ip,
                                                 Projector.port == projector.port)
        if old_projector is not None:
            log.warning(f'add_projector() Duplicate record ip={old_projector} port={old_projector.port}')
            return False
        log.debug(f'add_projector() saving new entry name="{projector.name}" ip={projector.ip} port={projector.port}')
        return self.save_object(projector)

    def update_projector(self, projector=None):
        """
        Update projector entry

        :param projector: Projector() instance with new information
        :returns: bool
                  True if DB record updated
                  False if entry not in DB or DB error
        """
        if projector is None:
            log.error('No Projector() instance to update - cancelled')
            return False
        old_projector = self.get_object_filtered(Projector, Projector.id == projector.id)
        if old_projector is None:
            log.error('Edit called on projector instance not in database - cancelled')
            return False
        log.debug('({ip}) Updating projector with dbid={dbid}'.format(ip=projector.ip, dbid=projector.id))
        old_projector.ip = projector.ip
        old_projector.name = projector.name
        old_projector.location = projector.location
        old_projector.pin = projector.pin
        old_projector.port = projector.port
        old_projector.pjlink_name = projector.pjlink_name
        old_projector.manufacturer = projector.manufacturer
        old_projector.model = projector.model
        old_projector.other = projector.other
        old_projector.sources = projector.sources
        old_projector.serial_no = projector.serial_no
        old_projector.sw_version = projector.sw_version
        old_projector.model_filter = projector.model_filter
        old_projector.model_lamp = projector.model_lamp
        return self.save_object(old_projector)

    def delete_projector(self, projector):
        """
        Delete an entry by record id

        :param projector: Projector() instance to delete
        :returns: bool
                  True if record deleted
                  False if DB error
        """
        deleted = self.delete_object(Projector, projector.id)
        if deleted:
            log.debug('delete_by_id() Removed entry id="{data}"'.format(data=projector.id))
        else:
            log.error('delete_by_id() Entry id="{data}" not deleted for some reason'.format(data=projector.id))
        return deleted

    def get_source_list(self, projector):
        """
        Retrieves the source inputs pjlink code-to-text if available based on
        manufacturer and model.
        If not available, then returns the PJLink code to default text.

        :param projector: Projector instance
        :returns: dict
                  key: (str) PJLink code for source
                  value: (str) From ProjectorSource, Sources tables or PJLink default code list
        """
        source_dict = {}
        # Apparently, there was a change to the projector object. Test for which object has db id
        if hasattr(projector, 'entry') and hasattr(projector.entry, 'id'):
            chk = projector.entry.id
        else:
            chk = projector.id

        # Get default list first
        for key in projector.source_available:
            item = self.get_object_filtered(ProjectorSource,
                                            and_(ProjectorSource.code == key,
                                                 ProjectorSource.projector_id == chk))
            if item is None:
                source_dict[key] = PJLINK_DEFAULT_CODES[key]
            else:
                source_dict[key] = item.text
        return source_dict

    def get_source_by_id(self, source):
        """
        Retrieves the ProjectorSource by ProjectorSource.id

        :param source: ProjectorSource id
        :returns: ProjetorSource instance or None
        """
        source_entry = self.get_object_filtered(ProjectorSource, ProjectorSource.id == source)
        if source_entry is None:
            # Not found
            log.warning('get_source_by_id() did not find "{source}"'.format(source=source))
            return None
        log.debug('get_source_by_id() returning one entry for "{source}""'.format(source=source))
        return source_entry

    def get_source_by_code(self, code, projector_id):
        """
        Retrieves the ProjectorSource by ProjectorSource.id

        :param source: PJLink ID
        :param projector_id: Projector.id
        :returns: ProjetorSource instance or None
        """
        source_entry = self.get_object_filtered(ProjectorSource,
                                                and_(ProjectorSource.code == code,
                                                     ProjectorSource.projector_id == projector_id))

        if source_entry is None:
            # Not found
            log.warning('get_source_by_id() not found')
            log.warning('code="{code}" projector_id="{data}"'.format(code=code, data=projector_id))
            return None
        log.debug('get_source_by_id() returning one entry')
        log.debug('code="{code}" projector_id="{data}"'.format(code=code, data=projector_id))
        return source_entry

    def add_source(self, source):
        """
        Add a new ProjectorSource record

        :param source: ProjectorSource() instance to add
        """
        log.debug('Saving ProjectorSource(projector_id="{data}" '
                  'code="{code}" text="{text}")'.format(data=source.projector_id, code=source.code, text=source.text))
        return self.save_object(source)
