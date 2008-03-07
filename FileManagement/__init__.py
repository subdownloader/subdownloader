##    Copyright (C) 2007 Ivan Garcia contact@ivangarcia.org
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License along
##    with this program; if not, write to the Free Software Foundation, Inc.,
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''
FileManagement package
'''
import re, string

def get_extension(path):
    if re.search("\.\w+$", path):
        return re.search("\w+$", path).group(0)
    return ""

def clear_string(strng):
    r_chars = '_.,()'
    return strng.translate(string.maketrans(r_chars," "*len(r_chars))).replace(" ", "")
    
def without_extension(filename):
    ext = get_extension(filename)
    return filename.replace("."+ext, "")
