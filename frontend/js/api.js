/**
 * Cliente de API HTTP para Maniquí Studio.
 * Maneja peticiones REST, inyección de tokens de autenticación y captura de errores.
 */

const API = {
    /**
     * Obtiene el token de administrador guardado en sessionStorage.
     */
    getAdminToken() {
        return sessionStorage.getItem('maniqui_admin_token');
    },

    /**
     * Guarda el token de sesión.
     */
    setAdminToken(token) {
        sessionStorage.setItem('maniqui_admin_token', token);
    },

    /**
     * Elimina el token de sesión.
     */
    clearAdminToken() {
        sessionStorage.removeItem('maniqui_admin_token');
    },

    /**
     * Petición genérica con manejo de cabeceras de autorización y errores.
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise<any>}
     */
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(options.headers || {})
        };

        const token = this.getAdminToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const data = await response.json().catch(() => ({
                success: false,
                error: 'Respuesta inválida del servidor.'
            }));

            if (!response.ok) {
                const errorMessage = data.error || `Error ${response.status}: Solicitud no completada`;
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            console.error(`[API Error] ${endpoint}:`, error.message);
            throw error;
        }
    },

    // --- Autenticación Administrativa ---
    loginAdmin(password) {
        return this.request('/admin/login', {
            method: 'POST',
            body: JSON.stringify({ password })
        });
    },

    verifyAdminSession() {
        return this.request('/admin/verify');
    },

    logoutAdmin() {
        this.clearAdminToken();
    },

    // --- Productos ---
    getProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/products${query ? '?' + query : ''}`);
    },

    getProduct(idOrSlug) {
        return this.request(`/products/${idOrSlug}`);
    },

    createProduct(productData) {
        return this.request('/products', {
            method: 'POST',
            body: JSON.stringify(productData)
        });
    },

    updateProduct(id, productData) {
        return this.request(`/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(productData)
        });
    },

    deleteProduct(id) {
        return this.request(`/products/${id}`, {
            method: 'DELETE'
        });
    },

    // --- Categorías ---
    getCategories() {
        return this.request('/categories');
    },

    // --- Libro de Reclamaciones ---
    submitClaim(claimData) {
        return this.request('/claims', {
            method: 'POST',
            body: JSON.stringify(claimData)
        });
    },

    getClaim(claimCode) {
        return this.request(`/claims/${claimCode}`);
    },

    getAllClaims() {
        return this.request('/claims/all');
    },

    // --- Contacto y Boletín ---
    sendMessage(contactData) {
        return this.request('/contact', {
            method: 'POST',
            body: JSON.stringify(contactData)
        });
    },

    getMessages() {
        return this.request('/messages');
    },

    subscribeNewsletter(email) {
        return this.request('/subscribe', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    },

    // --- Estadísticas y Legal ---
    getStats() {
        return this.request('/stats');
    },

    getLegalInfo() {
        return this.request('/legal');
    }
};

window.API = API;
