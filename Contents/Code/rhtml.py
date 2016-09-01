####################################################################################################
def ElementFromURL(url):
    """setup requests html"""

    match = False
    name = Hash.MD5(url)
    path = Core.storage.data_item_path(URL_CACHE_DIR)
    Core.storage.ensure_dirs(path)
    files = [f for f in Core.storage.list_dir(path) if not Core.storage.dir_exists(Core.storage.join_path(path, f))]

    for filename in files:
        if filename == name:
            match = True
            if (Datetime.FromTimestamp(Core.storage.last_modified(Core.storage.join_path(path, filename))) + TIMEOUT) <= Datetime.Now():
                Log.Debug('* Re-Caching \'{}\' to {}'.format(url, URL_CACHE_DIR))
                html = get_element_from_url(url, name)
                break
            else:
                Log.Debug('* Fetching \'{}\' from {}'.format(url, URL_CACHE_DIR))
                html = HTML.ElementFromString(Data.Load(Core.storage.join_path(URL_CACHE_DIR, filename)))
                break

    if not match:
        Log.Debug('* Caching \'{}\' to {}'.format(url, URL_CACHE_DIR))
        html = get_element_from_url(url, name)

    return html

####################################################################################################
def get_element_from_url(url, name, count=0):
    """error handling for URL requests"""

    try:
        page = requests.get(url, headers=Headers.get_headers_for_url(url))
        if (int(page.status_code) == 503) or (len(page.history) > 0):
            if count <= 1:
                count += 1
                if len(page.history) > 0:
                    type_title = Common.GetTypeTitle(url)
                    req_base_url = Regex(r'(https?\:\/\/(?:www\.)?\w+\.\w+)').search(page.url).group(1)
                    base_url = Regex(r'(https?\:\/\/(?:www\.)?\w+\.\w+)').search(url).group(1)
                    if req_base_url == base_url:
                        page = requests.get(page.url, headers=Headers.get_headers_for_url(req_base_url))
                        if Regex(r'(^The service is unavailable.$)').search(page.text):
                            Log.Warn('* The service is unavailable. Not caching \'{}\''.format(page.url))
                        elif Regex(r'\/recaptcha\/api\.js').search(page.text):
                            Log.Error(u'* Human Verification needed for \'{}\''.format(page.url))
                            Log.Warn(str(page.text))
                            return HTML.Element('head', 'Error')
                        else:
                            Data.Save(Core.storage.join_path(URL_CACHE_DIR, name), page.text)
                        return HTML.ElementFromString(page.text)
                    else:
                        Log.Warn('* get_element_from_url Error: HTTP {} Error. Refreshing {} Domain'.format(page.status_code, type_title))
                        Log.Warn('* get_element_from_url Error: req_base_url | base_url = {} | {}'.format(page.url, url))
                        Log.Warn('* get_element_from_url Error: page history {} | {}'.format(url, page.history))
                        Domain.UpdateDomain(type_title, True)
                        url = Common.CorrectURL(url)
                else:
                    Log.Warn('* get_element_from_url Error: HTTP 503 Site Error. Refreshing site cookies')
                    Headers.get_headers_for_url(url, update=True)
                return get_element_from_url(url, name, count)
            else:
                Log.Error('* get_element_from_url Error: HTTP 503 Site error, tried refreshing cookies but that did not fix the issue')
                if Data.Exists(Core.storage.join_path(URL_CACHE_DIR, name)):
                    Log.Warn('* Using old cached page')
                    return HTML.ElementFromString(page.text)
        else:
            try:
                page.raise_for_status()
                if Regex(r'(^The service is unavailable.$)').search(page.text):
                    Log.Warn('* The service is unavailable. Not caching \'{}\''.format(page.url))
                elif Regex(r'\/recaptcha\/api\.js').search(page.text):
                    Log.Error(u'* Human Verification needed for \'{}\''.format(page.url))
                    Log.Warn(str(page.text))
                    return HTML.Element('head', 'Error')
                else:
                    Data.Save(Core.storage.join_path(URL_CACHE_DIR, name), page.text)
                return HTML.ElementFromString(page.text)
            except:
                if (int(page.status_code) == 522):
                    Log.Exception('* get_element_from_url Error: HTTP 522 Site error, site is currently offline')
                elif (int(page.status_code) == 524):
                    Log.Exception('* get_element_from_url Error: HTTP 524 Site Error, A timeout occurred')
                    if count < 1:
                        Log.Debug('* ReTrying \'{}\''.format(page.url))
                        count += 1
                        return get_element_from_url(url, name, count)
                else:
                    Log.Exception('* get_element_from_url Error: Unknown Site Error, check output below.')
    except:
        Log.Exception('* get_element_from_url Error: Failed to load {}'.format(url))

    return HTML.Element('head', 'Error')
