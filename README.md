KissNetwork
===========

This is a plugin that creates a new channel in Plex Media Server to view content from these websites: [Kissanime.com](http://kissanime.com/), [Kissasian.com](http://kissasian.com/), [Kisscartoon.me](http://kisscartoon.me/), and [Kissmanga.com](http://kissmanga.com/). It is currently under development and as such, should be considered alpha software and potentially unstable. If you try it and it works for you (or if not!) please let me know.

**Note:** the author of this plugin has no affiliation with the Kiss sites or the owners of the content that they host.

Features
--------

- Watch video content across all Kiss sites (quality ranges from 360p to 1080p)
- Choose which Kiss sites to view content, hide others
- Option to Block most Adult content
- Read manga from Kissmanga
- Create custom Bookmarks
- Search all Kiss sites for videos/manga

Operation
---------

- Sort List by...
    - Set list order for "All", "Alphabets", "Genres", and "Movies"
- View Kiss(anime, asian, cartoon, manga)
    - If site enabled then it will be availible in the Channel for viewing. This includes Bookmarks and Searching.
- Cache All Covers Locally (overrides "Cache Bookmark Covers Locally" function)
    - If enabled, will download and index cover images
    - If disabled, will remove all downloaded images from computer. If "Cache Bookmark Covers Locally" is True, then bookmark covers will be kept from deletion.
- Cache Bookmark Covers Locally
    - If enabled AND "Cache All Covers Locally" is False, will download cover images and only display them in your "My Bookmarks" list.
    - If disabled AND 'Cache All Covers Locally" is False, will delete all bookmarked covers from computer.
- Allow Adult Content
    - Attempt to block adult content from the kiss sites. If content blocked, then will removed adult themed genres from genre list and provide a popup whenever an adult video/manga is accessed providing feedback as to why the content is blocked.
- Enable Developer Tools
    - Hide/Un-Hide Developer Tools Menu located in "About / Help" section
- Developer Tools
    - Reset Header_Dict File: Create backup of old Header_Dict, then delete current, and write new Header_Dict with freash headers
    - Reset Domain_Dict File: Create backup of old Domain_Dict, then delete current, and write new Domain_Dict with freash domains
    - Reset Dict cfscrape Test Key: Delete test key and then force the channel to retake the cfscrape test. It is testing for a valid JavaScript Runtime
- Bookmark Tools (located in "Enable Developer Tools")
    - Toggle Hiding "Clear Bookmarks" Function: For those of us who accidentally delete our bookmarks but don't mean to
    - Reset "All" Bookmarks: Same as "Clear All Bookmarks"
    - Reset "Anime" Bookmarks: Same as "Clear Anime Bookmarks"
    - Reset... etc...

System Requirements
-------------------

- **Plex Media Server**

  - Tested Working:
    - Linux
      - PMS version 0.9.12.13
      - [Ubuntu 14.04 x86_64 Linux 3.13.0-63-generic](http://i.imgur.com/ZiO7htR.png)
        - Installation of a Javascript runtime may be required
        - Refer to [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape#readme) for valid JavaScript Engines
        - For Ubuntu use: `sudo apt-get install nodejs` (installs nodejs)
    - Windows 7 & 10
      - PMS version 0.9.12.13

- **Plex Clients:**

  - Tested Working:
    - Plex Media Center / Home Theater (Ubuntu & Windows 7 & 10, same as above)
    - Android (4.4.2)
    - Plex/Web (2.4.23)
    - Chromecast (Videos)

  - Not Working:
    - Chromecast (Pictures)

How To Install
--------------

- [Download](https://github.com/Twoure/KissNetwork.bundle/archive/master.zip) and install it by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
- Unzip and rename the folder to "KissNetwork.bundle"
- Copy KissNetwork.bundle into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
- ~~Restart PMS~~ **This is old, should not have to restart PMS.  If channel does not appear then Restart PMS**

Known Issues
------------

- General
  - Cookie cache times keep changing. I try and keep these up-to-date, untill I create a checker for valid cookie cache times.
  - First time the Channel runs (this means ever, not every time it starts just the first time) you need to wait about 20-30 seconds for the headers to be set.
  - If the headers are not set before Plex Framework tries to scrape the site then an error message will popup saying you need to wait until the headers are set.
  - Kissasian.com (Drama) has a very short cache time for its cookies, about 30-45 minutes.  This can bog down the Search function (only if Drama section enabled) since the Drama section will need re-caching after 30 minutes have passed since the last time it was cached.  You should notice a 5 second delay if it is re-caching the Drama section (or any one of the sites, if two sites have to re-cache then it may take 10 seconds etc...).
  - Episode, Movie, VideoClip data may be incorrect depending on how the shows are archived on the Kiss sites.  I've accounted for most variations but some info will still be incorrect.
  - Sometimes the date the video aired only has a year.  If this is the case then the metadata will set the originally_available_at to the current month and day with the year from the video.  Also aired dates are when the season started or movie came out, so not the actual date the episode aired.

- Kiss(anime, asian, cartoon, manga) are all hosted behind Cloudflare so added a modified version of [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape) as a work around
  - Kisscartoon has no "Mature" filter/genre so my Adult Prefs Optioin cannot filter out Adult Cartoons
  - Cover art does not load for Videos
    - Plex Framework does not allow me to set headers for directory object thumbs, still looking into this issue
    - I have added a local caching option for video bookmarks to work around cloudflare
  - Kissmanga is not the most useful reader for the Plex/Web client, but works reasonably well for Smart phones and Plex Media Center.

- Chromecast does not work for Photo Albums but does for Videos, don't know why yet.  Assuming it has to do with how the Photo Albums are created.

- Plex Home Theater
  - Channel exits when adding/removing bookmarks.  Has to do with pop up messages.

Plans
-----

- General
  - Might look into grouping seasons of the same show for the directory list
  - Implement some kind of Password protection for choosing which sites to display
  - Updater similar to [piplongrun](https://github.com/piplongrun/lmwt-kiss.bundle/blob/70d1abc8001962892b2f54afe6252e6be02e7eb7/Contents/Code/updater.py)
  - Continue Improving Metadata

- Bookmarks
  - Add option to add all seasons at once for a show
  - Group seasons into one show
  - Create separate directories for TV and Movies
  - Might move bookmarks to own file like I did with Header_Dict

ChangeLog
---------

**0.06** - 11/06/15 - Fix for Kissmanga. New Cache Covers Option. New About/Help, Dev Tools, Bookmark Tools sections. Dynamically set domain URL's now.
- **NOTE:** Kissanime.com changed to Kissanime.to You will need to Reset your Header_Dict. Follow **Operation** above for usage.

**0.05** - 10/29/15 - Improved Metadata & summary.  Added 'Adult' to Prefs and  _Top_ list to Cartoon and Drama sections.  Fixed Cartoon cache time.
- **Note** Due to a string encode/decode error you will have to **Clear All Bookmarks** before updating from **0.04** to **0.05**.

**0.04** - 10/16/15 - Moved to "Shared Code" for setting headers.  Improved Header Cache times.

**0.03** - 10/13/15 - Major overhaul of headers.  No more 5 second wait time for each directory.  Improved Bookmarking, Search, and cookie cache time. **Note** Bookmarks changed from previous version.  You will have to delete your old Dictionary file "Dict" from the "Plug-in Support" Path.

**0.02** - 10/09/15 - Fixed Windows 10 not displaying channel [issue](https://github.com/Twoure/KissNetwork.bundle/issues/1), and added site selection in channel preferences.

**0.01** - 10/03/15 - Initial version

**0.00** - 09/21/15 - First push of local code to GitHub

About/Notes
-----------

Hey you, you scrolled to the end of the page! [Yeah](http://i.imgur.com/ZGfN8eb.gif)

Little background to this project.  I decided it was time I start learning some Python, so what better way than to learn it and get some fun results to play with.  I started out working on revamping the unsupported app store.  Currently I've created a way to search github for new channels and import them into the store and then install them.  Also you can remove channels from the store, maybe it's old or you don't want them anymore.  My version would allow you to import your own custom channels from Github and not have to worry about asking me to add them. This works but has some bugs in it still.  For now that project is on the back-burner since I've gotten tired of it as-well-as I'm unsure if it's OK to put the store back up on Github.

[Mangahere.bundle](https://github.com/Twoure/Mangahere.bundle) (based off of [Mangafox.bundle](https://github.com/hojel/Mangafox.bundle)) was my first attempt at creating a new channel.  I soon realized that the Service URL could not handle pulling consecutive page images, so I set out to find a site that presented all the album images on one page per chapter.  Thus KissManga.bundle was born.  Once I got the basics down for Kissmanga I noticed that the other Kiss sites were created similarly and would take some tweaking of my code to crawl each site.

This prompted me to make [KissNetwork.bundle](https://github.com/Twoure/KissNetwork.bundle).  I've tried to use Plex's built in framework as much as possible in hopes of maximizing cross platform compatibility.  It has been a fun project so far and has gotten me more comfortable with Python.  Have fun with it and let me know of any other issues or suggestions of how to make this faster and more user friendly.
