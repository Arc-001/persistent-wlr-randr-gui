import os
import tempfile
from pathlib import Path

import tomli
import tomli_w

cfg_file = Path("~/.config/wlrlui.toml").expanduser()


def load_profiles():
    try:
        with cfg_file.open("rb") as f:
            return tomli.load(f)
    except FileNotFoundError:
        return {}


def save_profile(name: str, profile_data):
    profiles = load_profiles()
    profiles[name] = profile_data

    # write to a temp file first so a crash can't leave a truncated config behind
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=cfg_file.parent, prefix=f".{cfg_file.name}.")
    try:
        with os.fdopen(fd, "wb") as f:
            tomli_w.dump(profiles, f)
        Path(tmp_path).replace(cfg_file)
    except BaseException:
        Path(tmp_path).unlink(missing_ok=True)
        raise
