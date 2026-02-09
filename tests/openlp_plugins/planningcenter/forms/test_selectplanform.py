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
Package to test the openlp.plugins.planningcenter.forms.selectplanform package.
"""
import os
import re
from datetime import date, datetime
from unittest.mock import patch, MagicMock

import pytest
from PySide6 import QtTest, QtCore

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.state import State
from openlp.core.ui.servicemanager import ServiceManager
from openlp.plugins.bibles.bibleplugin import BiblePlugin
from openlp.plugins.bibles.lib.mediaitem import BibleMediaItem
from openlp.plugins.custom.customplugin import CustomPlugin
from openlp.plugins.custom.lib.mediaitem import CustomMediaItem
from openlp.plugins.planningcenter.forms.selectplanform import SelectPlanForm
from openlp.plugins.planningcenter.planningcenterplugin import PlanningCenterPlugin
from openlp.plugins.songs.lib.mediaitem import SongMediaItem
from openlp.plugins.songs.songsplugin import SongsPlugin
from tests.utils.constants import TEST_RESOURCES_PATH

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), TEST_RESOURCES_PATH, 'planningcenter'))


@pytest.fixture
def plugin(registry: Registry, settings: Settings, state: State):
    settings.setValue('planningcenter/application_id', 'test-id')
    settings.setValue('planningcenter/secret', 'test-secret')
    registry.register('theme_manager', MagicMock())
    yield PlanningCenterPlugin()


@pytest.fixture
def form(plugin: PlanningCenterPlugin):
    form_ = SelectPlanForm()
    form_.planning_center_api.airplane_mode = True
    form_.planning_center_api.airplane_mode_directory = TEST_PATH
    yield form_


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.date')
def test_initial_defaults(mocked_date: MagicMock, mocked_exec: MagicMock, form: SelectPlanForm):
    """
    Test that the SelectPlanForm displays with correct defaults
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    # a theme manager with mocked themes, and a fake date = Sunday (7/29/2018)
    # need to always return 9/29/2019 for date.today()
    mocked_date.today.return_value = date(2019, 9, 29)
    mocked_date.side_effect = lambda *args, **kw: date(*args, **kw)
    # WHEN: The form is shown
    form.exec()
    # THEN: The correct count of service types show up in the combo box
    assert form.service_type_combo_box.count() == 2, 'The service_type_combo_box contains 2 items'
    # The first service type is selected
    assert form.service_type_combo_box.currentText() == 'gbf', 'The service_type_combo_box defaults to "gbf"'
    # the selected plan is today (the mocked date is a Sunday). Set to lowercase beacuse in some locales
    # months is not capitalized.
    assert form.plan_selection_combo_box.currentText() == 'September 29, 2019 - Morning Worship', \
        'Incorrect default date selected for Plan Date'
    # count the number of themes listed and make sure it matches expected value
    assert form.song_theme_selection_combo_box.count() == 0, 'Count of song themes is incorrect'
    assert form.slide_theme_selection_combo_box.count() == 0, 'Count of custom slide themes is incorrect'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QMessageBox.warning')
def test_warning_messagebox_shown_for_bad_credentials(mocked_warning: MagicMock, mocked_exec: MagicMock,
                                                      form: SelectPlanForm):
    """
    Test that if we don't have good credentials, then it will show a QMessageBox with a warning in it
    """
    # GIVEN: A SelectPlanForm instance with airplane mode enabled, resources, available,
    #        mocked check_credentials function to return ''
    with patch.object(form.planning_center_api, 'check_credentials', return_value=''):
        # WHEN: form is displayed
        form.exec()
        # THEN: we should have called a warning messagebox
        mocked_warning.assert_called_once()


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
def test_disable_import_buttons(mocked_exec: MagicMock, form: SelectPlanForm):
    """
    Test that the import buttons are disabled when the "Select Plan Date" element in the
    Plan Selection List is selected.
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available, and the form
    form.exec()
    # WHEN: The Select Plan combo box is set to "Select Plan Date"
    index = form.plan_selection_combo_box.findText('Select Plan Date')
    form.plan_selection_combo_box.setCurrentIndex(index)
    # THEN: "Import New" and "Refresh Service" buttons become inactive
    assert not form.import_as_new_button.isEnabled(), '"Import as New" button should be disabled'
    assert not form.update_existing_button.isEnabled(), '"Refresh Service" button should be disabled'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.date')
def test_default_plan_date_is_next_sunday(mocked_date: MagicMock, mocked_exec: MagicMock, form: SelectPlanForm):
    """
    Test that the SelectPlanForm displays Next Sunday's Date by Default
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    # a theme manager with mocked themes, and a fake date =  (9/24/2019)
    # need to always return 9/24/2019 for date.today()
    mocked_date.today.return_value = date(2019, 9, 24)
    mocked_date.side_effect = lambda *args, **kw: date(*args, **kw)
    form.exec()
    # WHEN: The second (index=1) service type is selected
    form.service_type_combo_box.setCurrentIndex(1)
    # THEN: The plan selection date is 9/29 (the following Sunday)
    assert form.plan_selection_combo_box.currentText() == 'September 29, 2019', \
        'The next Sunday\'s Date is not selected in the plan_selection_combo_box'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.PlanningCenterAPI.get_plan_list')
def test_plan_selection_combobox_item_texts(mocked_get_plan_list: MagicMock, mocked_exec: MagicMock,
                                            form: SelectPlanForm):
    """
    Test that plan titles in the plan selection combobox are set correctly
    """

    # GIVEN: a SelectPlanForm and a PlanningCenterAPI that returns mocked plans
    mocked_get_plan_list.return_value = [
        # plan with no title
        {'id': '1', 'attributes': {'dates': 'January 1, 2019',
                                   'sort_date': '2019-01-01T10:30:00Z', 'title': None,
                                   'series_title': None}},
        # plan with 'title'
        {'id': '2', 'attributes': {'dates': 'January 2, 2019',
                                   'sort_date': '2019-01-02T10:30:00Z', 'title': 'Test',
                                   'series_title': None}},
        # plan with 'title' and 'series_title'
        {'id': '3', 'attributes': {'dates': 'January 3, 2019',
                                   'sort_date': '2019-01-03T10:30:00Z', 'title': 'Test',
                                   'series_title': 'Series'}},
        # plan with 'series title'
        {'id': '4', 'attributes': {'dates': 'January 4, 2019',
                                   'sort_date': '2019-01-04T10:30:00Z', 'title': None,
                                   'series_title': 'Series'}},
    ]
    # WHEN: the form is executed, causing plans to be loaded
    form.exec()
    # THEN: the plan titles in the plan select combobox should be assigned correctly
    assert form.plan_selection_combo_box.count() == 5
    assert form.plan_selection_combo_box.itemText(1) == 'January 1, 2019'
    assert form.plan_selection_combo_box.itemText(2) == 'January 2, 2019 - Test'
    assert form.plan_selection_combo_box.itemText(3) == 'January 3, 2019 - Test'
    assert form.plan_selection_combo_box.itemText(4) == 'January 4, 2019 - Series'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
def test_service_type_changed_called_when_service_type_combo_changed(mocked_exec: MagicMock, form: SelectPlanForm):
    """
    Test that the "on_service_type_combobox_changed" function is executed when the
    service_type_combobox is changed
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available
    form.exec()
    # WHEN: The Service Type combo is set to index 1
    form.service_type_combo_box.setCurrentIndex(1)
    # THEN: The on_service_type_combobox_changed function is called
    assert form.plan_selection_combo_box.count() > 0, 'Plan Selection Combo Box is not empty'
    assert form.plan_selection_combo_box.itemText(0) == 'Select Plan Date', 'Plan Combo Box has default text'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
def test_plan_selection_changed_called_when_plan_selection_combo_changed(mocked_exec: MagicMock,
                                                                         form: SelectPlanForm):
    """
    Test that the "on_plan_selection_combobox_changed" function is executed when the
    plan_selection_combobox is changed
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    form.exec()

    # WHEN: The Service Type combo is set to index 1
    form.service_type_combo_box.setCurrentIndex(1)
    form.plan_selection_combo_box.setCurrentIndex(1)

    # THEN: The import and update buttons should be enabled
    assert form.import_as_new_button.isEnabled(), 'Import button should be enabled'
    assert form.update_existing_button.isEnabled(), 'Update button should be enabled'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
def test_settings_tab_displayed_when_edit_auth_button_clicked(mocked_exec: MagicMock, registry: Registry,
                                                              form: SelectPlanForm):
    """
    Test that the settings dialog is displayed when the edit_auth_button is clicked
    """
    # GIVEN: A SelectPlanForm instance with airplane mode enabled and resources available
    mocked_settings_form = MagicMock()
    registry.register('settings_form', mocked_settings_form)
    form.exec()

    # WHEN: the edit_auth_button is clicked
    QtTest.QTest.mouseClick(form.edit_auth_button, QtCore.Qt.MouseButton.LeftButton)

    # THEN: Settings
    mocked_settings_form.exec.assert_called_once()


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.SelectPlanForm._do_import')
def test_import_function_called_when_import_button_clicked(mocked_do_import: MagicMock, mocked_exec: MagicMock,
                                                           form: SelectPlanForm):
    """
    Test that the "on_import_as_new_button_clicked" function is executed when the
    "Import New" button is clicked
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    form.exec()
    # WHEN: The Service Type combo is set to index 1 and the Select Plan combo box is set
    # to index 1 and the "Import New" button is clicked
    form.service_type_combo_box.setCurrentIndex(1)
    form.plan_selection_combo_box.setCurrentIndex(4)
    QtTest.QTest.mouseClick(form.import_as_new_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN: The on_import_as_new_button_cliced function is called
    mocked_do_import.assert_called_with(update=False)


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.warning_message_box')
@patch('openlp.plugins.planningcenter.lib.songimport.PlanningCenterSongImport.finish')
@patch('openlp.plugins.planningcenter.lib.customimport.CustomSlide')
@patch('openlp.plugins.planningcenter.forms.selectplanform.parse_reference')
@patch('openlp.plugins.planningcenter.forms.selectplanform.date')
def test_service_imported_when_import_button_clicked(mocked_date: MagicMock, mocked_parse_reference: MagicMock,
                                                     MockCustomSlide: MagicMock, mocked_finish: MagicMock,
                                                     mocked_warning_box: MagicMock, mocked_exec: MagicMock,
                                                     form: SelectPlanForm):
    """
    Test that a service is imported when the "Import New" button is clicked
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    # mocked out "on_new_service_clicked"
    # need to always return 9/29/2019 for date.today()
    mocked_date.today.return_value = date(2019, 9, 29)
    mocked_date.side_effect = lambda *args, **kw: date(*args, **kw)
    form.exec()
    mocked_bible_plugin = MagicMock()
    mocked_bible_plugin.version_combo_box.currentText.return_value = 'mocked_bible'
    Registry().register('service_manager', MagicMock())
    Registry().register('plugin_manager', MagicMock())
    Registry().register('songs', MagicMock())
    Registry().register('bibles', mocked_bible_plugin)
    Registry().register('custom', MagicMock())
    # WHEN: The Service Type combo is set to index 1 and the Select Plan combo box is set to
    # index 1 and the "Import New" button is clicked
    form.service_type_combo_box.setCurrentIndex(1)
    QtTest.QTest.mouseClick(form.import_as_new_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN: There should be 5 service items added, 1 song, 3 custom slides (one is a bible
    # title slide), and 1 bible verse
    mocked_finish.assert_called_once()
    assert MockCustomSlide.call_count == 4, '4 custom slide added via custom_media_item'
    assert mocked_parse_reference.call_count == 2, '2 bible verses submitted for parsing'
    assert mocked_warning_box.call_count == 0, 'No warnings triggered'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.warning_message_box')
@patch('openlp.plugins.planningcenter.lib.songimport.PlanningCenterSongImport.finish')
@patch('openlp.plugins.planningcenter.lib.customimport.CustomSlide')
@patch('openlp.plugins.planningcenter.forms.selectplanform.parse_reference')
@patch('openlp.plugins.planningcenter.forms.selectplanform.date')
def test_service_refreshed_when_refresh_button_clicked(mocked_date: MagicMock, mocked_parse_reference: MagicMock,
                                                       MockCustomSlide: MagicMock, mocked_finish: MagicMock,
                                                       mocked_warning_box: MagicMock, mocked_exec: MagicMock,
                                                       form: SelectPlanForm):
    """
    Test that a service is refreshed when the "Refresh Service" button is clicked
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    # mocked out "on_new_service_clicked"
    # need to always return 9/29/2019 for date.today()
    mocked_date.today.return_value = date(2019, 9, 29)
    mocked_date.side_effect = lambda *args, **kw: date(*args, **kw)
    form.exec()
    mocked_bible_plugin = MagicMock()
    mocked_bible_plugin.version_combo_box.currentText.return_value = 'mocked_bible'
    Registry().register('service_manager', MagicMock())
    Registry().register('plugin_manager', MagicMock())
    Registry().register('songs', MagicMock())
    Registry().register('bibles', mocked_bible_plugin)
    Registry().register('custom', MagicMock())
    # WHEN: The Service Type combo is set to index 1 and the Select Plan combo box is
    # set to index 1 and the "Update" button is clicked
    form.service_type_combo_box.setCurrentIndex(1)
    QtTest.QTest.mouseClick(form.update_existing_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN: There should be 5 service items added, 1 song, 3 custom slides (one is a bible
    # title slide), and 1 bible verse
    mocked_finish.assert_called_once()
    assert MockCustomSlide.call_count == 4, '4 custom slide added via custom_media_item'
    assert mocked_parse_reference.call_count == 2, '2 bible verses submitted for parsing'
    assert mocked_warning_box.call_count == 0, 'No warnings triggered'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.warning_message_box')
@patch('openlp.plugins.planningcenter.lib.songimport.PlanningCenterSongImport.finish')
@patch('openlp.plugins.planningcenter.lib.customimport.CustomSlide')
@patch('openlp.plugins.planningcenter.forms.selectplanform.parse_reference')
@patch('openlp.plugins.planningcenter.forms.selectplanform.date')
def test_other_bible_is_used_when_bible_gui_form_is_blank(mocked_date: MagicMock, mocked_parse_reference: MagicMock,
                                                          MockCustomSlide: MagicMock, mocked_finish: MagicMock,
                                                          mocked_warning_box: MagicMock, mocked_exec: MagicMock,
                                                          form: SelectPlanForm):
    """
    Test that an other bible is used when the GUI has an empty string for current selected bible
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    # mocked out "on_new_service_clicked"
    # need to always return 9/29/2019 for date.today()
    mocked_date.today.return_value = date(2019, 9, 29)
    mocked_date.side_effect = lambda *args, **kw: date(*args, **kw)
    mocked_bible_plugin = MagicMock()
    mocked_bible_plugin.version_combo_box.currentText.return_value = 'mocked_bible'
    Registry().register('service_manager', MagicMock())
    Registry().register('plugin_manager', MagicMock())
    Registry().register('songs', MagicMock())
    Registry().register('bibles', mocked_bible_plugin)
    Registry().register('custom', MagicMock())
    form.exec()
    # WHEN: The Service Type combo is set to index 1 and the Select Plan combo box
    # is set to index 1 and the "Import New" button is clicked
    form.service_type_combo_box.setCurrentIndex(1)
    QtTest.QTest.mouseClick(form.import_as_new_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN: There should be 2 bible verse parse attempts
    assert mocked_parse_reference.call_count == 2, '2 bible verses submitted for parsing'
    assert mocked_warning_box.call_count == 0, 'No warnings triggered'


@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.warning_message_box')
@patch('openlp.plugins.planningcenter.forms.selectplanform.PlanningCenterSongImport.finish')
@patch('openlp.plugins.planningcenter.lib.customimport.CustomSlide')
@patch('openlp.plugins.planningcenter.forms.selectplanform.parse_reference')
@patch('openlp.plugins.planningcenter.forms.selectplanform.date')
def test_warning_importing_bible_with_no_bible_available(mocked_date: MagicMock, mocked_parse_reference: MagicMock,
                                                         MockCustomSlide: MagicMock, mocked_finish: MagicMock,
                                                         mocked_warning_box: MagicMock, mocked_exec: MagicMock,
                                                         form: SelectPlanForm):
    """
    Test that a warning is shown when trying to import a bible text without having a bible installed
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    # mocked out "on_new_service_clicked"
    # need to always return 9/29/2019 for date.today()
    mocked_date.today.return_value = date(2019, 9, 29)
    mocked_date.side_effect = lambda *args, **kw: date(*args, **kw)
    mocked_bible_plugin = MagicMock()
    mocked_bible_plugin.version_combo_box.currentText.return_value = ''
    Registry().register('service_manager', MagicMock())
    Registry().register('plugin_manager', MagicMock())
    Registry().register('songs', MagicMock())
    Registry().register('bibles', mocked_bible_plugin)
    Registry().register('custom', MagicMock())
    form.exec()
    # WHEN: The Service Type combo is set to index 1 and the Select Plan combo box
    # is set to index 1 and the "Import New" button is clicked
    form.service_type_combo_box.setCurrentIndex(1)
    QtTest.QTest.mouseClick(form.import_as_new_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN: There should be 2 bible verse parse attempts
    assert mocked_parse_reference.call_count == 0, '0 bible verses submitted for parsing'
    assert mocked_warning_box.call_count == 2, '2 warnings should be triggered'


@pytest.mark.skip('fails to run when executed with all other openlp tests.  awaiting pytest fixtures to enable again')
@patch('openlp.plugins.planningcenter.forms.selectplanform.QtWidgets.QDialog.exec')
@patch('openlp.plugins.planningcenter.forms.selectplanform.date')
def test_less_mocking_service_refreshed_when_refresh_button_clicked(mocked_date: MagicMock, mocked_exec: MagicMock,
                                                                    form: SelectPlanForm):
    """
    Test that a service is refreshed when the "Refresh Service" button is clicked
    """
    # GIVEN: An SelectPlanForm instance with airplane mode enabled, resources available,
    # mocked out "on_new_service_clicked"
    # need to always return 9/29/2019 for date.today()
    mocked_date.today.return_value = date(2019, 9, 29)
    mocked_date.side_effect = lambda *args, **kw: date(*args, **kw)
    # init ServiceManager
    Registry().register('plugin_manager', MagicMock())
    Registry().register('renderer', MagicMock())
    Registry().register('main_window', MagicMock())
    Registry().register('live_controller', MagicMock())
    Registry().register('preview_controller', MagicMock())
    Registry().register('songs', MagicMock())
    Registry().register('bibles', MagicMock())
    Registry().register('custom', MagicMock())
    service_manager = ServiceManager()
    service_manager.setup_ui(service_manager)
    # init songs plugin
    with patch('openlp.plugins.songs.lib.mediaitem.EditSongForm'), \
            patch('openlp.plugins.custom.lib.mediaitem.EditCustomForm'), \
            patch('openlp.core.lib.mediamanageritem.create_widget_action'), \
            patch('openlp.core.widgets.toolbar.create_widget_action'):
        # init songs plugin
        songs_plugin = SongsPlugin()
        song_media_item = SongMediaItem(None, songs_plugin)
        song_media_item.search_text_edit = MagicMock()
        song_media_item.initialise()
        # init custom plugin
        custom_plugin = CustomPlugin()
        CustomMediaItem(None, custom_plugin)
        # init bible plugin
        bible_plugin = BiblePlugin()
        bible_media_item = BibleMediaItem(None, bible_plugin)
        bible_media_item.build_display_results = MagicMock()
        form.exec()
    # WHEN:
    # The Service Type combo is set to index 1 and "Import New" button is clicked
    form.service_type_combo_box.setCurrentIndex(1)
    QtTest.QTest.mouseClick(form.import_as_new_button, QtCore.Qt.MouseButton.LeftButton)
    # make changes to the now imported service items
    # first, for serviceitem[0] update last_updated in xml_string and change "sweet" to "sublime"
    old_match = re.search('modifiedDate="(.+?)Z*"',
                          service_manager.service_items[0]['service_item'].xml_version)
    old_string = old_match.group(1)
    now_string = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    service_manager.service_items[0]['service_item'].xml_version = \
        service_manager.service_items[0]['service_item'].xml_version.replace(old_string, now_string)
    service_manager.service_items[0]['service_item'].xml_version = \
        service_manager.service_items[0]['service_item'].xml_version.replace("sweet", "sublime")
    # second, add the word modified to the slide text for serviceitem[1]
    service_manager.service_items[1]['service_item'].slides[0]['text'] = \
        service_manager.service_items[1]['service_item'].slides[0]['text'].replace("Test", "Modified Test")
    # third, delete serviceitems[2] and serviceitem[3]
    del service_manager.service_items[3]
    del service_manager.service_items[2]
    # last, draw the form again and request refresh
    form.exec()
    form.service_type_combo_box.setCurrentIndex(1)
    QtTest.QTest.mouseClick(form.update_existing_button, QtCore.Qt.MouseButton.LeftButton)
    # THEN:
    # There should be 4 service items added
    assert len(service_manager.service_items) == 5, '5 items should be in the ServiceManager'
    # Amazon Grace should still include sublime
    assert 'sublime' in service_manager.service_items[0]['service_item'].xml_version
    # Slides in service_item[1] should still contain the word "Modified"
    assert 'Modified' in service_manager.service_items[1]['service_item'].slides[0]['text']
