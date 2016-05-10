import os
import requests
from slugify import slugify
Common = SharedCodeService.common
Headers = SharedCodeService.headers
Domain = SharedCodeService.domain

TIMEOUT = Datetime.Delta(hours=1)

####################################################################################################
def ElementFromURL(url):
    """setup requests html"""

    cachetime = Datetime.Now()
    name = slugify(url) + '__cachetime__%i' %Datetime.TimestampFromDatetime(cachetime)

    match = False
    path = os.path.join(Common.SUPPORT_PATH, "DataItems")
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
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
        page = requests.get(url, headers=Headers.GetHeadersForURL(url))
        if (int(page.status_code) == 503) or (len(page.history) > 0):
            if count <= 1:
                count += 1
                if len(page.history) > 0:
                    type_title = Common.GetTypeTitle(url)
                    Log.Warn('* get_element_from_url Error: HTTP 301 Redirect Error. Refreshing %s Domain' %type_title)
                    Log.Warn('* get_element_from_url Error: page history %s | %s' %(url, page.history))
                    Domain.UpdateDomain(type_title)
                    url = Common.CorrectURL(url)
                else:
                    Log.Warn('* get_element_from_url Error: HTTP 503 Site Error. Refreshing site cookies')
                    Headers.GetHeadersForURL(url, update=True)
                return get_element_from_url(url, name, count)
            else:
                Log.Error('* get_element_from_url Error: HTTP 503 Site error, tried refreshing cookies but that did not fix the issue')
                if Data.Exists(name):
                    Log.Warn('* Using old cached page')
                    html = HTML.ElementFromString(page.text)
                else:
                    html = HTML.Element('head', 'Error')
        else:
            Data.Save(name, page.text)
            html = HTML.ElementFromString(page.text)
    except Exception as e:
        Log.Error('* get_element_from_url Error: Cannot load %s' %url)
        Log.Error('* get_element_from_url Error: %s' %str(e))
        html = HTML.Element('head', 'Error')

    return html
