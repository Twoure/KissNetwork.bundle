####################################################################################################
#                                                                                                  #
#                               KissNetwork Plex Channel -- v0.03                                  #
#                                                                                                  #
####################################################################################################
# import section(s) not included in Plex Plug-In Framwork
import sys, shutil, io, time

# add custom modules to python path
path = Core.storage.join_path(
    Core.app_support_path, Core.config.bundles_dir_name,
    'KissNetwork.bundle', 'Contents', 'Modules')

if path not in sys.path:
    sys.path.append(path)
    Log.Debug('%s added to sys.path' % path)

# import custom module cfscrape to load url's hosted on cloudflare
import cfscrape, requests

# set global variables
PREFIX = '/video/kissnetwork'
TITLE = 'KissNetwork'
LIST_VIEW_CLIENTS = ['Android', 'iOS']

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
    HTTP.Headers['User-Agent'] = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')

    Dict['First Headers Cached'] = False

    if Dict['Headers Auto Cached']:
        if not Dict['Headers Auto Cached']:
            Log('caching cookies')
            Thread.Create(BackgroundAutoCache)
        else:
            Log('cookies already cached')
    else:
        Dict['Headers Auto Cached'] = False
        Log('caching cookies')
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
            page=1, pname='All', category='All', base_url=url, type_title=title, art=art), title='All'))
    oc.add(DirectoryObject(
        key=Callback(AlphabetList, url=url, title=title, art=art), title='Alphabets'))
    oc.add(DirectoryObject(
        key=Callback(GenreList, url=url, title=title, art=art), title='Genres'))

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
        return ObjectContainer(header=title,
            message='No Bookmarks yet. Get out there and start adding some!!!.', no_cache=True)
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

            Logger(art)
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
            return ObjectContainer(header=title,
                message='At least one source must be selected in Preferences to view Bookmarks',
                no_cache=True)

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
        item_sys_name = bookmark[type_title]
        item_title = bookmark['item_title']
        summary = bookmark['summary']

        if summary:
            summary = summary.decode('unicode_escape')

        page_url = bookmark['page_url']

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

        # gotta send the bookmark somewhere
        oc.add(DirectoryObject(
            key=Callback(ItemPage, item_sys_name=item_sys_name, item_title=item_title, type_title=type_title, page_url=page_url, art=art),
            title=item_title.decode('unicode_escape'), summary=summary, thumb=cover))
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
        return ObjectContainer(header='Error',
                message='Bookmarks list is dirty, add bookmarks to this list or start over',
                no_cache=True)

####################################################################################################
# Creates ABC directory

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
# Creates Genre directory

@route(PREFIX + '/genres')
def GenreList(url, title, art):
    genre_url = url + '/%sList' % title  # setup url for finding current Genre list

    # add exception in case the cookies are being refreshed
    try:
        # formate url response into html for xpath
        html = HTML.ElementFromURL(genre_url, headers=GetHeadersForURL(genre_url))
    except:
        return ObjectContainer(header=title,
            message='Please wait a second or two while the URL Headers are set, then try again',
            no_cache=True)

    oc = ObjectContainer(title2='%s By Genres' % title, art=R(art))

    # For loop to pull out valid Genres
    for genre in html.xpath('//div[@class="barContent"]//a'):
        if "Genre" in genre.get('href'):
            pname = genre.get('href')  # name used internally
            category = genre.text.replace('\n', '').strip()  # name used for title2

            oc.add(DirectoryObject(
                key=Callback(DirectoryList,
                    page=1, pname=pname, category=category, base_url=url, type_title=title, art=art),
                title=category))

    return oc

####################################################################################################
# Creates Country directory for KissAsian

@route(PREFIX + '/countries')
def CountryList(url, title, art):
    country_url = url + '/DramaList'  # setup url for finding current Country list

    try:
        html = HTML.ElementFromURL(country_url, headers=GetHeadersForURL(country_url))
    except:
        return ObjectContainer(header=title,
            message='Please wait a second or two while the URL Headers are set, then try again',
            no_cache=True)

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
        html = HTML.ElementFromURL(item_url, headers=GetHeadersForURL(item_url))
    except:
        return ObjectContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again',
            no_cache=True)

    pages = "Last Page"
    nextpg_node = None

    # determine if 'next page' is used in directory page
    if "Search" in pname:
        # The Search result page returnes a long list with no 'next page' option
        # set url back to base url
        base_url = item_url.rsplit('Search', 1)[0][:-1]
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
                if type_title == 'Manga':
                    category = 'Chapter'
                    thumb = Regex('src=\"([\S].*?)\"').search(title_text).group(1)
                else:
                    category = 'Episode'
                    thumb = None

                summary = Regex('(?s)<p>([\r\n].*)</p>').search(title_text)
                summary = summary.group(1).strip().encode('ascii', 'ignore')
                #item_title = Regex('\">([\S].*?)</a>').search(title_text).group(1)
                item_url_base = m[0].xpath('./a/@href')[0]
                item_sys_name = item_url_base.rsplit('/')[-1].strip().encode('unicode_escape')
                item_url_final = base_url + String.Quote(item_url_base)
                #item_title = item_url_base.rsplit('/')[-1]
                item_title = m[0].xpath('./a/text()')[0].strip()

                Logger('item_title = %s | item_url = %s | item_url_final = %s' %(item_title, item_url, item_url_final))

                if m[1].xpath('./a'):
                    item_title_cleaned = Regex('[^a-zA-Z0-9 \n]').sub('', item_title)
                    latest = m[1].xpath('./a/text()')[0].strip().replace(item_title_cleaned, '')
                    latest = latest.replace('Read Online', '').replace('Watch Online', '').strip()
                    title2 = '%s | Latest %s %s' % (item_title, category, latest)
                else:
                    title2 = '%s | %s Completed' % (item_title, type_title)
        else:
            # if no 'title' section is found then sets values to 'None'
            # ensures the oc.add doesn't have problems
            thumb = None
            summary = None
            item_title = None
            item_sys_name = None

        if item_sys_name and item_title:  # ensure all the items are here before adding
            oc.add(DirectoryObject(
                key=Callback(ItemPage,
                    item_sys_name=item_sys_name, item_title=item_title.encode('unicode_escape'),
                    type_title=type_title, page_url=item_url_final, art=art),
                title=title2, summary=summary, thumb=thumb))

    if nextpg_node:  # if not 'None' then find the next page and create a button
        nextpg = int(Regex("page=(\d+)").search(nextpg_node).group(1))
        Logger('NextPage = %d' % nextpg)
        #base_url = 'http://' + item_url_final.rsplit('/')[2]
        Logger('base url = %s' %base_url)
        oc.add(NextPageObject(
            key=Callback(DirectoryList,
                page=nextpg, pname=pname, category=category, base_url=base_url, type_title=type_title, art=art),
            title='Next Page>>', thumb=R(NEXT_ICON) if not Client.Platform in LIST_VIEW_CLIENTS else None))

    return oc

####################################################################################################
# Creates the Media Page with the Video(s)/Chapter(s) section and a Bookmark option Add/Remove

@route(PREFIX + '/item')
def ItemPage(item_sys_name, item_title, type_title, page_url, art):
    Logger('testing GetHeadersForURL | %s' %GetHeadersForURL(page_url))
    # decode unicode string(s)
    item_title_decode = item_title.decode('unicode_escape')

    # setup new title2 for container
    title2 = '%s | %s' % (type_title, item_title_decode)

    oc = ObjectContainer(title2=title2, art=R(art))

    # page category stings depending on media
    if not 'Manga' in type_title:
        category_thumb = CATEGORY_VIDEO_ICON
        page_category = 'Video(s)'
    else:
        category_thumb = CATEGORY_PICTURE_ICON
        page_category = 'Chapter(s)'

    base_url = 'http://' + page_url.rsplit('/')[2]

    # format item_url for parsing
    Logger('page url = %s | base url = %s' %(page_url, base_url))

    try:
        html = HTML.ElementFromURL(page_url, headers=GetHeadersForURL(page_url))
    except:
        return ObjectContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again',
            no_cache=True)

    # add video(s)/chapter(s) container
    oc.add(DirectoryObject(
        key=Callback(ItemSubPage,
            item_sys_name=item_sys_name, item_title=item_title, type_title=type_title,
            page_url=page_url, page_category=page_category, art=art),
        title=page_category,
        thumb=R(category_thumb),
        summary='List all currently avalible %s for \"%s\"' %
        (page_category.lower(), item_title_decode)))

    # Test if the Dict does have the 'Bookmarks' section
    if Dict['Bookmarks']:
        book_match = False
        if type_title in Dict['Bookmarks']:
            for category in Dict['Bookmarks'][type_title]:
                if item_sys_name == category[type_title]:
                    book_match = True
                    break  # Stop for loop if match found

        # If Item found in 'Bookmarks'
        if book_match:
            # provide a way to remove Item from bookmarks list
            oc.add(DirectoryObject(
                key=Callback(RemoveBookmark,
                    item_sys_name=item_sys_name, item_title=item_title, type_title=type_title),
                title='Remove Bookmark', thumb=R(BOOKMARK_REMOVE_ICON),
                summary = 'Remove \"%s\" from your Bookmarks list.' % item_title_decode))
        # Item not in 'Bookmarks' yet, so lets parse it for adding!
        else:
            cover_url = html.xpath('//head/link[@rel="image_src"]')[0].get('href')
            summary = None
            match = None

            # enumerate array so we can find the Summary text
            for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
                if node.xpath('./span[@class="info"][text()="Summary:"]'):
                    match = int(i)
                    break

            # add 1 to our Summary match to find the Summary text
            # fix string encoding errors before they happen by converting to ascii
            #   and ignoring unknown charaters in summary string
            # wish the site was more consistant with its summary location... ugh
            for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
                if match and match + 1 == i:
                    # sometimes summary is inside a <span>
                    if node.xpath('./span'):
                        summary = node.xpath('./span/text()')[0]
                        break
                    else:
                        summary = node.xpath('./text()')[0].strip()
                        break

            # some Summary text is not in the <p> but in it's own <div> or within a <table>
            summary_div = html.xpath('//div[@id="container"]//div[@class="barContent"]/div/div/text()')
            summary_table = html.xpath('//div[@id="container"]//table//td/text()')
            if not summary and summary_div:
                summary = summary_div[0].strip()
            elif not summary and summary_table:
                summary = summary_table[0].strip()

            if summary:
                summary = summary.encode('unicode_escape')

            Log('summary = %s' %summary)

            # provide a way to add Item to the bookmarks list
            oc.add(DirectoryObject(
                key = Callback(AddBookmark,
                    item_sys_name=item_sys_name, item_title=item_title, type_title=type_title,
                    cover_url=cover_url, summary=summary, page_url=page_url),
                title = 'Add Bookmark', thumb=R(BOOKMARK_ADD_ICON),
                summary = 'Add \"%s\" to your Bookmarks list.' % item_title_decode))
    # No 'Bookmarks' section in Dict yet, so don't look for Item in 'Bookmarks'
    else:
        # Same stuff as above
        cover_url = html.xpath('//head/link[@rel="image_src"]')[0].get('href')
        summary = None
        match = None

        for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
            if node.xpath('./span[@class="info"][text()="Summary:"]'):
                match = int(i)
                break

        for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
            if match and match + 1 == i:
                    if node.xpath('./span'):
                        summary = node.xpath('./span/text()')[0]
                        break
                    else:
                        summary = node.xpath('./text()')[0]
                        break

        summary_div = html.xpath('//div[@id="container"]//div[@class="barContent"]/div/div/text()')
        summary_table = html.xpath('//div[@id="container"]//table//td/text()')
        if not summary and summary_div:
            summary = summary_div[0].strip()
        elif not summary and summary_table:
            summary = summary_table[0].strip()

        if summary:
            summary = summary.encode('unicode_escape')

        Log('summary = %s' %summary)

        # provide a way to add Item to bookmarks list
        oc.add(DirectoryObject(
            key=Callback(AddBookmark,
                item_sys_name=item_sys_name, item_title=item_title, type_title=type_title,
                cover_url=cover_url, summary=summary, page_url=page_url),
            title='Add Bookmark', thumb=R(BOOKMARK_ADD_ICON),
            summary='Add \"%s\" to your Bookmarks list.' % item_title_decode))

    return oc

####################################################################################################
# Create the Item Sub Page with Video or Chapter list

@route(PREFIX + '/itemsubpage')
def ItemSubPage(item_sys_name, item_title, type_title, page_url, page_category, art):
    # decode unicode string(s)
    item_title_decode = item_title.decode('unicode_escape')

    # setup title2 for container
    title2 = '%s | %s | %s' % (type_title, item_title_decode, page_category.lower())

    # remove special charaters from item_title for matching later
    item_title_decode = Regex('[^a-zA-Z0-9 \n\.]').sub('', item_title_decode)

    # remove '(s)' from page_category string for logs
    s_removed_page_category = page_category.rsplit('(')[0]

    oc = ObjectContainer(title2=title2, art=R(art))

    # get base url from url
    base_url = 'http://' + page_url.rsplit('/')[2]
    Logger('item sub page url = %s' %page_url)

    try:
        # setup html for parsing
        html = HTML.ElementFromURL(page_url, headers=GetHeadersForURL(page_url))
    except:
        return ObjectContainer(header=type_title,
            message='Please wait a second or two while the URL Headers are set, then try again',
            no_cache=True)

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
            oc.add(DirectoryObject(
                key=Callback(VideoDetail, title=x[1].encode('unicode_escape'), url=x[0], art=art),
                title='%s | %s' % (x[1], y)))
    else:
        for x, y in map(None, a, b):
            oc.add(PhotoAlbumObject(url=x[0], title='%s | %s' % (x[1], y)))

    return oc

####################################################################################################
# Create Video container
# don't like that I need this, but if not the Service URL will parse all the videos
#   and bog down the server respose time

@route(PREFIX + '/videodetail')
def VideoDetail(title, url, art):
    oc = ObjectContainer(title2=title.decode('unicode_escape'), art=R(art))
    Logger('vido url in video detail section = %s' %url)
    oc.add(VideoClipObject(title=title, url=url, art=R(art)))

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
        # change kissasian urls to 'Drama' for type title
        if type_title == 'Asian':
            type_title = 'Drama'
            art = ASIAN_ART
            thumb = ASIAN_ICON
            prefs_name = 'kissasian'
        else:
            art = '%s_ART' % type_title.upper()
            thumb = 'icon-%s.png' % type_title.lower()
            prefs_name = 'kiss%s' %type_title.lower()

        if Prefs[prefs_name]:
            Logger('Search url=%s' % search_url_filled)
            Logger('type title = %s' %type_title)

            html = HTML.ElementFromURL(search_url_filled, headers=GetHeadersForURL(search_url))
            if html.xpath('//table[@class="listing"]'):
                oc.add(DirectoryObject(
                    key=Callback(SearchPage, type_title=type_title, search_url=search_url_filled, art=art),
                    title=type_title, thumb=R(thumb)))

    if len(oc) > 0:
        return oc
    else:
        return ObjectContainer(header='Search',
            message=
                """
                There are no search results for \"%s\". Try being less specific or make sure
                at least one source is selected in the Preferences.
                """ %query,
            no_cache=True)

####################################################################################################
# Retrun searches for each kiss() page
# The results can return the Item itself via a url redirect.

@route(PREFIX + '/searchpage')
def SearchPage(type_title, search_url, art):
    # Check for "exact" matches and send them to ItemPage
    # If normal seach result then send to DirectoryList

    try:
        html = HTML.ElementFromURL(search_url, headers=GetHeadersForURL(search_url))
    except:
        return ObjectContainer(header=type_title + ' Search',
            message='Please wait a second or two while the URL Headers are set, then try again',
            no_cache=True)

    # Check for results if none then give a pop up window saying so
    if html.xpath('//table[@class="listing"]'):
        # Test for "exact" match, if True then send to 'ItemPage'
        node = html.xpath('//div[@id="headnav"]/script/text()')[0]
        search_match = Regex('var\ path\ =\ (\'Search\')').search(node)
        if not search_match:
            # Send url to 'ItemPage'
            base_url = 'http://' + search_url.rsplit('/')[2]
            node = html.xpath('//div[@class="barContent"]/div/a')[0]
            item_url = base_url + '/' + type_title + '/' + String.Quote(node.get('href').rsplit('/')[-1].strip())
            item_sys_name = node.get('href').rsplit('/')[-1].encode('unicode_escape')
            item_title = node.text.encode('unicode_escape')
            Logger('\nitem_title=%s\nitem=%s\ntype_title=%s\nbase_url=%s\nitem_url=%s'
                % (item_title, item_sys_name, type_title, base_url, item_url))

            return ItemPage(item_sys_name=item_sys_name, item_title=item_title, type_title=type_title, page_url=item_url, art=art)
        else:
            # Send results to 'DirectoryList'
            query = search_url.rsplit('=')[-1]
            return DirectoryList(1, 'Search', query, search_url, type_title, art)
    # No results found :( keep trying
    else:
        Logger('Search returned no results.')
        query = search_url.rsplit('=')[-1]
        return ObjectContainer(header='Search',
            message=
                'There are no search results for \"%s\" in \"%s\" Category.\r\nTry being less specific.'
                %(query, type_title))

####################################################################################################
# Adds Item to the bookmarks list

@route(PREFIX + '/addbookmark')
def AddBookmark(item_sys_name, item_title, type_title, cover_url, summary, page_url):
    item_title_decode = item_title.decode('unicode_escape')
    Logger('item = %s' %item_sys_name)

    # setup new bookmark json data to add to Dict
    # Manga cover urls are accessible so no need to store images locally
    if type_title == 'Manga':
        new_bookmark = {
            type_title: item_sys_name, 'item_title': item_title,
            'cover_url': cover_url, 'summary': summary, 'page_url': page_url}
    # Need to store covers locally as files
    else:
        if Prefs['cache_covers']:
            image_file = SaveCoverImage(cover_url)
        else:
            image_file = cover_url.rsplit('/')[-1]

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
        return ObjectContainer(header=item_title_decode,
            message='\"%s\" has been added to your bookmarks.' % item_title_decode, no_cache = True)
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
            return ObjectContainer(header=item_title_decode,
                message='\"%s\" is already in your bookarks.' % item_title_decode, no_cache=True)
        # append new bookmark to its correct category, i.e. 'Anime', 'Drama', etc...
        else:
            temp = {}
            temp.setdefault(type_title, Dict['Bookmarks'][type_title]).append(new_bookmark)
            Dict['Bookmarks'][type_title] = temp[type_title]
            Logger('bookmark list after addition\n%s' % Dict['Bookmarks'])

            # Update Dict to include new Item
            Dict.Save()

            # Provide feedback that the Item has been added to bookmarks
            return ObjectContainer(header=item_title_decode,
                message='\"%s\" has been added to your bookmarks.' % item_title_decode, no_cache=True)
    # the category key does not exist yet so create it and fill with new bookmark
    else:
        Dict['Bookmarks'].update({type_title: [new_bookmark]})
        Logger('bookmark list after addition of new section\n%s' % Dict['Bookmarks'])

        # Update Dict to include new Item
        Dict.Save()

        # Provide feedback that the Item has been added to bookmarks
        return ObjectContainer(header=item_title_decode,
            message='\"%s\" has been added to your bookmarks.' % item_title, no_cache=True)

####################################################################################################
# Removes item from the bookmarks list using the item as a key

@route(PREFIX + '/removebookmark')
def RemoveBookmark(item_sys_name, item_title, type_title):
    item_title_decode = item_title.decode('unicode_escape')
    # index 'Bookmarks' list
    bm = Dict['Bookmarks'][type_title]
    Log('boomarks = %s' %bm)
    Log('bookmark lenght = %s' %len(bm))
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
        return ObjectContainer(header=type_title,
            message='\"%s\" has been removed from your bookmarks.' % item_title_decode, no_cache=True)

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
def Logger(message, force=False):
    if force or Prefs['debug']:
        Log.Debug(message)
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
# Save image to Cover Image Path and return the file name

@route(PREFIX + '/save-cover-image')
def SaveCoverImage(image_url):
    image_file = image_url.rsplit('/')[-1]
    type_title = GetTypeTitle(image_url)

    path = Core.storage.join_path(GetCoverImagePath(), image_file)
    Logger('image file path = %s' %path)

    if not Core.storage.file_exists(path):
        r = requests.get(image_url, headers=Dict['Cookies'][type_title], stream=True)
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
# Get type title from url

@route(PREFIX + 'get-type-title')
def GetTypeTitle(url):
    type_title = url.rsplit('/')[2].rsplit('kiss')[1].rsplit('.')[0].title()
    # correct title for Dict
    if type_title == 'Asian':
        type_title = 'Drama'

    return type_title

####################################################################################################
# Inital setup of Cookies Dict

@route(PREFIX + '/create-cookies-dict')
def CreateCookiesDict():
    Logger('Cookies dictionary not yet created. Creating new Cookies Dict and filling in data')
    # set initial Dict up for Cookies
    # set cookie for first url, so we can update the Dict later
    cookie = cfscrape.get_cookie_string(
        url=ANIME_BASE_URL, user_agent=HTTP.Headers['User-Agent'])
    Dict['Cookies'] = {
        'Anime': {'cookie': cookie[0], 'user-agent': cookie[1], 'date': Datetime.Now()}}

    Logger('cookies for Anime = %s' %Dict['Cookies']['Anime']['cookie'])

    url_list = [
        ('Drama', ASIAN_BASE_URL), ('Cartoon', CARTOON_BASE_URL), ('Manga', MANGA_BASE_URL)]
    # Now get cookies for the other urls and save to Dict for future use.
    for item in url_list:
        cookie = cfscrape.get_cookie_string(url=item[1], user_agent=HTTP.Headers['User-Agent'])
        Dict['Cookies'].update(
            {item[0]: {'cookie': cookie[0], 'user-agent': cookie[1], 'date': Datetime.Now()}})

        Logger('cookies for %s = %s' %(item[0], Dict['Cookies'][item[0]]['cookie']))

    # Save changes to Dict
    Dict.Save()

    return

####################################################################################################
# Set headers for url.  Return headers from Dict.
# If cookies have expired then get new ones.

@route(PREFIX + '/get-headers')
def GetHeadersForURL(url):

    # get base url for headers
    base_url = 'http://' + url.rsplit('/')[2]
    # get title for headers
    type_title = GetTypeTitle(url)
    # get current datetime
    current_datetime = Datetime.Now()
    # cookie time constants for each site.
    time_constants = {
        'Anime': Datetime.Delta(days=7, hours=1), 'Cartoon': Datetime.Delta(days=16, hours=1),
        'Drama': Datetime.Delta(hours=1, minutes=30), 'Manga': Datetime.Delta(days=365)}

    Logger('current datetime = %s' %current_datetime)

    # check if cookies fiel exist in Dict
    # if so then update, otherwise create the Dict['Cookies'] section
    if Dict['Cookies']:
        cachetime = Dict['Cookies'][type_title]['date']
        deltatime = current_datetime - cachetime
        Logger('delta time = %s' %str(deltatime))
        if deltatime >= time_constants[type_title]:
            Logger('Time to update %s cookies.' %type_title)

            cookie_string = cfscrape.get_cookie_string(
                url=base_url, user_agent=HTTP.Headers['User-Agent'])
            Dict['Cookies'].update(
                {type_title: {
                    'cookie': cookie_string[0], 'user-agent': cookie_string[1],
                    'date': Datetime.Now()}})

            Logger('updated %s cookies to %s' %(type_title, Dict['Cookies'][type_title]))

            # update Dict
            Dict.Save()
        else:
            Logger('Time left until %s cookies need to be udated = %s' %(type_title, str(time_constants[type_title] - deltatime)))
            pass
    else:
        # Cookies Dict not yet setup, so create it and fill in the data
        CreateCookiesDict()

    # setup headers to return, do not want date in header field
    temp_headers = {'cookie': Dict['Cookies'][type_title]['cookie'],
        'user-agent': Dict['Cookies'][type_title]['user-agent']}

    return temp_headers

####################################################################################################
# auto cache headers

@route(PREFIX + '/auto-cache')
def BackgroundAutoCache():
    if not Dict['First Headers Cached']:
        Logger("Running Background Auto-Cache.", force=True)

        if Dict['Cookies']:
            Logger('Cookies dictionary already found, writing new cookies to old Dict')
            # setup urls for setting cookies
            url_list = [ANIME_BASE_URL, ASIAN_BASE_URL, CARTOON_BASE_URL, MANGA_BASE_URL]

            # get cookies for each url
            for url in url_list:
                GetHeadersForURL(url)

        else:
            # Cookies Dict not yet setup, so create it and fill in the data
            CreateCookiesDict()

        # check to make sure each section/url has cookies now
        Logger('all cookies =%s' %(Dict['Cookies']), force=True)

        # Setup the Dict and save
        Dict['First Headers Cached'] = True
        Dict['Headers Auto Cached'] = True
        Dict.Save()
    else:
        Logger('Headers were already cached.  Will cache them independently when needed')
        pass

    return
