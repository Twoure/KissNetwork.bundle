####################################################################################################
#                                                                                                  #
#                               KissNetwork Plex Channel -- v1.0                                   #
#                                                                                                  #
####################################################################################################
# import section(s) not included in Plex Plug-In Framwork
import random, os, sys

# add custom modules to python path
submodule_folders = ['cfscrape', 'execjs', 'requests']
for folder in submodule_folders:
    try:
        path = os.getcwd().split("?\\")[1].split('Plug-in Support')[0] + "Plug-ins/KissNetwork.bundle/Contents/Modules/" + folder
        Log('try 1 %s' % path)
    except:
        path = os.getcwd().split("Plug-in Support")[0] + "Plug-ins/KissNetwork.bundle/Contents/Modules/" + folder
        Log('try 2 %s' % path)

    if path not in sys.path:
        sys.path.append(path)
        Log('%s added to sys.path' % path)

# import custom module cfscrape to load url's hosted on cloudflare
import cfscrape

# set global variables
PREFIX = '/video/kissnetwork'
TITLE = 'KissNetwork'

# KissAnime
ANIME_BASE_URL = 'http://kissanime.com'
ANIME_SEARCH_URL = ANIME_BASE_URL + '/Search/Anime?keyword=%s'

# KissAsian
ASIAN_BASE_URL = 'http://kissasian.com'
ASIAN_SEARCH_URL = ASIAN_BASE_URL + '/Search/Drama?keyword=%s'

# KissCartoon
CARTOON_BASE_URL = 'http://kisscartoon.me'
CARTOON_SEARCH_URL = CARTOON_BASE_URL + '/Search/Cartoon?keyword=%s'

# KissManga
MANGA_BASE_URL = 'http://kissmanga.com'
MANGA_SEARCH_URL = MANGA_BASE_URL + '/Search/Manga?keyword=%s'
#[ANIME_SEARCH_URL, ASIAN_SEARCH_URL, CARTOON_SEARCH_URL, MANGA_SEARCH_URL]
randomArt = random.randint(1, 8)
ART = 'art-default_' + str(randomArt) + '.png'
ICON = 'icon-default.png'

####################################################################################################

def Start():
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = TITLE
    DirectoryObject.thumb = R(ICON)

#    HTTP.CacheTime = CACHE_1DAY  # 1 day cache time  # once done editing will change back
    HTTP.CacheTime = 300  # 0 sec cache time, 300 sec = 5 mins

####################################################################################################
# Create the main menu

@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
    oc = ObjectContainer(title2=TITLE)
    oc.add(DirectoryObject(
        key=Callback(KissAnime, url=ANIME_BASE_URL, title='Anime'),
        title='Anime'))
    oc.add(DirectoryObject(
        key=Callback(KissCartoon, url=CARTOON_BASE_URL, title='Cartoon'),
        title='Cartoons'))
    oc.add(DirectoryObject(
        key=Callback(KissAsian, url=ASIAN_BASE_URL, title='Drama'),
        title='Drama'))
    oc.add(DirectoryObject(
        key=Callback(KissManga, url=MANGA_BASE_URL, title='Manga'),
        title='Manga'))
    oc.add(DirectoryObject(key=Callback(BookmarksMain, title='My Bookmarks'), title='My Bookmarks'))
    oc.add(PrefsObject(title='Preferences'))
    oc.add(InputDirectoryObject(
        key=Callback(Search),
        title='Search',
        summary='Search KissNetwork',
        prompt='Search for...'))

    return oc

####################################################################################################
# Create KissAnime site Menu

@route(PREFIX + '/kissanime')
def KissAnime(url, title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(
        key=Callback(
            DirectoryList,
            page=1, pname='All', category='All', url=url, title=title), title='All'))
    oc.add(DirectoryObject(key=Callback(AlphabetList, url=url, title=title), title='Alphabets'))
    oc.add(DirectoryObject(key=Callback(GenreList, url=url, title=title), title='Genres'))
    """
    oc.add(InputDirectoryObject(
        key=Callback(Search, title=title, url=ANIME_SEARCH_URL),
        title='Search',
        summary='Search Kissanime',
        prompt='Search for...'))
    """

    return oc

####################################################################################################
# Create KissAsian site Menu

@route(PREFIX + '/kissasian')
def KissAsian(url, title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(
        key=Callback(
            DirectoryList,
            page=1, pname='All', category='All', url=url, title=title), title='All'))
    oc.add(DirectoryObject(key=Callback(AlphabetList, url=url, title=title), title='Alphabets'))
    oc.add(DirectoryObject(key=Callback(CountryList, url=url, title=title), title='Countries'))
    oc.add(DirectoryObject(key=Callback(GenreList, url=url, title=title), title='Genres'))
    """
    oc.add(InputDirectoryObject(
        key=Callback(Search, title=title, url=ASIAN_SEARCH_URL),
        title='Search',
        summary='Search Kissasian',
        prompt='Search for...'))
    """

    return oc

####################################################################################################
# Create KissCartoon site Menu

@route(PREFIX + '/kisscartoon')
def KissCartoon(url, title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(
        key=Callback(
            DirectoryList,
            page=1, pname='All', category='All', url=url, title=title), title='All'))
    oc.add(DirectoryObject(key=Callback(AlphabetList, url=url, title=title), title='Alphabets'))
    oc.add(DirectoryObject(key=Callback(GenreList, url=url, title=title), title='Genres'))
    """
    oc.add(InputDirectoryObject(
        key=Callback(Search, title=title, url=CARTOON_SEARCH_URL),
        title='Search',
        summary='Search Kisscartoon',
        prompt='Search for...'))
    """

    return oc

####################################################################################################
# Create KissManga site Menu

@route(PREFIX + '/kissmanga')
def KissManga(url, title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(
        key=Callback(
            DirectoryList,
            page=1, pname='All', category='All', url=url, title=title), title='All'))
    oc.add(DirectoryObject(key=Callback(AlphabetList, url=url, title=title), title='Alphabets'))
    oc.add(DirectoryObject(key=Callback(GenreList, url=url, title=title), title='Genres'))
    """
    oc.add(InputDirectoryObject(
        key=Callback(Search, title=title, url=MANGA_SEARCH_URL),
        title='Search',
        summary='Search Kissmanga',
        prompt='Search for...'))
    """

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

    # Update the Dict to latest prefs
    Dict.Save()

####################################################################################################
# Crates Bookmark Menu

@route(PREFIX + '/bookmarks')
def BookmarksMain(title):
    oc = ObjectContainer(title1=title)  #, no_cache=True)

    # check for 'Bookmarks' section in Dict
    if not Dict['Bookmarks']:
        # if no 'Bookmarks' section the return pop up
        return ObjectContainer(
            header=title,
            message='No Bookmarks yet. Get out there and start adding some!!!.',
            no_cache = True)
    # create boomark directory based on category
    else:
        for key in sorted(Dict['Bookmarks'].keys()):
            # Create sub Categories for Anime, Cartoon, Drama, and Manga
            oc.add(DirectoryObject(
                key=Callback(BookmarksSub, key=key),
                title=key,
                summary='Display Anime Bookmarks'))

        # add a way to clear the entire bookmarks list, i.e. start fresh
        oc.add(DirectoryObject(
            key=Callback(ClearBookmarks, title='All'),
            title='Clear All Bookmarks',
            summary='CAUTION! This will clear your entire bookmark list!'))

        return oc

####################################################################################################
# Loads bookmarked items from Dict.

@route(PREFIX + '/bookmarkssub')
def BookmarksSub(key):
    oc = ObjectContainer(title1='My Bookmarks | %s' % key)  #, no_cache=True)
    Log(key)

    # Fill in DirectoryObject information from the bookmark list
    for bookmark in Dict['Bookmarks'][key]:
        item = bookmark[key]
        item_title = bookmark['title']
        cover = bookmark['cover']
        summary = bookmark['summary']
        url = bookmark['base_url']

        # gotta send the bookmark somewhere
        oc.add(DirectoryObject(
            key=Callback(ItemPage, item=item, item_title=item_title, title=key, url=url),
            title=item_title,
            summary=summary,
            thumb=cover))

    # add a way to clear this bookmark section and start fresh
    oc.add(DirectoryObject(
        key=Callback(ClearBookmarks, title=key),
        title='Clear All \"%s\" Bookmarks' % key,
        summary='CAUTION! This will clear your entire \"%s\" bookmark section!' % key))

    return oc

####################################################################################################
# Creates ABC directory

@route(PREFIX + '/alphabets')
def AlphabetList(url, title):
    oc = ObjectContainer(title2='%s By #, A-Z' % title)

    # Manually create the '#' Directory
    oc.add(DirectoryObject(
        key=Callback(
            DirectoryList, page=1, pname='0',
            category='#', url=url, title=title),
            title='#'))

    # Create a list of Directories from A to Z
    for pname in map(chr, range(ord('A'), ord('Z')+1)):
        oc.add(DirectoryObject(
            key=Callback(
                DirectoryList, page=1, pname=pname.lower(),
                category=pname, url=url, title=title),
                title=pname))

    Log('Built #, A-Z... Directories')

    return oc

####################################################################################################
# Creates Genre directory

@route(PREFIX + '/genres')
def GenreList(url, title):
    genre_url = url + '/%sList' % title
    html = ElementFromURL(genre_url)

    oc = ObjectContainer(title2='%s By Genres' % title)

    # For loop to pull out valid Genres
    for genre in html.xpath('//div[@class="barContent"]//a'):
        if "Genre" in genre.get('href'):
            pname = genre.get('href')  # name used internally
            category = genre.text.replace('\n', '').strip()  # name used for title2

            oc.add(DirectoryObject(
                key=Callback(
                    DirectoryList, page=1, pname=pname,
                    category=category, url=url, title=title),
                    title=category))

    return oc

####################################################################################################
# Creates Country directory for KissAsian

@route(PREFIX + '/countries')
def CountryList(url, title):
    country_url = url + '/DramaList'  # set url for populating genres array
    html = ElementFromURL(country_url)  # formate url response into html for xpath

    oc = ObjectContainer(title2='Drama By Country')

    # For loop to pull out valid Genres
    for country in html.xpath('//div[@class="barContent"]//a'):
        if "Country" in country.get('href'):
            pname = country.get('href')  # name used internally
            category = country.text.replace('\n', '').strip()  # name used for title2

            oc.add(DirectoryObject(
                key=Callback(
                    DirectoryList, page=1, pname=pname,
                    category=category, url=url, title=title),
                    title=category))

    return oc

####################################################################################################
# GenreList, AlphabetList, and Search are sent here
# Pulls out Items name and creates directories for them
# Plan to add section that detects if Genre is empty

@route(PREFIX + '/directory')
def DirectoryList(page, pname, category, url, title):
    # Define url based on genre, abc, or search
    if "Search" in pname:
        item_url = url
        Log('Searching for \"%s\"' % category)
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

    Log('Sorting Option = %s' % Dict['s_opt'])  # Log Pref being used
    Log('Category= %s | URL= %s' % (pname, item_url))

    # format url and set variables
    html = ElementFromURL(item_url)
    pages = "Last Page"
    nextpg_node = None

    # determine if 'next page' is used in directory page
    if "Search" in pname:
        # The Search result page returnes a long list with no 'next page' option
        Log("Searching for %s" % category)  # check to make sure its searching
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

    oc = ObjectContainer(title2=main_title)  # , view_group='List')

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
                else:
                    thumb = None
                summary = Regex('(?s)<p>([\r\n].*)</p>').search(title_text).group(1).strip()
                item_title = Regex('\">([\S].*?)</a>').search(title_text).group(1)
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
                key=Callback(ItemPage, item=name, item_title=item_title, title=title, url=url),
                title=item_title,
                summary=summary,
                thumb=thumb))

    if nextpg_node:  # if not 'None' then find the next page and create a button
        nextpg = int(Regex("page=(\d+)").search(nextpg_node).group(1))
        Log.Debug('NextPage = %d' % nextpg)
        oc.add(NextPageObject(
            key=Callback(DirectoryList, page=nextpg, pname=pname, category=category, url=url, title=title),
            title='Next Page>>'))

    return oc

####################################################################################################
# Creates the Manga Page with a Chapter(s) section and a Bookmark option

@route(PREFIX + '/item')
def ItemPage(item, item_title, title, url):
    title2 = '%s | %s' % (title, item_title)
    oc = ObjectContainer(title2=title2)

    item_url = url + '/%s/' % title + item
    html = ElementFromURL(item_url)

    if not 'Manga' in title:
        # add the ItemSubPage section
        oc.add(DirectoryObject(
            key=Callback(ItemSubPage, item=item, item_title=item_title, title=title, url=url),
            title='Video(s)',
            summary='List all currently avalible episode(s), movie(s) or video(s) for \"%s\"' % item_title))
    else:
        # add the Chapter(s) section
        oc.add(DirectoryObject(
            key=Callback(ChaptersPage, manga=item, manga_title=item_title, title=title, url=url),
            title='Chapter(s)',
            summary='List all currently avalible chapter(s) for \"%s\"' % item_title))

    # Test if the Dict does have the 'Bookmarks' section
    if Dict['Bookmarks']:
        book_match = False
        if title in Dict['Bookmarks']:
            for category in Dict['Bookmarks'][title]:
                if item in category[title]:
                    book_match = True
                    break  # Stop for loop if match found

        # If Manga found in 'Bookmarks'
        if book_match:
            # provide a way to remove manga from bookmarks list
            oc.add(DirectoryObject(
                key = Callback(RemoveBookmark, item=item, item_title=item_title, title=title),
                title = 'Remove Bookmark',
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
                        summary = node.xpath('./span/text()')[0].encode('ascii', 'ignore')
                        break
                    else:
                        summary = node.xpath('./text()')[0].strip().encode('ascii', 'ignore')
                        break

            # some Summary text is not in the <p> but in it's own <div>
            if not summary:
                summary = html.xpath(
                    '//div[@id="container"]//div[@class="barContent"]/div/div/text()'
                    )[0].strip().encode('ascii', 'ignore')
            # in event summary isn't found set to 'None'
            else:
                summary = summary

            # provide a way to add manga to the bookmarks list
            oc.add(DirectoryObject(
                key = Callback(
                    AddBookmark, item=item, item_title=item_title,
                    title=title, cover=cover, summary=summary, url=url),
                title = 'Add Bookmark',
                summary = 'Add \"%s\" to your Bookmarks list.' % item_title))
    # No 'Bookmarks' section in Dict yet, so don't look for Manga in 'Bookmarks'
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
                        summary = node.xpath('./span/text()')[0].encode('ascii', 'ignore')
                        break
                    else:
                        summary = node.xpath('./text()')[0].encode('ascii', 'ignore')
                        break

        if not summary:
            summary = html.xpath(
                '//div[@id="container"]//div[@class="barContent"]/div/div/text()'
                )[0].strip().encode('ascii', 'ignore')
        else:
            summary = summary

        # provide a way to add item to bookmarks list
        oc.add(DirectoryObject(
            key=Callback(
                AddBookmark, item=item, item_title=item_title,
                title=title, cover=cover, summary=summary, url=url),
            title='Add Bookmark',
            summary='Add \"%s\" to your Bookmarks list.' % item_title))

    return oc

####################################################################################################
# Create the Item Sub Page with Seasons, Movies and Misc Video list

@route(PREFIX + '/itemsubpage')
def ItemSubPage(item, item_title, title, url):
    title2 = '%s | %s | Video(s)' % (title, item_title)
    oc = ObjectContainer(title2=title2)

    sub_url = url + '/%s/' % title + item
    Log(sub_url)
    html = ElementFromURL(sub_url)
    item_title = Regex('[^a-zA-Z0-9 \n\.]').sub('', item_title)

    # parse html for internal item name and public name
    for video in html.xpath('//table[@class="listing"]/tr//a'):
        video_page_url = url + video.get('href')  # url for Video page
        Log('Video Page URL = %s' % video_page_url)
        raw_title = Regex('[^a-zA-Z0-9 \n\.]').sub('', video.text).replace(item_title, '')
        video_title = raw_title.replace('Watch Online', '').strip()
        Log('Video Title = %s' % video_title)

        oc.add(DirectoryObject(
            key=Callback(VideoDetail, title=video_title, url=video_page_url), title=video_title))

    return oc

####################################################################################################
# Create Video container

@route(PREFIX + '/videodetail')
def VideoDetail(title, url):
    oc = ObjectContainer(title2=title)
    oc.add(VideoClipObject(title=title, url=url))

    return oc

####################################################################################################
# Create the Manga Page with it's chapters

@route(PREFIX + '/chapters')
def ChaptersPage(manga, manga_title, title, url):
    title2 = '%s | %s | Chapter(s)' % (title, manga_title)
    oc = ObjectContainer(title2=title2)

    chp_url = url + '/%s/' % title + manga
    html = ElementFromURL(chp_url)
    manga_title = Regex('[^a-zA-Z0-9 \n\.]').sub('', manga_title)

    # parse html for internal chapter name and public name
    for chapter in html.xpath('//table[@class="listing"]/tr//a'):
        chapter_url = url + chapter.get('href')  # url for Photo Album
        Log('Chapter URL = %s' % chapter_url)
        raw_title = Regex('[^a-zA-Z0-9 \n\.]').sub('', chapter.text).replace(manga_title, '')
        chapter_title = raw_title.replace('Read Online', '').strip()  # title for Chapter and Photo Album
        Log('Chapter Title = %s' % title)

        # Add Photo Album. Service url gets the images for the Chapter
        oc.add(PhotoAlbumObject(url=chapter_url, title=chapter_title))

    return oc

####################################################################################################
# Set up Search for kiss(anime, asian, cartoon, manga)

@route(PREFIX + '/search')
def Search(query=''):
    # format search query

    # set defaults
    title2 = 'Search for %s' % query
    search_match = []

    oc = ObjectContainer(title2=title2)

    all_search_urls = [ANIME_SEARCH_URL, ASIAN_SEARCH_URL, CARTOON_SEARCH_URL, MANGA_SEARCH_URL]

    # format each search url and send to 'SearchPage'
    # can't check each url here, would take too long since behind cloudflare and timeout the server
    for search_url in all_search_urls:
        search_url_filled = search_url % String.Quote(query, usePlus=True)
        base_url = search_url_filled.rsplit('Search', 1)[0][:-1]
        title = base_url.rsplit('/', 2)[2].rsplit('kiss', 1)[1].rsplit('.', 1)[0].title()
        if title == 'Asian':
            title = 'Drama'
        Log('Search url=%s' % search_url_filled)

        oc.add(DirectoryObject(
            key=Callback(SearchPage, title=title, search_url=search_url_filled),
            title=title))

    return oc

####################################################################################################
# Retrun searches for each kiss() page
# The results can return the Item itself via a url redirect.

@route(PREFIX + '/searchpage')
def SearchPage(title, search_url):
    # Check for "exact" matches and send them to ItemPage
    # If normal seach result then send to DirectoryList

    html = ElementFromURL(search_url)

    # Check for results if none then give a pop up window saying so
    if html.xpath('//table[@class="listing"]'):
        # Test for "exact" match, if True then send to 'ItemPage'
        node = html.xpath('//div[@id="headnav"]/script/text()')[0]
        search_match = Regex('var\ path\ =\ (\'Search\')').search(node)
        if not search_match:
            base_url = search_url.rsplit('Search', 1)[0][:-1]
            node = html.xpath('//div[@class="barContent"]/div/a')[0]
            item = node.get('href').rsplit('/')[-1]
            item_title = node.text
            Log('\nitem_title=%s\nitem=%s\ntitle=%s\nurl=%s' % (item_title, item, title, base_url))

            return ItemPage(item=item, item_title=item_title, title=title, url=base_url)
        else:
            # Send results to 'DirectoryList'
            query = search_url.rsplit('=')[-1]
            return DirectoryList(1, 'Search', query, search_url, title)
    # No results found :( keep trying
    else:
        Log('Search returned no results.')
        query = search_url.rsplit('=')[-1]
        return ObjectContainer(
            header='Search',
            message='There are no search results for \"%s\" in \"%s\" Category.\r\nTry being less specific.' % (query, title))

####################################################################################################
# Adds Item to the bookmarks list

@route(PREFIX + '/addbookmark')
def AddBookmark(item, item_title, title, cover, summary, url):
    # setup new bookmark json data to add to Dict
    Log(item)
    new_bookmark = {title: item, 'title': item_title, 'cover': cover, 'summary': summary, 'base_url': url}
    Log('new bookmark to add\n%s' % new_bookmark)

    # Test if the Dict has the 'Bookmarks' section yet
    if not Dict['Bookmarks']:
        # Create new 'Bookmarks' section and fill with the first bookmark
        Dict['Bookmarks'] = {title: [new_bookmark]}
        Log('Inital bookmark list created\n%s' % Dict['Bookmarks'])

        # Update Dict to include new 'Bookmarks' section
        Dict.Save()

        # Provide feedback that the Manga has been added to bookmarks
        return ObjectContainer(
            header=item_title,
            message='\"%s\" has been added to your bookmarks.' % item_title,
            no_cache = True)
    # check if key 'Anime', 'Manga', 'Cartoon', or 'Drama' exist
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
            return ObjectContainer(
                header=item_title,
                message='\"%s\" is already in your bookarks.' % item_title,
                no_cache=True)
        else:
            temp = {}
            temp.setdefault(title, Dict['Bookmarks'][title]).append(new_bookmark)
            Dict['Bookmarks'][title] = temp[title]
            Log('bookmark list after addition\n%s' % Dict['Bookmarks'])

            # Update Dict to include new Manga
            Dict.Save()

            # Provide feedback that the Manga has been added to bookmarks
            return ObjectContainer(
                header=item_title,
                message='\"%s\" has been added to your bookmarks.' % item_title,
                no_cache=True)
    # the category key does not exist yet so create it and fill with new bookmark
    else:
        Dict['Bookmarks'].update({title: [new_bookmark]})
        Log('bookmark list after addition of new section\n%s' % Dict['Bookmarks'])

        # Update Dict to include new Manga
        Dict.Save()

        # Provide feedback that the Manga has been added to bookmarks
        return ObjectContainer(
            header=item_title,
            message='\"%s\" has been added to your bookmarks.' % item_title,
            no_cache=True)

####################################################################################################
# Removes item from the bookmarks list using the item as a key

@route(PREFIX + '/removebookmark')
def RemoveBookmark(item, item_title, title):
    # index 'Bookmarks' list
    bm = Dict['Bookmarks'][title]
    for i in xrange(len(bm)):
        # remove item's data from 'Bookmarks' list
        if bm[i][title] == item:
            bm.pop(i)
            break

    # update Dict, and debug log
    Dict.Save()
    Log('\"%s\" has been removed from Bookmark List' % item_title)
    Log('bookmark list after removal\n%s' % Dict['Bookmarks'])

    # Provide feedback that the Manga has been removed from the 'Bookmarks' list
    return ObjectContainer(
        header=title,
        message='\"%s\" has been removed from your bookmarks.' % item_title,
        no_cache=True)

####################################################################################################
# Remove 'Bookmarks' Section(s) from Dict. Note: This removes all bookmarks in list

@route(PREFIX + '/clearbookmarks')
def ClearBookmarks(title):
    if 'All' in title:
        # delete 'Bookmarks' section from Dict
        del Dict['Bookmarks']
        Log('Bookmarks section cleared')
    else:
        # delete section 'Anime', 'Manga', 'Cartoon', or 'Drama' from bookmark list
        del Dict['Bookmarks'][title]
        Log('Bookmark section %s cleared' % title)
        Log('bookmarks after deletion\n%s' % Dict['Bookmarks'])

    # update Dict, and debug log
    Dict.Save()

    # Provide feedback that the correct 'Bookmarks' section is removed
    return ObjectContainer(
        header="My Bookmarks",
        message='%s bookmarks have been cleared.' % title,
        no_cache=True)

####################################################################################################
# No route needed, this is a function to simplify cfscraper
# Same as HTML.ElementFromURL() but for url's hosted on cloudflare

def ElementFromURL(url):
    """
    Retrun url in html formate
    """

    scraper = cfscrape.create_scraper()
    page = scraper.get(url)
    myscrape = HTML.ElementFromString(page.text)

    return myscrape

####################################################################################################
# No route needed, this is a function to simplify cfscraper
# Same as HTTP.Request() but for url's hosted on cloudflare

def Request(url):
    """
    Get url data so it can be manipulated for headers or content
    """

    scraper = cfscrape.create_scraper()
    page = scraper.get(url)

    return page
