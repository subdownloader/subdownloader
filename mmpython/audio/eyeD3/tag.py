################################################################################
#
#  Copyright (C) 2002-2004  Travis Shirk <travis@pobox.com>
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
import re, os, string, stat, shutil, tempfile, binascii;
import mimetypes;
from stat import *;
from mmpython.audio.eyeD3 import *;

import utils as utils
import mp3 as eyeD3_mp3

from frames import *;
from binfuncs import *;


ID3_V1_COMMENT_DESC = "ID3 v1 Comment";

################################################################################
class TagException:
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;

################################################################################
class TagHeader:
   SIZE = 10;

   version = None;
   majorVersion = None;
   minorVersion = None;
   revVersion = None;

   # Flag bits
   unsync = 0;
   extended = 0;
   experimental = 0;
   # v2.4 addition
   footer = 0;

   # The size in the most recently parsed header.
   tagSize = 0;
   
   # Constructor
   def __init__(self):
      self.clear();

   def clear(self):
      self.setVersion(None);
      self.unsync = 0;
      self.extended = 0;
      self.experimental = 0;
      self.tagSize = 0;

   def setVersion(self, v):
      if v == None:
         self.version = None;
         self.majorVersion = None;
         self.minorVersion = None;
         self.revVersion = None;
         return;

      if v == ID3_CURRENT_VERSION:
         if self.majorVersion == None or self.minorVersion == None:
            v = ID3_DEFAULT_VERSION;
         else:
            return;
      elif v == ID3_ANY_VERSION:
         v = ID3_DEFAULT_VERSION;

      # Handle 3-element lists or tuples.
      if isinstance(v, tuple) or isinstance(v, list):
         self.version = utils.versionsToConstant(v);
         (self.majorVersion,
          self.minorVersion,
          self.revVersion) = v;
      # Handle int constants.
      elif isinstance(v, int):
         (self.majorVersion,
          self.minorVersion,
          self.revVersion) = utils.constantToVersions(v);
         self.version = v;
      else:
         raise TypeError("Wrong type: %s" % str(type(v)));

   # Given a file handle this method attempts to identify and then parse
   # a ID3 v2 header.  If successful, the parsed values are stored in
   # the instance variable.  If the files does not contain an ID3v2 tag
   # false is returned. A TagException is thrown if a tag is found, but is
   # not valid or corrupt.
   def parse(self, f):
      self.clear();

      # The first three bytes of a v2 header is "ID3".
      if f.read(3) != "ID3":
         return 0;
      TRACE_MSG("Located ID3 v2 tag");

      # The next 2 bytes are the minor and revision versions.
      version = f.read(2);
      major = 2;
      minor = ord(version[0]);
      rev = ord(version[1]);
      TRACE_MSG("TagHeader [major]: " + str(major));
      TRACE_MSG("TagHeader [minor]: " + str(minor));
      TRACE_MSG("TagHeader [revis]: " + str(rev));
      if not (major == 2 and (minor == 3 or minor == 4)):
         raise TagException("ID3 v" + str(major) + "." + str(minor) +\
                            " is not supported.");
      # Get all the version madness in sync.
      self.setVersion([major, minor, rev]);

      # The first 4 bits of the next byte are flags.
      (self.unsync,
       self.extended,
       self.experimental,
       self.footer) = bytes2bin(f.read(1))[0:4];
      TRACE_MSG("TagHeader [flags]: unsync(%d) extended(%d) "\
                "experimental(%d) footer(%d)" % (self.unsync, self.extended,
                                                 self.experimental,
                                                 self.footer));

      # The size of the optional extended header, frames, and padding
      # afer unsynchronization.  This is a sync safe integer, so only the
      # bottom 7 bits of each byte are used.
      tagSizeStr = f.read(4);
      TRACE_MSG("TagHeader [size string]: 0x%02x%02x%02x%02x" %\
                (ord(tagSizeStr[0]), ord(tagSizeStr[1]),
                 ord(tagSizeStr[2]), ord(tagSizeStr[3])));
      self.tagSize = bin2dec(bytes2bin(tagSizeStr, 7));
      TRACE_MSG("TagHeader [size]: %d (0x%x)" % (self.tagSize, self.tagSize));

      return 1;

   def render(self, tagLen = None):
      if tagLen != None:
         self.tagSize = tagLen;

      data = "ID3";
      data += chr(self.minorVersion) + chr(self.revVersion);
      # not not the values so we only get 1's and 0's.
      data += bin2bytes([not not self.unsync,
                         not not self.extended,
                         not not self.experimental,
                         not not self.footer,
                         0, 0, 0, 0]);
      TRACE_MSG("Setting tag size to %d" % tagLen);
      szBytes = bin2bytes(bin2synchsafe(dec2bin(tagLen, 32)));
      data += szBytes;
      TRACE_MSG("TagHeader Rendered");
      return data;

################################################################################
class ExtendedTagHeader:
   size = 0;
   flags = 0;
   crc = 0;
   restrictions = 0;

   def isUpdate(self):
      return self.flags & 0x40;
   def hasCRC(self):
      return self.flags & 0x20;
   def hasRestrictions(self):
      return self.flags & 0x10;

   def setSizeRestrictions(self, v):
      assert(v >= 0 and v <= 3);
      self.restrictions = (v << 6) | (self.restrictions & 0x3f);
   def getSizeRestrictions(self):
      return self.restrictions >> 6;
   def getSizeRestrictionsString(self):
      val = self.getSizeRestrictions();
      if val == 0x00:
         return "No more than 128 frames and 1 MB total tag size.";
      elif val == 0x01:
         return "No more than 64 frames and 128 KB total tag size.";
      elif val == 0x02:
         return "No more than 32 frames and 40 KB total tag size.";
      elif val == 0x03:
         return "No more than 32 frames and 4 KB total tag size.";

   def setTextEncodingRestrictions(self, v):
      assert(v == 0 or v == 1);
      self.restrictions ^= 0x20;
   def getTextEncodingRestrictions(self):
      return self.restrictions & 0x20;
   def getTextEncodingRestrictionsString(self):
      if self.getTextEncodingRestrictions():
         return "Strings are only encoded with ISO-8859-1 [ISO-8859-1] or "\
                "UTF-8 [UTF-8].";
      else:
         return "None";

   def setTextFieldSizeRestrictions(self, v):
      assert(v >= 0 and v <= 3);
      self.restrictions = (v << 3) | (self.restrictions & 0xe7);
   def getTextFieldSizeRestrictions(self):
      return (self.restrictions >> 3) & 0x03;
   def getTextFieldSizeRestrictionsString(self):
      val = self.getTextFieldSizeRestrictions();
      if val == 0x00:
         return "None";
      elif val == 0x01:
         return "No string is longer than 1024 characters.";
      elif val == 0x02:
         return "No string is longer than 128 characters.";
      elif val == 0x03:
         return "No string is longer than 30 characters.";

   def setImageEncodingRestrictions(self, v):
      assert(v == 0 or v == 1);
      self.restrictions ^= 0x04;
   def getImageEncodingRestrictions(self):
      return self.restrictions & 0x04;
   def getImageEncodingRestrictionsString(self):
      if self.getImageEncodingRestrictions():
         return "Images are encoded only with PNG [PNG] or JPEG [JFIF].";
      else:
         return "None";

   def setImageSizeRestrictions(self, v):
      assert(v >= 0 and v <= 3);
      self.restrictions = v | (self.restrictions & 0xfc);
   def getImageSizeRestrictions(self):
      return self.restrictions & 0x03;
   def getImageSizeRestrictionsString(self):
      val = self.getImageSizeRestrictions();
      if val == 0x00:
         return "None";
      elif val == 0x01:
         return "All images are 256x256 pixels or smaller.";
      elif val == 0x02:
         return "All images are 64x64 pixels or smaller.";
      elif val == 0x03:
         return "All images are exactly 64x64 pixels, unless required "\
                "otherwise.";

   def render(self, header, frameData, padding = 0):
      assert(header.majorVersion == 2);

      data = "";
      if header.minorVersion == 4:
         # Version 2.4
         crc = None;
         size = 6;
         # Extended flags.
         if self.isUpdate():
            data = "\x00";
         if self.hasCRC():
            data += "\x05";
            self.crc = binascii.crc32(data);
            data += bin2bytes(dec2bin(self.crc, 40));
         if self.hasRestrictions():
            data += "\x01";
            assert(len(self.restrictions) == 1);
            data += self.restrictions;

         # Extended header size.
         size = bin2bytes(bin2synchsafe(dec2bin(len(data) + 6, 32)))
         assert(len(size) == 4);

         assert(len(self.flags) == 2);
         data = size + "\x01" + self.flags + data;
      else:
         # Version 2.3
         crc = None;
         size = 6;
         # Extended flags.
         f = [0] * 16;
         if self.hasCRC():
            f[0] = 1;
            self.crc = binascii.crc32(data);
            crc = bin2bytes(dec2bin(self.crc));
            assert(len(crc) == 4);
            size += 4;
         flags = bin2bytes(f);
         assert(len(flags) == 2);
         # Extended header size.
         size = bin2bytes(dec2bin(size, 32))
         assert(len(size) == 4);
         # Padding size
         paddingSize = bin2bytes(dec2bin(padding, 32));

         data = size + flags + paddingSize;
         if crc:
            data += crc;
      return data; 

   # Only call this when you *know* there is an extened header.
   def parse(self, fp, header):
      assert(header.majorVersion == 2);

      # First 4 bytes is the size of the extended header.
      data = fp.read(4);
      if header.minorVersion == 4:
         TRACE_MSG("Parsing extended header for v2.4");
         # sync-safe
         sz = bin2dec(bytes2bin(data, 7));
         TRACE_MSG("Extended header size: %d" % (sz - 4));
         data = fp.read(sz - 4);

         if ord(data[0]) != 1 or (ord(data[1]) & 0x8f):
            # As of 2.4 the first byte is 1 and the second can only have
            # bits 6, 5, and 4 set.
            raise TagException("Invalid Extended Header");

         offset = 2;
         self.flags = ord(data[1]);
         TRACE_MSG("Extended header flags: %x" % self.flags);

         if self.isUpdate():
            TRACE_MSG("Extended header has update bit set");
            assert(ord(data[offset]) == 0);
            offset += 1;
         if self.hasCRC():
            TRACE_MSG("Extended header has CRC bit set");
            assert(ord(data[offset]) == 5);
            offset += 1;
            crcData = data[offset:offset + 5];
            # This is sync-safe.
            self.crc = bin2dec(bytes2bin(crcData, 7));
            TRACE_MSG("Extended header CRC: %d" % self.crc);
            offset += 5;
         if self.hasRestrictions():
            TRACE_MSG("Extended header has restrictions bit set");
            assert(ord(data[offset]) == 5);
            offset += 1;
            self.restrictions = ord(data[offset]);
            offset += 1;
      else:
         TRACE_MSG("Parsing extended header for v2.3");
         # v2.3 is totally different... *sigh*
         sz = bin2dec(bytes2bin(data));
         TRACE_MSG("Extended header size: %d" % sz);
         data = fp.read(sz);
         tmpFlags = fp.read(2);
         # Make this look like a v2.4 mask.
         self.flags = ord(tmpFlags[0]) >> 2;
         if self.hasCRC():
            TRACE_MSG("Extended header has CRC bit set");
            crcData = fp.read(4);
            self.crc = bin2dec(bytes2bin(crcData));
            TRACE_MSG("Extended header CRC: %d" % self.crc);
         # Read the padding size, but it'll be computed during the parse.
         fp.read(4);


################################################################################
# ID3 tag class.  The class is capable of reading v1 and v2 tags.  ID3 v1.x
# are converted to v2 frames.
class Tag:
   # Latin1 is the default (0x00)
   encoding = DEFAULT_ENCODING;

   # ID3v1 tags do not contain a header.  The only ID3v1 values stored
   # in this header are the major/minor version.
   header = TagHeader();

   # Optional in v2 tags.
   extendedHeader = ExtendedTagHeader();

   # Contains the tag's frames.  ID3v1 fields are read and converted
   # the the corresponding v2 frame.  
   frames = None;

   # Used internally for iterating over frames.
   iterIndex = None;

   # If this value is None the tag is not linked to any particular file..
   linkedFile = None;

   # Constructor.  An empty tag is created and the link method is used
   # to read an mp3 file's v1.x or v2.x tag.  You can optionally set a 
   # file name, but it will not be read, but may be written to.
   def __init__(self, fileName = None):
      if fileName:
         self.linkedFile = LinkedFile(fileName);
      self.clear();

   def clear(self):
      self.header = TagHeader();
      self.frames = FrameSet(self.header);
      self.iterIndex = None;
      linkedFile = None;

   # Returns an read-only iterator for all frames.
   def __iter__(self):
      if len(self.frames):
         self.iterIndex = 0;
      else:
         self.iterIndex = None;
      return self;

   def next(self):
      if self.iterIndex == None or self.iterIndex == len(self.frames):
         raise StopIteration;
      frm = self.frames[self.iterIndex];
      self.iterIndex += 1;
      return frm;

   # Returns true when an ID3 tag is read from f which may be a file name
   # or an aleady opened file object.  In the latter case, the file object 
   # is not closed when this method returns.
   #
   # By default, both ID3 v2 and v1 tags are parsed in that order.
   # If a v2 tag is found then a v1 parse is not performed.  This behavior
   # can be refined by passing ID3_V1 or ID3_V2 as the second argument 
   # instead of the default ID3_ANY_VERSION.
   #
   # Converts all ID3v1 data into ID3v2 frames internally.
   # May throw IOError, or TagException if parsing fails.
   def link(self, f, v = ID3_ANY_VERSION):
      self.clear();

      fileName = "";
      if isinstance(f, file):
         fileName = f.name;
      elif isinstance(f, str):
         fileName = f;
      else:
         raise TagException("Invalid type passed to Tag.link: " + 
                            str(type(f)));

      if v != ID3_V1 and v != ID3_V2 and v != ID3_ANY_VERSION:
         raise TagException("Invalid version: " + hex(v));

      tagFound = 0;
      padding = 0;
      TRACE_MSG("Linking File: " + fileName);
      if v == ID3_V1:
         if self.__loadV1Tag(f):
            tagFound = 1;
      elif v == ID3_V2:
         padding = self.__loadV2Tag(f);
         if padding >= 0:
            tagFound = 1;
      elif v == ID3_ANY_VERSION:
         padding = self.__loadV2Tag(f);
         if padding >= 0:
            tagFound = 1;
         else:
            padding = 0;
            if self.__loadV1Tag(f):
               tagFound = 1;

      self.linkedFile = LinkedFile(fileName);
      if tagFound:
         # In the case of a v1.x tag this is zero.
         self.linkedFile.tagSize = self.header.tagSize;
         self.linkedFile.tagPadding = padding;
         return 1;
      else:
         self.linkedFile.tagSize = 0;
         self.linkedFile.tagPadding = 0;
         return 0;

   # Write the current tag state to the linked file.
   # The version of the ID3 file format that should be written can
   # be passed as an argument; the default is ID3_CURRENT_VERSION.
   def update(self, version = ID3_CURRENT_VERSION, backup = 0):
      if not self.linkedFile:
         raise TagException("The Tag is not linked to a file.");

      if backup:
         shutil.copyfile(self.linkedFile.name, self.linkedFile.name + ".orig");

      self.setVersion(version);
      version = self.getVersion();
      # If v1.0 is being for explicitly then so be it, if not and there is
      # a track number then bumping to v1.1 is /probably/ best.
      if self.header.majorVersion == 1 and self.header.minorVersion == 0 and\
         self.getTrackNum()[0] != None and version != ID3_V1_0:
         version = ID3_V1_1;
         self.setVersion(version);
      
      # If there are no frames then simply remove the current tag.
      if len(self.frames) == 0:
         self.remove(version);
         self.header = TagHeader();
         self.frames.setTagHeader(self.header);
         self.linkedFile.tagPadding = 0;
         self.linkedFile.tagSize = 0;
         return;

      if version & ID3_V1:
         self.__saveV1Tag(version);
         return 1;
      elif version & ID3_V2:
         self.__saveV2Tag(version);
         return 1;
      else:
         raise TagException("Invalid version: %s" % hex(version));
      return 0;

   # Remove the tag.  The version argument can selectively remove specific
   # ID3 tag versions; the default is ID3_CURRENT_VERSION meaning the version
   # of the current tag.  A value of ID3_ANY_VERSION causes all tags to be
   # removed.
   def remove(self, version = ID3_CURRENT_VERSION):
      if not self.linkedFile:
         raise TagException("The Tag is not linked to a file; nothing to "\
                            "remove.");

      if version == ID3_CURRENT_VERSION:
         version = self.getVersion();

      retval = 0;   
      if version & ID3_V1 or version == ID3_ANY_VERSION:
         tagFile = file(self.linkedFile.name, "r+b");
         tagFile.seek(-128, 2);
         if tagFile.read(3) == "TAG":
            TRACE_MSG("Removing ID3 v1.x Tag");
            tagFile.seek(-3, 1);
            tagFile.truncate();
            retval |= 1;
         tagFile.close();

      if ((version & ID3_V2) or (version == ID3_ANY_VERSION)) and\
          self.header.tagSize:
         tagFile = file(self.linkedFile.name, "r+b");
         if tagFile.read(3) == "ID3":
            TRACE_MSG("Removing ID3 v2.x Tag");
            tagSize = self.header.tagSize + self.header.SIZE;
            tagFile.seek(tagSize);
            data = tagFile.read();
            tagFile.seek(0);
            tagFile.write(data);
            tagFile.truncate();
            tagFile.close();
            retval |= 1;

      return retval;



   # Get artist.  There are a few frames that can contain this information,
   # and they are subtley different. 
   #   eyeD3.frames.ARTIST_FID - Lead performer(s)/Soloist(s)
   #   eyeD3.frames.BAND_FID - Band/orchestra/accompaniment
   #   eyeD3.frames.CONDUCTOR_FID - Conductor/performer refinement
   #   eyeD3.frames.REMIXER_FID - Interpreted, remixed, or otherwise modified by
   #
   # Any of these values can be passed as an argument to select the artist
   # of interest.  By default, the first one found (searched in the above order)
   # is the value returned.  Most tags only have the ARTIST_FID, btw.
   # 
   # When no artist is found, an empty string is returned.
   # 
   def getArtist(self, artistID = ARTIST_FIDS):
      if isinstance(artistID, list):
         frameIDs = artistID;
      else:
         frameIDs = [artistID];

      for fid in frameIDs:
         f = self.frames[fid];
         if f:
            return f[0].text;
      return ""; 
 
   def getAlbum(self):
      f = self.frames[ALBUM_FID];
      if f:
         return f[0].text;
      else:
         return "";

   # Get the track title.  By default the main title is returned.  Optionally,
   # you can pass:
   #   eyeD3.frames.TITLE_FID - The title; the default.
   #   eyeD3.frames.SUBTITLE_FID - The subtitle.
   #   eyeD3.frames.CONTENT_TITLE_FID - Conten group description???? Rare.
   # An empty string is returned when no title exists.
   def getTitle(self, titleID = TITLE_FID):
      f = self.frames[titleID];
      if f:
         return f[0].text;
      else:
         return "";

   def getDate(self, fid = None):
       if not fid:
           for fid in ["TDRL", "TDOR", "TDRC",
                       OBSOLETE_YEAR_FID, OBSOLETE_DATE_FID]:
               if self.frames[fid]:
                   return self.frames[fid];
           return None;
       return self.frames[fid];

   def getYear(self, fid = None):
       dateFrame = self.getDate(fid);
       if dateFrame:
           return dateFrame[0].getYear();
       else:
           return None;
            
   # Throws GenreException when the tag contains an unrecognized genre format.
   # Note this method returns a eyeD3.Genre object, not a raw string.
   def getGenre(self):
      f = self.frames[GENRE_FID];
      if f and f[0].text:
         g = Genre();
         g.parse(f[0].text);
         return g;
      else:
         return None;

   # Returns a tuple with the first value containing the track number and the
   # second the total number of tracks.  One or both of these values may be
   # None depending on what is available in the tag. 
   def getTrackNum(self):
      f = self.frames[TRACKNUM_FID];
      if f:
         n = string.split(f[0].text, '/');
         tn = self.toInt(n[0]);
         tt = None;
         if len(n) == 2:
            tt = self.toInt(n[1]);
         if tn != None and tt != None:
            return (tn, tt);
         elif tn != None:
            return (tn, None);
      return (None, None);

   # Since multiple comment frames are allowed this returns a list with 0
   # or more elements.  The elements are not the comment strings, they are
   # eyeD3.frames.CommentFrame objects.
   def getComments(self):
      return self.frames[COMMENT_FID];

   # Returns a list (possibly empty) of eyeD3.frames.ImageFrame objects.
   def getImages(self):
      return self.frames[IMAGE_FID];

   # Returns a list (possibly empty) of eyeD3.frames.URLFrame objects.
   # Both URLFrame and UserURLFrame objects are returned.  UserURLFrames
   # add a description and encoding, and have a different frame ID.
   def getURLs(self):
      urls = list();
      for fid in URL_FIDS:
         urls.extend(self.frames[fid]);
      urls.extend(self.frames[USERURL_FID]);
      return urls;

   def getUserTextFrames(self):
      return self.frames[USERTEXT_FID];

   def getCDID(self):
      return self.frames[CDID_FID];

   def getVersion(self):
      return self.header.version;

   def getVersionStr(self):
      return versionToString(self.header.version);

   # Set the artist name.  Arguments equal to None or "" cause the frame to
   # be removed. An optional second argument can be passed to select the
   # actual artist frame that should be set.  By default, the main artist frame
   # (TPE1) is the value used.
   def setArtist(self, a, id = ARTIST_FID):
       self.setTextFrame(id, a);

   def setAlbum(self, a):
       self.setTextFrame(ALBUM_FID, a);

   def setTitle(self, t, titleID = TITLE_FID):
       self.setTextFrame(titleID, t);

   def setDate(self, year, month = None, dayOfMonth = None,
               hour = None, minute = None, second = None, fid = None):
      if not year and not fid:
          dateFrame = self.getDate;
          self.frames.removeFramesByID(dateFrame.id);
          return;
      elif not year:
          self.frames.removeFramesByID(fid);

      dateStr = str(year);
      if len(dateStr) != 4:
         raise TagException("Invalid Year field: " + dateStr);
      if month:
         dateStr += "-" + self.__padDateField(month);
         if dayOfMonth:
            dateStr += "-" + self.__padDateField(dayOfMonth);
            if hour:
               dateStr += "T" + self.__padDateField(hour);
               if minute:
                  dateStr += ":" + self.__padDateField(minute);
                  if second:
                     dateStr += ":" + self.__padDateField(second);

      if not fid:
          fid = "TDRL";
      dateFrame = self.frames[fid];
      try:
         if dateFrame:
            dateFrame[0].setDate(self.encoding + dateStr);
         else:
            header = FrameHeader(self.header);
            header.id = fid;
            dateFrame = DateFrame(self.encoding + dateStr, header);
            self.frames.addFrame(dateFrame);
      except FrameException, ex:
         raise TagException(str(ex));

   # Three types are accepted for the genre parameter.  A Genre object, an
   # acceptable (see Genre.parse) genre string, or an integer genre id.
   # Arguments equal to None or "" cause the frame to be removed.
   def setGenre(self, g):
      if g == None or g == "":
         self.frames.removeFramesByID(GENRE_FID);
         return;

      if isinstance(g, Genre):
         self.frames.setTextFrame(GENRE_FID, str(g), self.encoding);
      elif isinstance(g, str):
         gObj = Genre();
         gObj.parse(g);
         self.frames.setTextFrame(GENRE_FID, str(gObj), self.encoding);
      elif isinstance(g, int):
         gObj = Genre();
         gObj.id = g;
         self.frames.setTextFrame(GENRE_FID, str(gObj), self.encoding);
      else:
         raise TagException("Invalid type passed to setGenre: %s" +
                            str(type(g)));

   # Accepts a tuple with the first value containing the track number and the
   # second the total number of tracks.  One or both of these values may be
   # None.  If both values are None, the frame is removed.
   def setTrackNum(self, n):
      if n[0] == None and n[1] == None:
         self.frames.removeFramesByID(TRACKNUM_FID);
         return;

      totalStr = "";
      zPadding = 1;
      if n[1] != None:
         if n[1] >= 0 and n[1] <= 9:
            totalStr = "0" + str(n[1]);
         else:
            totalStr = str(n[1]);
         zPadding = len(totalStr) - 1;

      t = n[0];
      if t == None:
         t = 0;

      # Pad with zeros according to how large the total count is.
      trackStr = str(t);
      if len(trackStr) == 1:
         trackStr = "0" + trackStr;
      if len(trackStr) < len(totalStr):
         trackStr = ("0" * (len(totalStr) - len(trackStr))) + trackStr;

      s = "";
      if trackStr and totalStr:
         s = trackStr + "/" + totalStr;
      elif trackStr and not totalStr:
         s = trackStr;

      self.frames.setTextFrame(TRACKNUM_FID, s, self.encoding);

   # Add a comment.  This adds a comment unless one is already present with
   # the same language and description in which case the current value is
   # either changed (cmt evalues true) or removed (cmt equals "" or None).
   def addComment(self, cmt, desc = "", lang = DEFAULT_LANG):
      if not cmt:
         # A little more then a call to removeFramesByID is involved since we
         # need to look at more than the frame ID.
         comments = self.frames[COMMENT_FID];
         for c in comments:
            if c.lang == lang and c.description == desc:
               self.frames.remove(c);
               break;
      else:
         self.frames.setCommentFrame(cmt, desc, lang, self.encoding);

   def removeComments(self):
       return self.frames.removeFramesByID(COMMENT_FID);

   def addImage(self, type, image_file_path, desc = u""):
       image_frame = ImageFrame.create(type, image_file_path, desc);
       self.frames.addFrame(image_frame);

   # Test ID3 major version.
   def isV1(self):
      return self.header.majorVersion == 1;
   def isV2(self):
      return self.header.majorVersion == 2;

   def setVersion(self, v):
      if v == ID3_V1:
         v = ID3_V1_1;
      elif v == ID3_V2:
         v = ID3_DEFAULT_VERSION;

      if v != ID3_CURRENT_VERSION:
         self.header.setVersion(v);
         self.frames.setTagHeader(self.header);
   
   def setTextFrame(self, fid, txt):
       if not txt:
          self.frames.removeFramesByID(fid);
       else:
          self.frames.setTextFrame(fid, txt, self.encoding);

   def __saveV1Tag(self, version):
      assert(version & ID3_V1);

      # Build tag buffer.
      tag = "TAG";
      tag += self.fixToWidth(self.getTitle().encode("latin_1"), 30);
      tag += self.fixToWidth(self.getArtist().encode("latin_1"), 30);
      tag += self.fixToWidth(self.getAlbum().encode("latin_1"), 30);
      tag += self.fixToWidth(self.getYear().encode("latin_1"), 4);

      cmt = "";
      for c in self.getComments():
         if c.description == ID3_V1_COMMENT_DESC:
            cmt = c.comment;
            # We prefer this one over "";
            break; 
         elif c.description == "":
            cmt = c.comment;
            # Keep searching in case we find the description eyeD3 uses.
      cmt = self.fixToWidth(cmt, 30);
      if version != ID3_V1_0:
         track = self.getTrackNum()[0];
         if track != None:
            cmt = cmt[0:28] + "\x00" + chr(int(track) & 0xff);
      tag += cmt;

      if not self.getGenre():
         genre = 0;
      else:
         genre = self.getGenre().getId();
      tag += chr(genre & 0xff);

      assert(len(tag) == 128);

      tagFile = file(self.linkedFile.name, "r+b");
      # Write the tag over top an original or append it.
      try:
         tagFile.seek(-128, 2);
         if tagFile.read(3) == "TAG":
            tagFile.seek(-128, 2);
         else:
            tagFile.seek(0, 2);
      except IOError:
         # File is smaller than 128 bytes.
         tagFile.seek(0, 2);

      tagFile.write(tag);
      tagFile.flush();
      tagFile.close();
      
   def fixToWidth(self, s, n):
      retval = str(s);
      retval = retval[0:n];
      retval = retval + ("\x00" * (n - len(retval)));
      return retval;

   # Returns false when an ID3 v1 tag is not present, or contains no data.
   def __loadV1Tag(self, f):
      if isinstance(f, str):
         fp = file(f, "rb")
         closeFile = 1;
      else:
         fp = f;
         closeFile = 0;

      # Seek to the end of the file where all ID3v1 tags are written.
      fp.seek(0, 2);
      if fp.tell() > 127:
         fp.seek(-128, 2);
         id3tag = fp.read(128);
         if id3tag[0:3] == "TAG":
            TRACE_MSG("Located ID3 v1 tag");
            # 1.0 is implied until a 1.1 feature is recognized.
            self.setVersion(ID3_V1_0);

            title = re.sub("\x00+$", "", id3tag[3:33].strip());
            TRACE_MSG("Tite: " + title);
            if title:
               self.setTitle(title);

            artist = re.sub("\x00+$", "", id3tag[33:63].strip());
            TRACE_MSG("Artist: " + artist);
            if artist:
               self.setArtist(artist);

            album = re.sub("\x00+$", "", id3tag[63:93].strip());
            TRACE_MSG("Album: " + album);
            if album:
               self.setAlbum(album);

            year = re.sub("\x00+$", "", id3tag[93:97].strip());
            TRACE_MSG("Year: " + year);
            try:
               if year and int(year):
                  self.setDate(year);
            except ValueError:
               # Bogus year strings.
               pass;

	    if re.sub("\x00+$", "", id3tag[97:127]):
	       comment = id3tag[97:127];
               TRACE_MSG("Comment: " + comment);
               if comment[-2] == "\x00" and comment[-1] != "\x00":
                  # Parse track number (added to ID3v1.1) if present.
                  TRACE_MSG("Comment contains track number per v1.1 spec");
                  track = ord(comment[-1]);
                  self.setTrackNum((track, None));
                  TRACE_MSG("Track: " + str(track));
                  TRACE_MSG("Track Num found, setting version to v1.1s");
                  self.setVersion(ID3_V1_1);
		  comment = comment[:-2];
               else:
                  track = None
               comment = re.sub("\x00+$", "", comment).rstrip();
               TRACE_MSG("Comment: " + comment);
               if comment:
                  self.addComment(comment, ID3_V1_COMMENT_DESC);

            genre = ord(id3tag[127:128])
            TRACE_MSG("Genre ID: " + str(genre));
            self.setGenre(genre);

      if closeFile:
         fp.close()
      return len(self.frames);

   def __saveV2Tag(self, version):
      assert(version & ID3_V2);
      TRACE_MSG("Rendering tag version: " + versionToString(version));

      self.setVersion(version);

      currPadding = 0;
      currTagSize = 0
      if currTagSize == 0:
         # We may be converting from 1.x to 2.x so we need to find any
         # current v2.x tag otherwise we're gonna hork the file.
         tmpTag = Tag();
         if tmpTag.link(self.linkedFile.name, ID3_V2):
            TRACE_MSG("Found current v2.x tag:");
            currTagSize = tmpTag.linkedFile.tagSize;
            TRACE_MSG("Current tag size: %d" % currTagSize);
            currPadding = tmpTag.linkedFile.tagPadding;
            TRACE_MSG("Current tag padding: %d" % currPadding);

      # Tag it!
      if self.header.minorVersion == 4:
          h = FrameHeader(self.header);
          h.id = "TDTG";
          dateFrame = DateFrame(self.encoding +\
                                time.strftime("%Y-%m-%dT%H:%M:%S"), h);
          self.frames.removeFramesByID("TDTG");
          self.frames.addFrame(dateFrame);

      # Render all frames first so the data size is known for the tag header.
      frameData = "";
      for f in self.frames:
         TRACE_MSG("Rendering frame: " + f.header.id);
         raw_frame = f.render();
         TRACE_MSG("Rendered %d bytes" % len(raw_frame));
         frameData += raw_frame;

      TRACE_MSG("Rendered tag size: " + str(len(frameData)));

      rewriteFile = 0;
      paddingSize = 0;
      headerData = "";

      # Extended header
      if self.header.extended:
         # This is sorta lame.  We don't know the total framesize until
         # this is rendered, yet we can't render it witout knowing the
         # amount of padding.  Force it.
         rewriteFile = 1;
         paddingSize = 2048;
         TRACE_MSG("Rendering extended header");
         headerData += self.extendedHeader.render(self.header, frameData,
                                                  paddingSize);

      if rewriteFile or (10 + len(headerData) + len(frameData)) >= currTagSize:
         TRACE_MSG("File rewrite required");
         rewriteFile = 1;
         paddingSize = 2048;
      else:
         paddingSize = currTagSize - (len(headerData) + len(frameData));
      frameData += ("\x00" * paddingSize);

      # Render the tag header.
      TRACE_MSG("Rendering %s tag header with size %d" %\
                (versionToString(self.getVersion()), len(frameData)));
      headerData = self.header.render(len(frameData));

      # Assemble frame.
      tagData = headerData + frameData;

      # Write the tag.
      if not rewriteFile:
         tagFile = file(self.linkedFile.name, "r+b");
         TRACE_MSG("Writing %d bytes of tag data" % len(tagData));
         tagFile.write(tagData);
         tagFile.close();
      else:
         # Open original
         tagFile = file(self.linkedFile.name, "rb");
         # Read all audio data
         tagFile.seek(currTagSize);
         audioData = tagFile.read();
         tagFile.close();

         # Open tmp file
         tmpName = tempfile.mktemp();
         tmpFile = file(tmpName, "w+b");
         TRACE_MSG("Writing %d bytes of tag data" % len(tagData));
         tmpFile.write(tagData);
         tmpFile.write(audioData);
         tmpFile.close();

         # Move tmp to orig.
         shutil.copyfile(tmpName, self.linkedFile.name);
         os.unlink(tmpName);

      # Update our state.
      TRACE_MSG("Tag write complete.  Updating state.");
      self.linkedFile.tagPadding = paddingSize;
      # XXX: getSize could cache sizes so to prevent rendering again.
      self.linkedFile.tagSize = self.frames.getSize();


   # Returns >= 0 to indicate the padding size of the read frame; -1 returned
   # when not tag was found.
   def __loadV2Tag(self, f):
      if isinstance(f, str):
         fp = file(f, "rb")
         closeFile = 1;
      else:
         fp = f;
         closeFile = 0;

      padding = -1;
      try:
         # Look for a tag and if found load it.
         if not self.header.parse(fp):
            return -1;

         # Read the extended header if present.
         if self.header.extended:
            self.extendedHeader.parse(fp, self.header);

         # Header is definitely there so at least one frame *must* follow.
         self.frames.setTagHeader(self.header);
         padding = self.frames.parse(fp, self.header);
         TRACE_MSG("Tag contains %d bytes of padding." % padding);
      except FrameException, ex:
         #fp.close();
         #raise TagException(str(ex));
         # Technically, it's not a well-formed MP3, but we can still get data out of it.
         # it's better than crashing....
         pass
      except TagException:
         fp.close();
         raise;

      if closeFile:
         fp.close();
      return padding;

   def toInt(self, s):
      try:
         return int(s);
      except ValueError:
         return None;
      except TypeError:
         return None;

   def __padDateField(self, f):
      fStr = str(f);
      if len(fStr) == 2:
         pass;
      elif len(fStr) == 1:
         fStr = "0" + fStr;
      else:
         raise TagException("Invalid date field: " + fStr);
      return fStr;

   # DEPRECATED
   # This method will return the first comment in the FrameSet
   # and not all of them.  Multiple COMM frames are common and useful.  Use
   # getComments which returns a list.
   def getComment(self):
      f = self.frames[COMMENT_FID];
      if f:
         return f[0].comment;
      else:
         return None;


################################################################################
class GenreException(Exception):
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;


################################################################################
class Genre:
   id = None;
   name = None;

   def __init__(self):
      pass;

   def getId(self):
      return self.id;
   def getName(self):
      return self.name;

   # Sets the genre id.  The objects name field is set to the corresponding
   # value obtained from eyeD3.genres.
   #
   # Throws GenreException when name does not map to a valid ID3 v1.1. id.
   # This behavior can be disabled by passing 0 as the second argument.
   def setId(self, id, verify = 1):
      if not isinstance(id, int):
         raise TypeError("Invalid genre id: " + str(id));

      try:
         name = genres[id];
      except Exception, ex:
         if verify:
            raise GenreException("Invalid genre id: " + str(id));

      if verify and not name:
         raise GenreException("Genre id maps to a null name: " + str(id));

      self.id = id;
      self.name = name;

   # Sets the genre name.  The objects id field is set to the corresponding
   # value obtained from eyeD3.genres.
   #
   # Throws GenreException when name does not map to a valid ID3 v1.1. name.
   # This behavior can be disabled by passing 0 as the second argument.
   def setName(self, name, verify = 1):
      if not isinstance(name, str):
         raise GenreException("Invalid genre name: " + str(name));

      try:
         id = genres[name];
         # Get titled case.
         name = genres[id];
      except:
         if verify:
            raise GenreException("Invalid genre name: " + name);

      self.id = id;
      self.name = name;


   # Sets the genre id and name. 
   #
   # Throws GenreException when eyeD3.genres[id] != name (case insensitive). 
   # This behavior can be disabled by passing 0 as the second argument.
   def set(self, id, name, verify = 1):
      if not isinstance(id, int):
         raise GenreException("Invalid genre id: " + id);
      if not isinstance(name, str):
         raise GenreException("Invalid genre name: " + str(name));

      if not verify:
         self.id = id;
         self.name = name;
      else:
         try:
            if genres[name] != id:
               raise GenreException("eyeD3.genres[" + str(id) + "] " +\
                                    "does not match " + name);
            self.id = id;
            self.name = name;
         except:
            raise GenreException("eyeD3.genres[" + str(id) + "] " +\
                                 "does not match " + name);
      
   # Parses genre information from genreStr. 
   # The following formats are supported:
   # 01, 2, 23, 125 - ID3 v1 style.
   # (01), (2), (129)Hardcore, (9)Metal - ID3 v2 style with and without
   #                                      refinement.
   #
   # Throws GenreException when an invalid string is passed.
   def parse(self, genreStr, verify = 1):
      genreStr = str(genreStr.encode('utf-8')).strip();
      self.id = None;
      self.name = None;

      if not genreStr:
         return;

      # XXX: Utf-16 conversions leave a null byte at the end of the string.
      while genreStr[len(genreStr) - 1] == "\x00":
         genreStr = genreStr[:len(genreStr) - 1];

      # ID3 v1 style.
      # Match 03, 34, 129.
      regex = re.compile("[0-9][0-9]?[0-9]?$");
      if regex.match(genreStr):
         if len(genreStr) != 1 and genreStr[0] == '0':
            genreStr = genreStr[1:];

         self.setId(int(genreStr), verify);
         return;

      # ID3 v2 style.
      # Match (03), (0)Blues, (15) Rap
      regex = re.compile("\(([0-9][0-9]?[0-9]?)\)(.*)$");
      m = regex.match(genreStr);
      if m:
         (id, name) = m.groups();
         if len(id) != 1 and id[0] == '0':
            id = id[1:];
            
         if id and name:
            self.set(int(id), name.strip(), verify);
         else:
            self.setId(int(id), verify);
         return;

      # Non standard, but witnessed.
      # Match genreName alone.  e.g. Rap, Rock, blues.
      regex = re.compile("^[A-Z 0-9+/\-&]+\00*$", re.IGNORECASE);
      if regex.match(genreStr):
         self.setName(genreStr, verify);
         return;
      else:
          print regex.pattern;
      raise GenreException("Genre string cannot be parsed: " + genreStr);

   def __str__(self):
      s = "";
      if self.id != None:
         s += "(" + str(self.id) + ")"
      if self.name:
         s += self.name;
      return s;

################################################################################
class InvalidAudioFormatException:
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;

################################################################################
class Mp3AudioFile:
   fileName       = str();
   fileSize       = int();
   header         = eyeD3_mp3.Header();
   xingHeader     = None;
   tag            = Tag();
   invalidFileExc = InvalidAudioFormatException("File is not mp3");
   # Number of seconds required to play the audio file.
   playTime       = None;

   def __init__(self, fileName, tagVersion = ID3_ANY_VERSION):
      self.playTime = None;
      self.fileName = fileName;

#      if not isMp3File(fileName):
#         raise self.invalidFileExc;

      # Parse ID3 tag.
      f = file(fileName, "rb");
      tag = Tag();
      hasTag = tag.link(f, tagVersion);
      # Find the first mp3 frame.
      if tag.isV1():
         framePos = 0;
      elif not hasTag:
         framePos = 0;
         tag = None;
      else:
         # XXX: Note that v2.4 allows for appended tags; account for that.
         framePos = tag.header.SIZE + tag.header.tagSize;
      f.seek(framePos);
      bString = f.read(4);
      if len(bString) < 4:
         raise InvalidAudioFormatException("Unable to find a valid mp3 "\
                                           "frame");
      frameHead = bin2dec(bytes2bin(bString));
      header = eyeD3_mp3.Header();
      # Keep reading until we find a valid mp3 frame header.
      while not header.isValid(frameHead):
         frameHead <<= 8;
         bString = f.read(1);
         if len(bString) != 1:
            raise InvalidAudioFormatException("Unable to find a valid mp3 "\
                                              "frame");
         frameHead |= ord(bString[0]);
      TRACE_MSG("mp3 header %x found at position: %d (0x%x)" % \
                (frameHead, f.tell() - 4, f.tell() - 4));

      # Decode the header.
      try:
         header.decode(frameHead);
         # Check for Xing header inforamtion which will always be in the
         # first "null" frame.
         f.seek(-4, 1);
         mp3Frame = f.read(header.frameLength);
         if mp3Frame.find("Xing") != -1:
            xingHeader = eyeD3_mp3.XingHeader();
            if not xingHeader.decode(mp3Frame):
               raise InvalidAudioFormatException("Corrupt Xing header");
         else:
            xingHeader = None;
      except eyeD3_mp3.Mp3Exception, ex:
         raise InvalidAudioFormatException(str(ex));

      # Compute track play time.
      tpf = eyeD3_mp3.computeTimePerFrame(header);
      if xingHeader:
         self.playTime = int(tpf * xingHeader.numFrames);
      else:
         length = self.getSize();
         if tag and tag.isV2():
            length -= tag.header.SIZE + tag.header.tagSize;
            # Handle the case where there is a v2 tag and a v1 tag.
            f.seek(-128, 2)
            if f.read(3) == "TAG":
               length -= 128;
         elif tag and tag.isV1():
            length -= 128;
         self.playTime = int((length / header.frameLength) * tpf);    

      self.header = header;
      self.xingHeader = xingHeader;
      self.tag = tag;
      f.close();

   def getTag(self):
      return self.tag;

   def getSize(self):
      if not self.fileSize:
         self.fileSize = os.stat(self.fileName)[ST_SIZE];
      return self.fileSize;

   def getPlayTime(self):
      return self.playTime;

   def getPlayTimeString(self):
      total = self.getPlayTime();
      h = total / 3600;
      m = (total % 3600) / 60;
      s = (total % 3600) % 60;
      if h:
         timeStr = "%d:%.2d:%.2d" % (h, m, s);
      else:
         timeStr = "%d:%.2d" % (m, s);
      return timeStr;

   # Returns a tuple.  The first value is a boolean which if true means the
   # bit rate returned in the second value is variable.
   def getBitRate(self):
      xHead = self.xingHeader;
      if xHead:
         tpf = eyeD3_mp3.computeTimePerFrame(self.header);
         br = int((xHead.numBytes * 8) / (tpf * xHead.numFrames * 1000));
         vbr = 1;
      else:
         br = self.header.bitRate;
         vbr = 0;
      return (vbr, br);

   def getBitRateString(self):
      (vbr, bitRate) = self.getBitRate();
      brs = "%d kb/s" % bitRate;
      if vbr:
         brs = "~" + brs;
      return brs;

################################################################################
def isMp3File(fileName):
    (type, enc) = mimetypes.guess_type(fileName);
    return type == "audio/mpeg";

################################################################################
class GenreMap(list):

   #######################################################################
   # Accepts both int and string keys. Throws IndexError and TypeError.
   def __getitem__(self, key):
      if isinstance(key, int):
         if key >= 0 and key < len(self):
            v = list.__getitem__(self, key);
            if v:
               return v;
            else:
               return None;
         else:
            raise IndexError("genre index out of range");
      elif isinstance(key, str):
         if self.reverseDict.has_key(key.lower()):
            return self.reverseDict[key.lower()];
         else:
            raise IndexError(key + " genre not found");
      else:
         raise TypeError("genre key must be type int or string");

   def __init__(self):
      self.data = []
      self.reverseDict = {}
      # ID3 genres as defined by the v1.1 spec with WinAmp extensions.
      self.append('Blues');
      self.append('Classic Rock');
      self.append('Country');
      self.append('Dance');
      self.append('Disco');
      self.append('Funk');
      self.append('Grunge');
      self.append('Hip-Hop');
      self.append('Jazz');
      self.append('Metal');
      self.append('New Age');
      self.append('Oldies');
      self.append('Other');
      self.append('Pop');
      self.append('R&B');
      self.append('Rap');
      self.append('Reggae');
      self.append('Rock');
      self.append('Techno');
      self.append('Industrial');
      self.append('Alternative');
      self.append('Ska');
      self.append('Death Metal');
      self.append('Pranks');
      self.append('Soundtrack');
      self.append('Euro-Techno');
      self.append('Ambient');
      self.append('Trip-Hop');
      self.append('Vocal');
      self.append('Jazz+Funk');
      self.append('Fusion');
      self.append('Trance');
      self.append('Classical');
      self.append('Instrumental');
      self.append('Acid');
      self.append('House');
      self.append('Game');
      self.append('Sound Clip');
      self.append('Gospel');
      self.append('Noise');
      self.append('AlternRock');
      self.append('Bass');
      self.append('Soul');
      self.append('Punk');
      self.append('Space');
      self.append('Meditative');
      self.append('Instrumental Pop');
      self.append('Instrumental Rock');
      self.append('Ethnic');
      self.append('Gothic');
      self.append('Darkwave');
      self.append('Techno-Industrial');
      self.append('Electronic');
      self.append('Pop-Folk');
      self.append('Eurodance');
      self.append('Dream');
      self.append('Southern Rock');
      self.append('Comedy');
      self.append('Cult');
      self.append('Gangsta Rap');
      self.append('Top 40');
      self.append('Christian Rap');
      self.append('Pop / Funk');
      self.append('Jungle');
      self.append('Native American');
      self.append('Cabaret');
      self.append('New Wave');
      self.append('Psychedelic');
      self.append('Rave');
      self.append('Showtunes');
      self.append('Trailer');
      self.append('Lo-Fi');
      self.append('Tribal');
      self.append('Acid Punk');
      self.append('Acid Jazz');
      self.append('Polka');
      self.append('Retro');
      self.append('Musical');
      self.append('Rock & Roll');
      self.append('Hard Rock');
      self.append('Folk');
      self.append('Folk-Rock');
      self.append('National Folk');
      self.append('Swing');
      self.append('Fast  Fusion');
      self.append('Bebob');
      self.append('Latin');
      self.append('Revival');
      self.append('Celtic');
      self.append('Bluegrass');
      self.append('Avantgarde');
      self.append('Gothic Rock');
      self.append('Progressive Rock');
      self.append('Psychedelic Rock');
      self.append('Symphonic Rock');
      self.append('Slow Rock');
      self.append('Big Band');
      self.append('Chorus');
      self.append('Easy Listening');
      self.append('Acoustic');
      self.append('Humour');
      self.append('Speech');
      self.append('Chanson');
      self.append('Opera');
      self.append('Chamber Music');
      self.append('Sonata');
      self.append('Symphony');
      self.append('Booty Bass');
      self.append('Primus');
      self.append('Porn Groove');
      self.append('Satire');
      self.append('Slow Jam');
      self.append('Club');
      self.append('Tango');
      self.append('Samba');
      self.append('Folklore');
      self.append('Ballad');
      self.append('Power Ballad');
      self.append('Rhythmic Soul');
      self.append('Freestyle');
      self.append('Duet');
      self.append('Punk Rock');
      self.append('Drum Solo');
      self.append('A Cappella');
      self.append('Euro-House');
      self.append('Dance Hall');
      self.append('Goa');
      self.append('Drum & Bass');
      self.append('Club-House');
      self.append('Hardcore');
      self.append('Terror');
      self.append('Indie');
      self.append('BritPop');
      self.append('Negerpunk');
      self.append('Polsk Punk');
      self.append('Beat');
      self.append('Christian Gangsta Rap');
      self.append('Heavy Metal');
      self.append('Black Metal');
      self.append('Crossover');
      self.append('Contemporary Christian');
      self.append('Christian Rock');
      self.append('Merengue');
      self.append('Salsa');
      self.append('Thrash Metal');
      self.append('Anime');
      self.append('JPop');
      self.append('Synthpop');

      # Pad up to 255 with "Unknown"
      count = len(self);
      while count < 256:
         self.append("Unknown");
         count += 1;
      
      for index in range(len(self)):
         if self[index]:
	    self.reverseDict[string.lower(self[index])] = index
class LinkedFile:
   name = "";
   tagPadding = 0;
   tagSize = 0;  # This includes the padding byte count.

   def __init__(self, fileName):
      self.name = fileName;

def tagToUserTune(tag):
    audio_file = None;
    if isinstance(tag, Mp3AudioFile):
        audio_file = tag;
        tag = audio_file.getTag();
        
    tune =  "<tune xmlns='http://jabber.org/protocol/tune'>\n";
    if tag.getArtist():
        tune += "  <artist>" + tag.getArtist() + "</artist>\n";
    if tag.getTitle():
        tune += "  <title>" + tag.getTitle() + "</title>\n";
    if tag.getAlbum():
        tune += "  <source>" + tag.getAlbum() + "</source>\n";
    tune += "  <track>" + "file://" + os.path.abspath(tag.linkedFile.name) +\
            "</track>\n";
    if audio_file:
        # XXX: This should be an xs:duration
        tune += "  <length>" + audio_file.getPlayTimeString() + "</length>\n";
    tune += "</tune>\n";
    return tune;

#
# Module level globals.
#
genres = GenreMap();

