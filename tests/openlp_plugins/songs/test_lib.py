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
This module contains tests for the lib submodule of the Songs plugin.
"""
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.plugins.songs.lib import VerseType, clean_string, clean_title, delete_song, strip_rtf, \
    transpose_chord, transpose_lyrics
from openlp.plugins.songs.lib.songcompare import _op_length, _remove_typos, songs_probably_equal

full_lyrics = '''amazing grace how sweet the sound that saved a wretch like me i once was lost but now am
    found was blind but now i see  twas grace that taught my heart to fear and grace my fears relieved how
    precious did that grace appear the hour i first believed  through many dangers toils and snares i have
    already come tis grace that brought me safe thus far and grace will lead me home'''
short_lyrics = '''twas grace that taught my heart to fear and grace my fears relieved how precious did
that grace appear the hour i first believed'''
error_lyrics = '''amazing how sweet the trumpet that saved a wrench like me i once was losst but now am
    found waf blind but now i see  it was grace that taught my heart to fear and grace my fears relieved how
    precious did that grace appppppppear the hour i first believedxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx snares i have
    already come to this grace that brought me safe so far and grace will lead me home'''
different_lyrics = '''on a hill far away stood an old rugged cross the emblem of suffering and shame and
    i love that old cross where the dearest and best for a world of lost sinners was slain  so ill cherish the
    old rugged cross till my trophies at last i lay down i will cling to the old rugged cross and exchange it
    some day for a crown'''


def test_clean_string():
    """
    Test the clean_string() function
    """
    # GIVEN: A "dirty" string
    dirty_string = 'Ain\'t gonna   find\t you there.'

    # WHEN: We run the string through the function
    result = clean_string(dirty_string)

    # THEN: The string should be cleaned up and lower-cased
    assert result == 'aint gonna find you there ', 'The string should be cleaned up properly'


def test_clean_title():
    """
    Test the clean_title() function
    """
    # GIVEN: A "dirty" string
    dirty_string = 'This\u0000 is a\u0014 dirty \u007Fstring\u009F'

    # WHEN: We run the string through the function
    result = clean_title(dirty_string)

    # THEN: The string should be cleaned up
    assert result == 'This is a dirty string', 'The title should be cleaned up properly: "%s"' % result


def test_songs_probably_equal_same_song():
    """
    Test the songs_probably_equal function with twice the same song.
    """
    # GIVEN: Two equal songs.
    song_tuple1 = (2, full_lyrics)
    song_tuple2 = (4, full_lyrics)

    # WHEN: We compare those songs for equality.
    result = songs_probably_equal((song_tuple1, song_tuple2))

    # THEN: The result should be a tuple..
    assert result == (2, 4), 'The result should be the tuble of song positions'


def test_songs_probably_equal_short_song():
    """
    Test the songs_probably_equal function with a song and a shorter version of the same song.
    """
    # GIVEN: A song and a short version of the same song.
    song_tuple1 = (1, full_lyrics)
    song_tuple2 = (3, short_lyrics)

    # WHEN: We compare those songs for equality.
    result = songs_probably_equal((song_tuple1, song_tuple2))

    # THEN: The result should be a tuple..
    assert result == (1, 3), 'The result should be the tuble of song positions'


def test_songs_probably_equal_error_song():
    """
    Test the songs_probably_equal function with a song and a  very erroneous version of the same song.
    """
    # GIVEN: A song and the same song with lots of errors.
    song_tuple1 = (4, full_lyrics)
    song_tuple2 = (7, error_lyrics)

    # WHEN: We compare those songs for equality.
    result = songs_probably_equal((song_tuple1, song_tuple2))

    # THEN: The result should be a tuple of song positions.
    assert result == (4, 7), 'The result should be the tuble of song positions'


def test_songs_probably_equal_different_song():
    """
    Test the songs_probably_equal function with two different songs.
    """
    # GIVEN: Two different songs.
    song_tuple1 = (5, full_lyrics)
    song_tuple2 = (8, different_lyrics)

    # WHEN: We compare those songs for equality.
    result = songs_probably_equal((song_tuple1, song_tuple2))

    # THEN: The result should be None.
    assert result is None, 'The result should be None'


def test_remove_typos_beginning():
    """
    Test the _remove_typos function with a typo at the beginning.
    """
    # GIVEN: A diffset with a difference at the beginning.
    diff = [('replace', 0, 2, 0, 1), ('equal', 2, 11, 1, 10)]

    # WHEN: We remove the typos in there.
    result = _remove_typos(diff)

    # THEN: There should be no typos at the beginning anymore.
    assert len(result) == 1, 'The result should contain only one element.'
    assert result[0][0] == 'equal', 'The result should contain an equal element.'


def test_remove_typos_beginning_negated():
    """
    Test the _remove_typos function with a large difference at the beginning.
    """
    # GIVEN: A diffset with a large difference at the beginning.
    diff = [('replace', 0, 20, 0, 1), ('equal', 20, 29, 1, 10)]

    # WHEN: We remove the typos in there.
    result = _remove_typos(list(diff))

    # THEN: There diff should not have changed.
    assert result == diff


def test_remove_typos_end():
    """
    Test the _remove_typos function with a typo at the end.
    """
    # GIVEN: A diffset with a difference at the end.
    diff = [('equal', 0, 10, 0, 10), ('replace', 10, 12, 10, 11)]

    # WHEN: We remove the typos in there.
    result = _remove_typos(diff)

    # THEN: There should be no typos at the end anymore.
    assert len(result) == 1, 'The result should contain only one element.'
    assert result[0][0] == 'equal', 'The result should contain an equal element.'


def test_remove_typos_end_negated():
    """
    Test the _remove_typos function with a large difference at the end.
    """
    # GIVEN: A diffset with a large difference at the end.
    diff = [('equal', 0, 10, 0, 10), ('replace', 10, 20, 10, 1)]

    # WHEN: We remove the typos in there.
    result = _remove_typos(list(diff))

    # THEN: There diff should not have changed.
    assert result == diff


def test_remove_typos_middle():
    """
    Test the _remove_typos function with a typo in the middle.
    """
    # GIVEN: A diffset with a difference in the middle.
    diff = [('equal', 0, 10, 0, 10), ('replace', 10, 12, 10, 11), ('equal', 12, 22, 11, 21)]

    # WHEN: We remove the typos in there.
    result = _remove_typos(diff)

    # THEN: There should be no typos in the middle anymore. The remaining equals should have been merged.
    assert len(result) == 1, 'The result should contain only one element.'
    assert result[0][0] == 'equal', 'The result should contain an equal element.'
    assert result[0][1] == 0, 'The start indices should be kept.'
    assert result[0][2] == 22, 'The stop indices should be kept.'
    assert result[0][3] == 0, 'The start indices should be kept.'
    assert result[0][4] == 21, 'The stop indices should be kept.'


def test_remove_typos_middle_negated():
    """
    Test the _remove_typos function with a large difference in the middle.
    """
    # GIVEN: A diffset with a large difference in the middle.
    diff = [('equal', 0, 10, 0, 10), ('replace', 10, 20, 10, 11), ('equal', 20, 30, 11, 21)]

    # WHEN: We remove the typos in there.
    result = _remove_typos(list(diff))

    # THEN: There diff should not have changed.
    assert result == diff


def test_op_length():
    """
    Test the _op_length function.
    """
    # GIVEN: A diff entry.
    diff_entry = ('replace', 0, 2, 4, 14)

    # WHEN: We calculate the length of that diff.
    result = _op_length(diff_entry)

    # THEN: The maximum length should be returned.
    assert result == 10, 'The length should be 10.'


def test_strip_rtf_charsets():
    """
    Test that the strip_rtf() method properly decodes the supported charsets.
    """
    test_charset_table = [
        ('0', 'weor\\\'F0-myndum \\\'FEah\\par ', 'weorð-myndum þah\n'),
        ('128', '\\\'83C\\\'83G\\\'83X\\\'A5\\\'83L\\\'83\\\'8A\\\'83X\\\'83g\\\'A1 '
                '\\\\ \\\'95\\\\ \\\'8E\\} \\\'8E\\{ \\\'A1\\par ', 'イエス･キリスト｡ ¥ 表 枝 施 ｡\n'),
        ('129', '\\\'BF\\\'B9\\\'BC\\\'F6 \\\'B1\\\'D7\\\'B8\\\'AE\\\'BD\\\'BA\\\'B5\\\'B5\\par ', '예수 그리스도\n'),
        ('134', '\\\'D2\\\'AE\\\'F6\\\'D5\\\'BB\\\'F9\\\'B6\\\'BD\\\'CA\\\'C7\\\'D6\\\'F7\\par ', '耶稣基督是主\n'),
        ('161', '\\\'D7\\\'F1\\\'E9\\\'F3\\\'F4\\\'FC\\\'F2\\par ', 'Χριστός\n'),
        ('162', 'Hazreti \\\'DDsa\\par ', 'Hazreti İsa\n'),
        ('163', 'ph\\\'FD\\\'F5ng\\par ', 'phương\n'),
        ('177', '\\\'E1\\\'F8\\\'E0\\\'F9\\\'E9\\\'FA\\par ', 'בראשית\n'),
        ('178', '\\\'ED\\\'D3\\\'E6\\\'DA \\\'C7\\\'E1\\\'E3\\\'D3\\\'ED\\\'CD\\par ', 'يسوع المسيح\n'),
        ('186', 'J\\\'EBzus Kristus yra Vie\\\'F0pats\\par ', 'Jėzus Kristus yra Viešpats\n'),
        ('204', '\\\'D0\\\'EE\\\'F1\\\'F1\\\'E8\\\'FF\\par ', 'Россия\n'),
        ('222', '\\\'A4\\\'C3\\\'D4\\\'CA\\\'B5\\\'EC\\par ', 'คริสต์\n'),
        ('238', 'Z\\\'E1v\\\'ECre\\\'E8n\\\'E1 zkou\\\'9Aka\\par ', 'Závěrečná zkouška\n')
    ]

    # GIVEN: For each character set and input
    for charset, input, exp_result in test_charset_table:

        # WHEN: We call strip_rtf on the input RTF
        result, result_enc = strip_rtf(
            '{\\rtf1 \\ansi \\ansicpg1252 {\\fonttbl \\f0 \\fswiss \\fcharset%s Helvetica;}'
            '{\\colortbl ;\\red0 \\green0 \\blue0 ;}\\pard \\f0 %s}' % (charset, input))

        # THEN: The stripped text matches thed expected result
        assert result == exp_result, 'The result should be %s' % exp_result


def test_transpose_chord_up():
    """
    Test that the transpose_chord() method works when transposing up
    """
    # GIVEN: A Chord
    chord = 'C'
    key = None
    last_chord = None
    is_bass = False

    # WHEN: Transposing it 1 up
    new_chord, key, last_chord = transpose_chord(chord, 1, 'english', key, last_chord, is_bass)

    # THEN: The chord should be transposed up one note
    assert new_chord == 'C#', 'The chord should be transposed up.'
    assert key is None, 'The key should not be set'
    assert last_chord == 'C#', 'If not is_bass, then last_chord should be returned'


def test_transpose_chord_up_adv():
    """
    Test that the transpose_chord() method works when transposing up an advanced chord
    """
    # GIVEN: An advanced Chord
    chord = '(D/F#)'
    key = None
    last_chord = None
    is_bass = False
    chord_split = chord.split("/")
    # WHEN: Transposing it 1 up
    new_chord, key, last_chord = transpose_chord(chord_split[0], 1, 'english', key, last_chord, is_bass)

    # AFTER "/" isbass is true, lastchord is set
    is_bass = True
    new_bass, key, last_chord = transpose_chord(chord_split[1], 1, 'english', key, last_chord, is_bass)

    # THEN: The chord should be transposed up one note
    assert new_chord == '(Eb', 'The chord should be transposed up.'
    assert new_bass == 'G)', 'Bass should be transposed up.'
    assert key is None, 'no key should be defined'
    assert last_chord == 'Eb', 'last_chord is generated'


def test_transpose_chord_down():
    """
    Test that the transpose_chord() method works when transposing down
    """
    # GIVEN: A Chord
    chord = 'C'
    key = None
    last_chord = None
    is_bass = False

    # WHEN: Transposing it 1 down
    new_chord, key, last_chord = transpose_chord(chord, -1, 'english', key, last_chord, is_bass)

    # THEN: The chord should be transposed down one note
    assert new_chord == 'B', 'The chord should be transposed down.'
    assert key is None, 'The key should not be set'
    assert last_chord == 'B', 'If not is_bass, then last_chord should be returned'


def test_transpose_chord_error():
    """
    Test that the transpose_chord() raises exception on invalid chord
    """
    # GIVEN: A invalid Chord
    chord = 'T'

    # WHEN: Transposing it 1 down
    # THEN: An exception should be raised
    with pytest.raises(KeyError) as err:
        transpose_chord(chord, -1, 'english', None, None, False)
    assert err.value != KeyError('\'T\' is not in list'), \
        'KeyError exception should have been thrown for invalid chord'


@patch('openlp.plugins.songs.lib.transpose_verse')
def test_transpose_lyrics(mocked_transpose_verse: MagicMock, mock_settings: MagicMock):
    """
    Test that the transpose_lyrics() splits verses correctly
    """
    # GIVEN: Lyrics with verse splitters and a mocked settings
    lyrics = '---[Verse:1]---\n'\
             'Amazing grace how sweet the sound\n'\
             '[---]\n'\
             'That saved a wretch like me.\n'\
             '---[Verse:2]---\n'\
             'I once was lost but now I\'m found.'
    mock_settings.value.return_value = 'english'
    mocked_transpose_verse.return_value = ['', None]
    # WHEN: Transposing the lyrics
    transpose_lyrics(lyrics, 1)

    # THEN: transpose_verse should have been called
    mocked_transpose_verse.assert_any_call('', 1, 'english', None)
    mocked_transpose_verse.assert_any_call('\nAmazing grace how sweet the sound\n', 1, 'english', None)
    mocked_transpose_verse.assert_any_call('\nThat saved a wretch like me.\n', 1, 'english', None)
    mocked_transpose_verse.assert_any_call('\nI once was lost but now I\'m found.', 1, 'english', None)


def test_translated_tag():
    """
    Test that the translated_tag() method returns the correct tags
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the translated_tag() method with a "verse"
        result = VerseType.translated_tag('v')

        # THEN: The result should be "V"
        assert result == 'V', 'The result should be "V"'

        # WHEN: We run the translated_tag() method with a "chorus"
        result = VerseType.translated_tag('c')

        # THEN: The result should be "C"
        assert result == 'C', 'The result should be "C"'


def test_translated_invalid_tag():
    """
    Test that the translated_tag() method returns the default tag when passed an invalid tag
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the translated_tag() method with an invalid verse type
        result = VerseType.translated_tag('z')

        # THEN: The result should be "O"
        assert result == 'O', 'The result should be "O", but was "%s"' % result


def test_translated_invalid_tag_with_specified_default():
    """
    Test that the translated_tag() method returns the specified default tag when passed an invalid tag
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the translated_tag() method with an invalid verse type and specify a default
        result = VerseType.translated_tag('q', VerseType.Bridge)

        # THEN: The result should be "B"
        assert result == 'B', 'The result should be "B", but was "%s"' % result


def test_translated_invalid_tag_with_invalid_default():
    """
    Test that the translated_tag() method returns a sane default tag when passed an invalid default
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the translated_tag() method with an invalid verse type and an invalid default
        result = VerseType.translated_tag('q', 29)

        # THEN: The result should be "O"
        assert result == 'O', 'The result should be "O", but was "%s"' % result


def test_translated_name():
    """
    Test that the translated_name() method returns the correct name
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the translated_name() method with a "verse"
        result = VerseType.translated_name('v')

        # THEN: The result should be "Verse"
        assert result == 'Verse', 'The result should be "Verse"'

        # WHEN: We run the translated_name() method with a "chorus"
        result = VerseType.translated_name('c')

        # THEN: The result should be "Chorus"
        assert result == 'Chorus', 'The result should be "Chorus"'


def test_translated_invalid_name():
    """
    Test that the translated_name() method returns the default name when passed an invalid tag
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the translated_name() method with an invalid verse type
        result = VerseType.translated_name('z')

        # THEN: The result should be "Other"
        assert result == 'Other', 'The result should be "Other", but was "%s"' % result


def test_translated_invalid_name_with_specified_default():
    """
    Test that the translated_name() method returns the specified default name when passed an invalid tag
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the translated_name() method with an invalid verse type and specify a default
        result = VerseType.translated_name('q', VerseType.Bridge)

        # THEN: The result should be "Bridge"
        assert result == 'Bridge', 'The result should be "Bridge", but was "%s"' % result


def test_translated_invalid_name_with_invalid_default():
    """
    Test that the translated_name() method returns the specified default tag when passed an invalid tag
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the translated_name() method with an invalid verse type and specify an invalid default
        result = VerseType.translated_name('q', 29)

        # THEN: The result should be "Other"
        assert result == 'Other', 'The result should be "Other", but was "%s"' % result


def test_from_tag():
    """
    Test that the from_tag() method returns the correct VerseType.
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the from_tag() method with a valid verse type, we get the name back
        result = VerseType.from_tag('v')

        # THEN: The result should be VerseType.Verse
        assert result == VerseType.Verse, 'The result should be VerseType.Verse, but was "%s"' % result


def test_from_tag_with_invalid_tag():
    """
    Test that the from_tag() method returns the default VerseType when it is passed an invalid tag.
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the from_tag() method with a valid verse type, we get the name back
        result = VerseType.from_tag('w')

        # THEN: The result should be VerseType.Other
        assert result == VerseType.Other, 'The result should be VerseType.Other, but was "%s"' % result


def test_from_tag_with_specified_default():
    """
    Test that the from_tag() method returns the specified default when passed an invalid tag.
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the from_tag() method with an invalid verse type, we get the specified default back
        result = VerseType.from_tag('x', VerseType.Chorus)

        # THEN: The result should be VerseType.Chorus
        assert result == VerseType.Chorus, 'The result should be VerseType.Chorus, but was "%s"' % result


def test_from_tag_with_invalid_intdefault():
    """
    Test that the from_tag() method returns a sane default when passed an invalid tag and an invalid int default.
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the from_tag() method with an invalid verse type, we get the specified default back
        result = VerseType.from_tag('m', 29)

        # THEN: The result should be VerseType.Other
        assert result == VerseType.Other, 'The result should be VerseType.Other, but was "%s"' % result


def test_from_tag_with_invalid_default():
    """
    Test that the from_tag() method returns a sane default when passed an invalid tag and an invalid default.
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the from_tag() method with an invalid verse type, we get the specified default back
        result = VerseType.from_tag('@', 'asdf')

        # THEN: The result should be VerseType.Other
        assert result == VerseType.Other, 'The result should be VerseType.Other, but was "%s"' % result


def test_from_tag_with_none_default():
    """
    Test that the from_tag() method returns a sane default when passed an invalid tag and None as default.
    """
    # GIVEN: A mocked out translate() function that just returns what it was given
    with patch('openlp.plugins.songs.lib.translate') as mocked_translate:
        mocked_translate.side_effect = lambda x, y: y

        # WHEN: We run the from_tag() method with an invalid verse type, we get the specified default back
        result = VerseType.from_tag('m', None)

        # THEN: The result should be None
        assert result is None, 'The result should be None, but was "%s"' % result


@patch('openlp.plugins.songs.lib.VerseType.translated_tags', new_callable=PropertyMock, return_value=['x'])
def test_from_loose_input_with_invalid_input(mocked_translated_tags: MagicMock):
    """
    Test that the from_loose_input() method returns a sane default when passed an invalid tag and None as default.
    """
    # GIVEN: A mocked VerseType.translated_tags
    # WHEN: We run the from_loose_input() method with an invalid verse type, we get the specified default back
    result = VerseType.from_loose_input('m', None)

    # THEN: The result should be None
    assert result is None, 'The result should be None, but was "%s"' % result


@patch('openlp.plugins.songs.lib.VerseType.translated_tags', new_callable=PropertyMock, return_value=['x'])
def test_from_loose_input_with_valid_input(mocked_translated_tags: MagicMock):
    """
    Test that the from_loose_input() method returns valid output on valid input.
    """
    # GIVEN: A mocked VerseType.translated_tags
    # WHEN: We run the from_loose_input() method with a valid verse type, we get the expected VerseType back
    result = VerseType.from_loose_input('v')

    # THEN: The result should be a Verse
    assert result == VerseType.Verse, 'The result should be a verse, but was "%s"' % result


@patch('openlp.plugins.songs.lib.AppLocation.get_section_data_path')
@patch('openlp.plugins.songs.lib.MediaFile')
@patch('openlp.plugins.songs.lib.Song')
@patch('openlp.plugins.songs.lib.os.unlink')
def test_delete_song(mocked_unlink: MagicMock, MockSong: MagicMock, MockMediaFile: MagicMock,
                     mocked_get_section_data_path: MagicMock, registry: Registry):
    """Test deleting a song and all its media files"""
    # GIVEN: A song ID and some mocked objects
    song_id = 1234
    MockMediaFile.song_id = song_id
    mocked_songs_manager = MagicMock()
    mocked_media_file_str = MagicMock(file_path='/path/to/file.mp3')
    mocked_media_file_path = MagicMock()
    mocked_songs_manager.get_all_objects.return_value = [mocked_media_file_str, mocked_media_file_path]
    registry.register('songs_manager', mocked_songs_manager)
    mocked_save_path = MagicMock()
    mocked_save_path.exists.return_value = True
    mocked_get_section_data_path.return_value.__truediv__.return_value.__truediv__.return_value = mocked_save_path
    mocked_song_deleted = MagicMock()
    registry.register_function('song_deleted', mocked_song_deleted)

    # WHEN: delete_song() is called
    delete_song(song_id, True)

    # THEN: All the files should be deleted
    mocked_songs_manager.get_all_objects.assert_called_once_with(MockMediaFile, MockMediaFile.song_id == song_id)
    mocked_unlink.assert_called_once_with(mocked_media_file_str.file_path)
    mocked_media_file_path.file_path.unlink.assert_called_once_with()
    mocked_save_path.rmdir.assert_called_once_with()
    mocked_songs_manager.delete_object.assert_called_once_with(MockSong, song_id)
    mocked_song_deleted.assert_called_once_with(song_id)
