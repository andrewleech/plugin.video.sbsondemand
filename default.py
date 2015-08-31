import sys
import json
import urllib
import urlparse
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from webdriver._utils import *

trace_on = False
# if True:
if False:
    pydev_egg="/Applications/PyCharm.app/Contents/debug-eggs/pycharm-debug.egg"
    if pydev_egg not in sys.path:
        sys.path.insert(0,pydev_egg)
    import pydevd
    pydevd.settrace('192.168.0.16', port=51380, stdoutToServer=True, stderrToServer=True)
    trace_on = True


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
    if isinstance(params.get('feedPath'), unicode):
        params['feedPath'] = params['feedPath'].encode('utf8')
    url =  sys.argv[0] + "?" + urllib.urlencode(params)
    a_info = ""
    if info:
        a_info = unicode(info).encode('utf8')
    print "::", url,  params, a_info, "%%"
    liz=xbmcgui.ListItem(name, iconImage=still, thumbnailImage="")
    if info:
        liz.setInfo( type="Video", infoLabels={ "Title":name, "Plot":info})#, "Genre":genre})

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
        path = params.get('path')
        startIndex = 0
        itemsPerPage = 40
        menu = SbsOnDemand.Menu.Menu(path, startIndex, itemsPerPage).getMenu()

        if isinstance(menu, list):
            for name, item in menu:

                if isinstance(item, SbsOnDemand.Feed.Feed):
                    # TODO add description from first, add
                    # quantity of items in folder
                    params={ 'name':feed.name,
                             'path':feed.path,
                             'query':json.dumps(feed.query),
                             'mode' : params["mode"],
                             'startIndex': startIndex,
                             'itemsPerPage': itemsPerPage,
                             }
                    addDir(params, folder=True, still=icon)

                elif isinstance(item, SbsOnDemand.Menu.Menu):
                    # TODO add description from first, add
                    # quantity of items in folder
                    params={ 'name':name,
                             'path':item.path,
                             'mode' : params["mode"],
                             'startIndex': startIndex,
                             'itemsPerPage': itemsPerPage,
                             }
                    addDir(params, folder=True, still=icon)

                elif isinstance(item, list):
                    params={ 'name':name + " (%d)"%len(item),
                             'path':path+'/'+name,
                             'mode' : params["mode"],
                             'startIndex': startIndex,
                             'itemsPerPage': itemsPerPage,
                             }
                    if isinstance(item[0], SbsOnDemand.Video.Video):
                        still = item[0].thumbnail
                        info = item[0].description
                    else:
                        still = icon
                        info = ""
                    addDir(params, folder=True, still=still, info=info)

                elif isinstance(item, SbsOnDemand.Video.Video):
                    video = item
                    url = video.getBrowserUrl()
                    webdriver = True

                    if url:
                        addDir(params={ 'name':video.title,
                                        # 'feedId':feed.feedId,
                                        'mode' : 'playVideo',
                                        'url' : url,
                                        'webdriver' : webdriver,
                                     },
                               folder=False,
                               info=video.description,
                               still=video.thumbnail
                               )
                else:
                    raise NotImplementedError

            if itemsPerPage == len(menu):
                new_params = params.copy()
                new_params.update({'startIndex': startIndex + len(menu),
                                   'itemsPerPage': itemsPerPage})
                addDir(params=new_params, folder=True)


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