import api.views
from rest_framework import status
from rest_framework.decorators import api_view
import uqx_api.courses
from collections import OrderedDict

from datetime import datetime, timedelta
import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from uqx_api import settings
from optparse import OptionParser

# Logging
import logging
logger = logging.getLogger(__name__)


def youtube_setup():
    global api_youtube
    global api_youtube_analytics

    youtube_file = "youtube.json"
    youtube_scopes = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/yt-analytics.readonly"]
    youtube_servicename = "youtube"
    youtube_version = "v3"
    youtube_analytics_servicename = "youtubeAnalytics"
    youtube_analytics_version = "v1"

    flow = OAuth2WebServerFlow(client_id=settings.YOUTUBE_CLIENT_ID,
                           client_secret=settings.YOUTUBE_CLIENT_SECRET,
                           scope=" ".join(youtube_scopes))

    storage = Storage("youtube_oauth2.json")
    youtube_credentials = storage.get()

    print youtube_credentials

    if youtube_credentials is None or youtube_credentials.invalid:
        youtube_credentials = run(flow, storage)

    http = youtube_credentials.authorize(httplib2.Http())
    api_youtube = build(youtube_servicename, youtube_version, http=http)
    api_youtube_analytics = build(youtube_analytics_servicename, youtube_analytics_version, http=http)


def youtube_query(command, options):

    channels_response = api_youtube.channels().list(
        mine=True,
        part="id"
    ).execute()

    response = {'status': 'bad command'}

    if command == "get_stats":

        for channel in channels_response.get("items", []):
            response = {'id': channel["id"], 'items': []}
            analytics_response = api_youtube_analytics.reports().query(
                ids="channel==%s" % response['id'],
                metrics=options.metrics,
                dimensions=options.dimensions,
                start_date=options.start_date,
                end_date=options.end_date,
                start_index=options.start_index,
                max_results=options.max_results,
                sort=options.sort
            ).execute()

            headers = analytics_response.get("columnHeaders", [])
            rows = analytics_response.get("rows", [])

            for i in range(0, len(rows)):
                item = {}
                hi = 0
                for val in rows[i]:
                    item[headers[hi]['name']] = val
                    hi += 1
                response['items'].append(item)

            response['status'] = 'success'

    return response



@api_view(['GET'])
def videos_views(request):
    """
    Lists the course information, in particular the course ID
    """







    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    youtube_setup()

    now = datetime.now()
    one_day_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    one_week_ago = (now - timedelta(days=365)).strftime("%Y-%m-%d")
    parser = OptionParser()
    parser.add_option("--metrics", dest="metrics", help="Report metrics",
      default="views,comments,favoritesAdded,favoritesRemoved,likes,dislikes,shares")
    parser.add_option("--dimensions", dest="dimensions", help="Report dimensions",
      default="video")
    parser.add_option("--start-date", dest="start_date",
      help="Start date, in YYYY-MM-DD format", default=one_week_ago)
    parser.add_option("--end-date", dest="end_date",
      help="End date, in YYYY-MM-DD format", default=one_day_ago)
    parser.add_option("--start-index", dest="start_index", help="Start index",
      default=1, type="int")
    parser.add_option("--max-results", dest="max_results", help="Max results",
      default=10, type="int")
    parser.add_option("--sort", dest="sort", help="Sort order", default="-views")
    (options, args) = parser.parse_args()

    data = youtube_query("get_stats", options)
    return api.views.api_render(request, data, status.HTTP_200_OK)


