#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from .utils import *
from .explorer import *
from .manager import *
from .asyncExecutor import AsyncExecutor


#*****************************************************
# AnyExplorer
#*****************************************************
class AnyExplorer(Explorer):
    def __init__(self):
        self._executor = []

    def setConfig(self, category, config):
        self._category, self._config = category, config

    def getContent(self, *args, **kwargs):
        source = self._config.get("source")
        if isinstance(source, vim.List):
            return list(lfEncode(lfBytes2Str(line)) for line in source)
        elif isinstance(source, vim.Function):
            return list(lfBytes2Str(line) for line in list(source()))
        elif type(source) == type(b"string"): # "grep -r '%s' *"
            executor = AsyncExecutor()
            self._executor.append(executor)
            result = executor.execute(lfBytes2Str(source))
            return result
        else:
            return None

    def getStlCategory(self):
        return self._category

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
        return bool(self._config.get("supports_name_only", False))

    def supportsMulti(self):
        return bool(self._config.get("supports_multi", False))

"""
let g:Lf_Extensions = {
    \ "apple": {
    \       "source": [], "grep -r '%s' *", funcref,
    \       "accept": funcref,
    \       "preview": funcref,
    \       "supports_name_only": 0,
    \       "get_digest": funcref,
    \       "before_enter": funcref,
    \       "after_enter": funcref,
    \       "before_exit": funcref,
    \       "after_exit": funcref,
    \       "highlights_def": {
    \               "Lf_hl_apple": "^\s*\zs\d\+",
    \               "Lf_hl_appleId": "\d\+$",
    \       }
    \       "highlights_cmd": [
    \               "hi Lf_hl_apple guifg=red",
    \               "hi Lf_hl_appleId guifg=green",
    \       ],
    \       "supports_multi": 0,
    \       "supports_refine": 0,
    \ },
    \ "orange": {}
\}
"""
#*****************************************************
# AnyExplManager
#*****************************************************
class AnyExplManager(Manager):
    def __init__(self, category, config):
        super(AnyExplManager, self).__init__()
        self._getExplorer().setConfig(category, config)
        self._config = config
        self._match_ids = []

    def _getExplClass(self):
        return AnyExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Any#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
        lfCmd("hide buffer %d" % buf_number)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if not line:
            return ""
        if "get_digest" in self._config:
            return self._config["get_digest"][0](line, mode)
        else:
            return super(AnyExplManager, self)._getDigest(line, mode)

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if not line:
            return 0
        if "get_digest" in self._config:
            return self._config["get_digest"][1](line, mode)
        else:
            return super(AnyExplManager, self)._getDigestStartPos(line, mode)

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" d : wipe out buffer under cursor')
        help.append('" D : delete buffer under cursor')
        help.append('" i : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _beforeEnter(self):
        super(AnyExplManager, self)._beforeEnter()
        if "before_enter" in self._config:
            self._config["before_enter"]()

    def _afterEnter(self):
        super(AnyExplManager, self)._afterEnter()
        if "after_enter" in self._config:
            self._config["after_enter"]()

        highlights_cmd = self._config.get("highlights_cmd", [])
        for cmd in highlights_cmd:
            lfCmd(cmd)
        highlights_def = self._config.get("highlights_def", {})
        for group, pattern in highlights_def.items():
            id = int(lfEval("matchadd('%s', '%s')" %
                        (lfBytes2Str(group), escQuote(lfBytes2Str(pattern)))))
            self._match_ids.append(id)

    def _beforeExit(self):
        super(AnyExplManager, self)._beforeExit()
        if "before_exit" in self._config:
            self._config["before_exit"]()

        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []

    def _afterExit(self):
        super(AnyExplManager, self)._afterExit()
        if "after_exit" in self._config:
            self._config["after_exit"]()

    def _supportsRefine(self):
        return bool(self._config.get("supports_refine", False))


class AnyHub(object):
    def __init__(self):
        self._extensions = vim.bindeval("g:Lf_Extensions")
        self._managers = {}

    def start(self, category, *args, **kwargs):
        if category not in self._managers:
            self._managers[category] = AnyExplManager(category, self._extensions[category])
        self._managers[category].startExplorer("bottom", *args, **kwargs)

#*****************************************************
# anyHub is a singleton
#*****************************************************
anyHub = AnyHub()

__all__ = ['anyHub']
