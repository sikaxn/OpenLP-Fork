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
Test ProjectorEditForm.accept_me
"""
from unittest.mock import MagicMock, patch, call

from openlp.core.projectors.editform import ProjectorEditForm, Message
from openlp.core.projectors.constants import PJLINK_VALID_PORTS
from openlp.core.projectors.db import Projector
from tests.resources.projector.data import TEST1_DATA


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_name_blank(mocked_show_warning: MagicMock, mocked_log: MagicMock, mock_settings: MagicMock):
    """
    Test when name field blank
    """
    # GIVEN: Test setup
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText('')

    # WHEN: The accept_me slot is called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_show_warning.assert_called_once_with(message=Message.NameBlank)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_database_error_id(mocked_show_warning: MagicMock, mocked_log: MagicMock,
                                     mock_settings: MagicMock):
    """
    Test with mismatch ID between Projector() and DB
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    test_id = TEST1_DATA['id']
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.projector.id = test_id

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_log.warning.assert_called_once_with(f'editform(): No record found but projector had id={test_id}')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.DatabaseError)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_name_database_error_name(mocked_show_warning: MagicMock, mocked_log: MagicMock,
                                            mock_settings: MagicMock):
    """
    Test with mismatch between name and DB
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.projector.name = name
    projector_editform.new_projector = False

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_log.warning.assert_called_once_with(f'editform(): No record found when there should be name="{name}"')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.DatabaseError)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_name_duplicate(mocked_show_warning: MagicMock, mocked_log: MagicMock,
                                  mock_settings: MagicMock):
    """
    Test when name duplicate
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = [MagicMock()]
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.projector.name = name

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_log.warning.assert_called_once_with(f'editform(): Name "{name}" already in database')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.NameDuplicate)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_name_multiple(mocked_show_warning: MagicMock, mocked_log: MagicMock, mock_settings: MagicMock):
    """
    Test when multiple database records have the same name
    """
    # GIVEN: Test setup
    # Save another instance of TEST1_DATA
    name = TEST1_DATA['name']
    projector_1 = Projector(**TEST1_DATA)
    projector_1.id = 1
    projector_2 = Projector(**TEST1_DATA)
    projector_2.id = 2
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = [projector_1, projector_2]
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    assert mocked_log.warning.call_args_list == [
        call(f'editform(): Multiple records found for name "{name}"'),
        call(f'editform() Found record={projector_1.id} name="{name}"'),
        call(f'editform() Found record={projector_2.id} name="{name}"'),
    ]
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.DatabaseMultiple)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_ip_blank(mocked_show_warning: MagicMock, mocked_log: MagicMock, mock_settings: MagicMock):
    """
    Test when IP field blank
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.ip_text.setText('')

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.IPBlank)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_ip_invalid(mocked_show_warning: MagicMock, mocked_log: MagicMock, mock_settings: MagicMock):
    """
    Test when IP invalid
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.ip_text.setText('300.256.900.512')

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.IPInvalid)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_port_blank(mocked_show_warning: MagicMock, mocked_log: MagicMock, mock_settings: MagicMock):
    """
    Test when port field blank
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    ip = TEST1_DATA['ip']
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.ip_text.setText(ip)
    projector_editform.port_text.setText('')

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.PortBlank)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_port_not_decimal(mocked_show_warning: MagicMock, mocked_log: MagicMock):
    """
    Test when port not a decimal digit
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    ip = TEST1_DATA['ip']
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.ip_text.setText(ip)
    projector_editform.port_text.setText('string')

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.PortInvalid)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_port_too_low(mocked_show_warning: MagicMock, mocked_log: MagicMock):
    """
    Test when port number less than PJLINK_VALID_PORTS lower value
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    ip = TEST1_DATA['ip']
    port = PJLINK_VALID_PORTS.start - 1
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.ip_text.setText(ip)
    projector_editform.port_text.setText(str(port))

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.PortInvalid)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accpt_me_port_too_high(mocked_show_warning: MagicMock, mocked_log: MagicMock):
    """
    Test when port number greater than PJLINK_VALID_PORTS higher value
    """
    # GIVEN: Test setup
    name = TEST1_DATA['name']
    ip = TEST1_DATA['ip']
    port = PJLINK_VALID_PORTS.stop + 1
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.ip_text.setText(ip)
    projector_editform.port_text.setText(str(port))

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_projectordb.get_projector.assert_called_once_with(name=name)
    mocked_show_warning.assert_called_once_with(message=Message.PortInvalid)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_address_duplicate(mocked_show_warning: MagicMock, mocked_log: MagicMock):
    """
    Test when IP:Port address duplicate
    """
    # GIVEN: Test setup
    name = 'A Different Name Not In DB'
    ip = TEST1_DATA['ip']
    port = TEST1_DATA['port']
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.side_effect = [[], [Projector(**TEST1_DATA)]]
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.ip_text.setText(ip)
    projector_editform.port_text.setText(str(port))

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    mocked_log.warning.assert_called_once_with(f'editform(): Address already in database {ip}:{port}')
    assert mocked_projectordb.get_projector.call_args_list == [call(name=name), call(ip=ip, port=port)]
    mocked_show_warning.assert_called_once_with(message=Message.AddressDuplicate)


@patch('openlp.core.projectors.editform.log')
@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_address_multiple(mocked_show_warning: MagicMock, mocked_log: MagicMock):
    """
    Test when database has multiple same IP:Port records
    """
    # GIVEN: Test setup
    t_name = TEST1_DATA['name']
    name = 'A Different Name Not In DB'
    ip = TEST1_DATA['ip']
    port = TEST1_DATA['port']
    projector_1 = Projector(**TEST1_DATA)
    projector_1.id = 1
    projector_2 = Projector(**TEST1_DATA)
    projector_2.id = 2
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.side_effect = [[], [projector_1, projector_2]]
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(name)
    projector_editform.ip_text.setText(ip)
    projector_editform.port_text.setText(str(port))

    # WHEN: Called
    projector_editform.accept_me()

    # THEN: Appropriate calls made
    mocked_log.debug.assert_called_once_with('accept_me() signal received')
    assert mocked_log.warning.call_args_list == [
        call(f'editform(): Multiple records found for {ip}:{port}'),
        call(f'editform(): record={projector_1.id} name="{t_name}" adx={ip}:{port}'),
        call(f'editform(): record={projector_2.id} name="{t_name}" adx={ip}:{port}')
    ]
    assert mocked_projectordb.get_projector.call_args_list == [call(name=name), call(ip=ip, port=port)]
    mocked_show_warning.assert_called_once_with(message=Message.DatabaseMultiple)


@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_save_new(mocked_show_warning: MagicMock):
    """
    Test editform saving new projector instance
    """
    # GIVEN: Test environment
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    mocked_projectordb.add_projector.return_value = True
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    projector_editform.new_projector = True
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(TEST1_DATA['name'])
    projector_editform.ip_text.setText(TEST1_DATA['ip'])
    projector_editform.port_text.setText(str(TEST1_DATA['port']))

    # WHEN: Called
    with patch.object(projector_editform, 'updateProjectors') as mocked_update_projectors, \
            patch.object(projector_editform, 'close') as mocked_close:
        projector_editform.accept_me()

    # THEN: appropriate message called
    assert mocked_show_warning.call_count == 0, 'No warnings should not have been shown'
    mocked_update_projectors.emit.assert_called_once()
    mocked_close.assert_called_once()


@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_save_new_fail(mocked_show_warning: MagicMock):
    """
    Test editform saving new projector instance where db fails to save
    """
    # GIVEN: Test environment
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.return_value = []
    mocked_projectordb.add_projector.return_value = False
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    projector_editform.new_projector = True
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(TEST1_DATA['name'])
    projector_editform.ip_text.setText(TEST1_DATA['ip'])
    projector_editform.port_text.setText(str(TEST1_DATA['port']))

    # WHEN: Called
    with patch.object(projector_editform, 'updateProjectors') as mocked_update_projectors, \
            patch.object(projector_editform, 'close') as mocked_close:
        projector_editform.accept_me()

    # THEN: appropriate message called
    mocked_show_warning.assert_called_once_with(message=Message.DatabaseError)
    assert mocked_update_projectors.emit.call_count == 0, 'The updateProjectors signal should have not emitted'
    assert mocked_close.call_count == 0, 'The form should not have closed'


@patch('openlp.core.projectors.editform.Message.show_warning')
def test_accept_me_save_update(mocked_show_warning: MagicMock):
    """
    Test editform update projector instance in database
    """
    # GIVEN: Test environment
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.side_effect = [[MagicMock()], []]
    mocked_projectordb.update_projector.return_value = True
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(TEST1_DATA['name'])
    projector_editform.ip_text.setText(TEST1_DATA['ip'])
    projector_editform.port_text.setText(str(TEST1_DATA['port']))
    projector_editform.new_projector = False

    # WHEN: Called
    with patch.object(projector_editform, 'updateProjectors') as mocked_update_projectors, \
            patch.object(projector_editform, 'close') as mocked_close:
        projector_editform.accept_me()

    # THEN: appropriate message called
    assert mocked_show_warning.call_count == 0, 'No warnings should not have been shown'
    mocked_update_projectors.emit.assert_called_once()
    mocked_close.assert_called_once()


@patch('openlp.core.projectors.editform.Message.show_warning')
def test_save_update_fail(mocked_show_warning: MagicMock):
    """
    Test editform updating projector instance where db fails to save
    """
    # GIVEN: Test environment
    mocked_projectordb = MagicMock()
    mocked_projectordb.get_projector.side_effect = [[MagicMock()], []]
    mocked_projectordb.update_projector.return_value = False
    projector_editform = ProjectorEditForm(None, mocked_projectordb)
    with patch('openlp.core.projectors.editform.QtWidgets.QDialog.exec'):
        projector_editform.exec()
    projector_editform.name_text.setText(TEST1_DATA['name'])
    projector_editform.ip_text.setText(TEST1_DATA['ip'])
    projector_editform.port_text.setText(str(TEST1_DATA['port']))
    projector_editform.new_projector = False

    # WHEN: Called
    with patch.object(projector_editform, 'updateProjectors') as mocked_update_projectors, \
            patch.object(projector_editform, 'close') as mocked_close:
        projector_editform.accept_me()

    # THEN: appropriate message called
    mocked_show_warning.assert_called_once_with(message=Message.DatabaseError)
    assert mocked_update_projectors.emit.call_count == 0, 'The updateProjectors signal should have not emitted'
    assert mocked_close.call_count == 0, 'The form should not have closed'
