/* The site has no interaction of its own left: a row is a link and a page
   is a page. What this file does is measure and observe — the canvas ground
   below, and the arrival at the bottom. */

/* The media canvas takes its ground from the pictures that move on it. The
   token says 217, but a video cannot promise a colour the way a PNG can:
   the value survives the trip through an encoder differently in every
   browser. So once the first loop has a frame, the page reads the corner
   of what was actually rendered and repaints the token to match. The still
   images sit on transparency, so everything shares whatever the answer is. */
const groundVideo = document.querySelector('.case-media video');

const takeGround = () => {
	try {
		const probe = document.createElement('canvas');
		probe.width = probe.height = 8;
		const ctx = probe.getContext('2d', { willReadFrequently: true });
		ctx.drawImage(groundVideo, 0, 0);
		const px = ctx.getImageData(2, 2, 1, 1).data;
		if (px[3] === 255) {
			document.documentElement.style.setProperty('--canvas', 'rgb(' + px[0] + ', ' + px[1] + ', ' + px[2] + ')');
		}
	} catch (err) {
		/* a browser that refuses the readback keeps the token's value */
	}
};

if (groundVideo) {
	/* the data may already be in by the time this runs, so ask first and
	   listen only if the answer is not there yet */
	if (groundVideo.readyState >= 2) takeGround();
	else groundVideo.addEventListener('loadeddata', takeGround, { once: true });
}

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
