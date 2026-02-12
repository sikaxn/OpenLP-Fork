#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Realtime LTC Quality Tool (Tk + QtMultimedia)

Captures audio input in realtime, estimates LTC lock quality, and shows:
- input level / clipping
- boundary lock %
- sync confidence %
- edge jitter (ms)
- estimated fps
- decoded timecode (best effort)

No third-party dependencies required beyond PySide6 (already used by OpenLP).
"""
from __future__ import annotations

import math
import tkinter as tk
from array import array
from collections import deque
from tkinter import messagebox, ttk

from PySide6.QtCore import QCoreApplication, QIODevice
from PySide6.QtMultimedia import QAudioFormat, QAudioSource, QMediaDevices


SYNC_WORD = 0xBFFC  # LSB-first in bit array


def sync_pattern_bits() -> list[int]:
    return [(SYNC_WORD >> i) & 1 for i in range(16)]


def bcd_value(bits: list[int], offset: int, width: int) -> int:
    value = 0
    for i in range(width):
        value |= (bits[offset + i] & 1) << i
    return value


def decode_timecode_from_frame_bits(frame_bits: list[int]) -> str | None:
    if len(frame_bits) < 80:
        return None
    frames = bcd_value(frame_bits, 0, 4) + (bcd_value(frame_bits, 8, 2) * 10)
    seconds = bcd_value(frame_bits, 16, 4) + (bcd_value(frame_bits, 24, 3) * 10)
    minutes = bcd_value(frame_bits, 32, 4) + (bcd_value(frame_bits, 40, 3) * 10)
    hours = bcd_value(frame_bits, 48, 4) + (bcd_value(frame_bits, 56, 2) * 10)
    if frames > 59 or seconds > 59 or minutes > 59 or hours > 23:
        return None
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}'


class AudioLtcAnalyzer:
    def __init__(self):
        self.sample_rate = 48000
        self.fps = 30.0
        self.hysteresis = 1200
        self._qt_app = QCoreApplication.instance() or QCoreApplication([])
        self._audio_source = None
        self._audio_io = None
        self._capturing = False
        self._sample_index = 0
        self._schmitt_state = 0
        self._transitions = deque(maxlen=20000)  # absolute sample indices
        self._level_window = deque(maxlen=4096)
        self._clipped_samples = 0
        self._total_samples = 0
        self.last_metrics = {}

    def list_input_devices(self):
        devices = []
        for device in QMediaDevices.audioInputs():
            devices.append((device, device.description()))
        return devices

    def _format(self) -> QAudioFormat:
        fmt = QAudioFormat()
        fmt.setSampleRate(self.sample_rate)
        fmt.setChannelCount(1)
        fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        return fmt

    def start(self, device):
        self.stop()
        fmt = self._format()
        self._audio_source = QAudioSource(device, fmt)
        self._audio_source.setBufferSize(16384)
        self._audio_io = self._audio_source.start()
        self._capturing = self._audio_io is not None
        self._sample_index = 0
        self._schmitt_state = 0
        self._transitions.clear()
        self._level_window.clear()
        self._clipped_samples = 0
        self._total_samples = 0

    def stop(self):
        self._capturing = False
        if self._audio_source:
            self._audio_source.stop()
        self._audio_io = None
        self._audio_source = None

    def set_fps(self, fps: float):
        self.fps = fps if fps > 0 else 30.0

    def process_qt_events(self):
        self._qt_app.processEvents()

    def poll(self):
        if not self._capturing or not self._audio_io:
            return
        available = int(self._audio_io.bytesAvailable())
        if available <= 0:
            return
        chunk = self._audio_io.read(min(available, 8192))
        if not chunk:
            return
        samples = array('h')
        samples.frombytes(bytes(chunk))
        self._consume_samples(samples)
        self.last_metrics = self._compute_metrics()

    def _consume_samples(self, samples: array):
        for s in samples:
            v = int(s)
            self._level_window.append(v)
            self._total_samples += 1
            if abs(v) >= 32760:
                self._clipped_samples += 1
            # Schmitt trigger transition detection
            if self._schmitt_state >= 0 and v <= -self.hysteresis:
                self._schmitt_state = -1
                self._transitions.append(self._sample_index)
            elif self._schmitt_state <= 0 and v >= self.hysteresis:
                self._schmitt_state = 1
                self._transitions.append(self._sample_index)
            self._sample_index += 1

    def _compute_metrics(self) -> dict:
        metrics = {
            'level_dbfs': None,
            'clip_pct': 0.0,
            'boundary_lock_pct': 0.0,
            'sync_conf_pct': 0.0,
            'jitter_ms': None,
            'fps_est': None,
            'decoded_tc': '--:--:--:--'
        }

        if self._level_window:
            rms = math.sqrt(sum(x * x for x in self._level_window) / float(len(self._level_window)))
            if rms > 0:
                metrics['level_dbfs'] = 20.0 * math.log10(rms / 32767.0)
        if self._total_samples > 0:
            metrics['clip_pct'] = (self._clipped_samples / float(self._total_samples)) * 100.0

        if len(self._transitions) < 200:
            return metrics

        transitions = list(self._transitions)
        intervals = [transitions[i] - transitions[i - 1] for i in range(1, len(transitions))]
        expected_half = self.sample_rate / (self.fps * 160.0)
        short_intervals = [d for d in intervals if d <= expected_half * 1.8]
        if short_intervals:
            short_sorted = sorted(short_intervals)
            half = float(short_sorted[len(short_sorted) // 2])
        else:
            half = expected_half
        if half < 2:
            return metrics
        metrics['fps_est'] = self.sample_rate / (half * 160.0)

        # Build slot transition map
        origin = transitions[0]
        tol = max(1.0, half * 0.35)
        slot_set = set()
        slot_errors = []
        for t in transitions:
            slot = int(round((t - origin) / half))
            ideal = origin + (slot * half)
            err = t - ideal
            if abs(err) <= tol:
                slot_set.add(slot)
                slot_errors.append(err)
        if slot_errors:
            rms_err = math.sqrt(sum(e * e for e in slot_errors) / float(len(slot_errors)))
            metrics['jitter_ms'] = (rms_err / self.sample_rate) * 1000.0

        max_slot = int(round((transitions[-1] - origin) / half))
        if max_slot < 200:
            return metrics

        best = None
        sync_bits = sync_pattern_bits()
        for parity in (0, 1):
            bit_count = max(0, (max_slot - parity - 1) // 2)
            if bit_count < 120:
                continue
            boundary_total = bit_count
            boundary_hits = 0
            bits = []
            for k in range(bit_count):
                boundary_slot = parity + (2 * k)
                data_slot = boundary_slot + 1
                if boundary_slot in slot_set:
                    boundary_hits += 1
                bits.append(1 if data_slot in slot_set else 0)
            boundary_lock = (boundary_hits / float(boundary_total)) * 100.0 if boundary_total else 0.0

            best_hd = 16
            best_i = -1
            for i in range(0, len(bits) - 15):
                hd = 0
                for j in range(16):
                    if bits[i + j] != sync_bits[j]:
                        hd += 1
                if hd < best_hd:
                    best_hd = hd
                    best_i = i
                    if hd == 0:
                        break
            sync_conf = max(0.0, (1.0 - (best_hd / 16.0)) * 100.0)
            candidate = (boundary_lock, sync_conf, best_i, bits)
            if best is None or (candidate[0], candidate[1]) > (best[0], best[1]):
                best = candidate

        if best is None:
            return metrics

        boundary_lock, sync_conf, best_i, bits = best
        metrics['boundary_lock_pct'] = boundary_lock
        metrics['sync_conf_pct'] = sync_conf
        if best_i >= 64:
            frame_start = best_i - 64
            if frame_start + 80 <= len(bits):
                decoded = decode_timecode_from_frame_bits(bits[frame_start:frame_start + 80])
                if decoded:
                    metrics['decoded_tc'] = decoded
        return metrics


class RealtimeQualityApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Realtime Timecode Quality Tool')
        self.root.geometry('860x520')
        self.analyzer = AudioLtcAnalyzer()
        self.device_map = {}

        self.fps_var = tk.StringVar(value='30')
        self.device_var = tk.StringVar(value='')
        self.status_var = tk.StringVar(value='Select input device and click Start.')
        self.running = False

        self._build_ui()
        self._load_devices()
        self._tick()

    def _build_ui(self):
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack(fill='x')

        tk.Label(top, text='Input Device').pack(side='left')
        self.device_combo = ttk.Combobox(top, textvariable=self.device_var, state='readonly', width=42)
        self.device_combo.pack(side='left', padx=8)
        tk.Button(top, text='Refresh', command=self._load_devices).pack(side='left')

        tk.Label(top, text='FPS').pack(side='left', padx=8)
        tk.Entry(top, textvariable=self.fps_var, width=7).pack(side='left')

        self.start_btn = tk.Button(top, text='Start', command=self.start)
        self.start_btn.pack(side='left', padx=8)
        self.stop_btn = tk.Button(top, text='Stop', command=self.stop, state='disabled')
        self.stop_btn.pack(side='left')

        metrics = tk.LabelFrame(self.root, text='Realtime Metrics', padx=10, pady=10)
        metrics.pack(fill='x', padx=10, pady=10)
        self.metric_labels = {}
        rows = [
            'Decoded Timecode',
            'Signal Level (dBFS)',
            'Clipping (%)',
            'Boundary Lock (%)',
            'Sync Confidence (%)',
            'Edge Jitter (ms)',
            'Estimated FPS'
        ]
        for i, label in enumerate(rows):
            tk.Label(metrics, text=label).grid(row=i, column=0, sticky='w')
            val = tk.Label(metrics, text='-', font=('Consolas', 10, 'bold'))
            val.grid(row=i, column=1, sticky='w', padx=14)
            self.metric_labels[label] = val

        note = tk.LabelFrame(self.root, text='Notes', padx=10, pady=10)
        note.pack(fill='both', expand=True, padx=10, pady=10)
        text = (
            'Quality guidance:\n'
            '- Boundary Lock should stay high (typically >95%).\n'
            '- Sync Confidence should be high and stable.\n'
            '- Edge Jitter should be low and stable.\n'
            '- Clipping should stay near 0%.\n'
            '\n'
            'If lock is unstable: adjust interface gain, disable processing/compression, and use a clean mono feed.'
        )
        tk.Label(note, text=text, justify='left', anchor='nw').pack(fill='both', expand=True, anchor='nw')

        bottom = tk.Frame(self.root, padx=10, pady=10)
        bottom.pack(fill='x')
        tk.Label(bottom, textvariable=self.status_var, anchor='w').pack(fill='x')

    def _load_devices(self):
        devices = self.analyzer.list_input_devices()
        names = []
        self.device_map = {}
        for device, desc in devices:
            names.append(desc)
            self.device_map[desc] = device
        self.device_combo['values'] = names
        if names:
            self.device_var.set(names[0])
            self.status_var.set(f'Found {len(names)} input device(s).')
        else:
            self.device_var.set('')
            self.status_var.set('No audio input devices found.')

    def start(self):
        try:
            device_name = self.device_var.get().strip()
            if not device_name:
                raise ValueError('Select an input device.')
            fps = float(self.fps_var.get().strip())
            if fps <= 0:
                raise ValueError('FPS must be > 0.')
            self.analyzer.set_fps(fps)
            self.analyzer.start(self.device_map[device_name])
            self.running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_var.set(f'Listening on: {device_name}')
        except Exception as exc:
            messagebox.showerror('Start Failed', str(exc))

    def stop(self):
        self.analyzer.stop()
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_var.set('Stopped.')

    def _set_metric(self, key: str, value: str):
        self.metric_labels[key].config(text=value)

    def _update_metrics(self):
        m = self.analyzer.last_metrics or {}
        self._set_metric('Decoded Timecode', m.get('decoded_tc', '--:--:--:--'))
        level = m.get('level_dbfs')
        self._set_metric('Signal Level (dBFS)', '-' if level is None else f'{level:.2f}')
        self._set_metric('Clipping (%)', f"{m.get('clip_pct', 0.0):.4f}")
        self._set_metric('Boundary Lock (%)', f"{m.get('boundary_lock_pct', 0.0):.2f}")
        self._set_metric('Sync Confidence (%)', f"{m.get('sync_conf_pct', 0.0):.2f}")
        jitter = m.get('jitter_ms')
        self._set_metric('Edge Jitter (ms)', '-' if jitter is None else f'{jitter:.4f}')
        fps_est = m.get('fps_est')
        self._set_metric('Estimated FPS', '-' if fps_est is None else f'{fps_est:.4f}')

    def _tick(self):
        try:
            self.analyzer.process_qt_events()
            if self.running:
                self.analyzer.poll()
                self._update_metrics()
        except Exception as exc:
            self.status_var.set(f'Error: {exc}')
            self.stop()
        self.root.after(30, self._tick)


def main():
    root = tk.Tk()
    app = RealtimeQualityApp(root)
    root.protocol('WM_DELETE_WINDOW', lambda: (app.stop(), root.destroy()))
    root.mainloop()


if __name__ == '__main__':
    main()

