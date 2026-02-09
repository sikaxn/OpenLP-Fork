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
Package to test the openlp.plugins.songs.forms.topicsform package.
"""
import pytest

from PySide6 import QtWidgets

from openlp.core.common.registry import Registry
from openlp.plugins.songs.forms.topicsform import TopicsForm


@pytest.fixture()
def form(settings):
    main_window = QtWidgets.QMainWindow()
    Registry().register('main_window', main_window)
    frm = TopicsForm()
    yield frm
    del frm
    del main_window


def test_ui_defaults(form):
    """
    Test the TopicsForm defaults are correct
    """
    assert form.name_edit.text() == '', 'The first name edit should be empty'


def test_get_name_property(form):
    """
    Test that getting the name property on the TopicsForm works correctly
    """
    # GIVEN: A topic name to set
    topic_name = 'Salvation'

    # WHEN: The name_edit's text is set
    form.name_edit.setText(topic_name)

    # THEN: The name property should have the correct value
    assert form.name == topic_name, 'The name property should be correct'


def test_set_name_property(form):
    """
    Test that setting the name property on the TopicsForm works correctly
    """
    # GIVEN: A topic name to set
    topic_name = 'James'

    # WHEN: The name property is set
    form.name = topic_name

    # THEN: The name_edit should have the correct value
    assert form.name_edit.text() == topic_name, 'The topic name should be set correctly'
