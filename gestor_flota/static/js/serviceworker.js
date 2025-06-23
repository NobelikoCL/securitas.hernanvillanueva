// Placeholder para el Service Worker
// Este archivo sería generado o personalizado por django-pwa o manualmente.

var staticCacheName = "django-pwa-v1"; // Cambiar con cada actualización de assets estáticos

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(staticCacheName).then(function(cache) {
            // Estos son ejemplos, deberías listar tus assets importantes aquí
            return cache.addAll([
                '/', // La URL raíz de tu PWA
                // '/static/css/base.css', // Ejemplo de CSS
                // '/static/js/main.js',   // Ejemplo de JS
                // '/static/images/logo.png',// Ejemplo de imagen
                // '/offline/', // Una página offline personalizada si la tienes
            ]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cacheName) {
                    return cacheName.startsWith('django-pwa-') &&
                           cacheName != staticCacheName;
                }).map(function(cacheName) {
                    return caches.delete(cacheName);
                })
            );
        })
    );
});
