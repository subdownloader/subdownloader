################################################################################
#  Copyright (C) 2003-2004  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#  $Id: utils.py,v 1.3 2004/05/14 14:44:59 outlyer Exp $
################################################################################
from mmpython.audio.eyeD3 import *

def versionsToConstant(v):
   major = v[0];
   minor = v[1];
   rev = v[2];
   if major == 1:
      if minor == 0:
	 return ID3_V1_0;
      elif minor == 1:
	 return ID3_V1_1;
   elif major == 2:
      if minor == 3:
	 return ID3_V2_3;
      elif minor == 4:
	 return ID3_V2_4;
   raise str("Invalid ID3 version: %s" % str(v));

def versionToString(v):
   if v & ID3_V1:
      if v == ID3_V1_0:
	 return "v1.0";
      elif v == ID3_V1_1:
	 return "v1.1";
      elif v == ID3_V1:
         return "v1.x";
   elif v & ID3_V2:
      if v == ID3_V2_3:
	 return "v2.3";
      elif v == ID3_V2_4:
	 return "v2.4";
      elif v == ID3_V2:
         return "v2.x";

   if v == ID3_ANY_VERSION:
      return "v1.x/v2.x";
   raise str("versionToString - Invalid ID3 version constant: %s" % hex(v));

def constantToVersions(v):
   if v & ID3_V1:
      if v == ID3_V1_0:
         return [1, 0, 0];
      elif v == ID3_V1_1:
         return [1, 1, 0];
      elif v == ID3_V1:
         return [1, 1, 0];
   elif v & ID3_V2:
      if v == ID3_V2_3:
         return [2, 3, 0];
      elif v == ID3_V2_4:
         return [2, 4, 0];
      elif v == ID3_V2:
         return [2, 4, 0];
   raise str("constantToVersions - Invalid ID3 version constant: %s" % hex(v));

################################################################################
TRACE = 0;
prefix = "eyeD3 trace> ";
def TRACE_MSG(msg):
   if TRACE:
      print prefix + msg;

STRICT_ID3 = 0;
def strictID3():
   return STRICT_ID3;

