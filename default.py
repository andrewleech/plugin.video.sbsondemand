import sys, os
import urllib
import subprocess
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

trace_on = False
# try:
#     from pycharm_debug import pydevd
#     pydevd.set_pm_excepthook()
#     pydevd.settrace('alelec.local', port=51380, stdoutToServer=True, stderrToServer=True)
#     trace_on = True
# except BaseException as ex:
#     pass

import resources.scraper


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

def addDir(params, folder = False, info = {}, still="DefaultFolder.png"):
    name = params["name"]
    url =  sys.argv[0] + "?" + "&".join(["%s=%s" % (urllib.quote_plus(k),urllib.quote_plus(str(v)))    for k, v in params.items()])
    print "::", url,  params, info, "%%"
    liz=xbmcgui.ListItem(name, iconImage=still, thumbnailImage="")
    if info:
        liz.setInfo("video", info)
    if not folder:
        liz.addContextMenuItems( [
            ("Record to disk", "XBMC.RunPlugin(%s?&%s)"   % (sys.argv[0], url.replace("mode=1", "mode=2") )),
            ("Play at Seek", "XBMC.RunPlugin(%s?&%s)"   % (sys.argv[0], url.replace("mode=1", "mode=3") ))
        ] )

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=folder)
    return ok

##############################################################
def INDEX(params):
    addon = xbmcaddon.Addon( id=ID)
    scraper = resources.scraper.SCRAPER

    node = scraper.menu_main(params["path"])

    if not node["children"]:
        for obj in scraper.menu_shows(node["url"]):
            addDir({"path" : params["path"], "name" : obj["title"], "url" : obj["url"], "mode" : params["mode"] + 1}, False, obj["info"], still = obj["thumbnail"])
    else:
#        for path in sorted(node["children"]):
        for path in (node["children"]):
            addDir({"path" : path, "name" : path[-1], "url" : scraper.menu_main(path)["url"], "mode" : params["mode"]}, True)

    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
    # Top two levels I want unsorted - ie the order comes from the website
    if len(params["path"]) > 1:
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def seekhack(player, url, item):
    addon   = xbmcaddon.Addon( id=ID )
    #if not xbmc.abortRequested:
    print ("***", bool(addon.getSetting( "seek_hack" )))

    if url.find("seek=") >= 0:
        flag, lastseek = url.split("&")[-1].split("=")
        lastseek = int(lastseek)
        if addon.getSetting( "seek_hack" ) == "true" and flag:
            import json
            import socket
            import select
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", 9090))

            while player.isPlaying():
                xbmc.sleep(1000)
                print "Sniffing for notifications..."

                if len(select.select([sock], [], [], 0)[0]) != 0:
                    notific_str = sock.recv(4096)
                    print ("??", notific_str)
                    notifs = ['{"jsonrpc"' + noti for noti in notific_str.split('{"jsonrpc"')]
                    for notific in notifs[1:]:
                        print ("??", notific)
                        notific = json.loads(notific)
                        if notific["method"] == "Player.OnSeek":
                            ctime = sum(
                                    int(notific["params"]["data"]["player"]["time"][k]) * mul
                                    for k, mul in ( ("hours", 3600 ), ("minutes", 60), ("seconds", 1))
                                )

                            seekoff = sum(
                                    int(notific["params"]["data"]["player"]["seekoffset"][k]) * mul
                                    for k, mul in ( ("hours", 3600 ), ("minutes", 60), ("seconds", 1))
                                )
                            curtime = player.getTime()
                            #UGLY hack because going backwards can take us beyond the current played item's start time, have to provide a good default (10min)
                            if ctime < 1:
                                seekoff = -600
                            lastseek =  (curtime + lastseek + seekoff)
                            if lastseek < 0:
                                lastseek = 0
                            print ("??", lastseek)
                            player.stop()
                            #item.setProperty("StartPercent",  "20")
                            #item.setInfo("video", {"Player.Time" :  str(seek), "VideoPlayer.Time" :  str(seek)})

                            player.play("&".join(url.split("&")[:-1]) + "&seek={0}".format(lastseek), item)
                            xbmc.sleep(int(addon.getSetting( "delay" )))
                            xbmc.executebuiltin("PlayerControl(Play)")

def play(params):
    scraper = resources.scraper.SCRAPER
    addon   = xbmcaddon.Addon( id=ID )
    bitrate = int(addon.getSetting( "vid_quality" ))
    obj,fmt     = scraper.menu_play(params["url"])
    if len(obj):
        if 'GeoLocationBlocked' in obj:
            xbmc.executebuiltin('XBMC.Notification(SBS:,'+str(translation(30705))+',5000,'+icon+')')
        else:
            diff, sbitrate, url = sorted([(abs(int(sbitrate) - int(bitrate)), sbitrate, pl) for sbitrate, pl in sorted(obj.iteritems())])[0]
            print ("using:",diff, bitrate, sbitrate, url)
            item = xbmcgui.ListItem(params["name"])

            player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
            player.play(url, item)

            xbmc.sleep(int(addon.getSetting( "delay" )))
            xbmc.executebuiltin("PlayerControl(Play)")
            seekhack(player, url, item)
    else:
        xbmc.executebuiltin('XBMC.Notification(SBS:,'+str(translation(30704))+',50000,'+icon+')')




def play_at_seek(params):
    offset = False
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        offset = int(keyboard.getText())


    if offset != False:
        scraper = resources.scraper.SCRAPER
        addon   = xbmcaddon.Addon( id=ID )
        bitrate = int(addon.getSetting( "vid_quality" ))
        obj,fmt     = scraper.menu_play(params["url"])
        diff, sbitrate, url = sorted([(abs(int(sbitrate) - int(bitrate)), sbitrate, pl) for sbitrate, pl in sorted(obj.iteritems())])[0]
        print ("using:",diff, bitrate, sbitrate, url, obj.iteritems)
        item = xbmcgui.ListItem(params["name"])

        player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
        player.play("&".join(url.split("&")[:-1]) + "&seek={0}".format(offset), item)

        xbmc.sleep(int(addon.getSetting( "delay" )))
        xbmc.executebuiltin("PlayerControl(Play)")
        seekhack(player, url, item)

def record(params):     
    def rpt(c):
        if c not in set(" %*^&$#@!~:"):
            return c
        else:
            return "_"
    print params
    scraper = resources.scraper.SCRAPER
    addon   = xbmcaddon.Addon( id=ID )
    bitrate = int(addon.getSetting( "vid_quality" ))
    obj,fmt     = scraper.menu_play(params["url"])
    diff, sbitrate, url = sorted([(abs(int(sbitrate) - int(bitrate)), sbitrate, play) for sbitrate, play in sorted(obj.iteritems())])[0]
    print ("using:",diff, bitrate, sbitrate, url)
    name= '%s%s%s' % (
            __settings__.getSetting( "path" ),
            "".join(rpt(c) for c in str(params["name"])),
            fmt
        )
    args = (
        __settings__.getSetting( "ffmpeg" ),
        '-i',  url,
        "-vcodec", "copy",
        "-acodec", "copy",
        name
    )
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    print " ".join(args)
    sout = open(name+".fmpeg.out", "w")
    serr = open(name+".ffmpeg.err", "w")
    try:
        xx = subprocess.call(args, stdin= subprocess.PIPE, stdout= sout, stderr= serr,shell= False, startupinfo=startupinfo)
    finally:
        sout.close()
        serr.close()
    #print xx.stdout.read()
    #print xx.stderr.read()

##############################################################
MODE_MAP    = {
    0   : lambda params:    INDEX(params),
    1   : lambda url:       play(url),
    2   : lambda params:    record(params),
    3   : lambda params:    play_at_seek(params)
}


def parse_args(args):
    out = {}
    if args[2]:
        for item in (args[2].split("?")[-1].split("&")):
#           print item
            items = item.split("=")
            k,v = items[0], "=".join(items[1:])
            out[k] = urllib.unquote_plus(v)
        out["path"] = eval(out["path"])
    else:
        out["mode"]     = "0"
        out["path"]     = []
        out["url"]      = ""

    out["mode"] = int(out["mode"])
    return out


def main():
#   item = xbmcgui.ListItem("test")
#   xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play("http://sbsauvod-f.akamaihd.net/SBS_Production/managed/2012/04/2221230187_,1500,1000,512,128,K.mp4.csmil/bitrate=0?v=2.5.14&fp=WIN%2011,1,102,55&r=HJHYK&g=SOENISYOINXG", item)
#   return
    params = parse_args(sys.argv)
    print "##", sys.argv, params
    MODE_MAP[params["mode"]](params)


main()
if trace_on:
    pydevd.stoptrace()