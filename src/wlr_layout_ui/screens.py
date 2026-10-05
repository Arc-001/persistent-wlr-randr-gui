import json
import re
import subprocess

from .types import Mode, Screen

__all__ = ["Mode", "Screen", "load"]
MODE_RE = re.compile(r"^(?P<width>\d+)x(?P<height>\d+)(?P<x>[+-]\d+)(?P<y>[+-]\d+)$")


displayInfo: list[Screen] = []


def _parseMode(txt):
    res, freq = txt.split("@")
    x, y = res.split("x")
    return (int(x), int(y), float(freq[:-2]))


def load():
    if displayInfo:
        displayInfo.clear()

    out = subprocess.getstatusoutput("wlr-randr")
    if out[0] != 0:
        print("persistent-wlr-randr-gui was unable to run the command \"wlr-randr\", are you sure it's installed?")
        print("output when running wlr-randr is below:")
        raise ValueError(out[1])
    current_screen: Screen | None = None
    mode_mode = False
    for line in out[1].splitlines():
        if not line.strip():
            continue
        if line[0] != " ":
            uid, name = line.split(None, 1)
            current_screen = Screen(uid=uid, name=name.strip('"'), mode=Mode(640, 480, 60))
            try:
                chim = name.split("(", 1)[0].strip().rsplit(None, 1)[1]
            except IndexError:
                current_screen.active = False
            else:
                mode_re = MODE_RE.match(chim)
                if mode_re:
                    current_screen.position = (
                        int(mode_re.group("x")),
                        int(mode_re.group("y")),
                    )

            displayInfo.append(current_screen)
            mode_mode = False
        else:
            if line[2] != " ":
                mode_mode = False
            assert current_screen
            sline = line.strip()
            if mode_mode:
                try:
                    res, freq = sline.split(",", 1)
                except ValueError:
                    print(f"Unable to parse: {sline}")
                else:
                    res = res.split(None, 1)[0]
                    res = tuple(int(x) for x in res.split("x"))
                    freq, comment = freq.strip().split(None, 1)
                    current_screen.available.append(Mode(res[0], res[1], float(freq)))
                    if "current" in comment:
                        current_screen.mode = current_screen.available[-1]

            elif sline.startswith("Modes:"):
                mode_mode = True
            elif sline.startswith("Enabled"):
                current_screen.active = "yes" in sline
            elif sline.startswith("Position"):
                current_screen.position = tuple(int(x) for x in sline.split(":")[1].strip().split(","))
    try:
        monitors = json.loads(subprocess.getoutput("hyprctl -j monitors all"))
    except json.decoder.JSONDecodeError:
        pass
    else:
        monitors = {o["name"]: o for o in monitors}
        for info in displayInfo:
            monitor = monitors.get(info.uid)
            if monitor is None:
                continue
            info.active = monitor["activeWorkspace"]["id"] >= 0
            info.scale = monitor["scale"]
