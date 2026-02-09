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
The :mod:`openlp.core.lib.projector.pjlinkcmmands` module provides the necessary functions for
processing projector replies.

NOTE: PJLink Class (version) checks are handled in the respective PJLink/PJLinkUDP classes.
      process_clss is the only exception.

NOTE: Some commands are both commannd replies as well as UDP terminal-initiated status
      messages.

      Ex: POWR

      CLSS1 (TCP): controller  sends "POWR x", projector replies "POWR=xxxxx"
      CLSS2 (UDP): projector sends "POWER=xxxx"

      Inn both instances, the messagege is processed the same.

      For CLSS1, we initiate communication, so we know which projecttor instance
      the message is routed to.

      For CLSS2, the terminal initiates communication, so as part of the UDP process
      we must find the projector that initiated the message.
"""

import logging
import re
import string

from openlp.core.common.registry import Registry

from openlp.core.projectors.constants import E_AUTHENTICATION, PJLINK_DEFAULT_CODES, PJLINK_ERRORS, \
    PJLINK_ERST_DATA, PJLINK_ERST_LIST, PJLINK_ERST_STATUS, PJLINK_POWR_STATUS, PJLINK_SVER_MAX_LEN, \
    PJLINK_TOKEN_SIZE, E_NO_AUTHENTICATION, S_AUTHENTICATE, S_CONNECT, S_DATA_OK, S_OFF, S_OK, S_ON, \
    S_STANDBY, STATUS_MSG

log = logging.getLogger(__name__)
log.debug('Loading pjlinkcommands')

__all__ = ['process_command']

_pjlink_functions = {}
# Helper until I update the rest of the tests
pjlink_functions = _pjlink_functions


# This should be the only function that's imported.
def process_command(projector, cmd, data):
    """
    Verifies any return error code. Calls the appropriate command handler.

    :param projector: Projector instance
    :param cmd: Command to process
    :param data: Data being processed
    """
    log.debug(f'({projector.entry.name}) Processing command "{cmd}" with data "{data}"')
    # cmd should already be in uppercase, but data may be in mixed-case.
    # Due to some replies should stay as mixed-case, validate using separate uppercase check
    _data = data.upper()
    # Check if we have a future command not available yet
    if cmd not in pjlink_functions:
        log.warning(f'({projector.entry.name}) Unable to process command="{cmd}" (Future option?)')
        return
    elif _data == 'OK':
        log.debug(f'({projector.entry.name}) Command "{cmd}" returned OK')
        # A command returned successfully, so do a query on command to verify status
        return S_DATA_OK

    elif _data in PJLINK_ERRORS:
        # Oops - projector error
        log.error(f'({projector.entry.name}) {cmd}: {STATUS_MSG[PJLINK_ERRORS[_data]]}')
        return PJLINK_ERRORS[_data]

    # Command checks already passed
    log.debug(f'({projector.entry.name}) Calling function for {cmd}')
    return pjlink_functions[cmd](projector=projector, data=data)


def process_ackn(projector, data):
    """
    Process the ACKN command.

    UDP reply to SRCH command

    :param projector: Projector instance
    :param data: Data in packet
    """
    # TODO: Have to rethink this one
    pass


_pjlink_functions['ACKN'] = process_ackn


def _process_avmt_mute(projector, data):
    """
    Helper to set projector.mute
    """
    projector.mute = data


def _process_avmt_shutter(projector, data):
    """
    Helper to set projector.shutter
    """
    projector.shutter = data


def _process_avmt(projector, data):
    """
    Process shutter and speaker status. See PJLink specification for format.

    Update projector.mute (audio mute) and projector.shutter (video mute).
    10 = Shutter open, audio unchanged
    11 = Shutter closed, audio unchanged
    20 = Shutter unchanged, audio normal
    21 = Shutter unchanged, audio mute
    30 = Shutter open, audio normal
    31 = Shutter closed, audio mute

    :param projector: Projector instance
    :param data: Shutter and audio status
    """
    settings = {'10': {'shutter': False, 'mute': projector.mute},
                '11': {'shutter': True, 'mute': projector.mute},
                '20': {'shutter': projector.shutter, 'mute': False},
                '21': {'shutter': projector.shutter, 'mute': True},
                '30': {'shutter': False, 'mute': False},
                '31': {'shutter': True, 'mute': True}
                }
    if data not in settings:
        log.warning(f'({projector.entry.name}) Invalid av mute response: {data}')
        return
    shutter = settings[data]['shutter']
    mute = settings[data]['mute']
    update_icons = False
    if projector.shutter != shutter:
        _process_avmt_shutter(projector=projector, data=shutter)
        update_icons = True
        log.debug(f'({projector.entry.name}) Setting shutter to {"closed" if shutter else "open"}')
    if projector.mute != mute:
        _process_avmt_mute(projector=projector, data=mute)
        projector.mute = mute
        update_icons = True
        log.debug(f'({projector.entry.name}) Setting speaker to {"muted" if mute else "normal"}')
    if update_icons:
        projector.projectorUpdateIcons.emit()
    projector.status_timer_delete('AVMT')


_pjlink_functions['AVMT'] = _process_avmt


def process_clss(projector, data):
    """
    PJLink class that this projector supports. See PJLink specification for format.
    Updates projector.class.

    :param projector: Projector instance
    :param data: Class that projector supports.
    """
    # bug 1550891: Projector returns non-standard class response:
    #            : Expected: '%1CLSS=1'
    #            : Received: '%1CLSS=Class 1'  (Optoma)
    #            : Received: '%1CLSS=Version1'  (BenQ)
    if len(data) > 1:
        log.warning(f'({projector.entry.name}) Non-standard CLSS reply: "{data}"')
        # Due to stupid projectors not following standards (Optoma, BenQ comes to mind),
        # AND the different responses that can be received, the semi-permanent way to
        # fix the class reply is to just remove all non-digit characters.
        chk = re.findall(r'\d', data)
        if len(chk) < 1:
            log.warning(f'({projector.entry.name}) No numbers found in class version reply '
                        f'"{data}" - defaulting to class "1"')
            clss = '1'
        else:
            clss = chk[0]  # Should only be the first match
    elif not data.isdigit():
        log.warning(f'({projector.entry.name}) NAN CLSS version reply '
                    f'"{data}" - defaulting to class "1"')
        clss = '1'
    else:
        clss = data
    projector.pjlink_class = clss
    log.debug(f'({projector.entry.name}) Setting pjlink_class for this projector to "{projector.pjlink_class}"')
    if not projector.no_poll:
        # Since we call this one on first connect, setup polling from here
        log.debug(f'({projector.entry.name}) process_pjlink(): Starting timer')
        projector.poll_timer.setInterval(1000)  # Set 1 second for initial information
        projector.poll_timer.start()


_pjlink_functions['CLSS'] = process_clss


def process_erst(projector, data):
    """
    Error status. See PJLink Specifications for format.
    Updates projector.projector_errors

    :param projector: Projector instance
    :param data: Error status
    """
    if len(data) != PJLINK_ERST_DATA['DATA_LENGTH']:
        count = PJLINK_ERST_DATA['DATA_LENGTH']
        log.warning(f'({projector.entry.name}) Invalid error status response "{data}": length != {count}')
        return
    if not data.isnumeric():
        # Bad data - ignore
        log.warning(f'({projector.entry.name}) Invalid error status response "{data}"')
        return
    if int(data) == 0:
        projector.projector_errors = None
        # No errors
        return
    # We have some sort of status error, so check out what it/they are
    projector.projector_errors = {}
    fan, lamp, temp, cover, filt, other = (data[PJLINK_ERST_DATA['FAN']],
                                           data[PJLINK_ERST_DATA['LAMP']],
                                           data[PJLINK_ERST_DATA['TEMP']],
                                           data[PJLINK_ERST_DATA['COVER']],
                                           data[PJLINK_ERST_DATA['FILTER']],
                                           data[PJLINK_ERST_DATA['OTHER']])
    if fan != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['FAN']] = PJLINK_ERST_STATUS[fan]
    if lamp != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['LAMP']] = PJLINK_ERST_STATUS[lamp]
    if temp != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['TEMP']] = PJLINK_ERST_STATUS[temp]
    if cover != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['COVER']] = PJLINK_ERST_STATUS[cover]
    if filt != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['FILTER']] = PJLINK_ERST_STATUS[filt]
    if other != PJLINK_ERST_STATUS[S_OK]:
        projector.projector_errors[PJLINK_ERST_LIST['OTHER']] = PJLINK_ERST_STATUS[other]
    return


_pjlink_functions['ERST'] = process_erst


def process_inf1(projector, data):
    """
    Manufacturer name set in projector.
    Updates projector.manufacturer

    :param projector: Projector instance
    :param data: Projector manufacturer
    """
    projector.manufacturer = data
    log.debug(f'({projector.entry.name}) Setting projector manufacturer data to "{projector.manufacturer}"')
    return


_pjlink_functions['INF1'] = process_inf1


def process_inf2(projector, data):
    """
    Projector Model set in projector.
    Updates projector.model.

    :param projector: Projector instance
    :param data: Model name
    """
    projector.model = data
    log.debug(f'({projector.entry.name}) Setting projector model to "{projector.model}"')
    return


_pjlink_functions['INF2'] = process_inf2


def process_info(projector, data):
    """
    Any extra info set in projector.
    Updates projector.other_info.

    :param projector: Projector instance
    :param data: Projector other info
    """
    projector.other_info = data
    log.debug(f'({projector.entry.name}) Setting projector other_info to "{projector.other_info}"')
    return


_pjlink_functions['INFO'] = process_info


def process_inpt(projector, data):
    """
    Current source input selected. See PJLink specification for format.
    Update projector.source

    :param projector: Projector instance
    :param data: Currently selected source
    """
    # First, see if we have a valid input based on what is installed (if available)
    if projector.source_available is not None:
        # We have available inputs, so verify it's in the list
        if data not in projector.source_available:
            log.warning(f'({projector.entry.name}) Input source not listed in available sources - ignoring')
            return
    elif data not in PJLINK_DEFAULT_CODES:
        # Hmm - no sources available yet, so check with PJLink defaults
        log.warning(f'({projector.entry.name}) Input source not listed as a PJLink valid source - ignoring')
        return
    projector.source = data
    log.debug(f'({projector.entry.name}) Setting current source to "{projector.source}"')
    return


_pjlink_functions['INPT'] = process_inpt


def process_inst(projector, data):
    """
    Available source inputs. See PJLink specification for format.
    Updates projector.source_available

    :param projector: Projector instance
    :param data: Sources list
    """
    sources = []
    check = data.split()
    for source in check:
        sources.append(source)
    sources.sort()
    projector.source_available = sources
    log.debug(f'({projector.entry.name}) Setting projector source_available to "{projector.source_available}"')
    projector.projectorUpdateIcons.emit()
    return


_pjlink_functions['INST'] = process_inst


def process_lamp(projector, data):
    """
    Lamp(s) status. See PJLink Specifications for format.
    Data may have more than 1 lamp to process.
    Update projector.lamp dictionary with lamp status.

    :param projector: Projector instance
    :param data: Lamp(s) status.
    """
    lamps = []
    lamp_list = data.split()
    if len(lamp_list) < 2:
        # Invalid data - not enough information
        log.warning(f'({projector.entry.name}) process_lamp(): Invalid data "{data}" - Missing data')
        return
    else:
        while lamp_list:
            if not lamp_list[0].isnumeric() or not lamp_list[1].isnumeric():
                # Invalid data - we'll ignore the rest for now
                log.warning(f'({projector.entry.name}) process_lamp(): Invalid data "{data}"')
                return
            fill = {'Hours': int(lamp_list[0]), 'On': False if lamp_list[1] == '0' else True}
            lamps.append(fill)
            lamp_list.pop(0)  # Remove lamp hours
            lamp_list.pop(0)  # Remove lamp on/off
    projector.lamp = lamps
    return


_pjlink_functions['LAMP'] = process_lamp


def _process_lkup(projector, data):
    """
    Process UDP request indicating remote is available for connection

    :param projector: Projector instance
    :param data: Data packet from remote
    """
    log.debug(f'({projector.entry.name}) Processing LKUP command')
    if Registry().get('settings').value('projector/connect when LKUP received'):
        projector.connect_to_host()


_pjlink_functions['LKUP'] = _process_lkup


def process_name(projector, data):
    """
    Projector name set in projector.
    Updates projector.pjlink_name

    :param projector: Projector instance
    :param data: Projector name
    """
    projector.pjlink_name = data
    log.debug(f'({projector.entry.name}) Setting projector PJLink name to "{projector.pjlink_name}"')
    return


_pjlink_functions['NAME'] = process_name


def process_pjlink(projector, data):
    """
    Process initial socket connection to terminal.

    :param projector: Projector instance
    :param data: Initial packet with authentication scheme
    """
    log.debug(f'({projector.entry.name}) Processing PJLINK command')
    chk = data.split(' ')
    if (len(chk[0]) != 1) or (chk[0] not in ('0', '1')):
        # Invalid - after splitting, first field should be 1 character, either '0' or '1' only
        log.error(f'({projector.entry.name}) Invalid initial authentication scheme - aborting')
        return E_AUTHENTICATION
    elif chk[0] == '0':
        # Normal connection no authentication
        if len(chk) > 1:
            # Invalid data - there should be nothing after a normal authentication scheme
            log.error(f'({projector.entry.name}) Normal connection with extra information - aborting')
            return E_NO_AUTHENTICATION
        elif projector.pin:
            log.error(f'({projector.entry.name}) Normal connection but PIN set - aborting')
            return E_NO_AUTHENTICATION
        log.debug(f'({projector.entry.name}) PJLINK: Returning S_CONNECT')
        return S_CONNECT
    elif chk[0] == '1':
        if len(chk) < 2:
            # Not enough information for authenticated connection
            log.error(f'({projector.entry.name}) Authenticated connection but not enough info - aborting')
            return E_NO_AUTHENTICATION
        elif len(chk[-1]) != PJLINK_TOKEN_SIZE:
            # Bad token - incorrect size
            log.error(f'({projector.entry.name}) Authentication token invalid (size) - aborting')
            return E_NO_AUTHENTICATION
        elif not all(c in string.hexdigits for c in chk[-1]):
            # Bad token - not hexadecimal
            log.error(f'({projector.entry.name}) Authentication token invalid (not a hexadecimal number) - aborting')
            return E_NO_AUTHENTICATION
        elif not projector.pin:
            log.error(f'({projector.entry.name}) Authenticate connection but no PIN - aborting')
            return E_NO_AUTHENTICATION
        log.debug(f'({projector.entry.name}) PJLINK: Returning S_AUTHENTICATE')
        return S_AUTHENTICATE


_pjlink_functions['PJLINK'] = process_pjlink


def process_powr(projector, data):
    """
    Power status. See PJLink specification for format.
    Update projector.power with status. Update icons if change from previous setting.

    :param projector: Projector instance
    :param data: Power status
    """
    log.debug(f'({projector.entry.name}) Processing POWR command')
    if data not in PJLINK_POWR_STATUS:
        # Log unknown status response
        log.warning(f'({projector.entry.name}) Unknown power response: "{data}"')
        return

    power = PJLINK_POWR_STATUS[data]
    if projector.power != power:
        projector.power = power
        projector.change_status(PJLINK_POWR_STATUS[data])
        projector.projectorUpdateIcons.emit()
        if power == S_ON:
            # Input sources list should only be available after power on, so update here
            projector.send_command('INST')

    if projector.power in [S_ON, S_STANDBY, S_OFF]:
        projector.status_timer_delete(cmd='POWR')
    return


_pjlink_functions['POWR'] = process_powr


def process_rfil(projector, data):
    """
    Process replacement filter type

    :param projector: Projector instance
    :param data: Filter replacement model number
    """
    if projector.model_filter is None:
        projector.model_filter = data
    else:
        log.warning(f'({projector.entry.name}) Filter model already set')
        log.warning(f'({projector.entry.name}) Saved model: "{projector.model_filter}"')
        log.warning(f'({projector.entry.name}) New model: "{data}"')


_pjlink_functions['RFIL'] = process_rfil


def process_rlmp(projector, data):
    """
    Process replacement lamp type

    :param projector: Projector instance
    :param data: Lamp replacement model number
    """
    if projector.model_lamp is None:
        projector.model_lamp = data
    else:
        log.warning(f'({projector.entry.name}) Lamp model already set')
        log.warning(f'({projector.entry.name}) Saved lamp: "{projector.model_lamp}"')
        log.warning(f'({projector.entry.name}) New lamp: "{data}"')


_pjlink_functions['RLMP'] = process_rlmp


def process_snum(projector, data):
    """
    Serial number of projector.

    :param projector: Projector instance
    :param data: Serial number from projector.
    """
    if projector.serial_no is None:
        log.debug(f'({projector.entry.name}) Setting projector serial number to "{data}"')
        projector.serial_no = data
        projector.db_update = False
        return

    # Compare serial numbers and see if we got the same projector
    if projector.serial_no != data:
        log.warning(f'({projector.entry.name}) Projector serial number does not match saved serial number')
        log.warning(f'({projector.entry.name}) Saved:    "{projector.serial_no}"')
        log.warning(f'({projector.entry.name}) Received: "{data}"')
        log.warning(f'({projector.entry.name}) NOT saving serial number')
        projector.serial_no_received = data


_pjlink_functions['SNUM'] = process_snum


def _process_srch(projector=None, data=None):
    """
    Process the SRCH command.

    SRCH is processed by terminals so we ignore any packet.

    UDP command to find active CLSS 2 projectors. Reply is ACKN.

    :param projector: Projector instance (actually ignored for this command)
    :param data: Data in packet
    """
    msg = 'SRCH packet detected - ignoring'
    name = ''
    if projector is not None:
        name = f'({projector.entry.name}) '
    log.warning(f'{name}{msg}')


_pjlink_functions['SRCH'] = _process_srch


def _process_sver(projector, data):
    """
    Software version of projector

    :param projector: Projector instance
    :param data: Software version of projector
    """
    if len(data) > PJLINK_SVER_MAX_LEN:
        # Defined in specs 0-32 characters max
        log.warning(f'({projector.name}) Invalid software version - too long')
        return
    elif projector.sw_version == data:
        log.debug(f'({projector.name}) Software version unchanged - returning')
        return
    elif projector.sw_version is not None:
        log.debug(f'({projector.name}) Old software version "{projector.sw_version}"')
        log.debug(f'({projector.name}) New software version "{data}"')

    # Software version changed - save
    log.debug(f'({projector.entry.name}) Setting projector software version to "{data}"')
    projector.sw_version = data
    projector.db_update = True


_pjlink_functions['SVER'] = _process_sver
