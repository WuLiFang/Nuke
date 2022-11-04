# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    import wulifang


import nuke
from wulifang.vendor.pathlib2_unicode import Path
from wulifang.vendor import cast_unknown as cast
import wulifang.vendor.wulifang_manifest as m6t


class ManifestService:
    pass

    def path(self):
        name = nuke.scriptName()
        if not name:
            return ""
        p = Path(name.decode("utf-8")).parent / "wulifang.toml"  # type: Path
        return cast.text(p)

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
    # type: (ManifestService) -> wulifang.types.ManifestService
    return v
