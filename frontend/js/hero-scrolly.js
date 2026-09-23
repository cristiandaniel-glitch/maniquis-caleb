/**
 * ==============================================================================
 * HERO SCROLLYTELLING — MANIQUÍES CALEB
 * ==============================================================================
 * Ancla (pin) el hero mientras el usuario baja: el texto inicial se desvanece,
 * el video de showroom hace un acercamiento cinemático continuo y tres tarjetas
 * (fibra, base, envíos) van apareciendo una a la vez, hasta cerrar con un CTA
 * al catálogo. Usa solo transform/opacity (GPU).
 *
 * Decisión del dueño del sitio: se muestra siempre, incluso con
 * "prefers-reduced-motion" activado — no se prioriza el impacto visual de la
 * página de ventas por sobre esa preferencia. El CSS (main.css, bloque
 * "@media (prefers-reduced-motion: reduce)" sobre .hero-scrolly-overlay)
 * queda igual como red de seguridad si GSAP no llega a cargar.
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
        const bgMedia = document.getElementById('hero-bg-media');
        const bgVideo = document.getElementById('hero-bg-video');
        const heroContent = document.getElementById('hero-initial-content');
        const h1 = document.getElementById('scrolly-hotspot-1');
        const h2 = document.getElementById('scrolly-hotspot-2');
        const h3 = document.getElementById('scrolly-hotspot-3');
        const conclusion = document.getElementById('scrolly-conclusion');

        if (!section || !bgMedia || !heroContent || !h1 || !h2 || !h3 || !conclusion) return;

        gsap.set(heroContent, { opacity: 1, y: 0, pointerEvents: 'auto' });
        gsap.set(bgMedia, { transformOrigin: 'center center', scale: 1 });
        gsap.set([h1, h2, h3, conclusion], { opacity: 0, scale: 0.95, pointerEvents: 'none' });

        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: section,
                start: 'top top',
                end: '+=220%',
                pin: true,
                scrub: 1,
                anticipatePin: 1
            }
        });

        // Acercamiento continuo del video a lo largo de todo el recorrido.
        tl.to(bgMedia, { scale: 1.15, ease: 'none', duration: 1 }, 0);
        if (bgVideo) {
            tl.to(bgVideo, { opacity: 0.5, ease: 'none', duration: 1 }, 0);
        }

        // Salida del texto inicial (título, CTAs, selector de modelos).
        tl.to(heroContent, {
            opacity: 0,
            y: -30,
            duration: 0.12,
            ease: 'power2.inOut',
            pointerEvents: 'none'
        }, 0);

        // Paso 1 — Fibra de Alta Densidad.
        tl.to(h1, { opacity: 1, scale: 1, duration: 0.1, ease: 'power2.out' }, 0.14)
          .to(h1, { opacity: 0, scale: 0.95, duration: 0.08, ease: 'power2.in' }, 0.32);

        // Paso 2 — Bases de Acero 10mm.
        tl.to(h2, { opacity: 1, scale: 1, duration: 0.1, ease: 'power2.out' }, 0.4)
          .to(h2, { opacity: 0, scale: 0.95, duration: 0.08, ease: 'power2.in' }, 0.58);

        // Paso 3 — Envíos Inmediatos.
        tl.to(h3, { opacity: 1, scale: 1, duration: 0.1, ease: 'power2.out' }, 0.66)
          .to(h3, { opacity: 0, scale: 0.95, duration: 0.08, ease: 'power2.in' }, 0.84);

        // Cierre — CTA al catálogo (queda visible hasta liberar el pin).
        tl.to(conclusion, {
            opacity: 1,
            scale: 1,
            duration: 0.12,
            ease: 'back.out(1.5)',
            pointerEvents: 'auto'
        }, 0.88);

        this.scrollTriggerInstance = tl.scrollTrigger;
    },

    /**
     * Esta es una SPA de vistas por display:none, no de secciones apiladas:
     * el pin de GSAP envuelve #view-inicio en un "pin-spacer" con altura fija
     * (la distancia de scroll reservada, ~220% del viewport). Si el usuario
     * navega a otra vista, esa sección pasa a display:none pero el spacer
     * (que tiene su propio alto inline, independiente del hijo) sigue
     * ocupando ese espacio vacío ANTES de la vista nueva, empujándola fuera
     * de pantalla. Por eso hay que matar el pin al salir de Inicio y
     * reconstruirlo al volver — ver la llamada en UI.navigateView().
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
