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
        // A dónde lleva el aviso al tocarlo. Un mensaje de chat abre la
        // conversación con quien escribe, no la portada.
        data: { url: data.url || '/' },
        // Misma etiqueta = se sustituye en la bandeja en vez de apilarse:
        // diez mensajes de la misma persona no dejan diez avisos.
        tag: data.tag || undefined,
        renotify: !!data.tag,
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    const destino = (event.notification.data && event.notification.data.url) || '/';

    // Si la app ya está abierta en alguna pestaña se reutiliza esa (y se la
    // lleva a donde toque); abrir una ventana nueva cada vez dejaba al usuario
    // con media docena de CalendPy abiertos.
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(lista) {
            for (const cliente of lista) {
                if ('focus' in cliente) {
                    if ('navigate' in cliente) {
                        try { cliente.navigate(destino); } catch (e) {}
                    }
                    return cliente.focus();
                }
            }
            return clients.openWindow(destino);
        })
    );
});
