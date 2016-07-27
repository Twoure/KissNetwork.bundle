####################################################################################################
def ElementFromURL(url):
    """setup requests html"""

    cachetime = Datetime.Now()
    name = slugify(url) + '__cachetime__%i' %Datetime.TimestampFromDatetime(cachetime)

    match = False
    path = Core.storage.join_path(Core.storage.data_path, 'DataItems')
    files = [f for f in Core.storage.list_dir(path) if not Core.storage.dir_exists(Core.storage.join_path(path, f))]
    for filename in files:
        item = filename.split('__cachetime__')
        if slugify(url) == item[0]:
            match = True
            if (Datetime.FromTimestamp(int(item[1])) + TIMEOUT) <= cachetime:
                Log.Debug('* Re-Caching URL')
                html = get_element_from_url(url, name)
                break
            else:
                Log.Debug('* Reading URL from Cache')
                html = HTML.ElementFromString(Data.Load(filename))
                break

    if not match:
        Log.Debug('* Caching URL')
        html = get_element_from_url(url, name)

    return html

####################################################################################################
def get_element_from_url(url, name, count=0):
    """error handling for URL requests"""

    try:
        page = requests.get(url, headers=KH.get_headers_for_url(url))
        if (int(page.status_code) == 503) or (len(page.history) > 0):
            if count <= 1:
                count += 1
                if len(page.history) > 0:
                    type_title = Common.GetTypeTitle(url)
                    req_base_url = Regex(r'(https?\:\/\/(?:www\.)?\w+\.\w+)').search(page.url).group(1)
                    base_url = Regex(r'(https?\:\/\/(?:www\.)?\w+\.\w+)').search(url).group(1)
                    if req_base_url == base_url:
                        page = requests.get(page.url, headers=KH.get_headers_for_url(req_base_url))
                        Data.Save(name, page.text)
                        html = HTML.ElementFromString(page.text)
                        return html
                    else:
                        Log.Warn('* get_element_from_url Error: HTTP 301 Redirect Error. Refreshing %s Domain' %type_title)
                        Log.Warn('* get_element_from_url Error: page history %s | %s' %(url, page.history))
                        Domain.UpdateDomain(type_title, True)
                        url = Common.CorrectURL(url)
                else:
                    Log.Warn('* get_element_from_url Error: HTTP 503 Site Error. Refreshing site cookies')
                    KH.get_headers_for_url(url, update=True)
                return get_element_from_url(url, name, count)
            else:
                Log.Error('* get_element_from_url Error: HTTP 503 Site error, tried refreshing cookies but that did not fix the issue')
                if Data.Exists(name):
                    Log.Warn('* Using old cached page')
                    html = HTML.ElementFromString(page.text)
                else:
                    html = HTML.Element('head', 'Error')
        elif (int(page.status_code) == 522):
            Log.Error('* get_element_from_url Error: HTTP 522 Site error, site is currently offline')
            html = HTML.Element('head', 'Error')
        else:
            Data.Save(name, page.text)
            html = HTML.ElementFromString(page.text)
    except Exception as e:
        Log.Error('* get_element_from_url Error: Cannot load %s' %url)
        Log.Error('* get_element_from_url Error: %s' %str(e))
        html = HTML.Element('head', 'Error')

    return html
