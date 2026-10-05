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
from .types import Mode
from .utils import Rect, get_size, make_command

# try:
#     import setproctitle

#     setproctitle.setproctitle(PROG_NAME)
# except ImportError:
#     pass


def apply_profile(profile: list[dict[str, float | bool | str]]):
    load()
    screen_info = {p["uid"]: p for p in profile}
    rects = []
    for di in displayInfo:
        si = screen_info.get(di.uid)
        if si is None:
            print(f"Profile has no entry for connected display {di.uid}")
            raise SystemExit(1)
        di.scale = cast("float | int", si.get("scale", 1))
        di.transform = cast("int", si.get("transform", "normal"))
        di.active = cast("bool", si.get("active", False))
        if di.active:
            w, h = get_size(
                cast("int", si["width"]),
                cast("int", si["height"]),
                cast("float", si.get("scale", 1)),
                cast(int, si.get("transform", "normal"))
            )
            di.mode = Mode((int)(w), (int)(h), cast("float", si["freq"]))
            rects.append(Rect(int(si["x"]), -int(si["y"]) - h, w, h))  # type: ignore
        else:
            rects.append(Rect(0, 0, 0, 0))  # width & height not used

    cmd = make_command(displayInfo, rects)
    time.sleep(0.5)
    print(cmd)
    if subprocess.run(shlex.split(cmd), check=False).returncode:
        print("Failed applying the layout")
        raise SystemExit(1)


def main():
    if len(sys.argv) > 1:
        profiles = load_profiles()
        if sys.argv[1] == "-l":
            print("")
            for p in profiles:
                print(f" - {p}")
        elif sys.argv[1] == "-m":
            load()
            current_uids = set(di.uid for di in displayInfo)
            for key in sorted(profiles):
                prof_uids = {p["uid"] for p in profiles[key]}
                # check that the two sets have the same elements
                if prof_uids == current_uids:
                    print(f"Matched profile {key}. Applying it...")
                    apply_profile(profiles[key])
                    sys.exit(0)
            print("No profile matches the currently connected displays")
            sys.exit(1)

        elif sys.argv[1][0] == "-":
            load()
            print(
                """With no options, launches the GUI
Options:
             -l : list profiles
             -m : find a profile that matches the currently plugged display set, and apply it.
                  No-op if not found; will apply first in alphabetical order if multiple found.
 <profile name> : loads a profile
            """
            )
        else:
            reload_pre_commands()
            try:
                profile = profiles[sys.argv[1]]
            except KeyError as e:
                print(f"No such profile: {sys.argv[1]}")
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
