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
Provide HTML Tag management and Formatting Tag access class
"""
import json

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry


class FormattingTags(object):
    """
    Static Class for HTML Tags to be access around the code the list is managed by the Options Tab.
    """
    html_expands = []

    @staticmethod
    def get_html_tags():
        """
        Provide access to the html_expands list.
        """
        if not FormattingTags.html_expands:
            FormattingTags.load_tags()
        return FormattingTags.html_expands

    @staticmethod
    def save_html_tags(new_tags):
        """
        Saves all formatting tags except protected ones

        `new_tags`
            The tags to be saved..
        """
        # Formatting Tags were also known as display tags.
        Registry().get('settings').setValue('formattingTags/html_tags', json.dumps(new_tags) if new_tags else '')

    @staticmethod
    def load_tags():
        """
        Load the Tags from store so can be used in the system or used to update the display.
        """
        temporary_tags = [tag for tag in FormattingTags.html_expands if tag.get('temporary')]
        FormattingTags.html_expands = []
        base_tags = [
            {
                'desc': translate('OpenLP.FormattingTags', 'Red'),
                'start tag': '{r}',
                'start html': '<span style="-webkit-text-fill-color:red">',
                'end tag': '{/r}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Black'),
                'start tag': '{b}',
                'start html': '<span style="-webkit-text-fill-color:black">',
                'end tag': '{/b}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Blue'),
                'start tag': '{bl}',
                'start html': '<span style="-webkit-text-fill-color:blue">',
                'end tag': '{/bl}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Yellow'),
                'start tag': '{y}',
                'start html': '<span style="-webkit-text-fill-color:yellow">',
                'end tag': '{/y}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Green'),
                'start tag': '{g}',
                'start html': '<span style="-webkit-text-fill-color:green">',
                'end tag': '{/g}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Pink'),
                'start tag': '{pk}',
                'start html': '<span style="-webkit-text-fill-color:#FFC0CB">',
                'end tag': '{/pk}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Orange'),
                'start tag': '{o}',
                'start html': '<span style="-webkit-text-fill-color:#FFA500">',
                'end tag': '{/o}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Purple'),
                'start tag': '{pp}',
                'start html': '<span style="-webkit-text-fill-color:#800080">',
                'end tag': '{/pp}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'White'),
                'start tag': '{w}',
                'start html': '<span style="-webkit-text-fill-color:white">',
                'end tag': '{/w}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Superscript'),
                'start tag': '{su}',
                'start html': '<sup>',
                'end tag': '{/su}',
                'end html': '</sup>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Subscript'),
                'start tag': '{sb}',
                'start html': '<sub>',
                'end tag': '{/sb}',
                'end html': '</sub>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Paragraph'),
                'start tag': '{p}',
                'start html': '<p>',
                'end tag': '{/p}',
                'end html': '</p>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Bold'),
                'start tag': '{st}',
                'start html': '<strong>',
                'end tag': '{/st}',
                'end html': '</strong>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Italics'),
                'start tag': '{it}',
                'start html': '<em>',
                'end tag': '{/it}',
                'end html': '</em>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Underline'),
                'start tag': '{u}',
                'start html': '<span style="text-decoration: underline;">',
                'end tag': '{/u}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'UpperCase'),
                'start tag': '{uc}',
                'start html': '<span style="text-transform: uppercase;">',
                'end tag': '{/uc}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Preview'),
                'start tag': '{preview}',
                'start html': '<span style="opacity: 0.6; font-size: 80%;">',
                'end tag': '{/preview}',
                'end html': '</span>',
                'protected': True,
                'temporary': False,
                'hidden': False
            },
            {
                'desc': translate('OpenLP.FormattingTags', 'Break'),
                'start tag': '{br}',
                'start html': '<br>',
                'end tag': '',
                'end html': '',
                'protected': True,
                'temporary': False,
                'hidden': False
            }
        ]
        # Append the base tags.
        FormattingTags.add_html_tags(base_tags)
        FormattingTags.add_html_tags(temporary_tags)
        user_expands_string = str(Registry().get('settings').value('formattingTags/html_tags'))
        # If we have some user ones added them as well
        if user_expands_string:
            user_tags = json.loads(user_expands_string)
            for tag in user_tags:
                if 'hidden' not in tag.keys():
                    tag['hidden'] = False
            FormattingTags.add_html_tags(user_tags)

    @staticmethod
    def add_html_tags(tags):
        """
        Add a list of tags to the list.

        :param tags: The list with tags to add.
            Each **tag** has to be a ``dict`` and should have the following keys:

            * desc
                The formatting tag's description, e. g. **Red**

            * start tag
                The start tag, e. g. ``{r}``

            * end tag
                The end tag, e. g. ``{/r}``

            * start html
                The start html tag. For instance ``<span style="-webkit-text-fill-color:red">``

            * end html
                The end html tag. For example ``</span>``

            * protected
                A boolean stating whether this is a build-in tag or not. Should be ``True`` in most cases.

            * temporary
                A temporary tag will not be saved, but is also considered when displaying text containing the tag. It
                has to be a ``boolean``.
        """
        FormattingTags.html_expands.extend(tags)

    @staticmethod
    def remove_html_tag(tag_id):
        """
        Removes an individual html_expands tag.
        """
        FormattingTags.html_expands.pop(tag_id)
