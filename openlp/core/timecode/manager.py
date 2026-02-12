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
:mod:`openlp.core.timecode.manager` module

Provides the dock widget for SMPTE/LTC timecode output.
"""
import logging
from datetime import datetime
from math import floor
from threading import Event, Lock, Thread
from time import perf_counter, sleep

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QIODevice
from PySide6.QtMultimedia import QAudioFormat, QAudioSink, QMediaDevices

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.timecode.midi import MIDI_OUTPUT_DEVICE_NONE, WinMMMidiOut, get_midi_output_devices
from openlp.core.ui.media import (
    AUDIO_OUTPUT_DEVICE_DEFAULT,
    AUDIO_OUTPUT_DEVICE_FOLLOW_PLAYBACK,
    AUDIO_OUTPUT_DEVICE_NONE,
    MediaState,
    MediaType,
    get_audio_output_device_by_id
)

TIMECODE_MODE_ZERO = 'zero'
TIMECODE_MODE_FOLLOW = 'follow_media'
TIMECODE_MODE_SYSTEM = 'system_time'
TIMECODE_MODE_FOLLOW_FREEZE = 'follow_media_freeze'

_TIMECODE_MODES = [TIMECODE_MODE_ZERO, TIMECODE_MODE_FOLLOW, TIMECODE_MODE_SYSTEM, TIMECODE_MODE_FOLLOW_FREEZE]
MTC_IDLE_KEEP_STREAM = 'keep_stream'
MTC_IDLE_ALLOW_DARK = 'allow_dark'

log = logging.getLogger(__name__)


def frame_to_timecode_parts(frame_number: int, fps: int) -> tuple[int, int, int, int]:
    """
    Convert absolute frame number to (hours, minutes, seconds, frames).
    """
    if fps <= 0:
        fps = 30
    frame_number = max(0, int(frame_number))
    total_frames_day = 24 * 60 * 60 * fps
    frame_number %= total_frames_day
    frames = frame_number % fps
    total_seconds = frame_number // fps
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = (total_minutes // 60) % 24
    return hours, minutes, seconds, frames


def frame_to_timecode_string(frame_number: int, fps: int) -> str:
    """
    Format frame number into SMPTE-like text: HH:MM:SS:FF.
    """
    hours, minutes, seconds, frames = frame_to_timecode_parts(frame_number, fps)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}'


def _set_bcd(bits: list[int], offset: int, value: int, width: int) -> None:
    for index in range(width):
        bits[offset + index] = (value >> index) & 0x1


def encode_ltc_bits(frame_number: int, fps: int) -> list[int]:
    """
    Encode one LTC frame to 80 bits (LSB first in each field).
    """
    bits = [0] * 80
    hours, minutes, seconds, frames = frame_to_timecode_parts(frame_number, fps)
    _set_bcd(bits, 0, frames % 10, 4)
    _set_bcd(bits, 8, frames // 10, 2)
    _set_bcd(bits, 16, seconds % 10, 4)
    _set_bcd(bits, 24, seconds // 10, 3)
    _set_bcd(bits, 32, minutes % 10, 4)
    _set_bcd(bits, 40, minutes // 10, 3)
    _set_bcd(bits, 48, hours % 10, 4)
    _set_bcd(bits, 56, hours // 10, 2)
    # We write bits LSB-first, so use 0xBFFC to produce the canonical sync
    # bit pattern (0011111111111101) expected by LTC decoders.
    sync_word = 0xBFFC
    for index in range(16):
        bits[64 + index] = (sync_word >> index) & 0x1
    return bits


class LtcWaveDevice(QIODevice):
    """
    QIODevice that generates continuous LTC waveform.
    """
    def __init__(self, frame_provider, speed_fps_provider, nominal_fps_provider,
                 sample_rate=48000, sample_format='int16', amplitude=9000, parent=None):
        super().__init__(parent)
        self.frame_provider = frame_provider
        self.speed_fps_provider = speed_fps_provider
        self.nominal_fps_provider = nominal_fps_provider
        self.sample_rate = sample_rate
        self.sample_format = sample_format
        self.amplitude = amplitude
        if sample_format == 'uint8':
            self._bytes_per_sample = 1
        elif sample_format == 'int32':
            self._bytes_per_sample = 4
        else:
            self._bytes_per_sample = 2
        self._current_bits = encode_ltc_bits(0, int(max(1, nominal_fps_provider())))
        self._bit_index = 0
        self._sample_in_bit = 0
        self._signal = 1
        self._cached_speed_fps = 30.0
        self._cached_nominal_fps = int(max(1, nominal_fps_provider()))
        self._samples_per_half_bit = max(1, int(sample_rate / (30.0 * 160)))
        self._samples_per_bit = self._samples_per_half_bit * 2
        self._frame_boundary_requested = True

    def _update_timing(self):
        fps = float(self.speed_fps_provider())
        if fps <= 0:
            fps = 30.0
        if abs(fps - self._cached_speed_fps) > 0.0001:
            self._cached_speed_fps = fps
            self._samples_per_half_bit = max(1, int(self.sample_rate / (fps * 160)))
            self._samples_per_bit = self._samples_per_half_bit * 2
        nominal = int(max(1, self.nominal_fps_provider()))
        if nominal != self._cached_nominal_fps:
            self._cached_nominal_fps = nominal

    def readData(self, maxlen):
        self._update_timing()
        sample_count = maxlen // self._bytes_per_sample
        chunk = bytearray()
        for _ in range(sample_count):
            if self._frame_boundary_requested:
                self._current_bits = encode_ltc_bits(int(self.frame_provider()), self._cached_nominal_fps)
                self._frame_boundary_requested = False
            bit_value = self._current_bits[self._bit_index]
            if self._sample_in_bit == 0:
                self._signal *= -1
            if bit_value and self._sample_in_bit == self._samples_per_half_bit:
                self._signal *= -1
            sample_value = self.amplitude if self._signal > 0 else -self.amplitude
            if self.sample_format == 'uint8':
                unsigned_value = 128 + int(self.amplitude if self._signal > 0 else -self.amplitude)
                unsigned_value = max(0, min(255, unsigned_value))
                chunk.append(unsigned_value)
            elif self.sample_format == 'int16':
                chunk.extend(int(sample_value).to_bytes(2, byteorder='little', signed=True))
            else:
                chunk.extend(int(sample_value).to_bytes(4, byteorder='little', signed=True))
            self._sample_in_bit += 1
            if self._sample_in_bit >= self._samples_per_bit:
                self._sample_in_bit = 0
                self._bit_index += 1
                if self._bit_index >= 80:
                    self._bit_index = 0
                    self._frame_boundary_requested = True
        return bytes(chunk)

    def writeData(self, _data):
        return 0

    def bytesAvailable(self):
        return 8192


class LtcAudioOutput:
    """
    Lightweight wrapper around QAudioSink for LTC playback.
    """
    def __init__(self, frame_provider, speed_fps_provider, nominal_fps_provider,
                 sample_rate_provider, bit_depth_provider, parent=None):
        self.parent = parent
        self.frame_provider = frame_provider
        self.speed_fps_provider = speed_fps_provider
        self.nominal_fps_provider = nominal_fps_provider
        self.sample_rate_provider = sample_rate_provider
        self.bit_depth_provider = bit_depth_provider
        self.wave_device = None
        self.audio_sink = None
        self._device_key = None
        self._is_active = False

    def _create_format(self):
        audio_format = QAudioFormat()
        sample_rate = int(self.sample_rate_provider())
        if sample_rate <= 0:
            sample_rate = 48000
        audio_format.setSampleRate(sample_rate)
        audio_format.setChannelCount(1)
        bit_depth = int(self.bit_depth_provider())
        if bit_depth == 8:
            audio_format.setSampleFormat(QAudioFormat.SampleFormat.UInt8)
        elif bit_depth == 32:
            audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int32)
        else:
            audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        return audio_format

    def stop(self):
        if self.audio_sink:
            self.audio_sink.stop()
            self.audio_sink.deleteLater()
            self.audio_sink = None
        if self.wave_device:
            self.wave_device.close()
            self.wave_device.deleteLater()
            self.wave_device = None
        self._is_active = False
        self._device_key = None

    def start(self, audio_device, device_key):
        if self._is_active and self._device_key == device_key:
            return
        self.stop()
        if audio_device is None:
            return
        bit_depth = int(self.bit_depth_provider())
        sample_format = 'uint8' if bit_depth == 8 else ('int32' if bit_depth == 32 else 'int16')
        sample_rate = int(self.sample_rate_provider())
        if sample_format == 'uint8':
            amplitude = 60
        elif sample_format == 'int32':
            amplitude = 500000000
        else:
            amplitude = 9000
        self.wave_device = LtcWaveDevice(
            self.frame_provider,
            self.speed_fps_provider,
            self.nominal_fps_provider,
            sample_rate=sample_rate,
            sample_format=sample_format,
            amplitude=amplitude,
            parent=self.parent
        )
        self.audio_sink = QAudioSink(audio_device, self._create_format(), self.parent)
        self.wave_device.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Unbuffered)
        self.audio_sink.start(self.wave_device)
        self._is_active = True
        self._device_key = device_key


class TimecodeClock:
    """
    Dedicated timing clock for timecode generation.
    """
    def __init__(self, ltc_fps_provider, mtc_fps_provider, mtc_sender=None, resync_callback=None):
        self._ltc_fps_provider = ltc_fps_provider
        self._mtc_fps_provider = mtc_fps_provider
        self._mtc_sender = mtc_sender
        self._resync_callback = resync_callback
        self._lock = Lock()
        self._stop_event = Event()
        self._thread = None
        self._mode = TIMECODE_MODE_ZERO
        self._frame = 0.0
        self._follow_anchor_media_ms = 0.0
        self._follow_anchor_t = perf_counter()
        self._follow_last_media_ms = 0.0
        self._follow_playing = False
        self._frozen_frame = 0.0
        self._last_tick = perf_counter()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run, name='TimecodeClock', daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _fps(self) -> float:
        fps = float(self._ltc_fps_provider())
        return fps if fps > 0 else 30.0

    def _run(self):
        self._last_tick = perf_counter()
        while not self._stop_event.is_set():
            now = perf_counter()
            self._last_tick = now
            with self._lock:
                fps = self._fps()
                if self._mode == TIMECODE_MODE_ZERO:
                    self._frame = 0.0
                elif self._mode == TIMECODE_MODE_SYSTEM:
                    wall = datetime.now()
                    seconds_since_midnight = ((wall.hour * 3600) + (wall.minute * 60) + wall.second +
                                              (wall.microsecond / 1_000_000))
                    self._frame = seconds_since_midnight * fps
                elif self._mode == TIMECODE_MODE_FOLLOW_FREEZE:
                    self._frame = self._frozen_frame
            current_frame = self.frame_for_output()
            current_fps = float(self._fps())
            if self._mtc_sender:
                self._mtc_sender.update(current_frame, current_fps, float(self._mtc_fps_provider()))
            sleep(0.002)

    def set_mode(self, mode: str):
        with self._lock:
            if mode == TIMECODE_MODE_FOLLOW_FREEZE and self._mode == TIMECODE_MODE_FOLLOW:
                if self._follow_playing:
                    media_ms = self._follow_anchor_media_ms + max(0.0, (perf_counter() - self._follow_anchor_t) * 1000.0)
                else:
                    media_ms = self._follow_anchor_media_ms
                self._frozen_frame = max(0.0, (media_ms / 1000.0) * self._fps())
            self._mode = mode
            if mode == TIMECODE_MODE_FOLLOW_FREEZE and self._frozen_frame <= 0.0:
                self._frozen_frame = self._frame

    def update_follow(self, media_ms: float, is_playing: bool, valid_media: bool):
        fps = self._fps()
        now = perf_counter()
        resync_event = None
        with self._lock:
            if not valid_media:
                self._frame = 0.0
                self._follow_anchor_media_ms = 0.0
                self._follow_anchor_t = now
                self._follow_last_media_ms = 0.0
                self._follow_playing = False
                return
            target_frame = max(0.0, (media_ms / 1000.0) * fps)
            if not is_playing:
                self._frame = target_frame
                self._follow_anchor_media_ms = media_ms
                self._follow_anchor_t = now
                self._follow_last_media_ms = media_ms
                self._follow_playing = False
                return
            if not self._follow_playing:
                self._frame = target_frame
                self._follow_anchor_media_ms = media_ms
                self._follow_anchor_t = now
                self._follow_last_media_ms = media_ms
                self._follow_playing = True
                resync_event = ('start', 0.0, media_ms, media_ms)
            else:
                predicted_ms = self._follow_anchor_media_ms + max(0.0, (now - self._follow_anchor_t) * 1000.0)
                drift_ms = media_ms - predicted_ms
                rewind = media_ms + 40.0 < self._follow_last_media_ms
                if abs(drift_ms) > 80.0 or rewind:
                    self._follow_anchor_media_ms = media_ms
                    self._follow_anchor_t = now
                    resync_event = ('seek/reanchor' if rewind else 'drift', drift_ms, media_ms, predicted_ms)
                else:
                    # Keep media as master, but gently absorb tiny timer noise.
                    self._follow_anchor_media_ms = media_ms - (drift_ms * 0.12)
                    self._follow_anchor_t = now
                self._follow_last_media_ms = media_ms
        if resync_event and self._resync_callback:
            self._resync_callback(*resync_event)

    def frame_for_output(self) -> int:
        with self._lock:
            if self._mode == TIMECODE_MODE_FOLLOW:
                if self._follow_playing:
                    media_ms = self._follow_anchor_media_ms + max(0.0, (perf_counter() - self._follow_anchor_t) * 1000.0)
                else:
                    media_ms = self._follow_anchor_media_ms
                fps = self._fps()
                return max(0, int(floor((media_ms / 1000.0) * fps)))
            return max(0, int(floor(self._frame)))


class TimecodeManager(QtWidgets.QWidget, RegistryProperties):
    """
    Manage timecode mode selection and LTC output.
    """
    def __init__(self, parent=None):
        widget_parent = parent if isinstance(parent, QtWidgets.QWidget) else None
        super().__init__(widget_parent)
        self._mode = TIMECODE_MODE_ZERO
        self._current_frame = 0
        self._current_device_signature = ''
        self._mtc_sender = MtcMidiOutput(self._mtc_fps, self._mtc_idle_behavior)
        self._clock = TimecodeClock(self._ltc_fps, self._mtc_fps, self._mtc_sender, self._on_timecode_resync)
        self._clock.start()
        self._ltc_output = LtcAudioOutput(
            self._clock.frame_for_output,
            self._ltc_fps,
            self._nominal_fps,
            self._sample_rate,
            self._bit_depth,
            self
        )
        self._setup_ui()
        self._load_settings()
        self._tick_timer = QtCore.QTimer(self)
        self._tick_timer.setInterval(40)
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_timer.start()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        self.mode_group_box = QtWidgets.QGroupBox(translate('OpenLP.TimecodeManager', 'Timecode Mode'), self)
        mode_layout = QtWidgets.QVBoxLayout(self.mode_group_box)
        self.mode_combo = QtWidgets.QComboBox(self.mode_group_box)
        self.mode_combo.addItem(translate('OpenLP.TimecodeManager', 'All Zero'), TIMECODE_MODE_ZERO)
        self.mode_combo.addItem(translate('OpenLP.TimecodeManager', 'Follow Media/Audio Player'), TIMECODE_MODE_FOLLOW)
        self.mode_combo.addItem(translate('OpenLP.TimecodeManager', 'System Time'), TIMECODE_MODE_SYSTEM)
        self.mode_combo.addItem(
            translate('OpenLP.TimecodeManager', 'Pause Sync (Freeze While Playback Continues)'),
            TIMECODE_MODE_FOLLOW_FREEZE
        )
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        layout.addWidget(self.mode_group_box)

        self.current_group_box = QtWidgets.QGroupBox(translate('OpenLP.TimecodeManager', 'Current Output'), self)
        current_layout = QtWidgets.QVBoxLayout(self.current_group_box)
        self.timecode_label = QtWidgets.QLabel('00:00:00:00', self.current_group_box)
        font = self.timecode_label.font()
        font.setPointSize(max(font.pointSize() + 6, 14))
        font.setBold(True)
        font.setStyleHint(font.StyleHint.Monospace)
        self.timecode_label.setFont(font)
        self.timecode_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        current_layout.addWidget(self.timecode_label)
        self.device_label = QtWidgets.QLabel('', self.current_group_box)
        self.device_label.setWordWrap(True)
        current_layout.addWidget(self.device_label)
        layout.addWidget(self.current_group_box)
        layout.addStretch(1)

    def _ltc_fps(self) -> float:
        fps = self.settings.value('timecode/frame rate')
        if fps is None:
            fps = self.settings.value('timecode/fps')
        try:
            fps = float(fps)
        except (TypeError, ValueError):
            fps = 30.0
        if fps <= 0:
            fps = 30.0
        return fps

    def _mtc_fps(self) -> float:
        fps = self.settings.value('timecode/mtc frame rate')
        if fps is None:
            # Backward compatibility: use the legacy shared fps when unset.
            fps = self._ltc_fps()
        try:
            fps = float(fps)
        except (TypeError, ValueError):
            fps = 30.0
        if fps <= 0:
            fps = 30.0
        return fps

    def _mtc_idle_behavior(self) -> str:
        behavior = str(self.settings.value('timecode/mtc idle behavior') or MTC_IDLE_KEEP_STREAM)
        if behavior not in [MTC_IDLE_KEEP_STREAM, MTC_IDLE_ALLOW_DARK]:
            behavior = MTC_IDLE_KEEP_STREAM
        return behavior

    def _nominal_fps(self) -> int:
        fps = self._ltc_fps()
        if abs(fps - 23.976) < 0.01:
            return 24
        if abs(fps - 29.97) < 0.01:
            return 30
        if abs(fps - 59.94) < 0.01:
            return 60
        return int(round(fps))

    def _sample_rate(self) -> int:
        sample_rate = self.settings.value('timecode/sample rate')
        try:
            sample_rate = int(sample_rate)
        except (TypeError, ValueError):
            sample_rate = 48000
        if sample_rate <= 0:
            sample_rate = 48000
        return sample_rate

    def _bit_depth(self) -> int:
        bit_depth = self.settings.value('timecode/bit depth')
        try:
            bit_depth = int(bit_depth)
        except (TypeError, ValueError):
            bit_depth = 16
        if bit_depth not in [8, 16, 32]:
            bit_depth = 16
        return bit_depth

    def _load_settings(self):
        mode = str(self.settings.value('timecode/mode') or TIMECODE_MODE_ZERO)
        if mode not in _TIMECODE_MODES:
            mode = TIMECODE_MODE_ZERO
        self._mode = mode
        self._clock.set_mode(mode)
        index = self.mode_combo.findData(mode)
        if index >= 0:
            self.mode_combo.setCurrentIndex(index)
        self._apply_output_device()
        self._on_tick()

    def _on_mode_changed(self):
        new_mode = self.mode_combo.currentData()
        if new_mode not in _TIMECODE_MODES:
            new_mode = TIMECODE_MODE_ZERO
        self._mode = new_mode
        self._clock.set_mode(new_mode)
        self.settings.setValue('timecode/mode', self._mode)
        self._on_tick()

    def _update_follow_sync(self) -> None:
        """
        Feed follow-sync hints to the dedicated timecode clock.
        """
        media_controller = self.media_controller
        if not media_controller:
            self._clock.update_follow(0.0, False, False)
            return
        live_controller = getattr(media_controller, 'live_controller', None)
        if not live_controller:
            self._clock.update_follow(0.0, False, False)
            return
        media_item = getattr(live_controller, 'media_play_item', None)
        if not media_item:
            self._clock.update_follow(0.0, False, False)
            return
        media_type = getattr(media_item, 'media_type', MediaType.Unused)
        valid_media = media_type in [MediaType.Audio, MediaType.Video, MediaType.Dual]
        media_state = getattr(media_item, 'is_playing', MediaState.Off)
        timer_ms = int(getattr(media_item, 'timer', 0) or 0)
        timer_ms = float(max(0, timer_ms))
        is_playing = media_state == MediaState.Playing
        self._clock.update_follow(timer_ms, is_playing, valid_media)

    @staticmethod
    def _on_timecode_resync(reason: str, drift_ms: float, media_ms: float, predicted_ms: float) -> None:
        message = (f'[Timecode] resync: reason={reason} drift_ms={drift_ms:.1f} '
                   f'media_ms={media_ms:.1f} predicted_ms={predicted_ms:.1f}')
        print(message)
        log.info(message)

    def _selected_timecode_device(self):
        timecode_device = self.settings.value('timecode/audio output device')
        playback_device = self.settings.value('media/audio output device')
        selected = timecode_device
        if timecode_device == AUDIO_OUTPUT_DEVICE_FOLLOW_PLAYBACK:
            selected = playback_device
        if selected == AUDIO_OUTPUT_DEVICE_NONE:
            return None, 'none'
        if selected == AUDIO_OUTPUT_DEVICE_DEFAULT or not selected:
            return QMediaDevices.defaultAudioOutput(), 'default'
        audio_device = get_audio_output_device_by_id(selected)
        if audio_device is None:
            return None, 'unavailable'
        return audio_device, selected

    def _device_description(self):
        timecode_device = self.settings.value('timecode/audio output device')
        midi_device = str(self.settings.value('timecode/midi output device') or MIDI_OUTPUT_DEVICE_NONE)
        mtc_idle_text = translate('OpenLP.TimecodeManager', 'keep stream') \
            if self._mtc_idle_behavior() == MTC_IDLE_KEEP_STREAM \
            else translate('OpenLP.TimecodeManager', 'allow dark')
        format_text = (f'LTC {self._ltc_fps()} fps, MTC {self._mtc_fps()} fps '
                       f'({mtc_idle_text}), {self._sample_rate()} Hz, {self._bit_depth()}-bit')
        midi_devices = {device_id: name for device_id, name in get_midi_output_devices()}
        midi_text = translate('OpenLP.TimecodeManager', 'MIDI: Disabled')
        if midi_device != MIDI_OUTPUT_DEVICE_NONE:
            midi_name = midi_devices.get(midi_device, translate('OpenLP.TimecodeManager', 'Unavailable'))
            midi_text = translate('OpenLP.TimecodeManager', 'MIDI: {name}').format(name=midi_name)
        if timecode_device == AUDIO_OUTPUT_DEVICE_FOLLOW_PLAYBACK:
            return translate('OpenLP.TimecodeManager',
                             'Output Device: Follows playback device setting ({format}) | {midi}').format(
                format=format_text, midi=midi_text)
        if timecode_device == AUDIO_OUTPUT_DEVICE_NONE:
            return translate('OpenLP.TimecodeManager', 'Output Device: None (muted) ({format})').format(
                format=format_text) + f' | {midi_text}'
        if timecode_device == AUDIO_OUTPUT_DEVICE_DEFAULT:
            return translate('OpenLP.TimecodeManager', 'Output Device: System default ({format})').format(
                format=format_text) + f' | {midi_text}'
        audio_device = get_audio_output_device_by_id(timecode_device)
        if audio_device:
            return translate('OpenLP.TimecodeManager', 'Output Device: {device} ({format})').format(
                device=audio_device.description(), format=format_text) + f' | {midi_text}'
        return (translate('OpenLP.TimecodeManager', 'Output Device: Unavailable ({format})').format(
            format=format_text) + f' | {midi_text}')

    def _apply_output_device(self):
        timecode_device = self.settings.value('timecode/audio output device')
        midi_device = self.settings.value('timecode/midi output device')
        playback_device = self.settings.value('media/audio output device')
        signature = (f'{timecode_device}|{playback_device}|{self._sample_rate()}|'
                     f'{self._bit_depth()}|{self._ltc_fps()}|{self._mtc_fps()}|{self._mtc_idle_behavior()}|'
                     f'{self._nominal_fps()}|{midi_device}')
        if signature == self._current_device_signature:
            return
        self._current_device_signature = signature
        audio_device, device_key = self._selected_timecode_device()
        try:
            if audio_device is None:
                self._ltc_output.stop()
            else:
                self._ltc_output.start(audio_device, str(device_key))
        except Exception:
            self._ltc_output.stop()
        self._mtc_sender.set_device(midi_device)
        self.device_label.setText(self._device_description())

    def apply_audio_output_device(self):
        """
        Public hook for settings changes.
        """
        self._apply_output_device()

    def _on_tick(self):
        self._apply_output_device()
        self._update_follow_sync()
        self._current_frame = self._clock.frame_for_output()
        self.timecode_label.setText(frame_to_timecode_string(self._current_frame, self._nominal_fps()))

    def closeEvent(self, event):
        self._tick_timer.stop()
        self._ltc_output.stop()
        self._mtc_sender.stop()
        self._clock.stop()
        super().closeEvent(event)


class MtcMidiOutput:
    """
    Sends MIDI Time Code quarter-frame messages.
    """
    def __init__(self, mtc_fps_provider, mtc_idle_behavior_provider=None):
        self.mtc_fps_provider = mtc_fps_provider
        self.mtc_idle_behavior_provider = mtc_idle_behavior_provider or (lambda: MTC_IDLE_KEEP_STREAM)
        self._midi = WinMMMidiOut()
        self._device = MIDI_OUTPUT_DEVICE_NONE
        self._opened = False
        self._qf_index = 0
        self._next_send_t = perf_counter()
        self._last_frame_sent = 0
        self._last_source_frame = 0
        self._latched_mtc_frame = 0
        self._has_sent = False
        self._last_full_frame_t = 0.0
        self._static_repeat_count = 0
        self._static_hold = False

    def set_device(self, device_id):
        device_id = str(device_id or MIDI_OUTPUT_DEVICE_NONE)
        if device_id == self._device:
            return
        self.stop()
        self._device = device_id
        if self._device == MIDI_OUTPUT_DEVICE_NONE:
            return
        if not self._midi.available():
            return
        try:
            self._opened = self._midi.open(int(self._device))
        except (TypeError, ValueError):
            self._opened = False
        self._qf_index = 0
        self._next_send_t = perf_counter()
        self._last_frame_sent = 0
        self._last_source_frame = 0
        self._latched_mtc_frame = 0
        self._has_sent = False
        self._last_full_frame_t = 0.0
        self._static_repeat_count = 0
        self._static_hold = False

    def stop(self):
        self._midi.close()
        self._opened = False
        self._qf_index = 0
        self._last_source_frame = 0
        self._has_sent = False
        self._last_full_frame_t = 0.0
        self._static_repeat_count = 0
        self._static_hold = False

    @staticmethod
    def _rate_code(fps: int, speed_fps: float) -> int:
        if fps == 24:
            return 0
        if fps == 25:
            return 1
        if fps == 30:
            # MTC code 2 represents 30-drop (commonly used for 29.97)
            if abs(speed_fps - 29.97) < 0.05 or abs(speed_fps - 59.94) < 0.05:
                return 2
            return 3
        return 3

    @staticmethod
    def _coerce_mtc_speed_fps(configured_fps: float) -> float:
        """
        MTC only supports 24, 25, 29.97-drop and 30.
        Pick the closest valid MTC frame rate from configuration.
        """
        fps = max(0.001, float(configured_fps))
        options = [24.0, 25.0, 29.97, 30.0]
        return min(options, key=lambda option: abs(option - fps))

    @staticmethod
    def _mtc_nominal_fps(mtc_speed_fps: float) -> int:
        if abs(mtc_speed_fps - 24.0) < 0.05:
            return 24
        if abs(mtc_speed_fps - 25.0) < 0.05:
            return 25
        return 30

    def _quarter_frame_data(self, frame_number: int, fps: int, speed_fps: float, qf_type: int) -> int:
        total_frames_day = 24 * 60 * 60 * max(1, fps)
        frame_number = max(0, int(frame_number)) % total_frames_day
        frames = frame_number % fps
        total_seconds = frame_number // fps
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = (total_minutes // 60) % 24
        if qf_type == 0:
            value = frames & 0x0F
        elif qf_type == 1:
            value = (frames >> 4) & 0x01
        elif qf_type == 2:
            value = seconds & 0x0F
        elif qf_type == 3:
            value = (seconds >> 4) & 0x03
        elif qf_type == 4:
            value = minutes & 0x0F
        elif qf_type == 5:
            value = (minutes >> 4) & 0x03
        elif qf_type == 6:
            value = hours & 0x0F
        else:
            rate_code = self._rate_code(fps, speed_fps)
            value = ((rate_code & 0x03) << 1) | ((hours >> 4) & 0x01)
        return ((qf_type & 0x07) << 4) | (value & 0x0F)

    def _send_full_frame(self, frame_number: int, fps: int, speed_fps: float, now: float) -> None:
        """
        Send a Full-Frame MTC SysEx packet to hard-lock receivers.
        """
        if not hasattr(self._midi, 'send_sysex'):
            return
        total_frames_day = 24 * 60 * 60 * max(1, fps)
        frame_number = max(0, int(frame_number)) % total_frames_day
        frames = frame_number % fps
        total_seconds = frame_number // fps
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = (total_minutes // 60) % 24
        rate_code = self._rate_code(fps, speed_fps)
        hr_byte = ((rate_code & 0x03) << 5) | (hours & 0x1F)
        # Universal Realtime Full Timecode Message (device id 0x7F = all-call)
        payload = bytes([0xF0, 0x7F, 0x7F, 0x01, 0x01, hr_byte, minutes & 0x3F, seconds & 0x3F, frames & 0x1F, 0xF7])
        try:
            self._midi.send_sysex(payload)
            self._last_full_frame_t = now
        except Exception:
            pass

    def update(self, current_frame: int, source_fps: float, mtc_fps=None):
        if not self._opened:
            return
        now = perf_counter()
        source_fps = max(0.001, float(source_fps))
        if mtc_fps is None:
            mtc_fps = self.mtc_fps_provider()
        configured_mtc_fps = self._coerce_mtc_speed_fps(float(mtc_fps))
        mtc_speed_fps = configured_mtc_fps
        fps = self._mtc_nominal_fps(mtc_speed_fps)
        current_source_frame = max(0, int(current_frame))
        current_mtc_frame = int(((current_source_frame * mtc_speed_fps) / source_fps) + 1e-6)
        interval = 1.0 / (mtc_speed_fps * 4.0)
        if now < self._next_send_t:
            return

        # Detect seek/large jump and restart quarter-frame cycle for clean decode.
        source_jump_threshold = max(2, int(source_fps * 0.25))
        mtc_jump_threshold = max(2, int(fps * 0.25))
        prev_mtc_frame = self._last_frame_sent
        source_jump = abs(current_source_frame - self._last_source_frame) > source_jump_threshold
        mtc_jump = abs(current_mtc_frame - prev_mtc_frame) > mtc_jump_threshold
        if self._has_sent and (source_jump or mtc_jump):
            message = (f'[Timecode] mtc resync: source_jump={source_jump} mtc_jump={mtc_jump} '
                       f'source_frame={current_source_frame} mtc_frame={current_mtc_frame}')
            print(message)
            log.info(message)
            self._qf_index = 0
            self._latched_mtc_frame = current_mtc_frame
            self._static_hold = False
            self._send_full_frame(current_mtc_frame, fps, mtc_speed_fps, now)

        if current_mtc_frame == prev_mtc_frame:
            self._static_repeat_count += 1
        else:
            self._static_repeat_count = 0

        allow_dark_on_idle = str(self.mtc_idle_behavior_provider()) == MTC_IDLE_ALLOW_DARK
        # Keep quarter-frame stream running even when static so desks don't blank.
        # Increase full-frame pinning cadence in static conditions to reduce wander.
        if self._static_repeat_count >= 8:
            self._static_hold = True
        if self._static_hold and current_mtc_frame != prev_mtc_frame:
            self._static_hold = False
            self._qf_index = 0
        if allow_dark_on_idle and self._static_hold:
            if (now - self._last_full_frame_t) >= 0.25:
                self._send_full_frame(current_mtc_frame, fps, mtc_speed_fps, now)
            self._last_source_frame = current_source_frame
            self._last_frame_sent = current_mtc_frame
            self._has_sent = True
            self._next_send_t = now + interval
            return

        # Keep one full timecode snapshot for all 8 quarter-frame packets.
        if self._qf_index == 0:
            self._latched_mtc_frame = current_mtc_frame
        data1 = self._quarter_frame_data(self._latched_mtc_frame, fps, mtc_speed_fps, self._qf_index)
        self._midi.send_short(0xF1, data1, 0)
        self._qf_index = (self._qf_index + 1) % 8
        self._last_source_frame = current_source_frame
        self._last_frame_sent = current_mtc_frame
        self._has_sent = True
        # Send full-frame periodically; faster while static to prevent receiver free-run drift.
        full_frame_interval = 0.25 if self._static_hold else 1.0
        if (now - self._last_full_frame_t) >= full_frame_interval:
            self._send_full_frame(current_mtc_frame, fps, mtc_speed_fps, now)
        self._next_send_t += interval
        if self._next_send_t < now - interval:
            self._next_send_t = now + interval
