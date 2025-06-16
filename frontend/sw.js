// Cache critical assets for offline use
const CACHE_NAME = 'kongchat-v1-static';
const urlsToCache = [
  '/',
  '/index.html',
  '/app.js',
  '/style.css',
  '/assets/icons/logo-48.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});
