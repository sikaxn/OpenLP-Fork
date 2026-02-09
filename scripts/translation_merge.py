#!/usr/bin/env python

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

'''
Combine all the xml files and remove the first 3 lines and the last 1.
'''

import sys

# Tags to be removed
matches = ['xml version', 'DOCTYPE TS', 'TS version', 'TS>']


def run(files):
    for filename in files:
        # print(filename)
        f = open(filename)
        rows = f.readlines()
        for row in rows:
            if any(m in row for m in matches):
                pass
            else:
                print(row.replace('\n', ''))


if __name__ == "__main__":
    run(sys.argv[1:])
