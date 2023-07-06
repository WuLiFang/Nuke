# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from .._types.aov_spec import AOVLayer, AOVSpec

from .aov_layer_impl import AOVLayerImpl as Layer
from .aov_layer_creation_method_impl import AOVLayerCreationMethodImpl as LayerCM


class ArnoldAOVSpec(object):
    def __init__(self):
        self.name = "Arnold"
        self.layers = (
            Layer(
                "diffuse",
                "漫反射",
                "PLUS",
            ),
            Layer(
                "diffuse_indirect",
                "间接漫反射",
                "COPY",
            ),
            Layer(
                "specular_indirect",
                "间接高光",
                "COPY",
            ),
            Layer(
                "specular_direct",
                "直接高光",
                "COPY",
            ),
            Layer(
                "specular",
                "高光",
                "PLUS",
                creation_methods=(
                    LayerCM(
                        "PLUS",
                        ("specular_indirect", "specular_direct"),
                    ),
                ),
            ),
            Layer(
                "reflection",
                "反射",
                "PLUS",
            ),
            Layer(
                "refraction",
                "折射",
                "PLUS",
            ),
            Layer(
                "sss",
                "次表面散射",
                "PLUS",
            ),
            Layer(
                "transmission",
                "透射",
                "PLUS",
            ),
            Layer(
                "transmission_albedo",
                "透射颜色",
                "IGNORE",
            ),
            Layer(
                "emission",
                "自发光",
                "PLUS",
            ),
        )  # type: tuple[AOVLayer, ...]
        self.output_layer_name = "beauty"


def _(v):
    # type: (ArnoldAOVSpec) -> AOVSpec
    return v
