# -*- coding=UTF-8 -*-
"""CLI interface for comp package.  """

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import logging
import logging.config
import os
import sys

from comp import Comp, FootageError, RenderError
from comp.config import START_MESSAGE

__path__ = os.path.abspath(__file__).rstrip('c')

LOGGER = logging.getLogger('com.wlf.comp')


def main():
    """Run this moudule as a script."""

    parser = argparse.ArgumentParser(description='WuLiFang auto comper.')
    parser.add_argument('input_dir', help='Folder that contained footages')
    parser.add_argument('output', help='Script output path.')
    args = parser.parse_args()

    LOGGER.info(START_MESSAGE)
    logging.getLogger('com.wlf').setLevel(logging.WARNING)
    try:
        comp = Comp()
        comp.import_resource(args.input_dir)
        comp.create_nodes()
        comp.output(args.output)
    except FootageError as ex:
        LOGGER.error('没有素材: %s', ex)
    except RenderError as ex:
        LOGGER.error('渲染出错: %s', ex)
    except Exception:
        LOGGER.error('Unexpected exception during comp.', exc_info=True)
        raise


if __name__ == '__main__':
    main()
