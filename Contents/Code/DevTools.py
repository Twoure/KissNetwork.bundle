import shutil
from io import open
Headers = SharedCodeService.headers
Domain = SharedCodeService.domain
Common = SharedCodeService.common
import requests
import json
from time import sleep
import rhtml as RHTML

PREFIX = '/video/kissnetwork'

####################################################################################################
def add_dev_tools(oc):
    oc.add(DirectoryObject(key=Callback(DevTools),
        title='Developer Tools',
        summary='WARNING!!\nDeveloper Tools.  Make sure you understand what these do before using.'
        ))

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

    oc = ObjectContainer(title2='Developer Tools', header=header, message=message, no_cache=True)

    if file_to_reset:
        header = 'Developer Tools'
        if file_to_reset == 'cfscrape_test':
            Log('\n----------Deleting cfscrape test key from Channel Dict----------')
            if Dict['cfscrape_test']:
                del Dict['cfscrape_test']
                Dict.Save()
                SetUpCFTest()
                message = 'Reset cfscrape Code Test'
            else:
                message = 'No Dict cfscrape Code Test Key to Remove'
        elif file_to_reset == 'restart_channel':
            Log('\n----------Attempting to Restart KissNetwork Channel----------')
            RestartChannel()
            message = 'Restarting channel'
        elif file_to_reset == 'clear_url_cache':
            Log('\n----------Clearing URL Cache----------')
            count = ClearCache(Datetime.Delta())
            message = 'Cleaned %i Cached URL files' %count
            Log('\n----------Cleaned %i Cached files----------' %count)
        return DevTools(header=header, message=message, file_to_reset=None)

    oc.add(DirectoryObject(key=Callback(DevToolsBM),
        title='Bookmark Tools',
        summary='Tools to Clean dirty bookmarks dictionary, and Toggle "Clear Bookmarks".'))
    oc.add(DirectoryObject(key=Callback(DevToolsC),
        title='Cover Cache Tools',
        summary='Tools to Cache All Covers or just certain sites. Includes Tool to Clean Dirty Resources Directory.'))
    oc.add(DirectoryObject(key=Callback(DevToolsD),
        title='Domain Tools',
        summary='Tools to Reset "Domain_Dict" or Update parts of "Domain_Dict".'))
    oc.add(DirectoryObject(key=Callback(DevToolsH),
        title='Header Tools',
        summary='Tools to Reset "Header_Dict" or Update parts of "Header_Dict".'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='cfscrape_test'),
        title='Reset Dict cfscrape Test Key',
        summary='Delete previous test key so the channel can retest for a valid JavaScript Runtime.'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='clear_url_cache'),
        title='Reset URL Cache',
        summary='Force delete current URL Cache.'))
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

            return DevToolsH(header=header, message=message, title=None)
        elif ( title == 'Anime' or title == 'Cartoon'
            or title == 'Drama' or title == 'Manga' or title == 'Comic' ):
            Log('\n----------Updating %s Headers in Header_Dict----------' %title)

            for (h_name, h_url) in Common.BaseURLListTuple():
                if h_name == title:
                    Headers.GetHeadersForURL(h_url, update=True)
                    break

            message = 'Updated %s Headers.' %title
            return DevTools(header=header, message=message, file_to_reset=None)

    oc.add(DirectoryObject(key=Callback(DevToolsH, title='Header_Dict'),
        title='Reset Header_Dict File',
        summary='Create backup of old Header_Dict, delete current, create new and fill with fresh headers. Remember Creating Header_Dict takes time, so the channel may timeout on the client while rebuilding.  Do not worry. Exit channel and refresh client. The channel should load normally now.'))
    for (name, url) in sorted(Common.BaseURLListTuple()):
        oc.add(DirectoryObject(key=Callback(DevToolsH, title=name),
            title='Update %s Headers' %name,
            summary='Update %s Headers Only in the "Header_Dict" file.' %name))

    return oc

####################################################################################################
@route(PREFIX + '/devtools-domain')
def DevToolsD(title=None, header=None, message=None):
    """URL Domain Tools"""

    oc = ObjectContainer(title2='Domain Tools', header=header, message=message)

    if title:
        header = 'Domain Tools'
        if title == 'Domain_Dict':
            Thread.Create(ResetCustomDict, file_to_reset=title)
            message = 'Resetting %s. New values for %s will be written soon' %(title, title)

            return DevToolsD(header=header, message=message, title=None)
        elif title == 'recache_default_domains':
            Log('\n----------Re-Caching Default Domains----------')
            Domain.get_domain_dict(True)
            message = 'Default Domains Re-Cached'

            return DevToolsD(header=header, message=message, title=None)
        elif ( title == 'Anime' or title == 'Cartoon'
            or title == 'Drama' or title == 'Manga' or title == 'Comic' ):
            Log('\n----------Updating %s Domain in Domain_Dict----------' %title)

            Domain.UpdateDomain(title)

            message = 'Updated %s Domain.' %title
            return DevTools(header=header, message=message, file_to_reset=None)

    oc.add(DirectoryObject(key=Callback(DevToolsD, title='recache_default_domains'),
        title='Re-Cache Default Domains',
        summary='Default Domains are pulled from Cached Gist URL. Use to Re-Cache Gist URL.'))
    oc.add(DirectoryObject(key=Callback(DevToolsD, title='Domain_Dict'),
        title='Reset Domain_Dict File',
        summary='Create backup of old Domain_Dict, delete current, create new and fill with fresh domains'))
    for (name, url) in sorted(Common.BaseURLListTuple()):
        oc.add(DirectoryObject(key=Callback(DevToolsD, title=name),
            title='Update %s Domain' %name,
            summary='Update %s Domain Only in the "Domain_Dict" file.' %name))

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

            for dirpath, dirnames, filenames in Core.storage.walk(Core.storage.join_path(Core.bundle_path, 'Contents', 'Resources')):
                for f in filenames:
                    # filter out default files
                    if not Regex('(^icon\-(?:\S+)\.png$|^art\-(?:\S+)\.jpg$)').search(f):
                        fp = Core.storage.join_path(dirpath, f)
                        Core.storage.remove(fp)
            if Dict['cover_files']:
                del Dict['cover_files']

            message = 'Reset Resources Directory, and Deleted Dict[\'cover_files\']'
        elif ( title == 'Anime_cache' or title == 'Cartoon_cache'
            or title == 'Drama_cache' or title == 'Manga_cache' or title == 'Comic_cache' ):
            category = title.split('_')[0]
            Log('\n----------Start Caching all %s Cover Images----------' %category)

            qevent = Thread.Event()  # create new Event object
            qevent.set()
            test = Thread.Create(CacheAllCovers, category=category, qevent=qevent, page=1)
            Log('\n\n%s\n\n' %test)
            message = 'All %s Cover Images are being Cached' %category

        elif title == 'All_cache':
            Log('\n----------Start Caching All Cover Images----------')

            Thread.Create(CacheCoverQ)

            message = 'All Cover Images are being Cached'
        return DevToolsC(header=header, message=message, title=None)

    for (name, url) in [('All', '')] + sorted(Common.BaseURLListTuple()):
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
    for (cat, url) in sorted(Common.BaseURLListTuple()):
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
            return DevToolsBM(header='Hide BM Clear Opts', message=message, title=None)
        elif title == 'All' and Dict['Bookmarks']:
            Log('\n----------Deleting Bookmark section from Channel Dict----------')
            del Dict['Bookmarks']
            Dict.Save()
            message = 'Bookmarks Section Cleaned.'
        elif title and title in Dict['Bookmarks'].keys():
            Log('\n----------Deleting %s Bookmark section from Channel Dict----------' %title)
            del Dict['Bookmarks'][title]
            Dict.Save()
            message = '%s Bookmark Section Cleaned.' %title
        elif not Dict['Bookmarks']:
            Log('\n----------Bookmarks Section Alread Removed----------')
            message = 'Bookmarks Section Already Cleaned.'
        elif not title in Dict['Bookmarks'].keys():
            Log('\n----------%s Bookmark Section Already Removed----------' %title)
            message = '%s Bookmark Section Already Cleaned.' %title
        return DevToolsBM(header='BookmarkTools', message=message, title=None)
    else:
        pass

    oc.add(DirectoryObject(key=Callback(DevToolsBMB),
        title='Backup Tools',
        summary='Manage bookmark backups.'))
    oc.add(DirectoryObject(key=Callback(DevToolsBM, title='hide_bm_clear'),
        title='Toggle Hiding "Clear Bookmarks" Function',
        summary='Hide the "Clear Bookmarks" Function from "My Bookmarks" and sub list. For those of us who do not want people randomly clearing our bookmarks.'))
    for (name, url) in [('All', '')] + sorted(Common.BaseURLListTuple()):
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
@route(PREFIX + '/devtools-bookmarks/backup')
def DevToolsBMB(title=None, header=None, message=None):
    """Tools to Manage Bookmark backups"""

    oc = ObjectContainer(title2='Bookmark Backup Tools', header=header, message=message)

    if title:
        if title == 'create_backup':
            Log('\n----------Creating Bookmark Backup from Current Bookmarks----------')
            cbmb = CreateBMBackup()
            if cbmb:
                message = 'Bookmark Backup Created'
            else:
                message = 'No Bookmarks to Backup yet'
        return DevToolsBMB(header='BookmarkTools', message=message, title=None)

    oc.add(DirectoryObject(key=Callback(DevToolsBMB, title='create_backup'),
        title='Backup Bookmarks',
        summary='Create a Backup file of all bookmarks'))
    oc.add(DirectoryObject(key=Callback(DevToolsBMBList, title='delete_backup'),
        title='Delete Backups',
        summary='Open menu to Delete old bookmark backups'))
    oc.add(DirectoryObject(key=Callback(DevToolsBMBList, title='load_backup'),
        title='Load Bookmarks from Backup',
        summary='Open menu to Load bookmarks from previously created backup file'))

    return oc

####################################################################################################
@route(PREFIX + '/devtools-bookmarks/backup/list')
def DevToolsBMBList(title=None, file_name=None, header=None, message=None):
    """Load/Delete list"""

    oc = ObjectContainer(title2='Load/Delete Backup List', header=header, message=message, no_cache=True)

    if title and file_name:
        if title == 'delete_backup':
            Log('\n----------Remove Bookmark Backup----------')
            fp = Core.storage.join_path(Core.storage.data_path, file_name)
            if Core.storage.file_exists(fp):
                Core.storage.remove(fp)
                message = 'Removed %s Bookmark Backup' %file_name
            else:
                message = '%s file already removed, not removing again' %file_name
        elif title == 'load_backup':
            Log('\n----------Loading Bookmarks from Backup----------')
            new_bookmarks = LoadBMBackup(file_name)
            if new_bookmarks:
                del Dict['Bookmarks']
                Dict['Bookmarks'] = new_bookmarks
                Dict.Save()
                message = 'Replaced Current Bookmarks with %s backup file' %file_name
            else:
                message = 'Error: %s file does not exist' %file_name
        return DevToolsBMB(header='Bookmark Backup Tools', message=message, title=None)

    bmb_list = []
    for dirpath, dirnames, filenames in Core.storage.walk(Core.storage.data_path):
        for f in filenames:
            # filter out default files
            bmb = Regex(r'bookmark_backup_(\d+)\.json').search(f)
            if bmb:
                timestamp = Datetime.FromTimestamp(int(bmb.group(1)))
                bmb_list.append(('Backup %s' %str(timestamp), bmb.group(0)))

    for n, fn in bmb_list:
        oc.add(DirectoryObject(key=Callback(DevToolsBMBList, title=title, file_name=fn),
            title=n,
            summary="%s %s" %(title.split('_')[0].title(), n)
            ))

    if len(oc) > 0:
        return oc
    else:
        message = 'No Bookmark Backups Yet'
        return DevToolsBMB(header='Bookmark Backup Tools', message=message, title=None)

####################################################################################################
def CreateBMBackup():
    """Create bookmark backup from current bookmarks"""

    timestamp = Datetime.TimestampFromDatetime(Datetime.Now())
    bm_bkup_file = Core.storage.join_path(Core.storage.data_path, 'bookmark_backup_%i.json' %timestamp)

    if Dict['Bookmarks']:
        with open(bm_bkup_file, 'wb') as f:
            json.dump(Dict['Bookmarks'], f, indent=4, sort_keys=True, separators=(',', ': '))
        return True
    else:
        Log.Warn('* No Bookmarks to backup yet')
        return False

####################################################################################################
def LoadBMBackup(file_name):
    """load bookmark backup into json format string"""

    fp = Core.stroage.join_path(Core.storage.data_path, file_name)
    if Core.storage.file_exists(fp) and Core.storage.file_size(fp) != 0:
        with open(fp) as data_file:
            data = json.load(data_file)

        return data
    else:
        return False

####################################################################################################
def CacheAllCovers(category, qevent, page=1):
    """Cache All, or any one of the Categories"""

    if category == 'Drama':
        drama_test = True
    else:
        drama_test = False
    base_url = Common.DomainDict[category]
    item_url = base_url + '/%sList?page=%s' % (category, page)

    html = RHTML.ElementFromURL(item_url)

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

            if Common.is_kiss_url(thumb):
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

        if thumb and (not Common.CoverImageFileExist(cover_file)):
            if Common.is_kiss_url(thumb):
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

    if Common.is_kiss_url(image_url):
        content_url = Common.GetBaseURL(image_url) + '/' + image_url.split('/', 3)[3]
        image_file = content_url.rsplit('/')[-1]
    else:
        content_url = image_url
        image_file = image_url.split('/', 3)[3].replace('/', '_')

    path = Core.storage.join_path(Core.bundle_path, 'Contents', 'Resources', image_file)
    Log.Debug('image file path = %s' %path)

    if not Core.storage.file_exists(path):
        if Common.is_kiss_url(content_url):
            r = requests.get(content_url, headers=Headers.GetHeadersForURL(content_url), stream=True)
        else:
            r = requests.get(content_url, stream=True)

        if r.status_code == 200:
            with open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            Log.Debug('* saved image %s' %image_file)
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
            Log.Warn(
                '* %s error code. Polling site too fast. Waiting %f sec then try again, try up to 3 times. Try %i'
                %(r.status_code, timer, count))
            Thread.CreateTimer(interval=timer, f=SaveCoverImage, image_url=content_url, count=count)
        else:
            Log.Debug('* status code for image url = %s' %r.status_code)
            Log.Error('* image url not found | %s' %content_url)
            return None  #replace with "no image" icon later
    else:
        Log.Debug('* file %s already exists' %image_file)
        return image_file

####################################################################################################
@route(PREFIX + '/cftest')
def SetUpCFTest():
    """setup test for cfscrape"""

    if not Dict['cfscrape_test']:
        try:
            cftest = Headers.CFTest()
            Log.Info('*' * 80)
            Log.Info('----------CFTest passed! Aime Cookies:----------')
            Log.Info(cftest)
            Dict['cfscrape_test'] = True
            Dict.Save()
        except Exception as e:
            Dict['cfscrape_test'] = False
            Dict.Save()
            Log.Error('*' * 80)
            Log.Error('----------CFTest Fail----------')
            Log.Error('You need to install a JavaScript Runtime like node.js or equivalent')
            Log.Error('Once JavaScript Runtime installed, Restart channel')
            Log.Error(str(e))
            Log.Error('*' * 80)
    else:
        Log.Debug('* CFTest Previously Passed, not running again.')

    return

####################################################################################################
def RestartChannel():
    """Try to Restart the KissNetwork Channel"""

    try:
        # touch Contents/Code/__init__.py
        plist_path = Core.storage.join_path(Common.BUNDLE_PATH, "Contents", "Info.plist")
        Core.storage.utime(plist_path, None)
        return True
    except Exception as e:
        Log.Error(str(e))
        return False

####################################################################################################
def ClearCache(timeout):
    """Clear old Cached URLs depending on input timeout"""

    cachetime = Datetime.Now()
    count = 0
    Log.Debug('* Clearing Cached URLs older than %s' %str(cachetime - timeout))
    path = Core.storage.join_path(Core.storage.data_path, "DataItems")
    files = [f for f in Core.storage.list_dir(path) if not Core.storage.dir_exists(Core.storage.join_path(path, f))]
    for filename in files:
        item = filename.split('__cachetime__')
        if (Datetime.FromTimestamp(int(item[1])) + timeout) <= cachetime:
            Data.Remove(filename)
            count += 1
    Log.Debug('* Cleaned %i Cached files' %count)
    return count
