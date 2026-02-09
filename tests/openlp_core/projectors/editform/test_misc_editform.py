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
Test ProjectorEditForm methods that don't have many paths/options
"""

import logging
import openlp.core.projectors.editform
import openlp.core.projectors.db

from unittest.mock import patch
from tests.resources.projector.data import TEST1_DATA, TEST2_DATA

_test_module = openlp.core.projectors.editform.__name__
_test_module_db = openlp.core.projectors.db.__name__

Message = openlp.core.projectors.editform.Message
Projector = openlp.core.projectors.db.Projector
ProjectorEditForm = openlp.core.projectors.editform.ProjectorEditForm


def test_exec_projector_bad(projector_editform, caplog):
    """
    Test projector edit form with bad projector
    """
    # GIVEN: Mocked setup
    t_chk_item = str()
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.WARNING, 'edit_form() Projector type not valid for this form'),
            (_test_module, logging.WARNING, f'editform() projector type is {type(t_chk_item)}')
            ]

    # WHEN: Calling edit form with existing projector instance
    projector_editform.exec(projector=t_chk_item)

    # THEN: Appropriate calls and log entries
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert projector_editform.new_projector is False, 'new_projector should not have changed'
    projector_editform.mock_dialog_box.exec.assert_not_called()
    projector_editform.mock_msg_box.warning.assert_called_with(None,
                                                               Message.ProjectorInvalid['title'],
                                                               Message.ProjectorInvalid['text']
                                                               )

    # TODO: Check signals for QDialogButtonBox (projector_editform.button_box_edit/button_box_view)


def test_exec_projector_edit(projector_editform, caplog):
    """
    Test projector edit form with existing projector entry

    :return:
    """
    # GIVEN: Mocked setup
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module_db, logging.DEBUG, 'Filter by ID')]

    t_chk_db = projector_editform.projectordb.get_projector(id=TEST2_DATA['id'])[0]
    projector_editform.new_projector = False
    projector_editform.projector = None

    # WHEN: Calling edit form with existing projector instance
    projector_editform.exec(projector=Projector(**TEST2_DATA))

    # THEN: Should be editing an existing entry
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert projector_editform.new_projector is False, 'Projector edit form should be marked as existing entry'
    assert projector_editform.projector == t_chk_db, 'Entries should match'
    projector_editform.mock_msg_box.assert_not_called()
    # TODO: Check signals for QDialogButtonBox (projector_editform.button_box_edit/button_box_view)


def test_exec_projector_new(projector_editform_mtdb, caplog):
    """
    Test projector edit form with existing projector entry

    :return:
    """
    # GIVEN: Mocked setup
    caplog.set_level(logging.DEBUG)
    logs = []
    projector_editform_mtdb.new_projector = False
    projector_editform_mtdb.projector = Projector(**TEST1_DATA)

    # WHEN: Calling edit form with existing projector instance
    projector_editform_mtdb.exec()
    t_chk_item = projector_editform_mtdb.projector

    # THEN: Should be editing an existing entry
    assert caplog.record_tuples == logs, 'Invalid log entries'
    assert projector_editform_mtdb.new_projector is True, 'Projector edit form should be marked as a new entry'
    assert isinstance(t_chk_item, Projector)
    assert t_chk_item.id is None, 'ID should have indicated new entry'
    assert t_chk_item.name is None, 'Name should have indicated new entry'
    assert t_chk_item.ip is None, 'IP should have indicated new entry'
    # TODO: Check signals for QDialogButtonBox (projector_editform.button_box_edit/button_box_view)


def test_cancel_me(projector_editform_mtdb, caplog):
    """
    Test cancel_me logs and calls close
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'cancel_me() signal received')]

    with patch.object(projector_editform_mtdb, 'close') as mock_close:
        # WHEN: Called
        projector_editform_mtdb.cancel_me()

        # THEN: Appropriate log entries made
        assert caplog.record_tuples == logs, 'Invalid log entries'
        mock_close.assert_called_once()


def test_help_me(projector_editform_mtdb, caplog):
    """
    TODO: Expand method, then expand test
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    logs = [(_test_module, logging.DEBUG, 'help_me() signal received')]

    # WHEN: Called
    projector_editform_mtdb.help_me()

    # THEN: Appropriate log entries made
    assert caplog.record_tuples == logs, 'Invalid log entries'
