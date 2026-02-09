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
The :mod:`presentationmanager` module provides the functionality for importing
Presentationmanager song files into the current database.
"""
import logging
import re

from lxml import etree, objectify

from openlp.core.common import get_file_encoding
from openlp.core.common.i18n import translate
from openlp.core.widgets.wizard import WizardStrings
from openlp.plugins.songs.lib.importers.songimport import SongImport

log = logging.getLogger(__name__)


class PresentationManagerImport(SongImport):
    """
    The :class:`PresentationManagerImport` class provides OpenLP with the
    ability to import Presentationmanager song files.
    """
    def do_import(self):
        self.import_wizard.progress_bar.setMaximum(len(self.import_source))
        for file_path in self.import_source:
            if self.stop_import_flag:
                return
            self.import_wizard.increment_progress_bar(WizardStrings.ImportingType.format(source=file_path.name))
            self.process_xml(file_path)

    def _get_attr(self, elem, name):
        """
        Due to PresentationManager's habit of sometimes capitilising the first letter of an element, we have to do
        some gymnastics.
        """
        if hasattr(elem, name):
            return str(getattr(elem, name))
        name = name[0].upper() + name[1:]
        if hasattr(elem, name):
            return str(getattr(elem, name))
        else:
            return ''

    def process_xml(self, file_path, encoding=None):
        if encoding is not None:
            # Open file with detected encoding and remove encoding declaration
            text = file_path.read_text(encoding=encoding)
            text = re.sub(r'.+\?>\n', '', text)
            try:
                tree = etree.fromstring(text, parser=etree.XMLParser(recover=True))
            except ValueError:
                log.exception('XML syntax error in file {name}'.format(name=file_path))
                self.log_error(file_path,
                               translate('SongsPlugin.PresentationManagerImport',
                                         'File is not in XML-format, which is the only format supported.'))
                return
        else:
            try:
                tree = etree.parse(str(file_path), parser=etree.XMLParser(recover=True))
            except etree.XMLSyntaxError:
                # Try to detect encoding and use it
                self.process_xml(file_path, get_file_encoding(file_path))
                return

        file_str = etree.tostring(tree)
        if not file_str:
            log.exception('Could not find XML in file {name}'.format(name=file_path))
            self.log_error(file_path, translate('SongsPlugin.PresentationManagerImport',
                                                'File is not in XML-format, which is the only format supported.'))
            return
        try:
            root = objectify.fromstring(file_str)
        except etree.XMLSyntaxError:
            if encoding is None:
                # Try to detect encoding and use it
                self.process_xml(file_path, get_file_encoding(file_path))
            return

        try:
            self.process_song(root, file_path)
        except AttributeError:
            log.exception('XML syntax error in file {name}'.format(name=file_path))
            self.log_error(file_path, translate('SongsPlugin.PresentationManagerImport',
                                                'File is not a valid PresentationManager XMl file.'))

    def process_song(self, root, file_path):
        """
        :param root:
        :param pathlib.Path file_path: Path to the file to process
        :rtype: None
        """
        self.set_defaults()
        attrs = None
        if hasattr(root, 'attributes'):
            attrs = root.attributes
        elif hasattr(root, 'Attributes'):
            attrs = root.Attributes
        if attrs is not None:
            self.title = self._get_attr(root.attributes, 'title')
            self.add_author(self._get_attr(root.attributes, 'author'))
            self.copyright = self._get_attr(root.attributes, 'copyright')
            self.ccli_number = self._get_attr(root.attributes, 'ccli_number')
            self.comments = str(root.attributes.comments) if hasattr(root.attributes, 'comments') else None
        verse_order_list = []
        verse_count = {}
        duplicates = []
        for verse in root.verses.verse:
            original_verse_def = verse.get('id')
            # Presentation Manager stores duplicate verses instead of a verse order.
            # We need to create the verse order from that.
            is_duplicate = False
            if original_verse_def in duplicates:
                is_duplicate = True
            else:
                duplicates.append(original_verse_def)
            if original_verse_def.startswith("Verse"):
                verse_def = 'v'
            elif original_verse_def.startswith("Chorus") or original_verse_def.startswith("Refrain"):
                verse_def = 'c'
            elif original_verse_def.startswith("Bridge"):
                verse_def = 'b'
            elif original_verse_def.startswith("End"):
                verse_def = 'e'
            else:
                verse_def = 'o'
            if not is_duplicate:  # Only increment verse number if no duplicate
                verse_count[verse_def] = verse_count.get(verse_def, 0) + 1
            verse_def = '{verse}{count:d}'.format(verse=verse_def, count=verse_count[verse_def])
            if not is_duplicate:  # Only add verse if no duplicate
                self.add_verse(str(verse).strip(), verse_def)
            verse_order_list.append(verse_def)

        self.verse_order_list = verse_order_list
        if not self.finish():
            self.log_error(file_path.name)
