#!/usr/bin/env python

# Module for fetching information about an audio compact disc and
# returning it in a format friendly to CDDB.

# If called from the command line, will print out disc info in a
# format identical to Robert Woodcock's 'cd-discid' program.

# Written 17 Nov 1999 by Ben Gertzfield <che@debian.org>
# This work is released under the GNU GPL, version 2 or later.

# Release version 1.3


# changes for mmpython:
#
# $Log: DiscID.py,v $
# Revision 1.4  2004/11/14 19:26:38  dischi
# fix future warning
#
# Revision 1.3  2003/06/23 19:26:16  dischi
# Fixed bug in the cdrommodule that the file was not closed after usage.
# The result was a drive you can't eject while the program (e.g. Freevo)
# is running. Added cvs log for DiscID and cdrommodule to keep track of
# all changes we did for mmpython.
#
#

try:
    import cdrom, sys
except ImportError:
    # Seems cdrom has either not been compiler or is not supported
    # on this System
    pass
    

def cddb_sum(n):
    ret = 0
    
    while n > 0:
	ret = ret + (n % 10)
	n = n / 10

    return ret

def disc_id(device):
    device = cdrom.open(device)
    (first, last) = cdrom.toc_header(device)

    track_frames = []
    checksum = 0
    
    for i in range(first, last + 1):
	(min, sec, frame) = cdrom.toc_entry(device, i)
	checksum = checksum + cddb_sum(min*60 + sec)
	track_frames.append(min*60*75 + sec*75 + frame)

    (min, sec, frame) = cdrom.leadout(device)
    track_frames.append(min*60*75 + sec*75 + frame)

    total_time = (track_frames[-1] / 75) - (track_frames[0] / 75)
	       
    discid = ((long(checksum) % 0xff) << 24 | total_time << 8 | last)
    cdrom.close(device)
    return [discid, last] + track_frames[:-1] + [ track_frames[-1] / 75 ]

if __name__ == '__main__':

    dev_name = None
    device = None
    
    if len(sys.argv) >= 2:
	dev_name = sys.argv[1]

    if dev_name:
        device = open(dev_name)
    else:
        device = open()
        
    disc_info = disc_id(device)

    print ('%08lx' % disc_info[0]),

    for i in disc_info[1:]:
	print ('%d' % i),
