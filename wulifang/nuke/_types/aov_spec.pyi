from typing import Protocol, Literal

AOVLayerOperation = Literal["COPY", "PLUS", "IGNORE"]
AOVLayerCreationOperation = Literal["MULTIPLY", "PLUS"]

class AOVLayerCreationMethod(Protocol):
    inputs: tuple[str, ...]
    operation: AOVLayerCreationOperation

class AOVLayer(Protocol):
    name: str
    alias: tuple[str, ...]
    label: str
    operation: AOVLayerOperation
    creation_methods: tuple[AOVLayerCreationMethod, ...]

class AOVSpec(Protocol):
    name: str
    layers: tuple[AOVLayer, ...]
    output_layer_name: str
