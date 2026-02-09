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
This module contains tests for the upgrade submodule of the Bibles plugin.
"""
import pytest
import shutil
import secrets
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import MagicMock, call, patch

from sqlalchemy import create_engine, select, table, column

from openlp.core.common.settings import ProxyMode
from openlp.core.db.upgrades import upgrade_db
from openlp.plugins.bibles.lib import upgrade
from tests.utils.constants import RESOURCE_PATH


@pytest.fixture()
def mock_message_box():
    patched_message_box = patch('openlp.plugins.bibles.lib.upgrade.QtWidgets.QMessageBox')
    mocked_message_box = patched_message_box.start()
    mocked_no_button = MagicMock()
    mocked_http_button = MagicMock()
    mocked_both_button = MagicMock()
    mocked_https_button = MagicMock()
    mocked_message_box_inst = MagicMock(
        **{'addButton.side_effect': [mocked_no_button, mocked_http_button,
                                     mocked_both_button, mocked_https_button]})
    mocked_message_box.return_value = mocked_message_box_inst
    yield mocked_message_box_inst, mocked_both_button, mocked_https_button, mocked_http_button, mocked_no_button
    patched_message_box.stop()


@pytest.fixture()
def db_url():
    tmp_path = Path(mkdtemp())
    src_path = RESOURCE_PATH / 'bibles' / 'web-bible-2.4.6-proxy-meta-v1.sqlite'
    dst_path = tmp_path / f'openlp-{secrets.token_urlsafe()}.sqlite'
    shutil.copyfile(src_path, dst_path)
    yield 'sqlite:///' + str(dst_path)
    try:
        dst_path.unlink()
    except PermissionError:
        # on windows sometimes we try to delete this while still in use...?
        pass


def test_upgrade_2_basic(mock_message_box, db_url, mock_settings):
    """
    Test that upgrade 2 completes properly when the user chooses not to use a proxy ('No')
    """
    # GIVEN: An version 1 web bible with proxy settings
    mocked_message_box = mock_message_box[0]

    # WHEN: Calling upgrade_db and the user has 'clicked' the 'No' button
    upgrade_db(db_url, upgrade)

    # THEN: The proxy meta data should have been removed, and the version should have been changed to version 2
    mocked_message_box.assert_not_called()
    engine = create_engine(db_url)
    conn = engine.connect()
    md = table('metadata', column('key'), column('value'))
    assert conn.execute(select(md.c.value).where(md.c.key == 'version')).scalar() == '2'


@pytest.mark.xfail
def test_upgrade_2_none_selected(mock_message_box, db_url, mock_settings):
    """
    Test that upgrade 2 completes properly when the user chooses not to use a proxy ('No')
    """
    # GIVEN: An version 1 web bible with proxy settings

    # WHEN: Calling upgrade_db and the user has 'clicked' the 'No' button
    mocked_message_box_instance = mock_message_box[0]
    mocked_no_button = mock_message_box[4]
    mocked_message_box_instance.clickedButton.return_value = mocked_no_button
    upgrade_db(db_url, upgrade)

    # THEN: The proxy meta data should have been removed, and the version should have been changed to version 2
    engine = create_engine(db_url)
    conn = engine.connect()
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_server"').fetchall()) == 0
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_username"').fetchall()) == 0
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_password"').fetchall()) == 0
    assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'
    mock_settings.setValue.assert_not_called()


@pytest.mark.xfail
def test_upgrade_2_http_selected(mock_message_box, db_url, mock_settings):
    """
    Test that upgrade 2 completes properly when the user chooses to use a HTTP proxy
    """
    # GIVEN: An version 1 web bible with proxy settings

    # WHEN: Calling upgrade_db and the user has 'clicked' the 'HTTP' button
    mocked_message_box_instance = mock_message_box[0]
    mocked_http_button = mock_message_box[3]
    mocked_message_box_instance.clickedButton.return_value = mocked_http_button
    upgrade_db(db_url, upgrade)

    # THEN: The proxy meta data should have been removed, the version should have been changed to version 2, and the
    #       proxy server saved to the settings
    engine = create_engine(db_url)
    conn = engine.connect()
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_server"').fetchall()) == 0
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_username"').fetchall()) == 0
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_password"').fetchall()) == 0
    assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'

    assert mock_settings.setValue.call_args_list == [
        call('advanced/proxy http', 'proxy_server'), call('advanced/proxy username', 'proxy_username'),
        call('advanced/proxy password', 'proxy_password'), call('advanced/proxy mode', ProxyMode.MANUAL_PROXY)]


@pytest.mark.xfail
def test_upgrade_2_https_selected(mock_message_box, db_url, mock_settings):
    """
    Tcest that upgrade 2 completes properly when the user chooses to use a HTTPS proxy
    """
    # GIVEN: An version 1 web bible with proxy settings

    # WHEN: Calling upgrade_db and the user has 'clicked' the 'HTTPS' button
    mocked_message_box_instance = mock_message_box[0]
    mocked_https_button = mock_message_box[2]
    mocked_message_box_instance.clickedButton.return_value = mocked_https_button
    upgrade_db(db_url, upgrade)

    # THEN: The proxy settings should have been removed, the version should have been changed to version 2, and the
    #       proxy server saved to the settings
    engine = create_engine(db_url)
    conn = engine.connect()
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_server"').fetchall()) == 0
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_username"').fetchall()) == 0
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_password"').fetchall()) == 0
    assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'

    assert mock_settings.setValue.call_args_list == [
        call('advanced/proxy https', 'proxy_server'), call('advanced/proxy username', 'proxy_username'),
        call('advanced/proxy password', 'proxy_password'), call('advanced/proxy mode', ProxyMode.MANUAL_PROXY)]


@pytest.mark.xfail
def test_upgrade_2_both_selected(mock_message_box, db_url, mock_settings):
    """
    Tcest that upgrade 2 completes properly when the user chooses to use a both HTTP and HTTPS proxies
    """

    # GIVEN: An version 1 web bible with proxy settings

    # WHEN: Calling upgrade_db
    mocked_message_box_instance = mock_message_box[0]
    mocked_both_button = mock_message_box[1]
    mocked_message_box_instance.clickedButton.return_value = mocked_both_button
    upgrade_db(db_url, upgrade)

    # THEN: The proxy settings should have been removed, the version should have been changed to version 2, and the
    #       proxy server saved to the settings
    engine = create_engine(db_url)
    conn = engine.connect()
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_server"').fetchall()) == 0
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_username"').fetchall()) == 0
    assert len(conn.execute('SELECT * FROM metadata WHERE key = "proxy_password"').fetchall()) == 0
    assert conn.execute('SELECT * FROM metadata WHERE key = "version"').first().value == '2'

    assert mock_settings.setValue.call_args_list == [
        call('advanced/proxy http', 'proxy_server'), call('advanced/proxy https', 'proxy_server'),
        call('advanced/proxy username', 'proxy_username'), call('advanced/proxy password', 'proxy_password'),
        call('advanced/proxy mode', ProxyMode.MANUAL_PROXY)]
