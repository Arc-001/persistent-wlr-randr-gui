# Persistent wlr-randr GUI

A simple GUI to setup the screen layout based on wlr-layout-ui, providing the functionality it offers to wlr-randr.

This is part of the tweaks I'm developing for many existing wlr configuration utilities so that they can be bundled into something capable of configuring any WLR or Smithay based compositor (but will primarily be tested via niri)

## Features

- Load, save and delete profiles
- Shows your current layout when it starts, and tells you which saved profile (if any) it matches
- Remembers the last layout you applied and restores it after a reboot
- No grid snapping, but anchors in a smart way on overlap
- Set the screen settings
  - Layout: position, rotation, scale and flipping
  - Resolution
  - Refresh rate
- Makes clean, easy to understand layouts, with no negative values or random offsets.

<img width="2274" height="1316" alt="image" src="https://github.com/user-attachments/assets/918702a7-4177-401f-8dc2-4899491ce135" />


## Requires

- Python
  - pyglet
  - tomli
  - tomli-w
  - poetry
  - pipx
- wlr-randr

## Building

1. `git clone https://github.com/alicealysia/persistent-wlr-randr-gui/`
2. `cd persistent-wlr-randr-gui`
3. `poetry install`
4. `poetry build`

## Installation

1. Either download the latest release or build the whl yourself
2. `pipx install ~/path/to/persistent_wlr_randr_ui-2.0.0a1.tar.gz` (or the `.whl` from `dist/`)
3. it's also recommended that you copy the file "wlr-layout-ui.desktop" to ~/.local/share/applications

`pipx` installs the app into its own isolated environment and puts `wlrlui` on your `PATH` (usually `~/.local/bin`).
If the command isn't found, run `pipx ensurepath` and restart your shell.

## Usage

### Start the GUI

```bash
wlrlui
```

Note that a `.desktop` file is provided in the `files` folder for an easy integration to your environment.

### List available profiles (CLI)

```bash
wlrlui -l
```

### Load a profile

To load the profile called "cinema":

```bash
wlrlui cinema
```

### Persist across reboots

`wlr-randr` changes are lost when the session ends. Every layout you confirm in the GUI (or apply from the CLI) is
remembered in `~/.local/state/wlrlui/last.toml`, and can be re-applied on login:

```bash
wlrlui -r          # or --restore
```

If the connected displays differ from the last layout, it falls back to the first saved profile matching them.

To run it automatically, either press **Persist** in the GUI (or run `wlrlui --install-autostart`, undo with
`wlrlui --remove-autostart`) to create an XDG autostart entry, or start it from your compositor's config:

```kdl
// niri: ~/.config/niri/config.kdl
spawn-at-startup "wlrlui" "--restore"
```

```ini
# hyprland: ~/.config/hypr/hyprland.conf
exec-once = wlrlui --restore
```

The XDG autostart entry only runs if your session starts autostart entries (e.g. `niri-session` with
systemd's xdg-autostart); otherwise use the compositor snippets above.

### Magic layout

_added in 1.6.11_

Applies the first profile (in alphabetical order) matching the set of monitors which are currently active:

```bash
wlrlui -m
```

It is highly recommended that you add this to a .desktop file under /etc/xdg/autostart

Other options are to create an appropriate systemd file, or to make it start automatically from your compositor's config file.

### GUI shortcuts

- `ENTER`: apply the current settings
- `ESC`: close the app
- `TAB`: switch between profiles
