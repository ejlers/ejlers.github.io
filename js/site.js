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
   nothing, and a return to the page skips the whole thing.

   A prerendered page waits: the speculation rules let the browser build
   the next page before it is asked for, and a develop that played in
   that hidden window would be spent on nobody. First sight means seen. */
(() => {
	if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

	const develop = () => {
		try {
			const key = 'developed:' + location.pathname;
			if (sessionStorage.getItem(key)) return;
			sessionStorage.setItem(key, '1');
		} catch (err) {
			/* storage refused: develop anyway, at worst it plays again */
		}

		document.body.classList.add('develop');

		const waiting = document.querySelectorAll('.band + .band, .entry, .case, .cycle, .ledger__row');
		if (!('IntersectionObserver' in window)) {
			waiting.forEach((el) => el.classList.add('arrived'));
			return;
		}
		const seen = new IntersectionObserver((entries) => {
			/* everything sighted together develops top to bottom, one step apart */
			let step = 0;
			for (const entry of entries) {
				if (!entry.isIntersecting) continue;
				entry.target.style.setProperty('--arrive', (step++) * 80 + 'ms');
				entry.target.classList.add('arrived');
				seen.unobserve(entry.target);
			}
		}, { rootMargin: '0px 0px -10% 0px' });
		waiting.forEach((el) => seen.observe(el));
	};

	if (document.prerendering) {
		document.addEventListener('prerenderingchange', develop, { once: true });
	} else {
		develop();
	}
})();
