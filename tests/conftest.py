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
All the tests
"""
import os
import shutil
from tempfile import mkdtemp
from tempfile import mkstemp
from unittest.mock import MagicMock

import pytest
from pytestqt.qt_compat import qt_api

from PySide6 import QtCore  # noqa

from openlp.core.app import OpenLP
from openlp.core.state import State
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings


@pytest.fixture
def qapp(qtbot):
    """An instance of QApplication"""
    # Newer versions of pytest-qt have QApplication in the widgets module.
    # Catch attribute error if the widgets module is missing and instantiate QApplication the old way.
    try:
        qt_api.QtWidgets.QApplication.instance()
    except AttributeError:
        qt_api.QApplication.instance()
    app = OpenLP()
    yield app
    del app


@pytest.fixture
def mocked_qapp():
    """A mocked instance of QApplication"""
    app = MagicMock()
    yield app
    del app


@pytest.fixture
def registry():
    """An instance of the Registry"""
    yield Registry.create()
    Registry._instances = {}


@pytest.fixture
def settings(qapp, registry):
    """A Settings() instance"""
    fd, ini_file = mkstemp('.ini')
    Settings.set_filename(ini_file)
    Settings().setDefaultFormat(QtCore.QSettings.Format.IniFormat)
    # Needed on windows to make sure a Settings object is available during the tests
    sets = Settings()
    sets.init_default_shortcuts()
    sets.setValue('themes/global theme', 'my_theme')
    registry.register('settings', sets)
    registry.register('settings_thread', sets)
    registry.register('application', qapp)
    qapp.settings = sets
    yield sets
    del sets
    registry.remove('settings')
    registry.remove('settings_thread')
    os.close(fd)
    os.unlink(Settings().fileName())


@pytest.fixture
def mock_settings(qapp, registry):
    """A Mock Settings() instance"""
    # Create and register a mock settings object to work with
    mk_settings = MagicMock()
    registry.register('settings', mk_settings)
    registry.register('application', qapp)
    registry.register('settings_thread', mk_settings)
    yield mk_settings
    registry.remove('settings')
    registry.remove('settings_thread')
    del mk_settings


@pytest.fixture
def state():
    yield State().load_settings()
    State._instances = {}


@pytest.fixture()
def state_media(state):
    State().add_service("media", 0)
    State().update_pre_conditions("media", True)
    State().flush_preconditions()
    yield state


@pytest.fixture()
def temp_folder():
    t_folder = mkdtemp(prefix='openlp_')
    yield t_folder
    shutil.rmtree(t_folder, ignore_errors=True)
