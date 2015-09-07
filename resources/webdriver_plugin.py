
import os
import json
from webdriver import Browser, Keys, By, js_fn
from webdriver._utils import *
PLUGIN_NAME="sbs_ondemand"

jsTargetBy = By.ID
jsTarget = 'player'

import xbmcgui
SBS_KEYMAP = {
    xbmcgui.ACTION_SELECT_ITEM   : ("handle_key",js_fn.keynameToKeycode.space),
    xbmcgui.ACTION_MOVE_RIGHT    : ("handle_key",js_fn.keynameToKeycode.right),
    xbmcgui.ACTION_MOVE_LEFT     : ("handle_key",js_fn.keynameToKeycode.left),
    xbmcgui.ACTION_MOVE_UP       : ("skip_forward",None),
    xbmcgui.ACTION_MOVE_DOWN     : ("skip_back",None),
    xbmcgui.ACTION_VOLUME_UP     : ("handle_key",js_fn.keynameToKeycode.up),
    xbmcgui.ACTION_VOLUME_DOWN   : ("handle_key",js_fn.keynameToKeycode.down),
    xbmcgui.ACTION_PLAY          : ("handle_key",js_fn.keynameToKeycode.space),
    xbmcgui.ACTION_NAV_BACK      : ("exit",None),
    xbmcgui.ACTION_PARENT_DIR    : ("exit",None),
    xbmcgui.ACTION_PREVIOUS_MENU : ("exit",None),
    xbmcgui.ACTION_STOP          : ("exit",None),
    xbmcgui.ACTION_SHOW_INFO     : ("exit",None),
    xbmcgui.ACTION_SHOW_GUI      : ("exit",None),
}

class PLUGIN(object):

    SKIP_SECONDS = 4*60

    def __init__(self, chrome):
        assert isinstance(chrome, Browser)
        self.chrome = chrome

    def action_handle_key(self, keyCode):
        js_key = str(keyCode)
        ret = self.chrome.execute_script('event = {"keyCode":%s,"preventDefault":function(){}}; window.embeddedPlayer.plugins.sbsmisc.handleKeyboardInput(event);return "done";' % str(js_key) )
        # log("keyCode:%d , res: %s"%(keyCode, str(ret)))

    def action_skip_forward(self, *_):
        # sbs keyboard controls don't include larger skips, so go straight to js
        # http://resources.sbs.com.au/vod/sbs/js/embeddedPlayer.plugin-sbsmisc.js
        ret = self.chrome.execute_script('window.embeddedPlayer.plugins.sbsmisc.keyboardSeek(%d);return "done";'%self.SKIP_SECONDS*1000)
        log("forward res: %s"%(str(ret)))

    def action_skip_back(self, *_):
        ret = self.chrome.execute_script('window.embeddedPlayer.plugins.sbsmisc.keyboardSeek(-%d);return "done";'%self.SKIP_SECONDS*1000)
        log("back res: %s"%(str(ret)))
