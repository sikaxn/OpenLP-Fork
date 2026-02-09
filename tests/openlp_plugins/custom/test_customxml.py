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

from openlp.plugins.custom.lib.customxmlhandler import CustomXML


custom_xml_test1 = '<?xml version="1.0" encoding="utf-8"?><song version="1.0"><lyrics language="en"/>' \
    '<lyrics language="en"><verse type="custom" label="1"><![CDATA[Slide\nnumber 1]]></verse>' \
    '<verse type="custom" label="2"><![CDATA[Slide\nnumber 2]]></verse></lyrics></song>'
custom_xml_output1 = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<song version="1.0"><lyrics language="en">' \
    b'<verse type="custom" label="1"><![CDATA[Custom slide 1]]></verse></lyrics></song>'
custom_xml_output2 = b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<song version="1.0"><lyrics language="en">' \
    b'<verse type="custom" label="1"><![CDATA[Custom slide 1]]></verse></lyrics><title>Test Title</title>' \
    b'<credit>Super User</credit></song>'


def test_custom_xml_import():
    # GIVEN: A CustomXML based on a xml string
    custom_xml = CustomXML(custom_xml_test1)

    # WHEN: get_verses() is called on the created CustomXML
    custom_verses = custom_xml.get_verses()

    # THEN: The returned verse list should be as expected from the input
    assert custom_verses == [[{'type': 'custom', 'label': '1'}, 'Slide\nnumber 1'],
                             [{'type': 'custom', 'label': '2'}, 'Slide\nnumber 2']]


def test_custom_xml_creation():
    # GIVEN: A "empty" CustomXML with inserted verses
    custom_xml = CustomXML()
    custom_xml.add_verse_to_lyrics('custom', 1, 'Custom slide 1')

    # WHEN: get_verses() is called on the created CustomXML
    custom_verses = custom_xml.get_verses()

    # THEN: The returned verse list should be as expected from the input
    assert custom_verses == [[{'type': 'custom', 'label': '1'}, 'Custom slide 1']]
    assert custom_xml.extract_xml() == custom_xml_output1


def test_custom_xml_title_credit():
    # GIVEN: A "empty" CustomXML
    custom_xml = CustomXML()

    # WHEN: title or credit has not been added

    # THEN: get_title() and get_credit()
    assert custom_xml.get_credit() == ''
    assert custom_xml.get_title() == ''

    # WHEN: title or credit has been added
    custom_xml.add_verse_to_lyrics('custom', 1, 'Custom slide 1')
    custom_xml.add_title_and_credit('Test Title', 'Super User')

    # THEN: The returned verse list should be as expected from the input
    assert custom_xml.get_credit() == 'Super User'
    assert custom_xml.get_title() == 'Test Title'
    assert custom_xml.extract_xml(True) == custom_xml_output2
