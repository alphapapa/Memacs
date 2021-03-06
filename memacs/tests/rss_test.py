# -*- coding: utf-8 -*-
# Time-stamp: <2011-10-28 15:13:31 aw>

import unittest
import os
from memacs.rss import RssMemacs


class TestRss(unittest.TestCase):

    def setUp(self):
        self.test_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data', 'sample-rss.txt'
        )
        self.argv = "-s -f " + self.test_file

    def test_false_appending(self):
        try:
            memacs = RssMemacs(argv=self.argv.split())
            memacs.test_get_entries()
        except Exception:
            pass

    def test_all(self):
        memacs = RssMemacs(argv=self.argv.split())
        data = memacs.test_get_entries()

        self.assertEqual(
            data[0],
            (
                "** <2009-09-06 Sun 16:45> "
                "[[http://www.wikipedia.org/][Example entry]]"
            )
        )
        self.assertEqual(
            data[1],
            "   Here is some text containing an interesting description."
        )
        self.assertEqual(
            data[3],
            "   :GUID:       unique string per item")
        self.assertEqual(
            data[4],
            '   :PUBLISHED:  Mon, 06 Sep 2009 16:45:00 +0000'
        )
        self.assertEqual(
            data[5],
            "   :ID:         a0df7d405a7e9822fdd86af04e162663f1dccf11"
        )

        self.assertEqual(data[2], "   :PROPERTIES:")
        self.assertEqual(data[6], "   :END:")
