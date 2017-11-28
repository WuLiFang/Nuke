# -*- coding=UTF-8 -*-
"""Comp footages and create output, can be run as script.  """

import logging
import os
import re
import sys
import webbrowser
import argparse

import nuke
import nukescripts

import wlf.config
import wlf.mp_logging
from wlf.notify import Progress

import precomp
from node import ReadNode
from orgnize import autoplace
from edit import undoable_func

__version__ = '0.19.6'

LOGGER = logging.getLogger('com.wlf.comp')
COMP_START_MESSAGE = '{:-^50s}'.format('COMP START')

if sys.getdefaultencoding != 'UTF-8':
    reload(sys)
    sys.setdefaultencoding('UTF-8')


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
        'tag_pat':
        r'(?i)(?:[^_]+_)?(?:ep\d+_)?(?:\d+[a-zA-Z]*_)?'
        r'(?:sc\d+[a-zA-Z]*_)?((?:[a-zA-Z][^\._]*_?){,2})',
        'mp': r"Z:\SNJYW\MP\EP14\MP_EP14_1.nk",
        'precomp': True,
        'masks': True,
        'colorcorrect': True,
        'filters': True,
        'zdefocus': True,
        'depth': True,
        'other': True,
    }
    path = os.path.expanduser(u'~/.nuke/wlf.comp.json')


CONFIG = Config()

if not nuke.GUI:
    nukescripts.PythonPanel = object


class Dialog(nukescripts.PythonPanel):
    """Dialog UI of comp config.  """

    knob_list = [
        (nuke.File_Knob, 'mp', '指定MP'),
        (nuke.File_Knob, 'mp_lut', 'MP LUT'),
        (nuke.Tab_Knob, 'parts', '节点组开关'),
        (nuke.Boolean_Knob, 'precomp', '预合成'),
        (nuke.Boolean_Knob, 'masks', '预建常用mask'),
        (nuke.Boolean_Knob, 'colorcorrect', '预建调色节点'),
        (nuke.Boolean_Knob, 'filters', '预建滤镜节点'),
        (nuke.Boolean_Knob, 'zdefocus', '预建ZDefocus'),
        (nuke.Boolean_Knob, 'depth', '合并depth'),
        (nuke.Boolean_Knob, 'other', '合并其他通道'),
        (nuke.Tab_Knob, 'filter', '正则过滤'),
        (nuke.String_Knob, 'footage_pat', '素材名'),
        (nuke.String_Knob, 'tag_pat', '标签'),
        (nuke.Script_Knob, 'reset', '重置'),
    ]

    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self, '自动合成设置', 'com.wlf.comp')
        self._shot_list = None

        for i in self.knob_list:
            k = i[0](i[1], i[2])
            try:
                k.setValue(CONFIG.get(i[1]))
            except TypeError:
                pass
            self.addKnob(k)
        for i in ('reset', 'precomp', 'masks', 'colorcorrect', 'filters', 'zdefocus',
                  'depth', 'other'):
            self.knobs()[i].setFlag(nuke.STARTLINE)

    def knobChanged(self, knob):
        """Overrride for buttons."""

        if knob is self.knobs()['OK']:
            self.update_config()
        elif knob is self.knobs()['reset']:
            self.reset()

    def reset(self):
        """Reset re pattern.  """

        for i in ('footage_pat', 'tag_pat'):
            knob = self.knobs()[i]
            knob.setValue(CONFIG.default.get(i))
            self.knobChanged(knob)

    def update_config(self):
        """Write all setting to config.  """

        for i in self.knob_list:
            if i[1] in CONFIG:
                CONFIG[i[1]] = self.knobs()[i[1]].value()


class Comp(object):
    """Create .nk file from footage that taged in filename."""

    tag_metadata_key = 'comp/tag'
    _attenuation_radial = None

    def __init__(self):
        LOGGER.info(u'吾立方自动合成 %s', __version__)

        self._errors = []
        self._bg_ch_end_nodes = []
        self._task = Progress(u'自动合成', total=20)

        for key, value in CONFIG.iteritems():
            if isinstance(value, str):
                CONFIG[key] = value.replace(u'\\', '/')

    @property
    def fps(self):
        """Frame per secondes.  """
        return CONFIG.get('fps') or nuke.numvalue('root.fps')

    def task_step(self, message=None):
        """Push task progress bar forward.  """
        if message:
            LOGGER.info(u'{:-^30s}'.format(message))
        self._task.step(message)

    def import_resource(self, dir_path):
        """Import footages from config dictionary."""

        # Get all subdir
        dirs = list(x[0] for x in os.walk(dir_path))
        self.task_step(u'导入素材')
        for dir_ in dirs:
            # Get footage in subdir
            LOGGER.info(u'文件夹 %s:', dir_)
            if not re.match(CONFIG['dir_pat'], os.path.basename(dir_.rstrip('\\/'))):
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
                    if re.match(CONFIG['footage_pat'], f, flags=re.I):
                        nuke.createNode(
                            u'Read', 'file {{{}/{}}}'.format(dir_, f))
                    else:
                        LOGGER.info(u'\t\t不匹配素材正则, 跳过')
        LOGGER.info(u'{:-^30s}'.format(u'结束 导入素材'))

        if not nuke.allNodes(u'Read'):
            raise FootageError(dir_path)

    def setup(self):
        """Add tag knob to read nodes, then set project framerange."""

        if not nuke.value('root.project_directory'):
            nuke.knob("root.project_directory",
                      r"[python {os.path.join("
                      r"nuke.value('root.name', ''), '../'"
                      r").replace('\\', '/')}]")

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

            # Ignore single frame.
            if n_first == n_last:
                continue

            # Expand frame range.
            if first is None:
                first = n_first
                last = n_last
            else:
                first = min(last, n.firstFrame())
                last = max(last, n.lastFrame())

        if first is None:
            first = last = 1

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
            output='rgb',
            mix='0.6',
            label='衰减调整',
            disable=True)

        return n

    @undoable_func('自动合成')
    def create_nodes(self):
        """Create nodes that a comp need."""

        self.task_step(u'分析读取节点')
        self.setup()
        self.task_step(u'创建节点树')

        self.task_step(u'合并BG CH')
        n = self._bg_ch_nodes()

        if CONFIG['other']:
            self.task_step(u'合并其他层')
            n = self._merge_other(n, self._bg_ch_end_nodes)

        if CONFIG['depth']:
            self.task_step(u'创建整体深度')
            nodes = nuke.allNodes('DepthFix')
            n = self._merge_depth(n, nodes)

        if CONFIG['zdefocus']:
            self.task_step(u'添加虚焦控制')
            self._add_zdefocus_control(n)

        n = nuke.nodes.Unpremult(inputs=[n], label='整体调色开始')

        n = nuke.nodes.Premult(inputs=[n], label='整体调色结束')

        n = nuke.nodes.Reformat(
            inputs=[n],
            resize='none',
            label='整体滤镜开始')

        n = nuke.nodes.SoftClip(
            inputs=[n], conversion='logarithmic compress')
        if CONFIG.get('filters'):
            n = nuke.nodes.Glow2(inputs=[n],
                                 tolerance=0.6,
                                 saturation=0.5,
                                 size=100,
                                 mix=0.25,
                                 disable=True)
            if 'motion' in nuke.layers(n):
                n = nuke.nodes.VectorBlur2(
                    inputs=[n], uv='motion', scale=1,
                    soft_lines=True, normalize=False, disable=True)
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

        autoplace(undoable=False)

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
            n = nuke.nodes.Precomp(file=mp_file,
                                   postage_stamp=True)
        else:
            n = nuke.nodes.Read(file=mp_file)
            n['file'].fromUserText(mp_file)
        n.setName(u'MP')
        n = nuke.nodes.ModifyMetaData(
            inputs=[n],
            label='元数据标签',
            metadata='{{set comp/tag {}}}'.format('MP'))

        n = nuke.nodes.Reformat(inputs=[n], resize='fill')
        n = nuke.nodes.Transform(inputs=[n])

        n = nuke.nodes.Unpremult(inputs=[n], label='调色开始')
        n = _add_lut(n)

        if CONFIG['colorcorrect']:
            n = nuke.nodes.Grade(inputs=[n], disable=True)
            n = nuke.nodes.Grade(
                inputs=[n, nuke.nodes.Ramp(p0='1700 1000', p1='1700 500')],
                disable=True)
        n = nuke.nodes.Premult(inputs=[n], label='调色结束')

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

    def output(self, filename):
        """Save .nk file and render .jpg file."""

        LOGGER.info(u'{:-^30s}'.format(u'开始 输出'))
        _path = filename.replace('\\', '/')
        _dir = os.path.dirname(_path)
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        # Save nk
        LOGGER.info(u'保存为:\t%s', _path)
        nuke.Root()['name'].setValue(_path)
        nuke.scriptSave(_path)

        # Render png
        if CONFIG.get('RENDER_JPG'):
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
            n = self._prepare_channels(n)
            n = self._add_colorcorrect_nodes(n)

            if i == 0:
                self.task_step(u'创建MP')
                n = self._merge_mp(
                    n, mp_file=CONFIG['mp'], lut=CONFIG.get('mp_lut'))
                n = self._merge_occ(n)
                n = self._merge_shadow(n)
                n = self._merge_screen(n)

            n = self._add_filter_nodes(n)

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
                if len(nodes) == 1 and not CONFIG.get('precomp'):
                    n = nodes[0]
                else:
                    n = precomp.redshift(nodes, async_=False)
                n = nuke.nodes.ModifyMetaData(
                    inputs=[n], metadata='{{set {} {}}}'.format(
                        self.tag_metadata_key, tag),
                    label='元数据标签')
                ret.append(n)
            except AssertionError:
                ret.extend(nodes)

        return ret

    @classmethod
    def _prepare_channels(cls, input_node):
        n = input_node
        if CONFIG['masks']:
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
        if 'MotionVectors' in nuke.layers(input_node):
            n = nuke.nodes.MotionFix(
                inputs=[n], channel='MotionVectors', output='motion')
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
        return n

    def _add_colorcorrect_nodes(self, input_node):

        tag = input_node.metadata(self.tag_metadata_key)
        n = input_node

        # if CONFIG['autograde']:
        #     if get_max(input_node, 'depth.Z') > 1.1:
        #         n['farpoint'].setValue(10000)

        n = nuke.nodes.Unpremult(inputs=[n], label='调色开始')

        # if CONFIG['autograde']:
        #     LOGGER.info(u'{:-^30s}'.format(u'开始 自动亮度'))
        #     n = nuke.nodes.Grade(
        #         inputs=[n],
        #         unpremult='rgba.alpha',
        #         label='白点: [value this.whitepoint]\n混合:[value this.mix]\n使亮度范围靠近0-1'
        #     )
        #     _max = self._autograde_get_max(input_node)
        #     n['whitepoint'].setValue(_max)
        #     n['mix'].setValue(0.3 if _max < 0.5 else 0.6)
        #     LOGGER.info(u'{:-^30s}'.format(u'结束 自动亮度'))
        if CONFIG['colorcorrect']:
            n = nuke.nodes.ColorCorrect(inputs=[n], disable=True)
            n = nuke.nodes.RolloffContrast(
                inputs=[n], channels='rgb',
                contrast=2, center=0.001, soft_clip=1, disable=True)

            if tag and tag.startswith('BG'):
                kwargs = {'in': 'depth', 'label': '远处'}
                input_mask = nuke.nodes.PositionKeyer(inputs=[n], **kwargs)
                n = nuke.nodes.ColorCorrect(
                    inputs=[n, input_mask], disable=True)
                n = nuke.nodes.Grade(
                    inputs=[n, input_mask],
                    black=0.05,
                    black_panelDropped=True,
                    label='深度雾',
                    disable=True)
                kwargs = {'in': 'depth', 'label': '近处'}
                input_mask = nuke.nodes.PositionKeyer(inputs=[n], **kwargs)
                n = nuke.nodes.ColorCorrect(
                    inputs=[n, input_mask], disable=True)
                n = nuke.nodes.RolloffContrast(
                    inputs=[n, input_mask],
                    channels='rgb',
                    contrast=2,
                    center=0.001,
                    soft_clip=1,
                    disable=True)
            n = self._attenuation_adjust(n)

        n = nuke.nodes.Premult(inputs=[n], label='调色结束')

        return n

    def _add_filter_nodes(self, input_node):
        n = nuke.nodes.Reformat(
            inputs=[input_node],
            resize='none',
            label='滤镜开始')

        n = nuke.nodes.SoftClip(
            inputs=[n], conversion='logarithmic compress')

        if CONFIG['zdefocus']:
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
            if not (n.metadata(self.tag_metadata_key) or '').startswith('BG'):
                n['autoLayerSpacing'].setValue(False)
                n['layers'].setValue(5)

        if CONFIG['filters']:
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

    # @staticmethod
    # def _autograde_get_max(n):
    #     # Exclude small highlight
    #     ret = 100
    #     erode = 0
    #     n = nuke.nodes.Dilate(inputs=[n])
    #     while ret > 1 and erode > n.height() / -100.0:
    #         n['size'].setValue(erode)
    #         LOGGER.info(u'收边 %s', erode)
    #         ret = get_max(n, 'rgb')
    #         erode -= 1
    #     nuke.delete(n)

    #     return ret

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
        _nodes = Comp.get_nodes_by_tags(('OC', 'OCC', 'AO'))
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

    parser = argparse.ArgumentParser(description='WuLiFang auto comper.')
    parser.add_argument('input_dir', help='Folder that contained footages')
    parser.add_argument('output', help='Script output path.')
    args = parser.parse_args()

    LOGGER.info(COMP_START_MESSAGE)
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
