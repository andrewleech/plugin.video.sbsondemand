import sys
import json
import urllib
import urlparse
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

trace_on = False
# if True:
if False:
    pydev_egg="/Applications/PyCharm.app/Contents/debug-eggs/pycharm-debug.egg"
    if pydev_egg not in sys.path:
        sys.path.insert(0,pydev_egg)
    import pydevd
    pydevd.settrace('192.168.0.16', port=51380, stdoutToServer=True, stderrToServer=True)
    trace_on = True

# import resources.scraper
# MenuItems = resources.scraper.MenuItems()

##############################################################
ID = 'plugin.video.sbsondemand'
__XBMC_Revision__   = xbmc.getInfoLabel('System.BuildVersion')
__settings__        = xbmcaddon.Addon( id=ID)
__language__        = __settings__.getLocalizedString
__version__         = __settings__.getAddonInfo('version')
__cwd__             = __settings__.getAddonInfo('path')
__addonname__       = __settings__.getAddonInfo('name')
__addonid__         = __settings__.getAddonInfo('id')

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
##############################################################


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')

def addDir(params, folder = False, info = None, still="DefaultFolder.png"):
    name = params['name']
    if isinstance(name, unicode):
        params['name'] = name.encode('utf8')

    url =  sys.argv[0] + "?" + urllib.urlencode(params)
    a_info = ""
    if info:
        a_info = unicode(info).encode('utf8')
    print "::", url,  params, a_info, "%%"
    liz=xbmcgui.ListItem(name, iconImage=still, thumbnailImage="")
    if info:
        liz.setInfo( type="Video", infoLabels={ "Title":name, "Plot":info})#, "Genre":genre})
        #liz.setInfo("video", {'tagline':info})
    if not folder:
        liz.addContextMenuItems( [
            ("Record to disk", "XBMC.RunPlugin(%s?&%s)"   % (sys.argv[0], url.replace("mode=1", "mode=2") )),
            ("Play at Seek", "XBMC.RunPlugin(%s?&%s)"   % (sys.argv[0], url.replace("mode=1", "mode=3") ))
        ] )

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=folder)
    return ok


webdriver_instance = None
def webDriver():
    global webdriver_instance
    if webdriver_instance is None:
        import webdriver
        from resources import webdriver_plugin

        webdriver_instance = webdriver.Browser()
        pluginfile = webdriver_plugin.__file__
        webdriver_instance.register_plugin(webdriver_plugin.PLUGIN_NAME, pluginfile)
    return webdriver_instance


##############################################################
def Menu(params):
    from resources.sbsOnDemand import SbsOnDemand
    feed = None

    if not params.get('feedId'):
        menu = SbsOnDemand.Menu.Menu(params.get('path')).getMenu()
        startIndex = 0

        if isinstance(menu, list):
            for name, item in menu:
                if isinstance(item, SbsOnDemand.Feed.Feed):
                    params={ 'name': name,
                             'feedId': item.feedId,
                             'feedFilter': json.dumps(item.filter),
                             'mode' : params["mode"],
                             'startIndex': startIndex,
                             'itemsPerPage': 40,
                             }
                elif isinstance(item, SbsOnDemand.Menu.Menu):
                    params={ 'name':name,
                             'path':item.path,
                             'mode' : params["mode"],
                             'startIndex': startIndex,
                             'itemsPerPage': 40,
                             }
                else:
                    raise NotImplementedError
                addDir(params, folder=True, still=icon)
        elif isinstance(menu, tuple):
            name, feed = menu

    else:
        if 'feedFilter' in params:
            params['filter'] = json.loads(params['feedFilter'])
        feed = SbsOnDemand.Feed.Feed(params)

    if feed:
        startIndex = int(params.get('startIndex') or 0)
        itemsPerPage = int(params.get('itemsPerPage') or 40)
        videos = feed.getVideos(startIndex = startIndex, itemsPerPage = itemsPerPage)

        if videos:
            for video in videos:

                browser_only = True #__settings__.getSetting('browser_only')

                prevBitrate = 0
                url = None
                webdriver = False
                medias = video.getMedia().get('content')
                for content in medias:
                    if content.contentType == 'video' and (content.bitrate > prevBitrate or content.bitrate is None):# and content.url:
                        if browser_only:
                            url = content.browserUrl # much quicker
                        else:
                            url = content.videoUrl
                        webdriver = content.format == SbsOnDemand.Media.TYPE_BROWSER
                        prevBitrate = content.bitrate

                if url:
                    addDir(params={ 'name':video.title,
                                    'feedId':feed.feedId,
                                    'mode' : 'playVideo',
                                    'url' : url,
                                    'webdriver' : webdriver,
                                 },
                           folder=False,
                           info=video.description,
                           still=video.thumbnail
                           )

            if feed.totalResults and feed.totalResults > len(videos):
                addDir(params={  'name':"Next Page",
                                 'feedId':feed.feedId,
                                 'feedFilter': json.dumps(feed.filter),
                                 'mode' : params["mode"],
                                 'startIndex': startIndex + len(videos),
                                 'itemsPerPage': itemsPerPage,
                                 },
                       folder=True)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def Play(params):
    if params.get('webdriver', False):
        browser = webDriver()
        url = params['url']

        browser.get(url)
        # browser.bring_browser_to_front()
        from resources.webdriver_plugin import SBS_KEYMAP, jsTargetBy, jsTarget
        browser.show_control_window(jsTargetBy, jsTarget, SBS_KEYMAP)
        browser.close()

def parse_args(args):
    out = {}
    if args[2]:
        out = dict(urlparse.parse_qsl(args[2].strip('?')))
    else:
        out["mode"]     = "0"
        out["feedId"]   = []
        out["url"]      = ""

    return out

def openWebdriverSettings(*_):
    import webdriver
    webdriver.openSettings()

def main():

    params = parse_args(sys.argv)
    # print "##", sys.argv, params
    {
    '0'                 : Menu,
    'playVideo'         : Play,
    'webdriverSettings' : openWebdriverSettings

    }[params["mode"]](params)

try:
    main()
except Exception as ex:
    print __import__('traceback').format_exc()
    print str(ex)
    raise
finally:
    if trace_on:
        pydevd.stoptrace()