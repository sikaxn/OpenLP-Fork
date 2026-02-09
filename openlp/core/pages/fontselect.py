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
The :mod:`~openlp.core.pages.fontselect` module contains the font selection page used in the theme wizard
"""
from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.pages import GridLayoutPage
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.buttons import ColorButton
from openlp.core.widgets.labels import FormLabel


class FontSelectPage(GridLayoutPage):
    """
    A font selection widget
    """
    Outline = 'outline'
    Shadow = 'shadow'
    Wrap = 'wrap'
    LineSpacing = 'line_spacing'
    LetterSpacing = 'letter_spacing'

    font_name_changed = QtCore.Signal(str)
    font_color_changed = QtCore.Signal(str)
    is_bold_changed = QtCore.Signal(bool)
    is_italic_changed = QtCore.Signal(bool)
    font_size_changed = QtCore.Signal(int)
    wrap_changed = QtCore.Signal(bool)
    line_spacing_changed = QtCore.Signal(int)
    letter_spacing_changed = QtCore.Signal(int)
    is_outline_enabled_changed = QtCore.Signal(bool)
    outline_color_changed = QtCore.Signal(str)
    outline_size_changed = QtCore.Signal(int)
    is_shadow_enabled_changed = QtCore.Signal(bool)
    shadow_color_changed = QtCore.Signal(str)
    shadow_size_changed = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.feature_widgets = {
            FontSelectPage.Outline: [self.outline_groupbox],
            FontSelectPage.Shadow: [self.shadow_groupbox],
            FontSelectPage.Wrap: [self.wrap_check_box],
            FontSelectPage.LineSpacing: [self.line_spacing_label, self.line_spacing_spinbox],
            FontSelectPage.LetterSpacing: [self.letter_spacing_label, self.letter_spacing_spinbox]
        }

    def setup_ui(self):
        # Font name
        self.font_name_label = FormLabel(self)
        self.font_name_label.setObjectName('font_name_label')
        self.layout.addWidget(self.font_name_label, 0, 0)
        self.font_name_combobox = QtWidgets.QFontComboBox(self)
        self.font_name_combobox.setObjectName('font_name_combobox')
        self.layout.addWidget(self.font_name_combobox, 0, 1, 1, 3)
        # Font color
        self.font_color_label = FormLabel(self)
        self.font_color_label.setObjectName('font_color_label')
        self.layout.addWidget(self.font_color_label, 1, 0)
        self.font_color_button = ColorButton(self)
        self.font_color_button.setObjectName('font_color_button')
        self.layout.addWidget(self.font_color_button, 1, 1)
        # Font style
        self.font_style_label = FormLabel(self)
        self.font_style_label.setObjectName('font_style_label')
        self.layout.addWidget(self.font_style_label, 1, 2)
        self.style_layout = QtWidgets.QHBoxLayout()
        self.style_bold_button = QtWidgets.QToolButton(self)
        self.style_bold_button.setCheckable(True)
        self.style_bold_button.setIcon(UiIcons().bold)
        self.style_bold_button.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Bold))
        self.style_bold_button.setObjectName('style_bold_button')
        self.style_layout.addWidget(self.style_bold_button)
        self.style_italic_button = QtWidgets.QToolButton(self)
        self.style_italic_button.setCheckable(True)
        self.style_italic_button.setIcon(UiIcons().italic)
        self.style_italic_button.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Italic))
        self.style_italic_button.setObjectName('style_italic_button')
        self.style_layout.addWidget(self.style_italic_button)
        self.style_layout.addStretch(1)
        self.layout.addLayout(self.style_layout, 1, 3)
        # Font size
        self.font_size_label = FormLabel(self)
        self.font_size_label.setObjectName('font_size_label')
        self.layout.addWidget(self.font_size_label, 2, 0)
        self.font_size_spinbox = QtWidgets.QSpinBox(self)
        self.font_size_spinbox.setMaximum(999)
        self.font_size_spinbox.setValue(16)
        self.font_size_spinbox.setObjectName('font_size_spinbox')
        self.layout.addWidget(self.font_size_spinbox, 2, 1)
        # Word wrap
        self.wrap_check_box = QtWidgets.QCheckBox(self)
        self.wrap_check_box.setObjectName('wrap_check_box')
        self.layout.addWidget(self.wrap_check_box, 3, 1)
        # Line spacing
        self.line_spacing_label = FormLabel(self)
        self.line_spacing_label.setObjectName('line_spacing_label')
        self.layout.addWidget(self.line_spacing_label, 2, 2)
        self.line_spacing_spinbox = QtWidgets.QSpinBox(self)
        self.line_spacing_spinbox.setMinimum(-250)
        self.line_spacing_spinbox.setMaximum(250)
        self.line_spacing_spinbox.setObjectName('line_spacing_spinbox')
        self.layout.addWidget(self.line_spacing_spinbox, 2, 3)
        # Letter spacing
        self.letter_spacing_label = FormLabel(self)
        self.letter_spacing_label.setObjectName('letter_spacing_label')
        self.layout.addWidget(self.letter_spacing_label, 3, 2)
        self.letter_spacing_spinbox = QtWidgets.QDoubleSpinBox(self)
        self.letter_spacing_spinbox.setMinimum(-250)
        self.letter_spacing_spinbox.setMaximum(250)
        self.letter_spacing_spinbox.setObjectName('letter_spacing_spinbox')
        self.layout.addWidget(self.letter_spacing_spinbox, 3, 3)
        # Outline
        self.outline_groupbox = QtWidgets.QGroupBox(self)
        self.outline_groupbox.setCheckable(True)
        self.outline_groupbox.setChecked(False)
        self.outline_groupbox.setObjectName('outline_groupbox')
        self.outline_layout = QtWidgets.QGridLayout(self.outline_groupbox)
        self.layout.addWidget(self.outline_groupbox, 4, 0, 1, 2)
        # Outline colour
        self.outline_color_label = FormLabel(self.outline_groupbox)
        self.outline_color_label.setObjectName('outline_color_label')
        self.outline_layout.addWidget(self.outline_color_label, 0, 0)
        self.outline_color_button = ColorButton(self.outline_groupbox)
        self.outline_color_button.setObjectName('outline_color_button')
        self.outline_layout.addWidget(self.outline_color_button, 0, 1)
        # Outline size
        self.outline_size_label = FormLabel(self.outline_groupbox)
        self.outline_size_label.setObjectName('outline_size_label')
        self.outline_layout.addWidget(self.outline_size_label, 1, 0)
        self.outline_size_spinbox = QtWidgets.QSpinBox(self.outline_groupbox)
        self.outline_size_spinbox.setMaximum(9999)
        self.outline_size_spinbox.setObjectName('outline_size_spinbox')
        self.outline_layout.addWidget(self.outline_size_spinbox, 1, 1)
        # Shadow
        self.shadow_groupbox = QtWidgets.QGroupBox(self)
        self.shadow_groupbox.setCheckable(True)
        self.shadow_groupbox.setChecked(False)
        self.shadow_groupbox.setObjectName('shadow_groupbox')
        self.shadow_layout = QtWidgets.QGridLayout(self.shadow_groupbox)
        self.layout.addWidget(self.shadow_groupbox, 4, 2, 1, 2)
        # Shadow color
        self.shadow_color_label = FormLabel(self.shadow_groupbox)
        self.shadow_color_label.setObjectName('shadow_color_label')
        self.shadow_layout.addWidget(self.shadow_color_label, 0, 0)
        self.shadow_color_button = ColorButton(self.shadow_groupbox)
        self.shadow_color_button.setObjectName('shadow_color_button')
        self.shadow_layout.addWidget(self.shadow_color_button, 0, 1)
        # Shadow size
        self.shadow_size_label = FormLabel(self.shadow_groupbox)
        self.shadow_size_label.setObjectName('shadow_size_label')
        self.shadow_layout.addWidget(self.shadow_size_label, 1, 0)
        self.shadow_size_spinbox = QtWidgets.QSpinBox(self.shadow_groupbox)
        self.shadow_size_spinbox.setMaximum(9999)
        self.shadow_size_spinbox.setObjectName('shadow_size_spinbox')
        self.shadow_layout.addWidget(self.shadow_size_spinbox, 1, 1)
        # Connect all the signals
        self.font_name_combobox.activated.connect(self._on_font_name_changed)
        self.font_color_button.colorChanged.connect(self._on_font_color_changed)
        self.style_bold_button.toggled.connect(self._on_style_bold_toggled)
        self.style_italic_button.toggled.connect(self._on_style_italic_toggled)
        self.font_size_spinbox.valueChanged.connect(self._on_font_size_changed)
        self.wrap_check_box.stateChanged.connect(self._on_wrap_changed)
        self.line_spacing_spinbox.valueChanged.connect(self._on_line_spacing_changed)
        self.letter_spacing_spinbox.valueChanged.connect(self._on_letter_spacing_changed)
        self.outline_groupbox.toggled.connect(self._on_outline_toggled)
        self.outline_color_button.colorChanged.connect(self._on_outline_color_changed)
        self.outline_size_spinbox.valueChanged.connect(self._on_outline_size_changed)
        self.shadow_groupbox.toggled.connect(self._on_shadow_toggled)
        self.shadow_color_button.colorChanged.connect(self._on_shadow_color_changed)
        self.shadow_size_spinbox.valueChanged.connect(self._on_shadow_size_changed)

    def retranslate_ui(self):
        self.font_name_label.setText(translate('OpenLP.FontSelectWidget', 'Font:'))
        self.font_color_label.setText(translate('OpenLP.FontSelectWidget', 'Color:'))
        self.font_style_label.setText(translate('OpenLP.FontSelectWidget', 'Style:'))
        self.style_bold_button.setToolTip('{name} ({shortcut})'.format(
            name=translate('OpenLP.FontSelectWidget', 'Bold'),
            shortcut=QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Bold).toString()
        ))
        self.style_italic_button.setToolTip('{name} ({shortcut})'.format(
            name=translate('OpenLP.FontSelectWidget', 'Italic'),
            shortcut=QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Italic).toString()
        ))
        self.font_size_label.setText(translate('OpenLP.FontSelectWidget', 'Size:'))
        self.font_size_spinbox.setSuffix(' {unit}'.format(unit=UiStrings().FontSizePtUnit))
        self.wrap_check_box.setText(translate('OpenLP.FontSelectWidget', 'Word Wrap'))
        self.line_spacing_label.setText(translate('OpenLP.FontSelectWidget', 'Line Spacing:'))
        self.letter_spacing_label.setText(translate('OpenLP.FontSelectWidget', 'Letter Spacing:'))
        self.outline_groupbox.setTitle(translate('OpenLP.FontSelectWidget', 'Outline'))
        self.outline_color_label.setText(translate('OpenLP.FontSelectWidget', 'Color:'))
        self.outline_size_label.setText(translate('OpenLP.FontSelectWidget', 'Size:'))
        self.shadow_groupbox.setTitle(translate('OpenLP.FontSelectWidget', 'Shadow'))
        self.shadow_color_label.setText(translate('OpenLP.FontSelectWidget', 'Color:'))
        self.shadow_size_label.setText(translate('OpenLP.FontSelectWidget', 'Size:'))

    def _on_font_name_changed(self, name):
        if isinstance(name, str):
            self.font_name_changed.emit(name)

    def _on_font_color_changed(self, color):
        self.font_color_changed.emit(color)

    def _on_style_bold_toggled(self, is_bold):
        self.is_bold_changed.emit(is_bold)

    def _on_style_italic_toggled(self, is_italic):
        self.is_italic_changed.emit(is_italic)

    def _on_font_size_changed(self, size):
        self.font_size_changed.emit(size)

    def _on_wrap_changed(self, _):
        self.wrap_changed.emit(self.wrap_check_box.isChecked())

    def _on_line_spacing_changed(self, spacing):
        self.line_spacing_changed.emit(spacing)

    def _on_letter_spacing_changed(self, spacing):
        self.letter_spacing_changed.emit(spacing)

    def _on_outline_toggled(self, is_enabled):
        self.is_outline_enabled_changed.emit(is_enabled)

    def _on_outline_color_changed(self, color):
        self.outline_color_changed.emit(color)

    def _on_outline_size_changed(self, size):
        self.outline_size_changed.emit(size)

    def _on_shadow_toggled(self, is_enabled):
        self.is_shadow_enabled_changed.emit(is_enabled)

    def _on_shadow_color_changed(self, color):
        self.shadow_color_changed.emit(color)

    def _on_shadow_size_changed(self, size):
        self.shadow_size_changed.emit(size)

    def enable_features(self, *features):
        """
        Enable a feature
        """
        for feature_name in features:
            if feature_name not in self.feature_widgets.keys():
                raise KeyError('No such feature: {feature_name}'.format(feature_name=feature_name))
            for widget in self.feature_widgets[feature_name]:
                widget.show()

    def disable_features(self, *features):
        """
        Disable a feature
        """
        for feature_name in features:
            if feature_name not in self.feature_widgets.keys():
                raise KeyError('No such feature: {feature_name}'.format(feature_name=feature_name))
            for widget in self.feature_widgets[feature_name]:
                widget.hide()

    @property
    def font_name(self):
        return self.font_name_combobox.currentFont().family()

    @font_name.setter
    def font_name(self, font):
        self.font_name_combobox.setCurrentFont(QtGui.QFont(font))

    @property
    def font_color(self):
        return self.font_color_button.color

    @font_color.setter
    def font_color(self, color):
        self.font_color_button.color = color

    @property
    def is_bold(self):
        return self.style_bold_button.isChecked()

    @is_bold.setter
    def is_bold(self, is_bold):
        self.style_bold_button.setChecked(is_bold)

    @property
    def is_italic(self):
        return self.style_italic_button.isChecked()

    @is_italic.setter
    def is_italic(self, is_italic):
        self.style_italic_button.setChecked(is_italic)

    @property
    def font_size(self):
        return self.font_size_spinbox.value()

    @font_size.setter
    def font_size(self, size):
        self.font_size_spinbox.setValue(size)

    @property
    def wrap(self):
        return self.wrap_check_box.isChecked()

    @wrap.setter
    def wrap(self, wrap):
        self.wrap_check_box.setChecked(wrap)

    @property
    def line_spacing(self):
        return self.line_spacing_spinbox.value()

    @line_spacing.setter
    def line_spacing(self, line_spacing):
        self.line_spacing_spinbox.setValue(line_spacing)

    @property
    def letter_spacing(self):
        return self.letter_spacing_spinbox.value()

    @letter_spacing.setter
    def letter_spacing(self, letter_spacing):
        self.letter_spacing_spinbox.setValue(letter_spacing)

    @property
    def is_outline_enabled(self):
        return self.outline_groupbox.isChecked()

    @is_outline_enabled.setter
    def is_outline_enabled(self, is_enabled):
        self.outline_groupbox.setChecked(is_enabled)

    @property
    def outline_color(self):
        return self.outline_color_button.color

    @outline_color.setter
    def outline_color(self, color):
        self.outline_color_button.color = color

    @property
    def outline_size(self):
        return self.outline_size_spinbox.value()

    @outline_size.setter
    def outline_size(self, size):
        self.outline_size_spinbox.setValue(size)

    @property
    def is_shadow_enabled(self):
        return self.shadow_groupbox.isChecked()

    @is_shadow_enabled.setter
    def is_shadow_enabled(self, is_enabled):
        self.shadow_groupbox.setChecked(is_enabled)

    @property
    def shadow_color(self):
        return self.shadow_color_button.color

    @shadow_color.setter
    def shadow_color(self, color):
        self.shadow_color_button.color = color

    @property
    def shadow_size(self):
        return self.shadow_size_spinbox.value()

    @shadow_size.setter
    def shadow_size(self, size):
        self.shadow_size_spinbox.setValue(size)
