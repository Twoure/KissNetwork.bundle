KissNetwork
===========

## Table of Contents
- [Introduction](#introduction)
  - [Version](#version)
  - [Features](#features)
  - [Changelog](Changelog.md)
- [Channel Support](#channel-support)
  - [Plex Media Server](#plex-media-server)
  - [Plex Clients](#plex-clients)
- [Install](#install)
- [Operation](#operation)
  - [Preferences](#preferences)
    - [Sort List by...](#sort-list-by)
    - [View Kiss(Anime, Asian, Cartoon, Manga)](#view-kissanime-asian-cartoon-manga)
    - [Cache All Covers Locally](#cache-all-covers-locally)
    - [Cache Bookmark Covers Locally](#cache-bookmark-covers-locally)
    - [Allow Adult Content](#allow-adult-content)
    - [Enable Developer Tools](#enable-developer-tools)
  - [About / Help](#about--help)
    - [Developer Tools](#developer-tools)
      - [Bookmark Tools](#bookmark-tools)
      - [Header Tools](#header-tools)
      - [Cover Cache Tools](#cover-cache-tools)
  - [Updater](#updater)
- [Issues](#issues)
  - [General](#general)
  - [Kiss(Anime, Asian, Cartoon, Manga)](#kissanime-asian-cartoon-manga)
  - [Chromecast](#chromecast)
  - [Plex Home Theater](#plex-home-theater)
- [Plans](#plans)
  - [General](#general-1)
  - [Bookmarks](#bookmarks)
- [About](#about)

## Introduction

This is a plugin that creates a new channel in [Plex Media Server](https://plex.tv/) to view content from these websites: [Kissanime.to](https://kissanime.to/), [Kissasian.com](http://kissasian.com/), [Kisscartoon.me](http://kisscartoon.me/), and [Kissmanga.com](http://kissmanga.com/). It is currently under development and as such, should be considered alpha software and potentially unstable. If you try it and it works for you (or if not!) please let me know.

> **Note:** the author of this plugin has no affiliation with the Kiss sites nor the owners of the content that they host.

[Table of Contents](#table-of-contents)

## Version

Current Version: `1.0.1`

[Table of Contents](#table-of-contents)

## Features

- Watch video content across all Kiss sites (quality ranges from 360p to 1080p)
- Choose which Kiss sites to view content, hide others
- Option to Block most Adult content
- Read manga from Kissmanga
- Create custom Bookmarks
- Search all Kiss sites for videos/manga

[Table of Contents](#table-of-contents)

## [Changelog](Changelog.md)

[Table of Contents](#table-of-contents)

## Channel Support

##### Plex Media Server:
- JavaScript Runtime Required:
    - Recomended Node.js or V8 (with or without the PyV8 module)
    - Refer to [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape#readme) for valid JavaScript Engines
    - For Ubuntu use: `sudo apt-get install nodejs` (installs nodejs)
- Tested Working:
  - Ubuntu 14.04 LTS: PMS version 0.9.12.19
  - Windows 7 & 10: PMS version 0.9.12.13

##### Plex Clients:
- Tested Working:
  - Plex Home Theater (Ubuntu 14.04 LTS, and Windows 7 & 10)
  - Android (4.4.2)
  - Plex/Web (2.4.23)
  - Chromecast (Videos)
- Not Working:
  - Chromecast (Pictures)

[Table of Contents](#table-of-contents)

## Install

- [Download](https://github.com/Twoure/KissNetwork.bundle/archive/master.zip) and install KissNetwork by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
  - Unzip and rename the folder to "KissNetwork.bundle"
  - Copy KissNetwork.bundle into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
  - ~~Restart PMS~~ **This is old, should not have to restart PMS.  If channel does not appear then Restart PMS**

[Table of Contents](#table-of-contents)

## Operation

### Preferences

##### Sort List by...
- Set list order for "All", "Alphabets", "Genres", and "Movies"

##### View Kiss(Anime, Asian, Cartoon, Manga)
- If site enabled then it will be availible in the Channel for viewing. This includes Bookmarks and Searching.

##### Cache All Covers Locally
- Overrides [Cache Bookmark Covers Locally](#cache-bookmark-covers-locally) function
- If enabled, will download and index cover images
- If disabled, will remove all downloaded images from computer. If "Cache Bookmark Covers Locally" is True, then bookmark covers will be kept from deletion.

##### Cache Bookmark Covers Locally
- If enabled AND "Cache All Covers Locally" is False, will download cover images and only display them in your "My Bookmarks" list.
- If disabled AND 'Cache All Covers Locally" is False, will delete all bookmarked covers from computer.

##### Allow Adult Content
- Attempt to block adult content from the kiss sites. If content blocked, then will removed adult themed genres from genre list and provide a popup whenever an adult video/manga is accessed providing feedback as to why the content is blocked.

##### Enable Developer Tools
- Hide/Un-Hide Developer Tools Menu located in [About / Help](#about--help) section

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
- **Reset... :** Same for Drama, Cartoon, and Manga

##### Header Tools
- **Reset Header_Dict File:** Create backup of old Header_Dict, then delete current, and write new Header_Dict with freash headers
- **Update Anime Headers:** Update Anime Headers in the `Header_Dict` file only
- **Update... :** Same for Drama, Cartoon, and Manga

##### Cover Cache Tools
- **Cache All Covers:** Download cover images from all sites.  Background process.
- **Cache All Anime Covers:** Download All Anime covers only.  Do not download covers from the other sites.
- **Cache All... :** Same for Drama, Cartoon, and Manga
- **Reset Resources Directory:** Clean dirty image cache in `Resources` directory.  Will delete all cached images and remove cache images Dict key.

### Updater

- Update button visible only when update avalible
- Checks KissNetwork.bundle Github [atom feed](https://github.com/Twoure/KissNetwork.bundle/commits/master.atom) every 12 hours.

[Table of Contents](#table-of-contents)

## Issues

##### General
- Cookie cache times keep changing. I try and keep these up-to-date, untill I create a checker for valid cookie cache times.
- First time the Channel runs (this means ever, not every time it starts just the first time) you need to wait about 20-30 seconds for the headers to be set.
- If the headers are not set before Plex Framework tries to scrape the site then an error message will popup saying you need to wait until the headers are set.
- Kissasian.com (Drama) has a very short cache time for its cookies, about 30-45 minutes.  This can bog down the Search function (only if Drama section enabled) since the Drama section will need re-caching after 30 minutes have passed since the last time it was cached.  You should notice a 5 second delay if it is re-caching the Drama section (or any one of the sites, if two sites have to re-cache then it may take 10 seconds etc...).
- Episode, Movie, VideoClip data may be incorrect depending on how the shows are archived on the Kiss sites.  I've accounted for most variations but some info will still be incorrect.
- Sometimes the date the video aired only has a year.  If this is the case then the metadata will set the originally_available_at to the current month and day with the year from the video.  Also aired dates are when the season started or movie came out, so not the actual date the episode aired.

##### Kiss(Anime, Asian, Cartoon, Manga)
- Hosted behind Cloudflare so added a modified version of [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape) as a work around
- Kisscartoon has no "Mature" filter/genre so my Adult Prefs Optioin cannot filter out Adult Cartoons
- Cover art does not load for Videos
  - Plex Framework does not allow me to set headers for directory object thumbs, still looking into this issue
  - I have added a local cover image caching option to work around cloudflare
- Kissmanga is not the most useful reader for the Plex/Web client, but works reasonably well for Smart phones and Plex Media Center.
- Cookie timeouts change too often, cannot parse expire time yet

##### Chromecast
- does not work for Photo Albums but does for Videos, don't know why yet.  Assuming it has to do with how the Photo Albums are created.

##### Plex Home Theater
- Channel exits when adding/removing bookmarks.  Has to do with pop up messages.

[Table of Contents](#table-of-contents)

## Plans

##### General
- Might look into grouping seasons of the same show for the directory list
- Implement some kind of Password protection for choosing which sites to display
- Continue Improving Metadata

##### Bookmarks
- Add option to add all seasons at once for a show
- Group seasons into one show
- Create separate directories for TV and Movies
- Might move bookmarks to own file like I did with Header_Dict

[Table of Contents](#table-of-contents)

## About

Hey you, you scrolled to the end of the page! [Yeah](http://i.imgur.com/ZGfN8eb.gif)

Little background to this project.  I decided it was time I start learning some Python, so what better way than to learn it and get some fun results to play with.  I started out working on revamping the unsupported app store.  Currently I've created a way to search github for new channels and import them into the store and then install them.  Also you can remove channels from the store, maybe it's old or you don't want them anymore.  My version would allow you to import your own custom channels from Github and not have to worry about asking me to add them. This works but has some bugs in it still.  For now that project is on the back-burner since I've gotten tired of it as-well-as I'm unsure if it's OK to put the store back up on Github.

[Mangahere.bundle](https://github.com/Twoure/Mangahere.bundle) (based off of [Mangafox.bundle](https://github.com/hojel/Mangafox.bundle)) was my first attempt at creating a new channel.  I soon realized that the Service URL could not handle pulling consecutive page images, so I set out to find a site that presented all the album images on one page per chapter.  Thus KissManga.bundle was born.  Once I got the basics down for Kissmanga I noticed that the other Kiss sites were created similarly and would take some tweaking of my code to crawl each site.

This prompted me to make [KissNetwork.bundle](https://github.com/Twoure/KissNetwork.bundle).  I've tried to use Plex's built in framework as much as possible in hopes of maximizing cross platform compatibility.  It has been a fun project so far and has gotten me more comfortable with Python.  Have fun with it and let me know of any other issues or suggestions of how to make this faster and more user friendly.

[Table of Contents](#table-of-contents)
