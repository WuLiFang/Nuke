import hiero.core
from .. import _reload
import wulifang.license
import wulifang

class _g:
    init_once = False

def init():
    if _g.init_once:
        return
    if hiero.core.GUI:
        from wulifang.infrastructure.tray_message_service import TrayMessageService
        from wulifang.infrastructure.multi_message_service import MultiMessageService
        wulifang.message = MultiMessageService(
            wulifang.message,
            TrayMessageService()
        )
    try:
        wulifang.license.check()
    except wulifang.license.LicenseError:
        return
    if hiero.core.GUI:
        from ._init_gui import init_gui

        init_gui()

    _g.init_once = True

def reload():
    _reload.reload()
    init()
