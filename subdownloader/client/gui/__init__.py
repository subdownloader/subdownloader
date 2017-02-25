# -*- coding: utf-8 -*-
# Copyright (c) 2017 SubDownloader Developers - See COPYING - GPLv3

from subdownloader.videofile import VIDEOS_EXT
from subdownloader.subtitlefile import SUBTITLES_EXT

SELECT_SUBTITLES = _("Subtitle Files (*.%s)") % " *.".join(SUBTITLES_EXT)
SELECT_VIDEOS = _("Video Files (*.%s)") % " *.".join(VIDEOS_EXT)
