# Persistent wlr-randr GUI

An simple GUI to setup the screens layout based on wlr-layout-ui, providing the functionality it offers to wlr-randr.

This is part of the tweaks I'm developing for many existing wlr configuration utilities so that they can be bundled into something capable of configuring any WLR or Smithay based compositor (but will primarily be tested via niri)

## Features

- Load and save profiles
- No grid snapping, but anchors in a smart way on overlap
- Set the screen settings
  - Layout: position, rotation, scale and flipping
  - Resolution
  - Refresh rate
- Makes clean, easy to understand layouts, with no negative values of random offsets `</monk>`

## Video / Demo

A bit outdated, but still relevant.

[![Video](https://img.youtube.com/vi/bJxVIu9cMzg/0.jpg)](https://www.youtube.com/watch?v=bJxVIu9cMzg)

## Requires

- Python
  - pyglet
  - tomli
  - tomli-w
- One of:
  - Hyprland >= 0.37
  - wlr-randr (for other wayland systems)
  - xrandr (for X11 / Xorg)

## Installation

```bash
python -m venv myenv
./myenv/bin/pip install wlr-layout-ui
```

This will create a "myenv" folder with the app installed.
You will need to run the app with the full path to it (/path/to/myenv/bin/wlrlui).

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
