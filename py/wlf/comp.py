# -*- coding=UTF-8 -*-
"""Comp footages adn create output, can be run as script.  """

import json
import locale
import os
import pprint
import re
import sys
import threading
import time
import traceback
import string
from subprocess import PIPE, Popen

import nuke
import nukescripts

from wlf.files import url_open

__version__ = '0.14.3'

OS_ENCODING = locale.getdefaultlocale()[1]
SCRIPT_CODEC = 'UTF-8'


class Config(dict):
    """Comp config.  """

    default = {
        'footage_pat': r'^.+_sc.+_.+\..+$',
        'dir_pat': r'^.{8,}$',
        'tag_pat': r'sc.+?_([^.]+)',
        'output_dir': 'E:/precomp',
        'input_dir': 'Z:/SNJYW/Render/EP',
        'mp': r"Z:\QQFC2017\Comp\mp\Panorama202_v2.jpg",
        'autograde': True,
        'exclude_existed': True,
    }
    path = os.path.expanduser(u'~/.nuke/wlf.comp.config.json')
    instance = None

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


def escape_batch(text):
    """Return escaped text for windows shell.

    >>> escape_batch('test_text "^%~1"')
    u'test_text \\\\"^^%~1\\\\"'
    >>> escape_batch(u'中文 \"^%1\"')
    u'\\xe4\\xb8\\xad\\xe6\\x96\\x87 \\\\"^^%1\\\\"'
    """

    return text.replace(u'"', r'\"').replace(u'^', r'^^')


class Comp(object):
    """Create .nk file from footage that taged in filename."""

    default_config = {
        'footage_pat': r'^.*_?sc.+_.+\.exr[0-9\- ]*$',
        'dir_pat': r'^.{8,}$',
        'tag_pat': r'sc.+?_([^.]+)',
        'output_dir': 'E:/precomp',
        'input_dir': 'Z:/SNJYW/Render/EP',
        'mp': r"Z:\QQFC2017\Comp\mp\Panorama202_v1.jpg",
        'autograde': False,
        'exclude_existed': True,
    }
    default_tag = '_OTHER'
    tag_knob_name = u'wlf_tag'

    def __init__(self, config=None):
        print(u'\n吾立方批量合成 {}\n'.format(__version__))
        with open(os.path.join(__file__, '../comp.tags.json')) as f:
            tags = json.load(f)
            self._regular_tags = tags['regular_tags']
            self._tag_convert_dict = tags['tag_convert_dict']
            del tags
        self._config = config or self.default_config
        self._config = dict(self._config)
        self._errors = []

        for key, value in self._config.iteritems():
            if isinstance(value, str):
                self._config[key] = value.replace(u'\\', '/')

        pprint.pprint(config)

        if config:
            print(u'\n# {}'.format(config['shot']))
            nuke.scriptClear()
            self.import_resource()
        if not nuke.value('root.project_directory'):
            nuke.knob("root.project_directory",
                      r"[python {os.path.join("
                      r"nuke.value('root.name', ''), '../'"
                      r").replace('\\', '/')}]")
        self.setup_nodes()
        self.create_nodes()
        if config:
            self.output()
        print(u'{:-^50s}\n'.format(u'全部结束'))

    @staticmethod
    def get_shot_list(config, include_existed=False):
        """Return shot_list generator from a config dict."""

        _dir = config['input_dir']
        if not os.path.isdir(_dir):
            return

        _ret = os.listdir(_dir)
        if isinstance(_ret[0], str):
            _ret = (unicode(i, OS_ENCODING) for i in _ret)
        if config['exclude_existed'] and not include_existed:
            _ret = (i for i in _ret if not os.path.exists(os.path.join(
                config[u'output_dir'], u'{}.nk'.format(i))))
        _ret = (i for i in _ret if (
            re.match(config['dir_pat'], i) and os.path.isdir(os.path.join(_dir, i))))

        if not _ret:
            _dir = _dir.rstrip('\\/')
            _dirname = os.path.basename(_dir)
            if re.match(config['dir_pat'], _dir):
                _ret = [_dir]
        return sorted(_ret)

    @staticmethod
    def show_dialog():
        """Show a dialog for user using this class."""

        CompDialog().showModalDialog()

    def import_resource(self):
        """Import footages from config dictionary."""

        # Get all subdir
        dirs = list(x[0] for x in os.walk(self._config['footage_dir']))
        print(u'{:-^30s}'.format(u'开始 导入素材'))
        for dir_ in dirs:
            # Get footage in subdir
            print(u'文件夹 {}:'.format(dir_))
            if not re.match(self._config['dir_pat'], os.path.basename(dir_.rstrip('\\/'))):
                print(u'\t不匹配文件夹正则, 跳过\n')
                continue

            _footages = [i for i in nuke.getFileNameList(dir_) if
                         not i.endswith(('副本', '.lock'))]
            if _footages:
                for f in _footages:
                    if os.path.isdir(os.path.join(dir_, f)):
                        print(u'\t文件夹: {}'.format(f))
                        continue
                    print(u'\t素材: {}'.format(f))
                    if re.match(self._config['footage_pat'], f, flags=re.I):
                        nuke.createNode(
                            u'Read', 'file {{{}/{}}}'.format(dir_, f))
                    else:
                        print(u'\t\t不匹配素材正则, 跳过\n')
            print('')
        print(u'{:-^30s}'.format(u'结束 导入素材'))

        if not nuke.allNodes(u'Read'):
            raise FootageError(self._config['footage_dir'], u'没有素材')

    def setup_nodes(self):
        """Add tag knob to read nodes, then set project framerange."""

        _nodes = nuke.allNodes(u'Read')
        if not _nodes:
            raise FootageError(u'没有读取节点')

        n = None
        root_format = None
        for n in _nodes:
            self._setup_node(n)
            if n.format().name() == 'HD_1080':
                root_format = 'HD_1080'
        if n:
            if not root_format:
                root_format = n.format()
            nuke.Root()['first_frame'].setValue(n['first'].value())
            nuke.Root()['last_frame'].setValue(n['last'].value())
            nuke.Root()['lock_range'].setValue(True)
            nuke.Root()['format'].setValue(root_format)

    def create_nodes(self):
        """Create nodes that a comp need."""

        n = self._bg_ch_nodes()
        print(u'{:-^30s}'.format('BG CH 节点创建'))

        nodes = nuke.allNodes(
            'DepthFix') or self.get_nodes_by_tags(['BG', 'CH'])
        n = self._merge_depth(n, nodes)

        print(u'{:-^30s}'.format(u'整体深度节点创建'))
        self._add_zdefocus_control(n)
        print(u'{:-^30s}'.format(u'添加虚焦控制'))
        # self._add_depthfog_control(n)
        # print(u'{:-^30s}'.format(u'添加深度雾控制'))
        n = self._merge_mp(
            n, mp_file=self._config['mp'], lut=self._config.get('mp_lut'))
        print(u'{:-^30s}'.format(u'MP节点创建'))

        n = nuke.nodes.HighPassSharpen(inputs=[n], mode='highpass only')
        n = nuke.nodes.Merge2(
            inputs=[n.input(0), n], operation='soft-light', mix='0.2')

        n = nuke.nodes.Aberration(inputs=[n], distortion1='0 0 0.003')

        n = nuke.nodes.wlf_Write(inputs=[n])
        n.setName(u'_Write')
        print(u'{:-^30s}'.format(u'输出节点创建'))
        _read_jpg = nuke.nodes.Read(
            file='[value _Write.Write_JPG_1.file]',
            label='输出的单帧',
            disable='{{! [file exist [value this.file]]}}',
            tile_color=0xbfbf00ff,
        )
        _read_jpg.setName('Read_Write_JPG')
        print(u'{:-^30s}'.format(u'读取输出节点创建'))

        map(nuke.delete, nuke.allNodes('Viewer'))
        nuke.nodes.Viewer(inputs=[n, n.input(0), n, _read_jpg])
        print(u'{:-^30s}'.format(u'设置查看器'))

        autoplace_all()

    @staticmethod
    def _merge_mp(input_node, mp_file='', lut=''):
        def _add_lut(input_node):
            if not lut:
                return input_node

            n = nuke.nodes.Vectorfield(
                inputs=[input_node],
                file_type='vf',
                label='[basename [value this.knob.vfield_file]]')
            n['vfield_file'].fromUserText(lut)
            return n

        n = nuke.nodes.Read(file=mp_file)
        n['file'].fromUserText(mp_file)
        n.setName(u'MP')

        n = nuke.nodes.Reformat(inputs=[n], resize='fill')
        n = nuke.nodes.Transform(inputs=[n])
        n = _add_lut(n)
        n = nuke.nodes.ColorCorrect(inputs=[n])
        n = nuke.nodes.Grade(
            inputs=[n, nuke.nodes.Ramp(p0='1700 1000', p1='1700 500')])
        n = nuke.nodes.ProjectionMP(inputs=[n])
        n = nuke.nodes.SoftClip(
            inputs=[n], conversion='logarithmic compress')
        n = nuke.nodes.Defocus(inputs=[n], disable=True)
        n = nuke.nodes.Crop(inputs=[n], box='0 0 root.width root.height')
        n = nuke.nodes.Merge2(
            inputs=[input_node, n], operation='under', bbox='B', label='MP')

        return n

    @staticmethod
    def _colorcorrect_with_positionkeyer(input_node, cc_label=None, **pk_kwargs):
        n = nuke.nodes.PositionKeyer(inputs=[input_node], **pk_kwargs)
        n = nuke.nodes.ColorCorrect(inputs=[input_node, n], label=cc_label)
        return n

    @classmethod
    def get_nodes_by_tags(cls, tags):
        """Return nodes that match given tags."""

        ret = []
        if isinstance(tags, (str, unicode)):
            tags = [tags]
        tags = tuple(unicode(i).upper() for i in tags)

        for n in nuke.allNodes(u'Read'):
            knob_name = u'{}.{}'.format(n.name(), cls.tag_knob_name)
            if nuke.value(knob_name.encode(SCRIPT_CODEC), '').startswith(tags):
                ret.append(n)

        def _nodes_order(n):
            return (
                u'_' + n[cls.tag_knob_name].value()).replace(u'_BG', '1_').replace(u'_CH', '0_')
        ret.sort(key=_nodes_order, reverse=True)
        return ret

    def output(self):
        """Save .nk file and render .jpg file."""

        print(u'{:-^30s}'.format(u'开始 输出'))
        _path = self._config['save_path'].replace('\\', '/').lower()
        _dir = os.path.dirname(_path)
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        # Save nk
        print(u'保存为:\n\t\t\t{}\n'.format(_path))
        nuke.Root()['name'].setValue(_path)
        nuke.scriptSave(_path)

        # Render png
        for n in nuke.allNodes('Read'):
            name = n.name()
            if name in ('MP', 'Read_Write_JPG'):
                continue
            for frame in (n.firstFrame(), n.lastFrame(), int(nuke.numvalue(u'_Write.knob.frame'))):
                try:
                    render_png(n, frame)
                    break
                except RuntimeError:
                    continue

        # Render Single Frame
        n = nuke.toNode(u'_Write')
        if n:
            n = n.node(u'Write_JPG_1')
            n['disable'].setValue(False)
            for frame in (int(nuke.numvalue(u'_Write.knob.frame')), n.firstFrame(), n.lastFrame()):
                try:
                    nuke.execute(n, frame, frame)
                    break
                except RuntimeError:
                    continue
            else:
                self._errors.append(
                    u'{}:\t渲染出错'.format(os.path.basename(_path)))
                raise RenderError(u'渲染出错: Write_JPG_1')
            print(u'{:-^30s}'.format(u'结束 输出'))

    def _setup_node(self, n):
        def _add_knob(k):
            _knob_name = k.name()
            if nuke.exists('{}.{}'.format(n.name(), k.name())):
                k.setValue(n[_knob_name].value())
                n.removeKnob(n[_knob_name])
            n.addKnob(k)
        _tag = nuke.value(u'{}.{}'.format(
            n.name(), self.tag_knob_name), '') or self._get_tag(nuke.filename(n))

        if not 'rgba.alpha' in n.channels():
            _tag = '_OTHER'

        k = nuke.String_Knob(self.tag_knob_name, '素材标签')
        _add_knob(k)
        k.setValue(_tag)

        if _tag.startswith(tuple(string.digits)):
            _tag = '_{}'.format(_tag)
        n.setName(_tag, updateExpressions=True)

    def _get_tag_from_pattern(self, str_):
        _tag_pat = re.compile(self.default_config['tag_pat'], flags=re.I)
        _ret = re.search(_tag_pat, str_)
        if _ret:
            _ret = _ret.group(1).upper()
        else:
            _ret = self.default_tag
        return _ret

    def _get_tag(self, filename):
        _ret = self._get_tag_from_pattern(os.path.basename(filename))

        if _ret not in self._regular_tags:
            _dir_result = self._get_tag_from_pattern(
                os.path.basename(os.path.dirname(filename)))
            if _dir_result != self.default_tag:
                _ret = _dir_result

        if _ret in self._tag_convert_dict:
            _ret = self._tag_convert_dict[_ret]

        return _ret

    def _bg_ch_nodes(self):
        nodes = self.get_nodes_by_tags(['BG', 'CH'])

        if not nodes:
            raise FootageError(u'BG', u'CH')

        for i, n in enumerate(nodes):
            read_node = n
            n = self._bg_ch_node(n)

            if i == 0:
                n = self._merge_occ(n)
                n = self._merge_shadow(n)
                n = self._merge_screen(n)
            if i > 0:
                n = nuke.nodes.Merge2(
                    inputs=[nodes[i - 1], n],
                    label=read_node[self.tag_knob_name].value()
                )
            nodes[i] = n
        return n

    def _bg_ch_node(self, input_node):
        n = input_node
        if 'MotionVectors' in nuke.layers(input_node):
            n = nuke.nodes.MotionFix(
                inputs=[n], channel='MotionVectors', output='motion')
        if 'SSS.alpha' in input_node.channels():
            n = nuke.nodes.Keyer(
                inputs=[n],
                input='SSS',
                output='SSS.alpha',
                operation='luminance key',
                range='0 0.007297795507 1 1'
            )
        if 'depth.Z' not in input_node.channels():
            _constant = nuke.nodes.Constant(
                channels='depth',
                color=1,
                label='**用渲染出的depth层替换这个**\n或者手动指定数值'
            )
            n = nuke.nodes.Merge2(
                inputs=[n, _constant],
                also_merge='all',
                label='add_depth'
            )
        n = nuke.nodes.Reformat(inputs=[n], resize='fit')

        n = nuke.nodes.DepthFix(inputs=[n])
        if self._config['autograde']:
            if get_max(input_node, 'depth.Z') > 1.1:
                n['farpoint'].setValue(10000)

        n = nuke.nodes.Grade(
            inputs=[n],
            unpremult='rgba.alpha',
            label='白点: [value this.whitepoint]\n混合:[value this.mix]\n使亮度范围靠近0-1'
        )
        if self._config['autograde']:
            print(u'{:-^30s}'.format(u'开始 自动亮度'))
            _max = self._autograde_get_max(input_node)
            n['whitepoint'].setValue(_max)
            n['mix'].setValue(0.3 if _max < 0.5 else 0.6)
            print(u'{:-^30s}'.format(u'结束 自动亮度'))
        n = nuke.nodes.Unpremult(inputs=[n])
        n = nuke.nodes.ColorCorrect(inputs=[n], label='亮度调整')
        n = nuke.nodes.ColorCorrect(
            inputs=[n], mix_luminance=1, label='颜色调整')
        if 'SSS.alpha' in input_node.channels():
            n = nuke.nodes.ColorCorrect(
                inputs=[n],
                maskChannelInput='SSS.alpha',
                label='SSS调整'
            )
        n = nuke.nodes.HueCorrect(inputs=[n])

        # n = self._depthfog(n)
        _kwargs = {'in': 'depth'}
        n = self._colorcorrect_with_positionkeyer(n, '远处', **_kwargs)
        n = self._colorcorrect_with_positionkeyer(n, '近处', **_kwargs)
        n = nuke.nodes.Premult(inputs=[n])

        n = nuke.nodes.SoftClip(
            inputs=[n], conversion='logarithmic compress')
        n = nuke.nodes.Crop(
            inputs=[n], box='0 0 {} {}'.format(n.width(), n.height()), crop=False)
        n = nuke.nodes.ZDefocus2(
            inputs=[n],
            math='depth',
            center='{{[value _ZDefocus.center curve]}}',
            focal_point='1.#INF 1.#INF',
            dof='{{[value _ZDefocus.dof curve]}}',
            blur_dof='{{[value _ZDefocus.blur_dof curve]}}',
            size='{{[value _ZDefocus.size curve]}}',
            max_size='{{[value _ZDefocus.max_size curve]}}',
            label='[\nset trg parent._ZDefocus\n'
            'knob this.math [value $trg.math depth]\n'
            'knob this.z_channel [value $trg.z_channel depth.Z]\n'
            'if {[exists _ZDefocus]} '
            '{return \"由_ZDefocus控制\"} '
            'else '
            '{return \"需要_ZDefocus节点\"}\n]',
            disable='{{![exists _ZDefocus] '
            '|| [if {[value _ZDefocus.focal_point \"200 200\"] == \"200 200\" '
            '|| [value _ZDefocus.disable]} {return True} else {return False}]}}'
        )
        if 'motion' in nuke.layers(n):
            n = nuke.nodes.VectorBlur2(
                inputs=[n], uv='motion', scale=1, soft_lines=True, normalize=True, disable=True)
        n = nuke.nodes.Crop(
            inputs=[n],
            box='0 0 root.width root.height')
        return n

    @staticmethod
    def _autograde_get_max(n):
        # Exclude small highlight
        ret = 100
        erode = 0
        n = nuke.nodes.Dilate(inputs=[n])
        while ret > 1 and erode > n.height() / -100.0:
            n['size'].setValue(erode)
            print(u'收边 {}'.format(erode))
            ret = get_max(n, 'rgb')
            erode -= 1
        nuke.delete(n)

        return ret

    @staticmethod
    def _merge_depth(input_node, nodes):
        if len(nodes) < 2:
            return input_node

        merge_node = nuke.nodes.Merge2(
            inputs=nodes[:2] + [None] + nodes[2:],
            tile_color=2184871423L,
            operation='min',
            Achannels='depth', Bchannels='depth', output='depth',
            label='Depth',
            hide_input=True)
        copy_node = nuke.nodes.Copy(
            inputs=[input_node, merge_node], from0='depth.Z', to0='depth.Z')
        return copy_node

    @staticmethod
    def _depthfog(input_node):
        _group = nuke.nodes.Group(
            inputs=[input_node],
            tile_color=0x2386eaff,
            label="深度雾\n由_DepthFogControl控制",
            disable='{{![exists _DepthFogControl] || _DepthFogControl.disable}}',
        )
        _group.setName(u'DepthFog1')

        _group.begin()
        _input_node = nuke.nodes.Input(name='Input')
        n = nuke.nodes.DepthKeyer(
            inputs=[_input_node],
            disable='{{![exists _DepthFogControl] || _DepthFogControl.disable}}',
        )
        n['range'].setExpression(
            u'([exists _DepthFogControl.range]) ? _DepthFogControl.range : curve')
        n = nuke.nodes.Grade(
            inputs=[_input_node, n],
            black='{{([exists _DepthFogControl.fog_color]) ? _DepthFogControl.fog_color : curve}}',
            unpremult='rgba.alpha',
            mix='{{([exists _DepthFogControl.fog_mix]) ? _DepthFogControl.fog_mix : curve}}',
            disable='{{![exists _DepthFogControl] || _DepthFogControl.disable}}',
        )
        n = nuke.nodes.Output(inputs=[n])
        _group.end()

        return _group

    @staticmethod
    def _merge_occ(input_node):
        _nodes = Comp.get_nodes_by_tags(u'OC')
        n = input_node
        for _read_node in _nodes:
            _reformat_node = nuke.nodes.Reformat(
                inputs=[_read_node], resize='fit')
            n = nuke.nodes.Merge2(
                inputs=[n, _reformat_node],
                operation='multiply',
                screen_alpha=True,
                label='OCC'
            )
        return n

    @staticmethod
    def _merge_shadow(input_node):
        _nodes = Comp.get_nodes_by_tags(['SH', 'SD'])
        n = input_node
        for _read_node in _nodes:
            _reformat_node = nuke.nodes.Reformat(
                inputs=[_read_node], resize='fit')
            n = nuke.nodes.Grade(
                inputs=[n, _reformat_node],
                white="0.08420000225 0.1441999972 0.2041999996 0.0700000003",
                white_panelDropped=True,
                label='Shadow'
            )
        return n

    @staticmethod
    def _merge_screen(input_node):
        _nodes = Comp.get_nodes_by_tags(u'FOG')
        n = input_node
        for _read_node in _nodes:
            _reformat_node = nuke.nodes.Reformat(
                inputs=[_read_node], resize='fit')
            n = nuke.nodes.Merge2(
                inputs=[n, _reformat_node],
                operation='screen',
                maskChannelInput='rgba.alpha',
                label=_read_node[Comp.tag_knob_name].value(),
            )
        return n

    @staticmethod
    def _add_zdefocus_control(input_node):
        # Use for one-node zdefocus control
        n = nuke.nodes.ZDefocus2(inputs=[input_node], math='depth', output='focal plane setup',
                                 center=0.00234567, blur_dof=False, label='** 虚焦总控制 **\n在此拖点定虚焦及设置')
        n.setName(u'_ZDefocus')
        return n

    @staticmethod
    def _add_depthfog_control(input_node):
        node_color = 596044543
        n = nuke.nodes.DepthKeyer(
            label='**深度雾总控制**\n在此设置深度雾范围及颜色',
            range='1 1 1 1',
            gl_color=node_color,
            tile_color=node_color,
        )

        n.setName(u'_DepthFogControl')
        # n = n.makeGroup()

        k = nuke.Text_Knob('颜色控制')
        n.addKnob(k)

        k = nuke.Color_Knob('fog_color', '雾颜色')
        k.setValue((0.009, 0.025133, 0.045))
        n.addKnob(k)

        k = nuke.Double_Knob('fog_mix', 'mix')
        k.setValue(1)
        n.addKnob(k)

        n.setInput(0, input_node)
        return n


if not nuke.GUI:
    nukescripts.PythonPanel = object


def render_png(nodes, frame=None, show=False):
    """create png for given @nodes."""
    assert isinstance(nodes, (nuke.Node, list, tuple))
    assert nuke.value('root.project_directory'), u'未设置工程目录'
    if isinstance(nodes, nuke.Node):
        nodes = (nodes,)
    script_name = os.path.join(os.path.splitext(
        os.path.basename(nuke.value('root.name')))[0])
    for read_node in nodes:
        if read_node.hasError() or read_node['disable'].value():
            continue
        name = read_node.name()
        print(u'渲染: {}'.format(name))
        n = nuke.nodes.Write(
            inputs=[read_node], channels='rgba')
        n['file'].fromUserText(os.path.join(
            script_name, '{}.png'.format(name)))
        if not frame:
            frame = nuke.frame()
        nuke.execute(n, frame, frame)

        nuke.delete(n)
    if show:
        url_open(
            'file://{}/{}'.format(nuke.value('root.project_directory'), script_name))


class CompDialog(nukescripts.PythonPanel):
    """Dialog UI of class Comp."""

    knob_list = [
        (nuke.Tab_Knob, 'general_setting', '常用设置'),
        (nuke.File_Knob, 'input_dir', '输入文件夹'),
        (nuke.File_Knob, 'output_dir', '输出文件夹'),
        (nuke.File_Knob, 'mp', '指定MP'),
        (nuke.File_Knob, 'mp_lut', 'MP LUT'),
        (nuke.Boolean_Knob, 'exclude_existed', '排除已输出镜头'),
        (nuke.Boolean_Knob, 'autograde', '自动亮度'),
        (nuke.Tab_Knob, 'filter', '正则过滤'),
        (nuke.String_Knob, 'footage_pat', '素材名'),
        (nuke.String_Knob, 'dir_pat', '路径'),
        (nuke.String_Knob, 'tag_pat', '标签'),
        (nuke.EndTabGroup_Knob, 'end_tab', ''),
        (nuke.Multiline_Eval_String_Knob, 'info', ''),
    ]
    config_file = os.path.expanduser(u'~/.nuke/wlf.comp.config.json')

    def __init__(self):
        nukescripts.PythonPanel.__init__(self, '吾立方批量合成', 'com.wlf.multicomp')
        self.config = Comp.default_config
        self._shot_list = None
        self.read_config()

        for i in self.knob_list:
            k = i[0](i[1], i[2])
            try:
                k.setValue(self.config.get(i[1]))
            except TypeError:
                pass
            self.addKnob(k)
        self.knobs()['exclude_existed'].setFlag(nuke.STARTLINE)
        # self.update()

    def read_config(self):
        """Read config from disk."""

        if os.path.isfile(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config.update(json.load(f))
        else:
            self.write_config()

    def write_config(self):
        """Write config to disk."""

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def knobChanged(self, knob):
        """Overrride for buttons."""

        if knob is self.knobs()['OK']:
            threading.Thread(target=self.progress).start()
        elif knob is self.knobs()['info']:
            self.update()
        else:
            self.config[knob.name()] = knob.value()
            self.update()

    def progress(self):
        """Start process all shots with a processbar."""

        task = nuke.ProgressTask('批量合成')
        shot_info = dict.fromkeys(Comp.get_shot_list(
            self.config, include_existed=True), '本次未处理')

        for i, shot in enumerate(self._shot_list):
            if task.isCancelled():
                break
            task.setMessage(shot)
            task.setProgress(i * 100 // len(self._shot_list))
            self.config['shot'] = os.path.basename(shot)
            self.config['save_path'] = os.path.join(
                self.config['output_dir'], '{}.nk'.format(self.config['shot']))
            self.config['footage_dir'] = shot if os.path.isdir(
                shot) else os.path.join(self.config['input_dir'], self.config['shot'])
            self.write_config()
            _cmd = u'"{nuke}" -t {script} "{config}"'.format(
                nuke=nuke.EXE_PATH,
                script=os.path.normcase(__file__).rstrip(u'c'),
                config=escape_batch(json.dumps(self.config))
            ).encode(OS_ENCODING)
            proc = Popen(_cmd, shell=True, stderr=PIPE)
            stderr = proc.communicate()[1]
            if stderr:
                shot_info[shot] = stderr
            elif proc.returncode:
                shot_info[shot] = '非正常退出码:{}'.format(proc.returncode)
            else:
                shot_info[shot] = '正常退出'

        infos = ''
        for shot in sorted(shot_info.keys()):
            infos += u'<tr>'\
                u'<td><img src="images/{0}.jpg" height="200" alt="<无图像>"></img></td>\n'\
                u'<td>{0}</td>\n<td>{1}</td></tr>\n'.format(
                    shot, shot_info[shot])
        infos = u'<head>\n<meta charset="UTF-8">\n<style>td{{padding:8px;}}</style>\n</head>\n'\
            u'<table><tr><th>图像</th><th>镜头</th><th>信息</th></tr>\n'\
            u'{}</table>'.format(infos)
        log_path = os.path.join(self.config['output_dir'], u'批量合成日志.html')
        with open(log_path, 'w') as f:
            f.write(infos.encode('UTF-8'))
        # nuke.executeInMainThread(nuke.message, args=(errors,))
        url_open(u'file://{}'.format(log_path))
        url_open(
            u'file://{}'.format(self.config['output_dir'].encode(SCRIPT_CODEC)))

    def update(self):
        """Update ui info and button enabled."""

        def _info():
            _info = u'测试'
            self._shot_list = list(Comp.get_shot_list(self.config))
            if self._shot_list:
                _info = u'# 共{}个镜头\n'.format(len(self._shot_list))
                _info += u'\n'.join(self._shot_list)
            else:
                _info = u'找不到镜头'
            self.knobs()['info'].setValue(_info.encode(SCRIPT_CODEC))

        def _button_enabled():
            _knobs = [
                'output_dir',
                'mp',
                'exclude_existed',
                'autograde',
                'info',
                'OK',
            ]

            _isdir = os.path.isdir(self.config['input_dir'])
            if _isdir:
                for k in ['exclude_existed', 'info']:
                    self.knobs()[k].setEnabled(True)
                if self._shot_list:
                    for k in _knobs:
                        self.knobs()[k].setEnabled(True)
                else:
                    for k in set(_knobs) - set(['exclude_existed']):
                        self.knobs()[k].setEnabled(False)
            else:
                for k in _knobs:
                    self.knobs()[k].setEnabled(False)

        _info()
        _button_enabled()


class FootageError(Exception):
    """Indicate not found needed footage."""

    def __init__(self, *args):
        super(FootageError, self).__init__()
        self.tags = args

    def __str__(self):
        return u' # '.join(self.tags)


class RenderError(Exception):
    """Indicate some problem caused when rendering."""

    def __init__(self, *args):
        super(RenderError, self).__init__()
        self.tags = args

    def __str__(self):
        return u' # '.join(self.tags)


def insert_node(node, input_node):
    """Insert @node after @input_node."""

    for n in nuke.allNodes():
        for i in range(n.inputs()):
            if n.input(i) == input_node:
                n.setInput(i, node)

    node.setInput(0, input_node)


def get_max(node, channel='rgb'):
    '''
    Return themax values of a given node's image at middle frame

    @parm n: node
    @parm channel: channel for sample
    '''
    first = node.firstFrame()
    last = node.lastFrame()
    middle = (first + last) // 2
    ret = 0

    n = nuke.nodes.Invert(channels=channel, inputs=[node])
    n = nuke.nodes.MinColor(
        channels=channel, target=0, inputs=[n])

    for frame in (middle, first, last):
        try:
            nuke.execute(n, frame, frame)
        except RuntimeError:
            continue
        ret = max(ret, n['pixeldelta'].value() + 1)
        if ret > 0.7:
            break

    print(u'getMax({1}, {0}) -> {2}'.format(channel, node.name(), ret))

    nuke.delete(n.input(0))
    nuke.delete(n)

    return ret


def autoplace_all():
    """Place all nodes position so them won't overlap."""

    for n in nuke.allNodes():
        nuke.autoplace(n)


def main():
    """Run this moudule as a script."""

    reload(sys)
    sys.setdefaultencoding('UTF-8')
    try:
        Comp(json.loads(sys.argv[1]))
    except FootageError as ex:
        print(u'** FootageError: {}\n\n'.format(ex).encode(OS_ENCODING))
        traceback.print_exc()


def pause():
    """Pause prompt with a countdown."""

    print(u'')
    for i in range(5)[::-1]:
        sys.stdout.write(u'\r{:2d}'.format(i + 1))
        time.sleep(1)
    sys.stdout.write(u'\r          ')
    print(u'')


if __name__ == '__main__':
    main()
