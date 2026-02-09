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

from PySide6 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.media import parse_stream_path


class StreamSelectorFormBase(QtWidgets.QDialog):
    """
    Class to manage the clip selection
    """

    def __init__(self, parent, callback, theme_stream=False):
        """
        Constructor
        """
        super(StreamSelectorFormBase, self).__init__(parent,
                                                     QtCore.Qt.WindowType.WindowSystemMenuHint |
                                                     QtCore.Qt.WindowType.WindowTitleHint |
                                                     QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.callback = callback
        self.theme_stream = theme_stream
        self.setup_base_ui()
        self.type = ''
        self.mrl = None

    def setup_base_ui(self):
        self.setObjectName('stream_selector')
        self.combobox_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                                          QtWidgets.QSizePolicy.Policy.Fixed)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                  QtWidgets.QSizePolicy.Policy.MinimumExpanding))
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setObjectName('main_layout')

        self.top_widget = QtWidgets.QWidget(self)
        self.top_widget.setObjectName('top_widget')
        self.top_layout = QtWidgets.QFormLayout(self.top_widget)
        self.top_layout.setObjectName('top_layout')
        # Stream name
        if not self.theme_stream:
            self.stream_name_label = QtWidgets.QLabel(self.top_widget)
            self.stream_name_label.setObjectName('stream_name_label')
            self.stream_name_edit = QtWidgets.QLineEdit(self.top_widget)
            self.stream_name_edit.setObjectName('stream_name_edit')
            self.top_layout.addRow(self.stream_name_label, self.stream_name_edit)

    def exec(self):
        """
        Start dialog
        """
        return QtWidgets.QDialog.exec(self)

    def accept(self):
        """
        Saves the current stream as a clip to the mediamanager
        """
        if not self.theme_stream:
            # Verify that a stream name exists
            if not self.stream_name_edit.text().strip():
                critical_error_message_box(message=translate('MediaPlugin.StreamSelector', 'A Stream name is needed.'))
                return
            stream_name = self.stream_name_edit.text().strip()
        else:
            stream_name = ' '
        stream_string = '{type}:{name}&&{mrl}&&{options}'.format(
            type=self.type, name=stream_name, mrl=self.mrl,
            options='')
        self.callback(stream_string)
        return QtWidgets.QDialog.accept(self)

    def update_mrl_from_form(self, mrl):
        """
        Callback method used to update the mrl from the stream selector form
        """
        self.mrl = mrl

    def set_mrl(self, stream_str):
        """
        Setup the stream widgets based on the saved stream string. This is best effort as the string is
        editable for the user.
        """
        (_, self.mrl, options) = parse_stream_path(stream_str)
