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
The :mod:`core` module provides state management

All the core functions of the OpenLP application including the GUI, settings, logging and a plugin framework are
contained within the openlp.core module.
"""
import logging
import getpass
import socket
import json
import time
from datetime import datetime
from threading import Timer

from PySide6 import QtWidgets  # noqa

from openlp.core.common.i18n import translate

log = logging.getLogger()

LOCK_UPDATE_SECS = 5 * 60
LOCK_EXPIRE_SECS = 7 * 60


class FileLock():
    """
    Implements a file lock, where the lock file contains the username and computername of the lock owner.
    When the file lock is released the lock file is deleted.
    If a lock aleady exists the user is informed who owns the lock.
    A timer is used to refresh the lockfile every 5th minute. If a lock file is not refreshed for 7 minutes, the lock
    can be claimed by a new user/instance.
    If an user/instance believes that it owns the lock, but the lock file content says that the lock has a different
    owner, the user will be warned and asked to close the instance immediately.
    """

    def __init__(self, data_folder, version):
        """
        Initialize lock.

        :param Path data_folder: The folder where the OpenLP data is located and where the lockfile is placed
        :param string version: The OpenLP version
        """
        self.lock_filepath = data_folder / 'openlp-data.lock'
        self.timer = None
        self.version = version
        self.has_lock = False

    def __del__(self):
        """
        Destructor
        """
        self.release()

    def release(self):
        """
        Release the lock
        """
        if self.timer:
            self.timer.cancel()
        if self.has_lock and self.lock_filepath.exists():
            self.lock_filepath.unlink()

    def parse_lock_file_content(self):
        """
        Parse the content of the lockfile, returns dict with the data from the lock file.
        """
        with self.lock_filepath.open('r') as lock_file:
            lock_file_data = lock_file.read()
            data = json.loads(lock_file_data)
            return data

    def update_lock_file(self):
        """
        Update the content of the lockfile with the current username, hostname, timestamp and openlp version.
        """
        username = getpass.getuser()
        hostname = socket.gethostname()
        if self.lock_filepath.exists():
            # check if the existing lock has been claimed by someone else, and if so stop the locking
            data = self.parse_lock_file_content()
            if data['username'] != username or data['hostname'] != hostname:
                self.has_lock = False
                log.critical('"{user}" on "{host}" has claimed the Data Directory Lock!'
                             .format(user=data['username'], host=data['hostname']))
                QtWidgets.QMessageBox.critical(
                    None, translate('OpenLP', 'Data Directory Lock Error'),
                    translate('OpenLP', 'You have lost OpenLPs shared Data Directory Lock, which instead has '
                                        'been claimed by "{user}" on "{host}"! You should close OpenLP '
                                        'immediately to avoid data corruption! You can try to reclaim the Data '
                                        'Directory Lock by restarting OpenLP')
                    .format(user=data['username'], host=data['hostname']),
                    QtWidgets.QMessageBox.StandardButton(QtWidgets.QMessageBox.StandardButton.Ok),
                    QtWidgets.QMessageBox.StandardButton.Ok)
            return
        self.has_lock = True
        with self.lock_filepath.open('w') as lock_file:
            data = {}
            data['version'] = self.version
            data['username'] = username
            data['hostname'] = hostname
            # the timestamp is mostly there to ensure that the file content changes and thereby the modification time
            data['timestamp'] = str(datetime.now())
            lock_file.write(json.dumps(data))
        # create and start timer for updating the lock file every 5 minutes
        self.timer = Timer(LOCK_UPDATE_SECS, self.update_lock_file)
        self.timer.start()

    def lock(self):
        """
        Create a lock if possible.

        :return: If the lock was acquired.
        :rtype: bool
        """
        if self.lock_filepath.exists():
            # check if the existing lock has expired
            stat_result = self.lock_filepath.stat()
            sec_since_modified = time.time() - stat_result.st_mtime
            if sec_since_modified > LOCK_EXPIRE_SECS:
                # the existing lock has expired! Claim it!
                self.lock_filepath.unlink(missing_ok=True)
                self.update_lock_file()
                return True
            # someone else has already claimed the lock!
            data = self.parse_lock_file_content()
            QtWidgets.QMessageBox.critical(
                None, translate('OpenLP', 'Data Directory Locked'),
                translate('OpenLP', 'OpenLPs shared Data Directory is being used by "{user}" on "{host}". '
                                    'To avoid data corruption only one user can access the data at a time! Please '
                                    'wait a few minutes and try again.')
                .format(user=data['username'], host=data['hostname']),
                QtWidgets.QMessageBox.StandardButton(QtWidgets.QMessageBox.StandardButton.Ok),
                QtWidgets.QMessageBox.StandardButton.Ok)
            return False
        else:
            self.update_lock_file()
            return self.has_lock
