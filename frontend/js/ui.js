/**
 * ==============================================================================
 * CONTROLADORES DE INTERFAZ CONTEMPORÁNEA (UI HELPERS 2026)
 * MANIQUÍES CALEB — ALTA COSTURA & VANGUARDIA
 * ==============================================================================
 */

const UI = {
    currentTheme: 'boutique',

    /**
     * Enlace directo a WhatsApp Oficial de Patrick Romero.
     */
    openWhatsApp(text = '') {
        const base = 'https://wa.me/51916126747';
        const defaultText = 'Hola Patrick (Novedades Caleb), deseo solicitar el catálogo de maniquíes y cotización para mi boutique.';
        const message = text || defaultText;
        const url = `${base}?text=${encodeURIComponent(message)}`;
        window.open(url, '_blank', 'noopener,noreferrer');
    },

    /**
     * Efecto Spotlight reactivo al cursor (la luz sigue el ratón sobre las tarjetas).
     */
    initSpotlightEffect() {
        const updateSpotlight = (e) => {
            const cards = document.querySelectorAll('.spotlight-card');
            cards.forEach(card => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.setProperty('--mouse-x', `${x}px`);
                card.style.setProperty('--mouse-y', `${y}px`);
            });
        };

        window.addEventListener('mousemove', updateSpotlight, { passive: true });
    },

    /**
     * Sincroniza la Floating Island Navbar en el scroll.
     */
    initFloatingNavbar() {
        const island = document.querySelector('.floating-island-inner');
        if (!island) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > 40) {
                island.style.background = 'rgba(10, 10, 14, 0.88)';
                island.style.boxShadow = '0 20px 50px -10px rgba(0, 0, 0, 0.95), 0 0 30px rgba(223, 199, 155, 0.12)';
            } else {
                island.style.background = 'rgba(14, 14, 18, 0.75)';
                island.style.boxShadow = '0 16px 40px -10px rgba(0, 0, 0, 0.8), 0 0 25px rgba(223, 199, 155, 0.08)';
            }
        }, { passive: true });
    },

    /**
     * Pantalla de Carga de Bienvenida (~0.9s ultra-fluida).
     */
    initIntroLoader() {
        const loader = document.getElementById('intro-loader');
        const fill = document.getElementById('loader-bar-fill');
        const percent = document.getElementById('loader-percent');
        const statusText = document.getElementById('loader-status-text');

        if (!loader || !fill) return;

        let progress = 0;
        const messages = [
            "El estilo es una forma de decir quién eres sin tener que hablar.",
            "Cada gran colección comienza con la exhibición perfecta.",
            "Vistiendo el éxito de tu boutique. Bienvenido a Maniquíes Caleb."
        ];

        const interval = setInterval(() => {
            progress += Math.random() * 6.5 + 5.5;
            if (progress > 100) progress = 100;

            const rounded = Math.floor(progress);
            fill.style.width = `${progress}%`;
            if (percent) percent.innerText = `${rounded}%`;

            const msgIndex = Math.min(Math.floor((progress / 100) * messages.length), messages.length - 1);
            if (statusText) statusText.innerText = messages[msgIndex];

            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    loader.classList.add('fade-out');
                    setTimeout(() => {
                        if (loader.parentNode) loader.remove();
                    }, 450);
                }, 140);
            }
        }, 25);
    },

    /**
     * Enrutador SPA de Vistas Independientes.
     */
    navigateView(viewName) {
        const validRoutes = ['inicio', 'catalogo', 'nosotros', 'colgantes', 'contacto', 'resenas', 'reclamos'];
        const targetView = validRoutes.includes(viewName) ? viewName : 'inicio';
        const previousView = document.body.getAttribute('data-view');

        const views = document.querySelectorAll('.page-view');
        const navLinks = document.querySelectorAll('.nav-link');
        const targetEl = document.getElementById(`view-${targetView}`);

        if (!targetEl) return;

        // El pin del hero scrollytelling reserva espacio en el documento (ver
        // hero-scrolly.js). Si no se destruye al salir de Inicio, ese espacio
        // vacío empuja la vista nueva fuera de pantalla.
        if (typeof HeroScrolly !== 'undefined' && previousView === 'inicio' && targetView !== 'inicio') {
            HeroScrolly.teardown();
        }

        views.forEach(v => v.classList.remove('active'));
        navLinks.forEach(l => {
            if (l.dataset.target === targetView) {
                l.classList.add('active');
            } else {
                l.classList.remove('active');
            }
        });

        targetEl.classList.add('active');
        document.body.setAttribute('data-view', targetView);
        window.history.replaceState(null, null, `#${targetView}`);

        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });

        if (typeof HeroScrolly !== 'undefined' && targetView === 'inicio' && previousView !== 'inicio') {
            HeroScrolly.rebuild();
        }

        if (targetView === 'catalogo') {
            if (typeof Catalog !== 'undefined' && (!Catalog.products || Catalog.products.length === 0)) {
                Catalog.loadData();
            }
        }
    },

    initRouter() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.dataset.target;
                if (target) this.navigateView(target);
            });
        });

        const hash = window.location.hash.replace('#', '').trim();
        if (hash === 'admin') {
            this.navigateView('inicio');
            if (typeof Admin !== 'undefined') Admin.openDashboard();
        } else if (hash) {
            this.navigateView(hash);
        } else {
            this.navigateView('inicio');
        }

        window.addEventListener('hashchange', () => {
            const h = window.location.hash.replace('#', '').trim();
            if (h === 'admin') {
                if (typeof Admin !== 'undefined') Admin.openDashboard();
            } else if (h) {
                this.navigateView(h);
            }
        });
    },

    /**
     * Generador de Destellos de Oro Ambiental.
     */
    createGoldDust() {
        let container = document.getElementById('gold-dust-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'gold-dust-container';
            container.className = 'gold-dust-container';
            document.body.appendChild(container);
        }

        container.innerHTML = '';
        const sparkleCount = window.innerWidth < 768 ? 14 : 26;

        for (let i = 0; i < sparkleCount; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'gold-sparkle';

            const size = Math.random() * 4 + 2;
            const left = Math.random() * 100;
            const duration = Math.random() * 8 + 10;
            const delay = -1 * (Math.random() * duration);

            sparkle.style.width = `${size}px`;
            sparkle.style.height = `${size}px`;
            sparkle.style.left = `${left}vw`;
            sparkle.style.animationDuration = `${duration}s`;
            sparkle.style.animationDelay = `${delay}s`;

            container.appendChild(sparkle);
        }
    },

    initTheme() {
        this.createGoldDust();
        this.initSpotlightEffect();
        this.initFloatingNavbar();
    },

    /**
     * Mide la altura real del header flotante (logo + nav + acciones, que puede
     * variar por breakpoint o al cargar las fuentes web) y la escribe en la
     * variable --header-height-desktop para que `main { padding-top }` nunca
     * quede desincronizado ni el contenido se tape debajo del header.
     */
    syncHeaderHeight() {
        const header = document.getElementById('floating-island-wrapper');
        if (!header) return;

        const rect = header.getBoundingClientRect();
        const totalHeight = Math.ceil(rect.top + rect.height);
        document.documentElement.style.setProperty('--header-height-desktop', `${totalHeight}px`);

        if (!this._headerResizeBound) {
            this._headerResizeBound = true;
            let resizeTimer;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(() => this.syncHeaderHeight(), 150);
            }, { passive: true });
        }
    },

    /**
     * Menú móvil/tablet: el pill de navegación no entra completo bajo ~1120px
     * (ver .nav-toggle-btn en main.css), así que se colapsa en un desplegable
     * accionado por un botón hamburguesa.
     */
    toggleMobileNav(forceOpen) {
        const menu = document.getElementById('nav-menu');
        const btn = document.getElementById('nav-toggle-btn');
        if (!menu || !btn) return;

        const shouldOpen = typeof forceOpen === 'boolean' ? forceOpen : !menu.classList.contains('is-open');
        menu.classList.toggle('is-open', shouldOpen);
        btn.setAttribute('aria-expanded', String(shouldOpen));
    },

    initMobileNav() {
        const menu = document.getElementById('nav-menu');
        const toggleBtn = document.getElementById('nav-toggle-btn');
        if (!menu || !toggleBtn) return;

        menu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => this.toggleMobileNav(false));
        });

        document.addEventListener('click', (e) => {
            if (!menu.classList.contains('is-open')) return;
            if (menu.contains(e.target) || toggleBtn.contains(e.target)) return;
            this.toggleMobileNav(false);
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.toggleMobileNav(false);
        });
    },

    showToast(message, type = 'info', title = '', duration = 4000) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const titles = { success: 'Excelente', error: 'Atención', info: 'Información' };
        const displayTitle = title || titles[type] || 'Notificación';

        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-title">${Security.escapeHTML(displayTitle)}</div>
                <div class="toast-message">${Security.escapeHTML(message)}</div>
            </div>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => {
                if (toast.parentNode) toast.remove();
            }, 300);
        }, duration);
    },

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    },

    closeModal(modalId) {
        if (modalId) {
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.remove('active');
        } else {
            document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
        }
        document.body.style.overflow = '';
    }
};

/**
 * ==============================================================================
 * HERO 3D SHOWCASE INTERACTIVO (MANIQUÍES CALEB)
 * ==============================================================================
 */
const Hero3D = {
    currentModel: 'aura',
    models: {
        aura: {
            name: 'Aura Femenino 1.78m — Oro Espejo',
            image: '/assets/images/mannequin-aura.png',
            badge: 'Edición Oro Reflejante'
        },
        noir: {
            name: 'Velvet Noir 1.85m — Negro Satinado',
            image: '/assets/images/mannequin-noir.png',
            badge: 'Acabado Negro Velvet Mate'
        },
        busto: {
            name: 'Busto Sastre Francés — Lino & Roble',
            image: '/assets/images/mannequin-busto.png',
            badge: 'Lino Natural Cosido a Mano'
        },
        titan: {
            name: 'Titán Masculino 1.88m — Acabado Platino',
            image: '/assets/images/mannequin-titan.png',
            badge: 'Alta Densidad & Facción Abstracta'
        }
    },

    targetX: 0,
    targetY: 0,
    currentX: 0,
    currentY: 0,
    isHovered: false,
    animating: false,

    init() {
        const stage = document.getElementById('hero-3d-interactive-stage');
        const viewport = document.getElementById('hero-mannequin-viewport');
        if (!stage || !viewport) return;

        const updateTilt = () => {
            if (this.animating) {
                this.currentX += (this.targetX - this.currentX) * 0.08;
                this.currentY += (this.targetY - this.currentY) * 0.08;

                const rotateY = (this.currentX * 12).toFixed(2);
                const rotateX = (-this.currentY * 8).toFixed(2);
                viewport.style.transform = `perspective(1200px) rotateY(${rotateY}deg) rotateX(${rotateX}deg) translateZ(14px)`;

                if (Math.abs(this.targetX - this.currentX) > 0.001 || Math.abs(this.targetY - this.currentY) > 0.001 || this.isHovered) {
                    requestAnimationFrame(updateTilt);
                } else {
                    this.animating = false;
                }
            }
        };

        stage.addEventListener('mousemove', (e) => {
            const rect = stage.getBoundingClientRect();
            this.targetX = (e.clientX - rect.left) / rect.width - 0.5;
            this.targetY = (e.clientY - rect.top) / rect.height - 0.5;
            this.isHovered = true;
            if (!this.animating) {
                this.animating = true;
                requestAnimationFrame(updateTilt);
            }
        });

        stage.addEventListener('mouseleave', () => {
            this.targetX = 0;
            this.targetY = 0;
            this.isHovered = false;
            if (!this.animating) {
                this.animating = true;
                requestAnimationFrame(updateTilt);
            }
        });
    },

    selectModel(key) {
        const data = this.models[key];
        if (!data) return;
        this.currentModel = key;

        document.querySelectorAll('.model-pill').forEach(btn => btn.classList.remove('active'));
        const activeBtn = document.getElementById(`btn-model-${key}`);
        if (activeBtn) activeBtn.classList.add('active');

        // El maniquí del hero está partido en 3 franjas (ver .mannequin-slice
        // en main.css); cada franja ya usa su propio transform para recortar
        // su tercio de la imagen, así que el cambio de modelo solo cruza en
        // opacidad la caja completa y reemplaza el src de las 3 <img>.
        const stage = document.getElementById('mannequin-explode-stage');
        const slices = document.querySelectorAll('#mannequin-explode-stage .slice-img');
        if (!stage || !slices.length) return;

        stage.style.opacity = '0';
        setTimeout(() => {
            slices.forEach(img => { img.src = data.image; });
            stage.style.opacity = '1';
        }, 180);
    }
};

window.UI = UI;
window.Hero3D = Hero3D;
