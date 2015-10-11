KissNetwork
===========

This is a plugin that creates a new channel in Plex Media Server to view content from these websites: [Kissanime.com](http://kissanime.com/), [Kissasian.com](http://kissasian.com/), [Kisscartoon.me](http://kisscartoon.me/), and [Kissmanga.com](http://kissmanga.com/). It is currently under development and as such, should be considered alpha software and potentially unstable. If you try it and it works for you (or if not!) please let me know.

**Note:** the author of this plugin has no affiliation with the Kiss sites or the owners of the content that they hosts.

Features
--------

- Watch video content across all Kiss sites (quality ranges from 360p to 1080p)
- Choose which Kiss sites to view content, hide others
- Read manga from Kissmanga
- Create custom Bookmarks
- Search all Kiss sites for videos/manga

System Requirements
-------------------

- **Plex Media Server**

  - Tested Working:
    - Linux
      - PMS version 0.9.12.13
      - [Ubuntu 14.04 x86_64 Linux 3.13.0-63-generic](http://i.imgur.com/ZiO7htR.png)
        - Installation of a Javascript runtime may be required
          - `sudo apt-get install nodejs` (installs nodejs)
    - Windows 10
      - PMS version 0.9.12.13

- **Plex Clients:**

  - Tested Working:
    - Plex Media Center / Home Theater (Ubuntu & Windows 10, same as above)
    - Android (4.4.2)
    - Plex/Web (2.4.23)
    - Chromecast (Videos)

  - Not Working:
    - Chromecast (Pictures)

How To Install
--------------

- [Download](http://github.com/Twoure/KissNetwork.bundle/zipball/master) and install it by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.

- Unzip and rename the folder to "KissNetwork.bundle"
- Copy KissNetwork.bundle into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
- ~~Restart PMS~~ **This is old, should not have to restart PMS.  If channel does not appear then Restart PMS**

Known Issues
------------

- General
  - Sometimes the headers are not set before Plex Framework tries to scrape the site.  This returns an error since the cookies need to be set before polling the site. I've added a pop-up message that says to wait about a second then try again.  Need to work on either threading with this issue, add a sleep function, or some kind of check that the headers are set before polling the site with the Plex Framework.

- Kiss(anime, asian, cartoon) are all hosted behind Cloudflare so added a modified version of [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape) as a work around
  - Cover art does not load for Videos
    - Plex Framework does not allow me to set hearders for directory object tumbs, still looking into this issue
    - I have added a local caching option for video bookmarks to work around cloudflare

- Chromecast does not work for Photo Albums but does for Videos, don't know why yet.  Assuming it has to do with how the Photo Albums are created.

- Kissmanga
  - For now Kissmanga is not behind the anit-bot rules, so it works
  - Sometimes the Cover Image do not display in the directory even though it has the image URL.
  - This is not a useful reader for the Plex/Web client, but works reasonably well for Smart phones and Plex Media Center.

- Plex Home Theater
  - thumbs don't show up on the left column but do for the buttons

Plans
-----

- General
  - Add preference to display __Sub__, __Dub__, or __Sub & Dub__ for videos
  - Might look into grouping seasons of the same show for the directory list
  - Try and display cover art for video items.  Not a thumb of the video, kiss sites don't include that data.
  - Implement some kind of Password protection for choosing which sites to display

- Bookmarks
  - Add option to add all seasons at once for a show
  - Group seasons into one show
  - Create separate directories for TV and Movies

- Search
  - Might try and restructure search setup to be faster and check for empty results before returning anything for the user

ChangeLog
---------

**0.03** - 10/11/15 - Major overhaul of headers.  No more 5 second wait time for each directory.

**0.02** - 10/09/15 - Fixed Windows 10 not displaying channel [issue](https://github.com/Twoure/KissNetwork.bundle/issues/1), and added site selection in channel preferences.

**0.01** - 10/03/15 - Initial version

**0.00** - 09/21/15 - First push of local code to GitHub

About/Notes
-----------

Hey you, you scrolled to the end of the page! [Yeah](http://i.imgur.com/ZGfN8eb.gif)

Little backgroud to this project.  I decided it was time I start learning some Python, so what better way than to learn it and get some fun results to play with.  I started out working on revamping the unsupported app store.  Currently I've created a way to search github for new channels and import them into the store and then install them.  Also you can remove channels from the store, maybe it's old or you don't want them anymore.  My version would allow you to import your own custom channels from Github and not have to worry about asking me to add them. This works but has some bugs in it still.  For now that project is on the backburner since I've gotten tired of it as-well-as I'm unsure if it's ok to put the store back up on Github.

[Mangahere.bundle](https://github.com/Twoure/Mangahere.bundle) (based off of [Mangafox.bundle](https://github.com/hojel/Mangafox.bundle)) was my first attempt at creating a new channel.  I soon realized that the service url could not handle pulling consecutive page images, so I set out to find a site that presented all the album images on one page per chapter.  Thus KissManga.bundle was born.  Once I got the basics down for Kissmanga I noticed that the other Kiss sites were created similarly and would take some tweaking of my code to crawl each site.

This prompted me to make [KissNetwork.bundle](https://github.com/Twoure/KissNetwork.bundle).  I've tried to use Plex's built in framework as much as possible in hopes of maximizing cross platform compatibility.  It has been a fun project so far and has gotten me more comfortable with Python.  Have fun with it and let me know of any other issues or suggestions of how to make this faster and more user friendly.
