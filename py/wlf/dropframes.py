# -*- coding=UTF-8 -*-
import nuke


def dropframe_ranges(file_path):
    """Return nuke framerange instance of dropframes."""
    ret = nuke.FrameRanges()
    if not self._node:
        return ret
    _filename = nuke.filename(self._node)
    if not _filename:
        return ret
    if expand_frame(_filename, 1) == _filename:
        if not os.path.isfile(_filename):
            ret = self._node.frameRange()
        return ret

    _read_framerange = xrange(
        self._node.firstFrame(), self._node.lastFrame() + 1)
    for f in _read_framerange:
        _file = expand_frame(_filename, f)
        if not os.path.isfile(unicode(_file, 'UTF-8').encode(SYS_CODEC)):
            ret.add([f])
    ret.compact()
    return ret
