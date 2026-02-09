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
The song import functions for OpenLP.
"""
import logging

from PySide6 import QtCore, QtWidgets, QtGui

from openlp.core.common.handlers import handle_permission_error
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.widgets.dialogs import FileDialog
from openlp.core.widgets.edits import PathEdit
from openlp.core.widgets.enums import PathEditType
from openlp.core.widgets.wizard import OpenLPWizard, WizardStrings
from openlp.plugins.songs.lib.importer import SongFormat, SongFormatSelect


log = logging.getLogger(__name__)


class SongImportForm(OpenLPWizard, RegistryProperties):
    """
    This is the Song Import Wizard, which allows easy importing of Songs
    into OpenLP from other formats like OpenLyrics, OpenSong and CCLI.
    """
    completeChanged = QtCore.Signal()
    log.info('SongImportForm loaded')

    def __init__(self, parent, plugin):
        """
        Instantiate the wizard, and run any extra setup we need to.

        :param parent: The QWidget-derived parent of the wizard.
        :param plugin: The songs plugin.
        """
        super(SongImportForm, self).__init__(parent, plugin, 'songImportWizard', ':/wizards/wizard_song.bmp')
        self.clipboard = self.main_window.clipboard

    def setup_ui(self, image):
        """
        Set up the song wizard UI.
        """
        self.format_widgets = dict([(song_format, {}) for song_format in SongFormat.get_format_list()])
        super(SongImportForm, self).setup_ui(image)
        self.current_format = SongFormat.OpenLyrics
        self.format_stack.setCurrentIndex(self.current_format)
        self.format_combo_box.currentIndexChanged.connect(self.on_current_index_changed)

    def on_current_index_changed(self, index):
        """
        Called when the format combo box's index changed.
        """
        self.current_format = index
        self.format_stack.setCurrentIndex(index)
        self.source_page.completeChanged.emit()

    def custom_init(self):
        """
        Song wizard specific initialisation.
        """
        for song_format in SongFormat.get_format_list():
            if not SongFormat.get(song_format, 'availability'):
                self.format_widgets[song_format]['disabled_widget'].setVisible(True)
                self.format_widgets[song_format]['import_widget'].setVisible(False)

    def custom_signals(self):
        """
        Song wizard specific signals.
        """
        for song_format in SongFormat.get_format_list():
            select_mode = SongFormat.get(song_format, 'selectMode')
            if select_mode == SongFormatSelect.MultipleFiles:
                self.format_widgets[song_format]['addButton'].clicked.connect(self.on_add_button_clicked)
                self.format_widgets[song_format]['removeButton'].clicked.connect(self.on_remove_button_clicked)
            else:
                self.format_widgets[song_format]['path_edit'].pathChanged.connect(self.on_path_edit_path_changed)

    def add_custom_pages(self):
        """
        Add song wizard specific pages.
        """
        # Source Page
        self.source_page = SongImportSourcePage()
        self.source_page.setObjectName('source_page')
        self.source_layout = QtWidgets.QVBoxLayout(self.source_page)
        self.source_layout.setObjectName('source_layout')
        self.format_layout = QtWidgets.QFormLayout()
        self.format_layout.setObjectName('format_layout')
        self.format_label = QtWidgets.QLabel(self.source_page)
        self.format_label.setObjectName('format_label')
        self.format_combo_box = QtWidgets.QComboBox(self.source_page)
        self.format_combo_box.setObjectName('format_combo_box')
        self.format_layout.addRow(self.format_label, self.format_combo_box)
        self.format_spacer = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.Policy.Fixed,
                                                   QtWidgets.QSizePolicy.Policy.Minimum)
        self.format_layout.setItem(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.format_spacer)
        self.source_layout.addLayout(self.format_layout)
        self.format_h_spacing = self.format_layout.horizontalSpacing()
        self.format_v_spacing = self.format_layout.verticalSpacing()
        self.format_layout.setVerticalSpacing(0)
        self.stack_spacer = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.Policy.Fixed,
                                                  QtWidgets.QSizePolicy.Policy.Expanding)
        self.format_stack = QtWidgets.QStackedLayout()
        self.format_stack.setObjectName('format_stack')
        self.disablable_formats = []
        for self.current_format in SongFormat.get_format_list():
            self.add_file_select_item()
        self.source_layout.addLayout(self.format_stack)
        self.addPage(self.source_page)

    def retranslate_ui(self):
        """
        Song wizard localisation.
        """
        self.setWindowTitle(translate('SongsPlugin.ImportWizardForm', 'Song Import Wizard'))
        self.title_label.setText(
            WizardStrings.HeaderStyle.format(text=translate('OpenLP.Ui', 'Welcome to the Song Import Wizard')))
        self.information_label.setText(
            translate('SongsPlugin.ImportWizardForm',
                      'This wizard will help you to import songs from a variety of formats. Click the next button '
                      'below to start the process by selecting a format to import from.'))
        self.source_page.setTitle(WizardStrings.ImportSelect)
        self.source_page.setSubTitle(WizardStrings.ImportSelectLong)
        self.format_label.setText(WizardStrings.FormatLabel)
        for format_list in SongFormat.get_format_list():
            format_name, custom_combo_text, description_text, select_mode = \
                SongFormat.get(format_list, 'name', 'comboBoxText', 'descriptionText', 'selectMode')
            combo_box_text = (custom_combo_text if custom_combo_text else format_name)
            self.format_combo_box.setItemText(format_list, combo_box_text)
            if description_text is not None:
                self.format_widgets[format_list]['description_label'].setText(description_text)
            if select_mode == SongFormatSelect.MultipleFiles:
                self.format_widgets[format_list]['addButton'].setText(
                    translate('SongsPlugin.ImportWizardForm', 'Add Files...'))
                self.format_widgets[format_list]['removeButton'].setText(
                    translate('SongsPlugin.ImportWizardForm', 'Remove File(s)'))
            else:
                f_label = 'Filename:'
                if select_mode == SongFormatSelect.SingleFolder:
                    f_label = 'Folder:'
                self.format_widgets[format_list]['filepathLabel'].setText(
                    translate('SongsPlugin.ImportWizardForm', f_label))
        for format_list in self.disablable_formats:
            self.format_widgets[format_list]['disabled_label'].setText(SongFormat.get(format_list, 'disabledLabelText'))
        self.progress_page.setTitle(WizardStrings.Importing)
        self.progress_page.setSubTitle(
            translate('SongsPlugin.ImportWizardForm', 'Please wait while your songs are imported.'))
        self.progress_label.setText(WizardStrings.Ready)
        self.progress_bar.setFormat(WizardStrings.PercentSymbolFormat)
        self.error_copy_to_button.setText(translate('SongsPlugin.ImportWizardForm', 'Copy'))
        self.error_save_to_button.setText(translate('SongsPlugin.ImportWizardForm', 'Save to File'))
        # Align all QFormLayouts towards each other.
        formats = [f for f in SongFormat.get_format_list() if 'filepathLabel' in self.format_widgets[f]]
        labels = [self.format_widgets[f]['filepathLabel'] for f in formats] + [self.format_label]
        # Get max width of all labels
        max_label_width = max(labels, key=lambda label: label.minimumSizeHint().width()).minimumSizeHint().width()
        for label in labels:
            label.setFixedWidth(max_label_width)
        # Align descriptionLabels with rest of layout
        for format_list in SongFormat.get_format_list():
            if SongFormat.get(format_list, 'descriptionText') is not None:
                self.format_widgets[format_list]['descriptionSpacer'].changeSize(
                    max_label_width + self.format_h_spacing, 0, QtWidgets.QSizePolicy.Policy.Fixed,
                    QtWidgets.QSizePolicy.Policy.Fixed)

    def custom_page_changed(self, page_id):
        """
        Called when changing to a page other than the progress page.
        """
        if self.page(page_id) == self.source_page:
            self.on_current_index_changed(self.format_stack.currentIndex())

    def validateCurrentPage(self):
        """
        Re-implement the validateCurrentPage() method. Validate the current page before moving on to the next page.
        Provide each song format class with a chance to validate its input by overriding is_valid_source().
        """
        if self.currentPage() == self.welcome_page:
            return True
        elif self.currentPage() == self.source_page:
            this_format = self.current_format
            self.settings.setValue('songs/last import type', this_format)
            select_mode, class_, error_msg = SongFormat.get(this_format, 'selectMode', 'class', 'invalidSourceMsg')
            if select_mode == SongFormatSelect.MultipleFiles:
                import_source = self.get_list_of_paths(self.format_widgets[this_format]['file_list_widget'])
                error_title = UiStrings().IFSp
                focus_button = self.format_widgets[this_format]['addButton']
            else:
                import_source = self.format_widgets[this_format]['path_edit'].path
                error_title = (UiStrings().IFSs if select_mode == SongFormatSelect.SingleFile else UiStrings().IFdSs)
                focus_button = self.format_widgets[this_format]['path_edit']
            if not class_.is_valid_source(import_source):
                critical_error_message_box(error_title, error_msg)
                focus_button.setFocus()
                return False
            return True
        elif self.currentPage() == self.progress_page:
            return True

    def get_files(self, title, listbox, filters=''):
        """
        Opens a QFileDialog and writes the filenames to the given listbox.

        :param title: The title of the dialog (str).
        :param listbox: A listbox (QListWidget).
        :param filters: The file extension filters. It should contain the file descriptions as well as the file
            extensions. For example::

                'SongBeamer Files (*.sng)'
        """
        if filters:
            filters += ';;'
        filters += '{text} (*)'.format(text=UiStrings().AllFiles)
        file_paths, filter_used = FileDialog.getOpenFileNames(
            self, title,
            self.settings.value('songs/last directory import'), filters)
        for file_path in file_paths:
            list_item = QtWidgets.QListWidgetItem(str(file_path))
            list_item.setData(QtCore.Qt.ItemDataRole.UserRole, file_path)
            listbox.addItem(list_item)
        if file_paths:
            self.settings.setValue('songs/last directory import', file_paths[0].parent)

    def get_list_of_paths(self, list_box):
        """
        Return a list of file from the list_box

        :param list_box: The source list box
        """
        return [list_box.item(i).data(QtCore.Qt.ItemDataRole.UserRole) for i in range(list_box.count())]

    def remove_selected_items(self, list_box):
        """
        Remove selected list_box items

        :param list_box: the source list box
        """
        for item in list_box.selectedItems():
            item = list_box.takeItem(list_box.row(item))
            del item

    def on_add_button_clicked(self):
        """
        Add a file or directory.
        """
        this_format = self.current_format
        select_mode, format_name, ext_filter, custom_title = \
            SongFormat.get(this_format, 'selectMode', 'name', 'filter', 'getFilesTitle')
        title = custom_title if custom_title else WizardStrings.OpenTypeFile.format(file_type=format_name)
        if select_mode == SongFormatSelect.MultipleFiles:
            self.get_files(title, self.format_widgets[this_format]['file_list_widget'], ext_filter)
            self.source_page.completeChanged.emit()

    def on_remove_button_clicked(self):
        """
        Remove a file from the list.
        """
        self.remove_selected_items(self.format_widgets[self.current_format]['file_list_widget'])
        self.source_page.completeChanged.emit()

    def on_path_edit_path_changed(self):
        """
        Called when the content of the Filename/Folder edit box changes.
        """
        self.source_page.completeChanged.emit()

    def set_defaults(self):
        """
        Set default form values for the song import wizard.
        """
        self.restart()
        self.finish_button.setVisible(False)
        self.cancel_button.setVisible(True)
        last_import_type = self.settings.value('songs/last import type')
        if last_import_type < 0 or last_import_type >= self.format_combo_box.count():
            last_import_type = 0
        self.format_combo_box.setCurrentIndex(last_import_type)
        for format_list in SongFormat.get_format_list():
            select_mode = SongFormat.get(format_list, 'selectMode')
            if select_mode == SongFormatSelect.MultipleFiles:
                self.format_widgets[format_list]['file_list_widget'].clear()
        self.error_report_text_edit.clear()
        self.error_report_text_edit.setHidden(True)
        self.error_copy_to_button.setHidden(True)
        self.error_save_to_button.setHidden(True)

    def pre_wizard(self):
        """
        Perform pre import tasks
        """
        super(SongImportForm, self).pre_wizard()
        self.progress_label.setText(WizardStrings.StartingImport)
        self.application.process_events()

    def perform_wizard(self):
        """
        Perform the actual import. This method pulls in the correct importer class, and then runs the ``do_import``
        method of the importer to do the actual importing.
        """
        source_format = self.current_format
        select_mode = SongFormat.get(source_format, 'selectMode')
        if select_mode == SongFormatSelect.SingleFile:
            importer = self.plugin.import_songs(source_format,
                                                file_path=self.format_widgets[source_format]['path_edit'].path)
        elif select_mode == SongFormatSelect.SingleFolder:
            importer = self.plugin.import_songs(source_format,
                                                folder_path=self.format_widgets[source_format]['path_edit'].path)
        else:
            importer = self.plugin.import_songs(
                source_format,
                file_paths=self.get_list_of_paths(self.format_widgets[source_format]['file_list_widget']))
        try:
            importer.do_import()
            self.progress_label.setText(WizardStrings.FinishedImport)
        except OSError as e:
            log.exception('Importing songs failed')
            self.progress_label.setText(translate('SongsPlugin.ImportWizardForm',
                                                  'Your Song import failed. {error}').format(error=e))

    def on_error_copy_to_button_clicked(self):
        """
        Copy the error report to the clipboard.
        """
        self.clipboard.setText(self.error_report_text_edit.toPlainText())

    def on_error_save_to_button_clicked(self):
        """
        Save the error report to a file.

        :rtype: None
        """
        file_path, filter_used = FileDialog.getSaveFileName(self,
                                                            translate('SongPlugin.SongImporter', 'Save Error File'),
                                                            self.settings.value('songs/last directory import'))
        if file_path is None:
            return
        file_path.write_text(self.error_report_text_edit.toPlainText(), encoding='utf-8')

    def add_file_select_item(self):
        """
        Add a file selection page.
        """
        this_format = self.current_format
        format_name, prefix, can_disable, description_text, select_mode, filters = \
            SongFormat.get(this_format, 'name', 'prefix', 'canDisable', 'descriptionText', 'selectMode', 'filter')
        page = QtWidgets.QWidget()
        page.setObjectName(prefix + 'Page')
        if can_disable:
            import_widget = self.disablable_widget(page, prefix)
        else:
            import_widget = page
        import_layout = QtWidgets.QVBoxLayout(import_widget)
        import_layout.setContentsMargins(0, 0, 0, 0)
        import_layout.setObjectName(prefix + 'ImportLayout')
        if description_text is not None:
            description_layout = QtWidgets.QHBoxLayout()
            description_layout.setObjectName(prefix + 'DescriptionLayout')
            description_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Fixed,
                                                       QtWidgets.QSizePolicy.Policy.Fixed)
            description_layout.addSpacerItem(description_spacer)
            description_label = QtWidgets.QLabel(import_widget)
            description_label.setWordWrap(True)
            description_label.setOpenExternalLinks(True)
            description_label.setObjectName(prefix + '_description_label')
            description_layout.addWidget(description_label)
            import_layout.addLayout(description_layout)
            self.format_widgets[this_format]['description_label'] = description_label
            self.format_widgets[this_format]['descriptionSpacer'] = description_spacer
        if select_mode == SongFormatSelect.SingleFile or select_mode == SongFormatSelect.SingleFolder:
            file_path_layout = QtWidgets.QHBoxLayout()
            file_path_layout.setObjectName(prefix + '_file_path_layout')
            file_path_label = QtWidgets.QLabel(import_widget)
            file_path_layout.addWidget(file_path_label)
            if select_mode == SongFormatSelect.SingleFile:
                path_type = PathEditType.Files
                dialog_caption = WizardStrings.OpenTypeFile.format(file_type=format_name)
            else:
                path_type = PathEditType.Directories
                dialog_caption = WizardStrings.OpenTypeFolder.format(folder_name=format_name)
            path_edit = PathEdit(
                parent=import_widget, path_type=path_type, dialog_caption=dialog_caption, show_revert=False)
            if path_edit.filters:
                path_edit.filters = filters + ';;' + path_edit.filters
            else:
                path_edit.filters = filters
            path_edit.path = self.settings.value('songs/last directory import')
            file_path_layout.addWidget(path_edit)
            import_layout.addLayout(file_path_layout)
            import_layout.addSpacerItem(self.stack_spacer)
            self.format_widgets[this_format]['filepathLabel'] = file_path_label
            self.format_widgets[this_format]['path_edit'] = path_edit
        elif select_mode == SongFormatSelect.MultipleFiles:
            file_list_widget = QtWidgets.QListWidget(import_widget)
            file_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
            file_list_widget.setObjectName(prefix + 'FileListWidget')
            import_layout.addWidget(file_list_widget)
            button_layout = QtWidgets.QHBoxLayout()
            button_layout.setObjectName(prefix + '_button_layout')
            add_button = QtWidgets.QPushButton(import_widget)
            add_button.setIcon(self.open_icon)
            add_button.setObjectName(prefix + 'AddButton')
            button_layout.addWidget(add_button)
            button_layout.addStretch()
            remove_button = QtWidgets.QPushButton(import_widget)
            remove_button.setIcon(self.delete_icon)
            remove_button.setObjectName(prefix + 'RemoveButton')
            button_layout.addWidget(remove_button)
            import_layout.addLayout(button_layout)
            self.format_widgets[this_format]['file_list_widget'] = file_list_widget
            self.format_widgets[this_format]['button_layout'] = button_layout
            self.format_widgets[this_format]['addButton'] = add_button
            self.format_widgets[this_format]['removeButton'] = remove_button
        self.format_stack.addWidget(page)
        self.format_widgets[this_format]['page'] = page
        self.format_widgets[this_format]['importLayout'] = import_layout
        self.format_combo_box.addItem('')

    def disablable_widget(self, page, prefix):
        """
        Disable a widget.
        """
        this_format = self.current_format
        self.disablable_formats.append(this_format)
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setObjectName(prefix + '_layout')
        disabled_widget = QtWidgets.QWidget(page)
        disabled_widget.setVisible(False)
        disabled_widget.setObjectName(prefix + '_disabled_widget')
        disabled_layout = QtWidgets.QVBoxLayout(disabled_widget)
        disabled_layout.setContentsMargins(0, 0, 0, 0)
        disabled_layout.setObjectName(prefix + '_disabled_layout')
        disabled_label = QtWidgets.QLabel(disabled_widget)
        disabled_label.setWordWrap(True)
        disabled_label.setObjectName(prefix + '_disabled_label')
        disabled_layout.addWidget(disabled_label)
        disabled_layout.addSpacerItem(self.stack_spacer)
        layout.addWidget(disabled_widget)
        import_widget = QtWidgets.QWidget(page)
        import_widget.setObjectName(prefix + '_import_widget')
        layout.addWidget(import_widget)
        self.format_widgets[this_format]['layout'] = layout
        self.format_widgets[this_format]['disabled_widget'] = disabled_widget
        self.format_widgets[this_format]['disabled_layout'] = disabled_layout
        self.format_widgets[this_format]['disabled_label'] = disabled_label
        self.format_widgets[this_format]['import_widget'] = import_widget
        return import_widget

    def provide_help(self):
        """
        Provide help within the wizard by opening the appropriate page of the openlp manual in the user's browser
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://manual.openlp.org/songs.html#song-importer"))


class SongImportSourcePage(QtWidgets.QWizardPage):
    """
    Subclass of QtGui.QWizardPage to override isComplete() for Source Page.
    """
    def isComplete(self):
        """
        Return True if:

        * an available format is selected, and
        * if MultipleFiles mode, at least one file is selected
        * or if SingleFile mode, the specified file exists
        * or if SingleFolder mode, the specified folder exists

        When this method returns True, the wizard's Next button is enabled.

        :rtype: bool
        """
        wizard = self.wizard()
        this_format = wizard.current_format
        select_mode, format_available = SongFormat.get(this_format, 'selectMode', 'availability')
        if format_available:
            if select_mode == SongFormatSelect.MultipleFiles:
                if wizard.format_widgets[this_format]['file_list_widget'].count() > 0:
                    return True
            else:
                file_path = wizard.format_widgets[this_format]['path_edit'].path
                if file_path and file_path.exists():
                    with handle_permission_error(file_path):
                        if select_mode == SongFormatSelect.SingleFile and file_path.is_file():
                            return True
                        elif select_mode == SongFormatSelect.SingleFolder and file_path.is_dir():
                            return True
        return False
