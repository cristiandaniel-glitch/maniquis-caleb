/**
 * Hero Inmersivo & Scrollytelling con GSAP y ScrollTrigger.
 * NOVEDADES CALEB - Maniquíes & Retail de Alta Costura.
 * 
 * Funcionalidades:
 * 1. Paneo Cinemático Automático de fondo (Modo Video) de izquierda a derecha.
 * 2. Arrastre manual (Drag & Touch) para inspeccionar libremente.
 * 3. Scrollytelling sincronizado con la rueda del ratón (pin: true, zoom progresivo,
 *    desvanecimiento del titular y emergencia de tarjetas flotantes glassmorphism con hotspots).
 */

const HeroScrolly = {
    autoPanTween: null,
    scrollTriggerInstance: null,
    isDragging: false,
    startX: 0,
    currentPanX: 0,

    init() {
        if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
            console.warn('[HeroScrolly] GSAP o ScrollTrigger no cargados. Reintentando...');
            setTimeout(() => this.init(), 100);
            return;
        }

        gsap.registerPlugin(ScrollTrigger);

        this.initAutoPan();
        this.initDragControls();
        this.initScrollytelling();
    },

    /**
     * Estado Inicial: Paneo Cinemático Automático (Modo Video en bucle)
     */
    initAutoPan() {
        const bgImg = document.getElementById('hero-showroom-bg');
        if (!bgImg) return;

        gsap.set(bgImg, { transformOrigin: 'center top' });

        // Paneo suave continuo de izquierda a derecha (yoyo alternate)
        this.autoPanTween = gsap.to(bgImg, {
            xPercent: 3.5,
            duration: 18,
            ease: 'sine.inOut',
            repeat: -1,
            yoyo: true,
            overwrite: 'auto'
        });
    },

    /**
     * Arrastre manual interactivo (Mouse y Touch)
     */
    initDragControls() {
        const stage = document.getElementById('hero-scrolly-stage');
        const bgImg = document.getElementById('hero-showroom-bg');
        if (!stage || !bgImg) return;

        const onStart = (clientX) => {
            if (window.scrollY > 50) return; // Solo en la cima
            this.isDragging = true;
            this.startX = clientX;
            if (this.autoPanTween) this.autoPanTween.pause();
            stage.style.cursor = 'grabbing';
        };

        const onMove = (clientX) => {
            if (!this.isDragging) return;
            const deltaX = (clientX - this.startX) * 0.03;
            this.currentPanX = Math.max(-8, Math.min(8, this.currentPanX + deltaX));
            this.startX = clientX;
            gsap.to(bgImg, {
                xPercent: this.currentPanX,
                duration: 0.3,
                ease: 'power1.out',
                overwrite: 'auto'
            });
        };

        const onEnd = () => {
            if (!this.isDragging) return;
            this.isDragging = false;
            stage.style.cursor = 'grab';
            // Reanudar el paneo automático tras 2.5s de inactividad
            setTimeout(() => {
                if (!this.isDragging && window.scrollY < 50 && this.autoPanTween) {
                    this.autoPanTween.resume();
                }
            }, 2500);
        };

        // Eventos de ratón
        stage.addEventListener('mousedown', (e) => onStart(e.clientX));
        window.addEventListener('mousemove', (e) => onMove(e.clientX));
        window.addEventListener('mouseup', onEnd);

        // Eventos táctiles
        stage.addEventListener('touchstart', (e) => {
            if (e.touches.length > 0) onStart(e.touches[0].clientX);
        }, { passive: true });
        window.addEventListener('touchmove', (e) => {
            if (e.touches.length > 0) onMove(e.touches[0].clientX);
        }, { passive: true });
        window.addEventListener('touchend', onEnd);
    },

    /**
     * Transición a Scrollytelling (GSAP ScrollTrigger con pin: true)
     */
    initScrollytelling() {
        const section = document.getElementById('view-inicio');
        const bgImg = document.getElementById('hero-showroom-bg');
        const heroContent = document.getElementById('hero-initial-content');
        const scrollyOverlay = document.getElementById('hero-scrolly-overlay');
        const h1 = document.getElementById('scrolly-hotspot-1');
        const h2 = document.getElementById('scrolly-hotspot-2');
        const h3 = document.getElementById('scrolly-hotspot-3');
        const conclusion = document.getElementById('scrolly-conclusion');

        if (!section || !bgImg) return;

        // Establecer estados iniciales limpios
        gsap.set(heroContent, { opacity: 1, y: 0, pointerEvents: 'auto' });
        gsap.set(scrollyOverlay, { opacity: 0, pointerEvents: 'none' });
        gsap.set(bgImg, { transformOrigin: 'center top', scale: 1, xPercent: 0 });
        gsap.set([h1, h2, h3, conclusion], { opacity: 0, scale: 0.85, y: 0 });

        // Timeline sincronizada con el scroll del ratón (pin: true)
        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: section,
                start: 'top top',
                end: '+=250%',
                pin: true,
                scrub: 1.2,
                anticipatePin: 1,
                onEnter: () => {
                    if (this.autoPanTween) this.autoPanTween.pause();
                },
                onLeaveBack: () => {
                    if (this.autoPanTween) this.autoPanTween.resume();
                }
            }
        });

        // 1. Desvanecer titular principal y enfocar la cámara hacia el primer maniquí (0% -> 25%)
        tl.to(heroContent, {
            opacity: 0,
            y: -40,
            duration: 0.25,
            ease: 'power2.inOut',
            pointerEvents: 'none'
        }, 0);

        tl.to(scrollyOverlay, {
            opacity: 1,
            duration: 0.2,
            pointerEvents: 'auto'
        }, 0.15);

        // PASO 1: Enfoque en Anatomía & Ergonomía (Hotspot 1) (20% -> 45%)
        tl.to(bgImg, {
            scale: 1.15,
            xPercent: -3,
            duration: 0.4,
            ease: 'power1.inOut'
        }, 0.15);

        tl.to(h1, {
            opacity: 1,
            scale: 1,
            y: 0,
            duration: 0.25,
            ease: 'back.out(1.4)'
        }, 0.25);

        // PASO 2: Transición de cámara hacia Acabados & Fibra de Vidrio (Hotspot 2) (45% -> 70%)
        tl.to(h1, {
            opacity: 0,
            scale: 0.85,
            duration: 0.2,
            ease: 'power1.in'
        }, 0.45);

        tl.to(bgImg, {
            scale: 1.20,
            xPercent: 1,
            duration: 0.45,
            ease: 'power1.inOut'
        }, 0.45);

        tl.to(h2, {
            opacity: 1,
            scale: 1,
            y: 0,
            duration: 0.25,
            ease: 'back.out(1.4)'
        }, 0.55);

        // PASO 3: Transición hacia Bases & Colgantes (Hotspot 3) y Tarjeta de Catálogo (70% -> 95%)
        tl.to(h2, {
            opacity: 0,
            scale: 0.85,
            duration: 0.2,
            ease: 'power1.in'
        }, 0.70);

        tl.to(bgImg, {
            scale: 1.14,
            xPercent: 3,
            duration: 0.45,
            ease: 'power1.inOut'
        }, 0.70);

        tl.to(h3, {
            opacity: 1,
            scale: 1,
            y: 0,
            duration: 0.25,
            ease: 'back.out(1.4)'
        }, 0.78);

        tl.to(conclusion, {
            opacity: 1,
            scale: 1,
            duration: 0.3,
            ease: 'back.out(1.2)'
        }, 0.82);

        // 4. Suavizar salida fluida al finalizar el recorrido (95% -> 100%)
        tl.to([h3, conclusion], {
            opacity: 0.85,
            duration: 0.1
        }, 0.95);

        this.scrollTriggerInstance = tl.scrollTrigger;
    },

    enable() {
        if (!this.scrollTriggerInstance) {
            this.initScrollytelling();
        } else {
            this.scrollTriggerInstance.enable(true, true);
        }
        if (this.autoPanTween) {
            this.autoPanTween.play();
        }
        if (typeof ScrollTrigger !== 'undefined') {
            ScrollTrigger.refresh();
        }
    },

    disable() {
        if (this.scrollTriggerInstance) {
            this.scrollTriggerInstance.kill(true);
            this.scrollTriggerInstance = null;
        }
        if (this.autoPanTween) {
            this.autoPanTween.pause();
        }
        const section = document.getElementById('view-inicio');
        if (section) {
            section.style.removeProperty('transform');
            section.style.removeProperty('position');
            section.style.removeProperty('top');
            section.style.removeProperty('left');
            section.style.removeProperty('width');
            section.style.removeProperty('height');
        }
        if (typeof ScrollTrigger !== 'undefined') {
            ScrollTrigger.refresh();
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    HeroScrolly.init();
});

window.HeroScrolly = HeroScrolly;
