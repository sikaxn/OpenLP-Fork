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
:mod:`openlp.core.companion.manager` module

Provides the dock widget for controlling Bitfocus Companion via UDP, TCP or HTTP.
"""
import json
import logging
import uuid

from PySide6 import QtCore, QtNetwork, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.ui.icons import UiIcons

log = logging.getLogger(__name__)
log.debug('companionmanager loaded')

COMPANION_METHOD_UDP = 'udp'
COMPANION_METHOD_TCP = 'tcp'
COMPANION_METHOD_HTTP = 'http'

COMPANION_DEFAULT_PORTS = {
    COMPANION_METHOD_UDP: 51235,
    COMPANION_METHOD_TCP: 51234,
    COMPANION_METHOD_HTTP: 8000
}

STATUS_DISCONNECTED = 'Disconnected'
STATUS_CONNECTING = 'Connecting'
STATUS_CONNECTED = 'Connected'
STATUS_READY = 'Ready'
STATUS_ERROR = 'Error'
STATUS_ARMED = 'Armed'

AUTO_TRIGGER_ENTER_PRESS = 'enter_press'
AUTO_TRIGGER_LEAVE_PRESS = 'leave_press'
AUTO_TRIGGER_HOLD = 'hold'


class CompanionEditForm(QtWidgets.QDialog):
    """
    Dialog for adding a Bitfocus Companion endpoint.
    """
    def __init__(self, parent=None):
        widget_parent = parent if isinstance(parent, QtWidgets.QWidget) else None
        super().__init__(widget_parent)
        self.setObjectName('companion_edit_form')
        self.setMinimumWidth(400)
        self.setModal(True)
        self.companion = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QGridLayout(self)

        self.ip_label = QtWidgets.QLabel(self)
        self.ip_label.setText(translate('OpenLP.CompanionEditForm', 'IP Address:'))
        self.ip_text = QtWidgets.QLineEdit(self)
        self.ip_text.setPlaceholderText('192.168.1.100')
        layout.addWidget(self.ip_label, 0, 0)
        layout.addWidget(self.ip_text, 0, 1)

        self.method_label = QtWidgets.QLabel(self)
        self.method_label.setText(translate('OpenLP.CompanionEditForm', 'Method:'))
        self.method_combo = QtWidgets.QComboBox(self)
        self.method_combo.addItem('UDP', COMPANION_METHOD_UDP)
        self.method_combo.addItem('TCP', COMPANION_METHOD_TCP)
        self.method_combo.addItem('HTTP', COMPANION_METHOD_HTTP)
        self.method_combo.currentIndexChanged.connect(self.on_method_changed)
        layout.addWidget(self.method_label, 1, 0)
        layout.addWidget(self.method_combo, 1, 1)

        self.port_label = QtWidgets.QLabel(self)
        self.port_label.setText(translate('OpenLP.CompanionEditForm', 'Port:'))
        self.port_spin = QtWidgets.QSpinBox(self)
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(COMPANION_DEFAULT_PORTS[COMPANION_METHOD_UDP])
        layout.addWidget(self.port_label, 2, 0)
        layout.addWidget(self.port_spin, 2, 1)

        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel |
                                           QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box, 3, 0, 1, 2)

        self.setWindowTitle(translate('OpenLP.CompanionEditForm', 'Add Bitfocus Companion'))

    def on_method_changed(self):
        method = self.method_combo.currentData()
        self.port_spin.setValue(COMPANION_DEFAULT_PORTS[method])

    def exec(self, companion=None):
        self.companion = companion
        if companion:
            self.ip_text.setText(companion.get('ip', ''))
            method = companion.get('method', COMPANION_METHOD_UDP)
            index = self.method_combo.findData(method)
            if index >= 0:
                self.method_combo.setCurrentIndex(index)
            self.port_spin.setValue(int(companion.get('port', COMPANION_DEFAULT_PORTS[method])))
            self.setWindowTitle(translate('OpenLP.CompanionEditForm', 'Edit Bitfocus Companion'))
        else:
            self.ip_text.setText('')
            self.method_combo.setCurrentIndex(0)
            self.port_spin.setValue(COMPANION_DEFAULT_PORTS[COMPANION_METHOD_UDP])
            self.setWindowTitle(translate('OpenLP.CompanionEditForm', 'Add Bitfocus Companion'))
        return super().exec()

    def accept(self):
        ip = self.ip_text.text().strip()
        if not ip:
            QtWidgets.QMessageBox.warning(
                self,
                translate('OpenLP.CompanionEditForm', 'Invalid Input'),
                translate('OpenLP.CompanionEditForm', 'Please enter an IP address.')
            )
            return
        if self.companion is None:
            self.companion = {
                'id': str(uuid.uuid4()),
                'buttons': []
            }
        self.companion['ip'] = ip
        self.companion['method'] = self.method_combo.currentData()
        self.companion['port'] = int(self.port_spin.value())
        super().accept()


class CompanionButtonEditForm(QtWidgets.QDialog):
    """
    Dialog for adding a button mapping to a Bitfocus Companion endpoint.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('companion_button_edit_form')
        self.setMinimumWidth(400)
        self.setModal(True)
        self.button_data = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QGridLayout(self)

        self.name_label = QtWidgets.QLabel(self)
        self.name_label.setText(translate('OpenLP.CompanionButtonEditForm', 'Name:'))
        self.name_text = QtWidgets.QLineEdit(self)
        layout.addWidget(self.name_label, 0, 0)
        layout.addWidget(self.name_text, 0, 1)

        self.page_label = QtWidgets.QLabel(self)
        self.page_label.setText(translate('OpenLP.CompanionButtonEditForm', 'Page:'))
        self.page_spin = QtWidgets.QSpinBox(self)
        self.page_spin.setRange(0, 999)
        self.page_spin.setValue(1)
        layout.addWidget(self.page_label, 1, 0)
        layout.addWidget(self.page_spin, 1, 1)

        self.row_label = QtWidgets.QLabel(self)
        self.row_label.setText(translate('OpenLP.CompanionButtonEditForm', 'Row:'))
        self.row_spin = QtWidgets.QSpinBox(self)
        self.row_spin.setRange(0, 99)
        self.row_spin.setValue(0)
        layout.addWidget(self.row_label, 2, 0)
        layout.addWidget(self.row_spin, 2, 1)

        self.column_label = QtWidgets.QLabel(self)
        self.column_label.setText(translate('OpenLP.CompanionButtonEditForm', 'Column:'))
        self.column_spin = QtWidgets.QSpinBox(self)
        self.column_spin.setRange(0, 99)
        self.column_spin.setValue(0)
        layout.addWidget(self.column_label, 3, 0)
        layout.addWidget(self.column_spin, 3, 1)

        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel |
                                           QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box, 4, 0, 1, 2)

        self.setWindowTitle(translate('OpenLP.CompanionButtonEditForm', 'Add Companion Button'))

    def exec(self, button=None):
        if button:
            self.button_data = dict(button)
            self.name_text.setText(button.get('name', ''))
            self.page_spin.setValue(int(button.get('page', 1)))
            self.row_spin.setValue(int(button.get('row', 0)))
            self.column_spin.setValue(int(button.get('column', 0)))
            self.setWindowTitle(translate('OpenLP.CompanionButtonEditForm', 'Edit Companion Button'))
        else:
            self.button_data = None
            self.name_text.setText('')
            self.page_spin.setValue(1)
            self.row_spin.setValue(0)
            self.column_spin.setValue(0)
            self.setWindowTitle(translate('OpenLP.CompanionButtonEditForm', 'Add Companion Button'))
        return super().exec()

    def accept(self):
        name = self.name_text.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(
                self,
                translate('OpenLP.CompanionButtonEditForm', 'Invalid Input'),
                translate('OpenLP.CompanionButtonEditForm', 'Please enter a button name.')
            )
            return
        button_id = self.button_data.get('id') if self.button_data else str(uuid.uuid4())
        self.button_data = {
            'id': button_id,
            'name': name,
            'page': int(self.page_spin.value()),
            'row': int(self.row_spin.value()),
            'column': int(self.column_spin.value())
        }
        super().accept()


class CompanionAutoTriggerEditForm(QtWidgets.QDialog):
    """
    Dialog for adding/editing an auto trigger that maps a live slide to a companion button action.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('companion_autotrigger_edit_form')
        self.setMinimumWidth(520)
        self.setModal(True)
        self.trigger_data = None
        self._buttons = []
        self._item_name_resolver = None
        self._item_ref = ''
        self._item_id = ''
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QGridLayout(self)

        self.name_label = QtWidgets.QLabel(translate('OpenLP.CompanionAutoTriggerEditForm', 'Name:'), self)
        self.name_text = QtWidgets.QLineEdit(self)
        layout.addWidget(self.name_label, 0, 0)
        layout.addWidget(self.name_text, 0, 1, 1, 2)

        self.button_label = QtWidgets.QLabel(translate('OpenLP.CompanionAutoTriggerEditForm', 'Button:'), self)
        self.button_combo = QtWidgets.QComboBox(self)
        layout.addWidget(self.button_label, 1, 0)
        layout.addWidget(self.button_combo, 1, 1, 1, 2)

        self.type_label = QtWidgets.QLabel(translate('OpenLP.CompanionAutoTriggerEditForm', 'Trigger Type:'), self)
        self.type_combo = QtWidgets.QComboBox(self)
        self.type_combo.addItem(
            translate('OpenLP.CompanionAutoTriggerEditForm', 'Press once on slide switch to'),
            AUTO_TRIGGER_ENTER_PRESS)
        self.type_combo.addItem(
            translate('OpenLP.CompanionAutoTriggerEditForm', 'Press once on slide switch away'),
            AUTO_TRIGGER_LEAVE_PRESS)
        self.type_combo.addItem(
            translate('OpenLP.CompanionAutoTriggerEditForm', 'Press DOWN on switch to, UP on switch away'),
            AUTO_TRIGGER_HOLD)
        layout.addWidget(self.type_label, 2, 0)
        layout.addWidget(self.type_combo, 2, 1, 1, 2)

        self.item_label = QtWidgets.QLabel(translate('OpenLP.CompanionAutoTriggerEditForm', 'Service Item Key:'), self)
        self.item_text = QtWidgets.QLineEdit(self)
        self.item_text.setReadOnly(True)
        layout.addWidget(self.item_label, 3, 0)
        layout.addWidget(self.item_text, 3, 1)
        self.capture_button = QtWidgets.QPushButton(translate('OpenLP.CompanionAutoTriggerEditForm',
                                                              'Capture Current Live Slide'), self)
        self.capture_button.clicked.connect(self.on_capture_slide)
        layout.addWidget(self.capture_button, 3, 2)

        self.item_name_label = QtWidgets.QLabel(translate('OpenLP.CompanionAutoTriggerEditForm', 'Service Item Name:'),
                                                self)
        self.item_name_text = QtWidgets.QLineEdit(self)
        self.item_name_text.setReadOnly(True)
        layout.addWidget(self.item_name_label, 4, 0)
        layout.addWidget(self.item_name_text, 4, 1, 1, 2)

        self.slide_label = QtWidgets.QLabel(translate('OpenLP.CompanionAutoTriggerEditForm', 'Slide Row:'), self)
        self.slide_spin = QtWidgets.QSpinBox(self)
        self.slide_spin.setRange(0, 10000)
        layout.addWidget(self.slide_label, 5, 0)
        layout.addWidget(self.slide_spin, 5, 1, 1, 2)

        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel |
                                           QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box, 6, 0, 1, 3)

    def exec(self, buttons, trigger_data=None, item_name_resolver=None, preferred_button_id=''):
        self._buttons = list(buttons or [])
        self._item_name_resolver = item_name_resolver
        self.button_combo.clear()
        for button in self._buttons:
            label = '{name} ({page}/{row}/{column})'.format(name=button.get('name', ''),
                                                             page=button.get('page', ''),
                                                             row=button.get('row', ''),
                                                             column=button.get('column', ''))
            self.button_combo.addItem(label, button.get('id'))
        self.trigger_data = dict(trigger_data) if trigger_data else None
        if trigger_data:
            self.name_text.setText(trigger_data.get('name', ''))
            index = self.button_combo.findData(trigger_data.get('button_id', ''))
            if index >= 0:
                self.button_combo.setCurrentIndex(index)
            type_index = self.type_combo.findData(trigger_data.get('mode', AUTO_TRIGGER_ENTER_PRESS))
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)
            self._item_ref = str(trigger_data.get('item_ref', '') or '')
            self._item_id = str(trigger_data.get('item_id', '') or '')
            self.item_text.setText(self._item_ref or self._item_id)
            self._update_item_name_text()
            self.slide_spin.setValue(int(trigger_data.get('slide_row', 0)))
            self.setWindowTitle(translate('OpenLP.CompanionAutoTriggerEditForm', 'Edit Auto Trigger'))
        else:
            self.name_text.setText('')
            preferred_index = self.button_combo.findData(preferred_button_id)
            if preferred_index >= 0:
                self.button_combo.setCurrentIndex(preferred_index)
            self._item_ref = ''
            self._item_id = ''
            self.item_text.setText('')
            self.item_name_text.setText(translate('OpenLP.CompanionAutoTriggerEditForm', 'Not exist'))
            self.slide_spin.setValue(0)
            self.type_combo.setCurrentIndex(0)
            self.setWindowTitle(translate('OpenLP.CompanionAutoTriggerEditForm', 'Add Auto Trigger'))
            self.on_capture_slide()
        return super().exec()

    def _update_item_name_text(self):
        item_ref = self._item_ref.strip() if isinstance(self._item_ref, str) else ''
        item_id = self._item_id.strip() if isinstance(self._item_id, str) else ''
        if not item_ref and not item_id:
            self.item_name_text.setText(translate('OpenLP.CompanionAutoTriggerEditForm', 'Not exist'))
            return
        if callable(self._item_name_resolver):
            name = self._item_name_resolver(item_ref, item_id)
        else:
            name = None
        if name:
            self.item_name_text.setText(str(name))
        else:
            self.item_name_text.setText(translate('OpenLP.CompanionAutoTriggerEditForm', 'Not exist'))

    def on_capture_slide(self):
        live_controller = Registry().get('live_controller')
        service_item = getattr(live_controller, 'service_item', None) if live_controller else None
        if not live_controller or not service_item:
            return
        service_manager = Registry().get('service_manager')
        item_ref = ''
        if service_manager and hasattr(service_manager, 'service_items'):
            item_ref = self._find_service_item_ref(service_manager, service_item)
        self._item_ref = item_ref
        item_id = str(getattr(service_item, 'unique_identifier', '') or '')
        self._item_id = item_id
        row = int(getattr(live_controller, 'selected_row', 0) or 0)
        self.item_text.setText(item_ref or item_id)
        self._update_item_name_text()
        self.slide_spin.setValue(row)

    @staticmethod
    def _find_service_item_ref(service_manager, service_item):
        for index, entry in enumerate(getattr(service_manager, 'service_items', [])):
            candidate = entry.get('service_item') if isinstance(entry, dict) else None
            if candidate is service_item:
                return f'index:{index}'
        target_id = str(getattr(service_item, 'unique_identifier', ''))
        if not target_id:
            return ''
        for index, entry in enumerate(getattr(service_manager, 'service_items', [])):
            candidate = entry.get('service_item') if isinstance(entry, dict) else None
            if candidate and str(getattr(candidate, 'unique_identifier', '')) == target_id:
                return f'index:{index}'
        return ''

    def accept(self):
        name = self.name_text.text().strip()
        item_ref = self._item_ref.strip() if isinstance(self._item_ref, str) else ''
        item_id = self._item_id.strip() if isinstance(self._item_id, str) else ''
        button_id = self.button_combo.currentData()
        if not button_id:
            QtWidgets.QMessageBox.warning(
                self,
                translate('OpenLP.CompanionAutoTriggerEditForm', 'Invalid Input'),
                translate('OpenLP.CompanionAutoTriggerEditForm', 'Please select a button.')
            )
            return
        if not item_ref and not item_id:
            QtWidgets.QMessageBox.warning(
                self,
                translate('OpenLP.CompanionAutoTriggerEditForm', 'Invalid Input'),
                translate('OpenLP.CompanionAutoTriggerEditForm',
                          'Capture a live slide to set Service Item.')
            )
            return
        trigger_id = self.trigger_data.get('id') if self.trigger_data else str(uuid.uuid4())
        self.trigger_data = {
            'id': trigger_id,
            'name': name,
            'button_id': button_id,
            'mode': self.type_combo.currentData(),
            'item_ref': item_ref,
            'item_id': item_id,
            'slide_row': int(self.slide_spin.value())
        }
        super().accept()


class CompanionManager(QtWidgets.QWidget):
    """
    Manage Bitfocus Companion connections and button triggers.
    """
    def __init__(self, parent=None):
        widget_parent = parent if isinstance(parent, QtWidgets.QWidget) else None
        super().__init__(widget_parent)
        self.settings = Settings()
        self.companions = []
        self.selected_companion_id = None
        self.default_companion_id = ''
        self.autotrigger_enabled = True
        self.filter_current_live_triggers = False
        self.connections = {}
        self.network_manager = QtNetwork.QNetworkAccessManager(self)
        self.live_controller = None
        self.service_manager = None
        self._last_live_slide_key = None
        self._last_service_config_signature = None
        self._disconnect_in_progress = set()
        self._service_sync_in_progress = False
        self._setup_ui()
        self._load_companions()
        self._refresh_companion_list()
        self._update_icons()
        self._hook_live_controller()
        self._hook_service_manager()

    @staticmethod
    def _trace(message):
        log.debug(message)
        print(f'[Companion] {message}')

    def _setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.companion_group_box = QtWidgets.QGroupBox(translate('OpenLP.CompanionManager', 'Companions'), self)
        self.companion_layout = QtWidgets.QVBoxLayout(self.companion_group_box)
        self.companion_actions_layout = QtWidgets.QHBoxLayout()
        self.companion_add_button = QtWidgets.QPushButton(UiIcons().new,
                                                          translate('OpenLP.CompanionManager', 'Add'))
        self.companion_add_button.clicked.connect(self.on_add_companion)
        self.companion_edit_button = QtWidgets.QPushButton(UiIcons().edit,
                                                           translate('OpenLP.CompanionManager', 'Edit'))
        self.companion_edit_button.clicked.connect(self.on_edit_companion)
        self.companion_delete_button = QtWidgets.QPushButton(UiIcons().delete,
                                                             translate('OpenLP.CompanionManager', 'Delete'))
        self.companion_delete_button.clicked.connect(self.on_delete_companion)
        self.companion_default_button = QtWidgets.QPushButton(UiIcons().favourite,
                                                              translate('OpenLP.CompanionManager', 'Set Default'))
        self.companion_default_button.clicked.connect(self.on_set_default_companion)
        self.companion_connect_button = QtWidgets.QPushButton(UiIcons().projector_connect,
                                                              translate('OpenLP.CompanionManager', 'Connect'))
        self.companion_connect_button.clicked.connect(self.on_connect_companion)
        self.companion_disconnect_button = QtWidgets.QPushButton(UiIcons().projector_disconnect,
                                                                 translate('OpenLP.CompanionManager', 'Disconnect'))
        self.companion_disconnect_button.clicked.connect(self.on_disconnect_companion)
        for button in [self.companion_add_button, self.companion_edit_button, self.companion_delete_button,
                       self.companion_default_button, self.companion_connect_button, self.companion_disconnect_button]:
            self.companion_actions_layout.addWidget(button)
        self.companion_layout.addLayout(self.companion_actions_layout)
        self.companion_list_widget = QtWidgets.QListWidget(self.companion_group_box)
        self.companion_list_widget.setAlternatingRowColors(True)
        self.companion_list_widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.companion_layout.addWidget(self.companion_list_widget)
        self.status_label = QtWidgets.QLabel('', self.companion_group_box)
        self.companion_layout.addWidget(self.status_label)
        self.layout.addWidget(self.companion_group_box, 1)

        self.button_group_box = QtWidgets.QGroupBox(translate('OpenLP.CompanionManager', 'Buttons'), self)
        self.button_layout = QtWidgets.QVBoxLayout(self.button_group_box)
        self.button_actions_layout = QtWidgets.QHBoxLayout()
        self.button_add_button = QtWidgets.QPushButton(UiIcons().plus, translate('OpenLP.CompanionManager', 'Add'))
        self.button_add_button.clicked.connect(self.on_add_button)
        self.button_edit_button = QtWidgets.QPushButton(UiIcons().edit, translate('OpenLP.CompanionManager', 'Edit'))
        self.button_edit_button.clicked.connect(self.on_edit_button)
        self.button_delete_button = QtWidgets.QPushButton(UiIcons().minus,
                                                          translate('OpenLP.CompanionManager', 'Delete'))
        self.button_delete_button.clicked.connect(self.on_delete_button)
        self.button_trigger_button = QtWidgets.QPushButton(UiIcons().play,
                                                           translate('OpenLP.CompanionManager', 'Trigger'))
        self.button_trigger_button.clicked.connect(self.on_trigger_button)
        for button in [self.button_add_button, self.button_edit_button, self.button_delete_button,
                       self.button_trigger_button]:
            self.button_actions_layout.addWidget(button)
        self.button_layout.addLayout(self.button_actions_layout)
        self.button_list_widget = QtWidgets.QListWidget(self.button_group_box)
        self.button_list_widget.setAlternatingRowColors(True)
        self.button_list_widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.button_list_widget.itemDoubleClicked.connect(self.on_edit_button)
        self.button_layout.addWidget(self.button_list_widget)
        self.layout.addWidget(self.button_group_box, 1)

        self.auto_trigger_group_box = QtWidgets.QGroupBox(translate('OpenLP.CompanionManager', 'Auto Triggers'), self)
        self.auto_trigger_layout = QtWidgets.QVBoxLayout(self.auto_trigger_group_box)
        self.auto_trigger_actions_layout = QtWidgets.QHBoxLayout()
        self.autotrigger_add_button = QtWidgets.QPushButton(UiIcons().new,
                                                            translate('OpenLP.CompanionManager', 'Add'))
        self.autotrigger_add_button.clicked.connect(self.on_add_autotrigger)
        self.autotrigger_edit_button = QtWidgets.QPushButton(UiIcons().edit,
                                                             translate('OpenLP.CompanionManager', 'Edit'))
        self.autotrigger_edit_button.clicked.connect(self.on_edit_autotrigger)
        self.autotrigger_delete_button = QtWidgets.QPushButton(UiIcons().delete,
                                                               translate('OpenLP.CompanionManager', 'Delete'))
        self.autotrigger_delete_button.clicked.connect(self.on_delete_autotrigger)
        self.autotrigger_toggle_button = QtWidgets.QPushButton(self.auto_trigger_group_box)
        self.autotrigger_toggle_button.clicked.connect(self.on_toggle_autotrigger_enabled)
        self.autotrigger_toggle_button.setCheckable(True)
        self.autotrigger_filter_live_button = QtWidgets.QPushButton(
            translate('OpenLP.CompanionManager', 'Filter Current Live'), self.auto_trigger_group_box)
        self.autotrigger_filter_live_button.setCheckable(True)
        self.autotrigger_filter_live_button.clicked.connect(self.on_toggle_autotrigger_filter_live)
        for button in [self.autotrigger_add_button, self.autotrigger_edit_button, self.autotrigger_delete_button]:
            self.auto_trigger_actions_layout.addWidget(button)
        self.auto_trigger_actions_layout.addWidget(self.autotrigger_toggle_button)
        self.auto_trigger_actions_layout.addWidget(self.autotrigger_filter_live_button)
        self.auto_trigger_layout.addLayout(self.auto_trigger_actions_layout)
        self.auto_trigger_list_widget = QtWidgets.QListWidget(self.auto_trigger_group_box)
        self.auto_trigger_list_widget.setAlternatingRowColors(True)
        self.auto_trigger_list_widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.auto_trigger_list_widget.itemDoubleClicked.connect(self.on_edit_autotrigger)
        self.auto_trigger_layout.addWidget(self.auto_trigger_list_widget)
        self.layout.addWidget(self.auto_trigger_group_box, 1)

        self.companion_list_widget.currentItemChanged.connect(self.on_companion_selected)
        self.companion_list_widget.itemDoubleClicked.connect(self.on_edit_companion)
        self.companion_list_widget.customContextMenuRequested.connect(self.on_companion_context_menu)
        self.button_list_widget.currentItemChanged.connect(self._update_icons)
        self.button_list_widget.customContextMenuRequested.connect(self.on_button_context_menu)
        self.auto_trigger_list_widget.currentItemChanged.connect(self._update_icons)
        self.auto_trigger_list_widget.customContextMenuRequested.connect(self.on_autotrigger_context_menu)
        self._update_button_colours()

    @staticmethod
    def _config_signature(config):
        if not isinstance(config, dict):
            return ''
        try:
            return json.dumps(config, sort_keys=True, separators=(',', ':'))
        except (TypeError, ValueError):
            return ''

    def _load_companions(self):
        config = None
        results = Registry().execute('service_get_companion_config')
        if results:
            config = results[0]
        if not isinstance(config, dict):
            config = {'companions': [], 'default_companion_id': ''}
        self._last_service_config_signature = self._config_signature(config)
        old_connections = self.connections
        new_connections = {}
        self.companions = config.get('companions', []) or []
        self.default_companion_id = config.get('default_companion_id', '') or ''
        enabled_value = self.settings.value('companion/autotrigger enabled')
        if isinstance(enabled_value, str):
            self.autotrigger_enabled = enabled_value.strip().lower() in ('1', 'true', 'yes', 'on')
        else:
            self.autotrigger_enabled = bool(enabled_value)
        for companion in self.companions:
            if 'id' not in companion:
                companion['id'] = str(uuid.uuid4())
            companion.setdefault('buttons', [])
            companion.setdefault('autotriggers', [])
            for trigger in companion.get('autotriggers', []):
                if 'item_ref' not in trigger:
                    trigger['item_ref'] = ''
                if not trigger.get('item_ref') and trigger.get('item_id'):
                    trigger['item_ref'] = self._resolve_item_ref_from_legacy_id(str(trigger.get('item_id')))
            companion_id = companion['id']
            old_connection = old_connections.get(companion_id)
            if old_connection and old_connection.get('method') == companion.get('method'):
                new_connections[companion_id] = old_connection
            else:
                if old_connection:
                    self._disconnect(companion)
                new_connections[companion_id] = self._create_connection(companion)
        active_ids = {companion.get('id') for companion in self.companions if companion.get('id')}
        for removed_id in list(old_connections.keys()):
            if removed_id in active_ids:
                continue
            removed_connection = old_connections.get(removed_id, {})
            removed_companion = {
                'id': removed_id,
                'method': removed_connection.get('method', COMPANION_METHOD_UDP)
            }
            self._disconnect(removed_companion)
        self.connections = new_connections

    def _create_connection(self, companion):
        return {
            'method': companion.get('method', COMPANION_METHOD_UDP),
            'status': STATUS_READY if companion.get('method') == COMPANION_METHOD_HTTP else STATUS_DISCONNECTED,
            'error': '',
            'tcp': None,
            'udp': None,
            'udp_armed': False
        }

    def _save_companions(self):
        if not self._service_sync_in_progress:
            self._service_sync_in_progress = True
            try:
                config = {
                    'companions': self.companions,
                    'default_companion_id': self.default_companion_id
                }
                Registry().execute('service_set_companion_config', config)
            finally:
                self._service_sync_in_progress = False
        self.settings.setValue('companion/autotrigger enabled', self.autotrigger_enabled)
        self._refresh_live_autotrigger_markers()

    def _get_auto_connect_on_file_open(self):
        value = self.settings.value('companion/auto connect default on file open')
        return self._to_bool(value, default=True)

    def _apply_autotrigger_mode_on_file_open(self):
        mode = str(self.settings.value('companion/autotrigger on file open mode') or 'last').strip().lower()
        if mode == 'on':
            self.autotrigger_enabled = True
            self.settings.setValue('companion/autotrigger enabled', True)
        elif mode == 'off':
            self.autotrigger_enabled = False
            self.settings.setValue('companion/autotrigger enabled', False)

    def _first_slide_safety_enabled(self):
        return self._to_bool(self.settings.value('companion/first slide safety'), default=False)

    def _refresh_companion_list(self):
        self.companion_list_widget.clear()
        selected_row = None
        for index, companion in enumerate(self.companions):
            item = QtWidgets.QListWidgetItem(self._format_companion_name(companion))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, companion['id'])
            self.companion_list_widget.addItem(item)
            if companion['id'] == self.selected_companion_id:
                selected_row = index
        if selected_row is None and self.companions:
            selected_row = 0
        if selected_row is not None:
            self.companion_list_widget.setCurrentRow(selected_row)
        else:
            self.selected_companion_id = None
            self._refresh_button_list()

    def _refresh_button_list(self):
        self.button_list_widget.clear()
        companion = self._get_selected_companion()
        if not companion:
            self.auto_trigger_list_widget.clear()
            self._update_icons()
            return
        for button in companion.get('buttons', []):
            text = '{name} ({page}/{row}/{column})'.format(name=button['name'],
                                                            page=button['page'],
                                                            row=button['row'],
                                                            column=button['column'])
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, button['id'])
            self.button_list_widget.addItem(item)
        if self.button_list_widget.count():
            self.button_list_widget.setCurrentRow(0)
        self._refresh_autotrigger_list()
        self._update_icons()
        self._update_status_label()

    def _refresh_autotrigger_list(self):
        self.auto_trigger_list_widget.clear()
        companion = self._get_selected_companion()
        if not companion:
            self._update_icons()
            return
        for trigger in companion.get('autotriggers', []):
            if not self._should_show_autotrigger(trigger):
                continue
            item = QtWidgets.QListWidgetItem(self._format_autotrigger_text(trigger))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, trigger.get('id'))
            self.auto_trigger_list_widget.addItem(item)
        if self.auto_trigger_list_widget.count():
            self.auto_trigger_list_widget.setCurrentRow(0)

    def _refresh_autotrigger_list_labels(self):
        companion = self._get_selected_companion()
        if not companion:
            return
        trigger_by_id = {trigger.get('id'): trigger for trigger in companion.get('autotriggers', [])}
        self.auto_trigger_list_widget.blockSignals(True)
        try:
            for index in range(self.auto_trigger_list_widget.count()):
                item = self.auto_trigger_list_widget.item(index)
                if item is None:
                    continue
                trigger_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
                trigger = trigger_by_id.get(trigger_id)
                if trigger and self._should_show_autotrigger(trigger):
                    item.setHidden(False)
                    item.setText(self._format_autotrigger_text(trigger))
                else:
                    item.setHidden(True)
        finally:
            self.auto_trigger_list_widget.blockSignals(False)

    def _should_show_autotrigger(self, trigger):
        if not self.filter_current_live_triggers:
            return True
        current_key = self._current_live_slide_key()
        if not current_key:
            return False
        return self._trigger_matches_item(trigger, current_key[0], current_key[1])

    def _format_autotrigger_text(self, trigger):
        mode = trigger.get('mode', AUTO_TRIGGER_ENTER_PRESS)
        mode_text = {
            AUTO_TRIGGER_ENTER_PRESS: translate('OpenLP.CompanionManager', 'On Enter: PRESS'),
            AUTO_TRIGGER_LEAVE_PRESS: translate('OpenLP.CompanionManager', 'On Leave: PRESS'),
            AUTO_TRIGGER_HOLD: translate('OpenLP.CompanionManager', 'On Enter: DOWN, On Leave: UP')
        }.get(mode, mode)
        item_name = self._resolve_service_item_name(
            str(trigger.get('item_ref', '') or ''),
            str(trigger.get('item_id', '') or '')
        ) or \
            translate('OpenLP.CompanionManager', 'Not exist')
        return '{name} | Item {item_name} Slide {slide} | {mode}'.format(
            name=trigger.get('name', ''),
            item_name=item_name,
            slide=trigger.get('slide_row', 0),
            mode=mode_text)

    def _format_companion_name(self, companion):
        companion_id = companion.get('id')
        connection = self.connections.get(companion_id, {})
        status = connection.get('status', STATUS_DISCONNECTED)
        default_text = ' [Default]' if companion_id == self.default_companion_id else ''
        return '{ip}:{port} ({method}) - {status}{default_text}'.format(ip=companion.get('ip', ''),
                                                                         port=companion.get('port', ''),
                                                                         method=str(companion.get('method', '')).upper(),
                                                                         status=status,
                                                                         default_text=default_text)

    def _get_selected_companion(self):
        if not self.selected_companion_id:
            return None
        for companion in self.companions:
            if companion['id'] == self.selected_companion_id:
                return companion
        return None

    def _get_selected_button(self):
        companion = self._get_selected_companion()
        if not companion:
            return None
        item = self.button_list_widget.currentItem()
        if item is None:
            return None
        button_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        for button in companion.get('buttons', []):
            if button['id'] == button_id:
                return button
        return None

    def _get_selected_autotrigger(self):
        companion = self._get_selected_companion()
        if not companion:
            return None
        item = self.auto_trigger_list_widget.currentItem()
        if item is None:
            return None
        trigger_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        for trigger in companion.get('autotriggers', []):
            if trigger.get('id') == trigger_id:
                return trigger
        return None

    def _update_icons(self, *_args):
        has_companion = self._get_selected_companion() is not None
        has_button = self._get_selected_button() is not None
        has_autotrigger = self._get_selected_autotrigger() is not None
        is_default = has_companion and self._get_selected_companion()['id'] == self.default_companion_id
        is_connected = has_companion and self._is_connected(self._get_selected_companion())
        self.companion_edit_button.setEnabled(has_companion)
        self.companion_delete_button.setEnabled(has_companion)
        self.companion_default_button.setEnabled(has_companion and not is_default)
        self.companion_connect_button.setEnabled(has_companion and not is_connected)
        self.companion_disconnect_button.setEnabled(has_companion and is_connected)
        self.button_add_button.setEnabled(has_companion)
        self.button_edit_button.setEnabled(has_button)
        self.button_delete_button.setEnabled(has_button)
        self.button_trigger_button.setEnabled(has_button)
        self.autotrigger_add_button.setEnabled(has_companion and has_button)
        self.autotrigger_edit_button.setEnabled(has_autotrigger)
        self.autotrigger_delete_button.setEnabled(has_autotrigger)
        self.autotrigger_toggle_button.setEnabled(True)
        self.autotrigger_filter_live_button.setEnabled(True)
        self._update_button_colours()

    def _update_button_colours(self):
        self.companion_connect_button.setStyleSheet('QPushButton { background-color: #2E7D32; color: white; }')
        self.companion_disconnect_button.setStyleSheet('QPushButton { background-color: #C62828; color: white; }')
        if self.autotrigger_enabled:
            self.autotrigger_toggle_button.setText(translate('OpenLP.CompanionManager', 'Auto Trigger: ON'))
            self.autotrigger_toggle_button.setChecked(True)
            self.autotrigger_toggle_button.setStyleSheet('QPushButton { background-color: #2E7D32; color: white; }')
        else:
            self.autotrigger_toggle_button.setText(translate('OpenLP.CompanionManager', 'Auto Trigger: OFF'))
            self.autotrigger_toggle_button.setChecked(False)
            self.autotrigger_toggle_button.setStyleSheet('QPushButton { background-color: #C62828; color: white; }')

    def on_companion_selected(self, *_args):
        item = self.companion_list_widget.currentItem()
        if item:
            self.selected_companion_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        else:
            self.selected_companion_id = None
        self._refresh_button_list()
        self._update_status_label()

    def _is_connected(self, companion):
        connection = self.connections.get(companion.get('id'))
        if not connection:
            return False
        method = companion.get('method')
        if method == COMPANION_METHOD_HTTP:
            return True
        if method == COMPANION_METHOD_UDP:
            return bool(connection.get('udp_armed'))
        return connection.get('status') == STATUS_CONNECTED

    def _update_status_label(self):
        companion = self._get_selected_companion()
        if companion is None:
            self.status_label.setText(translate('OpenLP.CompanionManager', 'Status: No companion selected'))
            return
        connection = self.connections.get(companion['id'], {})
        status = connection.get('status', STATUS_DISCONNECTED)
        error = connection.get('error', '')
        if error:
            self.status_label.setText(
                translate('OpenLP.CompanionManager', 'Status: {status} ({error})').format(status=status, error=error))
        else:
            self.status_label.setText(translate('OpenLP.CompanionManager', 'Status: {status}').format(status=status))

    def _show_inline_message(self, message, timeout_ms=5000):
        """
        Show a non-blocking status message in the dock panel.
        """
        self.status_label.setText(message)
        QtCore.QTimer.singleShot(timeout_ms, self._update_status_label)

    @staticmethod
    def _resolve_service_item_name(item_ref='', item_id=''):
        service_manager = Registry().get('service_manager')
        if service_manager and hasattr(service_manager, 'service_items'):
            items = getattr(service_manager, 'service_items', [])
            if isinstance(item_ref, str) and item_ref.startswith('index:'):
                try:
                    index = int(item_ref.split(':', 1)[1])
                    if 0 <= index < len(items):
                        entry = items[index]
                        service_item = entry.get('service_item') if isinstance(entry, dict) else None
                        if service_item:
                            title = getattr(service_item, 'title', None)
                            if title:
                                return title
                            display_title = getattr(service_item, 'get_display_title', None)
                            if callable(display_title):
                                try:
                                    return display_title()
                                except Exception:
                                    pass
                            return str(index + 1)
                except (TypeError, ValueError):
                    pass
            if item_id:
                for entry in items:
                    service_item = entry.get('service_item') if isinstance(entry, dict) else None
                    if service_item and str(getattr(service_item, 'unique_identifier', '')) == str(item_id):
                        title = getattr(service_item, 'title', None)
                        if title:
                            return title
                        display_title = getattr(service_item, 'get_display_title', None)
                        if callable(display_title):
                            try:
                                return display_title()
                            except Exception:
                                pass
                        return str(item_id)
        live_controller = Registry().get('live_controller')
        live_item = getattr(live_controller, 'service_item', None) if live_controller else None
        if item_id and live_item and str(getattr(live_item, 'unique_identifier', '')) == str(item_id):
            return getattr(live_item, 'title', str(item_id))
        return None

    @staticmethod
    def _resolve_service_item_ref(service_item):
        if not service_item:
            return ''
        service_manager = Registry().get('service_manager')
        if not service_manager or not hasattr(service_manager, 'service_items'):
            return ''
        items = getattr(service_manager, 'service_items', [])
        for index, entry in enumerate(items):
            candidate = entry.get('service_item') if isinstance(entry, dict) else None
            if candidate is service_item:
                return f'index:{index}'
        target_id = str(getattr(service_item, 'unique_identifier', ''))
        if not target_id:
            return ''
        for index, entry in enumerate(items):
            candidate = entry.get('service_item') if isinstance(entry, dict) else None
            if candidate and str(getattr(candidate, 'unique_identifier', '')) == target_id:
                return f'index:{index}'
        return ''

    @staticmethod
    def _resolve_item_ref_from_legacy_id(item_id):
        if not item_id:
            return ''
        service_manager = Registry().get('service_manager')
        if not service_manager or not hasattr(service_manager, 'service_items'):
            return ''
        for index, entry in enumerate(getattr(service_manager, 'service_items', [])):
            service_item = entry.get('service_item') if isinstance(entry, dict) else None
            if service_item and str(getattr(service_item, 'unique_identifier', '')) == str(item_id):
                return f'index:{index}'
        return ''

    def on_add_companion(self):
        dialog = CompanionEditForm(self)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        self.companions.append(dialog.companion)
        self.connections[dialog.companion['id']] = self._create_connection(dialog.companion)
        self.selected_companion_id = dialog.companion['id']
        self._save_companions()
        self._refresh_companion_list()
        self._update_status_label()

    def on_edit_companion(self):
        companion = self._get_selected_companion()
        if companion is None:
            return
        old_method = companion.get('method')
        dialog = CompanionEditForm(self)
        if dialog.exec(companion=companion) != QtWidgets.QDialog.DialogCode.Accepted:
            return
        self._disconnect(companion)
        self.connections[companion['id']] = self._create_connection(companion)
        self._save_companions()
        self._refresh_companion_list()
        if old_method in (COMPANION_METHOD_TCP, COMPANION_METHOD_UDP):
            self.on_connect_companion()

    def on_delete_companion(self):
        companion = self._get_selected_companion()
        if companion is None:
            return
        answer = QtWidgets.QMessageBox.question(
            self,
            translate('OpenLP.CompanionManager', 'Delete Companion'),
            translate('OpenLP.CompanionManager',
                      'Are you sure you want to delete "{name}"?').format(name=self._format_companion_name(companion)),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if answer != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self._disconnect(companion)
        self.companions = [item for item in self.companions if item['id'] != companion['id']]
        self.connections.pop(companion['id'], None)
        if self.default_companion_id == companion['id']:
            self.default_companion_id = ''
        self.selected_companion_id = None
        self._save_companions()
        self._refresh_companion_list()

    def on_add_button(self):
        companion = self._get_selected_companion()
        if companion is None:
            return
        dialog = CompanionButtonEditForm(self)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        companion.setdefault('buttons', [])
        companion['buttons'].append(dialog.button_data)
        self._save_companions()
        self._refresh_button_list()

    def on_edit_button(self):
        companion = self._get_selected_companion()
        button = self._get_selected_button()
        if companion is None or button is None:
            return
        dialog = CompanionButtonEditForm(self)
        if dialog.exec(button=button) != QtWidgets.QDialog.DialogCode.Accepted:
            return
        for index, item in enumerate(companion.get('buttons', [])):
            if item['id'] == button['id']:
                companion['buttons'][index] = dialog.button_data
                break
        self._save_companions()
        self._refresh_button_list()

    def on_delete_button(self):
        companion = self._get_selected_companion()
        button = self._get_selected_button()
        if companion is None or button is None:
            return
        companion['buttons'] = [item for item in companion.get('buttons', []) if item['id'] != button['id']]
        companion['autotriggers'] = [t for t in companion.get('autotriggers', []) if t.get('button_id') != button['id']]
        self._save_companions()
        self._refresh_button_list()

    def on_add_autotrigger(self):
        companion = self._get_selected_companion()
        button = self._get_selected_button()
        if companion is None or button is None:
            return
        dialog = CompanionAutoTriggerEditForm(self)
        if dialog.exec(buttons=companion.get('buttons', []),
                       item_name_resolver=self._resolve_service_item_name,
                       preferred_button_id=button.get('id')) != QtWidgets.QDialog.DialogCode.Accepted:
            return
        companion.setdefault('autotriggers', [])
        companion['autotriggers'].append(dialog.trigger_data)
        self._save_companions()
        self._refresh_autotrigger_list()

    def on_edit_autotrigger(self):
        companion = self._get_selected_companion()
        trigger = self._get_selected_autotrigger()
        if companion is None or trigger is None:
            return
        dialog = CompanionAutoTriggerEditForm(self)
        if dialog.exec(buttons=companion.get('buttons', []), trigger_data=trigger,
                       item_name_resolver=self._resolve_service_item_name) != \
                QtWidgets.QDialog.DialogCode.Accepted:
            return
        for index, item in enumerate(companion.get('autotriggers', [])):
            if item.get('id') == trigger.get('id'):
                companion['autotriggers'][index] = dialog.trigger_data
                break
        self._save_companions()
        self._refresh_autotrigger_list()

    def on_delete_autotrigger(self):
        companion = self._get_selected_companion()
        trigger = self._get_selected_autotrigger()
        if companion is None or trigger is None:
            return
        companion['autotriggers'] = [item for item in companion.get('autotriggers', [])
                                     if item.get('id') != trigger.get('id')]
        self._save_companions()
        self._refresh_autotrigger_list()

    def on_companion_context_menu(self, point):
        menu = QtWidgets.QMenu(self)
        add_action = menu.addAction(translate('OpenLP.CompanionManager', 'Add Companion'))
        edit_action = menu.addAction(translate('OpenLP.CompanionManager', 'Edit Companion'))
        delete_action = menu.addAction(translate('OpenLP.CompanionManager', 'Delete Companion'))
        selected = self._get_selected_companion() is not None
        edit_action.setEnabled(selected)
        delete_action.setEnabled(selected)
        action = menu.exec(self.companion_list_widget.mapToGlobal(point))
        if action == add_action:
            self.on_add_companion()
        elif action == edit_action:
            self.on_edit_companion()
        elif action == delete_action:
            self.on_delete_companion()

    def on_button_context_menu(self, point):
        menu = QtWidgets.QMenu(self)
        add_action = menu.addAction(translate('OpenLP.CompanionManager', 'Add Button'))
        edit_action = menu.addAction(translate('OpenLP.CompanionManager', 'Edit Button'))
        delete_action = menu.addAction(translate('OpenLP.CompanionManager', 'Delete Button'))
        trigger_action = menu.addAction(translate('OpenLP.CompanionManager', 'Trigger Button'))
        selected = self._get_selected_button() is not None
        has_companion = self._get_selected_companion() is not None
        add_action.setEnabled(has_companion)
        edit_action.setEnabled(selected)
        delete_action.setEnabled(selected)
        trigger_action.setEnabled(selected)
        action = menu.exec(self.button_list_widget.mapToGlobal(point))
        if action == add_action:
            self.on_add_button()
        elif action == edit_action:
            self.on_edit_button()
        elif action == delete_action:
            self.on_delete_button()
        elif action == trigger_action:
            self.on_trigger_button()

    def on_autotrigger_context_menu(self, point):
        menu = QtWidgets.QMenu(self)
        add_action = menu.addAction(translate('OpenLP.CompanionManager', 'Add Auto Trigger'))
        edit_action = menu.addAction(translate('OpenLP.CompanionManager', 'Edit Auto Trigger'))
        delete_action = menu.addAction(translate('OpenLP.CompanionManager', 'Delete Auto Trigger'))
        selected = self._get_selected_autotrigger() is not None
        add_enabled = self._get_selected_companion() is not None and self._get_selected_button() is not None
        add_action.setEnabled(add_enabled)
        edit_action.setEnabled(selected)
        delete_action.setEnabled(selected)
        action = menu.exec(self.auto_trigger_list_widget.mapToGlobal(point))
        if action == add_action:
            self.on_add_autotrigger()
        elif action == edit_action:
            self.on_edit_autotrigger()
        elif action == delete_action:
            self.on_delete_autotrigger()

    def on_set_default_companion(self):
        companion = self._get_selected_companion()
        if companion is None:
            return
        self.default_companion_id = companion['id']
        self._save_companions()
        self._refresh_companion_list()
        self._update_icons()

    def on_toggle_autotrigger_enabled(self):
        self.autotrigger_enabled = not self.autotrigger_enabled
        self._save_companions()
        self._update_button_colours()
        status = translate('OpenLP.CompanionManager', 'enabled') if self.autotrigger_enabled else \
            translate('OpenLP.CompanionManager', 'disabled')
        self._show_inline_message(translate('OpenLP.CompanionManager', 'Auto Trigger is now {state}.').format(
            state=status))

    def on_toggle_autotrigger_filter_live(self):
        self.filter_current_live_triggers = bool(self.autotrigger_filter_live_button.isChecked())
        self._refresh_autotrigger_list()

    def _set_status(self, companion_id, status, error=''):
        if companion_id not in self.connections:
            return
        self.connections[companion_id]['status'] = status
        self.connections[companion_id]['error'] = error
        self._trace(f'status[{companion_id}] -> {status}{" | " + error if error else ""}')
        self._refresh_companion_list_labels()
        self._update_icons()
        self._update_status_label()

    def _refresh_companion_list_labels(self):
        self.companion_list_widget.blockSignals(True)
        try:
            for index in range(self.companion_list_widget.count()):
                item = self.companion_list_widget.item(index)
                if item is None:
                    continue
                companion_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
                companion = next((c for c in self.companions if c.get('id') == companion_id), None)
                if companion:
                    item.setText(self._format_companion_name(companion))
        finally:
            self.companion_list_widget.blockSignals(False)

    def _get_connection(self, companion):
        companion_id = companion['id']
        if companion_id not in self.connections:
            self.connections[companion_id] = self._create_connection(companion)
        connection = self.connections[companion_id]
        connection['method'] = companion.get('method')
        return connection

    def on_connect_companion(self):
        companion = self._get_selected_companion()
        if companion is None:
            return
        self._connect(companion)

    def on_disconnect_companion(self):
        companion = self._get_selected_companion()
        if companion is None:
            return
        if companion['id'] in self._disconnect_in_progress:
            return
        self._disconnect(companion)
        self._set_status(companion['id'], STATUS_DISCONNECTED)

    def _connect(self, companion):
        method = companion.get('method')
        companion_id = companion['id']
        ip = companion.get('ip')
        port = int(companion.get('port', COMPANION_DEFAULT_PORTS.get(method, 0)))
        self._trace(f'connect requested: {companion_id} {method.upper()} {ip}:{port}')
        connection = self._get_connection(companion)
        if method == COMPANION_METHOD_HTTP:
            self._set_status(companion_id, STATUS_READY)
            return
        self._disconnect(companion)
        if method == COMPANION_METHOD_UDP:
            connection['udp_armed'] = True
            self._set_status(companion_id, STATUS_ARMED)
            return
        self._set_status(companion_id, STATUS_CONNECTING)
        if method == COMPANION_METHOD_TCP:
            sock = connection.get('tcp')
            if sock is None:
                sock = QtNetwork.QTcpSocket(self)
                sock.connected.connect(lambda cid=companion_id: self._on_tcp_connected(cid))
                sock.disconnected.connect(lambda cid=companion_id: self._on_tcp_disconnected(cid))
                sock.errorOccurred.connect(lambda err, cid=companion_id: self._on_tcp_error(cid, err))
                connection['tcp'] = sock
            sock.blockSignals(False)
            sock.connectToHost(ip, port)
            return

    def _disconnect(self, companion):
        connection = self._get_connection(companion)
        companion_id = companion.get('id')
        self._trace(f'disconnect requested: {companion_id} {companion.get("method", "").upper()}')
        if companion_id in self._disconnect_in_progress:
            return
        self._disconnect_in_progress.add(companion_id)
        try:
            connection['udp_armed'] = False
            tcp = connection.get('tcp')
            if tcp is not None:
                try:
                    if tcp.state() != QtNetwork.QAbstractSocket.SocketState.UnconnectedState:
                        tcp.disconnectFromHost()
                        tcp.abort()
                    tcp.close()
                except Exception as err:
                    self._trace(f'tcp disconnect error: {err}')
            udp = connection.get('udp')
            if udp is not None:
                try:
                    if udp.state() != QtNetwork.QAbstractSocket.SocketState.UnconnectedState:
                        udp.disconnectFromHost()
                    udp.close()
                except Exception as err:
                    self._trace(f'udp disconnect error: {err}')
        finally:
            self._disconnect_in_progress.discard(companion_id)

    def _on_tcp_connected(self, companion_id):
        self._trace(f'tcp connected: {companion_id}')
        self._set_status(companion_id, STATUS_CONNECTED)

    def _on_tcp_disconnected(self, companion_id):
        self._trace(f'tcp disconnected: {companion_id}')
        self._set_status(companion_id, STATUS_DISCONNECTED)

    def _on_tcp_error(self, companion_id, _error):
        self._trace(f'tcp error: {companion_id}')
        self._set_status(companion_id, STATUS_ERROR)

    def _on_udp_state_changed(self, companion_id, state):
        self._set_status(
            companion_id,
            STATUS_CONNECTED if state == QtNetwork.QAbstractSocket.SocketState.ConnectedState
            else STATUS_DISCONNECTED if state == QtNetwork.QAbstractSocket.SocketState.UnconnectedState
            else STATUS_CONNECTING
        )

    def _on_udp_error(self, companion_id, _error):
        self._set_status(companion_id, STATUS_ERROR)

    def _auto_connect_default(self):
        if not self._get_auto_connect_on_file_open():
            self._trace('auto-connect skipped: setting disabled')
            return
        if not self.default_companion_id:
            self._trace('auto-connect skipped: no default companion')
            return
        for companion in self.companions:
            if companion.get('id') == self.default_companion_id:
                self.selected_companion_id = companion['id']
                self._refresh_companion_list()
                self._connect(companion)
                break

    def _hook_live_controller(self):
        try:
            registry = Registry()
            if not hasattr(registry, 'service_list'):
                return
            controller = registry.get('live_controller')
        except Exception:
            return
        if controller is None:
            QtCore.QTimer.singleShot(1000, self._hook_live_controller)
            return
        if controller is self.live_controller:
            return
        if self.live_controller is not None:
            try:
                self.live_controller.slidecontroller_changed.disconnect(self.on_live_output_changed)
            except Exception:
                pass
        self.live_controller = controller
        self.live_controller.slidecontroller_changed.connect(self.on_live_output_changed)
        self._last_live_slide_key = self._current_live_slide_key()
        self._refresh_live_autotrigger_markers()

    def _hook_service_manager(self):
        try:
            registry = Registry()
            if not hasattr(registry, 'service_list'):
                return
            manager = registry.get('service_manager')
        except Exception:
            return
        if manager is None:
            QtCore.QTimer.singleShot(1000, self._hook_service_manager)
            return
        if manager is self.service_manager:
            return
        if self.service_manager is not None:
            try:
                self.service_manager.servicemanager_changed.disconnect(self.on_service_manager_changed)
            except Exception:
                pass
        self.service_manager = manager
        self.service_manager.servicemanager_changed.connect(self.on_service_manager_changed)

    def on_service_manager_changed(self):
        if self._service_sync_in_progress:
            return
        results = Registry().execute('service_get_companion_config')
        config = results[0] if results else None
        signature = self._config_signature(config if isinstance(config, dict) else {})
        if signature == self._last_service_config_signature:
            self._refresh_autotrigger_list_labels()
            return
        current_selection = self.selected_companion_id
        self._load_companions()
        self._apply_autotrigger_mode_on_file_open()
        self.selected_companion_id = current_selection
        self._refresh_companion_list()
        self._update_icons()
        self._refresh_live_autotrigger_markers()
        self._auto_connect_default()

    def _current_live_slide_key(self):
        controller = self.live_controller or Registry().get('live_controller')
        service_item = getattr(controller, 'service_item', None) if controller else None
        if controller is None or not service_item:
            return None
        item_ref = self._resolve_service_item_ref(service_item)
        item_id = str(getattr(service_item, 'unique_identifier', ''))
        row = int(getattr(controller, 'selected_row', 0) or 0)
        return item_ref, item_id, row

    def on_live_output_changed(self, *_args):
        new_key = self._current_live_slide_key()
        if new_key == self._last_live_slide_key:
            self._refresh_live_autotrigger_markers()
            if self.filter_current_live_triggers:
                self._refresh_autotrigger_list()
            else:
                self._refresh_autotrigger_list_labels()
            return
        old_key = self._last_live_slide_key
        self._last_live_slide_key = new_key
        self._refresh_live_autotrigger_markers()
        if self.filter_current_live_triggers:
            self._refresh_autotrigger_list()
        else:
            self._refresh_autotrigger_list_labels()
        service_item_changed = bool(
            old_key is not None and new_key is not None and (old_key[0] != new_key[0] or old_key[1] != new_key[1])
        )
        if old_key is not None:
            self._run_autotriggers(old_key[0], old_key[1], old_key[2], on_enter=False)
        if new_key is not None:
            self._run_autotriggers(new_key[0], new_key[1], new_key[2], on_enter=True,
                                   service_item_changed=service_item_changed)

    @staticmethod
    def _trigger_matches_item(trigger, item_ref, item_id):
        trigger_ref = str(trigger.get('item_ref', '') or '')
        trigger_item_id = str(trigger.get('item_id', '') or '')
        if trigger_ref and item_ref:
            return trigger_ref == item_ref
        return trigger_item_id == str(item_id)

    def _build_live_row_markers(self):
        markers_by_row = {}
        if not self.autotrigger_enabled:
            return markers_by_row
        current_key = self._current_live_slide_key()
        if not current_key:
            return markers_by_row
        item_ref, item_id, _row = current_key
        for companion in self.companions:
            buttons_by_id = {button.get('id'): button for button in companion.get('buttons', [])}
            for trigger in companion.get('autotriggers', []):
                if not self._trigger_matches_item(trigger, item_ref, item_id):
                    continue
                try:
                    row = int(trigger.get('slide_row', -1))
                except (TypeError, ValueError):
                    continue
                if row < 0:
                    continue
                button = buttons_by_id.get(trigger.get('button_id'))
                button_name = str(button.get('name')) if button else translate('OpenLP.CompanionManager', 'Unknown')
                markers_by_row.setdefault(row, [])
                if button_name not in markers_by_row[row]:
                    markers_by_row[row].append(button_name)
        return markers_by_row

    def _refresh_live_autotrigger_markers(self):
        controller = self.live_controller or Registry().get('live_controller')
        if controller is None or not getattr(controller, 'preview_widget', None):
            return
        try:
            controller.preview_widget.set_row_markers(self._build_live_row_markers())
        except Exception as err:
            self._trace(f'failed to update live auto-trigger markers: {err}')

    def _run_autotriggers(self, item_ref, item_id, slide_row, on_enter, service_item_changed=False):
        if not self.autotrigger_enabled:
            return
        for companion in self.companions:
            buttons_by_id = {button.get('id'): button for button in companion.get('buttons', [])}
            for trigger in companion.get('autotriggers', []):
                if not self._trigger_matches_item(trigger, item_ref, item_id):
                    continue
                if int(trigger.get('slide_row', -1)) != int(slide_row):
                    continue
                mode = trigger.get('mode', AUTO_TRIGGER_ENTER_PRESS)
                if (on_enter and service_item_changed and int(slide_row) == 0 and self._first_slide_safety_enabled() and
                        mode in (AUTO_TRIGGER_ENTER_PRESS, AUTO_TRIGGER_HOLD)):
                    continue
                action = None
                if mode == AUTO_TRIGGER_ENTER_PRESS and on_enter:
                    action = 'PRESS'
                elif mode == AUTO_TRIGGER_LEAVE_PRESS and not on_enter:
                    action = 'PRESS'
                elif mode == AUTO_TRIGGER_HOLD:
                    action = 'DOWN' if on_enter else 'UP'
                if action is None:
                    continue
                button = buttons_by_id.get(trigger.get('button_id'))
                if button is None:
                    continue
                self._send_button_action(companion, button, action, source='auto')

    def on_trigger_button(self, *_args):
        companion = self._get_selected_companion()
        button = self._get_selected_button()
        if companion is None or button is None:
            return
        self._send_button_action(companion, button, 'PRESS', source='manual')

    def _send_button_action(self, companion, button, action, source='manual'):
        ip = companion['ip']
        port = int(companion['port'])
        method = companion['method']
        page = int(button['page'])
        row = int(button['row'])
        column = int(button['column'])
        if method == COMPANION_METHOD_HTTP:
            action_path = action.lower()
            url = f'http://{ip}:{port}/api/location/{page}/{row}/{column}/{action_path}'
            request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
            reply = self.network_manager.post(request, QtCore.QByteArray())
            reply.finished.connect(
                lambda r=reply, name=button['name'], comp=companion, act=action, src=source: self._handle_http_reply(
                    r, name, comp, act, src))
            return
        if not self._is_connected(companion):
            if source == 'manual':
                self._show_inline_message(
                    translate('OpenLP.CompanionManager',
                              'Not connected: connect "{ip}:{port}" before triggering buttons.').format(
                        ip=companion['ip'],
                        port=companion['port']))
            return
        command = f'LOCATION {page}/{row}/{column} {action}\n'.encode('utf-8')
        if method == COMPANION_METHOD_TCP:
            connection = self._get_connection(companion)
            tcp = connection.get('tcp')
            if tcp is not None:
                tcp.write(command)
            else:
                self._show_inline_message(
                    translate('OpenLP.CompanionManager', 'TCP socket is not available for selected companion.'))
            return
        udp_socket = QtNetwork.QUdpSocket(self)
        udp_socket.writeDatagram(command, QtNetwork.QHostAddress(ip), port)
        udp_socket.deleteLater()

    def _handle_http_reply(self, reply, button_name, companion, action='PRESS', source='manual'):
        if reply.error() != QtNetwork.QNetworkReply.NetworkError.NoError:
            message = translate('OpenLP.CompanionManager',
                                'Trigger {action} failed for "{name}" on {ip}:{port}: {error}').format(
                action=action,
                name=button_name,
                ip=companion['ip'],
                port=companion['port'],
                error=reply.errorString())
            if source == 'manual':
                self._show_inline_message(message)
        reply.deleteLater()
    @staticmethod
    def _to_bool(value, default=False):
        if value is None:
            return default
        if isinstance(value, str):
            return value.strip().lower() in ('1', 'true', 'yes', 'on')
        return bool(value)
