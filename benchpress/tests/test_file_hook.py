#!/usr/bin/env python3
# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import unittest
from unittest.mock import MagicMock

from pyfakefs import fake_filesystem, fake_filesystem_unittest

from benchpress.plugins.hooks import FileHook


class TestFileHook(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)
        self.hook = FileHook()

    def test_directory_pre(self):
        """A directory is created during the before phase"""
        # make sure the dir didn't exist before and then exists afterwards
        self.assertFalse(self.fs.exists("/fake/dir"))
        self.hook.before_job([{"path": "/fake/dir", "type": "dir"}], MagicMock())
        self.assertTrue(self.fs.isdir("/fake/dir"))

    def test_directory_pre_exists(self):
        """If a directory already exists, don't fail"""
        self.fs.create_dir("/fake/dir")
        self.hook.before_job([{"path": "/fake/dir", "type": "dir"}], MagicMock())
        self.assertTrue(self.fs.isdir("/fake/dir"))

    def test_directory_pre_no_permissions(self):
        """No permission to create a directory raises an error"""
        self.fs.create_dir("/fake")
        # make the /fake directory readonly
        self.os.chmod("/fake", 0o444)
        with self.assertRaises(OSError):
            self.hook.before_job([{"path": "/fake/dir", "type": "dir"}], MagicMock())

    def test_directory_post(self):
        """A directory is deleted during the after phase"""
        # make sure the dir existed before and then does not exist afterwards
        self.fs.create_dir("/fake/dir")
        self.hook.after_job([{"path": "/fake/dir", "type": "dir"}], MagicMock())
        self.assertFalse(self.fs.exists("/fake/dir"))

    def test_file_pre(self):
        """A file is created during the before phase"""
        # make sure the file didn't exist before and then exists afterwards
        self.fs.create_dir("/fake")
        self.assertFalse(self.fs.exists("/fake/file"))
        self.hook.before_job([{"path": "/fake/file", "type": "file"}], MagicMock())
        self.assertTrue(self.fs.isfile("/fake/file"))

    def test_file_post(self):
        """A file is deleted during the after phase"""
        # make sure the file existed before and then does not exist afterwards
        self.fs.create_dir("/fake")
        self.fs.create_file("/fake/file")
        self.hook.after_job([{"path": "/fake/file", "type": "file"}], MagicMock())
        self.assertFalse(self.fs.exists("/fake/file"))


if __name__ == "__main__":
    unittest.main()
