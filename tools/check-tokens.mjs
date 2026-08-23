/* Fails when the stylesheet uses a colour or a spacing value that is not a
   token, and when the two colour schemes come apart. This is the half of
   "keeping the design system true" that a document cannot do for you: the
   system page reflects whatever styles.css says, so it stays honest either
   way — this is what stops styles.css itself from quietly growing a seventh
   grey, a 13px padding, or a colour that only exists in daylight. */

import { readFileSync } from 'node:fs';

const css = readFileSync(new URL('../css/styles.css', import.meta.url), 'utf8');

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

// The two schemes are one palette. Every colour token exists in both, and a
// scheme may not introduce a name the other does not have.
const declarations = (block) =>
	Object.fromEntries([...block.matchAll(/(--[\w-]+):\s*([^;]+);/g)].map((m) => [m[1], m[2].trim()]));

const lineOf = (index) => css.slice(0, index).split('\n').length;

const darkAt = css.indexOf('@media (prefers-color-scheme: dark)');
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

if (problems.length === 0) {
	console.log(`ok — every colour and spacing value in styles.css is a token, and both schemes carry every colour (ramp: ${ramp.join(', ')}px)`);
	process.exit(0);
}

console.error(`${problems.length} value${problems.length === 1 ? '' : 's'} outside the system:\n`);
for (const p of problems) console.error(`  styles.css:${p.line}  ${p.kind}  ${p.value}  — ${p.fix}`);
console.error('\nEither use a token, or add the value to both schemes in :root and say so on the system page.');
process.exit(1);
