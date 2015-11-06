####################################################################################################
#                                                                                                  #
#                               KissNetwork Plex Channel -- v0.06                                  #
#                                                                                                  #
####################################################################################################
# import section(s) not included in Plex Plug-In Framework
import os, sys, shutil, io, urllib

# import Shared Service Code
Test = SharedCodeService.test
Domain = SharedCodeService.domain

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
TITLE = 'KissNetwork'
VERSION = '0.06'
LIST_VIEW_CLIENTS = ['Android', 'iOS']
ADULT_LIST = set(['Adult', 'Smut', 'Ecchi', 'Lolicon', 'Mature', 'Yaoi', 'Yuri'])

# KissAnime
ANIME_BASE_URL = Test.ANIME_BASE_URL
ANIME_SEARCH_URL = ANIME_BASE_URL + '/Search/Anime?keyword=%s'
ANIME_ART = 'art-anime.jpg'
ANIME_ICON = 'icon-anime.png'

# KissAsian
ASIAN_BASE_URL = Test.ASIAN_BASE_URL
ASIAN_SEARCH_URL = ASIAN_BASE_URL + '/Search/Drama?keyword=%s'
ASIAN_ART = 'art-drama.jpg'
ASIAN_ICON = 'icon-drama.png'

# KissCartoon
CARTOON_BASE_URL = Test.CARTOON_BASE_URL
CARTOON_SEARCH_URL = CARTOON_BASE_URL + '/Search/Cartoon?keyword=%s'
CARTOON_ART = 'art-cartoon.jpg'
CARTOON_ICON = 'icon-cartoon.png'

# KissManga
MANGA_BASE_URL = Test.MANGA_BASE_URL
MANGA_SEARCH_URL = MANGA_BASE_URL + '/Search/Manga?keyword=%s'
MANGA_ART = 'art-manga.jpg'
MANGA_ICON = 'icon-manga.png'

# setup all url list
BASE_URL_LIST = [ANIME_BASE_URL, ASIAN_BASE_URL, CARTOON_BASE_URL, MANGA_BASE_URL]

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

    HTTP.CacheTime = 0
    HTTP.Headers['User-Agent'] = Test.USER_AGENT

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

        # Validate Prefs
        ValidatePrefs()
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
    if Client.Platform in LIST_VIEW_CLIENTS:
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
    oc.add(PrefsObject(title='Preferences', thumb=prefs_thumb))
    oc.add(DirectoryObject(key=Callback(About), title='About / Help', thumb=about_thumb))
    oc.add(InputDirectoryObject(
        key=Callback(Search), title='Search', summary='Search KissNetwork', prompt='Search for...',
        thumb=search_thumb))

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
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/LatestUpdate', category='Latest Update', base_url=url, type_title=title, art=art),
        title='Latest Update'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Newest', category='New Drama', base_url=url, type_title=title, art=art),
        title='New Drama'))
    oc.add(DirectoryObject(
        key=Callback(HomePageList,
            tab='day', category='Top Day', base_url=url, type_title=title, art=art),
        title='Top Day'))
    oc.add(DirectoryObject(
        key=Callback(HomePageList,
            tab='week', category='Top Week', base_url=url, type_title=title, art=art),
        title='Top Week'))
    oc.add(DirectoryObject(
        key=Callback(HomePageList,
            tab='month', category='Top Month', base_url=url, type_title=title, art=art),
        title='Top Month'))
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
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/LatestUpdate', category='Latest Update', base_url=url, type_title=title, art=art),
        title='Latest Update'))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Newest', category='New Cartoon', base_url=url, type_title=title, art=art),
        title='New Cartoon'))
    oc.add(DirectoryObject(
        key=Callback(HomePageList,
            tab='day', category='Top Day', base_url=url, type_title=title, art=art),
        title='Top Day'))
    oc.add(DirectoryObject(
        key=Callback(HomePageList,
            tab='week', category='Top Week', base_url=url, type_title=title, art=art),
        title='Top Week'))
    oc.add(DirectoryObject(
        key=Callback(HomePageList,
            tab='month', category='Top Month', base_url=url, type_title=title, art=art),
        title='Top Month'))
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

@route(PREFIX + '/about')
def About():
    """Return Resource Directory Size, and KissNetwork's Current Channel Version"""

    oc = ObjectContainer(title2='About / Help')

    # Get Resources Directory Size
    d = GetDirSize(Test.RESOURCES_PATH)
    if d == 'Error':
        cache_string = 'N/A | Removing Files Still'
    else:
        cache_string = d

    if Prefs['devtools']:
        oc.add(DirectoryObject(key=Callback(DevTools),
            title='Developer Tools',
            summary='WARNING!!\nThis section is for Resetting "Header_Dict", "Domain_Dict", and parts of the Channel\'s "Dict" manually.'))

    oc.add(DirectoryObject(key=Callback(About), title='Version %s' %VERSION))
    oc.add(DirectoryObject(key=Callback(About), title=cache_string))

    return oc

####################################################################################################

@route(PREFIX + '/devtools')
def DevTools(file_to_reset=None, header=None, message=None):
    """Reset/Clear Dictionaries manually"""

    oc = ObjectContainer(title2='Developer Tools', header=header, message=message)

    if file_to_reset:
        if file_to_reset == 'Header_Dict' or file_to_reset == 'Domain_Dict':
            Log('\n----------Removing %s File----------' %file_to_reset)

            file_path = Core.storage.join_path(Core.storage.data_path, file_to_reset)
            # create backup of file being removed
            Core.storage.copy(file_path, file_path + '.backup')
            Core.storage.remove_tree(file_path)

            if file_to_reset == 'Header_Dict':
                Test.CreateHeadersDict()
            elif file_to_reset == 'Domain_Dict':
                Domain.CreateDomainDict()

            Log('\n----------Reset %s----------\n----------New values for %s written to:\n%s' %(file_to_reset, file_to_reset, file_path))
            message = 'Reset %s. New values for %s written' %(file_to_reset, file_to_reset)

            return DevTools(header='Custom Dict', message=message)
        elif file_to_reset == 'cfscrape_test':
            Log('\n----------Deleting cfscrape test key from Channel Dict----------')

            if Dict['cfscrape_test']:
                del Dict['cfscrape_test']
                Dict.Save()
                SetUpCFTest()
                message = 'Reset cfscrape Code Test'
            else:
                message = 'No Dict cfscrape Code Test Key to Remove'

            return DevTools(header='CFTest Info', message=message)
        elif file_to_reset == 'hide_bm_clear':
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

            return DevTools(header='Hide BM Clear Opts', message=message)
    else:
        pass

    oc.add(DirectoryObject(key=Callback(DevToolsBM),
        title='Bookmark Tools',
        summary='Tools to Clean dirty bookmarks dictionary, and Toggle "Clear Bookmarks".'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='Header_Dict'),
        title='Reset Header_Dict File',
        summary='Create backup of old Header_Dict, delete current, create new and fill with fresh headers. Remember Creating Header_Dict takes time, so the channel may timeout on the client while rebuilding.  Do not worry. Exit channel and refresh client. The channel should load normally now.'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='Domain_Dict'),
        title='Reset Domain_Dict File',
        summary='Create backup of old Domain_Dict, delete current, create new and fill with fresh domains'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='cfscrape_test'),
        title='Reset Dict cfscrape Test Key',
        summary='Delete previous test key so the channel can retest for a valid JavaScript Runtime.'))

    return oc

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
    oc.add(DirectoryObject(key=Callback(DevToolsBM, title='All'),
        title='Reset "All" Bookmarks',
        summary='Delete Entire Bookmark Section. Same as "Clear All Bookmarks".'))
    oc.add(DirectoryObject(key=Callback(DevToolsBM, title='Anime'),
        title='Reset "Anime" Bookmarks',
        summary='Delete Entire "Anime" Bookmark Section. Same as "Clear Anime Bookmarks".'))
    oc.add(DirectoryObject(key=Callback(DevToolsBM, title='Cartoon'),
        title='Reset "Cartoon" Bookmarks',
        summary='Delete Entire "Cartoon" Bookmark Section. Same as "Clear Cartoon Bookmarks".'))
    oc.add(DirectoryObject(key=Callback(DevToolsBM, title='Drama'),
        title='Reset "Drama" Bookmarks',
        summary='Delete Entire "Drama" Bookmark Section. Same as "Clear Drama Bookmarks".'))
    oc.add(DirectoryObject(key=Callback(DevToolsBM, title='Manga'),
        title='Reset "Manga" Bookmarks',
        summary='Delete Entire "Manga" Bookmark Section. Same as "Clear Manga Bookmarks".'))

    return oc

####################################################################################################

@route(PREFIX + '/validateprefs')
def ValidatePrefs():
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
    Thread.Create(CacheCovers)

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
    for bookmark in sorted(Dict['Bookmarks'][type_title]):
        item_title = bookmark['item_title']
        summary = bookmark['summary']

        if summary:
            summary2 = StringCode(string=summary, code='decode')
        else:
            summary2 = None

        # setup cover depending of Prefs
        cover = bookmark['cover_file']
        # if any Prefs set to cache then try and get the thumb
        if Prefs['cache_bookmark_covers'] or Prefs['cache_covers']:
            # check if the thumb is already cached
            if Test.CoverImageFileExist(cover):
                cover = R(cover)
                cover_list_bool.append(True)
            # thumb not cached, set thumb to caching cover and save thumb in background
            else:
                cover_list_bool.append(False)
                cover = R(CACHE_COVER_ICON)
                Thread.Create(SaveCoverImage, image_url=bookmark['cover_url'])
        # no Prefs to cache thumb, set thumb to None
        else:
            cover_list_bool.append(False)
            cover = None

        item_info = {
            'item_sys_name': bookmark[type_title],
            'item_title': item_title,
            'short_summary': summary,
            'cover_url': bookmark['cover_url'],
            'cover_file': bookmark['cover_url'].rsplit('/')[-1],
            'type_title': type_title,
            'base_url': 'http://' + bookmark['page_url'].rsplit('/')[2],
            'page_url': bookmark['page_url'],
            'art': art}

        # gotta send the bookmark somewhere
        oc.add(DirectoryObject(
            key=Callback(ItemPage, item_info=item_info),
            title=StringCode(string=item_title, code='decode'),
            summary=summary2, thumb=cover, art=cover))

    if Dict['hide_bm_clear'] == 'unhide':
        # setup icons depending on platform and Prefs caching
        if Client.Platform in LIST_VIEW_CLIENTS and not True in cover_list_bool:
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

    # Manually create the '#' Directory
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='0', category='#', base_url=url, type_title=title, art=art),
        title='#'))

    # Create a list of Directories from A to Z
    for pname in map(chr, range(ord('A'), ord('Z')+1)):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList,
                page=1, pname=pname.lower(), category=pname, base_url=url, type_title=title, art=art),
            title=pname))

    Logger('Built #, A-Z... Directories')

    return oc

####################################################################################################

@route(PREFIX + '/genres')
def GenreList(url, title, art):
    """Create Genre Directory for each kiss site"""

    genre_url = url + '/%sList' % title  # setup url for finding current Genre list

    # formate url response into html for xpath
    html = HTML.ElementFromURL(genre_url, headers=Test.GetHeadersForURL(genre_url))

    oc = ObjectContainer(title2='%s By Genres' % title, art=R(art))

    # For loop to pull out valid Genres
    genre_list = set([])
    for genre in html.xpath('//div[@class="barContent"]//a'):
        genre_href = genre.get('href')
        if "Genre" in genre_href and not "Movie" in genre_href:
            genre_list.add(genre_href)

    if not Prefs['adult']:
        adult_genre_list = set(['/Genre/' + g for g in ADULT_LIST])
        clean_genre_list = sorted(genre_list.difference(adult_genre_list))
    else:
        clean_genre_list = sorted(genre_list)

    for genre in clean_genre_list:
        # name used internally
        pname = genre
        # name used for title2
        category = html.xpath('//div[@class="barContent"]//a[@href="%s"]/text()' %genre)[0].replace('\n', '').strip()

        oc.add(DirectoryObject(
            key=Callback(DirectoryList,
                page=1, pname=pname, category=category, base_url=url, type_title=title, art=art),
            title=category))

    return oc

####################################################################################################

@route(PREFIX + '/countries')
def CountryList(url, title, art):
    """Create Country Directory for KissAsian"""

    country_url = url + '/DramaList'  # setup url for finding current Country list

    html = HTML.ElementFromURL(country_url, headers=Test.GetHeadersForURL(country_url))

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
        if "Genre" in pname or "Country" in pname:
            # Genre Specific
            item_url = base_url + '%s?page=%s' % (pname, page)
        elif "All" in pname:
            item_url = base_url + '/%sList?page=%s' % (type_title, page)
        else:
            # No Genre
            item_url = base_url + '/%sList?c=%s&page=%s' % (type_title, pname, page)
    # Sort order for all options except 'A-Z'
    elif "Genre" in pname or "Country" in pname:
        # Genre Specific with Prefs
        item_url = base_url + '%s%s?page=%s' % (pname, Dict['s_opt'], page)
    elif "All" in pname:
        Logger('dict s_opt = %s' %Dict['s_opt'])
        item_url = base_url + '/%sList%s?page=%s' % (type_title, Dict['s_opt'], page)
    else:
        # No Genre with Prefs
        item_url = base_url + '/%sList%s?c=%s&page=%s' % (type_title, Dict['s_opt'], pname, page)

    Logger('Sorting Option = %s' % Dict['s_opt'])  # Log Pref being used
    Logger('Category= %s | URL= %s' % (pname, item_url))

    html = HTML.ElementFromURL(item_url, headers=Test.GetHeadersForURL(base_url))

    pages = "Last Page"
    nextpg_node = None

    # determine if 'next page' is used in directory page
    if "Search" in pname:
        # The Search result page returnes a long list with no 'next page' option
        # set url back to base url
        base_url = Test.GetBaseURL(item_url)
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
    listing_count = len(listing)
    allowed_count = 200
    Logger('%i items in Directory List.' %listing_count, kind='Info')
    if listing_count > allowed_count and 'Search' in pname:
        return MessageContainer(
            'Error',
            '%i found.  Directory can only list up to %i items.  Please narrow your Search Criteria.' %(listing_count, allowed_count))

    for item in listing:
        title_html = HTML.ElementFromString(item.get('title'))
        try:
            thumb = title_html.xpath('//img/@src')[0]
            cover_file = thumb.rsplit('/')[-1]
        except:
            thumb = None
            cover_file = None

        summary = title_html.xpath('//p/text()')[0].strip()

        a_node = item.xpath('./a')[0]

        item_url_base = a_node.get('href')
        item_sys_name = StringCode(string=item_url_base.rsplit('/')[-1].strip(), code='encode')
        item_url_final = base_url + StringCode(string=item_url_base, code='encode')
        Logger('\nitem_url_base = %s\nitem_sys_name = %s\nitem_url_final = %s' %(item_url_base, item_sys_name, item_url_final))
        Logger('thumb = %s' %thumb, kind='Info')

        item_title = a_node.text.strip()
        if 'Movie' in pname:
            title2 = item_title
        else:
            item_title_cleaned = Regex('[^a-zA-Z0-9 \n]').sub('', item_title)

            latest = item.xpath('./following-sibling::td')[0].text_content().strip().replace(item_title_cleaned, '')
            latest = latest.replace('Read Online', '').replace('Watch Online', '').strip()
            if 'Completed' in latest:
                title2 = '%s | %s Completed' %(item_title, type_title)
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
        if 'kiss' in thumb:
            if Prefs['cache_covers']:
                if cover_file:
                    # check if file already exist
                    if Test.CoverImageFileExist(cover_file):
                        Logger('cover file name = %s' %cover_file)
                        cover = R(cover_file)
                    # if no file then set thumb to caching cover icon and save thumb
                    else:
                        Logger('cover not yet saved, saving %s now' %cover_file)
                        cover = R(CACHE_COVER_ICON)
                        Thread.Create(SaveCoverImage, image_url=thumb)
                else:
                    # no cover file, set cover to None
                    cover = None
            else:
                # not caching covers, set cover to None
                cover = None
        else:
            # cover not hosted on kiss site, so set thumb to cover url
            cover = thumb

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
        return oc
    else:
        return MessageContainer(header=type_title, message='%s list is empty' %category)

####################################################################################################

@route(PREFIX + '/homedirectorylist')
def HomePageList(tab, category, base_url, type_title, art):
    """KissCartoon and KissAsian have 'Top' list on home page. This returns those list."""

    main_title = '%s | %s' % (type_title, category)
    oc = ObjectContainer(title2=main_title, art=R(art))

    html = HTML.ElementFromURL(base_url, headers=Test.GetHeadersForURL(base_url))

    # scrape home page for Top (Day, Week, and Month) list
    for node in html.xpath('//div[@id="tab-top-%s"]/div' %tab):
        page_node = StringCode(string=node.xpath('./a')[1].get('href'), code='encode')
        item_sys_name = StringCode(string=page_node.split('/')[-1], code='encode')
        item_title = node.xpath('./a/span[@class="title"]/text()')[0]
        latest = node.xpath('./p/span[@class="info"][text()="Latest:"]/../a/text()')[0]
        title2 = '%s | Latest %s' %(item_title, latest)
        summary = 'NA'  # no summarys are given in the 'Top' lists
        thumb = node.xpath('./a/img')[0].get('src')
        cover_file = thumb.rsplit('/')[-1]
        page_url = base_url + '/' + page_node

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

        if 'kiss' in thumb:
            if Prefs['cache_covers']:
                if cover_file:
                    if Test.CoverImageFileExist(cover_file):
                        Logger('cover file name = %s' %cover_file)
                        cover = R(cover_file)
                    else:
                        Logger('cover not yet saved, saving %s now' %cover_file)
                        cover = R(CACHE_COVER_ICON)
                        Thread.Create(SaveCoverImage, image_url=thumb)
                else:
                    cover = None
            else:
                cover = None
        else:
            cover = thumb

        # send results to ItemPage
        oc.add(DirectoryObject(
            key=Callback(ItemPage, item_info=item_info), title=title2, thumb=cover, art=cover))

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
        html = HTML.ElementFromURL(page_url, headers=Test.GetHeadersForURL(base_url))

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
    if Dict['Bookmarks']:
        # test if item already in bookmarks
        bm_match = False
        if type_title in Dict['Bookmarks']:
            for category in Dict['Bookmarks'][type_title]:
                if item_sys_name == category[type_title]:
                    bm_match = True
                    break  # Stop for loop if match found

        # If Item found in 'Bookmarks'
        if bm_match:
            # provide a way to remove Item from bookmarks list
            oc.add(DirectoryObject(
                key=Callback(RemoveBookmark, item_info=item_info),
                title='Remove Bookmark', thumb=R(BOOKMARK_REMOVE_ICON),
                summary = 'Remove \"%s\" from your Bookmarks list.' % item_title_decode))
        # Item not in 'Bookmarks' yet, so lets parse it for adding!
        else:
            # provide a way to add Item to the bookmarks list
            oc.add(DirectoryObject(
                key = Callback(AddBookmark, item_info=item_info),
                title = 'Add Bookmark', thumb=R(BOOKMARK_ADD_ICON),
                summary = 'Add \"%s\" to your Bookmarks list.' % item_title_decode))
    # No 'Bookmarks' section in Dict yet, so don't look for Item in 'Bookmarks'
    else:
        # provide a way to add Item to bookmarks list
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
    html = HTML.ElementFromURL(page_url, headers=Test.GetHeadersForURL(base_url))

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
                media_page_url = page_url + '/' + node[0].get('href').rsplit('/')[-1]
                Logger('%s Page URL = %s' % (s_removed_page_category, media_page_url))

                # title for Video/Chapter, cleaned
                raw_title = Regex('[^a-zA-Z0-9 \n\.]').sub('', node[0].text).replace(item_title_decode, '')
                if not 'Manga' in type_title:
                    media_title = raw_title.replace('Watch Online', '').strip()
                else:
                    media_title = raw_title.replace('Read Online', '').strip()
                Logger('%s Title = %s' % (s_removed_page_category, media_title))

                a.append((media_page_url, media_title))
            else:
                # date Video/Chapter added
                date = media.text.strip()
                Logger('date=%s' %date)
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
    thumb = item_info['cover_url']
    art = item_info['art']
    url = video_info['video_page_url']
    video_type = video_info['video_type']
    cover_file = item_info['cover_file']
    if Prefs['cache_covers']:
        if cover_file:
            if Test.CoverImageFileExist(cover_file):
                Logger('cover file name = %s' %cover_file)
                cover = R(cover_file)
            else:
                Logger('cover not yet saved, saving %s now' %cover_file)
                cover = R(CACHE_COVER_ICON)
                Thread.Create(SaveCoverImage, image_url=thumb)
        else:
            cover = None
    else:
        cover = None

    oc = ObjectContainer(title2=title, art=R(art))

    Logger('vido url in video detail section = %s' %url)

    # setup html for parsing
    html = HTML.ElementFromURL(url, headers=Test.GetHeadersForURL(url))

    # test if video link is hosted on OneDrive
    # currently the URL Service is not setup to handle OneDrive Links
    onedrive_test = html.xpath('//div[@id="centerDivVideo"]//iframe')
    if onedrive_test:
        if "onedrive" in onedrive_test[0].get('src'):
            return MessageContainer(header='Error',
                message='OneDrive Videos Not Yet Supported. Try another source if avalible.')

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

            html = HTML.ElementFromURL(search_url_filled, headers=Test.GetHeadersForURL(search_url))
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

    html = HTML.ElementFromURL(search_url, headers=Test.GetHeadersForURL(search_url))

    # Check for results if none then give a pop up window saying so
    if html.xpath('//table[@class="listing"]'):
        # Test for "exact" match, if True then send to 'ItemPage'
        node = html.xpath('//div[@id="headnav"]/script/text()')[0]
        search_match = Regex('var\ path\ =\ (\'Search\')').search(node)
        if not search_match:
            # Send url to 'ItemPage'
            base_url = Test.GetBaseURL(search_url)
            node = html.xpath('//div[@class="barContent"]/div/a')[0]

            item_sys_name = StringCode(string=node.get('href').rsplit('/')[-1].strip(), code='encode')
            item_url = base_url + '/' + type_title + '/' + StringCode(item_sys_name, code='encode')
            item_title = node.text
            cover_url = html.xpath('//head/link[@rel="image_src"]')[0].get('href')

            Logger('\nitem_title=%s\nitem=%s\ntype_title=%s\nbase_url=%s\nitem_url=%s'
                % (item_title, item_sys_name, type_title, base_url, item_url))

            item_info = {
                'item_sys_name': item_sys_name,
                'item_title': StringCode(string=item_title, code='encode'),
                'short_summary': None,
                'cover_url': cover_url,
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
    html = HTML.ElementFromURL(page_url, headers=Test.GetHeadersForURL(base_url))

    # if no cover url then try and find one on the item page
    if not cover_url:
        try:
            cover_url = html.xpath('//head/link[@rel="image_src"]')[0].get('href')
        except:
            cover_url = None

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
            if node is not None and not node.xpath('.//a'):
                sum_text = node.text_content().strip()
                if sum_text:
                    sum_list.append(sum_text)

        if len(sum_list) > 1:
            Logger('summary was in %i <p>\'s' %int(len(sum_list)), kind='Info')
            summary = '\n\n'.join(sum_list).replace('Related Series', '').replace('Related:', '').strip()
        else:
            if sum_list[0]:
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
            summary = html.xpath('//div[@id="container"]//table//td')
            # if summary found in own <table>
            if summary:
                Logger('summary is in own <table>', kind='Info')
                summary = summary[0].text_content().strip()
            else:
                summary = html.xpath('//div[@id="container"]//div[@class="barContent"]/div/div')
                # if summary found in own <div>
                if summary:
                    Logger('summary is in own <div>', kind='Info')
                    summary = summary[0].text_content().strip()
                    # fix string encoding errors before they happen by encoding
                    #summary = StringCode(string=summary, code='encode')
                else:
                    Logger('no summary found, setting summary to \"None\"', force=True)
                    summary = None

    if summary:
        Logger('summary = %s' %summary, kind='Debug')
        summary = StringCode(string=summary, code='encode')

    # setup new bookmark json data to add to Dict
    # Option to store covers locally as files
    if Prefs['cache_covers'] or Prefs['cache_bookmark_covers']:
        image_file = cover_url.rsplit('/')[-1]
        if Test.CoverImageFileExist(image_file):
            pass
        else:
            try:
                image_file = SaveCoverImage(cover_url)
            except:
                image_file = None
    # still set file name (if can) for later
    else:
        try:
            image_file = cover_url.rsplit('/')[-1]
        except:
            image_file = None

    new_bookmark = {
        type_title: item_sys_name, 'item_title': item_title, 'cover_file': image_file,
        'cover_url': cover_url, 'summary': summary, 'page_url': page_url}

    Logger('new bookmark to add\n%s' % new_bookmark)

    # Test if the Dict has the 'Bookmarks' section yet
    if not Dict['Bookmarks']:
        # Create new 'Bookmarks' section and fill with the first bookmark
        Dict['Bookmarks'] = {type_title: [new_bookmark]}
        Logger('Inital bookmark list created\n%s' % Dict['Bookmarks'])

        # Update Dict to include new 'Bookmarks' section
        Dict.Save()

        # Provide feedback that the Item has been added to bookmarks
        return MessageContainer(header=item_title_decode,
            message='\"%s\" has been added to your bookmarks.' % item_title_decode)
    # check if the category key 'Anime', 'Manga', 'Cartoon', or 'Drama' exist
    # if so then append new bookmark to one of those categories
    elif type_title in Dict['Bookmarks'].keys():
        # fail safe for when clients are out of sync and it trys to add
        # the bookmark in duplicate
        for bookmark in Dict['Bookmarks'][type_title]:
            if not bookmark[type_title] == new_bookmark[type_title]:
                match = False
            else:
                match = True
                break

        if match:
            Logger('bookmark \"%s\" already in your bookmarks' %item_title_decode, kind='Info')
            return MessageContainer(header=item_title_decode,
                message='\"%s\" is already in your bookmarks.' % item_title_decode)
        # append new bookmark to its correct category, i.e. 'Anime', 'Drama', etc...
        else:
            temp = {}
            temp.setdefault(type_title, Dict['Bookmarks'][type_title]).append(new_bookmark)
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
    Logger('bookmarks = %s' %bm)
    Logger('bookmark lenght = %s' %len(bm))
    for i in xrange(len(bm)):
        # remove item's data from 'Bookmarks' list
        if bm[i][type_title] == item_sys_name:
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

@route(PREFIX + '/cache-covers')
def CacheCovers():
    """Cache covers depending on prefs settings. Will remove or add covers if it can."""

    if not Prefs['cache_bookmark_covers'] and not Prefs['cache_covers']:
        # remove any cached covers from Dict['Bookmarks']
        # unless Prefs['cache_covers'] is true, then keep cached covers
        if Dict['cover_files']:
            for cover in Dict['cover_files']:
                Thread.Create(RemoveCoverImage, image_file=Dict['cover_files'][cover])

            del Dict['cover_files']
            Dict.Save()
            Logger('Removed cached covers using Dict[\'cover_files\'] list as key, and removed Dict[\'cover_files\'] once finished.', kind='Info')
        elif Dict['Bookmarks']:
            for key in Dict['Bookmarks'].keys():
                for bm in Dict['Bookmarks'][key]:
                    Thread.Create(RemoveCoverImage, image_file=bm['cover_file'])

            Logger('No Dict[\'cover_files\'] found, Removed cached covers using Dict[\'Bookmarks\'] list as key.', kind='Info')
    elif not Prefs['cache_covers'] and Prefs['cache_bookmark_covers']:
        # remove cached covers not in Dict['Bookmarks']
        # and save covers from Dict['Bookmarks'] in not already saved
        bookmark_cache = set([])
        if Dict['Bookmarks']:
            for key in Dict['Bookmarks'].keys():
                for bm in Dict['Bookmarks'][key]:
                    bookmark_cache.add(bm['cover_file'])
                    Thread.Create(SaveCoverImage, image_url=bm['cover_url'])

        Logger('Caching Bookmark Cover images if they have not been already.', kind='Info')
        if Dict['cover_files']:
            cover_cache = set([c for c in Dict['cover_files']])
            cover_cache_diff = cover_cache.difference(bookmark_cache)
            for cover in cover_cache_diff:
                Thread.Create(RemoveCoverImage, image_file=Dict['cover_files'][cover])
                del Dict['cover_files'][cover]

            Logger('Removed cached covers using Dict[\'cover_files\'] list as key, and removed Dict[\'cover_files\'] once finished.', kind='Info')
            Logger('But kept Bookmarks cached covers.', kind='Info')
    elif Prefs['cache_covers']:
        # cache bookmark covers from Dict['Bookmarks']
        if Dict['Bookmarks']:
            for key in Dict['Bookmarks'].keys():
                for bm in Dict['Bookmarks'][key]:
                    Thread.Create(SaveCoverImage, image_url=bm['cover_url'])

        Logger('Caching Bookmark Cover images if they have not been already.', kind='Info')
        Logger('All covers cached set to True.', kind='Info')

    return

####################################################################################################

@route(PREFIX + '/save-cover-image', count=int)
def SaveCoverImage(image_url, count=0):
    """Save image to Cover Image Path and return the file name"""

    url_node = image_url.split('/', 3)
    base_url = 'http://' + url_node[2]
    type_title = Test.GetTypeTitle(base_url)
    # test image url for correct domain
    if not (type_title, base_url) in Test.BASE_URL_LIST:
        # set image base url to new domain
        for tnode in Test.BASE_URL_LIST:
            if tnode[0] == type_title:
                base_url = tnode[1]
                break

        Logger('Old %s URL parsed from page! URL Domain changed to %s' %(type_title, base_url), kind='Warn', force=True)

    content_url = base_url + '/' + url_node[3]

    image_file = image_url.rsplit('/')[-1]

    path = Core.storage.join_path(Test.RESOURCES_PATH, image_file)
    Logger('image file path = %s' %path)

    if not Core.storage.file_exists(path):
        #r = requests.get(image_url, headers=Test.GetHeadersForURL(image_url), stream=True)
        r = requests.get(content_url, headers=Test.GetHeadersForURL(content_url), stream=True)

        if r.status_code == 200:
            with io.open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            Logger('saved image %s in path %s' %(image_file, path))
            # create dict for cover files, so we can clear them later
            #   seperate from bookmark covers if need be
            if Dict['cover_files']:
                Dict['cover_files'].update({image_file: image_file})
            else:
                Dict['cover_files'] = {image_file: image_file}

            Dict.Save()
            return image_file
        elif r.status_code == 503 and count < 3:
            count += 1
            timer = float(Util.RandomInt(5,10))
            Logger('%s error code. Polling site too fast. Waiting 3sec then try again, try up to 3 times. Try %i' %(r.status_code, count), kind='Warn', force=True)
            Thread.CreateTimer(timer, SaveCoverImage, image_url=content_url, count=count)
        else:
            Logger('status code for image url = %s' %r.status_code)
            Logger('image url not found | %s' %content_url, force=True, kind='Error')
            return None
    else:
        Logger('file %s already exists' %image_file)
        return image_file

####################################################################################################

@route(PREFIX + '/remove-cover-image')
def RemoveCoverImage(image_file):
    """Remove Cover Image"""

    path = Core.storage.join_path(Test.RESOURCES_PATH, image_file)

    if Core.storage.file_exists(path):
        Core.storage.remove(path)
    else:
        pass

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
            cftest = Test.CFTest()
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

    # setup urls for setting headers
    url_list = [ANIME_BASE_URL, ASIAN_BASE_URL, CARTOON_BASE_URL, MANGA_BASE_URL]
    if not Dict['First Headers Cached']:
        Logger('\n----------Running Background Auto-Cache----------', force=True)
        Log(Core.storage.file_exists(Core.storage.join_path(Core.storage.data_path, 'Header_Dict')))

        if Core.storage.file_exists(Core.storage.join_path(Core.storage.data_path, 'Header_Dict')):
            Logger('\n----------Header Dictionary already found, writing new Headers to old Dictionary----------', force=True)

            # get headers for each url
            for url in url_list:
                Test.GetHeadersForURL(url)

        else:
            # Header Dictionary not yet setup, so create it and fill in the data
            Test.CreateHeadersDict()

        # check to make sure each section/url has cookies now
        Logger('\n----------All cookies----------\n%s' %Test.LoadHeaderDict())

        # Setup the Dict and save
        Dict['First Headers Cached'] = True
        Dict['Headers Auto Cached'] = True
        Dict.Save()
    else:
        for url in url_list:
            Logger('\n----------Checking %s headers----------' %url, kind='Info', force=True)
            Test.GetHeadersForURL(url)

        Logger('\n----------Completed Header Cache Check----------', kind='Info', force=True)
        Logger('\n----------Headers will be cached independently when needed from now on----------', kind='Info', force=True)
        pass

    return

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
