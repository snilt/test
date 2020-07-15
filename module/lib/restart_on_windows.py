#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
from sys import exit
from time import sleep
from traceback import print_exc

def hasNotExited(pid):
    """ copied from Core.isAlreadyRunning() """
    ret = 0
    import ctypes
    import ctypes.wintypes

    TH32CS_SNAPPROCESS = 2
    INVALID_HANDLE_VALUE = -1

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [('dwSize', ctypes.wintypes.DWORD),
                    ('cntUsage', ctypes.wintypes.DWORD),
                    ('th32ProcessID', ctypes.wintypes.DWORD),
                    ('th32DefaultHeapID', ctypes.wintypes.LPVOID),
                    ('th32ModuleID', ctypes.wintypes.DWORD),
                    ('cntThreads', ctypes.wintypes.DWORD),
                    ('th32ParentProcessID', ctypes.wintypes.DWORD),
                    ('pcPriClassBase', ctypes.wintypes.LONG),
                    ('dwFlags', ctypes.wintypes.DWORD),
                    ('szExeFile', ctypes.c_char * 260)]

    kernel32 = ctypes.windll.kernel32

    processInfo = PROCESSENTRY32()
    processInfo.dwSize = ctypes.sizeof(PROCESSENTRY32)
    hProcessSnapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS , 0)
    if hProcessSnapshot != INVALID_HANDLE_VALUE:
        found = False
        status = kernel32.Process32First(hProcessSnapshot , ctypes.pointer(processInfo))
        while status:
            if processInfo.th32ProcessID == pid:
                found = True
                break
            status = kernel32.Process32Next(hProcessSnapshot, ctypes.pointer(processInfo))

        kernel32.CloseHandle(hProcessSnapshot)
        if found and processInfo.szExeFile.decode().lower() in ("python.exe", "pythonw.exe", "pyloadcore.exe"):
            ret = pid

    else:
        print "Unhandled error in CreateToolhelp32Snapshot: %s" % kernel32.GetLastError()

    return ret

def main():
    pid = int(sys.argv[1])
    for i in range(60):
        if hasNotExited(pid):
            sleep(0.5)

        else:
            if getattr(sys, "frozen", False):   # py2exe
                args = ["cmd.exe", "/c", "start"]
            else:
                args = ["cmd.exe", "/c", "start", sys.executable]
            args.extend(sys.argv[2:])

            try:
                subprocess.Popen(args, close_fds=True)
            except Exception:
                print_exc()
                # keep the terminal window open
                while True:
                    sleep(1)
            exit()

    print
    print "ERROR: Failed to restart pyLoad (timed out)"
    # keep the terminal window open
    while True:
        sleep(1)

if __name__=="__main__":
    main()

