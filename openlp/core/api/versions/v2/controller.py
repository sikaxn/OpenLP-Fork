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
The :mod:`~openlp.core.api.versions.v2.controller` module provides the
API v2 endpoints for the controller.
"""

import json
import logging

from flask import jsonify, request, abort, Blueprint, Response

from openlp.core.api.lib import login_required, xml_response
from openlp.core.common import ThemeLevel
from openlp.core.common.json import OpenLPJSONEncoder
from openlp.core.common.registry import Registry
from openlp.core.lib import image_to_data_uri

controller_views = Blueprint('controller', __name__)
log = logging.getLogger(__name__)


def _get_companion_manager():
    """
    Get the active Companion manager widget from the main window registry.

    :return: Companion manager instance.
    """
    main_window = Registry().get('main_window')
    manager = getattr(main_window, 'companion_manager_contents', None) if main_window else None
    if manager is None:
        log.error('Companion manager is not available')
        abort(503)
    return manager


def _find_companion(manager, companion_id):
    """
    Resolve a companion record by id.

    :param manager: Companion manager instance.
    :param companion_id: Companion id string.
    :return: Companion dictionary or None.
    """
    for companion in getattr(manager, 'companions', []):
        if str(companion.get('id', '')) == str(companion_id):
            return companion
    return None


def _to_bool(value):
    """
    Convert common payload values to boolean.

    :param value: Raw payload value.
    :return: Parsed bool or None if invalid.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ('1', 'true', 'yes', 'on'):
            return True
        if lowered in ('0', 'false', 'no', 'off'):
            return False
    return None


@controller_views.route('/live-items')
def controller_live_items():
    """
    This endpoint returns the current live service item with all slides,
    marking the currently selected slide.

    :return: JSON representation of the current live service item.
    :rtype: flask.Response
    """
    log.debug('controller-v2-live-items')
    live_item = _get_live_item_with_all_slides()
    json_live_item = json.dumps(live_item, cls=OpenLPJSONEncoder)
    return Response(json_live_item, mimetype='application/json')


@controller_views.route('/live-items-xml')
def controller_live_items_xml():
    """
    This endpoint returns the current live service item with all slides as XML,
    marking the currently selected slide.

    :return: XML representation of the current live service item.
    :rtype: flask.Response
    """
    log.debug('controller-v2-live-items-xml')
    live_item = _get_live_item_with_all_slides()
    return xml_response(live_item, root_name='live_item')


def _get_live_item_with_all_slides():
    """
    Build the live item payload with all slides and selected slide metadata.

    :return: A dictionary representation of the live service item.
    :rtype: dict
    """
    live_controller = Registry().get('live_controller')
    current_item = live_controller.service_item
    live_item = {}
    if current_item:
        live_item = current_item.to_dict()
        live_item['slides'][live_controller.selected_row]['selected'] = True
        live_item['id'] = str(current_item.unique_identifier)
    return live_item


@controller_views.route('/live-item')
def controller_live_item():
    """
    This endpoint returns the current live service item with the currently
    selected slide only.

    :return: JSON representation of the current live service item.
    :rtype: flask.Response
    """
    log.debug('controller-v2-live-item')
    live_controller = Registry().get('live_controller')
    current_item = live_controller.service_item
    live_item = {}
    if current_item:
        live_item = current_item.to_dict(True, live_controller.selected_row)
        live_item['id'] = str(current_item.unique_identifier)
    json_live_item = json.dumps(live_item, cls=OpenLPJSONEncoder)
    return Response(json_live_item, mimetype='application/json')


@controller_views.route('/current-live-line')
def controller_current_live_line():
    """
    Return the current live slide text as plain text.

    :return: The text of the currently selected live slide.
    :rtype: flask.Response
    """
    log.debug('controller-v2-current-live-line')
    return Response(_get_current_live_line(), mimetype='text/plain')


def _get_current_live_line():
    """
    Get the text for the currently selected live slide.

    :return: Current live slide text, or an empty string if unavailable.
    :rtype: str
    """
    live_controller = Registry().get('live_controller')
    current_item = live_controller.service_item
    if not current_item:
        return ''
    selected_row = live_controller.selected_row or 0
    live_item = current_item.to_dict(True, selected_row)
    slides = live_item.get('slides', [])
    if not slides:
        return ''
    slide = slides[0]
    return str(slide.get('text', ''))


@controller_views.route('/show', methods=['POST'])
@login_required
def controller_set():
    """
    Sets the current slide in the live controller.

    :return: HTTP return code.
    :rtype: flask.Response
    """
    log.debug('controller-v2-show-post')
    data = request.json
    if not data:
        log.error('Missing request data')
        abort(400)
    num = data.get('id', -1)
    Registry().get('live_controller').slidecontroller_live_set.emit([num])
    return '', 204


@controller_views.route('/progress', methods=['POST'])
@login_required
def controller_direction():
    """
    Moves the current slide in the live controller forward or backward.

    :return: HTTP return code.
    :rtype: flask.Response
    """
    log.debug('controller-v2-progress-post')
    data = request.json
    if not data:
        log.error('Missing request data')
        abort(400)
    action = data.get('action', '').lower()
    if action not in ['next', 'previous']:
        log.error('Invalid action passed %s', action)
        abort(400)
    getattr(Registry().get('live_controller'), f'slidecontroller_live_{action}').emit()
    return '', 204


@controller_views.route('/theme-level', methods=['GET'])
@login_required
def get_theme_level():
    """
    Get the current theme level.

    :return: The current theme level.
    :rtype: flask.Response
    """
    log.debug('controller-v2-theme-level-get')
    theme_level = Registry().get('settings').value('themes/theme level')
    if theme_level == ThemeLevel.Global:
        theme_level = 'global'
    elif theme_level == ThemeLevel.Service:
        theme_level = 'service'
    elif theme_level == ThemeLevel.Song:
        theme_level = 'song'
    return jsonify(theme_level)


@controller_views.route('/theme-level', methods=['POST'])
@login_required
def set_theme_level():
    """
    Set the current theme level.

    :return: HTTP return code.
    :rtype: flask.Response
    """
    log.debug('controller-v2-theme-level-post')
    data = request.json
    if not data:
        log.error('Missing request data')
        abort(400)
    theme_level = ''
    try:
        theme_level = str(data.get("level"))
    except ValueError:
        log.error('Invalid data passed %s', theme_level)
        abort(400)
    if theme_level == 'global':
        Registry().get('settings').setValue('themes/theme level', 1)
    elif theme_level == 'service':
        Registry().get('settings').setValue('themes/theme level', 2)
    elif theme_level == 'song':
        Registry().get('settings').setValue('themes/theme level', 3)
    else:
        log.error('Unsupported data passed %s', theme_level)
        abort(400)
    Registry().get('theme_manager').theme_level_updated.emit()
    return '', 204


@controller_views.route('/themes', methods=['GET'])
def get_themes():
    """
    Gets a list of all existing themes.

    :return: A list of all existing themes.
    :rtype: flask.Response
    """
    log.debug('controller-v2-themes-get')
    theme_level = Registry().get('settings').value('themes/theme level')
    theme_list = []
    current_theme = ''
    if theme_level == ThemeLevel.Global:
        current_theme = Registry().get('theme_manager').global_theme
    if theme_level == ThemeLevel.Service:
        current_theme = Registry().get('service_manager').service_theme
    # Gets and appends theme list
    themes = Registry().execute('get_theme_names')
    try:
        for theme in themes[0]:
            # Gets the background path, get the thumbnail from it, and encode it to a base64 data uri
            theme_path = Registry().get('theme_manager').theme_path
            encoded_thumb = image_to_data_uri(theme_path / 'thumbnails' / f'{theme}.png')
            # Append the theme to the list
            theme_list.append({
                'name': theme,
                'selected': False,
                'thumbnail': encoded_thumb
            })
        for i in theme_list:
            if i["name"] == current_theme:
                i["selected"] = True
    except IndexError:
        log.error('Missing theme passed %s', themes)
    return jsonify(theme_list)


@controller_views.route('/themes/<theme_name>', methods=['GET'])
def get_theme_data(theme_name):
    """
    Get a theme's data.

    :param theme_name: The name of the theme to get.
    :type theme_name: str
    :return: The theme's data.
    :rtype: flask.Response
    """
    log.debug('controller-v2-theme-data-get %s', theme_name)
    themes = Registry().execute('get_theme_names')[0]
    if theme_name not in themes:
        log.error('Requested non-existent theme')
        abort(404)
    theme_data = Registry().get('theme_manager').get_theme_data(theme_name).export_theme_self_contained(True)
    return Response(theme_data, mimetype='application/json')


@controller_views.route('/live-theme', methods=['GET'])
def get_live_theme_data():
    """
    Get the live theme's data.

    :return: The live theme's data.
    :rtype: flask.Response
    """
    log.debug('controller-v2-live-theme-data-get')
    live_service_item = Registry().get('live_controller').service_item
    if live_service_item:
        theme_data = live_service_item.get_theme_data()
    else:
        theme_data = Registry().get('theme_manager').get_theme_data(None)
    self_contained_theme = theme_data.export_theme_self_contained(True)
    return Response(self_contained_theme, mimetype='application/json')


@controller_views.route('/theme', methods=['GET'])
def get_theme():
    """
    Get the current theme name.

    :return: The current theme name.
    :rtype: flask.Response
    """
    log.debug('controller-v2-theme-get')
    theme_level = Registry().get('settings').value('themes/theme level')
    if theme_level == ThemeLevel.Service:
        theme = Registry().get('settings').value('servicemanager/service theme')
    else:
        theme = Registry().get('settings').value('themes/global theme')
    return jsonify(theme)


@controller_views.route('/theme', methods=['POST'])
@login_required
def set_theme():
    """
    Set the current theme.

    :return: HTTP return code.
    :rtype: flask.Response
    """
    log.debug('controller-v2-themes-post')
    data = request.json
    theme = ''
    theme_level = Registry().get('settings').value('themes/theme level')
    if not data:
        log.error('Missing request data')
        abort(400)
    try:
        theme = str(data.get('theme'))
    except ValueError:
        log.error('Invalid data passed %s', theme)
        abort(400)
    if theme_level == ThemeLevel.Global:
        Registry().get('settings').setValue('themes/global theme', theme)
        Registry().get('theme_manager').theme_update_global.emit()
    elif theme_level == ThemeLevel.Service:
        Registry().get('settings').setValue('servicemanager/service theme', theme)
        Registry().get('service_manager').theme_update_service.emit()
    elif theme_level == ThemeLevel.Song:
        log.error('Unimplemented method')
        return '', 501
    return '', 204


@controller_views.route('/clear/<controller>', methods=['POST'])
@login_required
def controller_clear(controller):
    """
    Clears the slide controller display.

    :param controller: The Live or Preview controller.
    :type controller: str
    :return: HTTP return code.
    :rtype: flask.Response
    """
    log.debug('controller-v2-clear-get %s', controller)
    if controller in ['live', 'preview']:
        getattr(Registry().get(f'{controller}_controller'), f'slidecontroller_{controller}_clear').emit()
        return '', 204
    return '', 404


@controller_views.route('/companion-connection-status', methods=['GET'])
def companion_connection_status():
    """
    Return all configured companion servers and their current connection status.
    """
    log.debug('controller-v2-companion-connection-status-get')
    manager = _get_companion_manager()
    companions = []
    for companion in getattr(manager, 'companions', []):
        companion_id = companion.get('id', '')
        connection = manager.connections.get(companion_id, {})
        companions.append({
            'id': str(companion_id),
            'ip': str(companion.get('ip', '')),
            'port': int(companion.get('port', 0) or 0),
            'method': str(companion.get('method', '')).upper(),
            'status': str(connection.get('status', 'Disconnected')),
            'default': bool(companion_id == manager.default_companion_id),
            'connected': bool(manager._is_connected(companion))
        })
    return jsonify({
        'companions': companions,
        'selected_companion_id': getattr(manager, 'selected_companion_id', None)
    })


@controller_views.route('/companion-connection', methods=['POST'])
@login_required
def companion_connection():
    """
    Connect or disconnect a configured companion server.
    """
    log.debug('controller-v2-companion-connection-post')
    data = request.json
    if not data:
        log.error('Missing request data')
        abort(400)
    companion_id = data.get('id') or data.get('companion_id')
    action = str(data.get('action', '')).strip().lower()
    if not companion_id or action not in ('connect', 'disconnect'):
        log.error('Invalid companion connection payload: %s', data)
        abort(400)
    manager = _get_companion_manager()
    companion = _find_companion(manager, companion_id)
    if companion is None:
        log.error('Unknown companion id: %s', companion_id)
        abort(404)
    if action == 'connect':
        manager._connect(companion)
    else:
        manager._disconnect(companion)
        manager._set_status(companion.get('id'), 'Disconnected')
    return '', 204


@controller_views.route('/companion-autotrigger-status', methods=['GET'])
def companion_autotrigger_status():
    """
    Return current companion auto-trigger state.
    """
    log.debug('controller-v2-companion-autotrigger-status-get')
    manager = _get_companion_manager()
    return jsonify({'enabled': bool(getattr(manager, 'autotrigger_enabled', False))})


@controller_views.route('/companion-autotrigger', methods=['POST'])
@login_required
def companion_autotrigger():
    """
    Toggle companion auto-trigger on or off.
    """
    log.debug('controller-v2-companion-autotrigger-post')
    data = request.json
    if not data:
        log.error('Missing request data')
        abort(400)
    manager = _get_companion_manager()
    enabled = _to_bool(data.get('enabled'))
    if enabled is None:
        action = str(data.get('action', '')).strip().lower()
        if action in ('toggle',):
            enabled = not bool(manager.autotrigger_enabled)
        elif action in ('on', 'enable', 'enabled'):
            enabled = True
        elif action in ('off', 'disable', 'disabled'):
            enabled = False
        else:
            log.error('Invalid companion auto-trigger payload: %s', data)
            abort(400)
    manager.autotrigger_enabled = bool(enabled)
    manager._save_companions()
    manager._update_button_colours()
    manager._refresh_live_autotrigger_markers()
    manager._refresh_autotrigger_list_labels()
    return '', 204


@controller_views.route('/companion', methods=['GET'])
def companion_control_page():
    """
    Serve a simple web UI for companion connect/disconnect and auto-trigger control.
    """
    log.debug('controller-v2-companion-page-get')
    html = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>OpenLP Companion Control</title>
  <style>
    body { font-family: sans-serif; margin: 20px; }
    .row { margin-bottom: 10px; }
    button { margin-right: 6px; }
    select, input { min-width: 280px; }
    #status { margin-top: 16px; white-space: pre-wrap; font-family: monospace; }
  </style>
</head>
<body>
  <h2>Companion Control</h2>
  <div class="row">
    <label for="token">Auth Token (optional)</label><br>
    <input id="token" type="text" placeholder="Only needed if API auth is enabled">
  </div>
  <div class="row">
    <label for="companions">Companion Server</label><br>
    <select id="companions"></select>
  </div>
  <div class="row">
    <button id="refresh">Refresh</button>
    <button id="connect">Connect</button>
    <button id="disconnect">Disconnect</button>
  </div>
  <div class="row">
    <strong>Auto Trigger:</strong>
    <span id="autotrigger-state">Unknown</span>
  </div>
  <div class="row">
    <button id="autotrigger-on">Auto Trigger ON</button>
    <button id="autotrigger-off">Auto Trigger OFF</button>
    <button id="autotrigger-toggle">Toggle Auto Trigger</button>
  </div>
  <div id="status"></div>
  <script>
    const companionsEl = document.getElementById('companions');
    const statusEl = document.getElementById('status');
    const tokenEl = document.getElementById('token');
    const autotriggerStateEl = document.getElementById('autotrigger-state');

    function headers(withJson = false) {
      const h = {};
      const token = tokenEl.value.trim();
      if (token) h['Authorization'] = token;
      if (withJson) h['Content-Type'] = 'application/json';
      return h;
    }

    async function refreshAll() {
      const [connRes, trigRes] = await Promise.all([
        fetch('/api/v2/controller/companion-connection-status'),
        fetch('/api/v2/controller/companion-autotrigger-status')
      ]);
      const conn = await connRes.json();
      const trig = await trigRes.json();
      companionsEl.innerHTML = '';
      (conn.companions || []).forEach(c => {
        const o = document.createElement('option');
        o.value = c.id;
        o.textContent = `${c.ip}:${c.port} (${c.method}) - ${c.status}${c.default ? ' [Default]' : ''}`;
        companionsEl.appendChild(o);
      });
      if (conn.selected_companion_id) {
        companionsEl.value = conn.selected_companion_id;
      }
      autotriggerStateEl.textContent = trig.enabled ? 'ON' : 'OFF';
      statusEl.textContent = JSON.stringify({connection: conn, autotrigger: trig}, null, 2);
    }

    async function postJson(url, body) {
      const res = await fetch(url, {method: 'POST', headers: headers(true), body: JSON.stringify(body)});
      if (!res.ok) throw new Error(`${url} failed: ${res.status}`);
      await refreshAll();
    }

    document.getElementById('refresh').addEventListener('click', refreshAll);
    document.getElementById('connect').addEventListener('click', () =>
      postJson('/api/v2/controller/companion-connection', {id: companionsEl.value, action: 'connect'}));
    document.getElementById('disconnect').addEventListener('click', () =>
      postJson('/api/v2/controller/companion-connection', {id: companionsEl.value, action: 'disconnect'}));
    document.getElementById('autotrigger-on').addEventListener('click', () =>
      postJson('/api/v2/controller/companion-autotrigger', {enabled: true}));
    document.getElementById('autotrigger-off').addEventListener('click', () =>
      postJson('/api/v2/controller/companion-autotrigger', {enabled: false}));
    document.getElementById('autotrigger-toggle').addEventListener('click', () =>
      postJson('/api/v2/controller/companion-autotrigger', {action: 'toggle'}));

    refreshAll().catch(err => { statusEl.textContent = String(err); });
  </script>
</body>
</html>
"""
    return Response(html, mimetype='text/html')
