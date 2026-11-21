# carlejlers.dk: working knowledge

What has been learned building and polishing Carl's portfolio site, carlejlers.dk. Read this before
changing anything. The site itself (stylesheet comments, `_covers/README.md`, `_covers/parked/README.md`)
holds the detail; this file is the short version and the working agreements.

## Working with Carl

- Carl is a product designer, not a developer. End every larger step with a short plain-language
  summary: what changed, what he will see. No jargon, no file paths, no code names.
- He writes in English or Danish; answer in the language he wrote in.
- He reviews by looking. Show screenshots or contact sheets of every format (laptop 1440, large 1920,
  ultrawide 3440, small laptop 1280, phone 430) before asking to publish.
- Publish only when he says so ("go", "publish", "do it"). Confirm anything that costs money first.
- When feedback is ambiguous ("flip the perspective"), show options side by side (A/B) rather than guess
  twice. A misread perspective request cost two rounds on the OK cover.
- He often tests on his phone and in Safari and Chrome; check both engines.

## Facts about Carl and the cases (get these right)

- Title: Senior Product Designer (also his title at e-conomic, never "Senior UX Designer").
- At e-conomic he is part of the EVA team; he did not design EVA's identity. EVA is "it", never "she".
- The Org: Senior, then Lead Product Designer, 2021 to 2023.
- TV2 Regionerne and OK: Product Designer at Shape, 2019.
- Case names and their "what it is" line carry no full stop.
- Never mention the friend's portfolio (the studio whose scattered-thumbnail idea came up) in commits,
  PRs, files or copy.

## Publishing

- Repository `ejlers/ejlers.github.io`, served by GitHub Pages from `master`, Jekyll defaults (folders
  starting with `_` or `.` are not published).
- Flow: commit on the working branch, open a PR, wait for the `check` run, squash-merge, then reset the
  working branch to `master`.
- Before committing: `node tools/stamp.mjs` (refreshes the `?v=` stamps so browsers fetch current
  files) and `npm run check` (every colour and spacing value is a token, both colour schemes complete,
  hovers guarded, no long dashes, prose keeps its measure).
- Local preview: `python3 -m http.server 8731` from the repository, Playwright for screenshots.

## Design principles in force

- One typeface (Switzer, self-hosted), one text size plus one display size; hierarchy is weight and grey.
- Every value is a token; spacing ramp 5, 10, 15, 20, 30, 40, 50, 80px. Light and dark schemes.
- A page is a stack of bands on twelve columns. Lists (the front page's index, More work) sit on the
  same twelve columns on a desk.
- A case gives its information in one order wherever it appears: name, what it is, role and years,
  disciplines, standfirst. Logos were removed.
- The breadcrumb ("trail") bar runs the full window width.
- Case pages open on their cover edge to edge (the header shot), name in display size on top.
- Each case has a share card made from its header shot.

## Motion (decided after many rounds)

- Work wall: plates develop one after another as their pictures load; a caption comes up with its own
  picture. Fades must not "blink in": slow enough to read as a develop.
- Opening a case from the work wall: the cover glides into the case header (View Transitions). One way
  only; going back is a plain crossing and the wall stands complete, scroll position restored.
- Between other pages: the new page appears and the old one fades. Never a load-in and a cross-fade
  together (that was the "double fade").
- Battery saving: the first visit measures frame pace; under about 40 fps every transition is skipped
  for that visit.
- Chrome prerenders pages; arrival logic must read its notes after `prerenderingchange`.

## The cover shoot (Blender)

Everything is in `_covers/` with its own README. Key points:

- The six covers are Blender scenes built by script (`scenes.py`, `studio.py`), Cycles on the CPU,
  `bpy` 5.3 in a virtualenv. Qualities: test, mid, final, blend (saves a `.blend` instead of rendering).
- Rules of the shoot (Carl's): device never covered; lies flat or stands against a surface; one flat
  wall behind it; large flat surfaces, not sculpture; light greys close in tone; focus on the screen;
  TrackMan is a projected picture with the launch monitor composited on the floor (`radar.py`).
- "Light in the room" (`PEOPLE=1`): soft daylight with an unseen cut-out casting a shadow. Carl wants
  it ambient and subtle, not literal: no recognisable people or hands, no sculptural leaf shapes.
  e-conomic: edge of shade on the wall. Donkey: soft round dapples. The Org: soft shade edge
  (spread 12). TV2: window light on the floor, same contrast in close-up and header. OK: plain sun
  from the top right, shadow in front, today's camera angle. TrackMan: none.
- Brightness is matched by dimming the room lamps, never by exposure (exposure dims the screens).
- The device must not cast a second hard shadow in the sun (TV2 fix: `sun_only_cut`).
- `masters/` holds every published render and `masters/blend/` every scene as a Blender file; update
  both whenever a picture is republished. `install_covers.py final` rebuilds all site images from them.
- Header shots are the same scene pulled back (`HEADER=1`, `PULL` table); the `--pull` values at the end
  of `css/styles.css` must match.

## Parked and rejected

- Parked: the front-page backdrop (hovering Work shows the cases full window, one still every 2.4 s,
  portrait steps out). Patch and instructions in `_covers/parked/`.
- Rejected: scattered thumbnails gathering around the cursor (too close to a friend's site); a Blender
  video backdrop ("too old-school"); a shadow of a person walking by on TrackMan.
