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
The :mod:`ui` module provides standard UI components for OpenLP.
"""
import logging

from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common.actions import ActionList
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.platform import is_macosx
from openlp.core.common.registry import Registry
from openlp.core.lib import build_icon
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.labels import FormLabel


log = logging.getLogger(__name__)


def add_welcome_page(parent, image):
    """
    Generate an opening welcome page for a wizard using a provided image.

    :param parent: A ``QWizard`` object to add the welcome page to.
    :param image: A splash image for the wizard.
    """
    parent.welcome_page = QtWidgets.QWizardPage()
    parent.welcome_page.setPixmap(QtWidgets.QWizard.WizardPixmap.WatermarkPixmap, QtGui.QPixmap(image))
    parent.welcome_page.setObjectName('welcome_page')
    parent.welcome_layout = QtWidgets.QVBoxLayout(parent.welcome_page)
    parent.welcome_layout.setObjectName('WelcomeLayout')
    parent.title_label = QtWidgets.QLabel(parent.welcome_page)
    parent.title_label.setObjectName('title_label')
    parent.welcome_layout.addWidget(parent.title_label)
    parent.title_label.setWordWrap(True)
    parent.welcome_layout.addSpacing(40)
    parent.information_label = QtWidgets.QLabel(parent.welcome_page)
    parent.information_label.setWordWrap(True)
    parent.information_label.setObjectName('information_label')
    parent.welcome_layout.addWidget(parent.information_label)
    parent.welcome_layout.addStretch()
    parent.addPage(parent.welcome_page)


def create_button_box(dialog, name, standard_buttons, custom_buttons=None):
    """
    Creates a QDialogButtonBox with the given buttons. The ``accepted()`` and ``rejected()`` signals of the button box
    are connected with the dialogs ``accept()`` and ``reject()`` slots.

    :param dialog: The parent object. This has to be a ``QDialog`` descendant.
    :param name: A string which is set as object name.
    :param standard_buttons: A list of strings for the used buttons. It might contain: ``ok``, ``save``, ``cancel``,
        ``close``, and ``defaults``.
    :param custom_buttons: A list of additional buttons. If an item is an instance of QtWidgets.QAbstractButton it is
    added with QDialogButtonBox.ButtonRole.ActionRole.
    Otherwise the item has to be a tuple of a Button and a ButtonRole.
    """
    if custom_buttons is None:
        custom_buttons = []
    if standard_buttons is None:
        standard_buttons = []
    buttons = QtWidgets.QDialogButtonBox.StandardButton.NoButton
    if 'ok' in standard_buttons:
        buttons |= QtWidgets.QDialogButtonBox.StandardButton.Ok
    if 'save' in standard_buttons:
        buttons |= QtWidgets.QDialogButtonBox.StandardButton.Save
    if 'cancel' in standard_buttons:
        buttons |= QtWidgets.QDialogButtonBox.StandardButton.Cancel
    if 'close' in standard_buttons:
        buttons |= QtWidgets.QDialogButtonBox.StandardButton.Close
    if 'help' in standard_buttons and hasattr(dialog, 'provide_help'):
        buttons |= QtWidgets.QDialogButtonBox.StandardButton.Help
    if 'defaults' in standard_buttons:
        buttons |= QtWidgets.QDialogButtonBox.StandardButton.RestoreDefaults
    button_box = QtWidgets.QDialogButtonBox(dialog)
    button_box.setObjectName(name)
    button_box.setStandardButtons(buttons)
    for button in custom_buttons:
        if isinstance(button, QtWidgets.QAbstractButton):
            button_box.addButton(button, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        else:
            button_box.addButton(*button)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    if 'help' in standard_buttons and hasattr(dialog, 'provide_help'):
        button_box.helpRequested.connect(dialog.provide_help)
    return button_box


def critical_error_message_box(title=None, message=None, parent=None, question=False):
    """
    Provides a standard critical message box for errors that OpenLP displays to users.

    :param title: The title for the message box.
    :param message: The message to display to the user.
    :param parent: The parent UI element to attach the dialog to.
    :param question: Should this message box question the user.
    """
    if question:
        return QtWidgets.QMessageBox.critical(parent, UiStrings().Error, message,
                                              QtWidgets.QMessageBox.StandardButton(
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No))
    # If used before the main window is created, fall back to direct use of QMessageBox
    main_window = Registry().get('main_window')
    if main_window:
        return main_window.error_message(title if title else UiStrings().Error, message)
    else:
        QtWidgets.QMessageBox.critical(parent, title, message)


def warning_message_box(title=None, message=None, parent=None, question=False):
    """
    Provides a standard critical message box for errors that OpenLP displays to users.

    :param title: The title for the message box.
    :param message: The message to display to the user.
    :param parent: The parent UI element to attach the dialog to.
    :param question: Should this message box question the user.
    """
    if question:
        return QtWidgets.QMessageBox.warning(parent, UiStrings().Warning, message,
                                             QtWidgets.QMessageBox.StandardButton(
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No))
    QtWidgets.QMessageBox.warning(parent, title, message)


def create_horizontal_adjusting_combo_box(parent, name):
    """
    Creates a QComboBox with adapting width for media items.

    :param parent: The parent widget.
    :param name: A string set as object name for the combo box.
    """
    combo = QtWidgets.QComboBox(parent)
    combo.setObjectName(name)
    combo.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
    return combo


def create_button(parent, name, **kwargs):
    """
    Return an button with the object name set and the given parameters.

    :param parent:  A QtCore.QWidget for the buttons parent (required).
    :param name: A string which is set as object name (required).
    :param kwargs:

    ``role``
        A string which can have one value out of ``delete``, ``up``, and ``down``. This decides about default values
        for properties like text, icon, or tooltip.

    ``text``
        A string for the action text.

    ``icon``
        Either a QIcon, a resource string, or a file location string for the action icon.

    ``tooltip``
        A string for the action tool tip.

    ``enabled``
        False in case the button should be disabled.

    """
    if 'role' in kwargs:
        role = kwargs.pop('role')
        if role == 'delete':
            kwargs.setdefault('text', UiStrings().Delete)
            kwargs.setdefault('tooltip', translate('OpenLP.Ui', 'Delete the selected item.'))
        elif role == 'up':
            kwargs.setdefault('icon', UiIcons().arrow_up)
            kwargs.setdefault('tooltip', translate('OpenLP.Ui', 'Move selection up one position.'))
        elif role == 'down':
            kwargs.setdefault('icon', UiIcons().arrow_down)
            kwargs.setdefault('tooltip', translate('OpenLP.Ui', 'Move selection down one position.'))
        else:
            log.warning('The role "{role}" is not defined in create_push_button().'.format(role=role))
    if kwargs.pop('btn_class', '') == 'toolbutton':
        button = QtWidgets.QToolButton(parent)
    else:
        button = QtWidgets.QPushButton(parent)
    button.setObjectName(name)
    if kwargs.get('text'):
        button.setText(kwargs.pop('text'))
    if kwargs.get('icon'):
        button.setIcon(build_icon(kwargs.pop('icon')))
    if kwargs.get('tooltip'):
        button.setToolTip(kwargs.pop('tooltip'))
    if not kwargs.pop('enabled', True):
        button.setEnabled(False)
    if kwargs.get('click'):
        button.clicked.connect(kwargs.pop('click'))
    for key in list(kwargs.keys()):
        if key not in ['text', 'icon', 'tooltip', 'click']:
            log.warning('Parameter {key} was not consumed in create_button().'.format(key=key))
    return button


def create_action(parent, name, **kwargs):
    """
    Return an action with the object name set and the given parameters.

    :param parent:  A QtCore.QObject for the actions parent (required).
    :param name:  A string which is set as object name (required).
    :param kwargs:

    ``text``
        A string for the action text.

    ``icon``
        Either a QIcon, a resource string, or a file location string for the
        action icon.

    ``tooltip``
        A string for the action tool tip.

    ``statustip``
        A string for the action status tip.

    ``checked``
        A bool for the state. If ``None`` the Action is not checkable.

    ``enabled``
        False in case the action should be disabled.

    ``visible``
        False in case the action should be hidden.

    ``separator``
        True in case the action will be considered a separator.

    ``data``
        The action's data.

    ``can_shortcuts``
        Capability stating if this action can have shortcuts. If ``True`` the action is added to shortcut dialog

        otherwise it it not. Define your shortcut in the :class:`~openlp.core.lib.Settings` class. *Note*: When *not*
        ``True`` you *must not* set a shortcuts at all.

    ``context``
        A context for the shortcut execution.

    ``category``
        A category the action should be listed in the shortcut dialog.

    ``triggers``
        A slot which is connected to the actions ``triggered()`` slot.
    """
    action = QtGui.QAction(parent)
    action.setObjectName(name)
    if is_macosx():
        action.setIconVisibleInMenu(False)
    if kwargs.get('text'):
        action.setText(kwargs.pop('text'))
    if kwargs.get('icon'):
        action.setIcon(build_icon(kwargs.pop('icon')))
    if kwargs.get('tooltip'):
        action.setToolTip(kwargs.pop('tooltip'))
    if kwargs.get('statustip'):
        action.setStatusTip(kwargs.pop('statustip'))
    if kwargs.get('checked') is not None:
        action.setCheckable(True)
        action.setChecked(kwargs.pop('checked'))
    if not kwargs.pop('enabled', True):
        action.setEnabled(False)
    if not kwargs.pop('visible', True):
        action.setVisible(False)
    if kwargs.pop('separator', False):
        action.setSeparator(True)
    if 'data' in kwargs:
        action.setData(kwargs.pop('data'))
    if kwargs.pop('can_shortcuts', False):
        action_list = ActionList.get_instance()
        action_list.add_action(action, kwargs.pop('category', None))
    if 'context' in kwargs:
        action.setShortcutContext(kwargs.pop('context'))
    if kwargs.get('triggers'):
        action.triggered.connect(kwargs.pop('triggers'))
    for key in list(kwargs.keys()):
        if key not in ['text', 'icon', 'tooltip', 'statustip', 'checked', 'can_shortcuts', 'category', 'triggers']:
            log.warning('Parameter {key} was not consumed in create_action().'.format(key=key))
    return action


def create_widget_action(parent, name='', **kwargs):
    """
    Return a new QAction by calling ``create_action(parent, name, **kwargs)``. The shortcut context defaults to
    ``QtCore.Qt.ShortcutContext.WidgetShortcut`` and the action is added to the parents action list.
    """
    kwargs.setdefault('context', QtCore.Qt.ShortcutContext.WidgetShortcut)
    action = create_action(parent, name, **kwargs)
    parent.addAction(action)
    return action


def set_case_insensitive_completer(cache, widget):
    """
    Sets a case insensitive text completer for a widget.

    :param cache: The list of items to use as suggestions.
    :param widget: A widget to set the completer (QComboBox or QLineEdit instance)
    """
    completer = QtWidgets.QCompleter(cache)
    completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
    widget.setCompleter(completer)


def create_halign_selection_widgets(parent):
    """
    Creates a standard label and combo box for asking users to select a horizontal alignment.

    :param parent: The parent object. This should be a ``QWidget`` descendant.
    """
    label = FormLabel(parent)
    label.setText(translate('OpenLP.ThemeWizard', 'Horizontal Align:'))
    combo_box = QtWidgets.QComboBox(parent)
    combo_box.addItems([UiStrings().Left, UiStrings().Right, UiStrings().Center, UiStrings().Justify])
    label.setBuddy(combo_box)
    return label, combo_box


def create_valign_selection_widgets(parent):
    """
    Creates a standard label and combo box for asking users to select a vertical alignment.

    :param parent: The parent object. This should be a ``QWidget`` descendant.
    """
    label = FormLabel(parent)
    label.setText(translate('OpenLP.Ui', '&Vertical Align:'))
    combo_box = QtWidgets.QComboBox(parent)
    combo_box.addItems([UiStrings().Top, UiStrings().Middle, UiStrings().Bottom])
    label.setBuddy(combo_box)
    return label, combo_box


def find_and_set_in_combo_box(combo_box, value_to_find, set_missing=True):
    """
    Find a string in a combo box and set it as the selected item if present

    :param combo_box: The combo box to check for selected items
    :param value_to_find: The value to find
    :param set_missing: if not found leave value as current
    """
    index = combo_box.findText(value_to_find, QtCore.Qt.MatchFlag.MatchExactly)
    if index == -1:
        # Not Found.
        index = 0 if set_missing else combo_box.currentIndex()
    combo_box.setCurrentIndex(index)


class MultipleViewModeList(QtWidgets.QListWidget):
    """
    An opinionated implementation of QListWidget that allows the list to use List View and
    Icon View.

    :param parent:
    :param mode: The default mode of the list.
    """
    def __init__(self, parent, mode=QtWidgets.QListWidget.ViewMode.ListMode):
        super().__init__(parent)
        self._view_mode_icon_size_list = None
        self._view_mode_icon_size_grid = None
        if mode == QtWidgets.QListWidget.ViewMode.IconMode:
            self.setViewMode(QtWidgets.QListWidget.ViewMode.IconMode)

    def set_icon_size_by_view_mode(self, mode, size):
        """
        Sets the preferred icon size by view mode.

        :param mode: Desired mode to set the default size
        :param size: Default size for the provided mode
        """
        if mode == QtWidgets.QListWidget.ViewMode.ListMode:
            self._view_mode_icon_size_list = size
        elif mode == QtWidgets.QListWidget.ViewMode.IconMode:
            self._view_mode_icon_size_grid = size
        if self.viewMode() == mode:
            self.setIconSize(size)

    def setViewMode(self, mode):
        if mode is None:
            mode = QtWidgets.QListWidget.ViewMode.ListMode
        super().setViewMode(mode)
        if mode == QtWidgets.QListWidget.ViewMode.IconMode:
            if self._view_mode_icon_size_list is None:
                self._view_mode_icon_size_list = self.iconSize()
            if self._view_mode_icon_size_grid is not None:
                self.setIconSize(self._view_mode_icon_size_grid)
            self.setUniformItemSizes(True)
            self.setResizeMode(QtWidgets.QListWidget.ResizeMode.Adjust)
            self._on_resize_icon_mode()
        elif mode == QtWidgets.QListWidget.ViewMode.ListMode:
            if self._view_mode_icon_size_grid is None:
                self._view_mode_icon_size_grid = self.iconSize()
            if self._view_mode_icon_size_list is not None:
                self.setIconSize(self._view_mode_icon_size_list)
            self.setUniformItemSizes(False)
            self.setResizeMode(QtWidgets.QListWidget.ResizeMode.Fixed)
            self.setFlow(QtWidgets.QListWidget.Flow.TopToBottom)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        self._on_resize_icon_mode()

    def _on_resize_icon_mode(self):
        if self.viewMode() == QtWidgets.QListWidget.ViewMode.IconMode:
            size = self.size()
            iconHeight = self.iconSize().height()
            if size.height() < ((iconHeight + (iconHeight / 2))):
                if self.flow() != QtWidgets.QListWidget.Flow.TopToBottom:
                    self.setFlow(QtWidgets.QListWidget.Flow.TopToBottom)
            elif self.flow() != QtWidgets.QListWidget.Flow.LeftToRight:
                self.setFlow(QtWidgets.QListWidget.Flow.LeftToRight)


def set_list_view_mode_toolbar_state(toolbar, mode):
    """
    Updates a OpenLPToolbar ListView button states after clicked

    :param toolbar: OpenLPToolbar instance
    :param mode: New QListView mode
    """
    if mode == QtWidgets.QListView.ViewMode.IconMode:
        toolbar.set_widget_checked('listView', False)
        toolbar.set_widget_checked('gridView', True)
    elif mode == QtWidgets.QListView.ViewMode.ListMode:
        toolbar.set_widget_checked('listView', True)
        toolbar.set_widget_checked('gridView', False)


def add_list_view_mode_items_to_toolbar(toolbar, trigger_handler):
    toolbar.add_toolbar_action('listView',
                               text=translate('OpenLP.Ui', 'List View'),
                               icon=UiIcons().view_list,
                               checked=False,
                               tooltip=translate('OpenLP.Ui', 'Shows the list in a list view.'),
                               triggers=trigger_handler.on_set_view_mode_list)
    toolbar.add_toolbar_action('gridView',
                               text=translate('OpenLP.Ui', 'Grid View'),
                               icon=UiIcons().view_grid,
                               checked=False,
                               tooltip=translate('OpenLP.Ui', 'Shows the list in a grid view.'),
                               triggers=trigger_handler.on_set_view_mode_grid)
