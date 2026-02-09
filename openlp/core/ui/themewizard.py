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
The Create/Edit theme wizard
"""
from PySide6 import QtCore, QtGui, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.platform import is_macosx
from openlp.core.display.render import ThemePreviewRenderer
from openlp.core.lib.ui import add_welcome_page
from openlp.core.pages.alignment import AlignmentTransitionsPage
from openlp.core.pages.areaposition import AreaPositionPage
from openlp.core.pages.background import BackgroundPage
from openlp.core.pages.fontselect import FontSelectPage
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.layouts import AspectRatioLayout


class Ui_ThemeWizard(object):
    """
    The Create/Edit theme wizard
    """
    def setup_ui(self, theme_wizard):
        """
        Set up the UI
        """
        theme_wizard.setObjectName('OpenLP.ThemeWizard')
        theme_wizard.setWindowIcon(UiIcons().main_icon)
        theme_wizard.setModal(True)
        theme_wizard.setOptions(QtWidgets.QWizard.WizardOption.IndependentPages |
                                QtWidgets.QWizard.WizardOption.NoBackButtonOnStartPage |
                                QtWidgets.QWizard.WizardOption.HaveCustomButton1)
        theme_wizard.setFixedWidth(640)
        if is_macosx():     # pragma: no cover
            theme_wizard.setPixmap(QtWidgets.QWizard.WizardPixmap.BackgroundPixmap,
                                   QtGui.QPixmap(':/wizards/openlp-osx-wizard.png'))
        else:
            theme_wizard.setWizardStyle(QtWidgets.QWizard.WizardStyle.ModernStyle)
        self.spacer = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.Policy.Fixed,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        # Welcome Page
        add_welcome_page(theme_wizard, ':/wizards/wizard_createtheme.bmp')
        # Background Page
        self.background_page = BackgroundPage()
        self.background_page.setObjectName('background_page')
        theme_wizard.addPage(self.background_page)
        # Main Area Page
        self.main_area_page = FontSelectPage()
        self.main_area_page.setObjectName('main_area_page')
        self.main_area_page.disable_features(FontSelectPage.Wrap)
        theme_wizard.addPage(self.main_area_page)
        # Footer Area Page
        self.footer_area_page = FontSelectPage()
        self.footer_area_page.setObjectName('footer_area_page')
        self.footer_area_page.disable_features(FontSelectPage.Outline, FontSelectPage.Shadow)
        theme_wizard.addPage(self.footer_area_page)
        # Alignment Page
        self.alignment_page = AlignmentTransitionsPage()
        self.alignment_page.setObjectName('alignment_page')
        theme_wizard.addPage(self.alignment_page)
        # Area Position Page
        self.area_position_page = AreaPositionPage()
        self.area_position_page.setObjectName('area_position_page')
        theme_wizard.addPage(self.area_position_page)
        # Preview Page
        self.preview_page = QtWidgets.QWizardPage()
        self.preview_page.setObjectName('preview_page')
        self.preview_layout = QtWidgets.QVBoxLayout(self.preview_page)
        self.preview_layout.setObjectName('preview_layout')
        self.theme_name_layout = QtWidgets.QFormLayout()
        self.theme_name_layout.setObjectName('theme_name_layout')
        self.theme_name_label = QtWidgets.QLabel(self.preview_page)
        self.theme_name_label.setObjectName('theme_name_label')
        self.theme_name_edit = QtWidgets.QLineEdit(self.preview_page)
        self.theme_name_edit.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'[^/\\?*|<>\[\]":<>+%]+'), self))
        self.theme_name_edit.setObjectName('ThemeNameEdit')
        self.theme_name_layout.addRow(self.theme_name_label, self.theme_name_edit)
        self.preview_layout.addLayout(self.theme_name_layout)
        self.preview_area = QtWidgets.QWidget(self.preview_page)
        self.preview_area.setObjectName('PreviewArea')
        self.preview_area_layout = AspectRatioLayout(self.preview_area, 0.75)  # Dummy ratio, will be update
        self.preview_area_layout.margin = 8
        self.preview_area_layout.setSpacing(0)
        self.preview_area_layout.setObjectName('preview_web_layout')
        self.preview_box = ThemePreviewRenderer(self, window_title="Theme Editor Preview")
        self.preview_box.setObjectName('preview_box')
        self.preview_area_layout.addWidget(self.preview_box)
        self.preview_layout.addWidget(self.preview_area)
        theme_wizard.addPage(self.preview_page)
        self.retranslate_ui(theme_wizard)

    def retranslate_ui(self, theme_wizard):
        """
        Translate the UI on the fly
        """
        theme_wizard.setWindowTitle(translate('OpenLP.ThemeWizard', 'Theme Wizard'))
        text = translate('OpenLP.ThemeWizard', 'Welcome to the Theme Wizard')
        self.title_label.setText('<span style="font-size:14pt; font-weight:600;">{text}</span>'.format(text=text))
        self.information_label.setText(
            translate('OpenLP.ThemeWizard', 'This wizard will help you to create and edit your themes. Click the next '
                      'button below to start the process by setting up your background.'))
        self.background_page.setTitle(translate('OpenLP.ThemeWizard', 'Set Up Background'))
        self.background_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Set up your theme\'s background '
                                         'according to the parameters below.'))
        self.main_area_page.setTitle(translate('OpenLP.ThemeWizard', 'Main Area Font Details'))
        self.main_area_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Define the font and display '
                                                  'characteristics for the Display text'))
        self.footer_area_page.setTitle(translate('OpenLP.ThemeWizard', 'Footer Area Font Details'))
        self.footer_area_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Define the font and display '
                                                    'characteristics for the Footer text'))
        self.alignment_page.setTitle(translate('OpenLP.ThemeWizard', 'Text Formatting Details'))
        self.alignment_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Allows additional display '
                                                  'formatting information to be defined'))
        self.area_position_page.setTitle(translate('OpenLP.ThemeWizard', 'Output Area Locations'))
        self.area_position_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Allows you to change and move the'
                                                      ' Main and Footer areas.'))
        theme_wizard.setOption(QtWidgets.QWizard.WizardOption.HaveCustomButton1, False)
        theme_wizard.setButtonText(QtWidgets.QWizard.WizardButton.CustomButton1,
                                   translate('OpenLP.ThemeWizard', 'Layout Preview'))
        self.preview_page.setTitle(translate('OpenLP.ThemeWizard', 'Preview and Save'))
        self.preview_page.setSubTitle(translate('OpenLP.ThemeWizard', 'Preview the theme and save it.'))
        self.theme_name_label.setText(translate('OpenLP.ThemeWizard', 'Theme name:'))
