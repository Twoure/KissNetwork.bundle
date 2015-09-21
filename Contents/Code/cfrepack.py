#!/usr/bin/env python

from lxml import html
import os, sys, inspect

custom_modules = ['cloudflare-scrape', 'PyExecJS', 'requests']

for folder in custom_modules:
    cmd_subfolder = os.path.realpath(
        os.path.abspath(
            os.path.join(
                os.path.split(inspect.getfile( inspect.currentframe() ))[0],
                "%s" % folder)))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

import execjs
import cfscrape
import requests

def ElementFromURL(url):
    """
    Retrun url in html formate
    """

    scraper = cfscrape.create_scraper()
    page = scraper.get(url)
    myscrape = html.fromstring(page.text)

    return myscrape

def Request(url):
    """
    Get url data so it can be manipulated for headers or content
    """

    scraper = cfscrape.create_scraper()
    page = scraper.get(url)

    return page
