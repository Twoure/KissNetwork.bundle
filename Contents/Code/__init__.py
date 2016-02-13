####################################################################################################
#                                                                                                  #
#                                   KissNetwork Plex Channel                                       #
#                                                                                                  #
####################################################################################################
# import section(s) not included in Plex Plug-In Framework
import os
import sys
import shutil
import io
import urllib
import urllib2
from time import sleep
from updater import Updater
from DumbTools import DumbKeyboard
from DumbTools import DumbPrefs
import AuthTools

# import Shared Service Code
Headers = SharedCodeService.headers
Domain = SharedCodeService.domain
Common = SharedCodeService.common

# add custom modules to python path
module_path = Core.storage.join_path(
    Core.app_support_path, Core.config.bundles_dir_name,
    'KissNetwork.bundle', 'Contents', 'Modules')

if module_path not in sys.path:
    sys.path.append(module_path)
    Log.Info(
        '\n----------\n%s\n---^^^^---added to sys.path---^^^^---\n----------By __init__.py----------'
        %module_path)

# import custom modules
import requests

# set global variables
PREFIX = '/video/kissnetwork'
TITLE = L('title')
VERSION = '1.0.1'
ADULT_LIST = set(['Adult', 'Smut', 'Ecchi', 'Lolicon', 'Mature', 'Yaoi', 'Yuri'])

# KissAnime
ANIME_BASE_URL = Common.ANIME_BASE_URL
ANIME_SEARCH_URL = ANIME_BASE_URL + '/Search/Anime?keyword=%s'
ANIME_ART = 'art-anime.jpg'
ANIME_ICON = 'icon-anime.png'

# KissAsian
ASIAN_BASE_URL = Common.ASIAN_BASE_URL
ASIAN_SEARCH_URL = ASIAN_BASE_URL + '/Search/Drama?keyword=%s'
ASIAN_ART = 'art-drama.jpg'
ASIAN_ICON = 'icon-drama.png'

# KissCartoon
CARTOON_BASE_URL = Common.CARTOON_BASE_URL
CARTOON_SEARCH_URL = CARTOON_BASE_URL + '/Search/Cartoon?keyword=%s'
CARTOON_ART = 'art-cartoon.jpg'
CARTOON_ICON = 'icon-cartoon.png'

# KissManga
MANGA_BASE_URL = Common.MANGA_BASE_URL
MANGA_SEARCH_URL = MANGA_BASE_URL + '/Search/Manga?keyword=%s'
MANGA_ART = 'art-manga.jpg'
MANGA_ICON = 'icon-manga.png'

# set background art and icon defaults
MAIN_ART = 'art-main.jpg'
MAIN_ICON = 'icon-default.png'
NEXT_ICON = 'icon-next.png'
CATEGORY_VIDEO_ICON = 'icon-video.png'
CATEGORY_PICTURE_ICON = 'icon-pictures.png'
BOOKMARK_ICON = 'icon-bookmark.png'
BOOKMARK_ADD_ICON = 'icon-add-bookmark.png'
BOOKMARK_REMOVE_ICON = 'icon-remove-bookmark.png'
BOOKMARK_CLEAR_ICON = 'icon-clear-bookmarks.png'
SEARCH_ICON = 'icon-search.png'
PREFS_ICON = 'icon-prefs.png'
CACHE_COVER_ICON = 'icon-cache-cover.png'
ABOUT_ICON = 'icon-about.png'

####################################################################################################
def Start():
    ObjectContainer.art = R(MAIN_ART)
    ObjectContainer.title1 = TITLE

    DirectoryObject.thumb = R(MAIN_ICON)

    InputDirectoryObject.art = R(MAIN_ART)

    HTTP.CacheTime = 0
    HTTP.Headers['User-Agent'] = Common.USER_AGENT

    # setup background auto cache of headers
    Dict['First Headers Cached'] = False

    # setup test for cfscrape
    SetUpCFTest()

    if Dict['cfscrape_test']:
        if Dict['Headers Auto Cached']:
            if not Dict['Headers Auto Cached']:
                Log.Info('\n----------Caching Headers----------')
                Thread.CreateTimer(5, BackgroundAutoCache)
            else:
                Log.Info('\n----------Cookies already cached----------')
                Log.Info('\n----------Checking Each URL Cache Time----------')
                Thread.CreateTimer(5, BackgroundAutoCache)
        else:
            Dict['Headers Auto Cached'] = False
            Dict.Save()
            Log.Info('\n----------Caching Headers----------')
            Thread.CreateTimer(5, BackgroundAutoCache)
    else:
        pass

####################################################################################################
@handler(PREFIX, TITLE, MAIN_ICON, MAIN_ART)
def MainMenu():
    """Create the Main Menu"""

    # if cfscrape failed then stop the channel, and return error message.
    SetUpCFTest()
    if Dict['cfscrape_test']:
        Log.Info('\n----------CFTest Previously Passed, not running again.----------')
        pass
    else:
        Log.Error(
            """
            ----------CFTest Failed----------
            You need to install a JavaScript Runtime like node.js or equivalent
            Once JavaScript Runtime installed, Restart channel
            """
            )
        return MessageContainer(
            'Error',
            'CloudFlare bypass fail. Please install a JavaScript Runtime like node.js or equivalent')

    oc = ObjectContainer(title2=TITLE, no_cache=True)

    # set thumbs based on client
    if Client.Platform in Common.LIST_VIEW_CLIENTS:
        anime_thumb = None
        anime_art = None
        cartoon_thumb = None
        cartoon_art = None
        asian_thumb = None
        asian_art = None
        manga_thumb = None
        manga_art = None
        bookmark_thumb = None
        prefs_thumb = None
        search_thumb = None
        about_thumb = None
    else:
        anime_thumb = R(ANIME_ICON)
        anime_art = R(ANIME_ART)
        cartoon_thumb = R(CARTOON_ICON)
        cartoon_art = R(CARTOON_ART)
        asian_thumb = R(ASIAN_ICON)
        asian_art = R(ASIAN_ART)
        manga_thumb = R(MANGA_ICON)
        manga_art = R(MANGA_ART)
        bookmark_thumb = R(BOOKMARK_ICON)
        prefs_thumb = R(PREFS_ICON)
        search_thumb = R(SEARCH_ICON)
        about_thumb = R(ABOUT_ICON)

    # set status for bookmark sub menu
    if Dict['Bookmark_Deleted']:
        if Dict['Bookmark_Deleted']['bool']:
            Dict['Bookmark_Deleted'].update({'bool': False, 'type_title': None})
            Dict.Save()
        else:
            pass
    else:
        Dict['Bookmark_Deleted'] = {'bool': False, 'type_title': None}
        Dict.Save()

    status = Dict['Bookmark_Deleted']
    Dict.Save()

    Updater(PREFIX + '/updater', oc)

    # set up Main Menu depending on what sites are picked in the Prefs menu
    if Prefs['kissanime']:
        oc.add(DirectoryObject(
            key=Callback(KissAnime, url=ANIME_BASE_URL, title='Anime', art=ANIME_ART),
            title='Anime', thumb=anime_thumb, art=anime_art))
    if Prefs['kisscartoon']:
        oc.add(DirectoryObject(
            key=Callback(KissCartoon, url=CARTOON_BASE_URL, title='Cartoon', art=CARTOON_ART),
            title='Cartoons', thumb=cartoon_thumb, art=cartoon_art))
    if Prefs['kissasian']:
        oc.add(DirectoryObject(
            key=Callback(KissAsian, url=ASIAN_BASE_URL, title='Drama', art=ASIAN_ART),
            title='Drama', thumb=asian_thumb, art=asian_art))

    if Prefs['kissmanga']:
        oc.add(DirectoryObject(
            key=Callback(KissManga, url=MANGA_BASE_URL, title='Manga', art=MANGA_ART),
            title='Manga', thumb=manga_thumb, art=manga_art))

    oc.add(DirectoryObject(
        key=Callback(BookmarksMain, title='My Bookmarks', status=status), title='My Bookmarks', thumb=bookmark_thumb))

    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=prefs_thumb)
    elif AuthTools.Auth():
        oc.add(PrefsObject(title='Preferences', thumb=prefs_thumb))

    oc.add(DirectoryObject(key=Callback(About), title='About / Help', thumb=about_thumb))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R(SEARCH_ICON))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search), title='Search', prompt='Search for...', thumb=search_thumb
            ))

    return oc

####################################################################################################
@route(PREFIX + '/kissanime')
def KissAnime(url, title, art):
    """Create KissAnime Site Menu"""

    oc = ObjectContainer(title2=title, art=R(art))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='All', category='All', base_url=url, type_title=title, art=art),
        title='All'))
    oc.add(DirectoryObject(
        key=Callback(AlphabetList, url=url, title=title, art=art), title='Alphabets'))
    oc.add(DirectoryObject(
        key=Callback(GenreList, url=url, title=title, art=art), title='Genres'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Genre/Movie', category='Movie', base_url=url, type_title=title, art=art),
        title='Movies'))
    oc.add(DirectoryObject(key=Callback(StatusList, url=url, type_title=title, art=art), title='Status'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/LatestUpdate', category='Latest Update', base_url=url, type_title=title, art=art),
        title='Latest Update'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/NewAndHot', category='New & Hot', base_url=url, type_title=title, art=art),
        title='New & Hot'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Newest', category='Recent Additions', base_url=url, type_title=title, art=art),
        title='Recent Additions'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/MostPopular', category='Most Popular', base_url=url, type_title=title, art=art),
        title='Most Popular'))

    return oc

####################################################################################################
@route(PREFIX + '/kissasian')
def KissAsian(url, title, art):
    """Create KissAsian Site Menu"""

    oc = ObjectContainer(title2=title, art=R(art))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='All', category='All', base_url=url, type_title=title, art=art), title='All'))
    oc.add(DirectoryObject(
        key=Callback(AlphabetList, url=url, title=title, art=art), title='Alphabets'))
    oc.add(DirectoryObject(
        key=Callback(CountryList, url=url, title=title, art=art), title='Countries'))
    oc.add(DirectoryObject(
        key=Callback(GenreList, url=url, title=title, art=art), title='Genres'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Genre/Movie', category='Movie', base_url=url, type_title=title, art=art),
        title='Movies'))
    oc.add(DirectoryObject(key=Callback(StatusList, url=url, type_title=title, art=art), title='Status'))
    oc.add(DirectoryObject(key=Callback(TopList, url=url, type_title=title, art=art), title='Top'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/LatestUpdate', category='Latest Update', base_url=url, type_title=title, art=art),
        title='Latest Update'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Newest', category='New Drama', base_url=url, type_title=title, art=art),
        title='New Drama'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/MostPopular', category='Most Popular', base_url=url, type_title=title, art=art),
        title='Most Popular'))

    return oc

####################################################################################################
@route(PREFIX + '/kisscartoon')
def KissCartoon(url, title, art):
    """Create KissCartoon site Menu"""

    oc = ObjectContainer(title2=title, art=R(art))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='All', category='All', base_url=url, type_title=title, art=art), title='All'))
    oc.add(DirectoryObject(
        key=Callback(AlphabetList, url=url, title=title, art=art), title='Alphabets'))
    oc.add(DirectoryObject(
        key=Callback(GenreList, url=url, title=title, art=art), title='Genres'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Genre/Movie', category='Movie', base_url=url, type_title=title, art=art),
        title='Movies'))
    oc.add(DirectoryObject(key=Callback(StatusList, url=url, type_title=title, art=art), title='Status'))
    oc.add(DirectoryObject(key=Callback(TopList, url=url, type_title=title, art=art), title='Top'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/LatestUpdate', category='Latest Update', base_url=url, type_title=title, art=art),
        title='Latest Update'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Newest', category='New Cartoon', base_url=url, type_title=title, art=art),
        title='New Cartoon'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/MostPopular', category='Most Popular', base_url=url, type_title=title, art=art),
        title='Most Popular'))

    return oc

####################################################################################################
@route(PREFIX + '/kissmanga')
def KissManga(url, title, art):
    """Create KissManga site Menu"""

    oc = ObjectContainer(title2=title, art=R(art))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='All', category='All', base_url=url, type_title=title, art=art), title='All'))
    oc.add(DirectoryObject(
        key=Callback(AlphabetList, url=url, title=title, art=art), title='Alphabets'))
    oc.add(DirectoryObject(
        key=Callback(GenreList, url=url, title=title, art=art), title='Genres'))
    oc.add(DirectoryObject(key=Callback(StatusList, url=url, type_title=title, art=art), title='Status'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/LatestUpdate', category='Latest Update', base_url=url, type_title=title, art=art),
        title='Latest Update'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Newest', category='New Manga', base_url=url, type_title=title, art=art),
        title='New Manga'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/MostPopular', category='Most Popular', base_url=url, type_title=title, art=art),
        title='Most Popular'))

    return oc

####################################################################################################
@route(PREFIX + '/status-list')
def StatusList(type_title, url, art):
    """
    Setup Status List for each site
    Ongoing and Completed list
    """

    oc = ObjectContainer(title2=type_title, art=R(art))
    s_list = ['Ongoing', 'Completed']
    for s in s_list:
        oc.add(DirectoryObject(
            key=Callback(DirectoryList,
                page=1, pname='/Status/%s' %s, category=s, base_url=url, type_title=type_title, art=art),
            title=s))

    return oc

####################################################################################################
@route(PREFIX + '/top-list')
def TopList(type_title, url, art):
    """
    Setup Top list for Cartoon and Drama
    Top Today, Week, Month
    """

    oc = ObjectContainer(title2=type_title, art=R(art))
    t_list = ['Top Day', 'Top Week', 'Top Month']
    for t in t_list:
        tab = t.split('Top')[1].strip().lower()
        oc.add(DirectoryObject(
            key=Callback(HomePageList,
                tab=tab, category=t, base_url=url, type_title=type_title, art=art),
            title=t))

    return oc

####################################################################################################
@route(PREFIX + '/about')
def About():
    """Return Resource Directory Size, and KissNetwork's Current Channel Version"""

    oc = ObjectContainer(title2='About / Help')

    # Get Resources Directory Size
    d = GetDirSize(Common.RESOURCES_PATH)
    if d == 'Error':
        cache_string = 'N/A | Removing Files Still'
    else:
        cache_string = d

    plist = Plist.ObjectFromString(Core.storage.load(
        Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, 'Contents', 'Info.plist'))))
    version = plist['CFBundleVersion']

    if Prefs['devtools'] and AuthTools.Auth():
        oc.add(DirectoryObject(key=Callback(DevTools),
            title='Developer Tools',
            summary='WARNING!!\nDeveloper Tools.  Make sure you understand what these do before using.'))

    oc.add(DirectoryObject(key=Callback(About),
        title='Version %s' %version, summary='Current Channel Version'))
    oc.add(DirectoryObject(key=Callback(About),
        title=cache_string, summary='Number of Images Cached | Total Images Cached Size'))

    return oc

####################################################################################################
def ResetCustomDict(file_to_reset):
    """
    Reset Cusom Dictionaries
    Valid for only "Header_Dict" and "Domain_Dict"
    """

    Log('\n----------Backing up %s File to %s.backup----------' %(file_to_reset, file_to_reset))
    file_path = Core.storage.join_path(Core.storage.data_path, file_to_reset)

    if Core.storage.file_exists(file_path):
        # create backup of file being removed
        Core.storage.copy(file_path, file_path + '.backup')
        Log('\n----------Removing %s File----------' %file_to_reset)
        Core.storage.remove_tree(file_path)

    if file_to_reset == 'Domain_Dict':
        Domain.CreateDomainDict()
    elif file_to_reset == 'Header_Dict':
        Headers.CreateHeadersDict()

    Log('\n----------Reset %s----------\n----------New values for %s written to:\n%s' %(file_to_reset, file_to_reset, file_path))

    return file_path

####################################################################################################
@route(PREFIX + '/devtools')
def DevTools(file_to_reset=None, header=None, message=None):
    """
    Includes "Bookmark Tools", "Header Tools" and "Cover Cache Tools"
    Reset Domain_Dict and CloudFlare Test Key
    """

    oc = ObjectContainer(title2='Developer Tools', header=header, message=message)

    if file_to_reset:
        header = 'Developer Tools'
        if file_to_reset == 'Domain_Dict':
            ResetCustomDict(file_to_reset)
            message = 'Reset %s. New values for %s written' %(file_to_reset, file_to_reset)

            return DevTools(header=header, message=message)
        elif file_to_reset == 'cfscrape_test':
            Log('\n----------Deleting cfscrape test key from Channel Dict----------')
            if Dict['cfscrape_test']:
                del Dict['cfscrape_test']
                Dict.Save()
                SetUpCFTest()
                message = 'Reset cfscrape Code Test'
            else:
                message = 'No Dict cfscrape Code Test Key to Remove'

            return DevTools(header=header, message=message)
        elif file_to_reset == 'restart_channel':
            Log('\n----------Attempting to Restart KissNetwork Channel----------')
            RestartChannel()
            message = 'Restarting channel'
            return DevTools(header=header, message=message)
    else:
        pass

    oc.add(DirectoryObject(key=Callback(DevToolsBM),
        title='Bookmark Tools',
        summary='Tools to Clean dirty bookmarks dictionary, and Toggle "Clear Bookmarks".'))
    oc.add(DirectoryObject(key=Callback(DevToolsH),
        title='Header Tools',
        summary='Tools to Reset "Header_Dict" or Update parts of "Header_Dict".'))
    oc.add(DirectoryObject(key=Callback(DevToolsC),
        title='Cover Cache Tools',
        summary='Tools to Cache All Covers or just certain sites. Includes Tool to Clean Dirty Resources Directory.'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='Domain_Dict'),
        title='Reset Domain_Dict File',
        summary='Create backup of old Domain_Dict, delete current, create new and fill with fresh domains'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='cfscrape_test'),
        title='Reset Dict cfscrape Test Key',
        summary='Delete previous test key so the channel can retest for a valid JavaScript Runtime.'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='restart_channel'),
        title='Restart KissNetwork Channel',
        summary='Should manually Restart the KissNetwork Channel.'))

    return oc

####################################################################################################
@route(PREFIX + '/devtools-headers')
def DevToolsH(title=None, header=None, message=None):
    """Tools to manipulate Headers"""

    oc = ObjectContainer(title2='Header Tools', header=header, message=message)

    if title:
        header = 'Header Tools'
        if title == 'Header_Dict':
            Thread.Create(ResetCustomDict, file_to_reset=title)
            message = 'Resetting %s. New values for %s will be written soon' %(title, title)

            return DevToolsH(header=header, message=message)
        elif ( title == 'Anime' or title == 'Cartoon'
            or title == 'Drama' or title == 'Manga' ):
            Log('\n----------Updating %s Headers in Header_Dict----------' %title)

            for (h_name, h_url) in Common.BASE_URL_LIST_T:
                if h_name == title:
                    Headers.GetHeadersForURL(h_url, update=True)
                    break

            message = 'Updated %s Headers.' %title
            return DevTools(header=header, message=message)
        elif title == 'test':
            sub_list = Test()
            message = 'list =\n%s' %sub_list
            return DevTools(header=header, message=message)
    else:
        pass

    #oc.add(DirectoryObject(key=Callback(DevToolsH, title='test'),
        #title='test', summary='test'))
    oc.add(DirectoryObject(key=Callback(DevToolsH, title='Header_Dict'),
        title='Reset Header_Dict File',
        summary='Create backup of old Header_Dict, delete current, create new and fill with fresh headers. Remember Creating Header_Dict takes time, so the channel may timeout on the client while rebuilding.  Do not worry. Exit channel and refresh client. The channel should load normally now.'))
    for (name, url) in sorted(Common.BASE_URL_LIST_T):
        oc.add(DirectoryObject(key=Callback(DevToolsH, title=name),
            title='Update %s Headers' %name,
            summary='Update %s Headers Only in the "Header_Dict" file.' %name))

    return oc

####################################################################################################
@route(PREFIX + '/devtools-cache')
def DevToolsC(title=None, header=None, message=None):
    """
    Tools to Cache Cover Images
    Reset/Clean Channel Resources Diretory
    """
    oc = ObjectContainer(title2='Cover Cache Tools', header=header, message=message)

    if title:
        header = 'Cover Cache Tools'
        if title == 'resources_cache':
            Log('\n----------Cleaning Dirty Resources Directory, and deleating Dict Keys if any----------')

            for dirpath, dirnames, filenames in os.walk(Common.RESOURCES_PATH):
                for f in filenames:
                    # filter out default files
                    if not Regex('(^icon\-(?:\S+)\.png$|^art\-(?:\S+)\.jpg$)').search(f):
                        fp = os.path.join(dirpath, f)
                        Core.storage.remove(fp)
            if Dict['cover_files']:
                del Dict['cover_files']

            message = 'Reset Resources Directory, and Deleted Dict[\'cover_files\']'
            return DevToolsC(header=header, message=message)
        elif ( title == 'Anime_cache' or title == 'Cartoon_cache'
            or title == 'Drama_cache' or title == 'Manga_cache' ):
            category = title.split('_')[0]
            Log('\n----------Start Caching all %s Cover Images----------' %category)

            qevent = Thread.Event()  # create new Event object
            qevent.set()
            test = Thread.Create(CacheAllCovers, category=category, qevent=qevent, page=1)
            Log('\n\n%s\n\n' %test)
            message = 'All %s Cover Images are being Cached' %category

            return DevToolsC(header=header, message=message)
        elif title == 'All_cache':
            Log('\n----------Start Caching All Cover Images----------')

            Thread.Create(CacheCoverQ)

            message = 'All Cover Images are being Cached'
            return DevToolsC(header=header, message=message)
    else:
        pass

    for (name, url) in [('All', '')] + sorted(Common.BASE_URL_LIST_T):
        oc.add(DirectoryObject(key=Callback(DevToolsC, title='%s_cache' %name),
            title='Cache All %s Covers' %name if not name == 'All' else 'Cache All Covers',
            summary='Download all %s Covers' %name if not name == 'All' else 'Download All Covers'))
    oc.add(DirectoryObject(key=Callback(DevToolsC, title='resources_cache'),
        title='Reset Resources Directory',
        summary='Clean Dirty Image Cache in Resources Directory.'))

    return oc

####################################################################################################
def CacheCoverQ():
    """
    Setup CacheAllCovers in a Queried manner
    Create Event, set = True
    Create First CacheAllCovers Thread, set Event = False
    For 2nd CacheAllCovers Thread, set Event to Wait until it is set to True
        It will be set to True Once the 1st CacheAllCovers Thread is Finished
        Once Wait is over, Re-set Event to Flase, and Start the 2nd CacheAllCovers Thread
    Repeat Process for remaining CacheAllCovers Threads (3rd and 4th)
    """

    qevent = Thread.Event()  # create new Event object
    qevent.set()  # set new Event object to True for first iteration of 'for loop'
    for (cat, url) in sorted(Common.BASE_URL_LIST_T):
        if qevent.is_set():
            Log('Create the First Cache All Covers Thread for %s' %cat)
            qevent.clear()  # set Event object to Flase for next iteration of 'for loop'
            Log('qevent set to %s, for next iteration' %qevent.is_set())
            Thread.Create(CacheAllCovers, category=cat, page=1, qevent=qevent)
        else:
            Log('set qevent to wait for %s' %cat)
            qevent.wait()  # make the 'for loop' wait until the Thread created in the 1st iteration completes
            Log('qevent is now set to %s, passing along %s' %(qevent.is_set(), cat))
            qevent.clear()  # re-set Event to False for next interation of 'for loop'
            Log('set qevent to %s for next iteration' %qevent.is_set())
            Thread.Create(CacheAllCovers, category=cat, page=1, qevent=qevent)

    Log.Info('Finished starting CacheAllCovers Query. %s is last to Cache Covers and will be done in about 7 minutes.' %cat)

    return

####################################################################################################
@route(PREFIX + '/devtools-bookmarks')
def DevToolsBM(title=None, header=None, message=None):
    """
    Tools to Delete all or certain sections of Bookmarks Dict
    Toggle "Clear Bookmarks" Function On/Off
    """

    oc = ObjectContainer(title2='Bookmark Tools', header=header, message=message)

    if title:
        if title == 'hide_bm_clear':
            Log('\n----------Hiding "Clear Bookmarks" and Sub List Clear from "My Bookmarks"----------')

            if not Dict['hide_bm_clear']:
                Dict['hide_bm_clear'] == 'hide'
                Dict.Save()
                message = '"Clear Bookmarks" is Hidden Now'
            elif Dict['hide_bm_clear'] == 'hide':
                Dict['hide_bm_clear'] = 'unhide'
                Dict.Save()
                message = '"Clear Bookmarks" is Un-Hidden Now'
            elif Dict['hide_bm_clear'] == 'unhide':
                Dict['hide_bm_clear'] = 'hide'
                Dict.Save()
                message = '"Clear Bookmarks" is Hidden Now'

            return DevToolsBM(header='Hide BM Clear Opts', message=message)
        elif title == 'All' and Dict['Bookmarks']:
            Log('\n----------Deleting Bookmark section from Channel Dict----------')
            del Dict['Bookmarks']
            Dict.Save()
            message = 'Bookmarks Section Cleaned.'
            return DevToolsBM(header='BookmarkTools', message=message)
        elif title and title in Dict['Bookmarks'].keys():
            Log('\n----------Deleting %s Bookmark section from Channel Dict----------' %title)
            del Dict['Bookmarks'][title]
            Dict.Save()
            message = '%s Bookmark Section Cleaned.' %title
            return DevToolsBM(header='BookmarkTools', message=message)
        elif not Dict['Bookmarks']:
            Log('\n----------Bookmarks Section Alread Removed----------')
            message = 'Bookmarks Section Already Cleaned.'
            return DevToolsBM(header='BookmarkTools', message=message)
        elif not title in Dict['Bookmarks'].keys():
            Log('\n----------%s Bookmark Section Already Removed----------' %title)
            message = '%s Bookmark Section Already Cleaned.' %title
            return DevToolsBM(header='BookmarkTools', message=message)
    else:
        pass

    oc.add(DirectoryObject(key=Callback(DevToolsBM, title='hide_bm_clear'),
        title='Toggle Hiding "Clear Bookmarks" Function',
        summary='Hide the "Clear Bookmarks" Function from "My Bookmarks" and sub list. For those of us who do not want people randomly clearing our bookmarks.'))
    for (name, url) in [('All', '')] + sorted(Common.BASE_URL_LIST_T):
        if name == 'All':
            oc.add(DirectoryObject(key=Callback(DevToolsBM, title=name),
                title='Reset "%s" Bookmarks' %name,
                summary='Delete Entire Bookmark Section. Same as "Clear All Bookmarks".'))
        else:
            oc.add(DirectoryObject(key=Callback(DevToolsBM, title=name),
                title='Reset "%s" Bookmarks' %name,
                summary='Delete Entire "%s" Bookmark Section. Same as "Clear %s Bookmarks".' %(name, name)))

    return oc

####################################################################################################
@route(PREFIX + '/validateprefs', start=bool, skip=bool)
def ValidatePrefs(start=False, skip=False):
    """Set the sorting options for displaying all lists"""

    # load prefs into dict for use later
    if Prefs['sort_opt'] == 'Alphabetical':
        Dict['s_opt'] = ''
    elif Prefs['sort_opt'] == 'Popularity':
        Dict['s_opt'] = '/MostPopular'
    elif Prefs['sort_opt'] == 'Latest Update':
        Dict['s_opt'] = '/LatestUpdate'
    elif Prefs['sort_opt'] == 'Newest':
        Dict['s_opt'] = '/Newest'

    Logger('Dict[\'s_opt\'] = %s' %Dict['s_opt'], kind='Info', force=True)

    # Update the Dict to latest prefs
    Dict.Save()

    """
    Check cache image opt's:
      if caching all or caching bookmarks true,
          then download thumbs from Dict['Bookmarks']
      if caching all false and caching bookmarks true,
          then keep thumbs for Bookmarks but delete all others
      if caching all false and caching bookmarks false,
          then delete all cached thumbs and remove Dict['cache_files']
    Created as Thread so it will run in the background
    """
    Thread.Create(CacheCovers, start=start, skip=skip)

####################################################################################################
@route(PREFIX + '/bookmarks', status=dict)
def BookmarksMain(title, status):
    """Create Bookmark Main Menu"""

    if status['bool']:
        oc = ObjectContainer(title2=title, header="My Bookmarks",
            message='%s bookmarks have been cleared.' % status['type_title'], no_cache=True)
    else:
        oc = ObjectContainer(title2=title, no_cache=True)

    # check for 'Bookmarks' section in Dict
    if not Dict['Bookmarks']:
        # if no 'Bookmarks' section the return pop up
        return MessageContainer(header=title,
            message='No Bookmarks yet. Get out there and start adding some!!!')
    # create boomark directory based on category
    else:
        for key in sorted(Dict['Bookmarks'].keys()):
            if not key == 'Drama':
                art = 'art-%s.jpg' %key.lower()
                thumb = 'icon-%s.png' %key.lower()
                prefs_name = 'kiss%s' %key.lower()
            else:
                art = 'art-drama.jpg'
                thumb = 'icon-drama.png'
                prefs_name = 'kissasian'

            # if site in Prefs then add its bookmark section
            if Prefs[prefs_name]:
                # Create sub Categories for Anime, Cartoon, Drama, and Manga
                oc.add(DirectoryObject(
                    key=Callback(BookmarksSub, type_title=key, art=art),
                    title=key, thumb=R(thumb), summary='Display %s Bookmarks' % key, art=R(art)))
        # set hide bm clear key if not created yet
        if not Dict['hide_bm_clear']:
            Dict['hide_bm_clear'] = 'unhide'
            Dict.Save()

        # test if no sites are picked in the Prefs
        if len(oc) > 0:
            # hide/unhide clear bookmarks option, from DevTools
            if Dict['hide_bm_clear'] == 'unhide':
                # add a way to clear the entire bookmarks list, i.e. start fresh
                oc.add(DirectoryObject(
                    key=Callback(ClearBookmarks, type_title='All'),
                    title='Clear All Bookmarks',
                    thumb=R(BOOKMARK_CLEAR_ICON),
                    summary='CAUTION! This will clear your entire bookmark list, even those hidden!'))

            return oc
        else:
            # Give error message
            return MessageContainer(header='Error',
                message='At least one source must be selected in Preferences to view Bookmarks')

####################################################################################################
@route(PREFIX + '/bookmarkssub')
def BookmarksSub(type_title, art):
    """Load Bookmarked items from Dict"""

    if not type_title in Dict['Bookmarks'].keys():
        return MessageContainer(header='Error',
            message='%s Bookmarks list is dirty. Use About/Help > Dev Tools > Bookmark Tools > Reset %s Bookmarks' %(type_title, type_title))

    oc = ObjectContainer(title2='My Bookmarks | %s' % type_title, art=R(art))
    Logger('category %s' %type_title)

    # Fill in DirectoryObject information from the bookmark list
    # create empty list for testing covers
    cover_list_bool = []
    for bookmark in sorted(Dict['Bookmarks'][type_title], key=lambda k: k[type_title]):
        item_title = bookmark['item_title']
        summary = bookmark['summary']

        if summary:
            summary2 = StringCode(string=summary, code='decode')
        else:
            summary2 = None

        # setup cover depending of Prefs
        cover = Common.CorrectCoverImage(bookmark['cover_file'])
        cover_file = cover
        if bookmark['cover_url']:
            cover_url = Common.CorrectCoverImage(bookmark['cover_url'])
        else:
            cover_url = None
        # if any Prefs set to cache then try and get the thumb
        if Prefs['cache_bookmark_covers'] or Prefs['cache_covers']:
            # check if the thumb is already cached
            if Common.CoverImageFileExist(cover):
                cover = R(cover)
                cover_list_bool.append(True)
            # thumb not cached, set thumb to caching cover and save thumb in background
            elif cover_url:
                cover_list_bool.append(False)
                cover = R(CACHE_COVER_ICON)
                if len(Dict['Bookmarks'][type_title]) <= 50:
                    Thread.Create(SaveCoverImage, image_url=cover_url)
                else:
                    ftimer = float(Util.RandomInt(0,30)) + Util.Random()
                    Thread.CreateTimer(interval=ftimer, f=SaveCoverImage, image_url=cover_url)
            # No cover url found, Will create thumb for this later
            else:
                cover = None
        # no Prefs to cache thumb, set thumb to None
        else:
            cover_list_bool.append(False)
            cover = None

        item_info = {
            'item_sys_name': bookmark[type_title],
            'item_title': item_title,
            'short_summary': summary,
            'cover_url': cover_url,
            'cover_file': cover_file,
            'type_title': type_title,
            'base_url': Common.GetBaseURL(bookmark['page_url']),
            'page_url': Common.GetBaseURL(bookmark['page_url']) + '/' + bookmark['page_url'].split('/', 3)[3],
            'art': art}

        # get genre info, provide legacy support for older Bookmarks
        #   by updating
        if 'genres' in bookmark.keys():
            genres = [g.replace('_', ' ') for g in bookmark['genres'].split()]
            if cover_url:
                if ('kissanime' in cover_url) and not ('https' in cover_url):
                    bm_info = item_info.copy()
                    bm_info.update({'type_title': type_title})
                    ftimer = float(Util.RandomInt(0,30)) + Util.Random()
                    Thread.CreateTimer(interval=ftimer, f=UpdateLegacyBookmark, bm_info=bm_info)
        else:
            bm_info = item_info.copy()
            bm_info.update({'type_title': type_title})
            ftimer = float(Util.RandomInt(0,30)) + Util.Random()
            Thread.CreateTimer(interval=ftimer, f=UpdateLegacyBookmark, bm_info=bm_info)
            genres = ['Temp']

        if not Prefs['adult']:
            matching_list = set(genres) & ADULT_LIST
            if len(matching_list) > 0:
                continue
            else:
                pass

        oc.add(DirectoryObject(
            key=Callback(ItemPage, item_info=item_info),
            title=StringCode(string=item_title, code='decode'),
            summary=summary2, thumb=cover, art=cover))

    if Dict['hide_bm_clear'] == 'unhide':
        # setup icons depending on platform and Prefs caching
        if Client.Platform in Common.LIST_VIEW_CLIENTS and not True in cover_list_bool:
            # client in list and no thumbs set for bookmarks, set bookmark clear icon to None
            bm_clr_icon = None
        else:
            # client not in list and thumbs found, set bookmark clear icon
            bm_clr_icon = R(BOOKMARK_CLEAR_ICON)

        # add a way to clear this bookmark section and start fresh
        oc.add(DirectoryObject(
            key=Callback(ClearBookmarks, type_title=type_title),
            title='Clear All \"%s\" Bookmarks' % type_title,
            thumb=bm_clr_icon,
            summary='CAUTION! This will clear your entire \"%s\" bookmark section!' % type_title))

    return oc

####################################################################################################
@route(PREFIX + '/alphabets')
def AlphabetList(url, title, art):
    """Create ABC Directory for each kiss site"""

    oc = ObjectContainer(title2='%s By #, A-Z' % title, art=R(art))

    # Create a list of Directories from (#, A to Z)
    for pname in ['#'] + map(chr, range(ord('A'), ord('Z')+1)):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList,
                page=1, pname=pname.lower() if not pname == '#' else '0',
                category=pname, base_url=url, type_title=title, art=art),
            title=pname))

    Logger('Built #, A-Z... Directories')

    return oc

####################################################################################################
@route(PREFIX + '/genres')
def GenreList(url, title, art):
    """Create Genre Directory for each kiss site"""

    genre_url = url + '/%sList' % title  # setup url for finding current Genre list

    # formate url response into html for xpath
    html = HTML.ElementFromURL(genre_url, headers=Headers.GetHeadersForURL(genre_url))

    oc = ObjectContainer(title2='%s By Genres' % title, art=R(art))

    # Generate Valid Genres based on Prefs['adult']
    for genre in html.xpath('//div[@class="barContent"]//a'):
        genre_href = genre.get('href')
        if 'Genre' in genre_href and not 'Movie' in genre_href:
            if not Prefs['adult']:
                if genre_href.replace('/Genre/', '') in ADULT_LIST:
                    continue
                else:
                    pass
            # name used for title2
            category = html.xpath('//div[@class="barContent"]//a[@href="%s"]/text()' %genre_href)[0].replace('\n', '').strip()

            oc.add(DirectoryObject(
                key=Callback(DirectoryList,
                    page=1, pname=genre_href, category=category, base_url=url, type_title=title, art=art),
                title=category))

    return oc

####################################################################################################
@route(PREFIX + '/countries')
def CountryList(url, title, art):
    """Create Country Directory for KissAsian"""

    country_url = url + '/DramaList'  # setup url for finding current Country list

    html = HTML.ElementFromURL(country_url, headers=Headers.GetHeadersForURL(country_url))

    oc = ObjectContainer(title2='Drama By Country', art=R(art))

    # For loop to pull out valid Countries
    for country in html.xpath('//div[@class="barContent"]//a'):
        if "Country" in country.get('href'):
            pname = country.get('href')  # name used internally
            category = country.text.replace('\n', '').strip()  # name used for title2

            oc.add(DirectoryObject(
                key=Callback(DirectoryList,
                    page=1, pname=pname, category=category, base_url=url, type_title=title, art=art),
                title=category))

    return oc

####################################################################################################
@route(PREFIX + '/directory')
def DirectoryList(page, pname, category, base_url, type_title, art):
    """
    GenreList, AlphabetList, CountryList, and Search are sent here
    Pulls out Items name and creates directories for them
    Might to add section that detects if Genre is empty
    """

    # Define url based on genre, abc, or search
    if "Search" in pname:
        item_url = base_url
        Logger('Searching for \"%s\"' % category)
        pass
    # New & Hot list is only on Anime site, but made it uniform just in case
    elif pname == '/NewAndHot':
        item_url = base_url + '/%sList%s' % (type_title, pname)
    # list from the front page, not effected by Prefs
    elif pname == '/LatestUpdate' or pname == '/Newest' or pname == '/MostPopular':
        item_url = base_url + '/%sList%s?page=%s' % (type_title, pname, page)
    # Sort order 'A-Z'
    elif Dict['s_opt'] == None:
        if ('Genre' in pname or 'Country' in pname
            or 'Ongoing' in pname or 'Completed' in pname):
            # Genre, Country, Ongoing, or Completed Specific
            item_url = base_url + '%s?page=%s' % (pname, page)
        elif "All" in pname:
            # All list
            item_url = base_url + '/%sList?page=%s' % (type_title, page)
        else:
            # No Genre, Country, Ongoing, or Completed
            item_url = base_url + '/%sList?c=%s&page=%s' % (type_title, pname, page)
    # Sort order for all options except 'A-Z'
    elif ('Genre' in pname or 'Country' in pname
        or 'Ongoing' in pname or 'Completed' in pname):
        # Specific with Prefs
        item_url = base_url + '%s%s?page=%s' % (pname, Dict['s_opt'], page)
    elif "All" in pname:
        Logger('dict s_opt = %s' %Dict['s_opt'])
        item_url = base_url + '/%sList%s?page=%s' % (type_title, Dict['s_opt'], page)
    else:
        # No Genre with Prefs
        item_url = base_url + '/%sList%s?c=%s&page=%s' % (type_title, Dict['s_opt'], pname, page)

    Logger('Sorting Option = %s' % Dict['s_opt'])  # Log Pref being used
    Logger('Category= %s | URL= %s' % (pname, item_url))

    html = HTML.ElementFromURL(item_url, headers=Headers.GetHeadersForURL(base_url))

    pages = "Last Page"
    nextpg_node = None

    # determine if 'next page' is used in directory page
    if "Search" in pname:
        # The Search result page returnes a long list with no 'next page' option
        # set url back to base url
        base_url = Common.GetBaseURL(item_url)
        Logger("Searching for %s" % category)  # check to make sure its searching
    else:
        # parse html for 'last' and 'next' page numbers
        for node in html.xpath('///div[@class="pagination pagination-left"]//li/a'):
            if "Last" in node.text:
                pages = str(node.get('href'))  # pull out last page if not on it
            elif "Next" in node.text:
                nextpg_node = str(node.get('href'))  # pull out next page if exist

    # Create title2 to include directory and page numbers
    if not "Last" in pages:
        total_pages = pages.split('page=')[1]
        # set title2 ie main_title
        main_title = '%s | %s | Page %s of %s' % (type_title, str(category), str(page), str(total_pages))
    elif "Search" in pname:
        # set title2 for search page
        main_title = 'Search for: %s in %s' % (str(category), type_title)
    else:
        # set title2 for last page
        main_title = '%s | %s | Page %s, Last Page' % (type_title, str(category), str(page))

    oc = ObjectContainer(title2=main_title, art=R(art), no_cache=True)

    # parse url for each Item and pull out its title, summary, and cover image
    # took some time to figure out how to get the javascript info
    listing = html.xpath('//table[@class="listing"]//td[@title]')
    if not listing:
        listing = html.xpath('//div[@class="item"]')
    if type_title == 'Drama' and ('Search' not in pname):
        drama_test = True
    else:
        drama_test = False
    listing_count = len(listing)
    allowed_count = 200
    Logger('%i items in Directory List.' %listing_count, kind='Info')
    if listing_count > allowed_count and 'Search' in pname:
        return MessageContainer(
            'Error',
            '%i found.  Directory can only list up to %i items.  Please narrow your Search Criteria.' %(listing_count, allowed_count))

    for item in listing:
        if not drama_test:
            title_html = HTML.ElementFromString(item.get('title'))
        else:
            title_html = item
            drama_title_html = HTML.ElementFromString(item.get('title'))
        try:
            if not drama_test:
                thumb = Common.CorrectCoverImage(title_html.xpath('//img/@src')[0])
            else:
                thumb = Common.CorrectCoverImage(item.xpath('./a/img/@src')[0])
            if not 'http' in thumb:
                Log.Debug('thumb missing valid url. | %s' %thumb)
                Log.Debug('thumb xpath = %s' %title_html.xpath('//img/@src'))
                Log.Debug('item name | %s | %s' %(title_html.xpath('//a/@href'), title_html.xpath('//a/text()')))
                thumb = None
                cover_file = None
            else:
                if thumb:
                    cover_file = thumb.rsplit('/')[-1]
                else:
                    cover_file = None
        except:
            thumb = None
            cover_file = None

        if not drama_test:
            summary = title_html.xpath('//p/text()')[0].strip()
        else:
            summary = drama_title_html.xpath('//p[@class="description"]/text()')[0].strip()

        a_node = item.xpath('./a')[0]

        item_url_base = a_node.get('href')
        item_sys_name = StringCode(string=item_url_base.rsplit('/')[-1].strip(), code='encode')
        item_url_final = base_url + StringCode(string=item_url_base, code='encode')
        Logger('\nitem_url_base = %s\nitem_sys_name = %s\nitem_url_final = %s' %(item_url_base, item_sys_name, item_url_final))
        Logger('thumb = %s' %thumb, kind='Info')

        if not drama_test:
            item_title = a_node.text.strip()
        else:
            item_title = a_node.xpath('./span[@class="title"]/text()')[0].strip()
        if 'Movie' in pname:
            title2 = item_title
        else:
            item_title_cleaned = Regex('[^a-zA-Z0-9 \n]').sub('', item_title)

            if not drama_test:
                latest = item.xpath('./following-sibling::td')[0].text_content().strip().replace(item_title_cleaned, '')
            else:
                try:
                    latest = item.xpath('./div[@class="ep-bg"]/a')[0].text_content()
                except:
                    latest = drama_title_html.xpath('./p')[1].text_content().split(' ')[1]
            latest = latest.replace('Read Online', '').replace('Watch Online', '').lstrip('_').strip()
            if 'Completed' in latest:
                title2 = '%s | %s Completed' %(item_title, type_title)
            elif 'Not yet aired' in latest:
                title2 = '%s | Not Yet Aired' %item_title
            else:
                title2 = '%s | Latest %s' %(item_title, latest)

        item_info = {
            'item_sys_name': item_sys_name,
            'item_title': StringCode(string=item_title, code='encode'),
            'short_summary': StringCode(string=summary, code='encode'),
            'cover_url': thumb,
            'cover_file': cover_file,
            'type_title': type_title,
            'base_url': base_url,
            'page_url': item_url_final,
            'art': art
            }

        # if thumb is hosted on kiss site then cache locally if Prefs Cache all covers
        cover = GetThumb(cover_url=thumb, cover_file=cover_file)

        oc.add(DirectoryObject(
            key=Callback(ItemPage, item_info=item_info),
            title=title2, summary=summary, thumb=cover, art=cover))

    if nextpg_node:  # if not 'None' then find the next page and create a button
        nextpg = int(nextpg_node.split('page=')[1])
        Logger('NextPage = %i' % nextpg)
        Logger('base url = %s' %base_url)
        oc.add(NextPageObject(
            key=Callback(DirectoryList,
                page=nextpg, pname=pname, category=category,
                base_url=base_url, type_title=type_title, art=art),
            title='Next Page>>', thumb=R(NEXT_ICON)))

    if len(oc) > 0:
        Dict.Save()
        return oc
    else:
        return MessageContainer(header=type_title, message='%s list is empty' %category)

####################################################################################################
@route(PREFIX + '/homedirectorylist')
def HomePageList(tab, category, base_url, type_title, art):
    """KissCartoon and KissAsian have 'Top' list on home page. This returns those list."""

    main_title = '%s | %s' % (type_title, category)
    oc = ObjectContainer(title2=main_title, art=R(art))

    html = HTML.ElementFromURL(base_url, headers=Headers.GetHeadersForURL(base_url))

    # scrape home page for Top (Day, Week, and Month) list
    for node in html.xpath('//div[@id="tab-top-%s"]/div' %tab):
        page_node = StringCode(string=node.xpath('./a')[1].get('href'), code='encode')
        item_sys_name = StringCode(string=page_node.split('/')[-1], code='encode')
        item_title = node.xpath('./a/span[@class="title"]/text()')[0]
        latest = node.xpath('./p/span[@class="info"][text()="Latest:"]/../a/text()')[0]
        title2 = '%s | Latest %s' %(item_title, latest)
        summary = 'NA'  # no summarys are given in the 'Top' lists
        try:
            thumb = Common.CorrectCoverImage(node.xpath('./a/img')[0].get('src'))
            if not 'http' in thumb:
                thumb = None
                cover_file = None
            else:
                cover_file = thumb.rsplit('/')[-1]
        except:
            thumb = None
            cover_file = None
        page_url = base_url + (page_node if page_node.startswith('/') else '/' + page_node)

        item_info = {
            'item_sys_name': item_sys_name,
            'item_title': StringCode(string=item_title, code='encode'),
            'short_summary': summary,
            'cover_url': thumb,
            'cover_file': cover_file,
            'type_title': type_title,
            'base_url': base_url,
            'page_url': page_url,
            'art': art
            }
        cover = GetThumb(cover_url=thumb, cover_file=cover_file)

        # send results to ItemPage
        oc.add(DirectoryObject(
            key=Callback(ItemPage, item_info=item_info), title=title2, thumb=cover, art=cover))

    Dict.Save()

    return oc

####################################################################################################
@route(PREFIX + '/item', item_info=dict)
def ItemPage(item_info):
    """Create the Media Page with the Video(s)/Chapter(s) section and a Bookmark option Add/Remove"""

    # set variables
    item_sys_name = item_info['item_sys_name']
    item_title = item_info['item_title']
    type_title = item_info['type_title']
    base_url = item_info['base_url']
    page_url = item_info['page_url']
    art = item_info['art']

    # decode string
    item_title_decode = StringCode(string=item_title, code='decode')

    # setup new title2 for container
    title2 = '%s | %s' % (type_title, item_title_decode)

    oc = ObjectContainer(title2=title2, art=R(art))

    if not Prefs['adult']:
        html = HTML.ElementFromURL(page_url, headers=Headers.GetHeadersForURL(base_url))

        # Check for Adult content, block if Prefs set.
        genres = html.xpath('//p[span[@class="info"]="Genres:"]/a/text()')
        Logger('genres = %s' %genres)
        if genres:
            matching_list = set(genres) & ADULT_LIST
            if len(matching_list) > 0:
                warning_string = ', '.join(list(matching_list))
                Logger('\n----------Adult Content Blocked: %s----------' %warning_string, force=True, kind='Info')
                return MessageContainer(header='Warning',
                    message='Adult Content Blocked: %s' %warning_string)

    # page category stings depending on media
    if not 'Manga' in type_title:
        category_thumb = CATEGORY_VIDEO_ICON
        page_category = 'Video(s)'
    else:
        category_thumb = CATEGORY_PICTURE_ICON
        page_category = 'Chapter(s)'

    # update item_info to include page_category
    item_info.update({'page_category': page_category})

    # format item_url for parsing
    Logger('page url = %s | base url = %s' %(page_url, base_url))

    # add video(s)/chapter(s) container
    oc.add(DirectoryObject(
        key=Callback(ItemSubPage, item_info=item_info),
        title=page_category,
        thumb=R(category_thumb),
        summary='List all currently avalible %s for \"%s\"' %
        (page_category.lower(), item_title_decode)))

    # Test if the Dict does have the 'Bookmarks' section
    bm = Dict['Bookmarks']
    if ((True if [b[type_title] for b in bm[type_title] if b[type_title] == item_sys_name] else False) if type_title in bm.keys() else False) if bm else False:
        # provide a way to remove Item from bookmarks list
        oc.add(DirectoryObject(
            key=Callback(RemoveBookmark, item_info=item_info),
            title='Remove Bookmark', thumb=R(BOOKMARK_REMOVE_ICON),
            summary = 'Remove \"%s\" from your Bookmarks list.' % item_title_decode))
    else:
        # Item not in 'Bookmarks' yet, so lets parse it for adding!
        oc.add(DirectoryObject(
            key=Callback(AddBookmark, item_info=item_info),
            title='Add Bookmark', thumb=R(BOOKMARK_ADD_ICON),
            summary='Add \"%s\" to your Bookmarks list.' % item_title_decode))

    return oc

####################################################################################################
@route(PREFIX + '/itemsubpage', item_info=dict)
def ItemSubPage(item_info):
    """Create the Item Sub Page with Video or Chapter list"""

    # set variables
    item_title = item_info['item_title']
    type_title = item_info['type_title']
    base_url = item_info['base_url']
    page_url = item_info['page_url']
    page_category = item_info['page_category']
    art = item_info['art']

    # decode string(s)
    item_title_decode = StringCode(string=item_title, code='decode')

    # setup title2 for container
    title2 = '%s | %s | %s' % (type_title, item_title_decode, page_category.lower())

    # remove special charaters from item_title for matching later
    item_title_decode = Regex('[^a-zA-Z0-9 \n\.]').sub('', item_title_decode)

    # remove '(s)' from page_category string for logs
    s_removed_page_category = page_category.rsplit('(')[0]

    oc = ObjectContainer(title2=title2, art=R(art))

    Logger('item sub page url = %s' %page_url)

    # setup html for parsing
    html = HTML.ElementFromURL(page_url, headers=Headers.GetHeadersForURL(base_url))

    # episode_list_node
    episode_list = html.xpath('//table[@class="listing"]/tr/td')

    # if no shows, then none have been added yet
    if not episode_list:
        return MessageContainer(header='Warning',
            message='%s \"%s\" Not Yet Aired.' %(type_title, item_title_decode))
    else:
        # parse html for media url, title and date added
        a = []
        b = []

        for media in episode_list:
            if media.xpath('./a'):
                node = media.xpath('./a')

                # url for Video/Chapter
                mpu_node = node[0].get('href').split('/')[-1].rsplit('?', 1)
                media_page_url = page_url + '/' + urllib2.quote((mpu_node[0]).encode("utf8")) + '?' + mpu_node[1]
                #Logger('* %s Page URL = %s' % (s_removed_page_category, media_page_url))

                # title for Video/Chapter, cleaned
                raw_title = Regex('[^a-zA-Z0-9 \n\.]').sub('', node[0].text).replace(item_title_decode, '')
                if not 'Manga' in type_title:
                    media_title = raw_title.replace('Watch Online', '').strip()
                else:
                    media_title = raw_title.replace('Read Online', '').strip()
                #Logger('* %s Title = %s' % (s_removed_page_category, media_title))

                a.append((media_page_url, media_title))
            else:
                # date Video/Chapter added
                date = media.text.strip()
                #Logger('date=%s' %date)
                b.append(date)

        # setup photo/video objects, Service URL's will do the rest
        if not 'Manga' in type_title:
            for x, y in map(None, a, b):
                video_info = {
                    'date': y,
                    'title': StringCode(string=x[1], code='encode'),
                    'video_page_url': x[0]
                    }

                if "movie" in x[1].lower():
                    video_info.update({'video_type': 'movie'})
                elif 'episode' in x[1].lower():
                    video_info.update({'video_type': 'episode'})
                else:
                    video_info.update({'video_type': 'na'})

                oc.add(DirectoryObject(
                    key=Callback(VideoDetail,
                        video_info=video_info, item_info=item_info),
                    title='%s | %s' % (x[1], y)))
        else:
            for x, y in map(None, a, b):
                oc.add(PhotoAlbumObject(url=x[0], title='%s | %s' % (x[1], y)))

        return oc

####################################################################################################
@route(PREFIX + '/videodetail', video_info=dict, item_info=dict)
def VideoDetail(video_info, item_info):
    """
    Create Video container
    Don't like that I need this, but if not the Service URL will parse all the videos
    and bog down the server respose time
    """

    # set variables
    title = StringCode(string=video_info['title'], code='decode')
    date = Datetime.ParseDate(video_info['date'])
    summary = item_info['short_summary']
    if summary:
        summary = StringCode(string=summary, code='decode')
    art = item_info['art']
    url = video_info['video_page_url']
    video_type = video_info['video_type']
    cover = GetThumb(cover_url=item_info['cover_url'], cover_file=item_info['cover_file'])

    oc = ObjectContainer(title2=title, art=R(art))

    Logger('video url in video detail section = %s' %url)

    # setup html for parsing
    html = HTML.ElementFromURL(url, headers=Headers.GetHeadersForURL(url))

    # test if video link is hosted on OneDrive
    # currently the URL Service is not setup to handle OneDrive Links
    onedrive_test = html.xpath('//div[@id="centerDivVideo"]//iframe')
    quality_test = html.xpath('//select[@id="selectQuality"]/option')
    if onedrive_test:
        if "onedrive" in onedrive_test[0].get('src'):
            return MessageContainer(header='Error',
                message='OneDrive Videos Not Yet Supported. Try another source if avalible.')
    elif not quality_test:
        return MessageContainer('Warning',
            'This video is broken, Kiss%s is working to fix it.' %item_info['type_title'])

    # Movie
    if video_type == 'movie':
        oc.add(
            MovieObject(
                title=title,
                summary=summary,
                originally_available_at=date,
                thumb=cover,
                art=R(art),
                url=url))
    # TV Episode
    elif video_type == 'episode':
        oc.add(
            EpisodeObject(
                title=title,
                summary=summary,
                thumb=cover,
                art=R(art),
                originally_available_at=date,
                url=url))
    # everything else
    else:
        oc.add(
            VideoClipObject(
                title=title,
                summary=summary,
                thumb=cover,
                art=R(art),
                originally_available_at=date,
                url=url))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Set up Search for kiss(anime, asian, cartoon, manga)"""

    # set defaults
    title2 = 'Search for \"%s\" in...' % query

    oc = ObjectContainer(title2=title2)
    # create list of search URL's
    all_search_urls = [ANIME_SEARCH_URL, CARTOON_SEARCH_URL, ASIAN_SEARCH_URL, MANGA_SEARCH_URL]

    # format each search url and send to 'SearchPage'
    # can't check each url here, would take too long since behind cloudflare and timeout the server
    for search_url in all_search_urls:
        search_url_filled = search_url % String.Quote(query, usePlus=True)
        type_title = search_url.rsplit('/')[2].rsplit('kiss', 1)[1].rsplit('.', 1)[0].title()
        # change kissasian info to 'Drama'
        if type_title == 'Asian':
            type_title = 'Drama'
            art = ASIAN_ART
            thumb = ASIAN_ICON
            prefs_name = 'kissasian'
        else:
            art = 'art-%s.jpg' % type_title.lower()
            thumb = 'icon-%s.png' % type_title.lower()
            prefs_name = 'kiss%s' %type_title.lower()

        if Prefs[prefs_name]:
            Logger('Search url = %s' % search_url_filled)
            Logger('type title = %s' %type_title)

            html = HTML.ElementFromURL(search_url_filled, headers=Headers.GetHeadersForURL(search_url))
            if html.xpath('//table[@class="listing"]'):
                oc.add(DirectoryObject(
                    key=Callback(SearchPage, type_title=type_title, search_url=search_url_filled, art=art),
                    title=type_title, thumb=R(thumb)))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Search',
            'There are no search results for \"%s\". Try being less specific or make sure at least one source is selected in Preferences.' %query)

####################################################################################################
@route(PREFIX + '/searchpage')
def SearchPage(type_title, search_url, art):
    """
    Retrun searches for each kiss() page
    The results can return the Item itself via a url redirect.
    Check for "exact" matches and send them to ItemPage
    If normal seach result then send to DirectoryList
    """

    html = HTML.ElementFromURL(search_url, headers=Headers.GetHeadersForURL(search_url))

    # Check for results if none then give a pop up window saying so
    if html.xpath('//table[@class="listing"]'):
        # Test for "exact" match, if True then send to 'ItemPage'
        node = html.xpath('//div[@id="headnav"]/script/text()')[0]
        search_match = Regex('var\ path\ =\ (\'Search\')').search(node)
        if not search_match:
            # Send url to 'ItemPage'
            base_url = Common.GetBaseURL(search_url)
            node = html.xpath('//div[@class="barContent"]/div/a')[0]

            item_sys_name = StringCode(string=node.get('href').rsplit('/')[-1].strip(), code='encode')
            item_url = base_url + '/' + type_title + '/' + StringCode(item_sys_name, code='encode')
            item_title = node.text
            try:
                cover_url = Common.CorrectCoverImage(html.xpath('//head/link[@rel="image_src"]')[0].get('href'))
                if not 'http' in cover_url:
                    cover_url = None
                    cover_file = None
                elif 'kiss' in cover_url:
                    cover_file = cover_url.rsplit('/')[-1]
                else:
                    cover_file = None
            except:
                cover_url = None
                cover_file = None

            Logger('\nitem_title=%s\nitem=%s\ntype_title=%s\nbase_url=%s\nitem_url=%s'
                % (item_title, item_sys_name, type_title, base_url, item_url))

            item_info = {
                'item_sys_name': item_sys_name,
                'item_title': StringCode(string=item_title, code='encode'),
                'short_summary': None,
                'cover_url': cover_url,
                'cover_file': cover_file,
                'type_title': type_title,
                'base_url': base_url,
                'page_url': item_url,
                'art': art}

            return ItemPage(item_info=item_info)
        else:
            # Send results to 'DirectoryList'
            query = search_url.rsplit('=')[-1]
            Logger('art = %s' %art, kind='Info')
            return DirectoryList(1, 'Search', query, search_url, type_title, art)
    # No results found :( keep trying
    else:
        Logger('Search returned no results.', kind='Warn')
        query = search_url.rsplit('=')[-1]
        return MessageContainer('Search',
            """
            There are no search results for \"%s\" in \"%s\" Category.
            Try being less specific.
            """ %(query, type_title))

####################################################################################################
@route(PREFIX + '/addbookmark', item_info=dict)
def AddBookmark(item_info):
    """Adds Item to the bookmarks list"""

    # set variables
    item_sys_name = item_info['item_sys_name']
    item_title = item_info['item_title']
    type_title = item_info['type_title']
    cover_url = item_info['cover_url']
    short_summary = item_info['short_summary']
    page_url = item_info['page_url']
    base_url = item_info['base_url']

    # decode title string
    item_title_decode = StringCode(string=item_title, code='decode')

    Logger('item to add = %s | %s' %(item_title_decode, item_sys_name), kind='Info')

    # setup html for parsing
    html = HTML.ElementFromURL(page_url, headers=Headers.GetHeadersForURL(base_url))

    # Genres
    genres = html.xpath('//p[span[@class="info"]="Genres:"]/a/text()')
    if genres:
        genres = ' '.join([g.replace(' ', '_') for g in genres])
    else:
        genres = ''

    # if no cover url then try and find one on the item page
    if cover_url:
        cover_url = Common.CorrectCoverImage(cover_url)
    else:
        try:
            cover_url = Common.CorrectCoverImage(html.xpath('//head/link[@rel="image_src"]')[0].get('href'))
            if not 'http' in cover_url:
                cover_url = None
        except:
            cover_url = None
    # Option to store covers locally as files
    if cover_url:
        try:
            image_file = cover_url.split('/', 3)[3].replace('/', '_')
        except:
            image_file = None
        if Prefs['cache_covers'] or Prefs['cache_bookmark_covers']:
            if not Common.CoverImageFileExist(image_file):
                try:
                    image_file = SaveCoverImage(cover_url)
                except:
                    image_file = None
    else:
        image_file = None

    # set full summary
    summary = html.xpath('//p[span[@class="info"]="Summary:"]/following-sibling::p')
    # if summary found in <p> after <p><span>Summary:</span></p>
    if summary:
        Logger('summary in <p>', kind='Info')
        p_list = html.xpath('//div[@id="container"]//p')
        p_num = len(p_list)
        match = int(0)
        for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
            if node.xpath('./span[@class="info"]="Summary:"'):
                match = int(i) + 1
                break

        new_p_list = p_list[match:p_num]
        sum_list = []
        for node in new_p_list:
            if node is not None:
                sum_text = node.text_content().strip()
                if sum_text:
                    sum_list.append(sum_text)

        if len(sum_list) > 1:
            Logger('summary was in %i <p>\'s' %int(len(sum_list)), kind='Info')
            summary = '\n\n'.join(sum_list).replace('Related Series', '').replace('Related:', '').strip().replace('\n\n\n', '\n')
        else:
            if len(sum_list) == 1:
                Logger('summary was in the only <p>', kind='Info')
                summary = sum_list[0]
            else:
                Logger('no summary found in <p>\'s, setting to \"None\"', force=True)
                summary = None
    else:
        summary = html.xpath('//p[span[@class="info"]="Summary:"]/following-sibling::p/span')
        # if summary found in <p><span> after <p><span>Summary:</span></p>
        if summary:
            Logger('summary is in <p><span>', kind='Info')
            summary = summary[0].text_content().strip()
        else:
            summary = html.xpath('//div[@id="container"]//div[@class="barContent"]/table//td')
            # if summary found in own <table>
            if summary:
                Logger('summary is in own <table>', kind='Info')
                summary = summary[0].text_content().strip()
            else:
                summary = html.xpath('//div[@id="container"]//div[@class="bigBarContainer"]/div[@class="barContent"]/div/div')
                # if summary found in own <div>
                if summary:
                    Logger('summary is in own <div>', kind='Info')
                    summary = summary[0].text_content().strip()
                    # fix string encoding errors before they happen by encoding
                    #summary = StringCode(string=summary, code='encode')
                else:
                    summary = html.xpath('//p[span[@class="info"]="Summary:"]')
                    # summary may be in <p><span>Summary:</span>summary</p>, ie text outside Summary span
                    if summary:
                        summary = summary[0].text_content().strip()
                        test = Regex('(?s)Summary\:.+?([\S].+)').search(summary)
                        if test:
                            Logger('summary is in <p><span>Summary:</span>summary</p>', kind='Info')
                            summary = test.group(1).strip()
                        else:
                            # if no summary found then set to 'None'
                            Logger('no summary found, setting summary to \"None\"', kind='Info')
                            summary = None
                    else:
                        # if no summary found then set to 'None'
                        Logger('no summary found, setting summary to \"None\"', kind='Info')
                        summary = None

    if summary:
        Logger('summary = %s' %summary, kind='Debug')
        summary = StringCode(string=summary, code='encode')

    # setup new bookmark json data to add to Dict

    new_bookmark = {
        type_title: item_sys_name, 'item_title': item_title, 'cover_file': image_file,
        'cover_url': cover_url, 'summary': summary, 'genres': genres, 'page_url': page_url}

    Logger('new bookmark to add\n%s' % new_bookmark)

    bm = Dict['Bookmarks']

    # Test if the Dict has the 'Bookmarks' section yet
    if not bm:
        # Create new 'Bookmarks' section and fill with the first bookmark
        Dict['Bookmarks'] = {type_title: [new_bookmark]}
        Logger('Inital bookmark list created\n%s' %bm)

        # Update Dict to include new 'Bookmarks' section
        Dict.Save()

        # Provide feedback that the Item has been added to bookmarks
        return MessageContainer(header=item_title_decode,
            message='\"%s\" has been added to your bookmarks.' % item_title_decode)
    # check if the category key 'Anime', 'Manga', 'Cartoon', or 'Drama' exist
    # if so then append new bookmark to one of those categories
    elif type_title in bm.keys():
        # fail safe for when clients are out of sync and it trys to add the bookmark in duplicate
        if (True if [b[type_title] for b in bm[type_title] if b[type_title] == item_sys_name] else False):
            # Bookmark already exist, don't add in duplicate
            Logger('bookmark \"%s\" already in your bookmarks' %item_title_decode, kind='Info')
            return MessageContainer(header=item_title_decode,
                message='\"%s\" is already in your bookmarks.' % item_title_decode)
        # append new bookmark to its correct category, i.e. 'Anime', 'Drama', etc...
        else:
            temp = {}
            temp.setdefault(type_title, bm[type_title]).append(new_bookmark)
            Dict['Bookmarks'][type_title] = temp[type_title]
            Logger('bookmark \"%s\" has been appended to your %s bookmarks' %(item_title_decode, type_title), kind='Info')

            # Update Dict to include new Item
            Dict.Save()

            # Provide feedback that the Item has been added to bookmarks
            return MessageContainer(header=item_title_decode,
                message='\"%s\" has been added to your bookmarks.' % item_title_decode)
    # the category key does not exist yet so create it and fill with new bookmark
    else:
        Dict['Bookmarks'].update({type_title: [new_bookmark]})
        Logger('bookmark \"%s\" has been created in new %s section in bookmarks' %(item_title_decode, type_title), kind='Info')

        # Update Dict to include new Item
        Dict.Save()

        # Provide feedback that the Item has been added to bookmarks
        return MessageContainer(header=item_title_decode,
            message='\"%s\" has been added to your bookmarks.' % item_title_decode)

####################################################################################################
@route(PREFIX + '/removebookmark', item_info=dict)
def RemoveBookmark(item_info):
    """Removes item from the bookmarks list using the item as a key"""

    # set variables
    item_sys_name = item_info['item_sys_name']
    item_title = item_info['item_title']
    type_title = item_info['type_title']

    # decode string
    item_title_decode = StringCode(string=item_title, code='decode')

    # index 'Bookmarks' list
    bm = Dict['Bookmarks'][type_title]
    #Logger('bookmarks = %s' %bm)
    Logger('bookmark length = %s' %len(bm))
    for i in xrange(len(bm)):
        # remove item's data from 'Bookmarks' list
        if bm[i][type_title] == item_sys_name:
            # if caching covers, then don't remove cover file
            if Prefs['cache_covers']:
                bm.pop(i)
            else:
                RemoveCoverImage(bm[i]['cover_file'])
                bm.pop(i)

            break

    # update Dict, and debug log
    Dict.Save()
    Logger('\"%s\" has been removed from Bookmark List' % item_title_decode, kind='Info')

    if len(bm) == 0:
        # if the last bookmark was removed then clear it's bookmark section
        Logger('%s bookmark was the last, so removed %s bookmark section' %(item_title_decode, type_title), force=True)
        return ClearBookmarks(type_title)
    else:
        # Provide feedback that the Item has been removed from the 'Bookmarks' list
        return MessageContainer(header=type_title,
            message='\"%s\" has been removed from your bookmarks.' % item_title_decode)

####################################################################################################
@route(PREFIX + '/clearbookmarks')
def ClearBookmarks(type_title):
    """Remove 'Bookmarks' Section(s) from Dict. Note: This removes all bookmarks in list"""

    if 'All' in type_title:
        if not Prefs['cache_covers']:
            for key in Dict['Bookmarks'].keys():
                for bookmark in Dict['Bookmarks'][key]:
                    RemoveCoverImage(bookmark['cover_file'])

        # delete 'Bookmarks' section from Dict
        del Dict['Bookmarks']
        Logger('Entire Bookmark Dict Removed')
    else:
        if not Prefs['cache_covers']:
            for bookmark in Dict['Bookmarks'][type_title]:
                RemoveCoverImage(bookmark['cover_file'])

        # delete section 'Anime', 'Manga', 'Cartoon', or 'Drama' from bookmark list
        del Dict['Bookmarks'][type_title]
        Logger('\"%s\" Bookmark Section Cleared' % type_title)

    Dict['Bookmark_Deleted'] = {'bool': True, 'type_title': type_title}
    status = Dict['Bookmark_Deleted']

    # update Dict
    Dict.Save()

    # Provide feedback that the correct 'Bookmarks' section is removed
    #   and send back to Bookmark Main Menu
    return BookmarksMain(title='My Bookmarks', status=status)

####################################################################################################
@route(PREFIX + '/cache-covers', start=bool)
def CacheCovers(start=False, skip=True):
    """Cache covers depending on prefs settings. Will remove or add covers if it can."""

    bm = Dict['Bookmarks']
    cf = Dict['cover_files']

    if not Dict['cache_covers_key']:
        Dict['cache_covers_key'] = Prefs['cache_covers']
        Dict['cache_bookmark_covers_key'] = Prefs['cache_bookmark_covers']

    if (Prefs['cache_bookmark_covers'] == Dict['cache_bookmark_covers_key'] and
        Prefs['cache_covers'] == Dict['cache_covers_key'] and start == False or skip == True):
        Dict.Save()
        # Attempt to update Anime Bookmarks to new domain and genres
        if skip == True and bm:
            if 'Anime' in bm.keys():
                Thread.Create(BookmarksSub, type_title='Anime', art='anime-art.jpg')
                Logger('Attempting to update Anime Bookmarks', kind='Debug', force=True)
        Logger('Skipping Caching Covers on Prefs Update. Bookmark Covers Already Cached.', kind='Info', force=True)
        return

    if not Prefs['cache_bookmark_covers'] and not Prefs['cache_covers']:
        # remove any cached covers from Dict['Bookmarks']
        # unless Prefs['cache_covers'] is true, then keep cached covers
        if cf:
            for cover in cf:
                RemoveCoverImage(image_file=cf[cover])

            del Dict['cover_files']
            Dict.Save()
            Logger('Removed cached covers using Dict[\'cover_files\'] list as key, and removed Dict[\'cover_files\'] once finished.', kind='Info')
        elif bm:
            [[RemoveCoverImage(image_file=bbm['cover_file']) for bbm in bm[key]] for key in bm.keys()]

            Logger('No Dict[\'cover_files\'] found, Removed cached covers using Dict[\'Bookmarks\'] list as key.', kind='Info')
    elif not Prefs['cache_covers'] and Prefs['cache_bookmark_covers']:
        # remove cached covers not in Dict['Bookmarks']
        # and save covers from Dict['Bookmarks'] in not already saved
        bookmark_cache = set([])
        if bm:
            for key in bm.keys():
                for sbm in bm[key]:
                    bm_count = len(bm[key])
                    if sbm['cover_file'] and sbm['cover_url']:
                        cover_file = sbm['cover_file']
                        bookmark_cache.add(cover_file)
                        thumb = Common.CorrectCoverImage(sbm['cover_url'])
                        if not Common.CoverImageFileExist(cover_file) and bm_count <= 50:
                            Thread.Create(SaveCoverImage, image_url=thumb)
                        elif not Common.CoverImageFileExist(cover_file):
                            ftimer = float(Util.RandomInt(0,30)) + Util.Random()
                            Thread.CreateTimer(interval=ftimer, f=SaveCoverImage, image_url=thumb)
                        elif Common.CoverImageFileExist(cover_file):
                            Logger('file %s already exist' %cover_file, kind='Info')
                        else:
                            Log.Error('%s | %s | Unknown Error Occurred' %(cover_file, thumb))
                    else:
                        Log.Error('%s | %s | Unknown Error Occurred' %(sbm['cover_file'], sbm['cover_url']))

        Logger('Caching Bookmark Cover images if they have not been already.', kind='Info')
        if cf:
            cover_cache = set([c for c in cf])
            cover_cache_diff = cover_cache.difference(bookmark_cache)
            for cover in cover_cache_diff:
                RemoveCoverImage(image_file=cf[cover])
                del Dict['cover_files'][cover]

            Logger('Removed cached covers using Dict[\'cover_files\'] list as key, and removed Dict[\'cover_files\'] once finished.', kind='Info')
            Logger('But kept Bookmarks cached covers.', kind='Info')
    elif Prefs['cache_covers']:
        # cache bookmark covers from Dict['Bookmarks']
        if bm:
            for key in bm.keys():
                for sbm in bm[key]:
                    bm_count = len(bm[key])
                    if sbm['cover_file'] and sbm['cover_url']:
                        cover_file = sbm['cover_file']
                        thumb = Common.CorrectCoverImage(sbm['cover_url'])
                        if not Common.CoverImageFileExist(cover_file) and bm_count <= 50:
                            Thread.Create(SaveCoverImage, image_url=thumb)
                        elif not Common.CoverImageFileExist(cover_file):
                            ftimer = float(Util.RandomInt(0,30)) + Util.Random()
                            Thread.CreateTimer(interval=ftimer, f=SaveCoverImage, image_url=thumb)
                        elif Common.CoverImageFileExist(cover_file):
                            Logger('file %s already exist' %cover_file, kind='Info')
                        else:
                            Log.Error('%s | %s | Unknown Error Occurred' %(cover_file, thumb))
                    else:
                        Log.Error('%s | %s | Unknown Error Occurred' %(sbm['cover_file'], sbm['cover_url']))

        Logger('Caching Bookmark Cover images if they have not been already.', kind='Info')
        Logger('All covers cached set to True.', kind='Info')

    Dict.Save()
    return

####################################################################################################
def Test():
    """
    Testing bookmark cache stuff
    Trying to get rid of so many nested for loops and if/else statments
    """

    Logger('*' * 80)
    bm = Dict['Bookmarks']
    test = []
    if [[((test.append(Common.CorrectCoverImage(sbm['cover_url'])) if 'kiss' in sbm['cover_url'] else None) if (sbm['cover_file'] and sbm['cover_url']) else None) for sbm in bm[key]] for key in bm.keys()] if bm else []:
        Logger('* we have bookmarks')
    else:
        Logger('* no bookmarks')

    Logger('* test list = %s' %test)
    Logger('*' * 80)

    return test

####################################################################################################
def CacheAllCovers(category, qevent, page=1):
    """Cache All, or any one of the Categories"""

    if category == 'Drama':
        ncategory = 'Asian'
        drama_test = True
    else:
        ncategory = category
        drama_test = False
    base_url = Common.Domain_Dict[ncategory]
    item_url = base_url + '/%sList?page=%s' % (category, page)

    html = HTML.ElementFromURL(item_url, headers=Headers.GetHeadersForURL(base_url))

    nextpg_node = None
    # parse html for 'next' page node
    for node in html.xpath('///div[@class="pagination pagination-left"]//li/a'):
        if "Next" in node.text:
            nextpg_node = str(node.get('href'))  # pull out next page if exist
            break

    listing = html.xpath('//table[@class="listing"]//td[@title]')
    if not listing:
        listing = html.xpath('//div[@class="item"]')

    for item in listing:
        if not drama_test:
            title_html = HTML.ElementFromString(item.get('title'))
        else:
            title_html = item
            drama_title_html = HTML.ElementFromString(item.get('title'))

        try:
            if drama_test:
                thumb = Common.CorrectCoverImage(item.xpath('./a/img/@src')[0])
            else:
                thumb = Common.CorrectCoverImage(title_html.xpath('//img/@src')[0])
            if 'kiss' in thumb:
                cover_file = thumb.rsplit('/')[-1]
            elif 'http' in thumb:
                cover_file = thumb.split('/', 3)[3].replace('/', '_')
            else:
                Log.Debug('thumb missing valid url. | %s' %thumb)
                Log.Debug('thumb xpath = %s' %title_html.xpath('//img/@src'))
                Log.Debug('item name | %s | %s' %(title_html.xpath('//a/@href'), title_html.xpath('//a/text()')))
                thumb = None
                cover_file = None
        except:
            thumb = None
            cover_file = None

        if thumb:
            if (not Common.CoverImageFileExist(cover_file)) and ('kiss' in thumb):
                timer = float(Util.RandomInt(0,30)) + Util.Random()
                Thread.CreateTimer(interval=timer, f=SaveCoverImage, image_url=thumb)

    if nextpg_node:
        sleep(2)  # wait 2 sec before calling next page
        Dict.Save()
        nextpg = int(nextpg_node.split('page=')[1])
        return CacheAllCovers(category=category, qevent=qevent, page=nextpg)
    else:
        Dict.Save()
        sleep(5)  # wait 5 seconds before starting next Threaded instance of CacheAllCovers for next Category
        qevent.set()  # set Event object to True for 'for loop' in CacheCoverQ()
        Log.Info(
            '%s Finished caching covers. Set qevent to %s, so next category can start caching covers.'
            %(category, qevent.is_set()))
        return

####################################################################################################
@route(PREFIX + '/save-cover-image', count=int)
def SaveCoverImage(image_url, count=0):
    """Save image to Cover Image Path and return the file name"""

    if 'kiss' in image_url:
        content_url = Common.GetBaseURL(image_url) + '/' + image_url.split('/', 3)[3]
        image_file = content_url.rsplit('/')[-1]
    else:
        content_url = image_url
        image_file = image_url.split('/', 3)[3].replace('/', '_')

    path = Core.storage.join_path(Common.RESOURCES_PATH, image_file)
    Logger('image file path = %s' %path)

    if not Core.storage.file_exists(path):
        if 'kiss' in content_url:
            r = requests.get(content_url, headers=Headers.GetHeadersForURL(content_url), stream=True)
        else:
            r = requests.get(content_url, stream=True)

        if r.status_code == 200:
            with io.open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            Logger('saved image %s' %image_file)
            #Logger('saved image %s in path %s' %(image_file, path))
            # create dict for cover files, so we can clear them later
            #   seperate from bookmark covers if need be
            if Dict['cover_files']:
                Dict['cover_files'].update({image_file: image_file})
            else:
                Dict['cover_files'] = {image_file: image_file}

            #Dict.Save()
            return image_file
        elif r.status_code == 503 and count < 3:
            count += 1
            timer = float(Util.RandomInt(5,10)) + Util.Random()
            Logger(
                '%s error code. Polling site too fast. Waiting %f sec then try again, try up to 3 times. Try %i'
                %(r.status_code, timer, count), kind='Warn', force=True)
            Thread.CreateTimer(interval=timer, f=SaveCoverImage, image_url=content_url, count=count, name=name)
        else:
            Logger('status code for image url = %s' %r.status_code)
            Logger('image url not found | %s' %content_url, force=True, kind='Error')
            return None  #replace with "no image" icon later
    else:
        Logger('file %s already exists' %image_file)
        return image_file

####################################################################################################
@route(PREFIX + '/remove-cover-image')
def RemoveCoverImage(image_file):
    """Remove Cover Image"""
    if image_file:
        path = Core.storage.join_path(Common.RESOURCES_PATH, image_file)

        if Core.storage.file_exists(path):
            Core.storage.remove(path)
        else:
            pass
    else:
        pass

    return

####################################################################################################
def UpdateLegacyBookmark(bm_info=dict):
    """
    Update Old Bookmark to new Style of bookmarks.
    Update includes "Genres" for now, will add more here later if need be
    """

    type_title = bm_info['type_title']
    item_title = bm_info['item_title']
    item_title_decode = StringCode(string=item_title, code='decode')
    base_url = bm_info['base_url']
    page_url = base_url + '/' + bm_info['page_url'].split('/', 3)[3]

    html = HTML.ElementFromURL(page_url, headers=Headers.GetHeadersForURL(bm_info['base_url']))

    if bm_info['cover_url'] and base_url in bm_info['cover_url']:
        cover_url = base_url + '/' + bm_info['cover_url'].split('/', 3)[3]
    elif base_url in bm_info['cover_url']:
        try:
            cover_url = base_url + '/' + Common.CorrectCoverImage(html.xpath('//head/link[@rel="image_src"]')[0].get('href').split('/', 3)[3])
            if not 'http' in cover_url:
                cover_url = None
        except:
            cover_url = None
    else:
        try:
            cover_url = Common.CorrectCoverImage(html.xpath('//head/link[@rel="image_src"]')[0].get('href'))
            if not 'http' in cover_url:
                cover_url = None
        except:
            cover_url = None

    genres = html.xpath('//p[span[@class="info"]="Genres:"]/a/text()')
    if genres:
        genres = ' '.join([g.replace(' ', '_') for g in genres])
    else:
        genres = ''

    new_bookmark = {
        type_title: bm_info['item_sys_name'], 'item_title': item_title,
        'cover_file': bm_info['cover_file'], 'cover_url': cover_url,
        'summary': bm_info['short_summary'], 'genres': genres, 'page_url': page_url}

    bm = Dict['Bookmarks'][type_title]
    for i in xrange(len(bm)):
        if bm[i][type_title] == new_bookmark[type_title]:
            Log.Debug('*' * 80)

            bm[i].update(new_bookmark)
            Logger('* %s Bookmark \"%s\" Updated' %(type_title, item_title_decode), kind='Info', force=True)

            Log.Debug('* updated bookmark = %s' %bm[i])
            Log.Debug('*' * 80)
            break

    # Update Dict to include new Item
    Dict.Save()

    return

####################################################################################################
@route(PREFIX + '/string-code', string=str, code=str)
def StringCode(string, code):
    """Handle String Coding"""

    if code == 'encode':
        string_code = urllib.quote(string.encode('utf8'))
    elif code == 'decode':
        # Â artifact in Windows OS, don't know why, think it has to do with the Dict protocall
        string_code = urllib.unquote(string).decode('utf8').replace('Â', '')

    return string_code

####################################################################################################
@route(PREFIX + '/dirsize')
def GetDirSize(start_path='.'):
    """Get Directory Size in Megabytes or Gigabytes. Returns String rounded to 3 decimal places"""

    try:
        bsize = 1000  #1000 decimal, 1024 binary
        total_size = 0
        count = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                # filter out default files
                if not Regex('(^icon\-(?:\S+)\.png$|^art\-(?:\S+)\.jpg$)').search(f):
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
                    count += 1

        if total_size > float(1000000000):
            # gigabytes
            for i in range(3):
                total_size = total_size / bsize
            d = '%i Cached | %s GB Used' %(count, str(round(total_size, 3)))
        elif total_size > float(1000000):
            # megabytes
            for i in range(2):
                total_size = total_size / bsize
            d = '%i Cached | %s MB Used' %(count, str(round(total_size, 3)))
        else:
            # kilobytes
            for i in range(1):
                total_size = total_size / bsize
            d = '%i Cached | %s kB Used' %(count, str(round(total_size, 3)))

        return d
    except:
        return 'Error'

####################################################################################################
@route(PREFIX + '/cftest')
def SetUpCFTest():
    """setup test for cfscrape"""

    if not Dict['cfscrape_test']:
        try:
            cftest = Headers.CFTest()
            Log.Info('\n----------CFTest passed! Aime Cookies:----------\n%s' %cftest)
            Dict['cfscrape_test'] = True
            Dict.Save()
        except:
            Dict['cfscrape_test'] = False
            Dict.Save()
            Log.Error(
                """
                ----------CFTest Fail----------
                You need to install a JavaScript Runtime like node.js or equivalent
                """
                )
    else:
        Log.Info('\n----------CFTest Previously Passed, not running again.----------')

    return

####################################################################################################
@route(PREFIX + '/auto-cache')
def BackgroundAutoCache():
    """Auto Cache Headers"""

    if not Dict['patch_anime_domain']:
        start = False
        skip = True
        ResetCustomDict('Domain_Dict')
        Dict['patch_anime_domain'] = True
    else:
        skip = False
        start = True

    # setup urls for setting headers
    if not Dict['First Headers Cached']:
        Logger('\n----------Running Background Auto-Cache----------', force=True)

        if Core.storage.file_exists(Core.storage.join_path(Core.storage.data_path, 'Header_Dict')):
            Logger('\n----------Header Dictionary already found, writing new Headers to old Dictionary----------', force=True)

            # get headers for each url
            for url in Common.BASE_URL_LIST:
                Headers.GetHeadersForURL(url)

        else:
            # Header Dictionary not yet setup, so create it and fill in the data
            Headers.CreateHeadersDict()

        # check to make sure each section/url has cookies now
        Logger('\n----------All cookies----------\n%s' %Headers.LoadHeaderDict())

        # Setup the Dict and save
        Dict['First Headers Cached'] = True
        Dict['Headers Auto Cached'] = True
        Dict.Save()
    else:
        for url in Common.BASE_URL_LIST:
            Logger('\n----------Checking %s headers----------' %url, kind='Info', force=True)
            Headers.GetHeadersForURL(url)

        Logger('\n----------Completed Header Cache Check----------', kind='Info', force=True)
        Logger('\n----------Headers will be cached independently when needed from now on----------', kind='Info', force=True)
        pass

    return ValidatePrefs(start=start, skip=skip)

####################################################################################################
def RestartChannel():
    """Try to Restart the KissNetwork Channel"""

    try:
        # touch Contents/Code/__init__.py
        #os.utime(os.path.join(Common.BUNDLE_PATH, 'Contents', 'Code', '__init__.py'), None)
        plist_path = Core.storage.join_path(Common.BUNDLE_PATH, "Contents", "Info.plist")
        Core.storage.utime(plist_path, None)
        return True
    except Exception, e:
        Log.Error(e)
        return False

####################################################################################################
def GetThumb(cover_url, cover_file):
    """
    Get Thumb
    Return cover file or save new cover and return cover caching icon
    """

    cover = None
    if not cover_url:
        return cover
    elif 'kiss' in cover_url:
        if Prefs['cache_covers'] and cover_file:
            Logger('* cover file name = %s' %cover_file)
            if Common.CoverImageFileExist(cover_file):
                if cover_file in Dict['cover_files']:
                    cover = R(cover_file)
                else:
                    Logger('* cover not in cache dict yet, adding to Dict[\'cover_files\'] now')
                    Dict['cover_files'].update({cover_file: cover_file})
                    cover = R(cover_file)
            else:
                Logger('* cover not yet saved, saving %s now' %cover_file)
                cover = R(CACHE_COVER_ICON)
                Thread.Create(SaveCoverImage, image_url=cover_url)
    elif 'http' in cover_url:
        cover = Common.CorrectCoverImage(cover_url)

    return cover

####################################################################################################
@route(PREFIX + '/logger', force=bool)
def Logger(message, force=False, kind=None):
    """Setup logging options based on prefs, indirect because it has no return"""

    if force or Prefs['debug']:
        if kind == 'Debug' or kind == None:
            Log.Debug(message)
        elif kind == 'Info':
            Log.Info(message)
        elif kind == 'Warn':
            Log.Warn(message)
        elif kind == 'Error':
            Log.Error(message)
        elif kind == 'Critical':
            Log.Critical(message)
    else:
        pass

    return
