#!/usr/bin/env python
#
# Facebook Insights(FBI) 1.0.0
# Copyright 2014 OpenBridge. All Rights Reserved.
# Developer: Dairon Medina <dairon.medina@gmail.com>
# Coded with pride in Ecuador, South America
from datetime import datetime
import os
import datetime
import ConfigParser
import csv, codecs
import logging
import json
import urllib2
import urllib
import urlparse
import BaseHTTPServer
import webbrowser

insights_groups = {
    "app-user-demographic": [
                        'application_active_users',
                        'application_active_users_locale',
                        'application_active_users_city',
                        'application_active_users_country',
                        'application_active_users_gender',
                        'application_active_users_age',
                        'application_active_users_gender_age',
                        'application_installed_users',
                        'application_installed_users_locale',
                        'application_installed_users_city',
                        'application_installed_users_country',
                        'application_installed_users_gender',
                        'application_installed_users_age',
                        'application_installed_users_gender_age',
                        'application_installation_adds',
                        'application_installation_adds_unique',
                        'application_installation_removes',
                        'application_installation_removes_unique',
                        'application_tos_views',
                        'application_tos_views_unique'
    ],
    "2009": [4,7],
    "1989": [8]
}


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ColoredFormatter(logging.Formatter):

    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

# Custom logger class with multiple destinations
class ColoredLogger(logging.Logger):
    FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    COLOR_FORMAT = formatter_message(FORMAT, True)

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)

        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return

logging.setLoggerClass(ColoredLogger)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


ROOT = os.path.dirname(__file__)
path = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)

settings = ConfigParser.ConfigParser()
settings.read(path('insights.conf'))

APP_ID = '1390941031127476'
APP_SECRET = 'c4eb7acdae5847b8766b051316a82898'
ENDPOINT = 'graph.facebook.com'
REDIRECT_URI = 'http://localhost:8080/'
ACCESS_TOKEN = None
LOCAL_FILE = '.fb_access_token'
STATUS_TEMPLATE = u"{name}\033[0m: {message}"


def removeNonAscii(s):
    if isinstance(s, basestring):
        return "".join(i for i in s if ord(i)<128)
    else:
        return str(s)

class FacebookGraphAPI(object):

    def __init__(self):
        self.page = '293778137393372'
        self.token = ACCESS_TOKEN
        self.api_url = "https://graph.facebook.com"
        self.last_url = ''

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
        params['access_token'] = self.token
        url = "%s/%s/%s?%s" % (self.api_url,
                               self.page,
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
       __  _      _
      / _|| |    |_|
     | |_ | |__   _
     |  _|| '_ \ | |
     | |  | |_) || |
     |_|  |_.__/ |_|

    FACEBOOK INSIGHTS
    VERSION: 1.0.0
    '''
    print INTRO_MESSAGE

    if not os.path.exists(LOCAL_FILE):
        LOG.info('Logging you in to facebook...')
        webbrowser.open(get_url('/oauth/authorize',
                                {'client_id':APP_ID,
                                 'redirect_uri':REDIRECT_URI,
                                 'scope':'read_insights,manage_pages,offline_access'}))

        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), RequestHandler)
        while ACCESS_TOKEN is None:
            httpd.handle_request()
    else:
        ACCESS_TOKEN = open(LOCAL_FILE).read()
        LOG.info('Using saved Facebook Access Token...')

    try:
        api = FacebookGraphAPI()
        LOG.info('Connectd to facebook page or app.')
    except:
        api = None
        LOG.error('Cant connect to facebook page or app')


    for name, value in settings.items('insights'):
        insight_path = 'facebook/insights/%s' % (name)
        fullpath = path(insight_path)
        #create the paths
        if not os.path.exists(fullpath):
            LOG.warning('Directory "%s" not exists. Creating it...' % (fullpath))
            try:
                os.makedirs(fullpath)
            except OSError:
                LOG.error('Error creating directory: "%s".' % (fullpath))

        #get insights data
        insights = api.insights__page_posts_impressions()

        #initialize the csv writer
        csvname = '%s-%s.csv' % (name, datetime.datetime.strftime(
                        datetime.datetime.today(), '%Y%m%d%H%M%S'))
        LOG.info(csvname)

        tsvh = csv.writer(open(os.path.join(fullpath, csvname), 'wb'))

        for metric in insights['data']:
                for row in metric['values']:
                    date = datetime.datetime.strptime(
                        row['end_time'], '%Y-%m-%dT%H:%M:%S+0000'
                        ).date() + datetime.timedelta(-1)
                    out = [metric['name'], date,
                           metric['period'], row['value']]

                    #write to csv file
                    tsvh.writerow(out)
    LOG.info('Process Finished Correctly! :)')
