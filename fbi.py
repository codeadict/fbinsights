#!/usr/bin/env python
#
# Facebook Insights(FBI) 1.0.0
# Copyright 2014. All Rights Reserved.
# Developer: Dairon Medina <dairon.medina@gmail.com>
# Coded with pride in Ecuador, South America
from datetime import datetime
import os
import itertools
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
                        'application_tos_views_unique',
                        'application_permission_views_top',
                        'application_permission_views_top_unique',
                        'application_permission_grants_top',
                        'application_permission_grants_top_unique',
                        'application_block_adds',
                        'application_block_adds_unique',
                        'application_block_removes',
                        'application_block_removes_unique',
    ],
    "app-mobile-users":[
                        'application_mobile_app_installs',
    ],
    "app-related-content":[
                        'application_like_adds',
                        'application_like_adds_unique',
                        'application_like_removes',
                        'application_like_removes_unique',
                        'application_comment_adds',
                        'application_comment_adds_unique',
                        'application_photos',
                        'application_photos_unique',
                        'application_shares',
                        'application_shares_unique',
                        'application_status_updates',
                        'application_status_updates_unique',
                        'application_stream_stories',
                        'application_stream_stories_unique',
                        'application_feed_form_views',
                        'application_feed_form_views_unique',
                        'application_feed_form_views_login',
                        'application_feed_form_views_login_unique',
                        'application_feed_form_views_logout',
    ],
    "social-plugins": [
                        'application_widget_activity_views',
                        'application_widget_activity_views_unique',
                        'application_widget_activity_views_login',
                        'application_widget_activity_views_login_unique',
                        'application_widget_activity_views_logout',
                        'application_widget_activity_views_external_referrals',
                        'application_widget_comments_views',
                        'application_widget_comments_views_unique',
                        'application_widget_comments_views_login',
                        'application_widget_comments_views_login_unique',
                        'application_widget_comments_views_logout',
                        'application_widget_fan_views',
                        'application_widget_fan_views_unique',
                        'application_widget_fan_views_login',
                        'application_widget_fan_views_login_unique',
                        'application_widget_fan_views_logout',
                        'application_widget_fan_views_external_referrals',
                        'application_widget_like_views',
                        'application_widget_like_views_unique',
                        'application_widget_like_views_login',
                        'application_widget_like_views_login_unique',
                        'application_widget_like_views_logout',
                        'application_widget_like_views_external_referrals',
                        'application_widget_live_stream_views',
                        'application_widget_live_stream_views_unique',
                        'application_widget_live_stream_views_login',
                        'application_widget_live_stream_views_login_unique',
                        'application_widget_live_stream_views_logout',
                        'application_widget_live_stream_views_external_referrals',
                        'application_widget_recommendation_views',
                        'application_widget_recommendation_views_unique',
                        'application_widget_recommendation_views_login',
                        'application_widget_recommendation_views_login_unique',
                        'application_widget_recommendation_views_logout',
                        'application_widget_recommendation_views_external_referrals',
                        'application_widget_share_views',
                        'application_widget_share_views_unique',
                        'application_widget_views',
                        'application_widget_views_unique',
                        'application_widget_views_login',
                        'application_widget_views_login_unique',
                        'application_widget_views_logout',
    ],
    "open-graph": [
                        'application_opengraph_action_create',
                        'application_opengraph_action_delete',
                        'application_opengraph_object_create',
                        'application_opengraph_object_update',
                        'application_opengraph_story_impressions',
                        'application_opengraph_story_click',
                        'application_opengraph_story_like',
                        'application_opengraph_story_unlike',
                        'application_opengraph_story_comment',
                        'application_opengraph_story_hide',
                        'application_opengraph_story_hide_all',
                        'application_opengraph_story_report_spam',
                        'application_opengraph_link_impression',
                        'application_opengraph_link_click',
                        'application_opengraph_timeline_impressions',
                        'application_opengraph_timeline_spam',
                        'application_opengraph_timeline_clicked',

    ],
    "canvas-app-only-metrics": [
                        'application_canvas_views',
                        'application_canvas_views_unique',
                        'application_canvas_views_login',
                        'application_canvas_views_login_unique',
                        'application_canvas_views_logout',
                        'application_canvas_views_internal_referrals',
                        'application_canvas_views_external_referrals',
    ],
    "tab-app-only-metrics": [
                        'application_tab_views',
                        'application_tab_views_unique',
    ],
    "api-performance-for-apps": [
                        'application_api_calls',
                        'application_api_calls_top',
                        'application_api_calls_unique',
                        'application_api_errors',
                        'application_api_errors_rate',
                        'application_api_errors_top',
                        'application_api_time_average',
                        'application_canvas_errors',
                        'application_canvas_errors_rate',
                        'application_canvas_time_average',
    ],
    "page-and-post-stories": [
                        'page_stories',
                        'page_storytellers',
                        'page_stories_by_story_type',
                        'page_storytellers_by_story_type',
                        'page_storytellers_by_age_gender',
                        'page_storytellers_by_city',
                        'page_storytellers_by_country',
                        'page_storytellers_by_locale',
                        'post_stories',
                        'post_storytellers',
                        'post_stories_by_action_type',
                        'post_storytellers_by_action_type',
    ],
    "page-impressions": [
                        'page_impressions',
                        'page_impressions_unique',
                        'page_impressions_paid',
                        'page_impressions_paid_unique',
                        'page_impressions_organic',
                        'page_impressions_organic_unique',
                        'page_impressions_viral',
                        'page_impressions_viral_unique',
                        'page_impressions_by_story_type',
                        'page_impressions_by_story_type_unique',
                        'page_impressions_by_city_unique',
                        'page_impressions_by_country_unique',
                        'page_impressions_by_age_gender_unique',
                        'page_impressions_frequency_distribution',
                        'page_impressions_viral_frequency_distribution',
                        'page_impressions_by_paid_non_paid',
                        'page_impressions_by_paid_non_paid_unique',
    ],
    "page-engagement": [
                        'page_engaged_users',
                        'page_consumptions',
                        'page_consumptions_unique',
                        'page_consumptions_by_consumption_type',
                        'page_consumptions_by_consumption_type_unique',
                        'page_places_checkin_total',
                        'page_places_checkin_total_unique',
                        'page_places_checkin_mobile',
                        'page_places_checkin_mobile_unique',
                        'page_places_checkins_by_age_gender',
                        'page_places_checkins_by_locale',
                        'page_places_checkins_by_country',
                        'page_negative_feedback',
                        'page_negative_feedback_unique',
                        'page_negative_feedback_by_type',
                        'page_negative_feedback_by_type_unique',
                        'page_positive_feedback_by_type',
                        'page_positive_feedback_by_type_unique',
                        'page_fans_online',
                        'page_fans_online_per_day',
    ],
    "page-user-demographics": [
                        'page_fans',
                        'page_fans_locale',
                        'page_fans_city',
                        'page_fans_country',
                        'page_fans_gender_age',
                        'page_fan_adds',
                        'page_fan_adds_unique',
                        'page_fans_by_like_source',
                        'page_fans_by_like_source_unique',
                        'page_fan_removes',
                        'page_fan_removes_unique',
                        'page_fans_by_unlike_source_unique',
    ],
    "page-views": [
                        'page_views',
                        'page_views_unique',
                        'page_views_login',
                        'page_views_login_unique',
                        'page_views_logout',
                        'page_views_external_referrals',
    ],
    "page-posts": [
                        'page_posts_impressions',
                        'page_posts_impressions_unique',
                        'page_posts_impressions_paid',
                        'page_posts_impressions_paid_unique',
                        'page_posts_impressions_organic',
                        'page_posts_impressions_organic_unique',
                        'page_posts_impressions_viral',
                        'page_posts_impressions_viral_unique',
                        'page_posts_impressions_frequency_distribution',
                        'page_posts_impressions_by_paid_non_paid',
                        'page_posts_impressions_by_paid_non_paid_unique',
    ],
    "page-post-impressions": [
                        'post_impressions',
                        'post_impressions_unique',
                        'post_impressions_paid',
                        'post_impressions_paid_unique',
                        'post_impressions_fan',
                        'post_impressions_fan_unique',
                        'post_impressions_fan_paid',
                        'post_impressions_fan_paid_unique',
                        'post_impressions_organic',
                        'post_impressions_organic_unique',
                        'post_impressions_viral',
                        'post_impressions_viral_unique',
                        'post_impressions_by_story_type',
                        'post_impressions_by_story_type_unique',
                        'post_impressions_by_paid_non_paid',
                        'post_impressions_by_paid_non_paid_unique',
    ],
    "page-post-engagement": [
                        'post_consumptions',
                        'post_consumptions_unique',
                        'post_consumptions_by_type',
                        'post_consumptions_by_type_unique',
                        'post_engaged_users',
                        'post_negative_feedback',
                        'post_negative_feedback_unique',
                        'post_negative_feedback_by_type',
                        'post_negative_feedback_by_type_unique',
    ],
    "domain-content": [
                        'domain_feed_clicks',
                        'domain_feed_views',
                        'domain_stories',
                        'domain_widget_comments_adds',
                        'domain_widget_comments_views',
                        'domain_widget_comments_feed_views',
                        'domain_widget_comments_feed_clicks',
                        'domain_widget_like_views',
                        'domain_widget_likes',
                        'domain_widget_like_feed_views',
                        'domain_widget_like_feed_clicks',
                        'domain_widget_send_views',
                        'domain_widget_send_clicks',
                        'domain_widget_send_inbox_views',
                        'domain_widget_send_inbox_clicks',
    ],
    "page-like-sources": [
                        'page_suggestion',
                        'timeline',
                        'ads',
                        'registration',
                        'mobile',
                        'wizard-suggestion',
                        'profile-connect',
                        'external-connect',
                        'recommended-pages',
                        'favorites',
                        'api',
                        'page-browser',
                        'hovercard',
                        'search',
                        'page-profile',
                        'ticker',
                        'like-story',
    ],
    "negative-feedback-types": [
                        'hide_all',
                        'hide',
                        'unlike_page',
                        'report_spam',
    ],
    "positive-feedback-types": [
                        'like',
                        'comment',
                        'link',
    ],
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
LOCAL_FILE = '.fb_access_token'


class FacebookGraphAPI(object):

    def __init__(self):
        self.page = settings.get('facebook', 'app_or_page')
        self.token = settings.get('facebook', 'access_token')
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
        LOG.info('Making request to "%s"' % (url))
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

        for k, v in insights_groups.iteritems():
            if (k == name) and (bool(value) is True):
                for metric in v:
                    filepath = os.path.join(fullpath, metric)
                    #create the paths
                    if not os.path.exists(filepath):
                        LOG.warning('Directory "%s" not exists. Creating it...' % (filepath))
                        try:
                            os.makedirs(filepath)
                        except OSError:
                            LOG.error('Error creating directory: "%s".' % (filepath))

                    metric_name = 'insights__%s' % metric

                    #get insights data
                    insights = getattr(api, metric_name)()

                    #initialize the csv writer
                    csvname = '%s-%s.csv' % (metric, datetime.datetime.strftime(
                                                datetime.datetime.today(), '%Y%m%d%H%M%S'))
                    LOG.info(csvname)

                    tsvh = csv.writer(open(os.path.join(filepath, csvname), 'wb'))
                    header = ['date', 'period', 'metric_values']
                    #tsvh.writerow(header)

                    for metric in insights['data']:
                            for row in metric['values']:
                                date = datetime.datetime.strptime(row['end_time'], '%Y-%m-%dT%H:%M:%S+0000').date() + datetime.timedelta(-1)

                                if type(row['value']) is dict:
                                    values = list(row['value'].values())
                                    print "VALORES"
                                    print values
                                    out = [date, metric['period']]
                                    out = out.extend(values)
                                else:
                                    out = [date, metric['period'], row['value']]

                                print out


                                #write to csv file
                                tsvh.writerow(out)
    LOG.info('Process Finished Correctly! :)')
