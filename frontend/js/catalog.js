/**
 * Controlador del Catálogo 3D con Proporción 60/40 y Sidebar Derecho.
 * MANIQUÍES CALEB - Alta Costura (100% Profesional, Sin Emojis).
 */

const WHATSAPP_SVG_ICON = `<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>`;

const SVG_ICONS = {
    'all': `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>`,
    'maniquies-femeninos': `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a5 5 0 100 10 5 5 0 000-10zm0 10v10m-4-6h8"/></svg>`,
    'maniquies-masculinos': `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6m0-6L14 10m-4 11a7 7 0 100-14 7 7 0 000 14z"/></svg>`,
    'bustos-sastreria': `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3h12l-2 9H8L6 3zm6 9v9m-4 0h8"/></svg>`,
    'exhibidores-colgantes': `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3a3 3 0 00-3 3c0 1.5 1 2.5 3 3.5v1.5L2 19h20L12 11V6"/></svg>`,
    'maniquies-infantiles': `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/></svg>`,
    'accesorios-bases': `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="14" width="18" height="8" rx="2"/><path d="M12 2v12"/></svg>`
};

const Catalog = {
    products: [],
    categories: [],
    selectedCategory: 'all',
    searchQuery: '',

    viewMode: 'carousel', // 'carousel' o 'grid'

    async init() {
        this.bindEvents();
        await this.loadData();
    },

    bindEvents() {
        const searchInput = document.getElementById('catalog-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.trim().toLowerCase();
                this.renderProducts();
            });
        }
    },

    async loadData() {
        const container = document.getElementById('products-grid');
        if (container) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 4rem;">
                    <p style="color: var(--text-secondary); font-size: 1.05rem;">Cargando catálogo de 12 maniquíes y exhibidores...</p>
                </div>
            `;
        }

        try {
            const [catsRes, prodsRes] = await Promise.all([
                API.getCategories(),
                API.getProducts()
            ]);

            if (catsRes.success) {
                this.categories = catsRes.data;
                this.renderCategories();
            }

            if (prodsRes.success) {
                this.products = prodsRes.data;
                // Pre-decodificación en memoria GPU para que el carrusel aparezca 100% instantáneo sin lag tras F5
                this.products.forEach(p => {
                    if (p.image_url) {
                        const img = new Image();
                        img.src = p.image_url;
                        if (img.decode) img.decode().catch(() => {});
                    }
                });
                this.renderProducts();
                this.renderCarousel();
            }
        } catch (error) {
            if (container) {
                container.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--state-danger);">
                        <p>No se pudo conectar con el catálogo. Verifique su conexión.</p>
                    </div>
                `;
            }
        }
    },

    setViewMode(mode) {
        this.viewMode = mode;
        const carouselView = document.getElementById('catalog-carousel-view');
        const gridView = document.getElementById('products-grid');
        const sidebarToggleLabel = document.getElementById('sidebar-toggle-mode-label');
        const sidebarToggleBtn = document.getElementById('btn-toggle-catalog-mode');
        const titleEl = document.getElementById('catalog-section-title');
        const subtitleEl = document.getElementById('catalog-section-subtitle');

        if (mode === 'carousel') {
            if (carouselView) carouselView.style.display = 'flex';
            if (gridView) gridView.style.display = 'none';
            if (sidebarToggleLabel) sidebarToggleLabel.textContent = 'Ver Todos en Lista';
            if (sidebarToggleBtn) sidebarToggleBtn.setAttribute('title', 'Cambiar a Vista en Lista');
            if (titleEl) titleEl.innerHTML = 'Catálogo de Maniquíes & <span class="gold-text">Colgantes de Exhibición</span>';
            if (subtitleEl) subtitleEl.innerHTML = 'Encuentra maniquíes de cuerpo entero, medios cuerpos, bustos y colgantes resistentes para exhibir la ropa de tu tienda con la mejor presentación.';
        } else {
            if (carouselView) carouselView.style.display = 'none';
            if (gridView) {
                gridView.style.display = 'grid';
                this.renderProducts();
            }
            if (sidebarToggleLabel) sidebarToggleLabel.textContent = 'Ver en Galería 3D';
            if (sidebarToggleBtn) sidebarToggleBtn.setAttribute('title', 'Cambiar a Galería 3D');
            if (titleEl) titleEl.innerHTML = 'Lista Completa de <span class="gold-text">Maniquíes y Colgantes</span>';
            if (subtitleEl) subtitleEl.innerHTML = 'Consulta medidas, acabados y precios al por mayor y menor para equipar tu tienda con stock disponible.';
        }
    },

    toggleViewMode() {
        const newMode = this.viewMode === 'carousel' ? 'grid' : 'carousel';
        this.setViewMode(newMode);
    },

    getWheelRadius() {
        const width = window.innerWidth;
        if (width < 400) return 135;
        if (width < 600) return 165;
        if (width < 900) return 215;
        if (width < 1200) return 265;
        return 320;
    },

    updateWheelTransforms() {
        const radius = this.getWheelRadius();
        document.querySelectorAll('.wheel-3d-item').forEach(item => {
            const angle = item.getAttribute('data-angle');
            if (angle !== null) {
                item.style.transform = `rotateY(${angle}deg) translateZ(${radius}px)`;
            }
        });
    },

    renderCarousel() {
        if (!this.products || this.products.length === 0) return;

        // Distribución perfecta de los 12 productos en 2 ruedas cinemáticas de 6 items
        const row1 = this.products.slice(0, 6);
        const row2 = this.products.slice(6, 12);

        const radius = this.getWheelRadius();

        // Ángulo para 6 elementos en un círculo completo de 360 grados (360 / 6 = 60 grados)
        const createWheelItemsHTML = (productsList) => {
            return productsList.map((p, index) => {
                const angle = index * 60;
                return `
                    <div class="wheel-3d-item" data-angle="${angle}" style="transform: rotateY(${angle}deg) translateZ(${radius}px);" onclick="Catalog.showProductDetail(${p.id})">
                        <img src="${Security.escapeHTML(p.image_url)}" alt="${Security.escapeHTML(p.name)}" decoding="async" loading="lazy">
                    </div>
                `;
            }).join('');
        };

        const r1 = document.getElementById('carousel-row-1');
        const r2 = document.getElementById('carousel-row-2');

        if (r1) r1.innerHTML = createWheelItemsHTML(row1);
        if (r2) r2.innerHTML = createWheelItemsHTML(row2);

        this.enableDragToScroll();
        this.startContinuousWheelAnimation();

        if (!this.resizeListenerAdded) {
            let resizeTimer = null;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(() => {
                    if (this.viewMode === 'carousel') {
                        this.updateWheelTransforms();
                    }
                }, 100);
            });
            this.resizeListenerAdded = true;
        }
    },

    wheelAnimationId: null,
    ringAngles: [0, 0],
    ringVelocities: [0, 0],
    ringSpeeds: [6.0, -6.0], // Grados por segundo (giro suave y continuo)
    lastFrameTime: null,

    startContinuousWheelAnimation() {
        if (this.wheelAnimationId) return;

        const ringEls = [
            document.getElementById('carousel-row-1'),
            document.getElementById('carousel-row-2')
        ];

        const loop = (timestamp) => {
            if (!this.lastFrameTime) this.lastFrameTime = timestamp;
            const dt = Math.min((timestamp - this.lastFrameTime) / 1000, 0.1);
            this.lastFrameTime = timestamp;

            ringEls.forEach((ring, i) => {
                if (ring) {
                    const movement = (this.ringSpeeds[i] * dt) + this.ringVelocities[i];
                    this.ringAngles[i] = (this.ringAngles[i] + movement) % 360;
                    this.ringVelocities[i] *= 0.95; // Fricción suave y amortiguada
                    if (Math.abs(this.ringVelocities[i]) < 0.0001) this.ringVelocities[i] = 0;
                    ring.style.transform = `rotateY(${this.ringAngles[i].toFixed(3)}deg)`;
                }
            });
            this.wheelAnimationId = requestAnimationFrame(loop);
        };

        if (!this.visibilityListenerAdded) {
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    if (this.wheelAnimationId) {
                        cancelAnimationFrame(this.wheelAnimationId);
                        this.wheelAnimationId = null;
                        this.lastFrameTime = null;
                    }
                } else if (this.viewMode === 'carousel') {
                    this.lastFrameTime = null;
                    this.startContinuousWheelAnimation();
                }
            });
            this.visibilityListenerAdded = true;
        }

        this.wheelAnimationId = requestAnimationFrame(loop);
    },

    enableDragToScroll() {
        const ringIds = ['carousel-row-1', 'carousel-row-2'];
        ringIds.forEach((id, i) => {
            const ring = document.getElementById(id);
            if (!ring || ring.dataset.dragEnabled) return;
            ring.dataset.dragEnabled = 'true';

            let isDown = false;
            let lastX = 0;

            // Mouse Events (PC / Mac / Laptops)
            ring.addEventListener('mousedown', (e) => {
                isDown = true;
                lastX = e.pageX;
                ring.style.cursor = 'grabbing';
            });

            window.addEventListener('mouseup', () => {
                if (isDown) {
                    isDown = false;
                    ring.style.cursor = 'grab';
                }
            });

            ring.addEventListener('mousemove', (e) => {
                if (!isDown) return;
                e.preventDefault();
                const rawDelta = e.pageX - lastX;
                lastX = e.pageX;
                const clampedDelta = Math.max(-14, Math.min(14, rawDelta));
                this.ringAngles[i] += clampedDelta * 0.14;
                this.ringVelocities[i] = Math.max(-0.4, Math.min(0.4, clampedDelta * 0.03));
            });

            // Touch Events (Móviles Android / iPhone / iPad)
            ring.addEventListener('touchstart', (e) => {
                if (!e.touches || e.touches.length === 0) return;
                isDown = true;
                lastX = e.touches[0].pageX;
            }, { passive: true });

            ring.addEventListener('touchmove', (e) => {
                if (!isDown || !e.touches || e.touches.length === 0) return;
                const currentX = e.touches[0].pageX;
                const rawDelta = currentX - lastX;
                lastX = currentX;
                const clampedDelta = Math.max(-14, Math.min(14, rawDelta));
                this.ringAngles[i] += clampedDelta * 0.16;
                this.ringVelocities[i] = Math.max(-0.45, Math.min(0.45, clampedDelta * 0.035));
            }, { passive: true });

            ring.addEventListener('touchend', () => {
                isDown = false;
            }, { passive: true });

            // Rueda de mouse horizontal
            ring.parentElement.addEventListener('wheel', (e) => {
                if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
                    e.preventDefault();
                    const delta = Math.max(-8, Math.min(8, e.deltaX));
                    this.ringVelocities[i] -= delta * 0.015;
                }
            }, { passive: false });
        });
    },

    renderCategories() {
        const container = document.getElementById('sidebar-category-list');
        if (!container) return;

        let html = `
            <button class="sidebar-cat-btn ${this.selectedCategory === 'all' ? 'active' : ''}" onclick="Catalog.filterCategory('all')">
                <span class="cat-icon-svg">${SVG_ICONS['all']}</span>
                <span>Todos los Modelos</span>
            </button>
        `;

        this.categories.forEach(cat => {
            const iconSvg = SVG_ICONS[cat.slug] || SVG_ICONS['all'];
            html += `
                <button class="sidebar-cat-btn ${this.selectedCategory === cat.slug ? 'active' : ''}" onclick="Catalog.filterCategory('${cat.slug}')">
                    <span class="cat-icon-svg">${iconSvg}</span>
                    <span>${Security.escapeHTML(cat.name)}</span>
                </button>
            `;
        });

        container.innerHTML = html;
    },

    filterCategory(slug) {
        this.selectedCategory = slug;
        this.renderCategories();
        this.renderProducts();
    },

    renderProducts() {
        const container = document.getElementById('products-grid');
        if (!container) return;

        let filtered = this.products;

        if (this.selectedCategory !== 'all') {
            filtered = filtered.filter(p => p.category_slug === this.selectedCategory);
        }

        if (this.searchQuery) {
            filtered = filtered.filter(p => 
                (p.name && p.name.toLowerCase().includes(this.searchQuery)) ||
                (p.material && p.material.toLowerCase().includes(this.searchQuery)) ||
                (p.color && p.color.toLowerCase().includes(this.searchQuery)) ||
                (p.sku && p.sku.toLowerCase().includes(this.searchQuery)) ||
                (p.description && p.description.toLowerCase().includes(this.searchQuery))
            );
        }

        if (filtered.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 4rem; background: var(--bg-wine-card); border-radius: var(--radius-lg); border: 1px solid var(--border-subtle);">
                    <p style="font-size: 1.2rem; color: var(--accent-gold); margin-bottom: 0.5rem;">No se encontraron modelos con ese criterio.</p>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Prueba con otra búsqueda o selecciona una categoría en el panel derecho.</p>
                    <button class="btn btn-secondary" onclick="Catalog.resetFilters()">Ver todos los modelos</button>
                </div>
            `;
            return;
        }

        container.innerHTML = filtered.map(p => {
            const escapedName = (p.name || '').replace(/'/g, "\\'");
            const escapedSku = (p.sku || '').replace(/'/g, "\\'");

            return `
                <div class="product-card-3d" data-id="${p.id}" onmousemove="Catalog.handleTilt(event, this)" onmouseleave="Catalog.resetTilt(this)">
                    <div class="product-img-box">
                        <img src="${Security.escapeHTML(p.image_url)}" alt="${Security.escapeHTML(p.name)}" loading="lazy">
                    </div>

                    <div class="product-category-script">
                        ${Security.escapeHTML(p.category_name || 'Alta Costura')}
                    </div>

                    <h3 class="product-title-cinzel">
                        ${Security.escapeHTML(p.name)}
                    </h3>

                    <p class="product-desc-clean">
                        ${Security.escapeHTML(p.description)}
                    </p>

                    <div class="product-specs-clean">
                        <span>Material: ${Security.escapeHTML(p.material || 'Fibra')}</span>
                        <span class="spec-dot">•</span>
                        <span>Color: ${Security.escapeHTML(p.color || 'Personalizado')}</span>
                    </div>

                    <div class="product-card-actions">
                        <button type="button" class="btn product-btn-wa" onclick="Catalog.orderProduct('${escapedName}', '${escapedSku}')">
                            <span>Pedir WhatsApp</span>
                        </button>
                        <button type="button" class="btn product-btn-ficha" onclick="Catalog.showProductDetail(${p.id})">
                            <span>Ficha Técnica</span>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    },

    orderProduct(name, sku) {
        const text = `Hola Novedades Caleb, deseo consultar precio y disponibilidad de: ${name} (SKU: ${sku}) en Stand 3 Galería La Exitosa.`;
        UI.openWhatsApp(text);
    },

    resetFilters() {
        this.selectedCategory = 'all';
        this.searchQuery = '';
        const searchInput = document.getElementById('catalog-search-input');
        if (searchInput) searchInput.value = '';
        this.renderCategories();
        this.renderProducts();
    },

    handleTilt(e, card) {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = ((y - centerY) / centerY) * -1.8;
        const rotateY = ((x - centerX) / centerX) * 1.8;

        card.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    },

    resetTilt(card) {
        card.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) translateY(0)';
    },

    showProductDetail(productId) {
        const product = this.products.find(p => p.id === productId);
        if (!product) return;

        const body = document.getElementById('modal-product-detail-body');
        if (body) {
            const escapedName = (product.name || '').replace(/'/g, "\\'");
            const escapedSku = (product.sku || '').replace(/'/g, "\\'");

            body.innerHTML = `
                <div class="product-modal-grid">
                    <div style="background: rgba(0, 0, 0, 0.4); padding: 1.5rem; border-radius: var(--radius-md); text-align: center; border: 1px solid var(--border-gold);">
                        <img src="${Security.escapeHTML(product.image_url)}" alt="${Security.escapeHTML(product.name)}" style="max-height: 320px; max-width: 100%; object-fit: contain;">
                    </div>
                    <div>
                        <span class="badge badge-success" style="margin-bottom: 0.5rem;">${Security.escapeHTML(product.category_name || 'Alta Costura')}</span>
                        <h3 style="font-family: var(--font-heading); font-size: 1.5rem; font-weight: 700; color: var(--accent-gold); margin-bottom: 0.5rem;">${Security.escapeHTML(product.name)}</h3>
                        <p style="color: var(--text-secondary); font-size: 0.92rem; line-height: 1.6; margin-bottom: 1.25rem;">${Security.escapeHTML(product.description)}</p>
                        
                        <div style="background: var(--bg-surface-elevated); padding: 1rem; border-radius: var(--radius-md); font-size: 0.85rem; line-height: 1.8; border: 1px solid var(--border-subtle); margin-bottom: 1.5rem;">
                            <div><strong>Código SKU:</strong> ${Security.escapeHTML(product.sku)}</div>
                            <div><strong>Material:</strong> ${Security.escapeHTML(product.material || 'Fibra reforzada')}</div>
                            <div><strong>Color / Acabado:</strong> ${Security.escapeHTML(product.color || 'Personalizado')}</div>
                            <div><strong>Medidas:</strong> ${Security.escapeHTML(product.dimensions || 'Estándar')}</div>
                            <div><strong>Garantía:</strong> 1 Año de Estructura Comercial</div>
                        </div>

                        <button type="button" class="btn modal-btn-cotizar" onclick="Catalog.orderProduct('${escapedName}', '${escapedSku}')" style="width: 100%; padding: 1.1rem; font-size: 1rem; display: flex; align-items: center; justify-content: center; gap: 0.6rem; font-weight: 700; border-radius: var(--radius-md); cursor: pointer;">
                            ${WHATSAPP_SVG_ICON}
                            <span>Consultar Precio & Cotizar al WhatsApp</span>
                        </button>
                    </div>
                </div>
            `;
            UI.openModal('modal-product-detail');
        }
    }
};

window.Catalog = Catalog;
