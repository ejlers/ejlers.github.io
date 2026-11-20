# The cover shoot

The six cover pictures on the Work page are not photographs. Each is a small scene built and rendered
with Blender from the scripts in this folder: a device (or, for TrackMan, a projected picture) on plain
grey surfaces, with the case's own screen on it.

This folder is everything needed to make them again or to change one. The folder name starts with an
underscore so the website does not publish it; it lives in the repository only.

## The rules of the shoot

Set by Carl. They hold for every cover.

1. The device is never covered: nothing in front of it, no part of it sunk into anything.
2. It lies flat on a surface or stands against one. It never rests on a corner or an edge.
   One deliberate exception: The Org's tablet lets a corner overhang the table edge.
3. No bend in the wall behind the device: one flat plane, no corner, no edge crossing behind it.
4. Large flat surfaces, not sculpture. The backdrop stays the backdrop.
5. Light greys close in tone, so the device is the foreground. Concrete floors, painted walls.
6. Focus on the screen, with the fall-off a camera would give.
7. TrackMan is not a device. It is a picture projected on a wall, with the launch monitor on the floor.

## What is here

| File | What it does |
| --- | --- |
| `studio.py` | The toolkit: materials, the phone, tablet and laptop, the projected picture, lights, camera, render. |
| `scenes.py` | One function per cover (`economic`, `trackman`, `donkey`, `theorg`, `tv2`, `ok`) plus the two small-screen scenes (`tv2s`, `oks`). Sizes, focus and aperture per cover are here too. |
| `radar.py` | Places the launch monitor on the floor of the TrackMan render, in its perspective. A flat composite, no re-render. |
| `install_covers.py` | Writes the finished covers into `img/work/<case>/` (desk cut and 4:3 small-screen cut) and updates the pictures in `work/index.html`. |
| `sheet.py` | A contact sheet of all six, for looking at them together. |
| `tex/` | The screens shown on the devices, the keyboard, and the launch monitor cut-out. |

Renders go to `out/`, which is not kept in the repository. The finished ones are: see below.

## The finished renders

`masters/` holds the finished full-quality render of every picture on the site, as it stood when it was
last published:

- the eight covers (`<scene>-mix-final.jpg`): the six on the Work page and the two small-screen scenes;
- the six header shots (`<scene>-mix-final-header.jpg`);
- TrackMan's two raw renders (`.png`), the room without the launch monitor, so the launch monitor can be
  moved or resized without rendering the room again.

- `blend/`: every one of those pictures as a Blender file (see "Opening a scene in Blender" below).

Everything that reads a render looks in `out/` first and then here. So from a fresh copy of the
repository, with nothing rendered:

```bash
python3 install_covers.py final
```

rebuilds every cover, header picture and share card on the site exactly as published, and

```bash
python3 radar.py trackman-mix-final.png 0.30 0.756 0.925 trackman-mix-final.jpg
```

places the launch monitor again. Only a change to a scene itself needs Blender.

When a picture is rendered anew and published, copy its finished `.jpg` from `out/` over the one in
`masters/` (and for TrackMan the raw `.png` too), and save its Blender file again into `masters/blend/`
(below), in the same change. That is what keeps this folder
the truth about what is on the site.

## Opening a scene in Blender

`masters/blend/` holds each published picture as a Blender file (Blender 5.3 or later): the room, the
device, the lights, the light in the room and the camera exactly as the final render had them, with the
screens and shadow pictures packed inside, so a file opens on its own anywhere. Open one, press F12 and
Blender renders the picture. Two things are added after the render and are not in the file: the faint
lens glow and film grain (the end of `scenes.py`), and TrackMan's launch monitor (`radar.py`).

A change made by hand in Blender stays in that file only. To keep it, carry it back into the scene's
function in `scenes.py`, so the next render from the scripts has it too.

To save the files again after changing a scene, use the quality `blend`, with the same settings as the
render (the table below), and copy the result from `out/` to `masters/blend/`, dropping `-people` from
the name:

```bash
PEOPLE=1 b3d/bin/python scenes.py -- tv2 blend mix
```

## The light in the room

Five of the covers have daylight falling into the room: a soft sun, and in its path a cut-out the camera
never sees, so only its shadow lands (`figure_shadow` in `studio.py`, the cut-outs drawn by `shadows.py`
into `tex/shadows/`). It is switched on with `PEOPLE=1`, and the render's name then ends in `-people`;
copy it to the plain name before installing. OK's light (a plain sun from the top right, its shadow
falling in front of the phone) is part of its scene and needs no switch. TrackMan has none.

The light is matched to the room by turning the room's lamps down, never by exposure, which would dim
the screens with everything else. Each cover's light and how far the lamps go down are in its function
and in the `ROOM` table in `scenes.py`.

| Picture | Light | Settings |
| --- | --- | --- |
| e-conomic | an edge of shade on the wall | `PEOPLE=1` |
| Donkey Republic | soft dapples, as through leaves | `PEOPLE=1` |
| The Org | a soft edge of shade across the table | `PEOPLE=1` |
| TV2 (and `tv2s`) | a window's light on the floor | `PEOPLE=1` |
| OK (and `oks`) | sun from the top right | none |
| TrackMan | none | none |

Add `HEADER=1` to any of them for the header shot.

## Setting up

Blender runs as a Python module, on the processor, no graphics card needed.

```bash
python3 -m venv b3d
```

```bash
b3d/bin/pip install bpy==5.3.0 pillow numpy
```

`radar.py`, `install_covers.py` and `sheet.py` only need Pillow and numpy, so any Python with those will do.

## Making a cover

From this folder:

```bash
b3d/bin/python scenes.py -- trackman test mix
```

The three words after `--` are the cover, the quality and the look.

- Quality: `test` (small and fast, for checking a composition), `mid` (a preview worth showing), `final` (what goes on the site, about ten minutes a cover). `focus` renders nothing and prints how sharp the screen will be.
- Look: `mix` is the one in use (concrete floor, painted wall).

Each render writes `out/<cover>-mix-<quality>.png` (the raw render) and a `.jpg` beside it with the lens glow and film grain every cover gets.

### TrackMan, the extra step

The launch monitor is added after the render:

```bash
python3 radar.py trackman-mix-final.png 0.30 0.756 0.925 trackman-mix-final.jpg
```

The three numbers are its size, how far across the frame its left edge sits, and how far down its feet stand. It reads the raw `.png` and writes the finished `.jpg` over the plain one, so the installer picks up the version with the launch monitor.

### Putting them on the site

```bash
python3 install_covers.py final
```

It needs a `final` render of every cover in `out/`, the two small-screen scenes included. For the others the small-screen cut is a 4:3 window out of the desk picture; where that window starts is the `SMALL` table at the top of the script.

Then look at the Work page at laptop and phone width before publishing.

## The header shots

Each case page opens on its cover from one edge of the window to the other. That picture is the same
scene in a 2:1 frame, pulled back, so the device keeps clear of every edge and a window of any shape
crops into plain wall and floor.

```bash
HEADER=1 b3d/bin/python scenes.py -- trackman final mix
```

`HEADER=1` turns any scene into its header shot (`out/<scene>-mix-<quality>-header.png` and `.jpg`).
How far back each one stands is the `PULL` table in `scenes.py`. Every header shot is made from the
same scene, and so the same camera, as the cover on the Work page; that is what lets the picture travel
between the two. The tall covers (`tv2`, `ok`) are no exception: their header shots stand at pull 1, the
phone as large as on the cover.

TrackMan's launch monitor goes on the same way, with the scene's pull as a last number:

```bash
python3 radar.py trackman-mix-final-header.png 0.30 0.756 0.925 trackman-mix-final-header.jpg 0.82
```

`install_covers.py` writes the header shots too, in three widths per case, each as a WebP and a JPEG. It
also writes each case's share card (`card.jpg`, the picture a link to the case shows in a message or a
feed): the header shot seen closer.

One thing ties the header shot to the stylesheet. Pressing a plate on the Work page carries its picture
into the case's header, and for the two to line up the stylesheet has to know each shot's pull: the
`--pull` values at the end of `css/styles.css`. Change a pull here and change it there.

## The front page's shots (parked)

The front page's backdrop (pointing at Work puts the cases behind the page) uses a third, wider shot of
each scene: `SUFFIX=-far HEADER=1 PULL=<p>` with economic 0.56, trackman 0.6, donkey 0.52, theorg 0.55,
tv2 0.55, ok 0.62; TrackMan's launch monitor is placed with `radar.py ... 0.6`. The installer writes
them as `front.webp` and prints where each device's middle is, for the SHOTS table in `js/site.js`.
The finished ones are in `masters/` (`*-far-header`).

## Changing a cover

Everything about a cover's composition is in its function in `scenes.py`: where the surfaces are, where the device lies, where the camera stands and what it looks at. Change, render at `test`, look, repeat; render `final` only when it is right.

A new screen for a device is a new picture in `tex/` with the same name.
