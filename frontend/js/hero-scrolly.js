/**
 * ==============================================================================
 * HERO SCROLLYTELLING — MANIQUÍES CALEB
 * ==============================================================================
 * Ancla (pin) el hero mientras el usuario baja: el texto inicial se desvanece
 * y el MANIQUÍ se abre en 3 partes (cabeza, torso, base) — cada hueco que se
 * abre muestra una tarjeta con el detalle real de esa zona — hasta que las
 * partes se vuelven a unir y cierra con un CTA al catálogo. Usa solo
 * transform/opacity (GPU). No hay video de fondo: nada que tiemble.
 *
 * Decisión del dueño del sitio: se muestra siempre, incluso con
 * "prefers-reduced-motion" activado. El CSS (main.css, bloque
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
        const textContent = document.getElementById('hero-text-content');
        const modelSelector = document.getElementById('hero-model-selector');
        const sliceHead = document.getElementById('slice-head');
        const sliceTorso = document.getElementById('slice-torso');
        const sliceBase = document.getElementById('slice-base');
        const h1 = document.getElementById('scrolly-hotspot-1');
        const h2 = document.getElementById('scrolly-hotspot-2');
        const h3 = document.getElementById('scrolly-hotspot-3');
        const conclusion = document.getElementById('scrolly-conclusion');

        if (!section || !textContent || !sliceHead || !sliceTorso || !sliceBase || !h1 || !h2 || !h3 || !conclusion) return;

        const fadeInitial = [textContent, modelSelector].filter(Boolean);

        gsap.set(fadeInitial, { opacity: 1, y: 0, pointerEvents: 'auto' });
        gsap.set([sliceHead, sliceTorso, sliceBase], { yPercent: 0 });
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

        // Salida del texto inicial y el selector de modelos.
        tl.to(fadeInitial, {
            opacity: 0,
            y: -20,
            duration: 0.1,
            ease: 'power2.inOut',
            pointerEvents: 'none'
        }, 0);

        // El maniquí se abre: la cabeza sube, la base baja, el torso no se mueve.
        tl.to(sliceHead, { yPercent: -55, duration: 0.22, ease: 'power2.inOut' }, 0.05)
          .to(sliceBase, { yPercent: 55, duration: 0.22, ease: 'power2.inOut' }, 0.05);

        // Paso 1 — Cabeza & Hombros.
        tl.to(h1, { opacity: 1, scale: 1, duration: 0.08, ease: 'power2.out' }, 0.28)
          .to(h1, { opacity: 0, scale: 0.95, duration: 0.06, ease: 'power2.in' }, 0.44);

        // Paso 2 — Torso.
        tl.to(h2, { opacity: 1, scale: 1, duration: 0.08, ease: 'power2.out' }, 0.50)
          .to(h2, { opacity: 0, scale: 0.95, duration: 0.06, ease: 'power2.in' }, 0.66);

        // Paso 3 — Base & Piernas.
        tl.to(h3, { opacity: 1, scale: 1, duration: 0.08, ease: 'power2.out' }, 0.72)
          .to(h3, { opacity: 0, scale: 0.95, duration: 0.06, ease: 'power2.in' }, 0.86);

        // Las partes se vuelven a unir antes del cierre.
        tl.to([sliceHead, sliceBase], { yPercent: 0, duration: 0.1, ease: 'power2.inOut' }, 0.86);

        // Cierre — CTA al catálogo (queda visible hasta liberar el pin).
        tl.to(conclusion, {
            opacity: 1,
            scale: 1,
            duration: 0.1,
            ease: 'back.out(1.5)',
            pointerEvents: 'auto'
        }, 0.90);

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
