#ChangeLog

###### 1.0.0
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

###### 0.07
- _11/10/15_
- Fixes:
  - Kissmanga cookie cache
  - Bookmark image cache error
  - Dict writing too fast
- Update/New:
  - Update: Split `test.pys` into `common.pys` and `headers.pys`
  - New: `Update "type" Headers` "type" = Anime, Cartoon, Drama, and Manga.

###### 0.06
- _11/06/15_
- Fixes:
  - Kissmanga
- Update/New:
  - New: Cache Covers Option
  - New: About/Help, Dev Tools, Bookmark Tools sections
  - New: Dynamically set domain URL's
> **NOTE:** Kissanime.com changed to Kissanime.to You will need to Reset your Header_Dict. Follow **Operation** above for usage.

###### 0.05
- _10/29/15_
- Fixes:
  - Cartoon cache time
- Update/New:
  - Update: Improved Metadata & summary
  - New: 'Adult' to Prefs and  _Top_ list to Cartoon and Drama sections
> **NOTE:** Due to a string encode/decode error you will have to **Clear All Bookmarks** before updating from **0.04** to **0.05**.

###### 0.04
- _10/16/15_
- Moved to "Shared Code" for setting headers
- Improved Header Cache times

###### 0.03
- _10/13/15_
- Major overhaul of headers
- No more 5 second wait time for each directory
- Improved Bookmarking, Search, and cookie cache time
> **Note** Bookmarks changed from previous version.  You will have to delete your old Dictionary file "Dict" from the "Plug-in Support" Path.

###### 0.02
- _10/09/15_
- Fixed Windows 10 not displaying channel [issue](https://github.com/Twoure/KissNetwork.bundle/issues/1)
- Added site selection in channel preferences

###### 0.01
- _10/03/15_
- Initial version

###### 0.00
- _09/21/15_
- First push of local code to GitHub
