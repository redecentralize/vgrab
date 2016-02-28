#!/usr/bin/env python
import os
import re
import requests
from urlparse import urlparse, parse_qs
import urllib

import feedparser
from slugify import slugify

ATOM_FEED = "https://www.youtube.com/feeds/videos.xml?user=redecentralize"
YTDL_GET  = "youtube-dl --no-progress -f {0} -o {1} {2}"
FOLDER = "/var/www/redecentralise.net/video"

# Get the feed
feed = feedparser.parse(ATOM_FEED)
for item in feed.entries:
    title, link = item.title, item.link
    # Tiny bit of cleanup
    title = slugify(title)
    if title.startswith("redecentralize-interviews-"):
        title = title[len("redecentralize-interviews-"):]

    obj = link[link.find('=')+1:]
    poster_url = "http://img.youtube.com/vi/" + obj + "/maxresdefault.jpg"
    # Should parse this from qs['fmt_list']
    formats = {'webm': 43, 'mp4': 18}

    poster = os.path.join(FOLDER, title + ".jpg")
    pre_poster = os.path.join(FOLDER, "pre." + title + ".jpg")
    if not os.path.exists(poster):
        print "Fetching {0} as {1}".format(poster_url, poster)
        urllib.urlretrieve(poster_url, pre_poster)
        # resize them all to same size so consistent
        os.system("convert -resize 1280x720 " + pre_poster + " " + poster)
    else:
        print "Skipping {0} as {1}".format(poster_url, poster)

    for ext, fmt in formats.iteritems():
        out = os.path.join(FOLDER, title + "." + ext)
        if os.path.exists(out):
            print "Skipping fmt:{0} for {1}".format(ext, title)
            continue
        else:
            print "Fetching {0} as {1}".format(title, ext)

            get_cmd = YTDL_GET.format(fmt, out, link)
            # Run the command and just wait
            f = os.popen(get_cmd)
            # We have to consume the data otherwise it will blow up.
            while True:
                data = f.read(2048)
                if not data:
                    break
