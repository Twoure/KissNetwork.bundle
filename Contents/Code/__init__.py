####################################################################################################
#                                                                                                  #
#                               KissManga Plex Channel -- v1.0                                     #
#                                                                                                  #
####################################################################################################
# import section(s) not included in Plex Plug-In Framwork
import random

# set global variables
PREFIX = '/photos/kissmanga'
TITLE = 'KissManga'
BASE_URL = 'http://kissmanga.com'
SEARCH_URL = BASE_URL + '/Search/Manga?keyword=%s'

randomArt = random.randint(1, 8)
ART = 'art-default_' + str(randomArt) + '.png'
ICON = 'icon-default.png'

####################################################################################################

def Start():
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = TITLE
    DirectoryObject.thumb = R(ICON)

#    HTTP.CacheTime = CACHE_1DAY  # 1 day cache time  # once done editing will change back
    HTTP.CacheTime = 0  # 0 sec cache time

####################################################################################################
# Create the main menu

@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
    oc = ObjectContainer(title2=TITLE)  #, view_group='List')
    oc.add(DirectoryObject(key=Callback(AlphabetList), title='Alphabets'))
    oc.add(DirectoryObject(key=Callback(GenreList), title='Genres'))
    oc.add(DirectoryObject(key=Callback(Bookmarks, title='My Bookmarks'), title='My Bookmarks'))
    oc.add(PrefsObject(title='Preferences'))
    oc.add(InputDirectoryObject(
        key=Callback(Search),
        title='Search',
        summary='Search Kissmanga',
        prompt='Search for...'))

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
    elif Prefs['sort_opt'] == 'New Manga':
        Dict['s_opt'] = '/Newest'

    # Update the Dict to latest prefs
    Dict.Save()

####################################################################################################
# Loads bookmarked manga from Dict.

@route(PREFIX + '/bookmarks')
def Bookmarks(title):
    oc = ObjectContainer(title1=title, no_cache=True)

    # check for 'Bookmarks' section in Dict
    if not Dict['Bookmarks']:
        # if no 'Bookmarks' section the return pop up
        return ObjectContainer(
            header=title,
            message='No Bookmarks yet. Get out there and start adding some!!!.',
            no_cache = True)
    # create manga list from bookmarks info
    else:
        for bookmark in Dict['Bookmarks']:
            manga = bookmark['manga']
            title = bookmark['title']
            cover = bookmark['cover']
            summary = bookmark['summary']

            oc.add(DirectoryObject(
                key=Callback(MangaPage, manga=manga, title=title),
                title=title,
                summary=summary,
                thumb=cover))

        # add a way to clear the entire bookmarks list, i.e. start fresh
        oc.add(DirectoryObject(
            key=Callback(ClearBookmarks),
            title='Clear All Bookmarks',
            summary='CAUTION! This will clear your entire bookmark list!'))

        return oc

####################################################################################################
# Creates ABC directory

@route(PREFIX + '/alphabets')
def AlphabetList():
    oc = ObjectContainer(title2='Manga By #, A-Z')  # , view_group='List')

    # Manually create the '#' Directory
    oc.add(DirectoryObject(key=Callback(DirectoryList, page=1, pname='0', ntitle='#'), title='#'))

    # Create a list of Directories from A to Z
    for pname in map(chr, range(ord('A'), ord('Z')+1)):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, page=1, pname=pname.lower(), ntitle=pname),
            title=pname))

    Log('Built #, A-Z... Directories')

    return oc

####################################################################################################
# Creates Genre directory

@route(PREFIX + '/genres')
def GenreList():
    url = BASE_URL + '/MangaList'  # set url for populating genres array
    html = HTML.ElementFromURL(url)  # formate url response into html for xpath

    oc = ObjectContainer(title2='Manga By Genres')  # , view_group='List')

    # For loop to pull out valid Genres
    for genre in html.xpath('//div[@class="barContent"]//a'):
        if "Genre" in genre.get('href'):
            pname = genre.get('href')  # name used internally
            new_title = genre.text.replace('\n', '')  # name used for title2

            oc.add(DirectoryObject(
                key=Callback(DirectoryList, page=1, pname=pname, ntitle=new_title),
                title=new_title,))

    return oc

####################################################################################################
# GenreList, AlphabetList, and Search are sent here
# Pulls out Manga names and creates directories for them
# Plan to add section that detects if Genre is empty

@route(PREFIX + '/directory')
def DirectoryList(page, pname, ntitle):
    # Define url based on genre, abc, or search
    if "Search" in pname:
        url = SEARCH_URL % String.Quote(ntitle, usePlus=True)
    # Sort order 'A-Z'
    elif Dict['s_opt'] == None:
        if "Genre" in pname:
            # Genre Specific
            url = BASE_URL + '%s?page=%s' %(pname, page)
        else:
            # No Genre
            url = BASE_URL + '/MangaList?c=%s&page=%s' %(pname, page)
    # Sort order for all options except 'A-Z'
    elif "Genre" in pname:
        # Genre Specific with Prefs
        url = BASE_URL + '%s%s?page=%s' %(pname, Dict['s_opt'], page)
    else:
        # No Genre with Prefs
        url = BASE_URL + '/MangaList%s?c=%s&page=%s' %(Dict['s_opt'], pname, page)

    Log(Dict['s_opt'])  # Log Pref being used

    # format url and set variables
    html = HTML.ElementFromURL(url)
    pages = "Last Page"
    nextpg_node = None

    # determine if 'next page' is used in directory page
    if "Search" in pname:
        # The Search result page returnes a long list with no 'next page' option
        Log("Searching for %s" % ntitle)  # check to make sure its searching
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
        main_title = '%s: Page %s of %s' % (str(ntitle), str(page), str(total_pages))
    elif "Search" in pname:
        # set title2 for search page
        main_title = 'Search for: %s' % str(ntitle)
    else:
        # set title2 for last page
        main_title = '%s: Page %s, Last Page' % (str(ntitle), str(page))

    oc = ObjectContainer(title2=main_title)  # , view_group='List')

    # parse url for each Manga and pull out its title, summary, and cover image
    # took some time to figure out how to get the javascript info
    for manga in html.xpath('//table[@class="listing"]/tr'):
        m = manga.xpath('./td')
        if m:  # skip empty matches
            if m[0].get('title'):  # pull out the first 'td' since there are two
                title_text = m[0].get('title')  # convert section to string for searching
                # search for cover url and summary string
                thumb = Regex('src=\"([\S].*?)\"').search(title_text).group(1)
                summary = Regex('(?s)<p>([\r\n].*)</p>').search(title_text).group(1).strip()
                title = Regex('\">([\S].*?)</a>').search(title_text).group(1)
                manga_name = Regex('href=\"/Manga/([\S].*?)\"').search(title_text).group(1)
        else:
            # if no 'title' section is found then sets values to 'None'
            # ensures the oc.add doesn't have problems
            thumb = None
            summary = None
            title = None
            manga_name = None

        if manga_name and title:  # ensure all the items are here before adding
            oc.add(DirectoryObject(
                key=Callback(MangaPage, manga=manga_name, title=title),
                title=title,
                summary=summary,
                thumb=thumb))

    if nextpg_node:  # if not 'None' then find the next page and create a button
        nextpg = int(Regex("page=(\d+)").search(nextpg_node).group(1))
        Log.Debug('NextPage = %d' % nextpg)
        oc.add(NextPageObject(
            key=Callback(DirectoryList, page=nextpg, pname=pname, ntitle=ntitle),
            title='Next Page>>'))

    return oc

####################################################################################################
# Creates the Manga Page with a Chapter(s) section and a Bookmark option

@route(PREFIX + '/manga')
def MangaPage(manga, title):
    oc = ObjectContainer(title2=title)

    url = BASE_URL + '/Manga/' + manga
    html = HTML.ElementFromURL(url)

    # add the Chapter(s) section
    oc.add(DirectoryObject(
        key=Callback(ChaptersPage, manga=manga, title=title),
        title='Chapter(s)',
        summary='List all currently avalible chapter(s) for \"%s\"' % title))

    # Test if the Dict has the 'Bookmarks' section yet
    if Dict['Bookmarks']:
        match = False
        for bookmark in Dict['Bookmarks']:
            if manga in bookmark['manga']:
                match = True
                break  # Stop for loop if match found

        # If Manga found in 'Bookmarks'
        if match:
            # provide a way to remove manga from bookmarks list
            oc.add(DirectoryObject(
                key = Callback(RemoveBookmark, manga=manga, title=title),
                title = 'Remove Bookmark',
                summary = 'Remove \"%s\" from your Bookmarks list.' % title))
        # No Manga in 'Bookmarks' yet, so lets parse it for adding!
        else:
            cover = html.xpath('//head/link[@rel="image_src"]')[0].get('href')
            summary = None

            # enumerate array so we can find the Summary text
            for i, item in enumerate(html.xpath('//div[@id="container"]//p')):
                if "Summary:" in item.xpath('./span[@class="info"]/text()'):
                    match = int(i)
                    break

            # add 1 to our Summary match to find the Summary text
            # fix string encoding errors before they happen by converting to ascii
            #   and ignoring unknown charaters in summary string
            # wish the site was more consistant with its summary location... ugh
            for i, item in enumerate(html.xpath('//div[@id="container"]//p')):
                if match + 1 == i:
                    # sometimes summary is inside a <span>
                    if item.xpath('./span'):
                        summary = item.xpath('./span/text()')[0].encode('ascii', 'ignore')
                        break
                    else:
                        summary = item.xpath('./text()')[0].strip().encode('ascii', 'ignore')
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
                key = Callback(AddBookmark, manga=manga, title=title, cover=cover, summary=summary),
                title = 'Add Bookmark',
                summary = 'Add \"%s\" to your Bookmarks list.' % title))
    # No 'Bookmarks' section in Dict yet, so don't look for Manga in 'Bookmarks'
    else:
        # Same stuff as above
        cover = html.xpath('//head/link[@rel="image_src"]')[0].get('href')
        summary = None

        for i, item in enumerate(html.xpath('//div[@id="container"]//p')):
            if "Summary:" in item.xpath('./span[@class="info"]/text()'):
                match = int(i)
                break

        for i, item in enumerate(html.xpath('//div[@id="container"]//p')):
            if match + 1 == i:
                    if item.xpath('./span'):
                        summary = item.xpath('./span/text()')[0].encode('ascii', 'ignore')
                        break
                    else:
                        summary = item.xpath('./text()')[0].encode('ascii', 'ignore')
                        break

        if not summary:
            summary = html.xpath(
                '//div[@id="container"]//div[@class="barContent"]/div/div/text()'
                )[0].strip().encode('ascii', 'ignore')
        else:
            summary = summary

        # provide a way to add or remove from bookmarks list
        oc.add(DirectoryObject(
            key=Callback(AddBookmark, manga=manga, title=title, cover=cover, summary=summary),
            title='Add Bookmark',
            summary='Add \"%s\" to your Bookmarks list.' % title))

    return oc

####################################################################################################
# Create the Manga Page with it's chapters

@route(PREFIX + '/chapters')
def ChaptersPage(manga, title):
    oc = ObjectContainer(title2=title)  #, view_group='List')

    url = BASE_URL + '/Manga/' + manga
    html = HTML.ElementFromURL(url)

    # parse html for internal chapter name and public name
    for chapter in html.xpath('//table[@class="listing"]/tr//a'):
        chapter_url = BASE_URL + chapter.get('href')  # url for Photo Album
        Log('Chapter URL = %s' % chapter_url)
        title = chapter.text.replace('\n', '')  # title for Chapter and Photo Album
        Log('Chapter Title = %s' % title)

        # Add Photo Album. Service url gets the images for the Chapter
        oc.add(PhotoAlbumObject(url=chapter_url, title=title))

    return oc

####################################################################################################
# Search kissmanga for Manga. The results can return the Manga itself via a url redirect.

@route(PREFIX + '/search')
def Search(query=''):
    # format search query
    # Check for "exact" matches and send them to MangaPage
    # If normal seach result then send to DirectoryList
    url = SEARCH_URL % String.Quote(query, usePlus=True)
    h = HTTP.Request(url)
    header = h.headers  # pull out headers in JSON format
    html = HTML.ElementFromString(h.content)  # convert page to html

    # Check for results if none then give a pop up window saying so
    if html.xpath('//table[@class="listing"]'):
        # Test for "exact" match, if True then send to 'MangaPage'
        if 'transfer-encoding' in str(header):
            node = html.xpath('//head/link[@rel="alternate"]')[0]
            title = node.get('title')  # name used for title2
            manga = node.get('href').rsplit('/')[-1]  # name used internally
            return MangaPage(manga, title)
        # Send results to 'DirectoryList'
        else:
            return DirectoryList(1, 'Search', query)
    # No results found :( keep trying
    else:
        Log('Search returned no results.')
        return ObjectContainer(
            header='Search',
            message='There are no search results for "%s".\r\nTry being less specific.' % query)

####################################################################################################
# Adds manga to the bookmarks list

@route(PREFIX + '/addbookmark')
def AddBookmark(manga, title, cover, summary):
    # setup new bookmark json data
    new_bookmark = {'manga': manga, 'title': title, 'cover': cover, 'summary': summary}

    # Test if the Dict has the 'Bookmarks' section yet
    if not Dict['Bookmarks']:
        # Create new 'Bookmarks' section and fill with the first bookmark
        Dict['Bookmarks'] = [new_bookmark]

        # Update Dict to include new 'Bookmarks' section
        Dict.Save()

        # Provide feedback that the Manga has been added to bookmarks
        return ObjectContainer(
            header=title,
            message='\"%s\" has been added to your bookmarks.' % title,
            no_cache = True)

    # Index the current manga and find if it's already in the 'Bookmarks' list
    match = False
    for bookmark in Dict['Bookmarks']:
        if manga in bookmark['manga']:
            match = True
            break

    # If Manga is already in 'Bookmarks' list then tell the user, and skip adding it
    # this happens when the channel tries to added the same manga more than once
    # can happen if the back button is used too
    if match:
        return ObjectContainer(
            header=title,
            message='\"%s\" is already in your bookmarks.' % title,
            no_cache = True)
    # Add Manga to 'Bookmarks' list in Dict
    else:
        bookmarks = Dict['Bookmarks']
        bookmarks.append(new_bookmark)
        Log('\"%s\" added to Bookmark List' % title)

        # Update Dict to include new Manga
        Dict.Save()

        # Provide feedback that the Manga has been added to bookmarks
        return ObjectContainer(
            header=title,
            message='\"%s\" has been added to your bookmarks.' % title,
            no_cache = True)

####################################################################################################
# Removes manga from the bookmarks list using the manga as a key

@route(PREFIX + '/removebookmark')
def RemoveBookmark(manga, title):
    # index 'Bookmarks' list
    for i in xrange(len(Dict['Bookmarks'])):
        # remove Manga data from 'Bookmarks' list
        if Dict['Bookmarks'][i]['manga'] == manga:
            Dict['Bookmarks'].pop(i)
            break

    # update Dict, and debug log
    Dict.Save()
    Log('\"%s\" has been removed from Bookmark List' % title)

    # Provide feedback that the Manga has been removed from the 'Bookmarks' list
    return ObjectContainer(
        header=title,
        message='\"%s\" has been removed from your bookmarks.' % title,
        no_cache = True)

####################################################################################################
# Remove 'Bookmarks' Section from Dict. Note: This removes all bookmarks

@route(PREFIX + '/clearbookmarks')
def ClearBookmarks():
    # delet 'Bookmarks' section from Dict
    del Dict['Bookmarks']

    # update Dict, and debug log
    Dict.Save()
    Log('Bookmarks section removed from Dict')

    # Provide feedback that the 'Bookmarks' section is removed
    return ObjectContainer(
        header="My Bookmarks",
        message='Your bookmark list has been cleared.',
        no_cache = True)
