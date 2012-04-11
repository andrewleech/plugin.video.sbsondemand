import urllib, urllib2, httplib
import re
from  time import localtime
from BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString 


def geturl(url):
	return  urllib2.urlopen(urllib2.Request(url, headers = {"Accept-Encoding":"gzip"})).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def jsonc(st):
	for i,o in (
		('true', 'True'),
		('false', 'False')
	):
		st = st.replace(i,o)
	return eval(st)


class MenuItems(object):
	def __init__(self):
		self.base				= 'http://www.sbs.com.au/ondemand/'
		self.main_txt			= re.sub(r'^[^=]+=','', geturl(self.base + 'js/video-menu'))
		self.main				= jsonc(self.main_txt)
		self.cache				= {}
		self.cache[tuple([])]	= {"url"		: None, "children" : self.__menu([], self.main.values())}
		print self.main
		
	def __menu(self, parent, items):
		out = []
		for item in items:
			if "name" in item:
				name		= tuple(list(parent) + [item["name"]])
				children	= item.get("children", [])
				url			= "http://www.sbs.com.au{}".format(re.sub(r'%([0-9,A-F,a-f]{2})', lambda m : chr(int(m.group(1),16)), item["url"].replace("\\", "")))
				
				if children:
					self.cache[name]				= {"url"	:  None, "children" : 	self.__menu(name, children)}
					alli 							= tuple(list(name) + ["All Items"])
					self.cache[alli]				= {"url"	: url, "children" : []}
					self.cache[name]["children"]	= [alli] + self.cache[name]["children"]
				else:
					self.cache[name]				= {"url"	:  url, "children" : []}
				
				out.append(name)
			
		return out
		
		
	def menu_main(self, *args):
		key = 	tuple([] if not len(args) else args[0])
		return self.cache[key]

	
	def menu_shows(self, st):
		print st
		for entry in jsonc(geturl(st))["entries"]:
			hours, remainder = divmod(int(entry["media$content"][0]['plfile$duration']), 3600)
			minutes, seconds = divmod(remainder, 60)		
			#entry["description"], entry['plmedia$defaultThumbnailUrl']

			rec  =  {
				"title" 		: entry["title"],
				"description"	: entry["description"],
				"thumbnail"		: entry["plmedia$defaultThumbnailUrl"],
				"url"			: 'http://www.sbs.com.au/ondemand/video/%s' % entry["id"].split('/')[-1],
				"time"			: "%s:%s.%s" % (hours, minutes, seconds),
				"date_avail"	: localtime(entry["media$availableDate"]/1000),
				"date_expirey"	: localtime(entry["media$expirationDate"]/1000),
				"date_pub"		: localtime(entry["pubDate"]/1000),
			}
			yield rec
		
	def menu_play(self, lk):
		print lk
		contents = geturl(lk)
		out = {}
		for mtch in re.findall(r'^[ \t]+player.releaseUrl = "(.*)";', contents, re.MULTILINE):
			contents2 =  geturl(mtch)
			print contents2
			soup = BeautifulSoup(contents2)
			for item in soup.findAll('meta'):
				out["rtmp"] = item["base"]
			out["play"] = [] 
			for item in soup.findAll('video'):	
				out["play"].append((item["src"], item["system-bitrate"]))
		return out

	def menu_tree(self, node, out):
		for i in self.menu_main(node)["children"]:
			out.append(i)
			self.menu_tree(i, out)
		return out

if __name__ == "__main__":
	from  pprint import PrettyPrinter, pprint

	m = MenuItems()
	print "#" * 20	
	menues = []		
	m.menu_tree([], menues)
	PrettyPrinter(indent=1).pprint(menues)
	print "#" * 30
	leafs = [i for i in menues if not m.menu_main(i)["children"]]
	print "#" * 30
	shows = list(m.menu_shows(m.menu_main(leafs[30])["url"]))
	PrettyPrinter(indent=1).pprint(shows)
	print "#" * 30
	PrettyPrinter(indent=1).pprint(m.menu_play(shows[2]["url"]))
