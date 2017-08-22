# -*-coding=UTF-8-*-
"""Config file on disk.  """

import os
import json

__version__ = '0.1.4'


class Config(dict):
    """Comp config.  """
    default = {
        'footage_pat': r'^.+\.exr[0-9\- ]*$',
        'dir_pat': r'^.{4,}$',
        'tag_pat':
        r'(?i)(?:[^_]+_)?(?:ep\d+_)?(?:\d+[a-zA-Z]*_)?'
        r'(?:sc\d+[a-zA-Z]*_)?((?:[a-zA-Z][^\._]*_?){,2})',
        'output_dir': 'E:/precomp',
        'input_dir': 'Z:/SNJYW/Render/EP',
        'mp': r"Z:\QQFC2017\Comp\mp\Panorama202_v2.jpg",
        'autograde': False,
        'exclude_existed': True,
        'csheet_database': 'proj_big',
        'csheet_prefix': 'SNJYW_EP14_',
        'csheet_outdir': 'E:/',
        'csheet_checked': False,
    }
    path = os.path.expanduser(u'~/.nuke/wlf.config.json')
    instance = None
    with open(os.path.join(__file__, '../comp.tags.json')) as f:
        tags = json.load(f)
        regular_tags = tags['regular_tags']
        tag_convert_dict = tags['tag_convert_dict']
    del tags, f
    default_tag = u'_OTHER'

    def __new__(cls):
        if not cls.instance:
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super(Config, self).__init__()
        self.update(dict(self.default))
        self.read()

    def __str__(self):
        return json.dumps(self)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.write()

    def write(self):
        """Write config to disk.  """

        with open(self.path, 'w') as f:
            json.dump(self, f, indent=4, sort_keys=True)

    def read(self):
        """Read config from disk.  """

        if os.path.isfile(self.path):
            with open(self.path) as f:
                self.update(dict(json.load(f)))
