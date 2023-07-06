# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from .._types.aov_spec import AOVLayer, AOVSpec

from .aov_layer_impl import AOVLayerImpl as Layer
from .aov_layer_creation_method_impl import AOVLayerCreationMethodImpl as LayerCM


class RedshiftAOVSpec(object):
    def __init__(self):
        self.name = "Redshift"
        self.layers = (
            Layer(
                "VolumeFogTint",
                "体积雾染色",
                "COPY",
            ),
            Layer(
                "depth",
                "深度",
                "COPY",
                alias=("Z",),
            ),
            Layer(
                "P",
                "位置",
                "COPY",
            ),
            Layer(
                "BumpNormals",
                "凹凸法线",
                "COPY",
                alias=("N",),
            ),
            Layer(
                "MotionVectors",
                "速度向量",
                "COPY",
            ),
            Layer(
                "PuzzleMatte",
                "拼图遮罩",
                "COPY",
            ),
            Layer(
                "DiffuseLightingRaw",
                "原始漫反射",
                "COPY",
            ),
            Layer(
                "DiffuseFilter",
                "漫反射过滤",
                "COPY",
            ),
            Layer(
                "DiffuseLighting",
                "漫反射",
                "PLUS",
                creation_methods=(
                    LayerCM(
                        "MULTIPLY",
                        ("DiffuseLightingRaw", "DiffuseFilter"),
                    ),
                ),
            ),
            Layer(
                "SSS",
                "次表面散射",
                "PLUS",
            ),
            Layer(
                "GI",
                "全局光照",
                "PLUS",
                creation_methods=(
                    LayerCM(
                        "MULTIPLY",
                        ("GIRaw", "DiffuseFilter"),
                    ),
                ),
            ),
            Layer(
                "GIRaw",
                "原始全局光照",
                "COPY",
            ),
            Layer(
                "SpecularLighting",
                "高光",
                "PLUS",
            ),
            Layer(
                "Reflections",
                "反射",
                "PLUS",
            ),
            Layer(
                "Refractions",
                "折射",
                "PLUS",
            ),
            Layer(
                "TransLightingRaw",
                "原始半透光",
                "COPY",
            ),
            Layer(
                "TransTint",
                "半透染色",
                "COPY",
            ),
            Layer(
                "TransLighting",
                "半透光",
                "PLUS",
                creation_methods=(
                    LayerCM(
                        "MULTIPLY",
                        ("TransLightingRaw", "TransTint"),
                    ),
                ),
            ),
            Layer(
                "TransGIRaw",
                "原始半透全局光照",
                "COPY",
            ),
            Layer(
                "TransGI",
                "半透全局光照",
                "PLUS",
                creation_methods=(
                    LayerCM(
                        "MULTIPLY",
                        ("TransGIRaw", "TransTint"),
                    ),
                ),
            ),
            Layer(
                "VolumeLighting",
                "体积光",
                "PLUS",
            ),
            Layer(
                "Emission",
                "自发光",
                "PLUS",
            ),
            Layer(
                "Caustics",
                "焦散",
                "PLUS",
            ),
        )  # type: tuple[AOVLayer, ...]
        self.output_layer_name = "rgba"


def _(v):
    # type: (RedshiftAOVSpec) -> AOVSpec
    return v

