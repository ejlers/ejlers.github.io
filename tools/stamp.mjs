/* Stamps every page's own stylesheets and scripts with a short fingerprint
   of the file (styles.css?v=1a2b3c4d). A browser keeps a stylesheet for a
   while after it has fetched it, so without the stamp a page published a
   minute ago can arrive with yesterday's styles and script. With it, a
   changed file has a new address and is fetched fresh, and an unchanged
   one stays cached.

   node tools/stamp.mjs          writes the stamps
   node tools/stamp.mjs --check  fails if any stamp is missing or stale */

import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const checkOnly = process.argv.includes('--check');
const SKIP = new Set(['node_modules', '.git', 'tools']);

const pages = [];
const walk = (dir) => {
	for (const entry of readdirSync(dir, { withFileTypes: true })) {
		if (entry.name.startsWith('.') || SKIP.has(entry.name)) continue;
		const path = join(dir, entry.name);
		if (entry.isDirectory()) walk(path);
		else if (entry.name.endsWith('.html')) pages.push(path);
	}
};
walk(root);

const prints = new Map();
const print = (file) => {
	if (!prints.has(file)) prints.set(file, createHash('sha256').update(readFileSync(file)).digest('hex').slice(0, 8));
	return prints.get(file);
};

/* A local stylesheet or script: href or src, a path with no scheme or host,
   ending in .css or .js, with or without an earlier stamp. */
const REF = /\b(href|src)="((?![a-z][a-z0-9+.-]*:|\/\/)[^"?#]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"/g;

const stale = [];
for (const page of pages) {
	const html = readFileSync(page, 'utf8');
	const next = html.replace(REF, (whole, attr, path) => {
		const file = path.startsWith('/') ? join(root, path) : resolve(dirname(page), path);
		if (!existsSync(file)) return whole;
		const stamped = `${attr}="${path}?v=${print(file)}"`;
		if (stamped !== whole) stale.push(`${relative(root, page)}  ${path}`);
		return stamped;
	});
	if (next !== html && !checkOnly) writeFileSync(page, next);
}

if (checkOnly && stale.length) {
	console.error(`${stale.length} stamp(s) out of date. Run: node tools/stamp.mjs`);
	for (const line of stale) console.error('  ' + line);
	process.exit(1);
}
console.log(checkOnly ? 'ok: every page asks for the current stylesheets and scripts' : `stamped ${stale.length} reference(s) across ${pages.length} pages`);
