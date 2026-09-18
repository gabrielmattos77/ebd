const CACHE_NAME = "ebd-static-v4";

const STATIC_ASSETS = [
    "/static/manifest.json",
    "/static/icons/ebd-logo.png",
    "/static/icons/logos-imw-rodape.png"
];

self.addEventListener("install", event => {
    self.skipWaiting();

    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", event => {
    const request = event.request;

    if (request.method !== "GET") {
        return;
    }

    const url = new URL(request.url);

    // Páginas do Flask: sempre vêm da rede.
    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request).catch(() => caches.match(request))
        );
        return;
    }

    // Arquivos estáticos: cache primeiro.
    if (url.pathname.startsWith("/static/")) {
        event.respondWith(
            caches.match(request).then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }

                return fetch(request).then(response => {
                    if (response.ok) {
                        const copy = response.clone();

                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(request, copy);
                        });
                    }

                    return response;
                });
            })
        );
    }
});
