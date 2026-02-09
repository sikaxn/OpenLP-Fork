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
The Media plugin
"""
import logging
import os
from pathlib import Path

from openlp.core.common import sha256_file_hash
from openlp.core.common.i18n import translate
from openlp.core.lib import build_icon
from openlp.core.db.manager import DBManager
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media import parse_stream_path

from openlp.plugins.media.lib.db import Item, init_schema
from openlp.plugins.media.lib.mediaitem import MediaMediaItem


log = logging.getLogger(__name__)


# Some settings starting with "media" are in core, because they are needed for core functionality.

class MediaPlugin(Plugin):
    """
    The media plugin adds the ability to playback audio and video content.
    """
    log.info('{name} MediaPlugin loaded'.format(name=__name__))

    def __init__(self):
        super().__init__('media', MediaMediaItem)
        self.manager = DBManager(plugin_name='media', init_schema=init_schema)
        self.weight = -6
        self.icon_path = UiIcons().video
        self.icon = build_icon(self.icon_path)
        # passed with drag and drop messages
        self.dnd_id = 'Media'
        State().add_service(self.name, self.weight, requires='mediacontroller', is_plugin=True)
        State().update_pre_conditions(self.name, self.check_pre_conditions())

    def initialise(self):
        """
        Override the inherited initialise() method in order to upgrade the media before trying to load it
        """
        media_files = self.settings.value('media/media files') or []
        for filename in media_files:
            if not isinstance(filename, (Path, str)):
                continue
            if isinstance(filename, Path):
                name = filename.name
                filename = str(filename)
            elif filename.startswith('devicestream:') or filename.startswith('networkstream:'):
                _, name, _, _ = parse_stream_path(filename)
            else:
                name = os.path.basename(filename)
            item = Item(name=name, file_path=filename)
            if not filename.startswith('devicestream:') and not filename.startswith('networkstream:') \
               and not filename.startswith('optical:'):
                file_path = Path(filename)
                if file_path.is_file() and file_path.exists():
                    item.file_hash = sha256_file_hash(file_path)
            self.manager.save_object(item)
        self.settings.remove('media/media files')
        super().initialise()

    def check_pre_conditions(self):
        """
        Check the plugin can run and the media controller is available.
        """
        return State().is_module_active('mediacontroller')

    @staticmethod
    def about():
        """
        Return the about text for the plugin manager
        """
        about_text = translate('MediaPlugin', '<strong>Media Plugin</strong>'
                               '<br />The media plugin provides playback of audio and video.')
        return about_text

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('MediaPlugin', 'Media', 'name singular'),
            'plural': translate('MediaPlugin', 'Media', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('MediaPlugin', 'Media', 'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': translate('MediaPlugin', 'Load new media.'),
            'import': '',
            'new': translate('MediaPlugin', 'Add new media.'),
            'edit': translate('MediaPlugin', 'Edit the selected media.'),
            'delete': translate('MediaPlugin', 'Delete the selected media.'),
            'preview': translate('MediaPlugin', 'Preview the selected media.'),
            'live': translate('MediaPlugin', 'Send the selected media live.'),
            'service': translate('MediaPlugin', 'Add the selected media to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)

    def finalise(self):
        """
        Time to tidy up on exit.
        """
        log.info('Media Finalising')
        self.media_controller.finalise()
        Plugin.finalise(self)
