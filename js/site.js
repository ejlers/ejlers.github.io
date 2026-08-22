/* The site has one interaction: a row opens.
   Opening a row never closes another, so nothing above it ever changes
   height and the row cannot move under the cursor. Everything else —
   the unfold, the chevron, the timing — is CSS. */

document.addEventListener('click', (event) => {
	const row = event.target.closest('.row');
	if (!row) return;

	const open = row.getAttribute('aria-expanded') !== 'true';
	row.setAttribute('aria-expanded', open);
	row.closest('.item').classList.toggle('is-open', open);
});
