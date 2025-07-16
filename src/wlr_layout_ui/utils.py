import re

from .types import Rect, Screen

config = {"hyprland": False}

hex_re = re.compile(r"^[0-9x]+$")


def get_size(width: int, height: int, scale: float, transform: str, glob_scale: float = 1):
    w, h = (
        ((width / glob_scale) / scale),
        ((height / glob_scale) / scale),
    )
    if transform in (1, 3, 5, 7):
        return (h, w)
    return (w, h)


def get_screen_size(screen: Screen, scale: float = 1):
    """Get the size of the window based on the screen size and UI_RATIO."""
    assert screen.mode
    return get_size(screen.mode.width, screen.mode.height, screen.scale, screen.transform, scale)


def simplify_model_name(name):
    # remove duplicate words keeping order (comparing lowercase)
    words = list(dict.fromkeys(word for word in name.split() if not hex_re.match(word)))
    return " ".join(words)


def make_command(screens: list[Screen], rects: list[Rect]) -> str:
    cmd = make_command_legacy(screens, rects)
    return cmd


def make_command_legacy(screens: list[Screen], rects: list[Rect]) -> str:
    screens_rect = rects.copy()
    trim_rects_flip_y(screens_rect)
    command = ["wlr-randr"]

    for screen, rect in zip(screens, screens_rect):
        if not screen.active:
            command.append(f"--output {screen.uid} --off")
            continue
        assert screen.mode
        sep = ","
        mode = f"{int(screen.mode.width)}x{int(screen.mode.height)}@{screen.mode.freq}"
        transform_text = [
            "normal",
            "90",
            "180",
            "270",
            "flipped",
            "flipped-90",
            "flipped-180",
            "flipped-270"
        ]
        command.append(f"--output {screen.uid} --on --pos {int(rect.x)}{sep}{int(rect.y)} --mode {mode} --scale {screen.scale} --transform {transform_text[screen.transform]}")  # noqa: E501

    cmd = " ".join(command)
    return cmd


def brighten(color):
    return tuple(min(255, c + 20) for c in color)


def sorted_resolutions(modes):
    res = set((m.width, m.height) for m in modes)
    lres = list(res)
    lres.sort(reverse=True)
    return lres


def sorted_frequencies(modes, filter_w=None, filter_h=None):
    filtered_modes = modes.copy()
    if filter_w:
        filtered_modes = filter(lambda m: m.width == filter_w, filtered_modes)
    if filter_h:
        filtered_modes = filter(lambda m: m.height == filter_h, filtered_modes)
    res = set(m.freq for m in filtered_modes)
    lres = list(res)
    lres.sort(reverse=True)
    return lres


def find_matching_mode(modes, res, freq):
    for mode in modes:
        if mode.width == res[0] and mode.height == res[1] and mode.freq == freq:
            return mode


def compute_bounding_box(rects):
    min_x = min(r.x for r in rects)
    min_y = min(r.y for r in rects)
    max_x = max(r.x + r.width for r in rects)
    max_y = max(r.y + r.height for r in rects)
    return (min_x, min_y, max_x - min_x, max_y - min_y)


def trim_rects_flip_y(rects):
    min_x = min([r.x for r in rects if r])
    max_y = max([r.y + r.height for r in rects if r])
    for rect in rects:
        if rect is None:
            continue
        rect.x = rect.x - min_x
        rect.y = max_y - (rect.y + rect.height)
