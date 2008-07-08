################################################################################
#
#  Copyright (C) 2002-2004  Travis Shirk <travis@pobox.com>
#  Copyright (C) 2001  Ryan Finne <ryan@finnie.org>
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
################################################################################
import os, os.path, re, zlib, StringIO, time, mimetypes;
from StringIO import StringIO;
from utils import *;
from binfuncs import *;

# Valid time stamp formats per ISO 8601 and used by time.strptime.
timeStampFormats = ["%Y",
                    "%Y-%m",
                    "%Y-%m-%d",
                    "%Y-%m-%dT%H",
                    "%Y-%m-%dT%H:%M",
                    "%Y-%m-%dT%H:%M:%S"];

ARTIST_FID         = "TPE1";
BAND_FID           = "TPE2";
CONDUCTOR_FID      = "TPE3";
REMIXER_FID        = "TPE4";
COMPOSER_FID       = "TCOM";
ARTIST_FIDS        = [ARTIST_FID, BAND_FID, CONDUCTOR_FID,
                      REMIXER_FID, COMPOSER_FID];
ALBUM_FID          = "TALB";
TITLE_FID          = "TIT2";
SUBTITLE_FID       = "TIT3";
CONTENT_TITLE_FID  = "TIT1";
TITLE_FIDS         = [TITLE_FID, SUBTITLE_FID, CONTENT_TITLE_FID];
COMMENT_FID        = "COMM";
GENRE_FID          = "TCON";
TRACKNUM_FID       = "TRCK";
USERTEXT_FID       = "TXXX";
CDID_FID           = "MCDI";
IMAGE_FID          = "APIC";
URL_COMMERCIAL_FID = "WCOM";
URL_COPYRIGHT_FID  = "WCOP";
URL_AUDIOFILE_FID  = "WOAF";
URL_ARTIST_FID     = "WOAR";
URL_AUDIOSRC_FID   = "WOAS";
URL_INET_RADIO_FID = "WORS";
URL_PAYMENT_FID    = "WPAY";
URL_PUBLISHER_FID  = "WPUB";
URL_FIDS           = [URL_COMMERCIAL_FID, URL_COPYRIGHT_FID,
                      URL_AUDIOFILE_FID, URL_ARTIST_FID, URL_AUDIOSRC_FID,
                      URL_INET_RADIO_FID, URL_PAYMENT_FID,
                      URL_PUBLISHER_FID];
USERURL_FID        = "WXXX";

obsoleteFrames = {"EQUA": "Equalisation",
                  "IPLS": "Involved people list",
                  "RVAD": "Relative volume adjustment",
                  "TDAT": "Date",
                  "TORY": "Original release year",
                  "TRDA": "Recording dates",
                  "TYER": "Year"};
# Both of these are "coerced" into a v2.4 TDRC frame when read, and 
# recreated when saving v2.3.
OBSOLETE_DATE_FID            = "TDAT";
OBSOLETE_YEAR_FID            = "TYER";
OBSOLETE_TIME_FID            = "TIME";
OBSOLETE_ORIG_RELEASE_FID    = "TORY";
OBSOLETE_RECORDING_DATE_FID  = "TRDA";

frameDesc = { "AENC": "Audio encryption",
              "APIC": "Attached picture",
              "ASPI": "Audio seek point index",

              "COMM": "Comments",
              "COMR": "Commercial frame",

              "ENCR": "Encryption method registration",
              "EQU2": "Equalisation (2)",
              "ETCO": "Event timing codes",

              "GEOB": "General encapsulated object",
              "GRID": "Group identification registration",

              "LINK": "Linked information",

              "MCDI": "Music CD identifier",
              "MLLT": "MPEG location lookup table",

              "OWNE": "Ownership frame",

              "PRIV": "Private frame",
              "PCNT": "Play counter",
              "POPM": "Popularimeter",
              "POSS": "Position synchronisation frame",

              "RBUF": "Recommended buffer size",
              "RVA2": "Relative volume adjustment (2)",
              "RVRB": "Reverb",

              "SEEK": "Seek frame",
              "SIGN": "Signature frame",
              "SYLT": "Synchronised lyric/text",
              "SYTC": "Synchronised tempo codes",

              "TALB": "Album/Movie/Show title",
              "TBPM": "BPM (beats per minute)",
              "TCOM": "Composer",
              "TCON": "Content type",
              "TCOP": "Copyright message",
              "TDEN": "Encoding time",
              "TDLY": "Playlist delay",
              "TDOR": "Original release time",
              "TDRC": "Recording time",
              "TDRL": "Release time",
              "TDTG": "Tagging time",
              "TENC": "Encoded by",
              "TEXT": "Lyricist/Text writer",
              "TFLT": "File type",
              "TIPL": "Involved people list",
              "TIT1": "Content group description",
              "TIT2": "Title/songname/content description",
              "TIT3": "Subtitle/Description refinement",
              "TKEY": "Initial key",
              "TLAN": "Language(s)",
              "TLEN": "Length",
              "TMCL": "Musician credits list",
              "TMED": "Media type",
              "TMOO": "Mood",
              "TOAL": "Original album/movie/show title",
              "TOFN": "Original filename",
              "TOLY": "Original lyricist(s)/text writer(s)",
              "TOPE": "Original artist(s)/performer(s)",
              "TOWN": "File owner/licensee",
              "TPE1": "Lead performer(s)/Soloist(s)",
              "TPE2": "Band/orchestra/accompaniment",
              "TPE3": "Conductor/performer refinement",
              "TPE4": "Interpreted, remixed, or otherwise modified by",
              "TPOS": "Part of a set",
              "TPRO": "Produced notice",
              "TPUB": "Publisher",
              "TRCK": "Track number/Position in set",
              "TRSN": "Internet radio station name",
              "TRSO": "Internet radio station owner",
              "TSOA": "Album sort order",
              "TSOP": "Performer sort order",
              "TSOT": "Title sort order",
              "TSRC": "ISRC (international standard recording code)",
              "TSSE": "Software/Hardware and settings used for encoding",
              "TSST": "Set subtitle",
              "TXXX": "User defined text information frame",

              "UFID": "Unique file identifier",
              "USER": "Terms of use",
              "USLT": "Unsynchronised lyric/text transcription",

              "WCOM": "Commercial information",
              "WCOP": "Copyright/Legal information",
              "WOAF": "Official audio file webpage",
              "WOAR": "Official artist/performer webpage",
              "WOAS": "Official audio source webpage",
              "WORS": "Official Internet radio station homepage",
              "WPAY": "Payment",
              "WPUB": "Publishers official webpage",
              "WXXX": "User defined URL link frame" };

NULL_FRAME_FLAGS = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

TEXT_FRAME_RX = re.compile("^T[A-Z0-9][A-Z0-9][A-Z0-9]$");
USERTEXT_FRAME_RX = re.compile("^" + USERTEXT_FID + "$");
URL_FRAME_RX = re.compile("^W[A-Z0-9][A-Z0-9][A-Z0-9]$");
USERURL_FRAME_RX = re.compile("^" + USERURL_FID + "$");
COMMENT_FRAME_RX = re.compile("^" + COMMENT_FID + "$");
CDID_FRAME_RX = re.compile("^" + CDID_FID + "$");
IMAGE_FRAME_RX = re.compile("^" + IMAGE_FID + "$");

LATIN1_ENCODING   = "\x00";
UTF_16_ENCODING   = "\x01";
UTF_16BE_ENCODING = "\x02";
UTF_8_ENCODING    = "\x03";

DEFAULT_ENCODING = LATIN1_ENCODING;
DEFAULT_ID3_MAJOR_VERSION = 2;
DEFAULT_ID3_MINOR_VERSION = 4;
DEFAULT_LANG = "eng";

def id3EncodingToString(encoding):
    if encoding == LATIN1_ENCODING:
        return "latin_1";
    elif encoding == UTF_8_ENCODING:
        return "utf_8";
    elif encoding == UTF_16_ENCODING:
        return "utf_16";
    elif encoding == UTF_16BE_ENCODING:
        return "utf_16_be";
    else:
        raise ValueError;

################################################################################
class FrameException:
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;

################################################################################
class FrameHeader:
   FRAME_HEADER_SIZE = 10;
   # The tag header
   majorVersion = DEFAULT_ID3_MAJOR_VERSION;
   minorVersion = DEFAULT_ID3_MINOR_VERSION;
   # The 4 character frame ID.
   id = None;
   # An array of 16 "bits"...
   flags = NULL_FRAME_FLAGS;
   # ...and the info they store.
   tagAlter = 0;
   fileAlter = 0;
   readOnly = 0;
   compressed = 0;
   encrypted = 0;
   grouped = 0;
   unsync = 0;
   dataLenIndicator = 0;
   # The size of the data following this header.
   dataSize = 0;

   # 2.4 not only added flag bits, but also reordered the previously defined
   # flags.  So these are mapped once we know the version.
   TAG_ALTER   = None;   
   FILE_ALTER  = None;   
   READ_ONLY   = None;   
   COMPRESSION = None;   
   ENCRYPTION  = None;   
   GROUPING    = None;   
   UNSYNC      = None;   
   DATA_LEN    = None;   

   # Constructor.
   def __init__(self, tagHeader = None):
      if tagHeader:
         self.setVersion(tagHeader);
      else:
         self.setVersion([DEFAULT_ID3_MAJOR_VERSION,
                          DEFAULT_ID3_MINOR_VERSION]);

   def setVersion(self, tagHeader):
      # A slight hack to make the default ctor work.
      if isinstance(tagHeader, list):
         self.majorVersion = tagHeader[0];
         self.minorVersion = tagHeader[1];
      else:
         self.majorVersion = tagHeader.majorVersion;
         self.minorVersion = tagHeader.minorVersion;
      self.setBitMask();

   def setBitMask(self):
      major = self.majorVersion;
      minor = self.minorVersion;

      # 1.x tags are converted to 2.4 frames internally.  These frames are
      # created with frame flags \x00.
      if (major == 2 and minor == 3):
         self.TAG_ALTER   = 0;   
         self.FILE_ALTER  = 1;   
         self.READ_ONLY   = 2;   
         self.COMPRESSION = 8;   
         self.ENCRYPTION  = 9;   
         self.GROUPING    = 10;   
         # This is not really in 2.3 frame header flags, but there is
         # a "global" unsync bit in the tag header and that is written here
         # so access to the tag header is not required.
         self.UNSYNC      = 14;   
         # And this is mapped to an used bit, so that 0 is returned.
         self.DATA_LEN    = 4;
      elif (major == 2 and minor == 4) or \
           (major == 1 and (minor == 0 or minor == 1)):
         self.TAG_ALTER   = 1;   
         self.FILE_ALTER  = 2;   
         self.READ_ONLY   = 3;   
         self.COMPRESSION = 12;   
         self.ENCRYPTION  = 13;   
         self.GROUPING    = 9;   
         self.UNSYNC      = 14;   
         self.DATA_LEN    = 15;   
      else:
         raise ValueError("ID3 v" + str(major) + "." + str(minor) +\
                          " is not supported.");

   def render(self, dataSize):
      data = self.id;

      if self.minorVersion == 3:
         data += bin2bytes(dec2bin(dataSize, 32));
      else:
         data += bin2bytes(bin2synchsafe(dec2bin(dataSize, 32)));

      self.setBitMask();
      self.flags = NULL_FRAME_FLAGS;
      self.flags[self.TAG_ALTER] = self.tagAlter;
      self.flags[self.FILE_ALTER] = self.fileAlter;
      self.flags[self.READ_ONLY] = self.readOnly;
      self.flags[self.COMPRESSION] = self.compressed;
      self.flags[self.COMPRESSION] = self.compressed;
      self.flags[self.ENCRYPTION] = self.encrypted;
      self.flags[self.GROUPING] = self.grouped;
      self.flags[self.UNSYNC] = self.unsync;
      self.flags[self.DATA_LEN] = self.dataLenIndicator;

      data += bin2bytes(self.flags);

      return data;

   # Returns 1 on success and 0 when a null tag (marking the beginning of
   # padding).  In the case of an invalid frame header, a FrameException is 
   # thrown.
   def parse(self, f):
      TRACE_MSG("FrameHeader [start byte]: %d (0x%X)" % (f.tell(),
                                                         f.tell()));
      frameId = f.read(4);
      TRACE_MSG("FrameHeader [id]: %s (0x%x%x%x%x)" % (frameId,
                                                       ord(frameId[0]),
                                                       ord(frameId[1]),
                                                       ord(frameId[2]),
                                                       ord(frameId[3])));

      if self.isFrameIdValid(frameId):
         self.id = frameId;
         # dataSize corresponds to the size of the data segment after
         # encryption, compression, and unsynchronization.
         sz = f.read(4);
         # In ID3 v2.4 this value became a synch-safe integer, meaning only
         # the low 7 bits are used per byte.
         if self.minorVersion == 3:
            self.dataSize = bin2dec(bytes2bin(sz, 8));
         else:
            self.dataSize = bin2dec(bytes2bin(sz, 7));
         TRACE_MSG("FrameHeader [data size]: %d (0x%X)" % (self.dataSize,
                                                           self.dataSize));
 
         # Frame flags.
         flags = f.read(2);
         self.flags = bytes2bin(flags);
         self.tagAlter = self.flags[self.TAG_ALTER];
         self.fileAlter = self.flags[self.FILE_ALTER];
         self.readOnly = self.flags[self.READ_ONLY];
         self.compressed = self.flags[self.COMPRESSION];
         self.encrypted = self.flags[self.ENCRYPTION];
         self.grouped = self.flags[self.GROUPING];
         self.unsync = self.flags[self.UNSYNC];
         self.dataLenIndicator = self.flags[self.DATA_LEN];
         TRACE_MSG("FrameHeader [flags]: ta(%d) fa(%d) ro(%d) co(%d) "\
                   "en(%d) gr(%d) un(%d) dl(%d)" % (self.tagAlter,
                                                    self.fileAlter,
                                                    self.readOnly,
                                                    self.compressed,
                                                    self.encrypted,
                                                    self.grouped,
                                                    self.unsync,
                                                    self.dataLenIndicator));
         if self.minorVersion >= 4 and self.compressed and \
            not self.dataLenIndicator:
            raise FrameException("Invalid frame; compressed with no data "
                                 "length indicator");

      elif frameId == '\x00\x00\x00\x00':
         TRACE_MSG("FrameHeader: Null frame id found at byte " +\
                   str(f.tell()));
         return 0;
      else:
         raise FrameException("FrameHeader: Illegal Frame ID: " + frameId);
      return 1;


   def isFrameIdValid(self, id):
      return re.compile(r"^[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]$").match(id) or \
             id == 'MP3e' or id[1:] == 'MP3'

   def clearFlags(self):
      flags = [0] * 16;

################################################################################
def unsyncData(data):
   subs = (0, 0);
   (data, subs[0]) = re.compile("\xff\x00").subn("\xff\x00\x00", data);
   (data, subs[1]) = re.compile("\xff(?=[\xe0-\xff])").subn("\xff\x00", data);
   TRACE_MSG("Unsynchronizing data: " + str(subs));
   return data;

def deunsyncData(data):
   TRACE_MSG("Frame: [size before deunsync]: " + str(len(data)));
   data = re.compile("\xff\x00([\xe0-\xff])").sub("\xff\\1", data);
   TRACE_MSG("Frame: [size after stage #1 deunsync]: " + str(len(data)));
   data = re.compile("\xff\x00\x00").sub("\xff\x00", data);
   TRACE_MSG("Frame: [size after deunsync: " + str(len(data)));
   return data;

################################################################################
class Frame:
   header = None;
   decompressedSize = 0;
   groupId = 0;
   encryptionMethod = 0;
   dataLen = 0;

   def __repr__(self):
      desc = self.getFrameDesc();
      return '<%s Frame (%s)>' % (desc, self.header.id);

   def unsync(self, data):
      if self.header.unsync:
         data = unsyncData(data);
      return data;

   def deunsync(self, data):
      data = deunsyncData(data);
      return data;

   def decompress(self, data):
      TRACE_MSG("before decompression: %d bytes" % len(data));
      data = zlib.decompress(data, 15, self.decompressedSize);
      TRACE_MSG("after decompression: %d bytes" % len(data));
      return data;

   def compress(self, data):
      TRACE_MSG("before compression: %d bytes" % len(data));
      data = zlib.compress(data);
      TRACE_MSG("after compression: %d bytes" % len(data));
      return data;

   def decrypt(self, data):
      raise FrameException("Ecnyption Not Supported");

   def encrypt(self, data):
      raise FrameException("Ecnyption Not Supported");

   def disassembleFrame(self, data):
      # Format flags in the frame header may add extra data to the
      # beginning of this data.
      if self.header.minorVersion == 3:
         # 2.3:  compression(4), encryption(1), group(1) 
         if self.header.compressed:
            self.decompressedSize = bin2dec(bytes2bin(data[:4]));
            data = data[4:];
            TRACE_MSG("Decompressed Size: %d" % self.decompressedSize);
         if self.header.encrypted:
            self.encryptionMethod = bin2dec(bytes2bin(data[0]));
            data = data[1:];
            TRACE_MSG("Encryption Method: %d" % self.encryptionMethod);
         if self.header.grouped:
            self.groupId = bin2dec(bytes2bin(data[0]));
            data = data[1:];
            TRACE_MSG("Group ID: %d" % self.groupId);
      else:
         # 2.4:  group(1), encrypted(1), dataLenIndicator(4,7)
         if self.header.grouped:
            self.groupId = bin2dec(bytes2bin(data[0]));
            data = data[1:];
         if self.header.encrypted:
            self.encryptionMethod = bin2dec(bytes2bin(data[0]));
            data = data[1:];
            TRACE_MSG("Encryption Method: %d" % self.encryptionMethod);
            TRACE_MSG("Group ID: %d" % self.groupId);
         if self.header.dataLenIndicator:
            self.dataLen = bin2dec(bytes2bin(data[:4], 7));
            data = data[4:];
            TRACE_MSG("Data Length: %d" % self.dataLen);
            if self.header.compressed:
               self.decompressedSize = self.dataLen;
               TRACE_MSG("Decompressed Size: %d" % self.decompressedSize);

      if self.header.unsync:
         data = self.deunsync(data);
      if self.header.encrypted:
         data = self.decrypt(data);
      if self.header.compressed:
         data = self.decompress(data);
      return data;

   def assembleFrame (self, data):
      formatFlagData = "";
      if self.header.minorVersion == 3:
         if self.header.compressed:
            formatFlagData += bin2bytes(dec2bin(len(data), 32));
         if self.header.encrypted:
            formatFlagData += bin2bytes(dec2bin(self.encryptionMethod, 8));
         if self.header.grouped:
            formatFlagData += bin2bytes(dec2bin(self.groupId, 8));
      else:
         if self.header.grouped:
            formatFlagData += bin2bytes(dec2bin(self.groupId, 8));
         if self.header.encrypted:
            formatFlagData += bin2bytes(dec2bin(self.encryptionMethod, 8));
         if self.header.compressed or self.header.dataLenIndicator:
            # Just in case, not sure about this?
            self.header.dataLenIndicator = 1;
            formatFlagData += bin2bytes(dec2bin(len(data), 32));

      if self.header.compressed:
         data = self.compress(data);
      if self.header.encrypted:
         data = self.encrypt(data);
      if self.header.unsync:
         data = self.unsync(data);

      data = formatFlagData + data;
      return self.header.render(len(data)) + data;

   def getFrameDesc(self):
      try:
         return frameDesc[self.header.id];
      except KeyError:
         try:
            return obsoleteFrames[self.header.id];
         except KeyError:
            return "UNKOWN FRAME";

################################################################################
class TextFrame(Frame):
   encoding = DEFAULT_ENCODING;
   text = u"";

   # Data string format:
   # encoding (one byte) + text;
   def __init__(self, data, frameHeader):
      self.set(data, frameHeader);

   # Data string format:
   # encoding (one byte) + text;
   def set(self, data, frameHeader):
      fid = frameHeader.id;
      if not TEXT_FRAME_RX.match(fid) or USERTEXT_FRAME_RX.match(fid):
         raise FrameException("Invalid frame id for TextFrame: " + fid);
      self.header = frameHeader;

      data = self.disassembleFrame(data);
      self.encoding = data[0];
      TRACE_MSG("TextFrame encoding: %s" % id3EncodingToString(self.encoding));
      self.text = unicode(data[1:], id3EncodingToString(self.encoding));
      TRACE_MSG("TextFrame text: %s" % self.text);

   def __repr__(self):
      return '<%s (%s): %s>' % (self.getFrameDesc(), self.header.id, self.text);

   def render(self):
       if self.header.minorVersion == 4 and self.header.id == "TSIZ":
           TRACE_MSG("Dropping deprecated frame TSIZ");
           return "";
       data = self.encoding +\
              self.text.encode(id3EncodingToString(self.encoding));
       return self.assembleFrame(data);

################################################################################
class DateFrame(TextFrame):
   def __init__(self, data, frameHeader):
      self.date = None;
      self.date_str = "";
      self.set(data, frameHeader);

   def set(self, data, frameHeader):
      TextFrame.set(self, data, frameHeader);
      if self.header.id[:2] != "TD" and self.header.minorVersion != 3:
         raise FrameException("Invalid frame id for DateFrame: " + \
                              self.header.id);
      self.setDate(self.text);
   
   def setDate(self, d):
      if not d:
         self.date = None;
         self.date_str = "";
         return;

      for fmt in timeStampFormats:
         try:
            if isinstance(d, tuple):
               self.date_str = time.strftime(fmt, d);
               self.date = d;
            else:
               d = d.strip("\x00");

               # Witnessed oddball tags with NULL bytes (ozzy.tag from id3lib)
               strippedDate = "";
               for c in d:
                  if ord(c) != 0:
                     strippedDate += c;
               d = strippedDate;

               try:
                  self.date = time.strptime(d, fmt);
               except TypeError, ex:
                  continue;
               self.date_str = d;
            break;
         except ValueError:
            self.date = None;
            self.date_str = "";
            continue;
      if strictID3() and not self.date:
         raise FrameException("Invalid Date: " + str(d));
      self.text = self.date_str;

   def getDate(self):
      return self.date_str;

   def getYear(self):
      if self.date:
	 return self.__padDateField(self.date[0], 4);
      else:
         return None;

   def getMonth(self):
      if self.date:
	 return self.__padDateField(self.date[1], 2);
      else:
         return None;

   def getDay(self):
      if self.date:
	 return self.__padDateField(self.date[2], 2);
      else:
         return None;

   def getHour(self):
      if self.date:
	 return self.__padDateField(self.date[3], 2);
      else:
         return None;

   def getMinute(self):
      if self.date:
	 return self.__padDateField(self.date[4], 2);
      else:
         return None;

   def getSecond(self):
      if self.date:
	 return self.__padDateField(self.date[5], 2);
      else:
         return None;

   def __padDateField(self, f, sz):
      fStr = str(f);
      if len(fStr) == sz:
         pass;
      elif len(fStr) < sz:
         fStr = ("0" * (sz - len(fStr))) + fStr;
      else:
         raise TagException("Invalid date field: " + fStr);
      return fStr;

   def render(self):
       # Conversion crap
       if self.header.minorVersion == 4 and\
          (self.header.id == OBSOLETE_DATE_FID or\
           self.header.id == OBSOLETE_YEAR_FID or\
           self.header.id == OBSOLETE_TIME_FID or\
           self.header.id == OBSOLETE_RECORDING_DATE_FID):
           self.header.id = "TDRC";
       elif self.header.minorVersion == 4 and\
            self.header.id == OBSOLETE_ORIG_RELEASE_FID:
           self.header.id = "TDOR";
       elif self.header.minorVersion == 3 and self.header.id == "TDOR":
           self.header.id = OBSOLETE_ORIG_RELEASE_FID;
       elif self.header.minorVersion == 3 and self.header.id[:2] == "TD":
           self.header.id = OBSOLETE_YEAR_FID;

       data = self.encoding + str(self.date_str);
       data = self.assembleFrame(data);
       return data;


################################################################################
class UserTextFrame(TextFrame):
   description = u"";

   # Data string format:
   # encoding (one byte) + description + "\x00" + text;
   def __init__(self, data, frameHeader = None):
      self.set(data, frameHeader);

   # Data string format:
   # encoding (one byte) + description + "\x00" + text;
   def set(self, data, frameHeader = None):
      if frameHeader:
         if not USERTEXT_FRAME_RX.match(frameHeader.id):
            raise FrameException("Invalid frame id for UserTextFrame: " +\
                                 frameHeader.id);
      else:
         frameHeader = FrameHeader();
         frameHeader.id = USERTEXT_FID;
      self.header = frameHeader;

      data = self.disassembleFrame(data);
      self.encoding = data[0];
      TRACE_MSG("UserTextFrame encoding: %s" %\
                id3EncodingToString(self.encoding));
      (d, t) = splitUnicode(data[1:], self.encoding);
      self.description = unicode(d, id3EncodingToString(self.encoding));
      TRACE_MSG("UserTextFrame description: %s" % self.description);
      self.text = unicode(t, id3EncodingToString(self.encoding));
      TRACE_MSG("UserTextFrame text: %s" % self.text);

   def render(self):
      data = self.encoding +\
             self.description.encode(id3EncodingToString(self.encoding)) +\
             "\x00" +\
             self.text.encode(id3EncodingToString(self.encoding));
      return self.assembleFrame(data);

################################################################################
class URLFrame(Frame):
   url = "";

   # Data string format:
   # url
   def __init__(self, data, frameHeader):
      self.set(data, frameHeader);

   # Data string format:
   # url
   def set(self, data, frameHeader):
      fid = frameHeader.id;
      if not URL_FRAME_RX.match(fid) or USERURL_FRAME_RX.match(fid):
         raise FrameException("Invalid frame id for URLFrame: " + fid);
      self.header = frameHeader;

      data = self.disassembleFrame(data);
      self.url = data;

   def render(self):
      data = str(self.url);
      return self.assembleFrame(data);

   def __repr__(self):
      return '<%s (%s): %s>' % (self.getFrameDesc(), self.header.id,
                                self.url);

################################################################################
class UserURLFrame(URLFrame):
   encoding = DEFAULT_ENCODING;
   description = u"";

   # Data string format:
   # encoding (one byte) + description + "\x00" + url;
   def __init__(self, data, frameHeader = None):
      self.set(data, frameHeader);

   # Data string format:
   # encoding (one byte) + description + "\x00" + url;
   def set(self, data, frameHeader = None):
      if frameHeader:
         if not USERURL_FRAME_RX.match(frameHeader.id):
            raise FrameException("Invalid frame id for UserURLFrame: " +\
                                 frameHeader.id);
      else:
         frameHeader = FrameHeader();
         frameHeader.id = USERURL_FID;
      self.header = frameHeader;

      data = self.disassembleFrame(data);
      self.encoding = data[0];
      TRACE_MSG("UserURLFrame encoding: %s" %\
                id3EncodingToString(self.encoding));
      (d, u) = splitUnicode(data[1:], self.encoding);
      self.description = unicode(d, id3EncodingToString(self.encoding));
      TRACE_MSG("UserURLFrame description: %s" % self.description);
      self.url = u;
      TRACE_MSG("UserURLFrame text: %s" % self.url);

   def render(self):
      data = self.encoding +\
             self.description.encode(id3EncodingToString(self.encoding)) +\
             "\x00" + self.url;
      return self.assembleFrame(data);

   def __repr__(self):
      return '<%s (%s): %s [Encoding: %s] [Desc: %s]>' %\
             (self.getFrameDesc(), self.header.id,
              self.url, self.encoding, self.description)

################################################################################
class CommentFrame(Frame):
   encoding = DEFAULT_ENCODING;
   lang = u"";
   description = u"";
   comment = u"";

   # Data string format:
   # encoding (one byte) + lang (three byte code) + description + "\x00" +
   # text
   def __init__(self, data, frameHeader = None):
      self.set(data, frameHeader);

   # Data string format:
   # encoding (one byte) + lang (three byte code) + description + "\x00" +
   # text
   def set(self, data, frameHeader = None):
      if frameHeader:
         if not COMMENT_FRAME_RX.match(frameHeader.id):
            raise FrameException("Invalid frame id for CommentFrame: " +\
                                 frameHeader.id);
      else:
         frameHeader = FrameHeader();
         frameHeader.id = COMMENT_FID;
      self.header = frameHeader;

      data = self.disassembleFrame(data);
      self.encoding = data[0];
      TRACE_MSG("CommentFrame encoding: " + id3EncodingToString(self.encoding));
      try:
          self.lang = str(data[1:4]).strip("\x00");
          self.lang = unicode(self.lang, "ascii");
          if self.lang and \
             not re.compile("[A-Z][A-Z][A-Z]", re.IGNORECASE).match(self.lang):
             if strictID3():
                 raise FrameException("[CommentFrame] Invalid language "\
                                       "code: %s" % self.lang);
      except UnicodeDecodeError, ex:
          if strictID3():
              raise FrameException("[CommentFrame] Invalid language code: "\
                                   "[%s] %s" % (ex.object, ex.reason));
          else:
              self.lang = "";
      try:
         (d, c) = splitUnicode(data[4:], self.encoding);
         self.description = unicode(d, id3EncodingToString(self.encoding));
         self.comment = unicode(c, id3EncodingToString(self.encoding));
      except ValueError:
          if strictID3():
              raise FrameException("Invalid comment; no description/comment");
          else:
              self.description = u"";
              self.comment = u"";

   def render(self):
      data = self.encoding + self.lang.encode("ascii") +\
             self.description.encode(id3EncodingToString(self.encoding)) +\
             "\x00" +\
             self.comment.encode(id3EncodingToString(self.encoding));
      return self.assembleFrame(data);

   def __repr__(self):
      return "<%s (%s): %s [Lang: %s] [Desc: %s]>" %\
             (self.getFrameDesc(), self.header.id, self.comment,
              self.lang, self.description);

################################################################################
# This class refers to the APIC frame, otherwise known as an "attached
# picture".
class ImageFrame(Frame):
   encoding = DEFAULT_ENCODING;
   mimeType = None;
   pictureType = None;
   description = u"";
   # Contains the image data when the mimetype is image type.
   # Otherwise it is None.
   imageData = None;
   # Contains a URL for the image when the mimetype is "-->" per the spec.
   # Otherwise it is None.
   imageURL = None;
   # Declared "picture types".
   OTHER               = 0x00;
   ICON                = 0x01; # 32x32 png only.
   OTHER_ICON          = 0x02;
   FRONT_COVER         = 0x03;
   BACK_COVER          = 0x04;
   LEAFLET             = 0x05;
   MEDIA               = 0x06; # label side of cd, picture disc vinyl, etc.
   LEAD_ARTIST         = 0x07;
   ARTIST              = 0x08;
   CONDUCTOR           = 0x09;
   BAND                = 0x0A;
   COMPOSER            = 0x0B;
   LYRICIST            = 0x0C;
   RECORDING_LOCATION  = 0x0D;
   DURING_RECORDING    = 0x0E;
   DURING_PERFORMANCE  = 0x0F;
   VIDEO               = 0x10;
   BRIGHT_COLORED_FISH = 0x11; # There's always room for porno.
   ILLUSTRATION        = 0x12; 
   BAND_LOGO           = 0x13; 
   PUBLISHER_LOGO      = 0x14; 
   MIN_TYPE            = OTHER;
   MAX_TYPE            = PUBLISHER_LOGO;

   def __init__(self, data = None, frameHeader = None):
       if data:
           self.set(data, frameHeader);

   # Factory method
   def create(type, imgFile, desc = u""):
       if not isinstance(desc, unicode) or \
          not isinstance(type, int):
           raise FrameException("Wrong description and/or image-type type.");
       # Load img
       fp = file(imgFile, "rb");
       imgData = fp.read();
       mt = mimetypes.guess_type(imgFile);
       if not mt[0]:
           raise FrameException("Unable to guess mime-type for %s" % (imgFile));

       frameData = DEFAULT_ENCODING;
       frameData += mt[0] + "\x00";
       frameData += bin2bytes(dec2bin(type, 8));
       frameData += desc.encode(id3EncodingToString(DEFAULT_ENCODING)) + "\x00";
       frameData += imgData;

       return ImageFrame(frameData);
   # Make create a static method.  Odd....
   create = staticmethod(create);

   # Data string format:
   # <Header for 'Attached picture', ID: "APIC">
   #  Text encoding      $xx
   #  MIME type          <text string> $00
   #  Picture type       $xx
   #  Description        <text string according to encoding> $00 (00)
   #  Picture data       <binary data>
   def set(self, data, frameHeader = None):
      if frameHeader:
         if not IMAGE_FRAME_RX.match(frameHeader.id):
            raise FrameException("Invalid frame id for ImageFrame: " +\
                                 frameHeader.id);
      else:
         frameHeader = FrameHeader();
         frameHeader.id = IMAGE_FID;
      self.header = frameHeader;

      data = self.disassembleFrame(data);

      input = StringIO(data);
      TRACE_MSG("APIC frame data size: " + str(len(data)));
      self.encoding = input.read(1);
      TRACE_MSG("APIC encoding: " + id3EncodingToString(self.encoding));

      self.mimeType = "";
      ch = input.read(1);
      while ch != "\x00":
         self.mimeType += ch;
         ch = input.read(1);
      TRACE_MSG("APIC mime type: " + self.mimeType);
      if strictID3() and not self.mimeType:
         raise FrameException("APIC frame does not contain a mime type");
      if self.mimeType.find("/") == -1:
         self.mimeType = "image/" + self.mimeType;

      pt = ord(input.read(1));
      TRACE_MSG("Initial APIC picture type: " + str(pt));
      if pt < self.MIN_TYPE or pt > self.MAX_TYPE:
          if strictID3():
              raise FrameException("Invalid APIC picture type: %d" % (pt));
          # Rather than force this to UNKNOWN, let's assume that they put a
          # character literal instead of it's byte value.
          try:
              pt = int(chr(pt));
          except:
              pt = self.OTHER;
          if pt < self.MIN_TYPE or pt > self.MAX_TYPE:
              self.pictureType = self.OTHER;
      self.pictureType = pt;
      TRACE_MSG("APIC picture type: " + str(self.pictureType));

      self.desciption = u"";
      buffer = "";
      ch = input.read(1);
      while ch != "\x00":
         buffer += ch;
         ch = input.read(1);
      self.description = unicode(buffer, id3EncodingToString(self.encoding));
      TRACE_MSG("APIC description: " + self.description);

      if self.mimeType.find("-->") != -1:
         self.imageData = None;
         self.imageURL = input.read();
      else:
         self.imageData = input.read();
         self.imageURL = None;
      TRACE_MSG("APIC image data: " + str(len(self.imageData)) + " bytes");
      if strictID3() and not self.imageData and not self.imageURL:
         raise FrameException("APIC frame does not contain any image data");

      input.close();

   def writeFile(self, path = "./", name = None):
      if not self.imageData:
         raise IOError("Fetching remote image files is not implemented.");
      if not name:
         name = self.getDefaultFileName();
      imageFile = os.path.join(path, name);

      f = file(imageFile, "wb");
      f.write(self.imageData);
      f.flush();
      f.close();
   def getDefaultFileName(self):
      nameStr = self.picTypeToString(self.pictureType);
      nameStr = nameStr +  "." + self.mimeType.split("/")[1];
      return nameStr;

   def render(self):
      data = self.encoding + self.mimeType + "\x00" +\
             bin2bytes(dec2bin(self.pictureType, 8)) +\
             self.description.encode(id3EncodingToString(self.encoding)) +\
             "\x00";
      if self.imageURL:
          data += self.imageURL.encode("ascii");
      else:
          data += self.imageData;
      return self.assembleFrame(data);

   def stringToPicType(self, s):
       if s == "OTHER":
           return self.OTHER;
       elif s == "ICON":
           return self.ICON;
       elif s == "OTHER_ICON":
           return self.OTHER_ICON;
       elif s == "FRONT_COVER":
           return self.FRONT_COVER
       elif s == "BACK_COVER":
           return self.BACK_COVER;
       elif s == "LEAFLET":
           return self.LEAFLET;
       elif s == "MEDIA":
           return self.MEDIA;
       elif s == "LEAD_ARTIST":
           return self.LEAD_ARTIST;
       elif s == "ARTIST":
           return self.ARTIST;
       elif s == "CONDUCTOR":
           return self.CONDUCTOR;
       elif s == "BAND":
           return self.BAND;
       elif s == "COMPOSER":
           return self.COMPOSER;
       elif s == "LYRICIST":
           return self.LYRICIST;
       elif s == "RECORDING_LOCATION":
           return self.RECORDING_LOCATION;
       elif s == "DURING_RECORDING":
           return self.DURING_RECORDING;
       elif s == "DURING_PERFORMANCE":
           return self.DURING_PERFORMANCE;
       elif s == "VIDEO":
           return self.VIDEO;
       elif s == "BRIGHT_COLORED_FISH":
           return self.BRIGHT_COLORED_FISH;
       elif s == "ILLUSTRATION":
           return self.ILLUSTRATION;
       elif s == "BAND_LOGO":
           return self.BAND_LOGO;
       elif s == "PUBLISHER_LOGO":
           return self.PUBLISHER_LOGO;
       else:
         raise FrameException("Invalid APIC picture type: %s" % s);

   def picTypeToString(self, t):
      if t == self.OTHER:
         return "OTHER";
      elif t == self.ICON:
         return "ICON";
      elif t == self.OTHER_ICON:
         return "OTHER_ICON";
      elif t == self.FRONT_COVER:
         return "FRONT_COVER";
      elif t == self.BACK_COVER:
         return "BACK_COVER";
      elif t == self.LEAFLET:
         return "LEAFLET";
      elif t == self.MEDIA:
         return "MEDIA";
      elif t == self.LEAD_ARTIST:
         return "LEAD_ARTIST";
      elif t == self.ARTIST:
         return "ARTIST";
      elif t == self.CONDUCTOR:
         return "CONDUCTOR";
      elif t == self.BAND:
         return "BAND";
      elif t == self.COMPOSER:
         return "COMPOSER";
      elif t == self.LYRICIST:
         return "LYRICIST";
      elif t == self.RECORDING_LOCATION:
         return "RECORDING_LOCATION";
      elif t == self.DURING_RECORDING:
         return "DURING_RECORDING";
      elif t == self.DURING_PERFORMANCE:
         return "DURING_PERFORMANCE";
      elif t == self.VIDEO:
         return "VIDEO";
      elif t == self.BRIGHT_COLORED_FISH:
         return "BRIGHT_COLORED_FISH";
      elif t == self.ILLUSTRATION:
         return "ILLUSTRATION";
      elif t == self.BAND_LOGO:
         return "BAND_LOGO";
      elif t == self.PUBLISHER_LOGO:
         return "PUBLISHER_LOGO";
      else:
         raise FrameException("Invalid APIC picture type: %d" % t);

################################################################################
class UnknownFrame(Frame):
   data = "";

   def __init__(self, data, frameHeader):
      self.set(data, frameHeader);

   def set(self, data, frameHeader):
      self.header = frameHeader;
      data = self.disassembleFrame(data);
      self.data = data;

   def render(self):
      return self.assembleFrame(self.data)

################################################################################
class MusicCDIdFrame(Frame):
   toc = "";

   def __init__(self, data, frameHeader = None):
      self.set(data, frameHeader);

   # TODO: Parse the TOC and comment the format.
   def set(self, data, frameHeader = None):
      if frameHeader:
         if not CDID_FRAME_RX.match(frameHeader.id):
            raise FrameException("Invalid frame id for MusicCDIdFrame: " +\
                                 frameHeader.id);
      else:
         frameHeader = FrameHeader();
         frameHeader.id = CDID_FID;
      self.header = frameHeader;

      data = self.disassembleFrame(data);
      self.toc = data;

   def render(self):
      data = self.toc;
      return self.assembleFrame(data);

################################################################################
# A class for containing and managing ID3v2.Frame objects.
class FrameSet(list):
   tagHeader = None;

   def __init__(self, tagHeader, l = None):
      self.tagHeader = tagHeader;
      if l:
         for f in l:
            if not isinstance(f, Frame):
               raise TypeError("Invalid type added to FrameSet: " +\
                               f.__class__);
            self.append(f);

   # Setting a FrameSet instance like this 'fs = []' morphs the instance into
   # a list object.
   def clear(self):
      del self[0:];

   # Read frames starting from the current read position of the file object.
   # Returns the amount of padding which occurs after the tag, but before the
   # audio content.  A return valule of 0 DOES NOT imply an error.
   def parse(self, f, tagHeader):
      self.tagHeader = tagHeader;
      paddingSize = 0;
      sizeLeft = tagHeader.tagSize;

      # Handle a tag-level unsync.  Some frames may have their own unsync bit
      # set instead.
      tagData = f.read(sizeLeft);
      if tagHeader.unsync:
         TRACE_MSG("Tag has unsync bit set");
         tagData = deunsyncData(tagData);
         sizeLeft = len(tagData);
      # Adding 10 to simulate the tag header in the buffer.  This keeps 
      # f.tell() values the same as in the file.
      tagBuffer = StringIO((10 * '\x00') + tagData);
      tagBuffer.seek(10);
      tagBuffer.tell();

      while sizeLeft > 0:
         TRACE_MSG("sizeLeft: " + str(sizeLeft));
         if sizeLeft < (10 + 1):
            TRACE_MSG("FrameSet: Implied padding (sizeLeft < minFrameSize)");
            paddingSize = sizeLeft;
            break;

         TRACE_MSG("+++++++++++++++++++++++++++++++++++++++++++++++++");
         TRACE_MSG("FrameSet: Reading Frame #" + str(len(self) + 1));
         frameHeader = FrameHeader(tagHeader);
         if not frameHeader.parse(tagBuffer):
            paddingSize = sizeLeft;
            break;

         # Frame data.
         TRACE_MSG("FrameSet: Reading %d (0x%X) bytes of data from byte "\
                   "pos %d (0x%X)" % (frameHeader.dataSize,
                                      frameHeader.dataSize, tagBuffer.tell(),
                                      tagBuffer.tell()));
         data = tagBuffer.read(frameHeader.dataSize);
         TRACE_MSG("FrameSet: %d bytes of data read" % len(data));

         self.addFrame(createFrame(frameHeader, data));

         # Each frame contains dataSize + headerSize(10) bytes.
         sizeLeft -= (frameHeader.FRAME_HEADER_SIZE + frameHeader.dataSize);

      return paddingSize;

   # Returrns the size of the frame data.
   def getSize(self):
      sz = 0;
      for f in self:
         sz += len(f.render());
      return sz;
   
   def setTagHeader(self, tagHeader):
      self.tagHeader = tagHeader;
      for f in self:
         f.header.setVersion(tagHeader);

   # This methods adds the frame if it is addable per the ID3 spec.
   def addFrame(self, frame):
      fid = frame.header.id;

      # Text frame restrictions.
      # No multiples except for TXXX which must have unique descriptions.
      if strictID3() and TEXT_FRAME_RX.match(fid) and self[fid]:
         if not USERTEXT_FRAME_RX.match(fid):
            raise FrameException("Multiple %s frames now allowed." % fid);
         userTextFrames = self[fid];
         for frm in userTextFrames:
            if frm.description == frame.description:
               raise FrameException("Multiple %s frames with the same\
                                     description now allowed." % fid);

      # Comment frame restrictions.
      # Multiples must have a unique description/language combination.
      if strictID3() and COMMENT_FRAME_RX.match(fid) and self[fid]:
         commentFrames = self[fid];
         for frm in commentFrames:
            if frm.description == frame.description and\
               frm.lang == frame.lang:
               raise FrameException("Multiple %s frames with the same\
                                     language and description now allowed." %\
                                     fid);

      # URL frame restrictions.
      # No multiples except for TXXX which must have unique descriptions.
      if strictID3() and URL_FRAME_RX.match(fid) and self[fid]:
         if not USERURL_FRAME_RX.match(fid):
            raise FrameException("Multiple %s frames now allowed." % fid);
         userUrlFrames = self[fid];
         for frm in userUrlFrames:
            if frm.description == frame.description:
               raise FrameException("Multiple %s frames with the same\
                                     description now allowed." % fid);

      # Music CD ID restrictions.
      # No multiples.
      if strictID3() and CDID_FRAME_RX.match(fid) and self[fid]:
         raise FrameException("Multiple %s frames now allowed." % fid);

      # Image (attached picture) frame restrictions.
      # Multiples must have a unique content desciptor.  I'm assuming that
      # the spec means the picture type.....
      if IMAGE_FRAME_RX.match(fid) and self[fid]:
         imageFrames = self[fid];
         for frm in imageFrames:
            if frm.pictureType == frame.pictureType:
               raise FrameException("Multiple %s frames with the same\
                                     content descriptor now allowed." % fid);
      self.append(frame);

   # Set a text frame value.  Text frame IDs must be unique.  If a frame with
   # the same Id is already in the list it's value is changed, otherwise
   # the frame is added.
   def setTextFrame(self, frameId, text, encoding = DEFAULT_ENCODING):
      if not TEXT_FRAME_RX.match(frameId):
         raise FrameException("Invalid Frame ID: " + frameId);
      if USERTEXT_FRAME_RX.match(frameId):
         raise FrameException("Wrong method, use setUserTextFrame");

      if self[frameId]:
          curr = self[frameId][0];
          curr.encoding = encoding;
          if isinstance(curr, DateFrame):
              curr.setDate(text);
          else:
              curr.text = text;
      else:
          h = FrameHeader(self.tagHeader);
          h.id = frameId;
          self.addFrame(createFrame(h, encoding + text));

   # If a comment frame with the same language and description exists then
   # the comment text is replaced, otherwise the frame is added.
   def setCommentFrame(self, comment, description, lang = DEFAULT_LANG,
                       encoding = DEFAULT_ENCODING):

      if self[COMMENT_FID]:
         found = 0;
         for f in self[COMMENT_FID]:
            if f.lang == lang and f.description == description:
               f.comment = comment;
               f.encoding = encoding;
               found = 1;
               break;
         if not found:
            h = FrameHeader(self.tagHeader);
            h.id = COMMENT_FID;
            self.addFrame(CommentFrame(encoding + lang + description + "\x00" +
                                       comment, h));
      else:
         h = FrameHeader(self.tagHeader);
         h.id = COMMENT_FID;
         self.addFrame(CommentFrame(encoding + lang + description + "\x00" +
                                    comment, h));
         
   # This method removes all frames with the matching frame ID.
   # The number of frames removed is returned.
   # Note that calling this method with a key like "COMM" may remove more
   # frames then you really want.
   def removeFramesByID(self, fid):
      if not isinstance(fid, str):
         raise FrameException("removeFramesByID only operates on frame IDs");

      i = 0;
      count = 0;
      while i < len(self):
         if self[i].header.id == fid:
            del self[i];
            count += 1;
         else:
            i += 1;
      return count;

   # Removes the frame at index.  True is returned if the element was
   # removed, and false otherwise.
   def removeFrameByIndex(self, index):
      if not isinstance(index, int):
         raise\
           FrameException("removeFrameByIndex only operates on a frame index");
      try:
         del self.frames[key];
         return 1;
      except:
         return 0;

   # Accepts both int (indexed access) and string keys (a valid frame Id).
   # A list of frames (commonly with only one element) is returned when the
   # FrameSet is accessed using frame IDs since some frames can appear
   # multiple times in a tag.  To sum it all up htis method returns
   # string or None when indexed using an integer, and a 0 to N length
   # list of strings when indexed with a frame ID.
   #
   # Throws IndexError and TypeError.
   def __getitem__(self, key):
      if isinstance(key, int):
         if key >= 0 and key < len(self):
            return list.__getitem__(self, key);
         else:
            raise IndexError("FrameSet index out of range");
      elif isinstance(key, str):
         retList = list();
         for f in self:
            if f.header.id == key:
               retList.append(f);
         return retList;
      else:
         raise TypeError("FrameSet key must be type int or string");

#  Mmmmm!  Cheesy!
def splitUnicode(data, encoding):
    if encoding == LATIN1_ENCODING or encoding == UTF_8_ENCODING or\
       encoding == UTF_16BE_ENCODING:
        return data.split("\x00", 1);
    elif encoding == UTF_16_ENCODING:
        (d, t) = data.split("\x00\x00\x00", 1);
        d += "\x00";
        t += "\x00";
        return (d, t);


#######################################################################
# Create and return the appropriate frame.
# Exceptions: ....
def createFrame(frameHeader, data):
  f = None;

  # Text Frames
  if TEXT_FRAME_RX.match(frameHeader.id):
     if USERTEXT_FRAME_RX.match(frameHeader.id):
        f = UserTextFrame(data, frameHeader);
     else:
        if frameHeader.id[:2] == "TD" or\
           frameHeader.id == OBSOLETE_DATE_FID or\
           frameHeader.id == OBSOLETE_YEAR_FID or \
           frameHeader.id == OBSOLETE_ORIG_RELEASE_FID:
           f = DateFrame(data, frameHeader);
        else:
           f = TextFrame(data, frameHeader);

  # Comment Frames.
  elif COMMENT_FRAME_RX.match(frameHeader.id):
     f = CommentFrame(data, frameHeader);

  # URL Frames.
  elif URL_FRAME_RX.match(frameHeader.id):
     if USERURL_FRAME_RX.match(frameHeader.id):
        f = UserURLFrame(data, frameHeader);
     else:
        f = URLFrame(data, frameHeader);

  # CD Id frame.
  elif CDID_FRAME_RX.match(frameHeader.id):
     f = MusicCDIdFrame(data, frameHeader);

  # Attached picture
  elif IMAGE_FRAME_RX.match(frameHeader.id):
     f = ImageFrame(data, frameHeader);

  if f == None:
     f = UnknownFrame(data, frameHeader);

  return f;
