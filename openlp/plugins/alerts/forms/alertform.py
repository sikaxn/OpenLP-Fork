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

from PySide6 import QtCore, QtWidgets, QtGui

from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.plugins.alerts.lib.db import AlertItem

from openlp.plugins.alerts.forms.alertdialog import AlertDialog


class AlertForm(QtWidgets.QDialog, AlertDialog):
    """
    Provide UI for the alert system
    """
    def __init__(self, plugin):
        """
        Initialise the alert form
        """
        super(AlertForm, self).__init__(Registry().get('main_window'),
                                        QtCore.Qt.WindowType.WindowSystemMenuHint |
                                        QtCore.Qt.WindowType.WindowTitleHint |
                                        QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.manager = plugin.manager
        self.plugin = plugin
        self.item_id = None
        self.setup_ui(self)
        self.display_button.clicked.connect(self.on_display_clicked)
        self.display_close_button.clicked.connect(self.on_display_close_clicked)
        self.alert_text_edit.textChanged.connect(self.on_text_changed)
        self.new_button.clicked.connect(self.on_new_click)
        self.save_button.clicked.connect(self.on_save_all)
        self.alert_list_widget.doubleClicked.connect(self.on_double_click)
        self.alert_list_widget.clicked.connect(self.on_single_click)
        self.alert_list_widget.currentRowChanged.connect(self.on_current_row_changed)

    def exec(self):
        """
        Execute the dialog and return the exit code.
        """
        self.display_button.setEnabled(False)
        self.display_close_button.setEnabled(False)
        self.alert_text_edit.setText('')
        return QtWidgets.QDialog.exec(self)

    def load_list(self):
        """
        Loads the list with alerts.
        """
        self.alert_list_widget.clear()
        alerts = self.manager.get_all_objects(AlertItem, order_by_ref=AlertItem.text)
        for alert in alerts:
            item_name = QtWidgets.QListWidgetItem(alert.text)
            item_name.setData(QtCore.Qt.ItemDataRole.UserRole, alert.id)
            self.alert_list_widget.addItem(item_name)
            if alert.text == self.alert_text_edit.text():
                self.item_id = alert.id
                self.alert_list_widget.setCurrentRow(self.alert_list_widget.row(item_name))

    def on_display_clicked(self):
        """
        Display the current alert text.
        """
        self.trigger_alert(self.alert_text_edit.text())

    def on_display_close_clicked(self):
        """
        Close the alert preview.
        """
        if self.trigger_alert(self.alert_text_edit.text()):
            self.close()

    def on_delete_button_clicked(self):
        """
        Deletes the selected item.
        """
        item = self.alert_list_widget.currentItem()
        if item:
            item_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.manager.delete_object(AlertItem, item_id)
            row = self.alert_list_widget.row(item)
            self.alert_list_widget.takeItem(row)
        self.item_id = None
        self.alert_text_edit.setText('')

    def on_new_click(self):
        """
        Create a new alert.
        """
        if not self.alert_text_edit.text():
            QtWidgets.QMessageBox.information(self,
                                              translate('AlertsPlugin.AlertForm', 'New Alert'),
                                              translate('AlertsPlugin.AlertForm',
                                                        'You haven\'t specified any text for your alert. \n'
                                                        'Please type in some text before clicking New.'))
        else:
            alert = AlertItem(text=self.alert_text_edit.text())
            self.manager.save_object(alert)
        self.load_list()

    def on_save_all(self):
        """
        Save the alert, we are editing.
        """
        if self.item_id:
            alert = self.manager.get_object(AlertItem, self.item_id)
            alert.text = self.alert_text_edit.text()
            self.manager.save_object(alert)
            self.item_id = None
            self.load_list()
        self.save_button.setEnabled(False)

    def on_text_changed(self):
        """
        Enable save button when data has been changed by editing the form.
        """
        # Only enable the button, if we are editing an item.
        if self.item_id:
            self.save_button.setEnabled(True)
        if self.alert_text_edit.text():
            self.display_button.setEnabled(True)
            self.display_close_button.setEnabled(True)
        else:
            self.display_button.setEnabled(False)
            self.display_close_button.setEnabled(False)

    def on_double_click(self):
        """
        List item has been double clicked to display it.
        """
        item = self.alert_list_widget.selectedIndexes()[0]
        list_item = self.alert_list_widget.item(item.row())
        self.trigger_alert(list_item.text())
        self.alert_text_edit.setText(list_item.text())
        self.item_id = list_item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.save_button.setEnabled(False)

    def on_single_click(self):
        """
        List item has been single clicked to add it to the edit field so it can be changed.
        """
        item = self.alert_list_widget.selectedIndexes()[0]
        list_item = self.alert_list_widget.item(item.row())
        self.alert_text_edit.setText(list_item.text())
        self.item_id = list_item.data(QtCore.Qt.ItemDataRole.UserRole)
        # If the alert does not contain '<>' we clear the ParameterEdit field.
        if self.alert_text_edit.text().find('<>') == -1:
            self.parameter_edit.setText('')
        self.save_button.setEnabled(False)

    def trigger_alert(self, text):
        """
        Prepares the alert text for displaying.

        :param text: The alert text.
        """
        if not text:
            return False
        # We found '<>' in the alert text, but the ParameterEdit field is empty.
        if text.find('<>') != -1 and not self.parameter_edit.text() and \
            QtWidgets.QMessageBox.question(self,
                                           translate('AlertsPlugin.AlertForm', 'No Parameter Found'),
                                           translate('AlertsPlugin.AlertForm',
                                                     'You have not entered a parameter to be replaced.\n'
                                                     'Do you want to continue anyway?')
                                           ) == QtWidgets.QMessageBox.StandardButton.No:
            self.parameter_edit.setFocus()
            return False
        # The ParameterEdit field is not empty, but we have not found '<>'
        # in the alert text.
        elif text.find('<>') == -1 and self.parameter_edit.text() and \
            QtWidgets.QMessageBox.question(self,
                                           translate('AlertsPlugin.AlertForm', 'No Placeholder Found'),
                                           translate('AlertsPlugin.AlertForm',
                                                     'The alert text does not contain \'<>\'.\n'
                                                     'Do you want to continue anyway?')
                                           ) == QtWidgets.QMessageBox.StandardButton.No:
            self.parameter_edit.setFocus()
            return False
        text = text.replace('<>', self.parameter_edit.text())
        self.plugin.alerts_manager.display_alert(text)
        return True

    def on_current_row_changed(self, row):
        """
        Called when the *alert_list_widget*'s current row has been changed. This enables or disables buttons which
        require an item to act on.

        :param row: The row (int). If there is no current row, the value is -1.
        """
        if row == -1:
            self.display_button.setEnabled(False)
            self.display_close_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        else:
            self.display_button.setEnabled(True)
            self.display_close_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            # We do not need to enable the save button, as it is only enabled
            # when typing text in the "alert_text_edit".

    def provide_help(self):
        """
        Provide help within the form by opening the appropriate page of the openlp manual in the user's browser
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://manual.openlp.org/alert.html"))
