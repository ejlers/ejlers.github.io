/* The site has almost no interaction of its own left: a row is a link and
   a page is a page. What remains here is one courtesy and one observer. */

/* The clips are the only motion on the site that runs without being asked.
   A reader who asked for reduced motion gets them still, standing on their
   first frame; any reader can press one to hold it and press again to let
   it run: the clip itself is the control, no chrome added. */
(() => {
	const clips = document.querySelectorAll('.case-media video');
	if (!clips.length) return;

	const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	clips.forEach((clip) => {
		if (still) {
			clip.removeAttribute('autoplay');
			clip.pause();
		}
		clip.setAttribute('tabindex', '0');
		clip.setAttribute('role', 'button');
		clip.setAttribute('aria-label', 'Pause or resume the clip');
		const toggle = () => { if (clip.paused) clip.play(); else clip.pause(); };
		clip.addEventListener('click', toggle);
		clip.addEventListener('keydown', (e) => {
			if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); toggle(); }
		});
	});
})();

/* The page develops, once. On a path's first view this visit, the body
   gets .develop and the arrival plays: ink settles, rules draw, marks come
   up — all of it CSS, all of it behind prefers-reduced-motion. Pieces
   below the window (bands, entries, work rows) wait for first sight and
   are marked .arrived as the reader reaches them; scrolling back replays
   nothing, and a return to the page skips the whole thing. A reload is a new visit.

   A prerendered page waits: the speculation rules let the browser build
   the next page before it is asked for, and a develop that played in
   that hidden window would be spent on nobody. First sight means seen. */
(() => {
	if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

	const develop = () => {
		try {
			const key = 'developed:' + location.pathname;
			/* a reload asks to see the page arrive again; a return by a link or
			   the back button does not */
			const nav = performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
			if (sessionStorage.getItem(key) && !(nav && nav.type === 'reload')) return;
			sessionStorage.setItem(key, '1');
		} catch (err) {
			/* storage refused: develop anyway, at worst it plays again */
		}

		document.body.classList.add('develop');

		const waiting = document.querySelectorAll('.band + .band, .entry, .cycle, .ledger__row');
		const plates = document.querySelectorAll('.case');
		if (!('IntersectionObserver' in window)) {
			waiting.forEach((el) => el.classList.add('arrived'));
			plates.forEach((el) => el.classList.add('arrived'));
			return;
		}
		/* First sight is the moment a piece enters the window, not a step
		   inside it: a phone shows the page under its own toolbar, and a piece
		   held back there reads as a page that has ended. A plate is a large
		   picture, so it starts a little before the edge and is under way by
		   the time it is looked at. */
		const watch = (pieces, margin, sighted) => {
			const sight = new IntersectionObserver((entries, seen) => {
				const now = [];
				for (const entry of entries) {
					if (!entry.isIntersecting) continue;
					now.push(entry.target);
					seen.unobserve(entry.target);
				}
				if (now.length) sighted(now);
			}, { rootMargin: margin });
			pieces.forEach((el) => sight.observe(el));
		};

		/* everything sighted together develops top to bottom, one step apart */
		watch(waiting, '0px', (pieces) => pieces.forEach((el, step) => {
			el.style.setProperty('--arrive', step * 80 + 'ms');
			el.classList.add('arrived');
		}));

		/* A plate develops when its picture is ready, never before: a fade
		   spent on an empty frame leaves the picture to pop in afterwards.
		   And plates develop in a line, each a clear beat after the one above
		   it, so a wall of them reads as arriving one by one. A picture that
		   takes too long is not waited for. */
		const BEAT = 220;
		const PATIENCE = 3000;
		const pause = (ms) => new Promise((done) => setTimeout(done, ms));
		const ready = (el) => {
			const img = el.querySelector('.case__cover img');
			if (!img) return Promise.resolve();
			img.loading = 'eager';
			const loaded = img.complete ? Promise.resolve() : new Promise((done) => {
				img.addEventListener('load', done, { once: true });
				img.addEventListener('error', done, { once: true });
			});
			const decoded = loaded.then(() => (img.decode ? img.decode().catch(() => {}) : null));
			return Promise.race([decoded, pause(PATIENCE)]);
		};
		let line = Promise.resolve();
		const hang = (pieces) => pieces.forEach((el) => {
			const picture = ready(el);
			line = Promise.all([line, picture]).then(() => {
				el.classList.add('arrived');
				return pause(BEAT);
			});
		});

		/* A touch screen draws the page under the browser's own bars, so what
		   is on screen at the start reaches further than the window it
		   reports, and it may report nothing more until a finger moves. So
		   there the first plates are measured against the whole screen and
		   develop at once; the rest are watched, from further out. */
		const touch = window.matchMedia('(pointer: coarse)').matches;
		const reach = touch ? Math.max(window.innerHeight, window.screen.height) : 0;
		const first = [];
		const later = [];
		plates.forEach((el) => (el.getBoundingClientRect().top < reach ? first : later).push(el));
		hang(first);
		watch(later, touch ? '0px 0px 20% 0px' : '0px 0px 15% 0px', hang);
	};

	if (document.prerendering) {
		document.addEventListener('prerenderingchange', develop, { once: true });
	} else {
		develop();
	}
})();
