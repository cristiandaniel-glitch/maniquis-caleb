/**
 * Gestor de Reseñas y Testimonios de Boutiques (Novedades Caleb).
 * Carga dinámica, puntuación interactiva con estrellas y envío mediante API REST.
 */

const Reviews = {
    selectedRating: 5,
    reviewsList: [],

    init() {
        this.loadReviews();
        this.initRatingStars();
        this.initFormSubmit();
    },

    /**
     * Consulta y renderiza las reseñas desde el backend.
     */
    async loadReviews() {
        const container = document.getElementById('reviews-grid');
        if (!container) return;

        try {
            const res = await API.get('/reviews');
            if (res && res.reviews && res.reviews.length > 0) {
                this.reviewsList = res.reviews;
                this.renderReviews(this.reviewsList);
            }
        } catch (e) {
            console.warn('Cargando reseñas predeterminadas locales.', e);
        }
    },

    /**
     * Renderiza las tarjetas de reseñas en el contenedor.
     */
    renderReviews(list) {
        const container = document.getElementById('reviews-grid');
        if (!container) return;

        container.innerHTML = list.map(rev => {
            const stars = '★'.repeat(rev.rating || 5) + '☆'.repeat(5 - (rev.rating || 5));
            const initials = (rev.name || 'Caleb')
                .split(' ')
                .map(n => n[0])
                .slice(0, 2)
                .join('')
                .toUpperCase() || 'MC';

            return `
                <div class="review-card-luxury" style="background: var(--bg-wine-card); border: 1.5px solid var(--border-gold); border-radius: 24px; padding: 2.25rem; box-shadow: var(--glow-card); display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.3s ease, box-shadow 0.3s ease;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.15rem;">
                            <div style="color: #ffd700; font-size: 1.3rem; letter-spacing: 3px;">${stars}</div>
                            <span style="font-size: 0.78rem; background: rgba(37, 211, 102, 0.15); color: #25D366; border: 1px solid rgba(37, 211, 102, 0.35); padding: 0.25rem 0.65rem; border-radius: 20px; font-weight: 700;">✓ Verificado</span>
                        </div>
                        ${rev.product_model ? `<div style="font-size: 0.8rem; color: var(--accent-gold); font-weight: 600; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">${Security.escapeHTML(rev.product_model)}</div>` : ''}
                        <p style="font-size: 1.02rem; color: var(--text-secondary); line-height: 1.75; font-style: italic; margin-bottom: 1.5rem;">
                            "${Security.escapeHTML(rev.comment)}"
                        </p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem; border-top: 1px solid var(--border-subtle); padding-top: 1.15rem;">
                        <div style="width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-gold), #b88d3b); color: #170206; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.1rem; flex-shrink: 0; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
                            ${initials}
                        </div>
                        <div>
                            <strong style="display: block; color: var(--text-primary); font-size: 1.02rem;">${Security.escapeHTML(rev.name)}</strong>
                            <span style="font-size: 0.85rem; color: var(--accent-gold);">${Security.escapeHTML(rev.boutique)} • ${Security.escapeHTML(rev.city || 'Cusco')}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    /**
     * Inicializa las estrellas de calificación interactiva.
     */
    initRatingStars() {
        const starContainer = document.getElementById('review-rating-stars');
        if (!starContainer) return;

        const starSpans = starContainer.querySelectorAll('.star-item');
        starSpans.forEach(star => {
            star.addEventListener('click', () => {
                const val = parseInt(star.dataset.value, 10) || 5;
                this.setRating(val);
            });

            star.addEventListener('mouseenter', () => {
                const val = parseInt(star.dataset.value, 10) || 5;
                this.previewRating(val);
            });
        });

        starContainer.addEventListener('mouseleave', () => {
            this.previewRating(this.selectedRating);
        });

        this.setRating(5);
    },

    setRating(val) {
        this.selectedRating = val;
        const input = document.getElementById('review-rating-input');
        if (input) input.value = val;

        const ratingText = document.getElementById('review-rating-text');
        const labels = {
            1: "1 Estrella - Regular",
            2: "2 Estrellas - Aceptable",
            3: "3 Estrellas - Bueno",
            4: "4 Estrellas - Muy Bueno",
            5: "5 Estrellas - ¡Excelente Experiencia!"
        };
        if (ratingText) ratingText.textContent = labels[val] || `${val} Estrellas`;

        this.previewRating(val);
    },

    previewRating(val) {
        const starContainer = document.getElementById('review-rating-stars');
        if (!starContainer) return;

        const starSpans = starContainer.querySelectorAll('.star-item');
        starSpans.forEach(star => {
            const starVal = parseInt(star.dataset.value, 10);
            if (starVal <= val) {
                star.style.color = '#ffd700';
                star.style.transform = 'scale(1.15)';
            } else {
                star.style.color = 'rgba(255, 255, 255, 0.25)';
                star.style.transform = 'scale(1)';
            }
        });
    },

    /**
     * Maneja el envío del formulario de reseña.
     */
    initFormSubmit() {
        const form = document.getElementById('modal-review-form-element');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('review-author-name')?.value.trim();
            const boutique = document.getElementById('review-boutique-name')?.value.trim();
            const city = document.getElementById('review-city')?.value.trim() || 'Cusco';
            const product_model = document.getElementById('review-product-model')?.value.trim();
            const comment = document.getElementById('review-comment')?.value.trim();
            const rating = parseInt(document.getElementById('review-rating-input')?.value, 10) || this.selectedRating || 5;

            if (!name || !boutique || !comment) {
                UI.showToast('Por favor completa todos los campos requeridos.', 'warning');
                return;
            }

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerText = 'Publicando Reseña...';
            }

            try {
                const res = await API.post('/reviews', {
                    name,
                    boutique,
                    city,
                    product_model,
                    rating,
                    comment
                });

                if (res && res.status === 'success') {
                    UI.closeModal('modal-review-form');
                    form.reset();
                    this.setRating(5);
                    UI.showToast('¡Gracias! Tu reseña ha sido publicada con éxito.', 'success');

                    // Agregar de inmediato la nueva reseña arriba
                    if (res.review) {
                        this.reviewsList.unshift(res.review);
                        this.renderReviews(this.reviewsList);
                    } else {
                        this.loadReviews();
                    }
                } else {
                    UI.showToast(res.message || 'Error al enviar la reseña.', 'error');
                }
            } catch (err) {
                console.error(err);
                UI.showToast('No se pudo enviar la reseña. Inténtalo nuevamente.', 'error');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = 'Publicar Reseña Oficial';
                }
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Reviews.init();
});
