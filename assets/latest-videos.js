(() => {
  const root = document.querySelector('[data-latest-videos]');
  if (!root) return;
  const grid = root.querySelector('[data-latest-grid]');
  const status = root.querySelector('[data-latest-status]');
  const dateFmt = new Intl.DateTimeFormat(document.documentElement.lang || 'en', {year:'numeric',month:'short',day:'numeric'});
  fetch('/data/latest-videos.json', {cache:'no-cache'})
    .then(r => { if (!r.ok) throw Error('Feed not yet available'); return r.json(); })
    .then(data => {
      if (!Array.isArray(data.videos) || !data.videos.length) throw Error('Empty feed');
      const fragment = document.createDocumentFragment();
      for (const video of data.videos.slice(0,6)) {
        if (!/^[\w-]{11}$/.test(video.id)) continue;
        const card = document.createElement('article'); card.className = 'story-card';
        const a = document.createElement('a'); a.className = 'clip-poster'; a.href = 'https://www.youtube.com/watch?v=' + video.id; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.setAttribute('aria-label', video.title + ' (YouTube, new tab)');
        const img = document.createElement('img'); img.loading = 'lazy'; img.width = 480; img.height = 360; img.alt = video.title; img.src = 'https://i.ytimg.com/vi/' + video.id + '/hqdefault.jpg';
        const play = document.createElement('span'); play.className = 'clip-play'; play.setAttribute('aria-hidden','true'); play.textContent = '▶';
        a.append(img,play);
        const body = document.createElement('div'); body.className = 'story-body';
        const label = document.createElement('span'); label.className = 'story-label';
        const dt = new Date(video.published); label.textContent = Number.isNaN(dt.getTime()) ? 'LATEST UPLOAD' : dateFmt.format(dt);
        const h = document.createElement('h3'); h.textContent = video.title;
        const link = document.createElement('a'); link.href = a.href; link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = root.dataset.watchLabel || 'Watch on YouTube ↗';
        body.append(label,h,link); card.append(a,body); fragment.append(card);
      }
      if (!fragment.childNodes.length) throw Error('Invalid video IDs');
      grid.replaceChildren(fragment); status.hidden = true;
    })
    .catch(() => { status.textContent = root.dataset.errorLabel || 'Latest uploads are temporarily unavailable. Visit YouTube for the newest videos.'; });
})();
