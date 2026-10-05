"""Persistence of the last applied layout, and restoring it on login."""

import os
import shutil
import sys
from pathlib import Path

from .profiles import load_toml, write_toml

APP_NAME = "wlrlui"


def _xdg(var: str, default: str) -> Path:
    return Path(os.environ.get(var) or default).expanduser()


def state_file() -> Path:
    return _xdg("XDG_STATE_HOME", "~/.local/state") / APP_NAME / "last.toml"


def autostart_file() -> Path:
    return _xdg("XDG_CONFIG_HOME", "~/.config") / "autostart" / f"{APP_NAME}-restore.desktop"


def save_last_layout(layout: list[dict]) -> None:
    """Remember the layout that was last applied (and confirmed) so it can be restored after a reboot."""
    write_toml(state_file(), {"layout": layout})


def load_last_layout() -> list[dict] | None:
    layout = load_toml(state_file()).get("layout")
    return layout or None


def _executable() -> str:
    """Absolute path to wlrlui, since autostart entries don't see the pipx PATH."""
    exe = shutil.which(APP_NAME) or (sys.argv[0] if Path(sys.argv[0]).name == APP_NAME else None)
    return str(Path(exe).resolve()) if exe else APP_NAME


def _exec_quote(arg: str) -> str:
    """Quote a path for a .desktop Exec= line (double quotes, per the Desktop Entry spec)."""
    if not any(c in arg for c in ' \t"\'\\><~|&;$*?#()`'):
        return arg
    escaped = arg.replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
    return f'"{escaped}"'


def autostart_enabled() -> bool:
    return autostart_file().exists()


def set_autostart(*, enabled: bool) -> None:
    """Create or remove the XDG autostart entry that runs `wlrlui --restore` on login."""
    path = autostart_file()
    if not enabled:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=WLR Layout UI (restore layout)\n"
        "Comment=Re-apply the last monitor layout\n"
        f"Exec={_exec_quote(_executable())} --restore\n"
        "NoDisplay=true\n"
        "Terminal=false\n"
        "X-GNOME-Autostart-enabled=true\n"
    )
