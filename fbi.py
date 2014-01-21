#!/usr/bin/env python
#
# Facebook Insights(FBI) 1.0.0
# Copyright 2014 OpenBridge. All Rights Reserved.
# Developer: Dairon Medina <dairon.medina@gmail.com>
# Coded with pride in Ecuador, South America

import os, sys
import datetime
import ConfigParser
import csv
import logging
import os.path
import json
import urllib2
import urllib
import urlparse
import BaseHTTPServer
import webbrowser

logger = logging.getLogger(__name__)


ROOT = os.path.dirname(sys.executable)
path = lambda *a: os.path.join(ROOT, *a)

settings = ConfigParser.ConfigParser()
settings.read(path('insights.conf'))

APP_ID = '1390941031127476'
APP_SECRET = 'c4eb7acdae5847b8766b051316a82898'
ENDPOINT = 'graph.facebook.com'
REDIRECT_URI = 'http://localhost:8080/'
ACCESS_TOKEN = None
LOCAL_FILE = '.fb_access_token'
STATUS_TEMPLATE = u"{name}\033[0m: {message}"

class FacebookGraphAPI(object):

    def __init__(self, page_label):
        self.page = settings.get('facebook', 'app_or_page')

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        else:
            def caller(**params):
                url = self.construct_api_url(name, params)
                return self.api_request(url)
            return caller

    def construct_api_url(self, method_name, params):
        """
        If the 'since' parameter is provided, it cannot be further back
        than 35 days prior to today or the API will return an error.
        To counter this, if 'since' exceeds 35 days, we amend it to a
        35 day period ending yesterday.
        'since' should be a string in %Y-%m-%d format.
        """
        since = params.get('since', None)
        if since:
            since = datetime.date(*time.strptime(since, "%Y-%m-%d")[0:3])
            today = datetime.date.today()
            delta = today - since
            if delta.days > 35:
                diff = datetime.timedelta(days=36)
                params['since'] = today - diff
        api_method = "/".join(method_name.split('__'))
        params['access_token'] = self.access_token.token
        url = "%s/%s/%s?%s" % (self.api_url,
                               self.page.page_id,
                               api_method,
                               urllib.urlencode(params))
        return url

    def api_request(self, url):
        handle = urllib2.urlopen(url)
        self.last_url = handle.geturl()
        return json.load(handle)

def get_url(path, args=None):
    args = args or {}
    if ACCESS_TOKEN:
        args['access_token'] = ACCESS_TOKEN
    if 'access_token' in args or 'client_secret' in args:
        endpoint = "https://"+ENDPOINT
    else:
        endpoint = "http://"+ENDPOINT
    return endpoint+path+'?'+urllib.urlencode(args)

def get(path, args=None):
    return urllib2.urlopen(get_url(path, args=args)).read()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        global ACCESS_TOKEN
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        code = urlparse.parse_qs(urlparse.urlparse(self.path).query).get('code')
        code = code[0] if code else None
        if code is None:
            self.wfile.write("Sorry, authentication failed.")
            sys.exit(1)
        response = get('/oauth/access_token', {'client_id':APP_ID,
                                               'redirect_uri':REDIRECT_URI,
                                               'client_secret':APP_SECRET,
                                               'code':code})
        ACCESS_TOKEN = urlparse.parse_qs(response)['access_token'][0]
        open(LOCAL_FILE,'w').write(ACCESS_TOKEN)
        self.wfile.write("You have successfully logged in to facebook. "
                         "You can close this window now.")

def print_status(item, color=u'\033[1;35m'):
    print color+STATUS_TEMPLATE.format(name=item['from']['name'],
                                       message="item['message'].strip()")

if __name__ == '__main__':
    INTRO_MESSAGE = '''\
      __ _      _
     / _| |    | |
    | |_| |__  | |
    |  _| '_ \ | |
    | | | |_) || |
    |_| |_.__/ |_|

    FACEBOOK INSIGHTS
    '''
    if not os.path.exists(LOCAL_FILE):
        print "Logging you in to facebook..."
        webbrowser.open(get_url('/oauth/authorize',
                                {'client_id':APP_ID,
                                 'redirect_uri':REDIRECT_URI,
                                 'scope':'read_insights,manage_pages,offline_access'}))

        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), RequestHandler)
        while ACCESS_TOKEN is None:
            httpd.handle_request()
    else:
        ACCESS_TOKEN = open(LOCAL_FILE).read()
    for item in json.loads(get('/1390941031127476/insights'))['data']:
        print item
