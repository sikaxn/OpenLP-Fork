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
The :mod:`~openlp.core.db.upgrades` module contains the database upgrade functionality
"""
import logging
from types import ModuleType
from typing import Tuple

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Column
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.types import Unicode, UnicodeText

from openlp.core.db.helpers import database_exists, init_db

log = logging.getLogger(__name__)


def get_upgrade_op(session: Session) -> Operations:
    """
    Create a migration context and an operations object for performing upgrades.

    :param session: The SQLAlchemy session object.
    """
    context = MigrationContext.configure(session.bind.connect())
    return Operations(context)


def upgrade_db(url: str, upgrade: ModuleType) -> Tuple[int, int]:
    """
    Upgrade a database.

    :param url: The url of the database to upgrade.
    :param upgrade: The python module that contains the upgrade instructions.
    """
    log.debug('Checking upgrades for DB {db}'.format(db=url))

    if not database_exists(url):
        log.warning("Database {db} doesn't exist - skipping upgrade checks".format(db=url))
        return 0, 0

    Base = declarative_base()

    class Metadata(Base):
        """
        Provides a class for the metadata table.
        """
        __tablename__ = 'metadata'
        key = Column(Unicode(64), primary_key=True)
        value = Column(UnicodeText(), default=None)

    session, metadata = init_db(url, base=Base)
    metadata.create_all(bind=metadata.bind, checkfirst=True)

    version_meta = session.get(Metadata, 'version')
    if version_meta:
        version = int(version_meta.value)
    else:
        # Due to issues with other checks, if the version is not set in the DB then default to 0
        # and let the upgrade function handle the checks
        version = 0
        version_meta = Metadata(key='version', value=version)
        session.add(version_meta)
        session.commit()
    if version > upgrade.__version__:
        session.remove()
        return version, upgrade.__version__
    version += 1
    try:
        while hasattr(upgrade, 'upgrade_{version:d}'.format(version=version)):
            log.debug('Running upgrade_{version:d}'.format(version=version))
            try:
                upgrade_func = getattr(upgrade, 'upgrade_{version:d}'.format(version=version))
                upgrade_func(session, metadata)
                session.commit()
                # Update the version number AFTER a commit so that we are sure the previous transaction happened
                version_meta.value = str(version)
                session.add(version_meta)
                session.commit()
                version += 1
            except (SQLAlchemyError, DBAPIError):
                log.exception('Could not run database upgrade script '
                              '"upgrade_{version:d}", upgrade process has been halted.'.format(version=version))
                break
    except (SQLAlchemyError, DBAPIError) as e:
        version_meta = Metadata(key='version', value=int(upgrade.__version__))
        session.commit()
        print('Got exception outside upgrades', e)
    upgrade_version = upgrade.__version__
    version = int(version_meta.value)
    session.remove()
    return version, upgrade_version
