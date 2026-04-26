// assets/service-worker.js

self.addEventListener('push', function(event) {
    let data = { title: 'CalendPy', body: 'Nueva notificación recibida' };
    
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: '/favicon.ico',      // usa el mismo icono que la web
        badge: '/favicon.ico',
        vibrate: [200, 100, 200],
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});