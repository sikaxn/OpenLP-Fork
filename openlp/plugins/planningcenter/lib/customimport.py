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
The :mod:`~openlp.plugins.planningcenter.lib.customimport` module provides
a function that imports a single custom slide into the database and returns
the database ID of the slide.  This mimics the implementation for SongPlugin
that was used to import songs from Planning Center.
"""
import re

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.lib.formattingtags import FormattingTags
from openlp.plugins.custom.lib.customxmlhandler import CustomXML
from openlp.plugins.custom.lib.db import CustomSlide


class PlanningCenterCustomImport(object):
    """
    Creates a custom slide and returns the database ID of that slide

    :param item_title: The text to put on the slide.
    :param html_details: The "details" element from PCO, with html formatting
    :param theme_name:  The theme_name to use for the slide.
    """
    def add_slide(self, item_title, html_details, theme_name):
        sxml = CustomXML()
        slide_content = ''
        if html_details is None:
            slide_content = item_title
        else:
            # we need non-html here, but the input is html
            slide_content = self._process_details(html_details)
        sxml.add_verse_to_lyrics('custom', str(1), slide_content)
        custom_slide = CustomSlide(title=item_title, text=str(sxml.extract_xml(), 'utf-8'), credits='pco',
                                   theme_name=theme_name)
        custom = Registry().get('custom')
        custom_db_manager = custom.plugin.db_manager
        custom_db_manager.save_object(custom_slide)
        return custom_slide.id
    """
    Converts the "details" section of a PCO slide into text suitable for
    slides in OLP

    :param html_details: The html_details string from the PCO API
    """
    def _process_details(self, html_details):
        # convert <br> into new lines
        html_details = re.sub(r'<br>', '\n', html_details)
        # covert formatting tags from list to dict to I can do arbitrary lookups
        FormattingTags.load_tags()
        openlp_formatting_tags = {}
        for formatting_tag in FormattingTags.get_html_tags():
            openlp_formatting_tags[formatting_tag['desc']] = {}
            openlp_formatting_tags[formatting_tag['desc']]['start tag'] = formatting_tag['start tag']
            openlp_formatting_tags[formatting_tag['desc']]['end tag'] = formatting_tag['end tag']
        # convert bold
        html_details = re.sub(r'<strong>(.*?)</strong>',
                              r"{start}\1{end}".format(
                                  start=openlp_formatting_tags[
                                      translate('OpenLP.FormattingTags', 'Bold')]['start tag'],
                                  end=openlp_formatting_tags[
                                      translate('OpenLP.FormattingTags', 'Bold')]['end tag']),
                              html_details)
        # convert underline
        html_details = re.sub(r'<span style="text-decoration: underline;">(.*?)</span>',
                              r"{start}\1{end}".format(
                                  start=openlp_formatting_tags[
                                      translate('OpenLP.FormattingTags', 'Underline')]['start tag'],
                                  end=openlp_formatting_tags[
                                      translate('OpenLP.FormattingTags', 'Underline')]['end tag']),
                              html_details)
        # convert italics
        html_details = re.sub(r'<em>(.*?)</em>',
                              r"{start}\1{end}".format(
                                  start=openlp_formatting_tags[
                                      translate('OpenLP.FormattingTags', 'Italics')]['start tag'],
                                  end=openlp_formatting_tags[
                                      translate('OpenLP.FormattingTags', 'Italics')]['end tag']),
                              html_details)
        # convert PlanningCenter colors to OpenLP base tags
        color_lookup = {
            'Red': 'ff0000',
            'Black': '000000',
            'Blue': '0000ff',
            'Yellow': 'ffff00',
            'Green': '008000',
            'Pink': 'ff99cc',
            'Orange': 'ff6600',
            'Purple': '800080',
            'White': 'ffffff',
        }
        for color in color_lookup.keys():
            html_details = re.sub(r'<span style="color: #{number};">(.*?)</span>'.format(number=color_lookup[color]),
                                  r"{start}\1{end}".format(
                                      start=openlp_formatting_tags[
                                          translate('OpenLP.FormattingTags', color)]['start tag'],
                                      end=openlp_formatting_tags[
                                          translate('OpenLP.FormattingTags', color)]['end tag']),
                                  html_details)
        # throw away the rest of the html
        html_details = re.sub(r'(<!--.*?-->|<[^>]*>)', '', html_details)
        return html_details
