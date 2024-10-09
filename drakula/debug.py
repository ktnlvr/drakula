import os
from typing import Optional

from .logging import logger

DEBUG_LAYER_SHOW_SOLAR_TERMINATOR = "SHOW_SOLAR_TERMINATOR"
DEBUG_LAYER_TIMESKIP = "TIMESKIP"
DEBUG_LAYER_STRESSTEST = "STRESSTEST"
DEBUG_LAYER_LOG_VERBOSE = "LOG_VERBOSE"


def debug_layers():
    return [
        layer.strip().upper()
        for layer in (os.environ.get("DRAKULA_DEBUG_LAYERS") or "").split(",")
    ]


_dev_seed_reported = False


def get_dev_seed() -> Optional[int]:
    if seed := os.environ.get("DRAKULA_SEED"):
        global _dev_seed_reported
        n = int.from_bytes(seed.encode("utf-8")) % (2**32)
        if not _dev_seed_reported:
            logger.info(f"Using dev seed {seed} ({n})")
            _dev_seed_reported = True
        return n
    return None


def is_debug_layer_enabled(layer_name: str):
    return layer_name.strip().upper() in debug_layers()
