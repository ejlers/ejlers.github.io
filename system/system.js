/* Everything numeric on this page is read from the live stylesheet at load —
   hex values, contrast ratios, the space ramp, page metrics and durations.
   Nothing here is typed in, so nothing here can quietly go stale. */

const root = getComputedStyle(document.documentElement);
const token = (name) => root.getPropertyValue(name).trim();

/* --- Both palettes, read out of the stylesheet ------------------------ */

/* getComputedStyle only ever knows the scheme in use, and this page has to
   show the one you are not looking at as well. So the values come from the
   sheet itself: the :root block, and the :root inside the dark media query.
   Still read live — nothing here is typed in, and neither is which of the two
   you are currently in. */

const SCHEMES = { light: {}, dark: {} };

function collect(rule, into) {
	if (rule.media) {
		if (/prefers-color-scheme:\s*dark/.test(rule.conditionText)) {
			for (const inner of rule.cssRules) collect(inner, SCHEMES.dark);
		}
		return;
	}
	if (rule.selectorText !== ':root') return;
	for (const name of rule.style) into[name] = rule.style.getPropertyValue(name).trim();
}

for (const sheet of document.styleSheets) {
	let rules;
	try {
		rules = sheet.cssRules;
	} catch {
		continue; /* a sheet from another origin */
	}
	for (const rule of rules) collect(rule, SCHEMES.light);
}

const CURRENT = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

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

/* Against the paper of its own scheme, never against white: the dark column
   is measured on dark paper, and the ladder has to come out the same. */
function contrastOnPaper(hex, paper) {
	const [a, b] = [luminance(hex), luminance(paper)].sort((x, y) => y - x);
	return (a + 0.05) / (b + 0.05);
}

/* --- Colour table ----------------------------------------------------- */

/* The threshold depends on the job: text needs 4.5:1, an interface mark
   needs 3:1, and a surface is not measured against itself at all. */
const COLOURS = [
	['--paper', 'Paper', 'surface', 'Every background. There is no second background. The device picks which of the two it is.'],
	['--ink', 'Ink', 'text', 'Primary text: names, body copy, anything read closely.'],
	['--ink-strong', 'Ink Strong', 'text', 'Row headers, open-state chevrons, secondary emphasis.'],
	['--ink-muted', 'Ink Muted', 'text', 'Secondary copy and links. Anything at 16px takes this or darker.'],
	['--grey', 'Grey', 'mark', 'Icons and interface marks only. Never text, because it does not reach 4.5:1.'],
	['--rule', 'Rule', 'surface', 'Hairlines. Never text, never an icon that means something.'],
	['--fill', 'Fill', 'surface', 'The one fill, for the grey button.'],
	['--hover', 'Hover', 'surface', 'The row under a pointer. Solid, like every surface here: nothing on the site is translucent.'],
	['--canvas', 'Canvas', 'surface', 'The ground case imagery sits on. The same value in both schemes, because a screenshot keeps its own light whatever the page does.']
];

const FLOOR = { text: 4.5, mark: 3 };

const colours = document.getElementById('colours');

/* One cell per scheme: the value, and what it measures on that scheme's own
   paper. The scheme you are in is inked, the other one recedes to muted. */
function cell(scheme, name, role) {
	const value = SCHEMES[scheme][name];
	if (!value) return '<span class="scheme"></span>';

	const floor = FLOOR[role];
	const measured = floor && value.startsWith('#')
		? contrastOnPaper(value, SCHEMES[scheme]['--paper'])
		: null;
	const fails = measured !== null && measured < floor;

	return `<span class="scheme"${scheme === CURRENT ? ' data-current' : ''}${fails ? ' data-fails' : ''}>`
		+ value + (measured === null ? '' : ' · ' + measured.toFixed(1) + ':1')
		+ '</span>';
}

for (const [name, label, role, job] of COLOURS) {
	const row = document.createElement('div');
	row.className = 'spec';
	row.innerHTML = `
		<span class="swatch-pair">
			<span class="swatch" style="background: ${SCHEMES.light[name]}"></span>
			<span class="swatch" style="background: ${SCHEMES.dark[name]}"></span>
		</span>
		<span>${label}</span>
		${cell('light', name, role)}
		${cell('dark', name, role)}
		<span class="spec__note">${job}</span>`;
	colours.append(row);
}

/* The head says which of the two you are reading in. */
for (const head of document.querySelectorAll('#colours [data-scheme]')) {
	head.toggleAttribute('data-current', head.dataset.scheme === CURRENT);
}

/* --- Typeface, read rather than restated ------------------------------ */

document.getElementById('typeface').textContent =
	getComputedStyle(document.body).fontFamily.replaceAll('"', '');

/* --- The space ramp --------------------------------------------------- */

const RAMP = [
	['--s1', 'Hairline offsets and optical nudges. Rare; not a layout value.'],
	['--s2', 'Gap inside a single element: icon to label, dot to text.'],
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
	['--term-col', 'The first column, everywhere it appears: index terms and the labels\' column, so bylines and media start on the same line down a page.']
];

const metrics = document.getElementById('page-metrics');

for (const [name, note] of METRICS) {
	const block = document.createElement('div');
	block.className = 'block';
	block.innerHTML = `<span class="block__title">${token(name)}</span><span class="block__body">${note}</span>`;
	metrics.append(block);
}

/* --- The grid, measured off a real band -------------------------------- */

/* A band built and thrown away rather than a twelve typed in here. The ruler
   under the table is drawn from the same reading, so the page cannot show a
   grid the stylesheet is not using. */

const probe = document.body.appendChild(Object.assign(document.createElement('div'), { className: 'band' }));
probe.style.cssText = 'position: absolute; left: -9999px; width: 600px; visibility: hidden';

const bandStyle = getComputedStyle(probe);
const columns = bandStyle.gridTemplateColumns.split(' ').length;
const rhythm = bandStyle.paddingTop;

probe.remove();

/* On a phone the band really is one column, and saying twelve there would
   be the page describing a grid it is not currently using. */
document.getElementById('grid-cols').textContent = columns === 1 ? '1 · collapsed' : columns;
document.getElementById('grid-gutter').textContent = token('--gutter');
document.getElementById('grid-rhythm').textContent = rhythm;

const ruler = document.getElementById('ruler');
ruler.style.gridTemplateColumns = `repeat(${columns}, minmax(0, 1fr))`;
for (let i = 0; i < columns; i++) ruler.append(document.createElement('span'));

/* --- Motion ----------------------------------------------------------- */

const MOTION = [
	['--t-open', 'Menu opening', 'opacity, ease-out', 'Nothing in the menu came out of the heading and nothing is left behind it, so there is no parentage to show. It covers, and covering fades.'],
	['--t-close', 'Menu closing', 'opacity, ease-in', 'Put away, not deleted. Faster than opening, because nobody watches something leave.'],
	['--t-confirm', 'Hover fill', 'background-color, ease', 'The whole row is the target, not just the words in it. Behind (hover: hover), like every hover here: a touch screen has no pointer to leave, so an unguarded one stays lit on whatever was tapped last.'],
	['--t-develop', 'The develop', 'color, hairlines and grey, ease', 'The one arrival. The address settles, the claim follows, rules draw left to right, settling type comes up as it takes its weight and the marks come up from grey: once per visit, on first sight, and the page never moves while it happens.'],
	['--t-confirm', 'The arrow reaches', 'stroke-dashoffset, ease', 'On a pointer, an index row\'s arrow leans into its direction. The head holds the row\'s very edge, because nothing crosses an edge; the shaft grows one small step back toward the words.'],
	['--t-open', 'Crossing pages', 'view-transition, browsers that can', 'Navigation is a soft crossing, not a reload. The name and the portrait hold still while the rest fades, because they exist on both sides; the next page is often prerendered on hover, so the crossing starts the instant it is asked for.']
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
const tocList = toc.appendChild(Object.assign(document.createElement('div'), { className: 'toc__list' }));
const sections = [...document.querySelectorAll('.doc .section')];

const slug = (text) => text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

for (const section of sections) {
	const name = section.querySelector('.section__heading').textContent.trim();
	section.id = slug(name);

	const item = document.createElement('a');
	item.className = 'toc__item';
	item.href = '#' + section.id;
	item.append(Object.assign(document.createElement('span'), { className: 'toc__tick' }));
	item.append(Object.assign(document.createElement('span'), { textContent: name }));
	tocList.append(item);
}

/* --- Where you are: one pass, one rule ---------------------------------- */

/* Both marks answer the same question — which section is at the top of the
   window — so they are one loop over one measurement rather than two
   mechanisms that can disagree. A section becomes current once its top
   crosses --s8: the gap between sections, and the line navigating to one
   lands on, so arriving marks it at once. Its heading shrinks a little
   later, when the section itself passes the edge.

   A plain scroll check rather than observers: the heading holds one height
   whatever size its type is, so its own state can never move the thing being
   measured. Twelve rect reads per scroll on a page that never reflows is
   cheaper than the machinery to avoid them. */

const items = [...tocList.children];
const landing = parseFloat(token('--s8'));

function mark() {
	const tops = sections.map((section) => section.getBoundingClientRect().top);

	let current = 0;
	tops.forEach((top, i) => { if (top <= landing) current = i; });

	sections.forEach((section, i) => {
		const heading = section.querySelector('.section__heading');
		heading.classList.toggle('is-stuck', tops[i] < 0);
		heading.classList.toggle('is-current', i === current);
	});

	items.forEach((item, i) => item.classList.toggle('is-current', i === current));
}

addEventListener('scroll', mark, { passive: true });
mark();

/* --- On a phone the sticky heading is the menu --------------------------- */

/* No hamburger and no second vocabulary: the heading of the section you are
   in sits at the top of the window already, so it takes the chevron, renames
   itself Menu and covers the page with the contents. Choosing an entry closes
   it and scrolls there.

   Only that one heading is the menu, and only ever one at a time. Opening it
   moves nothing: the page does not scroll and the bar stays where it was. */

const narrow = matchMedia('(max-width: 1100px)');

for (const section of sections) {
	const heading = section.querySelector('.section__heading');

	/* Two words in one box: the section's own name, and Menu for while the
	   menu is open. Built here rather than in the markup so a section is still
	   written as a heading and nothing else. */
	const title = document.createElement('span');
	title.className = 'section__title';
	title.append(Object.assign(document.createElement('span'), {
		className: 'section__name',
		textContent: heading.textContent.trim()
	}));
	const word = Object.assign(document.createElement('span'), { className: 'section__menu', textContent: 'Menu' });
	word.setAttribute('aria-hidden', 'true');
	title.append(word);
	heading.textContent = '';
	heading.append(title);

	const chevron = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
	chevron.setAttribute('class', 'chevron');
	/* Its own size, not the stylesheet's: an SVG with neither renders at the
	   width of its container, so a late or stale sheet turns it into a poster. */
	chevron.setAttribute('width', '20');
	chevron.setAttribute('height', '20');
	chevron.setAttribute('aria-hidden', 'true');
	chevron.setAttribute('focusable', 'false');
	const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
	use.setAttribute('href', '#i-chevron');
	chevron.append(use);
	heading.append(chevron);

	heading.addEventListener('click', () => {
		if (!narrow.matches || !heading.classList.contains('is-current')) return;
		const opening = !document.body.classList.contains('menu-open');
		/* The panel covers the screen; --menu-top only tells its list where
		   this heading ends. A custom property rather than an inline style,
		   so it cannot leak into the sticky rail on a wide screen. */
		if (opening) {
			toc.style.setProperty('--menu-top', Math.round(heading.getBoundingClientRect().bottom) + 'px');
			toc.scrollTop = 0;
		}
		document.body.classList.toggle('menu-open', opening);
	});
}

tocList.addEventListener('click', (event) => {
	if (event.target.closest('.toc__item')) document.body.classList.remove('menu-open');
});

narrow.addEventListener('change', () => document.body.classList.remove('menu-open'));
