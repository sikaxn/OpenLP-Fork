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
Test methods called by toolbar icons part 1

on_blank_projector()
on_connect_projector()
on_disconnect_projector()
on_poweroff_projector()
on_poweron_projector()
on_show_projector()

"""

from unittest.mock import DEFAULT, patch

from openlp.core.projectors.db import Projector

from tests.helpers.projector import FakePJLink
from tests.resources.projector.data import TEST1_DATA, TEST2_DATA, TEST3_DATA


def helper_method(test_fixture, method, effect, test_item=None):
    """
    Boilerplate for tests

    :param test_fixture: Fixture used for testing
    :param method: Method in fixture to test
    :param effect: Dict of items for testing
                    {'item': Item class
                     'select': Boolean to enable selected() in projector_list_widget
    :param test_item: (Optional) Item to call method with

    """
    with patch.multiple(test_fixture,
                        udp_listen_add=DEFAULT,
                        udp_listen_delete=DEFAULT,
                        update_icons=DEFAULT,
                        _add_projector=DEFAULT) as mock_manager:

        mock_manager['_add_projector'].side_effect = [item['item'] for item in effect]
        test_fixture.bootstrap_initialise()
        # projector_list_widget created here
        test_fixture.bootstrap_post_set_up()

        # Add ProjectorItem instances to projector_list_widget
        for item in effect:
            test_fixture.add_projector(projector=item['item'])

        # Set at least one instance as selected to verify projector_list_widget is not called
        for item in range(len(effect)):
            test_fixture.projector_list_widget.item(item).setSelected(effect[item]['select'])

        # WHEN: Called with projector instance
        method(item=test_item)


def test_on_blank_projector_direct(projector_manager_mtdb):
    """
    Test calling method directly - projector_list_widget should not be called
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_blank_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ],
                  test_item=t_1
                  )

    # THEN: Only t_1.set_shutter_closed() should be called
    t_1.set_shutter_closed.assert_called_once()
    t_2.set_shutter_closed.assert_not_called()
    t_3.set_shutter_closed.assert_not_called()


def test_on_blank_projector_one_item(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_blank_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': True},
                          {'item': t_3, 'select': False}
                          ]
                  )

    # THEN: Only t_3.set_shutter_closed() should be called
    t_1.set_shutter_closed.assert_not_called()
    t_2.set_shutter_closed.assert_called_once()
    t_3.set_shutter_closed.assert_not_called()


def test_on_blank_projector_multiple_items(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with more than one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_blank_projector,
                  effect=[{'item': t_1, 'select': True},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: t_1 and t_3 set_shutter_closed() should be called
    t_1.set_shutter_closed.assert_called_once()
    t_2.set_shutter_closed.assert_not_called()
    t_3.set_shutter_closed.assert_called_once()


def test_on_connect_projector_direct(projector_manager_mtdb):
    """
    Test calling method directly - projector_list_widget should not be called
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_connect_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ],
                  test_item=t_1
                  )

    # THEN: Only t_1.connect_to_host() should be called
    t_1.connect_to_host.assert_called_once()
    t_2.connect_to_host.assert_not_called()
    t_3.connect_to_host.assert_not_called()


def test_on_connect_projector_one_item(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_connect_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: Only t_3.connect_to_host() should be called
    t_1.connect_to_host.assert_not_called()
    t_2.connect_to_host.assert_not_called()
    t_3.connect_to_host.assert_called_once()


def test_on_connect_projector_multiple_items(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with more than one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_connect_projector,
                  effect=[{'item': t_1, 'select': True},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: t_1 and t_3 connect_to_host() should be called
    t_1.connect_to_host.assert_called_once()
    t_2.connect_to_host.assert_not_called()
    t_3.connect_to_host.assert_called_once()


def test_on_disconnect_projector_direct(projector_manager_mtdb):
    """
    Test calling method directly - projector_list_widget should not be called
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_disconnect_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ],
                  test_item=t_1
                  )

    # THEN: Only t_1.disconnect_from_host() should be called
    t_1.disconnect_from_host.assert_called_once()
    t_2.disconnect_from_host.assert_not_called()
    t_3.disconnect_from_host.assert_not_called()


def test_on_disconnect_projector_one_item(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_disconnect_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: Only t_3.disconnect_from_host() should be called
    t_1.disconnect_from_host.assert_not_called()
    t_2.disconnect_from_host.assert_not_called()
    t_3.disconnect_from_host.assert_called_once()


def test_on_disconnect_projector_multiple_items(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with more than one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_disconnect_projector,
                  effect=[{'item': t_1, 'select': True},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: t_1 and t_3 disconnect_from_host() should be called
    t_1.disconnect_from_host.assert_called_once()
    t_2.disconnect_from_host.assert_not_called()
    t_3.disconnect_from_host.assert_called_once()


def test_on_poweroff_projector_direct(projector_manager_mtdb):
    """
    Test calling method directly - projector_list_widget should not be called
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_poweroff_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ],
                  test_item=t_1
                  )

    # THEN: Only t_1.set_power_off() should be called
    t_1.set_power_off.assert_called_once()
    t_2.set_power_off.assert_not_called()
    t_3.set_power_off.assert_not_called()


def test_on_poweroff_projector_one_item(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_poweroff_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: Only t_3.set_power_off() should be called
    t_1.set_power_off.assert_not_called()
    t_2.set_power_off.assert_not_called()
    t_3.set_power_off.assert_called_once()


def test_on_poweroff_projector_multiple_items(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with more than one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_poweroff_projector,
                  effect=[{'item': t_1, 'select': True},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: t_1 and t_3 set_power_off() should be called
    t_1.set_power_off.assert_called_once()
    t_2.set_power_off.assert_not_called()
    t_3.set_power_off.assert_called_once()


def test_on_poweron_projector_direct(projector_manager_mtdb):
    """
    Test calling method directly - projector_list_widget should not be called
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_poweron_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ],
                  test_item=t_1
                  )

    # THEN: Only t_1.set_power_on() should be called
    t_1.set_power_on.assert_called_once()
    t_2.set_power_on.assert_not_called()
    t_3.set_power_on.assert_not_called()


def test_on_poweron_projector_one_item(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_poweron_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: Only t_3.set_power_on() should be called
    t_1.set_power_on.assert_not_called()
    t_2.set_power_on.assert_not_called()
    t_3.set_power_on.assert_called_once()


def test_on_poweron_projector_multiple_items(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with more than one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_poweron_projector,
                  effect=[{'item': t_1, 'select': True},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: t_1 and t_3 set_power_on() should be called
    t_1.set_power_on.assert_called_once()
    t_2.set_power_on.assert_not_called()
    t_3.set_power_on.assert_called_once()


def test_on_show_projector_direct(projector_manager_mtdb):
    """
    Test calling method directly - projector_list_widget should not be called
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_show_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ],
                  test_item=t_1
                  )

    # THEN: Only t_1.set_shutter_open() should be called
    t_1.set_shutter_open.assert_called_once()
    t_2.set_shutter_open.assert_not_called()
    t_3.set_shutter_open.assert_not_called()


def test_on_show_projector_one_item(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_show_projector,
                  effect=[{'item': t_1, 'select': False},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: Only t_3.set_shutter_open() should be called
    t_1.set_shutter_open.assert_not_called()
    t_2.set_shutter_open.assert_not_called()
    t_3.set_shutter_open.assert_called_once()


def test_on_show_projector_multiple_items(projector_manager_mtdb):
    """
    Test calling method using projector_list_widget with more than one item selected
    """
    # GIVEN: Test setup
    t_1 = FakePJLink(Projector(**TEST1_DATA))
    t_2 = FakePJLink(Projector(**TEST2_DATA))
    t_3 = FakePJLink(Projector(**TEST3_DATA))

    # WHEN: called
    helper_method(test_fixture=projector_manager_mtdb,
                  method=projector_manager_mtdb.on_show_projector,
                  effect=[{'item': t_1, 'select': True},
                          {'item': t_2, 'select': False},
                          {'item': t_3, 'select': True}
                          ]
                  )

    # THEN: t_1 and t_3 set_shutter_open() should be called
    t_1.set_shutter_open.assert_called_once()
    t_2.set_shutter_open.assert_not_called()
    t_3.set_shutter_open.assert_called_once()
