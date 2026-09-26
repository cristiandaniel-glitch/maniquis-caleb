/**
 * ==============================================================================
 * HERO SCROLLYTELLING — MANIQUÍES CALEB
 * ==============================================================================
 * Ancla (pin) el hero mientras el usuario baja: el texto inicial se
 * desvanece y el SCROLL controla directamente el currentTime del video real
 * (cielo → aparece la laptop → el maniquí emerge → gira solo) — no es un
 * loop autoplay con zoom en CSS, es scroll-scrubbing de verdad, la misma
 * técnica que usan los sitios de referencia. Sobre el tramo final (el
 * maniquí ya solo, girando) aparecen las tarjetas de detalle, hasta cerrar
 * con un CTA al catálogo.
 *
 * Decisión del dueño del sitio: se muestra siempre, incluso con
 * "prefers-reduced-motion" activado.
 */

const HeroScrolly = {
    scrollTriggerInstance: null,

    init() {
        if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
            console.warn('[HeroScrolly] GSAP o ScrollTrigger no cargados. Reintentando...');
            setTimeout(() => this.init(), 100);
            return;
        }

        gsap.registerPlugin(ScrollTrigger);
        this.initScrollytelling();
    },

    initScrollytelling() {
        const section = document.getElementById('view-inicio');
        const textContent = document.getElementById('hero-text-content');
        const scrollCue = document.getElementById('hero-scroll-cue');
        const video = document.getElementById('hero-reveal-video');
        const h1 = document.getElementById('scrolly-hotspot-1');
        const h2 = document.getElementById('scrolly-hotspot-2');
        const h3 = document.getElementById('scrolly-hotspot-3');
        const conclusion = document.getElementById('scrolly-conclusion');

        if (!section || !textContent || !video || !h1 || !h2 || !h3 || !conclusion) return;

        const build = () => {
            // Sin duración conocida no hay nada que scrubear.
            if (!video.duration || Number.isNaN(video.duration)) {
                video.addEventListener('loadedmetadata', build, { once: true });
                return;
            }

            const fadeInitial = [textContent, scrollCue].filter(Boolean);

            gsap.set(fadeInitial, { opacity: 1, y: 0, pointerEvents: 'auto' });
            gsap.set(video, { currentTime: 0 });
            gsap.set([h1, h2, h3, conclusion], { opacity: 0, scale: 0.95, pointerEvents: 'none' });

            const tl = gsap.timeline({
                scrollTrigger: {
                    trigger: section,
                    start: 'top top',
                    end: '+=260%',
                    pin: true,
                    scrub: 1,
                    anticipatePin: 1
                }
            });

            // El scroll recorre el video entero de punta a punta.
            tl.to(video, { currentTime: video.duration, ease: 'none', duration: 1 }, 0);

            // Salida del texto inicial y el aviso de scroll (bien al arranque).
            tl.to(fadeInitial, {
                opacity: 0,
                y: -20,
                duration: 0.08,
                ease: 'power2.inOut',
                pointerEvents: 'none'
            }, 0.02);

            // El último cuarto del video es el maniquí ya solo, girando en el
            // cielo — ahí van las 3 tarjetas de detalle real del producto.
            tl.to(h1, { opacity: 1, scale: 1, duration: 0.06, ease: 'power2.out' }, 0.78)
              .to(h1, { opacity: 0, scale: 0.95, duration: 0.05, ease: 'power2.in' }, 0.86);

            tl.to(h2, { opacity: 1, scale: 1, duration: 0.06, ease: 'power2.out' }, 0.87)
              .to(h2, { opacity: 0, scale: 0.95, duration: 0.05, ease: 'power2.in' }, 0.94);

            tl.to(h3, { opacity: 1, scale: 1, duration: 0.06, ease: 'power2.out' }, 0.95)
              .to(h3, { opacity: 0, scale: 0.95, duration: 0.04, ease: 'power2.in' }, 1.0);

            // Cierre — CTA al catálogo, coincide con el último frame del video.
            tl.to(conclusion, {
                opacity: 1,
                scale: 1,
                duration: 0.06,
                ease: 'back.out(1.5)',
                pointerEvents: 'auto'
            }, 0.97);

            this.scrollTriggerInstance = tl.scrollTrigger;
        };

        build();
    },

    /**
     * Esta es una SPA de vistas por display:none, no de secciones apiladas:
     * el pin de GSAP envuelve #view-inicio en un "pin-spacer" con altura fija
     * (la distancia de scroll reservada). Si el usuario navega a otra vista,
     * esa sección pasa a display:none pero el spacer (que tiene su propio
     * alto inline, independiente del hijo) sigue ocupando ese espacio vacío
     * ANTES de la vista nueva, empujándola fuera de pantalla. Por eso hay
     * que matar el pin al salir de Inicio y reconstruirlo al volver — ver
     * la llamada en UI.navigateView().
     */
    teardown() {
        if (this.scrollTriggerInstance) {
            this.scrollTriggerInstance.kill();
            this.scrollTriggerInstance = null;
        }
    },

    rebuild() {
        this.teardown();
        if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
        this.initScrollytelling();
        ScrollTrigger.refresh();
    }
};

document.addEventListener('DOMContentLoaded', () => {
    HeroScrolly.init();
});

window.HeroScrolly = HeroScrolly;
