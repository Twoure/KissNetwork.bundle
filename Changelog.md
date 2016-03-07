# ChangeLog

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
