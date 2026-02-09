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
The :mod:`importer` modules provides the general song import functionality.
"""
import logging

from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.platform import is_win
from openlp.core.widgets.wizard import WizardStrings

from .importers.cclifile import CCLIFileImport
from .importers.chordpro import ChordProImport
from .importers.datasoul import DatasoulImport
from .importers.dreambeam import DreamBeamImport
from .importers.easyslides import EasySlidesImport
from .importers.easyworship import EasyWorshipSongImport
from .importers.foilpresenter import FoilPresenterImport
from .importers.liveworship import LiveWorshipImport
from .importers.lyrix import LyrixImport
from .importers.openlp import OpenLPSongImport
from .importers.openlyrics import OpenLyricsImport
from .importers.opensong import OpenSongImport
from .importers.powerpraise import PowerPraiseImport
from .importers.powersong import PowerSongImport
from .importers.presentationmanager import PresentationManagerImport
from .importers.propresenter import ProPresenterImport
from .importers.singingthefaith import SingingTheFaithImport
from .importers.songbeamer import SongBeamerImport
from .importers.songpro import SongProImport
from .importers.songshowplus import SongShowPlusImport
from .importers.sundayplus import SundayPlusImport
from .importers.videopsalm import VideoPsalmImport
from .importers.wordsofworship import WordsOfWorshipImport
from .importers.worshipassistant import WorshipAssistantImport
from .importers.zionworx import ZionWorxImport


log = logging.getLogger(__name__)

# Imports that might fail
try:
    from .importers.songsoffellowship import SongsOfFellowshipImport
    HAS_SOF = True
except ImportError:
    log.exception('Error importing {text}'.format(text='SongsOfFellowshipImport'))
    HAS_SOF = False
try:
    from .importers.openoffice import OpenOfficeImport
    HAS_OOO = True
except ImportError:
    log.exception('Error importing {text}'.format(text='OooImport'))
    HAS_OOO = False
HAS_MEDIASHOUT = False
if is_win():
    try:
        from .importers.mediashout import MediaShoutImport
        HAS_MEDIASHOUT = True
    except ImportError:
        log.exception('Error importing {text}'.format(text='MediaShoutImport'))
HAS_WORSHIPCENTERPRO = False
if is_win():
    try:
        from .importers.worshipcenterpro import WorshipCenterProImport
        HAS_WORSHIPCENTERPRO = True
    except ImportError:
        log.exception('Error importing {text}'.format(text='WorshipCenterProImport'))
HAS_OPSPRO = False
if is_win():
    try:
        from .importers.opspro import OPSProImport
        HAS_OPSPRO = True
    except ImportError:
        log.exception('Error importing {text}'.format(text='OPSProImport'))


class SongFormatSelect(object):
    """
    This is a special enumeration class listing available file selection modes.
    """
    SingleFile = 0
    MultipleFiles = 1
    SingleFolder = 2


class SongFormat(object):
    """
    This is a special static class that holds an enumeration of the various
    song formats handled by the importer, the attributes of each song format,
    and a few helper functions.

    Required attributes for each song format:

    ``'class'``
        Import class, e.g. ``OpenLyricsImport``

    ``'name'``
        Name of the format, e.g. ``'OpenLyrics'``

    ``'prefix'``
        Prefix for Qt objects. Use mixedCase, e.g. ``'openLyrics'``
        See ``SongImportForm.add_file_select_item()``

    Optional attributes for each song format:

    ``'canDisable'``
        Whether song format importer is disablable.
        If ``True``, then ``'disabledLabelText'`` must also be defined.

    ``'availability'``
        Whether song format importer is available.

    ``'selectMode'``
        Whether format accepts single file, multiple files, or single folder
        (as per ``SongFormatSelect`` options).

    ``'filter'``
        File extension filter for ``QFileDialog``.

    Optional/custom text Strings for ``SongImportForm`` widgets:

    ``'comboBoxText'``
        Combo box selector (default value is the format's ``'name'``).

    ``'disabledLabelText'``
        Required for disablable song formats.

    ``'getFilesTitle'``
        Title for ``QFileDialog`` (default includes the format's ``'name'``).

    ``'invalidSourceMsg'``
        Message displayed if ``is_valid_source()`` returns ``False``.

    ``'descriptionText'``
        Short description (1-2 lines) about the song format.
    """
    # Song formats (ordered alphabetically after Generic)
    # * Numerical order of song formats is significant as it determines the
    #   order used by format_combo_box.
    Unknown = -1
    OpenLyrics = 0
    OpenLP2 = 1
    Generic = 2
    CCLI = 3
    ChordPro = 4
    DreamBeam = 5
    EasySlides = 6
    EasyWorshipDB = 7
    EasyWorshipSqliteDB = 8
    EasyWorshipService = 9
    EasyWorshipServiceSqliteDB = 10
    FoilPresenter = 11
    LiveWorship = 12
    Lyrix = 13
    MediaShout = 14
    OpenSong = 15
    OPSPro = 16
    PowerPraise = 17
    PowerSong = 18
    PresentationManager = 19
    ProPresenter = 20
    SingingTheFaith = 21
    SongBeamer = 22
    SongPro = 23
    SongShowPlus = 24
    SongsOfFellowship = 25
    SundayPlus = 26
    VideoPsalm = 27
    WordsOfWorship = 28
    WorshipAssistant = 29
    WorshipCenterPro = 30
    ZionWorx = 31
    Datasoul = 32

    # Set optional attribute defaults
    __defaults__ = {
        'canDisable': False,
        'availability': True,
        'selectMode': SongFormatSelect.MultipleFiles,
        'filter': '',
        'comboBoxText': None,
        'disabledLabelText': translate('SongsPlugin.ImportWizardForm', 'This importer has been disabled.'),
        'getFilesTitle': None,
        'invalidSourceMsg': None,
        'descriptionText': None
    }

    # Set attribute values for each Song Format
    __attributes__ = {
        OpenLyrics: {
            'class': OpenLyricsImport,
            'name': 'OpenLyrics',
            'prefix': 'openLyrics',
            'filter': '{text} (*.xml)'.format(text=translate('SongsPlugin.ImportWizardForm', 'OpenLyrics Files')),
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'OpenLyrics or OpenLP 2 Exported Song')
        },
        OpenLP2: {
            'class': OpenLPSongImport,
            'name': UiStrings().OpenLPv2AndUp,
            'prefix': 'openLP2',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.sqlite)'.format(text=translate('SongsPlugin.ImportWizardForm', 'OpenLP 2 Databases'))
        },
        Generic: {
            'name': translate('SongsPlugin.ImportWizardForm', 'Generic Document/Presentation'),
            'prefix': 'generic',
            'canDisable': True,
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The generic document/presentation importer has been disabled '
                                           'because OpenLP cannot access OpenOffice or LibreOffice.'),
            'getFilesTitle': translate('SongsPlugin.ImportWizardForm', 'Select Document/Presentation Files')
        },
        CCLI: {
            'class': CCLIFileImport,
            'name': 'CCLI/SongSelect',
            'prefix': 'ccli',
            'filter': '{text} (*.usr *.txt *.bin)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                                         'CCLI SongSelect Files'))
        },
        ChordPro: {
            'class': ChordProImport,
            'name': 'ChordPro',
            'prefix': 'chordPro',
            'filter': '{text} (*.cho  *.crd *.chordpro *.chopro *.txt)'.format(
                text=translate('SongsPlugin.ImportWizardForm', 'ChordPro Files'))
        },
        DreamBeam: {
            'class': DreamBeamImport,
            'name': 'DreamBeam',
            'prefix': 'dreamBeam',
            'filter': '{text} (*.xml)'.format(text=translate('SongsPlugin.ImportWizardForm', 'DreamBeam Song Files'))
        },
        EasySlides: {
            'class': EasySlidesImport,
            'name': 'EasySlides',
            'prefix': 'easySlides',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.xml)'.format(text=translate('SongsPlugin.ImportWizardForm', 'EasySlides XML File'))
        },
        EasyWorshipDB: {
            'class': EasyWorshipSongImport,
            'name': 'EasyWorship 2007/2009 Song Database',
            'prefix': 'ew',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.DB)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                            'EasyWorship 2007/2009 Song Database'))
        },
        EasyWorshipSqliteDB: {
            'class': EasyWorshipSongImport,
            'name': 'EasyWorship 6/7 Song Database',
            'prefix': 'ew',
            'selectMode': SongFormatSelect.SingleFolder,
            'filter': '{text} (*.db)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                            'EasyWorship 6/7 Song Data Directory'))
        },
        EasyWorshipService: {
            'class': EasyWorshipSongImport,
            'name': 'EasyWorship 2007/2009 Service File',
            'prefix': 'ew',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.ews)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                             'EasyWorship 2007/2009 Service File'))
        },
        EasyWorshipServiceSqliteDB: {
            'class': EasyWorshipSongImport,
            'name': 'EasyWorship 6/7 Service File',
            'prefix': 'ew',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.ewsx)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                              'EasyWorship 6/7 Service File'))
        },
        FoilPresenter: {
            'class': FoilPresenterImport,
            'name': 'Foilpresenter',
            'prefix': 'foilPresenter',
            'filter': '{text} (*.foil)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                              'Foilpresenter Song Files'))
        },
        LiveWorship: {
            'class': LiveWorshipImport,
            'name': 'LiveWorship Database Dump',
            'prefix': 'liveWorship',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.xml)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                             'LiveWorship Database')),
            'descriptionText': translate('SongsPlugin.ImportWizardForm',
                                         'First convert your LiveWorship database to an XML text file, as '
                                         'explained in the <a href="http://manual.openlp.org/songs.html'
                                         '#importing-from-liveworship">User Manual</a>.')
        },
        Lyrix: {
            'class': LyrixImport,
            'name': 'LyriX',
            'prefix': 'lyrix',
            'filter': '{text} (*.txt)'.format(text=translate('SongsPlugin.ImportWizardForm', 'LyriX Files')),
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'LyriX (Exported TXT-files)')
        },
        MediaShout: {
            'name': 'MediaShout',
            'prefix': 'mediaShout',
            'canDisable': True,
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.mdb)'.format(text=translate('SongsPlugin.ImportWizardForm', 'MediaShout Database')),
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The MediaShout importer is only supported on Windows. It has '
                                           'been disabled due to a missing Python module. If you want to '
                                           'use this importer, you will need to install the "pyodbc" '
                                           'module.')
        },
        OpenSong: {
            'class': OpenSongImport,
            'name': WizardStrings.OS,
            'prefix': 'openSong'
        },
        OPSPro: {
            'name': 'OPS Pro',
            'prefix': 'OPSPro',
            'canDisable': True,
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.mdb)'.format(text=translate('SongsPlugin.ImportWizardForm', 'OPS Pro database')),
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The OPS Pro importer is only supported on Windows. It has been '
                                           'disabled due to a missing Python module. If you want to use this '
                                           'importer, you will need to install the "pyodbc" module.')
        },
        PowerPraise: {
            'class': PowerPraiseImport,
            'name': 'PowerPraise',
            'prefix': 'powerPraise',
            'filter': '{text} (*.ppl)'.format(text=translate('SongsPlugin.ImportWizardForm', 'PowerPraise Song Files'))
        },
        PowerSong: {
            'class': PowerSongImport,
            'name': 'PowerSong 1.0',
            'prefix': 'powerSong',
            'selectMode': SongFormatSelect.SingleFolder,
            'invalidSourceMsg': translate('SongsPlugin.ImportWizardForm', 'You need to specify a valid PowerSong 1.0 '
                                                                          'database folder.')
        },
        PresentationManager: {
            'class': PresentationManagerImport,
            'name': 'PresentationManager',
            'prefix': 'presentationManager',
            'filter': '{text} (*.sng)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                             'PresentationManager Song Files'))
        },
        ProPresenter: {
            'class': ProPresenterImport,
            'name': 'ProPresenter 4, 5 and 6',
            'prefix': 'proPresenter',
            'filter': '{text} (*.pro4 *.pro5 *.pro6)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                                            'ProPresenter Song Files'))
        },
        SingingTheFaith: {
            'class': SingingTheFaithImport,
            'name': 'SingingTheFaith',
            'prefix': 'singingTheFaith',
            'filter': '{text} (*.txt)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                             'Singing The Faith Exported Files')),
            'descriptionText': translate('SongsPlugin.ImportWizardForm',
                                         'First use Singing The Faith Electronic edition to export '
                                         'the song(s) in Text format.')
        },
        SongBeamer: {
            'class': SongBeamerImport,
            'name': 'SongBeamer',
            'prefix': 'songBeamer',
            'filter': '{text} (*.sng)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                             'SongBeamer Files'))
        },
        SongPro: {
            'class': SongProImport,
            'name': 'SongPro',
            'prefix': 'songPro',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.txt)'.format(text=translate('SongsPlugin.ImportWizardForm', 'SongPro Text Files')),
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'SongPro (Export File)'),
            'descriptionText': translate('SongsPlugin.ImportWizardForm',
                                         'In SongPro, export your songs using the File -> Export menu')
        },
        SongShowPlus: {
            'class': SongShowPlusImport,
            'name': 'SongShow Plus',
            'prefix': 'songShowPlus',
            'filter': '{text} (*.sbsong)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                                'SongShow Plus Song Files'))
        },
        SongsOfFellowship: {
            'name': 'Songs of Fellowship',
            'prefix': 'songsOfFellowship',
            'canDisable': True,
            'filter': '{text} (*.rtf)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                             'Songs Of Fellowship Song Files')),
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The Songs of Fellowship importer has been disabled because '
                                           'OpenLP cannot access OpenOffice or LibreOffice.')
        },
        SundayPlus: {
            'class': SundayPlusImport,
            'name': 'SundayPlus',
            'prefix': 'sundayPlus',
            'filter': '{text} (*.ptf)'.format(text=translate('SongsPlugin.ImportWizardForm', 'SundayPlus Song Files'))
        },
        VideoPsalm: {
            'class': VideoPsalmImport,
            'name': 'VideoPsalm',
            'prefix': 'videopsalm',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.json)'.format(text=translate('SongsPlugin.ImportWizardForm', 'VideoPsalm Files')),
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'VideoPsalm'),
            'descriptionText': translate('SongsPlugin.ImportWizardForm', 'The VideoPsalm songbooks are normally located'
                                         ' in {path}').format(path='C:\\Users\\Public\\Documents\\VideoPsalm'
                                                                   '\\SongBooks\\')
        },
        WordsOfWorship: {
            'class': WordsOfWorshipImport,
            'name': 'Words of Worship',
            'prefix': 'wordsOfWorship',
            'filter': '{text} (*.wsg *.wow-song)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                                        'Words Of Worship Song Files'))
        },
        WorshipAssistant: {
            'class': WorshipAssistantImport,
            'name': 'Worship Assistant 0',
            'prefix': 'worshipAssistant',
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.csv)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                             'Worship Assistant Files')),
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'Worship Assistant (CSV)'),
            'descriptionText': translate('SongsPlugin.ImportWizardForm',
                                         'In Worship Assistant, export your Database to a CSV file.')
        },
        WorshipCenterPro: {
            'name': 'WorshipCenter Pro',
            'prefix': 'worshipCenterPro',
            'canDisable': True,
            'selectMode': SongFormatSelect.SingleFile,
            'filter': '{text} (*.mdb)'.format(text=translate('SongsPlugin.ImportWizardForm',
                                                             'WorshipCenter Pro Song Files')),
            'disabledLabelText': translate('SongsPlugin.ImportWizardForm',
                                           'The WorshipCenter Pro importer is only supported on Windows. It has been '
                                           'disabled due to a missing Python module. If you want to use this '
                                           'importer, you will need to install the "pyodbc" module.')
        },
        ZionWorx: {
            'class': ZionWorxImport,
            'name': 'ZionWorx',
            'prefix': 'zionWorx',
            'selectMode': SongFormatSelect.SingleFile,
            'comboBoxText': translate('SongsPlugin.ImportWizardForm', 'ZionWorx (CSV)'),
            'descriptionText': translate('SongsPlugin.ImportWizardForm',
                                         'First convert your ZionWorx database to a CSV text file, as '
                                         'explained in the <a href="http://manual.openlp.org/songs.html'
                                         '#importing-from-zionworx">User Manual</a>.')
        },
        Datasoul: {
            'class': DatasoulImport,
            'name': 'Datasoul',
            'prefix': 'datasoul',
            'filter': '{text} (*.song)'.format(text=translate('SongsPlugin.ImportWizardForm', 'Datasoul Song Files'))
        }
    }

    @staticmethod
    def get_format_list():
        """
        Return a list of the supported song formats.
        """
        return sorted([
            SongFormat.OpenLyrics,
            SongFormat.OpenLP2,
            SongFormat.Generic,
            SongFormat.CCLI,
            SongFormat.ChordPro,
            SongFormat.Datasoul,
            SongFormat.DreamBeam,
            SongFormat.EasySlides,
            SongFormat.EasyWorshipDB,
            SongFormat.EasyWorshipSqliteDB,
            SongFormat.EasyWorshipService,
            SongFormat.EasyWorshipServiceSqliteDB,
            SongFormat.FoilPresenter,
            SongFormat.LiveWorship,
            SongFormat.Lyrix,
            SongFormat.MediaShout,
            SongFormat.OpenSong,
            SongFormat.OPSPro,
            SongFormat.PowerPraise,
            SongFormat.PowerSong,
            SongFormat.PresentationManager,
            SongFormat.ProPresenter,
            SongFormat.SingingTheFaith,
            SongFormat.SongBeamer,
            SongFormat.SongPro,
            SongFormat.SongShowPlus,
            SongFormat.SongsOfFellowship,
            SongFormat.SundayPlus,
            SongFormat.VideoPsalm,
            SongFormat.WordsOfWorship,
            SongFormat.WorshipAssistant,
            SongFormat.WorshipCenterPro,
            SongFormat.ZionWorx
        ])

    @staticmethod
    def get(song_format, *attributes):
        """
        Return requested song format attribute(s).

        :param song_format: A song format from SongFormat.
        :param attributes: Zero or more song format attributes from SongFormat.

        Return type depends on number of supplied attributes:

        :0: Return dict containing all defined attributes for the format.
        :1: Return the attribute value.
        :>1: Return tuple of requested attribute values.
        """
        if not attributes:
            return SongFormat.__attributes__.get(song_format)
        elif len(attributes) == 1:
            default = SongFormat.__defaults__.get(attributes[0])
            return SongFormat.__attributes__[song_format].get(attributes[0], default)
        else:
            values = []
            for attr in attributes:
                default = SongFormat.__defaults__.get(attr)
                values.append(SongFormat.__attributes__[song_format].get(attr, default))
            return tuple(values)

    @staticmethod
    def set(song_format, attribute, value):
        """
        Set specified song format attribute to the supplied value.
        """
        SongFormat.__attributes__[song_format][attribute] = value


SongFormat.set(SongFormat.SongsOfFellowship, 'availability', HAS_SOF)
if HAS_SOF:
    SongFormat.set(SongFormat.SongsOfFellowship, 'class', SongsOfFellowshipImport)
SongFormat.set(SongFormat.Generic, 'availability', HAS_OOO)
if HAS_OOO:
    SongFormat.set(SongFormat.Generic, 'class', OpenOfficeImport)
SongFormat.set(SongFormat.MediaShout, 'availability', HAS_MEDIASHOUT)
if HAS_MEDIASHOUT:
    SongFormat.set(SongFormat.MediaShout, 'class', MediaShoutImport)
SongFormat.set(SongFormat.WorshipCenterPro, 'availability', HAS_WORSHIPCENTERPRO)
if HAS_WORSHIPCENTERPRO:
    SongFormat.set(SongFormat.WorshipCenterPro, 'class', WorshipCenterProImport)
SongFormat.set(SongFormat.OPSPro, 'availability', HAS_OPSPRO)
if HAS_OPSPRO:
    SongFormat.set(SongFormat.OPSPro, 'class', OPSProImport)


__all__ = ['SongFormat', 'SongFormatSelect']
