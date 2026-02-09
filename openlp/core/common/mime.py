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

def get_mime_type(file):
    if file.lower().endswith('.aac'):
        mime_type = 'audio/aac'
    elif file.lower().endswith('.abw'):
        mime_type = 'application/x-abiword'
    elif file.lower().endswith('.arc'):
        mime_type = 'application/x-freearc'
    elif file.lower().endswith('.avi'):
        mime_type = 'video/x-msvideo'
    elif file.lower().endswith('.azw'):
        mime_type = 'application/vnd.amazon.ebook'
    elif file.lower().endswith('.bin'):
        mime_type = 'application/octet-stream'
    elif file.lower().endswith('.bmp'):
        mime_type = 'image/bmp'
    elif file.lower().endswith('.bz'):
        mime_type = 'application/x-bzip'
    elif file.lower().endswith('.bz2'):
        mime_type = 'application/x-bzip2'
    elif file.lower().endswith('.cda'):
        mime_type = 'application/x-cdf'
    elif file.lower().endswith('.csh'):
        mime_type = 'application/x-csh'
    elif file.lower().endswith('.css'):
        mime_type = 'text/css'
    elif file.lower().endswith('.csv'):
        mime_type = 'text/csv'
    elif file.lower().endswith('.doc'):
        mime_type = 'application/msword'
    elif file.lower().endswith('.docx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file.lower().endswith('.eot'):
        mime_type = 'application/vnd.ms-fontobject'
    elif file.lower().endswith('.epub'):
        mime_type = 'application/epub+zip'
    elif file.lower().endswith('.gz'):
        mime_type = 'application/gzip'
    elif file.lower().endswith('.gif'):
        mime_type = 'image/gif'
    elif file.lower().endswith('.htm'):
        mime_type = 'text/html'
    elif file.lower().endswith('.html'):
        mime_type = 'text/html'
    elif file.lower().endswith('.ico'):
        mime_type = 'image/vnd.microsoft.icon'
    elif file.lower().endswith('.ics'):
        mime_type = 'text/calendar'
    elif file.lower().endswith('.jar'):
        mime_type = 'application/java-archive'
    elif file.lower().endswith('.jpeg'):
        mime_type = 'image/jpeg'
    elif file.lower().endswith('.jpg'):
        mime_type = 'image/jpeg'
    elif file.lower().endswith('.js'):
        mime_type = 'application/javascript'
    elif file.lower().endswith('.json'):
        mime_type = 'application/json'
    elif file.lower().endswith('.jsonld'):
        mime_type = 'application/ld+json'
    elif file.lower().endswith('.mid'):
        mime_type = 'audio/midi'
    elif file.lower().endswith('.midi'):
        mime_type = 'audio/x-midi'
    elif file.lower().endswith('.mjs'):
        mime_type = 'text/javascript'
    elif file.lower().endswith('.mp3'):
        mime_type = 'audio/mpeg'
    elif file.lower().endswith('.mp4'):
        mime_type = 'video/mp4'
    elif file.lower().endswith('.mpeg'):
        mime_type = 'video/mpeg'
    elif file.lower().endswith('.mpkg'):
        mime_type = 'application/vnd.apple.installer+xml'
    elif file.lower().endswith('.odp'):
        mime_type = 'application/vnd.oasis.opendocument.presentation'
    elif file.lower().endswith('.ods'):
        mime_type = 'application/vnd.oasis.opendocument.spreadsheet'
    elif file.lower().endswith('.odt'):
        mime_type = 'application/vnd.oasis.opendocument.text'
    elif file.lower().endswith('.oga'):
        mime_type = 'audio/ogg'
    elif file.lower().endswith('.ogv'):
        mime_type = 'video/ogg'
    elif file.lower().endswith('.ogx'):
        mime_type = 'application/ogg'
    elif file.lower().endswith('.opus'):
        mime_type = 'audio/opus'
    elif file.lower().endswith('.otf'):
        mime_type = 'application/x-font-opentype'
    elif file.lower().endswith('.png'):
        mime_type = 'image/png'
    elif file.lower().endswith('.pdf'):
        mime_type = 'application/pdf'
    elif file.lower().endswith('.php'):
        mime_type = 'application/x-httpd-php'
    elif file.lower().endswith('.ppt'):
        mime_type = 'application/vnd.ms-powerpoint'
    elif file.lower().endswith('.pptx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif file.lower().endswith('.rar'):
        mime_type = 'application/vnd.rar'
    elif file.lower().endswith('.rtf'):
        mime_type = 'application/rtf'
    elif file.lower().endswith('.sfnt'):
        mime_type = 'application/font-sfnt'
    elif file.lower().endswith('.sh'):
        mime_type = 'application/x-sh'
    elif file.lower().endswith('.svg'):
        mime_type = 'image/svg+xml'
    elif file.lower().endswith('.swf'):
        mime_type = 'application/x-shockwave-flash'
    elif file.lower().endswith('.tar'):
        mime_type = 'application/x-tar'
    elif file.lower().endswith('.tif'):
        mime_type = 'image/tiff'
    elif file.lower().endswith('.tiff'):
        mime_type = 'image/tiff'
    elif file.lower().endswith('.ts'):
        mime_type = 'video/mp2t'
    elif file.lower().endswith('.ttf'):
        mime_type = 'application/x-font-ttf'
    elif file.lower().endswith('.txt'):
        mime_type = 'text/plain'
    elif file.lower().endswith('.vsd'):
        mime_type = 'application/vnd.visio'
    elif file.lower().endswith('.wav'):
        mime_type = 'audio/wav'
    elif file.lower().endswith('.weba'):
        mime_type = 'audio/webm'
    elif file.lower().endswith('.webm'):
        mime_type = 'video/webm'
    elif file.lower().endswith('.webp'):
        mime_type = 'image/webp'
    elif file.lower().endswith('.woff'):
        mime_type = 'application/font-woff'
    elif file.lower().endswith('.woff2'):
        mime_type = 'application/font-woff2'
    elif file.lower().endswith('.xhtml'):
        mime_type = 'application/xhtml+xml'
    elif file.lower().endswith('.xls'):
        mime_type = 'application/vnd.ms-excel'
    elif file.lower().endswith('.xlsx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif file.lower().endswith('.xml'):
        mime_type = 'application/xml'
    elif file.lower().endswith('.xul'):
        mime_type = 'application/vnd.mozilla.xul+xml'
    elif file.lower().endswith('.zip'):
        mime_type = 'application/zip'
    elif file.lower().endswith('.7z'):
        mime_type = 'application/x-7z-compressed'
    else:
        mime_type = 'application/octet-stream'
    return mime_type
