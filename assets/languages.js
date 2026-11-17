/* Language URLs are authoritative. Only an English entry may auto-select a language. */
(() => {
  'use strict';
  const supported = ['en', 'da', 'de', 'zh-Hans'];
  const key = 'linux-observatory-language';
  const routes = ['/', '/about/', '/start-here/'];
  const path = location.pathname.replace(/index\.html$/, '').replace(/\/?$/, '/');
  const localized = /^\/(da|de|zh-hans)(\/.*)$/.exec(path);
  const page = localized ? localized[2] : path;
  if (!routes.includes(page)) return;
  function read() { try { return localStorage.getItem(key); } catch (_) { return null; } }
  function write(value) { try { localStorage.setItem(key, value); } catch (_) {} }
  function match(tag) {
    tag = tag.toLowerCase();
    if (/^zh(?:-|$)/.test(tag)) {
      if (/hant|(?:^|-)(tw|hk|mo)(?:-|$)/.test(tag)) return null;
      return 'zh-Hans';
    }
    return supported.find(l => tag === l || tag.startsWith(l + '-')) || null;
  }
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-language]').forEach(link => {
      link.addEventListener('click', event => {
        if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        write(link.dataset.language);
        // Keep section links and query strings when changing language.
        const target = new URL(link.href, location.origin);
        target.search = location.search;
        target.hash = location.hash;
        link.href = target.href;
      });
    });
  });
  if (localized) return;
  // Internal English links and back navigation must not trap visitors in redirects.
  try { if (document.referrer && new URL(document.referrer).origin === location.origin) return; } catch (_) {}
  if (performance.getEntriesByType('navigation')[0]?.type === 'back_forward') return;
  let preferred = read();
  if (!supported.includes(preferred)) {
    preferred = (navigator.languages || [navigator.language]).map(match).find(Boolean) || 'en';
  }
  if (preferred !== 'en') location.replace('/' + preferred.toLowerCase() + page + location.search + location.hash);
})();
