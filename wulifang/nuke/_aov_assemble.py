# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
import inspect
import hashlib

from wulifang._util import (
    cast_iterable,
    layer_from_filename,
    cast_text,
    cast_str,
    iteritems,
    create_iife,
)
from wulifang.nuke._util import (
    add_rgba_layer,
    knob_of,
    copy_layer,
    create_node,
    undoable,
)
from ._auto_place import auto_place
from wulifang.nuke.infrastructure.redshift_aov_spec import RedshiftAOVSpec
from wulifang.nuke.infrastructure.arnold_aov_spec import ArnoldAOVSpec

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import (
        Text,
        Union,
        Optional,
        Iterable,
        Iterator,
    )
    from wulifang.nuke import _types
    from wulifang._compat.str import Str


def all_spec():
    # type: () -> Iterator[_types.AOVSpec]
    yield RedshiftAOVSpec()
    yield ArnoldAOVSpec()


class _InputNodes(object):
    def __init__(self, inputs):
        # type: (Union[nuke.Node,Iterable[nuke.Node]]) -> None
        self.nodes = tuple(cast_iterable(inputs))
        self.by_layer = {}  # type: dict[Text, nuke.Node]
        if len(self.nodes) == 1:
            n = self.nodes[0]
            for layer in nuke.layers(n):
                self.by_layer[cast_text(layer)] = n
        else:
            for n in self.nodes:
                filename = cast_text(nuke.filename(n))
                layer = layer_from_filename(filename)
                self.by_layer[layer] = n

    def _spec_score(self, spec):
        # type: (_types.AOVSpec ) -> float
        ret = 0
        for layer in spec.layers:
            if layer.name in self.by_layer:
                ret += 1
            elif any(i for i in layer.alias if i in self.by_layer):
                ret += 0.9
        return ret

    def detect_spec(self):
        # type: () -> Optional[_types.AOVSpec]
        ret = None
        max_score = 0
        for spec in all_spec():
            score = self._spec_score(spec)
            if score > max_score:
                ret = spec
                max_score = score
        return ret


class _Context(object):
    def __init__(self, inputs, spec):
        # type: (_InputNodes, _types.AOVSpec) -> None
        self._inputs = inputs
        self._spec = spec
        self._layer_spec_index_by_name = {}  # type: dict[str, int]
        for index, i in enumerate(self._spec.layers):
            self._layer_spec_index_by_name[i.name] = index
            for j in i.alias:
                self._layer_spec_index_by_name[j] = index
        # self._output = None  # type: Optional[nuke.Node]

    def layer(self, name):
        # type: (Text) -> Optional[_types.AOVLayer]
        index = self._layer_spec_index_by_name.get(name)
        if index is None:
            return
        return self._spec.layers[index]

    def obtain_rgb_node(self, layer_name):
        # type: (Text) -> Optional[nuke.Node]
        layer = self.layer(layer_name)
        if not layer:
            return
        existing = self._inputs.by_layer.get(layer.name)
        if existing:
            if cast_text(existing.Class()) != "Shuffle":
                add_rgba_layer(layer.name)
                n = create_node(
                    "Shuffle",
                    "in %s\nout rgb" % layer.name,
                    inputs=(existing,),
                    hide_input=True,
                )
                self._inputs.by_layer[layer.name] = n
                return n
            return existing
        for method in layer.creation_methods:
            inputs = tuple(self.obtain_rgb_node(i) for i in method.inputs)
            if any(i is None for i in inputs):
                continue
            return create_node(
                "Merge",
                "\n".join(
                    (
                        "operation %s" % (method.operation.lower(),),
                        "output rgb",
                    )
                ),
                inputs=inputs,
                label=layer.name,
            )


class _Switch(object):
    knob_ignore = (
        "xpos",
        "ypos",
        "selected",
        "name",
        "gl_color",
        "tile_color",
        "label",
        "note_font",
        "note_font_size",
        "note_font_color",
        "hide_input",
        "cached",
        "dope_sheet",
        "bookmark",
        "postage_stamp",
        "postage_stamp_frame",
    )

    @staticmethod
    def _str_output(v):
        # type: (Str) -> str
        import sys

        if sys.version_info[0] == 2:
            return v.decode("utf-8")
        return v  # type: ignore

    @staticmethod
    def _str_input(v):
        # type: (str) -> Str
        import sys

        if sys.version_info[0] == 2:
            return v.encode("utf-8")
        return v  # type: ignore

    @classmethod
    def hash(cls, node):
        # type: (Optional[nuke.Node]) -> Text
        """Node hash result of @node up to upstream start."""
        if not node:
            return ""

        import hashlib

        def knob_input(node):
            # type: (nuke.Node) -> Iterator[Text]

            for i in cls._str_output(
                node.writeKnobs(
                    nuke.WRITE_ALL | nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_VALUE
                )
            ).split("\n"):
                if i.partition(" ")[0] in cls.knob_ignore:
                    continue
                yield i

        def upstream(start):
            # type: (nuke.Node) -> set[nuke.Node]
            ret = set()  # type: set[nuke.Node]

            nodes = [start]  # type: list[nuke.Node]
            while nodes:
                deps = set(
                    j
                    for i in nodes
                    for j in i.dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)
                    if i
                )
                ret.update(set(deps))
                nodes = [n for n in deps if n not in ret and n not in nodes]
            return ret

        h = hashlib.md5()
        for n in upstream(node):
            for i in knob_input(n):
                h.update(i.encode("utf-8"))
                h.update("\n\n".encode("utf-8"))
        return h.hexdigest()

    @classmethod
    def which(cls, raw_hash):
        # type: (Text) -> int
        n = nuke.thisNode()
        if cls.hash(n.input(1)) == raw_hash:
            return 0
        return 1


_SWITCH_SOURCE = inspect.getsource(_Switch)
_SWITCH_GLOBAL_CLASS = "__Switch_%s" % (
    hashlib.md5(inspect.getsource(_Switch).encode("utf-8")).hexdigest(),
)
_SWITCH_ON_CREATE = create_iife(
    """\
%s
globals()["%s"] = _Switch
"""
    % (_SWITCH_SOURCE, _SWITCH_GLOBAL_CLASS)
)


@undoable("AOV 组装")
def assemble(nodes, spec=None):
    # type: (Union[Iterable[nuke.Node], nuke.Node], Optional[_types.AOVSpec]) -> Optional[nuke.Node]

    input = _InputNodes(cast_iterable(nodes))
    spec = spec or input.detect_spec()
    if not spec:
        nuke.message(cast_str("输入节点不匹配任何已知的规范"))
        return
    ctx = _Context(input, spec)

    # set label to input nodes
    if len(input.nodes) > 1:
        for name, n in iteritems(input.by_layer):
            layer = ctx.layer(name)
            if not layer:
                continue
            label_knob = knob_of(n, "label", nuke.String_Knob)
            if layer.label not in cast_text(label_knob.value()):
                label_knob.setValue(
                    cast_str(
                        "\n".join(
                            i
                            for i in (
                                cast_text(label_knob.value()),
                                layer.label,
                            )
                            if i
                        )
                    )
                )

    output = (
        ctx.obtain_rgb_node(spec.output_layer_name)
        or input.by_layer.get(spec.output_layer_name)
        or input.by_layer.get("rgb")
    )

    # prepare input nodes

    # rename
    for layer in (i for i in spec.layers if i.name not in input.by_layer):
        for alias in layer.alias:
            src_node = input.by_layer.get(alias)
            if not src_node:
                continue
            src_layers = set(cast_text(i) for i in nuke.layers(src_node))
            output = copy_layer(
                output,
                layer.name,
                src_node,
                next(j for j in (alias, layer.name, "rgba") if j in src_layers),
            )
            input.by_layer[layer.name] = output
    # copy
    for layer in (i for i in spec.layers if i.operation == "COPY"):
        src_node = input.by_layer.get(layer.name)
        if not src_node:
            continue
        src_layers = set(cast_text(i) for i in nuke.layers(src_node))
        output = copy_layer(
            output,
            layer.name,
            src_node,
            next(j for j in (layer.name, "rgba") if j in src_layers),
        )

    # plus
    dot_before_plus = create_node("Dot", inputs=(output,))
    remove_node = create_node("Remove", "channels rgb", inputs=(dot_before_plus,))
    output = remove_node

    for layer in (i for i in spec.layers if i.operation == "PLUS"):
        src_node = ctx.obtain_rgb_node(layer.name)
        if src_node:
            output_layers = set(cast_text(i) for i in nuke.layers(output))
            output = create_node(
                "Merge2",
                "\n".join(
                    (
                        "operation plus",
                        "output rgb",
                        "also_merge %s"
                        % (layer.name if layer.name not in output_layers else "none",),
                    )
                ),
                inputs=(output, src_node),
                label=layer.label,
            )

    # switch
    switch = create_node(
        "Switch",
        "\n".join(
            (
                r"""which {{{\[python %s.which(\"%s\")]}}}"""
                % (
                    _SWITCH_GLOBAL_CLASS,
                    _Switch.hash(node=output),
                ),
                "onCreate {%s}" % (_SWITCH_ON_CREATE,),
            )
        ),
        label="%s 组装\n自动开关" % (spec.name,),
        inputs=(dot_before_plus, output),
    )

    if remove_node is output:
        knob_of(switch, "disable", class_=nuke.Boolean_Knob).setValue(True)

    auto_place(switch, recursive=True, async_=True)
    return switch
