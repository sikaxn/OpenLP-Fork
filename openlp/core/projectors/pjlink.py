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
The :mod:`openlp.core.lib.projector.pjlink` module provides the necessary functions for connecting to a PJLink-capable
projector.

PJLink Class 1 Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Website: http://pjlink.jbmia.or.jp/english/dl_class1.html

- Section 5-1 PJLink Specifications
- Section 5-5 Guidelines for Input Terminals

PJLink Class 2 Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Website: http://pjlink.jbmia.or.jp/english/dl_class2.html

- Section 5-1 PJLink Specifications
- Section 5-5 Guidelines for Input Terminals

.. note:
    Function names follow the following syntax::

        def process_CCCC(...):

    where ``CCCC`` is the PJLink command being processed
"""
import logging
from codecs import decode
from copy import copy

from PySide6 import QtCore, QtNetwork

from openlp.core.common import qmd5_hash
from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import CONNECTION_ERRORS, E_AUTHENTICATION, E_CONNECTION_REFUSED, E_GENERAL, \
    E_NETWORK, E_NOT_CONNECTED, E_SOCKET_TIMEOUT, PJLINK_CLASS, \
    PJLINK_MAX_PACKET, PJLINK_PORT, PJLINK_PREFIX, PJLINK_SUFFIX, \
    PJLINK_VALID_CMD, PROJECTOR_STATE, QSOCKET_STATE, S_AUTHENTICATE, S_CONNECT, S_CONNECTED, S_CONNECTING, \
    S_DATA_OK, S_NOT_CONNECTED, S_OFF, S_OK, S_ON, STATUS_CODE, STATUS_MSG


log = logging.getLogger(__name__)
log.debug('pjlink loaded')

__all__ = ['PJLink', 'PJLinkUDP']

# Shortcuts
SocketError = QtNetwork.QAbstractSocket.SocketError
SocketSTate = QtNetwork.QAbstractSocket.SocketState

# Add prefix here, but defer linkclass expansion until later when we have the actual
# PJLink class for the command
PJLINK_HEADER = f'{PJLINK_PREFIX}{{linkclass}}'


class PJLinkUDP(QtNetwork.QUdpSocket):
    """
    Socket service for PJLink UDP socket.
    """

    data_received = QtCore.Signal(QtNetwork.QHostAddress, int, str, name='udp_data')  # host, port, data

    def __init__(self, port=PJLINK_PORT):
        """
        Socket services for PJLink UDP packets.

        Since all UDP packets from any projector will come into the same
        port, process UDP packets here then route to the appropriate
        projector instance as needed.

        :param port:  UDP port to listen on
        """
        super().__init__()
        self.port = port
        # Local defines
        self.search_active = False
        self.search_time = 30000  # 30 seconds for allowed time
        self.search_timer = QtCore.QTimer()
        self.udp_broadcast_listen_setting = False
        self.settings = Registry().get('settings')
        log.debug(f'(UDP:{self.port}) PJLinkUDP() Initialized')
        if self.settings.value('projector/udp broadcast listen'):
            self.udp_start()

    def udp_start(self):
        """
        Start listening on UDP port
        """
        log.debug(f'(UDP:{self.port}) Start called')
        self.readyRead.connect(self.get_datagram)
        self.check_settings(checked=self.settings.value('projector/udp broadcast listen'))

    def udp_stop(self):
        """
        Stop listening on UDP port
        """
        log.debug(f'(UDP:{self.port}) Stopping listener')
        self.close()
        self.readyRead.disconnect(self.get_datagram)

    @QtCore.Slot()
    def get_datagram(self):
        """
        Retrieve packet and basic checks
        """
        log.debug(f'(UDP:{self.port}) get_datagram() - Receiving data')
        read_size = self.pendingDatagramSize()
        if -1 == read_size:
            log.warning(f'(UDP:{self.port}) No data (-1)')
            return
        elif 0 == read_size:
            log.warning(f'(UDP:{self.port}) get_datagram() called when pending data size is 0')
            return
        elif read_size > PJLINK_MAX_PACKET:
            log.warning(f'(UDP:{self.port}) UDP Packet too large ({read_size} bytes)- ignoring')
            return
        data_in, peer_host, peer_port = self.readDatagram(read_size)
        data = data_in.decode('utf-8') if isinstance(data_in, bytes) else data_in
        log.debug(f'(UDP:{self.port}) {len(data)} bytes received from {peer_host.toString()}')
        log.debug(f'(UDP:{self.port}) packet "{data}"')
        log.debug(f'(UDP:{self.port}) Sending data_received signal to projectors')
        self.data_received.emit(peer_host, self.localPort(), data)
        return

    def search_start(self):
        """
        Start search for projectors on local network
        """
        self.search_active = True
        # TODO: Send SRCH packet here
        self.search_timer.singleShot(self.search_time, self.search_stop)

    @QtCore.Slot()
    def search_stop(self):
        """
        Stop search
        """
        self.search_active = False
        self.search_timer.stop()

    def check_settings(self, checked):
        """
        Update UDP listening state based on settings change.
        NOTE: This method is called by projector settings tab and setup/removed by ProjectorManager
        """
        if self.udp_broadcast_listen_setting == checked:
            log.debug(f'(UDP:{self.port}) No change to status - skipping')
            return
        self.udp_broadcast_listen_setting = checked
        if self.udp_broadcast_listen_setting:
            if self.state().value == self.SocketState.ListeningState:
                log.debug(f'(UDP:{self.port}) Already listening - skipping')
                return
            self.bind(self.port)
            log.debug(f'(UDP:{self.port}) Listening')
        else:
            # Close socket
            self.udp_stop()


class PJLink(QtNetwork.QTcpSocket):
    """
    Socket services for PJLink TCP packets.
    """
    # Signals sent by this module
    projectorChangeStatus = QtCore.Signal(str, int, str)
    projectorStatus = QtCore.Signal(int)  # Status update
    projectorAuthentication = QtCore.Signal(str)  # Authentication error
    projectorNoAuthentication = QtCore.Signal(str)  # PIN set and no authentication needed
    projectorReceivedData = QtCore.Signal()  # Notify when received data finished processing
    projectorUpdateIcons = QtCore.Signal()  # Update the status icons on toolbar
    # Deprecated
    changeStatus = projectorChangeStatus  # Use projectorChangeStatus

    def __init__(self, projector, *args, **kwargs):
        """
        Setup for instance.
        Options should be in kwargs except for port which does have a default.

        :param projector: Database record of projector

        Optional parameters
        :param poll_time: Time (in seconds) to poll connected projector
        :param socket_timeout: Time (in seconds) to abort the connection if no response
        """
        log.debug(f'PJLink(projector="{projector}", args="{args}" kwargs="{kwargs}")')
        super().__init__()
        self.settings_section = 'projector'
        self.db = projector
        self.entry = self.db  # Deprecated use self.db
        self.ip = self.entry.ip
        self.qhost = QtNetwork.QHostAddress(self.ip)
        self.location = self.entry.location
        self.mac_adx = self.entry.mac_adx
        self.name = self.entry.name
        self.notes = self.entry.notes
        self.pin = self.entry.pin
        self.port = int(self.entry.port)
        self.pjlink_class = PJLINK_CLASS if self.entry.pjlink_class is None else self.entry.pjlink_class
        self.ackn_list = {}  # Replies from online projectors (Class 2 option)
        self.db_update = False  # Use to check if db needs to be updated prior to exiting
        # Poll time 20 seconds unless called with something else
        self.poll_time = 20000 if 'poll_time' not in kwargs else kwargs['poll_time'] * 1000
        # Socket timeout (in case of brain-dead projectors) 5 seconds unless called with something else
        self.socket_timeout = 5000 if 'socket_timeout' not in kwargs else kwargs['socket_timeout'] * 1000
        # In case we're called from somewhere that only wants information
        self.no_poll = 'no_poll' in kwargs
        self.status_connect = S_NOT_CONNECTED
        self.last_command = ''
        self.projector_status = S_NOT_CONNECTED
        self.error_status = S_OK
        # Socket information
        # Add enough space to input buffer for extraneous \n \r
        self.max_size = PJLINK_MAX_PACKET + 2
        self.setReadBufferSize(self.max_size)
        self.reset_information()
        self.send_queue = []
        self.priority_queue = []
        self.send_busy = False
        # Poll timer for status updates
        self.poll_timer = QtCore.QTimer(self)  # Timer that calls the poll_loop
        self.poll_timer.setInterval(self.poll_time)
        self.poll_timer.timeout.connect(self.poll_loop)
        # Socket timer for some possible brain-dead projectors or network issues
        self.socket_timer = QtCore.QTimer(self)
        self.socket_timer.setInterval(self.socket_timeout)
        self.socket_timer.timeout.connect(self.socket_abort)
        # Timer for doing status updates for commands that change state and should update faster
        self.status_timer_checks = {}  # Keep track of events for the status timer
        self.status_timer = QtCore.QTimer(self)
        self.status_timer.setInterval(2000)  # 2 second interval should be fast enough
        self.status_timer.timeout.connect(self.status_timer_update)
        # Socket status signals
        self.connected.connect(self.check_login)
        self.disconnected.connect(self.disconnect_from_host)
        self.errorOccurred.connect(self.get_error)
        self.projectorReceivedData.connect(self._send_command)

    def reset_information(self):
        """
        Initialize instance variables. Also used to reset projector-specific information to default.
        """
        conn_state = STATUS_CODE[QSOCKET_STATE[self.state().value]]
        log.debug(f'({self.entry.name}) reset_information() connect status is {conn_state}')
        self.fan = None  # ERST
        self.filter_time = None  # FILT
        self.lamp = None  # LAMP
        self.mac_adx_received = None  # ACKN
        self.manufacturer = None  # INF1
        self.model = None  # INF2
        self.model_filter = None  # RFIL
        self.model_lamp = None  # RLMP
        self.mute = None  # AVMT
        self.other_info = None  # INFO
        self.pjlink_class = copy(PJLINK_CLASS)
        self.pjlink_name = None  # NAME
        self.power = S_OFF  # POWR
        self.projector_errors = {}  # Full ERST errors
        self.serial_no = None  # SNUM
        self.serial_no_received = None
        self.sw_version = None  # SVER
        self.sw_version_received = None
        self.shutter = None  # AVMT
        self.source_available = None  # INST
        self.source = None  # INPT
        # These should be part of PJLink() class, but set here for convenience
        if hasattr(self, 'poll_timer'):
            log.debug(f'({self.entry.name}): Calling poll_timer.stop()')
            self.poll_timer.stop()
        if hasattr(self, 'socket_timer'):
            log.debug(f'({self.entry.name}): Calling socket_timer.stop()')
            self.socket_timer.stop()
        if hasattr(self, 'status_timer'):
            log.debug(f'({self.entry.name}): Calling status_timer.stop()')
            self.status_timer.stop()
        self.status_timer_checks = {}
        self.send_busy = False
        self.send_queue = []
        self.priority_queue = []

    def socket_abort(self):
        """
        Aborts connection and closes socket in case of brain-dead projectors.
        Should normally be called by socket_timer().
        """
        log.debug(f'({self.entry.name}) socket_abort() - Killing connection')
        self.disconnect_from_host(abort=True)

    def poll_loop(self):
        """
        Retrieve information from projector that changes.
        Normally called by timer().
        """
        if QSOCKET_STATE[self.state()] != S_CONNECTED:
            log.warning(f'({self.entry.name}) poll_loop(): Not connected - returning')
            # Stop timer just in case it's missed elsewhere
            self.poll_timer.stop()
            return
        log.debug(f'({self.entry.name}) poll_loop(): Updating projector status')
        # The following commands do not change, so only check them once
        # Call them first in case other functions rely on something here
        if self.power == S_ON and self.source_available is None:
            self.send_command('INST')
        if self.other_info is None:
            self.send_command('INFO')
        if self.manufacturer is None:
            self.send_command('INF1')
        if self.model is None:
            self.send_command('INF2')
        if self.pjlink_name is None:
            self.send_command('NAME')
        if self.pjlink_class == '2':
            # Class 2 specific checks
            if self.serial_no is None:
                self.send_command('SNUM')
            if self.sw_version is None:
                self.send_command('SVER')
            if self.model_filter is None:
                self.send_command('RFIL')
            if self.model_lamp is None:
                self.send_command('RLMP')
        # These commands may change during connection
        check_list = ['POWR', 'ERST', 'LAMP', 'AVMT', 'INPT']
        if self.pjlink_class == '2':
            check_list.extend(['FILT', 'FREZ'])
        for command in check_list:
            self.send_command(command)
        # Reset the poll_timer for normal operations in case of initial connection
        self.poll_timer.setInterval(self.poll_time)

    def _get_status(self, status):
        """
        Helper to retrieve status/error codes and convert to strings.

        :param status: Status/Error code
        :returns: tuple (-1 if code not INT, None)
        :returns: tuple (string: code as string, None if no description)
        :returns: tuple (string: code as string, string: Status/Error description)
        """
        if not isinstance(status, int):
            return -1, None
        elif status not in STATUS_MSG:
            return None, None
        else:
            return STATUS_CODE[status], STATUS_MSG[status]

    def change_status(self, status, msg=None):
        """
        Check connection/error status, set status for projector, then emit status change signal
        for gui to allow changing the icons.

        :param status: Status code
        :param msg: Optional message
        """
        if status in STATUS_CODE:
            log.debug(f'({self.entry.name}) Changing status to {STATUS_CODE[status]} '
                      f'"{STATUS_MSG[status] if msg is None else msg}"')
        else:
            log.warning(f'({self.entry.name}) Unknown status change code: {status}')
            return
        if status in CONNECTION_ERRORS:
            # Connection state error affects both socket and projector
            self.error_status = status
            self.status_connect = E_NOT_CONNECTED
        elif status >= S_NOT_CONNECTED and status in QSOCKET_STATE:
            # Socket connection status update
            self.status_connect = status
            # Check if we need to update error state as well
            if self.error_status != S_OK and status != S_NOT_CONNECTED:
                self.error_status = S_OK
        elif status >= S_NOT_CONNECTED and status in PROJECTOR_STATE:
            # Only affects the projector status
            self.projector_status = status

        # These log entries are for troubleshooting only
        (status_code, status_message) = self._get_status(self.status_connect)
        log.debug(f'({self.entry.name}) status_connect: {status_code}: "{status_message if msg is None else msg}"')
        (status_code, status_message) = self._get_status(self.projector_status)
        log.debug(f'({self.entry.name}) projector_status: {status_code}: "{status_message if msg is None else msg}"')
        (status_code, status_message) = self._get_status(self.error_status)
        log.debug(f'({self.entry.name}) error_status: {status_code}: "{status_message if msg is None else msg}"')

        # Now that we logged extra information for debugging, broadcast the original change/message
        # Check for connection errors first
        if self.error_status != S_OK:
            log.debug(f'({self.entry.name}) Signalling error code')
            code, message = self._get_status(self.error_status)
            status = self.error_status
        else:
            log.debug(f'({self.entry.name}) Signalling status code')
            code, message = self._get_status(status)
        if msg is not None:
            message = msg
        elif message is None:
            # No message for status code
            message = translate('OpenLP.PJLink', 'No message') if msg is None else msg

        self.changeStatus.emit(self.ip, status, message)
        self.projectorUpdateIcons.emit()

    @QtCore.Slot()
    def check_login(self, data=None):
        """
        Processes the initial connection and convert to a PJLink packet if valid initial connection

        :param data: Optional data if called from another routine
        """
        log.debug(f'({self.entry.name}) check_login(data="{data}")')
        if data is None:
            # Reconnected setup?
            log.debug(f'({self.name}) check_login() Waiting for readyRead()')
            _chk = self.waitForReadyRead(2000)  # 2 seconds should be plenty of time
            if not _chk:
                # Possible timeout issue
                log.error(f'({self.entry.name}) Socket timeout waiting for login')
                self.change_status(E_SOCKET_TIMEOUT)
                return
            log.debug(f'({self.name}) check_login() Checking for data')
            data = self.readLine(self.max_size)
            if data is None:
                log.warning(f'({self.entry.name}) read is None - socket error?')
                return
            elif len(data) < 8:
                log.warning(f'({self.entry.name}) Not enough data read - skipping')
                return
            # Possibility of extraneous data on input when reading.
            # Clean out extraneous characters in buffer.
            _ = self.read(1024)
            log.debug(f'({self.entry.name}) check_login() read "{data.strip()}"')
        # At this point, we should only have the initial login prompt with
        # possible authentication
        # PJLink initial login will be:
        # 'PJLink 0' - Unauthenticated login - no extra steps required.
        # 'PJLink 1 XXXXXX' Authenticated login - extra processing required.
        if type(data) is bytes:
            data = decode(data, 'utf-8')
        if not data.upper().startswith('PJLINK'):
            # Invalid initial packet - close socket
            log.error(f'({self.entry.name}) Invalid initial packet received - closing socket')
            return self.disconnect_from_host()
        # Convert the initial login prompt with the expected PJLink normal command format for processing
        log.debug(f'({self.entry.name}) check_login(): Formatting initial connection prompt to PJLink packet')
        return self.get_data(f'{PJLINK_PREFIX}1{data.replace(" ", "=", 1)}'.strip())

    def _trash_buffer(self, msg=None):
        """
        Clean out extraneous stuff in the buffer.
        """
        log.debug(f'({self.entry.name}) Cleaning buffer - msg = "{msg}"')
        if msg is None:
            msg = 'Invalid packet'
        log.warning(f'({self.entry.name}) {msg}')
        self.send_busy = False
        trash_count = 0
        while self.bytesAvailable() > 0:
            trash = self.read(self.max_size)
            trash_count += len(trash)
        log.debug(f'({self.entry.name}) Finished cleaning buffer - {trash_count} bytes dropped')
        return

    @QtCore.Slot(QtNetwork.QHostAddress, int, str, name='udp_data')  # host, port, data
    def get_buffer(self, host, port, data):
        """
        Get data from somewhere other than TCP socket

        :param host:  QHostAddress of sender
        :param port:  Destination port
        :param data:  Data to process. buffer must be formatted as a proper PJLink packet.
        """
        if (port == int(self.port)) and (host.isEqual(self.qhost)):
            log.debug(f'({self.entry.name}) Received data from {host.toString()}')
            log.debug(f'({self.entry.name}) get_buffer(data="{data}")')
            return self.get_data(buff=data)
        else:
            log.debug(f'({self.entry.name}) Ignoring data for {host.toString()} - not me')

    @QtCore.Slot()
    def get_socket(self):
        """
        Get data from TCP socket.
        """
        log.debug(f'({self.entry.name}) get_socket(): Reading data')
        if QSOCKET_STATE[self.state()] != S_CONNECTED:
            log.debug(f'({self.entry.name}) get_socket(): Not connected - returning')
            self.send_busy = False
            return
        # Although we have a packet length limit, go ahead and use a larger buffer
        self.socket_timer.start()
        while self.bytesAvailable() >= 1:
            data = self.readLine(1024)
            data = data.strip()
            if not data:
                log.warning(f'({self.entry.name}) get_socket(): Ignoring empty packet')
                if self.bytesAvailable() < 1:
                    break

        self.socket_timer.stop()
        if data:
            log.debug(f'({self.entry.name}) get_socket(): "{data}"')
        if data == -1:
            # No data available
            log.debug(f'({self.entry.namee}) get_socket(): No data available (-1)')
            return
        return self.get_data(buff=data)

    def get_data(self, buff, *args, **kwargs):
        """
        Process received data

        :param buff:    Data to process.
        """
        log.debug(f'({self.entry.name}) get_data(buffer="{buff}"')
        ignore_class = False if 'ignore_class' not in kwargs else kwargs['ignore_class']
        log.debug(f'({self.entry.name}) Setting ignore_class to "{ignore_class}"')
        # NOTE: Class2 has changed to some values being UTF-8
        if type(buff) is bytes:
            data = decode(buff, 'utf-8')
        else:
            data = buff
        data = data.strip()
        self.receive_data_signal()
        # Initial packet checks
        if len(data) < 7:
            self._trash_buffer(msg='get_data(): Invalid packet - length')
            return
        elif len(data) > self.max_size:
            self._trash_buffer(msg=f'get_data(): Invalid packet - too long ({len(data)} bytes)')
            return
        elif not data.startswith(PJLINK_PREFIX):
            self._trash_buffer(msg='get_data(): Invalid packet - PJLink prefix missing')
            return
        elif data[6] != '=' and data[8] != '=':
            # data[6] = standard command packet
            # data[8] = initial PJLink connection (after mangling)
            self._trash_buffer(msg='get_data(): Invalid reply - Does not have "="')
            return
        log.debug(f'({self.entry.name}) get_data(): Checking new data "{data}"')
        header, data = data.split('=')
        log.debug(f'({self.entry.name}) get_data() header="{header}" data="{data}"')
        # At this point, the header should contain:
        #   "PVCCCC"
        #   Where:
        #       P = PJLINK_PREFIX
        #       V = PJLink class or version
        #       C = PJLink command
        version, cmd = header[1], header[2:].upper()
        log.debug(f'({self.entry.name}) get_data() version="{version}" cmd="{cmd}" data="{data}"')
        if cmd not in PJLINK_VALID_CMD:
            self._trash_buffer(msg=f'get_data(): Invalid packet - unknown command "{cmd}"')
            return
        elif version not in PJLINK_VALID_CMD[cmd]['version']:
            self._trash_buffer(msg='get_data() Command reply version does not match a valid command version')
            return
        elif int(self.pjlink_class) < int(version):
            log.warning(f'({self.entry.name}) get_data(): pjlink_class={self.pjlink_class} packet={version}')
            if not ignore_class:
                log.warning(f'({self.entry.name}) get_data(): Projector returned class reply higher '
                            'than projector stated class')
                return

        chk = process_command(self, cmd, data)
        if chk is None:
            # Command processed normally and not initial connection, so skip other checks
            return
        # PJLink initial connection checks
        elif chk == S_DATA_OK:
            # Previous command returned OK - resend command to retrieve status
            log.debug(f'({self.entry.name}) OK returned - resending command')
            self.send_command(cmd=cmd, priority=True)
        elif chk == S_CONNECT:
            # Normal connection
            log.debug(f'({self.entry.name}) Connecting normal')
            self.change_status(S_CONNECTED)
            self.send_command(cmd='CLSS', priority=True)
            self.readyRead.connect(self.get_socket)
        elif chk == S_AUTHENTICATE:
            # Connection with pin
            log.debug(f'({self.entry.name}) Connecting with pin')
            data_hash = str(qmd5_hash(salt=data.split()[1].encode('utf-8'),
                                      data=self.pin.encode('utf-8')),
                            encoding='ascii')
            self.change_status(S_CONNECTED)
            self.readyRead.connect(self.get_socket)
            self.send_command(cmd='CLSS', salt=data_hash, priority=True)
        elif chk == E_AUTHENTICATION:
            # Projector did not like our pin
            log.warning(f'({self.entry.name}) Failed authentication - disconnecting')
            self.disconnect_from_host()
            self.projectorAuthentication.emit(self.entry.name)
            self.change_status(status=E_AUTHENTICATION)

        return

    @QtCore.Slot(QtNetwork.QAbstractSocket.SocketError)
    def get_error(self, err):
        """
        Process error from SocketError signal.
        Remaps system error codes to projector error codes.

        :param err: Error code
        """
        log.debug(f'({self.entry.name}) get_error(err={err}): {self.errorString()}')
        if err <= 18:
            # QSocket errors. Redefined in projector.constants so we don't mistake
            # them for system errors
            check = err + E_CONNECTION_REFUSED
            self.poll_timer.stop()
        else:
            check = err
        if check < E_GENERAL:
            # Some system error?
            self.change_status(err, self.errorString())
        else:
            self.change_status(E_NETWORK, self.errorString())
        self.projectorUpdateIcons.emit()
        if self.status_connect == E_NOT_CONNECTED:
            self.abort()
            self.reset_information()
        return

    def send_command(self, cmd, opts='?', salt=None, priority=False):
        """
        Add command to output queue if not already in queue.

        :param cmd: Command to send
        :param opts: Command option (if any) - defaults to '?' (get information)
        :param salt: Optional  salt for md5 hash initial authentication
        :param priority: Option to send packet now rather than queue it up
        """
        log.debug(f'({self.entry.name}) send_command(cmd="{cmd}" opts="{opts}" salt="{salt}" priority={priority}')
        if QSOCKET_STATE[self.state()] != S_CONNECTED:
            log.warning(f'({self.entry.name}) send_command(): Not connected - returning')
            return self.reset_information()
        if cmd not in PJLINK_VALID_CMD:
            log.error(f'({self.entry.name}) send_command(): Invalid command requested - ignoring.')
            if self.priority_queue or self.send_queue:
                # Just in case there's already something to send
                return self._send_command()
            return
        log.debug(f'({self.entry.name}) send_command(): Building cmd="{cmd}" opts="{opts}" '
                  f'{"" if salt is None else "with hash"}')
        # Until we absolutely have to start doing version checks, use the default
        # for PJLink class
        header = PJLINK_HEADER.format(linkclass=PJLINK_VALID_CMD[cmd]['default'])
        out = f'{"" if salt is None else salt}{header}{cmd} {opts}{PJLINK_SUFFIX}'
        if out in self.priority_queue:
            log.warning(f'({self.entry.name}) send_command(): Already in priority queue - skipping')
        elif out in self.send_queue:
            log.warning(f'({self.entry.name}) send_command(): Already in normal queue - skipping')
        else:
            if priority:
                log.debug(f'({self.entry.name}) send_command(): Adding to priority queue')
                self.priority_queue.append(out)
            else:
                log.debug(f'({self.entry.name}) send_command(): Adding to normal queue')
                self.send_queue.append(out)
        if self.priority_queue or self.send_queue:
            # May be some initial connection setup so make sure we send data
            self._send_command()

    @QtCore.Slot()
    def _send_command(self, data=None, utf8=False):
        """
        Socket interface to send data. If data=None, then check queue.

        :param data: Immediate data to send (Optional)
        :param utf8: Send as UTF-8 string otherwise send as ASCII string
        """
        if not data and not self.priority_queue and not self.send_queue:
            log.warning(f'({self.entry.name}) _send_command(): Nothing to send - returning')
            self.send_busy = False
            return
        log.debug(f'({self.entry.name}) _send_command(data="{data if not data else data.strip()}")')
        log.debug(f'({self.entry.name}) _send_command(): priority_queue: {self.priority_queue}')
        log.debug(f'({self.entry.name}) _send_command(): send_queue: {self.send_queue}')
        conn_state = STATUS_CODE[QSOCKET_STATE[self.state()]]
        log.debug(f'({self.entry.name}) _send_command(): Connection status: {conn_state}')
        if QSOCKET_STATE[self.state()] != S_CONNECTED:
            log.warning(f'({self.entry.name}) _send_command() Not connected - abort')
            self.send_busy = False
            return self.disconnect_from_host()
        if data and data not in self.priority_queue:
            log.debug(f'({self.entry.name}) _send_command(): Priority packet - adding to priority queue')
            self.priority_queue.append(data)

        if self.send_busy:
            # Still waiting for response from last command sent
            log.debug(f'({self.entry.name}) _send_command(): Still busy, returning')
            log.debug(f'({self.entry.name}) _send_command(): Priority queue = {self.priority_queue}')
            log.debug(f'({self.entry.name}) _send_command(): Normal queue = {self.send_queue}')
            return

        if not self.priority_queue and not self.send_queue:
            # No data to send
            log.warning(f'({self.entry.name}) _send_command(): No data to send')
            self.send_busy = False
            return
        elif self.priority_queue:
            out = self.priority_queue.pop(0)
            log.debug(f'({self.entry.name}) _send_command(): Getting priority queued packet')
        elif self.send_queue:
            out = self.send_queue.pop(0)
            log.debug(f'({self.entry.name}) _send_command(): Getting normal queued packet')
        self.send_busy = True
        log.debug(f'({self.entry.name}) _send_command(): Sending "{out.strip()}"')
        self.socket_timer.start()
        sent = self.write(out.encode(f'{"utf-8" if utf8 else "ascii"}'))
        self.waitForBytesWritten(2000)  # 2 seconds should be enough
        if sent == -1:
            # Network error?
            self.change_status(E_NETWORK,
                               translate('OpenLP.PJLink', 'Error while sending data to projector'))
            log.warning(f'({self.entry.name}) _send_command(): -1 received - disconnecting from host')
            self.disconnect_from_host()

    def connect_to_host(self):
        """
        Initiate connection to projector.
        """
        log.debug(f'({self.entry.name}) connect_to_host(): Starting connection')
        if QSOCKET_STATE[self.state()] == S_CONNECTED:
            log.warning(f'({self.entry.name}) connect_to_host(): Already connected - returning')
            return
        self.error_status = S_OK
        self.change_status(S_CONNECTING)
        self.connectToHost(self.ip, self.port)

    @QtCore.Slot()
    def disconnect_from_host(self, abort=False):
        """
        Close socket and cleanup.
        """
        if abort or QSOCKET_STATE[self.state()] != S_NOT_CONNECTED:
            if abort:
                log.warning(f'({self.entry.name}) disconnect_from_host(): Aborting connection')
                self.abort()
            else:
                log.warning(f'({self.entry.name}) disconnect_from_host(): Not connected')
        try:
            self.readyRead.disconnect(self.get_socket)
        except TypeError:
            # Since we already know what's happening, just log it for reference.
            log.debug(f'({self.entry.name}) disconnect_from_host(): Issue detected with readyRead.disconnect')
        log.debug(f'({self.entry.name}) disconnect_from_host(): '
                  f'Current status {self._get_status(self.status_connect)[0]}')
        self.disconnectFromHost()
        if abort:
            self.change_status(E_NOT_CONNECTED)
        else:
            self.change_status(S_NOT_CONNECTED)
        self.reset_information()

    def get_av_mute_status(self, priority=False):
        """
        Send command to retrieve shutter status.
        """
        log.debug(f'({self.entry.name}) Sending AVMT command')
        return self.send_command(cmd='AVMT', priority=priority)

    def get_available_inputs(self):
        """
        Send command to retrieve available source inputs.
        """
        log.debug(f'({self.entry.name}) Sending INST command')
        return self.send_command(cmd='INST')

    def get_error_status(self):
        """
        Send command to retrieve currently known errors.
        """
        log.debug(f'({self.entry.name}) Sending ERST command')
        return self.send_command(cmd='ERST')

    def get_input_source(self):
        """
        Send command to retrieve currently selected source input.
        """
        log.debug(f'({self.entry.name}) Sending INPT command')
        return self.send_command(cmd='INPT')

    def get_lamp_status(self):
        """
        Send command to return the lap status.
        """
        log.debug(f'({self.entry.name}) Sending LAMP command')
        return self.send_command(cmd='LAMP')

    def get_manufacturer(self):
        """
        Send command to retrieve manufacturer name.
        """
        log.debug(f'({self.entry.name}) Sending INF1 command')
        return self.send_command(cmd='INF1')

    def get_model(self):
        """
        Send command to retrieve the model name.
        """
        log.debug(f'({self.entry.name}) Sending INF2 command')
        return self.send_command(cmd='INF2')

    def get_name(self):
        """
        Send command to retrieve name as set by end-user (if set).
        """
        log.debug(f'({self.entry.name}) Sending NAME command')
        return self.send_command(cmd='NAME')

    def get_other_info(self):
        """
        Send command to retrieve extra info set by manufacturer.
        """
        log.debug(f'({self.entry.name}) Sending INFO command')
        return self.send_command(cmd='INFO')

    def get_power_status(self, priority=False):
        """
        Send command to retrieve power status.

        :param priority: (OPTIONAL) Send in priority queue
        """
        log.debug(f'({self.entry.name}) Sending POWR command')
        return self.send_command(cmd='POWR', priority=priority)

    def set_audio_mute(self, priority=False):
        """
        Send command to set audio to muted
        """
        log.debug(f'({self.entry.name}) Setting AVMT to 21 (audio mute)')
        self.send_command(cmd='AVMT', opts='21', priority=True)
        self.status_timer_add(cmd='AVMT', callback=self.get_av_mute_status)
        self.poll_loop()

    def set_audio_normal(self, priority=False):
        """
        Send command to set audio to normal
        """
        log.debug(f'({self.entry.name}) Setting AVMT to 20 (audio normal)')
        self.send_command(cmd='AVMT', opts='20', priority=True)
        self.status_timer_add(cmd='AVMT', callback=self.get_av_mute_status)
        self.poll_loop()

    def set_input_source(self, src=None):
        """
        Verify input source available as listed in 'INST' command,
        then send the command to select the input source.

        :param src: Video source to select in projector
        """
        log.debug(f'({self.entry.name}) set_input_source(src="{src}")')
        if self.source_available is None:
            return
        elif src not in self.source_available:
            return
        log.debug(f'({self.entry.name}) Setting input source to "{src}"')
        self.send_command(cmd='INPT', opts=src, priority=True)
        self.poll_loop()

    def set_power_on(self):
        """
        Send command to turn power to on.
        """
        log.debug(f'({self.entry.name}) Setting POWR to 1 (on)')
        self.send_command(cmd='POWR', opts='1', priority=True)
        self.status_timer_add(cmd='POWR', callback=self.get_power_status)
        self.poll_loop()

    def set_power_off(self):
        """
        Send command to turn power to standby.
        """
        log.debug(f'({self.entry.name}) Setting POWR to 0 (standby)')
        self.send_command(cmd='POWR', opts='0', priority=True)
        self.status_timer_add(cmd='POWR', callback=self.get_power_status)
        self.poll_loop()

    def set_shutter_closed(self):
        """
        Send command to set shutter to closed position.
        """
        log.debug(f'({self.entry.name}) Setting AVMT to 11 (shutter closed)')
        self.send_command(cmd='AVMT', opts='11', priority=True)
        self.status_timer_add('AVMT', self.get_av_mute_status)
        self.poll_loop()

    def set_shutter_open(self):
        """
        Send command to set shutter to open position.
        """
        log.debug(f'({self.entry.name}) Setting AVMT to "10" (shutter open)')
        self.send_command(cmd='AVMT', opts='10', priority=True)
        self.status_timer_add('AVMT', self.get_av_mute_status)
        self.poll_loop()

    def status_timer_add(self, cmd, callback):
        """
        Add a callback to the status timer.

        :param cmd: PJLink command associated with callback
        :param callback: Method to call
        """
        if cmd in self.status_timer_checks:
            log.warning(f'({self.entry.name}) "{cmd}" already in checks - returning')
            return
        log.debug(f'({self.entry.name}) Adding "{cmd}" callback for status timer')
        self.status_timer_checks[cmd] = callback
        if not self.status_timer.isActive():
            self.status_timer.start()

    def status_timer_delete(self, cmd):
        """
        Delete a callback from the status timer.

        :param cmd: PJLink command associated with callback
        :param callback: Method to call
        """
        if cmd not in self.status_timer_checks:
            log.warning(f'({self.entry.name}) "{cmd}" not listed in status timer - returning')
            return
        log.debug(f'({self.entry.name}) Removing "{cmd}" from status timer')
        self.status_timer_checks.pop(cmd)
        if not self.status_timer_checks:
            self.status_timer.stop()

    def status_timer_update(self):
        """
        Call methods defined in status_timer_checks for updates
        """
        if not self.status_timer_checks:
            log.warning(f'({self.entry.name}) status_timer_update() called when no callbacks - Race condition?')
            self.status_timer.stop()
            return
        for cmd, callback in self.status_timer_checks.items():
            log.debug(f'({self.entry.name}) Status update call for {cmd}')
            callback(priority=True)

    def receive_data_signal(self):
        """
        Clear any busy flags and send data received signal
        """
        self.send_busy = False
        self.projectorReceivedData.emit()
        return
