## @namespace SbsOnDemand::Feed
# Module for managing video feeds

import re
try:
    import simplejson as json
except ImportError: 
    import json
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs
import urlparse
import urllib
import config
from Video import Video

## Gets the default set of video feeds
# @return Dict of Video objects, with their name as key
def getDefaultFeeds():
    feeds = {};
    for feed in config.DEFAULT_FEEDS:
        feeds[feed['name']] = Feed(feed)
    return feeds

## Gets the set of video feeds from SBS website menu
# @return Array of dict objects, each object may contain a Feed object and/or an array of child Feeds
# @note Not all feeds are video feeds, in that they may only have a title but no videos
def getMenuFeeds():
    def parseMenuItem(menuItem):
        item = {"feed":Feed(menuItem)}
        if (menuItem.has_key('children')):
            item['children'] = {}
            for childItem in menuItem['children']:
                item['children'][childItem['name']] = parseMenuItem(childItem)
        return item
    
    page = urllib.urlopen(config.MENU_URI)
    data = re.match('^VideoMenu\s*=\s*({.*})$', page.read()).group(1)
    menu = json.loads(data)
    feeds = {}
    for rootMenuName in menu.keys():
        feeds[rootMenuName] = parseMenuItem(menu[rootMenuName])
    return feeds   

## Gets a video feed based on a search query
# @param query the search query 
# @return A Feed object
def searchFeed(query):
    return Feed({"prefix": config.SEARCH_PREFIX, "query":{"m":1,"q":query}})

## Gets a video feed from the specified url
# @param url the absolute url to fetch the feed from
# @return A Feed object
def getFeedFromUrl(url):
    return Feed({"url":url})

## Gets a video feed by its unique feed identifier (PID)
# @param feedId the feed unique identifier 
def getFeedFromId(feedId):
    return Feed({"feedId": feedId})

## Represents a video feed
class Feed(object):
    
    ## Creates a Feed object
    # @param feed the feed to be parsed
    def __init__(self,feed):
        self.feedId = None
        self.url = None
        self._url_prefix = None
        self.title = None
        self.thumbnail = None
        self.query = {}
        self._totalResults = None
        self.startIndex = None
        self.itemsPerPage = None
        self._videos = None
        self._parseFeed(feed)
        
    ## Downloads the feed, allowing it to be parsed
    # @param count whether to ask for the total number of results or not
    # @param startIndex the start index (offset) of entries within the feed to obtain
    # @param itemsPerPage the maximum number of entries to contain within the feed
    def _updateFeed(self, count = True, startIndex = 0, itemsPerPage = 10, sort = 'pubDate'):
        # We can't retrieve videos without a feed id
        if self.feedId is None and self.url is None and self._url_prefix is None:
            raise Exception("Feed ID not specified")

        # Build the URL of the feed
        # This way because it turns out SBS cares about form=json being first...
        url = None
        if self.url:
            url = self.url
        else:
            if self.feedId:
                query = [('form','json'),('range',str(startIndex) + '-' + str(startIndex + itemsPerPage))]
                if count is True:
                    query.append(('count', 'true'))
                if sort:
                    query.append(('sort', sort))
                query += self.query.items()
                url = config.API_BASE + '/f/' + config.MPX_FEEDID + '/' + self.feedId + '?' + urllib.urlencode(query)
            elif self._url_prefix:
                query = [('form','json')]
                if count is True:
                    query.append(('count', 'true'))
                query += self.query.items()
                url = self._url_prefix + '?' + urllib.urlencode(query)
       
        if url:
            # Fetch the feed
            page = urllib.urlopen(url)
            feed = json.load(page)
            self._parseFeed(feed)
        
    ## Parses a feed
    # @param feed the feed to be parsed, in dict form
    def _parseFeed(self, feed):
        self.title = feed.get("name", self.title)
        self.thumbnail = feed.get("thumbnail", self.thumbnail)
        self.query = feed.get("query", self.query)
        self._totalResults = feed.get('totalResults', self._totalResults)
        self.startIndex = feed.get('startIndex', self.startIndex)
        self.itemsPerPage = feed.get('itemsPerPage', self.itemsPerPage)
    
        try:
            self._setFeedId(feed)
        except:
            pass
        if not self.feedId:
            self._url_prefix = feed.get('prefix', None)
            self.url = feed.get('url', None)

        # Form is not a query, get rid of it
        if self.query.has_key('form'):
            del self.query['form']
            
        # Parse video entries
        if feed.has_key('entries'):
            videos = []
            for video in feed['entries']:
                videos.append(Video(video))
            self._videos = videos
        
    def _setFeedId(self, feed):
        if feed.has_key("feedId"):
            self.feedId = feed["feedId"]
        else:
            # Extract feed PID from url
            url = feed.get("furl", None)
            if url is None or len(url) == 0:
                url = feed.get("url",None)
            if url is not None and len(url) > 0:
                parsedurl = urlparse.urlparse(url)
                
                # Extract feed id from parsedurl path
                match = re.match('^/api/video_feed/f/'+config.MPX_FEEDID+'/(.+)$', parsedurl[2]) #parsedurl.path
                if match is None:
                    raise Exception("Cannot extract feed identifier from url")
                self.feedId = match.group(1)
                
                # Extract url query parameters into query dict
                for k, v in parse_qs(parsedurl[4]).iteritems(): #parsedurl.query
                    if len(v)>1:
                        self.query[k] = v
                    else:
                        self.query[k] = v[0] 

    ## Gets the video entries from the feed
    # @param count whether to ask for the total number of results or not
    # @param startIndex the start index (offset) of entries within the feed to obtain
    # @param itemsPerPage the maximum number of entries to contain within the feed
    # @return an array of Video objects
    def getVideos(self, count = True, startIndex = 0, itemsPerPage = 10):
        # Use cached content if we can
        if self._videos is not None and startIndex == self.startIndex and itemsPerPage <= self.itemsPerPage:  # TODO handle pagination (count=true, range=start-finish, etc.)
            if itemsPerPage < self.itemsPerPage:
                return self._videos[0:itemsPerPage]
            else:
                return self._videos
            
        # Call update feed to download new data
        self._updateFeed(count, startIndex, itemsPerPage)
        
        # Return videos
        return self._videos
    
    ## Gets the total number of video entries contained in the feed
    # @return the total number of video entries contained in the feed
    def getTotalResults(self):
        if self.feedId is None:
            return 0
        
        if self._totalResults is not None:
            return self._totalResults
        
        self._updateFeed(True)
        
        return self._totalResults
    ## @see getVideos
    videos = property(getVideos)
    ## @see getTotalResults
    totalResults = property(getTotalResults)
        
