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
This module contains tests for the lib submodule of the Images plugin.
"""
import pytest
import shutil
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from sqlalchemy import create_engine, select, table, column

from openlp.core.common.applocation import AppLocation
from openlp.core.db.upgrades import upgrade_db
from openlp.plugins.images.lib import upgrade
from tests.utils.constants import RESOURCE_PATH


@pytest.fixture()
def temp_path():
    tmp_path = Path(mkdtemp())
    yield tmp_path
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture()
def db_url():
    tmp_path = Path(mkdtemp())
    db_path = RESOURCE_PATH / 'images' / 'image-v0.sqlite'
    db_tmp_path = tmp_path / 'image-v0.sqlite'
    shutil.copyfile(db_path, db_tmp_path)
    yield 'sqlite:///' + str(db_tmp_path)
    shutil.rmtree(tmp_path, ignore_errors=True)


def test_image_filenames_table(db_url, settings):
    """
    Test that the ImageFilenames table is correctly upgraded to the latest version
    """
    # GIVEN: An unversioned image database
    with patch.object(AppLocation, 'get_data_path', return_value=Path('/', 'test', 'dir')), \
            patch('openlp.plugins.images.lib.upgrade.sha256_file_hash') as mocked_sha256_file_hash:
        mocked_sha256_file_hash.return_value = 'abcd'
        # WHEN: Initalising the database manager

        upgrade_db(db_url, upgrade)

        engine = create_engine(db_url)
        conn = engine.connect()
        md = table('metadata', column('key'), column('value'))
        assert conn.execute(select(md.c.value).where(md.c.key == 'version')).scalar() == '2'
