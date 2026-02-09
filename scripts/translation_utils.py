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
This script is used to maintain the translation files in OpenLP.
It generates the base en.ts file used to drive all translations
on Transifex.
For more details on the translation process see the Translation pages on the
Wiki
"""

import os


IGNORED_PATHS = ['scripts', 'tests']
IGNORED_FILES = ['setup.py']


def prepare_project():
    """
    This method creates the project file needed to update the translation files and compile them into .qm files.
    """
    print('Generating the openlp.pro file')
    lines = []
    start_dir = os.path.abspath('..')
    start_dir = start_dir + os.sep
    print('Starting directory: %s' % start_dir)
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            path = root.replace(start_dir, '').replace('\\', '/')
            if file.startswith('hook-') or file.startswith('test_'):
                continue
            ignore = False
            for ignored_path in IGNORED_PATHS:
                if path.startswith(ignored_path):
                    ignore = True
                    break
            if ignore:
                continue
            ignore = False
            for ignored_file in IGNORED_FILES:
                if file == ignored_file:
                    ignore = True
                    break
            if ignore:
                continue
            if file.endswith('.py') or file.endswith('.pyw'):
                if path:
                    line = '%s/%s' % (path, file)
                else:
                    line = file
                print('Parsing "%s"' % line)
                lines.append('SOURCES      += %s' % line)
    lines.append('TRANSLATIONS += resources/i18n/en.ts')
    lines.sort()
    file = open(os.path.join(start_dir, 'openlp.pro'), 'w')
    file.write('\n'.join(lines))
    file.close()


if __name__ == '__main__':
    prepare_project()
