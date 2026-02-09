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
from pathlib import Path
from typing import Optional

from PySide6 import QtCore, QtNetwork

from openlp.core.common.mixins import LogMixin
from openlp.core.common.registry import Registry

# The maximum amount of time to wait before giving up, 120s
MAX_WAIT_TIME_MS = 120000


class Server(QtCore.QObject, LogMixin):
    """
    The local server to handle OpenLP running in more than one instance and allows file
    handles to be transferred from the new to the existing one.
    """
    def __init__(self):
        super(Server, self).__init__()
        self.out_socket = QtNetwork.QLocalSocket()
        self.server: Optional[QtNetwork.QLocalServer] = None
        self.file_name: Optional[Path | str] = None
        self.id = 'OpenLPDual'
        self._ms_waited = 0

    def is_another_instance_running(self) -> bool:
        """
        Check the see if an other instance is running
        :return: True of False
        """
        # Is there another instance running?
        self.out_socket.connectToServer(self.id)
        return self.out_socket.waitForConnected()

    def post_to_server(self, args: list):
        """
        Post the file name to the over instance
        :param args: The passed arguments including maybe a file name
        """
        if 'OpenLP' in args:
            args.remove('OpenLP')
        # Yes, there is.
        if len(args):
            self.out_stream = QtCore.QTextStream(self.out_socket)
            self.out_stream.setCodec('UTF-8')
            self.out_socket.write(str.encode("".join(args)))
            if not self.out_socket.waitForBytesWritten(10):
                raise Exception(str(self.out_socket.errorString()))
            self.out_socket.disconnectFromServer()

    def start_server(self) -> bool:
        """
        Start the socket server to allow inter app communication
        :return:
        """
        self.out_socket = None
        self.out_stream = None
        self.in_socket = None
        self.in_stream = None
        self.server = QtNetwork.QLocalServer()
        self.server.listen(self.id)
        self.server.newConnection.connect(self._on_new_connection)
        return True

    def _on_new_connection(self):
        """
        Handle a new connection to the server
        :return:
        """
        if self.in_socket:
            self.in_socket.readyRead.disconnect(self._on_ready_read)
        self.in_socket = self.server.nextPendingConnection()
        if not self.in_socket:
            return
        self.in_stream = QtCore.QTextStream(self.in_socket)
        self.in_stream.setCodec('UTF-8')
        self.in_socket.readyRead.connect(self._on_ready_read)

    @QtCore.Slot()
    def _on_ready_read(self):
        """
        Read a record passed to the server and pass to the service manager to handle
        :return:
        """
        if not self.file_name:
            self.file_name = self.in_stream.readLine()
            self.log_debug(f'file name = "{self.file_name}"')
        try:
            service_manager = Registry().get('service_manager')
        except KeyError:
            service_manager = None
        if service_manager:
            service_manager.load_service(Path(self.file_name))
        elif self._ms_waited > MAX_WAIT_TIME_MS:
            self.log_error('OpenLP is taking too long to start up, abandoning file load')
        else:
            self.log_info('Service manager is not loaded yet, waiting 500ms')
            self._ms_waited += 500
            QtCore.QTimer.singleShot(500, self._on_ready_read)

    def close_server(self):
        """
        Shutdown to local socket server and make sure the server is removed.
        :return:
        """
        if self.server:
            self.server.close()
        # Make sure the server file is removed.
        QtNetwork.QLocalServer.removeServer(self.id)
