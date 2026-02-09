#!/bin/bash
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

# Loop through all python files and extract the translations
# store in in individual xml files ready to be combined

count=0
for f in $(find ../openlp/ -name '*.py'); do
  echo $f
  (( count++))
  #echo $count
  pyside6-lupdate $f -no-obsolete -ts ../resources/i18n/en.ts
  mv ../resources/i18n/en.ts ../resources/i18n/en_$count.xml
done
