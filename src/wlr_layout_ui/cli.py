import argparse
import shlex
import subprocess
import sys
import time
from typing import cast

import pyglet

from .gui import UI
from .profiles import load_profiles
from .screens import displayInfo, load
from .settings import UI_RATIO, reload_pre_commands
from .state import autostart_file, load_last_layout, save_last_layout, set_autostart
from .types import Mode
from .utils import Rect, get_size, make_command

# try:
#     import setproctitle

#     setproctitle.setproctitle(PROG_NAME)
# except ImportError:
#     pass


def apply_profile(profile: list[dict[str, float | bool | str]], *, remember: bool = True):
    """Apply a profile with wlr-randr, and remember it as the layout to restore after a reboot."""
    load()
    screen_info = {p["uid"]: p for p in profile}
    rects = []
    for di in displayInfo:
        si = screen_info.get(di.uid)
        if si is None:
            print(f"Profile has no entry for connected display {di.uid}")
            raise SystemExit(1)
        di.scale = cast("float | int", si.get("scale", 1))
        di.transform = cast("int", si.get("transform", 0))
        di.active = cast("bool", si.get("active", False))
        if di.active:
            w, h = get_size(
                cast("int", si["width"]),
                cast("int", si["height"]),
                cast("float", si.get("scale", 1)),
                cast("int", si.get("transform", 0)),
            )
            # the mode is the panel's native one; only the layout rectangle uses the scaled size
            di.mode = Mode(int(si["width"]), int(si["height"]), cast("float", si["freq"]))
            rects.append(Rect(int(si["x"]), -int(si["y"]) - h, w, h))  # type: ignore
        else:
            rects.append(Rect(0, 0, 0, 0))  # width & height not used

    cmd = make_command(displayInfo, rects)
    time.sleep(0.5)
    print(cmd)
    if subprocess.run(shlex.split(cmd), check=False).returncode:
        print("Failed applying the layout")
        raise SystemExit(1)
    if remember:
        save_last_layout(profile)


def find_matching_profile(profiles: dict) -> str | None:
    """Return the first profile (alphabetically) that covers exactly the connected displays."""
    current_uids = {di.uid for di in displayInfo}
    for key in sorted(profiles):
        if {p["uid"] for p in profiles[key]} == current_uids:
            return key
    return None


def restore_last_layout() -> int:
    """Re-apply the last confirmed layout (used on login); falls back to a matching profile."""
    # right after login the compositor may not have its outputs ready yet
    for _attempt in range(5):
        try:
            load()
        except ValueError:
            time.sleep(1)
        else:
            if displayInfo:
                break
            time.sleep(1)
    else:
        print("No displays available, nothing to restore")
        return 1

    last = load_last_layout()
    if last and {p["uid"] for p in last} == {di.uid for di in displayInfo}:
        print("Restoring the last applied layout...")
        apply_profile(last)
        return 0

    match = find_matching_profile(load_profiles())
    if match:
        print(f"Connected displays differ from the last layout. Applying matching profile {match}...")
        apply_profile(load_profiles()[match])
        return 0
    print("No saved layout matches the connected displays")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wlrlui", description="With no options, launches the GUI.")
    parser.add_argument("profile", nargs="?", help="load this profile")
    parser.add_argument("-l", "--list", action="store_true", help="list profiles")
    parser.add_argument(
        "-m",
        "--magic",
        action="store_true",
        help="find a profile that matches the currently plugged display set, and apply it "
        "(first in alphabetical order if multiple match)",
    )
    parser.add_argument(
        "-r",
        "--restore",
        action="store_true",
        help="re-apply the last layout applied from the GUI or CLI (meant for login/autostart)",
    )
    parser.add_argument("--install-autostart", action="store_true", help="restore the last layout automatically on login")
    parser.add_argument("--remove-autostart", action="store_true", help="stop restoring the layout on login")
    return parser


def main():
    args = build_parser().parse_args()

    if args.install_autostart:
        set_autostart(enabled=True)
        print(f"Installed {autostart_file()}")
        return
    if args.remove_autostart:
        set_autostart(enabled=False)
        print("Autostart removed")
        return
    if args.restore:
        sys.exit(restore_last_layout())
    if args.list:
        print("")
        for p in load_profiles():
            print(f" - {p}")
        return
    if args.magic:
        load()
        profiles = load_profiles()
        key = find_matching_profile(profiles)
        if key is None:
            print("No profile matches the currently connected displays")
            sys.exit(1)
        print(f"Matched profile {key}. Applying it...")
        apply_profile(profiles[key])
        sys.exit(0)
    if args.profile:
        profiles = load_profiles()
        reload_pre_commands()
        try:
            profile = profiles[args.profile]
        except KeyError as e:
            print(f"No such profile: {args.profile}")
            raise SystemExit(1) from e
        apply_profile(profile)
        return

    load()
    if not displayInfo:
        print("wlr-randr reported no displays")
        raise SystemExit(1)
    widest = [max(screen.available, key=lambda mode: mode.width).width for screen in displayInfo]
    tallest = [max(screen.available, key=lambda mode: mode.height).height for screen in displayInfo]
    max_width = int(sum(widest) // UI_RATIO)
    max_height = int(sum(tallest) // UI_RATIO)
    average_width = int(sum(widest) / len(displayInfo) // UI_RATIO)
    average_height = int(sum(tallest) / len(displayInfo) // UI_RATIO)

    width = max_width + average_width * 2
    height = max_height + average_height * 2
    window = UI(width, height)  # noqa: F841
    pyglet.app.run()
