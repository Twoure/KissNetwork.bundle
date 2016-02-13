#!/usr/bin/env python

import urllib2

HOST = 'http://127.0.0.1:32400'

def CheckAuth():
    """ Only the main users token is accepted at /myplex/account """
    headers = {'X-Plex-Token': Request.Headers.get('X-Plex-Token', '')}
    req = urllib2.Request("%s/myplex/account" %HOST, headers=headers)
    res = urllib2.urlopen(req)

def Auth():
    try:
        CheckAuth()
        return True
    except Exception as e:
        Log.Error('CheckAuth: this user can\'t access: %s' % str(e))
        return False
