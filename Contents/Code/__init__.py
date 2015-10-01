####################################################################################################
#                                                                                                  #
#                               KissNetwork Plex Channel -- v0.01                                  #
#                                                                                                  #
####################################################################################################
# import section(s) not included in Plex Plug-In Framwork
import sys, shutil, io

# add custom modules to python path
path = Core.storage.join_path(
    Core.app_support_path, Core.config.bundles_dir_name,
    'KissNetwork.bundle', 'Contents', 'Modules')

if path not in sys.path:
    sys.path.append(path)
    Log.Debug('%s added to sys.path' % path)

# import custom module cfscrape to load url's hosted on cloudflare
import cfscrape

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

#    HTTP.CacheTime = CACHE_1DAY  # 1 day cache time  # once done editing will change back
    HTTP.CacheTime = 300  # 0 sec cache time, 300 sec = 5 mins

####################################################################################################
# Create the main menu

@handler(PREFIX, TITLE, thumb='icon-default.png', art='art-main.png')
def MainMenu():
    oc = ObjectContainer(title2=TITLE)

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

    oc.add(DirectoryObject(
        key=Callback(KissAnime, url=ANIME_BASE_URL, title='Anime', art=ANIME_ART),
        title='Anime', thumb=R(anime_thumb)))
    oc.add(DirectoryObject(
        key=Callback(KissCartoon, url=CARTOON_BASE_URL, title='Cartoon', art=CARTOON_ART),
        title='Cartoons', thumb=R(cartoon_thumb)))
    oc.add(DirectoryObject(
        key=Callback(KissAsian, url=ASIAN_BASE_URL, title='Drama', art=ASIAN_ART),
        title='Drama', thumb=R(drama_thumb)))
    oc.add(DirectoryObject(
        key=Callback(KissManga, url=MANGA_BASE_URL, title='Manga', art=MANGA_ART),
        title='Manga', thumb=R(manga_thumb)))
    oc.add(DirectoryObject(
        key=Callback(BookmarksMain, title='My Bookmarks'), title='My Bookmarks', thumb=R(bookmark_thumb)))
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
            page=1, pname='All', category='All', url=url, title=title, art=art), title='All'))
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
            page=1, pname='All', category='All', url=url, title=title, art=art), title='All'))
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
            page=1, pname='All', category='All', url=url, title=title, art=art), title='All'))
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
            page=1, pname='All', category='All', url=url, title=title, art=art), title='All'))
    oc.add(DirectoryObject(
        key=Callback(AlphabetList, url=url, title=title, art=art), title='Alphabets'))
    oc.add(DirectoryObject(
        key=Callback(GenreList, url=url, title=title, art=art), title='Genres'))

    return oc

####################################################################################################
# Set the sorting options for displaying all Manga lists

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
    if not Prefs['cache_covers']:
        if Dict['Bookmarks']:
            for key in Dict['Bookmarks'].keys():
                if not key == 'Manga':
                    for bm in Dict['Bookmarks'][key]:
                        RemoveCoverImage(bm['cover_file'])
    else:
        if Dict['Bookmarks']:
            for key in Dict['Bookmarks'].keys():
                if not key == 'Manga':
                    for bm in Dict['Bookmarks'][key]:
                        SaveCoverImage(bm['cover_url'])

    # Update the Dict to latest prefs
    Dict.Save()

####################################################################################################
# Crates Bookmark Menu

@route(PREFIX + '/bookmarks')
def BookmarksMain(title):
    oc = ObjectContainer(title2=title)

    # check for 'Bookmarks' section in Dict
    if not Dict['Bookmarks']:
        # if no 'Bookmarks' section the return pop up
        return ObjectContainer(header=title,
            message='No Bookmarks yet. Get out there and start adding some!!!.', no_cache = True)
    # create boomark directory based on category
    else:
        for key in sorted(Dict['Bookmarks'].keys()):
            if not key == 'Drama':
                art = 'art-%s.png' % key.lower()
                thumb = 'icon-%s.png' % key.lower()
            else:
                art = 'art-drama.png'
                thumb = 'icon-drama.png'
            Logger(art)
            # Create sub Categories for Anime, Cartoon, Drama, and Manga
            oc.add(DirectoryObject(
                key=Callback(BookmarksSub, key=key, art=art),
                title=key, thumb=R(thumb), summary='Display %s Bookmarks' % key))

        # add a way to clear the entire bookmarks list, i.e. start fresh
        oc.add(DirectoryObject(
            key=Callback(ClearBookmarks, title='All'),
            title='Clear All Bookmarks',
            thumb=R(BOOKMARK_CLEAR_ICON),
            summary='CAUTION! This will clear your entire bookmark list!'))

        return oc

####################################################################################################
# Loads bookmarked items from Dict.

@route(PREFIX + '/bookmarkssub')
def BookmarksSub(key, art):
    oc = ObjectContainer(title2='My Bookmarks | %s' % key, art=R(art))
    Logger('category %s' %key)

    # Fill in DirectoryObject information from the bookmark list
    for bookmark in sorted(Dict['Bookmarks'][key]):
        item = bookmark[key]
        item_title = bookmark['title']
        summary = bookmark['summary']
        url = bookmark['base_url']

        if key == 'Manga':
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
            key=Callback(ItemPage, item=item, item_title=item_title, title=key, url=url, art=art),
            title=item_title.decode('unicode_escape'), summary=summary.decode('unicode_escape'),
            thumb=cover))

    if Client.Platform in LIST_VIEW_CLIENTS and not cover:
        bm_clr_icon = None
    else:
        bm_clr_icon = R(BOOKMARK_CLEAR_ICON)

    # add a way to clear this bookmark section and start fresh
    oc.add(DirectoryObject(
        key=Callback(ClearBookmarks, title=key),
        title='Clear All \"%s\" Bookmarks' % key,
        thumb=bm_clr_icon,
        summary='CAUTION! This will clear your entire \"%s\" bookmark section!' % key))

    return oc

####################################################################################################
# Creates ABC directory

@route(PREFIX + '/alphabets')
def AlphabetList(url, title, art):
    oc = ObjectContainer(title2='%s By #, A-Z' % title, art=R(art))

    # Manually create the '#' Directory
    oc.add(DirectoryObject(
        key=Callback(DirectoryList,
            page=1, pname='0', category='#', url=url, title=title, art=art),
        title='#'))

    # Create a list of Directories from A to Z
    for pname in map(chr, range(ord('A'), ord('Z')+1)):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList,
                page=1, pname=pname.lower(), category=pname, url=url, title=title, art=art),
            title=pname))

    Logger('Built #, A-Z... Directories')

    return oc

####################################################################################################
# Creates Genre directory

@route(PREFIX + '/genres')
def GenreList(url, title, art):
    genre_url = url + '/%sList' % title
    html = ElementFromURL(genre_url)

    oc = ObjectContainer(title2='%s By Genres' % title, art=R(art))

    # For loop to pull out valid Genres
    for genre in html.xpath('//div[@class="barContent"]//a'):
        if "Genre" in genre.get('href'):
            pname = genre.get('href')  # name used internally
            category = genre.text.replace('\n', '').strip()  # name used for title2

            oc.add(DirectoryObject(
                key=Callback(DirectoryList,
                    page=1, pname=pname, category=category, url=url, title=title, art=art),
                title=category))

    return oc

####################################################################################################
# Creates Country directory for KissAsian

@route(PREFIX + '/countries')
def CountryList(url, title, art):
    country_url = url + '/DramaList'  # set url for populating genres array
    html = ElementFromURL(country_url)  # formate url response into html for xpath

    oc = ObjectContainer(title2='Drama By Country', art=R(art))

    # For loop to pull out valid Genres
    for country in html.xpath('//div[@class="barContent"]//a'):
        if "Country" in country.get('href'):
            pname = country.get('href')  # name used internally
            category = country.text.replace('\n', '').strip()  # name used for title2

            oc.add(DirectoryObject(
                key=Callback(DirectoryList,
                    page=1, pname=pname, category=category, url=url, title=title, art=art),
                title=category))

    return oc

####################################################################################################
# GenreList, AlphabetList, and Search are sent here
# Pulls out Items name and creates directories for them
# Plan to add section that detects if Genre is empty

@route(PREFIX + '/directory')
def DirectoryList(page, pname, category, url, title, art):
    # Define url based on genre, abc, or search
    if "Search" in pname:
        item_url = url
        Logger('Searching for \"%s\"' % category)
        pass
    # Sort order 'A-Z'
    elif Dict['s_opt'] == None:
        if "Genre" in pname or "Country" in pname:
            # Genre Specific
            item_url = url + '%s?page=%s' % (pname, page)
        elif "All" in pname:
            item_url = url + '/%sList?page=%s' % (title, page)
        else:
            # No Genre
            item_url = url + '/%sList?c=%s&page=%s' % (title, pname, page)
    # Sort order for all options except 'A-Z'
    elif "Genre" in pname or "Country" in pname:
        # Genre Specific with Prefs
        item_url = url + '%s%s?page=%s' % (pname, Dict['s_opt'], page)
    elif "All" in pname:
        item_url = url + '/%sList%s?page=%s' % (title, Dict['s_opt'], page)
    else:
        # No Genre with Prefs
        item_url = url + '/%sList%s?c=%s&page=%s' % (title, Dict['s_opt'], pname, page)

    Logger('Sorting Option = %s' % Dict['s_opt'])  # Log Pref being used
    Logger('Category= %s | URL= %s' % (pname, item_url))

    # format url and set variables
    html = ElementFromURL(item_url)
    pages = "Last Page"
    nextpg_node = None

    # determine if 'next page' is used in directory page
    if "Search" in pname:
        # The Search result page returnes a long list with no 'next page' option
        # set url back to base url
        url = item_url.rsplit('Search', 1)[0][:-1]
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
        main_title = '%s | %s | Page %s of %s' % (title, str(category), str(page), str(total_pages))
    elif "Search" in pname:
        # set title2 for search page
        main_title = 'Search for: %s in %s' % (str(category), title)
    else:
        # set title2 for last page
        main_title = '%s | %s | Page %s, Last Page' % (title, str(category), str(page))

    oc = ObjectContainer(title2=main_title, art=R(art))

    # parse url for each Manga and pull out its title, summary, and cover image
    # took some time to figure out how to get the javascript info
    for item in html.xpath('//table[@class="listing"]/tr'):
        m = item.xpath('./td')
        if m:  # skip empty matches
            if m[0].get('title'):  # pull out the first 'td' since there are two
                title_text = m[0].get('title')  # convert section to string for searching
                # search for cover url and summary string
                if title == 'Manga':
                    thumb = Regex('src=\"([\S].*?)\"').search(title_text).group(1)
                    category = 'Chapter'
                else:
                    thumb = None
                    category = 'Episode'

                summary = Regex('(?s)<p>([\r\n].*)</p>').search(title_text)
                summary = summary.group(1).strip().encode('ascii', 'ignore')
                item_title = Regex('\">([\S].*?)</a>').search(title_text).group(1)

                Logger('item_title = %s' % item_title)

                if m[1].xpath('./a'):
                    item_title_cleaned = Regex('[^a-zA-Z0-9 \n]').sub('', item_title)
                    latest = m[1].xpath('./a/text()')[0].strip().replace(item_title_cleaned, '')
                    latest = latest.replace('Read Online', '').replace('Watch Online', '').strip()
                    title2 = '%s | Latest %s %s' % (item_title, category, latest)
                else:
                    title2 = '%s | %s Completed' % (item_title, title)

                name = Regex('href=\"/(?:Anime|Drama|Cartoon|Manga)/([\S].*?)\"').search(title_text).group(1)
        else:
            # if no 'title' section is found then sets values to 'None'
            # ensures the oc.add doesn't have problems
            thumb = None
            summary = None
            item_title = None
            name = None

        if name and item_title:  # ensure all the items are here before adding
            oc.add(DirectoryObject(
                key=Callback(ItemPage,
                    item=name, item_title=item_title.encode('unicode_escape'),
                    title=title, url=url, art=art),
                title=title2, summary=summary, thumb=thumb))

    if nextpg_node:  # if not 'None' then find the next page and create a button
        nextpg = int(Regex("page=(\d+)").search(nextpg_node).group(1))
        Logger('NextPage = %d' % nextpg)
        oc.add(NextPageObject(
            key=Callback(DirectoryList,
                page=nextpg, pname=pname, category=category, url=url, title=title, art=art),
            title='Next Page>>', thumb=R(NEXT_ICON) if not Client.Platform in LIST_VIEW_CLIENTS else None))

    return oc

####################################################################################################
# Creates the Media Page with the Video(s)/Chapter(s) section and a Bookmark option Add/Remove

@route(PREFIX + '/item')
def ItemPage(item, item_title, title, url, art):
    # decode item_title if need be
    item_title_decode = item_title.decode('unicode_escape')
    # setup new title2 for container
    title2 = '%s | %s' % (title, item_title_decode)
    oc = ObjectContainer(title2=title2, art=R(art))

    # page category stings depending on media
    if not 'Manga' in title:
        category_thumb = CATEGORY_VIDEO_ICON
        page_category = 'Video(s)'
    else:
        category_thumb = CATEGORY_PICTURE_ICON
        page_category = 'Chapter(s)'

    # format item_url for parsing
    item_url = url + '/%s/' % title + item
    html = ElementFromURL(item_url)
    Logger('item_url = %s' % item_url)

    # add video(s)/chapter(s) container
    oc.add(DirectoryObject(
        key=Callback(ItemSubPage,
            item=item, item_title=item_title, title=title,
            url=url, page_category=page_category, art=art),
        title=page_category,
        thumb=R(category_thumb),
        summary='List all currently avalible %s for \"%s\"' %
        (page_category.lower(), item_title_decode)))

    # Test if the Dict does have the 'Bookmarks' section
    if Dict['Bookmarks']:
        book_match = False
        if title in Dict['Bookmarks']:
            for category in Dict['Bookmarks'][title]:
                if item in category[title]:
                    book_match = True
                    break  # Stop for loop if match found

        # If Item found in 'Bookmarks'
        if book_match:
            # provide a way to remove Item from bookmarks list
            oc.add(DirectoryObject(
                key=Callback(RemoveBookmark,
                    item=item, item_title=item_title, title=title),
                title='Remove Bookmark', thumb=R(BOOKMARK_REMOVE_ICON),
                summary = 'Remove \"%s\" from your Bookmarks list.' % title))
        # Item not in 'Bookmarks' yet, so lets parse it for adding!
        else:
            cover = html.xpath('//head/link[@rel="image_src"]')[0].get('href')
            summary = None

            # enumerate array so we can find the Summary text
            for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
                if "Summary:" in node.xpath('./span[@class="info"]/text()'):
                    match = int(i)
                    break

            # add 1 to our Summary match to find the Summary text
            # fix string encoding errors before they happen by converting to ascii
            #   and ignoring unknown charaters in summary string
            # wish the site was more consistant with its summary location... ugh
            for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
                if match + 1 == i:
                    # sometimes summary is inside a <span>
                    if node.xpath('./span'):
                        summary = node.xpath('./span/text()')[0].encode('unicode_escape')
                        break
                    else:
                        summary = node.xpath('./text()')[0].strip().encode('unicode_escape')
                        break

            # some Summary text is not in the <p> but in it's own <div>
            if not summary:
                summary = html.xpath(
                    '//div[@id="container"]//div[@class="barContent"]/div/div/text()'
                    )[0].strip().encode('unicode_escape')
            # in event summary isn't found set to 'None'
            else:
                summary = summary

            # provide a way to add Item to the bookmarks list
            oc.add(DirectoryObject(
                key = Callback(AddBookmark,
                    item=item, item_title=item_title, title=title,
                    cover=cover, summary=summary, url=url),
                title = 'Add Bookmark', thumb=R(BOOKMARK_ADD_ICON),
                summary = 'Add \"%s\" to your Bookmarks list.' % item_title_decode))
    # No 'Bookmarks' section in Dict yet, so don't look for Item in 'Bookmarks'
    else:
        # Same stuff as above
        cover = html.xpath('//head/link[@rel="image_src"]')[0].get('href')
        summary = None

        for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
            if "Summary:" in node.xpath('./span[@class="info"]/text()'):
                match = int(i)
                break

        for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
            if match + 1 == i:
                    if node.xpath('./span'):
                        summary = node.xpath('./span/text()')[0].encode('unicode_escape')
                        break
                    else:
                        summary = node.xpath('./text()')[0].encode('unicode_escape')
                        break

        if not summary:
            summary = html.xpath(
                '//div[@id="container"]//div[@class="barContent"]/div/div/text()'
                )[0].strip().encode('unicode_escape')
        else:
            summary = summary

        # provide a way to add Item to bookmarks list
        oc.add(DirectoryObject(
            key=Callback(AddBookmark,
                item=item, item_title=item_title, title=title,
                cover=cover, summary=summary, url=url),
            title='Add Bookmark', thumb=R(BOOKMARK_ADD_ICON),
            summary='Add \"%s\" to your Bookmarks list.' % item_title_decode))

    return oc

####################################################################################################
# Create the Item Sub Page with Video or Chapter list

@route(PREFIX + '/itemsubpage')
def ItemSubPage(item, item_title, title, url, page_category, art):
    # decode item_title
    item_title_decode = item_title.decode('unicode_escape')
    # setup title2 for container
    title2 = '%s | %s | %s' % (title, item_title_decode, page_category.lower())
    # remove special charaters from item_title for matching later
    item_title_decode = Regex('[^a-zA-Z0-9 \n\.]').sub('', item_title_decode)
    # remove '(s)' from page_category string for logs
    s_removed_page_category = page_category.rsplit('(')[0]

    oc = ObjectContainer(title2=title2, art=R(art))

    # setup url for parsing
    sub_url = url + '/%s/' % title + item
    Logger(sub_url)
    html = ElementFromURL(sub_url)

    # parse html for media url, title and date added
    a = []
    b = []

    for media in html.xpath('//table[@class="listing"]/tr/td'):
        if media.xpath('./a'):
            node = media.xpath('./a')

            # url for Video/Chapter
            media_page_url = url + node[0].get('href')
            Logger('%s Page URL = %s' % (s_removed_page_category, media_page_url))

            # title for Video/Chapter, cleaned
            raw_title = Regex('[^a-zA-Z0-9 \n\.]').sub('', node[0].text).replace(item_title_decode, '')
            if not 'Manga' in title:
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
    if not 'Manga' in title:
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
    oc.add(VideoClipObject(title=title, url=url.encode('unicode_escape')))

    return oc

####################################################################################################
# Set up Search for kiss(anime, asian, cartoon, manga)

@route(PREFIX + '/search')
def Search(query=''):
    # set defaults
    title2 = 'Search for \"%s\" in...' % query

    oc = ObjectContainer(title2=title2)
    # create list of search URL's
    all_search_urls = [ANIME_SEARCH_URL, ASIAN_SEARCH_URL, CARTOON_SEARCH_URL, MANGA_SEARCH_URL]

    # format each search url and send to 'SearchPage'
    # can't check each url here, would take too long since behind cloudflare and timeout the server
    for search_url in all_search_urls:
        search_url_filled = search_url % String.Quote(query, usePlus=True)
        base_url = search_url_filled.rsplit('Search', 1)[0][:-1]
        title = base_url.rsplit('/', 2)[2].rsplit('kiss', 1)[1].rsplit('.', 1)[0].title()
        # change kissasian urls to 'Drama' for title
        if title == 'Asian':
            title = 'Drama'
            art = ASIAN_ART
            thumb = ASIAN_ICON
        else:
            art = '%s_ART' % title.upper()
            thumb = 'icon-%s.png' % title.lower()
        Logger('Search url=%s' % search_url_filled)

        oc.add(DirectoryObject(
            key=Callback(SearchPage, title=title, search_url=search_url_filled, art=art),
            title=title, thumb=R(thumb)))

    return oc

####################################################################################################
# Retrun searches for each kiss() page
# The results can return the Item itself via a url redirect.

@route(PREFIX + '/searchpage')
def SearchPage(title, search_url, art):
    # Check for "exact" matches and send them to ItemPage
    # If normal seach result then send to DirectoryList

    html = ElementFromURL(search_url)

    # Check for results if none then give a pop up window saying so
    if html.xpath('//table[@class="listing"]'):
        # Test for "exact" match, if True then send to 'ItemPage'
        node = html.xpath('//div[@id="headnav"]/script/text()')[0]
        search_match = Regex('var\ path\ =\ (\'Search\')').search(node)
        if not search_match:
            # Send url to 'ItemPage'
            base_url = search_url.rsplit('Search', 1)[0][:-1]
            node = html.xpath('//div[@class="barContent"]/div/a')[0]
            item = node.get('href').rsplit('/')[-1]
            item_title = node.text
            Logger('\nitem_title=%s\nitem=%s\ntitle=%s\nurl=%s' % (item_title, item, title, base_url))

            return ItemPage(
                item=item, item_title=item_title.encode('unicode_escape'),
                title=title, url=base_url, art=art)
        else:
            # Send results to 'DirectoryList'
            query = search_url.rsplit('=')[-1]
            return DirectoryList(1, 'Search', query, search_url, title, art)
    # No results found :( keep trying
    else:
        Logger('Search returned no results.')
        query = search_url.rsplit('=')[-1]
        return ObjectContainer(header='Search',
            message='There are no search results for \"%s\" in \"%s\" Category.\r\nTry being less specific.' %(query, title))

####################################################################################################
# Adds Item to the bookmarks list

@route(PREFIX + '/addbookmark')
def AddBookmark(item, item_title, title, cover, summary, url):
    item_title_decode = item_title.decode('unicode_escape')
    Logger(item)

    # setup new bookmark json data to add to Dict
    # Manga cover urls are accessible so no need to store images locally
    if title == 'Manga':
        new_bookmark = {
            title: item, 'title': item_title,
            'cover_url': cover, 'summary': summary, 'base_url': url}
    # Need to store covers locally as files
    else:
        if Prefs['cache_covers']:
            image_file = SaveCoverImage(cover)
        else:
            image_file = cover.rsplit('/')[-1]

        new_bookmark = {
            title: item, 'title': item_title, 'cover_file': image_file,
            'cover_url': cover, 'summary': summary, 'base_url': url}

    Logger('new bookmark to add\n%s' % new_bookmark)

    # Test if the Dict has the 'Bookmarks' section yet
    if not Dict['Bookmarks']:
        # Create new 'Bookmarks' section and fill with the first bookmark
        Dict['Bookmarks'] = {title: [new_bookmark]}
        Logger('Inital bookmark list created\n%s' % Dict['Bookmarks'])

        # Update Dict to include new 'Bookmarks' section
        Dict.Save()

        # Provide feedback that the Item has been added to bookmarks
        return ObjectContainer(header=item_title_decode,
            message='\"%s\" has been added to your bookmarks.' % item_title_decode, no_cache = True)
    # check if the category key 'Anime', 'Manga', 'Cartoon', or 'Drama' exist
    # if so then append new bookmark to one of those categories
    elif title in Dict['Bookmarks'].keys():
        # fail safe for when clients are out of sync and it trys to add
        # the bookmark in duplicate
        for bookmark in Dict['Bookmarks'][title]:
            if not bookmark[title] == new_bookmark[title]:
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
            temp.setdefault(title, Dict['Bookmarks'][title]).append(new_bookmark)
            Dict['Bookmarks'][title] = temp[title]
            Logger('bookmark list after addition\n%s' % Dict['Bookmarks'])

            # Update Dict to include new Item
            Dict.Save()

            # Provide feedback that the Item has been added to bookmarks
            return ObjectContainer(header=item_title_decode,
                message='\"%s\" has been added to your bookmarks.' % item_title_decode, no_cache=True)
    # the category key does not exist yet so create it and fill with new bookmark
    else:
        Dict['Bookmarks'].update({title: [new_bookmark]})
        Logger('bookmark list after addition of new section\n%s' % Dict['Bookmarks'])

        # Update Dict to include new Manga
        Dict.Save()

        # Provide feedback that the Manga has been added to bookmarks
        return ObjectContainer(header=item_title_decode,
            message='\"%s\" has been added to your bookmarks.' % item_title, no_cache=True)

####################################################################################################
# Removes item from the bookmarks list using the item as a key

@route(PREFIX + '/removebookmark')
def RemoveBookmark(item, item_title, title):
    item_title_decode = item_title.decode('unicode_escape')
    # index 'Bookmarks' list
    bm = Dict['Bookmarks'][title]
    for i in xrange(len(bm)):
        # remove item's data from 'Bookmarks' list
        if bm[i][title] == item:
            if item == 'Manga' or not Prefs['cache_covers']:
                bm.pop(i)
            else:
                RemoveCoverImage(bm[i]['cover_file'])
                bm.pop(i)
            break

    # update Dict, and debug log
    Dict.Save()
    Logger('\"%s\" has been removed from Bookmark List' % item_title)
    Logger('bookmark list after removal\n%s' % Dict['Bookmarks'])

    # Provide feedback that the Item has been removed from the 'Bookmarks' list
    return ObjectContainer(header=title,
        message='\"%s\" has been removed from your bookmarks.' % item_title_decode, no_cache=True)

####################################################################################################
# Remove 'Bookmarks' Section(s) from Dict. Note: This removes all bookmarks in list

@route(PREFIX + '/clearbookmarks')
def ClearBookmarks(title):
    if 'All' in title:
        if Prefs['cache_covers']:
            for key in Dict['Bookmarks'].keys():
                if not key == 'Manga':
                    for bookmark in Dict['Bookmarks'][key]:
                        RemoveCoverImage(bookmark['cover_file'])

        # delete 'Bookmarks' section from Dict
        del Dict['Bookmarks']
        Logger('Bookmarks section cleared')
    else:
        if not title == 'Manga' and Prefs['cache_covers']:
            for bookmark in Dict['Bookmarks'][title]:
                RemoveCoverImage(bookmark['cover_file'])

        # delete section 'Anime', 'Manga', 'Cartoon', or 'Drama' from bookmark list
        del Dict['Bookmarks'][title]
        Logger('Bookmark section %s cleared' % title)
        Logger('bookmarks after deletion\n%s' % Dict['Bookmarks'])

    # update Dict
    Dict.Save()

    # Provide feedback that the correct 'Bookmarks' section is removed
    return ObjectContainer(header="My Bookmarks",
        message='%s bookmarks have been cleared.' % title, no_cache=True)

####################################################################################################
# Setup logging options based on prefs, indirect because it has no return

@indirect
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
    path = Core.storage.join_path(GetCoverImagePath(), image_file)

    if not Core.storage.file_exists(path):
        scraper = cfscrape.create_scraper()
        r = scraper.get(image_url, stream=True)

        if r.status_code == 200:
            with io.open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            Logger('saved image %s' %path)
    else:
        Logger('file %s already exists' %image_file)

    return image_file

####################################################################################################
# Remove Cover Image

@indirect
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
# Same as HTML.ElementFromURL() but for url's hosted on cloudflare

@route(PREFIX + '/cfscrape-html')
def ElementFromURL(url):
    return HTML.ElementFromString(Request(url).text)

####################################################################################################
# Same as HTTP.Request() but for url's hosted on cloudflare

@route(PREFIX + '/cfscrape-http')
def Request(url):
    scraper = cfscrape.create_scraper()

    return scraper.get(url)
