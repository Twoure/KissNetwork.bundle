####################################################################################################
#                                                                                                  #
#                               KissNetwork Plex Channel -- v0.04                                  #
#                                                                                                  #
####################################################################################################
# import section(s) not included in Plex Plug-In Framwork
import sys, shutil, io

# import Shared Service Code
Test = SharedCodeService.test

# add custom modules to python path
module_path = Core.storage.join_path(
    Core.app_support_path, Core.config.bundles_dir_name,
    'KissNetwork.bundle', 'Contents', 'Modules')

if module_path not in sys.path:
    sys.path.append(module_path)
    Log.Info('\n----------\n%s\n---^^^^---added to sys.path---^^^^---' % module_path)

# import custom modules
import requests

# set global variables
PREFIX = '/video/kissnetwork'
TITLE = 'KissNetwork'
LIST_VIEW_CLIENTS = ['Android', 'iOS']
ADULT_LIST = set(['Adult', 'Smut', 'Ecchi', 'Lolicon', 'Mature', 'Yaoi', 'Yuri'])

# KissAnime
ANIME_BASE_URL = 'http://kissanime.com'
ANIME_SEARCH_URL = ANIME_BASE_URL + '/Search/Anime?keyword=%s'
ANIME_ART = 'art-anime.png'
ANIME_ICON = 'icon-anime.png'

# KissAsian
ASIAN_BASE_URL = 'http://kissasian.com'
ASIAN_SEARCH_URL = ASIAN_BASE_URL + '/Search/Drama?keyword=%s'
ASIAN_ART = 'art-drama.png'
ASIAN_ICON = 'icon-drama.png'

# KissCartoon
CARTOON_BASE_URL = 'http://kisscartoon.me'
CARTOON_SEARCH_URL = CARTOON_BASE_URL + '/Search/Cartoon?keyword=%s'
CARTOON_ART = 'art-cartoon.png'
CARTOON_ICON = 'icon-cartoon.png'

# KissManga
MANGA_BASE_URL = 'http://kissmanga.com'
MANGA_SEARCH_URL = MANGA_BASE_URL + '/Search/Manga?keyword=%s'
MANGA_ART = 'art-manga.png'
MANGA_ICON = 'icon-manga.png'

# set background art and icon defaults
MAIN_ART = 'art-main.png'
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

####################################################################################################

def Start():
    ObjectContainer.art = R(MAIN_ART)
    ObjectContainer.title1 = TITLE

    DirectoryObject.thumb = R(MAIN_ICON)

    HTTP.CacheTime = 0
    HTTP.Headers['User-Agent'] = Test.USER_AGENT

    Dict['First Headers Cached'] = False

    if Dict['Headers Auto Cached']:
        if not Dict['Headers Auto Cached']:
            Log.Info('\n----------Caching Headers----------')
            Thread.Create(BackgroundAutoCache)
        else:
            Log.Info('\n----------Cookies already cached----------')
    else:
        Dict['Headers Auto Cached'] = False
        Log.Info('\n----------Caching Headers----------')
        Thread.Create(BackgroundAutoCache)

####################################################################################################
# Create the main menu

@handler(PREFIX, TITLE, thumb='icon-default.png', art='art-main.png')
def MainMenu():
    oc = ObjectContainer(title2=TITLE, no_cache=True)

    # set thumbs based on client
    if Client.Platform in LIST_VIEW_CLIENTS:
        anime_thumb = None
        cartoon_thumb = None
        drama_thumb = None
        manga_thumb = None
        bookmark_thumb = None
        prefs_thumb = None
        search_thumb = None
    else:
        anime_thumb = ANIME_ICON
        cartoon_thumb = CARTOON_ICON
        drama_thumb = ASIAN_ICON
        manga_thumb = MANGA_ICON
        bookmark_thumb = BOOKMARK_ICON
        prefs_thumb = PREFS_ICON
        search_thumb = SEARCH_ICON

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
            title='Anime', thumb=R(anime_thumb)))

    if Prefs['kisscartoon']:
        oc.add(DirectoryObject(
            key=Callback(KissCartoon, url=CARTOON_BASE_URL, title='Cartoon', art=CARTOON_ART),
            title='Cartoons', thumb=R(cartoon_thumb)))

    if Prefs['kissasian']:
        oc.add(DirectoryObject(
            key=Callback(KissAsian, url=ASIAN_BASE_URL, title='Drama', art=ASIAN_ART),
            title='Drama', thumb=R(drama_thumb)))

    if Prefs['kissmanga']:
        oc.add(DirectoryObject(
            key=Callback(KissManga, url=MANGA_BASE_URL, title='Manga', art=MANGA_ART),
            title='Manga', thumb=R(manga_thumb)))

    oc.add(DirectoryObject(
        key=Callback(BookmarksMain, title='My Bookmarks', status=status), title='My Bookmarks', thumb=R(bookmark_thumb)))
    oc.add(PrefsObject(title='Preferences', thumb=R(prefs_thumb)))
    oc.add(InputDirectoryObject(
        key=Callback(Search), title='Search', summary='Search KissNetwork', prompt='Search for...',
        thumb=R(search_thumb)))

    return oc

####################################################################################################
# Create KissAnime site Menu

@route(PREFIX + '/kissanime')
def KissAnime(url, title, art):
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
# Create KissAsian site Menu

@route(PREFIX + '/kissasian')
def KissAsian(url, title, art):
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
# Create KissCartoon site Menu

@route(PREFIX + '/kisscartoon')
def KissCartoon(url, title, art):
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
# Create KissManga site Menu

@route(PREFIX + '/kissmanga')
def KissManga(url, title, art):
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
# Set the sorting options for displaying all lists

@route(PREFIX + '/validateprefs')
def ValidatePrefs():
    # load prefs into dict for use later
    if Prefs['sort_opt'] == 'Alphabet':
        Dict['s_opt'] = ''
    elif Prefs['sort_opt'] == 'Popularity':
        Dict['s_opt'] = '/MostPopular'
    elif Prefs['sort_opt'] == 'Latest Update':
        Dict['s_opt'] = '/LatestUpdate'
    elif Prefs['sort_opt'] == 'Newest':
        Dict['s_opt'] = '/Newest'

    # Check bookmark cache image opt
    # if not cache images then remove any old ones
    # created as Thread so it will run in the background
    Thread.Create(CacheBookmarkCovers)

    # Update the Dict to latest prefs
    Dict.Save()

####################################################################################################
# Create Bookmark Main Menu

@route(PREFIX + '/bookmarks', status=dict)
def BookmarksMain(title, status):
    if status['bool']:
        oc = ObjectContainer(title2=title, header="My Bookmarks",
            message='%s bookmarks have been cleared.' % status['type_title'], no_cache=True)
    else:
        oc = ObjectContainer(title2=title, no_cache=True)

    # check for 'Bookmarks' section in Dict
    if not Dict['Bookmarks']:
        # if no 'Bookmarks' section the return pop up
        return MessageContainer(header=title,
            message='No Bookmarks yet. Get out there and start adding some!!!.')
    # create boomark directory based on category
    else:
        for key in sorted(Dict['Bookmarks'].keys()):
            if not key == 'Drama':
                art = 'art-%s.png' %key.lower()
                thumb = 'icon-%s.png' %key.lower()
                prefs_name = 'kiss%s' %key.lower()
            else:
                art = 'art-drama.png'
                thumb = 'icon-drama.png'
                prefs_name = 'kissasian'

            # if site in Prefs then add its bookmark section
            if Prefs[prefs_name]:
                # Create sub Categories for Anime, Cartoon, Drama, and Manga
                oc.add(DirectoryObject(
                    key=Callback(BookmarksSub, type_title=key, art=art),
                    title=key, thumb=R(thumb), summary='Display %s Bookmarks' % key))
        # test if no sites are picked in the Prefs
        if len(oc) > 0:
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
# Loads bookmarked items from Dict.

@route(PREFIX + '/bookmarkssub')
def BookmarksSub(type_title, art):
    if type_title == 'Drama':
        base_url = ASIAN_BASE_URL
    elif type_title == 'Cartoon':
        base_url = CARTOON_BASE_URL
    else:
        base_url = 'http://kiss%s.com' %type_title.lower()

    oc = ObjectContainer(title2='My Bookmarks | %s' % type_title, art=R(art))
    Logger('category %s' %type_title)

    # Fill in DirectoryObject information from the bookmark list
    for bookmark in sorted(Dict['Bookmarks'][type_title]):
        item_title = bookmark['item_title']
        summary = bookmark['summary']

        if summary:
            summary2 = summary.decode('unicode_escape')
        else:
            summary2 = None

        if type_title == 'Manga':
            cover = bookmark['cover_url']
        elif Prefs['cache_covers']:
            cover = bookmark['cover_file']
            if CoverImageFileExist(cover):
                cover = R(cover)
            else:
                cover = R(SaveCoverImage(bookmark['cover_url']))
        else:
            cover = None

        item_info = {
            'item_sys_name': bookmark[type_title],
            'item_title': item_title,
            'short_summary': summary,
            'cover_url': bookmark['cover_url'],
            'type_title': type_title,
            'base_url': 'http://' + bookmark['page_url'].rsplit('/')[2],
            'page_url': bookmark['page_url'],
            'art': art}

        # gotta send the bookmark somewhere
        oc.add(DirectoryObject(
            key=Callback(ItemPage, item_info=item_info),
            title=item_title.decode('unicode_escape'), summary=summary2, thumb=cover))
    # setup icons depending on platform
    if Client.Platform in LIST_VIEW_CLIENTS and not cover:
        bm_clr_icon = None
    else:
        bm_clr_icon = R(BOOKMARK_CLEAR_ICON)

    # add a way to clear this bookmark section and start fresh
    oc.add(DirectoryObject(
        key=Callback(ClearBookmarks, type_title=type_title),
        title='Clear All \"%s\" Bookmarks' % type_title,
        thumb=bm_clr_icon,
        summary='CAUTION! This will clear your entire \"%s\" bookmark section!' % type_title))

    if Dict['Bookmarks'][type_title]:
        return oc
    else:
        return MessageContainer(header='Error',
                message='Bookmarks list is dirty, add bookmarks to this list or start over')

####################################################################################################
# Create ABC directory for each kiss site

@route(PREFIX + '/alphabets')
def AlphabetList(url, title, art):
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
# Create Genre directory for each kiss site

@route(PREFIX + '/genres')
def GenreList(url, title, art):
    genre_url = url + '/%sList' % title  # setup url for finding current Genre list

    # add exception in case the cookies are being refreshed
    try:
        # formate url response into html for xpath
        html = HTML.ElementFromURL(genre_url, headers=Test.GetHeadersForURL(genre_url))
    except:
        return MessageContainer(header=title,
            message='Please wait a second or two while the URL Headers are set, then try again')

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
# Create Country directory for KissAsian

@route(PREFIX + '/countries')
def CountryList(url, title, art):
    country_url = url + '/DramaList'  # setup url for finding current Country list

    try:
        html = HTML.ElementFromURL(country_url, headers=Test.GetHeadersForURL(country_url))
    except:
        return MessageContainer(header=title,
            message='Please wait a second or two while the URL Headers are set, then try again')

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
# GenreList, AlphabetList, CountryList, and Search are sent here
# Pulls out Items name and creates directories for them
# Plan to add section that detects if Genre is empty

@route(PREFIX + '/directory')
def DirectoryList(page, pname, category, base_url, type_title, art):
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
        item_url = base_url + '/%sList%s?page=%s' % (type_title, Dict['s_opt'], page)
    else:
        # No Genre with Prefs
        item_url = base_url + '/%sList%s?c=%s&page=%s' % (type_title, Dict['s_opt'], pname, page)

    Logger('Sorting Option = %s' % Dict['s_opt'])  # Log Pref being used
    Logger('Category= %s | URL= %s' % (pname, item_url))

    try:
        # format url and set variables
        html = HTML.ElementFromURL(item_url, headers=Test.GetHeadersForURL(base_url))
    except:
        return MessageContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again')

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
        total_pages = Regex("page=(\d+)").search(pages).group(1)  # give last page number
        # set title2 ie main_title
        main_title = '%s | %s | Page %s of %s' % (type_title, str(category), str(page), str(total_pages))
    elif "Search" in pname:
        # set title2 for search page
        main_title = 'Search for: %s in %s' % (str(category), type_title)
    else:
        # set title2 for last page
        main_title = '%s | %s | Page %s, Last Page' % (type_title, str(category), str(page))

    oc = ObjectContainer(title2=main_title, art=R(art))

    # parse url for each Item and pull out its title, summary, and cover image
    # took some time to figure out how to get the javascript info
    for item in html.xpath('//table[@class="listing"]/tr'):
        m = item.xpath('./td')
        if m:  # skip empty matches
            if m[0].get('title'):  # pull out the first 'td' since there are two
                title_text = m[0].get('title')  # convert section to string for searching
                # search for cover url and summary string
                try:
                    thumb = Regex('src=\"([\S].*?)\"').search(title_text).group(1)
                except:
                    thumb = None

                summary = Regex('(?s)<p>([\r\n].*)</p>').search(title_text)
                summary = summary.group(1).strip().encode('ascii', 'ignore')

                item_url_base = m[0].xpath('./a/@href')[0]
                item_sys_name = item_url_base.rsplit('/')[-1].strip().encode('unicode_escape')
                item_url_final = base_url + String.Quote(item_url_base)

                item_title = m[0].xpath('./a/text()')[0].strip()

                if m[1].xpath('./a'):
                    item_title_cleaned = Regex('[^a-zA-Z0-9 \n]').sub('', item_title)
                    latest = m[1].xpath('./a/text()')[0].strip().replace(item_title_cleaned, '')
                    latest = latest.replace('Read Online', '').replace('Watch Online', '').strip()
                    title2 = '%s | Latest %s' % (item_title, latest)
                else:
                    if 'Movie' in pname:
                        title2 = item_title
                    else:
                        title2 = '%s | %s Completed' % (item_title, type_title)

            item_info = {
                'item_sys_name': item_sys_name,
                'item_title': item_title.encode('unicode_escape'),
                'short_summary': summary,
                'cover_url': thumb,
                'type_title': type_title,
                'base_url': base_url,
                'page_url': item_url_final,
                'art': art
                }

            oc.add(DirectoryObject(
                key=Callback(ItemPage, item_info=item_info),
                title=title2, summary=summary, thumb=thumb if type_title == 'Manga' else None))

    if nextpg_node:  # if not 'None' then find the next page and create a button
        nextpg = int(Regex("page=(\d+)").search(nextpg_node).group(1))
        Logger('NextPage = %d' % nextpg)
        Logger('base url = %s' %base_url)
        oc.add(NextPageObject(
            key=Callback(DirectoryList,
                page=nextpg, pname=pname, category=category, base_url=base_url, type_title=type_title, art=art),
            title='Next Page>>', thumb=R(NEXT_ICON) if not Client.Platform in LIST_VIEW_CLIENTS else None))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer(header=type_title, message='%s list is empty' %category)

####################################################################################################
@route(PREFIX + '/homedirectorylist')
def HomePageList(tab, category, base_url, type_title, art):
    main_title = '%s | %s' % (type_title, category)
    oc = ObjectContainer(title2=main_title, art=R(art))

    try:
        html = HTML.ElementFromURL(base_url, headers=Test.GetHeadersForURL(base_url))
    except:
        return MessageContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again')

    # scrape home page for Top (Day, Week, and Month) list
    for node in html.xpath('//div[@id="tab-top-%s"]/div' %tab):
        page_node = node.xpath('./a')[1].get('href')
        item_sys_name = page_node.split('/')[-1]
        item_title = node.xpath('./a/span[@class="title"]/text()')[0]
        latest = node.xpath('./p/span[@class="info"][text()="Latest:"]/../a/text()')[0]
        title2 = '%s | Latest %s' %(item_title, latest)
        summary = 'NA'  # no summarys are given in the 'Top' lists
        thumb = node.xpath('./a/img')[0].get('src')
        page_url = base_url + '/' + page_node

        item_info = {
            'item_sys_name': item_sys_name,
            'item_title': item_title.encode('unicode_escape'),
            'short_summary': summary,
            'cover_url': thumb,
            'type_title': type_title,
            'base_url': base_url,
            'page_url': page_url,
            'art': art
            }

        # send results to ItemPage
        oc.add(DirectoryObject(
            key=Callback(ItemPage, item_info=item_info), title=title2))

    return oc

####################################################################################################
# Create the Media Page with the Video(s)/Chapter(s) section and a Bookmark option Add/Remove

@route(PREFIX + '/item', item_info=dict)
def ItemPage(item_info):
    # set variables
    item_sys_name = item_info['item_sys_name']
    item_title = item_info['item_title']
    type_title = item_info['type_title']
    base_url = item_info['base_url']
    page_url = item_info['page_url']
    art = item_info['art']

    # decode unicode string
    item_title_decode = item_info['item_title'].decode('unicode_escape')

    # setup new title2 for container
    title2 = '%s | %s' % (type_title, item_title_decode)

    oc = ObjectContainer(title2=title2, art=R(art))

    try:
        html = HTML.ElementFromURL(page_url, headers=Test.GetHeadersForURL(base_url))
    except:
        return MessageContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again')

    # Check for Adult content, block if Prefs set.
    genres = html.xpath('//p[span[@class="info"]="Genres:"]/a/text()')
    Log('genres = %s' %genres)
    if genres and not Prefs['adult']:
        matching_list = set(genres) & ADULT_LIST
        Log
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
# Create the Item Sub Page with Video or Chapter list

@route(PREFIX + '/itemsubpage', item_info=dict)
def ItemSubPage(item_info):
    # set variables
    item_sys_name = item_info['item_sys_name']
    item_title = item_info['item_title']
    type_title = item_info['type_title']
    base_url = item_info['base_url']
    page_url = item_info['page_url']
    page_category = item_info['page_category']
    art = item_info['art']

    # decode unicode string(s)
    item_title_decode = item_title.decode('unicode_escape')

    # setup title2 for container
    title2 = '%s | %s | %s' % (type_title, item_title_decode, page_category.lower())

    # remove special charaters from item_title for matching later
    item_title_decode = Regex('[^a-zA-Z0-9 \n\.]').sub('', item_title_decode)

    # remove '(s)' from page_category string for logs
    s_removed_page_category = page_category.rsplit('(')[0]

    oc = ObjectContainer(title2=title2, art=R(art))

    Logger('item sub page url = %s' %page_url)

    try:
        # setup html for parsing
        html = HTML.ElementFromURL(page_url, headers=Test.GetHeadersForURL(page_url))
    except:
        return MessageContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again')

    # parse html for media url, title and date added
    a = []
    b = []

    for media in html.xpath('//table[@class="listing"]/tr/td'):
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
                'title': x[1].encode('unicode_escape'),
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
# Create Video container
# don't like that I need this, but if not the Service URL will parse all the videos
#   and bog down the server respose time

@route(PREFIX + '/videodetail', video_info=dict, item_info=dict)
def VideoDetail(video_info, item_info):
    # set variables
    title = video_info['title'].decode('unicode_escape')
    date = Datetime.ParseDate(video_info['date'])
    summary = item_info['short_summary']
    if summary:
        summary = summary.decode('unicode_escape')
    thumb = item_info['cover_url']
    art = item_info['art']
    url = video_info['video_page_url']

    oc = ObjectContainer(title2=title, art=R(art))

    Logger('vido url in video detail section = %s' %url)

    try:
        # setup html for parsing
        html = HTML.ElementFromURL(url, headers=Test.GetHeadersForURL(url))
    except:
        return MessageContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again')

    # test if video link is hosted on OneDrive
    # currently the URL Service is not setup to handle OneDrive Links
    onedrive_test = html.xpath('//div[@id="centerDivVideo"]//iframe')
    if onedrive_test:
        if "onedrive" in onedrive_test[0].get('src'):
            return MessageContainer(header='Error',
                message=
                    """
                    OneDrive Videos Not Yet Supported.
                    Try another source if avalible.
                    """)

    # Movie
    if video_info['video_type'] == 'movie':
        oc.add(
            MovieObject(
                title=title,
                summary=summary,
                originally_available_at=date,
                thumb=thumb,
                art=R(art),
                url=url))
    # TV Episode
    elif video_info['video_type'] == 'episode':
        oc.add(
            EpisodeObject(
                title=title,
                summary=summary,
                thumb=thumb,
                art=R(art),
                originally_available_at=date,
                url=url))
    # everything else
    else:
        oc.add(
            VideoClipObject(
                title=title,
                summary=summary,
                thumb=thumb,
                art=R(art),
                originally_available_at=date,
                url=url))

    return oc

####################################################################################################
# Set up Search for kiss(anime, asian, cartoon, manga)

@route(PREFIX + '/search')
def Search(query=''):
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
            art = 'art-%s.png' % type_title.lower()
            thumb = 'icon-%s.png' % type_title.lower()
            prefs_name = 'kiss%s' %type_title.lower()

        if Prefs[prefs_name]:
            Logger('Search url=%s' % search_url_filled)
            Logger('type title = %s' %type_title)

            html = HTML.ElementFromURL(search_url_filled, headers=Test.GetHeadersForURL(search_url))
            if html.xpath('//table[@class="listing"]'):
                oc.add(DirectoryObject(
                    key=Callback(SearchPage, type_title=type_title, search_url=search_url_filled, art=art),
                    title=type_title, thumb=R(thumb)))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer("Search",
            """
            There are no search results for \"%s\".
            Try being less specific or make sure at least one source is selected in the Preferences.
            """ %query)

####################################################################################################
# Retrun searches for each kiss() page
# The results can return the Item itself via a url redirect.

@route(PREFIX + '/searchpage')
def SearchPage(type_title, search_url, art):
    # Check for "exact" matches and send them to ItemPage
    # If normal seach result then send to DirectoryList

    try:
        html = HTML.ElementFromURL(search_url, headers=Test.GetHeadersForURL(search_url))
    except:
        return MessageContainer(header=type_title + ' Search',
            message='Please wait a second or two while the URL Headers are set, then try again')

    # Check for results if none then give a pop up window saying so
    if html.xpath('//table[@class="listing"]'):
        # Test for "exact" match, if True then send to 'ItemPage'
        node = html.xpath('//div[@id="headnav"]/script/text()')[0]
        search_match = Regex('var\ path\ =\ (\'Search\')').search(node)
        if not search_match:
            # Send url to 'ItemPage'
            base_url = Test.GetBaseURL(search_url)
            node = html.xpath('//div[@class="barContent"]/div/a')[0]

            item_sys_name = node.get('href').rsplit('/')[-1].strip()
            item_url = base_url + '/' + type_title + '/' + String.Quote(item_sys_name)
            item_title = node.text
            cover_url = html.xpath('//head/link[@rel="image_src"]')[0].get('href')

            Logger('\nitem_title=%s\nitem=%s\ntype_title=%s\nbase_url=%s\nitem_url=%s'
                % (item_title, item_sys_name, type_title, base_url, item_url))

            item_info = {
                'item_sys_name': item_sys_name,
                'item_title': item_title.encode('unicode_escape'),
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
            Log.Debug('art = %s' %art)
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
# Adds Item to the bookmarks list

@route(PREFIX + '/addbookmark', item_info=dict)
def AddBookmark(item_info):
    # set variables
    item_sys_name = item_info['item_sys_name']
    item_title = item_info['item_title']
    type_title = item_info['type_title']
    cover_url = item_info['cover_url']
    short_summary = item_info['short_summary']
    page_url = item_info['page_url']

    # decode title string
    item_title_decode = item_title.decode('unicode_escape')

    Logger('item to add = %s' %item_sys_name, kind='Info')

    try:
        # setup html for parsing
        html = HTML.ElementFromURL(page_url, headers=Test.GetHeadersForURL(page_url))
    except:
        return MessageContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again')

    # if no cover url then try and find one on the item page
    if not cover_url:
        try:
            cover_url = html.xpath('//head/link[@rel="image_src"]')[0].get('href')
        except:
            cover_url = None

    # set full summary
    summary = html.xpath('//p[span[@class="info"]="Summary:"]/following-sibling::p')
    if summary:
        summary = summary[0].text_content().strip()
    else:
        summary = html.xpath('//p[span[@class="info"]="Summary:"]/following-sibling::p/span')
        if summary:
            summary = summary[0].text_content().strip()
        else:
            summary = html.xpath('//div[@id="container"]//table//td')
            if summary:
                summary = summary[0].text_content().strip()
            else:
                summary = html.xpath('//div[@id="container"]//div[@class="barContent"]/div/div')
                if summary:
                    summary = summary[0].text_content().strip()
                    # fix string encoding errors before they happen by converting to unicode
                    summary = summary.encode('unicode_escape')
                else:
                    summary = None

    Logger('summary = %s' %summary, kind='Debug')

    # setup new bookmark json data to add to Dict
    # Manga cover urls are accessible so no need to store images locally
    if type_title == 'Manga':
        new_bookmark = {
            type_title: item_sys_name, 'item_title': item_title,
            'cover_url': cover_url, 'summary': summary, 'page_url': page_url}
    # Need to store covers locally as files
    else:
        if Prefs['cache_covers']:
            try:
                image_file = SaveCoverImage(cover_url)
            except:
                image_file = None
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
            return MessageContainer(header=item_title_decode,
                message='\"%s\" is already in your bookarks.' % item_title_decode)
        # append new bookmark to its correct category, i.e. 'Anime', 'Drama', etc...
        else:
            temp = {}
            temp.setdefault(type_title, Dict['Bookmarks'][type_title]).append(new_bookmark)
            Dict['Bookmarks'][type_title] = temp[type_title]
            Logger('bookmark list after addition\n%s' % Dict['Bookmarks'], kind='Info')

            # Update Dict to include new Item
            Dict.Save()

            # Provide feedback that the Item has been added to bookmarks
            return MessageContainer(header=item_title_decode,
                message='\"%s\" has been added to your bookmarks.' % item_title_decode)
    # the category key does not exist yet so create it and fill with new bookmark
    else:
        Dict['Bookmarks'].update({type_title: [new_bookmark]})
        Logger('bookmark list after addition of new section\n%s' % Dict['Bookmarks'], kind='Info')

        # Update Dict to include new Item
        Dict.Save()

        # Provide feedback that the Item has been added to bookmarks
        return MessageContainer(header=item_title_decode,
            message='\"%s\" has been added to your bookmarks.' % item_title)

####################################################################################################
# Removes item from the bookmarks list using the item as a key

@route(PREFIX + '/removebookmark', item_info=dict)
def RemoveBookmark(item_info):
    # set variables
    item_sys_name = item_info['item_sys_name']
    item_title = item_info['item_title']
    type_title = item_info['type_title']

    # decode string
    item_title_decode = item_title.decode('unicode_escape')

    # index 'Bookmarks' list
    bm = Dict['Bookmarks'][type_title]
    Logger('boomarks = %s' %bm)
    Logger('bookmark lenght = %s' %len(bm))
    for i in xrange(len(bm)):
        # remove item's data from 'Bookmarks' list
        if bm[i][type_title] == item_sys_name:
            if type_title == 'Manga' or not Prefs['cache_covers']:
                bm.pop(i)
            else:
                RemoveCoverImage(bm[i]['cover_file'])
                bm.pop(i)

            break

    # update Dict, and debug log
    Dict.Save()
    Logger('\"%s\" has been removed from Bookmark List' % item_title_decode)
    Logger('bookmark list after removal\n%s' % Dict['Bookmarks'])

    if len(bm) == 0:
        # if the last bookmark was removed then clear it's bookmark section
        Logger('%s bookmarks was the last, so removed %s bookmark section' %(item_title_decode, type_title), force=True)
        return ClearBookmarks(type_title)
    else:
        # Provide feedback that the Item has been removed from the 'Bookmarks' list
        return MessageContainer(header=type_title,
            message='\"%s\" has been removed from your bookmarks.' % item_title_decode)

####################################################################################################
# Remove 'Bookmarks' Section(s) from Dict. Note: This removes all bookmarks in list

@route(PREFIX + '/clearbookmarks')
def ClearBookmarks(type_title):
    if 'All' in type_title:
        if Prefs['cache_covers']:
            for key in Dict['Bookmarks'].keys():
                if not key == 'Manga':
                    for bookmark in Dict['Bookmarks'][key]:
                        RemoveCoverImage(bookmark['cover_file'])

        # delete 'Bookmarks' section from Dict
        del Dict['Bookmarks']
        Logger('Bookmarks section cleared')
    else:
        if not type_title == 'Manga' and Prefs['cache_covers']:
            for bookmark in Dict['Bookmarks'][type_title]:
                RemoveCoverImage(bookmark['cover_file'])

        # delete section 'Anime', 'Manga', 'Cartoon', or 'Drama' from bookmark list
        del Dict['Bookmarks'][type_title]
        Logger('Bookmark section %s cleared' % type_title)
        Logger('bookmarks after deletion\n%s' % Dict['Bookmarks'])

    Dict['Bookmark_Deleted'] = {'bool': True, 'type_title': type_title}
    status = Dict['Bookmark_Deleted']

    # update Dict
    Dict.Save()

    # Provide feedback that the correct 'Bookmarks' section is removed
    #   and send back to Bookmark Main Menu
    return BookmarksMain(title='My Bookmarks', status=status)

####################################################################################################
# Setup logging options based on prefs, indirect because it has no return

@route(PREFIX + '/logger')
def Logger(message, force=False, kind=None):
    if force or Prefs['debug']:
        if kind == 'Debug' or kind == None:
            Log.Debug(message)
        elif kind == 'Info':
            Log.Info(message)
        elif kind == 'Warn':
            Log.Warn(message)
    else:
        pass

####################################################################################################
# Get Plug-in Bundle path

@route(PREFIX + '/bundlepath')
def GetBundlePath():
    path = Core.storage.join_path(
        Core.app_support_path, Core.config.bundles_dir_name, 'KissNetwork.bundle')

    return path

####################################################################################################
# Get image directory, for now it's Contents/Resources

@route(PREFIX + '/cover-imagepath')
def GetCoverImagePath():
    return Core.storage.join_path(GetBundlePath(), 'Contents', 'Resources')

####################################################################################################
# Cache bookmark covers depending on prefs settings

@route(PREFIX + '/cache-bookmark-covers')
def CacheBookmarkCovers():
    if Prefs['cache_covers']:
        Logger('Caching Bookmark covers locally')
        if Dict['Bookmarks']:
            for key in Dict['Bookmarks'].keys():
                if not key == 'Manga':
                    for bm in Dict['Bookmarks'][key]:
                        SaveCoverImage(bm['cover_url'])
    else:
        Logger('Removing Cached Bookmark Covers')
        if Dict['Bookmarks']:
            for key in Dict['Bookmarks'].keys():
                if not key == 'Manga':
                    for bm in Dict['Bookmarks'][key]:
                        RemoveCoverImage(bm['cover_file'])

                    Logger('Finished Removing Cached Bookmark Covers')

####################################################################################################
# Save image to Cover Image Path and return the file name

@route(PREFIX + '/save-cover-image')
def SaveCoverImage(image_url):
    image_file = image_url.rsplit('/')[-1]

    path = Core.storage.join_path(GetCoverImagePath(), image_file)
    Logger('image file path = %s' %path)

    if not Core.storage.file_exists(path):
        r = requests.get(image_url, headers=Test.GetHeadersForURL(image_url), stream=True)
        Logger('status code for image url = %s' %r.status_code)

        if r.status_code == 200:
            with io.open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            Logger('saved image %s in path %s' %(image_file, path))
    else:
        Logger('file %s already exists' %image_file)

    return image_file

####################################################################################################
# Remove Cover Image

@route(PREFIX + '/remove-cover-image')
def RemoveCoverImage(image_file):
    path = Core.storage.join_path(GetCoverImagePath(), image_file)

    if Core.storage.file_exists(path):
        Core.storage.remove(path)
    else:
        pass

####################################################################################################
# Check if resource file exist

@route(PREFIX + '/cover-image-file-exist')
def CoverImageFileExist(image_file):
    if Core.storage.file_exists(Core.storage.join_path(GetCoverImagePath(), image_file)):
        return True
    else:
        return False

####################################################################################################
# auto cache headers

@route(PREFIX + '/auto-cache')
def BackgroundAutoCache():
    if not Dict['First Headers Cached']:
        Logger("Running Background Auto-Cache.", force=True)

        if Core.storage.file_exists(Test.LoadHeaderDict(False)):
            Logger('Header Dictionary already found, writing new Headers to old Dictionary')
            # setup urls for setting headers
            url_list = [ANIME_BASE_URL, ASIAN_BASE_URL, CARTOON_BASE_URL, MANGA_BASE_URL]

            # get headers for each url
            for url in url_list:
                Test.GetHeadersForURL(url)

        else:
            # Header Dictionary not yet setup, so create it and fill in the data
            Test.CreateHeadersDict()

        # check to make sure each section/url has cookies now
        Logger('all cookies =%s' %Test.LoadHeaderDict(setup=True), force=True)

        # Setup the Dict and save
        Dict['First Headers Cached'] = True
        Dict['Headers Auto Cached'] = True
        Dict.Save()
    else:
        Logger('Headers were already cached.  Will cache them independently when needed')
        pass

    return
