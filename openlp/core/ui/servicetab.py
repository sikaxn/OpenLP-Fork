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
The services tab of the configuration dialog.
"""
import logging
from datetime import datetime, timedelta

from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common import SlideLimits
from openlp.core.common.i18n import UiStrings, format_time, translate
from openlp.core.ui.icons import UiIcons
from openlp.core.lib.settingstab import SettingsTab

log = logging.getLogger(__name__)


class ServiceTab(SettingsTab):
    """
    ServiceTab is the service settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Initialise the service settings tab
        """
        # self.logo_background_color = '#ffffff'
        self.icon_path = UiIcons().live
        self.should_update_service_name_example = True
        service_translated = translate('OpenLP.ServiceTab', 'Service')
        super(ServiceTab, self).__init__(parent, 'Service', service_translated)

    def setup_ui(self):
        """
        Create the user interface for the service settings tab
        """
        self.setObjectName('ServiceTab')
        super(ServiceTab, self).setup_ui()
        self.tab_layout.setStretch(1, 1)
        # Default service name
        self.service_name_group_box = QtWidgets.QGroupBox(self.left_column)
        self.service_name_group_box.setObjectName('service_name_group_box')
        self.service_name_layout = QtWidgets.QFormLayout(self.service_name_group_box)
        self.service_name_check_box = QtWidgets.QCheckBox(self.service_name_group_box)
        self.service_name_check_box.setObjectName('service_name_check_box')
        self.service_name_layout.setObjectName('service_name_layout')
        self.service_name_layout.addRow(self.service_name_check_box)
        self.service_name_time_label = QtWidgets.QLabel(self.service_name_group_box)
        self.service_name_time_label.setObjectName('service_name_time_label')
        self.service_name_day = QtWidgets.QComboBox(self.service_name_group_box)
        self.service_name_day.addItems(['', '', '', '', '', '', '', ''])
        self.service_name_day.setObjectName('service_name_day')
        self.service_name_time = QtWidgets.QTimeEdit(self.service_name_group_box)
        self.service_name_time.setObjectName('service_name_time')
        self.service_name_time_layout = QtWidgets.QHBoxLayout()
        self.service_name_time_layout.setObjectName('service_name_time_layout')
        self.service_name_time_layout.addWidget(self.service_name_day)
        self.service_name_time_layout.addWidget(self.service_name_time)
        self.service_name_layout.addRow(self.service_name_time_label, self.service_name_time_layout)
        self.service_name_label = QtWidgets.QLabel(self.service_name_group_box)
        self.service_name_label.setObjectName('service_name_label')
        self.service_name_edit = QtWidgets.QLineEdit(self.service_name_group_box)
        self.service_name_edit.setObjectName('service_name_edit')
        self.service_name_edit.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'[^/\\?*|<>\[\]":+]+'), self))
        self.service_name_revert_button = QtWidgets.QToolButton(self.service_name_group_box)
        self.service_name_revert_button.setObjectName('service_name_revert_button')
        self.service_name_revert_button.setIcon(UiIcons().undo)
        self.service_name_button_layout = QtWidgets.QHBoxLayout()
        self.service_name_button_layout.setObjectName('service_name_button_layout')
        self.service_name_button_layout.addWidget(self.service_name_edit)
        self.service_name_button_layout.addWidget(self.service_name_revert_button)
        self.service_name_layout.addRow(self.service_name_label, self.service_name_button_layout)
        self.service_name_example_label = QtWidgets.QLabel(self.service_name_group_box)
        self.service_name_example_label.setObjectName('service_name_example_label')
        self.service_name_example = QtWidgets.QLabel(self.service_name_group_box)
        self.service_name_example.setObjectName('service_name_example')
        self.service_name_layout.addRow(self.service_name_example_label, self.service_name_example)
        self.left_layout.addWidget(self.service_name_group_box)
        # Slide Controller
        self.slide_controller_groupbox = QtWidgets.QGroupBox(self.left_column)
        self.slide_controller_groupbox.setObjectName('slide_controller_groupbox')
        self.slide_controller_layout = QtWidgets.QFormLayout(self.slide_controller_groupbox)
        self.slide_controller_layout.setObjectName('slide_controller_layout')
        self.auto_unblank_check_box = QtWidgets.QCheckBox(self.slide_controller_groupbox)
        self.auto_unblank_check_box.setObjectName('auto_unblank_check_box')
        self.slide_controller_layout.addRow(self.auto_unblank_check_box)
        self.click_live_slide_to_unblank_check_box = QtWidgets.QCheckBox(self.slide_controller_groupbox)
        self.click_live_slide_to_unblank_check_box.setObjectName('click_live_slide_to_unblank')
        self.slide_controller_layout.addRow(self.click_live_slide_to_unblank_check_box)
        self.auto_preview_check_box = QtWidgets.QCheckBox(self.slide_controller_groupbox)
        self.auto_preview_check_box.setObjectName('auto_preview_check_box')
        self.slide_controller_layout.addRow(self.auto_preview_check_box)
        self.live_preview_shows_blank_screen_check_box = QtWidgets.QCheckBox(self.slide_controller_groupbox)
        self.live_preview_shows_blank_screen_check_box.setObjectName('live_preview_shows_blank_screen_check_box')
        self.slide_controller_layout.addRow(self.live_preview_shows_blank_screen_check_box)
        self.timeout_label = QtWidgets.QLabel(self.slide_controller_groupbox)
        self.timeout_label.setObjectName('timeout_label')
        self.timeout_spin_box = QtWidgets.QSpinBox(self.slide_controller_groupbox)
        self.timeout_spin_box.setObjectName('timeout_spin_box')
        self.timeout_spin_box.setRange(1, 180)
        self.slide_controller_layout.addRow(self.timeout_label, self.timeout_spin_box)
        self.left_layout.addWidget(self.slide_controller_groupbox)
        # Service Item Wrapping
        self.slide_group_box = QtWidgets.QGroupBox(self.right_column)
        self.slide_group_box.setObjectName('slide_group_box')
        self.slide_layout = QtWidgets.QVBoxLayout(self.slide_group_box)
        self.slide_layout.setObjectName('slide_layout')
        self.slide_label = QtWidgets.QLabel(self.slide_group_box)
        self.slide_label.setWordWrap(True)
        self.slide_layout.addWidget(self.slide_label)
        self.end_slide_radio_button = QtWidgets.QRadioButton(self.slide_group_box)
        self.end_slide_radio_button.setObjectName('end_slide_radio_button')
        self.slide_layout.addWidget(self.end_slide_radio_button)
        self.wrap_slide_radio_button = QtWidgets.QRadioButton(self.slide_group_box)
        self.wrap_slide_radio_button.setObjectName('wrap_slide_radio_button')
        self.slide_layout.addWidget(self.wrap_slide_radio_button)
        self.next_item_radio_button = QtWidgets.QRadioButton(self.slide_group_box)
        self.next_item_radio_button.setObjectName('next_item_radio_button')
        self.slide_layout.addWidget(self.next_item_radio_button)
        self.right_layout.addWidget(self.slide_group_box)
        # Service Editing
        self.service_editing_groupbox = QtWidgets.QGroupBox(self.left_column)
        self.service_editing_groupbox.setObjectName('service_editing_groupbox')
        self.service_editing_layout = QtWidgets.QFormLayout(self.service_editing_groupbox)
        self.service_editing_layout.setObjectName('service_editing_layout')
        self.service_editing_check_box = QtWidgets.QCheckBox(self.service_editing_groupbox)
        self.service_editing_check_box.setObjectName('service_editing_check_box')
        self.service_editing_layout.addRow(self.service_editing_check_box)
        self.right_layout.addWidget(self.service_editing_groupbox)
        # Push everything in both columns to the top
        self.left_layout.addStretch()
        self.right_layout.addStretch()
        # Connect signals and slots
        self.should_update_service_name_example = False
        # Default Service Name
        self.service_name_check_box.toggled.connect(self.service_name_check_box_toggled)
        self.service_name_day.currentIndexChanged.connect(self.on_service_name_day_changed)
        self.service_name_time.timeChanged.connect(self.update_service_name_example)
        self.service_name_edit.textChanged.connect(self.update_service_name_example)
        self.service_name_revert_button.clicked.connect(self.on_service_name_revert_button_clicked)
        # Service Item Wrapping
        self.end_slide_radio_button.clicked.connect(self.on_end_slide_button_clicked)
        self.wrap_slide_radio_button.clicked.connect(self.on_wrap_slide_button_clicked)
        self.next_item_radio_button.clicked.connect(self.on_next_item_button_clicked)

    def retranslate_ui(self):
        """
        Translate the service settings tab to the currently selected language
        """
        self.tab_title_visible = translate('OpenLP.ServiceTab', 'Service')
        # Default Service Name
        self.service_name_group_box.setTitle(translate('OpenLP.ServiceTab', 'Default Service Name'))
        self.service_name_check_box.setText(translate('OpenLP.ServiceTab', 'Enable default service name'))
        self.service_name_time_label.setText(translate('OpenLP.ServiceTab', 'Date and Time:'))
        self.service_name_day.setItemText(0, translate('OpenLP.ServiceTab', 'Monday'))
        self.service_name_day.setItemText(1, translate('OpenLP.ServiceTab', 'Tuesday'))
        self.service_name_day.setItemText(2, translate('OpenLP.ServiceTab', 'Wednesday'))
        self.service_name_day.setItemText(3, translate('OpenLP.ServiceTab', 'Thursday'))
        self.service_name_day.setItemText(4, translate('OpenLP.ServiceTab', 'Friday'))
        self.service_name_day.setItemText(5, translate('OpenLP.ServiceTab', 'Saturday'))
        self.service_name_day.setItemText(6, translate('OpenLP.ServiceTab', 'Sunday'))
        self.service_name_day.setItemText(7, translate('OpenLP.ServiceTab', 'Now'))
        self.service_name_time.setToolTip(translate('OpenLP.ServiceTab', 'Time service usually starts.'))
        self.service_name_label.setText(translate('OpenLP.ServiceTab', 'Name:'))
        self.service_name_edit.setToolTip(translate('OpenLP.ServiceTab', 'Consult the OpenLP manual for usage.'))
        self.service_name_revert_button.setToolTip(
            translate('OpenLP.ServiceTab',
                      'Revert to the default service name "{name}".').format(name=UiStrings().DefaultServiceName))
        self.service_name_example_label.setText(translate('OpenLP.ServiceTab', 'Example:'))
        # Slide Controller
        self.slide_controller_groupbox.setTitle(translate('OpenLP.ServiceTab', 'Slide Controller'))
        self.click_live_slide_to_unblank_check_box.setText(translate('OpenLP.ServiceTab',
                                                           'Unblank display when changing slide in Live'))
        self.auto_unblank_check_box.setText(translate('OpenLP.ServiceTab', 'Unblank display when sending '
                                                                           'items to Live'))
        self.auto_preview_check_box.setText(translate('OpenLP.ServiceTab',
                                                      'Automatically preview the next item in service'))
        self.live_preview_shows_blank_screen_check_box.setText(UiStrings().LivePreviewShowsBlankScreen)
        self.timeout_label.setText(translate('OpenLP.ServiceTab', 'Timed slide interval:'))
        self.timeout_spin_box.setSuffix(translate('OpenLP.ServiceTab', ' sec'))
        # Service Item Wrapping
        self.slide_group_box.setTitle(translate('OpenLP.ServiceTab', 'Service Item Wrapping'))
        self.slide_label.setText(translate('OpenLP.ServiceTab', 'Behavior of next/previous on the last/first slide:'))
        self.end_slide_radio_button.setText(translate('OpenLP.ServiceTab', '&Remain on Slide'))
        self.wrap_slide_radio_button.setText(translate('OpenLP.ServiceTab', '&Wrap around'))
        self.next_item_radio_button.setText(translate('OpenLP.ServiceTab', '&Move to next/previous service item'))
        # Service Editing
        self.service_editing_groupbox.setTitle(translate('OpenLP.ServiceTab', 'Service Editing'))
        self.service_editing_check_box.setText(translate('OpenLP.ServiceTab', 'Show confirmation box when deleting '
                                                                              'item from service'))

    def load(self):
        """
        Load the settings to populate the form
        """
        # Default Service Name
        self.service_name_day.setCurrentIndex(self.settings.value('advanced/default service day'))
        self.service_name_time.setTime(QtCore.QTime(self.settings.value('advanced/default service hour'),
                                                    self.settings.value('advanced/default service minute')))
        self.should_update_service_name_example = True
        self.service_name_edit.setText(self.settings.value('advanced/default service name'))
        default_service_enabled = self.settings.value('advanced/default service enabled')
        self.service_name_check_box.setChecked(default_service_enabled)
        self.service_name_check_box_toggled(default_service_enabled)
        # Slide Controller
        self.auto_unblank_check_box.setChecked(self.settings.value('core/auto unblank'))
        self.click_live_slide_to_unblank_check_box.setChecked(self.settings.value('core/click live slide to unblank'))
        self.auto_preview_check_box.setChecked(self.settings.value('core/auto preview'))
        self.live_preview_shows_blank_screen_check_box.setChecked(
            self.settings.value('core/live preview shows blank screen')
        )
        self.timeout_spin_box.setValue(self.settings.value('core/loop delay'))
        # Service Item Wrapping
        self.slide_limits = self.settings.value('advanced/slide limits')
        if self.slide_limits == SlideLimits.End:
            self.end_slide_radio_button.setChecked(True)
        elif self.slide_limits == SlideLimits.Wrap:
            self.wrap_slide_radio_button.setChecked(True)
        else:
            self.next_item_radio_button.setChecked(True)
        # Service Editing
        self.service_editing_check_box.setChecked(self.settings.value('advanced/delete service item confirmation'))

    def save(self):
        """
        Save the settings from the form
        """
        # Default Service Name
        self.settings.setValue('advanced/default service enabled', self.service_name_check_box.isChecked())
        service_name = self.service_name_edit.text()
        preset_is_valid = self.generate_service_name_example()[0]
        if service_name == UiStrings().DefaultServiceName or not preset_is_valid:
            self.settings.remove('advanced/default service name')
            self.service_name_edit.setText(service_name)
        else:
            self.settings.setValue('advanced/default service name', service_name)
        self.settings.setValue('advanced/default service day', self.service_name_day.currentIndex())
        self.settings.setValue('advanced/default service hour', self.service_name_time.time().hour())
        self.settings.setValue('advanced/default service minute', self.service_name_time.time().minute())
        # Slide Controller
        self.settings.setValue('core/auto unblank', self.auto_unblank_check_box.isChecked())
        self.settings.setValue('core/click live slide to unblank',
                               self.click_live_slide_to_unblank_check_box.isChecked())
        self.settings.setValue('core/auto preview', self.auto_preview_check_box.isChecked())
        live_preview_shows_blank_screen_check_box_is_checked = \
            self.live_preview_shows_blank_screen_check_box.isChecked()
        self.settings.setValue('core/live preview shows blank screen',
                               live_preview_shows_blank_screen_check_box_is_checked)
        if not live_preview_shows_blank_screen_check_box_is_checked:
            self.settings_form.register_post_process('slidecontroller_preview_display_show_display')
        self.settings.setValue('core/loop delay', self.timeout_spin_box.value())
        # Service Item Wrapping
        self.settings.setValue('advanced/slide limits', self.slide_limits)
        self.settings_form.register_post_process('slidecontroller_update_slide_limits')
        # Service Editing
        self.settings.setValue('advanced/delete service item confirmation', self.service_editing_check_box.isChecked())
        self.post_set_up()

    def post_set_up(self):
        """
        Apply settings after the tab has loaded
        """
        self.settings_form.register_post_process('slidecontroller_live_spin_delay')

    def service_name_check_box_toggled(self, default_service_enabled):
        """
        Service Name options changed
        """
        self.service_name_day.setEnabled(default_service_enabled)
        time_enabled = default_service_enabled and self.service_name_day.currentIndex() != 7
        self.service_name_time.setEnabled(time_enabled)
        self.service_name_edit.setEnabled(default_service_enabled)
        self.service_name_revert_button.setEnabled(default_service_enabled)

    def generate_service_name_example(self):
        """
        Display an example of the template used
        """
        preset_is_valid = True
        if self.service_name_day.currentIndex() == 7:
            local_time = datetime.now()
        else:
            now = datetime.now()
            day_delta = self.service_name_day.currentIndex() - now.weekday()
            if day_delta < 0:
                day_delta += 7
            time = now + timedelta(days=day_delta)
            local_time = time.replace(
                hour=self.service_name_time.time().hour(),
                minute=self.service_name_time.time().minute()
            )
        try:
            service_name_example = format_time(self.service_name_edit.text(), local_time)
        except ValueError:
            preset_is_valid = False
            service_name_example = translate('OpenLP.ServiceTab', 'Syntax error.')
        return preset_is_valid, service_name_example

    def update_service_name_example(self, returned_value):
        """
        Update the example service name.
        """
        if not self.should_update_service_name_example:
            return
        name_example = self.generate_service_name_example()[1]
        self.service_name_example.setText(name_example)

    def on_service_name_day_changed(self, service_day):
        """
        React to the day of the service name changing.
        """
        self.service_name_time.setEnabled(service_day != 7)
        self.update_service_name_example(None)

    def on_service_name_revert_button_clicked(self):
        """
        Revert to the default service name.
        """
        self.service_name_edit.setText(UiStrings().DefaultServiceName)
        self.service_name_edit.setFocus()

    def on_end_slide_button_clicked(self):
        """
        Stop at the end either top ot bottom
        """
        self.slide_limits = SlideLimits.End

    def on_wrap_slide_button_clicked(self):
        """
        Wrap round the service item
        """
        self.slide_limits = SlideLimits.Wrap

    def on_next_item_button_clicked(self):
        """
        Advance to the next service item
        """
        self.slide_limits = SlideLimits.Next
