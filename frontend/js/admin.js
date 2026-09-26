/**
 * Panel de Administración Interactivo y Seguro para Maniquí Studio.
 * Requiere autenticación mediante Token seguro para realizar operaciones sobre la base de datos.
 */

const Admin = {
    /**
     * Inicializa el panel administrativo y los eventos.
     */
    async init() {
        this.setupLoginForm();
        this.setupNewProductForm();
        this.setupTabs();
    },

    /**
     * Abre el modal de inicio de sesión o directamente el panel si la sesión está activa.
     */
    async openDashboard() {
        const token = API.getAdminToken();
        if (!token) {
            UI.openModal('modal-admin-login');
            return;
        }

        try {
            await API.verifyAdminSession();
            UI.openModal('modal-admin-dashboard');
            await this.loadStats();
            await this.loadAdminProducts();
        } catch (error) {
            API.clearAdminToken();
            UI.openModal('modal-admin-login');
        }
    },

    /**
     * Configura el formulario de inicio de sesión administrativo.
     */
    setupLoginForm() {
        const form = document.getElementById('admin-login-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const passwordInput = document.getElementById('admin-password');
            const password = passwordInput?.value.trim();

            if (!password) {
                return UI.showToast('Por favor ingrese la contraseña.', 'error');
            }

            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerText = 'Verificando credenciales...';
            }

            try {
                const res = await API.loginAdmin(password);
                if (res.success && res.data.token) {
                    API.setAdminToken(res.data.token);
                    UI.showToast('Acceso autorizado al panel de control.', 'success', 'Bienvenido Administrador');
                    form.reset();
                    UI.closeModal('modal-admin-login');
                    UI.openModal('modal-admin-dashboard');
                    await this.loadStats();
                    await this.loadAdminProducts();
                }
            } catch (error) {
                UI.showToast(error.message, 'error', 'Error de Autenticación');
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerText = 'Iniciar Sesión Segura';
                }
            }
        });
    },

    /**
     * Cierra la sesión de administrador.
     */
    logout() {
        API.logoutAdmin();
        UI.closeModal('modal-admin-dashboard');
        UI.showToast('Sesión de administrador cerrada correctamente.', 'info', 'Sesión');
    },

    /**
     * Configura el cambio entre pestañas del panel admin.
     */
    setupTabs() {
        const tabs = document.querySelectorAll('.admin-tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                const target = tab.dataset.adminTab;
                document.querySelectorAll('.admin-tab-content').forEach(c => c.style.display = 'none');

                const targetContent = document.getElementById(`admin-tab-${target}`);
                if (targetContent) targetContent.style.display = 'block';

                if (target === 'products') this.loadAdminProducts();
                if (target === 'messages') this.loadMessages();
                if (target === 'claims') this.loadClaims();
            });
        });
    },

    /**
     * Carga estadísticas del sistema.
     */
    async loadStats() {
        try {
            const res = await API.getStats();
            if (res.success && res.data) {
                const s = res.data;
                const setEl = (id, val) => {
                    const el = document.getElementById(id);
                    if (el) el.innerText = val;
                };
                setEl('stat-total-products', s.products_total);
                setEl('stat-total-categories', s.categories_total);
                setEl('stat-total-messages', s.messages_total);
                setEl('stat-pending-claims', s.claims_pending);
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    },

    /**
     * Carga la tabla de productos para administración.
     */
    async loadAdminProducts() {
        const container = document.getElementById('admin-products-table-body');
        if (!container) return;

        container.innerHTML = '<tr><td colspan="6" style="text-align:center;">Cargando inventario...</td></tr>';

        try {
            const res = await API.getProducts();
            if (res.success) {
                if (res.data.length === 0) {
                    container.innerHTML = '<tr><td colspan="6" style="text-align:center;">No hay productos registrados.</td></tr>';
                    return;
                }

                container.innerHTML = res.data.map(p => `
                    <tr>
                        <td><strong>#${p.id}</strong></td>
                        <td>
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <img src="${Security.escapeHTML(p.image_url)}" alt="${Security.escapeHTML(p.name)}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">
                                <span>${Security.escapeHTML(p.name)}</span>
                            </div>
                        </td>
                        <td>${Security.escapeHTML(p.category_name || 'Sin Categoría')}</td>
                        <td><strong>${CONFIG.CURRENCY_SYMBOL}${parseFloat(p.price).toFixed(2)}</strong></td>
                        <td><span class="badge ${p.stock > 0 ? 'badge-success' : 'badge-danger'}">${p.stock} un.</span></td>
                        <td>
                            <button class="btn btn-danger" style="padding: 0.35rem 0.75rem; font-size: 0.75rem;" onclick="Admin.deleteProduct(${p.id})">
                                Eliminar
                            </button>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            container.innerHTML = `<tr><td colspan="6" style="color:var(--state-danger);text-align:center;">Error: ${Security.escapeHTML(error.message)}</td></tr>`;
        }
    },

    /**
     * Configura el formulario para añadir un nuevo producto.
     */
    setupNewProductForm() {
        const form = document.getElementById('admin-new-product-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('new-prod-name')?.value.trim();
            const categoryId = parseInt(document.getElementById('new-prod-category')?.value || '1');
            const price = parseFloat(document.getElementById('new-prod-price')?.value) || 0.0;
            const stock = parseInt(document.getElementById('new-prod-stock')?.value) || 1;
            const description = document.getElementById('new-prod-desc')?.value.trim();
            const material = document.getElementById('new-prod-material')?.value.trim();
            const color = document.getElementById('new-prod-color')?.value.trim();
            const dimensions = document.getElementById('new-prod-dimensions')?.value.trim();
            const imageUrl = document.getElementById('new-prod-image')?.value.trim() || '/assets/productos/maniqui-femenino-abstracto-blanco.webp';
            const isFeatured = document.getElementById('new-prod-featured')?.checked || false;

            if (!name) return UI.showToast('El nombre del maniquí es obligatorio.', 'error');
            if (!description) return UI.showToast('La descripción es obligatoria.', 'error');
            if (price <= 0) return UI.showToast('Ingrese un precio válido.', 'error');

            const payload = {
                name,
                category_id: categoryId,
                price,
                stock,
                description,
                material,
                color,
                dimensions,
                image_url: imageUrl,
                is_featured: isFeatured
            };

            try {
                const res = await API.createProduct(payload);
                if (res.success) {
                    UI.showToast('¡Maniquí añadido exitosamente a la base de datos!', 'success', 'Inventario');
                    form.reset();
                    await this.loadAdminProducts();
                    await this.loadStats();
                    Catalog.loadProducts();
                }
            } catch (error) {
                UI.showToast(error.message, 'error', 'Error al crear');
            }
        });
    },

    /**
     * Elimina un producto.
     */
    async deleteProduct(productId) {
        if (!confirm('¿Está seguro de eliminar este producto del catálogo?')) return;

        try {
            const res = await API.deleteProduct(productId);
            if (res.success) {
                UI.showToast('Producto eliminado correctamente.', 'success');
                await this.loadAdminProducts();
                await this.loadStats();
                Catalog.loadProducts();
            }
        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    /**
     * Carga mensajes de contacto en la pestaña admin.
     */
    async loadMessages() {
        const container = document.getElementById('admin-messages-list');
        if (!container) return;

        container.innerHTML = '<p style="color: var(--text-secondary);">Cargando mensajes...</p>';

        try {
            const res = await API.getMessages();
            if (res.success) {
                if (res.data.length === 0) {
                    container.innerHTML = '<p style="color: var(--text-secondary);">Bandeja de entrada vacía.</p>';
                    return;
                }

                container.innerHTML = res.data.map(m => `
                    <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); padding: 1.25rem; border-radius: var(--radius-md); margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong>${Security.escapeHTML(m.name)} &lt;${Security.escapeHTML(m.email)}&gt;</strong>
                            <span style="font-size: 0.75rem; color: var(--text-muted);">${new Date(m.created_at).toLocaleString()}</span>
                        </div>
                        <div style="font-size: 0.9rem; font-weight: 600; color: var(--accent-gold); margin-bottom: 0.5rem;">Asunto: ${Security.escapeHTML(m.subject)}</div>
                        <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5;">${Security.escapeHTML(m.message)}</p>
                        ${m.phone ? `<div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">Teléfono / WhatsApp: ${Security.escapeHTML(m.phone)}</div>` : ''}
                    </div>
                `).join('');
            }
        } catch (error) {
            container.innerHTML = `<p style="color: var(--state-danger);">Error: ${Security.escapeHTML(error.message)}</p>`;
        }
    },

    /**
     * Carga las reclamaciones en la pestaña admin.
     */
    async loadClaims() {
        const container = document.getElementById('admin-claims-list');
        if (!container) return;

        container.innerHTML = '<p style="color: var(--text-secondary);">Cargando registro del Libro de Reclamaciones...</p>';

        try {
            const res = await API.getAllClaims();
            if (res.success) {
                if (res.data.length === 0) {
                    container.innerHTML = '<p style="color: var(--text-secondary);">No hay reclamaciones registradas.</p>';
                    return;
                }

                container.innerHTML = res.data.map(c => `
                    <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); padding: 1.25rem; border-radius: var(--radius-md); margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div>
                                <span class="claim-receipt-code" style="font-size: 1rem; padding: 0.2rem 0.5rem; margin: 0 0.5rem 0 0;">${Security.escapeHTML(c.claim_code)}</span>
                                <strong>${Security.escapeHTML(c.full_name)}</strong>
                            </div>
                            <span class="badge ${c.status === 'Pendiente' ? 'badge-warning' : 'badge-success'}">${Security.escapeHTML(c.status)}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin-top: 0.5rem;">
                            <p><strong>Tipo:</strong> ${Security.escapeHTML(c.claim_type)} | <strong>Fecha:</strong> ${new Date(c.created_at).toLocaleString()}</p>
                            <p><strong>Bien Contratado:</strong> ${Security.escapeHTML(c.contracted_good)} (${CONFIG.CURRENCY_SYMBOL}${parseFloat(c.amount_claimed).toFixed(2)})</p>
                            <p><strong>Descripción:</strong> ${Security.escapeHTML(c.claim_description)}</p>
                            <p><strong>Pedido del Consumidor:</strong> ${Security.escapeHTML(c.consumer_request)}</p>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            container.innerHTML = `<p style="color: var(--state-danger);">Error: ${Security.escapeHTML(error.message)}</p>`;
        }
    }
};

window.Admin = Admin;
