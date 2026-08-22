/* Everything numeric on this page is read from the live stylesheet at load —
   hex values, contrast ratios, the space ramp, page metrics and durations.
   Nothing here is typed in, so nothing here can quietly go stale. */

const root = getComputedStyle(document.documentElement);
const token = (name) => root.getPropertyValue(name).trim();

/* --- Contrast, computed rather than remembered ----------------------- */

function channel(c) {
	c /= 255;
	return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function luminance(hex) {
	const m = hex.replace('#', '');
	const full = m.length === 3 ? m.split('').map((c) => c + c).join('') : m;
	const [r, g, b] = [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16));
	return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

function contrastOnWhite(hex) {
	return 1.05 / (luminance(hex) + 0.05);
}

/* --- Colour table ----------------------------------------------------- */

/* The threshold depends on the job: text needs 4.5:1, an interface mark
   needs 3:1, and a surface is not measured against itself at all. */
const COLOURS = [
	['--paper', 'Paper', 'surface', 'Every background. There is no second background.'],
	['--ink', 'Ink', 'text', 'Primary text — names, body copy, anything read closely.'],
	['--ink-strong', 'Ink Strong', 'text', 'Row headers, open-state chevrons, secondary emphasis.'],
	['--ink-muted', 'Ink Muted', 'text', 'Secondary copy and links. Anything at 16px takes this or darker.'],
	['--grey', 'Grey', 'mark', 'Icons and interface marks only. Never text — it does not reach 4.5:1.'],
	['--rule', 'Rule', 'surface', 'Hairlines. Never text, never an icon that means something.'],
	['--fill', 'Fill', 'surface', 'The one fill, for the grey button.'],
	['--veil', 'Veil', 'surface', 'Sticky headers over scrolling content, with a 5px blur. The only depth cue.']
];

const FLOOR = { text: 4.5, mark: 3 };

const colours = document.getElementById('colours');

for (const [name, label, role, job] of COLOURS) {
	const value = token(name);
	const floor = FLOOR[role];
	const measured = floor && value.startsWith('#') ? contrastOnWhite(value) : null;
	const fails = measured !== null && measured < floor;

	const row = document.createElement('div');
	row.className = 'spec';
	row.innerHTML = `
		<span><span class="swatch" style="background: var(${name})"></span></span>
		<span>${label}</span>
		<span class="spec__value">${value}</span>
		<span class="ratio"${fails ? ' data-fails' : ''}>${measured === null ? '—' : measured.toFixed(1) + ':1'}</span>
		<span class="spec__note">${job}</span>`;
	colours.append(row);
}

/* --- The space ramp --------------------------------------------------- */

const RAMP = [
	['--s1', 'Hairline offsets and optical nudges. Rare; not a layout value.'],
	['--s2', 'Gap inside a single element — icon to label, dot to text.'],
	['--s3', 'Row padding, vertical. The list rhythm.'],
	['--s4', 'Paragraph spacing, and the page inset.'],
	['--s5', 'Drawer inset, gap between grouped blocks.'],
	['--s6', 'Between grouped blocks that need more air.'],
	['--s7', 'Column gap, section break.'],
	['--s8', 'Page top, major section break.']
];

const ramp = document.getElementById('ramp');

for (const [name, use] of RAMP) {
	const row = document.createElement('div');
	row.className = 'spec';
	row.style.gridTemplateColumns = '90px 150px minmax(0, 1fr)';
	row.innerHTML = `
		<span>${token(name)}</span>
		<span><span class="ramp-bar" style="width: var(${name})"></span></span>
		<span class="spec__note">${use}</span>`;
	ramp.append(row);
}

/* --- Page metrics ----------------------------------------------------- */

const METRICS = [
	['--page-x', 'The page inset, and the only horizontal spacing there is. Held once, at the page level.'],
	['--page-max', 'The widest the content ever gets. Beyond it the page centres.'],
	['--measure', 'Reading measure. Never wider, whatever the viewport.'],
	['--drawer-text', 'The drawer text column. Fixed, with the media taking the rest.']
];

const metrics = document.getElementById('page-metrics');

for (const [name, note] of METRICS) {
	const block = document.createElement('div');
	block.className = 'block';
	block.innerHTML = `<span class="block__title">${token(name)}</span><span class="block__body">${note}</span>`;
	metrics.append(block);
}

/* --- Motion ----------------------------------------------------------- */

const MOTION = [
	['--t-open', 'Drawer opening', 'grid-template-rows 0fr to 1fr, ease-out', 'This content belongs to that row, and it came from there. A fade would lose the parentage — the unfold is the sentence.'],
	['--t-close', 'Drawer closing', 'grid-template-rows 1fr to 0fr, ease-in', 'Put away, not deleted. Faster than opening, because nobody watches something leave.'],
	['--t-confirm', 'Chevron', 'transform, ease', 'I heard you, and this row is now open. It confirms rather than reveals, so it finishes long before the drawer.'],
	['--t-confirm', 'Hover veil', 'background-color, ease', 'The whole row is the target, not just the words in it.']
];

const motion = document.getElementById('motion');

for (const [name, label, spec, says] of MOTION) {
	const row = document.createElement('div');
	row.className = 'spec';
	row.innerHTML = `
		<span>${label}</span>
		<span class="spec__value">${token(name)} · ${spec}</span>
		<span class="spec__note">${says}</span>`;
	motion.append(row);
}

const scroll = document.createElement('div');
scroll.className = 'spec';
scroll.innerHTML = `
	<span>Scroll to the project</span>
	<span class="spec__value">scrollIntoView, block start</span>
	<span class="spec__note">You start at the first line of what you opened, not wherever its row happened to sit. A decision about where reading begins, not a rescue for a displaced click.</span>`;
motion.append(scroll);

/* --- Contents ---------------------------------------------------------- */

/* Built from the sections on the page rather than kept as a second list,
   so a new section cannot be missing from the contents. */

const toc = document.getElementById('toc');
const sections = [...document.querySelectorAll('.doc .section')];

for (const section of sections) {
	const heading = section.querySelector('.section__heading');
	const no = heading.querySelector('.section__no').textContent.trim();
	const name = heading.textContent.replace(no, '').trim();
	section.id = 's' + no;

	const item = document.createElement('a');
	item.className = 'toc__item';
	item.href = '#s' + no;
	item.append(Object.assign(document.createElement('span'), { className: 'toc__no', textContent: no }));
	item.append(Object.assign(document.createElement('span'), { textContent: name }));
	toc.append(item);
}

/* Mark the section being read: the first one still overlapping the top
   quarter of the window. */
const items = [...toc.children];
const onScreen = new Set();

const watcher = new IntersectionObserver((entries) => {
	for (const entry of entries) {
		if (entry.isIntersecting) onScreen.add(entry.target);
		else onScreen.delete(entry.target);
	}
	const current = sections.find((section) => onScreen.has(section)) ?? sections[0];
	items.forEach((item, i) => item.classList.toggle('is-current', sections[i] === current));
}, { rootMargin: '0px 0px -75% 0px' });

sections.forEach((section) => watcher.observe(section));
