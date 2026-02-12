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
Tests for :mod:`openlp.core.timecode.manager`.
"""
from openlp.core.timecode.manager import (
    MtcMidiOutput,
    encode_ltc_bits,
    frame_to_timecode_parts,
    frame_to_timecode_string
)


class FakeMidi:
    def __init__(self):
        self.messages = []

    def send_short(self, status, data1=0, data2=0):
        self.messages.append((status, data1, data2))

    def close(self):
        pass


def test_frame_to_timecode_parts():
    """
    Test conversion from frames to timecode parts.
    """
    hours, minutes, seconds, frames = frame_to_timecode_parts((1 * 3600 + 2 * 60 + 3) * 30 + 4, 30)
    assert (hours, minutes, seconds, frames) == (1, 2, 3, 4)


def test_frame_to_timecode_wraps_24_hours():
    """
    Test that timecode wraps after 24h.
    """
    text = frame_to_timecode_string(24 * 3600 * 30, 30)
    assert text == '00:00:00:00'


def test_encode_ltc_bits_length_and_sync():
    """
    Test encoded LTC frame shape and sync word.
    """
    bits = encode_ltc_bits(0, 30)
    assert len(bits) == 80
    sync_value = sum((bits[64 + index] << index) for index in range(16))
    assert sync_value == 0xBFFC


def test_mtc_latches_frame_across_qf_cycle():
    """
    Test that all 8 quarter-frame packets in a cycle use one frame snapshot.
    """
    sender = MtcMidiOutput(lambda: 30)
    sender._midi = FakeMidi()
    sender._opened = True
    for frame in range(100, 108):
        sender._next_send_t = 0.0
        sender.update(frame, 30.0, 30.0)
    assert len(sender._midi.messages) == 8
    data_bytes = [message[1] for message in sender._midi.messages]
    expected = [sender._quarter_frame_data(100, 30, 30.0, index) for index in range(8)]
    assert data_bytes == expected


def test_mtc_maps_60fps_to_30fps_encoding():
    """
    Test that 60fps source timing is mapped to valid 30fps MTC encoding.
    """
    sender = MtcMidiOutput(lambda: 60)
    sender._midi = FakeMidi()
    sender._opened = True
    sender._next_send_t = 0.0
    sender.update(59, 60.0, 30.0)
    sender._next_send_t = 0.0
    sender.update(60, 60.0, 30.0)
    assert len(sender._midi.messages) == 2
    assert sender._midi.messages[0][1] == sender._quarter_frame_data(29, 30, 30.0, 0)
    assert sender._midi.messages[1][1] == sender._quarter_frame_data(29, 30, 30.0, 1)
