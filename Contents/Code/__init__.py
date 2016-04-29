####################################################################################################
#                                                                                                  #
#                                   KissNetwork Plex Channel                                       #
#                                                                                                  #
####################################################################################################
# import section(s) not included in Plex Plug-In Framework
import os
import sys
import shutil
from io import open
import urllib2
from time import sleep
from updater import Updater
from DumbTools import DumbKeyboard
from DumbTools import DumbPrefs
import messages
from AuthTools import CheckAdmin
from DevTools import add_dev_tools
from DevTools import SaveCoverImage
from DevTools import SetUpCFTest
from slugify import slugify

# import Shared Service Code
Headers = SharedCodeService.headers
Domain = SharedCodeService.domain
Common = SharedCodeService.common
Metadata = SharedCodeService.metadata

# import custom modules
import requests

# set global variables
PREFIX = '/video/kissnetwork'
TITLE = L('title')
ADULT_LIST = set(['Adult', 'Smut', 'Ecchi', 'Lolicon', 'Mature', 'Yaoi', 'Yuri'])
CP_DATE = ['Plex for Android', 'Plex for iOS', 'Plex Home Theater', 'OpenPHT']
TIMEOUT = Datetime.Delta(hours=1)

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

# ReadComincOnline
COMIC_BASE_URL = Common.COMIC_BASE_URL
COMIC_SEARCH_URL = COMIC_BASE_URL + '/Search/Comic?keyword=%s'
COMIC_ART = 'art-comic.jpg'
COMIC_ICON = 'icon-comic.png'

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

MC = messages.NewMessageContainer(PREFIX, TITLE)

####################################################################################################
def Start():
    ObjectContainer.art = R(MAIN_ART)
    ObjectContainer.title1 = TITLE

    DirectoryObject.thumb = R(MAIN_ICON)
    DirectoryObject.art = R(MAIN_ART)
    PopupDirectoryObject.art = R(MAIN_ART)

    InputDirectoryObject.art = R(MAIN_ART)

    HTTP.CacheTime = 0
    HTTP.Headers['User-Agent'] = Common.USER_AGENT

    Log.Debug('*' * 80)
    Log.Debug('* Platform.OS            = %s' %Platform.OS)
    Log.Debug('* Platform.OSVersion     = %s' %Platform.OSVersion)
    Log.Debug('* Platform.ServerVersion = %s' %Platform.ServerVersion)
    Log.Debug('*' * 80)

    # setup background auto cache of headers
    Dict['First Headers Cached'] = False

    # setup test for cfscrape
    SetUpCFTest()

    if Dict['cfscrape_test']:
        if Dict['Headers Auto Cached']:
            if not Dict['Headers Auto Cached']:
                Log.Debug('* Caching Headers')
                Thread.CreateTimer(5, BackgroundAutoCache)
            else:
                Log.Debug('* Cookies already cached')
                Log.Debug('* Checking Each URL Cache Time')
                Thread.CreateTimer(5, BackgroundAutoCache)
        else:
            Dict['Headers Auto Cached'] = False
            Dict.Save()
            Log.Debug('* Caching Headers ')
            Thread.CreateTimer(5, BackgroundAutoCache)
        Log.Debug('*' * 80)
    else:
        pass

    # Clear Old Cached URLs
    Thread.Create(ClearCache, timeout=TIMEOUT)

####################################################################################################
@handler(PREFIX, TITLE, MAIN_ICON, MAIN_ART)
def MainMenu():
    """Create the Main Menu"""

    Log.Debug('*' * 80)
    Log.Debug('* Client.Product         = %s' %Client.Product)
    Log.Debug('* Client.Platform        = %s' %Client.Platform)
    Log.Debug('* Client.Version         = %s' %Client.Version)

    # if cfscrape failed then stop the channel, and return error message.
    SetUpCFTest()
    if not Dict['cfscrape_test']:
        Log.Error(
            """
            ----------CFTest Failed----------
            You need to install a JavaScript Runtime like node.js or equivalent
            Once JavaScript Runtime installed, Restart channel
            """
            )
        Log.Debug('*' * 80)
        return MC.message_container('Error',
            'CloudFlare bypass fail. Please install a JavaScript Runtime like node.js or equivalent')

    admin = CheckAdmin()

    oc = ObjectContainer(title2=TITLE, no_cache=admin)

    cp_match = True if Client.Platform in Common.LIST_VIEW_CLIENTS else False

    for i, (t, u) in enumerate(Common.BASE_URL_LIST_T):
        thumb = 'icon-%s.png' %t.lower()
        rthumb = None if cp_match else R(thumb)
        art = 'art-%s.jpg' %t.lower()
        #rart = None if cp_match else R(art)
        rart = R(art)
        prefs_name = 'kissasian' if t == 'Drama' else 'kiss%s' %t.lower()
        new_data = {
            'prefs_name': prefs_name, 'title': t, 'art': art,
            'rart': rart, 'thumb': thumb, 'rthumb': rthumb, 'url': u
            }
        if i == 0:
            data = [new_data]
        else:
            data.append(new_data)

    # set thumbs based on client
    if cp_match:
        bookmark_thumb = None
        prefs_thumb = None
        search_thumb = None
        about_thumb = None
    else:
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

    if admin:
        Updater(PREFIX + '/updater', oc)

    # set up Main Menu depending on what sites are picked in the Prefs menu
    prefs_names = ['kissanime', 'kissasian', 'kisscartoon', 'kissmanga', 'kisscomic']
    b_prefs_names = [p for p in prefs_names if Prefs[p]]
    # present KissMain directly if no other sites selected
    if len(b_prefs_names) == 1:
        b_prefs_name = b_prefs_names[0]
        p_data = [d for d in data if d['prefs_name'] == b_prefs_name][0]
        KissMain(url=p_data['url'], title=p_data['title'], art=p_data['art'], ob=False, oc=oc)
    else:
        for d in sorted(data, key=lambda k: k['title']):
            if Prefs[d['prefs_name']]:
                oc.add(DirectoryObject(
                    key=Callback(KissMain, url=d['url'], title=d['title'], art=d['art']),
                    title=d['title'], thumb=d['rthumb'], art=d['rart']
                    ))

    oc.add(DirectoryObject(
        key=Callback(BookmarksMain, title='My Bookmarks', status=status), title='My Bookmarks',
        thumb=bookmark_thumb
        ))

    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=prefs_thumb)
    elif admin:
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
@route(PREFIX + '/kissmain', ob=bool)
def KissMain(url, title, art, ob=True, oc=None):
    """Create All Kiss Site Menu"""

    if ob:
        oc = ObjectContainer(title2=title, art=R(art))
    newest_c_title = 'New %s' %title

    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='All', category='All', base_url=url, type_title=title, art=art),
        title='All'))
    oc.add(DirectoryObject(
        key=Callback(AlphabetList, url=url, title=title, art=art), title='Alphabets'))
    oc.add(DirectoryObject(
        key=Callback(GenreList, url=url, title=title, art=art), title='Genres'))

    if title == 'Drama':
        oc.add(DirectoryObject(
            key=Callback(CountryList, url=url, title=title, art=art), title='Countries'))

    if (title == 'Anime') or (title == 'Cartoon') or (title == 'Drama'):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList,
                page=1, pname='/Genre/Movie', category='Movie', base_url=url, type_title=title, art=art),
            title='Movies'))

    oc.add(DirectoryObject(key=Callback(StatusList, url=url, type_title=title, art=art),
        title='Status'))

    if (title == 'Drama') or (title == 'Cartoon') or (title == 'Comic'):
        oc.add(DirectoryObject(key=Callback(TopList, url=url, type_title=title, art=art),
            title='Top'))

    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/LatestUpdate', category='Latest Update', base_url=url, type_title=title, art=art),
        title='Latest Update'))

    if title == 'Anime':
        newest_c_title = 'Recent Additions'
        oc.add(DirectoryObject(
            key=Callback(DirectoryList,
                page=1, pname='/NewAndHot', category='New & Hot', base_url=url, type_title=title, art=art),
            title='New & Hot'))

    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/Newest', category=newest_c_title, base_url=url, type_title=title, art=art),
        title=newest_c_title))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='/MostPopular', category='Most Popular', base_url=url, type_title=title, art=art),
        title='Most Popular'))

    if ob:
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
    # Get Channel Version
    plist = Plist.ObjectFromString(Core.storage.load(
        Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, 'Contents', 'Info.plist'))))
    version = plist['CFBundleVersion']
    # show developer tools if enabled in prefs and current user is admin
    if Prefs['devtools'] and CheckAdmin():
        add_dev_tools(oc)

    oc.add(DirectoryObject(key=Callback(About),
        title='Version %s' %version, summary='Current Channel Version'))
    oc.add(DirectoryObject(key=Callback(About),
        title=cache_string, summary='Number of Images Cached | Total Images Cached Size'))

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
        return MC.message_container(title,
            'No Bookmarks yet. Get out there and start adding some!!!')
    # create boomark directory based on category
    else:
        key_list = sorted(Dict['Bookmarks'].keys())
        # return bookmark list directly if only one kiss site selected in prefs
        bm_prefs_names = [('kissasian' if m == 'Drama' else 'kiss%s' %m.lower()) for m in key_list]
        bool_prefs_names = [p for p in bm_prefs_names if Prefs[p]]
        if len(bool_prefs_names) == 1:
            b_prefs_name = bool_prefs_names[0].split('kiss')[1].title()
            b_prefs_name = 'Drama' if b_prefs_name == 'Asian' else b_prefs_name
            if b_prefs_name in key_list:
                art = 'art-%s.jpg' %b_prefs_name.lower()
                return BookmarksSub(b_prefs_name, art)
        # list categories in bookmarks dictionary that are selected in prefs
        for key in key_list:
            prefs_name = 'kissasian' if key == 'Drama' else 'kiss%s' %key.lower()
            art = 'art-%s.jpg' %key.lower()
            thumb = 'icon-%s.png' %key.lower()

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
            return MC.message_container('Error',
                'At least one source must be selected in Preferences to view Bookmarks')

####################################################################################################
@route(PREFIX + '/bookmarkssub')
def BookmarksSub(type_title, art):
    """Load Bookmarked items from Dict"""

    if not type_title in Dict['Bookmarks'].keys():
        return MC.message_container('Error',
            '%s Bookmarks list is dirty. Use About/Help > Dev Tools > Bookmark Tools > Reset %s Bookmarks' %(type_title, type_title))

    oc = ObjectContainer(title2='My Bookmarks | %s' % type_title, art=R(art))
    Logger('category %s' %type_title)

    # Fill in DirectoryObject information from the bookmark list
    # create empty list for testing covers
    cover_list_bool = []
    for bookmark in sorted(Dict['Bookmarks'][type_title], key=lambda k: k[type_title]):
        item_title = bookmark['item_title']
        summary = bookmark['summary']

        if summary:
            summary2 = Common.StringCode(string=summary, code='decode')
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
            title=Common.StringCode(string=item_title, code='decode'),
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
    #html = HTML.ElementFromURL(genre_url, headers=Headers.GetHeadersForURL(genre_url))
    #html = Headers.ElementFromURL(genre_url)
    html = ElementFromURL(genre_url)

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

    #html = HTML.ElementFromURL(country_url, headers=Headers.GetHeadersForURL(country_url))
    #html = Headers.ElementFromURL(country_url)
    html = ElementFromURL(country_url)

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

    #html = HTML.ElementFromURL(item_url, headers=Headers.GetHeadersForURL(base_url))
    #html = Headers.ElementFromURL(item_url)
    html = ElementFromURL(item_url)

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

    #oc = ObjectContainer(title2=main_title, art=R(art), no_cache=True)
    oc = ObjectContainer(title2=main_title, art=R(art))

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
        return MC.message_container('Error',
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
        item_sys_name = Common.StringCode(string=item_url_base.rsplit('/')[-1].strip(), code='encode')
        item_url_final = base_url + Common.StringCode(string=item_url_base, code='encode')
        Logger('*' * 80)
        Logger('* item_url_base     = %s' %item_url_base)
        Logger('* item_sys_name     = %s' %item_sys_name)
        Logger('* item_url_final    = %s' %item_url_final)
        Logger('* thumb             = %s' %thumb)

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
            'item_title': Common.StringCode(string=item_title, code='encode'),
            'short_summary': Common.StringCode(string=summary, code='encode'),
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
        Logger('* NextPage          = %i' % nextpg)
        Logger('* base url          = %s' %base_url)
        oc.add(NextPageObject(
            key=Callback(DirectoryList,
                page=nextpg, pname=pname, category=category,
                base_url=base_url, type_title=type_title, art=art),
            title='Next Page>>', thumb=R(NEXT_ICON)))

    if len(oc) > 0:
        Dict.Save()
        return oc
    else:
        return MC.message_container(type_title, '%s list is empty' %category)

####################################################################################################
@route(PREFIX + '/homedirectorylist')
def HomePageList(tab, category, base_url, type_title, art):
    """
    KissCartoon, KissAsian, and ReadComicOnline have 'Top' list on home page.
    This returns those list.
    """

    main_title = '%s | %s' % (type_title, category)
    oc = ObjectContainer(title2=main_title, art=R(art))

    #html = HTML.ElementFromURL(base_url, headers=Headers.GetHeadersForURL(base_url))
    #html = Headers.ElementFromURL(base_url)
    html = ElementFromURL(base_url)

    # scrape home page for Top (Day, Week, and Month) list
    for node in html.xpath('//div[@id="tab-top-%s"]/div' %tab):
        page_node = Common.StringCode(string=node.xpath('./a')[1].get('href'), code='encode')
        item_sys_name = Common.StringCode(string=page_node.split('/')[-1], code='encode')
        item_title = node.xpath('./a/span/text()')[0]
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
            'item_title': Common.StringCode(string=item_title, code='encode'),
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

    # decode string & set title2 for oc
    item_title_decode = Common.StringCode(string=item_title, code='decode')
    title2 = '%s | %s' % (type_title, item_title_decode)
    oc = ObjectContainer(title2=title2, art=R(art))

    #html = HTML.ElementFromURL(page_url, headers=Headers.GetHeadersForURL(base_url))
    #html = Headers.ElementFromURL(page_url)
    html = ElementFromURL(page_url)
    genres, genres_list = Metadata.GetGenres(html)

    if not Prefs['adult']:

        # Check for Adult content, block if Prefs set.
        genres = html.xpath('//p[span[@class="info"]="Genres:"]/a/text()')
        Logger('* genres = %s' %genres)
        if genres:
            matching_list = set(genres) & ADULT_LIST
            if len(matching_list) > 0:
                warning_string = ', '.join(list(matching_list))
                Logger('* Adult Content Blocked: %s' %warning_string, force=True, kind='Info')
                Logger('*' * 80)
                return MC.message_container('Warning',
                    'Adult Content Blocked: %s' %warning_string)

    # page category stings depending on media
    page_category = 'Chapter(s)' if (type_title == 'Manga' or type_title == 'Comic') else 'Video(s)'

    # update item_info to include page_category
    item_info.update({'page_category': page_category})

    # format item_url for parsing
    Logger('* page url = %s' %page_url)
    Logger('* base url = %s' %base_url)
    Logger('*' * 80)
    cover = GetThumb(cover_url=item_info['cover_url'], cover_file=item_info['cover_file'])

    if ('Manga' in type_title) or ('Comic' in type_title):
        manga_info = Metadata.GetBaseMangaInfo(html, page_url)
        summary = manga_info['summary'] if manga_info['summary'] else (item_info['short_summary'] if item_info['short_summary'] else None)
        item_info.update({'summary': summary})
        item_info.pop('short_summary')
        manga_info.pop('summary')
        summary2 = Common.StringCode(string=summary, code='decode')

        oc.add(TVShowObject(
            key=Callback(MangaSubPage, item_info=item_info, manga_info=manga_info),
            rating_key=page_url, title=manga_info['title'], genres=genres,
            source_title=manga_info['source_title'], summary=summary2,
            thumb=cover, art=R(art)
            ))

    elif 'Movie' in genres:
        movie_info = Metadata.GetBaseMovieInfo(html, page_url)
        summary = movie_info['summary'] if movie_info['summary'] else (item_info['short_summary'] if item_info['short_summary'] else None)
        item_info.update({'summary': summary})
        item_info.pop('short_summary')
        movie_info.pop('summary')
        summary2 = Common.StringCode(string=summary, code='decode')

        oc.add(TVShowObject(
            key=Callback(MovieSubPage, item_info=item_info, movie_info=movie_info),
            rating_key=page_url, title=movie_info['title'], genres=genres,
            source_title=movie_info['source_title'], summary=summary2,
            thumb=cover, art=R(art)
            ))

    else:
        show_info = Metadata.GetBaseShowInfo(html, page_url)
        summary = string=show_info['summary'] if show_info['summary'] else (item_info['short_summary'] if item_info['short_summary'] else None)
        item_info.update({'summary': summary})
        item_info.pop('short_summary')
        show_info.pop('summary')
        summary2 = Common.StringCode(string=summary, code='decode')

        oc.add(TVShowObject(
            key=Callback(ShowSubPage, item_info=item_info, show_info=show_info),
            rating_key=page_url, title=show_info['tv_show_name'], genres=genres,
            source_title=show_info['source_title'], summary=summary2,
            thumb=cover, art=R(art)
            ))

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
def GetItemList(html, url, item_title, type_title):
    """Get list of Episodes, Movies, or Chapters"""

    episode_list = html.xpath('//table[@class="listing"]/tr/td')
    item_title_decode = Common.StringCode(string=item_title, code='decode')
    item_title_regex = Regex('[^a-zA-Z0-9 \n\.]').sub('', item_title_decode)

    # if no shows, then none have been added yet
    if not episode_list:
        return 'Not Yet Aired'
    else:
        a = []
        b = []
        c = []

        for media in episode_list:
            if media.xpath('./a'):
                node = media.xpath('./a')

                # url for Video/Chapter
                media_page_url = url + '/' + node[0].get('href').rsplit('/')[-1]

                # title for Video/Chapter, cleaned
                raw_title = Regex('[^a-zA-Z0-9 \n\.]').sub('', node[0].text).replace(item_title_regex, '')
                if ('Manga' in type_title) or ('Comic' in type_title):
                    media_title = raw_title.replace('Read Online', '').strip()
                else:
                    media_title = raw_title.replace('Watch Online', '').strip()

                a.append((media_page_url, media_title))
            else:
                # date Video/Chapter added
                date = media.text.strip()
                b.append(date)

        for x, y in reversed(map(None, a, b)):
            c.append({'title':x[1], 'date': y, 'url': x[0]})

        return c

####################################################################################################
@route(PREFIX + '/movie-sub-page', item_info=dict, movie_info=dict)
def MovieSubPage(item_info, movie_info):
    """Setup Movie Page"""

    item_title_decode = Common.StringCode(string=item_info['item_title'], code='decode')
    title2 = '%s | %s | %s' % (item_info['type_title'], item_title_decode, item_info['page_category'].lower())

    oc = ObjectContainer(title2=title2, art=R(item_info['art']))

    #html = HTML.ElementFromURL(item_info['page_url'], headers=Headers.GetHeadersForURL(item_info['base_url']))
    #html = Headers.ElementFromURL(item_info['page_url'])
    html = ElementFromURL(item_info['page_url'])

    movie_list = GetItemList(html, item_info['page_url'], item_info['item_title'], item_info['type_title'])
    if movie_list == 'Not Yet Aired':
        return MC.message_container('Warning', '%s \"%s\" Not Yet Aired.' %(item_info['type_title'], item_title_decode))
    else:
        summary = Common.StringCode(string=item_info['summary'], code='decode') if item_info['summary'] else None
        cover = GetThumb(cover_url=item_info['cover_url'], cover_file=item_info['cover_file'])
        genres, genres_list = Metadata.GetGenres(html)
        for movie in movie_list:
            oc.add(MovieObject(
                title='%s | %s' %(movie['title'], movie['date']),
                source_title=movie_info['source_title'],
                summary=summary,
                year=int(movie_info['year']) if movie_info['year'] else None,
                genres=genres if genres else [],
                originally_available_at=Datetime.ParseDate(movie['date']) if movie['date'] else None,
                thumb=cover,
                art=R(item_info['art']),
                url=movie['url']
                ))

    return oc

####################################################################################################
@route(PREFIX + '/manga-sub-page', item_info=dict, manga_info=dict)
def MangaSubPage(item_info, manga_info):
    """Create the Manga/Comic Sub Page with Chapter list"""
    #TODO split this into ~30 chapters per book or so, similar to what was done with seasons

    item_title_decode = Common.StringCode(string=item_info['item_title'], code='decode')
    title2 = '%s | %s | %s' % (item_info['type_title'], item_title_decode, item_info['page_category'].lower())

    oc = ObjectContainer(title2=title2, art=R(item_info['art']))
    #html = HTML.ElementFromURL(item_info['page_url'], headers=Headers.GetHeadersForURL(item_info['base_url']))
    #html = Headers.ElementFromURL(item_info['page_url'])
    html = ElementFromURL(item_info['page_url'])

    cp_list = GetItemList(html, item_info['page_url'], item_info['item_title'], item_info['type_title'])
    if cp_list == 'Not Yet Aired':
        return MC.message_container('Warning', '%s \"%s\" Not Yet Aired.' %(item_info['type_title'], item_title_decode))
    else:
        cover = GetThumb(cover_url=item_info['cover_url'], cover_file=item_info['cover_file'])
        for cp in reversed(cp_list):
            oc.add(PhotoAlbumObject(
                key=Callback(GetPhotoAlbum,
                    url=cp['url'], source_title=manga_info['source_title'], title=cp['title'],
                    art=item_info['art']),
                rating_key=cp['url'],
                title='%s | %s' %(cp['title'], cp['date']),
                source_title=manga_info['source_title'],
                originally_available_at=Datetime.ParseDate(cp['date']) if cp['date'] else None,
                thumb=cover,
                art=R(item_info['art'])
                ))

    return oc

####################################################################################################
@route(PREFIX + '/getphotoablum')
def GetPhotoAlbum(url, source_title, title, art):
    """
    This function pulls down all the image urls for a chapter and adds them to the
    'PhotoObject' container.
    """

    oc = ObjectContainer(title2=title, art=R(art))

    # get relevant javascript block
    #html = HTML.ElementFromURL(url, headers=Headers.GetHeadersForURL(url))
    #html = Headers.ElementFromURL(url)
    html = ElementFromURL(url)

    for java in html.xpath('//script[@type="text/javascript"]'):
        javatext = java.text
        if javatext:
            if "lstImages" in javatext:
                # then do a regex search to pull out relevant text
                m = Regex('(?s)lstImages\.push\(\"([\S].*)\"\);').search(javatext).group(0)
                break

    # then split the string by the ';' to get each relevant line in an array
    image_lines = m.rsplit(';')

    # now iterate over each line and pull out the image url
    for item in image_lines:
        m = Regex('lstImages\.push\(\"([\S].*?)\"\)').search(item)

        if m:  # test for empty results
            image = m.group(1)
            image_title = image.rsplit('/')[-1].rsplit('.', 1)[0]

            if "proxy" in image_title:
                image_title = image_title.rsplit('%')[-1].rsplit('2f')[1]

            oc.add(CreatePhotoObject(
                url=image, source_title=source_title, art=art, title=image_title
                ))

    return oc

####################################################################################################
@route(PREFIX + '/show-sub-page', item_info=dict, show_info=dict)
def ShowSubPage(item_info, show_info):
    """Setup Show page"""

    item_title_decode = Common.StringCode(string=item_info['item_title'], code='decode')
    title2 = '%s | %s | %s' % (item_info['type_title'], item_title_decode, item_info['page_category'].lower())

    oc = ObjectContainer(title2=title2, art=R(item_info['art']))

    #html = HTML.ElementFromURL(item_info['page_url'], headers=Headers.GetHeadersForURL(item_info['base_url']))
    #html = Headers.ElementFromURL(item_info['page_url'])
    html = ElementFromURL(item_info['page_url'])
    ep_list = GetItemList(html, item_info['page_url'], item_info['item_title'], item_info['type_title'])
    if ep_list == 'Not Yet Aired':
        return MC.message_container('Warning', '%s \"%s\" Not Yet Aired.' %(item_info['type_title'], item_title_decode))
    else:
        tags = Metadata.string_to_list(Common.StringCode(string=show_info['tags'], code='decode')) if show_info['tags'] else []
        thumb = GetThumb(cover_url=item_info['cover_url'], cover_file=item_info['cover_file'])
        summary = Metadata.GetSummary(html)
        show_name_raw = html.xpath('//div[@class="barContent"]/div/a[@class="bigChar"]/text()')[0]
        season_dict = None
        main_ep_count = len(ep_list)
        ips = 30
        cp = Client.Product
        season_info = {
            'season': '1', 'ep_count': main_ep_count, 'tv_show_name': show_info['tv_show_name'],
            'art': item_info['art'], 'source_title': show_info['source_title'],
            'page_url': item_info['page_url'], 'cover_url': item_info['cover_url'],
            'cover_file': item_info['cover_file'], 'year': show_info['year'], 'tags': show_info['tags'],
            'item_title': item_info['item_title'], 'type_title': item_info['type_title'], 'ips': str(ips)
            }

        Logger('*' * 80)
        Logger('* ep_list lenght = %i' %main_ep_count)

        for ep in ep_list:
            title_lower = ep['title'].lower()

            if 'episode' in title_lower and 'uncensored' not in title_lower:
                season_number = Metadata.GetSeasonNumber(ep['title'], show_name_raw, tags, summary)
                pass
            else:
                season_number = '0'

            if not season_dict:
                season_dict = {season_number: [ep['title']]}
            elif season_number in season_dict.keys():
                season_dict[season_number].append(ep['title'])
            else:
                season_dict.update({season_number: [ep['title']]})

        for season in sorted(season_dict.keys()):
            ep_count = len(season_dict[season])
            Logger('* ep_count = %i' %ep_count)
            s0 = (ep_count if season == '0' else (len(season_dict['0']) if '0' in season_dict.keys() else 0))
            season_info.update({'season': season, 'ep_count': ep_count, 'fseason': season, 'season0': s0})
            ep_info = '' if cp in CP_DATE else ' | %i Episodes' %ep_count
            s0_summary = '%s: S0 Specials, Uncensored Episodes, and Miscellaneous Videos%s' %(show_info['tv_show_name'], ep_info)
            s_summary = '%s: S%s Episodes%s' %(show_info['tv_show_name'], season, ep_info)
            if (ep_count > ips) and (season != '0'):
                season = int(season)
                x, r = divmod(main_ep_count-s0, ips)
                nseason_list = [str(t) for t in xrange(season, x + (1 if r > 0 else 0) + season)]
                Logger('* new season list = %s' %nseason_list)
                for i, nseason in enumerate(nseason_list):
                    nep_count = ((ips if r == 0 else r) if i+1 == len(nseason_list) else ips)
                    Logger('* nep_count = %i' %nep_count)
                    season_info.update({'season': nseason, 'ep_count': nep_count, 'fseason': str(i+1)})
                    nep_info = '' if cp in CP_DATE else ' | %i Episodes' %nep_count
                    s_summary = '%s: S%s seperated out S%s into multiple seasons%s' %(show_info['tv_show_name'], nseason, season, nep_info)
                    oc.add(SeasonObject(
                        key=Callback(SeasonSubPage, season_info=season_info),
                        rating_key=item_info['page_url'] + nseason,
                        title='Season %s' %nseason, show=show_info['tv_show_name'],
                        index=int(nseason), episode_count=nep_count,
                        source_title=show_info['source_title'], thumb=thumb, art=R(item_info['art']),
                        summary=s_summary
                        ))
            else:
                oc.add(SeasonObject(
                    key=Callback(SeasonSubPage, season_info=season_info),
                    rating_key=item_info['page_url'] + season,
                    title='Season %s' %season, show=show_info['tv_show_name'],
                    index=int(season), episode_count=ep_count,
                    source_title=show_info['source_title'], thumb=thumb, art=R(item_info['art']),
                    summary=s0_summary if season == '0' else s_summary
                    ))

        Logger('*' * 80)
        return oc

####################################################################################################
@route(PREFIX + '/season/sub-page', season_info=dict)
def SeasonSubPage(season_info):
    """Setup Episodes for Season"""

    title2 = '%s | Season %s' %(season_info['tv_show_name'], season_info['season'])

    oc = ObjectContainer(title2=title2, art=R(season_info['art']))

    #html = HTML.ElementFromURL(season_info['page_url'], headers=Headers.GetHeadersForURL(season_info['page_url']))
    #html = Headers.ElementFromURL(season_info['page_url'])
    html = ElementFromURL(season_info['page_url'])

    ep_list = GetItemList(html, season_info['page_url'], season_info['item_title'], season_info['type_title'])
    tags = Metadata.string_to_list(Common.StringCode(string=season_info['tags'], code='decode')) if season_info['tags'] else []
    thumb = GetThumb(cover_url=season_info['cover_url'], cover_file=season_info['cover_file'])
    summary = Metadata.GetSummary(html)
    show_name_raw = html.xpath('//div[@class="barContent"]/div/a[@class="bigChar"]/text()')[0]
    season_dict = None
    ips = int(season_info['ips'])
    cp = Client.Product

    ep_list2 = []
    for ep in ep_list:
        ep_name, ep_number = Metadata.GetEpisodeNameAndNumber(html, ep['title'], ep['url'])
        season_number = Metadata.GetSeasonNumber(ep['title'], show_name_raw, tags, summary)
        if season_number == season_info['season']:
            ep.update({'season_number': season_number, 'ep_number': ep_number})
            ep_list2.append(ep)

    if ((len(ep_list2) > ips and season_info['season'] != '0') or (len(ep_list2) == 0)):
        temp = int(season_info['fseason'])
        s0 = int(season_info['season0'])
        if len(ep_list2) == 0:
            nep_list = ep_list[ ( ((temp-1)*ips) + s0 ) : ((temp*ips) + s0) ]
        else:
            nep_list = ep_list2[((temp - 1)*ips):((temp)*ips)]
        for nep in nep_list:
            ep_name, ep_number = Metadata.GetEpisodeNameAndNumber(html, nep['title'], nep['url'])
            season_number = Metadata.GetSeasonNumber(nep['title'], show_name_raw, tags, summary)
            oc.add(EpisodeObject(
                source_title=season_info['source_title'],
                title=nep['title'] if cp in CP_DATE else '%s | %s' %(nep['title'], (nep['date'] if nep['date'] else 'NA')),
                show=season_info['tv_show_name'],
                season=int(season_number),
                index=int(ep_number),
                thumb=thumb,
                art=R(season_info['art']),
                originally_available_at=Datetime.ParseDate(nep['date']) if nep['date'] else None,
                url=nep['url']
                ))
    else:
        for ep in ep_list2:
            oc.add(EpisodeObject(
                source_title=season_info['source_title'],
                title=ep['title'] if cp in CP_DATE else '%s | %s' %(ep['title'], (ep['date'] if ep['date'] else 'NA')),
                show=season_info['tv_show_name'],
                season=int(ep['season_number']),
                index=int(ep['ep_number']),
                thumb=thumb,
                art=R(season_info['art']),
                originally_available_at=Datetime.ParseDate(ep['date']) if ep['date'] else None,
                url=ep['url']
                ))

    return oc

####################################################################################################
@route(PREFIX + '/create-photo-object', include_container=bool)
def CreatePhotoObject(title, url, art, source_title, include_container=False, *args, **kwargs):

    photo_object = PhotoObject(
        key=Callback(CreatePhotoObject,
            title=title, url=url, art=art, source_title=source_title, include_container=True),
        rating_key=url,
        source_title=source_title,
        title=title,
        thumb=url,
        art=R(art),
        items=[MediaObject(parts=[PartObject(key=url)])]
        )

    if include_container:
        return ObjectContainer(objects=[photo_object])
    else:
        return photo_object

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Set up Search for kiss(anime, asian, cartoon, manga)"""

    # set defaults
    query = query.strip()
    title2 = 'Search for \"%s\" in...' % query

    oc = ObjectContainer(title2=title2)
    # create list of search URL's
    all_search_urls = [ANIME_SEARCH_URL, CARTOON_SEARCH_URL, ASIAN_SEARCH_URL, MANGA_SEARCH_URL, COMIC_SEARCH_URL]

    # format each search url and send to 'SearchPage'
    # can't check each url here, would take too long since behind cloudflare and timeout the server
    prefs_names = ['kissanime', 'kissasian', 'kisscartoon', 'kissmanga', 'kisscomic']
    b_prefs_names = [p for p in prefs_names if Prefs[p]]
    if len(b_prefs_names) == 1:
        b_prefs_name = b_prefs_names[0]
        b_prefs_name = 'comic' if b_prefs_name == 'kisscomic' else b_prefs_name
        search_url = [s for s in all_search_urls if b_prefs_name in s][0]
        search_url_filled = search_url %String.Quote(query, usePlus=True)
        type_title = 'Drama' if b_prefs_name == 'kissasian' else (b_prefs_name.split('kiss')[1].title() if 'kiss' in b_prefs_name else 'Comic')
        art = 'art-%s.jpg' %type_title.lower()

        #html = HTML.ElementFromURL(search_url_filled, headers=Headers.GetHeadersForURL(search_url))
        #html = Headers.ElementFromURL(search_url_filled)
        html = ElementFromURL(search_url_filled)
        if html.xpath('//table[@class="listing"]'):
            return SearchPage(type_title=type_title, search_url=search_url_filled, art=art)
    else:
        Logger('*' * 80)
        for search_url in all_search_urls:
            search_url_filled = search_url % String.Quote(query, usePlus=True)
            type_title = Common.GetTypeTitle(search_url_filled)
            # change kissasian info to 'Drama'
            art = 'art-%s.jpg' %type_title.lower()
            thumb = 'icon-%s.png' %type_title.lower()
            prefs_name = 'kissasian' if type_title == 'Drama' else 'kiss%s' %type_title.lower()

            if Prefs[prefs_name]:
                Logger('* Search url = %s' %search_url_filled)
                Logger('* type title = %s' %type_title)

                #html = HTML.ElementFromURL(search_url_filled, headers=Headers.GetHeadersForURL(search_url))
                #html = Headers.ElementFromURL(search_url_filled)
                html = ElementFromURL(search_url_filled)
                if html.xpath('//table[@class="listing"]'):
                    oc.add(DirectoryObject(
                        key=Callback(SearchPage, type_title=type_title, search_url=search_url_filled, art=art),
                        title=type_title, thumb=R(thumb)
                        ))

    if len(oc) > 0:
        Logger('*' * 80)
        return oc
    else:
        Logger('* Search retunred no results')
        Logger('*' * 80)
        return MC.message_container('Search',
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

    #html = HTML.ElementFromURL(search_url, headers=Headers.GetHeadersForURL(search_url))
    #html = Headers.ElementFromURL(search_url)
    html = ElementFromURL(search_url)

    # Check for results if none then give a pop up window saying so
    if html.xpath('//table[@class="listing"]'):
        # Test for "exact" match, if True then send to 'ItemPage'
        node = html.xpath('//div[@id="headnav"]/script/text()')[0]
        search_match = Regex('var\ path\ =\ (\'Search\')').search(node)
        if not search_match:
            # Send url to 'ItemPage'
            base_url = Common.GetBaseURL(search_url)
            node = html.xpath('//div[@class="barContent"]/div/a')[0]

            item_sys_name = Common.StringCode(string=node.get('href').rsplit('/')[-1].strip(), code='encode')
            item_url = base_url + '/' + type_title + '/' + Common.StringCode(item_sys_name, code='encode')
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

            Logger('* item_title    = %s' %item_title)
            Logger('* item          = %s' %item_sys_name)
            Logger('* type_title    = %s' %type_title)
            Logger('* base_url      = %s' %base_url)
            Logger('* item_url      = %s' %item_url)

            item_info = {
                'item_sys_name': item_sys_name,
                'item_title': Common.StringCode(string=item_title, code='encode'),
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
            Logger('* art           = %s' %art)
            Logger('*' * 80)
            return DirectoryList(1, 'Search', query, search_url, type_title, art)
    # No results found :( keep trying
    else:
        Logger('* Search returned no results.', kind='Warn')
        Logger('*' * 80)
        query = search_url.rsplit('=')[-1]
        return MC.message_container('Search',
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
    page_url = item_info['page_url']
    base_url = item_info['base_url']

    # decode title string
    item_title_decode = Common.StringCode(string=item_title, code='decode')
    Logger('*' * 80)
    Logger('* item to add = %s | %s' %(item_title_decode, item_sys_name), kind='Info')

    # setup html for parsing
    #html = HTML.ElementFromURL(page_url, headers=Headers.GetHeadersForURL(base_url))
    #html = Headers.ElementFromURL(page_url)
    html = ElementFromURL(page_url)

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

    # get summary
    summary = Metadata.GetSummary(html)

    # setup new bookmark json data to add to Dict

    new_bookmark = {
        type_title: item_sys_name, 'item_title': item_title, 'cover_file': image_file,
        'cover_url': cover_url, 'summary': summary, 'genres': genres, 'page_url': page_url}

    Logger('* new bookmark to add >>')
    Logger('* %s' % new_bookmark)

    bm = Dict['Bookmarks']

    # Test if the Dict has the 'Bookmarks' section yet
    if not bm:
        # Create new 'Bookmarks' section and fill with the first bookmark
        Dict['Bookmarks'] = {type_title: [new_bookmark]}
        Logger('* Inital bookmark list created >>')
        Logger('* %s' %bm)
        Logger('*' * 80)

        # Update Dict to include new 'Bookmarks' section
        Dict.Save()

        # Provide feedback that the Item has been added to bookmarks
        return MC.message_container(item_title_decode,
            '\"%s\" has been added to your bookmarks.' %item_title_decode)
    # check if the category key 'Anime', 'Manga', 'Cartoon', 'Drama', or 'Comic' exist
    # if so then append new bookmark to one of those categories
    elif type_title in bm.keys():
        # fail safe for when clients are out of sync and it trys to add the bookmark in duplicate
        if (True if [b[type_title] for b in bm[type_title] if b[type_title] == item_sys_name] else False):
            # Bookmark already exist, don't add in duplicate
            Logger('* bookmark \"%s\" already in your bookmarks' %item_title_decode, kind='Info')
            Logger('*' * 80)
            return MC.message_container(item_title_decode,
                '\"%s\" is already in your bookmarks.' %item_title_decode)
        # append new bookmark to its correct category, i.e. 'Anime', 'Drama', etc...
        else:
            temp = {}
            temp.setdefault(type_title, bm[type_title]).append(new_bookmark)
            Dict['Bookmarks'][type_title] = temp[type_title]
            Logger('* bookmark \"%s\" has been appended to your %s bookmarks' %(item_title_decode, type_title), kind='Info')
            Logger('*' * 80)

            # Update Dict to include new Item
            Dict.Save()

            # Provide feedback that the Item has been added to bookmarks
            return MC.message_container(item_title_decode,
                '\"%s\" has been added to your bookmarks.' %item_title_decode)
    # the category key does not exist yet so create it and fill with new bookmark
    else:
        Dict['Bookmarks'].update({type_title: [new_bookmark]})
        Logger('* bookmark \"%s\" has been created in new %s section in bookmarks' %(item_title_decode, type_title), kind='Info')
        Logger('*' * 80)

        # Update Dict to include new Item
        Dict.Save()

        # Provide feedback that the Item has been added to bookmarks
        return MC.message_container(item_title_decode,
            '\"%s\" has been added to your bookmarks.' %item_title_decode)

####################################################################################################
@route(PREFIX + '/removebookmark', item_info=dict)
def RemoveBookmark(item_info):
    """Removes item from the bookmarks list using the item as a key"""

    # set variables
    item_sys_name = item_info['item_sys_name']
    item_title = item_info['item_title']
    type_title = item_info['type_title']

    # decode string
    item_title_decode = Common.StringCode(string=item_title, code='decode')

    # index 'Bookmarks' list
    bm = Dict['Bookmarks'][type_title]
    Logger('* bookmark length = %s' %len(bm))
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
    Logger('* \"%s\" has been removed from Bookmark List' % item_title_decode, kind='Info')

    if len(bm) == 0:
        # if the last bookmark was removed then clear it's bookmark section
        Logger('* %s bookmark was the last, so removed %s bookmark section' %(item_title_decode, type_title), force=True)
        Logger('*' * 80)
        return ClearBookmarks(type_title)
    else:
        Logger('*' * 80)
        # Provide feedback that the Item has been removed from the 'Bookmarks' list
        return MC.message_container(type_title,
            '\"%s\" has been removed from your bookmarks.' %item_title_decode)

####################################################################################################
@route(PREFIX + '/clearbookmarks')
def ClearBookmarks(type_title):
    """Remove 'Bookmarks' Section(s) from Dict. Note: This removes all bookmarks in list"""

    Logger('*' * 80)
    if 'All' in type_title:
        if not Prefs['cache_covers']:
            for key in Dict['Bookmarks'].keys():
                for bookmark in Dict['Bookmarks'][key]:
                    RemoveCoverImage(bookmark['cover_file'])

        # delete 'Bookmarks' section from Dict
        del Dict['Bookmarks']
        Logger('* Entire Bookmark Dict Removed')
    else:
        if not Prefs['cache_covers']:
            for bookmark in Dict['Bookmarks'][type_title]:
                RemoveCoverImage(bookmark['cover_file'])

        # delete section 'Anime', 'Manga', 'Cartoon', 'Drama', or 'Comic' from bookmark list
        del Dict['Bookmarks'][type_title]
        Logger('* \"%s\" Bookmark Section Cleared' % type_title)

    Dict['Bookmark_Deleted'] = {'bool': True, 'type_title': type_title}
    status = Dict['Bookmark_Deleted']
    Logger('*' * 80)

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
    Logger('*' * 80)

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
                Logger('* Attempting to update Anime Bookmarks', kind='Debug', force=True)
        Logger('* Skipping Caching Covers on Prefs Update. Bookmark Covers Already Cached.', kind='Info', force=True)
        return

    if not Prefs['cache_bookmark_covers'] and not Prefs['cache_covers']:
        # remove any cached covers from Dict['Bookmarks']
        # unless Prefs['cache_covers'] is true, then keep cached covers
        if cf:
            for cover in cf:
                RemoveCoverImage(image_file=cf[cover])

            del Dict['cover_files']
            Dict.Save()
            Logger('* Removed cached covers using Dict[\'cover_files\'] list as key, and removed Dict[\'cover_files\'] once finished.', kind='Info')
        elif bm:
            [[RemoveCoverImage(image_file=bbm['cover_file']) for bbm in bm[key]] for key in bm.keys()]

            Logger('* No Dict[\'cover_files\'] found, Removed cached covers using Dict[\'Bookmarks\'] list as key.', kind='Info')
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
                            Logger('* file %s already exist' %cover_file, kind='Info')
                        else:
                            Log.Error('* %s | %s | Unknown Error Occurred' %(cover_file, thumb))
                    else:
                        Log.Error('* %s | %s | Unknown Error Occurred' %(sbm['cover_file'], sbm['cover_url']))

        Logger('* Caching Bookmark Cover images if they have not been already.', kind='Info')
        if cf:
            cover_cache = set([c for c in cf])
            cover_cache_diff = cover_cache.difference(bookmark_cache)
            for cover in cover_cache_diff:
                RemoveCoverImage(image_file=cf[cover])
                del Dict['cover_files'][cover]

            Logger('* Removed cached covers using Dict[\'cover_files\'] list as key, and removed Dict[\'cover_files\'] once finished.', kind='Info')
            Logger('* But kept Bookmarks cached covers.', kind='Info')
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
                            Logger('* file %s already exist' %cover_file, kind='Info')
                        else:
                            Log.Error('* %s | %s | Unknown Error Occurred' %(cover_file, thumb))
                    else:
                        Log.Error('* %s | %s | Unknown Error Occurred' %(sbm['cover_file'], sbm['cover_url']))

        Logger('* Caching Bookmark Cover images if they have not been already.', kind='Info')
        Logger('* All covers cached set to True.', kind='Info')
    Logger('*' * 80)
    Dict.Save()
    return

####################################################################################################
@route(PREFIX + '/remove-cover-image')
def RemoveCoverImage(image_file):
    """Remove Cover Image"""
    if image_file:
        path = Core.storage.join_path(Common.RESOURCES_PATH, image_file)

        if Core.storage.file_exists(path):
            Core.storage.remove(path)

    return

####################################################################################################
def UpdateLegacyBookmark(bm_info=dict):
    """
    Update Old Bookmark to new Style of bookmarks.
    Update includes "Genres" for now, will add more here later if need be
    """

    type_title = bm_info['type_title']
    item_title = bm_info['item_title']
    item_title_decode = Common.StringCode(string=item_title, code='decode')
    base_url = bm_info['base_url']
    page_url = base_url + '/' + bm_info['page_url'].split('/', 3)[3]

    #html = HTML.ElementFromURL(page_url, headers=Headers.GetHeadersForURL(bm_info['base_url']))
    #html = Headers.ElementFromURL(page_url)
    html = ElementFromURL(page_url)

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
            Log.Debug('* %s Bookmark \"%s\" Updated' %(type_title, item_title_decode))
            Log.Debug('* updated bookmark = %s' %bm[i])
            Log.Debug('*' * 80)
            break

    # Update Dict to include new Item
    Dict.Save()

    return

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
@route(PREFIX + '/auto-cache')
def BackgroundAutoCache():
    """Auto Cache Headers"""

    Logger('*' * 80)
    # setup urls for setting headers
    if not Dict['First Headers Cached']:
        Logger('* Running Background Auto-Cache', force=True)

        if Core.storage.file_exists(Core.storage.join_path(Core.storage.data_path, 'Header_Dict')):
            Logger('* Header Dictionary already found, writing new Headers to old Dictionary', force=True)

            # get headers for each url
            for (t, u) in Common.BASE_URL_LIST_T:
                prefs_name = 'kissasian' if t == 'Drama' else 'kiss%s' %t.lower()
                if Prefs[prefs_name]:
                    Headers.GetHeadersForURL(u)

        else:
            # Header Dictionary not yet setup, so create it and fill in the data
            Headers.CreateHeadersDict()

        # check to make sure each section/url has cookies now
        Logger('* All cookies')
        Logger('* %s' %Headers.LoadHeaderDict())

        # Setup the Dict and save
        Dict['First Headers Cached'] = True
        Dict['Headers Auto Cached'] = True
        Dict.Save()
    else:
        for (t, u) in Common.BASE_URL_LIST_T:
            prefs_name = 'kissasian' if t == 'Drama' else 'kiss%s' %t.lower()
            if Prefs[prefs_name]:
                Logger('* Checking %s headers' %u, kind='Info', force=True)
                Headers.GetHeadersForURL(u)

        Logger('* Completed Header Cache Check', force=True)
        Logger('* Headers will be cached independently when needed from now on', force=True)
        pass
    Logger('*' * 80)

    return ValidatePrefs(start=True, skip=False)

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
            Logger('* cover file name   = %s' %cover_file)
            if Common.CoverImageFileExist(cover_file):
                if cover_file not in Dict['cover_files']:
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
def ClearCache(timeout):
    """Clear old Cached URLs depending on input timeout"""

    cachetime = Datetime.Now()
    count = 0
    Log.Debug('* Clearing Cached URLs older than %s' %str(cachetime - timeout))
    path = os.path.join(Common.SUPPORT_PATH, "DataItems")
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for filename in files:
        item = filename.split('__cachetime__')
        if (Datetime.FromTimestamp(int(item[1])) + timeout) <= cachetime:
            Data.Remove(filename)
            count += 1
    Log.Debug('* Cleaned %i Cached files' %count)
    return

####################################################################################################
def ElementFromURL(url):
    """setup requests html"""

    cachetime = Datetime.Now()
    #timeout = Datetime.Delta(hours=1)
    name = slugify(url) + '__cachetime__%i' %Datetime.TimestampFromDatetime(cachetime)

    match = False
    path = os.path.join(Common.SUPPORT_PATH, "DataItems")
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for filename in files:
        item = filename.split('__cachetime__')
        if slugify(url) == item[0]:
            match = True
            if (Datetime.FromTimestamp(int(item[1])) + TIMEOUT) <= cachetime:
                Log.Debug('* Re-Caching URL')
                html = get_element_from_url(url, name)
                break
            else:
                Log.Debug('* Reading URL from Cache')
                html = HTML.ElementFromString(Data.Load(filename))
                break

    if not match:
        Log.Debug('* Caching URL')
        html = get_element_from_url(url, name)

    return html

####################################################################################################
def get_element_from_url(url, name, count=0):
    """error handling for URL requests"""

    try:
        page = requests.get(url, headers=Headers.GetHeadersForURL(url))
        if int(page.status_code) == 503:
            Log.Error('* get_element_from_url Error: HTTP 503 Site Error. Refreshing site cookies')
            if count <= 1:
                count += 1
                Headers.GetHeadersForURL(url, update=True)
                return get_element_from_url(url, name, count)
            else:
                Log.Error('* get_element_from_url Error: HTTP 503 Site error, tried refreshing cookies but that did not fix the issue')
                if Data.Exists(name):
                    Log.Error('* Using old cached page')
                    html = HTML.ElementFromString(page.text)
                else:
                    html = HTML.Element('head', 'Error')
        else:
            Data.Save(name, page.text)
            html = HTML.ElementFromString(page.text)
    except Exception as e:
        Log.Error('* get_element_from_url Error: Cannot load %s' %url)
        Log.Error('* get_element_from_url Error: %s' %str(e))
        html = HTML.Element('head', 'Error')

    return html

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
