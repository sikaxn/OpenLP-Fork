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
:mod:`openlp.core.autoplayer.manager` module

Provides the dock widget for automating playback of service items.
"""
import json
import math
import uuid

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtMultimedia import QMediaPlayer

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media import MediaState, MediaType


class AutomationCueEditForm(QtWidgets.QDialog):
    """
    Dialog for creating/editing automation cues in one place.
    """
    def __init__(self, companions, parent=None):
        widget_parent = parent if isinstance(parent, QtWidgets.QWidget) else None
        super().__init__(widget_parent)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.companions = companions or []
        self.cue_data = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QGridLayout(self)

        self.companion_label = QtWidgets.QLabel(translate('OpenLP.AutoplayerManager', 'Companion:'), self)
        self.companion_combo = QtWidgets.QComboBox(self)
        self.companion_combo.currentIndexChanged.connect(self._populate_buttons)
        layout.addWidget(self.companion_label, 0, 0)
        layout.addWidget(self.companion_combo, 0, 1)

        self.button_label = QtWidgets.QLabel(translate('OpenLP.AutoplayerManager', 'Button:'), self)
        self.button_combo = QtWidgets.QComboBox(self)
        layout.addWidget(self.button_label, 1, 0)
        layout.addWidget(self.button_combo, 1, 1)

        self.follow_autotrigger_checkbox = QtWidgets.QCheckBox(
            translate('OpenLP.AutoplayerManager', 'Follow autotrigger on/off'), self)
        self.follow_autotrigger_checkbox.setChecked(True)
        layout.addWidget(self.follow_autotrigger_checkbox, 2, 0, 1, 2)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Save, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box, 3, 0, 1, 2)

    def _populate_companions(self):
        self.companion_combo.blockSignals(True)
        self.companion_combo.clear()
        for companion in self.companions:
            companion_label = '{ip}:{port}'.format(ip=companion.get('ip', ''), port=companion.get('port', ''))
            self.companion_combo.addItem(companion_label, companion)
        self.companion_combo.blockSignals(False)
        self._populate_buttons()

    def _populate_buttons(self):
        self.button_combo.clear()
        companion = self.companion_combo.currentData()
        if not isinstance(companion, dict):
            return
        for button in companion.get('buttons', []) or []:
            label = '{name} ({page}/{row}/{column})'.format(
                name=button.get('name', ''),
                page=button.get('page', ''),
                row=button.get('row', ''),
                column=button.get('column', '')
            )
            self.button_combo.addItem(label, button)

    def exec(self, cue_data=None):
        self.cue_data = dict(cue_data) if isinstance(cue_data, dict) else {}
        self._populate_companions()
        target_companion_id = str(self.cue_data.get('companion_id', '') or '')
        target_button_id = str(self.cue_data.get('button_id', '') or '')
        if target_companion_id:
            for index in range(self.companion_combo.count()):
                companion = self.companion_combo.itemData(index)
                if isinstance(companion, dict) and str(companion.get('id', '') or '') == target_companion_id:
                    self.companion_combo.setCurrentIndex(index)
                    break
        self._populate_buttons()
        if target_button_id:
            for index in range(self.button_combo.count()):
                button = self.button_combo.itemData(index)
                if isinstance(button, dict) and str(button.get('id', '') or '') == target_button_id:
                    self.button_combo.setCurrentIndex(index)
                    break
        self.follow_autotrigger_checkbox.setChecked(bool(self.cue_data.get('follow_autotrigger', True)))
        return super().exec()

    def accept(self):
        companion = self.companion_combo.currentData()
        button = self.button_combo.currentData()
        if not isinstance(companion, dict) or not isinstance(button, dict):
            QtWidgets.QMessageBox.warning(
                self,
                translate('OpenLP.AutoplayerManager', 'Invalid Selection'),
                translate('OpenLP.AutoplayerManager', 'Please select both Companion and Button.')
            )
            return
        self.cue_data = {
            'uid': str(self.cue_data.get('uid', '') or str(uuid.uuid4())),
            'type': 'automation',
            'companion_id': str(companion.get('id', '') or ''),
            'button_id': str(button.get('id', '') or ''),
            'action': 'PRESS',
            'label': str(button.get('name', '') or ''),
            'follow_autotrigger': self.follow_autotrigger_checkbox.isChecked()
        }
        super().accept()


class AutoplayerManager(QtWidgets.QWidget):
    """
    Manage playlists made from service items and play them automatically.
    """
    def __init__(self, parent=None):
        widget_parent = parent if isinstance(parent, QtWidgets.QWidget) else None
        super().__init__(widget_parent)
        self.playlists = []
        self.selected_playlist_id = ''
        self.auto_advance_seconds = 5
        self.loop_enabled = False

        self.service_manager = None
        self.live_controller = None
        self.media_controller = None
        self._service_sync_in_progress = False
        self._last_service_config_signature = ''
        self._last_service_item_order = []

        self._is_playing = False
        self._is_paused = False
        self._stop_after_current = False
        self._active_playlist_index = -1
        self._active_entry_type = 'service'
        self._active_item_id = ''
        self._active_item_is_media = False
        self._active_item_plugin_name = ''
        self._media_has_started = False
        self._active_item_started_msecs = 0
        self._slide_due_msecs = 0
        self._slide_remaining_msecs = 0
        self._last_autotrigger_enabled_state = None

        self._setup_ui()
        self._tick_timer = QtCore.QTimer(self)
        self._tick_timer.setInterval(250)
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_timer.start()

        self._load_config()
        self._refresh_playlist_list()
        self._refresh_playlist_items()
        self._hook_service_manager()
        self._hook_live_controller()
        self._hook_media_controller()
        self._last_autotrigger_enabled_state = self._is_companion_autotrigger_enabled()
        self._update_transport_state()

    @staticmethod
    def _config_signature(config):
        if not isinstance(config, dict):
            return ''
        try:
            return json.dumps(config, sort_keys=True, separators=(',', ':'))
        except (TypeError, ValueError):
            return ''

    def _setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

        self.tabs = QtWidgets.QTabWidget(self)
        self.layout.addWidget(self.tabs, 1)

        self.playlist_tab = QtWidgets.QWidget(self.tabs)
        self.playlist_tab_layout = QtWidgets.QVBoxLayout(self.playlist_tab)
        self.playlist_actions_layout = QtWidgets.QHBoxLayout()
        self.playlist_add_button = QtWidgets.QPushButton(UiIcons().new, translate('OpenLP.AutoplayerManager', 'Add'))
        self.playlist_rename_button = QtWidgets.QPushButton(UiIcons().edit,
                                                            translate('OpenLP.AutoplayerManager', 'Rename'))
        self.playlist_delete_button = QtWidgets.QPushButton(UiIcons().delete,
                                                            translate('OpenLP.AutoplayerManager', 'Delete'))
        self.playlist_actions_layout.addWidget(self.playlist_add_button)
        self.playlist_actions_layout.addWidget(self.playlist_rename_button)
        self.playlist_actions_layout.addWidget(self.playlist_delete_button)
        self.playlist_tab_layout.addLayout(self.playlist_actions_layout)
        self.playlist_list_widget = QtWidgets.QListWidget(self.playlist_tab)
        self.playlist_list_widget.setAlternatingRowColors(True)
        self.playlist_tab_layout.addWidget(self.playlist_list_widget, 1)
        self.tabs.addTab(self.playlist_tab, translate('OpenLP.AutoplayerManager', 'Playlist'))

        self.content_tab = QtWidgets.QWidget(self.tabs)
        self.content_tab_layout = QtWidgets.QVBoxLayout(self.content_tab)
        self.content_actions_layout = QtWidgets.QHBoxLayout()
        self.content_add_service_button = QtWidgets.QPushButton(
            UiIcons().plus, translate('OpenLP.AutoplayerManager', 'Add Selected Service Item'))
        self.content_add_pause_button = QtWidgets.QPushButton(
            UiIcons().time, translate('OpenLP.AutoplayerManager', 'Add Pause'))
        self.content_add_manual_pause_button = QtWidgets.QPushButton(
            UiIcons().pause, translate('OpenLP.AutoplayerManager', 'Add Pause (Manual)'))
        self.content_add_automation_button = QtWidgets.QPushButton(
            UiIcons().remote, translate('OpenLP.AutoplayerManager', 'Add Automation'))
        self.content_remove_button = QtWidgets.QPushButton(UiIcons().minus,
                                                           translate('OpenLP.AutoplayerManager', 'Remove'))
        self.content_up_button = QtWidgets.QPushButton(UiIcons().move_up, '')
        self.content_up_button.setToolTip(translate('OpenLP.AutoplayerManager', 'Move selected item up'))
        self.content_down_button = QtWidgets.QPushButton(UiIcons().move_down, '')
        self.content_down_button.setToolTip(translate('OpenLP.AutoplayerManager', 'Move selected item down'))
        self.content_actions_layout.addWidget(self.content_add_service_button)
        self.content_actions_layout.addWidget(self.content_add_pause_button)
        self.content_actions_layout.addWidget(self.content_add_manual_pause_button)
        self.content_actions_layout.addWidget(self.content_add_automation_button)
        self.content_actions_layout.addWidget(self.content_remove_button)
        self.content_actions_layout.addWidget(self.content_up_button)
        self.content_actions_layout.addWidget(self.content_down_button)
        self.content_tab_layout.addLayout(self.content_actions_layout)
        self.playlist_items_widget = QtWidgets.QListWidget(self.content_tab)
        self.playlist_items_widget.setAlternatingRowColors(True)
        self.playlist_items_widget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.playlist_items_widget.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.content_tab_layout.addWidget(self.playlist_items_widget, 1)
        self.tabs.addTab(self.content_tab, translate('OpenLP.AutoplayerManager', 'Playlist Content'))

        self.transport_layout = QtWidgets.QHBoxLayout()
        self.play_button = QtWidgets.QPushButton(UiIcons().play, translate('OpenLP.AutoplayerManager', 'Play'))
        self.pause_button = QtWidgets.QPushButton(UiIcons().pause, translate('OpenLP.AutoplayerManager', 'Pause'))
        self.stop_button = QtWidgets.QPushButton(UiIcons().stop, translate('OpenLP.AutoplayerManager', 'Stop'))
        self.loop_button = QtWidgets.QPushButton(UiIcons().loop, translate('OpenLP.AutoplayerManager', 'Loop'))
        self.loop_button.setCheckable(True)
        self.stop_after_button = QtWidgets.QPushButton(translate('OpenLP.AutoplayerManager', 'Stop After'))
        self.stop_after_button.setCheckable(True)
        self.transport_layout.addWidget(self.play_button)
        self.transport_layout.addWidget(self.pause_button)
        self.transport_layout.addWidget(self.stop_button)
        self.transport_layout.addWidget(self.loop_button)
        self.transport_layout.addWidget(self.stop_after_button)
        self.layout.addLayout(self.transport_layout)

        self.auto_advance_layout = QtWidgets.QHBoxLayout()
        self.auto_advance_label = QtWidgets.QLabel(translate('OpenLP.AutoplayerManager', 'Auto advance (seconds):'))
        self.auto_advance_spin = QtWidgets.QSpinBox(self)
        self.auto_advance_spin.setRange(1, 180)
        self.auto_advance_spin.setValue(5)
        self.auto_advance_layout.addWidget(self.auto_advance_label)
        self.auto_advance_layout.addWidget(self.auto_advance_spin)
        self.auto_advance_layout.addStretch(1)
        self.layout.addLayout(self.auto_advance_layout)

        self.status_label = QtWidgets.QLabel('', self)
        self.layout.addWidget(self.status_label)

        self.playlist_add_button.clicked.connect(self.on_add_playlist)
        self.playlist_rename_button.clicked.connect(self.on_rename_playlist)
        self.playlist_delete_button.clicked.connect(self.on_delete_playlist)
        self.playlist_list_widget.currentItemChanged.connect(self.on_playlist_selected)
        self.playlist_list_widget.itemDoubleClicked.connect(self.on_playlist_double_clicked)
        self.playlist_items_widget.itemDoubleClicked.connect(self.on_playlist_item_double_clicked)
        self.playlist_items_widget.model().rowsMoved.connect(self.on_playlist_items_reordered)
        self.content_add_service_button.clicked.connect(self.on_add_selected_service_items)
        self.content_add_pause_button.clicked.connect(self.on_add_pause_cue)
        self.content_add_manual_pause_button.clicked.connect(self.on_add_manual_pause_cue)
        self.content_add_automation_button.clicked.connect(self.on_add_automation_cue)
        self.content_remove_button.clicked.connect(self.on_remove_playlist_item)
        self.content_up_button.clicked.connect(self.on_move_playlist_item_up)
        self.content_down_button.clicked.connect(self.on_move_playlist_item_down)
        self.play_button.clicked.connect(self.on_restart_from_beginning)
        self.pause_button.clicked.connect(self.on_play_pause_current)
        self.stop_button.clicked.connect(self.on_stop)
        self.loop_button.clicked.connect(self.on_loop_toggled)
        self.stop_after_button.clicked.connect(self.on_stop_after_toggled)
        self.auto_advance_spin.valueChanged.connect(self.on_auto_advance_changed)

    def _hook_service_manager(self):
        manager = self._safe_registry_get('service_manager')
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
        self._last_service_item_order = self._service_item_order()
        if self.playlists:
            changed = self._refresh_refs_from_current_service()
            if changed:
                self._save_config(modified=False)
                self._refresh_playlist_items()

    def _hook_live_controller(self):
        controller = self._safe_registry_get('live_controller')
        if controller is None:
            QtCore.QTimer.singleShot(1000, self._hook_live_controller)
            return
        self.live_controller = controller

    def _hook_media_controller(self):
        controller = self._safe_registry_get('media_controller')
        if controller is None:
            QtCore.QTimer.singleShot(1000, self._hook_media_controller)
            return
        if controller is self.media_controller:
            return
        if self.media_controller is not None:
            try:
                self.media_controller.live_media_status_changed.disconnect(self.on_live_media_finished)
            except Exception:
                pass
        self.media_controller = controller
        self.media_controller.live_media_status_changed.connect(self.on_live_media_finished)

    def on_live_media_finished(self):
        """
        Advance playlist when current live media/audio item reaches end.
        """
        if not self._is_playing or self._is_paused or not self._active_item_is_media:
            return
        # Guard against stale finish events from previous item transitions.
        if not self._active_item_id:
            return
        self._advance_to_next_playlist_item()

    def _load_config(self):
        config = None
        results = Registry().execute('service_get_autoplayer_config')
        if results:
            config = results[0]
        if not isinstance(config, dict):
            config = {}
        self._last_service_config_signature = self._config_signature(config)
        self.playlists = config.get('playlists', []) or []
        self.selected_playlist_id = config.get('selected_playlist_id', '') or ''
        self.auto_advance_seconds = int(config.get('auto_advance_seconds', 5) or 5)
        self.loop_enabled = bool(config.get('loop', False))
        for playlist in self.playlists:
            if 'id' not in playlist:
                playlist['id'] = str(uuid.uuid4())
            playlist.setdefault('name', translate('OpenLP.AutoplayerManager', 'Playlist'))
            items = []
            for entry in playlist.get('items', []):
                normalized = self._normalise_playlist_item_entry(entry)
                if normalized:
                    items.append(normalized)
            playlist['items'] = items
        self._refresh_refs_from_current_service()
        if self.selected_playlist_id and not self._find_playlist_by_id(self.selected_playlist_id):
            self.selected_playlist_id = ''
        if not self.selected_playlist_id and self.playlists:
            self.selected_playlist_id = self.playlists[0].get('id', '')
        self.auto_advance_spin.blockSignals(True)
        self.auto_advance_spin.setValue(self.auto_advance_seconds)
        self.auto_advance_spin.blockSignals(False)
        self.loop_button.setChecked(self.loop_enabled)

    def _save_config(self, modified=True):
        config = {
            'playlists': self.playlists,
            'selected_playlist_id': self.selected_playlist_id,
            'auto_advance_seconds': self.auto_advance_seconds,
            'loop': self.loop_enabled
        }
        self._last_service_config_signature = self._config_signature(config)
        self._service_sync_in_progress = True
        try:
            Registry().execute('service_set_autoplayer_config', config, modified)
        finally:
            self._service_sync_in_progress = False

    def _find_playlist_by_id(self, playlist_id):
        for playlist in self.playlists:
            if playlist.get('id') == playlist_id:
                return playlist
        return None

    def _current_playlist(self):
        return self._find_playlist_by_id(self.selected_playlist_id)

    def _service_item_order(self):
        if not self.service_manager:
            return []
        ordered_ids = []
        for entry in getattr(self.service_manager, 'service_items', []):
            service_item = entry.get('service_item') if isinstance(entry, dict) else None
            if service_item:
                ordered_ids.append(str(getattr(service_item, 'unique_identifier', '') or ''))
        return ordered_ids

    def _resolve_item_ref(self, service_item):
        if not self.service_manager or not service_item:
            return ''
        for index, entry in enumerate(getattr(self.service_manager, 'service_items', [])):
            candidate = entry.get('service_item') if isinstance(entry, dict) else None
            if candidate is service_item:
                return f'index:{index}'
        item_id = str(getattr(service_item, 'unique_identifier', '') or '')
        if not item_id:
            return ''
        for index, entry in enumerate(getattr(self.service_manager, 'service_items', [])):
            candidate = entry.get('service_item') if isinstance(entry, dict) else None
            if candidate and str(getattr(candidate, 'unique_identifier', '') or '') == item_id:
                return f'index:{index}'
        return ''

    def _service_item_from_ref_or_id(self, item_ref='', item_id=''):
        if self.service_manager and isinstance(item_ref, str) and item_ref.startswith('index:'):
            try:
                index = int(item_ref.split(':', 1)[1])
            except (TypeError, ValueError):
                index = -1
            if 0 <= index < len(self.service_manager.service_items):
                entry = self.service_manager.service_items[index]
                service_item = entry.get('service_item') if isinstance(entry, dict) else None
                if service_item:
                    return service_item
        if item_id:
            return self._service_item_by_id(item_id)
        return None

    @staticmethod
    def _entry_item_ref(entry):
        if not isinstance(entry, dict):
            return ''
        value = entry.get('item_ref', '')
        if value:
            return str(value)
        return ''

    @staticmethod
    def _entry_item_id(entry):
        if not isinstance(entry, dict):
            return ''
        if entry.get('item_id'):
            return str(entry.get('item_id'))
        if entry.get('service_item_id'):
            return str(entry.get('service_item_id'))
        return ''

    @staticmethod
    def _entry_type(entry):
        if not isinstance(entry, dict):
            return 'service'
        return str(entry.get('type') or 'service')

    @staticmethod
    def _entry_uid(entry):
        if not isinstance(entry, dict):
            return ''
        return str(entry.get('uid', '') or '')

    def _sync_playlist_refs_with_service_reorder(self):
        current_order = self._service_item_order()
        if not current_order:
            self._last_service_item_order = current_order
            return
        old_order = list(self._last_service_item_order or [])
        self._last_service_item_order = current_order
        if not old_order or old_order == current_order:
            return
        common_ids = set(old_order).intersection(set(current_order))
        minimum_expected_overlap = max(1, min(len(old_order), len(current_order)) // 2)
        if len(common_ids) < minimum_expected_overlap:
            return
        new_index_by_id = {item_id: index for index, item_id in enumerate(current_order)}
        changed = False
        for playlist in self.playlists:
            updated_items = []
            for entry in playlist.get('items', []):
                if self._entry_type(entry) != 'service':
                    updated_items.append(entry)
                    continue
                item_ref = self._entry_item_ref(entry)
                if not item_ref.startswith('index:'):
                    updated_items.append(entry)
                    continue
                try:
                    old_index = int(item_ref.split(':', 1)[1])
                except (TypeError, ValueError):
                    updated_items.append(entry)
                    continue
                if old_index < 0 or old_index >= len(old_order):
                    updated_items.append(entry)
                    continue
                old_item_id = old_order[old_index]
                new_index = new_index_by_id.get(old_item_id)
                if new_index is None:
                    changed = True
                    continue
                new_ref = f'index:{new_index}'
                if new_ref != item_ref:
                    entry['item_ref'] = new_ref
                    changed = True
                updated_items.append(entry)
            if len(updated_items) != len(playlist.get('items', [])):
                changed = True
            playlist['items'] = updated_items
        if changed:
            self._save_config()

    def _service_item_by_id(self, item_id):
        if not self.service_manager:
            return None
        for entry in getattr(self.service_manager, 'service_items', []):
            service_item = entry.get('service_item') if isinstance(entry, dict) else None
            if not service_item:
                continue
            if str(getattr(service_item, 'unique_identifier', '')) == str(item_id):
                return service_item
        return None

    def _display_name_for_item_id(self, item_id):
        service_item = self._service_item_by_id(item_id)
        if service_item:
            return service_item.get_display_title()
        return translate('OpenLP.AutoplayerManager', '[Missing] {item_id}').format(item_id=item_id)

    def _display_name_for_entry(self, entry):
        entry_type = self._entry_type(entry)
        if entry_type == 'pause':
            seconds = int(entry.get('seconds', 1) or 1)
            return translate('OpenLP.AutoplayerManager', '[Pause] {seconds} sec').format(seconds=seconds)
        if entry_type == 'pause_manual':
            return translate('OpenLP.AutoplayerManager', '[Pause] Manual Resume')
        if entry_type == 'automation':
            label = str(entry.get('label') or '')
            if label:
                return translate('OpenLP.AutoplayerManager', '[Automation] {label}').format(label=label)
            return translate('OpenLP.AutoplayerManager', '[Automation]')
        item_ref = self._entry_item_ref(entry)
        item_id = self._entry_item_id(entry)
        service_item = self._service_item_from_ref_or_id(item_ref, item_id)
        if service_item:
            return service_item.get_display_title()
        return translate('OpenLP.AutoplayerManager', '[Missing] {item}').format(item=item_ref or item_id)

    def _refresh_playlist_list(self):
        self.playlist_list_widget.blockSignals(True)
        try:
            self.playlist_list_widget.clear()
            selected_row = None
            for index, playlist in enumerate(self.playlists):
                item = QtWidgets.QListWidgetItem(str(playlist.get('name') or ''))
                item.setData(QtCore.Qt.ItemDataRole.UserRole, playlist.get('id'))
                self.playlist_list_widget.addItem(item)
                if playlist.get('id') == self.selected_playlist_id:
                    selected_row = index
            if selected_row is None and self.playlists:
                selected_row = 0
                self.selected_playlist_id = self.playlists[0].get('id', '')
            if selected_row is not None:
                self.playlist_list_widget.setCurrentRow(selected_row)
        finally:
            self.playlist_list_widget.blockSignals(False)
        self.playlist_rename_button.setEnabled(self._current_playlist() is not None)
        self.playlist_delete_button.setEnabled(self._current_playlist() is not None)

    def _refresh_playlist_items(self):
        playlist = self._current_playlist()
        selected_row = self.playlist_items_widget.currentRow()
        if selected_row < 0:
            selected_row = None
        self.playlist_items_widget.clear()
        if not playlist:
            self.content_remove_button.setEnabled(False)
            self.content_up_button.setEnabled(False)
            self.content_down_button.setEnabled(False)
            self._update_status(translate('OpenLP.AutoplayerManager', 'No playlist selected.'))
            return
        for index, entry in enumerate(playlist.get('items', []), start=1):
            label = '{index}. {name}'.format(index=index, name=self._display_name_for_entry(entry))
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, self._entry_uid(entry))
            item.setData(QtCore.Qt.ItemDataRole.UserRole + 1, self._entry_type(entry))
            if self._entry_type(entry) == 'automation':
                enabled = self._automation_entry_effective_enabled(entry)
                item.setForeground(QtGui.QBrush(QtGui.QColor('#15803d' if enabled else '#9ca3af')))
                item.setToolTip(
                    translate('OpenLP.AutoplayerManager', 'Automation enabled')
                    if enabled else translate('OpenLP.AutoplayerManager', 'Automation disabled'))
            self.playlist_items_widget.addItem(item)
        has_items = bool(playlist.get('items'))
        self.content_remove_button.setEnabled(has_items)
        self.content_up_button.setEnabled(has_items)
        self.content_down_button.setEnabled(has_items)
        if has_items:
            if selected_row is None:
                if 0 <= self._active_playlist_index < len(playlist.get('items', [])):
                    selected_row = self._active_playlist_index
                else:
                    selected_row = 0
            selected_row = max(0, min(selected_row, len(playlist.get('items', [])) - 1))
            self.playlist_items_widget.setCurrentRow(selected_row)
        self._update_status(translate('OpenLP.AutoplayerManager', '{count} item(s) in current playlist.').format(
            count=len(playlist.get('items', []))))

    def on_playlist_items_reordered(self, parent, start, end, destination, row):
        del parent, start, end, destination, row
        playlist = self._current_playlist()
        if not playlist:
            return
        items = playlist.get('items', [])
        if not items:
            return
        by_uid = {self._entry_uid(entry): entry for entry in items}
        reordered = []
        for index in range(self.playlist_items_widget.count()):
            uid = str(self.playlist_items_widget.item(index).data(QtCore.Qt.ItemDataRole.UserRole) or '')
            entry = by_uid.get(uid)
            if entry:
                reordered.append(entry)
        if len(reordered) != len(items):
            return
        playlist['items'] = reordered
        self._save_config()
        self._refresh_playlist_items()

    def _update_status(self, text):
        self.status_label.setText(text)

    def on_playlist_selected(self, current, previous=None):
        if current is None:
            return
        self.selected_playlist_id = str(current.data(QtCore.Qt.ItemDataRole.UserRole) or '')
        self._save_config()
        self._refresh_playlist_items()

    def on_playlist_double_clicked(self, item):
        """
        Open playlist content tab when a playlist is double-clicked.
        """
        del item
        self.tabs.setCurrentWidget(self.content_tab)

    def on_add_playlist(self):
        name, accepted = QtWidgets.QInputDialog.getText(
            self,
            translate('OpenLP.AutoplayerManager', 'New Playlist'),
            translate('OpenLP.AutoplayerManager', 'Playlist name:')
        )
        if not accepted:
            return
        playlist_name = str(name).strip()
        if not playlist_name:
            return
        playlist = {'id': str(uuid.uuid4()), 'name': playlist_name, 'items': []}
        self.playlists.append(playlist)
        self.selected_playlist_id = playlist['id']
        self._save_config()
        self._refresh_playlist_list()
        self._refresh_playlist_items()
        self.tabs.setCurrentWidget(self.content_tab)

    def on_rename_playlist(self):
        playlist = self._current_playlist()
        if not playlist:
            return
        name, accepted = QtWidgets.QInputDialog.getText(
            self,
            translate('OpenLP.AutoplayerManager', 'Rename Playlist'),
            translate('OpenLP.AutoplayerManager', 'Playlist name:'),
            text=str(playlist.get('name') or '')
        )
        if not accepted:
            return
        playlist_name = str(name).strip()
        if not playlist_name:
            return
        playlist['name'] = playlist_name
        self._save_config()
        self._refresh_playlist_list()

    def on_delete_playlist(self):
        playlist = self._current_playlist()
        if not playlist:
            return
        answer = QtWidgets.QMessageBox.question(
            self,
            translate('OpenLP.AutoplayerManager', 'Delete Playlist'),
            translate('OpenLP.AutoplayerManager', 'Delete playlist "{name}"?').format(name=playlist.get('name', '')),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if answer != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self.playlists = [entry for entry in self.playlists if entry.get('id') != playlist.get('id')]
        self.selected_playlist_id = self.playlists[0].get('id', '') if self.playlists else ''
        self._save_config()
        self._refresh_playlist_list()
        self._refresh_playlist_items()
        if self._is_playing and not self._current_playlist():
            self._stop_playback_runtime()

    def _selected_service_item_ids(self):
        items = []
        if not self.service_manager:
            return items
        seen = set()
        selected_items = self.service_manager.service_manager_list.selectedItems()
        for selected_item in selected_items:
            root_item = selected_item.parent() or selected_item
            pos = root_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            try:
                index = int(pos) - 1
            except (TypeError, ValueError):
                continue
            if index < 0 or index >= len(self.service_manager.service_items):
                continue
            service_item = self.service_manager.service_items[index].get('service_item')
            if not service_item:
                continue
            item_id = str(getattr(service_item, 'unique_identifier', '') or '')
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            items.append({
                'item_ref': self._resolve_item_ref(service_item),
                'item_id': item_id
            })
        return items

    def on_add_selected_service_items(self):
        playlist = self._current_playlist()
        if not playlist:
            self._update_status(translate('OpenLP.AutoplayerManager', 'Select or create a playlist first.'))
            return
        selected_entries = self._selected_service_item_ids()
        if not selected_entries:
            self._update_status(translate('OpenLP.AutoplayerManager', 'No service item selected.'))
            return
        for entry in selected_entries:
            entry['type'] = 'service'
            entry['uid'] = str(uuid.uuid4())
            playlist['items'].append(entry)
        self._save_config()
        self._refresh_playlist_items()

    def on_add_pause_cue(self):
        playlist = self._current_playlist()
        if not playlist:
            self._update_status(translate('OpenLP.AutoplayerManager', 'Select or create a playlist first.'))
            return
        seconds, ok = QtWidgets.QInputDialog.getInt(
            self,
            translate('OpenLP.AutoplayerManager', 'Add Pause'),
            translate('OpenLP.AutoplayerManager', 'Pause duration (seconds):'),
            3,
            1,
            3600,
            1
        )
        if not ok:
            return
        playlist['items'].append({'uid': str(uuid.uuid4()), 'type': 'pause', 'seconds': int(seconds)})
        self._save_config()
        self._refresh_playlist_items()

    def on_add_manual_pause_cue(self):
        playlist = self._current_playlist()
        if not playlist:
            self._update_status(translate('OpenLP.AutoplayerManager', 'Select or create a playlist first.'))
            return
        playlist['items'].append({'uid': str(uuid.uuid4()), 'type': 'pause_manual'})
        self._save_config()
        self._refresh_playlist_items()

    def _companions_with_buttons(self):
        results = Registry().execute('service_get_companion_config')
        config = results[0] if results and isinstance(results[0], dict) else {'companions': []}
        companions = []
        for companion in config.get('companions', []) or []:
            if companion.get('buttons'):
                companions.append(companion)
        return companions

    def on_add_automation_cue(self):
        playlist = self._current_playlist()
        if not playlist:
            self._update_status(translate('OpenLP.AutoplayerManager', 'Select or create a playlist first.'))
            return
        companions = self._companions_with_buttons()
        if not companions:
            QtWidgets.QMessageBox.information(
                self,
                translate('OpenLP.AutoplayerManager', 'No Companion Buttons'),
                translate('OpenLP.AutoplayerManager', 'No Companion with buttons is available in this service.')
            )
            return
        dialog = AutomationCueEditForm(companions, self)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        playlist['items'].append(dialog.cue_data)
        self._save_config()
        self._refresh_playlist_items()

    def on_playlist_item_double_clicked(self, item):
        """
        Open cue editor for pause/automation, or load service item live.
        """
        del item
        index = self.playlist_items_widget.currentRow()
        if index < 0:
            return
        playlist = self._current_playlist()
        if not playlist:
            return
        if index >= len(playlist.get('items', [])):
            return
        entry = playlist['items'][index]
        entry_type = self._entry_type(entry)
        if self._is_playing:
            if entry_type == 'service':
                self._is_paused = False
                self._active_playlist_index = index
                self._active_item_id = ''
                self._start_current_playlist_item()
                self._update_transport_state()
                return
            if entry_type == 'automation':
                self._trigger_automation_entry(entry)
                return
            # pause cues do nothing while autoplay is running
            return
        if entry_type == 'pause':
            self.on_edit_pause_cue(index)
            return
        if entry_type == 'pause_manual':
            return
        if entry_type == 'automation':
            self.on_edit_automation_cue(index)
            return
        if self._load_playlist_item_to_live(index):
            self._update_status(translate('OpenLP.AutoplayerManager', 'Loaded selected playlist item to live.'))

    def on_edit_pause_cue(self, index):
        playlist = self._current_playlist()
        if not playlist:
            return
        entry = playlist['items'][index]
        seconds, ok = QtWidgets.QInputDialog.getInt(
            self,
            translate('OpenLP.AutoplayerManager', 'Edit Pause'),
            translate('OpenLP.AutoplayerManager', 'Pause duration (seconds):'),
            int(entry.get('seconds', 1) or 1),
            1,
            3600,
            1
        )
        if not ok:
            return
        entry['seconds'] = int(seconds)
        self._save_config()
        self._refresh_playlist_items()
        self.playlist_items_widget.setCurrentRow(index)

    def on_edit_automation_cue(self, index):
        playlist = self._current_playlist()
        if not playlist:
            return
        companions = self._companions_with_buttons()
        if not companions:
            QtWidgets.QMessageBox.information(
                self,
                translate('OpenLP.AutoplayerManager', 'No Companion Buttons'),
                translate('OpenLP.AutoplayerManager', 'No Companion with buttons is available in this service.')
            )
            return
        entry = playlist['items'][index]
        dialog = AutomationCueEditForm(companions, self)
        if dialog.exec(cue_data=entry) != QtWidgets.QDialog.DialogCode.Accepted:
            return
        playlist['items'][index] = dialog.cue_data
        self._save_config()
        self._refresh_playlist_items()
        self.playlist_items_widget.setCurrentRow(index)

    def on_remove_playlist_item(self):
        playlist = self._current_playlist()
        if not playlist:
            return
        row = self.playlist_items_widget.currentRow()
        if row < 0 or row >= len(playlist.get('items', [])):
            return
        del playlist['items'][row]
        self._save_config()
        self._refresh_playlist_items()
        if self._is_playing:
            if self._active_playlist_index > row:
                self._active_playlist_index -= 1
            elif self._active_playlist_index == row:
                self._active_item_id = ''

    def on_move_playlist_item_up(self):
        playlist = self._current_playlist()
        if not playlist:
            return
        row = self.playlist_items_widget.currentRow()
        if row <= 0:
            return
        playlist['items'][row - 1], playlist['items'][row] = playlist['items'][row], playlist['items'][row - 1]
        self._save_config()
        self._refresh_playlist_items()
        self.playlist_items_widget.setCurrentRow(row - 1)

    def on_move_playlist_item_down(self):
        playlist = self._current_playlist()
        if not playlist:
            return
        row = self.playlist_items_widget.currentRow()
        if row < 0 or row >= len(playlist.get('items', [])) - 1:
            return
        playlist['items'][row + 1], playlist['items'][row] = playlist['items'][row], playlist['items'][row + 1]
        self._save_config()
        self._refresh_playlist_items()
        self.playlist_items_widget.setCurrentRow(row + 1)

    def on_auto_advance_changed(self, value):
        self.auto_advance_seconds = int(value)
        self._save_config()
        if self._is_playing and not self._active_item_is_media and not self._is_paused:
            now_msecs = QtCore.QDateTime.currentMSecsSinceEpoch()
            self._slide_due_msecs = now_msecs + (self.auto_advance_seconds * 1000)

    def on_loop_toggled(self):
        self.loop_enabled = bool(self.loop_button.isChecked())
        self._save_config()
        self._update_transport_state()

    def on_stop_after_toggled(self):
        self._stop_after_current = bool(self.stop_after_button.isChecked())
        if self._stop_after_current:
            self._update_status(translate('OpenLP.AutoplayerManager',
                                          'Will stop after current service item finishes.'))

    def _update_transport_state(self):
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(self._is_playing)
        if self._is_playing:
            self.play_button.setText(translate('OpenLP.AutoplayerManager', 'Restart'))
            self.play_button.setIcon(UiIcons().undo)
            if self._is_paused:
                self.pause_button.setText(translate('OpenLP.AutoplayerManager', 'Resume'))
                self.pause_button.setIcon(UiIcons().play)
                self.pause_button.setStyleSheet('background-color: #d97706; color: white;')
            else:
                self.pause_button.setText(translate('OpenLP.AutoplayerManager', 'Pause'))
                self.pause_button.setIcon(UiIcons().pause)
                self.pause_button.setStyleSheet('background-color: #0f766e; color: white;')
        else:
            self.play_button.setText(translate('OpenLP.AutoplayerManager', 'Play from Beginning'))
            self.play_button.setIcon(UiIcons().play)
            self.pause_button.setText(translate('OpenLP.AutoplayerManager', 'Play / Resume'))
            self.pause_button.setIcon(UiIcons().play)
            self.pause_button.setStyleSheet('')
        if self.loop_enabled:
            self.loop_button.setStyleSheet('background-color: #2563eb; color: white;')
        else:
            self.loop_button.setStyleSheet('')

    def on_restart_from_beginning(self):
        playlist = self._current_playlist()
        if not playlist or not playlist.get('items'):
            self._update_status(translate('OpenLP.AutoplayerManager', 'Current playlist is empty.'))
            return
        self._is_playing = True
        self._is_paused = False
        self._active_playlist_index = 0
        self._active_item_id = ''
        self._start_current_playlist_item()
        self._update_status(translate('OpenLP.AutoplayerManager', 'Autoplayer restarted from beginning.'))
        self._update_transport_state()

    def on_play_pause_current(self):
        playlist = self._current_playlist()
        if not playlist or not playlist.get('items'):
            self._update_status(translate('OpenLP.AutoplayerManager', 'Current playlist is empty.'))
            return
        if not self._is_playing:
            selected_index = self._selected_playlist_item_index()
            self._is_playing = True
            self._is_paused = False
            self._active_playlist_index = selected_index if selected_index >= 0 else 0
            self._active_item_id = ''
            self._start_current_playlist_item(preserve_live_if_same=True)
            self._update_status(translate('OpenLP.AutoplayerManager', 'Autoplayer started from current selection.'))
            self._update_transport_state()
            return
        self._is_paused = not self._is_paused
        if self._active_entry_type == 'pause_manual' and not self._is_paused:
            self._update_transport_state()
            self._advance_to_next_playlist_item()
            return
        if self._active_item_is_media:
            if self._is_paused:
                self._send_media_command('playbackPause')
            else:
                self._send_media_command('playbackPlay')
        else:
            now_msecs = QtCore.QDateTime.currentMSecsSinceEpoch()
            if self._is_paused:
                self._slide_remaining_msecs = max(0, self._slide_due_msecs - now_msecs)
            else:
                self._slide_due_msecs = now_msecs + max(0, self._slide_remaining_msecs)
        self._update_transport_state()

    def on_stop(self):
        self._stop_playback_runtime()
        self._update_status(translate('OpenLP.AutoplayerManager', 'Autoplayer stopped.'))
        self._update_transport_state()

    def _stop_playback_runtime(self):
        if self._active_item_is_media:
            self._send_media_command('playbackStop')
        self._is_playing = False
        self._is_paused = False
        self._active_entry_type = 'service'
        self._active_item_is_media = False
        self._active_item_plugin_name = ''
        self._media_has_started = False
        self._active_item_started_msecs = 0
        self._active_item_id = ''
        self._active_playlist_index = -1
        self._slide_due_msecs = 0
        self._slide_remaining_msecs = 0
        self._stop_after_current = False
        self.stop_after_button.setChecked(False)
        self._update_transport_state()

    def _selected_playlist_item_index(self):
        row = self.playlist_items_widget.currentRow()
        if row < 0:
            return -1
        playlist = self._current_playlist()
        if not playlist:
            return -1
        if row >= len(playlist.get('items', [])):
            return -1
        return row

    def _is_live_on_item(self, resolved_item_id):
        controller = self.live_controller or self._safe_registry_get('live_controller')
        live_item = getattr(controller, 'service_item', None) if controller else None
        if not live_item:
            return False
        return str(getattr(live_item, 'unique_identifier', '') or '') == str(resolved_item_id)

    def _is_live_audio_playing(self):
        """
        Check live audio backend state directly (used for LRC player reliability).
        """
        controller = self.live_controller or self._safe_registry_get('live_controller')
        if not controller:
            return False
        audio_player = getattr(controller, 'audio_player', None)
        media_player = getattr(audio_player, 'media_player', None) if audio_player else None
        if media_player is None or not hasattr(media_player, 'playbackState'):
            return False
        try:
            return media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        except Exception:
            return False

    def _is_live_media_backend_playing(self):
        """
        Check the active live media backend (audio/video) playback state directly.
        """
        controller = self.live_controller or self._safe_registry_get('live_controller')
        if not controller:
            return False
        media_play_item = getattr(controller, 'media_play_item', None)
        media_type = getattr(media_play_item, 'media_type', None) if media_play_item else None
        if media_type in [MediaType.Audio, MediaType.Dual]:
            backend = getattr(getattr(controller, 'audio_player', None), 'media_player', None)
        else:
            backend = getattr(getattr(controller, 'media_player', None), 'media_player', None)
        if backend is None or not hasattr(backend, 'playbackState'):
            return False
        try:
            return backend.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        except Exception:
            return False

    def _load_playlist_item_to_live(self, index):
        playlist = self._current_playlist()
        if not playlist:
            return False
        items = playlist.get('items', [])
        if index < 0 or index >= len(items):
            return False
        entry = items[index]
        if self._entry_type(entry) != 'service':
            return False
        service_item = self._service_item_from_ref_or_id(self._entry_item_ref(entry), self._entry_item_id(entry))
        if not service_item:
            return False
        resolved_item_id = str(getattr(service_item, 'unique_identifier', '') or '')
        if not resolved_item_id or not self.service_manager:
            return False
        self.service_manager.set_item_by_uuid(resolved_item_id)
        return True

    def _start_current_playlist_item(self, preserve_live_if_same=False):
        playlist = self._current_playlist()
        if not playlist:
            self._stop_playback_runtime()
            return
        items = playlist.get('items', [])
        if not items:
            self._stop_playback_runtime()
            return
        if self._active_playlist_index < 0 or self._active_playlist_index >= len(items):
            self._active_playlist_index = 0
        entry = items[self._active_playlist_index]
        entry_type = self._entry_type(entry)
        self._active_entry_type = entry_type
        if entry_type == 'pause':
            pause_seconds = int(entry.get('seconds', 1) or 1)
            self._active_item_is_media = False
            self._active_item_plugin_name = ''
            self._active_item_id = ''
            self._slide_remaining_msecs = pause_seconds * 1000
            self._slide_due_msecs = QtCore.QDateTime.currentMSecsSinceEpoch() + self._slide_remaining_msecs
            self._highlight_active_row()
            self._update_status(translate('OpenLP.AutoplayerManager', 'Pause cue: {seconds} second(s)').format(
                seconds=pause_seconds))
            return
        if entry_type == 'pause_manual':
            self._active_item_is_media = False
            self._active_item_plugin_name = ''
            self._active_item_id = ''
            self._slide_remaining_msecs = 0
            self._slide_due_msecs = 0
            self._is_paused = True
            self._highlight_active_row()
            self._update_status(translate('OpenLP.AutoplayerManager', 'Paused by cue. Resume manually.'))
            self._update_transport_state()
            return
        if entry_type == 'automation':
            self._active_item_is_media = False
            self._active_item_plugin_name = ''
            self._active_item_id = ''
            self._highlight_active_row()
            self._trigger_automation_entry(entry)
            QtCore.QTimer.singleShot(0, self._advance_to_next_playlist_item)
            return
        item_ref = self._entry_item_ref(entry)
        item_id = self._entry_item_id(entry)
        if not item_ref and not item_id:
            self._advance_to_next_playlist_item()
            return
        service_item = self._service_item_from_ref_or_id(item_ref, item_id)
        if not service_item:
            self._advance_to_next_playlist_item()
            return
        resolved_item_id = str(getattr(service_item, 'unique_identifier', '') or '')
        self._active_item_id = resolved_item_id
        self._active_item_plugin_name = str(getattr(service_item, 'name', '') or '')
        entry['item_ref'] = self._resolve_item_ref(service_item)
        entry['item_id'] = resolved_item_id
        self._active_item_is_media = self._service_item_has_media_playback(service_item)
        self._media_has_started = False
        self._active_item_started_msecs = QtCore.QDateTime.currentMSecsSinceEpoch()
        self._slide_remaining_msecs = self.auto_advance_seconds * 1000
        self._slide_due_msecs = QtCore.QDateTime.currentMSecsSinceEpoch() + self._slide_remaining_msecs
        already_live = self._is_live_on_item(resolved_item_id)
        if self.service_manager and not (preserve_live_if_same and already_live):
            self.service_manager.set_item_by_uuid(resolved_item_id)
        if self._active_item_is_media:
            self._disable_live_media_loop()
            self._request_media_autoplay(resolved_item_id)
        self._highlight_active_row()
        self._update_status(translate('OpenLP.AutoplayerManager', 'Now playing: {name}').format(
            name=service_item.get_display_title()))

    @staticmethod
    def _service_item_has_media_playback(service_item):
        """
        Determine if the service item should trigger media/audio playback controls.
        """
        if not service_item:
            return False
        if service_item.is_media() or service_item.requires_media():
            return True
        return bool(
            service_item.is_capable(ItemCapabilities.HasBackgroundAudio)
            or service_item.is_capable(ItemCapabilities.HasBackgroundVideo)
            or service_item.is_capable(ItemCapabilities.HasBackgroundStream)
            or service_item.is_capable(ItemCapabilities.CanStream)
        )

    def _request_media_autoplay(self, item_id):
        """
        Trigger playback after the service item is loaded to ensure both media and audio start.
        """
        def _try_play():
            if not self._is_playing or self._is_paused:
                return
            if self._active_item_id != item_id:
                return
            self._send_media_command('playbackPlay')

        _try_play()
        QtCore.QTimer.singleShot(120, _try_play)
        QtCore.QTimer.singleShot(350, _try_play)

    def _disable_live_media_loop(self):
        """
        Ensure live media loop is disabled when Autoplayer is handling media.
        """
        Settings().setValue('media/live loop', False)
        controller = self.live_controller or self._safe_registry_get('live_controller')
        if controller is None:
            return
        self._safe_registry_execute('playbackLoop', [controller, (False,)])

    def _send_media_command(self, event_name):
        """
        Send media toolbar-equivalent commands for the live controller.
        """
        controller = self.live_controller or self._safe_registry_get('live_controller')
        if controller is None:
            return
        self._safe_registry_execute(event_name, [controller])

    def _get_companion_manager(self):
        main_window = self._safe_registry_get('main_window')
        if not main_window:
            return None
        manager = getattr(main_window, 'companion_manager_contents', None)
        return manager

    @staticmethod
    def _safe_registry_get(key):
        """
        Safely access the Registry during startup/shutdown and test teardown.
        """
        try:
            return Registry().get(key)
        except Exception:
            return None

    @staticmethod
    def _safe_registry_execute(event_name, args=None):
        """
        Safely execute Registry events during startup/shutdown and test teardown.
        """
        try:
            return Registry().execute(event_name, args if args is not None else [])
        except Exception:
            return []

    @staticmethod
    def _to_bool(value, default=False):
        if value is None:
            return default
        if isinstance(value, str):
            return value.strip().lower() in ('1', 'true', 'yes', 'on')
        return bool(value)

    def _is_companion_autotrigger_enabled(self):
        companion_manager = self._get_companion_manager()
        if companion_manager is not None and hasattr(companion_manager, 'autotrigger_enabled'):
            return bool(getattr(companion_manager, 'autotrigger_enabled'))
        return self._to_bool(Settings().value('companion/autotrigger enabled'), default=True)

    def _automation_entry_effective_enabled(self, entry):
        if self._entry_type(entry) != 'automation':
            return True
        if not bool(entry.get('enabled', True)):
            return False
        if bool(entry.get('follow_autotrigger', True)):
            return self._is_companion_autotrigger_enabled()
        return True

    def _trigger_automation_entry(self, entry):
        if not self._automation_entry_effective_enabled(entry):
            self._update_status(translate('OpenLP.AutoplayerManager', 'Automation skipped: cue is disabled.'))
            return
        companion_manager = self._get_companion_manager()
        if companion_manager is None or not hasattr(companion_manager, '_send_button_action'):
            self._update_status(translate('OpenLP.AutoplayerManager', 'Automation skipped: Companion panel unavailable.'))
            return
        companion_id = str(entry.get('companion_id', '') or '')
        button_id = str(entry.get('button_id', '') or '')
        action = str(entry.get('action', 'PRESS') or 'PRESS')
        companion = next((c for c in companion_manager.companions if str(c.get('id', '')) == companion_id), None)
        if not companion:
            self._update_status(translate('OpenLP.AutoplayerManager', 'Automation skipped: Companion missing.'))
            return
        button = next((b for b in companion.get('buttons', []) if str(b.get('id', '')) == button_id), None)
        if not button:
            self._update_status(translate('OpenLP.AutoplayerManager', 'Automation skipped: Button missing.'))
            return
        companion_manager._send_button_action(companion, button, action, source='auto')
        self._update_status(translate('OpenLP.AutoplayerManager', 'Automation triggered: {name}').format(
            name=str(button.get('name', ''))))

    def _highlight_active_row(self):
        playlist = self._current_playlist()
        if not playlist:
            return
        if self._active_playlist_index < 0 or self._active_playlist_index >= len(playlist.get('items', [])):
            return
        self.playlist_items_widget.setCurrentRow(self._active_playlist_index)

    def _advance_to_next_playlist_item(self):
        playlist = self._current_playlist()
        if not playlist:
            self._stop_playback_runtime()
            return
        items = playlist.get('items', [])
        if not items:
            self._stop_playback_runtime()
            return
        if self._stop_after_current:
            self._stop_playback_runtime()
            self._update_status(translate('OpenLP.AutoplayerManager', 'Stopped after current item.'))
            return
        next_index = self._active_playlist_index + 1
        if next_index >= len(items):
            if not self.loop_enabled:
                self._stop_playback_runtime()
                self._update_status(translate('OpenLP.AutoplayerManager', 'Playlist finished.'))
                return
            next_index = 0
        self._active_playlist_index = next_index
        self._active_item_id = ''
        self._start_current_playlist_item()

    def _media_state(self):
        results = self._safe_registry_execute('media_state')
        if results:
            return results[0]
        return MediaState.Off

    def _on_tick(self):
        current_autotrigger_state = self._is_companion_autotrigger_enabled()
        if self._last_autotrigger_enabled_state is None:
            self._last_autotrigger_enabled_state = current_autotrigger_state
        elif self._last_autotrigger_enabled_state != current_autotrigger_state:
            self._last_autotrigger_enabled_state = current_autotrigger_state
            self._refresh_playlist_items()
        if not self._is_playing or self._is_paused:
            return
        if self._active_entry_type == 'pause':
            now_msecs = QtCore.QDateTime.currentMSecsSinceEpoch()
            remaining_msecs = max(0, self._slide_due_msecs - now_msecs)
            remaining_seconds = int(math.ceil(remaining_msecs / 1000.0))
            self._update_status(translate('OpenLP.AutoplayerManager', 'Pause cue: {seconds} second(s) remaining').format(
                seconds=remaining_seconds))
            if now_msecs >= self._slide_due_msecs:
                self._advance_to_next_playlist_item()
            return
        if self._active_entry_type == 'pause_manual':
            return
        if not self._active_item_id:
            self._start_current_playlist_item()
            return
        if self._active_item_is_media:
            media_state = self._media_state()
            if media_state == MediaState.Playing or self._is_live_media_backend_playing():
                self._media_has_started = True
                return
            # LRC audio can report media_state as Off while the audio backend is still playing.
            if self._active_item_plugin_name == 'lrcplayer':
                if self._is_live_audio_playing():
                    self._media_has_started = True
                    return
                if self._media_has_started:
                    self._advance_to_next_playlist_item()
                return
            if media_state in (MediaState.Stopped, MediaState.Off):
                # Advance only after media has actually started once, then ended.
                if self._media_has_started:
                    self._advance_to_next_playlist_item()
            return

        if not self.live_controller:
            self._hook_live_controller()
            return
        now_msecs = QtCore.QDateTime.currentMSecsSinceEpoch()
        if now_msecs < self._slide_due_msecs:
            return
        slide_count = self.live_controller.preview_widget.slide_count() if self.live_controller.preview_widget else 0
        current_row = self.live_controller.preview_widget.current_slide_number() if self.live_controller.preview_widget \
            else 0
        if slide_count <= 1 or current_row >= slide_count - 1:
            self._advance_to_next_playlist_item()
            return
        self.live_controller.on_slide_selected_next(False)
        self._slide_remaining_msecs = self.auto_advance_seconds * 1000
        self._slide_due_msecs = now_msecs + self._slide_remaining_msecs

    def on_service_manager_changed(self):
        if self._service_sync_in_progress:
            return
        self._sync_playlist_refs_with_service_reorder()
        self._refresh_playlist_items()
        results = Registry().execute('service_get_autoplayer_config')
        config = results[0] if results else None
        signature = self._config_signature(config if isinstance(config, dict) else {})
        if signature != self._last_service_config_signature:
            self._load_config()
            self._refresh_playlist_list()
            self._refresh_playlist_items()
        if self._is_playing and self._active_item_id and not self._service_item_by_id(self._active_item_id):
            self._active_item_id = ''
            self._advance_to_next_playlist_item()
        self._update_transport_state()

    def _normalise_playlist_item_entry(self, entry):
        if not isinstance(entry, dict):
            return None
        entry_type = self._entry_type(entry)
        if entry_type == 'pause':
            return {
                'uid': str(entry.get('uid', '') or str(uuid.uuid4())),
                'type': 'pause',
                'seconds': int(entry.get('seconds', 1) or 1)
            }
        if entry_type == 'pause_manual':
            return {
                'uid': str(entry.get('uid', '') or str(uuid.uuid4())),
                'type': 'pause_manual'
            }
        if entry_type == 'automation':
            return {
                'uid': str(entry.get('uid', '') or str(uuid.uuid4())),
                'type': 'automation',
                'companion_id': str(entry.get('companion_id', '') or ''),
                'button_id': str(entry.get('button_id', '') or ''),
                'action': str(entry.get('action', 'PRESS') or 'PRESS'),
                'label': str(entry.get('label', '') or ''),
                'follow_autotrigger': bool(entry.get('follow_autotrigger', True)),
                'enabled': bool(entry.get('enabled', True))
            }
        item_ref = self._entry_item_ref(entry)
        item_id = self._entry_item_id(entry)
        if not item_ref and not item_id:
            return None
        return {'uid': str(entry.get('uid', '') or str(uuid.uuid4())),
                'type': 'service',
                'item_ref': item_ref,
                'item_id': item_id}

    def _refresh_refs_from_current_service(self):
        changed = False
        if not self.service_manager:
            return changed
        for playlist in self.playlists:
            for entry in playlist.get('items', []):
                if self._entry_type(entry) != 'service':
                    continue
                service_item = self._service_item_from_ref_or_id(self._entry_item_ref(entry), self._entry_item_id(entry))
                if not service_item:
                    continue
                resolved_ref = self._resolve_item_ref(service_item)
                resolved_id = str(getattr(service_item, 'unique_identifier', '') or '')
                if resolved_ref and entry.get('item_ref') != resolved_ref:
                    entry['item_ref'] = resolved_ref
                    changed = True
                if resolved_id and entry.get('item_id') != resolved_id:
                    entry['item_id'] = resolved_id
                    changed = True
        return changed
