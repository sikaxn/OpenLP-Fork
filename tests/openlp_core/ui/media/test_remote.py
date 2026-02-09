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
Package to test the openlp.core.ui.media.remote package.
"""
import pytest
from unittest.mock import MagicMock

from openlp.core.api import app as flask_app
from openlp.core.common.registry import Registry
from openlp.core.ui.media.remote import media_play, media_pause, media_stop, register_views


def test_media_play_valid(settings):
    # GIVEN: A loaded service with media set up
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'media'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    Registry().register('live_controller', live_controller)
    # WHEN: Play is pressed
    ret = media_play()
    # THEN: We should have a successful outcome
    assert live_controller.mediacontroller_live_play.emit.call_count == 1, 'Should have be called once'
    assert ret[1] == 202, 'Should be a valid call'


def test_media_play_not_media(settings):
    # GIVEN: A loaded service with songs not media
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'songs'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    Registry().register('live_controller', live_controller)
    # WHEN: Play is pressed
    with pytest.raises(Exception) as e:
        _ = media_play()
    # THEN: We should have a rejected outcome
    assert e.value.code == 400, 'Should be an invalid call'
    assert live_controller.mediacontroller_live_play.emit.call_count == 0, 'Should have be not have been called'


def test_media_play_call_fail(settings):
    # GIVEN: A loaded service with no media_controller
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'media'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    live_controller.mediacontroller_live_play.emit.return_value = False
    Registry().register('live_controller', live_controller)
    # WHEN: Play is pressed
    with pytest.raises(Exception) as e:
        _ = media_play()
    # THEN: We should have a rejected outcome
    assert e.value.code == 400, 'Should be an invalid call'
    assert live_controller.mediacontroller_live_play.emit.call_count == 1, 'Should have be called once'


def test_media_pause_valid(settings):
    # GIVEN: A loaded service with media set up
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'media'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    Registry().register('live_controller', live_controller)
    # WHEN: Pause is pressed
    ret = media_pause()
    # THEN: We should have a successful outcome
    assert live_controller.mediacontroller_live_pause.emit.call_count == 1, 'Should have be called once'
    assert ret[1] == 202, 'Should be a valid call'


def test_media_pause_not_media(settings):
    # GIVEN: A loaded service with songs not media
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'songs'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    Registry().register('live_controller', live_controller)
    # WHEN: Pause is pressed
    with pytest.raises(Exception) as e:
        _ = media_pause()
    # THEN: We should have a rejected outcome
    assert e.value.code == 400, 'Should be an invalid call'
    assert live_controller.mediacontroller_live_pause.emit.call_count == 0, 'Should have be not have been called'


def test_media_pause_call_fail(settings):
    # GIVEN: A loaded service with no media_controller
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'media'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    live_controller.mediacontroller_live_pause.emit.return_value = False
    Registry().register('live_controller', live_controller)
    # WHEN: Pause is pressed
    with pytest.raises(Exception) as e:
        _ = media_pause()
    # THEN: We should have a rejected outcome
    assert e.value.code == 400, 'Should be an invalid call'
    assert live_controller.mediacontroller_live_pause.emit.call_count == 1, 'Should have be called once'


def test_media_stop_valid(settings):
    # GIVEN: A loaded service with media set up
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'media'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    Registry().register('live_controller', live_controller)
    # WHEN: Stop is pressed
    ret = media_stop()
    # THEN: We should have a successful outcome
    assert live_controller.mediacontroller_live_stop.emit.call_count == 1, 'Should have be called once'
    assert ret[1] == 202, 'Should be a valid call'


def test_media_stop_not_media(settings):
    # GIVEN: A loaded service with songs not media
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'songs'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    Registry().register('live_controller', live_controller)
    # WHEN: Stop is pressed
    with pytest.raises(Exception) as e:
        _ = media_stop()
    # THEN: We should have a rejected outcome
    assert e.value.code == 400, 'Should be an invalid call'
    assert live_controller.mediacontroller_live_stop.emit.call_count == 0, 'Should have be not have been called'


def test_media_stop_call_fail(settings):
    # GIVEN: A loaded service with no media_controller
    settings.setValue('api/authentication enabled', False)
    service_item = MagicMock()
    service_item.name = 'media'
    live_controller = MagicMock()
    live_controller.service_item = service_item
    live_controller.mediacontroller_live_stop.emit.return_value = False
    Registry().register('live_controller', live_controller)
    # WHEN: Stop is pressed
    with pytest.raises(Exception) as e:
        _ = media_stop()
    # THEN: We should have a rejected outcome
    assert e.value.code == 400, 'Should be an invalid call'
    assert live_controller.mediacontroller_live_stop.emit.call_count == 1, 'Should have be called once'


@pytest.mark.skip(reason='We need to refactor the register_views() methods')
def test_register():
    # GIVEN: A blank setup
    # WHEN: I register the views for media
    register_views()
    # THEN: The following elements should have been defined.
    assert len(flask_app.blueprints['v2-media-controller'].deferred_functions) == 3, \
        'we should have 3 functions defined'
    assert 'v2-media-controller.media_play' in flask_app.view_functions, 'we should the play defined'
    assert 'v2-media-controller.media_pause' in flask_app.view_functions, 'we should the pause defined'
    assert 'v2-media-controller.media_stop' in flask_app.view_functions, 'we should the stop defined'
