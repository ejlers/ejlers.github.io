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
			plate.header.srcset = at + 'header-1600.webp 1600w, ' + at + 'header-2400.webp 2400w, ' + at + 'header.webp 3200w';
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

   One return is not an opening: the work wall, come back to from a case.
   The reader has just seen it, so it stands complete.

   A prerendered page waits: the speculation rules let the browser build
   the next page before it is asked for, and a develop that played in
   that hidden window would be spent on nobody. First sight means seen. */
(() => {
	if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

	let sights = [];

	/* A case's picture travels from its plate on the work wall into the
	   header of its case (see Crossing pages in the stylesheet). A picture
	   that has travelled is already in hand, so its header does not develop
	   it. Each page leaves a note of where the reader set out from and when;
	   the next page reads it once, and only a fresh one counts. */
	const HERE = location.pathname.replace(/index\.html$/, '');
	/* The note is left as early as the page knows the reader is going: at
	   the press on a link, again when the crossing is about to start, and
	   last when the page is hidden. Early matters, because a browser may
	   have built the next page already and hand it over at once. */
	const leaveNote = () => {
		try {
			sessionStorage.setItem('crossing', HERE + ' ' + Date.now());
			/* and where the wall stood, so a return finds it there
			   (work/index.html puts it back before the page is first shown) */
			if (/\/work\/$/.test(HERE)) sessionStorage.setItem('wall-at', String(Math.round(window.scrollY)));
		} catch (err) { /* no note, no harm */ }
	};
	document.addEventListener('click', (event) => {
		if (event.target.closest && event.target.closest('a[href]')) leaveNote();
	}, true);
	window.addEventListener('pageswap', leaveNote);
	window.addEventListener('pagehide', leaveNote);
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

	/* Where the reader has just come from, read once per arrival: when the
	   script first runs, or, on a page the browser built ahead of the press
	   (the speculation rules), when it is actually handed over, since until
	   then nobody has left anywhere; and again when the browser hands back
	   a page it kept. The work wall is put back where it was left first
	   (work/index.html), while the note still says where from. */
	let came = '';
	const arrive = () => {
		if (typeof window.putWallBack === 'function') window.putWallBack();
		came = cameFrom();
	};
	if (!document.prerendering) arrive();

	/* A page arrives in one of two ways, never both at once. It develops,
	   or it crosses softly from the page before. The soft crossing belongs
	   to the wall and its cases: a plate's picture travelling into its
	   header, and the wall standing complete on the way back. Every other
	   arrival develops, so there the crossing is called off and the page is
	   simply there to develop, as it is on a reload. The page being left
	   knows where the reader is going and the page arriving knows where
	   they came from; whichever of the two the browser lets speak calls it. */
	/* A device that cannot keep the frames coming (on battery saving, or
	   simply tired) gets the pages without the crossing: a travelling
	   picture that stutters is worse than none. Its pace is taken once per
	   visit, in a quiet moment after the first page has settled: the middle
	   frame of a short run. Under 40 frames a second, it is calm from then on. */
	const calm = () => { try { return sessionStorage.getItem('calm') === '1'; } catch (err) { return false; } };
	const takePace = () => {
		try { if (sessionStorage.getItem('calm') !== null) return; } catch (err) { return; }
		const gaps = [];
		let last = 0;
		const frame = (t) => {
			if (last) gaps.push(t - last);
			last = t;
			if (gaps.length < 24) { requestAnimationFrame(frame); return; }
			gaps.sort((x, y) => x - y);
			try { sessionStorage.setItem('calm', gaps[12] > 25 ? '1' : '0'); } catch (err) { /* no note, no harm */ }
		};
		setTimeout(() => { if (!document.hidden) requestAnimationFrame(frame); }, 1600);
	};
	if (document.readyState === 'complete') takePace(); else window.addEventListener('load', takePace, { once: true });

	const wallAndCase = (a, b) => (/\/work\/$/.test(a) && caseOf(b)) || (caseOf(a) && /\/work\/$/.test(b));
	window.addEventListener('pageswap', (event) => {
		if (!event.viewTransition || !event.activation || !event.activation.entry) return;
		const to = new URL(event.activation.entry.url).pathname.replace(/index\.html$/, '');
		if (calm() || !wallAndCase(HERE, to)) event.viewTransition.skipTransition();
	});
	window.addEventListener('pagereveal', (event) => {
		if (event.viewTransition && (calm() || (came && !wallAndCase(came, HERE)))) event.viewTransition.skipTransition();
	});

	const develop = () => {
		sights.forEach((sight) => sight.disconnect());
		sights = [];

		/* A picture travels one way, from its plate into the case's header, so
		   the only page that receives one is a case opened from the wall. Its
		   header is then already in hand and does not develop. A header whose
		   picture has not arrived made no trip (the page called it off), and
		   develops like any other. */
		const from = came;

		/* Coming back from a case, the wall is not arriving: the reader left it
		   a moment ago and has seen it. It is simply there, as they left it,
		   behind the page's own short crossing. */
		if (caseOf(from) && /\/work\/$/.test(HERE)) return;

		const landed = /\/work\/$/.test(from) && caseOf(HERE) ? document.querySelector('.hero') : null;
		if (landed && (landed.querySelector('img') || {}).complete) landed.classList.add('landed', 'arrived');

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
		document.addEventListener('prerenderingchange', () => { arrive(); develop(); }, { once: true });
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
		arrive();
		develop();
	});
})();
