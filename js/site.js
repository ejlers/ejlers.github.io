/* The site has one interaction: a row opens.
   Opening a row never closes another, so nothing above it ever changes
   height. Everything else — the unfold, the chevron, the timing — is CSS. */

document.addEventListener('click', (event) => {
	const row = event.target.closest('.row');
	if (!row) return;

	const item = row.closest('.item');
	const drawer = item.querySelector('.drawer');
	const open = row.getAttribute('aria-expanded') !== 'true';

	row.setAttribute('aria-expanded', open);
	item.classList.toggle('is-open', open);
	if (!open) return;

	/* Bring the project you opened to the top of the window. Its header sits
	   above the drawer, so it never moves as the drawer grows — but the page
	   has not grown yet, so this first call is clamped short for the projects
	   near the bottom. It is still the one that matters when there is no
	   animation to wait for. The second call, once the unfold has finished,
	   finishes the journey for the rest. Whether it glides or jumps is
	   scroll-behavior's call, in CSS with the other motion rules. */
	const toTop = () => item.scrollIntoView({ block: 'start' });

	toTop();
	drawer.addEventListener('transitionend', function done(e) {
		if (e.target !== drawer || e.propertyName !== 'grid-template-rows') return;
		drawer.removeEventListener('transitionend', done);
		toTop();
	});
});
