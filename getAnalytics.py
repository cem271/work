#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script returns the desired metrics for videos in a given CSV list. 
# For each individual video, the script returns the aggregate values from
# a set period of time the beginning date of which is the day the video 
# was published.

# You also need to create yourself a client_secrets.json using the Google Developers Dashboard.
# Follow the instructions on how to use the YouTube API to create one.

# By default the script reads from a file called 'videolist.csv' and outputs
# to a file called 'output.csv.' The names of these files can be changed using
# the arguments --source and --output, respectively. 

# Also by default, the script returns the first 7 day values. This can be changed
# with the argument --count. 

# Lastly, the script will by default return the following metrics: 
# views,likes,dislikes,shares,comments,estimatedMinutesWatched,averageViewPercentage,subscribersGained,subscribersLost.
# This can be changed by using the argument --metrics.

# Example usage:
# YourComputer:yourDirectory you$ python getAnalytics.py --source="myVids.csv" --output="myData.csv" --count=30 --metrics="views"



import datetime
import httplib2
import os
import sys
import csv
import time

reload(sys)
sys.setdefaultencoding('utf-8')

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
startTime = time.time()

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data and YouTube Analytics
# APIs for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# These OAuth 2.0 access scopes allow for read-only access to the authenticated
# user's account for both YouTube Data API resources and YouTube Analytics Data.
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v1"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This function authenticates this script, creating an oauth2 file
# and storing it in the same directory as the script. If the oauth2 file
# already exists, it simply loads it up.
def get_authenticated_services(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(YOUTUBE_SCOPES),
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  http = credentials.authorize(httplib2.Http())

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=http)
  youtube_analytics = build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION, http=http)

  return (youtube, youtube_analytics)

# Need to get the channel ID so that the analytics query can be done.
def get_channel_id(youtube):
  channels_list_response = youtube.channels().list(
    mine=True,
    part="id"
  ).execute()

  return channels_list_response["items"][0]["id"]

# Makes a query to retrieve the title of a video with a given video id.
def getName(youtube,videoid):
  videoname=''
  response = youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
  videoname = response["items"][0]["snippet"]["title"]
  return videoname

# Makes a query to retrieve the publishing date of a video with a given video id.
# Accounts for private videos, which do not have publishing dates. For these,
# the function returns nothing.
def getPubDate(youtube, videoid):
  pubDate = datetime.datetime.now()
  video_response = youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
  try:
    pubDate = video_response["items"][0]["snippet"]["publishedAt"]
    pubDate = pubDate[0:10]
  except:
    return
  #print pubDate
  return pubDate

# Makes a query to retrieve the publishing hour of a video with a given video id.
# Accounts for private videos, which do not have publishing dates. For these,
# the function returns nothing. By default, hour is in GMT.
def getPubHour(youtube, videoid):
  pubDate = datetime.datetime.now()
  video_response = youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
  try:
    pubHour = video_response["items"][0]["snippet"]["publishedAt"]
    pubHour = pubHour[11:19]
  except:
    return
  #print pubDate
  return pubHour

# For a given publishing date, this function creates an endate, which in effect
# creates a set period from which we can collect data.
def setEndDate(pubDate):
  #PubDate should be in YYYY-MM-DD format
  #Gets the date ranges required to acquire periodic data.
  count =int(args.count) - 1
  dateitems = [int(item) for item in pubDate.split('-')]
  pubDate = datetime.datetime(dateitems[0],dateitems[1],dateitems[2])
  endDate = (pubDate + datetime.timedelta(days=count)).strftime("%Y-%m-%d")
  ##print pubDate.strftime("%Y-%m-%d")
  ##print endDate
  return endDate

# Makes a query to get analytics information of a video with the given video id.
def queryVideo(youtube_analytics,channel_id,videoid,startdate,enddate):
  analytics_query_response = youtube_analytics.reports().query(
    ids="channel==%s" % channel_id,
    metrics=args.metrics,
    dimensions='video',
    start_date=startdate,
    end_date=enddate,
    max_results=10,
    sort='-views',
    filters='video==%s' % videoid
    ).execute()
  # print analytics_query_response
  return analytics_query_response

# The main function that runs the entire code. It runs queryVideo() on a list of
# video ids from a CSV file in the same directory as the script. In turn, it
# creates an output CSV file with the analytics items from queryVideo().
def getAnalytics(youtube_analytics, channel_id):
  with open (args.source+'.csv') as allvids:
    reader = csv.DictReader(allvids)
    videos = []
    for row in reader:
      videos.append(row['ID'])
  with open (args.name+'.csv', 'wb') as output:
    writer = csv.writer(output)
    i = 0
    headers = ['PubDate','PubHour','Title','ID','Views','Likes','Dislikes','Shares','Comments','Minutes Watched','Average % Viewed','Subscribers Gained','Subscribers Lost']
    writer.writerow(headers)
    while i < len(videos):
      videoid = videos[i]
      sys.stdout.write('\rCurrently getting information for: %s Progress: %i/%i' % (str(videoid), int(i), int(len(videos))))
      sys.stdout.flush()
      
      videoname = getName(youtube, videoid)
      videoname = videoname.encode('utf8')
      pubDate = getPubDate(youtube, videoid)
      pubHour = getPubHour(youtube, videoid)
      endDate = setEndDate(pubDate)

      result = queryVideo(youtube_analytics,channel_id,videoid,pubDate,endDate)

      for row in result.get("rows",[]):
        rows=[pubDate, pubHour]
        rows.append(videoname)
        for value in row:
          rows.append(value)
        writer.writerow(rows)
      i += 1
  print "\nDone."
  print "It took", time.time()-startTime, 'seconds to get data from', i, 'videos.'


if __name__ == "__main__":
  now = datetime.datetime.now()

  argparser.add_argument("--count", help="Set range. Default brings 7 day views. ", default=7)
  argparser.add_argument("--name", help="Set output filename. Default is output.csv", default='output')
  argparser.add_argument("--source", help="Set source of video Ids. Default is videolist.csv", default='videolist')
  argparser.add_argument("--metrics", help="Set metrics. Default is= views,likes,dislikes,shares,comments,estimatedMinutesWatched,averageViewPercentage,subscribersGained,subscribersLost", 
    default='views,likes,dislikes,shares,comments,estimatedMinutesWatched,averageViewPercentage,subscribersGained,subscribersLost')
  args = argparser.parse_args()


  (youtube, youtube_analytics) = get_authenticated_services(args)
  try:
    channel_id = get_channel_id(youtube)
    getAnalytics(youtube_analytics, channel_id)

  except KeyboardInterrupt:
    print "User aborted."
    print "You waited", time.time()-startTime, 'seconds before giving up.'
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
