CFTest = SharedCodeService.kheaders.CFTest
import shutil
import json

class BookmarksToolkit(object):
    def __init__(self):
        Route.Connect(PREFIX + '/devtools/bookmarks/gui', self.gui_tools)
        Route.Connect(PREFIX + '/devtools/bookmarks/gui/reset', self.gui_reset)
        Route.Connect(PREFIX + '/devtools/bookmarks/gui/backup/tools', self.gui_backup_tools)
        Route.Connect(PREFIX + '/devtools/bookmarks/gui/backup/create', self.gui_backup_create)
        Route.Connect(PREFIX + '/devtools/bookmarks/gui/backup/remove', self.gui_backup_remove)
        Route.Connect(PREFIX + '/devtools/bookmarks/gui/backup/load', self.gui_backup_load)
        Route.Connect(PREFIX + '/devtools/bookmarks/gui/backup/list/{item}', self.gui_backup_list)
        self.context = dict()
        self.context_reset = list()
        self.context_backup = dict()
        self.context_backup_list = list()
        self.context_list = list()
        self.data_item_path = Core.storage.join_path(Core.storage.data_path, 'DataItems')
        self.old_user_backup_dir = Dict['old_user_bookmark_backup_dir'] if 'old_user_bookmark_backup_dir' in Dict else self.data_item_path

    @property
    def check_user_path(self):
        if Prefs['use_custom_boomark_backup_dir'] and Prefs['bookmark_backup_dir']:
            user_dir = Core.storage.abs_path(Prefs['bookmark_backup_dir'])
            header = "Validate User Bookmark Backup Directory"
            try:
                if Core.storage.file_exists(user_dir):
                    ufolder = Core.storage.join_path(user_dir, BOOKMARK_CACHE_DIR)
                    Core.storage.ensure_dirs(ufolder)
                    self.user_backup_dir = ufolder
                    return True
                else:
                    message = u"User directory '{}' does not exists. Using defaults instead.".format(user_dir)
                    self.context.update({'header': header, 'message': message})
                    Log.Error("* "+message)
            except:
                message = u"User directory '{}' does not have correct permissions. Using defaults instead.".format(user_dir)
                self.context.update({'header': header, 'message': message})
                Log.Exception("* "+message)
        return False

    def migrate_backups(self, path):
        """migrate backups from old_user_path to new directory"""
        src = Core.storage.join_path(self.old_user_backup_dir, BOOKMARK_CACHE_DIR)
        dst = Core.storage.join_path(path, BOOKMARK_CACHE_DIR)
        files = [f for f in Core.storage.list_dir(src) if not Core.storage.dir_exists(Core.storage.join_path(src, f))]
        src_is_default = self.data_item_path == self.old_user_backup_dir
        passed = list()
        for filename in files:
            src_path = Core.storage.join_path(src, filename)
            dst_path = Core.storage.join_path(dst, filename)
            try:
                if src_is_default:
                    # Keep local copy within the default directory
                    Core.storage.copy(src_path, dst_path)
                else:
                    # Move bookmarks from src to dst
                    Core.storage.rename(src_path, dst_path)
                passed.append(True)
            except Exception, e:
                Log.Error(u"* Error: Cannot handle '{}' >>> {}".format(filename, e))
        if len(passed) == len([t for t in passed if t == True]):
            Log(u"* Bookmark Backup Directory migrated from '{}' to '{}'".format(src, dst))
            self.old_user_backup_dir = path
            Dict['old_user_bookmark_backup_dir'] = path
            Dict.Save()

    @property
    def backup_dir(self):
        """setup default path for user backups"""
        folder = Core.storage.data_item_path(BOOKMARK_CACHE_DIR)
        Core.storage.ensure_dirs(folder)
        if self.check_user_path:
            if self.old_user_backup_dir != Core.storage.abs_path(Prefs['bookmark_backup_dir']):
                self.migrate_backups(Core.storage.abs_path(Prefs['bookmark_backup_dir']))
            return self.user_backup_dir
        elif self.old_user_backup_dir != self.data_item_path:
            self.migrate_backups(self.data_item_path)
        return folder

    def gui_tools(self):
        self.check_user_path
        oc = ObjectContainer(title2='Bookmark Tools', header=self.context.get('header', None), message=self.context.get('message', None), no_cache=True)
        self.context.clear()
        oc.add(DirectoryObject(key=Callback(self.gui_backup_tools),
            title="Backup Tools", summary="Manage bookmark backups."))
        for name in ['All'] + sorted(KCore.util.tt_list):
            name2 = '\"' + name + '\"'
            if name == 'All':
                name2 = ''
            self.context_reset.append({'item': name})
            oc.add(DirectoryObject(key=Callback(self.gui_reset, item=name),
                title='Reset \"{}\" Bookmarks'.format(name),
                summary='Delete Entire {} Bookmark Section. Same as \"Clear {} Bookmarks\".'.format(name2, name)))
        return oc

    def gui_reset(self, item):
        if not self.reset(item):
            Log("* Unable to reset '{}'".format(item))
        return self.gui_tools()

    def reset(self, item):
        header = 'BookmarkTools'
        if not self.context_reset:
            Log("* Unable to reset Bookmark '{}', because the context does not exists".format(item))
            return False

        if not Dict['Bookmarks']:
            Log("* No Bookmarks Dict Yet. Skipping Reset '{}'".format(item))
            return False

        for i, c in enumerate(self.context_reset):
            if item in c.values() and Dict['Bookmarks']:
                Log("* Removing '{}' Bookmarks".format(item))
                if item == 'All':
                    del Dict['Bookmarks']
                    message = 'Bookmarks Section Cleaned.'
                elif item in Dict['Bookmarks']:
                    del Dict['Bookmarks'][item]
                    message = '{} Bookmark Section Cleaned.'.format(item)
                Dict.Save()
                self.context.update({'header': header, 'message': message})
                self.context_reset.pop(i)
                return True
        Log("* Unable to reset Bookmark '{}', because it does not exists".format(item))
        return False

    def gui_backup_tools(self):
        """
        Tools to Manage Bookmark backups
        Create, Delete (from list), Load (from list)
        """
        self.backup_saved = False
        oc = ObjectContainer(title2='Backup Tools', header=self.context_backup.get('header', None), message=self.context_backup.get('message', None), no_cache=True)
        self.context_backup.clear()
        oc.add(DirectoryObject(key=Callback(self.gui_backup_create),
            title='Backup Bookmarks',
            summary='Create a Backup file of all bookmarks'))
        oc.add(DirectoryObject(key=Callback(self.gui_backup_list, item='remove'),
            title='Delete Backups',
            summary='Open menu to Delete old bookmark backups'))
        oc.add(DirectoryObject(key=Callback(self.gui_backup_list, item='load'),
            title='Load Bookmarks from Backup',
            summary='Open menu to Load bookmarks from previously created backup file'))
        return oc

    def gui_backup_create(self):
        if not self.backup_save():
            Log("* Cannot backup current bookmarks")
        return self.gui_backup_tools()

    def backup_save(self, basename=None, silent=False, auto=False):
        """Create bookmark backup from current bookmarks"""
        if self.backup_saved:
            self.context_backup.clear()
            return True

        timestamp = int(Datetime.TimestampFromDatetime(Datetime.Now()))
        basename = basename + '_' if basename else ''
        bkup_filename = u'{}bookmark_backup_{}.json'.format(basename, timestamp)
        bkup_file = Core.storage.join_path(self.backup_dir, bkup_filename)

        if Dict['Bookmarks']:
            with open(bkup_file, 'wb') as f:
                json.dump(Dict['Bookmarks'], f, indent=4, sort_keys=True, separators=(',', ': '))
            self.backup_saved = True
            message = "New Backup Created '{}'".format(bkup_filename)
            Log('* '+message)
            if not silent:
                self.context_backup.update({'header': 'Backup Tools', 'message': message})
            return True

        Log.Warn(u"* Failed to create backup for '{}'".format(bkup_filename))
        return False

    def gui_backup_list(self, item):
        """List backups to remove/load"""

        header = "{} Backup".format(item.title())
        if not self.backup_list:
            message = "No backups to list"
            Log(message)
            self.context_backup.update({'header': header, 'message': message})
            return self.gui_backup_tools()

        oc = ObjectContainer(title2=header, no_cache=True)
        func = self.gui_backup_remove if item == 'remove' else self.gui_backup_load
        for n, fn in reversed(sorted(self.backup_list)):
            oc.add(DirectoryObject(key=Callback(func, item=fn),
                title=n, summary=u"{} '{}'".format(item.title(), n)
                ))
        return oc

    @property
    def backup_list(self):
        backup_list = list()
        self.context_backup_list = list()
        self.context_backup_dict = list()
        folder = self.backup_dir
        files = [f for f in Core.storage.list_dir(folder) if not Core.storage.dir_exists(Core.storage.join_path(folder, f))]
        for filename in files:
            bmb = Regex(r'(?:\w+\_)?bookmark\_backup\_(\d+)\.json').search(filename)
            abmb = Regex(r'\w+\_bookmark\_backup_(\d+)\.json').search(filename)
            if bmb:
                timestamp = Datetime.FromTimestamp(int(bmb.group(1)))
                backup_list.append(('{}Backup {}'.format('Auto-' if abmb else '', timestamp), filename))
                self.context_backup_list.append(filename)
            if abmb:
                self.context_backup_dict.append({'filename': filename, 'datetime': Datetime.FromTimestamp(int(abmb.group(1)))})
        return backup_list

    def gui_backup_remove(self, item):
        if not self.backup_remove(item):
            Log(u"* Cannot remove backup for '{}'".format(item))
        return self.gui_backup_tools()

    def backup_remove(self, item, silent=False):
        if item not in self.context_backup_list:
            self.context_backup.clear()
            return False

        filepath = Core.storage.join_path(self.backup_dir, item)
        if Core.storage.file_exists(filepath):
            Core.storage.remove(filepath)
            self.context_backup_list.remove(item)
            message = u'Removed {} Bookmark Backup'.format(item)
            if not silent:
                self.context_backup.update({'header': 'Removed Backup', 'message': message})
            Log('* '+message)
        else:
            Log("* Not removing. Backup '{}' no longer exists.".format(item))
        return True

    def gui_backup_load(self, item):
        if not self.backup_load(item):
            Log("* Unable to load backup for '{}'".format(item))
        return self.gui_backup_tools()

    def backup_load(self, item):
        if item not in self.context_backup_list:
            self.context_backup.clear()
            return False

        if not self.load(item):
            Log(u"* Cannot load '{}'".format(item))
            return False

        if Dict['Bookmarks']:
            del Dict['Bookmarks']
        Dict['Bookmarks'] = self.backup_data
        Dict.Save()

        self.context_backup_list.remove(item)
        message = u'Replaced Current Bookmarks with {} backup file'.format(item)
        self.context_backup.update({'header': 'Loaded Bookmakrs', 'message': message})
        Log('* '+message)
        return True

    def load(self, item):
        self.backup_data = dict()
        filepath = Core.storage.join_path(self.backup_dir, item)
        if item and Core.storage.file_exists(filepath) and (Core.storage.file_size(filepath) != 0):
            with open(filepath, 'rb') as datafile:
                self.backup_data = json.load(datafile)
        return bool(self.backup_data)

    def auto_backup(self):
        """
        Create backup of bookmarks everytime channel starts
        Only keep last 5 Auto backups
        """
        auto_backup_limit = 5
        Log("* Managing Auto Bookmark Backups")
        Log("* Keeping latest {} Auto Backups".format(auto_backup_limit))
        self.backup_saved = False
        if not self.backup_save('auto', True):
            Log("* Cannot auto backup current bookmarks")
            return

        if not self.backup_list:
            Log("* No backups to manage")
            return
        elif not self.context_backup_dict:
            Log("* No context dict list to manage")
            return

        Util.SortListByKey(self.context_backup_dict, 'datetime')
        count = 0
        while (len(self.context_backup_dict) > auto_backup_limit) and (count < 10):
            count += 1
            self.backup_remove(self.context_backup_dict[0]['filename'], True)
            self.context_backup_dict.pop(0)
        return

BookmarkTools = BookmarksToolkit()
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
        Core.storage.remove(file_path)

    if file_to_reset == 'Domain_Dict':
        KCore.domain.create_dict()
    elif file_to_reset == 'Header_Dict':
        Headers.create_dict()

    Log('\n----------Reset {}----------\n----------New values for {} written to:\n{}'.format(file_to_reset, file_to_reset, file_path))

    return file_path

####################################################################################################
@route(PREFIX + '/devtools')
def DevTools(file_to_reset=None, header=None, message=None):
    """
    Includes "Bookmark Tools", "Header Tools" and "Cache Tools"
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
        elif file_to_reset == 'temp_upgrade':
            Log('\n----------Attempting to Upgrade Cartoon Section----------')
            message = UpgradeTemp()
        return DevTools(header=header, message=message, file_to_reset=None)

    if not Dict['kimcartoon_upgrade']:
        oc.add(DirectoryObject(key=Callback(DevTools, file_to_reset='temp_upgrade'),
            title='-->Cartoon Upgrade<--',
            summary='Run before using New KimCartoon temp source for Cartoons.'))
    oc.add(DirectoryObject(key=Callback(BookmarkTools.gui_tools),
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

            for (h_name, h_url) in KCore.util.base_url_list_tuple:
                if h_name == title:
                    Headers.get_headers_for_url(h_url, update=True)
                    break

            message = 'Updated {} Headers.'.format(title)
            return DevTools(header=header, message=message, file_to_reset=None)

    oc.add(DirectoryObject(key=Callback(DevToolsH, title='Header_Dict'),
        title='Reset Header_Dict File',
        summary='Create backup of old Header_Dict, delete current, create new and fill with fresh headers. Remember Creating Header_Dict takes time, so the channel may timeout on the client while rebuilding.  Do not worry. Exit channel and refresh client. The channel should load normally now.'))
    for name in sorted(KCore.util.tt_list):
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
            KCore.domain.fetch(True)
            message = 'Default Domains Re-Cached'

            return DevToolsD(header=header, message=message, title=None)
        elif ( title == 'Anime' or title == 'Cartoon'
            or title == 'Drama' or title == 'Manga' or title == 'Comic' ):
            Log('\n----------Updating {} Domain in Domain_Dict----------'.format(title))

            KCore.domain.update(title, True)

            message = 'Updated {} Domain.'.format(title)
            return DevTools(header=header, message=message, file_to_reset=None)

    oc.add(DirectoryObject(key=Callback(DevToolsD, title='recache_default_domains'),
        title='Re-Cache Default Domains',
        summary='Default Domains are pulled from Cached Gist URL. Use to Re-Cache Gist URL.'))
    oc.add(DirectoryObject(key=Callback(DevToolsD, title='Domain_Dict'),
        title='Reset Domain_Dict File',
        summary='Create backup of old Domain_Dict, delete current, create new and fill with fresh domains'))
    for name in sorted(KCore.util.tt_list):
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
            count = ClearCache(THUMB_CACHE_DIR, Datetime.Delta())
            message = 'Cleaned {} Cached Cover files'.format(count)
            Log(u'\n----------Removed {} Cached Cover files from {}----------'.format(count, THUMB_CACHE_DIR))
        elif title == 'data_http':
            count = ClearCache(URL_CACHE_DIR, Datetime.Delta())
            message = 'Cleaned {} Cached URL files'.format(count)
            Log(u'\n----------Removed {} Cached URL files from {}----------'.format(count, URL_CACHE_DIR))
        elif title == 'zip_cache':
            message = ZipCache()
        return DevToolsC(title=None, header=header, message=message)

    oc.add(DirectoryObject(key=Callback(DevToolsC, title='data_covers'),
        title=u'Reset {} Cache'.format(THUMB_CACHE_DIR),
        summary=u'Remove all cached Covers from {} directory.'.format(THUMB_CACHE_DIR)))
    oc.add(DirectoryObject(key=Callback(DevToolsC, title='data_http'),
        title=u'Reset {} Cache'.format(URL_CACHE_DIR),
        summary=u'Remove all cached URLs from {} directory.'.format(URL_CACHE_DIR)))
    oc.add(DirectoryObject(key=Callback(DevToolsC, title='zip_cache'),
        title=u'Zip Cache',
        summary=u'Copy URL & RKS cache into zip file.'))

    return oc

####################################################################################################
def MoveOldBookmarks():
    """move old bookmarks into new directory"""

    count = 0
    old_dir = Core.storage.data_path
    new_dir = Core.storage.data_item_path(BOOKMARK_CACHE_DIR)
    Core.storage.ensure_dirs(new_dir)

    old_files = [f for f in Core.storage.list_dir(old_dir) if Regex(r'bookmark_backup_(\d+)\.json').search(f) and not Core.storage.dir_exists(Core.storage.join_path(old_dir, f))]
    for filename in old_files:
        old_filepath = Core.storage.join_path(old_dir, filename)
        new_filepath = Core.storage.join_path(new_dir, filename)
        if not Core.storage.file_exists(new_filepath):
            Core.storage.copy(old_filepath, new_filepath)
        else:
            Log(u"* Skipped moving '{}' because it already exists within '{}'".format(filename, BOOKMARK_CACHE_DIR))

        if Core.storage.file_exists(new_filepath) and (Core.storage.file_size(new_filepath) != 0):
            count += 1
            Core.storage.remove(old_filepath)

    if count == 0:
        Log('* No Old Bookmarks to Migrate')
    else:
        Log(u"* Finished Migrating '{}' Old Bookmarks to '{}'".format(count, new_dir))
    return

####################################################################################################
@route(PREFIX + '/save-cover-image', count=int)
def SaveCoverImage(image_url, count=0, page_url=None):
    """Save image to Cover Image Path and return the file name"""

    content_url = KCore.util.correct_cover_image(image_url)
    if KCore.util.is_kiss_url(image_url):
        image_file = content_url.rsplit('/')[-1]
        type_title = KCore.util.get_tt(image_url)
    else:
        image_file = image_url.split('/', 3)[3].replace('/', '_')
        type_title = 'Unknow'

    data_covers_type_path = Core.storage.data_item_path(Core.storage.join_path(THUMB_CACHE_DIR, type_title))
    Core.storage.ensure_dirs(data_covers_type_path)
    path = Core.storage.join_path(data_covers_type_path, image_file)
    Log.Debug('Image File Path = {}'.format(path))

    if not Core.storage.file_exists(path):
        if KCore.util.is_kiss_url(content_url):
            r = requests.get(content_url, headers=Headers.get_headers_for_url(content_url), stream=True)
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
            Log.Warn('* HTTP 503 Error: Either cookies need to be refreshed or site is offline.')
            return None
            #Log.Warn('* Polling site too fast. Waiting {} sec then try again, try up to 3 times. Try {}.'.format(timer, count))
            #Thread.CreateTimer(interval=timer, f=SaveCoverImage, image_url=content_url, count=count)
        elif (r.status_code == 403) and (count < 1):
            Log.Warn('* 403 Error Code.')
            Log.Warn('* Image Offline {}'.format(content_url))
            if page_url:
                Log.Warn('* Trying to Pull down fresh image from {}'.format(page_url))
                html = RHTML.ElementFromURL(page_url)
                try:
                    cover_url = KCore.util.correct_cover_image(html.xpath('//head/link[@rel="image_src"]')[0].get('href'))
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
        except:
            Dict['cfscrape_test'] = False
            Dict.Save()
            Log.Error('*' * 80)
            Log.Exception('----------{} Failed CFTest----------'.format(test))
            Log.Error('*' * 80)
    return

####################################################################################################
def RestartChannel():
    """Try to Restart the KissNetwork Channel"""

    try:
        # touch Contents/Info.plist
        Core.storage.utime(Core.plist_path, None)
        return True
    except:
        Log.Exception('* Failed to Restart KissNetwork')
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
        if Regex(r'^((?:icon|art)\-\S+\.(?:png|jpg))$').search(filename):
            continue
        Core.storage.remove(Core.storage.join_path(itempath, filename))

    Log.Debug('* Finished Resetting \'{}\''.format(itempath))
    return True

####################################################################################################
def ZipCache():
    """copy cached resources into zip folder, then move to resources directory"""
    rks_dir = Core.storage.data_item_path(KCore.cache.rks_cache_dir)
    http_dir = Core.storage.data_item_path(KCore.cache.url_cache_dir)
    zip_dir = Core.storage.data_item_path(KCore.cache.zip_cache_dir)
    log_dir = Core.storage.join_path(zip_dir, "Logs")

    # clean zip_dir before copying in new files
    Core.storage.remove_tree(zip_dir)

    # copy DataHTTP into zip dir
    KCore.storage.copytree(http_dir, Core.storage.join_path(zip_dir, KCore.cache.url_cache_dir))
    # copy DataRKS into zip dir
    KCore.storage.copytree(rks_dir, Core.storage.join_path(zip_dir, KCore.cache.rks_cache_dir))

    # clean user-ip from DataHTTP files
    for fn in Core.storage.list_dir(Core.storage.join_path(zip_dir, KCore.cache.url_cache_dir)):
        fn_tpath = Core.storage.join_path(KCore.cache.zip_cache_dir, KCore.cache.url_cache_dir, fn)
        Log(u"* Cleaning Public IP from '{}'".format(fn_tpath))
        fn_data = Data.Load(fn_tpath) # open file as string
        # clean public ip
        fn_data = Regex(r"'\d+\.\d+\.\d+\.\d+\-\d+'").sub("'xxx.xxx.xxx.xxx-xxxxxxxxx'", fn_data)
        Data.Save(fn_tpath, fn_data) # re-save cleaned file in zip cache location

    # copy kissnetwork logs
    Core.storage.ensure_dirs(log_dir)
    for l in KCore.logs.logs_for_identifier(Core.identifier):
        # copy kissnetwork logs into zip dir
        Core.storage.copy(l, log_dir)

    # we need the system logs as well
    for l in KCore.logs.logs_for_identifier('com.plexapp.system'):
        Core.storage.copy(l, log_dir)

    zip_filename = 'KissNetwork_cache_' + Datetime.Now().strftime("%Y%m%d-%H%M%S") + '.zip'

    # create and save zip file from zip dir
    zip_filepath = KCore.storage.compress(zip_filename, zip_dir)

    # move final zip file to channel resources directory, make easier for user to find.
    res_dir = Core.storage.join_path(Core.bundle_path, 'Contents', 'Resources')
    try:
        Core.storage.rename(zip_filepath, Core.storage.join_path(res_dir, zip_filename))
        message = 'Copied Video Page cache to Zip file'
    except IOError as e:
        Log.Error("* ZipCache[IOError]: {}".format(e))
        message = u"Error 'Permission denied'. Zipfile left in {}".format(zip_filepath)
    except Exception as e:
        Log.Error("* ZipCache[Exception]: {}".format(e))
        message = u"Error '{}'. Zipfile left in {}".format(e, zip_filepath)

    # TODO add way to clean zip cache in Resources dir?

    return message

####################################################################################################
def UpgradeTemp():
    """Temp update procedure between v1.2.9 and v1.3.0"""

    msl = list()
    # first update cartoon domain
    try:
        KCore.domain.update('Cartoon', True)
        msl.append("Domain")
    except:
        Log.Exception("* <DevTools.UpgradeTemp[error][0]>: Cannot setup new domain >>>")
        return "Error: Failed to update Cartoon Domain"
    # 2nd update cartoon header
    try:
        Headers.get_headers_for_url(KCore.util.base_url('Cartoon'), True)
        msl.append("Header")
    except:
        Log.Exception("* <DevTools.UpgradeTemp[error][1]>: Cannot setup new header >>>")
        return "Error: Failed to update Cartoon Header"
    # once finished, tell user to access Cartoon bookmarks, so the covers can update ?
    if msl:
        Dict['kimcartoon_upgrade'] = True
        Dict.Save()
        return "Finished updating Cartoon " + ' & '.join(msl) + '. '
    return "Warn: Did not Update"
