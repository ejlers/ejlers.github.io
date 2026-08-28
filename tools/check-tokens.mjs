/* Fails when the stylesheet uses a colour or a spacing value that is not a
   token, and when the two colour schemes come apart. This is the half of
   "keeping the design system true" that a document cannot do for you: the
   system page reflects whatever styles.css says, so it stays honest either
   way — this is what stops styles.css itself from quietly growing a seventh
   grey, a 13px padding, or a colour that only exists in daylight. */

import { readFileSync } from 'node:fs';

/* Comments are prose about the rules, not the rules — a sentence explaining
   why :hover is guarded is not an unguarded hover. Blank them rather than
   remove them, so every offset and line number below still points at the
   real file. */
const css = readFileSync(new URL('../css/styles.css', import.meta.url), 'utf8')
	.replace(/\/\*[\s\S]*?\*\//g, (comment) => comment.replace(/[^\n]/g, ' '));

/* Every :root block declares tokens — the base set, the dark scheme and the
   reduced-motion durations — so all of them are exempt and everything else
   is the body this checks. */
const blocks = [...css.matchAll(/:root \{/g)].map((m) => [m.index, css.indexOf('}', m.index)]);
if (blocks.length === 0) throw new Error('no :root token block found');

const tokenBlock = blocks.map(([a, b]) => css.slice(a, b)).join('\n');

let body = '';
let cut = 0;
for (const [a, b] of blocks) {
	body += css.slice(cut, a);
	cut = b;
}
body += css.slice(cut);

const ramp = [...tokenBlock.matchAll(/--s\d:\s*(\d+)px/g)].map((m) => Number(m[1]));
const allowedSpace = new Set([0, ...ramp]);

const problems = [];

// Colours outside the token block.
for (const m of body.matchAll(/#[0-9a-fA-F]{3,8}\b/g)) {
	problems.push({
		kind: 'colour',
		value: m[0],
		line: body.slice(0, m.index).split('\n').length,
		fix: 'use a token from :root'
	});
}

// Spacing off the ramp. Only padding / margin / gap — widths and hit targets
// are sized by what they hold, not by the ramp.
for (const m of body.matchAll(/\b(padding|margin|gap|row-gap|column-gap)(-top|-right|-bottom|-left|-inline|-block)?:\s*([^;{}]+);/g)) {
	if (/var\(|calc\(|auto|%/.test(m[3])) continue;
	for (const part of m[3].trim().split(/\s+/)) {
		const px = /^(-?\d+(?:\.\d+)?)px$/.exec(part);
		if (!px) continue;
		if (allowedSpace.has(Math.abs(Number(px[1])))) continue;
		problems.push({
			kind: 'space',
			value: `${m[1]}${m[2] || ''}: ${part}`,
			line: body.slice(0, m.index).split('\n').length,
			fix: `nearest step is ${ramp.reduce((b, v) => Math.abs(v - Math.abs(Number(px[1]))) < Math.abs(b - Math.abs(Number(px[1]))) ? v : b)}px`
		});
	}
}

// Hover is a pointer idea. Unguarded, a touch browser leaves :hover applied to
// whatever was tapped last, so the row you opened stays lit.
const guarded = [];
for (const m of css.matchAll(/@media \(hover: hover\)\s*\{/g)) {
	let depth = 1;
	let i = m.index + m[0].length;
	while (depth > 0) depth += css[i++] === '{' ? 1 : css[i - 1] === '}' ? -1 : 0;
	guarded.push([m.index, i]);
}

for (const m of css.matchAll(/:hover\b/g)) {
	if (guarded.some(([a, b]) => m.index > a && m.index < b)) continue;
	problems.push({
		kind: 'hover',
		value: css.slice(css.lastIndexOf('\n', m.index) + 1, css.indexOf('{', m.index)).trim(),
		line: css.slice(0, m.index).split('\n').length,
		fix: 'put it behind @media (hover: hover) — a touch screen has no pointer to leave'
	});
}

// The two schemes are one palette. Every colour token exists in both, and a
// scheme may not introduce a name the other does not have.
const declarations = (block) =>
	Object.fromEntries([...block.matchAll(/(--[\w-]+):\s*([^;]+);/g)].map((m) => [m[1], m[2].trim()]));

const lineOf = (index) => css.slice(0, index).split('\n').length;

const darkAt = css.search(/@media (?:screen and )?\(prefers-color-scheme: dark\)/);
const darkPair = darkAt === -1 ? null : blocks.find(([a]) => a > darkAt);

if (!darkPair) {
	problems.push({
		kind: 'scheme',
		value: 'no dark scheme',
		line: 1,
		fix: 'colour is defined in two schemes; :root inside @media (prefers-color-scheme: dark) is missing'
	});
} else {
	const light = declarations(css.slice(...blocks[0]));
	const dark = declarations(css.slice(...darkPair));
	const isColour = (value) => /^(#|rgba?\()/.test(value);

	for (const [name, value] of Object.entries(light)) {
		if (!isColour(value) || name in dark) continue;
		problems.push({
			kind: 'scheme',
			value: name,
			line: lineOf(blocks[0][0] + css.slice(...blocks[0]).indexOf(name)),
			fix: 'a colour token needs a value in both schemes'
		});
	}

	for (const name of Object.keys(dark)) {
		if (name in light) continue;
		problems.push({
			kind: 'scheme',
			value: name,
			line: lineOf(darkPair[0] + css.slice(...darkPair).indexOf(name)),
			fix: 'a scheme may not introduce a token the other one does not have'
		});
	}
}

// No long dashes in anything a reader sees. An em dash is a sentence that has
// not decided where it ends; the rule is to rewrite it, not to swap it for a
// shorter dash. Comments are exempt: they are notes to whoever is reading the
// file, not text on a page.
const stripJs = (src) =>
	src.replace(/\/\*[\s\S]*?\*\//g, (c) => c.replace(/[^\n]/g, ' '))
	   .replace(/(^|[^:])\/\/[^\n]*/g, (m, p) => p + ' '.repeat(m.length - p.length));

const PAGES = ['../index.html', '../work/index.html', '../work/economic/index.html', '../work/theorg/index.html', '../work/trackman/index.html', '../work/donkey/index.html', '../work/tv2/index.html', '../work/ok/index.html', '../cv/index.html', '../system/index.html', '../404.html', '../notes/index.html', '../notes/building-to-learn/index.html', '../notes/nothing-is-written-twice/index.html'];
const dashes = /[\u2014\u2013]|&#821[12];|&[mn]dash;/g;

for (const rel of [...PAGES, '../system/system.js']) {
	let text;
	try {
		text = readFileSync(new URL(rel, import.meta.url), 'utf8');
	} catch {
		continue;
	}
	if (rel.endsWith('.js')) text = stripJs(text);

	for (const m of text.matchAll(dashes)) {
		const line = text.slice(0, m.index).split('\n').length;
		const from = text.lastIndexOf('\n', m.index) + 1;
		problems.push({
			kind: 'dash',
			value: text.slice(Math.max(from, m.index - 34), m.index + 34).replace(/\s+/g, ' ').trim(),
			line,
			file: rel.replace('../', ''),
			fix: 'rewrite the sentence, a dash is not a decision'
		});
	}
}

if (problems.length === 0) {
	console.log(`ok: every colour and spacing value in styles.css is a token, both schemes carry every colour, every hover is guarded, and no page uses a long dash (ramp: ${ramp.join(', ')}px)`);
	process.exit(0);
}

console.error(`${problems.length} value${problems.length === 1 ? '' : 's'} outside the system:\n`);
for (const p of problems) console.error(`  ${p.file ?? 'styles.css'}:${p.line}  ${p.kind}  ${p.value}  ${p.fix}`);
console.error('\nEither use a token, or add the value to both schemes in :root and say so on the system page.');
process.exit(1);
