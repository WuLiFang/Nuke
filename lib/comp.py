# -*- coding=UTF-8 -*-
"""Comp footages and create output, can be run as script.  """

import json
import logging
import os
import re
import sys
import webbrowser

import nuke
import nukescripts

import wlf.config
import wlf.mp_logging
from wlf.notify import Progress
from wlf.path import get_unicode

import precomp
from edit import get_max
from node import ReadNode
from orgnize import autoplace

__version__ = '0.18.10'

LOGGER = logging.getLogger('com.wlf.comp')
COMP_START_MESSAGE = '{:-^50s}'.format('COMP START')


def _set_logger():
    logger = logging.getLogger('com.wlf.comp')
    logger.propagate = False
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        '%(levelname)-6s[%(asctime)s]:%(name)s:%(threadName)s:%(message)s', '%H:%M:%S')
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)

    try:
        loglevel = int(os.getenv('WLF_LOGLEVEL', logging.INFO))
        logger.setLevel(loglevel)
    except TypeError:
        logger.warning('Can not recognize env:WLF_LOGLEVEL, expect a int')


if __name__ != '__main__':
    _set_logger()


class Config(wlf.config.Config):
    """Comp config.  """
    default = {
        'fps': 25,
        'footage_pat': r'^.+\.exr[0-9\- ]*$',
        'dir_pat': r'^.{4,}$',
        'tag_pat':
        r'(?i)(?:[^_]+_)?(?:ep\d+_)?(?:\d+[a-zA-Z]*_)?'
        r'(?:sc\d+[a-zA-Z]*_)?((?:[a-zA-Z][^\._]*_?){,2})',
        'output_dir': 'E:/precomp',
        'input_dir': 'Z:/SNJYW/Render/EP',
        'txt_name': '镜头备注',
        'mp': r"Z:\SNJYW\MP\EP14\MP_EP14_1.nk",
        'autograde': False,
        'exclude_existed': True,
    }
    path = os.path.expanduser(u'~/.nuke/wlf.comp.json')


CONFIG = Config()


class Comp(object):
    """Create .nk file from footage that taged in filename."""

    tag_metadata_key = 'comp/tag'
    _attenuation_radial = None

    def __init__(self, config=None):
        LOGGER.info(u'吾立方批量合成 %s', __version__)

        self._config = dict(config or Config())
        self._errors = []
        self._bg_ch_end_nodes = []

        for key, value in self._config.iteritems():
            if isinstance(value, str):
                self._config[key] = value.replace(u'\\', '/')

        self._task = Progress(u'自动合成', total=20)
        if config:
            LOGGER.info(u'# %s', config['shot'])
            nuke.scriptClear()
            self.import_resource()
        if not nuke.value('root.project_directory'):
            nuke.knob("root.project_directory",
                      r"[python {os.path.join("
                      r"nuke.value('root.name', ''), '../'"
                      r").replace('\\', '/')}]")
        self.task_step(u'分析读取节点')
        self.setup()
        self.task_step(u'创建节点树')
        self.create_nodes()
        if config:
            self.output()
        LOGGER.info(u'\n\n')

    @property
    def fps(self):
        """Frame per secondes.  """
        return self._config.get('fps') or nuke.numvalue('root.fps')

    def task_step(self, message=None):
        """Push task progress bar forward.  """
        if message:
            LOGGER.info(u'{:-^30s}'.format(message))
        self._task.step(message)

    @staticmethod
    def get_shot_list(config, include_existed=False):
        """Return shot_list generator from a config dict."""

        _dir = config['input_dir']
        _out_dir = config[u'output_dir']
        if not os.path.isdir(_dir):
            return

        _ret = os.listdir(_dir)
        if isinstance(_ret[0], str):
            _ret = (get_unicode(i) for i in _ret)
        if config['exclude_existed'] and not include_existed:
            _ret = (i for i in _ret
                    if not os.path.exists(os.path.join(_out_dir, u'{}_v0.nk'.format(i)))
                    and not os.path.exists(os.path.join(_out_dir, u'{}.nk'.format(i))))
        _ret = (i for i in _ret if (
            re.match(config['dir_pat'], i) and os.path.isdir(os.path.join(_dir, i))))

        if not _ret:
            _dir = _dir.rstrip('\\/')
            _dirname = os.path.basename(_dir)
            if re.match(config['dir_pat'], _dir):
                _ret = [_dir]
        return sorted(_ret)

    def import_resource(self):
        """Import footages from config dictionary."""

        # Get all subdir
        dirs = list(x[0] for x in os.walk(self._config['footage_dir']))
        self.task_step(u'导入素材')
        for dir_ in dirs:
            # Get footage in subdir
            LOGGER.info(u'文件夹 %s:', dir_)
            if not re.match(self._config['dir_pat'], os.path.basename(dir_.rstrip('\\/'))):
                LOGGER.info(u'\t不匹配文件夹正则, 跳过')
                continue

            _footages = [i for i in nuke.getFileNameList(dir_) if
                         not i.endswith(('副本', '.lock'))]
            if _footages:
                for f in _footages:
                    if os.path.isdir(os.path.join(dir_, f)):
                        LOGGER.info(u'\t文件夹: %s', f)
                        continue
                    LOGGER.info(u'\t素材: %s', f)
                    if re.match(self._config['footage_pat'], f, flags=re.I):
                        nuke.createNode(
                            u'Read', 'file {{{}/{}}}'.format(dir_, f))
                    else:
                        LOGGER.info(u'\t\t不匹配素材正则, 跳过')
        LOGGER.info(u'{:-^30s}'.format(u'结束 导入素材'))

        if not nuke.allNodes(u'Read'):
            raise FootageError(self._config['footage_dir'], u'没有素材')

    def setup(self):
        """Add tag knob to read nodes, then set project framerange."""

        nodes = nuke.allNodes(u'Read')
        if not nodes:
            raise FootageError(u'没有读取节点')

        n = None
        root_format = None
        root = nuke.Root()
        first = None
        last = None

        for n in nodes:
            ReadNode(n)
            if n.format().name() == 'HD_1080':
                root_format = 'HD_1080'
            n_first, n_last = n.firstFrame(), n.lastFrame()
            if first is None:
                first = n_first
                last = n_last
            elif n_first != n_last:
                first = min(last, n.firstFrame())
                last = max(last, n.lastFrame())

        root_format = root_format or n.format()

        root['first_frame'].setValue(first)
        root['last_frame'].setValue(last)
        nuke.frame((first + last) / 2)
        root['lock_range'].setValue(True)
        root['format'].setValue(root_format)
        root['fps'].setValue(self.fps)

    def _attenuation_adjust(self, input_node):
        n = input_node
        if self._attenuation_radial is None:
            radial_node = nuke.nodes.Radial(
                area='0 0 {} {}'.format(n.width(), n.height()))
            self._attenuation_radial = radial_node
        else:
            radial_node = nuke.nodes.Dot(
                inputs=[self._attenuation_radial], hide_input=True)

        n = nuke.nodes.Merge2(
            inputs=[n, radial_node],
            operation='soft-light',
            mix='0.618',
            label='衰减调整',
            disable=True)

        return n

    def create_nodes(self):
        """Create nodes that a comp need."""
        self.task_step(u'合并BG CH')
        n = self._bg_ch_nodes()

        self.task_step(u'合并其他层')
        n = self._merge_other(n, self._bg_ch_end_nodes)

        self.task_step(u'创建整体深度')
        nodes = nuke.allNodes('DepthFix')
        n = self._merge_depth(n, nodes)
        self.task_step(u'添加虚焦控制')
        self._add_zdefocus_control(n)

        n = nuke.nodes.Unpremult(inputs=[n], label='整体调色开始')

        # n = self._attenuation_adjust(n)

        n = nuke.nodes.Premult(inputs=[n], label='整体调色结束')

        n = nuke.nodes.Reformat(
            inputs=[n],
            resize='none',
            label='整体滤镜开始')

        n = nuke.nodes.SoftClip(
            inputs=[n], conversion='logarithmic compress')

        n = nuke.nodes.Glow2(inputs=[n],
                             tolerance=0.6,
                             saturation=0.5,
                             size=100,
                             mix=0.25,
                             disable=True)
        # n = nuke.nodes.HighPassSharpen(inputs=[n], mode='highpass only')
        # n = nuke.nodes.Merge2(
        #     inputs=[n.input(0), n], operation='soft-light', mix='0.2', label='略微锐化')
        if 'motion' in nuke.layers(n):
            n = nuke.nodes.VectorBlur2(
                inputs=[n], uv='motion', scale=1, soft_lines=True, normalize=False, disable=True)
        n = nuke.nodes.Aberration(
            inputs=[n], distortion1='0 0 0.003', label='溢色')

        n = nuke.nodes.Reformat(
            inputs=[n],
            resize='none',
            label='整体滤镜结束')

        n = nuke.nodes.wlf_Write(inputs=[n])
        n.setName(u'_Write')
        self.task_step(u'输出节点创建')

        self.task_step(u'设置查看器')
        map(nuke.delete, nuke.allNodes('Viewer'))
        nuke.nodes.Viewer(inputs=[n, n.input(0), n, n])

        autoplace()

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

        mp_file = mp_file.replace('\\', '/')

        if mp_file.endswith('.nk'):
            n = nuke.nodes.Precomp(file=mp_file, postage_stamp=True)
        else:
            n = nuke.nodes.Read(file=mp_file)
            n['file'].fromUserText(mp_file)
        n.setName(u'MP')
        n = nuke.nodes.ModifyMetaData(
            inputs=[n], metadata='{{set comp/tag {}}}'.format('MP'))

        n = nuke.nodes.Reformat(inputs=[n], resize='fill')
        n = nuke.nodes.Transform(inputs=[n])
        n = _add_lut(n)
        n = nuke.nodes.Grade(inputs=[n], disable=True)
        n = nuke.nodes.Grade(
            inputs=[n, nuke.nodes.Ramp(p0='1700 1000', p1='1700 500')],
            disable=True)
        n = nuke.nodes.ProjectionMP(inputs=[n])
        n = nuke.nodes.SoftClip(
            inputs=[n], conversion='logarithmic compress')
        n = nuke.nodes.Reformat(inputs=[n], resize='none')
        n = nuke.nodes.DiskCache(inputs=[n])
        input_node = nuke.nodes.wlf_Lightwrap(inputs=[input_node, n],
                                              label='MP灯光包裹')
        n = nuke.nodes.Merge2(
            inputs=[input_node, n], operation='under', bbox='B', label='MP')

        return n

    @classmethod
    def _nodes_order(cls, n):
        tag = n.metadata(
            cls.tag_metadata_key) or n[ReadNode.tag_knob_name].value()
        return (u'_' + tag.replace(u'_BG', '1_').replace(u'_CH', '0_'))

    @classmethod
    def get_nodes_by_tags(cls, tags):
        """Return nodes that match given tags."""
        ret = []
        if isinstance(tags, (str, unicode)):
            tags = [tags]
        tags = tuple(unicode(i).upper() for i in tags)

        for n in nuke.allNodes(u'Read'):
            knob_name = u'{}.{}'.format(n.name(), ReadNode.tag_knob_name)
            tag = nuke.value(knob_name, '')
            if tag.partition('_')[0] in tags:
                ret.append(n)

        ret.sort(key=cls._nodes_order, reverse=True)
        return ret

    def output(self):
        """Save .nk file and render .jpg file."""

        LOGGER.info(u'{:-^30s}'.format(u'开始 输出'))
        _path = self._config['save_path'].replace('\\', '/')
        _dir = os.path.dirname(_path)
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        # Save nk
        LOGGER.info(u'保存为:\t%s', _path)
        nuke.Root()['name'].setValue(_path)
        nuke.scriptSave(_path)

        # Render png
        if self._config.get('RENDER_JPG'):
            for n in nuke.allNodes('Read'):
                name = n.name()
                if name in ('MP', 'Read_Write_JPG'):
                    continue
                for frame in (n.firstFrame(), n.lastFrame(),
                              int(nuke.numvalue(u'_Write.knob.frame'))):
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
                raise RenderError(u'Write_JPG_1')
            LOGGER.info(u'{:-^30s}'.format(u'结束 输出'))

    def _bg_ch_nodes(self):
        nodes = self._precomp()

        if not nodes:
            raise FootageError(u'BG', u'CH')

        for i, n in enumerate(nodes):
            self.task_step(u'创建{}'.format(
                n.metadata(self.tag_metadata_key) or n.name()))
            n = self._bg_ch_node_1(n)

            if i == 0:
                self.task_step(u'创建MP')
                n = self._merge_mp(
                    n, mp_file=self._config['mp'], lut=self._config.get('mp_lut'))
                n = self._merge_occ(n)
                n = self._merge_shadow(n)
                n = self._merge_screen(n)
            n = self._bg_ch_node_2(n)
            if i == 0:
                n = nuke.nodes.ModifyMetaData(
                    inputs=[n], metadata='{{set {} main}}'.format(
                        self.tag_metadata_key),
                    label='主干开始')

            if i > 0:
                n = nuke.nodes.Merge2(
                    inputs=[nodes[i - 1], n],
                    label=n.metadata(self.tag_metadata_key) or ''
                )

            nodes[i] = n
        return n

    def _precomp(self):
        tag_nodes_dict = {}
        ret = []

        def _tag_order(tag):
            return (u'_' + tag.replace(u'_BG', '1_').replace(u'_CH', '0_'))

        for n in self.get_nodes_by_tags(['BG', 'CH']):
            tag = n[ReadNode.tag_knob_name].value()
            tag_nodes_dict.setdefault(tag, [])
            tag_nodes_dict[tag].append(n)

        tags = sorted(tag_nodes_dict.keys(), key=_tag_order)
        for tag in tags:
            nodes = tag_nodes_dict[tag]
            try:
                LOGGER.debug('Precomp: %s', tag)
                n = precomp.redshift(nodes, async_=False)
                n = nuke.nodes.ModifyMetaData(
                    inputs=[n], metadata='{{set {} {}}}'.format(
                        self.tag_metadata_key, tag),
                    label='预合成结束')
                ret.append(n)
            except AssertionError:
                ret.extend(nodes)

        return ret

    def _bg_ch_node_1(self, input_node):
        n = input_node
        tag = n.metadata(self.tag_metadata_key)
        if 'MotionVectors' in nuke.layers(input_node):
            n = nuke.nodes.MotionFix(
                inputs=[n], channel='MotionVectors', output='motion')
        if 'SSS.alpha' in input_node.channels():
            n = nuke.nodes.Keyer(
                inputs=[n],
                input='SSS',
                output='SSS.alpha',
                operation='luminance key',
                range='0 0.01 1 1'
            )
        if 'Emission.alpha' in input_node.channels():
            n = nuke.nodes.Keyer(
                inputs=[n],
                input='Emission',
                output='Emission.alpha',
                operation='luminance key',
                range='0 0.2 1 1'
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

        n = nuke.nodes.Unpremult(inputs=[n], label='调色开始')

        if self._config['autograde']:
            LOGGER.info(u'{:-^30s}'.format(u'开始 自动亮度'))
            n = nuke.nodes.Grade(
                inputs=[n],
                unpremult='rgba.alpha',
                label='白点: [value this.whitepoint]\n混合:[value this.mix]\n使亮度范围靠近0-1'
            )
            _max = self._autograde_get_max(input_node)
            n['whitepoint'].setValue(_max)
            n['mix'].setValue(0.3 if _max < 0.5 else 0.6)
            LOGGER.info(u'{:-^30s}'.format(u'结束 自动亮度'))
        n = nuke.nodes.ColorCorrect(inputs=[n], disable=True)
        n = nuke.nodes.RolloffContrast(
            inputs=[n], contrast=2, center=0.001, soft_clip=1, disable=True)

        if tag and tag.startswith('BG'):
            kwargs = {'in': 'depth', 'label': '远处'}
            input_mask = nuke.nodes.PositionKeyer(inputs=[n], **kwargs)
            n = nuke.nodes.ColorCorrect(inputs=[n, input_mask], disable=True)
            n = nuke.nodes.Grade(
                inputs=[n, input_mask],
                black=0.05,
                black_panelDropped=True,
                label='深度雾',
                disable=True)
            kwargs = {'in': 'depth', 'label': '近处'}
            input_mask = nuke.nodes.PositionKeyer(inputs=[n], **kwargs)
            n = nuke.nodes.RolloffContrast(
                inputs=[n, input_mask],
                contrast=2,
                center=0.001,
                soft_clip=1,
                disable=True)
        n = self._attenuation_adjust(n)

        n = nuke.nodes.Premult(inputs=[n], label='调色结束')

        return n

    def _bg_ch_node_2(self, input_node):
        n = nuke.nodes.Reformat(
            inputs=[input_node],
            resize='none',
            label='滤镜开始')

        n = nuke.nodes.SoftClip(
            inputs=[n], conversion='logarithmic compress')
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

        try:
            n = nuke.nodes.RSMB(inputs=[n], disable=True, label='运动模糊')
        except RuntimeError:
            LOGGER.info(u'RSMB插件未安装')

        if 'Emission' in nuke.layers(n):
            kwargs = {'W': 'Emission.alpha'}
        else:
            kwargs = {'disable': True}
        n = nuke.nodes.Glow2(inputs=[n], size=30, label='自发光辉光', **kwargs)

        n = nuke.nodes.Reformat(
            inputs=[n],
            resize='none',
            label='滤镜结束')

        n = nuke.nodes.DiskCache(inputs=[n])

        self._bg_ch_end_nodes.append(n)
        return n

    @staticmethod
    def _autograde_get_max(n):
        # Exclude small highlight
        ret = 100
        erode = 0
        n = nuke.nodes.Dilate(inputs=[n])
        while ret > 1 and erode > n.height() / -100.0:
            n['size'].setValue(erode)
            LOGGER.info(u'收边 %s', erode)
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
            label='整体深度',
            hide_input=True)
        copy_node = nuke.nodes.Copy(
            inputs=[input_node, merge_node], from0='depth.Z', to0='depth.Z')
        return copy_node

    @classmethod
    def _merge_other(cls, input_node, nodes):
        nodes.sort(key=cls._nodes_order)
        if not nodes:
            return input_node
        input0 = input_node
        n = None
        for n in nodes:
            n = nuke.nodes.Dot(inputs=[n], hide_input=True)
            n = nuke.nodes.Grade(inputs=[n],
                                 channels='alpha',
                                 blackpoint='0.99',
                                 label='去除抗锯齿部分的内容')
            n = nuke.nodes.Merge2(
                inputs=[input0, n, n],
                operation='copy',
                also_merge='all',
                label=n.metadata(cls.tag_metadata_key) or '')
            input0 = n
        n = nuke.nodes.Remove(inputs=[n],
                              channels='rgba')
        n = nuke.nodes.Merge2(
            inputs=[input_node, n],
            operation='copy',
            Achannels='none', Bchannels='none', output='none',
            also_merge='all',
            label='合并rgba以外的层'
        )
        return n

    @staticmethod
    def _merge_occ(input_node):
        _nodes = Comp.get_nodes_by_tags(('OC', 'OCC'))
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
                label=_read_node[ReadNode.tag_knob_name].value(),
            )
        return n

    @staticmethod
    def _add_zdefocus_control(input_node):
        # Use for one-node zdefocus control
        n = nuke.nodes.ZDefocus2(inputs=[input_node], math='depth', output='focal plane setup',
                                 center=0.00234567, blur_dof=False, label='** 虚焦总控制 **\n在此拖点定虚焦及设置')
        n.setName(u'_ZDefocus')
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
        LOGGER.info(u'渲染: %s', name)
        n = nuke.nodes.Write(
            inputs=[read_node], channels='rgba')
        n['file'].fromUserText(os.path.join(
            script_name, '{}.png'.format(name)))
        if not frame:
            frame = nuke.frame()
        nuke.execute(n, frame, frame)

        nuke.delete(n)
    if show:
        webbrowser.open(os.path.join(nuke.value(
            'root.project_directory'), script_name))


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


def main():
    """Run this moudule as a script."""

    if sys.getdefaultencoding != 'UTF-8':
        reload(sys)
        sys.setdefaultencoding('UTF-8')
    LOGGER.info(COMP_START_MESSAGE)
    logging.getLogger('com.wlf').setLevel(logging.WARNING)
    try:
        Comp(json.loads(sys.argv[1]))
    except FootageError:
        LOGGER.error('没有素材')
    except RenderError as ex:
        LOGGER.error('渲染出错: %s', ex)
    except Exception:
        LOGGER.error('Unexpected exception during comp.', exc_info=True)
        raise


if __name__ == '__main__':
    main()
