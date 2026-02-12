#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Timecode Drift Analyzer (Tkinter)

Loads CSV or pasted samples and analyzes drift between reference and observed timecode.

Accepted sample formats:
1) reference_tc,observed_tc
2) reference_ms,observed_ms
3) elapsed_ms,drift_ms
4) Any CSV with headers containing:
   - ref/reference + tc/timecode OR ms
   - obs/observed + tc/timecode OR ms
   - OR drift (+ optional elapsed/time/timestamp)

Timecode format: HH:MM:SS:FF
"""
from __future__ import annotations

import csv
import math
import re
import statistics
import tkinter as tk
from tkinter import filedialog, messagebox


TC_RE = re.compile(r'^\s*(\d{1,2}):(\d{2}):(\d{2}):(\d{2})\s*$')


def parse_timecode_to_ms(value: str, fps: float) -> float:
    match = TC_RE.match(str(value))
    if not match:
        raise ValueError(f'Invalid timecode: {value}')
    hh, mm, ss, ff = [int(x) for x in match.groups()]
    return ((hh * 3600 + mm * 60 + ss) * 1000.0) + ((ff / fps) * 1000.0)


def normalize_header(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', name.lower().strip())


def parse_number(value: str) -> float:
    return float(str(value).strip())


def linear_regression_slope(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    mean_x = statistics.mean(xs)
    mean_y = statistics.mean(ys)
    numerator = 0.0
    denominator = 0.0
    for x, y in zip(xs, ys):
        dx = x - mean_x
        numerator += dx * (y - mean_y)
        denominator += dx * dx
    if denominator == 0:
        return 0.0
    return numerator / denominator


class DriftAnalyzerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Timecode Drift Analyzer')
        self.root.geometry('1120x760')

        self.samples: list[tuple[float, float]] = []  # (elapsed_ms, drift_ms)
        self.fps_var = tk.StringVar(value='30')
        self.status_var = tk.StringVar(value='Load CSV or paste samples, then click Analyze.')
        self.path_var = tk.StringVar(value='')

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root, padx=10, pady=8)
        top.pack(fill='x')

        tk.Label(top, text='FPS').pack(side='left')
        tk.Entry(top, width=8, textvariable=self.fps_var).pack(side='left', padx=(6, 12))
        tk.Button(top, text='Load CSV', command=self.load_csv).pack(side='left')
        tk.Button(top, text='Analyze', command=self.analyze).pack(side='left', padx=6)
        tk.Button(top, text='Clear', command=self.clear).pack(side='left', padx=6)
        tk.Label(top, text='File:').pack(side='left', padx=(12, 4))
        tk.Entry(top, textvariable=self.path_var).pack(side='left', fill='x', expand=True)

        mid = tk.PanedWindow(self.root, orient='horizontal', sashrelief='raised')
        mid.pack(fill='both', expand=True, padx=10, pady=(0, 8))

        left = tk.Frame(mid)
        right = tk.Frame(mid)
        mid.add(left, minsize=380)
        mid.add(right, minsize=400)

        tk.Label(left, text='Paste Samples (CSV):').pack(anchor='w')
        self.text = tk.Text(left, wrap='none', height=16)
        self.text.pack(fill='both', expand=True, pady=(4, 8))
        self.text.insert(
            '1.0',
            'reference_tc,observed_tc\n'
            '00:00:00:00,00:00:00:00\n'
            '00:00:10:00,00:00:09:29\n'
        )

        stats_frame = tk.LabelFrame(left, text='Stats', padx=8, pady=8)
        stats_frame.pack(fill='x')
        self.stats_labels = {}
        stat_names = [
            'Samples',
            'Mean Drift (ms)',
            'Median Drift (ms)',
            'Std Dev (ms)',
            'Peak + Drift (ms)',
            'Peak - Drift (ms)',
            'Max Abs Drift (ms)',
            'Drift Rate (ms/min)',
            'Drift Rate (ppm)'
        ]
        for i, name in enumerate(stat_names):
            tk.Label(stats_frame, text=name).grid(row=i, column=0, sticky='w')
            val = tk.Label(stats_frame, text='-')
            val.grid(row=i, column=1, sticky='e', padx=(12, 0))
            self.stats_labels[name] = val

        tk.Label(right, text='Drift Plot (ms over elapsed time)').pack(anchor='w')
        self.canvas = tk.Canvas(right, bg='white', highlightthickness=1, highlightbackground='#c0c0c0')
        self.canvas.pack(fill='both', expand=True, pady=(4, 0))
        self.canvas.bind('<Configure>', lambda _e: self.draw_plot())

        bottom = tk.Frame(self.root, padx=10, pady=(0, 10))
        bottom.pack(fill='x')
        tk.Label(bottom, textvariable=self.status_var, anchor='w').pack(fill='x')

    def clear(self):
        self.samples = []
        self.path_var.set('')
        self.status_var.set('Cleared.')
        self.text.delete('1.0', tk.END)
        self.draw_plot()
        for label in self.stats_labels.values():
            label.config(text='-')

    def load_csv(self):
        path = filedialog.askopenfilename(
            title='Open CSV',
            filetypes=[('CSV files', '*.csv'), ('Text files', '*.txt'), ('All files', '*.*')]
        )
        if not path:
            return
        self.path_var.set(path)
        with open(path, 'r', encoding='utf-8-sig', newline='') as fh:
            self.text.delete('1.0', tk.END)
            self.text.insert('1.0', fh.read())
        self.status_var.set(f'Loaded: {path}')

    def _parse_text(self) -> list[tuple[float, float]]:
        text = self.text.get('1.0', tk.END).strip()
        if not text:
            raise ValueError('No samples provided.')
        fps = float(self.fps_var.get().strip())
        if fps <= 0:
            raise ValueError('FPS must be > 0.')

        rows = list(csv.reader(text.splitlines()))
        if not rows:
            raise ValueError('No rows found.')

        header = [normalize_header(x) for x in rows[0]]
        has_header = any(any(ch.isalpha() for ch in cell) for cell in rows[0])
        data_rows = rows[1:] if has_header else rows

        if has_header:
            return self._parse_rows_with_header(header, data_rows, fps)
        return self._parse_rows_no_header(data_rows, fps)

    def _find_col(self, header: list[str], options: list[str]) -> int | None:
        for i, name in enumerate(header):
            for opt in options:
                if opt in name:
                    return i
        return None

    def _parse_rows_with_header(self, header: list[str], rows: list[list[str]], fps: float) -> list[tuple[float, float]]:
        elapsed_idx = self._find_col(header, ['elapsed', 'time', 'timestamp'])
        drift_idx = self._find_col(header, ['drift'])
        ref_tc_idx = self._find_col(header, ['referencetc', 'reftc', 'referencetimecode', 'reftimecode'])
        obs_tc_idx = self._find_col(header, ['observedtc', 'obstc', 'observedtimecode', 'obstimecode'])
        ref_ms_idx = self._find_col(header, ['referencems', 'refms'])
        obs_ms_idx = self._find_col(header, ['observedms', 'obsms'])

        samples = []
        for row in rows:
            if not row:
                continue
            if drift_idx is not None:
                drift_ms = parse_number(row[drift_idx])
                if elapsed_idx is not None:
                    elapsed_ms = parse_number(row[elapsed_idx])
                else:
                    elapsed_ms = len(samples) * 1000.0 / fps
                samples.append((elapsed_ms, drift_ms))
                continue

            if ref_tc_idx is not None and obs_tc_idx is not None:
                ref_ms = parse_timecode_to_ms(row[ref_tc_idx], fps)
                obs_ms = parse_timecode_to_ms(row[obs_tc_idx], fps)
            elif ref_ms_idx is not None and obs_ms_idx is not None:
                ref_ms = parse_number(row[ref_ms_idx])
                obs_ms = parse_number(row[obs_ms_idx])
            else:
                continue

            elapsed_ms = ref_ms if elapsed_idx is None else parse_number(row[elapsed_idx])
            samples.append((elapsed_ms, obs_ms - ref_ms))

        if not samples:
            raise ValueError('Could not detect compatible columns in header.')
        return samples

    def _parse_rows_no_header(self, rows: list[list[str]], fps: float) -> list[tuple[float, float]]:
        samples = []
        for i, row in enumerate(rows):
            if len(row) < 2:
                continue
            a = row[0].strip()
            b = row[1].strip()
            if TC_RE.match(a) and TC_RE.match(b):
                ref_ms = parse_timecode_to_ms(a, fps)
                obs_ms = parse_timecode_to_ms(b, fps)
                samples.append((ref_ms, obs_ms - ref_ms))
            else:
                x = parse_number(a)
                y = parse_number(b)
                # Assume "elapsed_ms,drift_ms"
                samples.append((x, y))
        if not samples:
            raise ValueError('No parseable data rows found.')
        return samples

    def analyze(self):
        try:
            self.samples = self._parse_text()
            self.samples.sort(key=lambda x: x[0])
            self._update_stats()
            self.draw_plot()
            self.status_var.set(f'Analyzed {len(self.samples)} samples.')
        except Exception as exc:
            messagebox.showerror('Analyze Failed', str(exc))
            self.status_var.set(f'Error: {exc}')

    def _update_stats(self):
        drifts = [d for _, d in self.samples]
        xs = [x for x, _ in self.samples]
        sample_count = len(drifts)

        mean_drift = statistics.mean(drifts)
        median_drift = statistics.median(drifts)
        stdev = statistics.pstdev(drifts) if sample_count > 1 else 0.0
        peak_pos = max(drifts)
        peak_neg = min(drifts)
        max_abs = max(abs(peak_pos), abs(peak_neg))

        slope_ms_per_ms = linear_regression_slope(xs, drifts) if sample_count > 1 else 0.0
        drift_rate_ms_per_min = slope_ms_per_ms * 60_000.0
        drift_rate_ppm = slope_ms_per_ms * 1_000_000.0

        values = {
            'Samples': f'{sample_count}',
            'Mean Drift (ms)': f'{mean_drift:.3f}',
            'Median Drift (ms)': f'{median_drift:.3f}',
            'Std Dev (ms)': f'{stdev:.3f}',
            'Peak + Drift (ms)': f'{peak_pos:.3f}',
            'Peak - Drift (ms)': f'{peak_neg:.3f}',
            'Max Abs Drift (ms)': f'{max_abs:.3f}',
            'Drift Rate (ms/min)': f'{drift_rate_ms_per_min:.4f}',
            'Drift Rate (ppm)': f'{drift_rate_ppm:.4f}'
        }
        for key, value in values.items():
            self.stats_labels[key].config(text=value)

    def draw_plot(self):
        self.canvas.delete('all')
        width = max(10, self.canvas.winfo_width())
        height = max(10, self.canvas.winfo_height())
        pad_l, pad_r, pad_t, pad_b = 56, 20, 20, 36
        plot_w = max(1, width - pad_l - pad_r)
        plot_h = max(1, height - pad_t - pad_b)

        self.canvas.create_rectangle(pad_l, pad_t, pad_l + plot_w, pad_t + plot_h, outline='#b0b0b0')

        if not self.samples:
            self.canvas.create_text(width // 2, height // 2, text='No data', fill='#666666')
            return

        xs = [x for x, _ in self.samples]
        ys = [y for _, y in self.samples]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        if x_max <= x_min:
            x_max = x_min + 1.0
        if math.isclose(y_max, y_min):
            y_max += 1.0
            y_min -= 1.0

        max_abs = max(abs(y_min), abs(y_max))
        y_min, y_max = -max_abs, max_abs

        def map_x(x: float) -> float:
            return pad_l + ((x - x_min) / (x_max - x_min)) * plot_w

        def map_y(y: float) -> float:
            return pad_t + plot_h - ((y - y_min) / (y_max - y_min)) * plot_h

        # Zero line
        y0 = map_y(0.0)
        self.canvas.create_line(pad_l, y0, pad_l + plot_w, y0, fill='#c04040', dash=(4, 2))
        self.canvas.create_text(pad_l - 8, y0, text='0', anchor='e', fill='#804040')

        # Drift line
        points = []
        for x, y in self.samples:
            points.extend([map_x(x), map_y(y)])
        if len(points) >= 4:
            self.canvas.create_line(*points, fill='#2468b4', width=2, smooth=False)

        # Y labels
        for val in [y_min, y_min / 2, 0.0, y_max / 2, y_max]:
            yy = map_y(val)
            self.canvas.create_line(pad_l - 4, yy, pad_l, yy, fill='#707070')
            self.canvas.create_text(pad_l - 8, yy, text=f'{val:.1f}', anchor='e', fill='#404040')

        # X labels
        for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
            x_val = x_min + (x_max - x_min) * frac
            xx = map_x(x_val)
            self.canvas.create_line(xx, pad_t + plot_h, xx, pad_t + plot_h + 4, fill='#707070')
            self.canvas.create_text(xx, pad_t + plot_h + 16, text=f'{x_val / 1000.0:.1f}s', fill='#404040')

        self.canvas.create_text(pad_l + 6, pad_t + 8, anchor='nw',
                                text='Drift (ms)', fill='#2468b4')


def main():
    root = tk.Tk()
    app = DriftAnalyzerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

