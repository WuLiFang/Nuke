# -*- coding=UTF-8 -*-
"""Batch comp runner.  """
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import re
import traceback
import webbrowser
from multiprocessing.dummy import Event, Pool, Process, Queue
from multiprocessing import cpu_count
from subprocess import PIPE, Popen

import nuke
from jinja2 import Environment, FileSystemLoader

from comp.__main__ import __absfile__
from comp.config import (IGNORE_EXISTED, MULTI_THREADING, START_MESSAGE,
                         BatchCompConfig)
import cast_unknown as cast
from wlf.decorators import run_with_memory_require
from wlf.progress import CancelledError, progress

LOGGER = logging.getLogger('com.wlf.batchcomp')


CONFIG = BatchCompConfig()


class BatchComp(Process):
    """Multiple comp.  """

    def __init__(self, input_dir, output_dir, flags=IGNORE_EXISTED | MULTI_THREADING):
        super(BatchComp, self).__init__()

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.flags = flags
        self._all_shots = tuple()

    def run(self):
        """Start process all shots with a processbar."""

        shots = self.get_shot_list()
        shots_info = dict.fromkeys(self._all_shots, '本次未处理')
        is_multi_threading = self.flags & MULTI_THREADING
        thread_count = cpu_count() if is_multi_threading else 1
        pool = Pool(thread_count)
        proc_queue = Queue()
        cancel_event = Event()

        def _run(shot):
            if cancel_event.is_set():
                return '取消: {}'.format(shot)

            output = os.path.join(
                CONFIG['output_dir'], '{}_v0.nk'.format(shot))
            input_dir = shot if os.path.isdir(
                shot) else os.path.join(CONFIG['input_dir'], shot)
            cmd = u'"{nuke}" -t -priority low "{script}" "{input_dir}" "{output}"'.format(
                nuke=nuke.EXE_PATH,
                script=__absfile__,
                input_dir=input_dir,
                output=output
            )

            try:
                LOGGER.info('%s:开始', shot)
                proc = Popen(cmd,
                             #  shell=True,
                             stdout=PIPE,
                             stderr=PIPE)
                proc_queue.put(proc)
                stderr = cast.text(proc.communicate()[1])

                if START_MESSAGE in stderr:
                    stderr = stderr.partition(
                        START_MESSAGE)[2].strip()

                if stderr:
                    shots_info[shot] = stderr
                elif proc.returncode:
                    if cancel_event.is_set():
                        shots_info[shot] = '用户取消'
                    else:
                        shots_info[shot] = 'Nuke非正常退出: {}'.format(
                            proc.returncode)
                else:
                    shots_info[shot] = '正常完成'

                LOGGER.info('%s:结束', shot)
            except:
                shots_info[shot] = traceback.format_exc()
                LOGGER.error('Unexpected exception during comp', exc_info=True)
                raise RuntimeError

            return '完成: {}'.format(shot)

        if is_multi_threading:
            _run = run_with_memory_require(8)(_run) # type: ignore

        def _oncancel():
            cancel_event.set()
            while not proc_queue.empty():
                proc = proc_queue.get()
                if proc.poll() is None:
                    try:
                        proc.terminate()
                    except OSError:
                        pass

        try:
            for _ in progress(pool.imap_unordered(_run, shots),
                              name='批量合成',
                              total=len(shots),
                              start_message=(
                                  '正在使用 {} 线程进行……'.format(thread_count)),
                              oncancel=_oncancel):
                pass
        except (CancelledError, RuntimeError):
            pass

        webbrowser.open(self.generate_report(shots_info))
        webbrowser.open(CONFIG['output_dir'])

    @classmethod
    def generate_report(cls, shots_info):
        """Generate batchcomp report.  """

        assert isinstance(shots_info, dict)
        env = Environment(loader=FileSystemLoader(
            os.path.abspath(__file__ + '/../../templates')))
        template = env.get_template('batchcomp.html')
        data = template.render(shots_info=sorted(shots_info.items()))

        log_path = os.path.join(CONFIG['output_dir'], u'批量合成日志.html')
        with open(cast.binary(log_path), 'w') as f:
            f.write(cast.text(data))

        return log_path

    def get_shot_list(self):
        """Return shot_list generator from a config dict."""

        _dir = self.input_dir
        _out_dir = self.output_dir
        if not os.path.isdir(_dir):
            return []

        _ret = os.listdir(_dir)
        if isinstance(_ret[0], str):
            _ret = tuple(cast.text(i) for i in _ret)
        self._all_shots = _ret
        if self.flags & IGNORE_EXISTED:
            _ret = (i for i in _ret
                    if not os.path.exists(os.path.join(_out_dir, u'{}_v0.nk'.format(i)))
                    and not os.path.exists(os.path.join(_out_dir, u'{}.nk'.format(i))))
        _ret = (i for i in _ret if (
            re.match(CONFIG['dir_pat'], i) and os.path.isdir(os.path.join(_dir, i))))

        if not _ret:
            _dir = _dir.rstrip('\\/')
            _dirname = os.path.basename(_dir)
            if re.match(CONFIG['dir_pat'], _dir):
                _ret = [_dir]
        return sorted(_ret)
