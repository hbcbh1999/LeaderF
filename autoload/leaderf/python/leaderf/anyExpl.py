#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from .utils import *
from .explorer import *
from .manager import *


#*****************************************************
# AnyExplorer
#*****************************************************
class AnyExplorer(Explorer):
    def __init__(self):
        pass

    def setConfig(self, category, config):
        self._category, self._config = category, config

    def getContent(self, *args, **kwargs):
        pass

    def getStlCategory(self):
        return self._category

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
        return True

"""
let g:Lf_Extensions = {
    \ apple: {
    \       source: [], "grep -r '%s' *", funcref,
    \       accept: funcref,
    \       preview: funcref,
    \       supports_name_only: 0,
    \       get_digest: funcref,
    \       before_enter: funcref,
    \       after_enter: funcref,
    \       before_exit: funcref,
    \       after_exit: funcref,
    \       highlights_def: {
    \               "Lf_hl_bufNumber": "^\s*\zs\d\+",
    \               "Lf_hl_buf": "^\s*\zs\d\+",
    \       }
    \       highlights_cmd: {
    \               "hi Lf_hl_bufNumber guifg=red",
    \               "hi Lf_hl_buf guifg=green",
    \       }
    \       supports_multi: 0,
    \       supports_refine: 0,
    \ },
    \ orange: {}
\}
"""
#*****************************************************
# AnyExplManager
#*****************************************************
class AnyExplManager(Manager):
    def __init__(self, category, config):
        super(AnyExplManager, self).__init__()
        self._getExplorer().setConfig(category, config)
        self._config = extension[1]
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
            return ''
        prefix_len = self._getExplorer().getPrefixLength()
        if mode == 0:
            return line[prefix_len:]
        elif mode == 1:
            buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
            basename = getBasename(vim.buffers[buf_number].name)
            return basename if basename else "[No Name]"
        else:
            start_pos = line.find(' "')
            return line[start_pos+2 : -1]

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
        prefix_len = self._getExplorer().getPrefixLength()
        if mode == 0:
            return prefix_len
        elif mode == 1:
            return prefix_len
        else:
            buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
            basename = getBasename(vim.buffers[buf_number].name)
            space_num = self._getExplorer().getMaxBufnameLen() \
                        - int(lfEval("strdisplaywidth('%s')" % escQuote(basename)))
            return prefix_len + lfBytesLen(basename) + space_num + 2

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

    def _afterEnter(self):
        super(AnyExplManager, self)._afterEnter()
        id = int(lfEval("matchadd('Lf_hl_bufNumber', '^\s*\zs\d\+')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufIndicators', '^\s*\d\+\s*\zsu\=\s*[#%]\=...')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufModified', '^\s*\d\+\s*u\=\s*[#%]\=.+\s*\zs.*$')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufNomodifiable', '^\s*\d\+\s*u\=\s*[#%]\=..-\s*\zs.*$')"))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_bufDirname', ' \zs".*"$')'''))
        self._match_ids.append(id)

    def _beforeExit(self):
        super(AnyExplManager, self)._beforeExit()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []


class AnyHub(object):
    def __init__(self):
        self._extensions = lfEval("g:Lf_Extensions")
        self._managers = {}

    def start(self, category, *args, **kwargs):
        if category not in self._managers:
            self._managers[category] = AnyExplManager(category, self._extensions[category])

#*****************************************************
# anyHub is a singleton
#*****************************************************
anyHub = AnyHub()

__all__ = ['anyHub']
