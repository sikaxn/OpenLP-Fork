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
:mod: `tests.interfaces.openlp_core_ui.test_projectorsourceform` module

Tests for the Projector Source Select form.
"""
import pytest
from unittest.mock import patch

from PySide6.QtWidgets import QDialog

from openlp.core.projectors.constants import PJLINK_DEFAULT_CODES, PJLINK_DEFAULT_SOURCES
from openlp.core.projectors.db import Projector, ProjectorDB
from openlp.core.projectors.sourceselectform import SourceSelectSingle, source_group
from tests.resources.projector.data import TEST1_DATA, TEST_DB


@pytest.fixture()
def projector_env(settings):
    with patch('openlp.core.projectors.db.init_url') as mocked_init_url:
        mocked_init_url.return_value = 'sqlite:///{}'.format(TEST_DB)
        projectordb = ProjectorDB()
    # Retrieve/create a database record
    projector = projectordb.get_projector_by_ip(TEST1_DATA['ip'])
    if not projector:
        projectordb.add_projector(projector=Projector(**TEST1_DATA))
        projector = projectordb.get_projector_by_ip(TEST1_DATA['ip'])
    projector.dbid = projector.id
    projector.db_item = projector
    yield projector, projectordb
    projectordb.session.close()
    del projectordb
    del projector


def build_source_dict():
    """
    Builds a source dictionary to verify source_group returns a valid dictionary of dictionary items

    :returns: dictionary of valid PJLink source codes grouped by PJLink source group
    """
    test_group = {}
    for group in PJLINK_DEFAULT_SOURCES.keys():
        test_group[group] = {}
    for key in PJLINK_DEFAULT_CODES:
        test_group[key[0]][key] = PJLINK_DEFAULT_CODES[key]
    return test_group


def test_source_dict():
    """
    Test that source list dict returned from sourceselectform module is a valid dict with proper entries
    """
    # GIVEN: A list of inputs
    codes = []
    for item in PJLINK_DEFAULT_CODES.keys():
        codes.append(item)
    codes.sort()

    # WHEN: projector.sourceselectform.source_select() is called
    check = source_group(codes, PJLINK_DEFAULT_CODES)

    # THEN: return dictionary should match test dictionary
    assert check == build_source_dict(), "Source group dictionary should match test dictionary"


@patch.object(QDialog, 'exec')
def test_source_select_edit_button(mocked_qdialog, projector_env):
    """
    Test source select form edit has Ok, Cancel, Reset, and Revert buttons
    """
    # GIVEN: Initial setup and mocks
    projector = projector_env[0]
    projectordb = projector_env[1]
    projector.source_available = ['11', ]
    projector.source = '11'

    # WHEN we create a source select widget and set edit=True
    select_form = SourceSelectSingle(parent=None, projectordb=projectordb)
    select_form.edit = True
    select_form.exec(projector=projector)

    # THEN: Verify all 4 buttons are available
    assert len(select_form.button_box.buttons()) == 4, \
        'SourceSelect dialog box should have "OK", "Cancel", "Rest", and "Revert" buttons available'


@patch.object(QDialog, 'exec')
def test_source_select_noedit_button(mocked_qdialog, projector_env):
    """
    Test source select form view has OK and Cancel buttons only
    """
    # GIVEN: Initial setup and mocks
    projector = projector_env[0]
    projectordb = projector_env[1]
    projector.source_available = ['11', ]
    projector.source = '11'

    # WHEN we create a source select widget and set edit=False
    select_form = SourceSelectSingle(parent=None, projectordb=projectordb)
    select_form.edit = False
    select_form.exec(projector=projector)

    # THEN: Verify only 2 buttons are available
    assert len(select_form.button_box.buttons()) == 2, \
        'SourceSelect dialog box should only have "OK" and "Cancel" buttons available'
