import sys, os
import collections
import urllib
import re
import subprocess
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

from resources.BeautifulSoup import BeautifulStoneSoup,NavigableString
import resources.scraper


##############################################################
ID = 'plugin.video.sbs2' #os.path.basename(os.getcwd())
__XBMC_Revision__	= xbmc.getInfoLabel('System.BuildVersion')
__settings__		= xbmcaddon.Addon( id=ID)
__language__		= __settings__.getLocalizedString
__version__			= __settings__.getAddonInfo('version')
__cwd__				= __settings__.getAddonInfo('path')
__addonname__		= __settings__.getAddonInfo('name')
__addonid__			= __settings__.getAddonInfo('id')
##############################################################


def addDir(params, folder = False, info = {}, still="DefaultFolder.png"):
	name = params["name"]
	url =  sys.argv[0] + "?" + "&".join(["%s=%s" % (urllib.quote_plus(k),urllib.quote_plus(str(v)))    for k, v in params.items()])
	print "::", url,  params, info, "%%"
	liz=xbmcgui.ListItem(name, iconImage=still, thumbnailImage="")
	if info:
		liz.setInfo("video", info)
	if not folder:
		liz.addContextMenuItems( [("Record to disk", "XBMC.RunPlugin(%s?&%s)"   % (sys.argv[0], url.replace("mode=1", "mode=2") ))] )
		
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
		for path in sorted(node["children"]):
			addDir({"path" : path, "name" : path[-1], "url" : scraper.menu_main(path)["url"], "mode" : params["mode"]}, True)

	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )	   

	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(params):
	scraper = resources.scraper.SCRAPER
	addon	= xbmcaddon.Addon( id=ID )
	bitrate	= int(addon.getSetting( "vid_quality" ))
	obj,fmt		= scraper.menu_play(params["url"])
	diff, sbitrate, url = sorted([(abs(int(sbitrate) - int(bitrate)), sbitrate, play) for sbitrate, play in sorted(obj.iteritems())])[0]	
	print ("using:",diff, bitrate, sbitrate, url)
	item = xbmcgui.ListItem(params["name"])
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, item)

def record(params):		
	def rpt(c):
		if c not in set(" %*^&$#@!~:"):
			return c
		else:
			return "_"
	print params
	scraper = resources.scraper.SCRAPER
	addon	= xbmcaddon.Addon( id=ID )
	bitrate	= int(addon.getSetting( "vid_quality" ))
	obj,fmt		= scraper.menu_play(params["url"])
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
MODE_MAP	= {
	0	: lambda params:	INDEX(params),
	1	: lambda url:		play(url),
	2	: lambda params: 	record(params)
}


def parse_args(args):
	out = {}
	if args[2]:
		for item in (args[2].split("?")[-1].split("&")):
#			print item
			items = item.split("=")
			k,v = items[0], "=".join(items[1:])
			out[k] = urllib.unquote_plus(v)
		out["path"] = eval(out["path"])
	else:
		out["mode"]		= "0"
		out["path"]		= []
		out["url"]		= ""

	out["mode"] = int(out["mode"])
	return out


def main():
		
#	item = xbmcgui.ListItem("test")
#	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play("http://sbsauvod-f.akamaihd.net/SBS_Production/managed/2012/04/2221230187_,1500,1000,512,128,K.mp4.csmil/bitrate=0?v=2.5.14&fp=WIN%2011,1,102,55&r=HJHYK&g=SOENISYOINXG", item)
#	return
	params = parse_args(sys.argv)
	print "##", sys.argv, params
	MODE_MAP[params["mode"]](params)


main()
