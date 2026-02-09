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
Media item implementation for the LRC Player plugin.
"""
from bisect import bisect_right
import logging
from pathlib import Path
import re
from typing import Any

from PySide6 import QtCore, QtWidgets
from sqlalchemy.sql import func, or_

from openlp.core.common import sha256_file_hash
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.registry import Registry
from openlp.core.lib import ServiceItemContext, check_item_selected
from openlp.core.lib.mediamanageritem import MediaManagerItem
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.core.lib.ui import create_widget_action, critical_error_message_box
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.plugins.lrcplayer.forms.lrcentryform import LrcEntryForm
from openlp.plugins.lrcplayer.lib.db import LrcSong


log = logging.getLogger(__name__)
LRC_TAG_RE = re.compile(r'\[(\d{1,3}):(\d{2})(?:[.:](\d{1,3}))?\]')
OFFSET_RE = re.compile(r'^\[offset:([+-]?\d+)\]\s*$', re.IGNORECASE)


class LrcPlayerMediaItem(MediaManagerItem):
    """
    Media manager item for LRC synced songs.
    """
    lrcplayer_go_live = QtCore.Signal(list)
    lrcplayer_add_to_service = QtCore.Signal(list)
    log.info('LrcPlayer Media Item loaded')

    def __init__(self, parent, plugin):
        self.icon_path = 'songs/song'
        super().__init__(parent, plugin)

    def setup_item(self):
        self.lrcplayer_go_live.connect(self.go_live_remote)
        self.lrcplayer_add_to_service.connect(self.add_to_service_remote)
        self.single_service_item = False
        self.quick_preview_allowed = True
        self.has_search = True
        self.is_search_as_you_type_enabled = True

        self.entry_form = LrcEntryForm(self.main_window)
        self.sync_timer = QtCore.QTimer(self)
        self.sync_timer.setInterval(120)
        self.sync_timer.timeout.connect(self.on_sync_timer)

        self.active_live_item_id = None
        self.active_live_slide_index = -1
        self.active_live_timestamps = []
        self.lrc_timestamps_by_id = {}
        self.lrc_timestamps_by_title = {}
        self.last_generated_timestamps = []
        self.last_generated_title = ''
        self._debug_last_second = -1
        self._suppress_live_seek = False
        self._lrc_was_live = False

        Registry().register_function('slidecontroller_live_started', self.on_live_item_started)
        Registry().register_function('slidecontroller_slide_selected', self.on_slide_selected)

    def add_end_header_bar(self):
        self.toolbar.addSeparator()
        self.add_search_to_toolbar()

    def retranslate_ui(self):
        self.search_text_label.setText('{text}:'.format(text=UiStrings().Search))
        self.search_text_button.setText(UiStrings().Search)

    def initialise(self):
        self.load_list()

    def load_list(self, search_text=''):
        self.save_auto_select_id()
        self.list_view.clear()
        search_text = search_text.strip().lower()
        if search_text:
            songs = self.plugin.db_manager.get_all_objects(
                LrcSong,
                or_(
                    func.lower(LrcSong.title).like(f'%{search_text}%'),
                    func.lower(LrcSong.audio_path).like(f'%{search_text}%'),
                    func.lower(LrcSong.lrc_path).like(f'%{search_text}%')
                ),
                order_by_ref=LrcSong.title
            )
        else:
            songs = self.plugin.db_manager.get_all_objects(LrcSong, order_by_ref=LrcSong.title)
        songs.sort()
        for song in songs:
            line = f'{song.title} ({Path(song.audio_path).name})'
            item = QtWidgets.QListWidgetItem(line)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, song.id)
            item.setIcon(UiIcons().audio)
            self.list_view.addItem(item)
            if song.id == self.auto_select_id:
                self.list_view.setCurrentItem(item)
        self.auto_select_id = -1

    def add_custom_context_actions(self):
        create_widget_action(self.list_view, separator=True)
        create_widget_action(
            self.list_view,
            text=translate('LrcPlayerPlugin.MediaItem', '&Clone'),
            icon=UiIcons().clone,
            triggers=self.on_clone_click
        )

    def on_new_click(self):
        self.entry_form.setWindowTitle(translate('LrcPlayerPlugin.MediaItem', 'Add LRC Song'))
        self.entry_form.load_values('', '', '')
        if self.entry_form.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            values = self.entry_form.values()
            song = LrcSong(title=values['title'], audio_path=values['audio_path'], lrc_path=values['lrc_path'])
            self.plugin.db_manager.save_object(song)
            self.auto_select_id = song.id
            self.load_list()
            self.on_selection_change()

    def on_edit_click(self):
        if not check_item_selected(self.list_view, UiStrings().SelectEdit):
            return
        item_id = self.list_view.currentItem().data(QtCore.Qt.ItemDataRole.UserRole)
        song = self.plugin.db_manager.get_object(LrcSong, item_id)
        if not song:
            return
        self.entry_form.setWindowTitle(translate('LrcPlayerPlugin.MediaItem', 'Edit LRC Song'))
        self.entry_form.load_values(song.title, song.audio_path, song.lrc_path)
        if self.entry_form.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            values = self.entry_form.values()
            song.title = values['title']
            song.audio_path = values['audio_path']
            song.lrc_path = values['lrc_path']
            self.plugin.db_manager.save_object(song)
            self.lrc_timestamps_by_id.pop(song.id, None)
            self.auto_select_id = song.id
            self.load_list()

    def on_delete_click(self):
        if not check_item_selected(self.list_view, UiStrings().SelectDelete):
            return
        items = self.list_view.selectedItems()
        if QtWidgets.QMessageBox.question(
                self,
                UiStrings().ConfirmDelete,
                translate('LrcPlayerPlugin.MediaItem',
                          'Are you sure you want to delete the "{items:d}" selected LRC song(s)?')
                .format(items=len(items)),
                defaultButton=QtWidgets.QMessageBox.StandardButton.Yes) == QtWidgets.QMessageBox.StandardButton.No:
            return
        for selected in items:
            item_id = selected.data(QtCore.Qt.ItemDataRole.UserRole)
            self.plugin.db_manager.delete_object(LrcSong, item_id)
            if item_id in self.lrc_timestamps_by_id:
                del self.lrc_timestamps_by_id[item_id]
            if self.active_live_item_id == item_id:
                self.stop_sync()
        self.load_list()

    def on_clone_click(self):
        if not check_item_selected(self.list_view, UiStrings().SelectEdit):
            return
        item_id = self.list_view.currentItem().data(QtCore.Qt.ItemDataRole.UserRole)
        song = self.plugin.db_manager.get_object(LrcSong, item_id)
        if not song:
            return
        copy_song = LrcSong(
            title='{title} <{text}>'.format(
                title=song.title,
                text=translate('LrcPlayerPlugin.MediaItem', 'copy', 'For item cloning')
            ),
            audio_path=song.audio_path,
            lrc_path=song.lrc_path
        )
        self.plugin.db_manager.save_object(copy_song)
        self.auto_select_id = copy_song.id
        self.load_list()

    def on_search_text_button_clicked(self):
        self.load_list(self.search_text_edit.displayText())

    def on_search_text_edit_changed(self, text):
        if self.is_search_as_you_type_enabled:
            if len(text) > 1:
                self.on_search_text_button_clicked()
            elif not text:
                self.on_clear_text_button_click()

    def on_clear_text_button_click(self):
        self.search_text_edit.clear()
        self.load_list()

    def generate_slide_data(self, service_item, *, item=None, context=ServiceItemContext.Service, **kwargs):
        item_id = self._get_id_of_item_to_generate(item, -1)
        song = self.plugin.db_manager.get_object(LrcSong, item_id)
        if not song:
            return False

        audio_path = Path(song.audio_path)
        lrc_path = Path(song.lrc_path)

        if not audio_path.exists():
            critical_error_message_box(
                translate('LrcPlayerPlugin.MediaItem', 'Missing Audio File'),
                translate('LrcPlayerPlugin.MediaItem', 'The file {name} no longer exists.').format(name=str(audio_path))
            )
            return False
        if not lrc_path.exists():
            critical_error_message_box(
                translate('LrcPlayerPlugin.MediaItem', 'Missing LRC File'),
                translate('LrcPlayerPlugin.MediaItem', 'The file {name} no longer exists.').format(name=str(lrc_path))
            )
            return False

        parsed_lines = self.parse_lrc(lrc_path)
        if not parsed_lines:
            critical_error_message_box(
                translate('LrcPlayerPlugin.MediaItem', 'Invalid LRC File'),
                translate('LrcPlayerPlugin.MediaItem',
                          'No timed lyric lines were found in {name}.').format(name=str(lrc_path))
            )
            return False

        service_item.title = song.title
        service_item.edit_id = item_id

        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanSoftBreak)
        service_item.add_capability(ItemCapabilities.OnLoadUpdate)
        service_item.add_capability(ItemCapabilities.CanEditTitle)

        timestamps = []
        for idx, (time_ms, lyric_line) in enumerate(parsed_lines):
            line_text = lyric_line if lyric_line else ' '
            service_item.add_from_text(line_text, str(idx + 1), metadata={'time_ms': time_ms})
            timestamps.append(time_ms)

        self.lrc_timestamps_by_id[item_id] = timestamps
        title_key = song.title.strip().lower()
        self.lrc_timestamps_by_title[title_key] = timestamps
        self.last_generated_timestamps = timestamps
        self.last_generated_title = title_key

        if State().check_preconditions('media'):
            service_item.add_capability(ItemCapabilities.HasBackgroundAudio)
            service_item.background_audio = [(audio_path, sha256_file_hash(audio_path))]
            service_item.set_media_length(self.media_controller.media_length(audio_path))
            service_item.will_auto_start = True
        return True

    def on_live_item_started(self, service_item=None):
        if isinstance(service_item, (list, tuple)):
            service_item = service_item[0] if service_item else None
        service_name = getattr(service_item, 'name', None) if service_item is not None else None
        if service_name != self.plugin.name:
            if self._lrc_was_live and hasattr(self.live_controller, 'audio_player'):
                self.live_controller.audio_player.stop()
            self._lrc_was_live = False
            self.stop_sync()
            return
        item_id = getattr(service_item, 'edit_id', None) if service_item is not None else None
        service_title = getattr(service_item, 'title', '') if service_item is not None else ''
        slide_count = len(getattr(service_item, 'slides', []) or []) if service_item is not None else 0
        metadata_count = sum(1 for slide in getattr(service_item, 'slides', [])
                             if isinstance(slide.get('metadata', {}), dict) and 'time_ms' in slide.get('metadata', {})) \
            if service_item is not None else 0
        timestamps = []
        if item_id is not None and item_id not in self.lrc_timestamps_by_id:
            song = self.plugin.db_manager.get_object(LrcSong, item_id)
            if song and Path(song.lrc_path).exists():
                parsed_lines = self.parse_lrc(Path(song.lrc_path))
                if parsed_lines:
                    parsed_timestamps = [time_ms for (time_ms, _) in parsed_lines]
                    self.lrc_timestamps_by_id[item_id] = parsed_timestamps
                    self.lrc_timestamps_by_title[song.title.strip().lower()] = parsed_timestamps
        if item_id in self.lrc_timestamps_by_id:
            timestamps = self.lrc_timestamps_by_id[item_id]
        elif service_title.strip().lower() in self.lrc_timestamps_by_title:
            timestamps = self.lrc_timestamps_by_title[service_title.strip().lower()]
        elif service_item is not None:
            for slide in getattr(service_item, 'slides', []):
                metadata = slide.get('metadata', {})
                if isinstance(metadata, dict) and 'time_ms' in metadata:
                    try:
                        timestamps.append(max(0, int(metadata['time_ms'])))
                    except (TypeError, ValueError):
                        continue
        if not timestamps and service_title:
            songs = self.plugin.db_manager.get_all_objects(
                LrcSong, func.lower(LrcSong.title) == service_title.lower(), order_by_ref=LrcSong.id
            )
            if songs:
                song = songs[0]
                lrc_path = Path(song.lrc_path)
                if lrc_path.exists():
                    parsed_lines = self.parse_lrc(lrc_path)
                    timestamps = [time_ms for (time_ms, _) in parsed_lines]
                    self.lrc_timestamps_by_title[song.title.strip().lower()] = timestamps
        if not timestamps and self.last_generated_timestamps:
            title_key = service_title.strip().lower()
            if not title_key or title_key == self.last_generated_title:
                timestamps = self.last_generated_timestamps
        if timestamps:
            self.active_live_item_id = item_id if item_id is not None else -1
            self.active_live_slide_index = -1
            self.active_live_timestamps = timestamps
            self._lrc_was_live = True
            self._debug_last_second = -1
            if hasattr(self.live_controller, 'audio_player'):
                self.live_controller.audio_player._lrc_timestamps = list(timestamps)
                self.live_controller.audio_player._lrc_current_index = -1
            self.sync_timer.start()
            self.on_sync_timer()
        else:
            self.stop_sync()

    def stop_sync(self):
        self.sync_timer.stop()
        self.active_live_item_id = None
        self.active_live_slide_index = -1
        self.active_live_timestamps = []

    def on_sync_timer(self):
        if not self.active_live_timestamps:
            return
        media_play_item = getattr(self.live_controller, 'media_play_item', None)
        if not media_play_item:
            return
        timestamps = self.active_live_timestamps
        if not timestamps:
            self.stop_sync()
            return

        if getattr(media_play_item, 'audio_file', None):
            media_time_ms = max(0, int(self.live_controller.audio_player.get_time()))
        else:
            media_time_ms = max(0, int(media_play_item.timer))
        self._debug_last_second = media_time_ms // 1000
        target_slide = bisect_right(timestamps, media_time_ms) - 1
        if target_slide < 0:
            target_slide = 0
        if target_slide != self.active_live_slide_index:
            self._suppress_live_seek = True
            self.live_controller.on_slide_selected_index([target_slide])
            self._suppress_live_seek = False
            self.active_live_slide_index = target_slide

    def on_slide_selected(self, message):
        """
        Seek live audio when the operator manually selects a lyric line.
        """
        if self._suppress_live_seek or not message or len(message) < 3:
            return
        service_item = message[0]
        is_live = bool(message[1])
        row = int(message[2])
        if not is_live or service_item is None or getattr(service_item, 'name', None) != self.plugin.name:
            return
        if row < 0:
            return

        timestamps = self.active_live_timestamps
        if not timestamps:
            title_key = getattr(service_item, 'title', '').strip().lower()
            if title_key in self.lrc_timestamps_by_title:
                timestamps = self.lrc_timestamps_by_title[title_key]
            else:
                timestamps = []
                for slide in getattr(service_item, 'slides', []):
                    metadata = slide.get('metadata', {})
                    if isinstance(metadata, dict) and 'time_ms' in metadata:
                        try:
                            timestamps.append(max(0, int(metadata['time_ms'])))
                        except (TypeError, ValueError):
                            continue
        if row >= len(timestamps):
            return

        target_ms = int(timestamps[row])
        current_ms = int(self.live_controller.audio_player.get_time())
        if abs(current_ms - target_ms) <= 800:
            return
        self.media_controller.media_seek(self.live_controller, target_ms)
        self.active_live_slide_index = row

    @staticmethod
    def parse_lrc(path):
        """
        Parse a .lrc file and return [(time_ms, lyric_text), ...] sorted by time.
        """
        try:
            raw_data = path.read_bytes()
        except OSError:
            log.exception('Failed to read LRC file: %s', path)
            return []
        text = None
        for encoding in ('utf-8-sig', 'gb18030', 'gbk'):
            try:
                text = raw_data.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            text = raw_data.decode('utf-8-sig', errors='replace')
        lines = text.splitlines()

        offset_ms = 0
        parsed = []

        for line in lines:
            offset_match = OFFSET_RE.match(line.strip())
            if offset_match:
                try:
                    offset_ms = int(offset_match.group(1))
                except ValueError:
                    offset_ms = 0
                continue

            tags = list(LRC_TAG_RE.finditer(line))
            if not tags:
                continue

            text = LRC_TAG_RE.sub('', line).strip()

            for match in tags:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                fraction = match.group(3) or '0'
                if len(fraction) == 1:
                    ms_fraction = int(fraction) * 100
                elif len(fraction) == 2:
                    ms_fraction = int(fraction) * 10
                else:
                    ms_fraction = int(fraction[:3])
                total_ms = (minutes * 60 * 1000) + (seconds * 1000) + ms_fraction + offset_ms
                parsed.append((max(0, total_ms), text))

        parsed.sort(key=lambda row: row[0])
        # Always start with a silent/blank line at 0:00 so lyrics begin from an empty slide.
        parsed.insert(0, (0, ''))
        return parsed

    @QtCore.Slot(str, bool, result=list)
    def search(self, string: str, show_error: bool = True) -> list[list[Any]]:
        search = '%{search}%'.format(search=string.lower())
        results = self.plugin.db_manager.get_all_objects(
            LrcSong,
            or_(
                func.lower(LrcSong.title).like(search),
                func.lower(LrcSong.audio_path).like(search),
                func.lower(LrcSong.lrc_path).like(search)
            ),
            order_by_ref=LrcSong.title
        )
        return [[song.id, song.title] for song in results]
