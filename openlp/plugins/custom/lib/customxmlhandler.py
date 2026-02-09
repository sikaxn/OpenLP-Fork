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
The :mod:`customxmlhandler` module provides the XML functionality for custom
slides

The basic XML is of the format::

    <?xml version="1.0" encoding="UTF-8"?>
    <song version="1.0">
        <lyrics language="en">
            <verse type="chorus" label="1">
                <![CDATA[ ... ]]>
            </verse>
        </lyrics>
    </song>
"""

import copy
import logging
from lxml import etree, objectify


log = logging.getLogger(__name__)


class CustomXML(object):
    """
    This class builds and parses the XML used to describe custom slides.
    """
    log.info('CustomXML Loaded')

    def __init__(self, xml=None):
        """
        Set up the custom builder.
        """
        if xml:
            if xml.startswith('<?xml'):
                xml = xml[38:]
            self.custom_xml = objectify.fromstring(xml)
        else:
            # Create the minidom document if no input given
            self.custom_xml = objectify.fromstring('<song version="1.0" />')
            self.add_lyrics_to_song()

    def add_lyrics_to_song(self):
        """
        Set up and add a ``<lyrics>`` tag which contains the lyrics of the
        custom item.
        """
        # Create the main <lyrics> element
        self.lyrics = etree.SubElement(self.custom_xml, 'lyrics')
        self.lyrics.set('language', 'en')

    def add_verse_to_lyrics(self, verse_type, number, content):
        """
        Add a verse to the ``<lyrics>`` tag.

        :param verse_type: A string denoting the type of verse. Possible values are "Chorus", "Verse", "Bridge",
            and "Custom".
        :param number:  An integer denoting the number of the item, for example: verse 1.
        :param content: The actual text of the verse to be stored.

        """
        verse = etree.Element('verse', type=str(verse_type), label=str(number))
        verse.text = etree.CDATA(content)
        self.lyrics.append(verse)

    def get_verses(self):
        """
        Iterates through the verses in the XML and returns a list of verses and their attributes.
        """
        xml_iter = self.custom_xml.getiterator()
        verse_list = []
        for element in xml_iter:
            if element.tag == 'verse':
                if element.text is None:
                    element.text = ''
                verse_list.append([element.attrib, str(element.text)])
        return verse_list

    def add_title_and_credit(self, title, credit):
        """
        Add title and credit to xml
        :param title: Title to add
        :param credit: Credit to add
        """
        # set title
        title_element = self.custom_xml.find('title')
        if not title_element:
            title_element = etree.Element('title')
            self.custom_xml.append(title_element)
        title_element.text = title
        # set credit
        credit_element = self.custom_xml.find('credit')
        if not credit_element:
            credit_element = etree.Element('credit')
            self.custom_xml.append(credit_element)
        credit_element.text = credit

    def get_title(self):
        """
        Return title if one exists
        """
        title_element = self.custom_xml.find('title')
        if not title_element:
            return ''
        return title_element.text

    def get_credit(self):
        """
        Return credit if one exists
        """
        credit_element = self.custom_xml.find('credit')
        if not credit_element:
            return ''
        return credit_element.text

    def _dump_xml(self, keep_title_and_credit=False):
        """
        Debugging aid to dump XML so that we can see what we have.
        """
        if keep_title_and_credit:
            return etree.tostring(self.custom_xml, encoding='utf-8', xml_declaration=True, pretty_print=True)
        else:
            tmp_xml = copy.copy(self.custom_xml)
            title_element = tmp_xml.find('title')
            if title_element:
                tmp_xml.remove(title_element)
            credit_element = tmp_xml.find('credit')
            if credit_element:
                tmp_xml.remove(credit_element)
            return etree.tostring(tmp_xml, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def extract_xml(self, keep_title_and_credit=False):
        """
        Extract our newly created XML custom.
        """
        if keep_title_and_credit:
            return etree.tostring(self.custom_xml, encoding='utf-8', xml_declaration=True)
        else:
            tmp_xml = copy.copy(self.custom_xml)
            title_element = tmp_xml.find('title')
            if title_element:
                tmp_xml.remove(title_element)
            credit_element = tmp_xml.find('credit')
            if credit_element:
                tmp_xml.remove(credit_element)
            return etree.tostring(tmp_xml, encoding='utf-8', xml_declaration=True)
