# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Self, Iterator


from collections import defaultdict
import io
import json

import nuke

from wulifang._util import cast_text, iteritems, iterkeys
from wulifang.nuke._util import knob_of

from ._cryptomatte_layer import CryptomatteLayer


class CryptomatteManifest:

    _METADATA_LEGAL_PREFIX = ("exr/cryptomatte/", "cryptomatte/")

    def __init__(self, raw):
        # type: (dict[Text,Text]) -> None
        self.raw = raw

    def names(self):
        return iterkeys(self.raw)

    @classmethod
    def _parse_metadata_key(cls, key):
        # type: (Text) -> tuple[Text, Text]
        for prefix in cls._METADATA_LEGAL_PREFIX:
            if key.startswith(prefix):
                numbered_key = key[
                    len(prefix) :
                ]  # ex: "exr/cryptomatte/ae93ba3/name" --> "ae93ba3/name"
                metadata_id, partial_key = numbered_key.split(
                    "/"
                )  # ex: "ae93ba3/name" --> ae93ba3, "name"
                return metadata_id, partial_key
        return "", ""

    @classmethod
    def from_file(cls, name):
        # type: (Text) -> Self
        with io.open(name, encoding="utf-8") as f:
            return cls(json.load(f))

    @classmethod
    def from_node(cls, node):
        # type: (nuke.Node) -> Iterator[tuple[CryptomatteLayer, Self]]

        by_id = defaultdict(dict)  # type: dict[Text, dict[Text,Text]]
        for k, v in iteritems(node.metadata()):
            id_, partial_key = cls._parse_metadata_key(cast_text(k))
            if id_:
                by_id[id_][partial_key] = cast_text(v)

        for id, metadata in iteritems(by_id):
            if "manifest" in metadata:
                yield CryptomatteLayer(id, metadata), cls(
                    json.loads(metadata["manifest"])
                )
            # spell-checker: word manif_file
            if "manif_file" in metadata:
                try:
                    yield CryptomatteLayer(id, metadata), cls.from_file(
                        metadata["manif_file"]
                    )
                except OSError:
                    pass

    @classmethod
    def from_cryptomatte(cls, __node):
        # type: (nuke.Node) -> tuple[CryptomatteLayer, Self]
        assert (
            cast_text(__node.Class()) == "Cryptomatte"
        ), "should be a Cryptomatte node, got %s " % (cast_text(__node.Class()),)
        layer_name = cast_text(knob_of(__node, "cryptoLayer", nuke.String_Knob).value())
        try:
            return next(i for i in cls.from_node(__node) if i[0].name() == layer_name)
        except StopIteration:
            raise ValueError("layer(%s) not found in manifest" % (layer_name,))

