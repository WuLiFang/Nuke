import init


def _enable_windows_unicode_console():
    import sys

    if sys.platform != "win32":
        return
    import win_unicode_console

    win_unicode_console.enable()


_enable_windows_unicode_console()
