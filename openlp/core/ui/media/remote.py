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
The :mod:`~openlp.core.ui.media` module contains various API endpoints
"""
import logging
from flask import abort, Blueprint

from openlp.core.api import app
from openlp.core.api.lib import login_required
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)

v2_media = Blueprint('v2-media-controller', __name__)


@v2_media.route('/play', methods=['POST'])
@login_required
def media_play():
    log.debug('media_play')
    live = Registry().get('live_controller')
    if live.service_item.name != 'media':
        abort(400)
    status = live.mediacontroller_live_play.emit()
    log.debug(f'media_play return {status}')
    if status:
        return '', 202
    abort(400)


@v2_media.route('/pause', methods=['POST'])
@login_required
def media_pause():
    log.debug('media_pause')
    live = Registry().get('live_controller')
    if live.service_item.name != 'media':
        abort(400)
    status = live.mediacontroller_live_pause.emit()
    log.debug(f'media_pause return {status}')
    if status:
        return '', 202
    abort(400)


@v2_media.route('/stop', methods=['POST'])
@login_required
def media_stop():
    log.debug('media_stop')
    live = Registry().get('live_controller')
    if live.service_item.name != 'media':
        abort(400)
    status = live.mediacontroller_live_stop.emit()
    log.debug(f'media_stop return {status}')
    if status:
        return '', 202
    abort(400)


def register_views():
    app.register_blueprint(v2_media, url_prefix='/api/v2/media/')
