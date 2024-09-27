import os

DEBUG_LAYER_SHOW_SOLAR_TERMINATOR = "SHOW_SOLAR_TERMINATOR"
DEBUG_LAYER_TIMESKIP = "TIMESKIP"


def debug_layers():
    return [
        layer.strip().upper()
        for layer in (os.environ.get("DRAKULA_DEBUG_LAYERS") or "").split(",")
    ]


def is_debug_layer_enabled(layer_name: str):
    return layer_name.strip().upper() in debug_layers()
