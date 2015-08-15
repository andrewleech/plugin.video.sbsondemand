import  os
import  urllib2
import  re
import orderedjson
from    time import strftime, gmtime
from    time import localtime, strftime, gmtime
from    BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString

TEST=True

def geturl(url):
    #, headers = {"Accept-Encoding":"gzip"}
    print "getting: %s" % url
    if TEST:
        endpoint = url.split('/')[-1].split('?')[0]
        with open(os.path.join(os.path.dirname(__file__), 'testdata', endpoint), 'r') as testdata:
            return  testdata.read()
    else:
        return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def jsonc(st):
    for i,o in (
        ('true', 'True'),
        ('false', 'False')
    ):
        st = st.replace(i,o)
    return eval(st)

class MenuItems(object):
    def __init__(self):
        import orderedjson

        # self.base               = 'http://www.sbs.com.au/ondemand/'
        # self.raw_txt            = geturl(self.base + 'js/video-menu')
        # self.main_txt           = re.sub(r'^[^=]+=','', self.raw_txt)
        # #self.main_txt           = re.sub(r'\\([^\\])', r'\1', self.main_txt).replace(r'\\\\', r'\\')
        #
        # self.main               = orderedjson.loads(self.main_txt)
        #
        # #self.main               = ordered_load(self.main_txt, yaml.SafeLoader) #jsonc(self.main_txt)
        # if 0:
        #     import pprint
        #     pprint.pprint(self.main)
        # self.cache              = orderedjson.ordereddict.OrderedDict()
        # self.cache[tuple([])]   = {"url"        : None, "children" : self.__menu([], self.main.values())}


    def __menu(self, parent, items):
        out = []
        if isinstance(items, dict):
            items = items.values()

        for item in items:
            if "name" in item:
                name        = tuple(list(parent) + [item["name"]])
                children    = item.get("children", [])
                if "url" in item:
                    url         = "http://www.sbs.com.au%s" % (re.sub(r'%([0-9,A-F,a-f]{2})', lambda m : chr(int(m.group(1),16)), item["url"].replace("\\", "")))

                    if children:
                        self.cache[name]                = {"url"    :  None, "children" :   self.__menu(name, children)}
                        alli                            = tuple(list(name) + ["All Items"])
                        self.cache[alli]                = {"url"    : url, "children" : []}
                        self.cache[name]["children"]    = [alli] + self.cache[name]["children"]
                    else:
                        self.cache[name]                = {"url"    :  url, "children" : []}

                    out.append(name)
                else:
                    print ("!!", item)

        return out


    def menu_main(self, *args):
        if not len(args):
            args = [[]]

        return self.cache[tuple(args[0])]


# class MenuItems(object):
#     def __init__(self):
#
#         # http://whirlpool.net.au/wiki/sbs_downloader
#         # http://feed.theplatform.com/f/dYtmxB/section-programs?form=json
#         # http://feed.theplatform.com/f/dYtmxB/section-sbstv?form=json&byCategories=Documentary%2CSection%2FPrograms
#
#         # self.base               = 'http://www.sbs.com.au/ondemand/'
#         # self.raw_txt            = geturl(self.base + 'js/video-menu')
#         # self.main_txt           = re.sub(r'^[^=]+=','', self.raw_txt)
#         # #self.main_txt           = re.sub(r'\\([^\\])', r'\1', self.main_txt).replace(r'\\\\', r'\\')
#
#         #self.base              = "http://feed.theplatform.com/f/dYtmxB/{ident}?form=json"
#         self.IDENT_PROGRAMS    =  "section-programs",       # contains all programs' videos
#         self.IDENT_CLIPS       =  "section-clips",          # contains all clips
#         self.IDENT_EVENTS      =  "section-events",         # contains all events' videos
#         self.IDENT_LAST_CHANCE =  "videos-lastchance",      # contains last chance videos
#         self.IDENT_FEATURED    =  "featured-programs-prod", # contains featured programs
#         self.IDENT_FEAT_CLIPS  =  "featured-clips",         # contains featured clips
#         self.IDENT_FULL        =  "e16qKzBBHt4R",           # Full Eps and Clips combined
#         self.IDENT_SBSTV       =  "section-sbstv",          #
#
#         # Programs
#         # http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-featured-programs-prod?form=json&count=true&sort=pubDate%7Casc&range=1-20&byCategories=!Film
#         # http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-sbstv/?form=json&count=true&sort=pubDate%7Cdesc&range=1-35&byCategories=Section%2FPrograms,Drama%7CComedy%7CDocumentary%7CArts%7CFood%7CEntertainment%7CNews%20and%20Current%20Affairs&byCustomValue={useType}{Full%20Episode}
#         # http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-programs/?form=json&byPubDate=1436254200000~1436275800000&sort=pubDate%7Cdesc&range=1-35
#         # http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-programs/?form=json&count=true&sort=pubDate%7Cdesc&range=1-18&byCustomValue={programName}{Rectify}
#
#         #self.main               = ordered_load(self.main_txt, yaml.SafeLoader) #jsonc(self.main_txt)
#         # self.cache              = orderedjson.ordereddict.OrderedDict()
#         # self.cache[tuple([])]   = {"url"        : None, "children" : self._menu([], self.main.values())}
#
#
#     def _menu(self, parent, items):
#         out = []
#         if isinstance(items, dict):
#             items = items.values()
#
#         for item in items:
#             if "name" in item:
#                 name        = tuple(list(parent) + [item["name"]])
#                 children    = item.get("children", [])
#                 if "url" in item:
#                     url         = "http://www.sbs.com.au%s" % (re.sub(r'%([0-9,A-F,a-f]{2})', lambda m : chr(int(m.group(1),16)), item["url"].replace("\\", "")))
#
#                     if children:
#                         self.cache[name]                = {"url"    :  None, "children" :   self._menu(name, children)}
#                         alli                            = tuple(list(name) + ["All Items"])
#                         self.cache[alli]                = {"url"    : url, "children" : []}
#                         self.cache[name]["children"]    = [alli] + self.cache[name]["children"]
#                     else:
#                         self.cache[name]                = {"url"    :  url, "children" : []}
#
#                     out.append(name)
#                 else:
#                     print ("!!", item)
#
#         return out
#
#
#     def menu_main(self, *args):
#         if not len(args):
#             args = [[]]
#
#         # self.base              = "http://www.sbs.com.au/api/video_feed/f/Bgtm9B/?form=json"
#         # self.raw_txt            = geturl(self.base)
#         # self.main_txt           = re.sub(r'^[^=]+=','', self.raw_txt)
#         # #self.main_txt           = re.sub(r'\\([^\\])', r'\1', self.main_txt).replace(r'\\\\', r'\\')
#         #
#         # self.main         = orderedjson.loads(self.main_txt)#.format(ident=self.IDENT_PROGRAMS))
#
#
#         node = orderedjson.OrderedDict()
#
#         if not args[0]: # Initial menu
#             main_node = orderedjson.OrderedDict()
#             main_node[('Programs',)] = 'sbs-featured-programs-prod'
#             main_node[('Movies',)]   = 'movies'
#             main_node[('Channels',)] = 'channels'
#             main_node[('News',)]     = 'news'
#             main_node[('Sport',)]    = 'sport'
#             node["children"] = main_node
#         else:
#             node.update(self.cache[tuple(args[0])])
#         return node


    def menu_shows(self, st):
        print st
        res = geturl(st)

        if '"status":"failed"' in res:
            st = st.rsplit('&',1)[0]
            print st
            res = geturl(st)

        jsres = jsonc(res)
        print "%%menu_shows", res

#       for entry in sorted(jsres["entries"], key = lambda x: x["title"]):
        for entry in jsres["entries"]:
            hours, remainder = divmod(int(entry["media$content"][0]['plfile$duration']), 3600)
            minutes, seconds = divmod(remainder, 60)
            #entry["description"], entry['plmedia$defaultThumbnailUrl']

            rec  =  {
                "title"         : entry["title"],
                "thumbnail"     : entry["media$thumbnails"][0]["plfile$downloadUrl"].replace("\\", ""),
                "url"           : 'http://www.sbs.com.au/ondemand/video/%s' % entry["id"].split('/')[-1],
                "info"          : {
                    "Country "  : entry.get("pl1$countryOfOrigin", "?"),
                    "plot"      : entry["description"],
                    "duration"  : "%s" % ((hours * 60) + minutes),
                    "date"      : strftime("%d.%m.%Y",gmtime(entry["pubDate"]/1000)),
                    "genre"     : "%s,%s" % (entry.get("pl1$countryOfOrigin", "?"), entry["media$keywords"]),
                }
            }
            try:
                rec["info"]["mpaa"]     = entry["media$ratings"][0]['rating']
            except Exception,e:
                rec["info"]["mpaa"]     = '?'
            yield rec

    def menu_play(self, lk):
        print lk
        contents = geturl(lk)

        out = {}
        fmt = None
        for mtch in re.findall(r"^[ \t]+standard: '(.*)'", contents, re.MULTILINE):
            contents2 =  geturl(mtch.split("?")[0])
            #print contents2
            soup = BeautifulSoup(contents2)

            if contents2.find('GeoLocationBlocked') > -1:
                out['GeoLocationBlocked'] = None
                fmt = None

            elif contents2.find('.flv') > -1:
                fmt = '.flv'
                for item in soup.findAll('video'):
                    out[int(item["system-bitrate"])] = item["src"]
            else:
                fmt = '.mp4'
                vals = {}
                if str(soup).find('akamaihd') <= -1:
                    for item in soup.findAll('video'):
                        out[int(item["system-bitrate"])] = item["src"]
                else:
                    for item in soup.findAll('video'):
                        try:
                            splts = item["src"].split("/manifest.f4m")[0].rsplit("/", 1)
                            hd = splts[:-1]
                            tl, rate = splts[-1].rsplit("K.",1)[0].rsplit("_", 1)
                            hd = "/".join(hd)
                            if (hd,tl) not in vals:
                                vals[hd,tl] = set([])
                            vals[hd,tl].add(rate)
                        except (ValueError, IndexError):
                            pass

                    for (hd,tl),rts in vals.iteritems():
                        for idx, rt in enumerate(sorted(rts, key = lambda x: int(x))):
                            out[int(rt) * 1000] = "%s/%s_,%s,K.mp4.csmil/bitrate=%s?v=2.5.14&fp=WIN%%%%2011,1,102,55&r=HJHYK&g=SOENISYOINXG&seek=0" % (hd,tl, ",".join(sorted(rts, key = lambda e: int(e))), idx)

        return out, fmt

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
