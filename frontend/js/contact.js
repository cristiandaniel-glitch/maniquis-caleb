/**
 * Controlador de Formulario de Contacto y Suscripción al Boletín.
 */

const Contact = {
    /**
     * Inicializa los formularios de contacto y newsletter.
     */
    init() {
        this.setupContactForm();
        this.setupNewsletterForm();
    },

    setupContactForm() {
        const form = document.getElementById('contact-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('contact-name')?.value.trim();
            const email = document.getElementById('contact-email')?.value.trim();
            const phone = document.getElementById('contact-phone')?.value.trim();
            const subject = document.getElementById('contact-subject')?.value.trim();
            const message = document.getElementById('contact-message')?.value.trim();

            if (!name || name.length < 2) return UI.showToast('Por favor ingrese su nombre.', 'error');
            if (!Security.isValidEmail(email)) return UI.showToast('Por favor ingrese un correo válido.', 'error');
            if (!subject) return UI.showToast('Por favor ingrese el asunto de su consulta.', 'error');
            if (!message || message.length < 5) return UI.showToast('Por favor escriba su mensaje con detalle.', 'error');

            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerText = 'Enviando consulta...';
            }

            try {
                const res = await API.sendMessage({ name, email, phone, subject, message });
                if (res.success) {
                    UI.showToast(res.data.message || 'Mensaje enviado exitosamente.', 'success', 'Contacto');
                    form.reset();
                }
            } catch (error) {
                UI.showToast(error.message, 'error', 'Error al enviar');
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerText = 'Enviar Mensaje Directo';
                }
            }
        });
    },

    setupNewsletterForm() {
        const form = document.getElementById('newsletter-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailInput = document.getElementById('newsletter-email');
            const email = emailInput?.value.trim();

            if (!Security.isValidEmail(email)) {
                return UI.showToast('Por favor ingrese un correo electrónico válido.', 'error');
            }

            try {
                const res = await API.subscribeNewsletter(email);
                if (res.success) {
                    UI.showToast(res.data.message, 'success', 'Boletín');
                    emailInput.value = '';
                }
            } catch (error) {
                UI.showToast(error.message, 'error');
            }
        });
    }
};

window.Contact = Contact;
