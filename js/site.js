/* The site has no interaction of its own left: a row is a link and a page
   is a page. All this file does is observe the arrival below. */

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
