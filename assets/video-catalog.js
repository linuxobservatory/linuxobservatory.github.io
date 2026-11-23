(async () => {
  const channel = 'UCNq7pDavJRTEjg3AOdcuMAg';
  const search = document.getElementById('obs-search');
  const resolution = document.getElementById('obs-resolution');
  const reset = document.getElementById('obs-reset');
  const status = document.getElementById('obs-count');
  const results = document.getElementById('catalog-results');
  const more = document.getElementById('catalog-more');
  const notes = new Map();
  for (const article of document.querySelectorAll('[data-record]')) {
    const watch = article.querySelector('a[href^="https://www.youtube.com/watch?"]');
    if (watch) notes.set(new URL(watch.href).searchParams.get('v'), article);
  }

  async function readFeed(path) {
    const response = await fetch(path, {cache: 'no-cache'});
    if (!response.ok) throw new Error('Unavailable feed');
    const data = await response.json();
    if (data.channel_id !== channel || !Array.isArray(data.videos) ||
        !data.videos.every(v => /^[\w-]{11}$/.test(v.id) && typeof v.title === 'string')) {
      throw new Error('Invalid feed');
    }
    return data.videos;
  }

  try {
    const [catalog, latest] = await Promise.all([
      readFeed('https://raw.githubusercontent.com/linuxobservatory/linuxobservatory.github.io/main/data/video-catalog.json')
        .catch(() => readFeed('/data/video-catalog.json')),
      readFeed('/data/latest-videos.json').catch(() => [])
    ]);
    const ids = new Set(catalog.map(video => video.id));
    const videos = [...latest.filter(video => !ids.has(video.id)), ...catalog].map(video => {
      const note = notes.get(video.id);
      const text = (video.title + ' ' + (note?.dataset.search || '')).toLowerCase();
      const sizes = new Set(Array.from(text.matchAll(/\b(32|16|8|6|4)k(?=\b|\d)/g), m => m[1] + 'k'));
      if (note && note.dataset.resolution !== 'unknown') sizes.add(note.dataset.resolution);
      return {...video, text, sizes, note};
    });
    const params = new URL(location.href).searchParams;
    search.value = params.get('q') || '';
    if (Array.from(resolution.options).some(o => o.value === params.get('resolution'))) {
      resolution.value = params.get('resolution');
    }
    let matches = [];
    let shown = 0;
    function appendPage() {
      const fragment = document.createDocumentFragment();
      for (const video of matches.slice(shown, shown + 30)) {
        const row = document.createElement('li');
        const watch = document.createElement('a');
        watch.textContent = video.title;
        watch.href = 'https://www.youtube.com/watch?v=' + video.id;
        row.append(watch);
        if (video.note) {
          const link = document.createElement('a');
          link.href = '#' + video.note.id;
          link.className = 'catalog-note';
          link.textContent = 'Recording notes';
          row.append(link);
        }
        fragment.append(row);
      }
      const first = fragment.firstElementChild;
      shown += fragment.childElementCount;
      results.append(fragment);
      more.hidden = shown >= matches.length;
      status.textContent = matches.length
        ? 'Showing ' + shown.toLocaleString() + ' of ' + matches.length.toLocaleString() + ' matching uploads'
        : 'No matching uploads. Try another title or clear the filters.';
      return first;
    }
    function filter() {
      const query = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      const size = resolution.value;
      matches = videos.filter(v => query.every(word => v.text.includes(word)) &&
        (size === 'all' || (size === 'unknown' ? !v.sizes.size : v.sizes.has(size))));
      results.replaceChildren();
      shown = 0;
      appendPage();
      reset.disabled = !search.value && size === 'all';
    }
    function update() {
      filter();
      const url = new URL(location.href);
      for (const [key,value] of [['q',search.value.trim()],['resolution',resolution.value === 'all' ? '' : resolution.value]]) {
        if (value) url.searchParams.set(key,value);
        else url.searchParams.delete(key);
      }
      history.replaceState(null,'',url);
    }
    more.addEventListener('click', () => appendPage()?.querySelector('a')?.focus());
    search.addEventListener('input', update);
    resolution.addEventListener('change', update);
    reset.addEventListener('click', () => {
      search.value = '';
      resolution.value = 'all';
      update();
      search.focus();
    });
    search.closest('.filter-bar').hidden = false;
    filter();
  } catch {
    status.textContent = 'The catalogue could not load. Browse all uploads on YouTube or read the recording notes below.';
  }
})();
