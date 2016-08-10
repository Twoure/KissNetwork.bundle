CFTest = SharedCodeService.kissheaders.CFTest
import shutil
import json

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

    Log('\n----------Backing up {} File to {}.backup----------'.format(file_to_reset, file_to_reset))
    file_path = Core.storage.join_path(Core.storage.data_path, file_to_reset)

    if Core.storage.file_exists(file_path):
        # create backup of file being removed
        Core.storage.copy(file_path, file_path + '.backup')
        Log('\n----------Removing {} File----------'.format(file_to_reset))
        Core.storage.remove_tree(file_path)

    if file_to_reset == 'Domain_Dict':
        Domain.CreateDomainDict()
    elif file_to_reset == 'Header_Dict':
        KH.create_dict()

    Log('\n----------Reset {}----------\n----------New values for {} written to:\n{}'.format(file_to_reset, file_to_reset, file_path))

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
                SetUpCFTest('Manga')
                message = 'Reset cfscrape Code Test'
            else:
                message = 'No Dict cfscrape Code Test Key to Remove'
        elif file_to_reset == 'restart_channel':
            Log('\n----------Attempting to Restart KissNetwork Channel----------')
            RestartChannel()
            message = 'Restarting channel'
        elif file_to_reset == 'clear_url_cache':
            Log('\n----------Clearing URL Cache----------')
            count = ClearCache('DataHTTP', Datetime.Delta())
            message = 'Cleaned {} Cached URL files'.format(count)
            Log('\n----------Cleaned {} Cached files----------'.format(count))
        return DevTools(header=header, message=message, file_to_reset=None)

    oc.add(DirectoryObject(key=Callback(DevToolsBM),
        title='Bookmark Tools',
        summary='Tools to Clean dirty bookmarks dictionary, and Toggle "Clear Bookmarks".'))
    oc.add(DirectoryObject(key=Callback(DevToolsC),
        title='Cache Tools',
        summary='Tools to Clean DataItems Cache.'))
    oc.add(DirectoryObject(key=Callback(DevToolsD),
        title='Domain Tools',
        summary='Tools to Reset "Domain_Dict" or Update parts of "Domain_Dict".'))
    oc.add(DirectoryObject(key=Callback(DevToolsH),
        title='Header Tools',
        summary='Tools to Reset "Header_Dict" or Update parts of "Header_Dict".'))
    oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='cfscrape_test'),
        title='Reset Dict cfscrape Test Key',
        summary='Delete previous test key so the channel can re-test the cfscrape code.'))
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
            message = 'Resetting {}. New values for {} will be written soon'.format(title, title)

            return DevToolsH(header=header, message=message, title=None)
        elif ( title == 'Anime' or title == 'Cartoon'
            or title == 'Drama' or title == 'Manga' or title == 'Comic' ):
            Log('\n----------Updating {} Headers in Header_Dict----------'.format(title))

            for (h_name, h_url) in Common.BaseURLListTuple():
                if h_name == title:
                    KH.get_headers_for_url(h_url, update=True)
                    break

            message = 'Updated {} Headers.'.format(title)
            return DevTools(header=header, message=message, file_to_reset=None)

    oc.add(DirectoryObject(key=Callback(DevToolsH, title='Header_Dict'),
        title='Reset Header_Dict File',
        summary='Create backup of old Header_Dict, delete current, create new and fill with fresh headers. Remember Creating Header_Dict takes time, so the channel may timeout on the client while rebuilding.  Do not worry. Exit channel and refresh client. The channel should load normally now.'))
    for name in sorted(Common.TypeTitleList()):
        oc.add(DirectoryObject(key=Callback(DevToolsH, title=name),
            title='Update {} Headers'.format(name),
            summary='Update {} Headers Only in the \"Header_Dict\" file.'.format(name)))

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
            message = 'Resetting {}. New values for {} will be written soon'.format(title, title)

            return DevToolsD(header=header, message=message, title=None)
        elif title == 'recache_default_domains':
            Log('\n----------Re-Caching Default Domains----------')
            Domain.get_domain_dict(True)
            message = 'Default Domains Re-Cached'

            return DevToolsD(header=header, message=message, title=None)
        elif ( title == 'Anime' or title == 'Cartoon'
            or title == 'Drama' or title == 'Manga' or title == 'Comic' ):
            Log('\n----------Updating {} Domain in Domain_Dict----------'.format(title))

            Domain.UpdateDomain(title, True)

            message = 'Updated {} Domain.'.format(title)
            return DevTools(header=header, message=message, file_to_reset=None)

    oc.add(DirectoryObject(key=Callback(DevToolsD, title='recache_default_domains'),
        title='Re-Cache Default Domains',
        summary='Default Domains are pulled from Cached Gist URL. Use to Re-Cache Gist URL.'))
    oc.add(DirectoryObject(key=Callback(DevToolsD, title='Domain_Dict'),
        title='Reset Domain_Dict File',
        summary='Create backup of old Domain_Dict, delete current, create new and fill with fresh domains'))
    for name in sorted(Common.TypeTitleList()):
        oc.add(DirectoryObject(key=Callback(DevToolsD, title=name),
            title='Update {} Domain'.format(name),
            summary='Update {} Domain Only in the \"Domain_Dict\" file.'.format(name)))

    return oc

####################################################################################################
@route(PREFIX + '/devtools-cache')
def DevToolsC(title=None, header=None, message=None):
    """Tools to Remove all Covers/URLs cached files"""

    oc = ObjectContainer(title2='Cache Tools', header=header, message=message)

    if title:
        header = 'Cache Tools'
        if title == 'data_covers':
            count = ClearCache('DataCovers', Datetime.Delta())
            message = 'Cleaned {} Cached Cover files'.format(count)
            Log(u'\n----------Removed {} Cached Cover files from DataCovers----------'.format(count))
        elif title == 'data_http':
            count = ClearCache('DataHTTP', Datetime.Delta())
            message = 'Cleaned {} Cached URL files'.format(count)
            Log(u'\n----------Removed {} Cached URL files from DataHTTP----------'.format(count))
        return DevToolsC(title=None, header=header, message=message)

    oc.add(DirectoryObject(key=Callback(DevToolsC, title='data_covers'),
        title='Reset DataCovers Cache',
        summary='Remove all cached Covers from DataCovers directory.'))
    oc.add(DirectoryObject(key=Callback(DevToolsC, title='data_http'),
        title='Reset DataHTTP Cache',
        summary='Remove all cached URLs from DataHTTP directory.'))

    return oc

####################################################################################################
@route(PREFIX + '/devtools-bookmarks')
def DevToolsBM(title=None, header=None, message=None):
    """Tools to Delete all or certain sections of Bookmarks Dict"""

    oc = ObjectContainer(title2='Bookmark Tools', header=header, message=message)

    if title:
        if title == 'All' and Dict['Bookmarks']:
            Log('\n----------Deleting Bookmark section from Channel Dict----------')
            del Dict['Bookmarks']
            Dict.Save()
            message = 'Bookmarks Section Cleaned.'
        elif title and title in Dict['Bookmarks'].keys():
            Log('\n----------Deleting {} Bookmark section from Channel Dict----------'.format(title))
            del Dict['Bookmarks'][title]
            Dict.Save()
            message = '{} Bookmark Section Cleaned.'.format(title)
        elif not Dict['Bookmarks']:
            Log('\n----------Bookmarks Section Alread Removed----------')
            message = 'Bookmarks Section Already Cleaned.'
        elif not title in Dict['Bookmarks'].keys():
            Log('\n----------{} Bookmark Section Already Removed----------'.format(title))
            message = '{} Bookmark Section Already Cleaned.'.format(title)
        return DevToolsBM(header='BookmarkTools', message=message, title=None)

    oc.add(DirectoryObject(key=Callback(DevToolsBMB),
        title='Backup Tools',
        summary='Manage bookmark backups.'))
    oc.add(DirectoryObject(key=Callback(DevToolsBM, title='hide_bm_clear'),
        title='Toggle Hiding "Clear Bookmarks" Function',
        summary='Hide the "Clear Bookmarks" Function from "My Bookmarks" and sub list. For those of us who do not want people randomly clearing our bookmarks.'))
    for name in ['All'] + sorted(Common.TypeTitleList()):
        if name == 'All':
            oc.add(DirectoryObject(key=Callback(DevToolsBM, title=name),
                title='Reset \"{}\" Bookmarks'.format(name),
                summary='Delete Entire Bookmark Section. Same as \"Clear All Bookmarks\".'))
        else:
            oc.add(DirectoryObject(key=Callback(DevToolsBM, title=name),
                title='Reset \"{}\" Bookmarks'.format(name),
                summary='Delete Entire \"{}\" Bookmark Section. Same as \"Clear {} Bookmarks\".'.format(name, name)))

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
                message = u'Removed {} Bookmark Backup'.format(file_name)
            else:
                message = u'{} file already removed, not removing again'.format(file_name)
        elif title == 'load_backup':
            Log('\n----------Loading Bookmarks from Backup----------')
            new_bookmarks = LoadBMBackup(file_name)
            if new_bookmarks:
                if Dict['Bookmarks']:
                    del Dict['Bookmarks']
                Dict['Bookmarks'] = new_bookmarks
                Dict.Save()
                message = u'Replaced Current Bookmarks with {} backup file'.format(file_name)
            else:
                message = u'Error: {} file does not exist'.format(file_name)
        return DevToolsBMB(header='Bookmark Backup Tools', message=message, title=None)

    bmb_list = list()
    files = [f for f in Core.storage.list_dir(Core.storage.data_path) if not Core.storage.dir_exists(Core.storage.join_path(Core.storage.data_path, f))]
    for filename in files:
        # filter out default files
        bmb = Regex(r'bookmark_backup_(\d+)\.json').search(filename)
        if bmb:
            timestamp = Datetime.FromTimestamp(int(bmb.group(1)))
            bmb_list.append(('Backup {}'.format(str(timestamp)), bmb.group(0)))

    for n, fn in reversed(sorted(bmb_list)):
        oc.add(DirectoryObject(key=Callback(DevToolsBMBList, title=title, file_name=fn),
            title=n,
            summary="{} {}".format(title.split('_')[0].title(), n)
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
    bm_bkup_file = Core.storage.data_item_path('bookmark_backup_{}.json'.format(timestamp))

    if Dict['Bookmarks']:
        with open(bm_bkup_file, 'wb') as f:
            json.dump(Dict['Bookmarks'], f, indent=4, sort_keys=True, separators=(',', ': '))
        return True

    Log.Warn('* No Bookmarks to backup yet')
    return False

####################################################################################################
def LoadBMBackup(filename):
    """load bookmark backup into json format string"""

    filepath = Core.storage.data_item_path(filename)
    if filename and Core.storage.file_exists(filepath) and Core.storage.file_size(filepath) != 0:
        with open(filepath) as datafile:
            data = json.load(datafile)
        return data
    return False

####################################################################################################
@route(PREFIX + '/save-cover-image', count=int)
def SaveCoverImage(image_url, count=0, page_url=None):
    """Save image to Cover Image Path and return the file name"""

    content_url = Common.CorrectCoverImage(image_url)
    if Common.is_kiss_url(image_url):
        image_file = content_url.rsplit('/')[-1]
        type_title = Common.GetTypeTitle(image_url)
    else:
        image_file = image_url.split('/', 3)[3].replace('/', '_')
        type_title = 'Unknow'

    data_covers_type_path = Core.storage.data_item_path(Core.storage.join_path('DataCovers', type_title))
    Core.storage.ensure_dirs(data_covers_type_path)
    path = Core.storage.join_path(data_covers_type_path, image_file)
    Log.Debug('Image File Path = {}'.format(path))

    if not Core.storage.file_exists(path):
        if Common.is_kiss_url(content_url):
            r = requests.get(content_url, headers=KH.get_headers_for_url(content_url), stream=True)
        else:
            r = requests.get(content_url, stream=True)

        if r.status_code == 200:
            with open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            Log.Debug('* Saved {} Image {}'.format(type_title, image_file))
            return (type_title, image_file)
        elif r.status_code == 503 and count < 3:
            count += 1
            timer = float(Util.RandomInt(5,10)) + Util.Random()
            Log.Warn('* 503 Error Code.')
            Log.Warn('* Polling site too fast. Waiting {} sec then try again, try up to 3 times. Try {}.'.format(timer, count))
            Thread.CreateTimer(interval=timer, f=SaveCoverImage, image_url=content_url, count=count)
        elif (r.status_code == 403) and (count < 1):
            Log.Warn('* 403 Error Code.')
            Log.Warn('* Image Offline {}'.format(content_url))
            if page_url:
                Log.Warn('* Trying to Pull down fresh image from {}'.format(page_url))
                html = RHTML.ElementFromURL(page_url)
                try:
                    cover_url = Common.CorrectCoverImage(html.xpath('//head/link[@rel="image_src"]')[0].get('href'))
                    if not 'http' in cover_url: cover_url = None
                except:
                    cover_url = None
                if cover_url:
                    count +=1
                    timer = float(Util.RandomInt(5,10)) + Util.Random()
                    Log.Warn('* Waiting {} sec before trying to Save new Image'.format(timer))
                    Thread.CreateTimer(interval=timer, f=SaveCoverImage, image_url=cover_url, count=count)
                else:
                    Log.Error('* No new cover image within {}'.format(page_url))
                    return None
            else:
                Log.Error('* No Page URL input to parse for new Image')
                return None
        else:
            Log.Debug('* {} Error Code.'.format(r.status_code))
            Log.Error('* Cannot Handle Image {}'.format(content_url))
            return None  #replace with "no image" icon later
    else:
        Log.Debug('* File Already Exists {}'.format(image_file))
        return (type_title, image_file)

####################################################################################################
@route(PREFIX + '/cftest')
def SetUpCFTest(test):
    """setup test for cfscrape"""

    if not Dict['cfscrape_test']:
        try:
            cftest = CFTest(test)
            Log.Info('*' * 80)
            Log.Info('----------CFTest passed! {} Cookies:----------'.format(test))
            Log.Info(cftest)
            Dict['cfscrape_test'] = True
            Dict.Save()
        except Exception as e:
            Dict['cfscrape_test'] = False
            Dict.Save()
            Log.Error('*' * 80)
            Log.Error('----------{} Failed CFTest----------'.format(test))
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
        Core.storage.utime(Core.init_path, None)
        return True
    except Exception as e:
        Log.Error(str(e))
    return False

####################################################################################################
def ClearCache(itemname, timeout):
    """Clear old Cached URLs depending on input timeout"""

    cachetime = Datetime.Now()
    count = 0
    Log.Debug('* Clearing \'{}\' items older than {}'.format(itemname, str(cachetime - timeout)))
    path = Core.storage.data_item_path(itemname)
    Core.storage.ensure_dirs(path)

    for dirpath, dirnames, filenames in Core.storage.walk(path):
        for filename in filenames:
            filepath = Core.storage.join_path(dirpath, filename)
            if (Datetime.FromTimestamp(Core.storage.last_modified(filepath)) + timeout) <= cachetime:
                if Core.storage.dir_exists(filepath):
                    continue
                Core.storage.remove_data_item(filepath)
                count += 1

    Log.Debug('* Cleaned {} Cached files from {}'.format(count, itemname))
    return count

####################################################################################################
def ClearOldCache(itempath):
    """Clean old style of caching"""
    itempath = Core.storage.abs_path(itempath)
    if not Core.storage.file_exists(itempath):
        return False

    files = [f for f in Core.storage.list_dir(itempath) if not Core.storage.dir_exists(Core.storage.join_path(itempath, f))]
    for filename in files:
        if Regex('(^icon\-(?:\S+)\.png$|^art\-(?:\S+)\.jpg$)').search(filename):
            continue
        Core.storage.remove(Core.storage.join_path(itempath, filename))

    Log.Debug('* Finished Resetting \'{}\''.format(itempath))
    return True
