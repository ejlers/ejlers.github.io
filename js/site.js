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

/* A case's header picture is fetched the moment a plate is pointed at or
   focused, so it is in hand by the time the plate is pressed and can make
   the trip to its header (see Crossing pages in the stylesheet). Only on a
   desk: below the columns the header uses the cut the plate already shows. */
(() => {
	const desk = window.matchMedia('(min-width: 1101px)');
	document.querySelectorAll('.plates .case').forEach((plate) => {
		const fetchHeader = () => {
			if (!desk.matches || plate.header) return;
			const at = new URL(plate.href).pathname.replace('/work/', '/img/work/');
			plate.header = new Image();
			plate.header.sizes = '100vw';
			plate.header.srcset = at + 'header-1600.jpg 1600w, ' + at + 'header-2400.jpg 2400w, ' + at + 'header.jpg 3200w';
		};
		plate.addEventListener('pointerenter', fetchHeader);
		plate.addEventListener('focus', fetchHeader);
	});
})();

/* The page develops each time it is opened. The body gets .develop and
   the arrival plays: ink settles, rules draw, marks come up — all of it
   CSS, all of it behind prefers-reduced-motion. Pieces below the window
   (bands, entries, work rows) wait for first sight and are marked .arrived
   as the reader reaches them; scrolling back replays nothing. Opening the
   page again does: by a link, a reload, or the back button, including
   when the browser hands back the page it kept instead of loading it.

   A prerendered page waits: the speculation rules let the browser build
   the next page before it is asked for, and a develop that played in
   that hidden window would be spent on nobody. First sight means seen. */
(() => {
	if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

	let sights = [];

	/* A case's picture travels between its plate on the work wall and the
	   header of its case (see Crossing pages in the stylesheet). A picture
	   that travels is already in hand at both ends, so neither end develops
	   it. Each page leaves a note of where the reader set out from and when;
	   the next page reads it once, and only a fresh one counts. */
	const HERE = location.pathname.replace(/index\.html$/, '');
	window.addEventListener('pagehide', () => {
		try { sessionStorage.setItem('crossing', HERE + ' ' + Date.now()); } catch (err) { /* no note, no harm */ }
	});
	const cameFrom = () => {
		try {
			const [path, at] = (sessionStorage.getItem('crossing') || '').split(' ');
			sessionStorage.removeItem('crossing');
			return path && Date.now() - Number(at) < 4000 ? path : '';
		} catch (err) {
			return '';
		}
	};
	const caseOf = (path) => (path.match(/\/work\/([a-z0-9]+)\/$/) || [])[1] || '';

	const develop = () => {
		sights.forEach((sight) => sight.disconnect());
		sights = [];

		/* which end of a travelling picture this page is, if either: the plate
		   on the wall the reader has come back to, or the header of the case
		   whose plate was just opened */
		const from = cameFrom();
		const landed = caseOf(from) && /\/work\/$/.test(HERE) ? document.querySelector('.case--' + caseOf(from))
			: /\/work\/$/.test(from) && caseOf(HERE) ? document.querySelector('.hero')
			: null;
		/* a header whose picture has not arrived made no trip (the page called
		   it off), so it develops like any other */
		const inHand = landed && (landed.matches('.case') || (landed.querySelector('img') || {}).complete);
		if (inHand) landed.classList.add('landed', 'arrived');

		document.body.classList.add('develop');

		const waiting = document.querySelectorAll('.band + .band, .entry, .cycle, .ledger__row');
		const plates = document.querySelectorAll('.case:not(.landed)');
		const hero = document.querySelector('.hero:not(.landed)');
		if (!('IntersectionObserver' in window)) {
			waiting.forEach((el) => el.classList.add('arrived'));
			plates.forEach((el) => el.classList.add('arrived'));
			if (hero) hero.classList.add('arrived');
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
			sights.push(sight);
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
		const BEAT = 360;
		const PATIENCE = 3000;
		const pause = (ms) => new Promise((done) => setTimeout(done, ms));
		const ready = (el) => {
			const img = el.querySelector('.case__cover img, .hero__cover img');
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
		/* a case's header is the top of its page: always in view, always first */
		if (hero) hang([hero]);

		const first = [];
		const later = [];
		plates.forEach((el) => {
			/* a plate already scrolled past is not on screen either: it waits
			   to be seen like the rest, and takes no beat from those that are */
			const box = el.getBoundingClientRect();
			(box.top < reach && box.bottom > 0 ? first : later).push(el);
		});
		hang(first);
		watch(later, touch ? '0px 0px 20% 0px' : '0px 0px 15% 0px', hang);
	};

	if (document.prerendering) {
		document.addEventListener('prerenderingchange', develop, { once: true });
	} else {
		develop();
	}

	/* The back button often shows the page the browser kept, finished, with
	   no script run. That is still the page being opened: clear what has
	   arrived and let it develop again. */
	window.addEventListener('pageshow', (event) => {
		if (!event.persisted) return;
		document.body.classList.remove('develop');
		document.querySelectorAll('.arrived').forEach((el) => {
			el.classList.remove('arrived', 'landed');
			el.style.removeProperty('--arrive');
		});
		void document.body.offsetWidth; /* the cleared state has to land before the arrival starts over */
		develop();
	});
})();
