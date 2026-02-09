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
The UI widgets of the print service dialog.
"""
from PySide6 import QtCore, QtPrintSupport, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.edits import SpellTextEdit


class ZoomSize(object):
    """
    Type enumeration for Combo Box sizes
    """
    Page = 0
    Width = 1
    OneHundred = 2
    SeventyFive = 3
    Fifty = 4
    TwentyFive = 5


class Ui_PrintServiceDialog(object):
    """
    The UI of the print service dialog
    """
    def setup_ui(self, print_service_dialog):
        """
        Set up the UI
        """
        print_service_dialog.setObjectName('print_service_dialog')
        print_service_dialog.setWindowIcon(UiIcons().main_icon)
        print_service_dialog.resize(664, 594)
        self.main_layout = QtWidgets.QVBoxLayout(print_service_dialog)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setObjectName('main_layout')
        self.toolbar = QtWidgets.QToolBar(print_service_dialog)
        self.toolbar.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.print_button = self.toolbar.addAction(UiIcons().print,
                                                   translate('OpenLP.PrintServiceForm', 'Print'))
        self.options_button = QtWidgets.QToolButton(self.toolbar)
        self.options_button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.options_button.setIcon(UiIcons().settings)
        self.options_button.setCheckable(True)
        self.toolbar.addWidget(self.options_button)
        self.toolbar.addSeparator()
        self.plain_copy = self.toolbar.addAction(UiIcons().clone,
                                                 translate('OpenLP.PrintServiceForm', 'Copy as Text'))
        self.html_copy = self.toolbar.addAction(UiIcons().clone,
                                                translate('OpenLP.PrintServiceForm', 'Copy as HTML'))
        self.toolbar.addSeparator()
        self.zoom_in_button = QtWidgets.QToolButton(self.toolbar)
        self.zoom_in_button.setIcon(UiIcons().search_plus)
        self.zoom_in_button.setObjectName('zoom_in_button')
        self.zoom_in_button.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.addWidget(self.zoom_in_button)
        self.zoom_out_button = QtWidgets.QToolButton(self.toolbar)
        self.zoom_out_button.setIcon(UiIcons().search_minus)
        self.zoom_out_button.setObjectName('zoom_out_button')
        self.zoom_out_button.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.addWidget(self.zoom_out_button)
        self.zoom_original_button = QtWidgets.QToolButton(self.toolbar)
        self.zoom_original_button.setIcon(UiIcons().search)
        self.zoom_original_button.setObjectName('zoom_original_button')
        self.zoom_original_button.setIconSize(QtCore.QSize(22, 22))
        self.toolbar.addWidget(self.zoom_original_button)
        self.zoom_combo_box = QtWidgets.QComboBox(print_service_dialog)
        self.zoom_combo_box.setObjectName('zoom_combo_box')
        self.toolbar.addWidget(self.zoom_combo_box)
        self.main_layout.addWidget(self.toolbar)
        self.preview_widget = QtPrintSupport.QPrintPreviewWidget(print_service_dialog)
        self.main_layout.addWidget(self.preview_widget)
        self.options_widget = QtWidgets.QWidget(print_service_dialog)
        self.options_widget.hide()
        self.options_widget.resize(400, 350)
        self.options_widget.setAutoFillBackground(True)
        self.options_layout = QtWidgets.QVBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(8, 8, 8, 8)
        self.title_label = QtWidgets.QLabel(self.options_widget)
        self.title_label.setObjectName('title_label')
        self.options_layout.addWidget(self.title_label)
        self.title_line_edit = QtWidgets.QLineEdit(self.options_widget)
        self.title_line_edit.setObjectName('title_line_edit')
        self.options_layout.addWidget(self.title_line_edit)
        self.footer_label = QtWidgets.QLabel(self.options_widget)
        self.footer_label.setObjectName('footer_label')
        self.options_layout.addWidget(self.footer_label)
        self.footer_text_edit = SpellTextEdit(self.options_widget, False)
        self.footer_text_edit.setObjectName('footer_text_edit')
        self.options_layout.addWidget(self.footer_text_edit)
        self.options_group_box = QtWidgets.QGroupBox()
        self.group_layout = QtWidgets.QVBoxLayout()
        self.slide_text_check_box = QtWidgets.QCheckBox()
        self.group_layout.addWidget(self.slide_text_check_box)
        self.page_break_after_text = QtWidgets.QCheckBox()
        self.group_layout.addWidget(self.page_break_after_text)
        self.notes_check_box = QtWidgets.QCheckBox()
        self.group_layout.addWidget(self.notes_check_box)
        self.meta_data_check_box = QtWidgets.QCheckBox()
        self.group_layout.addWidget(self.meta_data_check_box)
        self.show_chords_check_box = QtWidgets.QCheckBox()
        self.group_layout.addWidget(self.show_chords_check_box)
        self.group_layout.addStretch(1)
        self.options_group_box.setLayout(self.group_layout)
        self.options_layout.addWidget(self.options_group_box)

        self.retranslate_ui(print_service_dialog)
        self.options_button.toggled.connect(self.toggle_options)

    def retranslate_ui(self, print_service_dialog):
        """
        Translate the UI on the fly
        """
        print_service_dialog.setWindowTitle(UiStrings().PrintService)
        self.zoom_out_button.setToolTip(translate('OpenLP.PrintServiceForm', 'Zoom Out'))
        self.zoom_original_button.setToolTip(translate('OpenLP.PrintServiceForm', 'Zoom Original'))
        self.zoom_in_button.setToolTip(translate('OpenLP.PrintServiceForm', 'Zoom In'))
        self.options_button.setText(translate('OpenLP.PrintServiceForm', 'Options'))
        self.title_label.setText(translate('OpenLP.PrintServiceForm', 'Title:'))
        self.footer_label.setText(translate('OpenLP.PrintServiceForm', 'Service Note Text:'))
        self.options_group_box.setTitle(translate('OpenLP.PrintServiceForm', 'Other Options'))
        self.slide_text_check_box.setText(translate('OpenLP.PrintServiceForm', 'Include slide text if available'))
        self.page_break_after_text.setText(translate('OpenLP.PrintServiceForm', 'Add page break before each text item'))
        self.notes_check_box.setText(translate('OpenLP.PrintServiceForm', 'Include service item notes'))
        self.meta_data_check_box.setText(translate('OpenLP.PrintServiceForm', 'Include play length of media items'))
        self.show_chords_check_box.setText(translate('OpenLP.PrintServiceForm', 'Show chords'))
        self.title_line_edit.setText(translate('OpenLP.PrintServiceForm', 'Service Sheet'))
        # Do not change the order.
        self.zoom_combo_box.addItems([
            translate('OpenLP.PrintServiceDialog', 'Fit Page'),
            translate('OpenLP.PrintServiceDialog', 'Fit Width'),
            '100%',
            '75%',
            '50%',
            '25%'
        ])
