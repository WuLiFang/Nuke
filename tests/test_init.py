# -*- coding=UTF-8 -*-
"""Nuke initiate test.  """
from __future__ import absolute_import, unicode_literals, print_function
from unittest import TestCase, main


class NukeTestCase(TestCase):
    def test_init(self):
        before = dict(globals())
        import nuke

        print(nuke.env)
        after = dict(globals())
        for i in after:
            if i in ("__doc__", "__file__"):
                continue
            if i in before:
                self.assertIs(
                    after[i],
                    before[i],
                    (
                        "Initiate not clean: `{}` changed from\n`{}`\nto\n`{}`".format(
                            i, before[i], after[i]
                        )
                    ),
                )


if __name__ == "__main__":
    _ = main()
