" ============================================================================
" File:        Any.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.anyExpl import *"

function! leaderf#Any#parseArguments(A, L, P)
    return ["aaa", "bbb"]
endfunction

function! leaderf#Any#start(bang, ...)
    if a:0 == 0

    else

    endif
endfunction

