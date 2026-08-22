/* Fails when the stylesheet uses a colour or a spacing value that is not a
   token. This is the half of "keeping the design system true" that a
   document cannot do for you: the system page reflects whatever styles.css
   says, so it stays honest either way — this is what stops styles.css
   itself from quietly growing a seventh grey or a 13px padding. */

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

if (problems.length === 0) {
	console.log(`ok — every colour and spacing value in styles.css is a token (ramp: ${ramp.join(', ')}px)`);
	process.exit(0);
}

console.error(`${problems.length} value${problems.length === 1 ? '' : 's'} outside the system:\n`);
for (const p of problems) console.error(`  styles.css:${p.line}  ${p.kind}  ${p.value}  — ${p.fix}`);
console.error('\nEither use a token, or add the value to :root and say so on the system page.');
process.exit(1);
