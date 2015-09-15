## @namespace SbsOnDemand::Video
# Module for managing videos

import re
try:
    import simplejson as json
except ImportError: 
    import json
import urllib, urlparse
import config
import xml.etree.ElementTree as xml
from Category import Category
from Media import Media, TYPE_BROWSER

## This exception is raised when a method is invoked on a Video object that requires an ID
class NoIDException(Exception):
    def __str__(self):
        return "No ID Specified"

class NotUsableJson(Exception):
    def __str__(self):
        return "The Json object to parse isn't usable"

## Gets a video from its id
# @param videoId the ID number of the video
# @return a Video object
def getVideo(videoId):
    video = Video({"id":videoId})
    video._updateVideo()
    return video

## Represents a single video
class Video(object):

    ## Creates a video object
    # @param params the video data to be parsed
    def __init__(self,params):
        self._parseVideo(params)
        
    ## Parses video data and populates Video data members
    # @param params the video data to be parsed
    def _parseVideo(self,params):
        if (params.has_key('isException')):
            raise(NotUsableJson)
        videoId = params.get('id',None)
        if videoId is not None and videoId.isdigit():
            self.id = str(videoId)
        elif videoId is not None:
            self.id = re.search("\d+",videoId).group(0)
        else:
            self.id = None
        self.title = params.get('title',None)
        self.description = params.get('description',None)
        self.thumbnail = params.get('plmedia$defaultThumbnailUrl',None)
        self.episodeNumber = params.get('pl1$episodeNumber',None)
        self.availableDate = params.get('media$availableDate',None)
        self.expirationDate = params.get('media$expirationDate',None)
        self.programName = params.get('pl1$programName',None)
        self.pilatDealcode = params.get('pl1$pilatDealcode',None)
        keywords = params.get('media$keywords',None)
        if keywords is not None:
            self.keywords = keywords.split(",")
        else:
            self.keywords = None
        self.pubDate = params.get('pubDate',None)
        self.categories = []
        for category in params.get('media$categories',[]):
            self.categories.append(Category(category))
        self.duration = None
        self._media = {}
        self._media['content'] = []
        self._media['thumbnails'] = []
        self._mediaHasUrl = True
        mediaContent = params.get('media$content',[])
        for media in mediaContent:
            media['id'] = self.id
            mediaObj = Media(media)
            self._media['content'].append(mediaObj)
            if mediaObj.url is None:
                self._mediaHasUrl = False
            if self.duration is None and mediaObj.duration is not None:
                self.duration = mediaObj.duration
        mediaThumbnails = params.get('media$thumbnails',[])
        for media in mediaThumbnails:
            mediaObj = Media(media)
            self._media['thumbnails'].append(mediaObj)
            if mediaObj.url is None:
                self._mediaHasUrl = False
                
    ## Downloads the video data, allowing it to be parsed
    def _updateVideo(self):
        url = config.SINGLE_FEED_PREFIX + self.id + '?' + urllib.urlencode({"form":"json"})
        page = urllib.urlopen(url)
        data = json.load(page)
        try:
            self._parseVideo(data)
        except(NotUsableJson):
            self._getOnDemand()

    def _getOnDemand(self):
        url = config.ONDEMAND_UI_BASE_URI + self.id + '?' + urllib.urlencode({"form":"json"})
        print 'Try parse on demand: {0}'.format(url)
        page = urllib.urlopen(url)
        m = re.search('vod.cache.video.+?({.+})', page.read())
        jsonString = m.group(1)
        self._parseVideo(json.loads(jsonString))
        
    ## Gets the available media associated with the video
    # @param withUrl whether to ensure that the media has a download url
    # @return a dict with two keys, `content` and `thumbnails`, each containing an array of Media objects 
    def getMedia(self, withUrl = True):
        if self.id is None:
            raise NoIDException()
        if not self._mediaHasUrl and withUrl:
            self._updateVideo()
            return self._media
        else:
            return self._media

    ## Get the browser video url
    # @return the url to playback video is a web browser
    def getBrowserUrl(self):
        format = TYPE_BROWSER
        url = "{0}{1}".format(config.ONDEMAND_UI_FULLSCREEN_URI,self.id)
        return url

    ## @see getMedia
    media = property(getMedia)
    
