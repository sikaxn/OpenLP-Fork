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
Dialog for creating/editing an LRC song item.
"""
from pathlib import Path

from PySide6 import QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.ui.media import get_supported_media_suffix


class LrcEntryForm(QtWidgets.QDialog):
    """
    Simple editor for a song title + audio + LRC file pair.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.resize(640, 180)

        self.form_layout = QtWidgets.QFormLayout(self)
        self.form_layout.setObjectName('form_layout')

        self.title_edit = QtWidgets.QLineEdit(self)
        self.form_layout.addRow(translate('LrcPlayerPlugin.LrcEntryForm', 'Name'), self.title_edit)

        self.audio_layout = QtWidgets.QHBoxLayout()
        self.audio_path_edit = QtWidgets.QLineEdit(self)
        self.audio_browse_button = QtWidgets.QPushButton(translate('LrcPlayerPlugin.LrcEntryForm', 'Browse...'), self)
        self.audio_layout.addWidget(self.audio_path_edit)
        self.audio_layout.addWidget(self.audio_browse_button)
        self.form_layout.addRow(translate('LrcPlayerPlugin.LrcEntryForm', 'Audio File'), self.audio_layout)

        self.lrc_layout = QtWidgets.QHBoxLayout()
        self.lrc_path_edit = QtWidgets.QLineEdit(self)
        self.lrc_browse_button = QtWidgets.QPushButton(translate('LrcPlayerPlugin.LrcEntryForm', 'Browse...'), self)
        self.lrc_layout.addWidget(self.lrc_path_edit)
        self.lrc_layout.addWidget(self.lrc_browse_button)
        self.form_layout.addRow(translate('LrcPlayerPlugin.LrcEntryForm', 'LRC File'), self.lrc_layout)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel,
            parent=self
        )
        self.form_layout.addRow(self.button_box)

        self.audio_browse_button.clicked.connect(self.on_browse_audio)
        self.lrc_browse_button.clicked.connect(self.on_browse_lrc)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def load_values(self, title, audio_path, lrc_path):
        self.title_edit.setText(title or '')
        self.audio_path_edit.setText(audio_path or '')
        self.lrc_path_edit.setText(lrc_path or '')

    def values(self):
        return {
            'title': self.title_edit.text().strip(),
            'audio_path': self.audio_path_edit.text().strip(),
            'lrc_path': self.lrc_path_edit.text().strip()
        }

    def on_browse_audio(self):
        audio_exts, _ = get_supported_media_suffix()
        audio_filter = 'Audio ({exts});;{all_files} (*)'.format(
            exts=' '.join(audio_exts),
            all_files=UiStrings().AllFiles
        )
        selected_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            translate('LrcPlayerPlugin.LrcEntryForm', 'Select Audio File'),
            str(Path.home()),
            audio_filter
        )
        if selected_file:
            self.audio_path_edit.setText(selected_file)
            audio_path = Path(selected_file)
            self.title_edit.setText(audio_path.stem)
            guessed_lrc = audio_path.with_suffix('.lrc')
            if guessed_lrc.exists():
                self.lrc_path_edit.setText(str(guessed_lrc))

    def on_browse_lrc(self):
        selected_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            translate('LrcPlayerPlugin.LrcEntryForm', 'Select LRC File'),
            str(Path.home()),
            'LRC (*.lrc);;Text (*.txt);;{all_files} (*)'.format(all_files=UiStrings().AllFiles)
        )
        if selected_file:
            self.lrc_path_edit.setText(selected_file)

    def accept(self):
        values = self.values()
        if not values['title']:
            QtWidgets.QMessageBox.warning(
                self,
                translate('LrcPlayerPlugin.LrcEntryForm', 'Missing Name'),
                translate('LrcPlayerPlugin.LrcEntryForm', 'Please enter a name for this song.')
            )
            return
        if not Path(values['audio_path']).exists():
            QtWidgets.QMessageBox.warning(
                self,
                translate('LrcPlayerPlugin.LrcEntryForm', 'Missing Audio'),
                translate('LrcPlayerPlugin.LrcEntryForm', 'Please select a valid audio file.')
            )
            return
        if not Path(values['lrc_path']).exists():
            QtWidgets.QMessageBox.warning(
                self,
                translate('LrcPlayerPlugin.LrcEntryForm', 'Missing LRC'),
                translate('LrcPlayerPlugin.LrcEntryForm', 'Please select a valid LRC file.')
            )
            return
        super().accept()
