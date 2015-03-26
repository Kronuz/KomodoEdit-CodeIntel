# -*- coding: utf-8 -*-
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
#
# The Original Code is ActiveState Software Inc code.
# Portions created by German M. Bravo (Kronuz) are Copyright (C) 2015.
#
# Contributor(s):
#   German M. Bravo (Kronuz)
#   ActiveState Software Inc
#
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
#
from __future__ import absolute_import, unicode_literals, print_function

import os
import sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

python_sitelib_path = os.path.normpath(__path__)
if python_sitelib_path not in sys.path:
    sys.path.insert(0, python_sitelib_path)

import socket
import logging

from codeintel2.oop import Driver


class DummyStream(object):
    def write(self, message):
        pass

    def flush(self):
        pass


def oop_driver(db_base_dir, connect=None, log_levels=[], log_file=None):
    if log_file:
        if log_file in ('stdout', 'stderr'):
            stream = getattr(sys, log_file)
        else:
            stream = open(log_file, 'w', 0)
        logging.basicConfig(stream=stream)
        # XXX marky horrible ugly hack
        sys.stderr = stream
        sys.stdout = stream
    else:
        logging.basicConfig(stream=DummyStream())

    logger = logging.getLogger('codeintel')
    logger.setLevel(logging.INFO)

    for log_level in log_levels:
        name, _, level = log_level.rpartition(':')
        try:
            level = int(level)
        except ValueError:
            level = getattr(logging, level.upper(), logging.ERROR)
        logging.getLogger(name).setLevel(level)

    log = logging.getLogger('codeintel.oop.executable')

    try:
        set_process_limits(log)
    except:
        log.exception("Failed to set process memory/CPU limits")
    try:
        set_idle_priority(log)
    except:
        log.exception("Failed to set process CPU priority")

    if connect:
        host, _, port = connect.partition(':')
        port = int(port)
        log.debug("connecting to: %s:%s", host, port)
        conn = socket.create_connection((host, port))
        fd_in = conn.makefile('rwb', 0)
        fd_out = fd_in
    else:
        # force unbuffered stdout
        fd_in = sys.stdin
        fd_out = os.fdopen(sys.stdout.fileno(), 'wb', 0)

    driver = Driver(db_base_dir=db_base_dir, fd_in=fd_in, fd_out=fd_out)
    try:
        driver.start()
    except KeyboardInterrupt:
        pass


def set_idle_priority(log):
    """Attempt to set the process priority to idle"""
    try:
        os.nice(5)
    except AttributeError:
        pass  # No os.nice on Windows
    if sys.platform.startswith('win'):
        import ctypes
        from ctypes import wintypes
        SetPriorityClass = ctypes.windll.kernel32.SetPriorityClass
        SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        SetPriorityClass.restype = wintypes.BOOL
        HANDLE_CURRENT_PROCESS = -1
        BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
        SetPriorityClass(HANDLE_CURRENT_PROCESS, BELOW_NORMAL_PRIORITY_CLASS)


def set_process_limits(log):
    import ctypes
    if sys.platform.startswith("win"):
        """Pre-allocate (but don't commit) a 1GB chunk of memory to prevent it
        from actually being used by codeintel; this acts as a limit on the
        amount of memory we can actually use.  It has no effects on performance
        (since we're only eating address space, not RAM/swap) but helps to
        prevent codeintel from blowing up the system.
        """
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        VirtualAlloc = kernel32.VirtualAlloc
        VirtualAlloc.argtypes = [wintypes.LPVOID, wintypes.ULONG, wintypes.DWORD, wintypes.DWORD]
        VirtualAlloc.restype = wintypes.LPVOID
        MEM_RESERVE = 0x00002000
        MEM_TOP_DOWN = 0x00100000
        PAGE_NOACCESS = 0x01
        # we can only eat about 1GB; trying for 2GB causes the allocation to
        # (harmlessly) fail, which doesn't accomplish our goals
        waste = VirtualAlloc(None, 1 << 30, MEM_RESERVE | MEM_TOP_DOWN, PAGE_NOACCESS)
        if waste:
            log.debug("Successfullly allocated: %r", waste)
        else:
            log.debug("Failed to reduce address space: %s",
                      ctypes.WinError(ctypes.get_last_error()).strerror)


def main():
    def get(i, default=None):
        try:
            return sys.argv[i]
        except IndexError:
            return default
    db_base_dir = get(1, os.path.expanduser("~/.codeintel"))
    connect = get(2)
    log_levels = get(3, '').split(',')
    log_file = get(4, 'stderr')
    oop_driver(
        db_base_dir,
        connect,
        log_levels,
        log_file,
    )


if __name__ == '__main__':
    main()
