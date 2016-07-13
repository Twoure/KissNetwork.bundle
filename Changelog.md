# ChangeLog

##### 1.2.4
- _07/13/2016_
  - Updated decryption to use Plex Framework, removed unused code
  - Updated code to better handle domain name changes
  - Changed legacy bookmark update to match against `https` for kissanime
    - will cause issues when/if kissanime changes back to `https`
    - will look into better solution for next release

##### 1.2.3
- _07/01/2016_
  - `cloudflare-scrape`: updated to `v1.6.5`
  - Added default bitrate info to Videos
  - Improved Node.js uses with link decryption
    - If Server using Node.js, then execute javascript in virtual machine (vm)

##### 1.2.2
- _06/15/2016_
  - Fixes:
    - `DevTools`: `CacheAllCovers` error
    - `DevTools`: bookmark tools, load bookmark error when loading fresh bookmarks
    - `CFTest`: input errors
    - Openload: fixed for site changes
  - Updates:
    - `KissDecrypt.pys`: KissAsian updated to `v5` decryption _(they are changing it every day so don't expect this to work long)_
    - `rhtml.py`: added new HTTP 522 exception
    - `PyExecJS`: added `v1.1.0` as fallback
    - `PlayVideo`: added Openload redirect if kiss server video not present
    - `headers.pys`: added added javascript runtime engine test info to `CFTest`
    - `headers.pys`: updated `set_header` to skip off line sites _(still in testing)_
    - `CFTest`: changed test site to manga
    - `DefaultPrefs.json`: changed default pref for _Enable Debug Logging_ to `True`.  Allows errors to be caught on first run.
    - `cloudflare-scrape`: updated to `v1.6.4`
    - Stream.moe: site resolved ssl error. Removed `curl` code, and updated video URL code.

##### 1.2.1
- _06/05/2016_
  - Fixes:
    - `KissDecrypt.pys` KissCartoon updated to `v3` decryption
    - Comic cover URLs, added to caching rules
    - First attempt at error handling for offline host
    - Many DevTools errors
    - Common error within `headers.pys`
    - Common error within `CFTest` function
  - Updates:
    - `cloudflare-scrape` _v1.6.3_
    - `PyExecJS` _v1.4.0_
    - `six` _v1.10.0_ _(required for `PyExecJS` v1.4.0)_
    - Added new Related links
    - Improved dynamic domain handling
    - Improved cookie expire time handling
    - New Bookmark Backup tools within DevTools
    - Improved URL caching
    - Added Reset URL cache to DevTools
    - Switched to `Core` when available
    - New Domain tools within DevTools

##### 1.2.0
- _05/07/2016_
  - Fixed Kissasian video URL decryption v3
  - Updated `Info.plist`, removed unused code

##### 1.1.9
- _05/01/2016_
  - Fixes:
    - `Kissenc.pys` spelling error, updated an equality
    - PHT and OpenPHT Bookmark message error when bookmarks cleared
    - Tuple error in GetBaseURL function
    - Logging and SaveImage errors in DevTools
    - cfscrape test, would fail to import when no Java found
  - Updates:
    - New URL caching
    - New `HTTP 503` error handling for `requests`. Will try and pull fresh headers if `HTTP 503` error occurs.
    - Cleaned old code
    - Cleaned logging

##### 1.1.8
- _04/27/2016_
  - Fixes:
    - KissAsian and KissCartoon new Video URL encryption
    - Header_Dict empty file check
    - ShowSubPage message container
    - cfscrape status_code error: was being called before execution
  - Updates:
    - Optimize Openload, Domain, and GetThumb code
    - Updated requests lib to v2.9.1
    - Switched all Kiss URLs to requests library, no longer using Plex Framework
    - Added new Stream.moe server
      - Requires cURL to work
      - Only tested on Linux
    - Switched to requests.head in domain.pys
    - Switched to requests.head for URL Redirect
    - Up-to-date User-Agent

##### 1.1.7
- _03/21/2016_
  - Fixed Service Code file path error

##### 1.1.6
- _03/17/2016_
  - Fixes:
    - BackgroundAutoCache error
    - Season were binned incorrectly. Season 0 has no episode limit now.  Still some minor errors but all episodes will display in some format.
    - Episode dates added back for cients that do not support show date aired
  - Updates:
    - Added 480p stream support
    - Added option to Prefer **OpenLoad** video links.  In case the provided GoogleVideo links fail to play
    - Better Transcoding options.  Now supports selecting resolution.
      - If Transcoding is selected, then _Samsung Fix_ is disabled.
      - If server is trascoding, then it will correctly handle the URL redirect, so _Samsung Fix_ would be irrelevant
    - Added back Artwork for Menus on mobile phones
    - Added webm and flv resolution support when Force Transcoding enabled
    - Added additional 480p format (78) incase site changes
    - Added logging to report resolution used when video played
    - Added [Steamy.moe](https://steamy.moe/) video host support. Example usage: [Star Wars Rebels S2E17](http://kisscartoon.me/Cartoon/Star-Wars-Rebels-Season-2/Episode-17-New-Host-2?id=68897)
    - Added Short summary info for SeasonObjects
    - Added Default Artwork to DirectoryObject and PopupDirectoryObject
    - Updated descriptions in README

##### 1.1.5
- _03/12/2016_
  - Fixed Comic upgrade
  - Removed kissanime domain change

##### 1.1.4
- _03/12/2016_
  - Fixes:
    - Added _Force Transcoding_ to prefs to fix OpenLoad video remote play
      - OpenLoad videos have a hash tied to the PMS IP.  This is fine for playing videos inside the PMS network, but not for remote play.
      - _Force Transcoding_ removes video formatting metadata, forcing PMS to transcode the now unknow video format
      - The New Redirect Follower does not work with OpenLoad links, so the Transcoder is needed for clients that cannot follow redirects
    - OpenLoad site changes.  No access to `getdllink` anymore.
  - Updates:
    - Added ReadComicOnline as Comic Section
    - Comic and Manga sections: Reversed the list, newest chapters show first
    - New URL Redirect Follower

##### 1.1.3
- _03/07/2016_
  - Fixes:
    - GoogleVideo links: some links were of a different style
  - Updates:
    - Added logging for Video host
    - Looks like Kiss Sites are going with OpenLoad for now, and Removing OneDrive links

##### 1.1.2
- _03/06/2016_
 - Fixes:
   - Reduced kissanime and kissmanga cache time to 20 hrs
   - Removed ASP.Net_SessionId from cookie string. Should help with some of the cookie caching issues.
   - KissManga Chromecast support
 - Updates/New:
   - Added Onedrive and Openload video support
   - New SeasonObject and TVShowObject, now TV episodes can play back-to-back on supported clients
   - Cleaned KissVideo service code, finished integrating in new metadata.pys

##### 1.1.1
- _03/04/2016_
- Fixes:
  - Samsung Fix, Prefs were not updated correctly, fixed this.
  - OneDrive video error.  Still cannot play Onedrive videos.  Added popup to notify user.
  - Headers only cache for selected site in Prefs now.
    - The first time the channel ever runs it will still cache all headers.
    - After first time ever run, it will then only cache the sites selected in Prefs
  - AuthTools: fixed when user is not logged into server.
- Updates:
  - Split Developer code into it's own code
  - Started to implement new Metadata function
  - Condenced code
  - If only one site is selected in Prefs, then That sites Menus return directly for Main Menu, Bookmarks, and Search
  - Added 5 sec timeout to URL redirect function in KissVideo code.

##### 1.1.0
- _02/20/2016_
- Fixes:
  - Samsung Fix reads Preferences file directly now (no token required)
- Updates:
  - Added extra logging for Clients and Platform

##### 1.0.9
- _02/13/2016_
- Fixes:
  - Added Samsung Fix to Preferences
    - Adds back URL Redirect function, but disables remote play
    - If enabled, videos will only work within the host network
- Updates:
  - Preferences and DevTools only available to Admin Plex Account

##### 1.0.8
- _02/05/16_
- Fixes:
  - KissCartoon Covers, and any other covers no longer hosted on kiss sites
  - Bookmark Covers
  - CreateHeadersDict()
  - KissAsian directory list
  - KissManga special characters in Page URL
- Update:
  - Added ASP.Net_SessionId to cfscraper
  - Removed URL expand.  Was expanding the wrong IP for remote play
  - Changed KissCartoon cookie cache time from 7 days to 5 days

##### 1.0.7
- _01/21/16_
- New:
  - Added [DumbTools](https://github.com/coryo/DumbTools-for-Plex)
  - Input and Prefs directory support for "dumb" clients

##### 1.0.6
- _12/12/15_
- Update/New:
  - New: Status list, Ongoing and Completed
  - Update: Moved Top list into own list
  - Update: Removed _Latest_ from _Not Yet Aired_ title

##### 1.0.5
- _12/10/15_
- Expand PlayVideo URL in KissVideo ServiceCode.  Returns direct link now instead of redirect.

##### 1.0.4
- _12/02/15_
- Fixes:
  - KissCartoon Top Pages show page url
- Update/New:
  - New: Default Artwork for Search

##### 1.0.3
- _11/30/15_
- Added _KissCartoon_ back in. KissCartoon site fixed cookie issue

##### 1.0.2
- _11/30/15_
- Fixes:
  - Removed _KissCartoon_ until cookie issue solved
  - Fixed int error in service code
- Udate/New
  - Changed to different updater
  - Optimized bookmark code

##### 1.0.1
- _11/27/15_
- Update: Added check for broken or missing videos

##### 1.0.0
- _11/24/15_
- Fixes:
  - Cover image URLs, Summary, KissAnime _https_, KissAnime Bookmarks
- Update/New:
  - New: [Updater](https://github.com/mikew/plex-updater) (same as ss-plex)
  - New: Cache All Covers in background
  - Update: Bookmarks include genres now
  - Update: Split `DevTools` into `Header`, `Bookmark`, and `Cache`
  - Update: Cleaned redundancies in code
- Moved to new version numbering

##### 0.07
- _11/10/15_
- Fixes:
  - Kissmanga cookie cache
  - Bookmark image cache error
  - Dict writing too fast
- Update/New:
  - Update: Split `test.pys` into `common.pys` and `headers.pys`
  - New: `Update "type" Headers` "type" = Anime, Cartoon, Drama, and Manga.

##### 0.06
- _11/06/15_
- Fixes:
  - Kissmanga
- Update/New:
  - New: Cache Covers Option
  - New: About/Help, Dev Tools, Bookmark Tools sections
  - New: Dynamically set domain URL's
> **NOTE:** Kissanime.com changed to Kissanime.to You will need to Reset your Header_Dict. Follow **Operation** above for usage.

##### 0.05
- _10/29/15_
- Fixes:
  - Cartoon cache time
- Update/New:
  - Update: Improved Metadata & summary
  - New: 'Adult' to Prefs and  _Top_ list to Cartoon and Drama sections
> **NOTE:** Due to a string encode/decode error you will have to **Clear All Bookmarks** before updating from **0.04** to **0.05**.

##### 0.04
- _10/16/15_
- Moved to "Shared Code" for setting headers
- Improved Header Cache times

##### 0.03
- _10/13/15_
- Major overhaul of headers
- No more 5 second wait time for each directory
- Improved Bookmarking, Search, and cookie cache time
> **Note** Bookmarks changed from previous version.  You will have to delete your old Dictionary file "Dict" from the "Plug-in Support" Path.

##### 0.02
- _10/09/15_
- Fixed Windows 10 not displaying channel [issue](https://github.com/Twoure/KissNetwork.bundle/issues/1)
- Added site selection in channel preferences

##### 0.01
- _10/03/15_
- Initial version

##### 0.00
- _09/21/15_
- First push of local code to GitHub
