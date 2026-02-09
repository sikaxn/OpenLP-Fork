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
The :mod:`powerpraiseimport` module provides the functionality for importing
Powerpraise song files into the current database.
"""
import logging

from lxml import objectify, etree

from openlp.core.common.i18n import translate
from openlp.core.widgets.wizard import WizardStrings
from openlp.plugins.songs.lib.importers.songimport import SongImport
from openlp.plugins.songs.lib.ui import SongStrings

log = logging.getLogger(__name__)


class PowerPraiseImport(SongImport):
    """
    The :class:`PowerpraiseImport` class provides OpenLP with the
    ability to import Powerpraise song files.
    """
    def do_import(self):
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            self.import_wizard.increment_progress_bar(WizardStrings.ImportingType.format(source=file_path.name))
            with file_path.open('rb') as xml_file:
                try:
                    root = objectify.parse(xml_file).getroot()
                except etree.XMLSyntaxError:
                    log.exception('XML syntax error in file {name}'.format(name=file_path))
                    self.log_error(file_path, SongStrings().XMLSyntaxError)
                    continue
                except UnicodeDecodeError:
                    log.exception('Unreadable characters in {name}'.format(name=file_path))
                    self.log_error(file_path, SongStrings().XMLSyntaxError)
                    continue
                self.process_song(root, file_path)

    def process_song(self, root, file_path):
        self.set_defaults()
        try:
            self.title = str(root.general.title)
            verse_order_list = []
            verse_count = {}
            for item in root.order.item:
                verse_order_list.append(str(item))
            for part in root.songtext.part:
                original_verse_def = part.get('caption')
                # There are some predefined verse defitions in PowerPraise, try to parse these
                if original_verse_def.startswith("Strophe") or original_verse_def.startswith("Teil"):
                    verse_def = 'v'
                elif original_verse_def.startswith("Refrain"):
                    verse_def = 'c'
                elif original_verse_def.startswith("Bridge"):
                    verse_def = 'b'
                elif original_verse_def.startswith("Schluss"):
                    verse_def = 'e'
                else:
                    verse_def = 'o'
                verse_count[verse_def] = verse_count.get(verse_def, 0) + 1
                verse_def = '{verse}{count:d}'.format(verse=verse_def, count=verse_count[verse_def])
                verse_text = []
                for slide in part.slide:
                    if not hasattr(slide, 'line'):
                        continue  # No content
                    for line in slide.line:
                        verse_text.append(str(line))
                self.add_verse('\n'.join(verse_text), verse_def)
                # Update verse name in verse order list
                for i in range(len(verse_order_list)):
                    if verse_order_list[i].lower() == original_verse_def.lower():
                        verse_order_list[i] = verse_def

            self.verse_order_list = verse_order_list

            for text in root.information.copyright['text']:
                if not hasattr(text, 'line'):
                    continue
                for line in text.line:
                    if not line:
                        continue
                    if line.text.startswith('©') or line.text.lower().startswith('(c)') or \
                            line.text.lower().startswith('copyright'):
                        self.add_copyright(line.text)
                    else:
                        self.add_author(line.text)

            if not self.finish():
                self.log_error(file_path)
        except AttributeError:
            self.log_error(file_path, translate('SongsPlugin.PowerPraiseImport',
                                                'Invalid PowerPraise song file. Missing needed tag.'))
