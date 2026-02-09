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
Main API views for OpenLP.
"""

import os

from flask import Blueprint, send_from_directory
from openlp.core.common.applocation import AppLocation
from openlp.core.common.mime import get_mime_type

main_views = Blueprint('main', __name__)


@main_views.route('/', defaults={'path': ''})
@main_views.route('/<path>')
def index(path):
    """
    Serve the main index file or other files from the remotes directory.

    :param path: The path to the file.
    :type path: Path
    :return: The requested file or index.html.
    :rtype: flask.Response
    """
    directory = AppLocation.get_section_data_path('remotes')
    if os.path.isfile(directory / path):
        return send_from_directory(str(directory),
                                   path, mimetype=get_mime_type(path))
    return send_from_directory(str(directory),
                               'index.html', mimetype='text/html')


@main_views.route('/assets/<path:path>')
def assets(path):
    """
    Serve assets.

    :param path: The path to the asset file.
    :type path: str
    :return: The asset file.
    :rtype: flask.Response
    """
    directory = AppLocation.get_section_data_path('remotes')
    return send_from_directory(str(directory / 'assets'),
                               path, mimetype=get_mime_type(path))


@main_views.route('/media/<path:path>')
def media(path):
    """
    Serve media files.

    :param path: The path to the media file.
    :type path: str
    :return: The media file.
    :rtype: flask.Response
    """
    directory = AppLocation.get_section_data_path('remotes')
    return send_from_directory(str(directory / 'media'),
                               path, mimetype=get_mime_type(path))


@main_views.route('/stage/<path>/')
def stages(path):
    """
    Serve stage HTML file.

    :param path: The path to the stage directory.
    :type path: Path
    :return: The stage HTML file.
    :rtype: flask.Response
    """
    directory = AppLocation.get_section_data_path('stages')
    return send_from_directory(str(directory / path),
                               'stage.html', mimetype='text/html')


@main_views.route('/stage/<path:path>/<file>')
def stage_assets(path, file):
    """
    Serve stage asset files.

    :param path: The path to the stage directory.
    :type path: Path
    :param file: The asset file name.
    :type file: str
    :return: The stage asset file.
    :rtype: flask.Response
    """
    directory = AppLocation.get_section_data_path('stages')
    return send_from_directory(str(directory / path),
                               file, mimetype=get_mime_type(file))
