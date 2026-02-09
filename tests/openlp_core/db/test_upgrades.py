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
Package to test the openlp.core.lib package.
"""
from unittest.mock import MagicMock, patch

from openlp.core.db.upgrades import get_upgrade_op, upgrade_db


def test_get_upgrade_op():
    """
    Test that the ``get_upgrade_op`` function creates a MigrationContext and an Operations object
    """
    # GIVEN: Mocked out alembic classes and a mocked out SQLAlchemy session object
    with patch('openlp.core.db.upgrades.MigrationContext') as MockedMigrationContext, \
            patch('openlp.core.db.upgrades.Operations') as MockedOperations:
        mocked_context = MagicMock()
        mocked_op = MagicMock()
        mocked_connection = MagicMock()
        MockedMigrationContext.configure.return_value = mocked_context
        MockedOperations.return_value = mocked_op
        mocked_session = MagicMock()
        mocked_session.bind.connect.return_value = mocked_connection

        # WHEN: get_upgrade_op is executed with the mocked session object
        op = get_upgrade_op(mocked_session)

        # THEN: The op object should be mocked_op, and the correction function calls should have been made
        assert op is mocked_op, 'The return value should be the mocked object'
        mocked_session.bind.connect.assert_called_with()
        MockedMigrationContext.configure.assert_called_with(mocked_connection)
        MockedOperations.assert_called_with(mocked_context)


def test_skip_db_upgrade_with_no_database(temp_folder):
    """
    Test the upgrade_db function does not try to update a missing database
    """
    # GIVEN: Database URL that does not (yet) exist
    url = 'sqlite:///{tmp}/test_db.sqlite'.format(tmp=temp_folder)
    mocked_upgrade = MagicMock()

    # WHEN: We attempt to upgrade a non-existent database
    upgrade_db(url, mocked_upgrade)

    # THEN: upgrade should NOT have been called
    assert mocked_upgrade.called is False, 'Database upgrade function should NOT have been called'
