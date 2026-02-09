#!/bin/sh
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2024 OpenLP Developers                              #
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
#
# This script automates the generation of resources.py for OpenLP saving a
# backup of the old resources, inserting the coding and copyright header and
# conforming it to the project coding standards.
#
# To make use of the script:
# 1 - Add the new image files in resources/images/
# 2 - Modify resources/images/openlp-2.qrc as appropriate
# 3 - run sh scripts/generate_resources.sh
#
# Once you have confirmed the resources are correctly modified to an updated,
# working state you may optionally remove openlp/core/resources.py.old
#
###############################################################################

# Dependencies
#
# Depending on your platform, you will need to install the following for the "rcc" command:
#
# Debian: qt6-base-dev-tools
# Fedora: pyside6-tools

# Find the "rcc" binary
COMMANDS="pyside6-rcc rcc /usr/lib/qt6/libexec/rcc /usr/lib/qt6/rcc"
RCC_CMD=""
for RCC_CMD in $COMMANDS; do
    echo $RCC_CMD
    if command -v $RCC_CMD 2>&1 >/dev/null; then
        if [ "$RCC_CMD" = "rcc" ]; then
            RCC_VERSION=`rcc -v | cut -d' ' -f2 | cut -d. -f1`
            if [ "$RCC_VERSION" = "6" ]; then
                break
            fi
        else
            break
        fi
    fi
    RCC_CMD=""
done

if [ "$RCC_CMD" = "" ]; then
    echo "ERROR: rcc binary not found"
    exit 1
fi

# Backup the existing resources
if [ -f "openlp/core/resources.py" ]; then
    echo "Backup old resources file"
    mv openlp/core/resources.py openlp/core/resources.py.old
fi

# Create the new data from the updated qrc
echo "Generate new resources file"
$RCC_CMD -g python -o openlp/core/resources.py.new resources/images/openlp-2.qrc

# Remove patch breaking lines
echo "Remove comments at top of file"
cat openlp/core/resources.py.new | sed '1,5d' > openlp/core/resources.py

# Patch resources.py to OpenLP coding style
ARCH=`uname -m`
echo "Architecture is: $ARCH"
if [ "$ARCH" = "arm64" ]; then
    echo "Running ARM64 patch"
    patch --posix -s openlp/core/resources.py scripts/resources.arm64.patch
else
    echo "Running x86 patch"
    patch --posix -s openlp/core/resources.py scripts/resources.patch
fi

# Remove temporary file
rm -f openlp/core/resources.py.new 2>/dev/null
rm -f openlp/core/resources.py.old 2>/dev/null
rm -f openlp/core/resources.py.orig 2>/dev/null
