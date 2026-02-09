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
Package to test the openlp.core.lib.languages package.
"""
from unittest.mock import MagicMock, patch
import importlib.util
from openlp.core.common.i18n import LANGUAGES, Language, UiStrings, get_language, get_locale_key, get_natural_key, \
    translate, LanguageManager
from openlp.core.common.settings import Settings

icu_spec = importlib.util.find_spec('icu')
HAS_PYICU = icu_spec is not None


def test_languages_type():
    """
    Test the languages variable type
    """
    # GIVEN: The languages module
    # WHEN: Accessing the languages variable
    # THEN: It should be of type list
    assert isinstance(LANGUAGES, list), 'LANGUAGES should be of type list'


def test_language_selection_languages_type():
    """
    Test the selection of a language
    """
    # GIVEN: A list of languages from the languages module
    # WHEN: Selecting the first item
    language = LANGUAGES[0]

    # THEN: It should be an instance of the Language namedtuple
    assert isinstance(language, Language)
    assert language.id == 1
    assert language.name == '(Afan) Oromo'
    assert language.code == 'om'


def test_get_language_name():
    """
    Test get_language() when supplied with a language name.
    """

    # GIVEN: A language name, in capitals
    # WHEN: Calling get_language with it
    language = get_language('YORUBA')

    # THEN: The Language found using that name should be returned
    assert isinstance(language, Language)
    assert language.id == 137
    assert language.name == 'Yoruba'
    assert language.code == 'yo'


def test_get_language_code():
    """
    Test get_language() when supplied with a language code.
    """
    # GIVEN: A language code in capitals
    # WHEN: Calling get_language with it
    language = get_language('IA')

    # THEN: The Language found using that code should be returned
    assert isinstance(language, Language)
    assert language.id == 51
    assert language.name == 'Interlingua'
    assert language.code == 'ia'


def test_get_language_invalid():
    """
    Test get_language() when supplied with a string which is not a valid language name or code.
    """

    # GIVEN: A language code
    # WHEN: Calling get_language with it
    language = get_language('qwerty')

    # THEN: None should be returned
    assert language is None


def test_get_language_invalid_with_none():
    """
    Test get_language() when supplied with a string which is not a valid language name or code.
    """

    # GIVEN: A language code
    # WHEN: Calling get_language with it
    language = get_language(None)

    # THEN: None should be returned
    assert language is None


def test_get_locale_key():
    """
    Test the get_locale_key(string) function
    """
    with patch('openlp.core.common.i18n.LanguageManager.get_language') as mocked_get_language:
        # GIVEN: The language is German
        # 0x00C3 (A with diaresis) should be sorted as "A". 0x00DF (sharp s) should be sorted as "ss".
        mocked_get_language.return_value = 'de'
        unsorted_list = ['Auszug', 'Aushang', '\u00C4u\u00DFerung']

        # WHEN: We sort the list and use get_locale_key() to generate the sorting keys
        sorted_list = sorted(unsorted_list, key=get_locale_key)

        # THEN: We get a properly sorted list
        if HAS_PYICU:
            expected_list = ['Aushang', '\u00C4u\u00DFerung', 'Auszug']
        else:
            expected_list = ['Aushang', 'Auszug', '\u00C4u\u00DFerung']
        assert sorted_list == expected_list, 'Strings should be sorted properly'


def test_get_natural_key():
    """
    Test the get_natural_key(string) function
    """
    with patch('openlp.core.common.i18n.LanguageManager.get_language') as mocked_get_language:
        # GIVEN: The language is English (a language, which sorts digits before letters)
        mocked_get_language.return_value = 'en'
        unsorted_list = ['item 10a', 'item 3b', '1st item']

        # WHEN: We sort the list and use get_natural_key() to generate the sorting keys
        sorted_list = sorted(unsorted_list, key=get_natural_key)

        # THEN: We get a properly sorted list
        assert sorted_list == ['1st item', 'item 3b', 'item 10a'], 'Numbers should be sorted naturally'

        # GIVEN: The language is still English (a language, which sorts digits before letters)
        mocked_get_language.return_value = 'en'
        unsorted_list = ['1 songname', '100 songname', '2 songname']

        # WHEN: We sort the list and use get_natural_key() to generate the sorting keys
        sorted_list = sorted(unsorted_list, key=get_natural_key)

        # THEN: We get a properly sorted list
        assert sorted_list == ['1 songname', '2 songname', '100 songname'], 'Numbers should be sorted naturally'


def test_check_same_instance():
    """
    Test the UiStrings class - we always should have only one instance of the UiStrings class.
    """
    # WHEN: Create two instances of the UiStrings class.
    first_instance = UiStrings()
    second_instance = UiStrings()

    # THEN: Check if the instances are the same.
    assert first_instance is second_instance, 'Two UiStrings objects should be the same instance'


@patch('PySide6.QtCore.QLocale')
def test_get_language_from_settings(MockQLocale: MagicMock, settings: Settings):
    """
    Test that getting the language from settings returns the system locale
    """
    # GIVEN: A mocked out system locale
    MockQLocale.system.return_value.name.return_value = 'nl_NL'
    # WHEN: get_langauge() is called
    # THEN: The result should be correct
    assert LanguageManager.get_language() == 'nl'


def test_get_language_from_settings_returns_unchanged_if_unknown_format(settings: Settings):
    settings.setValue('core/language', '(foobar)')
    assert LanguageManager.get_language() == '(foobar)'


def test_translate():
    """
    Test the translate() function
    """
    # GIVEN: A string to translate and a mocked Qt translate function
    context = 'OpenLP.Tests'
    text = 'Untranslated string'
    comment = 'A comment'
    mocked_translate = MagicMock(return_value='Translated string')

    # WHEN: we call the translate function
    result = translate(context, text, comment, mocked_translate)

    # THEN: the translated string should be returned, and the mocked function should have been called
    mocked_translate.assert_called_with(context, text, comment)
    assert result == 'Translated string', 'The translated string should have been returned'
