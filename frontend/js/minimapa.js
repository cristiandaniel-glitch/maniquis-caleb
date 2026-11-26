/* ==========================================================================
   Minimapa de Google Maps (esquina inferior izquierda)

   - Una burbuja redonda muestra el mapa alrededor del stand.
   - Al tocarla se abre el mapa completo con tres vistas: Mapa, Satélite y
     Croquis 3D (vista satelital inclinada), más "Cómo llegar" y Google Earth 3D.
   - El mapa de la burbuja se carga después de que la página terminó de
     cargar, para no hacerla más lenta. En equipos lentos (clase "lite") la
     burbuja muestra solo el ícono y el mapa se carga al abrirla.
   - Sin claves ni API de pago: usa el mapa incrustado público de Google.
   ========================================================================== */
(function () {
    "use strict";

    const PLACE = {
        lat: -13.530833,
        lng: -71.93266,
        name: "Maniquíes y Exhibidores Caleb",
        address: "Galería La Exitosa, stand 3 · Calle 119 Tomás Tuyro Túpac, San Sebastián, Cusco",
    };
    const coords = `${PLACE.lat},${PLACE.lng}`;
    const embed = (zoom, satellite) =>
        `https://www.google.com/maps?q=${coords}&z=${zoom}&hl=es${satellite ? "&t=k" : ""}&output=embed`;
    const LINKS = {
        directions: `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(coords)}`,
        open: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(coords)}`,
        earth3d: `https://earth.google.com/web/@${coords},3400a,350d,35y,20h,65t,0r`,
    };
    const VIEWS = {
        mapa: { label: "Mapa", src: embed(17, false) },
        satelite: { label: "Satélite", src: embed(18, true) },
        croquis: { label: "Croquis 3D", src: embed(18, true) },
    };

    const NS = "http://www.w3.org/2000/svg";
    function icon(paths, size = 22) {
        const svg = document.createElementNS(NS, "svg");
        svg.setAttribute("viewBox", "0 0 24 24");
        svg.setAttribute("width", String(size));
        svg.setAttribute("height", String(size));
        svg.setAttribute("aria-hidden", "true");
        paths.forEach((d) => {
            const p = document.createElementNS(NS, "path");
            p.setAttribute("d", d);
            svg.append(p);
        });
        return svg;
    }
    const PIN = ["M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z", "M12 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"];
    const ROUTE = ["M3 11l18-8-8 18-2-8-8-2z"];
    const GLOBE = ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z", "M3 12h18", "M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"];
    const CLOSE = ["M6 6l12 12M18 6 6 18"];

    function el(tag, props = {}, children = []) {
        const node = document.createElement(tag);
        Object.entries(props).forEach(([k, v]) => {
            if (v == null) return;
            if (k === "class") node.className = v;
            else if (k === "text") node.textContent = v;
            else node.setAttribute(k, v);
        });
        [].concat(children).forEach((c) => c != null && node.append(c));
        return node;
    }

    function frame(src, title) {
        return el("iframe", {
            src,
            title,
            loading: "lazy",
            referrerpolicy: "no-referrer-when-downgrade",
            allowfullscreen: "",
        });
    }

    /* ------------------------------ burbuja ------------------------------ */
    const bubble = el("button", {
        class: "minimap",
        type: "button",
        "aria-haspopup": "dialog",
        "aria-label": "Ver nuestra ubicación en el mapa",
        "data-label": "¿Cómo llegar? Ver mapa",
    }, [
        el("span", { class: "minimap-view", "aria-hidden": "true" }),
        el("span", { class: "minimap-pin", "aria-hidden": "true" }, icon(PIN, 26)),
    ]);
    document.body.append(bubble);

    const lite = document.documentElement.classList.contains("lite");
    function loadBubbleMap() {
        if (lite || bubble.classList.contains("has-map")) return;
        const view = bubble.querySelector(".minimap-view");
        const f = frame(VIEWS.mapa.src, "Minimapa de la tienda");
        f.tabIndex = -1;
        f.addEventListener("load", () => bubble.classList.add("is-ready"), { once: true });
        view.append(f);
        bubble.classList.add("has-map");
    }

    // Espera a que la página (y la pantalla de carga de Inicio) terminen.
    function whenPageIsReady(cb) {
        const root = document.documentElement;
        const go = () => {
            const run = () => setTimeout(cb, 900);
            if (!root.classList.contains("is-loading")) return run();
            const mo = new MutationObserver(() => {
                if (!root.classList.contains("is-loading")) { mo.disconnect(); run(); }
            });
            mo.observe(root, { attributes: true, attributeFilter: ["class"] });
        };
        if (document.readyState === "complete") go();
        else window.addEventListener("load", go, { once: true });
    }
    whenPageIsReady(loadBubbleMap);

    /* ------------------------------ mapa completo ------------------------------ */
    let dialog;
    let stage;
    let current;

    function buildDialog() {
        const tabs = el("div", { class: "map-tabs", role: "tablist", "aria-label": "Tipo de mapa" });
        Object.entries(VIEWS).forEach(([key, view]) => {
            const tab = el("button", { type: "button", role: "tab", "data-view": key, "aria-selected": "false", text: view.label });
            tab.addEventListener("click", () => show(key));
            tabs.append(tab);
        });
        tabs.addEventListener("keydown", (e) => {
            const keys = Object.keys(VIEWS);
            const step = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
            if (!step) return;
            const next = keys[(keys.indexOf(current) + step + keys.length) % keys.length];
            show(next);
            tabs.querySelector(`[data-view="${next}"]`).focus();
        });

        const close = el("button", { class: "map-close", type: "button", "aria-label": "Cerrar mapa" }, icon(CLOSE, 22));
        close.addEventListener("click", () => dialog.close());

        stage = el("div", { class: "map-stage", role: "tabpanel" });

        dialog = el("dialog", { class: "map-dialog", "aria-labelledby": "map-title" }, [
            el("header", { class: "map-head" }, [
                el("div", { class: "map-title-wrap" }, [
                    el("p", { class: "map-kicker", text: "Visítanos" }),
                    el("h2", { id: "map-title", class: "map-title", text: PLACE.name }),
                    el("p", { class: "map-address", text: PLACE.address }),
                ]),
                close,
            ]),
            el("div", { class: "map-toolbar" }, [
                tabs,
                el("div", { class: "map-actions" }, [
                    el("a", { class: "btn btn-tape map-btn", href: LINKS.directions, target: "_blank", rel: "noopener" }, [icon(ROUTE, 18), "Cómo llegar"]),
                    el("a", { class: "btn btn-ghost-light map-btn", href: LINKS.earth3d, target: "_blank", rel: "noopener" }, [icon(GLOBE, 18), "Ver en 3D"]),
                ]),
            ]),
            stage,
            el("p", { class: "map-foot" }, [
                "Frente a Tottus, 4.º paradero de San Sebastián. ",
                el("a", { href: LINKS.open, target: "_blank", rel: "noopener", text: "Abrir en la app de Google Maps" }),
            ]),
        ]);
        dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
        dialog.addEventListener("close", () => {
            document.documentElement.classList.remove("map-open");
            bubble.focus({ preventScroll: true });
        });
        document.body.append(dialog);
    }

    function show(key) {
        if (key === current) return;
        current = key;
        dialog.querySelectorAll(".map-tabs [role=tab]").forEach((t) => {
            const on = t.dataset.view === key;
            t.setAttribute("aria-selected", String(on));
            t.tabIndex = on ? 0 : -1;
        });
        stage.className = `map-stage is-${key}`;
        const view = VIEWS[key];
        const f = frame(view.src, `${view.label} de la ubicación de la tienda`);
        f.loading = "eager";
        if (key === "croquis") {
            // Croquis 3D: la vista satelital inclinada en perspectiva, con cielo y
            // una marca flotante sobre el stand.
            stage.replaceChildren(
                el("div", { class: "map-sky", "aria-hidden": "true" }),
                // La marca va DENTRO del plano inclinado, en su centro exacto (donde
                // Google pone el punto), y se "levanta" para quedar de pie en 3D.
                el("div", { class: "map-tilt" }, [
                    f,
                    el("span", { class: "map-marker", "aria-hidden": "true" }, [icon(PIN, 34), el("b", { text: "Stand 3" })]),
                ]),
                el("p", { class: "map-hint", text: "Vista inclinada de referencia. Para edificios en 3D reales, usa «Ver en 3D» (Google Earth)." }),
            );
        } else {
            stage.replaceChildren(f);
        }
    }

    bubble.addEventListener("click", () => {
        if (!dialog) buildDialog();
        current = null;
        show("mapa");
        document.documentElement.classList.add("map-open");
        dialog.showModal();
    });
})();
