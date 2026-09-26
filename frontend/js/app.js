/**
 * ==============================================================================
 * ORQUESTADOR PRINCIPAL DE MANIQUÍES CALEB (ALTA COSTURA 3D)
 * Inicializa Intro Loader, Enrutador SPA, Módulos y Eventos Globales
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Iniciar Pantalla de Carga de Bienvenida
    UI.initIntroLoader();

    // 2. Inicializar Tema y Destellos de Oro
    UI.initTheme();

    // 3. Inicializar Enrutador SPA
    UI.initRouter();
    UI.initMobileNav();

    // 4. Sincronizar altura de cabecera fija
    UI.syncHeaderHeight();

    // 5. Inicializar Módulos del Sistema
    Hero3D.init();
    CatalogHero.init();
    await Catalog.init();
    Claims.init();
    Admin.init();
    Contact.init();

    // 6. Deshabilitar arrastre nativo de imágenes para garantizar fluidez en carrusel
    window.addEventListener('dragstart', (e) => {
        if (e.target.nodeName === 'IMG' || e.target.nodeName === 'A') {
            e.preventDefault();
            return false;
        }
    }, { capture: true });

    // 7. Sincronización post-carga de fuentes
    if (document.fonts) {
        document.fonts.ready.then(() => {
            UI.syncHeaderHeight();
        });
    }

    console.log('✨ Maniquíes Caleb — Plataforma de Alta Costura cargada exitosamente.');
});
