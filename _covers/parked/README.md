# Parked: the front page's backdrop

Pointing at the Work row on the front page puts the cases behind the page, full window, one still
after another every 2.4 seconds while the pointer stays. The portrait steps out, the page's ink turns
dark on the light shots, and the case's name stands on the left edge above the rows. Desk and hover
only; under reduced motion one case holds. Built and tried in November 2026, then parked by Carl.

Everything needed to finish it is in the repository:

- `front-backdrop.patch`: the code (stylesheet, page script, the front page's Work row, the system
  page's wording). It switches on only with `?preview` in the address; remove that line in `js/site.js`
  to switch it on for everyone.
- `img/work/<case>/front.webp` and `front-2400.webp`: the six front shots, already in place.
- `_covers/masters/*-far-header.*`: their finished renders; see the main guide for how they were made.

To pick it up again, from the repository root:

```bash
git apply _covers/parked/front-backdrop.patch
```

then `node tools/stamp.mjs` and `npm run check`.
