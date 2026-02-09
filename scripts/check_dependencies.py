#!/usr/bin/env python3
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
This script is used to check dependencies of OpenLP. It checks availability
of required python modules and their version. To verify availability of Python
modules, simply run this script::

    $ ./check_dependencies.py

"""
import importlib
import os
import sys
from packaging.version import parse

IS_WIN = sys.platform.startswith('win')
IS_LIN = sys.platform.startswith('lin')
IS_MAC = sys.platform.startswith('dar')


VERS = {
    'Python': '3.12',
    'PySide6': '6.7',
    'Qt6': '6.7',
    'sqlalchemy': '0.5',
    'enchant': '1.6'
}

# pywin32
WIN32_MODULES = [
    'win32com',
    'win32ui',
    'pywintypes',
    'icu',
]

LINUX_MODULES = [
    # Optical drive detection.
    'dbus',
    'distro',
]

MACOSX_MODULES = [
    'objc',
    'Pyro5',
    'AppKit'
]


MODULES = [
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtOpenGL',
    'PySide6.QtSvg',
    'PySide6.QtTest',
    ('PySide6.QtWebEngineCore', '(PySideWebEngine on PyPI)'),
    'PySide6.QtMultimedia',
    'platformdirs',
    'sqlalchemy',
    'alembic',
    'lxml',
    'chardet',
    'flask',
    'flask_cors',
    'bs4',
    'mako',
    'websockets',
    'waitress',
    'requests',
    'qtawesome',
    'qrcode',
    'packaging',
]


OPTIONAL_MODULES = [
    ('qdarkstyle', '(dark style support)'),
    ('pymysql', '(MySQL support)'),
    ('pyodbc', '(ODBC support)'),
    ('psycopg2', '(PostgreSQL support)'),
    ('enchant', '(spell checker)'),
    ('pysword', '(import SWORD bibles)'),
    ('uno', '(LibreOffice/OpenOffice support)'),
    # development/testing modules
    ('pytest', '(testing framework)'),
    ('pytestqt', '(PySide testing framework - pytest-qt on PyPI)'),
    ('flake8', '(linter)')
]

w = sys.stdout.write


def check_vers(version, required, text):
    """
    Check the version of a dependency. Returns ``True`` if the version is greater than or equal, or False if less than.

    ``version``
        The actual version of the dependency

    ``required``
        The required version of the dependency

    ``text``
        The dependency's name
    """
    space = (27 - len(required) - len(text)) * ' '
    if not isinstance(version, str):
        version = '.'.join(map(str, version))
    if not isinstance(required, str):
        required = '.'.join(map(str, required))
    w('  %s >= %s ...  ' % (text, required) + space)
    if parse(version) >= parse(required):
        w(version + os.linesep)
        return True
    else:
        w('FAIL' + os.linesep)
        return False


def check_module(mod, text='', indent='  '):
    """
    Check that a module is installed.

    ``mod``
        The module to check for.

    ``text``
        The text to display.

    ``indent``
        How much to indent the text by.
    """
    space = (31 - len(mod) - len(text)) * ' '
    w(indent + '%s %s...  ' % (mod, text) + space)
    try:
        importlib.import_module(mod)
        w('OK')
    except ImportError:
        w('FAIL')
    except Exception:
        w('ERROR')
    w(os.linesep)


def print_vers_fail(required, text):
    print('  %s >= %s ...    FAIL' % (text, required))


def verify_python():
    if not check_vers(list(sys.version_info)[0:3], VERS['Python'], text='Python'):
        exit(1)


def verify_versions():
    print('Verifying version of modules...')
    try:
        import PySide6
        check_vers(PySide6.__version__, VERS['PySide6'], 'PySide6')
        check_vers(PySide6.QtCore.qVersion(), VERS['Qt6'], 'Qt6')
    except ImportError:
        print_vers_fail(VERS['PySide6'], 'PySide6')
        print_vers_fail(VERS['Qt6'], 'Qt6')
    try:
        import sqlalchemy
        check_vers(sqlalchemy.__version__, VERS['sqlalchemy'], 'sqlalchemy')
    except ImportError:
        print_vers_fail(VERS['sqlalchemy'], 'sqlalchemy')
    try:
        import enchant
        check_vers(enchant.__version__, VERS['enchant'], 'enchant')
    except ImportError:
        print_vers_fail(VERS['enchant'], 'enchant')


def print_enchant_backends_and_languages():
    """
    Check if PyEnchant is installed.
    """
    w('Enchant (spell checker)... ')
    try:
        import enchant
        w(os.linesep)
        backends = ', '.join([x.name for x in enchant.Broker().describe()])
        print('  available backends: %s' % backends)
        langs = ', '.join(enchant.list_languages())
        print('  available languages: %s' % langs)
    except ImportError:
        w('FAIL' + os.linesep)


def print_qt_image_formats():
    """
    Print out the image formats that Qt6 supports.
    """
    w('Qt6 image formats... ')
    try:
        from PySide6 import QtGui
        read_f = ', '.join([bytes(fmt).decode().lower() for fmt in QtGui.QImageReader.supportedImageFormats()])
        write_f = ', '.join([bytes(fmt).decode().lower() for fmt in QtGui.QImageWriter.supportedImageFormats()])
        w(os.linesep)
        print('  read: %s' % read_f)
        print('  write: %s' % write_f)
    except ImportError:
        w('FAIL' + os.linesep)


def main():
    """
    Run the dependency checker.
    """
    print('Checking Python version...')
    verify_python()
    print('Checking for modules...')
    for m in MODULES:
        if isinstance(m, (tuple, list)):
            check_module(m[0], text=m[1])
        else:
            check_module(m)
    print('Checking for optional modules...')
    for m in OPTIONAL_MODULES:
        check_module(m[0], text=m[1])
    if IS_WIN:
        print('Checking for Windows specific modules...')
        for m in WIN32_MODULES:
            check_module(m)
    elif IS_LIN:
        print('Checking for Linux specific modules...')
        for m in LINUX_MODULES:
            check_module(m)
    elif IS_MAC:
        print('Checking for Mac OS X specific modules...')
        for m in MACOSX_MODULES:
            check_module(m)
    verify_versions()
    print_qt_image_formats()
    print_enchant_backends_and_languages()


if __name__ == '__main__':
    main()
