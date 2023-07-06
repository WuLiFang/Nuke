# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    import wulifang._types as _types


import nuke
from wulifang.vendor.pathlib2_unicode import Path
import wulifang.vendor.wulifang_manifest as m6t
from wulifang._util import cast_text


class ManifestService:
    def path(self):
        name = cast_text(nuke.scriptName())
        if not name:
            return ""
        return cast_text(Path(name).parent / "wulifang.toml") # type: ignore

    def save(self, manifest):
        # type: (m6t.Manifest) -> None
        p = self.path()
        if not p:
            raise ValueError("no save path")
        m6t.save(manifest, p)

    def load(self):
        return m6t.load(self.path())

    def request_user_edit(self, manifest, wait=False):
        # type: (m6t.Manifest, bool) -> None
        # TODO:
        import wulifang

        wulifang.message.info("内置清单编辑器尚未实现，请联系管理员为你配置清单文件。\n%s" % (manifest.path,))


def _(v):
    # type: (ManifestService) -> _types.ManifestService
    return v
