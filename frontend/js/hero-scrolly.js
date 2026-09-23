/**
 * ==============================================================================
 * HERO SCROLLYTELLING — MANIQUÍES CALEB
 * ==============================================================================
 * Ancla (pin) el hero mientras el usuario baja: el texto inicial se desvanece,
 * el video de showroom hace un acercamiento cinemático continuo y tres tarjetas
 * (fibra, base, envíos) van apareciendo una a la vez, hasta cerrar con un CTA
 * al catálogo. Usa solo transform/opacity (GPU) y se desactiva por completo si
 * el usuario prefiere movimiento reducido.
 */

const HeroScrolly = {
    scrollTriggerInstance: null,

    init() {
        if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
            console.warn('[HeroScrolly] GSAP o ScrollTrigger no cargados. Reintentando...');
            setTimeout(() => this.init(), 100);
            return;
        }

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) {
            // Sin scroll-hijack: el hero queda estático y siempre legible.
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
    }
};

document.addEventListener('DOMContentLoaded', () => {
    HeroScrolly.init();
});

window.HeroScrolly = HeroScrolly;
