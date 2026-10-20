/* EVA, e-conomic's assistant, drawn live. Her mark is the e-conomic logo
   set in motion: five circles, fused by a blur and a threshold, that the
   page redraws every frame. Twelve arrangements of the same five points:
   the pentagon she rests at and returns to, and eleven constellations a
   thought is drawn from.

   A mark is an <svg data-eva="…"> holding five circles. The markup carries
   each circle's resting place, so without this script the mark simply
   stands. With it, three kinds move for as long as the page is open:
     hero   at rest a slow turn; every few seconds a thought: the circles
            gather to a point, pass through six to eight constellations at
            a varying pace, and settle home.
     rest   the slow turn and nothing else.
     think  constant regrouping, a new constellation every half second or
            so, never settling.
   Like the clips, a mark is its own control: press to hold, press again to
   let it run. A mark inside a link is not a control; the link is. Under
   prefers-reduced-motion every mark stands where its markup put it. */
(() => {
	const POOL = [
		[[50, 14, 11], [84, 39, 11], [71, 79, 11], [29, 79, 11], [16, 39, 11]],
		[[30, 30, 16], [45, 48, 11], [60, 66, 8], [75, 22, 10], [14, 80, 8]],
		[[58, 32, 16], [42, 22, 10], [28, 58, 9], [78, 55, 8], [55, 82, 11]],
		[[35, 22, 16], [55, 28, 11], [52, 68, 9], [18, 55, 8], [80, 75, 11]],
		[[62, 22, 16], [58, 44, 11], [50, 66, 8], [82, 82, 8], [18, 76, 8]],
		[[45, 22, 16], [52, 42, 11], [60, 60, 9], [22, 72, 11], [78, 30, 9]],
		[[65, 22, 16], [50, 36, 10], [40, 54, 8], [50, 72, 6], [80, 80, 6]],
		[[30, 70, 16], [50, 80, 12], [65, 65, 10], [75, 25, 8], [30, 20, 8]],
		[[60, 25, 16], [70, 45, 11], [55, 55, 9], [20, 30, 7], [25, 80, 7]],
		[[35, 25, 16], [55, 22, 10], [45, 42, 8], [75, 65, 11], [22, 75, 8]],
		[[18, 28, 9], [55, 18, 11], [60, 50, 10], [78, 60, 14], [28, 80, 7]],
		[[40, 22, 14], [25, 40, 11], [40, 58, 10], [70, 50, 8], [85, 75, 8]]
	];
	const HOME = POOL[0];
	const GATHER = [[50, 50, 11], [50, 50, 11], [50, 50, 11], [50, 50, 11], [50, 50, 11]];

	const marks = document.querySelectorAll('svg[data-eva]');
	if (!marks.length) return;
	if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

	/* cubic-bezier(0.4, 0, 0.2, 1), solved for x = t: the mark's own easing,
	   kept with the mark rather than taken from the site's two keywords. */
	const bezier = (p1x, p1y, p2x, p2y) => {
		const cx = 3 * p1x, bx = 3 * (p2x - p1x) - cx, ax = 1 - cx - bx;
		const cy = 3 * p1y, by = 3 * (p2y - p1y) - cy, ay = 1 - cy - by;
		const sx = (t) => ((ax * t + bx) * t + cx) * t;
		const sy = (t) => ((ay * t + by) * t + cy) * t;
		const dx = (t) => (3 * ax * t + 2 * bx) * t + cx;
		return (x) => {
			let t = x;
			for (let i = 0; i < 8; i++) {
				const e = sx(t) - x;
				if (Math.abs(e) < 1e-6) break;
				const d = dx(t);
				if (Math.abs(d) < 1e-6) break;
				t -= e / d;
			}
			return sy(Math.min(1, Math.max(0, t)));
		};
	};
	const ease = bezier(0.4, 0, 0.2, 1);
	const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
	const rand = (a, b) => Math.floor(a + Math.random() * (b - a + 1));

	/* A constellation is never repeated while it is still fresh in the eye. */
	const picker = () => {
		let used = {};
		let last = 0;
		return () => {
			const available = [];
			for (let j = 1; j < POOL.length; j++) if (!used[j] && j !== last) available.push(j);
			const p = available[Math.floor(Math.random() * available.length)];
			used[p] = true;
			if (Object.keys(used).length >= POOL.length - 3) used = {};
			last = p;
			return POOL[p];
		};
	};

	class Mark {
		constructor(svg) {
			this.svg = svg;
			this.kind = svg.dataset.eva;
			this.group = svg.querySelector('g');
			this.circles = [...svg.querySelectorAll('circle')];
			this.cur = (this.kind === 'think' ? POOL[6] : HOME).map((p) => p.slice());
			this.from = null;
			this.to = null;
			this.t0 = 0;
			this.dur = 0;
			this.angle = 0;
			this.spin = this.kind !== 'think';
			this.held = false;
			this.alive = true;
			this.pick = picker();
			this.apply();
			if (!svg.closest('a')) this.control();
			this.run();
		}

		/* The mark is the control, no chrome added: the clips' own pattern. */
		control() {
			const svg = this.svg;
			svg.setAttribute('tabindex', '0');
			svg.setAttribute('role', 'button');
			svg.setAttribute('aria-label', 'Hold EVA, or let her run');
			const toggle = () => { this.held = !this.held; };
			svg.addEventListener('click', toggle);
			svg.addEventListener('keydown', (e) => {
				if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); toggle(); }
			});
		}

		go(shape, dur) {
			this.from = this.cur.map((p) => p.slice());
			this.to = shape;
			this.t0 = performance.now();
			this.dur = dur;
		}

		tick(now, dt) {
			if (this.held) {
				this.t0 += dt;
			} else {
				if (this.to) {
					const k = this.dur ? Math.min(1, (now - this.t0) / this.dur) : 1;
					const e = ease(k);
					this.cur = this.from.map((p, i) => p.map((v, j) => v + (this.to[i][j] - v) * e));
					if (k >= 1) this.to = null;
				}
				if (this.spin) this.angle = (this.angle + dt * 360 / 60000) % 360;
			}
			this.apply();
		}

		apply() {
			this.circles.forEach((c, i) => {
				const p = this.cur[i];
				c.setAttribute('transform', `translate(${p[0].toFixed(2)} ${p[1].toFixed(2)}) scale(${p[2].toFixed(3)})`);
			});
			this.group.setAttribute('transform', `rotate(${this.angle.toFixed(2)} 50 50)`);
		}

		/* Waits out ms, and keeps waiting while held. */
		async wait(ms) {
			let end = Date.now() + ms;
			while (this.alive && (Date.now() < end || this.held)) {
				if (this.held) end += 50;
				await sleep(50);
			}
		}

		async run() {
			if (this.kind === 'think') {
				while (this.alive) {
					const d = rand(450, 750);
					this.go(this.pick(), d);
					await this.wait(d + 30);
				}
			} else if (this.kind === 'hero') {
				while (this.alive) {
					await this.wait(rand(2500, 4000));
					this.spin = false;
					this.go(GATHER, 420);
					await this.wait(470);
					const steps = rand(6, 8);
					for (let n = 0; n < steps; n++) {
						const d = rand(450, 750);
						this.go(this.pick(), d);
						await this.wait(d + 30);
					}
					this.go(HOME, 950);
					await this.wait(980);
					this.spin = true;
				}
			}
		}
	}

	const all = [...marks].map((svg) => new Mark(svg));
	let last = performance.now();
	const frame = (now) => {
		const dt = Math.min(100, now - last);
		last = now;
		for (const m of all) m.tick(now, dt);
		requestAnimationFrame(frame);
	};
	requestAnimationFrame(frame);
})();
