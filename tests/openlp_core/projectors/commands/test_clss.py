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
Tests for PJLink CLSS command
"""

import logging
import openlp.core.projectors.pjlinkcommands

from openlp.core.projectors.pjlinkcommands import process_clss
from unittest.mock import patch

test_module = openlp.core.projectors.pjlinkcommands.__name__


def test_reply_long_no_number(pjlink, caplog):
    """
    Tests reply data length too long
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = 'Class A'
    logs = [(f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) Non-standard CLSS reply: "{t_data}"'),
            (f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) No numbers found in class version reply '
             f'"{t_data}" - defaulting to class "1"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting pjlink_class for this projector to "1"')
            ]

    with patch.object(pjlink, 'poll_timer') as mock_timer:
        # WHEN: process_clss called
        caplog.clear()
        t_chk = process_clss(projector=pjlink, data=t_data)

        # THEN: Log entries and settings apply
        assert t_chk is None, f'Invalid return code {t_chk}'
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.pjlink_class == '1', 'Should have set pjlink_class = "1"'
        mock_timer.setInterval.assert_not_called()
        mock_timer.start.assert_not_called()


def test_reply_long_optoma(pjlink, caplog):
    """
    Tests invalid reply from Optoma projectors
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = 'Class 1'
    logs = [(f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) Non-standard CLSS reply: "{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting pjlink_class for this projector to "1"')
            ]

    with patch.object(pjlink, 'poll_timer') as mock_timer:
        # WHEN: process_clss called
        caplog.clear()
        t_chk = process_clss(projector=pjlink, data=t_data)

        # THEN: Log entries and settings apply
        assert t_chk is None, f'Invalid return code {t_chk}'
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.pjlink_class == '1', 'Should have set pjlink_class = "1"'
        mock_timer.setInterval.assert_not_called()
        mock_timer.start.assert_not_called()


def test_reply_long_benq(pjlink, caplog):
    """
    Tests invalid reply from BenQ projectors
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = 'Version1'
    logs = [(f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) Non-standard CLSS reply: "{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting pjlink_class for this projector to "1"')
            ]

    with patch.object(pjlink, 'poll_timer') as mock_timer:
        # WHEN: process_clss called
        caplog.clear()
        t_chk = process_clss(projector=pjlink, data=t_data)

        # THEN: Log entries and settings apply
        assert t_chk is None, f'Invalid return code {t_chk}'
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.pjlink_class == '1', 'Should have set pjlink_class = "1"'
        mock_timer.setInterval.assert_not_called()
        mock_timer.start.assert_not_called()


def test_reply_nan(pjlink, caplog):
    """
    Tests invalid reply (Not A Number)
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = 'A'
    logs = [(f'{test_module}', logging.WARNING,
             f'({pjlink.entry.name}) NAN CLSS version reply '
             f'"{t_data}" - defaulting to class "1"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting pjlink_class for this projector to "1"')
            ]

    with patch.object(pjlink, 'poll_timer') as mock_timer:
        # WHEN: process_clss called
        caplog.clear()
        t_chk = process_clss(projector=pjlink, data=t_data)

        # THEN: Log entries and settings apply
        assert t_chk is None, f'Invalid return code {t_chk}'
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.pjlink_class == '1', 'Should have set pjlink_class = "1"'
        mock_timer.setInterval.assert_not_called()
        mock_timer.start.assert_not_called()


def test_class_1(pjlink, caplog):
    """
    Tests valid Class 1 reply
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = '1'
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting pjlink_class for this projector to "{t_data}"')
            ]

    with patch.object(pjlink, 'poll_timer') as mock_timer:
        # WHEN: process_clss called
        caplog.clear()
        t_chk = process_clss(projector=pjlink, data=t_data)

        # THEN: Log entries and settings apply
        assert t_chk is None, f'Invalid return code {t_chk}'
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.pjlink_class == '1', 'Should have set pjlink_class = "1"'
        mock_timer.setInterval.assert_not_called()
        mock_timer.start.assert_not_called()


def test_class_2(pjlink, caplog):
    """
    Tests valid Class 1 reply
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = '2'
    pjlink.pjlink_class = '1'
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting pjlink_class for this projector to "{t_data}"')
            ]

    with patch.object(pjlink, 'poll_timer') as mock_timer:
        # WHEN: process_clss called
        caplog.clear()
        t_chk = process_clss(projector=pjlink, data=t_data)

        # THEN: Log entries and settings apply
        assert t_chk is None, f'Invalid return code {t_chk}'
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.pjlink_class == t_data, f'Should have set pjlink_class = "{t_data}"'
        mock_timer.setInterval.assert_not_called()
        mock_timer.start.assert_not_called()


def test_start_poll(pjlink, caplog):
    """
    Tests poll_loop starts
    """
    # GIVEN: Test setup
    caplog.set_level(logging.DEBUG)
    t_data = '2'
    pjlink.no_poll = False
    logs = [(f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) Setting pjlink_class for this projector to "{t_data}"'),
            (f'{test_module}', logging.DEBUG,
             f'({pjlink.entry.name}) process_pjlink(): Starting timer')
            ]

    with patch.object(pjlink, 'poll_timer') as mock_timer:
        # WHEN: process_clss called
        caplog.clear()
        t_chk = process_clss(projector=pjlink, data=t_data)

        # THEN: Log entries and settings apply
        assert t_chk is None, f'Invalid return code {t_chk}'
        assert caplog.record_tuples == logs, 'Invalid log entries'
        assert pjlink.pjlink_class == t_data, f'Should have set pjlink_class = "{t_data}"'
        mock_timer.setInterval.assert_called_with(1000)
        mock_timer.start.assert_called_once()
