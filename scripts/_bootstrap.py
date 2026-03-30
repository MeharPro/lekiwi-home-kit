from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VENDORED_LEROBOT_SRC = REPO_ROOT / "vendor" / "lerobot" / "src"


def bootstrap_vendor() -> Path:
    if str(VENDORED_LEROBOT_SRC) not in sys.path:
        sys.path.insert(0, str(VENDORED_LEROBOT_SRC))
    return REPO_ROOT
