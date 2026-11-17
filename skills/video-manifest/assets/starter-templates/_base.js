// Fills [data-var] from the URL query (?title=Hello) and replays the animation every data-loop seconds for previews.
const q = new URLSearchParams(location.search);
document.querySelectorAll('[data-var]').forEach(el => { if (q.has(el.dataset.var)) el.textContent = q.get(el.dataset.var); });
const loop = parseFloat(document.body.dataset.loop || 4) * 1000;
const play = () => { document.body.classList.remove('play'); void document.body.offsetWidth; document.body.classList.add('play'); document.dispatchEvent(new Event('play')); };
play(); if (!q.has('once')) setInterval(play, loop);
