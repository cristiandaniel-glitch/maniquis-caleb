/* ==========================================================================
   Escena de Inicio: capas 2D movidas por el scroll.

   El avance del scroll dentro de #scene se traduce a un número p de 0 a 1,
   y cada capa lee su propio tramo de p:

     0.00 – 0.26  sube la fachada sobre el cielo, se va el título
     0.20 – 0.30  aparece el texto pintado en las paredes
     0.30 – 0.46  se abren las cortinas de la vitrina
     0.48 – 0.70  zoom: "entramos" por la vitrina (el interior se ve recortado
                  exactamente al hueco del vidrio y crece con él)
     0.66 – 0.90  llegan los maniquíes, la mano con la cinta y los objetos
     0.84 – 0.94  aparece el texto final con los botones
   ========================================================================== */
(function () {
    "use strict";

    const scene = document.getElementById("scene");
    if (!scene) return;

    const get = (id) => document.getElementById(id);
    const sticky = scene.querySelector(".scene-sticky");
    const L = {
        cielo: get("l-cielo"), interior: get("l-interior"), interiorBg: get("l-interior-bg"),
        negro: get("p-negro"), busto: get("p-busto"), blanco: get("p-blanco"),
        facade: get("facade"), curtainL: get("curtain-l"), curtainR: get("curtain-r"),
        tijeras: get("f-tijeras"), hilo: get("f-hilo"), alfileres: get("f-alfileres"),
        etiqueta: get("f-etiqueta"), mano: get("f-mano"), percha: get("f-percha"),
        intro: get("t-intro"), final: get("t-final"),
        wallL: get("wall-left"), wallR: get("wall-right"),
    };
    const introTitle = L.intro.querySelector("h1");
    const introLead = L.intro.querySelector(".lead");
    const introCue = L.intro.querySelector(".scroll-cue");
    const castBlanco = scene.querySelector(".cast-blanco");
    const castNegro = scene.querySelector(".cast-negro");
    const finalTitle = L.final.querySelector("h2");
    const finalLead = L.final.querySelector(".lead");
    const finalActions = L.final.querySelector(".actions");

    // El título de entrada se parte en letras para que caigan una por una.
    // El lector de pantalla sigue leyendo el texto completo por aria-label.
    (function splitTitle() {
        const text = introTitle.textContent.trim();
        introTitle.setAttribute("aria-label", text);
        introTitle.textContent = "";
        let i = 0;
        text.split(" ").forEach((word, w) => {
            if (w > 0) introTitle.append(" ");
            const wordEl = document.createElement("span");
            wordEl.className = "word";
            wordEl.setAttribute("aria-hidden", "true");
            for (const letter of word) {
                const ch = document.createElement("span");
                ch.className = "ch";
                ch.style.setProperty("--i", i++);
                ch.textContent = letter;
                wordEl.append(ch);
            }
            introTitle.append(wordEl);
        });
    })();

    // Se usa la propiedad CSS "translate" (no "transform") para el scroll,
    // así no choca con las animaciones de entrada que usan transform.
    const slide = (el, x, y = 0, opacity) => {
        el.style.translate = `${x} ${y}`;
        if (opacity !== undefined) el.style.opacity = String(opacity);
    };

    // fachada.webp mide 1024×559; la vitrina ocupa este rectángulo (en fracciones)
    const AR = 1024 / 559;
    const WIN = { x: 0.376, y: 0.2916, w: 0.2471, h: 0.4007 };
    // El hueco real del marco (385–639 × 162–388 px) es apenas mayor que WIN; el
    // interior se recorta 5 px más por lado para que quede detrás de la madera y
    // no asome el cielo por los bordes al hacer zoom.
    const CLIP = { w: 264 / 1024, h: 236 / 559 };

    const clamp = (v) => Math.min(1, Math.max(0, v));
    const seg = (p, a, b) => clamp((p - a) / (b - a));
    const easeOut = (t) => 1 - Math.pow(1 - t, 3);
    const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

    let vw, vh, fw, fh, fl, ft, zoomMax, winCx, winCy;

    // La fachada se dimensiona como object-fit: cover y se centra.
    // Las dos paredes con texto ocupan de ~6% a ~94% del ancho de la fachada.
    const WALLS_VISIBLE = 0.9;
    const wallBox = L.wallL.parentNode;
    const sticky2 = sticky;
    function layout() {
        vw = sticky.clientWidth;
        vh = sticky.clientHeight;
        // Llenar la pantalla (cover), pero sin recortar tanto que se pierdan las
        // paredes: si hace falta, la fachada se achica y se apoya abajo; el
        // cielo queda visible arriba.
        fw = Math.min(Math.max(vw, vh * AR), vw / WALLS_VISIBLE);
        fh = fw / AR;
        fl = (vw - fw) / 2;
        ft = fh >= vh ? (vh - fh) / 2 : vh - fh;

        // Si cada pared mide menos de ~230 px, el texto no cabe: se muestra
        // sobre el cielo (fuera de la fachada) en vez de pintado en la pared.
        const out = fw * 0.205 < 230;
        scene.classList.toggle("walls-out", out);
        const host = out ? sticky2 : wallBox;
        if (L.wallL.parentNode !== host) { host.append(L.wallL, L.wallR); }
        // Que el texto de la pared izquierda no quede bajo las burbujas de redes (≈ 90 px)
        const bubbles = window.innerWidth > 760 ? 92 : 0;
        const leftEdge = fl + fw * 0.104;
        L.wallL.style.marginLeft = !out && leftEdge < bubbles ? `${bubbles - leftEdge}px` : "";
        winCx = fw * (WIN.x + WIN.w / 2);
        winCy = fh * (WIN.y + WIN.h / 2);
        // escala a la que la vitrina cubre toda la pantalla
        zoomMax = Math.max(vw / (fw * WIN.w), vh / (fh * WIN.h)) * 1.06;
        Object.assign(L.facade.style, {
            width: fw + "px", height: fh + "px", left: fl + "px", top: ft + "px",
            transformOrigin: `${winCx}px ${winCy}px`,
        });
    }

    function frame(p) {
        // 1. Cielo y título de entrada
        const sky = seg(p, 0, 0.3);
        L.cielo.style.transform = `scale(${1.12 - 0.12 * sky}) translateY(${-3 * sky}vh)`;
        // Al bajar: el título y el subtítulo salen por la izquierda…
        const outTitle = Math.pow(seg(p, 0.01, 0.12), 1.6);
        const outLead = Math.pow(seg(p, 0.025, 0.14), 1.6);
        slide(introTitle, `${-75 * outTitle}vw`);
        slide(introLead, `${-75 * outLead}vw`);
        introCue.style.translate = `0 ${seg(p, 0, 0.04) * 20}px`;
        introCue.style.visibility = p > 0.04 ? "hidden" : "visible";
        L.intro.style.visibility = outLead >= 1 ? "hidden" : "visible";

        // …y los maniquíes por la derecha, cada uno a su ritmo
        slide(castBlanco, `${55 * Math.pow(seg(p, 0.02, 0.15), 1.5)}vw`);
        slide(castNegro, `${55 * Math.pow(seg(p, 0.01, 0.13), 1.5)}vw`);

        // 2. La fachada sube y 3. hace zoom hacia la vitrina
        const rise = easeOut(seg(p, 0.06, 0.26));
        const z = seg(p, 0.48, 0.7);
        const scale = 1 + (zoomMax - 1) * Math.pow(z, 2.2);
        const move = easeInOut(z);
        const dx = (vw / 2 - (fl + winCx)) * move;
        const dy = (vh / 2 - (ft + winCy)) * move + (1 - rise) * vh;
        L.facade.style.transform = `translate(${dx}px, ${dy}px) scale(${scale})`;
        const facadeGone = seg(p, 0.64, 0.7);
        L.facade.style.opacity = String(1 - facadeGone);
        L.facade.style.visibility = facadeGone >= 1 ? "hidden" : "visible";

        // Texto pintado en las paredes: aparece cuando la fachada ya subió
        const paint = seg(p, 0.2, 0.3);
        const paintE = easeOut(paint);
        // Fuera de la fachada (pantallas angostas) se retiran antes del zoom
        const wallsGone = scene.classList.contains("walls-out") ? seg(p, 0.42, 0.5) : 0;
        const wallOpacity = paint * (1 - wallsGone);
        slide(L.wallL, `${(1 - paintE) * -6}vw`, 0, wallOpacity);
        slide(L.wallR, `${(1 - paintE) * 6}vw`, 0, wallOpacity);
        L.wallL.style.visibility = L.wallR.style.visibility = wallOpacity > 0.01 ? "visible" : "hidden";

        // Cortinas
        const open = easeInOut(seg(p, 0.3, 0.46));
        L.curtainL.style.transform = `translateX(${-100 * open}%)`;
        L.curtainR.style.transform = `translateX(${100 * open}%)`;

        // El interior solo se ve a través del hueco de la vitrina
        if (facadeGone >= 1) {
            L.interior.style.clipPath = "none";
        } else {
            const cx = fl + winCx + dx;
            const cy = ft + winCy + dy;
            const hw = (fw * CLIP.w * scale) / 2;
            const hh = (fh * CLIP.h * scale) / 2;
            const top = Math.max(0, cy - hh), left = Math.max(0, cx - hw);
            const right = Math.max(0, vw - (cx + hw)), bottom = Math.max(0, vh - (cy + hh));
            L.interior.style.clipPath = `inset(${top}px ${right}px ${bottom}px ${left}px)`;
        }
        L.interiorBg.style.transform = `scale(${1.25 - 0.25 * easeOut(seg(p, 0.45, 0.82))})`;

        // 4. Maniquíes: cada uno llega a su propio ritmo
        const neg = easeOut(seg(p, 0.66, 0.82));
        const bla = easeOut(seg(p, 0.69, 0.85));
        const bus = easeOut(seg(p, 0.72, 0.87));
        L.negro.style.transform = `translateX(calc(-50% - ${(1 - neg) * 70}vw))`;
        L.blanco.style.transform = `translateX(calc(-50% + ${(1 - bla) * 70}vw))`;
        L.busto.style.transform = `translate(-50%, ${(1 - bus) * 80}vh)`;

        // Objetos flotantes: distinta velocidad = sensación de profundidad
        const drift = seg(p, 0.66, 1);
        const show = seg(p, 0.66, 0.74);
        const floatIn = (el, fromY, rot, speed) => {
            el.style.opacity = String(show);
            el.style.transform = `translateY(${(1 - easeOut(drift)) * fromY - drift * speed}vh) rotate(${rot * (1 - drift) + rot * 0.2}deg)`;
        };
        floatIn(L.tijeras, -60, -28, 4);
        floatIn(L.alfileres, -80, 40, 8);
        floatIn(L.etiqueta, 70, -35, 6);
        floatIn(L.hilo, 60, 20, 3);

        const hand = easeOut(seg(p, 0.74, 0.9));
        L.mano.style.opacity = String(show);
        L.mano.style.transform = `translateX(${(1 - hand) * 110}%) rotate(${(1 - hand) * -8}deg)`;

        const rack = easeOut(seg(p, 0.7, 0.88));
        L.percha.style.opacity = String(show);
        L.percha.style.transform = `translateX(${(1 - rack) * -100 - seg(p, 0.88, 1) * 6}%)`;

        // 5. Texto final: el titular entra por la izquierda, luego el texto y los botones suben
        const fTitle = easeOut(seg(p, 0.82, 0.9));
        const fLead = easeOut(seg(p, 0.85, 0.93));
        const fActions = easeOut(seg(p, 0.88, 0.96));
        slide(finalTitle, `${(1 - fTitle) * -45}vw`, 0, fTitle);
        slide(finalLead, `${(1 - fLead) * -30}vw`, 0, fLead);
        slide(finalActions, 0, `${(1 - fActions) * 40}px`, fActions);
        L.final.style.visibility = fTitle > 0.01 ? "visible" : "hidden";
    }

    /* ------------- maniquíes de la portada: giro 3D mientras esperas ------------- */
    // Siguen al mouse girando un poco sobre su eje; si no hay mouse (o no se
    // mueve por 2 s) giran solos, lento, a un lado y al otro.
    const tilt = { x: 0, target: 0, lastMove: -Infinity };
    scene.addEventListener("pointermove", (e) => {
        if (e.pointerType !== "mouse") return;
        tilt.target = ((e.clientX / window.innerWidth) - 0.5) * 2 * 22; // ±22°
        tilt.lastMove = performance.now();
    });
    // El giro solo corre mientras la portada está a la vista; al bajar se
    // detiene por completo (no consume CPU) y vuelve a arrancar al subir.
    let spinning = false;
    function spin(now) {
        if (reduce.matches || window.scrollY > window.innerHeight * 0.6) { spinning = false; return; }
        if (now - tilt.lastMove > 2000) tilt.target = Math.sin(now / 2600) * 14;
        const prev = tilt.x;
        tilt.x += (tilt.target - tilt.x) * 0.05;
        if (Math.abs(tilt.x - prev) > 0.01) {
            castBlanco.style.rotate = `y ${tilt.x.toFixed(2)}deg`;
            castNegro.style.rotate = `y ${(tilt.x * 0.85).toFixed(2)}deg`;
        }
        requestAnimationFrame(spin);
    }
    const startSpin = () => { if (!spinning && !reduce.matches && window.scrollY <= window.innerHeight * 0.6) { spinning = true; requestAnimationFrame(spin); } };
    window.addEventListener("scroll", startSpin, { passive: true });

    function progress() {
        const total = scene.offsetHeight - vh;
        return total > 0 ? clamp(-scene.getBoundingClientRect().top / total) : 1;
    }

    // ?animar fuerza la animación aunque el sistema pida reducir movimiento (para revisarla).
    const force = new URLSearchParams(location.search).has("animar");
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const reduce = { get matches() { return mq.matches && !force; } };
    let ticking = false;
    let lastP = -1;
    function update() {
        ticking = false;
        const p = reduce.matches ? 1 : progress();
        // Pasada la escena (o antes de empezar) no hay nada que mover
        if (p === lastP && (p === 0 || p === 1)) return;
        lastP = p;
        frame(p);
    }
    function request() {
        if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }
    function setup() {
        lastP = -1;
        // Con movimiento reducido se muestra directamente la escena final, sin recorrido.
        scene.classList.toggle("is-static", reduce.matches);
        layout();
        update();
    }

    window.addEventListener("scroll", request, { passive: true });
    // Resize: una vez por cuadro y solo si cambió el tamaño real de la escena (en
    // celulares la barra del navegador dispara "resize" al desplazarse)
    let lastSize = "", resizeQueued = false;
    window.addEventListener("resize", () => {
        if (resizeQueued) return;
        resizeQueued = true;
        requestAnimationFrame(() => {
            resizeQueued = false;
            const size = `${sticky.clientWidth}x${sticky.clientHeight}`;
            if (size === lastSize) return;
            lastSize = size;
            setup();
        });
    });
    if (mq.addEventListener) mq.addEventListener("change", setup); else mq.addListener(setup); // iOS 13
    const root = document.documentElement;
    const withIntro = root.classList.contains("with-intro");
    const store = {
        get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
        set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* sin almacenamiento */ } },
    };
    // Recordar dónde quedó el scroll para volver al mismo punto
    window.addEventListener("pagehide", () => store.set("caleb-scroll", String(Math.round(window.scrollY))));
    if (withIntro) {
        window.scrollTo(0, 0);
    } else {
        window.scrollTo(0, Number(store.get("caleb-scroll")) || 0);
    }
    setup();
    startSpin();

    /* ------------------------- pantalla de carga ------------------------- */
    // La cinta avanza según las capas que realmente terminaron de cargar,
    // con un mínimo de 0,7 s para que se alcance a ver y un tope de 3 s
    // por si alguna imagen falla.
    const loader = get("loader");
    const ready = () => { scene.classList.add("is-ready"); store.set("caleb-intro", "1"); };
    if (!loader || !withIntro) {
        if (loader) loader.remove();
        ready();
        return;
    }

    const fill = get("loader-fill");
    const urls = Array.from(new Set(Array.from(scene.querySelectorAll("img")).map((img) => img.currentSrc || img.src)));
    const total = urls.length + 1;
    let loaded = 0;
    const done = () => { loaded += 1; };
    urls.forEach((url) => {
        const img = new Image();
        img.onload = img.onerror = done;
        img.src = url;
    });
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(done);

    const start = performance.now();
    const minTime = reduce.matches ? 200 : 700;
    let shown = 0;
    function tick(now) {
        const elapsed = now - start;
        const goal = Math.min(loaded / total, elapsed / minTime, 1);
        shown += (goal - shown) * 0.3;
        const complete = (goal >= 1 && shown > 0.99) || elapsed > 3000;
        if (complete) shown = 1;
        fill.style.width = `max(8px, ${(shown * 100).toFixed(1)}%)`;
        if (!complete) { requestAnimationFrame(tick); return; }
        setTimeout(() => {
            loader.classList.add("is-done");
            document.documentElement.classList.remove("is-loading");
            ready();
            setTimeout(() => loader.remove(), reduce.matches ? 0 : 850);
        }, 120);
    }
    requestAnimationFrame(tick);
})();
