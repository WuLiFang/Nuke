import hiero.core
from .. import _reload

class _g:
    init_once = False

def init():
    if _g.init_once:
        return
    _g.init_once = True
    if hiero.core.GUI:
        from ._init_gui import init_gui

        init_gui()


def reload():
    _reload.reload()
    init()
