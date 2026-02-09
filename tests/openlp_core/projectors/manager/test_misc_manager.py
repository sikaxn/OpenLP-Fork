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
Test misc. functions with few test paths

_load_projectors()
add_projector_from_wizard()
get_projector_list()

"""
from threading import Thread
from time import sleep
from typing import Optional
from unittest.mock import DEFAULT, MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.projectors.db import Projector
from openlp.core.projectors.manager import ProjectorManager

from tests.resources.projector.data import TEST1_DATA, TEST2_DATA, TEST3_DATA


def test_private_load_projectors(projector_manager_mtdb):
    """
    Test that _load_projectors() retrieves all entries from projector database
    """
    # GIVEN: Test environment
    t_db = projector_manager_mtdb.projectordb  # Shortcut helper
    for itm in (TEST1_DATA, TEST2_DATA, TEST3_DATA):
        t_db.add_projector(Projector(**itm))
    t_db.session.commit()

    t_list = t_db.get_projector_all()

    # Mock to keep from getting event not registered error in Registry()
    # during bootstrap_post_set_up()
    # Although we're testing _load_projectors, need to mock
    # it first to get past bootstrap_post_set_up() before test
    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT,
                        _load_projectors=DEFAULT):
        projector_manager_mtdb.bootstrap_initialise()
        projector_manager_mtdb.bootstrap_post_set_up()

    # WHEN: Called
    projector_manager_mtdb._load_projectors()

    assert len(projector_manager_mtdb.projector_list) == len(t_list), \
        'Invalid number of entries between check and list'

    # Isolate the DB entries used to create projector_manager.projector_list
    t_chk = []
    for dbitem in projector_manager_mtdb.projector_list:
        t_chk.append(dbitem.db_item)

    assert t_chk == t_list, 'projector_list DB items do not match test items'


def test_add_projector_from_wizard(projector_manager):
    """
    Test when add projector from GUI, appropriate method is called correctly
    """
    # GIVEN: Test environment
    with patch.multiple(projector_manager,
                        projectordb=DEFAULT,
                        add_projector=DEFAULT) as mock_manager:
        t_item = Projector(**TEST1_DATA)

        mock_manager['projectordb'].get_projector_by_ip.return_value = t_item

        # WHEN: Called
        projector_manager.add_projector_from_wizard(ip=t_item.ip)

        # THEN: appropriate calls made
        mock_manager['add_projector'].assert_called_with(t_item)


def test_get_projector_list(projector_manager_mtdb):
    """
    Test get_projector_list() returns valid entries
    """
    # GIVEN: Test environment
    t_db = projector_manager_mtdb.projectordb  # Shortcut helper
    for itm in (TEST1_DATA, TEST2_DATA, TEST3_DATA):
        t_db.add_projector(Projector(**itm))
    t_list = t_db.get_projector_all()

    # Mock to keep from getting event not registered error in Registry()
    # during bootstrap_post_set_up()
    with patch.multiple(projector_manager_mtdb,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT):
        projector_manager_mtdb.bootstrap_initialise()
        projector_manager_mtdb.bootstrap_post_set_up()

    # WHEN: Called
    t_chk = projector_manager_mtdb.get_projector_list()

    # THEN: DB items for both t_list and projector_list are the same
    assert len(t_chk) == len(t_list), 'projector_list length mismatch with test items length'

    # Isolate the DB entries used to create projector_manager.projector_list
    t_chk_list = []
    for dbitem in t_chk:
        t_chk_list.append(dbitem.db_item)
    assert t_list == t_chk_list, 'projector_list DB items do not match test items'


def test_update_status_call_not_parallel(registry: Registry, projector_manager_nodb: ProjectorManager):
    """
    Tests if _replace_service_list calls are not done in parallel
    """
    # GIVEN a service manager and a mocked repaint
    def mock_update_status(ip: str, status: int, msg: Optional[str] = None):
        projector_manager_nodb.is_updating_status = True
        sleep(0.25)
        projector_manager_nodb.is_updating_status = False

    projector_manager_nodb._update_status = MagicMock(side_effect=mock_update_status)

    # WHEN repaint_service_list is called from different threads
    thread_1 = Thread(target=lambda: projector_manager_nodb.update_status('192.168.88.238', 1))
    thread_2 = Thread(target=lambda: projector_manager_nodb.update_status('192.168.88.238', 2))
    thread_1.start()
    thread_2.start()

    # THEN the _repaint_service_list call must be called only once
    thread_1.join()
    thread_2.join()
    projector_manager_nodb._update_status.assert_called_once()
