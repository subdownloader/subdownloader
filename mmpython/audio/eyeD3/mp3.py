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
from binfuncs import *;
from utils import *;

#######################################################################
class Mp3Exception:
   msg = "";

   def __init__(self, msg):
      self.msg = msg;

   def __str__(self):
      return self.msg;


#                   MPEG1  MPEG2  MPEG2.5
SAMPLE_FREQ_TABLE = ((44100, 22050, 11025),
                     (48000, 24000, 12000),
                     (32000, 16000, 8000),
                     (None,  None,  None));

#              V1/L1  V1/L2 V1/L3 V2/L1 V2/L2&L3 
BIT_RATE_TABLE = ((0,    0,    0,    0,    0),
                  (32,   32,   32,   32,   8),
                  (64,   48,   40,   48,   16),
                  (96,   56,   48,   56,   24),
                  (128,  64,   56,   64,   32),
                  (160,  80,   64,   80,   40),
                  (192,  96,   80,   96,   44),
                  (224,  112,  96,   112,  56),
                  (256,  128,  112,  128,  64),
                  (288,  160,  128,  144,  80),
                  (320,  192,  160,  160,  96),
                  (352,  224,  192,  176,  112),
                  (384,  256,  224,  192,  128),
                  (416,  320,  256,  224,  144),
                  (448,  384,  320,  256,  160),
                  (None, None, None, None, None));

#                             L1    L2    L3
TIME_PER_FRAME_TABLE = (None, 384, 1152, 1152);

# Emphasis constants
EMPHASIS_NONE = "None";
EMPHASIS_5015 = "50/15 ms";
EMPHASIS_CCIT = "CCIT J.17";

# Mode constants
MODE_STEREO              = "Stereo";
MODE_JOINT_STEREO        = "Joint stereo";
MODE_DUAL_CHANNEL_STEREO = "Dual channel stereo";
MODE_MONO                = "Mono";

# Flag bits
FRAMES_FLAG    = 0x0001
BYTES_FLAG     = 0x0002
TOC_FLAG       = 0x0004
VBR_SCALE_FLAG = 0x0008

#######################################################################
def computeTimePerFrame(frameHeader):
   tpf = TIME_PER_FRAME_TABLE[frameHeader.layer];
   tpf = float(tpf) / float(frameHeader.sampleFreq);
   return tpf;

#######################################################################
class Header:
   version = float();
   layer = int();
   errorProtection = 0;
   bitRate = int();
   playTime = long();
   sampleFreq = int();
   padding = 0;
   privateBit = 0;
   copyright = 0;
   original = 0;
   emphasis = str();
   mode = str();
   # This value is left as is: 0 <= modeExtension <= 3.  Consult the
   # mp3 spec here http://www.dv.co.yu/mpgscript/mpeghdr.htm if you wish to 
   # interpret it.
   modeExtension = 0;

   # Pass in a 4 byte integer to determine if it matches a valid mp3 frame
   # header.
   def isValid(self, header):
      # Test for the mp3 frame sync: 11 set bits.
      if (header & 0xffe00000L) != 0xffe00000L:
         return 0;
      if not ((header >> 17) & 3):
         return 0;
      if ((header >> 12) & 0xf) == 0xf:
         return 0;
      if not ((header >> 12) & 0xf):
         return 0;
      if ((header >> 10) & 0x3) == 0x3:
         return 0;
      if (((header >> 19) & 1) == 1) and (((header >> 17) & 3) == 3) and \
         (((header >> 16) & 1) == 1):
         return 0;
      if (header & 0xffff0000L) == 0xfffe0000L:
         return 0;

      return 1;

   # This may throw an Mp3Exception if the header is malformed.
   def decode(self, header):
      # MPEG audio version from bits 19 and 20.
      if not header & (1 << 20) and header & (1 << 19):
         raise Mp3Exception("Illegal MPEG audio version");
      elif not header & (1 << 20) and not header & (1 << 19):
         self.version = 2.5;
      else:
         if not header & (1 << 19):
            self.version = 2.0;
         else:
            self.version = 1.0;

      
      # MPEG audio layer from bits 18 and 17.
      if not header & (1 << 18) and not header & (1 << 17):
         raise Mp3Exception("Illegal MPEG layer value");
      elif not header & (1 << 18) and header & (1 << 17):
         self.layer = 3;
      elif header & (1 << 18) and not header & (1 << 17):
         self.layer = 2;
      else:
         self.layer = 1;

      # Decode some simple values.
      self.errorProtection = not (header >> 16) & 0x1;
      self.padding = (header >> 9) & 0x1;
      self.privateBit = (header >> 8) & 0x1;
      self.copyright = (header >> 3) & 0x1;
      self.original = (header >> 2) & 0x1;

      # Obtain sampling frequency.
      sampleBits = (header >> 10) & 0x3;
      if self.version == 2.5:
         freqCol = 2;
      else:
         freqCol = int(self.version - 1);
      self.sampleFreq = SAMPLE_FREQ_TABLE[sampleBits][freqCol];
      if not self.sampleFreq:
         raise Mp3Exception("Illegal MPEG sampling frequency");


      # Compute bitrate.
      bitRateIndex = (header >> 12) & 0xf;
      if int(self.version) == 1 and self.layer == 1:
         bitRateCol = 0;
      elif int(self.version) == 1 and self.layer == 2:
         bitRateCol = 1;
      elif int(self.version) == 1 and self.layer == 3:
         bitRateCol = 2;
      elif int(self.version) == 2 and self.layer == 1:
         bitRateCol = 3;
      elif int(self.version) == 2 and (self.layer == 2 or \
                                       self.layer == 3):
         bitRateCol = 4;
      else:
         raise Mp3Exception("Mp3 version %f and layer %d is an invalid "\
                            "combination" % (self.version, self.layer));
      self.bitRate = BIT_RATE_TABLE[bitRateIndex][bitRateCol];
      if self.bitRate == None:
         raise Mp3Exception("Invalid bit rate");
      # We know know the bit rate specified in this frame, but if the file
      # is VBR we need to obtain the average from the Xing header.
      # This is done by the caller since right now all we have is the frame
      # header.

      # Emphasis; whatever that means??
      emph = header & 0x3;
      if emph == 0:
         self.emphasis = EMPHASIS_NONE;
      elif emph == 1:
         self.emphasis = EMPHASIS_5015;
      elif emph == 2:
         self.emphasis = EMPHASIS_CCIT;
      elif strictID3():
         raise Mp3Exception("Illegal mp3 emphasis value: %d" % emph);

      # Channel mode.
      modeBits = (header >> 6) & 0x3;
      if modeBits == 0:
         self.mode = MODE_STEREO;
      elif modeBits == 1:
         self.mode = MODE_JOINT_STEREO;
      elif modeBits == 2:
         self.mode = MODE_DUAL_CHANNEL_STEREO;
      else:
         self.mode = MODE_MONO;
      self.modeExtension = (header >> 4) & 0x3; 

      # Layer II has restrictions wrt to mode and bit rate.  This code
      # enforces them.
      if self.layer == 2:
         m = self.mode;
         br = self.bitRate;
         if (br == 32 or br == 48 or br == 56 or br == 80) and \
            (m != MODE_MONO):
            raise Mp3Exception("Invalid mode/bitrate combination for layer "\
                               "II");
         if (br == 224 or br == 256 or br == 320 or br == 384) and \
            (m == MODE_MONO):
            raise Mp3Exception("Invalid mode/bitrate combination for layer "\
                               "II");

      br = self.bitRate * 1000;
      sf = self.sampleFreq;
      p  = self.padding;
      if self.layer == 1:
         # Layer 1 uses 32 bit slots for padding.
         p  = self.padding * 4;
         self.frameLength = int((((12 * br) / sf) + p) * 4);
      else:
         # Layer 2 and 3 uses 8 bit slots for padding.
         p  = self.padding * 1;
         self.frameLength = int(((144 * br) / sf) + p);

      # Dump the state.
      TRACE_MSG("MPEG audio version: " + str(self.version));
      TRACE_MSG("MPEG audio layer: " + ("I" * self.layer));
      TRACE_MSG("MPEG sampling frequency: " + str(self.sampleFreq));
      TRACE_MSG("MPEG bit rate: " + str(self.bitRate));
      TRACE_MSG("MPEG channel mode: " + self.mode);
      TRACE_MSG("MPEG channel mode extension: " + str(self.modeExtension));
      TRACE_MSG("MPEG CRC error protection: " + str(self.errorProtection));
      TRACE_MSG("MPEG original: " + str(self.original));
      TRACE_MSG("MPEG copyright: " + str(self.copyright));
      TRACE_MSG("MPEG private bit: " + str(self.privateBit));
      TRACE_MSG("MPEG padding: " + str(self.padding));
      TRACE_MSG("MPEG emphasis: " + str(self.emphasis));
      TRACE_MSG("MPEG frame length: " + str(self.frameLength));

#######################################################################
class XingHeader:
   numFrames = int();
   numBytes = int();
   toc = [0] * 100;
   vbrScale = int();

   # Pass in the first mp3 frame from the file as a byte string.
   # If an Xing header is present in the file it'll be in the first mp3
   # frame.  This method returns true if the Xing header is found in the
   # frame, and false otherwise.
   def decode(self, frame):
      # mp3 version
      id      = (ord(frame[1]) >> 3) & 0x1;
      # channel mode.
      mode    = (ord(frame[3]) >> 6) & 0x3;

      # Find the start of the Xing header.
      if id:
         if mode != 3:
            pos = 32 + 4;
         else:
            pos = 17 + 4;
      else:
         if mode != 3:
            pos = 17 + 4;
         else:
            pos = 9 + 4;
      if frame[pos] != 'X' or frame[pos + 1] != 'i' or \
         frame[pos + 2] != 'n' or frame[pos + 3] != 'g':
         return 0;
      TRACE_MSG("Xing header detected");
      pos += 4;

      # Read Xing flags.
      headFlags = bin2dec(bytes2bin(frame[pos:pos + 4]));
      pos += 4;
      TRACE_MSG("Xing header flags: 0x%x" % headFlags);

      # Read frames header flag and value if present
      if headFlags & FRAMES_FLAG:
         self.numFrames = bin2dec(bytes2bin(frame[pos:pos + 4]));
         pos += 4;
         TRACE_MSG("Xing numFrames: %d" % self.numFrames);

      # Read bytes header flag and value if present
      if headFlags & BYTES_FLAG:
         self.numBytes = bin2dec(bytes2bin(frame[pos:pos + 4]));
         pos += 4;
         TRACE_MSG("Xing numBytes: %d" % self.numBytes);

      # Read TOC header flag and value if present
      if headFlags & TOC_FLAG:
         i = 0;
         self.toc = frame[pos:pos + 100];
         pos += 100;
         TRACE_MSG("Xing TOC (100 bytes): PRESENT");
      else:
         TRACE_MSG("Xing TOC (100 bytes): NOT PRESENT");

      # Read vbr scale header flag and value if present
      if headFlags & VBR_SCALE_FLAG:
         self.vbrScale = bin2dec(bytes2bin(frame[pos:pos + 4]));
         pos += 4;
         TRACE_MSG("Xing vbrScale: %d" % self.vbrScale);

      return 1;
