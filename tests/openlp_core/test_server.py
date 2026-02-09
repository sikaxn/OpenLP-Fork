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
import pytest
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

from openlp.core.common.registry import Registry
from openlp.core.server import Server


@pytest.fixture
def server(registry: Registry) -> Generator:
    with patch('openlp.core.server.QtNetwork.QLocalSocket'):
        server = Server()
    yield server
    server.close_server()


def test_is_another_instance_running(server: Server):
    """
    Run a test as if this was the first time and no instance is running
    """
    # GIVEN: A running Server

    # WHEN: I ask for it to start
    value = server.is_another_instance_running()

    # THEN the following is called
    server.out_socket.waitForConnected.assert_called_once_with()
    server.out_socket.connectToServer.assert_called_once_with(server.id)
    assert isinstance(value, MagicMock)


def test_is_another_instance_running_true(server: Server):
    """
    Run a test as if there is another instance running
    """
    # GIVEN: A running Server
    server.out_socket.waitForConnected.return_value = True

    # WHEN: I ask for it to start
    value = server.is_another_instance_running()

    # THEN the following is called
    server.out_socket.waitForConnected.assert_called_once_with()
    server.out_socket.connectToServer.assert_called_once_with(server.id)
    assert value is True


def test_on_ready_read(server: Server):
    """
    Test the _on_ready_read method calls the service_manager
    """
    # GIVEN: A server with a service manager
    server.in_stream = MagicMock()
    service_manager = MagicMock()
    Registry().register('service_manager', service_manager)

    # WHEN: a file is added to the socket and the method called
    file_name = '\\home\\superfly\\'
    server.in_stream.readLine.return_value = file_name
    server._on_ready_read()

    # THEN: the service will be loaded
    assert service_manager.load_service.call_count == 1
    service_manager.load_service.assert_called_once_with(Path(file_name))


@patch('openlp.core.server.QtCore.QTimer')
def test_on_ready_read_no_service_manager(MockQTimer: MagicMock, server: Server):
    """
    Check that the _on_ready_read method calls a timer when the service_manager is not yet available
    """
    # GIVEN: A server with a service manager
    server.in_stream = MagicMock()

    # WHEN: a file is added to the socket and the method called
    file_name = '\\home\\superfly\\'
    server.in_stream.readLine.return_value = file_name
    server._on_ready_read()

    # THEN: the service will be loaded
    assert server._ms_waited == 500
    MockQTimer.singleShot.assert_called_once_with(500, server._on_ready_read)


def test_on_ready_read_giving_up(server: Server):
    """
    Check that the _on_ready_read gives up when it has waited for 2 minutes and the service manager is not available
    """
    # GIVEN: A server that has waited too long
    server.file_name = '/path/to/service.osz'
    server._ms_waited = 120500

    # WHEN: _on_ready_read has been called from the timer
    with patch.object(server, 'log_error') as mocked_log_error:
        server._on_ready_read()

    # THEN: the service will be loaded
    mocked_log_error.assert_called_once_with('OpenLP is taking too long to start up, abandoning file load')


@patch('openlp.core.server.QtCore.QTextStream')
def test_post_to_server(MockStream: MagicMock, server: Server):
    """
    A Basic test with a post to the service
    :return:
    """
    # GIVEN: A server
    # WHEN: I post to a server
    server.post_to_server(['l', 'l', 'a', 'm', 'a', 's'])

    # THEN: the file should be passed out to the socket
    server.out_socket.write.assert_called_once_with(b'llamas')


@patch('openlp.core.server.QtCore.QTextStream')
def test_post_to_server_openlp(MockStream: MagicMock, server: Server):
    """
    A Basic test with a post to the service with OpenLP
    :return:
    """
    # GIVEN: A server
    # WHEN: I post to a server
    server.post_to_server(['l', 'l', 'a', 'm', 'a', 's', 'OpenLP'])

    # THEN: the file should be passed out to the socket
    server.out_socket.write.assert_called_once_with(b'llamas')


@patch('openlp.core.server.QtCore.QTextStream')
def test_post_to_server_openlp_exception(MockStream: MagicMock, server: Server):
    """Test that we raise an exception when there are no bytes written"""
    # GIVEN: A server and a mocked stream
    server.out_socket.waitForBytesWritten.return_value = False
    server.out_socket.errorString.return_value = 'Error writing to socket'

    # WHEN: post_to_server is called
    # THEN: An exception is raised
    with pytest.raises(Exception) as e:
        server.post_to_server(['filename'])
    assert 'Error writing to socket' in str(e)


@patch('openlp.core.server.QtNetwork.QLocalServer')
def test_start_server(MockLocalServer: MagicMock, server: Server):
    """Test the start server method works correctly"""
    # GIVEN: A server
    server.out_stream = MagicMock()
    server.out_socket = MagicMock()
    server.in_stream = MagicMock()
    server.in_socket = MagicMock()
    mocked_server = MagicMock()
    MockLocalServer.return_value = mocked_server

    # WHEN: start_server is called
    result = server.start_server()

    # THEN: The server should have been started
    assert result is True
    assert server.out_socket is None
    assert server.out_stream is None
    assert server.in_socket is None
    assert server.in_stream is None
    assert server.server is mocked_server
    mocked_server.listen.assert_called_once_with(server.id)
    mocked_server.newConnection.connect.assert_called_once_with(server._on_new_connection)


@patch('openlp.core.server.QtCore.QTextStream')
def test_on_new_connection(MockTextStream: MagicMock, server: Server):
    """Test that the _on_new_connection slot works correctly"""
    # GIVEN: A server with some mocked properties
    mocked_stream = MagicMock()
    MockTextStream.return_value = mocked_stream
    server.in_socket = MagicMock()
    mocked_next_socket = MagicMock()
    server.server = MagicMock(**{'nextPendingConnection.return_value': mocked_next_socket})

    # WHEN: _on_new_connection is called
    server._on_new_connection()

    # THEN: The correct methods and attributes should have been called/set up
    assert server.in_socket is mocked_next_socket
    assert server.in_stream is mocked_stream
    MockTextStream.assert_called_once_with(mocked_next_socket)
    mocked_stream.setCodec.assert_called_once_with('UTF-8')
    mocked_next_socket.readyRead.connect.assert_called_once_with(server._on_ready_read)


@patch('openlp.core.server.QtCore.QTextStream')
def test_on_new_connection_no_socket(MockTextStream: MagicMock, server: Server):
    """Test that the _on_new_connection slot works correctly"""
    # GIVEN: A server with some mocked properties
    server.in_socket = MagicMock()
    server.server = MagicMock(**{'nextPendingConnection.return_value': None})

    # WHEN: _on_new_connection is called
    server._on_new_connection()

    # THEN: The correct methods and attributes should have been called/set up
    assert server.in_socket is None
    MockTextStream.assert_not_called()


def test_close_server(server: Server):
    """Test that the server is closed"""
    # GIVEN: A server
    server.server = MagicMock()

    # WHEN: The close_server() method is called
    server.close_server()

    # THEN: The server is closed
    server.server.close.assert_called_once_with()
