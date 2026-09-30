/* ==========================================================================
   Novedades Caleb — sitio público
   Todo el contenido que viene de la API se inserta con textContent (nunca
   innerHTML) para no abrir la puerta a XSS.
   ========================================================================== */
(function () {
    "use strict";

    const WA_NUMBER = "51916126747";

    // Equipos con poca memoria/procesador o con "ahorro de datos": modo liviano
    (function detectLite() {
        const c = navigator.connection || {};
        const lowMem = navigator.deviceMemory && navigator.deviceMemory <= 2;
        const lowCpu = navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2;
        if (lowMem || lowCpu || c.saveData || /(^|-)2g$/.test(c.effectiveType || "")) document.documentElement.classList.add("lite");
    })();
    const $ = (sel, root = document) => root.querySelector(sel);
    const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

    /* ----------------------------- utilidades ----------------------------- */

    // El backend guarda los textos escapados (&amp;, &quot;…). Los devolvemos
    // a texto plano para mostrarlos con textContent.
    const decoder = document.createElement("textarea");
    function plain(value) {
        if (value == null) return "";
        decoder.innerHTML = String(value);
        return decoder.value;
    }

    function el(tag, props = {}, children = []) {
        const node = document.createElement(tag);
        for (const [key, val] of Object.entries(props)) {
            if (val == null || val === false) continue;
            if (key === "class") node.className = val;
            else if (key === "text") node.textContent = val;
            else if (key.startsWith("on")) node.addEventListener(key.slice(2), val);
            else node.setAttribute(key, val === true ? "" : val);
        }
        for (const child of [].concat(children)) {
            if (child == null) continue;
            node.append(child instanceof Node ? child : document.createTextNode(child));
        }
        return node;
    }

    // Flecha en SVG (mismo trazo que las del catálogo)
    function svgIcon(d) {
        const NS = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(NS, "svg");
        svg.setAttribute("viewBox", "0 0 24 24");
        svg.setAttribute("width", "26");
        svg.setAttribute("height", "26");
        svg.setAttribute("aria-hidden", "true");
        const path = document.createElementNS(NS, "path");
        Object.entries({ d, fill: "none", stroke: "currentColor", "stroke-width": "2.2", "stroke-linecap": "round", "stroke-linejoin": "round" })
            .forEach(([k, v]) => path.setAttribute(k, v));
        svg.append(path);
        return svg;
    }

    const soles = (n) => "S/ " + Number(n || 0).toLocaleString("es-PE", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    const stockText = (p) => (p.stock > 0 ? `${p.stock} unidades` : "Consultar");
    const quoteMsg = (p, name) => `Hola, quiero cotizar: ${name} (código ${p.sku}).`;
    const waLink = (text) => `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(text)}`;

    // Cambia un parámetro de la dirección sin recargar ni tocar los demás
    function setQuery(key, value) {
        const u = new URL(location.href);
        if (value) u.searchParams.set(key, value); else u.searchParams.delete(key);
        history.replaceState(history.state, "", u.pathname + u.search + u.hash);
    }

    // Foto del producto; si no tiene, una genérica del catálogo
    function imgSrc(url) {
        return url || "/assets/productos/maniqui-femenino-abstracto-blanco.webp";
    }
    function withFallback(img, original) {
        img.addEventListener("error", function onErr() {
            img.removeEventListener("error", onErr);
            if (original) img.src = original;
        });
        return img;
    }

    async function api(path, options = {}) {
        const opts = { headers: { "Content-Type": "application/json" }, ...options };
        let res;
        try {
            res = await fetch(path, opts);
        } catch (e) {
            throw new Error("No hay conexión con el servidor. Revisa tu internet e inténtalo otra vez.");
        }
        let data = {};
        try { data = await res.json(); } catch (e) { /* respuesta sin cuerpo */ }
        if (!res.ok || data.success === false || data.status === "error") {
            throw new Error(data.error || data.message || `El servidor respondió con error ${res.status}.`);
        }
        return data;
    }

    let toastTimer;
    function toast(message, isError = false) {
        const t = $("#toast");
        t.textContent = message;
        t.classList.toggle("is-error", isError);
        t.hidden = false;
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => { t.hidden = true; }, 5000);
    }

    function formData(form) {
        const data = {};
        new FormData(form).forEach((v, k) => { data[k] = typeof v === "string" ? v.trim() : v; });
        return data;
    }

    // Validación nativa, pero con mensajes en el formulario y el foco en el
    // primer campo con problemas.
    function validate(form) {
        const errorBox = $(".form-error", form);
        let first = null;
        $$("input, select, textarea", form).forEach((field) => {
            if (field.classList.contains("hp")) return;
            const ok = field.checkValidity();
            field.setAttribute("aria-invalid", ok ? "false" : "true");
            if (!ok && !first) first = field;
        });
        if (first) {
            const label = first.closest("label");
            const name = label ? (label.querySelector("span") || label).textContent.trim() : "";
            let msg = "Revisa los campos marcados.";
            if (first.type === "checkbox") msg = "Para continuar, marca la casilla de aceptación.";
            else if (first.validity.valueMissing) msg = `Completa el campo "${name}".`;
            else if (first.validity.typeMismatch && first.type === "email") msg = "Escribe un correo válido, por ejemplo nombre@correo.com.";
            else if (first.validity.tooShort) msg = `El campo "${name}" necesita al menos ${first.minLength} caracteres.`;
            else if (first.validity.patternMismatch) msg = `Revisa el formato de "${name}".`;
            showFormError(form, msg);
            first.focus();
            return false;
        }
        if (errorBox) errorBox.hidden = true;
        return true;
    }
    function showFormError(form, msg) {
        const box = $(".form-error", form);
        if (box) { box.textContent = msg; box.hidden = false; }
    }
    function busy(button, isBusy, label) {
        if (isBusy) { button.dataset.label = button.textContent; button.textContent = label; button.disabled = true; }
        else { button.textContent = button.dataset.label || button.textContent; button.disabled = false; }
    }

    /* --------------------------- página actual --------------------------- */

    // Cada sección es una página propia; <body data-page> dice cuál es.
    const CURRENT = document.body.dataset.page || "inicio";
    $$(".main-nav a, .header-claims").forEach((a) => {
        if (a.dataset.route === CURRENT) a.setAttribute("aria-current", "page");
    });

    /* ----------------------- cabecera y cinta métrica ----------------------- */

    const header = $("#site-header");
    const tapeFill = $("#tape-progress-fill");
    const scene = $("#scene");
    function updateHeader() {
        const y = window.scrollY;
        const solidAt = scene ? scene.offsetHeight - window.innerHeight - 10 : 40;
        header.classList.toggle("is-solid", y > solidAt);
        const max = document.documentElement.scrollHeight - window.innerHeight;
        tapeFill.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + "%";
    }
    let ticking = false;
    window.addEventListener("scroll", () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => { updateHeader(); ticking = false; });
    }, { passive: true });

    const navToggle = $("#nav-toggle");
    const nav = $("#main-nav");
    function closeNav() {
        nav.classList.remove("is-open");
        document.body.classList.remove("nav-open");
        navToggle.setAttribute("aria-expanded", "false");
    }
    navToggle.addEventListener("click", () => {
        const open = !nav.classList.contains("is-open");
        nav.classList.toggle("is-open", open);
        document.body.classList.toggle("nav-open", open);
        navToggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeNav(); });

    /* ------------------------------ catálogo ------------------------------ */

    const Catalog = {
        products: [],
        categories: [],
        loaded: null,
        filter: "all",

        // El catálogo se guarda en la pestaña: al recargar (F5) se muestra al
        // instante, sin vitrina vacía, y por detrás se confirma con el servidor;
        // si algo cambió (p. ej. el dueño quitó un producto), se actualiza solo.
        load() {
            if (!this.loaded) {
                const KEY = "caleb-catalogo-v1";
                let cached = null;
                try { cached = sessionStorage.getItem(KEY); } catch (e) { /* sin almacenamiento */ }
                const fresh = Promise.all([api("/api/categories"), api("/api/products")])
                    .then(([cats, prods]) => ({ cats: cats.data || [], prods: prods.data || [] }));
                const save = (raw) => { try { sessionStorage.setItem(KEY, raw); } catch (e) { /* sin almacenamiento */ } };
                let data = null;
                try { data = cached && JSON.parse(cached); } catch (e) { data = null; }
                if (data && Array.isArray(data.prods) && data.prods.length) {
                    this.apply(data);
                    this.loaded = Promise.resolve();
                    fresh.then((d) => {
                        const raw = JSON.stringify(d);
                        if (raw === cached) return;
                        save(raw);
                        this.apply(d);
                        this.refresh();
                    }).catch(() => { /* se queda con lo guardado */ });
                } else {
                    this.loaded = fresh.then((d) => { save(JSON.stringify(d)); this.apply(d); });
                    this.loaded.catch(() => { this.loaded = null; });
                }
            }
            return this.loaded;
        },

        apply({ cats, prods }) {
            this.categories = cats.filter((c) => c.is_active !== 0);
            this.products = prods.filter((p) => p.is_active !== 0);
        },

        // Vuelve a pintar lo que ya está en pantalla con los datos nuevos
        refresh() {
            if (!this.shown) return;
            this.renderChips();
            this.renderGrid();
            Showcase.update(this.products);
        },

        lowestPrice(catId) { // (sin uso mientras no se publiquen precios)
            const prices = this.products.filter((p) => p.category_id === catId && p.price > 0).map((p) => p.price);
            return prices.length ? Math.min(...prices) : null;
        },

        // Rueda de Inicio: un producto por tarjeta, agrupados por línea
        async renderLineup() {
            const list = $("#home-lineup");
            try {
                await this.load();
            } catch (e) {
                list.replaceChildren(el("li", { class: "lineup-empty" }, [
                    "No pudimos cargar los modelos. ",
                    el("a", { href: waLink("Hola, quiero ver el catálogo de maniquíes."), target: "_blank", rel: "noopener", text: "Pide el catálogo por WhatsApp" }),
                    ".",
                ]));
                return;
            }
            const order = new Map(this.categories.map((c, i) => [c.id, i]));
            const pool = this.products.filter((p) => p.is_featured);
            const models = (pool.length >= 8 ? pool : this.products).slice(0, 16).sort((x, y) => (order.get(x.category_id) ?? 99) - (order.get(y.category_id) ?? 99));
            list.replaceChildren(...models.map((p) => {
                const name = plain(p.name);
                const short = (name.match(/"([^"]+)"/) || [])[1] || name;
                const open = (e) => { e.preventDefault(); ProductCard.open(p, e.currentTarget); };
                return el("li", {}, el("a", { href: `/catalogo.html?linea=${encodeURIComponent(p.category_slug || "")}`, onclick: open, "aria-label": `Ver ficha de ${name}` }, [
                    withFallback(el("img", { src: imgSrc(p.image_url), alt: "", loading: "lazy" }), p.image_url),
                    el("span", { class: "lineup-label" }, [
                        el("strong", { text: short }),
                        el("span", { text: plain(p.category_name) }),
                    ]),
                ]));
            }));
            Ring.mount(list);
        },

        async show(lineSlug) {
            const grid = $("#product-grid");
            if (!this.products.length) grid.replaceChildren(el("li", { class: "grid-empty", text: "Cargando modelos…" }));
            try {
                await this.load();
            } catch (e) {
                Showcase.fail(e.message);
                grid.replaceChildren(el("li", { class: "grid-empty" }, [
                    el("p", { text: e.message }),
                    el("p", {}, ["Mientras tanto, puedes ", el("a", { href: waLink("Hola, quiero ver el catálogo de maniquíes."), target: "_blank", rel: "noopener", text: "pedir el catálogo por WhatsApp" }), "."]),
                ]));
                return;
            }
            const cat = this.categories.find((c) => c.slug === lineSlug);
            this.filter = cat ? cat.id : "all";
            this.renderChips();
            this.renderGrid();
            Showcase.init(this.products, cat ? cat.id : null);
            this.shown = true;
        },

        renderChips() {
            const wrap = $("#catalog-chips");
            const make = (id, label) => el("button", {
                class: "chip", type: "button", "aria-pressed": String(this.filter === id),
                onclick: () => {
                    this.filter = id;
                    const slug = id === "all" ? "" : this.categories.find((c) => c.id === id).slug;
                    setQuery("linea", slug);
                    this.renderChips();
                    this.renderGrid();
                },
            }, label);
            const used = new Set(this.products.map((p) => p.category_id));
            // Nombres cortos para que todos los filtros entren en una sola fila
            const SHORT = {
                "maniquies-femeninos": "Femeninos", "maniquies-masculinos": "Masculinos", "bustos-sastreria": "Bustos",
                "exhibidores-colgantes": "Colgantes", "maniquies-infantiles": "Infantiles", "accesorios-bases": "Accesorios",
            };
            wrap.replaceChildren(make("all", "Todo"), ...this.categories.filter((c) => used.has(c.id)).map((c) => make(c.id, SHORT[c.slug] || plain(c.name))));
        },

        page: 0,

        // Productos por página: siempre 2 filas, así la hoja cabe en una pantalla
        perPage() {
            const w = window.innerWidth;
            return w >= 1100 ? 10 : w >= 700 ? 6 : 4;
        },

        renderGrid(keepPage) {
            if (!keepPage) this.page = 0;
            const q = "";
            let list = this.products.filter((p) => this.filter === "all" || p.category_id === this.filter);
            if (q) {
                list = list.filter((p) => [p.name, p.material, p.color, p.category_name, p.description]
                    .some((f) => plain(f).toLowerCase().includes(q)));
            }
            list = list.slice().sort((a, b) => (b.is_featured || 0) - (a.is_featured || 0));

            const per = this.perPage();
            const pages = Math.max(1, Math.ceil(list.length / per));
            this.page = Math.min(this.page, pages - 1);
            $("#catalog-count").textContent = `Página ${this.page + 1} de ${pages}  ·  ${list.length === 1 ? "1 producto" : `${list.length} productos`}`;
            $("#pager-prev").disabled = this.page === 0;
            $("#pager-next").disabled = this.page >= pages - 1;
            this.pages = pages;
            const grid = $("#product-grid");
            if (!list.length) {
                grid.replaceChildren(el("li", { class: "grid-empty" }, [
                    el("p", { text: q ? `Ningún modelo coincide con "${q}".` : "No hay modelos en esta línea por ahora." }),
                    el("p", {}, ["Prueba con otra palabra o ", el("a", { href: waLink(`Hola, busco ${q || "un modelo"} de maniquí.`), target: "_blank", rel: "noopener", text: "pregúntanos por WhatsApp" }), ": muchos modelos llegan por pedido."]),
                ]));
                return;
            }
            grid.replaceChildren(...list.slice(this.page * per, this.page * per + per).map((p) => this.card(p)));
        },

        card(p) {
            const name = plain(p.name);
            const img = withFallback(el("img", { src: imgSrc(p.image_url), alt: name, loading: "lazy" }), p.image_url);
            return el("li", { class: "product" }, [
                el("button", { class: "product-media", type: "button", "aria-label": `Ver ${name} en la vitrina`, onclick: () => Showcase.show(p, true) }, [
                    img,
                ]),
                el("div", { class: "product-body" }, [
                    el("span", { class: "product-cat", text: plain(p.category_name) }),
                    el("h3", { class: "product-name", text: name }),
                    el("span", { class: "product-mat", text: [plain(p.material), plain(p.color).toLowerCase()].filter((t) => t && t !== "Consultar").join(", ") }),
                    p.stock > 0 && p.stock <= 8 ? el("span", { class: "stock-low", text: `Quedan ${p.stock} en stock` }) : null,
                    el("div", { class: "product-actions" }, [
                        el("a", { class: "btn-quote", href: waLink(quoteMsg(p, name)), target: "_blank", rel: "noopener", text: "Cotizar" }),
                    ]),
                ]),
            ]);
        },

        // "180cm x 84cm x 62cm x 89cm" en maniquíes de cuerpo entero es
        // altura, busto, cintura y cadera. Otros formatos se muestran tal cual.
        measures(dim) {
            const text = plain(dim);
            const nums = text.match(/^\s*(\d+)\s*cm\s*x\s*(\d+)\s*cm\s*x\s*(\d+)\s*cm\s*x\s*(\d+)\s*cm\s*$/i);
            if (nums) {
                const labels = ["Altura", "Busto", "Cintura", "Cadera"];
                return { raw: false, items: labels.map((l, i) => [l, nums[i + 1]]) };
            }
            return { raw: true, items: [["Medidas", text.trim() || "Consultar"]] };
        },

        open(p) {
            const d = $("#product-dialog");
            const name = plain(p.name);
            const img = $("#pd-img");
            img.src = imgSrc(p.image_url);
            img.alt = name;
            $("#pd-cat").textContent = plain(p.category_name);
            $("#pd-name").textContent = name;
            $("#pd-desc").textContent = plain(p.description);

            const m = this.measures(p.dimensions);
            const dl = $("#pd-measures");
            dl.classList.toggle("is-raw", m.raw);
            dl.replaceChildren(...m.items.map(([label, value]) => el("div", {}, [
                el("dt", { text: label }),
                el("dd", {}, m.raw ? value : [value, el("small", { text: "cm" })]),
            ])));

            $("#pd-meta").replaceChildren(
                el("dt", { text: "Material" }), el("dd", { text: plain(p.material) }),
                el("dt", { text: "Color" }), el("dd", { text: plain(p.color) }),
                el("dt", { text: "Código" }), el("dd", { text: plain(p.sku) }),
                el("dt", { text: "Stock" }), el("dd", { text: stockText(p) }),
            );
            $("#pd-wa").href = waLink(quoteMsg(p, name));
            d.showModal();
        },
    };

    /* ------------------------ vitrina del catálogo ------------------------ */

    // Color de fondo de la vitrina para cada producto (por su imagen)
    const SHOWCASE_BG = {
        "maniqui-masculino-negro": "#A89B8C", "busto-femenino-piel": "#8E5B4A", "busto-sastre-blanco": "#7E9486",
        "colgador-torso-fierro": "#C9A24A", "cadera-femenina-piel": "#B98C82", "cadera-masculina-piel": "#8C7A6B",
        "brazo-cascada-cromado": "#56697A", "gancho-panel-largo": "#4F5F6E", "gancho-panel-corto": "#6A7F90",
        "colgador-madera-pinzas": "#6F8570", "colgador-plastico-amarillo": "#3E4A7A", "colgador-plastico-rosado": "#8C5A74",
        "colgador-plastico-rojo": "#2F5A57", "colgador-plastico-negro": "#D8CFC2", "colgador-pinzas-mostaza": "#5B4B6E",
        "colgador-madera-corazon": "#C98E8E", "maniqui-bebe-gateador": "#7FA3BF", "maniqui-nino-blanco": "#8FA88F",
        "maniqui-nina-peluca": "#B7937E", "maniqui-nino-piel": "#5E7A8C",
        "maniqui-nina-piel-peluca": "#6E8FA6", "maniqui-femenino-realista": "#4E6C78", "cabeza-femenina-realista": "#6B5A7A",
        "cabeza-masculina-realista": "#4F6B5E", "maniqui-masculino-realista": "#3F5566", "busto-sastre-femenino-blanco": "#8A6F63",
        "busto-sastre-femenino-negro": "#C7B299", "busto-sastre-femenino-crudo": "#5C6B7D", "maniqui-masculino-abstracto-blanco": "#3B4A5E",
        "maniqui-femenino-abstracto-blanco": "#B0766A", "maniqui-femenino-abstracto-negro": "#D2B48C", "torso-masculino-realista": "#56708A",
        "torso-femenino-realista": "#7A8C6E", "maniqui-femenino-realista-brazos": "#4A6670", "perchero-giratorio": "#C9B79C",
        "riel-u-pared": "#BFA88A", "perchero-regulable": "#9FB0A0", "perchero-doble-barra": "#5B6F82",
        "cremallera-pared": "#A7856A", "maniqui-colgante-femenino": "#5F6E86",
    };
    const SWATCH = { amarillo: "#F2C230", rosado: "#F2A7B8", rojo: "#D0312D", negro: "#1E1E20", blanco: "#F4F2EE", crudo: "#DCCFBC" };

    const Showcase = {
        items: [],
        index: 0,

        slug(p) { return (p.image_url.match(/([\w-]+)\.webp$/) || [])[1] || p.slug; },

        // Productos que son el mismo modelo en otro color ("Colgador de plástico rojo")
        family(p) {
            const color = plain(p.color).toLowerCase();
            const base = plain(p.name).toLowerCase().replace(new RegExp(`\\s${color}$`), "");
            return this.items.filter((q) => plain(q.name).toLowerCase().replace(new RegExp(`\\s${plain(q.color).toLowerCase()}$`), "") === base);
        },

        init(products, catId) {
            if (!$("#showcase")) return;
            this.items = products.slice();
            // Si la dirección trae ?producto=…, se vuelve a ese (F5 no te regresa al primero)
            const wanted = new URLSearchParams(location.search).get("producto");
            const byUrl = wanted ? this.items.findIndex((p) => p.slug === wanted) : -1;
            const start = byUrl >= 0 ? byUrl : catId ? Math.max(0, this.items.findIndex((p) => p.category_id === catId)) : 0;
            $("#sc-total").textContent = String(this.items.length);
            this.cache = new Map();
            const warmAll = () => this.items.forEach((p) => this.preload(p));
            ("requestIdleCallback" in window) ? requestIdleCallback(warmAll, { timeout: 3000 }) : setTimeout(warmAll, 1500);
            $("#sc-prev").onclick = () => this.step(-1);
            $("#sc-next").onclick = () => this.step(1);
            $("#sc-next-arrow").onclick = () => this.step(1);
            // En tablet y celular el producto va arriba y los textos debajo: la
            // vista previa del siguiente pasa a la zona del producto, a su derecha
            const compact = window.matchMedia("(max-width: 960px)");
            const placeNext = () => (compact.matches ? $(".sc-product") : $(".sc-side")).append($("#sc-next"));
            placeNext();
            // addListener: iPhone con iOS 13 no tiene addEventListener en matchMedia
            if (compact.addEventListener) compact.addEventListener("change", placeNext); else compact.addListener(placeNext);
            document.addEventListener("keydown", (e) => {
                if (e.target.closest("input, textarea, select, dialog")) return;
                if (window.scrollY > window.innerHeight * 0.6) return;
                if (e.key === "ArrowLeft") $("#sc-prev").click();
                if (e.key === "ArrowRight") $("#sc-next").click();
            });
            // Primer pintado: el color de fondo entra directo (sin transición) y
            // recién ahí se muestra la vitrina, ya completa
            const box = $("#showcase");
            box.classList.add("no-bg-anim");
            this.render(this.items[start], false);
            box.classList.remove("sc-loading");
            box.removeAttribute("aria-busy");
            requestAnimationFrame(() => requestAnimationFrame(() => box.classList.remove("no-bg-anim")));
        },

        // Datos nuevos del servidor: se queda en el mismo producto si sigue existiendo
        update(products) {
            if (!products.length) return;
            const current = this.items[this.index];
            this.items = products.slice();
            $("#sc-total").textContent = String(this.items.length);
            const keep = current ? this.items.find((p) => p.slug === current.slug) : null;
            this.render(keep || this.items[Math.min(this.index, this.items.length - 1)], false);
        },

        // Sin conexión o sin datos: se muestra el aviso en lugar de la vitrina vacía
        fail(message) {
            const box = $("#showcase");
            if (!box) return;
            box.classList.remove("sc-loading");
            box.removeAttribute("aria-busy");
            box.classList.add("is-failed");
            $("#sc-name").textContent = "No pudimos cargar el catálogo";
            $("#sc-desc").textContent = `${message} También puedes pedirlo por WhatsApp.`;
            $("#sc-wa").href = waLink("Hola, quiero ver el catálogo de maniquíes.");
        },

        // Descarga y decodifica una imagen una sola vez; devuelve una promesa
        preload(p) {
            const url = imgSrc(p.image_url);
            if (!this.cache.has(url)) {
                const im = new Image();
                im.decoding = "async";
                im.src = url;
                this.cache.set(url, im.decode ? im.decode().catch(() => {}) : Promise.resolve());
            }
            return this.cache.get(url);
        },

        // Flechas: todo se mueve sobre la diagonal "\" que une la vista previa
        // (abajo a la derecha) con el centro y sigue hacia arriba a la izquierda.
        //  -> el del centro sale hacia arriba-izquierda y "Siguiente" sube al centro.
        //  <- el del centro baja hasta "Siguiente" y el anterior entra desde arriba-izquierda.
        step(dir) {
            if (this.busy) return;
            const n = this.items.length;
            const target = this.items[(this.index + dir + n) % n];
            if (reduceMotion.matches) { this.render(target, false); return; }
            this.busy = true;
            const main = $("#sc-img");
            const thumb = $("#sc-next-img");
            const mRect = main.getBoundingClientRect();
            const tRect = thumb.getBoundingClientRect();
            // Vector de la diagonal: de la vista previa al centro
            const vx = (mRect.left + mRect.width / 2) - (tRect.left + tRect.width / 2);
            const vy = (mRect.top + mRect.height / 2) - (tRect.top + tRect.height / 2);
            const rectFrames = (from, to) => [
                { left: from.left + "px", top: from.top + "px", width: from.width + "px", height: from.height + "px" },
                { left: to.left + "px", top: to.top + "px", width: to.width + "px", height: to.height + "px" },
            ];
            const flyer = (src, r) => {
                const f = el("img", { class: "sc-flyer", src, alt: "" });
                Object.assign(f.style, { left: r.left + "px", top: r.top + "px", width: r.width + "px", height: r.height + "px" });
                document.body.append(f);
                return f;
            };
            const done = () => { main.style.opacity = ""; thumb.style.opacity = ""; this.busy = false; };

            // El producto del centro siempre sale como copia
            const out = flyer(main.src, mRect);
            main.style.opacity = "0";
            thumb.style.opacity = "0";

            if (dir > 0) {
                const inc = flyer(thumb.src, tRect);
                out.animate([
                    { transform: "none", opacity: 1 },
                    { transform: `translate(${vx}px, ${vy}px) scale(.55)`, opacity: 0 },
                ], { duration: 520, easing: "cubic-bezier(.5, 0, .75, .4)", fill: "forwards" }).finished.then(() => out.remove());
                this.preload(target).then(() => {
                    this.render(target, false);
                    requestAnimationFrame(() => {
                        const to = main.getBoundingClientRect();
                        inc.animate(rectFrames(tRect, to), { duration: 560, easing: "cubic-bezier(.3, .8, .25, 1)" }).finished.then(() => {
                            inc.remove();
                            thumb.animate([{ opacity: 0, transform: "translate(30px, 30px) scale(.7)" }, { opacity: 1, transform: "none" }], { duration: 300, easing: "ease-out" });
                            done();
                        });
                    });
                });
            } else {
                out.animate(rectFrames(mRect, tRect), { duration: 520, easing: "cubic-bezier(.5, 0, .3, 1)" }).finished.then(() => {
                    out.remove();
                    done();
                });
                this.preload(target).then(() => {
                    this.render(target, false);
                    main.style.opacity = "";
                    main.animate([
                        { transform: `translate(${vx}px, ${vy}px) scale(.55)`, opacity: 0 },
                        { transform: "none", opacity: 1 },
                    ], { duration: 560, easing: "cubic-bezier(.25, .8, .3, 1)" });
                });
            }
        },

        show(p, scrollUp) {
            if (scrollUp) window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
            if (this.items[this.index] === p) return;
            this.render(p, true);
        },

        // Cambia solo textos y color de fondo (instantáneo, sin esperar imágenes)
        fillText(p) {
            const box = $("#showcase");
            const bg = SHOWCASE_BG[this.slug(p)] || "#3E4450";
            box.style.setProperty("--sc-bg", bg);
            box.classList.toggle("is-light", luminance(bg) > 0.55);
            $("#sc-cat").textContent = plain(p.category_name);
            $("#sc-name").textContent = plain(p.name);
            $("#sc-desc").textContent = plain(p.description);
        },

        render(p, animate) {
            const box = $("#showcase");
            this.index = this.items.indexOf(p);
            const n = this.items.length;
            this.preload(this.items[(this.index + 1) % n]);
            this.preload(this.items[(this.index + 2) % n]);
            this.preload(this.items[(this.index - 1 + n) % n]);
            const bg = SHOWCASE_BG[this.slug(p)] || "#3E4450";
            const fill = () => {
                const name = plain(p.name);
                $("#sc-cat").textContent = plain(p.category_name);
                $("#sc-name").textContent = name;
                $("#sc-desc").textContent = plain(p.description);
                    const m = Catalog.measures(p.dimensions);
                const rows = [["Material", plain(p.material)], ["Color", plain(p.color)], ...m.items.map(([k, v]) => [k, m.raw ? v : `${v} cm`])];
                $("#sc-specs").replaceChildren(...rows.map(([k, v]) => el("div", {}, [el("dt", { text: k }), el("dd", { text: v })])));
                $("#sc-wa").href = waLink(quoteMsg(p, name));
                const fam = this.family(p);
                $("#sc-colors-wrap").hidden = fam.length < 2;
                $("#sc-swatches").replaceChildren(...(fam.length < 2 ? [] : fam.map((q) => {
                    const c = plain(q.color);
                    const b = el("button", { class: "sc-swatch", type: "button", "aria-label": c, title: c, "aria-pressed": String(q === p), onclick: () => this.show(q) });
                    b.style.background = SWATCH[c.toLowerCase()] || "#888";
                    return b;
                })));
                // Contador y vista previa del siguiente producto
                $("#sc-pos").textContent = String(this.index + 1);
                setQuery("producto", this.index === 0 ? "" : p.slug);
                const nxt = this.items[(this.index + 1) % this.items.length];
                $("#sc-next-img").src = imgSrc(nxt.image_url);
                $("#sc-next").setAttribute("aria-label", `Siguiente producto: ${plain(nxt.name)}`);
            };

            box.style.setProperty("--sc-bg", bg);
            box.classList.toggle("is-light", luminance(bg) > 0.55);
            const img = $("#sc-img");
            if (!animate || reduceMotion.matches) {
                img.src = imgSrc(p.image_url);
                img.alt = plain(p.name);
                fill();
                return;
            }
            img.classList.remove("is-in");
            img.classList.add("is-out");
            const next = new Image();
            next.src = imgSrc(p.image_url);
            setTimeout(() => {
                img.src = next.src;
                img.alt = plain(p.name);
                img.classList.remove("is-out");
                void img.offsetWidth;
                img.classList.add("is-in");
                fill();
            }, 220);
        },
    };

    function luminance(hex) {
        const n = parseInt(hex.slice(1), 16);
        const [r, g, b] = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => v / 255);
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }

    /* ------------------- ficha de producto (efecto tornado) ------------------- */

    // Se abre girando en espiral desde la foto tocada y al cerrar vuelve
    // "absorbida" hacia el centro de la rueda. La rueda sigue girando detrás.
    const ProductCard = {
        open(p, fromEl) {
            const d = $("#pcard");
            if (!d) return;
            const name = plain(p.name);
            $("#pc-img").src = imgSrc(p.image_url);
            $("#pc-img").alt = name;
            $("#pc-cat").textContent = plain(p.category_name);
            $("#pc-name").textContent = name;
            $("#pc-desc").textContent = plain(p.description);
            const m = Catalog.measures(p.dimensions);
            const dl = $("#pc-measures");
            dl.classList.toggle("is-raw", m.raw);
            dl.replaceChildren(...m.items.map(([label, value]) => el("div", {}, [
                el("dt", { text: label }),
                el("dd", {}, m.raw ? value : [value, el("small", { text: "cm" })]),
            ])));
            $("#pc-specs").replaceChildren(
                el("dt", { text: "Material" }), el("dd", { text: plain(p.material) }),
                el("dt", { text: "Color" }), el("dd", { text: plain(p.color) }),
                el("dt", { text: "Stock" }), el("dd", { text: stockText(p) }),
            );
            $("#pc-catalog").href = `/catalogo.html?linea=${encodeURIComponent(p.category_slug || "")}`;
            $("#pc-wa").href = waLink(quoteMsg(p, name));

            d.showModal();
            if (reduceMotion.matches) return;
            const to = d.getBoundingClientRect();
            const from = fromEl.getBoundingClientRect();
            const dx = (from.left + from.width / 2) - (to.left + to.width / 2);
            const dy = (from.top + from.height / 2) - (to.top + to.height / 2);
            const s0 = Math.max(0.08, from.width / to.width);
            d.animate([
                { transform: `translate(${dx}px, ${dy}px) scale(${s0}) rotate(-540deg) skewX(18deg)`, filter: "blur(14px)", opacity: 0 },
                { offset: 0.55, transform: `translate(${dx * 0.2}px, ${dy * 0.2}px) scale(.72) rotate(-110deg) skewX(6deg)`, filter: "blur(5px)", opacity: 1 },
                { transform: "none", filter: "blur(0)", opacity: 1 },
            ], { duration: 950, easing: "cubic-bezier(.2, .8, .2, 1)" });
        },

        close() {
            const d = $("#pcard");
            if (!d.open || this.closing) return;
            if (reduceMotion.matches) { d.close(); return; }
            this.closing = true;
            const to = d.getBoundingClientRect();
            const stage = $("#ring-stage").getBoundingClientRect();
            const dx = (stage.left + stage.width / 2) - (to.left + to.width / 2);
            const dy = (stage.top + stage.height / 2) - (to.top + to.height / 2);
            d.classList.add("is-closing");
            d.animate([
                { transform: "none", filter: "blur(0)", opacity: 1 },
                { offset: 0.45, transform: `translate(${dx * 0.2}px, ${dy * 0.2}px) scale(.7) rotate(120deg) skewX(-6deg)`, filter: "blur(4px)", opacity: 1 },
                { transform: `translate(${dx}px, ${dy}px) scale(.05) rotate(620deg) skewX(-18deg)`, filter: "blur(16px)", opacity: 0 },
            ], { duration: 700, easing: "cubic-bezier(.55, 0, .75, .3)" }).finished.then(() => {
                d.close();
                d.classList.remove("is-closing");
                this.closing = false;
            });
        },

        bind() {
            const d = $("#pcard");
            if (!d) return;
            d.addEventListener("click", (e) => {
                if (e.target === d || e.target.closest("[data-close]")) this.close();
            });
            d.addEventListener("cancel", (e) => { e.preventDefault(); this.close(); });
        },
    };

    /* --------------------------- carrusel en rueda --------------------------- */

    // Crea una rueda para un escenario (#ring-stage en Inicio, #about-ring en Nosotros)
    const makeRing = (stageSel) => ({
        angle: 0,          // giro actual de la rueda, en grados
        tilt: -13,         // inclinación: la rueda se ve ovalada, con las de atrás arriba
        shiftY: 0,         // desplazamiento para que las de atrás no se corten arriba
        target: null,      // ángulo al que va cuando se usan las flechas
        visible: true,
        mounted: false,

        mount(list) {
            this.list = list;
            this.all = $$(":scope > li", list).filter((li) => li.firstElementChild);
            if (!this.all.length) return;
            this.layout();
            if (this.mounted) return;
            this.mounted = true;
            this.bind();
            this.start();
        },

        // Rueda ovalada con 9 productos (11 en pantallas anchas), vista un poco desde
        // arriba: las de atrás se ven más arriba, más chicas y en sombra. Según el
        // ancho disponible se calcula el tamaño de las tarjetas y el radio para que:
        //  1) la de adelante y las cercanas (hasta ±62°) nunca se tapen entre sí;
        //  2) toda la rueda quepa a lo ancho dentro del escenario;
        //  3) el alto del escenario alcance para que nada se corte arriba ni abajo.
        layout() {
            const stage = $(stageSel);
            stage.style.removeProperty("--cw");
            stage.style.removeProperty("--ch");
            const cs = getComputedStyle(stage);
            const first = this.all[0];
            const baseW = first.offsetWidth || 250;
            const ratio = (first.offsetHeight || baseW * 1.56) / baseW;
            const p = parseFloat(cs.perspective) || 1000;
            const half = stage.clientWidth / 2 - 12;
            const n = Math.min(this.all.length, stage.clientWidth >= 900 ? 11 : 9);
            const st = 2 * Math.PI / n;
            const GAP = 16;
            const NEAR = 62 * Math.PI / 180;
            const edges = (R, cw, th) => [-1, 1].map((sgn) => {
                const x = R * Math.sin(th) + sgn * (cw / 2) * Math.cos(th);
                const z = R * Math.cos(th) - R - sgn * (cw / 2) * Math.sin(th);
                return x * p / (p - z);
            }).sort((u, v) => u - v);
            const fits = (R, cw) => {
                for (let f = 0; f < 4; f += 1) {
                    const phi = (f / 4) * st;
                    let prev = null;
                    for (let k = -n; k <= n; k += 1) {
                        const th = phi + k * st;
                        if (Math.abs(th) > NEAR) continue;
                        const e = edges(R, cw, th);
                        if (prev && e[0] < prev[1] + GAP) return false;
                        prev = e;
                    }
                }
                return true;
            };
            const extent = (R, cw) => {
                let m = 0;
                for (let a = 0; a <= 180; a += 2) m = Math.max(m, Math.abs(edges(R, cw, a * Math.PI / 180)[1]));
                return m;
            };
            // Radio mínimo sin encimar: pasos de 8 px y luego ajuste fino de 1 px
            const needR = (w) => {
                let R = w / 2;
                while (R < 4000 && !fits(R, w)) R += 8;
                let r = Math.max(w / 2, R - 8);
                while (r < R && !fits(r, w)) r += 1;
                return r;
            };
            // Tarjeta más grande que cabe a lo ancho (de 4 en 4 px desde el tamaño normal)
            let cw = baseW, R = needR(cw);
            while (cw > 90 && extent(R, cw) > half) { cw = Math.max(90, cw - 4); R = needR(cw); }
            if (cw !== baseW) {
                stage.style.setProperty("--cw", `${cw}px`);
                stage.style.setProperty("--ch", `${Math.round(cw * ratio)}px`);
            }
            this.radius = Math.round(R);
            this.items = this.all.slice(0, n);
            this.step = 360 / n;
            this.all.forEach((li, i) => {
                li.hidden = i >= n;
                if (i < n) li.style.transform = `rotateY(${i * this.step}deg) translateZ(${this.radius}px)`;
            });
            this.fitHeight(stage);
        },

        // Mide la rueda completa girando (sin pintar) y ajusta el alto del escenario
        // y la posición vertical para que ninguna tarjeta se corte
        fitHeight(stage) {
            const saved = this.angle;
            const MARGIN = 20;
            this.shiftY = 0;
            stage.style.height = "";
            for (let pass = 0; pass < 2; pass += 1) {
                const S = stage.getBoundingClientRect();
                let top = Infinity, bottom = -Infinity;
                for (let a = 0; a < this.step; a += this.step / 4) {
                    this.angle = a;
                    this.apply();
                    for (const li of this.items) {
                        const r = li.getBoundingClientRect();
                        top = Math.min(top, r.top - S.top);
                        bottom = Math.max(bottom, r.bottom - S.top);
                    }
                }
                this.shiftY += MARGIN - top;
                stage.style.height = `${Math.ceil(bottom - top + 2 * MARGIN)}px`;
            }
            this.angle = saved;
            this.apply();
        },

        apply() {
            this.list.style.transform = `translateY(${this.shiftY}px) translateZ(${-this.radius}px) rotateX(${this.tilt}deg) rotateY(${this.angle}deg)`;
            // La de adelante brilla; hacia los lados se oscurecen y las de atrás
            // desaparecen (así ninguna asoma detrás de las de adelante)
            this.items.forEach((li, i) => {
                const a = ((i * this.step + this.angle) % 360 + 360) % 360;
                const cos = Math.cos(a * Math.PI / 180);
                const facing = (cos + 1) / 2;
                // Oscurecer con una capa y opacidad (lo procesa la tarjeta gráfica);
                // un filtro de brillo por cuadro es muy pesado en celulares.
                li.style.setProperty("--shade", (0.65 * (1 - facing)).toFixed(3));
                li.style.zIndex = String(Math.round(facing * 100));
                li.classList.toggle("is-back", facing < 0.5);
                const link = li.querySelector("a");
                if (link) link.tabIndex = facing > 0.9 ? 0 : -1;
                li.setAttribute("aria-hidden", String(facing < 0.9));
            });
        },

        // El bucle solo corre mientras la rueda está en pantalla
        start() {
            if (this.running || !this.visible) return;
            this.running = true;
            this.last = 0;
            requestAnimationFrame((t) => this.loop(t));
        },

        loop(t) {
            if (!this.visible || (this.target === null && reduceMotion.matches)) { this.running = false; return; }
            const dt = this.last ? Math.min(64, t - this.last) : 16;
            this.last = t;
            if (this.target !== null) {
                const diff = this.target - this.angle;
                this.angle += diff * 0.12;
                if (Math.abs(diff) < 0.05) { this.angle = this.target; this.target = null; }
                this.apply();
            } else if (this.visible && !reduceMotion.matches) {
                this.angle -= dt * 0.012; // ~12° por segundo
                this.apply();
            }
            requestAnimationFrame((n) => this.loop(n));
        },

        go(dir) {
            // Avanza a la siguiente tarjeta, alineada al frente
            const base = this.target !== null ? this.target : this.angle;
            this.target = Math.round(base / this.step) * this.step - dir * this.step;
            this.start();
        },

        bind() {
            const stage = $(stageSel);
            // Flechas del teclado para girar cuando el foco está en la rueda
            stage.addEventListener("keydown", (e) => {
                if (e.key === "ArrowLeft") { e.preventDefault(); this.go(-1); }
                if (e.key === "ArrowRight") { e.preventDefault(); this.go(1); }
            });

            // No gastar batería girando cuando no se ve
            if ("IntersectionObserver" in window) {
                new IntersectionObserver(([entry]) => { this.visible = entry.isIntersecting; this.start(); }).observe(stage);
            }
            // En celulares, al desplazarse la barra del navegador aparece/desaparece y
            // dispara "resize": solo se recalcula si cambió el ancho, una vez por cuadro
            let lastW = window.innerWidth, pending = false;
            window.addEventListener("resize", () => {
                if (window.innerWidth === lastW || pending) return;
                pending = true;
                requestAnimationFrame(() => { pending = false; lastW = window.innerWidth; this.layout(); });
            });
        },
    });
    const Ring = makeRing("#ring-stage");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    if (CURRENT === "catalogo") {
        const turn = (d) => {
            const next = Catalog.page + d;
            if (next < 0 || next >= Catalog.pages) return;
            Catalog.page = next;
            const grid = $("#product-grid");
            if (reduceMotion.matches || !grid.animate) { Catalog.renderGrid(true); return; }
            grid.animate([{ opacity: 1, transform: "none" }, { opacity: 0, transform: `translateX(${-d * 40}px)` }], { duration: 160, easing: "ease-in" }).finished.then(() => {
                Catalog.renderGrid(true);
                grid.animate([{ opacity: 0, transform: `translateX(${d * 40}px)` }, { opacity: 1, transform: "none" }], { duration: 260, easing: "ease-out" });
            });
        };
        $("#pager-prev").addEventListener("click", () => turn(-1));
        $("#pager-next").addEventListener("click", () => turn(1));
        let lastPer = Catalog.perPage();
        window.addEventListener("resize", () => {
            if (Catalog.perPage() !== lastPer) { lastPer = Catalog.perPage(); Catalog.renderGrid(); }
        });
    }

    /* ------------------------------ reseñas ------------------------------ */

    const PER_PAGE = 10;
    const Reviews = {
        all: [],
        shown: PER_PAGE,
        loaded: null,

        load() {
            if (!this.loaded) {
                this.loaded = api("/api/reviews").then((data) => {
                    // La base tiene reseñas repetidas de pruebas: mostramos cada una una sola vez.
                    const seen = new Set();
                    this.all = (data.reviews || []).filter((r) => {
                        const key = (plain(r.name) + "|" + plain(r.comment)).toLowerCase();
                        if (seen.has(key)) return false;
                        seen.add(key);
                        return true;
                    });
                });
                this.loaded.catch(() => { this.loaded = null; });
            }
            return this.loaded;
        },

        stats() {
            const n = this.all.length;
            const sum = this.all.reduce((s, r) => s + Number(r.rating || 0), 0);
            const dist = [5, 4, 3, 2, 1].map((star) => [star, this.all.filter((r) => Number(r.rating) === star).length]);
            return { n, avg: n ? sum / n : 0, dist };
        },

        stars(rating) {
            const r = Math.max(0, Math.min(5, Number(rating) || 0));
            return el("span", { class: "review-stars", role: "img", "aria-label": `${r} de 5 estrellas` }, [
                "★".repeat(r), el("span", { class: "off", text: "★".repeat(5 - r) }),
            ]);
        },

        async homeQuote() {
            try { await this.load(); } catch (e) { return; }
            const { n, avg } = this.stats();
            if (!n) return;
            const best = this.all.find((r) => Number(r.rating) === 5 && plain(r.comment).length > 60) || this.all.find((r) => Number(r.rating) >= 4) || this.all[0];
            $("#home-quote-empty").hidden = true;
            $("#home-quote-real").hidden = false;
            $("#home-quote-cta").textContent = "Leer todas las reseñas";
            $("#home-score").textContent = avg.toFixed(1).replace(".", ",");
            $("#home-count").textContent = n === 1 ? "1 cliente" : `${n} clientes`;
            $("#home-quote-text").textContent = plain(best.comment);
            $("#home-quote-author").textContent = [plain(best.name), plain(best.boutique) || plain(best.city)].filter(Boolean).join(", ");
        },

        async show() {
            const list = $("#review-list");
            if (!this.all.length) list.replaceChildren(el("p", { class: "muted", text: "Cargando reseñas…" }));
            try {
                await this.load();
            } catch (e) {
                list.replaceChildren(el("p", { class: "muted", text: e.message }));
                $("#rev-total").textContent = "No se pudieron cargar las reseñas.";
                return;
            }
            this.renderSummary();
            this.renderList();
        },

        renderSummary() {
            const { n, avg, dist } = this.stats();
            $("#rev-avg").textContent = n ? avg.toFixed(1).replace(".", ",") : "—";
            // El promedio y el total usan TODAS las reseñas (no solo las que se muestran)
            $("#rev-total").textContent = !n ? "Todavía no hay reseñas" : n === 1 ? "Promedio de 1 reseña" : `Promedio de ${n} reseñas`;
            $("#rev-dist").replaceChildren(...dist.map(([star, count]) => {
                const bar = el("span");
                bar.style.width = n ? `${(count / n) * 100}%` : "0";
                return el("li", { "aria-label": `${star} estrellas: ${count}` }, [
                    el("span", { text: `${star}★`, "aria-hidden": "true" }),
                    el("span", { class: "dist-bar", "aria-hidden": "true" }, bar),
                    el("span", { text: String(count), "aria-hidden": "true" }),
                ]);
            }));
        },

        // Coverflow estilo Apple: solo reseñas de 4 y 5 estrellas, en filas de 5.
        // No gira solo: al tocar una reseña lateral, esa pasa al centro.
        renderList() {
            const wrap = $("#review-list");
            (this.timers || []).forEach(clearInterval);
            this.timers = [];
            const good = this.all.filter((r) => Number(r.rating) >= 4);
            if (!good.length) {
                wrap.replaceChildren(el("p", { class: "muted", text: "Aún no hay reseñas. Si ya compraste en el stand, cuéntanos cómo te fue." }));
                return;
            }
            const rows = [];
            for (let i = 0; i < good.length; i += 5) rows.push(good.slice(i, i + 5));
            wrap.replaceChildren(...rows.map((row, ri) => this.coverflow(row, ri)));
        },

        card(r) {
            const where = [plain(r.boutique), plain(r.city)].filter(Boolean).join(", ");
            return el("article", { class: "cf-card" }, [
                this.stars(r.rating),
                el("p", { class: "cf-text", text: plain(r.comment) }),
                el("footer", { class: "cf-who" }, [
                    el("strong", { text: plain(r.name) }),
                    el("span", { text: where + (r.product_model ? ` · ${plain(r.product_model)}` : "") }),
                ]),
            ]);
        },

        // Una reseña al frente y, si hay espacio, las vecinas a los lados sin
        // quedar tapadas. Se cambia con las flechas de abajo, tocando una lateral
        // o deslizando el dedo. La altura se ajusta a la reseña más larga.
        coverflow(row, ri) {
            const n = row.length;
            const cards = row.map((r) => this.card(r));
            const track = el("div", { class: "cf-track" }, cards);
            const box = el("div", { class: "coverflow", role: "region", "aria-label": `Reseñas, grupo ${ri + 1}` }, track);
            const arrow = (label, path) => el("button", { class: "cf-arrow", type: "button", "aria-label": label }, [svgIcon(path)]);
            const prev = arrow("Reseña anterior", "M15 5l-7 7 7 7");
            const next = arrow("Reseña siguiente", "M9 5l7 7-7 7");
            const pos = el("span", { text: "1" });
            const count = el("p", { class: "cf-count", "aria-live": "polite" }, [pos, ` / ${n}`]);
            const nav = el("div", { class: "cf-nav" }, [prev, count, next]);
            nav.hidden = n < 2;
            let active = 0;
            let wide = false;
            const place = () => {
                cards.forEach((c, i) => {
                    // distancia más corta (la fila es circular)
                    let d = i - active;
                    if (d > n / 2) d -= n;
                    if (d < -n / 2) d += n;
                    const ad = Math.abs(d);
                    const shown = d === 0 || (wide && ad === 1);
                    c.style.transform = d === 0
                        ? "translateX(-50%)"
                        : wide
                            ? `translateX(calc(-50% + ${d} * (90% + 16px))) scale(.8) rotateY(${d > 0 ? -35 : 35}deg)`
                            : `translateX(calc(-50% + ${d > 0 ? 70 : -70}%)) scale(.9)`;
                    c.style.zIndex = String(10 - ad);
                    c.style.opacity = d === 0 ? "1" : shown ? ".7" : "0";
                    c.style.visibility = shown ? "visible" : "hidden";
                    c.classList.toggle("is-active", d === 0);
                    c.setAttribute("aria-hidden", String(d !== 0));
                    c.onclick = () => { if (active !== i) go(i - active); };
                    c.tabIndex = d !== 0 && shown ? 0 : -1;
                    c.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); c.onclick(); } };
                });
                pos.textContent = String(active + 1);
            };
            const go = (step) => { active = (active + step + n) % n; place(); };
            prev.onclick = () => go(-1);
            next.onclick = () => go(1);
            // Deslizar con el dedo
            let x0 = null;
            box.addEventListener("pointerdown", (e) => { x0 = e.clientX; });
            box.addEventListener("pointerup", (e) => {
                if (x0 === null) return;
                const dx = e.clientX - x0;
                x0 = null;
                if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1);
            });
            // Ancho de tarjeta según el espacio y alto según la reseña más larga
            let lastW = 0;
            const fit = () => {
                const W = box.clientWidth;
                // solo cuando cambia el ancho (cambiar el alto no debe volver a medir)
                if (!W || W === lastW) return;
                lastW = W;
                wide = W >= 700 && n > 1;
                // En 3D la lateral se ve ≈0,8 del ancho: centro + separación + lateral
                // deben caber en la mitad de la caja
                const w = wide ? Math.min(340, (W / 2 - 24) / 1.32) : Math.min(440, W);
                box.style.setProperty("--cf-w", `${Math.floor(w)}px`);
                const h = Math.max(...cards.map((c) => c.offsetHeight));
                box.style.height = `${h + 24}px`;
                place();
            };
            new ResizeObserver(() => requestAnimationFrame(fit)).observe(box);
            place();
            return el("div", { class: "cf-group" }, [box, nav]);
        },
    };

    if (CURRENT === "resenas") {
        $("#open-review-form").addEventListener("click", () => $("#review-dialog").showModal());

        $("#review-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const form = e.currentTarget;
            if (!validate(form)) return;
            const btn = $("button[type=submit]", form);
            const data = formData(form);
            data.rating = Number(data.rating);
            busy(btn, true, "Publicando…");
            try {
                const res = await api("/api/reviews", { method: "POST", body: JSON.stringify(data) });
                Reviews.all.unshift(res.review);
                Reviews.renderSummary();
                Reviews.renderList();
                form.reset();
                $("#review-dialog").close();
                toast("Reseña publicada. Gracias por contarnos tu experiencia.");
            } catch (err) {
                showFormError(form, err.message);
            } finally {
                busy(btn, false);
            }
        });
    }

    /* ------------------------------ diálogos ------------------------------ */

    $$("dialog:not(#pcard)").forEach((d) => {
        d.addEventListener("click", (e) => {
            if (e.target === d || e.target.closest("[data-close]")) d.close();
        });
    });

    /* ------------------------------ contacto ------------------------------ */

    if (CURRENT === "nosotros") {
        $("#contact-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const form = e.currentTarget;
            if (!validate(form)) return;
            const data = formData(form);
            if (data.website) return; // campo trampa para bots
            const btn = $("button[type=submit]", form);
            busy(btn, true, "Enviando…");
            try {
                await api("/api/contact", {
                    method: "POST",
                    body: JSON.stringify({ name: data.name, email: data.email, phone: data.phone, subject: data.subject, message: data.message }),
                });
                form.reset();
                toast("Mensaje enviado. Te respondemos en horario de atención.");
            } catch (err) {
                showFormError(form, err.message);
            } finally {
                busy(btn, false);
            }
        });
    }

    /* ----------------------- libro de reclamaciones ----------------------- */

    if (CURRENT === "reclamaciones") {
        const today = new Date();
        $("#claim-date").textContent = today.toLocaleDateString("es-PE", { day: "numeric", month: "long", year: "numeric" });

        const minor = $("#claim-minor");
        minor.addEventListener("change", () => {
            const field = $("#guardian-field");
            field.hidden = !minor.checked;
            $("input", field).required = minor.checked;
        });

        $("#claims-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const form = e.currentTarget;
            if (!validate(form)) return;
            const data = formData(form);
            const payload = {
                claim_type: data.claim_type,
                full_name: data.full_name,
                doc_type: data.doc_type,
                doc_number: data.doc_number,
                email: data.email,
                phone: data.phone,
                address: data.address,
                is_minor: minor.checked,
                guardian_name: data.guardian_name || "",
                contracted_good: data.contracted_good,
                amount_claimed: Number(data.amount_claimed || 0),
                good_description: data.good_description,
                claim_description: data.claim_description,
                consumer_request: data.consumer_request,
            };
            const btn = $("button[type=submit]", form);
            busy(btn, true, "Registrando…");
            try {
                const res = await api("/api/claims", { method: "POST", body: JSON.stringify(payload) });
                showReceipt(res.data, payload);
                form.reset();
                $("#guardian-field").hidden = true;
            } catch (err) {
                showFormError(form, err.message);
            } finally {
                busy(btn, false);
            }
        });

        function showReceipt(result, payload) {
            $("#claims-sheet").hidden = true;
            const receipt = $("#claim-receipt");
            $("#receipt-code").textContent = result.claim_code;
            const when = result.created_at ? new Date(result.created_at) : new Date();
            const rows = [
                ["Tipo", result.claim_type],
                ["Fecha", when.toLocaleString("es-PE", { dateStyle: "long", timeStyle: "short" })],
                ["Consumidor", `${payload.full_name} (${payload.doc_type} ${payload.doc_number})`],
                ["Correo", payload.email],
                ["Bien contratado", `${payload.contracted_good}: ${payload.good_description}`],
                ["Monto reclamado", soles(payload.amount_claimed)],
                ["Detalle", payload.claim_description],
                ["Pedido", payload.consumer_request],
                ["Proveedor", "Romero Enriquez Patrick Junior, RUC 10727851971"],
            ];
            $("#receipt-data").replaceChildren(...rows.flatMap(([k, v]) => [el("dt", { text: k }), el("dd", { text: v })]));
            receipt.hidden = false;
            receipt.scrollIntoView();
            receipt.focus({ preventScroll: true });
        }

        $("#receipt-print").addEventListener("click", () => window.print());
        $("#receipt-new").addEventListener("click", () => {
            $("#claim-receipt").hidden = true;
            $("#claims-sheet").hidden = false;
            $("#claims-sheet").scrollIntoView();
        });
    }

    /* ---------------------- entradas al hacer scroll ---------------------- */

    // Los bloques con data-reveal entran desde su costado al aparecer en
    // pantalla y vuelven a salir cuando se van, para animarse otra vez.
    const revealables = $$("[data-reveal], [data-reveal-children]");
    if (revealables.length && "IntersectionObserver" in window) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => entry.target.classList.toggle("is-in", entry.isIntersecting));
        }, { threshold: 0.15 });
        revealables.forEach((el) => io.observe(el));
    } else {
        revealables.forEach((el) => el.classList.add("is-in"));
    }

    /* ------------------------------ arranque ------------------------------ */

    $("#year").textContent = String(new Date().getFullYear());
    updateHeader();
    if (CURRENT === "nosotros" && $("#about-ring")) makeRing("#about-ring").mount($("#about-lineup"));
    if (CURRENT === "inicio") { ProductCard.bind(); Catalog.renderLineup(); Reviews.homeQuote(); }
    if (CURRENT === "catalogo") Catalog.show(new URLSearchParams(location.search).get("linea"));
    if (CURRENT === "resenas") Reviews.show();
})();
