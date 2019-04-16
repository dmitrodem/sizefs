#!/usr/bin/env python

#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#

import sys, os, stat, errno
# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__, probably it's too old.")

fuse.fuse_python_api = (0, 2)

import gzip, json

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class SizeFS(Fuse):

    def __init__(self, db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db

    @staticmethod
    def lookup_path(db, path):
        if (path == ['']) or (path == []):
            return db
        return SizeFS.lookup_path(db[path[0]], path[1:])

    def getattr(self, path):
        st = MyStat()
        if path == os.path.sep:
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
            return st

        path = path.split(os.path.sep)[1:]

        try:
            content = SizeFS.lookup_path(self.db, path)
        except KeyError:
            return -errno.ENOENT

        if isinstance(content, float):
            # 1 GB (1e9 B) = 1 mm^2
            st.st_size = round(content*1000)
            st.st_mode = stat.S_IFREG | 0o644
            st.st_nlink = 1
            return st
        elif isinstance(content, dict):
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 1
            return st

        return -errno.ENOENT

    def readdir(self, path, offset):
        path = path.split(os.path.sep)[1:]
        for r in SizeFS.lookup_path(self.db, path).keys():
            yield fuse.Direntry(r)


def main():
    with gzip.open(sys.argv[1], "r") as fd:
        data = json.load(fd)
    usage="""
Size-only filesystem

""" + Fuse.fusage
    server = SizeFS(data,
                     version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
