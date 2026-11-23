(() => {
  const container = document.querySelector('[data-latest-videos]');
  if (!container) return;

  const verifiedChannel = 'UCNq7pDavJRTEjg3AOdcuMAg';
  const grid = container.querySelector('[data-latest-grid]');
  const status = container.querySelector('[data-latest-status]');
  const dateFormatter = new Intl.DateTimeFormat(
    document.documentElement.lang || 'en',
    { year: 'numeric', month: 'short', day: 'numeric' }
  );

  function displayError() {
    status.textContent = container.dataset.errorLabel || 'Visit our YouTube channel to see the latest uploads.';
    status.hidden = false;
  }

  fetch('/data/latest-videos.json', { cache: 'no-store' })
    .then(response => {
      if (!response.ok) throw new Error('Video data unavailable');
      return response.json();
    })
    .then(data => {
      // Fail closed. Never show videos if the feed's identity is unverified.
      if (data.channel_id !== verifiedChannel ||
          !Array.isArray(data.videos) || data.videos.length !== 6) {
        throw new Error('Not a verified six-video feed');
      }

      const fragment = document.createDocumentFragment();
      const seen = new Set();
      for (const video of data.videos) {
        if (!video || !/^[a-zA-Z0-9_-]{11}$/.test(video.id) ||
            typeof video.title !== 'string' || !video.title.trim() ||
            seen.has(video.id)) {
          throw new Error('Invalid video');
        }
        seen.add(video.id);

        const article = document.createElement('article');
        article.className = 'story-card';
        const poster = document.createElement('a');
        poster.className = 'clip-poster';
        poster.href = 'https://www.youtube.com/watch?v=' + video.id;
        poster.tabIndex = -1;
        poster.rel = 'noopener noreferrer';
        poster.setAttribute('aria-label', video.title);

        const thumbnail = document.createElement('img');
        thumbnail.loading = 'lazy';
        thumbnail.width = 480;
        thumbnail.height = 360;
        thumbnail.src = 'https://i.ytimg.com/vi/' + video.id + '/hqdefault.jpg';
        thumbnail.alt = video.title;

        const playIcon = document.createElement('span');
        playIcon.className = 'clip-play';
        playIcon.setAttribute('aria-hidden', 'true');
        playIcon.textContent = '▶';
        poster.append(thumbnail, playIcon);

        const body = document.createElement('div');
        body.className = 'story-body';
        const published = document.createElement('span');
        published.className = 'story-label';
        const publishedDate = new Date(video.published);
        published.textContent = Number.isNaN(publishedDate.getTime())
          ? 'LATEST UPLOAD' : dateFormatter.format(publishedDate);
        const title = document.createElement('h3');
        const watch = document.createElement('a');
        watch.href = poster.href;
        watch.rel = 'noopener noreferrer';
        watch.textContent = video.title;
        title.replaceChildren(watch);
        body.append(published, title);
        article.append(poster, body);
        fragment.append(article);
      }

      grid.replaceChildren(fragment);
      status.hidden = true;
    })
    .catch(displayError);
})();
