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

import fnmatch
import os

from lxml import etree


resource_path = os.path.join('..', 'resources', 'images')
resource_file_path = os.path.join(resource_path, 'openlp-2.qrc')
src_directory = os.path.join('..', 'openlp')

RESOURCES_TO_IGNORE = [
    'openlp.svg',
    'OpenLP.ico',
    'openlp-2.qrc',
    'openlp-logo-16x16.png',
    'openlp-logo-32x32.png',
    'openlp-logo-48x48.png',
    'openlp-logo-64x64.png',
    'openlp-logo-128x128.png',
    'README.txt'
]

tree = etree.parse(resource_file_path)
root = tree.getroot()

print('Looking for unused resources listed in openlp-2.qrc')
print('----------------------------------------------------------------')
resources = root.findall('.//file')
for current_dir, dirs, files in os.walk(src_directory):
    for file_name in files:
        if not fnmatch.fnmatch(file_name, '*.py'):
            continue
        file_path = os.path.join(current_dir, file_name)
        with open(file_path) as source_file:
            file_contents = source_file.read()
            # Create a copy of the resources list so that we don't change the list while we're iterating through it!
            for resource in list(resources):
                if resource.text in file_contents:
                    resources.remove(resource)
if resources:
    print('Unused resources listed in openlp-2.qrc:')
    print(*(x.text for x in resources), sep='\n')
    print('----------------------------------------------------------------')
    remove = None
    while remove != 'yes' and remove != 'no':
        remove = input('Would you like to remove these files from openlp-2.qrc? (yes/no)')
    if remove == 'yes':
        for resource in resources:
            parent = resource.find('..')
            parent.remove(resource)
    tree.write(resource_file_path, encoding='utf8')
else:
    print('No unused resources listed in openlp-2.qrc')
print('----------------------------------------------------------------')

print('\nLooking for resource files which are not lited in openlp-2.qrc')
print('----------------------------------------------------------------')
resources = [x.text for x in root.findall('.//file')]
removable_resources = []
for resource_name in os.listdir(resource_path):
    if resource_name not in RESOURCES_TO_IGNORE and resource_name not in resources:
        removable_resources.append(resource_name)
if removable_resources:
    print('Resource files not listed in openlp-2.qrc:')
    print(*removable_resources, sep='\n')
    print('----------------------------------------------------------------')
    remove = None
    while remove != 'yes' and remove != 'no':
        remove = input('Would you like to delete these files from the resource folder? (yes/no)')
        print('----------------------------------------------------------------')
    if remove == 'yes':
        for resource in removable_resources:
            resource_file = os.path.join(resource_path, resource)
            print('Removing {file}'.format(file=resource_file))
            os.remove(resource_file)
else:
    print('All resource files are listed!')
