/**
 * Controlador del Libro de Reclamaciones Virtual para NOVEDADES CALEB.
 * Cumplimiento estricto del Código de Protección y Defensa del Consumidor (Ley N° 29571)
 * y D.S. N° 011-2011-PCM del Indecopi.
 */

const Claims = {
    /**
     * Inicializa el formulario del Libro de Reclamaciones y los tipos de reclamo.
     */
    init() {
        this.setupTypeSelector();
        this.setupFormSubmit();
        this.setupMinorCheckbox();
    },

    setupTypeSelector() {
        const radios = document.querySelectorAll('input[name="claim_type"]');
        radios.forEach(r => {
            r.addEventListener('change', () => {
                document.querySelectorAll('.claim-type-card').forEach(c => c.classList.remove('selected'));
                const parent = r.closest('.claim-type-card');
                if (parent) parent.classList.add('selected');
            });
        });
    },

    setupMinorCheckbox() {
        const checkbox = document.getElementById('claim-is-minor');
        const guardianRow = document.getElementById('guardian-row');
        if (checkbox && guardianRow) {
            checkbox.addEventListener('change', () => {
                guardianRow.style.display = checkbox.checked ? 'block' : 'none';
            });
        }
    },

    setupFormSubmit() {
        const form = document.getElementById('claims-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const claimType = form.querySelector('input[name="claim_type"]:checked')?.value || 'Reclamo';
            const fullName = document.getElementById('claim-fullname')?.value.trim();
            const docType = document.getElementById('claim-doctype')?.value;
            const docNumber = document.getElementById('claim-docnumber')?.value.trim();
            const email = document.getElementById('claim-email')?.value.trim();
            const phone = document.getElementById('claim-phone')?.value.trim();
            const address = document.getElementById('claim-address')?.value.trim();
            const isMinor = document.getElementById('claim-is-minor')?.checked || false;
            const guardianName = document.getElementById('claim-guardian')?.value.trim();

            const contractedGood = form.querySelector('input[name="contracted_good"]:checked')?.value || 'Producto';
            const amountClaimed = parseFloat(document.getElementById('claim-amount')?.value) || 0.0;
            const goodDescription = document.getElementById('claim-good-desc')?.value.trim();
            const claimDescription = document.getElementById('claim-desc')?.value.trim();
            const consumerRequest = document.getElementById('claim-request')?.value.trim();
            const acceptTerms = document.getElementById('claim-accept-terms')?.checked;

            // Validaciones
            if (!fullName) return UI.showToast('Debe ingresar su nombre completo.', 'error');
            if (!Security.isValidDoc(docNumber)) return UI.showToast('Número de documento inválido.', 'error');
            if (!Security.isValidEmail(email)) return UI.showToast('Correo electrónico inválido.', 'error');
            if (!address) return UI.showToast('Debe ingresar su domicilio.', 'error');
            if (isMinor && !guardianName) return UI.showToast('Debe ingresar el nombre del padre o tutor.', 'error');
            if (!goodDescription) return UI.showToast('Debe describir el producto o servicio contratado.', 'error');
            if (!claimDescription) return UI.showToast('Debe detallar los motivos de su queja o reclamo.', 'error');
            if (!consumerRequest) return UI.showToast('Debe especificar su pedido o solución esperada.', 'error');
            if (!acceptTerms) return UI.showToast('Debe declarar la veracidad de los hechos y aceptar el tratamiento de datos para el reclamo.', 'error');

            const payload = {
                claim_type: claimType,
                full_name: fullName,
                doc_type: docType,
                doc_number: docNumber,
                email: email,
                phone: phone,
                address: address,
                is_minor: isMinor,
                guardian_name: guardianName,
                contracted_good: contractedGood,
                amount_claimed: amountClaimed,
                good_description: goodDescription,
                claim_description: claimDescription,
                consumer_request: consumerRequest
            };

            const submitBtn = document.getElementById('btn-submit-claim');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerText = 'Registrando Hoja de Reclamación...';
            }

            try {
                const res = await API.submitClaim(payload);
                if (res.success) {
                    UI.showToast(res.data.message, 'success', 'Hoja de Reclamación');
                    this.renderReceipt(res.data, payload);
                    form.reset();
                }
            } catch (error) {
                UI.showToast(error.message, 'error', 'Error al Registrar');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = 'Enviar Hoja de Reclamación Formal';
                }
            }
        });
    },

    /**
     * Muestra la constancia oficial de recepción de queja o reclamo con los datos formales de SUNAT.
     */
    renderReceipt(claimResult, payload) {
        const container = document.getElementById('claims-receipt-container');
        if (!container) return;

        const info = claimResult.company_info || {};

        container.innerHTML = `
            <div class="claim-receipt">
                <span class="claim-stamp">REGISTRADO ANTE INDECOPI</span>
                <h3 style="font-family: var(--font-display); font-size: 1.4rem; color: var(--accent-gold); margin-bottom: 0.25rem;">
                    HOJA DE RECLAMACIÓN VIRTUAL
                </h3>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    <strong>Titular:</strong> ${Security.escapeHTML(info.legal_name || CONFIG.LEGAL.LEGAL_NAME)}<br>
                    <strong>Nombre Comercial:</strong> ${Security.escapeHTML(info.commercial_name || CONFIG.LEGAL.COMMERCIAL_NAME)} | <strong>${Security.escapeHTML(info.tax_id || CONFIG.LEGAL.TAX_ID)}</strong><br>
                    <strong>Establecimiento:</strong> ${Security.escapeHTML(info.address || CONFIG.LEGAL.ADDRESS)}
                </div>

                <p style="font-size: 0.95rem; margin-bottom: 0.5rem;">Código Único de Seguimiento:</p>
                <div class="claim-receipt-code">${Security.escapeHTML(claimResult.claim_code)}</div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.88rem; background: var(--bg-surface-elevated); padding: 1.25rem; border-radius: var(--radius-md); margin: 1rem 0;">
                    <div><strong>Fecha y Hora:</strong> ${new Date(claimResult.created_at).toLocaleString('es-PE')}</div>
                    <div><strong>Tipo:</strong> ${Security.escapeHTML(claimResult.claim_type)}</div>
                    <div><strong>Reclamante:</strong> ${Security.escapeHTML(payload.full_name)}</div>
                    <div><strong>Documento:</strong> ${Security.escapeHTML(payload.doc_type)}: ${Security.escapeHTML(payload.doc_number)}</div>
                    <div><strong>Bien Contratado:</strong> ${Security.escapeHTML(payload.contracted_good)}</div>
                    <div><strong>Monto Reclamado:</strong> ${CONFIG.CURRENCY_SYMBOL}${parseFloat(payload.amount_claimed).toFixed(2)}</div>
                </div>

                <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 1.5rem;">
                    <strong>Plazo Legal de Respuesta:</strong> ${Security.escapeHTML(info.legal_response_time || 'Máximo 15 días hábiles conforme a Ley N° 29571')}. La respuesta formal motivada le será enviada a su correo <strong>${Security.escapeHTML(payload.email)}</strong> y remitida a la mesa de control de <strong>${CONFIG.LEGAL.EMAIL_LEGAL}</strong>.
                </div>

                <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="window.print()">
                        Imprimir / Guardar en PDF
                    </button>
                    <button class="btn btn-secondary" onclick="document.getElementById('claims-receipt-container').innerHTML = ''">
                        Nueva Consulta
                    </button>
                </div>
            </div>
        `;

        container.scrollIntoView({ behavior: 'smooth' });
    },

    /**
     * Consulta el estado de una reclamación existente por código.
     */
    async searchClaim() {
        const input = document.getElementById('search-claim-code');
        const resultContainer = document.getElementById('search-claim-result');
        if (!input || !resultContainer) return;

        const code = input.value.trim();
        if (!code) {
            return UI.showToast('Por favor ingrese el código de reclamación (ej. REC-2026-0001).', 'error');
        }

        resultContainer.innerHTML = '<p style="color: var(--text-secondary);">Buscando en registros oficiales de Novedades Caleb...</p>';

        try {
            const res = await API.getClaim(code);
            if (res.success && res.data) {
                const c = res.data;
                resultContainer.innerHTML = `
                    <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); padding: 1.25rem; border-radius: var(--radius-md); margin-top: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                            <strong>Código: ${Security.escapeHTML(c.claim_code)}</strong>
                            <span class="badge ${c.status === 'Pendiente' ? 'badge-warning' : 'badge-success'}">${Security.escapeHTML(c.status)}</span>
                        </div>
                        <div style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5;">
                            <p><strong>Tipo:</strong> ${Security.escapeHTML(c.claim_type)} | <strong>Fecha:</strong> ${new Date(c.created_at).toLocaleDateString('es-PE')}</p>
                            <p><strong>Reclamante:</strong> ${Security.escapeHTML(c.full_name)}</p>
                            <p><strong>Detalle:</strong> ${Security.escapeHTML(c.claim_description)}</p>
                            ${c.admin_response ? `<p style="margin-top: 0.75rem; padding: 0.75rem; background: var(--bg-card); border-left: 3px solid var(--accent-gold);"><strong>Respuesta Oficial:</strong> ${Security.escapeHTML(c.admin_response)}</p>` : '<p style="color: var(--state-warning); margin-top: 0.5rem;">En proceso de revisión por el área legal de Novedades Caleb.</p>'}
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            resultContainer.innerHTML = `<p style="color: var(--state-danger);">${Security.escapeHTML(error.message)}</p>`;
        }
    }
};

window.Claims = Claims;
