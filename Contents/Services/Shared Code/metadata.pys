#!/usr/bin/env python

import common as Common

########################################################################################
def FindPartElement(array=list, string=str):
    """fileter elements in array by sting, allows for loose matches"""

    return bool(filter(lambda element: string in element, array))

########################################################################################
def GetSummary(html):
    """Get Summary from HTML"""

    # set full summary
    summary = html.xpath('//p[span[@class="info"]="Summary:"]/following-sibling::p')
    # if summary found in <p> after <p><span>Summary:</span></p>
    if summary:
        #Log.Debug('* summary in <p>')
        p_list = html.xpath('//div[@id="container"]//p')
        p_num = len(p_list)
        match = int(0)
        for i, node in enumerate(html.xpath('//div[@id="container"]//p')):
            if node.xpath('./span[@class="info"]="Summary:"'):
                match = int(i) + 1
                break

        new_p_list = p_list[match:p_num]
        sum_list = []
        for node in new_p_list:
            if node is not None:
                sum_text = node.text_content().strip()
                if sum_text:
                    sum_list.append(sum_text)

        if len(sum_list) > 1:
            #Log.Debug('* summary was in {} <p>\'s'.format(len(sum_list)))
            summary = '\n\n'.join(sum_list).replace('Related Series', '').replace('Related:', '').strip().replace('\n\n\n', '\n')
        else:
            if len(sum_list) == 1:
                #Log.Debug('* summary was in the only <p>')
                summary = sum_list[0]
            else:
                #Log.Debug('* no summary found in <p>\'s, setting to \"None\"')
                summary = None
    else:
        summary = html.xpath('//p[span[@class="info"]="Summary:"]/following-sibling::p/span')
        # if summary found in <p><span> after <p><span>Summary:</span></p>
        if summary:
            #Log.Debug('* summary is in <p><span>')
            summary = summary[0].text_content().strip()
        else:
            summary = html.xpath('//div[@id="container"]//div[@class="barContent"]/table//td')
            # if summary found in own <table>
            if summary:
                #Log.Debug('* summary is in own <table>')
                summary = summary[0].text_content().strip()
            else:
                summary = html.xpath('//div[@id="container"]//div[@class="bigBarContainer"]/div[@class="barContent"]/div/div')
                # if summary found in own <div>
                if summary:
                    #Log.Debug('* summary is in own <div>')
                    summary = summary[0].text_content().strip()
                else:
                    summary = html.xpath('//p[span[@class="info"]="Summary:"]')
                    # summary may be in <p><span>Summary:</span>summary</p>, ie text outside Summary span
                    if summary:
                        summary = summary[0].text_content().strip()
                        test = Regex('(?s)Summary\:.+?([\S].+)').search(summary)
                        if test:
                            #Log.Debug('* summary is in <p><span>Summary:</span>summary</p>')
                            summary = test.group(1).strip()
                        else:
                            #Log.Debug('* no summary found, setting summary to \"None\"')
                            summary = None
                    else:
                        # if no summary found then set to 'None'
                        #Log.Debug('* no summary found, setting summary to \"None\"')
                        summary = None

    if summary:
        #Log.Debug('* summary = {}'.format(summary))
        summary = Common.StringCode(string=summary, code='encode')

    return summary

########################################################################################
def get_art(url):
    time_stamp = int(Datetime.TimestampFromDatetime(Datetime.Now()))
    return '/:/plugins/com.plexapp.plugins.kissnetwork/resources/art-{}.jpg?t={}'.format(Common.GetTypeTitle(url).lower(), str(time_stamp))

########################################################################################
def GetGenres(html):
    """Get Genres from HTML"""

    genres = html.xpath('//p[span[@class="info"]="Genres:"]/a/text()')
    genres_string_list = None
    if genres:
        genres_string_list = list_to_string(genres)

    return genres, genres_string_list

########################################################################################
def GetCountries(html):
    """Get Countries from HTML"""

    countries = html.xpath('//p[span[@class="info"]="Country:"]/a/text()')
    countries_string_list = None
    if countries:
        countries_string_list = Common.StringCode(string=list_to_string(countries), code='encode')

    return countries, countries_string_list

########################################################################################
def list_to_string(l=list):
    """Covert List into String"""

    return ' '.join([g.replace(' ', '_') for g in l]) if l else None

########################################################################################
def string_to_list(s=str):
    """Covert String into List"""

    return [g.replace('_', ' ') for g in s.split()] if s else list()

########################################################################################
def GetOtherNames(html):
    """Get Other Names from HTML"""

    return html.xpath('//p[span[@class="info"]="Other name:"]/a/text()')

########################################################################################
def GetDateAired(html):
    """Get date aired from HTML"""

    date_aired = html.xpath('//p[span[@class="info"]="Date aired:"]/text()')
    #Log.Debug('* date_aired = {}'.format(date_aired))
    if date_aired:
        try:
            date_aired = date_aired[1].lower().split(' to ')[0].split('-')[0].strip()
            #Log.Debug('* date_aired after cleaning = {}'.format(date_aired))
            try:
                date = str(Datetime.ParseDate(date_aired))
            except:
                date = None
        except:
            date_aired = None
            date = None
    else:
        date_aired = None
        date = None

    return date_aired, date

########################################################################################
def GetYear(html):
    """Get Year from date_aired"""

    date_aired, date = GetDateAired(html)
    #Log.Debug('* date_aired, date | {}, {}'.format(date_aired, date))
    if date_aired:
        try:
            year = int(Datetime.ParseDate(date_aired).year)
        except:
            year = None
    else:
        year = None

    return year

########################################################################################
def GetDateAdded(html, url):
    """Get Date Video was Added"""

    video_id = int(url.split('/', 3)[3].split('=')[-1])

    node = html.xpath('//table[@class="listing"]/tr')
    da = None
    for item in node:
        ep = item.xpath('./td/a')
        if ep:
            ep_id = int(item.xpath('./td/a/@href')[0].split('=')[-1])
            if video_id == ep_id:
                da = Datetime.ParseDate(item.xpath('./td')[1].text_content().strip())
                break
    return da

########################################################################################
def GetEpisodeNameAndNumber(html, title, url):
    """
    Get Episode Name and Number from HTML and title
    Search current title for Episode info
    """

    video_id = url.split('/', 3)[3].split('=')[-1]

    # test title for episode # and season # via Regex
    ep_node = Regex('Episode(?:(?:\ (\d+)(\ .*))|(?:\ (\d+))|(\ .*))').search(title)

    # set up episode_name and episode number
    if ep_node:
        # if ep # and text found after # then:
        if ep_node.group(1) and ep_node.group(2):
            # set episode number (ep #)
            episode_number = int(ep_node.group(1))
            # if ep # != 0 then strip leading 0 from #
            if not episode_number == int(0):
                episode_number = int(str(episode_number).lstrip('0'))
            # set episode name
            episode_name = 'E{}{}'.format(episode_number, ' | ' + ep_node.group(2).lstrip(' -'))
        # if ep # with no text after it then:
        elif ep_node.group(3):
            episode_number = int(ep_node.group(3))
            if not episode_number == int(0):
                episode_number = int(str(episode_number).lstrip('0'))

            episode_name = 'Episode {}'.format(episode_number)
        # if ep found with no number but has text after it then:
        elif ep_node.group(4):
            # get episode list from show page
            test = html.xpath('//table[@class="listing"]/tr/td/a')
            # reverse list and enumerate to match selected video id with interation
            for i, item in enumerate(list(reversed(test))):
                # get episode id
                ep_id = int(item.get('href').split('=')[-1])
                if int(video_id) == ep_id:
                    # add 1 to i since it starts at 0 in list
                    episode_number = int(i) + 1
                    episode_name = 'E{}{}'.format(episode_number, ' | ' + ep_node.group(4).lstrip(' -'))
                    break
        # this shouldn't be needed but just in case the above fails
        else:
            episode_number = None
            episode_name = title
    # if Episode in name but Regex has not matches then add ep # and format ep name
    else:
        # get episode list from show page
        test = html.xpath('//table[@class="listing"]/tr/td/a')
        # reverse list and enumerate to match selected video id with interation
        for i, item in enumerate(list(reversed(test))):
            # get episode id
            ep_id = int(item.get('href').split('=')[-1])
            if int(video_id) == ep_id:
                # add 1 to i since it starts at 0 in list
                episode_number = int(i) + 1
                episode_name = 'Episode {}'.format(episode_number)
                break

    return episode_name, str(episode_number)

########################################################################################
def GetSeasonNumber(title, show_name_raw, tags=list, summary=str):
    """Get Season Number"""

    summary = Common.StringCode(string=summary, code='decode') if summary else None

    season_number = None
    # test title for season # via Regex
    se_node = Regex('Season (\d+)').search(title)

    # if season in title then set season number
    if se_node:
        return str(se_node.group(1))
    # if not uncensored episode
    elif 'episode' in title.lower() and 'uncensored' not in title.lower():
        # set up tags test lits of strings for finding season
        tags_test = [x.lower() for x in tags]
        # setup summary for finding season
        if summary:
            summary_test = summary.lower()
        else:
            summary_test = 'none'

        # if season number was not found above and if 'season' in the show name
        # then try and find the season number in the show name
        if "season" in show_name_raw.lower() and not season_number:
            # test for "2nd Season" etc...
            test1 = Regex('(\d+)(?:[a-z][a-z]\ Season)').search(show_name_raw)
            if test1:
                season_number = int(test1.group(1))
            else:
                # test for "Season 2" etc...
                test2 = Regex('(?:Season\ )(\d+)').search(show_name_raw)
                if test2:
                    season_number = int(test2.group(1))
                else:
                    # test for "Second Season" etc...
                    test3 = Regex('(First|Second|2nd|Third|3rd)\ (?:Season)').search(show_name_raw)
                    if test3:
                        test3_text = test3.group(1)
                        if test3_text == 'First':
                            season_number = int(1)
                        elif test3_text == 'Second' or test3_text == '2nd':
                            season_number = int(2)
                        elif test3_text == 'Third' or test3_text == '3rd':
                            season_number = int(3)
                    # if season number not in show name then try and find it in the summary or tags test array
                    elif 'second season' in summary_test or FindPartElement(array=tags_test, string='second season'):
                        season_number = int(2)
                    elif 'third season' in summary_test or FindPartElement(array=tags_test, string='third season'):
                        season_number = int(3)
                    elif 'forth season' in summary_test or FindPartElement(array=tags_test, string='forth season'):
                        season_number = int(4)
                    elif FindPartElement(array=tags_test, string='short') or FindPartElement(array=tags_test, string='special'):
                        season_number = int(0)
                    # if no season number found then set season to 1
                    else:
                        season_number = int(1)
        # if season number not above and if 'season' not in show name
        # try and find season number in summary or tags test string
        elif not season_number:
            if 'first season' in summary_test or FindPartElement(array=tags_test, string='first season'):
                season_number = int(1)
            elif 'second season' in summary_test or FindPartElement(array=tags_test, string='second season'):
                season_number = int(2)
            elif 'third season' in summary_test or FindPartElement(array=tags_test, string='third season'):
                season_number = int(3)
            elif 'forth season' in summary_test or FindPartElement(array=tags_test, string='forth season'):
                season_number = int(4)
            elif FindPartElement(array=tags_test, string='short') or FindPartElement(array=tags_test, string='special'):
                season_number = int(0)
            # if no season number found then set season to 1
            else:
                season_number = int(1)
        return str(season_number)
    else:
        return str(0)

########################################################################################
def GetTVShowTitle(show_name_raw):
    """Get Show Title from show_name_raw"""

    show_title_regex = Regex('^(.+?)(?:\ |\ (?:[1-9][a-z][a-z]|First|Second)\ )(?:Season|Episode)(.+|)').search(show_name_raw)
    if show_title_regex:
        show_title = show_title_regex.group(1) + show_title_regex.group(2)
    else:
        show_title = show_name_raw

    return show_title

########################################################################################
def GetEpisodeTitle(season_number=int, episode_name=str, episode_number=int):
    """Get Episode Title depending on season number and episode name"""

    # set episode title for EpisodeObject
    if season_number or season_number == 0:
        ep_test = Regex('E(?:\d+)(.*)').search(episode_name)
        # if no show name then return 'Season {} | Episode {}'
        if not ep_test:
            new_title = 'Season {} | {}'.format(season_number, episode_name)
        # PHT displays season and episode already, so don't include in name
        elif Client.Platform == 'Plex Home Theater':
            new_title = ep_test.group(1).lstrip(' |')
        # shorten season and episode to include ep name
        else:
            new_title = 'S{} | E{}{}'.format(season_number, episode_number, ep_test.group(1))
    # no season # found, so just return ep # and name
    else:
        new_title = episode_name

    return new_title

########################################################################################
def GetSourceTitle(url):
    """Get Source Title"""

    if 'kiss' in url:
        source_title = 'Kiss' + Regex(r'^https?://(?:www\.)?kiss(\w+)\.[^/]+').search(url).group(1).title()
    else:
        source_title = 'KissComic'

    return source_title

########################################################################################
def get_title(html, video_id, show_name_raw):
    """Get the show title matching the video id"""
    title_raw = html.xpath('//table[@class="listing"]/tr/td/a[contains(@href, "{}")]/../a/text()'.format(video_id))[0]
    title = title_raw.replace(show_name_raw, '').replace('\n', '').strip()
    return title

########################################################################################
def GetBaseMovieInfo(html, url):
    """Get Movie Info to populate TVShowObject"""

    show_name_raw = html.xpath('//div[@class="barContent"]/div/a[@class="bigChar"]/text()')[0]
    other_names = html.xpath('//p[span[@class="info"]="Other name:"]/a/text()')
    countries, cstring = GetCountries(html)

    year = GetYear(html)
    if year:
        year = str(year)
    else:
        year = None

    tags_list = None
    if other_names:
        tags_list = Common.StringCode(string=' '.join([t.replace(' ', '_') for t in other_names]), code='encode')

    movie_info = {
        'title': show_name_raw.strip(), 'summary': GetSummary(html),
        'source_title': GetSourceTitle(url), 'tags': tags_list,
        'year': year, 'countries': cstring
        }

    return movie_info

########################################################################################
def GetBaseShowInfo(html, url):
    """Get Show Info to populate TVShowObject"""

    show_name_raw = html.xpath('//div[@class="barContent"]/div/a[@class="bigChar"]/text()')[0]
    countries, cstring = GetCountries(html)

    other_names = html.xpath('//p[span[@class="info"]="Other name:"]/a/text()')
    genres, gstring = GetGenres(html)
    tags = other_names + genres
    tags_list = None
    if tags:
        tags_list = Common.StringCode(string=' '.join([t.replace(' ', '_') for t in tags]), code='encode')

    year = GetYear(html)
    if year:
        year = str(year)
    else:
        year = None

    show_info = {
        'tv_show_name': GetTVShowTitle(show_name_raw), 'summary': GetSummary(html),
        'source_title': GetSourceTitle(url), 'tags': tags_list,
        'year': year, 'countries': cstring
        }

    return show_info

########################################################################################
def GetBaseMangaInfo(html, url):
    """Get Manga Info to populate TVShowObject"""

    show_name_raw = html.xpath('//div[@class="barContent"]/div/a[@class="bigChar"]/text()')[0]
    countries, cstring = GetCountries(html)

    other_names = html.xpath('//p[span[@class="info"]="Other name:"]/a/text()')
    genres, gstring = GetGenres(html)
    tags = other_names + genres
    tags_list = None
    if tags:
        tags_list = Common.StringCode(string=' '.join([t.replace(' ', '_') for t in tags]), code='encode')

    year = GetYear(html)
    if year:
        year = str(year)
    else:
        year = None

    show_info = {
        'title': show_name_raw.strip(), 'summary': GetSummary(html),
        'source_title': GetSourceTitle(url), 'tags': tags_list,
        'year': year, 'countries': cstring
        }

    return show_info
