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
The :mod:`openlp.core.lib.projector.constants` module provides the constants used for projector errors/status/defaults
"""
import logging

from openlp.core.common.i18n import translate


log = logging.getLogger(__name__)
log.debug('projector_constants loaded')

# Set common constants.
CR = chr(0x0D)  # \r
LF = chr(0x0A)  # \n
PJLINK_CLASS = '1'  # Default to class 1 until we query the projector
PJLINK_MAX_PACKET = 136
PJLINK_PREFIX = '%'
PJLINK_PORT = 4352
PJLINK_SUFFIX = CR
PJLINK_SVER_MAX_LEN = 32
PJLINK_TIMEOUT = 30.0
PJLINK_TOKEN_SIZE = 8  # PJLINK 1 <token> : where <token> is 8 characters
PJLINK_VALID_PORTS = range(1000, 32768)

# Error and status codes
S_OK = E_OK = 0  # E_OK included since I sometimes forget

# Error codes. Start at 200 so we don't duplicate system error codes.
E_GENERAL = 200  # Unknown error
E_NOT_CONNECTED = 201
E_UNDEFINED = 202           # PJLink ERR1
E_PARAMETER = 203           # PJLink ERR2
E_UNAVAILABLE = 204         # PJLink ERR3
E_PROJECTOR = 205           # PJLink ERR4
E_AUTHENTICATION = 206      # PJLink ERRA
E_NO_AUTHENTICATION = 207   # PJLink authentication mismatch between projector and program
E_PREFIX = 208              # PJLink invalid prefix for packet
E_CLASS = 209               # PJLink class version mismatch
E_INVALID_DATA = 210
E_WARN = 211
E_ERROR = 212
E_FAN = 213
E_LAMP = 214
E_TEMP = 215
E_COVER = 216
E_FILTER = 217
E_UNKNOWN = 218

# Remap Qt socket error codes to local error codes
E_CONNECTION_REFUSED = 230
E_REMOTE_HOST_CLOSED_CONNECTION = 231
E_HOST_NOT_FOUND = 232
E_SOCKET_ACCESS = 233
E_SOCKET_RESOURCE = 234
E_SOCKET_TIMEOUT = 235
E_DATAGRAM_TOO_LARGE = 236
E_NETWORK = 237
E_ADDRESS_IN_USE = 238
E_SOCKET_ADDRESS_NOT_AVAILABLE = 239
E_UNSUPPORTED_SOCKET_OPERATION = 240
E_PROXY_AUTHENTICATION_REQUIRED = 241
E_SLS_HANDSHAKE_FAILED = 242
E_UNFINISHED_SOCKET_OPERATION = 243
E_PROXY_CONNECTION_REFUSED = 244
E_PROXY_CONNECTION_CLOSED = 245
E_PROXY_CONNECTION_TIMEOUT = 246
E_PROXY_NOT_FOUND = 247
E_PROXY_PROTOCOL = 248
E_UNKNOWN_SOCKET_ERROR = 249

# Status codes start at 300

# Remap Qt socket states to local status codes
S_NOT_CONNECTED = 300
S_HOST_LOOKUP = 301
S_CONNECTING = 302
S_CONNECTED = 303
S_BOUND = 304
S_LISTENING = 305  # Listed as internal use only in QAbstractSocket
S_CLOSING = 306

# Projector states
S_INITIALIZE = 310
S_STATUS = 311
S_OFF = 312
S_STANDBY = 313
S_WARMUP = 314
S_ON = 315
S_COOLDOWN = 316
S_INFO = 317
S_CONNECT = 318  # Initial connection, connected
S_AUTHENTICATE = 319  # Initial connection, send pin hash
S_DATA_OK = 320  # Previous command returned OK

# Information that does not affect status
S_NETWORK_IDLE = 400
S_NETWORK_SENDING = 401
S_NETWORK_RECEIVING = 402

# Map PJLink errors to local status
PJLINK_ERRORS = {
    'ERRA': E_AUTHENTICATION,   # Authentication error
    'ERR1': E_UNDEFINED,        # Undefined command error
    'ERR2': E_PARAMETER,        # Invalid parameter error
    'ERR3': E_UNAVAILABLE,      # Projector busy
    'ERR4': E_PROJECTOR,        # Projector or display failure
    E_AUTHENTICATION: 'ERRA',
    E_UNDEFINED: 'ERR1',
    E_PARAMETER: 'ERR2',
    E_UNAVAILABLE: 'ERR3',
    E_PROJECTOR: 'ERR4'
}

# Map QAbstractSocketState enums to local status
QSOCKET_STATE = {
    0: S_NOT_CONNECTED,     # 'UnconnectedState',
    1: S_HOST_LOOKUP,       # 'HostLookupState',
    2: S_CONNECTING,        # 'ConnectingState',
    3: S_CONNECTED,         # 'ConnectedState',
    4: S_BOUND,             # 'BoundState',
    5: S_LISTENING,         # 'ListeningState' -  Noted as "Internal Use Only" on Qt website
    6: S_CLOSING,           # 'ClosingState',
    S_NOT_CONNECTED: 0,
    S_HOST_LOOKUP: 1,
    S_CONNECTING: 2,
    S_CONNECTED: 3,
    S_BOUND: 4,
    S_LISTENING: 5,
    S_CLOSING: 6
}

PROJECTOR_STATE = [
    S_INITIALIZE,
    S_STATUS,
    S_OFF,
    S_STANDBY,
    S_WARMUP,
    S_ON,
    S_COOLDOWN,
    S_INFO
]

# NOTE: Changed format to account for some commands are both class 1 and 2.
#       Make sure the sequence of 'version' is lowest-to-highest.
PJLINK_VALID_CMD = {
    'ACKN': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Acknowledge a PJLink SRCH command - returns MAC address.')
             },
    'AVMT': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Blank/unblank video and/or mute audio.')
             },
    'CLSS': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector PJLink class support.')
             },
    'ERST': {'version': ['1', '2'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query error status from projector. '
                                      'Returns fan/lamp/temp/cover/filter/other error status.')
             },
    'FILT': {'version': ['2'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query number of hours on filter.')
             },
    'FREZ': {'version': ['2'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Freeze or unfreeze current image being projected.')
             },
    'INF1': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector manufacturer name.')
             },
    'INF2': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector product name.')
             },
    'INFO': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector for other information set by manufacturer.')
             },
    'INNM': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query specified input source name')
             },
    'INPT': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Switch to specified video source.')
             },
    'INST': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query available input sources.')
             },
    'IRES': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query current input resolution.')
             },
    'LAMP': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query lamp time and on/off status. Multiple lamps supported.')
             },
    'LKUP': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'UDP Status - Projector is now available on network. Includes MAC address.')
             },
    'MVOL': {'version': ['2'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Adjust microphone volume by 1 step.')
             },
    'NAME': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query customer-set projector name.')
             },
    'PJLINK': {'version': ['1'],
               'default': '1',
               'description': translate('OpenLP.PJLinkConstants',
                                        'Initial connection with authentication/no authentication request.')
               },
    'POWR': {'version': ['1'],
             'default': '1',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Turn lamp on or off/standby.')
             },
    'RFIL': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query replacement air filter model number.')
             },
    'RLMP': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query replacement lamp model number.')
             },
    'RRES': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query recommended resolution.')
             },
    'SNUM': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector serial number.')
             },
    'SRCH': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'UDP broadcast search request for available projectors. Reply is ACKN.')
             },
    'SVER': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Query projector software version number.')
             },
    'SVOL': {'version': ['2'],
             'default': '2',
             'description': translate('OpenLP.PJLinkConstants',
                                      'Adjust speaker volume by 1 step.')
             }
}

CONNECTION_ERRORS = [
    E_ADDRESS_IN_USE,
    E_CONNECTION_REFUSED,
    E_DATAGRAM_TOO_LARGE,
    E_HOST_NOT_FOUND,
    E_NETWORK,
    E_NOT_CONNECTED,
    E_PROXY_AUTHENTICATION_REQUIRED,
    E_PROXY_CONNECTION_CLOSED,
    E_PROXY_CONNECTION_REFUSED,
    E_PROXY_CONNECTION_TIMEOUT,
    E_PROXY_NOT_FOUND,
    E_PROXY_PROTOCOL,
    E_REMOTE_HOST_CLOSED_CONNECTION,
    E_SLS_HANDSHAKE_FAILED,
    E_SOCKET_ACCESS,
    E_SOCKET_ADDRESS_NOT_AVAILABLE,
    E_SOCKET_RESOURCE,
    E_SOCKET_TIMEOUT,
    E_UNFINISHED_SOCKET_OPERATION,
    E_UNKNOWN_SOCKET_ERROR,
    E_UNSUPPORTED_SOCKET_OPERATION
]

PROJECTOR_ERRORS = [
    E_AUTHENTICATION,
    E_CLASS,
    E_INVALID_DATA,
    E_NO_AUTHENTICATION,
    E_PARAMETER,
    E_PREFIX,
    E_PROJECTOR,
    E_UNAVAILABLE,
    E_UNDEFINED,
    E_UNKNOWN
]

# Show status code as string
STATUS_CODE = {
    E_ADDRESS_IN_USE: 'E_ADDRESS_IN_USE',
    E_AUTHENTICATION: 'E_AUTHENTICATION',
    E_CLASS: 'E_CLASS',
    E_CONNECTION_REFUSED: 'E_CONNECTION_REFUSED',
    E_COVER: 'E_COVER',
    E_DATAGRAM_TOO_LARGE: 'E_DATAGRAM_TOO_LARGE',
    E_ERROR: 'E_ERROR',
    E_FAN: 'E_FAN',
    E_FILTER: 'E_FILTER',
    E_GENERAL: 'E_GENERAL',
    E_HOST_NOT_FOUND: 'E_HOST_NOT_FOUND',
    E_INVALID_DATA: 'E_INVALID_DATA',
    E_LAMP: 'E_LAMP',
    E_NETWORK: 'E_NETWORK',
    E_NO_AUTHENTICATION: 'E_NO_AUTHENTICATION',
    E_NOT_CONNECTED: 'E_NOT_CONNECTED',
    E_PARAMETER: 'E_PARAMETER',
    E_PREFIX: 'E_PREFIX',
    E_PROJECTOR: 'E_PROJECTOR',
    E_PROXY_AUTHENTICATION_REQUIRED: 'E_PROXY_AUTHENTICATION_REQUIRED',
    E_PROXY_CONNECTION_CLOSED: 'E_PROXY_CONNECTION_CLOSED',
    E_PROXY_CONNECTION_REFUSED: 'E_PROXY_CONNECTION_REFUSED',
    E_PROXY_CONNECTION_TIMEOUT: 'E_PROXY_CONNECTION_TIMEOUT',
    E_PROXY_NOT_FOUND: 'E_PROXY_NOT_FOUND',
    E_PROXY_PROTOCOL: 'E_PROXY_PROTOCOL',
    E_REMOTE_HOST_CLOSED_CONNECTION: 'E_REMOTE_HOST_CLOSED_CONNECTION',
    E_SLS_HANDSHAKE_FAILED: 'E_SLS_HANDSHAKE_FAILED',
    E_SOCKET_ACCESS: 'E_SOCKET_ACCESS',
    E_SOCKET_ADDRESS_NOT_AVAILABLE: 'E_SOCKET_ADDRESS_NOT_AVAILABLE',
    E_SOCKET_RESOURCE: 'E_SOCKET_RESOURCE',
    E_SOCKET_TIMEOUT: 'E_SOCKET_TIMEOUT',
    E_TEMP: 'E_TEMP',
    E_UNAVAILABLE: 'E_UNAVAILABLE',
    E_UNDEFINED: 'E_UNDEFINED',
    E_UNFINISHED_SOCKET_OPERATION: 'E_UNFINISHED_SOCKET_OPERATION',
    E_UNKNOWN: 'E_UNKNOWN',
    E_UNKNOWN_SOCKET_ERROR: 'E_UNKNOWN_SOCKET_ERROR',
    E_UNSUPPORTED_SOCKET_OPERATION: 'E_UNSUPPORTED_SOCKET_OPERATION',
    E_WARN: 'E_WARN',
    S_AUTHENTICATE: 'S_AUTHENTICATE',
    S_BOUND: 'S_BOUND',
    S_CONNECT: 'S_CONNECT',
    S_COOLDOWN: 'S_COOLDOWN',
    S_CLOSING: 'S_CLOSING',
    S_CONNECTED: 'S_CONNECTED',
    S_CONNECTING: 'S_CONNECTING',
    S_DATA_OK: 'S_DATA_OK',
    S_HOST_LOOKUP: 'S_HOST_LOOKUP',
    S_INFO: 'S_INFO',
    S_INITIALIZE: 'S_INITIALIZE',
    S_LISTENING: 'S_LISTENING',
    S_NETWORK_RECEIVING: 'S_NETWORK_RECEIVING',
    S_NETWORK_SENDING: 'S_NETWORK_SENDING',
    S_NETWORK_IDLE: 'S_NETWORK_IDLE',
    S_NOT_CONNECTED: 'S_NOT_CONNECTED',
    S_OFF: 'S_OFF',
    S_OK: 'S_OK',  # S_OK or E_OK
    S_ON: 'S_ON',
    S_STANDBY: 'S_STANDBY',
    S_STATUS: 'S_STATUS',
    S_WARMUP: 'S_WARMUP'
}

# Map status codes to message strings
STATUS_MSG = {
    E_ADDRESS_IN_USE: translate('OpenLP.ProjectorConstants',
                                'The address specified with socket.bind() '
                                'is already in use and was set to be exclusive'),
    E_AUTHENTICATION: translate('OpenLP.ProjectorConstants', 'PJLink returned "ERRA: Authentication Error"'),
    E_CONNECTION_REFUSED: translate('OpenLP.ProjectorConstants',
                                    'The connection was refused by the peer (or timed out)'),
    E_COVER: translate('OpenLP.ProjectorConstants', 'Projector cover open detected'),
    E_CLASS: translate('OpenLP.ProjectorConstants', 'PJLink class not supported'),
    E_DATAGRAM_TOO_LARGE: translate('OpenLP.ProjectorConstants',
                                    "The datagram was larger than the operating system's limit"),
    E_ERROR: translate('OpenLP.ProjectorConstants', 'Error condition detected'),
    E_FAN: translate('OpenLP.ProjectorConstants', 'Projector fan error'),
    E_FILTER: translate('OpenLP.ProjectorConstants', 'Projector check filter'),
    E_GENERAL: translate('OpenLP.ProjectorConstants', 'General projector error'),
    E_HOST_NOT_FOUND: translate('OpenLP.ProjectorConstants', 'The host address was not found'),
    E_INVALID_DATA: translate('OpenLP.ProjectorConstants', 'PJLink invalid packet received'),
    E_LAMP: translate('OpenLP.ProjectorConstants', 'Projector lamp error'),
    E_NETWORK: translate('OpenLP.ProjectorConstants',
                         'An error occurred with the network (Possibly someone pulled the plug?)'),
    E_NO_AUTHENTICATION: translate('OpenLP.ProjectorConstants', 'PJLink authentication Mismatch Error'),
    E_NOT_CONNECTED: translate('OpenLP.ProjectorConstants', 'Projector not connected error'),
    E_PARAMETER: translate('OpenLP.ProjectorConstants', 'PJLink returned "ERR2: Invalid Parameter"'),
    E_PREFIX: translate('OpenLP.ProjectorConstants', 'PJLink Invalid prefix character'),
    E_PROJECTOR: translate('OpenLP.ProjectorConstants', 'PJLink returned "ERR4: Projector/Display Error"'),
    E_PROXY_AUTHENTICATION_REQUIRED: translate('OpenLP.ProjectorConstants',
                                               'The socket is using a proxy, '
                                               'and the proxy requires authentication'),
    E_PROXY_CONNECTION_CLOSED: translate('OpenLP.ProjectorConstants',
                                         'The connection to the proxy server was closed unexpectedly '
                                         '(before the connection to the final peer was established)'),
    E_PROXY_CONNECTION_REFUSED: translate('OpenLP.ProjectorConstants',
                                          'Could not contact the proxy server because the connection '
                                          'to that server was denied'),
    E_PROXY_CONNECTION_TIMEOUT: translate('OpenLP.ProjectorConstants',
                                          'The connection to the proxy server timed out or the proxy '
                                          'server stopped responding in the authentication phase.'),
    E_PROXY_NOT_FOUND: translate('OpenLP.ProjectorConstants',
                                 'The proxy address set with setProxy() was not found'),
    E_PROXY_PROTOCOL: translate('OpenLP.ProjectorConstants',
                                'The connection negotiation with the proxy server failed because the '
                                'response from the proxy server could not be understood'),
    E_REMOTE_HOST_CLOSED_CONNECTION: translate('OpenLP.ProjectorConstants',
                                               'The remote host closed the connection'),
    E_SLS_HANDSHAKE_FAILED: translate('OpenLP.ProjectorConstants',
                                      'The SSL/TLS handshake failed'),
    E_SOCKET_ADDRESS_NOT_AVAILABLE: translate('OpenLP.ProjectorConstants',
                                              'The address specified to socket.bind() '
                                              'does not belong to the host'),
    E_SOCKET_ACCESS: translate('OpenLP.ProjectorConstants',
                               'The socket operation failed because the application '
                               'lacked the required privileges'),
    E_SOCKET_RESOURCE: translate('OpenLP.ProjectorConstants',
                                 'The local system ran out of resources (e.g., too many sockets)'),
    E_SOCKET_TIMEOUT: translate('OpenLP.ProjectorConstants',
                                'The socket operation timed out'),
    E_TEMP: translate('OpenLP.ProjectorConstants', 'Projector high temperature detected'),
    E_UNAVAILABLE: translate('OpenLP.ProjectorConstants', 'PJLink returned "ERR3: Busy"'),
    E_UNDEFINED: translate('OpenLP.ProjectorConstants', 'PJLink returned "ERR1: Undefined Command"'),
    E_UNFINISHED_SOCKET_OPERATION: translate('OpenLP.ProjectorConstants',
                                             'The last operation attempted has not finished yet '
                                             '(still in progress in the background)'),
    E_UNKNOWN: translate('OpenLP.ProjectorConstants', 'Unknown condition detected'),
    E_UNKNOWN_SOCKET_ERROR: translate('OpenLP.ProjectorConstants', 'An unidentified socket error occurred'),
    E_UNSUPPORTED_SOCKET_OPERATION: translate('OpenLP.ProjectorConstants',
                                              'The requested socket operation is not supported by the local '
                                              'operating system (e.g., lack of IPv6 support)'),
    E_WARN: translate('OpenLP.ProjectorConstants', 'Warning condition detected'),
    S_AUTHENTICATE: translate('OpenLP.ProjectorConstants', 'Connection initializing with pin'),
    S_BOUND: translate('OpenLP.ProjectorConstants', 'Socket is bound to an address or port'),
    S_CONNECT: translate('OpenLP.ProjectorConstants', 'Connection initializing'),
    S_CLOSING: translate('OpenLP.ProjectorConstants', 'Socket is about to close'),
    S_CONNECTED: translate('OpenLP.ProjectorConstants', 'Connected'),
    S_CONNECTING: translate('OpenLP.ProjectorConstants', 'Connecting'),
    S_COOLDOWN: translate('OpenLP.ProjectorConstants', 'Cooldown in progress'),
    S_DATA_OK: translate('OpenLP.ProjectorConstants', 'Command returned with OK'),
    S_HOST_LOOKUP: translate('OpenLP.ProjectorConstants', 'Performing a host name lookup'),
    S_INFO: translate('OpenLP.ProjectorConstants', 'Projector Information available'),
    S_INITIALIZE: translate('OpenLP.ProjectorConstants', 'Initialize in progress'),
    S_LISTENING: translate('OpenLP.ProjectorConstants', 'Socket is listening (internal use only)'),
    S_NETWORK_IDLE: translate('OpenLP.ProjectorConstants', 'No network activity at this time'),
    S_NETWORK_RECEIVING: translate('OpenLP.ProjectorConstants', 'Received data'),
    S_NETWORK_SENDING: translate('OpenLP.ProjectorConstants', 'Sending data'),
    S_NOT_CONNECTED: translate('OpenLP.ProjectorConstants', 'Not Connected'),
    S_OFF: translate('OpenLP.ProjectorConstants', 'Off'),
    S_OK: translate('OpenLP.ProjectorConstants', 'OK'),
    S_ON: translate('OpenLP.ProjectorConstants', 'Power is on'),
    S_STANDBY: translate('OpenLP.ProjectorConstants', 'Power in standby'),
    S_STATUS: translate('OpenLP.ProjectorConstants', 'Getting status'),
    S_WARMUP: translate('OpenLP.ProjectorConstants', 'Warmup in progress'),
}

# Map ERST reply positions to equipment
PJLINK_ERST_LIST = {
    "FAN": translate('OpenLP.PJLink', 'Fan'),
    "LAMP": translate('OpenLP.PJLink', 'Lamp'),
    "TEMP": translate('OpenLP.PJLink', 'Temperature'),
    "COVER": translate('OpenLP.PJLink', 'Cover'),
    "FILTER": translate('OpenLP.PJLink', 'Filter'),
    "OTHER": translate('OpenPL.PJLink', 'Other')
}

# Map projector item to ERST data position
PJLINK_ERST_DATA = {
    'DATA_LENGTH': 6,  # Zero based so enums are 0-5
    'FAN': 0,
    'LAMP': 1,
    'TEMP': 2,
    'COVER': 3,
    'FILTER': 4,
    'OTHER': 5,
    0: 'FAN',
    1: 'LAMP',
    2: 'TEMP',
    3: 'COVER',
    4: 'FILTER',
    5: 'OTHER'
}

# Map ERST reply codes to string
PJLINK_ERST_STATUS = {
    '0': S_OK,
    '1': E_WARN,
    '2': E_ERROR,
    S_OK: '0',
    E_WARN: '1',
    E_ERROR: '2'
}

# Map POWR return codes to status code
PJLINK_POWR_STATUS = {
    '0': S_STANDBY,
    '1': S_ON,
    '2': S_COOLDOWN,
    '3': S_WARMUP,
    S_STANDBY: '0',
    S_ON: '1',
    S_COOLDOWN: '2',
    S_WARMUP: '3'
}

PJLINK_DEFAULT_SOURCES = {
    '1': translate('OpenLP.DB', 'RGB'),
    '2': translate('OpenLP.DB', 'Video'),
    '3': translate('OpenLP.DB', 'Digital'),
    '4': translate('OpenLP.DB', 'Storage'),
    '5': translate('OpenLP.DB', 'Network'),
    '6': translate('OpenLP.DB', 'Internal')
}

PJLINK_DEFAULT_ITEMS = {
    '1': translate('OpenLP.DB', '1'),
    '2': translate('OpenLP.DB', '2'),
    '3': translate('OpenLP.DB', '3'),
    '4': translate('OpenLP.DB', '4'),
    '5': translate('OpenLP.DB', '5'),
    '6': translate('OpenLP.DB', '6'),
    '7': translate('OpenLP.DB', '7'),
    '8': translate('OpenLP.DB', '8'),
    '9': translate('OpenLP.DB', '9'),
    'A': translate('OpenLP.DB', 'A'),
    'B': translate('OpenLP.DB', 'B'),
    'C': translate('OpenLP.DB', 'C'),
    'D': translate('OpenLP.DB', 'D'),
    'E': translate('OpenLP.DB', 'E'),
    'F': translate('OpenLP.DB', 'F'),
    'G': translate('OpenLP.DB', 'G'),
    'H': translate('OpenLP.DB', 'H'),
    'I': translate('OpenLP.DB', 'I'),
    'J': translate('OpenLP.DB', 'J'),
    'K': translate('OpenLP.DB', 'K'),
    'L': translate('OpenLP.DB', 'L'),
    'M': translate('OpenLP.DB', 'M'),
    'N': translate('OpenLP.DB', 'N'),
    'O': translate('OpenLP.DB', 'O'),
    'P': translate('OpenLP.DB', 'P'),
    'Q': translate('OpenLP.DB', 'Q'),
    'R': translate('OpenLP.DB', 'R'),
    'S': translate('OpenLP.DB', 'S'),
    'T': translate('OpenLP.DB', 'T'),
    'U': translate('OpenLP.DB', 'U'),
    'V': translate('OpenLP.DB', 'V'),
    'W': translate('OpenLP.DB', 'W'),
    'X': translate('OpenLP.DB', 'X'),
    'Y': translate('OpenLP.DB', 'Y'),
    'Z': translate('OpenLP.DB', 'Z')
}

# Due to the expanded nature of PJLink class 2 video sources,
# translate the individual types then build the video source
# dictionary from the translations.
PJLINK_DEFAULT_CODES = dict()
for source in PJLINK_DEFAULT_SOURCES:
    for item in PJLINK_DEFAULT_ITEMS:
        label = "{source}{item}".format(source=source, item=item)
        PJLINK_DEFAULT_CODES[label] = "{source} {item}".format(source=PJLINK_DEFAULT_SOURCES[source],
                                                               item=PJLINK_DEFAULT_ITEMS[item])
