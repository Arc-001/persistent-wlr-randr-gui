import os
import tempfile
from pathlib import Path

import tomli
import tomli_w

cfg_file = Path("~/.config/wlrlui.toml").expanduser()


def load_toml(path: Path) -> dict:
    """Read a TOML file, returning an empty dict if it doesn't exist."""
    try:
        with path.open("rb") as f:
            return tomli.load(f)
    except FileNotFoundError:
        return {}


def write_toml(path: Path, data: dict) -> None:
    """Write a TOML file atomically so a crash can't leave a truncated file behind."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as f:
            tomli_w.dump(data, f)
        Path(tmp_path).replace(path)
    except BaseException:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def load_profiles():
    return load_toml(cfg_file)


def save_profile(name: str, profile_data):
    profiles = load_profiles()
    profiles[name] = profile_data
    write_toml(cfg_file, profiles)


def delete_profile(name: str) -> None:
    profiles = load_profiles()
    if profiles.pop(name, None) is not None:
        write_toml(cfg_file, profiles)
