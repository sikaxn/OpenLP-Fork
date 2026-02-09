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
The :mod:`~openlp.core.widgets.widgets` module contains custom widgets used in OpenLP
"""
from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.common.settings import ProxyMode
from openlp.core.lib.ui import critical_error_message_box


SCREENS_LAYOUT_STYLE = """
#screen_frame {
  background-color: palette(base);
}
#screen_frame QPushButton  {
  background-color: palette(window);
  border: 3px solid palette(text);
  border-radius: 3px;
  height: 100px;
  outline: 0;
  width: 150px;
}
#screen_frame QPushButton:checked  {
    border-color: palette(highlight);
}
"""


class ProxyWidget(QtWidgets.QGroupBox):
    """
    A proxy settings widget that implements loading and saving its settings.
    """
    def __init__(self, parent=None):
        """
        Initialise the widget.

        :param QtWidgets.QWidget | None parent: The widgets parent
        """
        super().__init__(parent)
        self.settings = Registry().get('settings')
        self._setup()

    def _setup(self):
        """
        A setup method seperate from __init__ to allow easier testing
        """
        self.setup_ui()
        self.load()

    def setup_ui(self):
        """
        Create the widget layout and sub widgets
        """
        self.layout = QtWidgets.QFormLayout(self)
        self.radio_group = QtWidgets.QButtonGroup(self)
        self.no_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.no_proxy_radio, ProxyMode.NO_PROXY)
        self.layout.setWidget(0, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.no_proxy_radio)
        self.use_sysem_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.use_sysem_proxy_radio, ProxyMode.SYSTEM_PROXY)
        self.layout.setWidget(1, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.use_sysem_proxy_radio)
        self.manual_proxy_radio = QtWidgets.QRadioButton('', self)
        self.radio_group.addButton(self.manual_proxy_radio, ProxyMode.MANUAL_PROXY)
        self.layout.setWidget(2, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.manual_proxy_radio)
        self.http_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('HTTP:', self.http_edit)
        self.https_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('HTTPS:', self.https_edit)
        self.username_edit = QtWidgets.QLineEdit(self)
        self.layout.addRow('Username:', self.username_edit)
        self.password_edit = QtWidgets.QLineEdit(self)
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout.addRow('Password:', self.password_edit)
        # Signal / Slots
        self.radio_group.buttonToggled.connect(self.on_radio_group_button_toggled)

    def on_radio_group_button_toggled(self, button, checked):
        """
        Handles the toggled signal on the radio buttons. The signal is emitted twice if a radio butting being toggled on
        causes another radio button in the group to be toggled off.

        En/Disables the `Manual Proxy` line edits depending on the currently selected radio button

        :param QtWidgets.QRadioButton button: The button that has toggled
        :param bool checked: The buttons new state
        """
        group_id = self.radio_group.id(button)  # The work around (see above comment)
        enable_manual_edits = group_id == ProxyMode.MANUAL_PROXY and checked
        self.http_edit.setEnabled(enable_manual_edits)
        self.https_edit.setEnabled(enable_manual_edits)
        self.username_edit.setEnabled(enable_manual_edits)
        self.password_edit.setEnabled(enable_manual_edits)

    def retranslate_ui(self):
        """
        Translate the Ui
        """
        self.setTitle(translate('OpenLP.ProxyWidget', 'Proxy Server Settings'))
        self.no_proxy_radio.setText(translate('OpenLP.ProxyWidget', 'No prox&y'))
        self.use_sysem_proxy_radio.setText(translate('OpenLP.ProxyWidget', '&Use system proxy'))
        self.manual_proxy_radio.setText(translate('OpenLP.ProxyWidget', '&Manual proxy configuration'))
        proxy_example = translate('OpenLP.ProxyWidget', 'e.g. proxy_server_address:port_no')
        self.layout.labelForField(self.http_edit).setText(translate('OpenLP.ProxyWidget', 'HTTP:'))
        self.http_edit.setPlaceholderText(proxy_example)
        self.layout.labelForField(self.https_edit).setText(translate('OpenLP.ProxyWidget', 'HTTPS:'))
        self.https_edit.setPlaceholderText(proxy_example)
        self.layout.labelForField(self.username_edit).setText(translate('OpenLP.ProxyWidget', 'Username:'))
        self.layout.labelForField(self.password_edit).setText(translate('OpenLP.ProxyWidget', 'Password:'))

    def load(self):
        """
        Load the data from the settings to the widget.
        """
        checked_radio = self.radio_group.button(self.settings.value('advanced/proxy mode'))
        checked_radio.setChecked(True)
        self.http_edit.setText(self.settings.value('advanced/proxy http'))
        self.https_edit.setText(self.settings.value('advanced/proxy https'))
        self.username_edit.setText(self.settings.value('advanced/proxy username'))
        self.password_edit.setText(self.settings.value('advanced/proxy password'))

    def save(self):
        """
        Save the widget data to the settings
        """
        self.settings.setValue('advanced/proxy mode', self.radio_group.checkedId())
        self.settings.setValue('advanced/proxy http', self.http_edit.text())
        self.settings.setValue('advanced/proxy https', self.https_edit.text())
        self.settings.setValue('advanced/proxy username', self.username_edit.text())
        self.settings.setValue('advanced/proxy password', self.password_edit.text())


class ProxyDialog(QtWidgets.QDialog):
    """
    A basic dialog to show proxy settingd
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.proxy_widget = ProxyWidget(self)
        self.layout.addWidget(self.proxy_widget)
        self.button_box = \
            QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok |
                                       QtWidgets.QDialogButtonBox.StandardButton.Cancel, self)
        self.layout.addWidget(self.button_box)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.retranslate_ui()

    def accept(self):
        """
        Reimplement the accept slot so that the ProxyWidget settings can be saved.
        :rtype: None
        """
        self.proxy_widget.save()
        super().accept()

    def retranslate_ui(self):
        self.proxy_widget.retranslate_ui()
        self.setWindowTitle(translate('OpenLP.ProxyDialog', 'Proxy Server Settings'))


class ScreenButton(QtWidgets.QPushButton):
    """
    A special button class that holds the screen information about it
    """
    def __init__(self, parent, screen):
        """
        Initialise this button
        """
        super().__init__(parent)
        self.setObjectName('screen_{number}_button'.format(number=screen.number))
        self.setCheckable(True)
        if isinstance(screen.geometry, QtCore.QRect):
            screen_size_text = translate('OpenLP.ScreenButton',
                                         f'({screen.geometry.width()} x {screen.geometry.height()} pixels)')
            self.setText(str(screen) + '\n' + screen_size_text)
        else:
            self.setText(str(screen))
        self.screen = screen


class ScreenSelectionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, screens=None):
        super().__init__(parent)
        self.current_screen = None
        self.identify_labels = []
        self.screens = screens or []
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self._on_identify_timer_shot)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(SCREENS_LAYOUT_STYLE)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.screen_frame = QtWidgets.QFrame(self)
        self.screen_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.screen_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.screen_frame.setObjectName('screen_frame')
        self.screen_frame_layout = QtWidgets.QHBoxLayout(self.screen_frame)
        self.screen_frame_layout.setContentsMargins(16, 16, 16, 16)
        self.screen_frame_layout.setSpacing(8)
        self.screen_frame_layout.setObjectName('screen_frame_layout')
        self.layout.addWidget(self.screen_frame)
        self.identify_layout = QtWidgets.QHBoxLayout()
        self.screen_details_layout = QtWidgets.QVBoxLayout()
        self.screen_details_layout.setObjectName('screen_details_layout')
        self.screen_number_label = QtWidgets.QLabel(self)
        self.screen_number_label.setObjectName('screen_number_label')
        self.screen_details_layout.addWidget(self.screen_number_label)
        self.use_screen_check_box = QtWidgets.QCheckBox(self)
        self.use_screen_check_box.setVisible(False)
        self.screen_details_layout.addWidget(self.use_screen_check_box)
        self.display_group_box = QtWidgets.QGroupBox(self)
        self.display_group_box.setObjectName('display_group_box')
        self.display_group_box.setCheckable(True)
        self.display_group_box_layout = QtWidgets.QGridLayout(self.display_group_box)
        self.display_group_box_layout.setSpacing(8)
        self.display_group_box_layout.setObjectName('display_group_box_layout')
        self.full_screen_radio_button = QtWidgets.QRadioButton(self.display_group_box)
        self.full_screen_radio_button.setObjectName('full_screen_radio_button')
        self.display_group_box_layout.addWidget(self.full_screen_radio_button, 0, 0, 1, 4)
        self.custom_geometry_button = QtWidgets.QRadioButton(self.display_group_box)
        self.custom_geometry_button.setObjectName('custom_geometry_button')
        self.display_group_box_layout.addWidget(self.custom_geometry_button, 1, 0, 1, 4)
        self.left_label = QtWidgets.QLabel(self.display_group_box)
        self.left_label.setObjectName('left_label')
        self.display_group_box_layout.addWidget(self.left_label, 2, 1, 1, 1)
        self.top_label = QtWidgets.QLabel(self.display_group_box)
        self.top_label.setObjectName('top_label')
        self.display_group_box_layout.addWidget(self.top_label, 2, 2, 1, 1)
        self.width_label = QtWidgets.QLabel(self.display_group_box)
        self.width_label.setObjectName('width_label')
        self.display_group_box_layout.addWidget(self.width_label, 2, 3, 1, 1)
        self.height_label = QtWidgets.QLabel(self.display_group_box)
        self.height_label.setObjectName('height_label')
        self.display_group_box_layout.addWidget(self.height_label, 2, 4, 1, 1)
        self.left_spin_box = QtWidgets.QSpinBox(self.display_group_box)
        self.left_spin_box.setObjectName('left_spin_box')
        self.left_spin_box.setEnabled(False)
        self.display_group_box_layout.addWidget(self.left_spin_box, 3, 1, 1, 1)
        self.top_spin_box = QtWidgets.QSpinBox(self.display_group_box)
        self.top_spin_box.setObjectName('top_spin_box')
        self.top_spin_box.setEnabled(False)
        self.display_group_box_layout.addWidget(self.top_spin_box, 3, 2, 1, 1)
        self.width_spin_box = QtWidgets.QSpinBox(self.display_group_box)
        self.width_spin_box.setObjectName('width_spin_box')
        self.width_spin_box.setEnabled(False)
        self.display_group_box_layout.addWidget(self.width_spin_box, 3, 3, 1, 1)
        self.height_spin_box = QtWidgets.QSpinBox(self.display_group_box)
        self.height_spin_box.setObjectName('height_spin_box')
        self.height_spin_box.setEnabled(False)
        self.display_group_box_layout.addWidget(self.height_spin_box, 3, 4, 1, 1)
        self.display_group_box_layout.setColumnStretch(3, 1)
        self.display_group_box.setLayout(self.display_group_box_layout)
        self.screen_details_layout.addWidget(self.display_group_box)
        self.identify_layout.addLayout(self.screen_details_layout)
        self.identify_button = QtWidgets.QPushButton(self)
        self.identify_button.setObjectName('identify_button')
        self.identify_layout.addWidget(
            self.identify_button, stretch=1,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop)
        self.screen_button_group = QtWidgets.QButtonGroup(self.screen_frame)
        self.screen_button_group.setExclusive(True)
        self.screen_button_group.setObjectName('screen_button_group')
        self.layout.addLayout(self.identify_layout)
        self.layout.addStretch()

        # Signals and slots
        self.display_group_box.clicked.connect(self.on_display_clicked)
        self.use_screen_check_box.clicked.connect(self.on_display_clicked)
        self.use_screen_check_box.toggled.connect(self.display_group_box.setChecked)
        self.custom_geometry_button.toggled.connect(self.height_spin_box.setEnabled)
        self.custom_geometry_button.toggled.connect(self.left_spin_box.setEnabled)
        self.custom_geometry_button.toggled.connect(self.top_spin_box.setEnabled)
        self.custom_geometry_button.toggled.connect(self.width_spin_box.setEnabled)
        self.identify_button.clicked.connect(self.on_identify_button_clicked)

        self._setup_spin_box(self.left_spin_box, -99999, 99999, 0)
        self._setup_spin_box(self.top_spin_box, -99999, 99999, 0)
        self._setup_spin_box(self.width_spin_box, -99999, 99999, 0)
        self._setup_spin_box(self.height_spin_box, -99999, 99999, 0)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.full_screen_radio_button.setText(translate('OpenLP.ScreensTab', 'F&ull screen'))
        self.width_label.setText(translate('OpenLP.ScreensTab', 'Width:'))
        use_screen_str = translate('OpenLP.ScreensTab', 'Use this screen as a display')
        self.use_screen_check_box.setText(use_screen_str)
        self.display_group_box.setTitle(use_screen_str)
        self.left_label.setText(translate('OpenLP.ScreensTab', 'Left:'))
        self.custom_geometry_button.setText(translate('OpenLP.ScreensTab', 'Custom &geometry'))
        self.top_label.setText(translate('OpenLP.ScreensTab', 'Top:'))
        self.height_label.setText(translate('OpenLP.ScreensTab', 'Height:'))
        self.identify_button.setText(translate('OpenLP.ScreensTab', 'Identify Screens'))

    def on_display_clicked(self, is_checked):
        if not is_checked:
            critical_error_message_box(translate('OpenLP.ScreensTab', 'Select a Display'),
                                       translate('OpenLP.ScreensTab', 'You need to select at least one screen to be '
                                                 'used as a display. Select the screen you wish to use as a display, '
                                                 'and check the checkbox for that screen.'),
                                       parent=self, question=False)
            self.use_screen_check_box.setChecked(True)
            self.display_group_box.setChecked(True)
        else:
            for screen in self.screens:
                screen.is_display = False
            self.current_screen.is_display = True

    def _save_screen(self, screen):
        """
        Save the details in the UI to the screen

        :param openlp.core.display.screens.Screen screen:
        :return: None
        """
        if not screen:
            return
        screen.is_display = self.display_group_box.isChecked()
        if self.custom_geometry_button.isChecked():
            screen.custom_geometry = QtCore.QRect(self.left_spin_box.value(), self.top_spin_box.value(),
                                                  self.width_spin_box.value(), self.height_spin_box.value())
        else:
            screen.custom_geometry = None

    def _setup_spin_box(self, spin_box, mininum, maximum, value):
        """
        Set up the spin box

        :param QtWidgets.QSpinBox spin_box:
        :param int minimun:
        :param int maximum:
        :param int value:
        :return: None
        """
        spin_box.setMinimum(mininum)
        spin_box.setMaximum(maximum)
        spin_box.setValue(value)

    def load(self):
        # Remove all the existing items in the layout
        while self.screen_frame_layout.count() > 0:
            item = self.screen_frame_layout.takeAt(0)
            if item.widget() is not None:
                widget = item.widget()
                if widget in self.screen_button_group.buttons():
                    self.screen_button_group.removeButton(widget)
                widget.setParent(None)
                widget.deleteLater()
            del item
        # Add the existing screens into the frame
        self.screen_frame_layout.addStretch()
        for screen in self.screens:
            screen_button = ScreenButton(self.screen_frame, screen)
            screen_button.clicked.connect(self.on_screen_button_clicked)
            self.screen_frame_layout.addWidget(screen_button)
            self.screen_button_group.addButton(screen_button)
            if screen.number == 0:
                screen_button.click()
        self.screen_frame_layout.addStretch()

    def save(self):
        """
        Save the screen settings
        """
        self._save_screen(self.current_screen)
        screen_settings = {}
        for screen in self.screens:
            screen_settings[screen.number] = screen.to_dict()
        Registry().get('settings').setValue('core/screens', screen_settings)
        # On save update the screens as well

    def use_simple_view(self):
        """
        Hide advanced options. Added for use in the FTW

        :rtype: None
        """
        self.use_screen_check_box.setVisible(True)
        self.display_group_box.setVisible(False)

    @QtCore.Slot()
    def _on_identify_timer_shot(self):
        for label in self.identify_labels:
            label.hide()
            label.setParent(None)
            label.deleteLater()
        self.identify_labels = []

    def on_identify_button_clicked(self):
        """
        Display a widget on every screen for 5 seconds
        """
        for screen in self.screens:
            label = QtWidgets.QLabel(None)
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label.setText(str(screen))
            label.setStyleSheet('font-size: 24pt; font-weight: bold; '
                                'background-color: #0C0; color: #000; border: 5px solid #000;')
            label.setGeometry(QtCore.QRect(screen.geometry.x(), screen.geometry.y(), screen.geometry.width(), 100))
            label.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint |
                                 QtCore.Qt.WindowType.Tool |
                                 QtCore.Qt.WindowType.WindowStaysOnTopHint |
                                 QtCore.Qt.WindowType.WindowDoesNotAcceptFocus)
            label.show()
            self.identify_labels.append(label)
        self.timer.start()

    def on_screen_button_clicked(self):
        """
        Respond to a screen button being clicked
        """
        screen = self.sender().screen
        if self.current_screen is not screen:
            self._save_screen(self.current_screen)
        self.screen_number_label.setText(str(screen))
        self.use_screen_check_box.setChecked(screen.is_display)
        self.display_group_box.setChecked(screen.is_display)
        self.full_screen_radio_button.setChecked(screen.custom_geometry is None)
        self.custom_geometry_button.setChecked(screen.custom_geometry is not None)
        if isinstance(screen.custom_geometry, QtCore.QRect):
            self.left_spin_box.setValue(screen.custom_geometry.x())
            self.top_spin_box.setValue(screen.custom_geometry.y())
            self.width_spin_box.setValue(screen.custom_geometry.width())
            self.height_spin_box.setValue(screen.custom_geometry.height())
        else:
            self.left_spin_box.setValue(0)
            self.top_spin_box.setValue(0)
            self.width_spin_box.setValue(screen.geometry.width())
            self.height_spin_box.setValue(screen.geometry.height())

        self.current_screen = screen
