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
The :mod:`lib` module contains all the library functionality for the bibles
plugin.
"""
import logging
import re

from openlp.core.common import Singleton
from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)


REFERENCE_MATCHES = {}
REFERENCE_SEPARATORS = {}


class BibleStrings(metaclass=Singleton):
    """
    Provide standard strings for objects to use.
    """
    def __init__(self):
        """
        These strings should need a good reason to be retranslated elsewhere.
        """
        self.BookNames = {
            'Gen': translate('BiblesPlugin', 'Genesis'),
            'Exod': translate('BiblesPlugin', 'Exodus'),
            'Lev': translate('BiblesPlugin', 'Leviticus'),
            'Num': translate('BiblesPlugin', 'Numbers'),
            'Deut': translate('BiblesPlugin', 'Deuteronomy'),
            'Josh': translate('BiblesPlugin', 'Joshua'),
            'Judg': translate('BiblesPlugin', 'Judges'),
            'Ruth': translate('BiblesPlugin', 'Ruth'),
            '1Sam': translate('BiblesPlugin', '1 Samuel'),
            '2Sam': translate('BiblesPlugin', '2 Samuel'),
            '1Kgs': translate('BiblesPlugin', '1 Kings'),
            '2Kgs': translate('BiblesPlugin', '2 Kings'),
            '1Chr': translate('BiblesPlugin', '1 Chronicles'),
            '2Chr': translate('BiblesPlugin', '2 Chronicles'),
            'Esra': translate('BiblesPlugin', 'Ezra'),
            'Neh': translate('BiblesPlugin', 'Nehemiah'),
            'Esth': translate('BiblesPlugin', 'Esther'),
            'Job': translate('BiblesPlugin', 'Job'),
            'Ps': translate('BiblesPlugin', 'Psalms'),
            'Prov': translate('BiblesPlugin', 'Proverbs'),
            'Eccl': translate('BiblesPlugin', 'Ecclesiastes'),
            'Song': translate('BiblesPlugin', 'Song of Solomon'),
            'Isa': translate('BiblesPlugin', 'Isaiah'),
            'Jer': translate('BiblesPlugin', 'Jeremiah'),
            'Lam': translate('BiblesPlugin', 'Lamentations'),
            'Ezek': translate('BiblesPlugin', 'Ezekiel'),
            'Dan': translate('BiblesPlugin', 'Daniel'),
            'Hos': translate('BiblesPlugin', 'Hosea'),
            'Joel': translate('BiblesPlugin', 'Joel'),
            'Amos': translate('BiblesPlugin', 'Amos'),
            'Obad': translate('BiblesPlugin', 'Obadiah'),
            'Jonah': translate('BiblesPlugin', 'Jonah'),
            'Mic': translate('BiblesPlugin', 'Micah'),
            'Nah': translate('BiblesPlugin', 'Nahum'),
            'Hab': translate('BiblesPlugin', 'Habakkuk'),
            'Zeph': translate('BiblesPlugin', 'Zephaniah'),
            'Hag': translate('BiblesPlugin', 'Haggai'),
            'Zech': translate('BiblesPlugin', 'Zechariah'),
            'Mal': translate('BiblesPlugin', 'Malachi'),
            'Matt': translate('BiblesPlugin', 'Matthew'),
            'Mark': translate('BiblesPlugin', 'Mark'),
            'Luke': translate('BiblesPlugin', 'Luke'),
            'John': translate('BiblesPlugin', 'John'),
            'Acts': translate('BiblesPlugin', 'Acts'),
            'Rom': translate('BiblesPlugin', 'Romans'),
            '1Cor': translate('BiblesPlugin', '1 Corinthians'),
            '2Cor': translate('BiblesPlugin', '2 Corinthians'),
            'Gal': translate('BiblesPlugin', 'Galatians'),
            'Eph': translate('BiblesPlugin', 'Ephesians'),
            'Phil': translate('BiblesPlugin', 'Philippians'),
            'Col': translate('BiblesPlugin', 'Colossians'),
            '1Thess': translate('BiblesPlugin', '1 Thessalonians'),
            '2Thess': translate('BiblesPlugin', '2 Thessalonians'),
            '1Tim': translate('BiblesPlugin', '1 Timothy'),
            '2Tim': translate('BiblesPlugin', '2 Timothy'),
            'Titus': translate('BiblesPlugin', 'Titus'),
            'Phlm': translate('BiblesPlugin', 'Philemon'),
            'Heb': translate('BiblesPlugin', 'Hebrews'),
            'Jas': translate('BiblesPlugin', 'James'),
            '1Pet': translate('BiblesPlugin', '1 Peter'),
            '2Pet': translate('BiblesPlugin', '2 Peter'),
            '1John': translate('BiblesPlugin', '1 John'),
            '2John': translate('BiblesPlugin', '2 John'),
            '3John': translate('BiblesPlugin', '3 John'),
            'Jude': translate('BiblesPlugin', 'Jude'),
            'Rev': translate('BiblesPlugin', 'Revelation'),
            'Jdt': translate('BiblesPlugin', 'Judith'),
            'Wis': translate('BiblesPlugin', 'Wisdom'),
            'Tob': translate('BiblesPlugin', 'Tobit'),
            'Sir': translate('BiblesPlugin', 'Sirach'),
            'Bar': translate('BiblesPlugin', 'Baruch'),
            '1Macc': translate('BiblesPlugin', '1 Maccabees'),
            '2Macc': translate('BiblesPlugin', '2 Maccabees'),
            '3Macc': translate('BiblesPlugin', '3 Maccabees'),
            '4Macc': translate('BiblesPlugin', '4 Maccabees'),
            'AddDan': translate('BiblesPlugin', 'Rest of Daniel'),
            'AddEsth': translate('BiblesPlugin', 'Rest of Esther'),
            'PrMan': translate('BiblesPlugin', 'Prayer of Manasses'),
            'LetJer': translate('BiblesPlugin', 'Letter of Jeremiah'),
            'PrAza': translate('BiblesPlugin', 'Prayer of Azariah'),
            'Sus': translate('BiblesPlugin', 'Susanna'),
            'Bel': translate('BiblesPlugin', 'Bel'),
            '1Esdr': translate('BiblesPlugin', '1 Esdras'),
            '2Esdr': translate('BiblesPlugin', '2 Esdras')
        }


def update_reference_separators():
    """
    Updates separators and matches for parsing and formatting scripture references.
    """
    default_separators = [
        '|'.join([
            translate('BiblesPlugin', ':', 'Verse identifier e.g. Genesis 1 : 1 = Genesis Chapter 1 Verse 1'),
            translate('BiblesPlugin', 'v', 'Verse identifier e.g. Genesis 1 v 1 = Genesis Chapter 1 Verse 1'),
            translate('BiblesPlugin', 'V', 'Verse identifier e.g. Genesis 1 V 1 = Genesis Chapter 1 Verse 1'),
            translate('BiblesPlugin', 'verse', 'Verse identifier e.g. Genesis 1 verse 1 = Genesis Chapter 1 Verse 1'),
            translate('BiblesPlugin', 'verses',
                      'Verse identifier e.g. Genesis 1 verses 1 - 2 = Genesis Chapter 1 Verses 1 to 2')]),
        '|'.join([
            translate('BiblesPlugin', '-',
                      'range identifier e.g. Genesis 1 verse 1 - 2 = Genesis Chapter 1 Verses 1 To 2'),
            translate('BiblesPlugin', 'to',
                      'range identifier e.g. Genesis 1 verse 1 - 2 = Genesis Chapter 1 Verses 1 To 2')]),
        '|'.join([
            translate('BiblesPlugin', ',', 'connecting identifier e.g. Genesis 1 verse 1 - 2, 4 - 5 = '
                                           'Genesis Chapter 1 Verses 1 To 2 And Verses 4 To 5'),
            translate('BiblesPlugin', 'and', 'connecting identifier e.g. Genesis 1 verse 1 - 2 and 4 - 5 = '
                                             'Genesis Chapter 1 Verses 1 To 2 And Verses 4 To 5')]),
        '|'.join([translate('BiblesPlugin', 'end', 'ending identifier e.g. Genesis 1 verse 1 - end = '
                                                   'Genesis Chapter 1 Verses 1 To The Last Verse')])]
    settings = Registry().get('settings')
    custom_separators = [
        settings.value('bibles/verse separator'),
        settings.value('bibles/range separator'),
        settings.value('bibles/list separator'),
        settings.value('bibles/end separator')]
    for index, role in enumerate(['v', 'r', 'l', 'e']):
        if custom_separators[index].strip('|') == '':
            source_string = default_separators[index].strip('|')
        else:
            source_string = custom_separators[index].strip('|')
        while '||' in source_string:
            source_string = source_string.replace('||', '|')
        if role != 'e':
            REFERENCE_SEPARATORS['sep_{role}_display'.format(role=role)] = source_string.split('|')[0]
        # escape reserved characters
        for character in '\\.^$*+?{}[]()':
            source_string = source_string.replace(character, '\\' + character)
        # add various Unicode alternatives
        source_string = source_string.replace('-', '(?:[-\u00AD\u2010\u2011\u2012\u2014\u2014\u2212\uFE63\uFF0D])')
        source_string = source_string.replace(',', '(?:[,\u201A])')
        REFERENCE_SEPARATORS['sep_{role}'.format(role=role)] = r'\s*(?:{source})\s*'.format(source=source_string)
        REFERENCE_SEPARATORS['sep_{role}_default'.format(role=role)] = default_separators[index]
    # verse range match: (<chapter>:)?<verse>(-((<chapter>:)?<verse>|end)?)?
    range_regex = '(?:(?P<from_chapter>[0-9]+){sep_v})?' \
        '(?P<from_verse>[0-9]+)(?P<range_to>{sep_r}(?:(?:(?P<to_chapter>' \
        '[0-9]+){sep_v})?(?P<to_verse>[0-9]+)|{sep_e})?)?'.format_map(REFERENCE_SEPARATORS)
    REFERENCE_MATCHES['range'] = re.compile(r'^\s*{range}\s*$'.format(range=range_regex))
    REFERENCE_MATCHES['range_separator'] = re.compile(REFERENCE_SEPARATORS['sep_l'])
    # full reference match: <book>(<range>(,(?!$)|(?=$)))+
    REFERENCE_MATCHES['full'] = \
        re.compile(r'^\s*(?!\s)(?P<book>[\d]*[.]?[^\d\.]+)\.*(?<!\s)\s*'
                   r'(?P<ranges>(?:{range_regex}(?:{sep_l}(?!\s*$)|(?=\s*$)))+)\s*$'.format(
                       range_regex=range_regex, sep_l=REFERENCE_SEPARATORS['sep_l']))


def get_reference_separator(separator_type):
    """
    Provides separators for parsing and formatting scripture references.

    :param separator_type: The role and format of the separator.
    """
    if not REFERENCE_SEPARATORS:
        update_reference_separators()
    return REFERENCE_SEPARATORS[separator_type]


def get_reference_match(match_type):
    """
    Provides matches for parsing scripture references strings.

    :param match_type:  The type of match is ``range_separator``, ``range`` or ``full``.
    """
    if not REFERENCE_MATCHES:
        update_reference_separators()
    return REFERENCE_MATCHES[match_type]


def parse_reference(reference, bible, language_selection, book_ref_id=False):
    r"""
    This is the next generation über-awesome function that takes a person's typed in string and converts it to a list
    of references to be queried from the Bible database files.

    :param reference: A string. The Bible reference to parse.
    :param bible:  A object. The Bible database object.
    :param language_selection:  An int. The language selection the user has chosen in settings section.
    :param book_ref_id: A string. The book reference id.

    The reference list is a list of tuples, with each tuple structured like this::

        (book, chapter, from_verse, to_verse)

    For example::

        [('John', 3, 16, 18), ('John', 4, 1, 1)]

    **Reference string details:**

    Each reference starts with the book name and a chapter number. These are both mandatory.

    * ``John 3`` refers to Gospel of John chapter 3

    A reference range can be given after a range separator.

    * ``John 3-5`` refers to John chapters 3 to 5

    Single verses can be addressed after a verse separator.

    * ``John 3:16`` refers to John chapter 3 verse 16
    * ``John 3:16-4:3`` refers to John chapter 3 verse 16 to chapter 4 verse 3

    After a verse reference all further single values are treat as verse in the last selected chapter.

    * ``John 3:16-18`` refers to John chapter 3 verses 16 to 18

    After a list separator it is possible to refer to additional verses. They are build analog to the first ones. This
    way it is possible to define each number of verse references. It is not possible to refer to verses in additional
    books.

    * ``John 3:16,18`` refers to John chapter 3 verses 16 and 18
    * ``John 3:16-18,20`` refers to John chapter 3 verses 16 to 18 and 20
    * ``John 3:16-18,4:1`` refers to John chapter 3 verses 16 to 18 and chapter 4 verse 1

    If there is a range separator without further verse declaration the last refered chapter is addressed until the end.

    ``range_regex`` is a regular expression which matches for verse range declarations:

    ``(?:(?P<from_chapter>[0-9]+)%(sep_v)s)?``
        It starts with a optional chapter reference ``from_chapter`` followed by a verse separator.

    ``(?P<from_verse>[0-9]+)``
        The verse reference ``from_verse`` is manditory

    ``(?P<range_to>%(sep_r)s(?:`` ... ``|%(sep_e)s)?)?``
        A ``range_to`` declaration is optional. It starts with a range separator and contains optional a chapter and
        verse declaration or a end separator.

    ``(?:(?P<to_chapter>[0-9]+)%(sep_v)s)?``
        The ``to_chapter`` reference with separator is equivalent to group 1.

    ``(?P<to_verse>[0-9]+)``
        The ``to_verse`` reference is equivalent to group 2.

    The full reference is matched against get_reference_match('full'). This regular expression looks like this:

    ``^\s*(?!\s)(?P<book>[\d]*[^\d]+)(?<!\s)\s*``
        The ``book`` group starts with the first non-whitespace character. There are optional leading digits followed by
        non-digits. The group ends before the whitespace, or a full stop in front of the next digit.

    ``(?P<ranges>(?:%(range_regex)s(?:%(sep_l)s(?!\s*$)|(?=\s*$)))+)\s*$``
        The second group contains all ``ranges``. This can be multiple declarations of range_regex separated by a list
        separator.

    """
    log.debug('parse_reference("{text}")'.format(text=reference))
    match = get_reference_match('full').match(reference)
    if match:
        log.debug('Matched reference {text}'.format(text=reference))
        book = match.group('book')
        if not book_ref_id:
            book_ref_ids = bible.get_book_ref_id_by_localised_name(book, language_selection)
        elif not bible.get_book_by_book_ref_id(book_ref_id):
            return []
        else:
            book_ref_ids = [book_ref_id]
        # We have not found the book so do not continue
        if not book_ref_ids:
            return []
        ranges = match.group('ranges')
        range_list = get_reference_match('range_separator').split(ranges)
        ref_list = []
        chapter = None
        for this_range in range_list:
            range_match = get_reference_match('range').match(this_range)
            from_chapter = range_match.group('from_chapter')
            from_verse = range_match.group('from_verse')
            has_range = range_match.group('range_to')
            to_chapter = range_match.group('to_chapter')
            to_verse = range_match.group('to_verse')
            if from_chapter:
                from_chapter = int(from_chapter)
            if from_verse:
                from_verse = int(from_verse)
            if to_chapter:
                to_chapter = int(to_chapter)
            if to_verse:
                to_verse = int(to_verse)
            # Fill chapter fields with reasonable values.
            if from_chapter:
                chapter = from_chapter
            elif chapter:
                from_chapter = chapter
            else:
                from_chapter = from_verse
                from_verse = None
            if to_chapter:
                if from_chapter and to_chapter < from_chapter:
                    continue
                else:
                    chapter = to_chapter
            elif to_verse:
                if chapter:
                    to_chapter = chapter
                else:
                    to_chapter = to_verse
                    to_verse = None
            # Append references to the list
            for book_ref_id in book_ref_ids:
                if has_range:
                    if not from_verse:
                        from_verse = 1
                    if not to_verse:
                        to_verse = -1
                    if to_chapter and to_chapter > from_chapter:
                        ref_list.append((book_ref_id, from_chapter, from_verse, -1))
                        for i in range(from_chapter + 1, to_chapter):
                            ref_list.append((book_ref_id, i, 1, -1))
                        ref_list.append((book_ref_id, to_chapter, 1, to_verse))
                    elif to_verse >= from_verse or to_verse == -1:
                        ref_list.append((book_ref_id, from_chapter, from_verse, to_verse))
                elif from_verse:
                    ref_list.append((book_ref_id, from_chapter, from_verse, from_verse))
                else:
                    ref_list.append((book_ref_id, from_chapter, 1, -1))
        return ref_list
    else:
        log.debug('Invalid reference: {text}'.format(text=reference))
        return []


class SearchResults(object):
    """
    Encapsulate a set of search results. This is Bible-type independent.
    """
    def __init__(self, book, chapter, verse_list):
        """
        Create the search result object.

        :param book: The book of the Bible.
        :param chapter: The chapter of the book.
        :param verse_list: The list of verses for this reading.
        """
        self.book = book
        self.chapter = chapter
        self.verse_list = verse_list

    def has_verse_list(self):
        """
        Returns whether or not the verse list contains verses.
        """
        return len(self.verse_list) > 0
