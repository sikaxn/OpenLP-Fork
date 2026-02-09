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
The :mod:`upgrade` module provides a way for the database and schema that is the backend for the Bibles plugin.
"""
import logging

from PySide6 import QtWidgets
from sqlalchemy import Table
from sqlalchemy.sql.expression import delete, select

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.common.settings import ProxyMode
from openlp.core.db.upgrades import get_upgrade_op


log = logging.getLogger(__name__)
__version__ = 2


# TODO: When removing an upgrade path the ftw-data needs updating to the minimum supported version
def upgrade_1(session, metadata):
    """
    Version 1 upgrade.

    This upgrade renamed a number of keys to a single naming convention.
    """
    log.info('No upgrades to perform')      # pragma: no cover


def upgrade_2(session, metadata):
    """
    Remove the individual proxy settings, after the implementation of central proxy settings.
    Added in 2.5 (3.0 development)
    """
    settings = Registry().get('settings')
    op = get_upgrade_op(session)
    metadata_table = Table('metadata', metadata, autoload_with=metadata.bind)
    proxy, = session.execute(
        select(metadata_table.c.value).where(metadata_table.c.key == 'proxy_server')).first() or ('', )
    if proxy and not \
            (proxy == settings.value('advanced/proxy http') or proxy == settings.value('advanced/proxy https')):
        http_proxy = ''
        https_proxy = ''
        name, = session.execute(select(metadata_table.c.value).where(metadata_table.c.key == 'name')).first()
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(translate('BiblesPlugin', f'The proxy server {proxy} was found in the bible {name}.<br>'
                                                  f'Would you like to set it as the proxy for OpenLP?'))
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Question)
        msg_box.addButton(QtWidgets.QMessageBox.StandardButton.No)
        http_button = msg_box.addButton('http', QtWidgets.QMessageBox.ButtonRole.ActionRole)
        both_button = msg_box.addButton(translate('BiblesPlugin', 'both'), QtWidgets.QMessageBox.ButtonRole.ActionRole)
        https_button = msg_box.addButton('https', QtWidgets.QMessageBox.ButtonRole.ActionRole)
        msg_box.setDefaultButton(both_button)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        if clicked_button in [http_button, both_button]:
            http_proxy = proxy
            settings.setValue('advanced/proxy http', proxy)
        if clicked_button in [https_button, both_button]:
            https_proxy = proxy
            settings.setValue('advanced/proxy https', proxy)
        if http_proxy or https_proxy:
            username, = session.execute(
                select(metadata_table.c.value).where(metadata_table.c.key == 'proxy_username')).scalar().first()
            proxy, = session.execute(
                select(metadata_table.c.value).where(metadata_table.c.key == 'proxy_password')).scalar().first()
            settings.setValue('advanced/proxy username', username)
            settings.setValue('advanced/proxy password', proxy)
            settings.setValue('advanced/proxy mode', ProxyMode.MANUAL_PROXY)

    op.execute(delete(metadata_table).where(metadata_table.c.key == 'proxy_server'))
    op.execute(delete(metadata_table).where(metadata_table.c.key == 'proxy_username'))
    op.execute(delete(metadata_table).where(metadata_table.c.key == 'proxy_password'))
