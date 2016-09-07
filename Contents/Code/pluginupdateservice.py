#!/usr/bin/env python
# Plugin Update Service Code
#------------------------------------------------------------
# Code modified from installservice.py and bundleservice.py
#------------------------------------------------------------
# Twoure - 09/07/2016

from os.path import split as split_path
import shutil

#CHECK_INTERVAL              = CACHE_1MINUTE * 5  # cache Github request URL for 5 mins. ONLY for testing
CHECK_INTERVAL              = CACHE_1HOUR * 12  # cache Github request URL for 12 hours
HISTORY_KEY                 = u"_{}:History"
IDENTIFIER_KEY              = "InstallIdentifier"
NOTES_KEY                   = "InstallNotes"
DATE_KEY                    = "InstallDate"
VERSION_KEY                 = "InstallVersion"
ACTION_KEY                  = "InstallAction"
BRANCH_KEY                  = "InstallBranch"
TAG_KEY                     = "InstallTag"

class BundleInfo(object):
    def __init__(self, plugin_path):
        self.path = plugin_path
        self.bundled = Core.bundled_plugins_path in plugin_path if Core.bundled_plugins_path is not None else False
        self.load_plist()

    def load_plist(self):
        plist = Plist.ObjectFromString(Core.storage.load(Core.storage.join_path(self.path, "Contents", "Info.plist")))
        self.service_dict = Core.services.get_services_from_bundle(self.path, plist)
        self.identifier = plist['CFBundleIdentifier']
        self.version = plist['CFBundleVersion'] if 'CFBundleVersion' in plist else None
        self.bundle_class = plist['PlexPluginClass'].lower() if 'PlexPluginClass' in plist else 'content'
        self.ignore = 'PlexPluginDevMode' in plist and plist['PlexPluginDevMode'] == '1'
        self.plugin_class = plist.get('PlexPluginClass', 'Channel')

        if self.plugin_class == 'Agent':
            self.ignore = True

        if Core.storage.link_exists(self.path):
            Log("Plug-in bundle with identifier '%s' is a symbolic link, and will be ignored.", self.identifier)
            self.ignore = True

    @property
    def has_services(self):
        for key in ('Services', 'ServiceSets', 'OldServices'):
            for service_type in self.service_dict[self.identifier][key]:
                if len(self.service_dict[self.identifier][key][service_type]) > 0:
                    return True
        return False


class PluginUpdateService(object):
    def __init__(self):
        self.bundle_name = self.splitall(Core.bundle_path)[-1]
        self.name = self.bundle_name.split('.bundle')[0]
        Log(u"Starting the {} Install Service".format(self.name))

        self.plugins_path = Core.storage.join_path(Core.app_support_path, 'Plug-ins')
        self.bundle = BundleInfo(Core.bundle_path)
        self.identifier = self.bundle.identifier
        self.stage = Core.storage.data_item_path('Stage')
        self.stage_path = Core.storage.join_path(self.stage, self.identifier)
        self.inactive = Core.storage.data_item_path('Deactivated')
        self.archive_url = u'https://github.com/{}/archive/{}.zip'
        self.commits_url = u'https://api.github.com/repos/{}/commits/{}'
        self.release_url = u'https://api.github.com/repos/{}/releases/{}'
        self.temp_info = dict()
        self.update_info = dict()
        self.current_info = dict()

        try:
            Core.storage.remove_tree(self.stage)
        except:
            Log.Error("Unalbe to remove staging root")
        Core.storage.make_dirs(self.stage)

        try:
            Core.storage.remove_tree(self.inactive)
        except:
            Log.Error("Unable to remove inactive root")
        Core.storage.make_dirs(self.inactive)

        if HISTORY_KEY.format(self.name) in Dict:
            self.history = Dict[HISTORY_KEY.format(self.name)]
        else:
            self.history = list()
        self.history_lock = Thread.Lock()

        self.setup_current_info()

    def info_record(self, action, branch='master', tag=None, version=None, notes=None):
        info = dict()
        info[IDENTIFIER_KEY] = self.identifier
        info[DATE_KEY] = Datetime.Now()
        info[ACTION_KEY] = action
        info[BRANCH_KEY] = branch
        if notes:
            info[NOTES_KEY] = notes
        if tag:
            info[TAG_KEY] = tag
        if version:
            info[VERSION_KEY] = version
        return info

    def add_history_record(self, action, branch='master', tag=None, version=None, notes=None):
        info = self.info_record(action, branch, tag, version, notes)
        try:
            self.history_lock.acquire()
            self.history.append(info)
            Dict[HISTORY_KEY.format(self.name)] = self.history
            Dict.Save()
        finally:
            self.history_lock.release()

    def read_history_record(self):
        ident_history = list()
        for item in self.history:
            if item[IDENTIFIER_KEY] == self.identifier:
                ident_history.append(item)
        return ident_history

    def read_last_history_record(self):
        record = self.read_history_record()
        if not record:
            return False
        record.reverse()
        return record[0]

    def setup_current_info(self):
        self.current_info.clear()
        record = self.read_last_history_record()
        if record:
            self.current_info.update({'date': record[DATE_KEY], 'branch': record[BRANCH_KEY]})
            if NOTES_KEY in record.keys():
                self.current_info.update({'notes': record[NOTES_KEY]})
            if VERSION_KEY in record.keys():
                self.current_info.update({'version': record[VERSION_KEY]})
            if TAG_KEY in record.keys():
                self.current_info.update({'tag': record[TAG_KEY]})
        return bool(self.current_info)

    def splitall(self, path):
        allparts = list()
        while True:
            parts = split_path(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts

    def copytree(self, src, dst):
        if not Core.storage.file_exists(dst):
            Log(u"Creating dir at '{}'".format(dst))
            Core.storage.make_dirs(dst)
        Log(u"Recursively copying contents of '{}' into '{}'".format(src, dst))
        for item in Core.storage.list_dir(src):
            s = Core.storage.join_path(src, item)
            d = Core.storage.join_path(dst, item)
            if Core.storage.dir_exists(s):
                Log(u"Copying '{}' into '{}'".format(s, d))
                self.copytree(s, d)
            else:
                Log(u"Copying with copy2 '{}' into '{}'".format(s, d))
                shutil.copy2(s, d)

    def datetime_to_utc(self, dt):
        n = Datetime.Now().replace(microsecond=0)
        nutc = Datetime.UTCNow().replace(microsecond=0)
        if n < nutc:
            return dt + (nutc - n)
        elif n == nutc:
            return dt
        return dt - (n - nutc)

    @property
    def setup_stage(self):
        Log(u"Setting up staging area for {} at {}".format(self.identifier, self.stage_path))
        Core.storage.remove_tree(self.stage_path)
        Core.storage.make_dirs(self.stage_path)
        return self.stage_path

    def unstage(self):
        Log(u"Unstaging files for {} (removing {})".format(self.identifier, self.stage_path))
        Core.storage.remove_tree(self.stage_path)

    def cleanup(self):
        inactive_path = Core.storage.join_path(self.inactive, self.identifier)
        if Core.storage.dir_exists(inactive_path):
            Log(u"Cleaning up after {} (removing {})".format(self.identifier, inactive_path))
            Core.storage.remove_tree(inactive_path)

    def clean_old_bundle(self):
        stage_paths = list()
        root = self.bundle_name
        stage_path = self.stage_path.lstrip('\\\?')
        bundle_path = Core.storage.abs_path(self.bundle.path).lstrip('\\\?')
        stage_index = int([i for i, l in enumerate(self.splitall(stage_path)) if l == self.identifier][1])
        bundle_index = int([i for i, l in enumerate(self.splitall(bundle_path)) if l == root][0])

        for dirpath, dirname, filenames in Core.storage.walk(stage_path):
            for f in filenames:
                filepath = Core.storage.join_path(stage_path, dirpath, f).lstrip('\\\?')
                filepaths = self.splitall(filepath)[stage_index:]
                stage_paths.append(Core.storage.join_path(root, *filepaths[1:]))

        for dirpath, dirname, filenames in Core.storage.walk(bundle_path):
            for f in filenames:
                filepath = Core.storage.join_path(bundle_path, dirpath, f).lstrip('\\\?')
                filepaths = self.splitall(filepath)[bundle_index:]
                if Core.storage.join_path(root, *filepaths[1:]) not in stage_paths:
                    old_item_path = Core.storage.abs_path(Core.storage.join_path(self.plugins_path, root, *filepaths[1:]))
                    Log(u"File/Folder does not exists in current Version.  Attempting to remove '{}'".format(old_item_path))
                    try:
                        if Core.storage.dir_exists(old_item_path):
                            Core.storage.remove_tree(old_item_path)
                        elif Core.storage.file_exists(old_item_path):
                            Core.storage.remove(old_item_path)
                        else:
                            Log.Warn(u"Cannot Remove Old '{}' file/folder, does not exists.".format(old_item_path))
                    except:
                        Log.Exception(u"Error Removing Old '{}' file/folder".format(old_item_path))

    def activate(self, fail_count=0):
        final_path = Core.storage.join_path(self.plugins_path, self.bundle_name)

        if not Core.storage.dir_exists(self.stage_path):
            Log(u"Unable to find stage for {}".format(self.identifier))
            return False

        Log(u"Activating a new installation of {}".format(self.identifier))
        try:
            if not Core.storage.dir_exists(final_path):
                Core.storage.rename(self.stage_path, final_path)
            else:
                self.copytree(self.stage_path, final_path)
        except:
            Log.Exception(u"Unable to activate {} at {}".format(self.identifier, final_path))
            if fail_count < 5:
                Log.Info("Waiting 2s and trying again")
                Thread.Sleep(2)
                return self.activate(fail_count + 1)
            else:
                Log.Info("Too many failures - returning")
                return False
        return True

    def install_zip_from_url(self, url):
        stage_path = self.setup_stage
        try:
            archive = Archive.Zip(HTTP.Request(url, cacheTime=0))
        except:
            Log(u"Unable to download archive for {}".format(self.identifier))
            self.unstage()
            return False

        if archive.Test() != None:
            Log(u"The archive of {} is invalid - unable to continue".format(self.identifier))
            self.unstage()
            return False

        try:
            for archive_name in archive:
                parts = archive_name.split('/')[1:]

                if parts[0] == '' and len(parts) > 1:
                    parts = parts[1:]

                if len(parts) > 1 and parts[0] == 'Contents' and len(parts[-1]) > 0 and parts[-1][0] != '.':
                    file_path = Core.storage.join_path(stage_path, *parts)
                    dir_path = Core.storage.join_path(stage_path, *parts[:-1])

                    if not Core.storage.dir_exists(dir_path):
                        Core.storage.make_dirs(dir_path)
                    Core.storage.save(file_path, archive[archive_name])
                    Log(u"Extracted {} to {} for {}".format(parts[-1], dir_path, self.identifier))
                else:
                    Log(U"Not extracting {}".format(archive_name))

        except:
            Log(u"Error extracting archive of {}".format(self.identifier))
            Log(Plugin.Traceback())
            self.unstage()
            return False

        finally:
            archive.Close()

        self.clean_old_bundle()
        if not self.activate():
            Log.Critical(u"Unable to activate {}".format(self.identifier))
            self.unstage()
            return False

        self.unstage()
        self.cleanup()

        return True

    def install(self, url, action, branch='master', tag=None, version=None, notes=None):
        Log(u"Preforming Update of {}".format(self.identifier))

        if not self.install_zip_from_url(url):
            return False

        # add install info to history record
        self.add_history_record(action, branch, tag, version, notes)

        # Check whether this bundle contains services & instruct it to reload if necessary
        #if self.bundle.has_services:
            #self.reload_services()

        Log("Installation of {} complete".format(self.identifier))
        return True

    def get_install_info(self, repo, branch='master', tag=None):
        url = self.release_url.format(repo, tag) if tag else self.commits_url.format(repo, branch)
        Log(u"Fetching {} update info from '{}'".format(self.identifier, url))
        Log(u"CHECK_INTERVAL = '{}'".format(Datetime.Delta(seconds=CHECK_INTERVAL)))
        try:
            info = JSON.ObjectFromURL(url, cacheTime=CHECK_INTERVAL, timeout=5)
            if tag:
                date = Datetime.ParseDate(info['published_at'][:-1], "%Y-%m-%dT%H:%M:%S")
                message = info['body']
                zipId = info['tag_name']
                version = zipId
            else:
                date = Datetime.ParseDate(info['commit']['author']['date'][:-1], "%Y-%m-%dT%H:%M:%S")
                message = info['commit']['message']
                zipId = branch
                version = str(date)
            self.temp_info.update({'date': date, 'notes': message, 'branch': branch, 'zipId': zipId, 'version': version})
            Log("Successfully retrieved Github info >>>")
            Log(u"branch='{}', date='{}', version='{}', zipId='{}'".format(
                self.temp_info['branch'], self.temp_info['date'], self.temp_info['version'], self.temp_info['zipId']))
        except:
            Log.Exception(u"Error retrieving {} Github info from {}".format(self.identifier, url))
            return False
        return bool(self.temp_info)

    def is_update_available(self, repo, branch='master', tag=None):
        if not self.get_install_info(repo, branch, tag):
            Log(u"Unable to check update {} because it has no {}".format(self.identifier, 'releases' if tag else 'commits'))
            return False

        if not self.temp_info:
            Log(u"Unable to check update {} because temp_info is empty".format(self.identifier))
            return False

        if 'init_run' in Dict:
            date = Dict['init_run']
        else:
            date = Datetime.UTCNow().replace(microsecond=0)
            Dict['init_run'] = date
            Dict.Save()

        #Log(u"Is Repo datetime '{}' > init_run datetime '{}'? If so then present the update function".format(self.temp_info['date'], date))
        #Log(u"Current Contents of update_info = '{}'".format(self.update_info))

        if self.temp_info['date'] > date:
            self.update_info.update(self.temp_info.copy())
        return bool(self.update_info)

    def update(self, repo, branch='master', tag=None):
        if not self.update_info:
            try: return ObjectContainer(header=u'{}'.format(L('updater.error')), message=u'Unable to install Update')
            except: return

        url = self.archive_url.format(repo, branch if tag == branch else tag)
        tag = tag if tag != branch else None
        version = self.update_info['version']
        action = 'Preform Update'
        if not self.install(url, action, branch, tag, version, self.update_info['notes']):
            try: return ObjectContainer(header=u'{}'.format(L('updater.error')), message=u'Unable to install Update')
            except: return

        # cleanup dict info
        self.update_info.clear()
        self.temp_info.clear()

        Log(u"Update of {} to {} complete".format(self.identifier, version))
        self.restart_channel()
        try: return ObjectContainer(header=u'{}'.format(L('updater.success')), message=u'%s' % F('updater.updated', version))
        except: return

    def reload_services(self):
        """Reload this channels Service Code"""
        try:
            Log(u"Plug-in {} is currrently running with old service code - reloading".format(self.identifier))
            HTTP.Request(u'http://127.0.0.1:32400/:/plugins/{}/reloadServices'.format(self.identifier), cacheTime=0, immediate=True)
        except:
            Log.Exception(u"Unable to reload services in {}".format(self.identifier))

        # Reload system services
        Core.services.load()

    def restart_self_silently(self):
        """Try to restart the channel from Plex API"""
        HTTP.Request(u'http://127.0.0.1:32400/:/plugins/{}/restart'.format(self.identifier), immediate=True)

    def restart_channel(self):
        """Try to restart the channel by updating the timestamp of the Info.plist file"""
        if Core.storage.file_exists(Core.plist_path):
            Log(u"Restarting {}".format(self.identifier))
            Core.storage.utime(Core.plist_path, None)
            return True
        Log(u"Failed to restart {} because of missing Info.plist file.".format(self.identifier))
        return False

    def item_last_modified(self, path, utc=False):
        if Core.storage.file_exists(path):
            ts = Core.storage.last_modified(path)
            if utc:
                return self.datetime_to_utc(Datetime.FromTimestamp(ts)).replace(microsecond=0)
            return Datetime.FromTimestamp(ts).replace(microsecond=0)
        return False

    @property
    def initial_run(self):
        """setup initial run status"""
        self.init_datetime = self.item_last_modified(Core.plist_path, utc=True)
        if not Dict['init_run']:
            Log('{} initial run. Logging datetime into Dict[\'init_run\']'.format(self.name))
            Dict['init_run'] = Datetime.UTCNow().replace(microsecond=0)
            Dict.Save()
            return False
        # Check Info.plist for changes, file modified time should only change with updates or install
        elif Dict['init_run'] < self.init_datetime:
            Log(u"* Updating old init time {} to {}".format(Dict['init_run'], self.init_datetime))
            Dict['init_run'] = self.init_datetime
            return False
        else:
            Log(u"* Dict['init_run'] = '{}'".format(Dict['init_run']))
            Log(u"* Info.plist last modified datetime.utc = '{}'".format(self.init_datetime))
            return True

    def gui_update(self, prefix, oc, repo, branch='master', tag=None, list_view_clients=list):
        """
        Create route for updater, and check for the latest release or commit depending on branch or tag inputs.
        Update option will on appear when an update is available.
        Change CHECK_INTERVAL to desired interval to allow for checking updates.
        CHECK_INTERVAL = cache time for Github request URL.
        Requires 'icon-update.png' within channel Resources directory for icon to display in menu, otherwise will be blank icon

        Input Help:
            prefix (required)
                Pass-in the channel's prefix
                Example: prefix='/video/kissnetwork/updater'

            oc (required)
                Pass-in the channel's current ObjectContainer so the updater can be added as a DirectoryObject

            repo (required)
                Pass-in the channel's Github repository information
                Example: repo='Twoure/KissNetwork.bundle'

            branch (optional)
                Pass-in the channels'Github repository branch to track
                Default: branch='master'
                Example: branch='dev'

            tag (optional)
                Use tag if wanting to track Github releases
                If tag is set, then branch is ignored...
                Example: if branch='dev' and tag='latest' then the updater will only check for the latest release

            list_view_clients (optional)
                Pass in a list of Client.Platform values to not display the updater icon on
                Example: list_view_clients=['Android', 'iOS'], will set icon to None for Android and iOS clients.
        """
        Route.Connect(prefix, self.update)
        if self.is_update_available(repo, branch, tag):
            oc.add(DirectoryObject(
                key=Callback(self.update, repo=repo, branch=branch, tag=self.update_info['zipId']),
                title=u'%s' % F('updater.update_available', self.update_info['version']),
                summary=u'{}\n{}'.format(L('updater.install'), self.update_info['notes']),
                thumb=R('icon-update.png') if Client.Platform not in list_view_clients else None
                ))
