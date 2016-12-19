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
def html_from_error(page, name):
    error = {'closed': False, 'unavailable': False, 'human': False}
    for err in Common.ERROR_LIST:
        if Regex(r'(?i)(^%s$)' %err).search(page.text):
            if err.lower() == "the service is unavailable.":
                Log.Warn(u"* {} Not Caching '{}'".format(err, page.url))
                error['unavailable'] = True
                break
            else:
                Log.Warn(str(page.text.strip()))
                error['closed'] = True
                return HTML.Element('head', 'Error'), error

    if Regex(r'(\/recaptcha\/api\.js)').search(page.text):
        Log.Error(u'* Human Verification needed for \'{}\''.format(page.url))
        Log.Warn(str(page.text.strip()))
        error['human'] = True
        return HTML.Element('head', 'Error'), error
    else:
        Data.Save(Core.storage.join_path(URL_CACHE_DIR, name), page.text)
    return HTML.ElementFromString(page.text), error

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
                    req_base_url = Regex(r'(https?://(?:www\.)?\w+\.\w+)').search(page.url).group(1)
                    base_url = Regex(r'(https?://(?:www\.)?\w+\.\w+)').search(url).group(1)
                    if req_base_url == base_url:
                        page = requests.get(page.url, headers=Headers.get_headers_for_url(req_base_url))
                        html = html_from_error(page, name)
                        return html[0]
                    else:
                        Log.Warn('* HTTP {} Error: Refreshing {} Domain'.format(page.status_code, type_title))
                        Log.Warn('* Error: req_base_url | base_url = {} | {}'.format(page.url, url))
                        Log.Warn('* Error: page history {} | {}'.format(url, page.history))
                        Domain.UpdateDomain(type_title, True)
                        url = Common.CorrectURL(url)
                else:
                    Log.Warn('* HTTP 503 Error: checking page for source of error')
                    error = html_from_error(page, name)
                    if error[1]['unavailable']:
                        Log.Warn('* Site Unavailable, trying again in 2 seconds')
                        Thread.Sleep(2)
                    if error[1]['closed']:
                        Log.Warn('* Site Closed for Maintenance.')
                        return error[0]
                    else:
                        Log.Warn('* HTTP 503 Error: Refreshing site cookies')
                        Headers.get_headers_for_url(url, update=True)
                return get_element_from_url(url, name, count)
            else:
                Log.Error('* HTTP 503 Error: tried refreshing cookies but that did not fix the issue')
                if Data.Exists(Core.storage.join_path(URL_CACHE_DIR, name)):
                    Log.Warn('* Using bad page')
                    return HTML.ElementFromString(page.text)
        else:
            try:
                page.raise_for_status()
                html = html_from_error(page, name)
                return html[0]
            except:
                if (int(page.status_code) == 522):
                    Log.Exception('* HTTP 522 Error: site is currently offline')
                elif (int(page.status_code) == 524):
                    Log.Exception('* HTTP 524 Error: A timeout occurred')
                    if count < 1:
                        Log.Debug("* ReTrying '{}'".format(page.url))
                        count += 1
                        return get_element_from_url(url, name, count)
                else:
                    Log.Exception('* Unknown Error: check output >>>')
    except:
        Log.Exception('* Error: Failed to load {}'.format(url))

    return HTML.Element('head', 'Error')
