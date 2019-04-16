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
        for e in db:
            if e['cell'] == path[0]:
                return SizeFS.lookup_path(e['children'], path[1:])

    def getattr(self, path):
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
            return st

        path = path.split('/')[1:]
        db = SizeFS.lookup_path(self.db, path[:-1])
        for e in db:
            if e['cell'] == path[-1]:
                try:
                    st.st_size = int(float(e['area']))
                    st.st_mode = stat.S_IFREG | 0o644
                    st.st_nlink = 1
                except KeyError:
                    st.st_mode = stat.S_IFDIR | 0o755
                    st.st_nlink = 1
                return st

        return -errno.ENOENT

    def readdir(self, path, offset):
        path = path.split('/')[1:]
        dirs = [".", ".."] + [e['cell'] for e in SizeFS.lookup_path(self.db, path)]
        for r in dirs:
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
