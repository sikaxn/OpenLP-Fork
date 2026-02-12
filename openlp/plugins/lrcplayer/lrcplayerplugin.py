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
The LRC Player plugin.
"""
import logging

from openlp.core.common.i18n import translate
from openlp.core.db.manager import DBManager
from openlp.core.lib import build_icon
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.plugins.lrcplayer.lib.db import init_schema
from openlp.plugins.lrcplayer.lib.mediaitem import LrcPlayerMediaItem
from openlp.plugins.lrcplayer.lib.lrcplayertab import LrcPlayerTab


log = logging.getLogger(__name__)


class LrcplayerPlugin(Plugin):
    """
    Plugin for audio + LRC synchronized lyric slides.
    """
    log.info('LrcPlayer Plugin loaded')

    def __init__(self):
        super().__init__('lrcplayer', LrcPlayerMediaItem, LrcPlayerTab)
        self.weight = -4
        self.db_manager = DBManager('lrcplayer', init_schema)
        self.icon_path = UiIcons().music
        self.icon = build_icon(self.icon_path)
        State().add_service(self.name, self.weight, is_plugin=True)
        State().update_pre_conditions(self.name, self.check_pre_conditions())

    def check_pre_conditions(self):
        return self.db_manager.session is not None

    @staticmethod
    def about():
        return translate(
            'LrcPlayerPlugin',
            '<strong>LRC Player Plugin</strong><br />'
            'Loads an audio file and a matching LRC lyric file, then projects lyrics '
            'as synchronized slides while the audio plays.'
        )

    def set_plugin_text_strings(self):
        self.text_strings[StringContent.Name] = {
            'singular': translate('LrcPlayerPlugin', 'LRC Song', 'name singular'),
            'plural': translate('LrcPlayerPlugin', 'LRC Songs', 'name plural')
        }
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('LrcPlayerPlugin', 'LRC Player', 'container title')
        }
        tooltips = {
            'load': translate('LrcPlayerPlugin', 'Load LRC songs.'),
            'import': '',
            'new': translate('LrcPlayerPlugin', 'Add a new LRC song.'),
            'edit': translate('LrcPlayerPlugin', 'Edit the selected LRC song.'),
            'delete': translate('LrcPlayerPlugin', 'Delete the selected LRC song.'),
            'preview': translate('LrcPlayerPlugin', 'Preview the selected LRC song.'),
            'live': translate('LrcPlayerPlugin', 'Send the selected LRC song live.'),
            'service': translate('LrcPlayerPlugin', 'Add the selected LRC song to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)

    def finalise(self):
        log.info('LrcPlayer Finalising')
        self.db_manager.finalise()
        super().finalise()
