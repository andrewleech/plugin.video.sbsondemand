## @namespace SbsOnDemand::Media
# Module for managing a/v media

import urllib
import urlparse
import config
import re

TYPE_RTMP   = 'RTMP secured'
TYPE_PUBLIC = 'Public'
TYPE_BROWSER = 'Browser'

## Represents an exception that occurs when a method is invoked on a media that doesn't support that method
class InvalidMediaType(Exception):
    pass

## This exception is raised when a method expects an RTMP URL, but doesn't have one
class NotRTMPException(Exception):
    def __str__(self):
        return "Not an RTMP URL"

## Represents a media (rendition) for a single video
class Media(object):
    
    ## Creates a media object
    # @param params the media data
    def __init__(self,params):
        self.audioChannels = params.get('plfile$audioChannels',None)
        self.audioSampleRate = params.get('plfile$audioSampleRate',None)
        self.bitrate = params.get('plfile$bitrate',None)
        self.checksums = params.get('plfile$checksums',None)
        self.contentType = params.get('plfile$contentType',None)
        self.duration = params.get('plfile$duration',None)
        self.expression = params.get('plfile$expression',None)
        self.fileSize = params.get('plfile$fileSize',None)
        self.frameRate = params.get('plfile$frameRate',None)
        self.format = params.get('plfile$format',None)
        self.height = params.get('plfile$height',None)
        self.isDefault = params.get('plfile$isDefault',None)
        self.language = params.get('plfile$language',None)
        self.sourceTime = params.get('plfile$sourceTime',None)
        self.url = params.get('plfile$downloadUrl',None)
        self.width = params.get('plfile$width',None)
        self.assetTypes = params.get('plfile$assetTypes',None)
        self.id = params.get('id', None)
        self._smil = None
        self._smilDOM = None
        
    ## Get the raw url for the media
    # @return a absolute url to the content or SMIL file for the content
    def getUrl(self):
        return self.url
        
    ## Get the raw SMIL data for the media
    # @return a string of raw SMIL data from the server
    # @warning This function is only valid for video media, calling it on other contentTypes will trigger a InvalidMediaType exception
    def getSMIL(self):
        if self.contentType != "video":
            raise InvalidMediaType();
        if self._smil is None:
            smil_uri = ''
            opener = urllib.FancyURLopener(config.PROXY)
            fullurl = "{0}{1}".format(config.ONDEMAND_UI_BASE_URI,self.id)
            f = opener.open(fullurl)
            rsp = f.read()
            og_video = re.findall('<.*?og:video.*?>', rsp)
            if (len(og_video) < 1):
                print "Can't find the video part on the webpage.  HELP!"
                pass #Need to complain loudly
            else:
                m = re.search('content="(.+?)"', og_video[0])
                videourl = m.group(1)
                p = urlparse.parse_qs(videourl)
                smil_uri = p.get(config.RELEASE_URL_KEY,[''])[0]
                if (smil_uri != ''):
                    smil_uri += "&format=smil"
            if len(smil_uri) > 0:
                f = opener.open(smil_uri)
                self._smil = f.read()
                return self._smil
    ## Get the SMIL data parsed by xml.dom.minidom
    # @return a Document parsed by xml.dom.minidom
    # @warning This function is only valid for video media, calling it on other contentTypes will trigger a InvalidMediaType exception
    def getSMILDOM(self):
        if self.contentType != "video":
            raise InvalidMediaType();
        if self._smilDOM is None:
            self._parseSMIL()
        return self._smilDOM
    
    ## Parse the SMIL data with xml.dom.minidom
    # @warning This function is only valid for video media, calling it on other contentTypes will trigger a InvalidMediaType exception
    def _parseSMIL(self):
        if self.contentType != "video":
            raise InvalidMediaType();
        import xml.dom.minidom
        smil = self.getSMIL()
        self._smilDOM = xml.dom.minidom.parseString(smil) if smil else None
    
    ## Get the base url
    # @return the base url (usually for rtmp streams in the form of "rtmp://server/path?auth=token")
    # @warning This function is only valid for video media, calling it on other contentTypes will trigger a InvalidMediaType exception
    def getBaseUrl(self):
        if self.contentType != "video":
            raise InvalidMediaType();
        if self._smilDOM is None:
            self._parseSMIL()
        if self._smilDOM:
            for meta in self._smilDOM.getElementsByTagName('meta'):
                if len(meta.getAttribute('base'))>0:
                    return meta.getAttribute('base')
    
    ## Get the video url
    # @return the video url (usually for rtmp streams in the form of "mp4:path/video.mp4") 
    # @warning This function is only valid for video media, calling it on other contentTypes will trigger a InvalidMediaType exception
    def getVideoUrl(self):
        if self.contentType != "video":
            raise InvalidMediaType()
        if self.assetTypes[0] == TYPE_PUBLIC:
            return self.url
        elif self.assetTypes[0] == TYPE_RTMP:
            medias = self._videosFromSmil()
            try:
                return self._watchableUrlFromSrc(medias[self.bitrate])
            except:
                if medias:
                    return medias.items().pop()[1]
                else:
                    self.format = TYPE_BROWSER
                    self.url = "{0}{1}".format(config.ONDEMAND_UI_FULLSCREEN_URI,self.id)
                    return self.url

    ## Get the browser video url
    # @return the video url (usually for rtmp streams in the form of "mp4:path/video.mp4")
    # @warning This function is only valid for video media, calling it on other contentTypes will trigger a InvalidMediaType exception
    def getBrowserUrl(self):
        if self.contentType != "video":
            raise InvalidMediaType()
        self.format = TYPE_BROWSER
        self.url = "{0}{1}".format(config.ONDEMAND_UI_FULLSCREEN_URI,self.id)
        return self.url


    
    ## Get captions for the media
    # @return an array of dict objects, each containing the src, lang, and type of the caption    
    # @warning This function is only valid for video media, calling it on other contentTypes will trigger a InvalidMediaType exception
    def getCaptions(self):
        if self.contentType != "video":
            raise InvalidMediaType();
        if self._smilDOM is None:
            self._parseSMIL()
        captions = []
        for textstream in self._smilDOM.getElementsByTagName('textstream'):
            if len(textstream.getAttribute('src')) == 0:
                continue
            captions.append({
                             "src":textstream.getAttribute('src'),
                             "lang":textstream.getAttribute('lang'),
                             "type":textstream.getAttribute('type')
                             })
        return captions
    
    def _watchableUrlFromSrc(self,src):
        url = re.sub('(\d+)K.mp4', r',\1,K.mp4', src)
        return url + config.VALID_URL_SUFFIX

    ## Get the associated videos from smil file
    def _videosFromSmil(self):
        if self._smilDOM is None:
            self._parseSMIL()

        medias = {}
        if self._smilDOM:
            for video in self._smilDOM.getElementsByTagName('video'):
                if len(video.getAttribute('src'))>0:
                    bitrate = int(video.getAttribute('system-bitrate'))
                    src = video.getAttribute('src')
                    medias[bitrate] = src
                    print '{0} {1}'.format(bitrate, src)
        return medias
    
    ## @see getBaseUrl
    baseUrl = property(getBaseUrl)
    ## @see getVideoUrl
    videoUrl = property(getVideoUrl)
    ## @see getBrowserUrl
    browserUrl = property(getBrowserUrl)
    ## @see getCaptions
    captions = property(getCaptions)
