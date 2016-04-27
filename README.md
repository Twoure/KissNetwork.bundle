KissNetwork
===========

## Table of Contents
- [Introduction](#introduction)
  - [Features](#features)
  - [Changelog](Changelog.md#changelog)
- [Channel Support](#channel-support)
  - [Plex Media Server](#plex-media-server)
  - [Plex Clients](#plex-clients)
- [Install](#install)
- [Operation](#operation)
  - [Preferences](#preferences)
    - [Sort List by...](#sort-list-by)
    - [View Anime, Cartoon, Comic, Drama, Manga](#view-anime-cartoon-comic-drama-manga)
    - [Preferred Video Server](#preferred-video-server)
    - [Cache All Covers Locally](#cache-all-covers-locally)
    - [Cache Bookmark Covers Locally](#cache-bookmark-covers-locally)
    - [Samsung Fix (disables remote play)](#samsung-fix-disables-remote-play)
    - [Force Transcoding (enables remote play)](#force-transcoding-enables-remote-play)
    - [Allow Adult Content](#allow-adult-content)
    - [Enable Developer Tools](#enable-developer-tools)
    - [Auth Admin Through Plex.tv](#auth-admin-through-plextv)
    - [Enable Debug Logging](#enable-debug-logging)
  - [About / Help](#about--help)
    - [Developer Tools](#developer-tools)
      - [Bookmark Tools](#bookmark-tools)
      - [Header Tools](#header-tools)
      - [Cover Cache Tools](#cover-cache-tools)
  - [Updater](#updater)
- [Issues](#issues)
  - [General](#general)
  - [Anime, Cartoon, Drama, Manga](#anime-cartoon-drama-manga)
  - [Manga, Comic](#manga-comic)
  - [Plex Home Theater](#plex-home-theater)
  - [OpenLoad-Stream](#openload)
- [Plans](#plans)
  - [General](#general-1)
  - [Bookmarks](#bookmarks)
- [About](#about)

## Introduction

This is a plugin that creates a new channel in [Plex Media Server](https://plex.tv/) to view content from these websites: [Kissanime.to](https://kissanime.to/), [Kissasian.com](http://kissasian.com/), [Kisscartoon.me](http://kisscartoon.me/), [Kissmanga.com](http://kissmanga.com/), and [ReadComicOnline.com](http://readcomiconline.com/). It is currently under development and as such, should be considered alpha software and potentially unstable. If you try it and it works for you (or if not!) please let me know.

> **Note:** the author of this plugin has no affiliation with the Kiss sites nor the owners of the content that they host.

[Table of Contents](#table-of-contents)

## Features

- Watch video content across all Kiss sites (quality ranges from 360p to 1080p)
- Choose which sites to view content, hide others
- Option to Block most _Adult_ content
- Read Manga from KissManga
- Read Comics from ReadComicOnline
- Create custom Bookmarks
- Search all sites for Videos/Manga/Comics

[Table of Contents](#table-of-contents)

## [Changelog](Changelog.md#changelog)

[Table of Contents](#table-of-contents)

## Channel Support

##### Plex Media Server:
- JavaScript Runtime Required:
  - Recomended Node.js or V8 (with or without the PyV8 module)
  - Refer to [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape#readme) for valid JavaScript Engines
  - For Ubuntu use: `sudo apt-get install nodejs` (installs nodejs)
- Tested Working:
  - Ubuntu 14.04 LTS: PMS version 0.9.16.6
  - Windows 7 & 10: PMS version 0.9.12.13

##### Plex Clients:
- Tested Working:
  - Plex Home Theater (Ubuntu 14.04 LTS, and Windows 7 & 10)
  - Android (4.4.2) (Plex Client App v4.24.2.563)
  - Plex Media Player (1.0.6)
  - Plex/Web (2.6.1)
  - Chromecast (Videos & Pictures)

[Table of Contents](#table-of-contents)

## Install

- [Download](https://github.com/Twoure/KissNetwork.bundle/releases) the latest release and install **KissNetwork** by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
  - Unzip and rename the folder to "KissNetwork.bundle"
  - Copy "KissNetwork.bundle" into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
  - ~~Restart PMS~~ **This is old, should not have to restart PMS.  If channel does not appear then Restart PMS**

Alternatively this channel can be installed via [WebTools.bundle](https://github.com/dagalufh/WebTools.bundle).

[Table of Contents](#table-of-contents)

## Operation

### Preferences

##### Sort List by...
- Set list order for "All", "Alphabets", "Country", "Genres", "Movies", "Ongoing", and "Completed"

##### View Anime, Cartoon, Comic, Drama, Manga
- If site enabled then it will be availible in the Channel for viewing. This includes Bookmarks and Searching.

##### Preferred Video Server
- Select a Default Video Server from the drop-down list
- Currently supported servers: KissNetwork(_default_), [Openload](https://openload.co/), [Stream](https://stream.moe/)
  - **Note:** Stream is experimental and requires [cURL](https://curl.haxx.se/). It is set to revert to GoogleVideo links if cURL is not present.
  - Default behavior: Use GoogleVideo links when available, otherwise try using the provided links
  - If a server other than _KissNetwork_ is selected: Use selected video server, and default to GoogleVideo links when selected server fails.

##### Cache All Covers Locally
- **Enabled:** Will download and index cover images
  - Overrides [Cache Bookmark Covers Locally](#cache-bookmark-covers-locally) function
- **Disabled(_default_):** Will remove all downloaded images from computer.
  - If "Cache Bookmark Covers Locally" is **Enabled**, then bookmark covers will be kept from deletion.

##### Cache Bookmark Covers Locally
- **Enabled:** AND "Cache All Covers Locally" **Disabled**, will download cover images and only display them in your "My Bookmarks" list.
- **Disabled(_default_):** AND 'Cache All Covers Locally" **Disabled**, will delete all bookmarked covers from computer.

##### Samsung Fix (disables remote play)
- **Enabled:** Turns On URL Redirect Function, making PMS follow the URL Redirect.
  - Follows URL through its redirect and returns the final URL
  - GoogleVideo Links: will expand around PMS IP rendering unusable outside of local network (i.e. remote play disabled)
- **Disabled(_default_):** URL Redirect is handled by client

##### Force Transcoding (enables remote play)
- OpenLoad videos have a hash tied to the PMS server IP.  Enable to watch OpenLoad videos outside the PMS local network.
- **Enabled:** Videos will be transcoded by PMS and available for use outside the servers network
  - Resolution will depend on available streams and client settings
  - Overrides [Samsung Fix](#samsung-fix-disables-remote-play), because PMS will properly handle any URL Redirects
- **Disabled(_default_):** Transcoding depends on clients settings/support

##### Allow Adult Content
- **Enabled:** Allows Adult Content to be viewed
- **Disabled(_default_):** Checks against contents _Genre_ list for adult themed genres. Current [block list](Contents/Code/__init__.py#L35).
  - Will provide a popup whenever an Adult themed video/comic/manga is accessed providing feedback as to why the content is blocked
  - Fails with KissCartoon because it does not have Adult themed _Genres_ but does have Adult content

##### Enable Developer Tools
- **Enabled:** Show Developer Tools Menu located in [About / Help](#about--help) section
- **Disabled(_default_):** Developer Tools Menu remains hidden
- Is only available to PMS admin regardless of enabled/disabled

##### Auth Admin Through Plex.tv
- Authenticate admin user through Plex.tv if Plex Media Server does not have Plex Home enabled
- **Enabled:** Auth against `https://plex.tv/user/account`
  - Use if PMS is _NOT_ setup as _Plex Home_
  - If plex.tv is down then this authentication will fail, locking the admin out from channel [Preferences](#preferences), [Updater](#updater), and [DevTools](#developer-tools) section
    - If this happens, open `Plug-in Support/Preferences/com.plexapp.plugins.kissnetwork.xml` and set `plextv` section to `false`. Save and exit file.
    - **Note 1:** if PMS is not setup as _Plex Home_ then admin features will now be available to all shared users
    - **Note 2:** when plex.tv comes online again, make sure to re-enable _Auth Admin Trough Plex.tv_ to ensure shared users are not allowed admin access
- **Disabled(_default_):** Auth against `http://127.0.0.1:32400/myplex/account`
  - Use when PMS is setup as _Plex Home_
  - **Note:** If PMS _NOT_ setup as _Plex Home_ then all shared users will have admin access
- If using Plex Web Client on Host Server Machine and not signed-in, then no Plex Token will be available to authenticate.  In this use case, the assumption is you are the admin so the channel will treat you as such.

##### Enable Debug Logging
- Turn on extra logging for debugging purposes

[Table of Contents](#table-of-contents)

### About / Help

##### Developer Tools
- [**Bookmark Tools**](#bookmark-tools)
- [**Header Tools**](#header-tools)
- [**Cover Cache Tools**](#cover-cache-tools)
- **Reset Domain_Dict File:** Create backup of old Domain_Dict, then delete current, and write new Domain_Dict with freash domains
- **Reset Dict cfscrape Test Key:** Delete test key and then force the channel to retake the cfscrape test. It is testing for a valid JavaScript Runtime
- **Restart KissNetwork Channel:** Will restart KissNetwork Channel in PMS, but will not refresh URL Service Code.

##### Bookmark Tools
- **Toggle Hiding "Clear Bookmarks" Function:** For those of us who accidentally delete our bookmarks but don't mean to
- **Reset "All" Bookmarks:** Same as "Clear All Bookmarks"
- **Reset "Anime" Bookmarks:** Same as "Clear Anime Bookmarks"
- **Reset... :** Same for Drama, Cartoon, Comic, and Manga

##### Header Tools
- **Reset Header_Dict File:** Create backup of old Header_Dict, then delete current, and write new Header_Dict with freash headers
- **Update Anime Headers:** Update Anime Headers in the `Header_Dict` file only
- **Update... :** Same for Drama, Cartoon, Comic, and Manga

##### Cover Cache Tools
- The Cache Cover tools are experimental, and could result in a temporary IP ban from using the Kiss sites. If this happens, just wait for the allotted time to pass (usually an hour, but could be up to 24 hours, do not remember).  I have yet to hear people report this issue, but did encounter it while developing these tools since I had to test and re-test the download functions multiple times.
- **Cache All Covers:** Download cover images from all sites.  Background process.
- **Cache All Anime Covers:** Download All Anime covers only.  Do not download covers from the other sites.
- **Cache All... :** Same for Drama, Cartoon, Comic, and Manga
- **Reset Resources Directory:** Clean dirty image cache in `Resources` directory.  Will delete all cached images and remove cache images Dict key.

### Updater

- Update button visible only to PMS admin and when update avalible
- Checks KissNetwork.bundle Github [atom feed](https://github.com/Twoure/KissNetwork.bundle/commits/master.atom) every 12 hours.

[Table of Contents](#table-of-contents)

## Issues

##### General
- Cookie cache times keep changing. I try and keep these up-to-date, untill I create a checker for valid cookie cache times.
- First time the Channel runs (this means ever, not every time it starts just the first time) you need to wait about 20-30 seconds for the headers to be set.
- If the headers are not set before Plex Framework tries to scrape the site then an error will occur.
- Kissasian.com (Drama) has a very short cache time for its cookies, about 30-45 minutes.  This can bog down the Search function (only if Drama section enabled) since the Drama section will need re-caching after 30 minutes have passed since the last time it was cached.  You should notice a 5 second delay if it is re-caching the Drama section (or any one of the sites, if two sites have to re-cache then it may take 10 seconds etc...).
- Episode, Movie, VideoClip data may be incorrect depending on how the shows are archived on the Kiss sites.  I've accounted for most variations but some info will still be incorrect.

##### Anime, Cartoon, Drama, Manga
- Hosted behind Cloudflare so added a modified version of [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape) as a work around
- **Kisscartoon** has no "Mature" filter/genre so my Adult Prefs Optioin cannot filter out Adult Cartoons
- Cover art does not load for Videos
  - Plex Framework does not allow me to set headers for directory object thumbs, still looking into this issue
  - I have added a local cover image caching option to work around cloudflare
- Cookie timeouts change too often, cannot parse expire time yet

##### Manga, Comics
- Kissmanga/ReadComicOnline is not the most useful reader for the _Plex Web_ client, but works reasonably well for Smart Phones, PMP, and PHT.

##### Plex Home Theater
- Channel exits when adding/removing bookmarks.  Has to do with pop up messages.
  - Working to fix this.  Have new message.py but have yet to integrate with bookmarks fully

##### OpenLoad, Stream
- OpenLoad and Stream links have a hash tied to your PMS IP.  To use these Servers outside your home network, enable [Force Transcoding](#force-transcoding-enables-remote-play).  Force transcoding will make video links compatible with all clients.

[Table of Contents](#table-of-contents)

## Plans

##### General
- Might look into grouping seasons of the same show for the directory list
- Continue Improving Metadata
- Remove Page previous to Season Page if only one Season present

##### Bookmarks
- Add option to add all seasons at once for a show
- Group seasons into one show
- Create separate directories for TV and Movies
- Might move bookmarks to own file like I did with Header_Dict
- Add Bookmark backup option, with function to restore old bookmarks

[Table of Contents](#table-of-contents)

## About

Hey you, you scrolled to the end of the page! [Yeah](http://i.imgur.com/ZGfN8eb.gifv)

Little background to this project.  I decided it was time I start learning some Python, so what better way than to learn it and get some fun results to play with.  I started out working on revamping the unsupported app store.  Currently I've created a way to search github for new channels and import them into the store and then install them.  Also you can remove channels from the store, maybe it's old or you don't want them anymore.  My version would allow you to import your own custom channels from Github and not have to worry about asking me to add them. This works but has some bugs in it still.  For now that project is on the back-burner since I've gotten tired of it as-well-as I'm unsure if it's OK to put the store back up on Github.

[Mangahere.bundle](https://github.com/Twoure/Mangahere.bundle) (based off of [Mangafox.bundle](https://github.com/hojel/Mangafox.bundle)) was my first attempt at creating a new channel.  I soon realized that the Service URL could not handle pulling consecutive page images, so I set out to find a site that presented all the album images on one page per chapter.  Thus KissManga.bundle was born.  Once I got the basics down for Kissmanga I noticed that the other Kiss sites were created similarly and would take some tweaking of my code to crawl each site.

This prompted me to make [KissNetwork.bundle](https://github.com/Twoure/KissNetwork.bundle).  I've tried to use Plex's built in framework as much as possible in hopes of maximizing cross platform compatibility.  It has been a fun project so far and has gotten me more comfortable with Python.  Have fun with it and let me know of any other issues or suggestions of how to make this faster and more user friendly.

[Table of Contents](#table-of-contents)
