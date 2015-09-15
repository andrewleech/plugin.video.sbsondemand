## @namespace SbsOnDemand::config
# Module for setting configuration variables and storing global constants such as urls

# User-specified constants

## Manual proxy specification (can be used for debugging)
#
# Set to None for default (system) proxy
#
# Should be a dict object, such as {'http': '127.0.0.1:8080'}
PROXY = None

# Constants - don't change
API_BASE = "http://www.sbs.com.au/api/video_feed"
#MENU_URI = "http://www.sbs.com.au/ondemand/js/video-menu" # It's gone now (2015/08/01)
LOGIN_URI = "http://my.sbs.com.au/go/login/onesiteSignIn"
LOGOUT_URI = "http://www.sbs.com.au/api/Member/logout"

SEARCH_PREFIX = "http://www.sbs.com.au/api/video_search/v2/"
SITENAV_URI = "http://www.sbs.com.au/ondemandcms/sitenav"

ONDEMAND_UI_BASE_URI = "http://www.sbs.com.au/ondemand/video/"
ONDEMAND_UI_FULLSCREEN_URI = "http://www.sbs.com.au/ondemand/video/single/"

RELEASE_URL_KEY = 'http://resources.sbs.com.au/vod/theplatform/core/current/swf/flvPlayer.swf?releaseUrl'
VALID_URL_SUFFIX = '.csmil/bitrate=0?v=2.9.4&fp=MAC%2011,5,502,136&r=XBQYK&g=FSCQTSPZYLLE'
ONDEMAND_UI_VIDEO_CSS_QUERY = 'meta[property="og:video"]'
#MPX_FEEDID = "dYtmxB"
MPX_FEEDID = "Bgtm9B"
# SEARCH_FEEDID = "search"
ALLDATA_FEEDID = "CxeOeDELXKEv"
SINGLE_FEED_PREFIX = 'http://feed.theplatform.com/f/Bgtm9B/sbs-section-programs/'

DEFAULT_FEEDS = [
    {"name": "Programs", "feedId": "section-programs"},
    {"name": "Clips", "feedId": "section-clips"},
    {"name": "Events", "feedId": "section-events"},
    {"name": "Last Chance", "feedId":"videos-lastchance"},
    {"name": "Featured Programs", "feedId":"featured-programs-prod"},
    {"name": "Documentary", "url": 'http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-sbstv?form=json&byCategories=Documentary|Factual|Factual%2FAnimation|Factual%2FArchaeology|Factual%2FBiography|Factual%2FBusiness+and+Economics|Factual%2FCulture+and+Society|Factual%2FDocu-drama|Factual%2FHealth+%2B+Science+and+Technology|Factual%2FHistory|Factual%2FLifestyle|Factual%2FPolitics+and+Current+Affairs|Factual%2FNature+and+Environment|Factual%2FSport|Factual%2FSexuality%2CSection%2FClips|Section%2FPrograms&count=true&defaultThumbnailAssetType=Thumbnail'},
    {"name": "Featured Clips", "feedId":"featured-clips"}
]

## Not sure how to use this one
# http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-xbox-search

MENU = [
    # TODO Featured comes up double menu

    ("Programs"  , { "menu": [
        ("Featured"     , { "feedId": 'sbs-featured-programs-prod', "query": {"byCategories": "!Film"}}), # "url": "http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-featured-programs-prod?form=json&count=true&sort=pubDate%7Casc&byCategories=!Film"}),
        ("Last Chance"  , { "feedId": 'sbs-video-lastchance', "query": {"byCategories": "Section/Programs,Drama|Comedy|Documentary|Arts|Entertainment|Food|Factual|Movies"}}), #"url": "http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-video-lastchance?form=json&count=true&byCategories=Section%2FPrograms,Drama%7CComedy%7CDocumentary%7CArts%7CEntertainment%7CFood%7CFactual%7CMovies&sort=expirationDate%7Casc"}),
        ("Genres"       , { "menu": [

            ("Arts",                         { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Arts"} }),
            ("Comedy",                       { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Comedy"} }),
            ("Culture & Society",            { "feedId": "sbs-section-sbstv",     "query" : {"byCategories" : "Factual/Culture and Society"} }),
            ("Documentary",                  { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Documentary"} }),
            ("Drama",                        { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Drama"} }),
            ("Entertainment",                { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Entertainment"} }),
            ("Food",                         { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Food"} }),
            ("Health, Science & Technology", { "feedId": "sbs-section-sbstv",     "query" : {"byCategories" : "Factual/Health + Science and Technology"} }),
            ("History",                      { "feedId": "sbs-section-sbstv",     "query" : {"byCategories" : "Factual/History"} }),
            ("Nature & Environment",         { "feedId": "sbs-section-sbstv",     "query" : {"byCategories" : "Factual/Nature and Environment"} }),
            ("News & Current Affairs",       { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "News and Current Affairs"} }),
        ]}),
    ]}),

    ("Movies"    , { "menu": [
        ("Featured"  , { "feedId": 'sbs-featured-programs-prod', "query": {"byCategories": "Film"}}), # "url": "http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-featured-programs-prod?form=json&count=true&sort=pubDate%7Casc&byCategories=Film"}),
        ("Collections" , { "sitenav": "Movies/groups/Collections"}),
        ("Genres" , { "menu": [
            ("Action",              { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Action Adventure"} }),
            ("Animation",           { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Animation"} }),
            ("Biography",           { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Biography"} }),
            ("Classic",             { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Classic"} }),
            ("Comedy",              { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Comedy"} }),
            ("Drama",               { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Drama"} }),
            ("Feature Documentary", { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Documentary Feature"} }),
            ("Fantasy",             { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Fantasy"} }),
            ("History",             { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/History"} }),
            ("Horror",              { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Horror"} }),
            ("Martial Arts",        { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Martial Arts"} }),
            ("Mystery & Crime",     { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Mystery Crime"} }),
            ("Romance",             { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Romance"} }),
            ("Romantic Comedy",     { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Romantic Comedy"} }),
            ("Science Fiction",     { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Science Fiction"} }),
            ("Thriller",            { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/Thriller"} }),
            ("War",                 { "feedId": "sbs-section-programs",  "query" : {"byCategories" : "Section/Programs,Film,Film/War"} }),
        ]}),
    ]}),

    # TODO fill out below

    ("Channels"  , { "menu": [
        ("SBS",                    { "url": "" }),
        ("SBS TWO",                { "url": "" }),
        ("NITV",                   { "url": "" }),
        ("World Movies",           { "url": "" }),
        ("On Demand Exclusives",   { "url": "" }),
    ]}),
    ("News"      , { "feedId": "sbs-section-sbstv", "query": {"byCategories": "News and Current Affairs"} }),
    ("Sport"     , { "feedId": "sbs-section-sbstv", "query": {"byCategories": "Sport"} }),
]