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
Test ProjectorDB.get_projectors()
"""

import logging
import openlp.core.projectors.db

from openlp.core.projectors.constants import PJLINK_PORT

from tests.resources.projector.data import TEST1_DATA, TEST2_DATA, TEST3_DATA

test_module = openlp.core.projectors.db.__name__
Projector = openlp.core.projectors.db.Projector


def test_invalid_projector(projectordb, caplog):
    """
    Test get_projector with no Projector() instance and no options
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.WARNING, 'get_projector(): No valid query found - cancelled')]

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector()

    # THEN: Only log entries found and return is None
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert t_chk is None, 'Should have returned None'


def test_invald_key(projectordb, caplog):
    """
    Test returning None if not one of the main keys
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.WARNING, 'get_projector(): No valid query found - cancelled')]

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(pin='')

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert t_chk is None, 'Should have returned None'


def test_by_id(projectordb, caplog):
    """
    Test returning one entry by ID
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by ID')]
    t_p2 = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(id=2)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2 == t_chk[0], 'DB record != t_chk'


def test_by_name(projectordb, caplog):
    """
    Test returning one entry by name
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by Name')]
    t_p2 = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(name=t_p2.name)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2 == t_chk[0], 'DB record != t_chk'


def test_by_ip_single(projectordb, caplog):
    """
    Test returning one entry by IP
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by IP')]
    t_p2 = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(ip=t_p2.ip)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2 == t_chk[0], 'DB record != t_chk'


def test_by_ip_multiple(projectordb, caplog):
    """
    Test returning multiple entries by IP
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by IP')]
    t_p2 = Projector(**TEST2_DATA)
    t_p2.id = None
    t_p2.port = PJLINK_PORT
    projectordb.add_projector(projector=t_p2)
    t_p2chk = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(ip=t_p2.ip)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 2, 'Should have returned 2 records'
    assert t_p2.name == t_chk[0].name and t_p2.name == t_chk[1].name, 'DB records names do not match'
    assert t_p2.ip == t_chk[0].ip and t_p2.ip == t_chk[1].ip, 'DB records IP addresses do not match'
    assert t_p2.name == t_chk[0].name and t_p2.name == t_chk[1].name, 'DB records names do not match'
    assert t_p2chk.port == t_chk[0].port and t_p2.port == t_chk[1].port, 'DB records ports do not match'


def test_by_port_single(projectordb, caplog):
    """
    Test returning one entry by Port
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by Port')]
    t_p2 = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(port=t_p2.port)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2 == t_chk[0], 'DB record != t_chk'


def test_by_port_multiple(projectordb_mtdb, caplog):
    """
    Test returning one entry by Port
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by Port')]

    t_p1 = Projector(**TEST1_DATA)
    t_p1.port = PJLINK_PORT
    projectordb_mtdb.add_projector(t_p1)
    t_p2 = Projector(**TEST2_DATA)
    t_p2.port = PJLINK_PORT
    projectordb_mtdb.add_projector(t_p2)
    t_p3 = Projector(**TEST3_DATA)
    t_p3.port = PJLINK_PORT
    projectordb_mtdb.add_projector(t_p3)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb_mtdb.get_projector(port=PJLINK_PORT)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 3, 'Should have returned 3 records'
    assert t_chk[0].ip == TEST1_DATA['ip'], 'DB record 1 IP does not match'
    assert t_chk[1].ip == TEST2_DATA['ip'], 'DB record 2 IP does not match'
    assert t_chk[2].ip == TEST3_DATA['ip'], 'DB record 3 IP does not match'


def test_by_ip_port(projectordb, caplog):
    """
    Test returning one entry by IP and Port
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by IP Port')]
    t_p2 = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(port=t_p2.port, ip=t_p2.ip)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2 == t_chk[0], 'DB record != t_chk'


def test_by_projector_id(projectordb, caplog):
    """
    Test returning one entry by projector.id
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by ID')]
    t_p2 = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(projector=t_p2)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2 == t_chk[0], 'DB record != t_chk'


def test_by_projector_name(projectordb, caplog):
    """
    Test returning one entry by projector.name
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by Name')]
    t_p2 = Projector(**TEST2_DATA)
    t_p2.id = None

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(projector=t_p2)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2 == t_chk[0], 'DB record != t_chk'


def test_by_projector_ip(projectordb, caplog):
    """
    Test returning one entry by projector.ip
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by IP')]
    t_p2 = Projector(**TEST2_DATA)
    t_p2.id = t_p2.name = t_p2.port = None
    t_p2chk = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(projector=t_p2)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2chk == t_chk[0], 'DB record != t_chk'


def test_by_projector_port(projectordb, caplog):
    """
    Test returning one entry by projector.port
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by Port')]
    t_p2 = Projector(**TEST2_DATA)
    t_p2.id = t_p2.name = t_p2.ip = None
    t_p2chk = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(projector=t_p2)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2chk == t_chk[0], 'DB record != t_chk'


def test_by_projector_ip_port(projectordb, caplog):
    """
    Test returning one entry by projector.port
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(test_module, logging.DEBUG, 'Filter by IP Port')]
    t_p2 = Projector(**TEST2_DATA)
    t_p2.id = t_p2.name = None
    t_p2chk = Projector(**TEST2_DATA)

    # WHEN: Called
    caplog.clear()
    t_chk = projectordb.get_projector(projector=t_p2)

    # THEN: Logs and one returned item
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert len(t_chk) == 1, 'More than one record returned'
    assert t_p2chk == t_chk[0], 'DB record != t_chk'
