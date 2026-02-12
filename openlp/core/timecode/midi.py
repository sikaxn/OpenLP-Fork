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
MIDI output helpers for MTC (Windows winmm backend).
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes


MIDI_OUTPUT_DEVICE_NONE = '__none__'


class MIDIIOCAPSW(ctypes.Structure):
    _fields_ = [
        ('wMid', wintypes.WORD),
        ('wPid', wintypes.WORD),
        ('vDriverVersion', wintypes.DWORD),
        ('szPname', wintypes.WCHAR * 32),
        ('wTechnology', wintypes.WORD),
        ('wVoices', wintypes.WORD),
        ('wNotes', wintypes.WORD),
        ('wChannelMask', wintypes.WORD),
        ('dwSupport', wintypes.DWORD)
    ]


class WinMMMidiOut:
    """
    Minimal winmm MIDI Out wrapper.
    """
    def __init__(self):
        self._winmm = None
        self._handle = wintypes.HANDLE()
        self._opened = False
        try:
            dword_ptr = getattr(wintypes, 'DWORD_PTR', ctypes.c_size_t)
            self._winmm = ctypes.WinDLL('winmm')
            self._winmm.midiOutGetNumDevs.restype = wintypes.UINT
            self._winmm.midiOutGetDevCapsW.argtypes = [wintypes.UINT, ctypes.POINTER(MIDIIOCAPSW), wintypes.UINT]
            self._winmm.midiOutGetDevCapsW.restype = wintypes.UINT
            self._winmm.midiOutOpen.argtypes = [ctypes.POINTER(wintypes.HANDLE), wintypes.UINT,
                                                dword_ptr, dword_ptr, wintypes.DWORD]
            self._winmm.midiOutOpen.restype = wintypes.UINT
            self._winmm.midiOutShortMsg.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            self._winmm.midiOutShortMsg.restype = wintypes.UINT
            self._winmm.midiOutReset.argtypes = [wintypes.HANDLE]
            self._winmm.midiOutReset.restype = wintypes.UINT
            self._winmm.midiOutClose.argtypes = [wintypes.HANDLE]
            self._winmm.midiOutClose.restype = wintypes.UINT
        except Exception:
            self._winmm = None

    def available(self) -> bool:
        return self._winmm is not None

    def list_devices(self) -> list[tuple[str, str]]:
        if not self._winmm:
            return []
        count = int(self._winmm.midiOutGetNumDevs())
        devices = []
        for idx in range(count):
            caps = MIDIIOCAPSW()
            result = self._winmm.midiOutGetDevCapsW(idx, ctypes.byref(caps), ctypes.sizeof(caps))
            if result == 0:
                devices.append((str(idx), str(caps.szPname)))
        return devices

    def open(self, device_id: int) -> bool:
        if not self._winmm:
            return False
        self.close()
        result = self._winmm.midiOutOpen(ctypes.byref(self._handle), int(device_id), 0, 0, 0)
        self._opened = (result == 0)
        return self._opened

    def send_short(self, status: int, data1: int = 0, data2: int = 0) -> None:
        if not self._opened or not self._winmm:
            return
        message = (int(status) & 0xFF) | ((int(data1) & 0xFF) << 8) | ((int(data2) & 0xFF) << 16)
        self._winmm.midiOutShortMsg(self._handle, message)

    def close(self) -> None:
        if not self._opened or not self._winmm:
            return
        self._winmm.midiOutReset(self._handle)
        self._winmm.midiOutClose(self._handle)
        self._opened = False


def get_midi_output_devices() -> list[tuple[str, str]]:
    midi = WinMMMidiOut()
    return midi.list_devices() if midi.available() else []
