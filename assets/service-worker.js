self.addEventListener('push', event => {
    event.waitUntil(
        (async () => {
            if (event.data) {
                const data = event.data.json();
                await self.registration.showNotification(data.title, {
                    body: data.body,
                    icon: '/assets/icono.png'  // Ajusta la ruta de tu icono
                });
            }
        })()
    );
});
