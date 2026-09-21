/**
 * Utilidades de Seguridad y Sanitización para el Frontend.
 * Previene vulnerabilidades de Cross-Site Scripting (XSS) y valida datos antes del envío.
 */

const Security = {
    /**
     * Escapa caracteres HTML especiales para evitar inyecciones XSS.
     * @param {string|number|null} str
     * @returns {string}
     */
    escapeHTML(str) {
        if (str === null || str === undefined) return '';
        const s = String(str);
        return s
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    /**
     * Valida sintaxis de correo electrónico.
     * @param {string} email
     * @returns {boolean}
     */
    isValidEmail(email) {
        if (!email || email.length > 254) return false;
        const re = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
        return re.test(email.trim());
    },

    /**
     * Valida números de teléfono.
     * @param {string} phone
     * @returns {boolean}
     */
    isValidPhone(phone) {
        if (!phone) return true;
        const re = /^[+0-9\s\-()]{6,20}$/;
        return re.test(phone.trim());
    },

    /**
     * Valida números de documento (DNI, CE, RUC, Pasaporte).
     * @param {string} doc
     * @returns {boolean}
     */
    isValidDoc(doc) {
        if (!doc) return false;
        const re = /^[a-zA-Z0-9\-]{5,20}$/;
        return re.test(doc.trim());
    }
};

window.Security = Security;
