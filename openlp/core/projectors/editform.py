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
The :mod: `openlp.core.ui.projector.editform` module provides the functions for adding/editing entries in the projector
database.
"""
import logging

from PySide6 import QtCore, QtWidgets

from openlp.core.common import verify_ip_address, Singleton
from openlp.core.common.i18n import translate
from openlp.core.projectors.constants import PJLINK_PORT, PJLINK_VALID_PORTS
from openlp.core.projectors.db import Projector
from openlp.core.ui.icons import UiIcons


log = logging.getLogger(__name__)
log.debug('editform loaded')

# TODO: Fix db entries for input source(s)

_translate_group = 'OpenLP.ProjectorEditForm'


class MessageList(metaclass=Singleton):
    """
    Consolidate the messages here. Simplify calls to QMessageBox.
    """
    def __init__(self):
        self.AddressDuplicate = {'title': translate(_translate_group, 'Duplicate Address'),
                                 'text': translate(_translate_group,
                                                   'IP:port combination are already in the database <br /><br />'
                                                   'Please Enter a different IP:port combination.')
                                 }
        self.DatabaseError = {'title': translate(_translate_group, 'Database Error'),
                              'text': translate(_translate_group,
                                                'There was an error saving projector information.<br /><br />'
                                                'See the log for the error')
                              }
        self.DatabaseID = {'title': translate(_translate_group, 'Database ID Error'),
                           'text': translate(_translate_group,
                                             'Mismatch between this entry and the database.<br /><br />'
                                             'See the log for possible issues.')
                           }
        self.DatabaseMultiple = {'title': translate(_translate_group, 'Multiple Records'),
                                 'text': translate(_translate_group,
                                                   'Multiple entries found in the database<br /><br />'
                                                   'Ensure Name and/or IP/Port data is unique')
                                 }
        self.IPBlank = {'title': translate(_translate_group, 'IP Address Not Set'),
                        'text': translate(_translate_group,
                                          'You must enter an IP address.<br /><br />'
                                          'Please enter a valid IP address.')
                        }
        self.IPInvalid = {'title': translate(_translate_group, 'Invalid IP Address'),
                          'text': translate(_translate_group,
                                            'IP address is not valid.<br /><br />'
                                            'Please enter a valid IP address.')
                          }
        self.NameBlank = {'title': translate(_translate_group, 'Name Not Set'),
                          'text': translate(_translate_group,
                                            'You must enter a name for this entry.<br /><br />'
                                            'Please enter a unique name for this entry.')
                          }
        self.NameDuplicate = {'title': translate(_translate_group, 'Duplicate Name'),
                              'text': translate(_translate_group,
                                                'Entries must have unique names.<br /><br />'
                                                'Please enter a different name.')
                              }
        self.ProjectorInvalid = {'title': translate(_translate_group, 'Invalid Projector'),
                                 'text': translate(_translate_group,
                                                   'Projector instance not a valid PJLink or Projector Instance'
                                                   '<br /><br />See log for issue')
                                 }
        self.PortBlank = {'title': translate(_translate_group, 'Port Not Set'),
                          'text': translate(_translate_group,
                                            'You must enter a port number for this entry.<br /><br />'
                                            'Please enter a valid port number.')
                          }
        self.PortInvalid = {'title': translate(_translate_group, 'Invalid Port Number'),
                            'text': translate(_translate_group,
                                              'Port numbers below 1000 are reserved for admin use only.<br />'
                                              'Port numbers above 32767 are not currently usable.<br /><br />'
                                              'Please enter a valid port number between 1000 and 32767 inclusive.'
                                              f'<br /><br />Default PJLink port is {PJLINK_PORT}')
                            }

    @staticmethod
    def show_warning(message, form=None):
        """
        Display QMessageBox.warning()
        """
        return QtWidgets.QMessageBox.warning(form, message['title'], message['text'])


Message = MessageList()


class Ui_ProjectorEditForm(object):
    """
    The :class:`~openlp.core.lib.ui.projector.editform.Ui_ProjectorEditForm` class defines
    the user interface for the ProjectorEditForm dialog.
    """
    def setup_ui(self, edit_projector_dialog):
        """
        Create the interface layout.
        """
        edit_projector_dialog.setObjectName('edit_projector_dialog')
        edit_projector_dialog.setWindowIcon(UiIcons().main_icon)
        edit_projector_dialog.setMinimumWidth(400)
        edit_projector_dialog.setModal(True)
        # Define the basic layout
        self.dialog_layout = QtWidgets.QGridLayout(edit_projector_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.dialog_layout.setSpacing(8)
        self.dialog_layout.setContentsMargins(8, 8, 8, 8)
        # Name
        _row = 0  # If I decide to rearrange the layout again
        self.name_label = QtWidgets.QLabel(edit_projector_dialog)
        self.name_label.setObjectName('projector_edit_name_label')
        self.name_text = QtWidgets.QLineEdit(edit_projector_dialog)
        self.name_text.setObjectName('projector_edit_name_text')
        self.dialog_layout.addWidget(self.name_label, _row, 0)
        self.dialog_layout.addWidget(self.name_text, _row, 1)
        # IP Address
        _row += 1
        self.ip_label = QtWidgets.QLabel(edit_projector_dialog)
        self.ip_label.setObjectName('projector_edit_ip_label')
        self.ip_text = QtWidgets.QLineEdit(edit_projector_dialog)
        self.ip_text.setObjectName('projector_edit_ip_text')
        self.dialog_layout.addWidget(self.ip_label, _row, 0)
        self.dialog_layout.addWidget(self.ip_text, _row, 1)
        # Port number
        _row += 1
        self.port_label = QtWidgets.QLabel(edit_projector_dialog)
        self.port_label.setObjectName('projector_edit_ip_label')
        self.port_text = QtWidgets.QLineEdit(edit_projector_dialog)
        self.port_text.setObjectName('projector_edit_port_text')
        self.dialog_layout.addWidget(self.port_label, _row, 0)
        self.dialog_layout.addWidget(self.port_text, _row, 1)
        # PIN
        _row += 1
        self.pin_label = QtWidgets.QLabel(edit_projector_dialog)
        self.pin_label.setObjectName('projector_edit_pin_label')
        self.pin_text = QtWidgets.QLineEdit(edit_projector_dialog)
        self.pin_label.setObjectName('projector_edit_pin_text')
        self.dialog_layout.addWidget(self.pin_label, _row, 0)
        self.dialog_layout.addWidget(self.pin_text, _row, 1)
        # Location
        _row += 1
        self.location_label = QtWidgets.QLabel(edit_projector_dialog)
        self.location_label.setObjectName('projector_edit_location_label')
        self.location_text = QtWidgets.QLineEdit(edit_projector_dialog)
        self.location_text.setObjectName('projector_edit_location_text')
        self.dialog_layout.addWidget(self.location_label, _row, 0)
        self.dialog_layout.addWidget(self.location_text, _row, 1)
        # Notes
        _row += 1
        self.notes_label = QtWidgets.QLabel(edit_projector_dialog)
        self.notes_label.setObjectName('projector_edit_notes_label')
        self.notes_text = QtWidgets.QPlainTextEdit(edit_projector_dialog)
        self.notes_text.setObjectName('projector_edit_notes_text')
        self.dialog_layout.addWidget(self.notes_label, _row, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.dialog_layout.addWidget(self.notes_text, _row, 1)
        # Time for the buttons
        self.button_box_edit = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Help |
                                                          QtWidgets.QDialogButtonBox.StandardButton.Save |
                                                          QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.dialog_layout.addWidget(self.button_box_edit, 8, 0, 1, 2)
        self.button_box_view = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.dialog_layout.addWidget(self.button_box_view, 8, 0, 1, 2)

    def retranslate_ui(self, edit_projector_dialog):
        if self.new_projector:
            title = translate('OpenLP.ProjectorEditForm', 'Add New Projector')
            self.projector.port = PJLINK_PORT
        else:
            title = translate('OpenLP.ProjectorEditForm', 'Edit Projector')
        edit_projector_dialog.setWindowTitle(title)
        self.ip_label.setText(translate('OpenLP.ProjectorEditForm', 'IP Address'))
        self.ip_text.setText(self.projector.ip)
        self.port_label.setText(translate('OpenLP.ProjectorEditForm', 'Port Number'))
        self.port_text.setText(str(self.projector.port))
        self.pin_label.setText(translate('OpenLP.ProjectorEditForm', 'PIN'))
        self.pin_text.setText(self.projector.pin)
        self.name_label.setText(translate('OpenLP.ProjectorEditForm', 'Name'))
        self.name_text.setText(self.projector.name)
        self.location_label.setText(translate('OpenLP.ProjectorEditForm', 'Location'))
        self.location_text.setText(self.projector.location)
        self.notes_label.setText(translate('OpenLP.ProjectorEditForm', 'Notes'))
        self.notes_text.clear()
        self.notes_text.insertPlainText(self.projector.notes)


class ProjectorEditForm(QtWidgets.QDialog, Ui_ProjectorEditForm):
    """
    Class to add or edit a projector entry in the database.

    Fields that are editable:
        name = Column(String(20))
        ip = Column(String(100))
        port = Column(String(8))
        pin = Column(String(20))
        location = Column(String(30))
        notes = Column(String(200))
    """
    updateProjectors = QtCore.Signal()

    def __init__(self, parent=None, projectordb=None):
        self.parent = parent
        self.projectordb = projectordb
        self.new_projector = False
        super(ProjectorEditForm, self).__init__(parent,
                                                QtCore.Qt.WindowType.WindowSystemMenuHint |
                                                QtCore.Qt.WindowType.WindowTitleHint |
                                                QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.setup_ui(self)
        self.button_box_edit.accepted.connect(self.accept_me)
        self.button_box_edit.helpRequested.connect(self.help_me)
        self.button_box_edit.rejected.connect(self.cancel_me)
        self.button_box_view.accepted.connect(self.cancel_me)

    def exec(self, projector=None, edit=True):
        if projector is None:
            self.projector = Projector()
            self.new_projector = True
        else:
            if not isinstance(projector, Projector):
                log.warning('edit_form() Projector type not valid for this form')
                log.warning(f'editform() projector type is {type(projector)}')
                return Message.show_warning(Message.ProjectorInvalid)
            self.projector = projector
            self.new_projector = False

        self.button_box_edit.setVisible(edit)
        self.button_box_view.setVisible(not edit)
        self.name_text.setReadOnly(not edit)
        self.ip_text.setReadOnly(not edit)
        self.port_text.setReadOnly(not edit)
        self.pin_text.setReadOnly(not edit)
        self.location_text.setReadOnly(not edit)
        self.notes_text.setReadOnly(not edit)
        if edit:
            self.name_text.setFocus()
        self.retranslate_ui(self)
        reply = QtWidgets.QDialog.exec(self)
        return reply

    @QtCore.Slot()
    def accept_me(self):
        """
        Validate inputs before accepting.
        """
        log.debug('accept_me() signal received')

        # Verify name
        _name = self.name_text.text().strip()

        if len(_name) < 1:
            return Message.show_warning(message=Message.NameBlank)
        _record = self.projectordb.get_projector(name=_name)
        if len(_record) == 0:
            if self.new_projector:
                if self.projector.id is not None:
                    log.warning(f'editform(): No record found but projector had id={self.projector.id}')
                    return Message.show_warning(message=Message.DatabaseError)
            else:
                if self.projector.name.strip() == _name:
                    log.warning(f'editform(): No record found when there should be name="{_name}"')
                    return Message.show_warning(message=Message.DatabaseError)
        elif len(_record) == 1 and self.new_projector:
            log.warning(f'editform(): Name "{_name}" already in database')
            return Message.show_warning(message=Message.NameDuplicate)
        elif len(_record) > 1:
            log.warning(f'editform(): Multiple records found for name "{_name}"')
            for item in _record:
                log.warning(f'editform() Found record={item.id} name="{item.name}"')
            return Message.show_warning(message=Message.DatabaseMultiple)

        # Verify IP address
        _ip = self.ip_text.text().strip()
        if len(_ip) < 1:
            return Message.show_warning(message=Message.IPBlank)
        elif not verify_ip_address(_ip):
            return Message.show_warning(message=Message.IPInvalid)

        # Verify valid port
        _port = self.port_text.text().strip()
        if len(_port) < 1:
            return Message.show_warning(message=Message.PortBlank)
        elif not _port.isdecimal():
            return Message.show_warning(message=Message.PortInvalid)
        elif int(_port) not in PJLINK_VALID_PORTS:
            return Message.show_warning(message=Message.PortInvalid)
        _port = int(_port)

        # Verify valid ip:port address
        check = self.projectordb.get_projector(ip=_ip, port=str(_port))
        if len(check) == 1:
            if self.projector.id != check[0].id:
                log.warning(f'editform(): Address already in database {_ip}:{_port}')
                return Message.show_warning(message=Message.AddressDuplicate)
        elif len(check) > 1:
            log.warning(f'editform(): Multiple records found for {_ip}:{_port}')
            for chk in check:
                log.warning(f'editform(): record={chk.id} name="{chk.name}" adx={chk.ip}:{chk.port}')
            return Message.show_warning(message=Message.DatabaseMultiple)

        self.projector.name = _name
        self.projector.ip = _ip
        self.projector.port = _port
        self.projector.pin = self.pin_text.text()
        self.projector.location = self.location_text.text()
        self.projector.notes = self.notes_text.toPlainText()
        # TODO: Update calls when update_projector fixed
        if self.new_projector:
            _saved = self.projectordb.add_projector(self.projector)
        else:
            _saved = self.projectordb.update_projector(self.projector)
        if not _saved:
            return Message.show_warning(message=Message.DatabaseError)

        self.updateProjectors.emit()
        self.projector = None
        self.close()

    @QtCore.Slot()
    def help_me(self):
        """
        Show a help message about the input fields.
        """
        log.debug('help_me() signal received')

    @QtCore.Slot()
    def cancel_me(self):
        """
        Cancel button clicked - just close.
        """
        log.debug('cancel_me() signal received')
        self.close()
