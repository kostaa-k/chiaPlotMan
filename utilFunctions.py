import ctypes
import os
import platform

import psutil

def listAllDisks():
    for disk in psutil.disk_partitions():
        diskLetter = disk.mountpoint[0]
        print(diskLetter, get_free_space_gb(disk.mountpoint))

def getDiskMountPointFromLetter(diskLetter):
    for disk in psutil.disk_partitions():
        if(disk.mountpoint[0] == diskLetter):
            return disk.mountpoint

def get_free_space_gb(dirname):
    """Return folder/drive free space (in gigabytes)."""
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 /  1024 / 1024
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize / 1024 / 1024 /1024


def clearCommandLine():
    """Return folder/drive free space (in gigabytes)."""
    if platform.system() == 'Windows':
        os.system("cls")
    else:
        os.system("reset")