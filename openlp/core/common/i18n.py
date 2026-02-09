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
The :mod:`languages` module provides a list of language names with utility functions.
"""
import itertools
import locale
import logging
import re
from collections import namedtuple

from PySide6 import QtCore, QtWidgets

from openlp.core.common import Singleton
from openlp.core.common.applocation import AppLocation
from openlp.core.common.platform import is_macosx, is_win
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)


# Due to dependency issues, this HAS to be at the top of the file
def translate(context, text, comment=None, qt_translate=QtCore.QCoreApplication.translate):
    """
    A special shortcut method to wrap around the Qt6 translation functions. This abstracts the translation procedure so
    that we can change it if at a later date if necessary, without having to redo the whole of OpenLP.

    :param context: The translation context, used to give each string a context or a namespace.
    :param text: The text to put into the translation tables for translation.
    :param comment: An identifying string for when the same text is used in different roles within the same context.
    :param qt_translate:
    """
    return qt_translate(context, text, comment)


Language = namedtuple('Language', ['id', 'name', 'code'])
ICU_COLLATOR = None
DIGITS_OR_NONDIGITS = re.compile(r'\d+|\D+')
LANGUAGES = sorted([
    Language(1, translate('common.languages', '(Afan) Oromo', 'Language code: om'), 'om'),
    Language(2, translate('common.languages', 'Abkhazian', 'Language code: ab'), 'ab'),
    Language(3, translate('common.languages', 'Afar', 'Language code: aa'), 'aa'),
    Language(4, translate('common.languages', 'Afrikaans', 'Language code: af'), 'af'),
    Language(5, translate('common.languages', 'Albanian', 'Language code: sq'), 'sq'),
    Language(6, translate('common.languages', 'Amharic', 'Language code: am'), 'am'),
    Language(140, translate('common.languages', 'Amuzgo', 'Language code: amu'), 'amu'),
    Language(152, translate('common.languages', 'Ancient Greek', 'Language code: grc'), 'grc'),
    Language(7, translate('common.languages', 'Arabic', 'Language code: ar'), 'ar'),
    Language(8, translate('common.languages', 'Armenian', 'Language code: hy'), 'hy'),
    Language(9, translate('common.languages', 'Assamese', 'Language code: as'), 'as'),
    Language(10, translate('common.languages', 'Aymara', 'Language code: ay'), 'ay'),
    Language(11, translate('common.languages', 'Azerbaijani', 'Language code: az'), 'az'),
    Language(12, translate('common.languages', 'Bashkir', 'Language code: ba'), 'ba'),
    Language(13, translate('common.languages', 'Basque', 'Language code: eu'), 'eu'),
    Language(14, translate('common.languages', 'Bengali', 'Language code: bn'), 'bn'),
    Language(15, translate('common.languages', 'Bhutani', 'Language code: dz'), 'dz'),
    Language(16, translate('common.languages', 'Bihari', 'Language code: bh'), 'bh'),
    Language(17, translate('common.languages', 'Bislama', 'Language code: bi'), 'bi'),
    Language(18, translate('common.languages', 'Breton', 'Language code: br'), 'br'),
    Language(19, translate('common.languages', 'Bulgarian', 'Language code: bg'), 'bg'),
    Language(20, translate('common.languages', 'Burmese', 'Language code: my'), 'my'),
    Language(21, translate('common.languages', 'Byelorussian', 'Language code: be'), 'be'),
    Language(142, translate('common.languages', 'Cakchiquel', 'Language code: cak'), 'cak'),
    Language(22, translate('common.languages', 'Cambodian', 'Language code: km'), 'km'),
    Language(23, translate('common.languages', 'Catalan', 'Language code: ca'), 'ca'),
    Language(24, translate('common.languages', 'Chinese', 'Language code: zh'), 'zh'),
    Language(141, translate('common.languages', 'Comaltepec Chinantec', 'Language code: cco'), 'cco'),
    Language(25, translate('common.languages', 'Corsican', 'Language code: co'), 'co'),
    Language(26, translate('common.languages', 'Croatian', 'Language code: hr'), 'hr'),
    Language(27, translate('common.languages', 'Czech', 'Language code: cs'), 'cs'),
    Language(28, translate('common.languages', 'Danish', 'Language code: da'), 'da'),
    Language(29, translate('common.languages', 'Dutch', 'Language code: nl'), 'nl'),
    Language(30, translate('common.languages', 'English', 'Language code: en'), 'en'),
    Language(31, translate('common.languages', 'Esperanto', 'Language code: eo'), 'eo'),
    Language(32, translate('common.languages', 'Estonian', 'Language code: et'), 'et'),
    Language(33, translate('common.languages', 'Faeroese', 'Language code: fo'), 'fo'),
    Language(34, translate('common.languages', 'Fiji', 'Language code: fj'), 'fj'),
    Language(35, translate('common.languages', 'Finnish', 'Language code: fi'), 'fi'),
    Language(36, translate('common.languages', 'French', 'Language code: fr'), 'fr'),
    Language(37, translate('common.languages', 'Frisian', 'Language code: fy'), 'fy'),
    Language(38, translate('common.languages', 'Galician', 'Language code: gl'), 'gl'),
    Language(39, translate('common.languages', 'Georgian', 'Language code: ka'), 'ka'),
    Language(40, translate('common.languages', 'German', 'Language code: de'), 'de'),
    Language(41, translate('common.languages', 'Greek', 'Language code: el'), 'el'),
    Language(42, translate('common.languages', 'Greenlandic', 'Language code: kl'), 'kl'),
    Language(43, translate('common.languages', 'Guarani', 'Language code: gn'), 'gn'),
    Language(44, translate('common.languages', 'Gujarati', 'Language code: gu'), 'gu'),
    Language(143, translate('common.languages', 'Haitian Creole', 'Language code: ht'), 'ht'),
    Language(45, translate('common.languages', 'Hausa', 'Language code: ha'), 'ha'),
    Language(46, translate('common.languages', 'Hebrew (former iw)', 'Language code: he'), 'he'),
    Language(144, translate('common.languages', 'Hiligaynon', 'Language code: hil'), 'hil'),
    Language(47, translate('common.languages', 'Hindi', 'Language code: hi'), 'hi'),
    Language(48, translate('common.languages', 'Hungarian', 'Language code: hu'), 'hu'),
    Language(49, translate('common.languages', 'Icelandic', 'Language code: is'), 'is'),
    Language(50, translate('common.languages', 'Indonesian (former in)', 'Language code: id'), 'id'),
    Language(51, translate('common.languages', 'Interlingua', 'Language code: ia'), 'ia'),
    Language(52, translate('common.languages', 'Interlingue', 'Language code: ie'), 'ie'),
    Language(54, translate('common.languages', 'Inuktitut (Eskimo)', 'Language code: iu'), 'iu'),
    Language(53, translate('common.languages', 'Inupiak', 'Language code: ik'), 'ik'),
    Language(55, translate('common.languages', 'Irish', 'Language code: ga'), 'ga'),
    Language(56, translate('common.languages', 'Italian', 'Language code: it'), 'it'),
    Language(145, translate('common.languages', 'Jakalteko', 'Language code: jac'), 'jac'),
    Language(57, translate('common.languages', 'Japanese', 'Language code: ja'), 'ja'),
    Language(58, translate('common.languages', 'Javanese', 'Language code: jw'), 'jw'),
    Language(150, translate('common.languages', 'K\'iche\'', 'Language code: quc'), 'quc'),
    Language(59, translate('common.languages', 'Kannada', 'Language code: kn'), 'kn'),
    Language(60, translate('common.languages', 'Kashmiri', 'Language code: ks'), 'ks'),
    Language(61, translate('common.languages', 'Kazakh', 'Language code: kk'), 'kk'),
    Language(146, translate('common.languages', 'Kekchí ', 'Language code: kek'), 'kek'),
    Language(62, translate('common.languages', 'Kinyarwanda', 'Language code: rw'), 'rw'),
    Language(63, translate('common.languages', 'Kirghiz', 'Language code: ky'), 'ky'),
    Language(64, translate('common.languages', 'Kirundi', 'Language code: rn'), 'rn'),
    Language(65, translate('common.languages', 'Korean', 'Language code: ko'), 'ko'),
    Language(66, translate('common.languages', 'Kurdish', 'Language code: ku'), 'ku'),
    Language(67, translate('common.languages', 'Laothian', 'Language code: lo'), 'lo'),
    Language(68, translate('common.languages', 'Latin', 'Language code: la'), 'la'),
    Language(69, translate('common.languages', 'Latvian, Lettish', 'Language code: lv'), 'lv'),
    Language(70, translate('common.languages', 'Lingala', 'Language code: ln'), 'ln'),
    Language(71, translate('common.languages', 'Lithuanian', 'Language code: lt'), 'lt'),
    Language(72, translate('common.languages', 'Macedonian', 'Language code: mk'), 'mk'),
    Language(73, translate('common.languages', 'Malagasy', 'Language code: mg'), 'mg'),
    Language(74, translate('common.languages', 'Malay', 'Language code: ms'), 'ms'),
    Language(75, translate('common.languages', 'Malayalam', 'Language code: ml'), 'ml'),
    Language(76, translate('common.languages', 'Maltese', 'Language code: mt'), 'mt'),
    Language(148, translate('common.languages', 'Mam', 'Language code: mam'), 'mam'),
    Language(77, translate('common.languages', 'Maori', 'Language code: mi'), 'mi'),
    Language(147, translate('common.languages', 'Maori', 'Language code: mri'), 'mri'),
    Language(78, translate('common.languages', 'Marathi', 'Language code: mr'), 'mr'),
    Language(79, translate('common.languages', 'Moldavian', 'Language code: mo'), 'mo'),
    Language(80, translate('common.languages', 'Mongolian', 'Language code: mn'), 'mn'),
    Language(149, translate('common.languages', 'Nahuatl', 'Language code: nah'), 'nah'),
    Language(81, translate('common.languages', 'Nauru', 'Language code: na'), 'na'),
    Language(82, translate('common.languages', 'Nepali', 'Language code: ne'), 'ne'),
    Language(83, translate('common.languages', 'Norwegian', 'Language code: no'), 'no'),
    Language(84, translate('common.languages', 'Occitan', 'Language code: oc'), 'oc'),
    Language(85, translate('common.languages', 'Oriya', 'Language code: or'), 'or'),
    Language(86, translate('common.languages', 'Pashto, Pushto', 'Language code: ps'), 'ps'),
    Language(87, translate('common.languages', 'Persian', 'Language code: fa'), 'fa'),
    Language(151, translate('common.languages', 'Plautdietsch', 'Language code: pdt'), 'pdt'),
    Language(88, translate('common.languages', 'Polish', 'Language code: pl'), 'pl'),
    Language(89, translate('common.languages', 'Portuguese', 'Language code: pt'), 'pt'),
    Language(90, translate('common.languages', 'Punjabi', 'Language code: pa'), 'pa'),
    Language(91, translate('common.languages', 'Quechua', 'Language code: qu'), 'qu'),
    Language(92, translate('common.languages', 'Rhaeto-Romance', 'Language code: rm'), 'rm'),
    Language(93, translate('common.languages', 'Romanian', 'Language code: ro'), 'ro'),
    Language(94, translate('common.languages', 'Russian', 'Language code: ru'), 'ru'),
    Language(95, translate('common.languages', 'Samoan', 'Language code: sm'), 'sm'),
    Language(96, translate('common.languages', 'Sangro', 'Language code: sg'), 'sg'),
    Language(97, translate('common.languages', 'Sanskrit', 'Language code: sa'), 'sa'),
    Language(98, translate('common.languages', 'Scots Gaelic', 'Language code: gd'), 'gd'),
    Language(99, translate('common.languages', 'Serbian', 'Language code: sr'), 'sr'),
    Language(100, translate('common.languages', 'Serbo-Croatian', 'Language code: sh'), 'sh'),
    Language(101, translate('common.languages', 'Sesotho', 'Language code: st'), 'st'),
    Language(102, translate('common.languages', 'Setswana', 'Language code: tn'), 'tn'),
    Language(103, translate('common.languages', 'Shona', 'Language code: sn'), 'sn'),
    Language(104, translate('common.languages', 'Sindhi', 'Language code: sd'), 'sd'),
    Language(105, translate('common.languages', 'Singhalese', 'Language code: si'), 'si'),
    Language(106, translate('common.languages', 'Siswati', 'Language code: ss'), 'ss'),
    Language(107, translate('common.languages', 'Slovak', 'Language code: sk'), 'sk'),
    Language(108, translate('common.languages', 'Slovenian', 'Language code: sl'), 'sl'),
    Language(109, translate('common.languages', 'Somali', 'Language code: so'), 'so'),
    Language(110, translate('common.languages', 'Spanish', 'Language code: es'), 'es'),
    Language(111, translate('common.languages', 'Sudanese', 'Language code: su'), 'su'),
    Language(112, translate('common.languages', 'Swahili', 'Language code: sw'), 'sw'),
    Language(113, translate('common.languages', 'Swedish', 'Language code: sv'), 'sv'),
    Language(114, translate('common.languages', 'Tagalog', 'Language code: tl'), 'tl'),
    Language(115, translate('common.languages', 'Tajik', 'Language code: tg'), 'tg'),
    Language(116, translate('common.languages', 'Tamil', 'Language code: ta'), 'ta'),
    Language(117, translate('common.languages', 'Tatar', 'Language code: tt'), 'tt'),
    Language(118, translate('common.languages', 'Tegulu', 'Language code: te'), 'te'),
    Language(119, translate('common.languages', 'Thai', 'Language code: th'), 'th'),
    Language(120, translate('common.languages', 'Tibetan', 'Language code: bo'), 'bo'),
    Language(121, translate('common.languages', 'Tigrinya', 'Language code: ti'), 'ti'),
    Language(122, translate('common.languages', 'Tonga', 'Language code: to'), 'to'),
    Language(123, translate('common.languages', 'Tsonga', 'Language code: ts'), 'ts'),
    Language(124, translate('common.languages', 'Turkish', 'Language code: tr'), 'tr'),
    Language(125, translate('common.languages', 'Turkmen', 'Language code: tk'), 'tk'),
    Language(126, translate('common.languages', 'Twi', 'Language code: tw'), 'tw'),
    Language(127, translate('common.languages', 'Uigur', 'Language code: ug'), 'ug'),
    Language(128, translate('common.languages', 'Ukrainian', 'Language code: uk'), 'uk'),
    Language(129, translate('common.languages', 'Urdu', 'Language code: ur'), 'ur'),
    Language(153, translate('common.languages', 'Uspanteco', 'Language code: usp'), 'usp'),
    Language(130, translate('common.languages', 'Uzbek', 'Language code: uz'), 'uz'),
    Language(131, translate('common.languages', 'Vietnamese', 'Language code: vi'), 'vi'),
    Language(132, translate('common.languages', 'Volapuk', 'Language code: vo'), 'vo'),
    Language(133, translate('common.languages', 'Welch', 'Language code: cy'), 'cy'),
    Language(134, translate('common.languages', 'Wolof', 'Language code: wo'), 'wo'),
    Language(135, translate('common.languages', 'Xhosa', 'Language code: xh'), 'xh'),
    Language(136, translate('common.languages', 'Yiddish (former ji)', 'Language code: yi'), 'yi'),
    Language(137, translate('common.languages', 'Yoruba', 'Language code: yo'), 'yo'),
    Language(138, translate('common.languages', 'Zhuang', 'Language code: za'), 'za'),
    Language(139, translate('common.languages', 'Zulu', 'Language code: zu'), 'zu')
], key=lambda language: language.name)


class LanguageManager(object):
    """
    Helper for Language selection
    """
    __qm_list__ = {}
    auto_language = False

    @staticmethod
    def get_translators(language):
        """
        Set up a translator to use in this instance of OpenLP

        :param language: The language to load into the translator
        """
        lang_path = str(AppLocation.get_directory(AppLocation.LanguageDir))
        app_translator = QtCore.QTranslator()
        app_translator.load(language, lang_path)
        log.info(f"Language: '{language}' loaded.")
        # A translator for buttons and other default strings provided by Qt.
        if not is_win() and not is_macosx():
            lang_path = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.LibraryPath.TranslationsPath)
        # As of Qt6, the core translations come in 2 files per language
        default_translator = QtCore.QTranslator()
        default_translator.load('qt_%s' % language, lang_path)
        base_translator = QtCore.QTranslator()
        base_translator.load('qtbase_%s' % language, lang_path)
        return app_translator, default_translator, base_translator

    @staticmethod
    def find_qm_files():
        """
        Find all available language files in this OpenLP install
        """
        log.debug('Translation files: {files}'.format(files=AppLocation.get_directory(AppLocation.LanguageDir)))
        trans_dir = QtCore.QDir(str(AppLocation.get_directory(AppLocation.LanguageDir)))
        file_names = trans_dir.entryList(['*.qm'], QtCore.QDir.Filter.Files, QtCore.QDir.SortFlag.Name)
        # Remove qm files from the list which start with "qt".
        file_names = [file_ for file_ in file_names if not file_.startswith('qt')]
        return list(map(trans_dir.filePath, file_names))

    @staticmethod
    def language_name(qm_file):
        """
        Load the language name from a language file

        :param qm_file: The file to obtain the name from
        """
        translator = QtCore.QTranslator()
        translator.load(qm_file)
        return translator.translate('OpenLP.MainWindow', 'English', 'Please add the name of your language here')

    @staticmethod
    def get_language():
        """
        Retrieve a saved language to use from settings
        """
        language = Registry().get('settings').value('core/language')
        language = str(language)
        if re.match(r'\[(.*)\]', language):
            LanguageManager.auto_language = True
            language = QtCore.QLocale.system().name()[:2]
        log.info(f"Language: '{language}' detected.")
        return language

    @staticmethod
    def set_language(action, message=True):
        """
        Set the language to translate OpenLP into

        :param action:  The language menu option
        :param message:  Display the message option
        """
        language = 'en'
        if action:
            action_name = str(action.objectName())
            if action_name == 'autoLanguageItem':
                LanguageManager.auto_language = True
            else:
                LanguageManager.auto_language = False
                qm_list = LanguageManager.get_qm_list()
                language = str(qm_list[action_name])
        if LanguageManager.auto_language:
            language = '[{language}]'.format(language=language)
        Registry().get('settings').setValue('core/language', language)
        log.info("Language file: '{language}' written to conf file".format(language=language))
        if message:
            QtWidgets.QMessageBox.information(None,
                                              translate('OpenLP.LanguageManager', 'Language'),
                                              translate('OpenLP.LanguageManager',
                                                        'Please restart OpenLP to use your new language setting.'))

    @staticmethod
    def init_qm_list():
        """
        Initialise the list of available translations
        """
        LanguageManager.__qm_list__ = {}
        qm_files = LanguageManager.find_qm_files()
        for counter, qmf in enumerate(qm_files):
            reg_ex = QtCore.QRegularExpression("^.*i18n/(.*).qm")
            match = reg_ex.match(qmf)
            if match.hasMatch():
                name = '{regex}'.format(regex=match.captured(1))
                LanguageManager.__qm_list__[
                    '{count:>2d} {name}'.format(count=counter + 1, name=LanguageManager.language_name(qmf))] = name

    @staticmethod
    def get_qm_list():
        """
        Return the list of available translations
        """
        if not LanguageManager.__qm_list__:
            LanguageManager.init_qm_list()
        return LanguageManager.__qm_list__


class UiStrings(metaclass=Singleton):
    """
    Provide standard strings for objects to use.
    """
    def __init__(self):
        """
        These strings should need a good reason to be retranslated elsewhere.
        Should some/more/less of these have an &amp; attached?
        """
        self.About = translate('OpenLP.Ui', 'About')
        self.Add = translate('OpenLP.Ui', '&Add')
        self.AddFolder = translate('OpenLP.Ui', 'Add folder')
        self.AddFolderDot = translate('OpenLP.Ui', 'Add folder.')
        self.AddGroup = translate('OpenLP.Ui', 'Add group')
        self.AddGroupDot = translate('OpenLP.Ui', 'Add group.')
        self.Advanced = translate('OpenLP.Ui', 'Advanced')
        self.AllFiles = translate('OpenLP.Ui', 'All Files')
        self.Automatic = translate('OpenLP.Ui', 'Automatic')
        self.BackgroundColor = translate('OpenLP.Ui', 'Background Color')
        self.BackgroundColorColon = translate('OpenLP.Ui', 'Background color:')
        self.BibleShortSearchTitle = translate('OpenLP.Ui', 'Search is Empty or too Short')
        self.BibleShortSearch = translate('OpenLP.Ui', '<strong>The search you have entered is empty or shorter '
                                                       'than 3 characters long.</strong><br><br>Please try again with '
                                                       'a longer search.')
        self.BibleNoBiblesTitle = translate('OpenLP.Ui', 'No Bibles Available')
        self.BibleNoBibles = translate('OpenLP.Ui', '<strong>There are no Bibles currently installed.</strong><br><br>'
                                                    'Please use the Import Wizard to install one or more Bibles.')
        self.Bottom = translate('OpenLP.Ui', 'Bottom')
        self.Bridge = translate('SongsPlugin.VerseType', 'Bridge')
        self.Browse = translate('OpenLP.Ui', 'Browse...')
        self.Cancel = translate('OpenLP.Ui', 'Cancel')
        self.Center = translate('OpenLP.ThemeWizard', 'Center')
        self.CCLINumberLabel = translate('OpenLP.Ui', 'CCLI number:')
        self.CCLISongNumberLabel = translate('OpenLP.Ui', 'CCLI song number:')
        self.Chorus = translate('SongsPlugin.VerseType', 'Chorus')
        self.CreateService = translate('OpenLP.Ui', 'Create a new service.')
        self.ConfirmDelete = translate('OpenLP.Ui', 'Confirm Delete')
        self.Continuous = translate('OpenLP.Ui', 'Continuous')
        self.Default = translate('OpenLP.Ui', 'Default')
        self.DefaultColor = translate('OpenLP.Ui', 'Default Color:')
        self.DefaultServiceName = translate('OpenLP.Ui', 'Service %Y-%m-%d %H-%M',
                                            'This may not contain any of the following characters: /\\?*|<>[]":+\n'
                                            'See http://docs.python.org/library/datetime'
                                            '.html#strftime-strptime-behavior for more information.')
        self.Delete = translate('OpenLP.Ui', '&Delete')
        self.DisplayStyle = translate('OpenLP.Ui', 'Display style:')
        self.Down = translate('SongsPlugin.EditVerseForm', 'Down')
        self.Duplicate = translate('OpenLP.Ui', 'Duplicate Error')
        self.Edit = translate('OpenLP.Ui', '&Edit')
        self.EditVerse = translate('SongsPlugin.EditVerseForm', 'Edit Verse')
        self.EmptyField = translate('OpenLP.Ui', 'Empty Field')
        self.Ending = translate('SongsPlugin.VerseType', 'Ending')
        self.Error = translate('OpenLP.Ui', 'Error')
        self.Export = translate('OpenLP.Ui', 'Export')
        self.File = translate('OpenLP.Ui', 'File')
        self.FileCorrupt = translate('OpenLP.Ui', 'File appears to be corrupt.')
        self.FontSizePtUnit = translate('OpenLP.Ui', 'pt', 'Abbreviated font point size unit')
        self.ForcedSplit = translate('SongsPlugin.EditVerseForm', '&Forced Split')
        self.ForcedSplitToolTip = translate('SongsPlugin.EditVerseForm', 'Split the verse when displayed '
                                                                         'regardless of the screen size.')
        self.Help = translate('OpenLP.Ui', 'Help')
        self.Hours = translate('OpenLP.Ui', 'h', 'The abbreviated unit for hours')
        self.IFdSs = translate('OpenLP.Ui', 'Invalid Folder Selected', 'Singular')
        self.IFSs = translate('OpenLP.Ui', 'Invalid File Selected', 'Singular')
        self.IFSp = translate('OpenLP.Ui', 'Invalid Files Selected', 'Plural')
        self.Image = translate('OpenLP.Ui', 'Image')
        self.Import = translate('OpenLP.Ui', 'Import')
        self.Insert = translate('SongsPlugin.EditVerseForm', '&Insert')
        self.InsertToolTip = translate('SongsPlugin.EditVerseForm',
                                       'Split a slide into two by inserting a verse splitter.')
        self.Intro = translate('SongsPlugin.VerseType', 'Intro')
        self.Justify = translate('OpenLP.ThemeWizard', 'Justify')
        self.LayoutStyle = translate('OpenLP.Ui', 'Layout style:')
        self.Left = translate('OpenLP.ThemeWizard', 'Left')
        self.Live = translate('OpenLP.Ui', 'Live')
        self.LivePreviewShowsBlankScreen = translate('OpenLP.ServiceTab', 'Live preview shows blank screen')
        self.LiveStream = translate('OpenLP.Ui', 'Live Stream')
        self.LiveBGError = translate('OpenLP.Ui', 'Live Background Error')
        self.LiveToolbar = translate('OpenLP.Ui', 'Live Toolbar')
        self.Load = translate('OpenLP.Ui', 'Load')
        self.Manufacturer = translate('OpenLP.Ui', 'Manufacturer', 'Singular')
        self.Manufacturers = translate('OpenLP.Ui', 'Manufacturers', 'Plural')
        self.Model = translate('OpenLP.Ui', 'Model', 'Singular')
        self.Models = translate('OpenLP.Ui', 'Models', 'Plural')
        self.Minutes = translate('OpenLP.Ui', 'm', 'The abbreviated unit for minutes')
        self.Middle = translate('OpenLP.Ui', 'Middle')
        self.New = translate('OpenLP.Ui', 'New')
        self.NewService = translate('OpenLP.Ui', 'New Service')
        self.NewTheme = translate('OpenLP.Ui', 'New Theme')
        self.NextTrack = translate('OpenLP.Ui', 'Next Track')
        self.NFdSs = translate('OpenLP.Ui', 'No Folder Selected', 'Singular')
        self.NFSs = translate('OpenLP.Ui', 'No File Selected', 'Singular')
        self.NFSp = translate('OpenLP.Ui', 'No Files Selected', 'Plural')
        self.NISs = translate('OpenLP.Ui', 'No Item Selected', 'Singular')
        self.NISp = translate('OpenLP.Ui', 'No Items Selected', 'Plural')
        self.NoResults = translate('OpenLP.Ui', 'No Search Results')
        self.OpenLP = translate('OpenLP.Ui', 'OpenLP')
        self.OpenLPv2AndUp = translate('OpenLP.Ui', 'OpenLP Song Database')
        self.OpenLPStart = translate('OpenLP.Ui', 'OpenLP is already running on this machine. \nClosing this instance')
        self.OpenService = translate('OpenLP.Ui', 'Open service.')
        self.OptionalShowInFooter = translate('OpenLP.Ui', 'Optional, this will be displayed in footer.')
        self.OptionalHideInFooter = translate('OpenLP.Ui', 'Optional, this won\'t be displayed in footer.')
        self.Other = translate('SongsPlugin.VerseType', 'Other')
        self.PermissionError = translate('OpenLP.Ui', 'Permission Error')
        self.PlaySlidesInLoop = translate('OpenLP.Ui', 'Play Slides in Loop')
        self.PlaySlidesToEnd = translate('OpenLP.Ui', 'Play Slides to End')
        self.PreChorus = translate('SongsPlugin.VerseType', 'Pre-Chorus')
        self.Preview = translate('OpenLP.Ui', 'Preview')
        self.PreviewToolbar = translate('OpenLP.Ui', 'Preview Toolbar')
        self.PrintService = translate('OpenLP.Ui', 'Print Service')
        self.Projector = translate('OpenLP.Ui', 'Projector', 'Singular')
        self.Projectors = translate('OpenLP.Ui', 'Projectors', 'Plural')
        self.ReplaceBG = translate('OpenLP.Ui', 'Replace Background')
        self.ReplaceLiveBG = translate('OpenLP.Ui', 'Replace live background.')
        self.ReplaceLiveBGDisabled = translate('OpenLP.Ui', 'Replace live background is not available when the WebKit '
                                                            'player is disabled.')
        self.ResetBG = translate('OpenLP.Ui', 'Reset Background')
        self.ResetLiveBG = translate('OpenLP.Ui', 'Reset live background.')
        self.RequiredShowInFooter = translate('OpenLP.Ui', 'Required, this will be displayed in footer.')
        self.Right = translate('OpenLP.ThemeWizard', 'Right')
        self.Seconds = translate('OpenLP.Ui', 's', 'The abbreviated unit for seconds')
        self.SaveAndClose = translate('OpenLP.ui', translate('SongsPlugin.EditSongForm', '&Save && Close'))
        self.SaveAndPreview = translate('OpenLP.Ui', 'Save && Preview')
        self.ScreenSetupHasChangedTitle = translate('OpenLP.MainWindow', 'Screen setup has changed')
        self.ScreenSetupHasChanged = translate('OpenLP.MainWindow',
                                               'The screen setup has changed. OpenLP will try to '
                                               'automatically select a display screen, but '
                                               'you should consider updating the screen settings.')
        self.Search = translate('OpenLP.Ui', 'Search')
        self.SearchThemes = translate('OpenLP.Ui', 'Search Themes...', 'Search bar place holder text ')
        self.SelectDelete = translate('OpenLP.Ui', 'You must select an item to delete.')
        self.SelectEdit = translate('OpenLP.Ui', 'You must select an item to edit.')
        self.Settings = translate('OpenLP.Ui', 'Settings')
        self.SaveService = translate('OpenLP.Ui', 'Save Service')
        self.Service = translate('OpenLP.Ui', 'Service')
        self.ShortResults = translate('OpenLP.Ui', 'Please type more text to use \'Search As You Type\'')
        self.Split = translate('OpenLP.Ui', 'Optional &Split')
        self.SplitToolTip = translate('OpenLP.Ui',
                                      'Split a slide into two only if it does not fit on the screen as one slide.')
        self.StartingImport = translate('OpenLP.Ui', 'Starting import...')
        self.StopPlaySlidesInLoop = translate('OpenLP.Ui', 'Stop Play Slides in Loop')
        self.StopPlaySlidesToEnd = translate('OpenLP.Ui', 'Stop Play Slides to End')
        self.Theme = translate('OpenLP.Ui', 'Theme', 'Singular')
        self.Themes = translate('OpenLP.Ui', 'Themes', 'Plural')
        self.Tools = translate('OpenLP.Ui', 'Tools')
        self.Top = translate('OpenLP.Ui', 'Top')
        self.Transpose = translate('SongsPlugin.EditVerseForm', 'Transpose:')
        self.UnableToRead = translate('OpenLP.Ui', 'Unable to read the file(s) listed below, please check that '
                                                   'your user has permission to read the file(s) or that the '
                                                   'file(s) are not using cloud storage (e.g. Dropbox, OneDrive).')
        self.UnsupportedFile = translate('OpenLP.Ui', 'Unsupported File')
        self.Up = translate('SongsPlugin.EditVerseForm', 'Up')
        self.Verse = translate('SongsPlugin.VerseType', 'Verse')
        self.VersePerSlide = translate('OpenLP.Ui', 'Verse Per Slide')
        self.VersePerLine = translate('OpenLP.Ui', 'Verse Per Line')
        self.VerseType = translate('SongsPlugin.EditVerseForm', '&Verse type:')
        self.Version = translate('OpenLP.Ui', 'Version')
        self.View = translate('OpenLP.Ui', 'View')
        self.ViewMode = translate('OpenLP.Ui', 'View Mode')
        self.Video = translate('OpenLP.Ui', 'Video')
        self.Warning = translate('OpenLP.Ui', 'Warning')
        self.WebDownloadText = translate('OpenLP.Ui', 'Web Interface, Download and Install Latest Version')
        self.WholeVerseContinuous = translate('OpenLP.Ui', 'Continuous (whole verses)')
        book_chapter = translate('OpenLP.Ui', 'Book Chapter')
        chapter = translate('OpenLP.Ui', 'Chapter')
        verse = translate('OpenLP.Ui', 'Verse')
        gap = ' | '
        psalm = translate('OpenLP.Ui', 'Psalm')
        may_shorten = translate('OpenLP.Ui', 'Book names may be shortened from full names, for an example Ps 23 = '
                                             'Psalm 23')
        bible_scripture_items = \
            [book_chapter, gap, psalm, ' 23<br>',
             book_chapter, '%(range)s', chapter, gap, psalm, ' 23%(range)s24<br>',
             book_chapter, '%(verse)s', verse, '%(range)s', verse, gap, psalm, ' 23%(verse)s1%(range)s2<br>',
             book_chapter, '%(verse)s', verse, '%(range)s', verse, '%(list)s', verse, '%(range)s', verse, gap, psalm,
             ' 23%(verse)s1%(range)s2%(list)s5%(range)s6<br>',
             book_chapter, '%(verse)s', verse, '%(range)s', verse, '%(list)s', chapter, '%(verse)s', verse, '%(range)s',
             verse, gap, psalm, ' 23%(verse)s1%(range)s2%(list)s24%(verse)s1%(range)s3<br>',
             book_chapter, '%(verse)s', verse, '%(range)s', chapter, '%(verse)s', verse, gap, psalm,
             ' 23%(verse)s1%(range)s24%(verse)s1<br><br>', may_shorten]
        itertools.chain.from_iterable(itertools.repeat(strings, 1) if isinstance(strings, str)
                                      else strings for strings in bible_scripture_items)
        self.BibleScriptureError = ''.join(str(joined) for joined in bible_scripture_items)


def format_time(text, local_time):
    """
    Workaround for Python built-in time formatting function time.strftime().

    time.strftime() accepts only ascii characters. This function accepts
    unicode string and passes individual % placeholders to time.strftime().
    This ensures only ascii characters are passed to time.strftime().

    :param text:  The text to be processed.
    :param local_time: The time to be used to add to the string.  This is a time object
    """

    def match_formatting(match):
        """
        Format the match
        """
        return local_time.strftime(match.group())

    return re.sub(r'%[a-zA-Z]', match_formatting, text)


def get_locale_key(string):
    """
    Creates a key for case insensitive, locale aware string sorting.

    :param string: The corresponding string.
    """
    string = string.lower()
    # ICU is the prefered way to handle locale sort key, we fallback to locale.strxfrm which will work in most cases.
    global ICU_COLLATOR
    try:
        if ICU_COLLATOR is None:
            import icu
            language = LanguageManager.get_language()
            icu_locale = icu.Locale(language)
            ICU_COLLATOR = icu.Collator.createInstance(icu_locale)
        return ICU_COLLATOR.getSortKey(string)
    except Exception:
        log.warning('ICU not found! Fallback to strxfrm')
        return locale.strxfrm(string).encode()


def get_natural_key(string):
    """
    Generate a key for locale aware natural string sorting.

    :param string: string to be sorted by
    Returns a list of string compare keys and integers.
    """
    key = DIGITS_OR_NONDIGITS.findall(string)
    key = [int(part) if part.isdigit() else get_locale_key(part) for part in key]
    # Python 3 does not support comparison of different types anymore. So make sure, that we do not compare str
    # and int.
    if string and string[0].isdigit():
        return [b''] + key
    return key


def get_language(name):
    """
    Find the language by its name or code.

    :param name: The name or abbreviation of the language.
    :return: The first match as a Language namedtuple or None
    """
    if name:
        name_lower = name.lower()
        name_title = name_lower[:1].upper() + name_lower[1:]
        for language in LANGUAGES:
            if language.name == name_title or language.code == name_lower:
                return language
    return None
