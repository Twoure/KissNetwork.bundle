About
===============

This is a plugin that creates a new channel in Plex Media Server to view content from the website [Kissmanga.com](http://kissmanga.com/). It is currently under development and as such, should be considered alpha software and potentially unstable. If you try it and it works for you (or if it not!) please let me know.

**Note:** the author of this plugin has no affiliation with [Kissmanga.com](http://kissmanga.com/) or the owners of the content that it hosts.

System Requirements
===================

- **Plex Media Server**

  - Tested Working:
		- Linux
      - [Ubuntu 14.04 x86_64 Linux 3.13.0-63-generic](http://i.imgur.com/ZiO7htR.png)
      - PMS version 0.9.12.12

- **Plex Clients:**

  - Tested Working:
		- Plex Media Center / Home Theater Ubuntu
    - Android
		- Plex/Web

  - Not Working:
    - Chromecast

How To Install
==============

- [Download](http://github.com/Twoure/KissManga.bundle/zipball/master) the latest version of the plugin.

- Unzip and rename folder to "KissManga.bundle"

- Copy KissManga.bundle into the PMS plugins directory under your user account:
	- Windows 7, Vista, or Server 2008: C:\Users[Your Username]\AppData\Local\Plex Media Server\Plug-ins
	- Windows XP, Server 2003, or Home Server: C:\Documents and Settings[Your Username]\Local Settings\Application Data\Plex Media Server\Plug-ins
	- Mac/Linux: ~/Library/Application Support/Plex Media Server/Plug-ins

- ~~Restart PMS~~ **This is old, should not have to restart PMS**

Known Issues
============

- Once in awhile the 'Add Bookmark' function will try and add duplicates, but I've corrected for it in the code so there should be no problem.
- Chromecast doesn't work, don't know why yet.  Assuming it has to do with how I create the Photo Albums
- Sometimes the Cover Art work does not display in the directory even though it has the image URL.  Might be a parallelization issue.
- This is not a useful reader for the Plex/Web client, but works well for Smart phones and Plex Media Center
