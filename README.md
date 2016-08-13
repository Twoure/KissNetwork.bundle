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
    - [Simple UI](#simple-ui)
    - [Sort List by...](#sort-list-by)
    - [View Anime, Cartoon, Comic, Drama, Manga](#view-anime-cartoon-comic-drama-manga)
    - [Preferred Video Server](#preferred-video-server)
    - [Hide "Clear Bookmarks"](#hide-clear-bookmarks)
    - [Force Redirect Fix (disables remote play)](#force-redirect-disables-remote-play)
    - [Force Transcoding (enables remote play)](#force-transcoding-enables-remote-play)
    - [Allow Adult Content](#allow-adult-content)
    - [Enable Developer Tools](#enable-developer-tools)
    - [Auth Admin Through Plex.tv](#auth-admin-through-plextv)
    - [Enable Debug Logging](#enable-debug-logging)
  - [About / Help](#about--help)
    - [Developer Tools](#developer-tools)
      - [Bookmark Tools](#bookmark-tools)
      - [Cache Tools](#cache-tools)
      - [Domain Tools](#domain-tools)
      - [Header Tools](#header-tools)
  - [Updater](#updater)
- [Issues](#issues)
  - [General](#general)
  - [Anime, Cartoon, Drama, Manga](#anime-cartoon-drama-manga)
  - [Cartoon](#cartoon)
  - [Manga, Comic](#manga-comic)
  - [Plex Home Theater](#plex-home-theater)
  - [OpenLoad, Stream](#openload-stream)
- [Plans](#plans)
  - [General](#general-1)
  - [Bookmarks](#bookmarks)
- [Support](#support)
- [About](#about)

## Introduction

This plugin creates a new channel within [Plex Media Server](https://plex.tv/) (PMS) to view content from these websites: [Kissanime.to](https://kissanime.to/), [Kissasian.com](http://kissasian.com/), [Kisscartoon.me](http://kisscartoon.me/), [Kissmanga.com](http://kissmanga.com/), and [ReadComicOnline.com](http://readcomiconline.com/). It is currently under development and as such, should be considered alpha software and potentially unstable. If you try it and it works for you (or if not!) please let me know.

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
- Tested Working:
  - Ubuntu 14.04 LTS: PMS version 1.0.3
  - Windows 7: PMS version 0.9.16.6

##### Plex Clients:
- Tested Working:
  - Plex Home Theater (Ubuntu 14.04 LTS, v1.4.1)
  - OpenPHT (Ubuntu 14.04 LTS, v1.6.2)
  - Android (4.4.2) (Plex Client App, v4.29.1.7)
  - Plex Media Player (1.1.4)
  - Plex/Web (2.7.7)
  - Chromecast (Videos & Pictures)

[Table of Contents](#table-of-contents)

## Install

- This channel can be installed via [WebTools.bundle](https://github.com/dagalufh/WebTools.bundle) or manually follow the directions below.
- [Download](https://github.com/Twoure/KissNetwork.bundle/releases) the latest release and install _KissNetwork_ by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
  - Unzip and rename the folder to **KissNetwork.bundle**
  - Copy **KissNetwork.bundle** into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
  - Restart PMS

[Table of Contents](#table-of-contents)

## Operation

### Preferences

##### Simple UI
- Remove all sub list in favor of one list per section sorted by the [Sort List by...](#sort-list-by) option.

##### Sort List by...
- Set list order for "All", "Alphabets", "Country", "Genres", "Movies", "Ongoing", and "Completed"

##### View Anime, Cartoon, Comic, Drama, Manga
- If site enabled then it will be availible in the Channel for viewing. This includes Bookmarks and Searching.

##### Preferred Video Server
- Select a Default Video Server from the drop-down list
- Currently supported servers: KissNetwork(_default_), [Openload](https://openload.co/), [Stream](https://stream.moe/)
  - Default behavior: Use GoogleVideo links when available, otherwise try using the provided links
  - If a server other than _KissNetwork_ is selected: Use selected video server, and default to GoogleVideo links when selected server fails.

##### Hide "Clear Bookmarks"
- **Enabled:** Hide the _Clear Bookmarks_ function within Main Bookmarks menu and sub-menus
- **Disabled(_default_):** Allow the _Clear Bookmarks_ function within Main Bookmarks menu and sub-menus

##### Force Redirect (disables remote play)
- **Enabled:** Turns On URL Redirect Function, making PMS follow the URL Redirect.
  - Follows URL through its redirect and returns the final URL
  - _GoogleVideo_ Links: expand around PMS IP rendering unusable outside of local network _(i.e. remote play disabled)_
- **Disabled(_default_):** URL Redirect is handled by client

##### Force Transcoding (enables remote play)
- Openload/Stream.moe videos have a hash tied to the PMS server IP.  Enable to watch Openload/Stream.moe videos outside the PMS local network.
- **Enabled:** Videos will be transcoded by PMS and available for use outside the servers network
  - Resolution will depend on available streams and client settings
  - Overrides [Force Redirect](#force-redirect-disables-remote-play), because PMS will properly handle any URL Redirects
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
- [**Cache Tools**](#cache-tools)
- [**Domain Tools**](#domain-tools)
- [**Header Tools**](#header-tools)
- **Reset Dict cfscrape Test Key:** Delete test key and then force the channel to retake the cfscrape test.
- **Restart KissNetwork Channel:** Will restart KissNetwork Channel in PMS, but will not refresh URL Service Code.

##### Bookmark Tools
- **Backup Tools:**
  - _Backup Bookmarks_ - Creates a Backup file of all bookmarks
  - _Delete Backups_ - Open menu to Detele old bookmark backups
  - _Load Bookmarks from Backup_ - Open menu to Load bookmarks from previously created backup file
- **Toggle Hiding "Clear Bookmarks" Function:** For those of us who accidentally delete our bookmarks but don't mean to
- **Reset "All" Bookmarks:** Same as "Clear All Bookmarks"
- **Reset "Anime" Bookmarks:** Same as "Clear Anime Bookmarks"
- **Reset... :** Same for Drama, Cartoon, Comic, and Manga

##### Cache Tools
- **Reset DataCovers Cache:** Force Remove all cached _Covers_ from DataCovers directory.
- **Reset DataHTTP Cache:** Force Remove all cached _URLs_ from DataHTTP directory.

##### Domain Tools
- **Reset Domain_Dict File:** Create backup of old Domain_Dict, then delete current, and write new Domain_Dict with freash domains
- **Update Anime Domain:** Update Anime Domain in the `Domain_Dict` file only
- **Update... :** Same for Drama, Cartoon, Comic, and Manga

##### Header Tools
- **Reset Header_Dict File:** Create backup of old Header_Dict, then delete current, and write new Header_Dict with freash headers
- **Update Anime Headers:** Update Anime Headers in the `Header_Dict` file only
- **Update... :** Same for Drama, Cartoon, Comic, and Manga

### Updater
- Update button visible only to PMS admin and when update avalible
- Checks KissNetwork.bundle Github [atom feed](https://github.com/Twoure/KissNetwork.bundle/commits/master.atom) every 12 hours.

[Table of Contents](#table-of-contents)

## Issues

##### General
- First time channel runs after installation or an upgrade, you may see a message saying to wait untile the headers are cached.  This is normal behavior.
- Episode, Movie, VideoClip data may be incorrect depending on how the shows are archived on the Kiss sites.  I've accounted for most variations but some info will still be incorrect.

##### Anime, Cartoon, Drama, Manga, Comics
- Hosted behind Cloudflare so added a modified version of [cloudflare-scrape](https://github.com/Anorov/cloudflare-scrape) as a work around

##### Cartoon
- No _Mature_ filter/genre so Adult Prefs Option cannot filter out Adult Cartoons

##### Manga, Comics
- Kissmanga/ReadComicOnline is not the most useful reader for the _Plex Web_ client, but works reasonably well for Smart Phones, PMP, and PHT.

##### Drama
- Keeps changing video URL obfuscation every so often.  Am able to decode daily, but will not be creating a new release every day it changes.  Depends on current frequency of changes.
- If and when _Drama_ videos start failing _(when obfuscation changes)_, users can try the `dev` branch code, or Switch the server pref to Openload or Stream.
- Header Cache time is very short, ~30-45 minutes, so can bog down Search Function

##### Plex Home Theater
- Channel exits when adding/removing bookmarks.  Has to do with pop up messages.
  - Working to fix this.  Have new message.py but have yet to integrate with bookmarks fully

##### Openload, Stream
- Openload/Stream.moe links have a hash tied to your PMS IP.  To use these Servers outside your home network, enable [Force Transcoding](#force-transcoding-enables-remote-play).  Force transcoding will make video links compatible with all clients.

[Table of Contents](#table-of-contents)

## Plans

##### General
- Might look into grouping seasons of the same show for the directory list
- Continue Improving Metadata
- Change Itempage to TVShowObject, so have Bookmark function within TVShowObject.

##### Bookmarks
- Add option for user to add custom bookmark backup path
- Improve bookmark backup functions, may setup rotating file style
- Add option to add all seasons at once for a show
- Group seasons into one show
- Might create separate directories for TV and Movies
- Might move bookmarks to own file like I did with Header_Dict

[Table of Contents](#table-of-contents)

## Support

- [Plex Forums Thread](https://forums.plex.tv/discussion/186988)
- [GitHub Issues](https://github.com/Twoure/KissNetwork.bundle/issues)

[Table of Contents](#table-of-contents)

## About

Hey you, you scrolled to the end of the page! [Yeah](http://i.imgur.com/ZGfN8eb.gifv)

Little background to this project.  I decided it was time I start learning some Python, so what better way than to learn it and get some fun results to play with.

[Mangahere.bundle](https://github.com/Twoure/Mangahere.bundle) (based off of [Mangafox.bundle](https://github.com/hojel/Mangafox.bundle)) was my first attempt at creating a new channel.  I soon realized that the URL ServiceCode could not handle pulling consecutive page images, so I set out to find a site that presented all the album images on one page per chapter.  Thus KissManga.bundle was born.  Once I got the basics down for Kissmanga I noticed that the other Kiss sites were created similarly and would take some tweaking of my code to crawl each site.

This prompted me to make [KissNetwork.bundle](https://github.com/Twoure/KissNetwork.bundle).  I've tried to use Plex's built in framework as much as possible in hopes of maximizing cross platform compatibility.  It has been a fun project so far and has gotten me more comfortable with Python.  Have fun with it and let me know of any other issues or suggestions of how to make this faster and more user friendly.

[Table of Contents](#table-of-contents)
