/* Panel de administración de Novedades Caleb (/admin).
   Ingreso con la contraseña maestra → token de sesión (4 h) guardado solo en
   esta pestaña. Todo el texto que viene de la base de datos se pinta con
   textContent, nunca como HTML. */
(() => {
    "use strict";

    const TOKEN_KEY = "caleb_admin_token";
    const $ = (sel) => document.querySelector(sel);

    // El servidor guarda el texto escapado (&quot; …); se decodifica para mostrarlo
    // como texto plano (un <textarea> no ejecuta nada al decodificar)
    const decoder = document.createElement("textarea");
    const plain = (v) => { decoder.innerHTML = String(v ?? ""); return decoder.value; };

    function el(tag, props = {}, children = []) {
        const node = document.createElement(tag);
        for (const [key, val] of Object.entries(props)) {
            if (val == null || val === false) continue;
            if (key === "class") node.className = val;
            else if (key === "text") node.textContent = plain(val);
            else node.setAttribute(key, val === true ? "" : plain(val));
        }
        for (const child of [].concat(children)) {
            if (child != null) node.append(child instanceof Node ? child : document.createTextNode(plain(child)));
        }
        return node;
    }

    const store = {
        get: () => { try { return sessionStorage.getItem(TOKEN_KEY); } catch (e) { return null; } },
        set: (v) => { try { sessionStorage.setItem(TOKEN_KEY, v); } catch (e) { /* sin almacenamiento */ } },
        clear: () => { try { sessionStorage.removeItem(TOKEN_KEY); } catch (e) { /* sin almacenamiento */ } },
    };

    class AuthError extends Error {}

    async function api(path, options = {}) {
        const headers = { "Content-Type": "application/json" };
        const token = store.get();
        if (token) headers.Authorization = `Bearer ${token}`;
        let res;
        try {
            // cache: "no-store" → el panel siempre ve el dato actual (la API pública
            // deja que el navegador reutilice respuestas hasta 60 s)
            res = await fetch(path, { ...options, headers, cache: "no-store" });
        } catch (e) {
            throw new Error("No hay conexión con el servidor. Revisa tu internet e inténtalo otra vez.");
        }
        let data = {};
        try { data = await res.json(); } catch (e) { /* respuesta sin cuerpo */ }
        if (res.status === 401) throw new AuthError(data.error || "La sesión venció. Vuelve a ingresar.");
        if (!res.ok || data.success === false) {
            throw new Error(data.error || data.message || `El servidor respondió con error ${res.status}.`);
        }
        return data;
    }

    let toastTimer;
    function toast(message, isError = false) {
        const t = $("#adm-toast");
        t.textContent = message;
        t.classList.toggle("is-error", isError);
        t.hidden = false;
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => { t.hidden = true; }, 5000);
    }

    const fecha = (v) => {
        const d = new Date(String(v).replace(" ", "T"));
        return isNaN(d) ? String(v || "") : d.toLocaleString("es-PE", { dateStyle: "medium", timeStyle: "short" });
    };
    const soles = (n) => "S/ " + Number(n || 0).toLocaleString("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    // ------------------------------------------------------------ vistas
    function showLogin(message) {
        store.clear();
        $("#adm-dash-view").hidden = true;
        $("#adm-logout").hidden = true;
        $("#adm-login-view").hidden = false;
        const err = $("#adm-login-error");
        err.textContent = message || "";
        err.hidden = !message;
        $("#adm-password").focus();
    }

    function showDashboard() {
        $("#adm-login-view").hidden = true;
        $("#adm-dash-view").hidden = false;
        $("#adm-logout").hidden = false;
        loadStats();
        loadProducts();
        loadCategories();
    }

    // Cualquier 401 devuelve al ingreso; los demás errores se muestran en un aviso
    function guard(promise) {
        return promise.catch((e) => {
            if (e instanceof AuthError) showLogin(e.message);
            else toast(e.message, true);
        });
    }

    // ------------------------------------------------------------ ingreso
    $("#adm-login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = $("#adm-password");
        const btn = e.currentTarget.querySelector("button[type=submit]");
        const err = $("#adm-login-error");
        if (!input.value.trim()) {
            err.textContent = "Escribe la contraseña.";
            err.hidden = false;
            input.setAttribute("aria-invalid", "true");
            input.focus();
            return;
        }
        input.removeAttribute("aria-invalid");
        btn.disabled = true;
        btn.textContent = "Verificando…";
        try {
            store.clear();
            const res = await api("/api/admin/login", { method: "POST", body: JSON.stringify({ password: input.value }) });
            store.set(res.data.token);
            input.value = "";
            err.hidden = true;
            showDashboard();
        } catch (ex) {
            err.textContent = ex.message;
            err.hidden = false;
        } finally {
            btn.disabled = false;
            btn.textContent = "Ingresar";
        }
    });

    $("#adm-logout").addEventListener("click", () => {
        showLogin();
        toast("Sesión cerrada.");
    });

    // ------------------------------------------------------------ pestañas
    const tabs = [...document.querySelectorAll(".admin-tabs [role=tab]")];
    const loaders = { "pane-inv": () => loadProducts(), "pane-msg": () => loadMessages(), "pane-clm": () => loadClaims() };
    function selectTab(tab) {
        tabs.forEach((t) => {
            const on = t === tab;
            t.setAttribute("aria-selected", String(on));
            t.tabIndex = on ? 0 : -1;
            $("#" + t.getAttribute("aria-controls")).hidden = !on;
        });
        const load = loaders[tab.getAttribute("aria-controls")];
        if (load) load();
    }
    tabs.forEach((t, i) => {
        t.addEventListener("click", () => selectTab(t));
        t.addEventListener("keydown", (e) => {
            const step = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
            if (!step) return;
            const next = tabs[(i + step + tabs.length) % tabs.length];
            next.focus();
            selectTab(next);
        });
    });

    // ------------------------------------------------------------ datos
    function loadStats() {
        return guard(api("/api/stats").then(({ data }) => {
            $("#st-products").textContent = data.products_total ?? "—";
            $("#st-categories").textContent = data.categories_total ?? "—";
            $("#st-messages").textContent = data.messages_total ?? "—";
            $("#st-claims").textContent = data.claims_pending ?? "—";
        }));
    }

    function loadCategories() {
        const select = $("#adm-categories");
        if (select.options.length) return;
        guard(api("/api/categories").then(({ data }) => {
            select.replaceChildren(...data.map((c) => el("option", { value: String(c.id), text: c.name })));
        }));
    }

    function emptyRow(tbody, text) {
        tbody.replaceChildren(el("tr", {}, el("td", { colspan: "5", class: "admin-empty", text })));
    }

    function loadProducts() {
        const tbody = $("#adm-products");
        emptyRow(tbody, "Cargando inventario…");
        return guard(api("/api/products").then(({ data }) => {
            if (!data.length) return emptyRow(tbody, "No hay productos en el catálogo.");
            tbody.replaceChildren(...data.map((p) => {
                const del = el("button", { class: "btn btn-outline admin-del", type: "button", text: "Eliminar", "aria-label": `Eliminar ${p.name}` });
                del.addEventListener("click", () => removeProduct(p, del));
                return el("tr", {}, [
                    el("td", {}, el("div", { class: "admin-prod" }, [
                        el("img", { src: p.image_url, alt: "", loading: "lazy", width: "44", height: "56" }),
                        el("span", { text: p.name }),
                    ])),
                    el("td", { "data-label": "Categoría", text: p.category_name || "—" }),
                    el("td", { "data-label": "Código", text: p.sku || "—" }),
                    el("td", { "data-label": "Stock", text: p.stock > 0 ? `${p.stock} un.` : "Consultar" }),
                    el("td", {}, del),
                ]);
            }));
        }));
    }

    async function removeProduct(p, btn) {
        if (!window.confirm(`¿Quitar "${plain(p.name)}" del catálogo? Dejará de verse en la página.`)) return;
        btn.disabled = true;
        await guard(api(`/api/products/${p.id}`, { method: "DELETE" }).then(() => {
            toast(`"${plain(p.name)}" se quitó del catálogo.`);
            loadProducts();
            loadStats();
        }));
        btn.disabled = false;
    }

    function loadMessages() {
        const list = $("#adm-messages");
        list.replaceChildren(el("li", { class: "admin-empty", text: "Cargando mensajes…" }));
        return guard(api("/api/messages").then(({ data }) => {
            if (!data.length) return list.replaceChildren(el("li", { class: "admin-empty", text: "No hay mensajes todavía." }));
            list.replaceChildren(...data.map((m) => el("li", { class: "admin-item" }, [
                el("div", { class: "admin-item-head" }, [
                    el("strong", { text: m.name }),
                    el("span", { class: "muted", text: fecha(m.created_at) }),
                ]),
                el("p", { class: "admin-item-sub", text: m.subject || "Sin asunto" }),
                el("p", { text: m.message }),
                el("p", { class: "muted" }, [
                    m.email ? el("a", { href: `mailto:${m.email}`, text: m.email }) : null,
                    m.email && m.phone ? " · " : null,
                    m.phone ? el("a", { href: `https://wa.me/${String(m.phone).replace(/\D/g, "")}`, target: "_blank", rel: "noopener", text: `WhatsApp ${m.phone}` }) : null,
                ]),
            ])));
        }));
    }

    function loadClaims() {
        const list = $("#adm-claims");
        list.replaceChildren(el("li", { class: "admin-empty", text: "Cargando Libro de Reclamaciones…" }));
        return guard(api("/api/claims/all").then(({ data }) => {
            if (!data.length) return list.replaceChildren(el("li", { class: "admin-empty", text: "No hay reclamos registrados." }));
            list.replaceChildren(...data.map((c) => el("li", { class: "admin-item" }, [
                el("div", { class: "admin-item-head" }, [
                    el("strong", { text: `${c.claim_code} · ${c.full_name}` }),
                    el("span", { class: `admin-badge${c.status === "Pendiente" ? " is-pending" : ""}`, text: c.status }),
                ]),
                el("p", { class: "admin-item-sub", text: `${c.claim_type} · ${fecha(c.created_at)} · responder en 15 días hábiles` }),
                el("dl", { class: "admin-dl" }, [
                    el("dt", { text: "Bien contratado" }), el("dd", { text: `${c.contracted_good || "—"}${c.amount_claimed ? ` (${soles(c.amount_claimed)})` : ""}` }),
                    el("dt", { text: "Detalle" }), el("dd", { text: c.claim_description }),
                    el("dt", { text: "Pedido del cliente" }), el("dd", { text: c.consumer_request }),
                    el("dt", { text: "Contacto" }), el("dd", { text: [c.email, c.phone].filter(Boolean).join(" · ") || "—" }),
                ]),
            ])));
        }));
    }

    // ------------------------------------------------------------ nuevo producto
    const imgInput = $("#adm-image");
    const preview = $("#adm-image-preview");
    const note = $("#adm-image-note");
    function showPreview() {
        const v = imgInput.value.trim();
        preview.hidden = true;
        if (!v) { note.textContent = "Sin foto"; return; }
        note.textContent = "Cargando…";
        preview.onload = () => { preview.hidden = false; note.textContent = ""; };
        preview.onerror = () => { preview.hidden = true; note.textContent = "No se encontró esa foto"; };
        preview.src = v;
    }
    imgInput.addEventListener("change", showPreview);
    // Al corregir un campo, se quita la marca de error
    $("#adm-new-form").addEventListener("input", (e) => {
        if (e.target.getAttribute("aria-invalid")) {
            e.target.removeAttribute("aria-invalid");
            $("#adm-new-error").hidden = true;
        }
    });

    $("#adm-new-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const form = e.currentTarget;
        const err = $("#adm-new-error");
        const bad = [...form.querySelectorAll("input, select, textarea")].find((f) => !f.checkValidity());
        form.querySelectorAll("[aria-invalid]").forEach((f) => f.removeAttribute("aria-invalid"));
        if (bad) {
            bad.setAttribute("aria-invalid", "true");
            err.textContent = bad.name === "image_url"
                ? "La foto debe estar en /assets/productos/ y terminar en .webp, .png o .jpg."
                : "Completa el nombre, la categoría y la descripción.";
            err.hidden = false;
            bad.focus();
            return;
        }
        err.hidden = true;
        const f = new FormData(form);
        const payload = {
            name: f.get("name").trim(),
            category_id: Number(f.get("category_id")),
            description: f.get("description").trim(),
            material: f.get("material").trim() || "Consultar",
            color: f.get("color").trim(),
            dimensions: f.get("dimensions").trim(),
            stock: Math.max(0, parseInt(f.get("stock"), 10) || 0),
            price: 0,
            image_url: f.get("image_url").trim() || "/assets/productos/maniqui-femenino-abstracto-blanco.webp",
            is_featured: f.get("is_featured") === "on",
        };
        const btn = form.querySelector("button[type=submit]");
        btn.disabled = true;
        await guard(api("/api/products", { method: "POST", body: JSON.stringify(payload) }).then(() => {
            toast(`"${payload.name}" ya aparece en el catálogo.`);
            form.reset();
            showPreview();
            loadStats();
            selectTab($("#tab-inv"));
        }));
        btn.disabled = false;
    });

    // ------------------------------------------------------------ arranque
    const saved = store.get();
    if (saved) {
        // Si mientras tanto el dueño ya ingresó de nuevo, esta respuesta (del
        // permiso anterior) no debe borrar la sesión nueva
        api("/api/admin/verify").then(() => { if (store.get() === saved) showDashboard(); })
            .catch(() => { if (store.get() === saved) showLogin(); });
    } else {
        showLogin();
    }
})();
