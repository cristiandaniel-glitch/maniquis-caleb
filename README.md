# 🏛️ Maniquíes y Exhibidores Caleb — Sitio web y panel de administración

Sitio web, catálogo y panel de administración de **Maniquíes y Exhibidores Caleb** (Galería La Exitosa, stand 3, San Sebastián, Cusco).

Incluye **Frontend interactivo** de alta gama, **Backend REST API** en Python nativo, **PostgreSQL alojado en Supabase**, **Módulo de Seguridad Integral**, **Libro de Reclamaciones Virtual** conforme a ley y **Centro de Políticas Legales** libres de derechos de autor.

---

## 📁 Estructura del Proyecto

```
maniquis-caleb/
├── server.py                 # Punto de entrada: python3 server.py
├── backend/
│   ├── config.py             # Configuración (lee .env) y datos oficiales de la empresa
│   ├── database.py           # Pool PostgreSQL/Supabase y consultas parametrizadas
│   ├── app.py                # Compatibilidad: expone run_server()
│   ├── web/                  # Capa HTTP
│   │   ├── server.py         # Servidor multihilo + procesos de trabajo
│   │   ├── handler.py        # Recibe cada petición: rate limit, token, JSON, errores
│   │   ├── router.py         # Enrutador declarativo (@router.get / post / put ...)
│   │   ├── headers.py        # CSP y cabeceras de seguridad, CORS con lista blanca
│   │   ├── static.py         # Archivos del frontend (lista blanca de extensiones)
│   │   └── cache.py          # Caché corta de respuestas públicas
│   ├── routes/               # Controladores de la API (un archivo por tema)
│   │   ├── products.py  categories.py  reviews.py  claims.py
│   │   ├── messages.py  newsletter.py  stats.py  legal.py  auth.py  health.py
│   ├── models/               # Consultas y validación de cada tipo de registro
│   │   ├── product.py  category.py  review.py  claim.py  message.py  subscriber.py
│   └── core/                 # Lógica transversal
│       ├── auth.py           # Contraseña PBKDF2, tokens firmados, bloqueo anti fuerza bruta
│       ├── validation.py     # Limpieza y conversión de datos (errores 400 claros)
│       ├── ratelimit.py      # Límite de peticiones por IP
│       └── moderation.py     # Filtro de groserías para reseñas
├── scripts/
│   └── generar_clave_admin.py  # Genera la contraseña del panel para el .env
├── database/                 # Esquema PostgreSQL, migración desde SQLite
├── frontend/                 # HTML, CSS, JS e imágenes
│   └── js/minimapa.js        # Minimapa de Google Maps (esquina inferior izquierda)
├── test_security.py          # Auditoría de seguridad (servidor encendido)
└── test_system.py            # Pruebas de integración de la API
```

**Cómo agregar una ruta nueva:** crea la función en `backend/routes/<tema>.py`,
decórala con `@router.get("/api/...")` (o `post`, `put`, `patch`, `delete`) y,
si es del panel, añade `admin=True`. El manejador se encarga del rate limit,
del token, de leer el JSON y de convertir los errores de validación en 400.

---

## 🛡️ Seguridad Implementada

1. **Sin contraseña por defecto**: el panel solo funciona con `ADMIN_SALT` y `ADMIN_PASSWORD_HASH` propios en el `.env` (PBKDF2-SHA256, 100 000 iteraciones). El hash de ejemplo que estuvo publicado en el repositorio está bloqueado.
2. **Inyección SQL**: todas las consultas son parametrizadas (`%s` de psycopg).
3. **XSS**: los textos se escapan en el servidor y el frontend los pinta con `textContent`. La CSP bloquea scripts externos.
4. **Archivos**: solo se sirven archivos dentro de `frontend/` con extensiones permitidas; rutas codificadas (`%2e%2e`, `%5c`, `%00`) devuelven 404.
5. **Peticiones malformadas**: JSON inválido, que no sea objeto, demasiado grande, sin `Content-Type: application/json` o con `Content-Length` falso se rechazan con 400/411/413/415. Los errores internos nunca muestran detalles al visitante.
6. **Rate limiting** por IP (API, formularios y login por separado) y **bloqueo de login** tras 5 intentos fallidos (10 min), guardado en PostgreSQL.
7. **CORS** solo para dominios de la lista blanca (antes reflejaba cualquier origen).
8. **Cabeceras**: CSP, `X-Frame-Options`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, HSTS opcional (`ENABLE_HSTS=true`), sin revelar la versión de Python.
9. **Detrás de un proxy** (Render, Nginx, Cloudflare): activar `TRUST_PROXY=true` para que el límite y el bloqueo usen la IP real del visitante.

---

## ⚖️ Marco Legal y Libro de Reclamaciones

- **Libro de Reclamaciones Virtual Integrado**:
  - Distinción legal entre **Reclamo** (disconformidad de producto) y **Queja** (atención al cliente).
  - Generación de **Código Único de Seguimiento** (ej. `REC-2026-0001`).
  - Constancia digital formal imprimible / exportable a PDF con sello legal.
  - Herramienta de consulta del estado del trámite en línea.
- **Centro de Políticas Legales (Modales interactivos)**:
  - Términos y Condiciones de Uso.
  - Política de Privacidad y Tratamiento de Datos Personales (Protección de datos conforme a ley).
  - Política de Envíos, Garantías (5 años) y Devoluciones.
  - Política y Banner de Consentimiento de Cookies.
- **Originalidad y Cero Infracción de Copyright**:
  - Código 100% original, recursos generados sin derechos de autor y distribuido bajo la **Licencia MIT**.

---

## 🚀 Cómo Ejecutar el Proyecto

Antes del primer inicio, instala las dependencias y configura la conexión privada:

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

Completa `DATABASE_URL` en `.env` y genera la contraseña del panel con
`python scripts/generar_clave_admin.py` (pega las 3 líneas que imprime). Ejecuta primero `database/schema.postgres.sql`
en el SQL Editor de Supabase. Consulta `database/README.postgres.md` para la
migración opcional de datos SQLite y las reglas de staging/producción.

### Opción 1: Con el script de inicio rápido (Recomendado)
```bash
./start.sh
```

### Opción 2: Con Python directamente
```bash
python3 server.py
```

Abre tu navegador en:
👉 **`http://localhost:8000`**

---

## 🔌 Documentación de Endpoints API REST

| Método | Endpoint | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/api/health` | público | Estado del servicio |
| `GET` | `/api/products` | público | Catálogo activo (`?category_id=`, `?q=`, `?featured=true`) |
| `GET` | `/api/products/<id_o_slug>` | público | Detalle (los inactivos solo los ve el admin) |
| `GET` | `/api/categories` | público | Categorías con cantidad de productos |
| `GET` | `/api/reviews` · `POST` | público | Listar / publicar reseñas |
| `POST` | `/api/claims` | público | Registrar hoja de reclamación |
| `GET` | `/api/claims/<código>` | público | Estado del reclamo (sin datos personales) |
| `POST` | `/api/contact` · `/api/subscribe` | público | Contacto y boletín |
| `GET` | `/api/legal` | público | Datos fiscales, ubicación y políticas |
| `POST` | `/api/admin/login` | público | Ingreso al panel (devuelve token de 4 h) |
| `GET` | `/api/admin/products` | admin | Inventario completo (activos e inactivos) |
| `POST` | `/api/products` | admin | Crear producto |
| `PUT` | `/api/products/<id>` | admin | Editar (nombre, descripción, categoría, etc.) |
| `PATCH` | `/api/products/<id>/active` | admin | Activar / desactivar: `{"is_active": true}` |
| `DELETE` | `/api/products/<id>` | admin | Igual que desactivar (no borra el historial) |
| `POST` | `/api/categories` | admin | Crear categoría |
| `GET` | `/api/messages` · `/api/claims/all` · `/api/subscribers` · `/api/stats` | admin | Bandejas y resumen del panel |
| `PATCH` | `/api/messages/<id>` | admin | `{"status": "read" \| "unread" \| "archived"}` |
| `PATCH` | `/api/claims/<código>` | admin | Responder reclamo: `{"status": "Atendido", "admin_response": "..."}` |
| `GET` | `/api/admin/reviews` | admin | Todas las reseñas (visibles y ocultas) |
| `PATCH` | `/api/reviews/<id>/visible` | admin | Ocultar / mostrar reseña: `{"is_visible": false}` |

---

## ⚙️ Panel de Administración
Abre **`/admin`** (por ejemplo `http://localhost:8000/admin`) o haz clic en el enlace **Administración** al final del pie de cualquier página. Con la contraseña maestra puedes:
- Ver el inventario completo, **activar o desactivar** productos (los inactivos no se ven en la página, pero no se borran).
- Editar nombre, categoría y **descripción** de cada producto.
- Añadir maniquíes nuevos (aparecen al instante en el catálogo).
- Leer los mensajes de contacto, marcarlos como leídos o archivarlos.
- **Responder** las hojas del Libro de Reclamaciones (estado + respuesta), con el contador de los 15 días hábiles que exige Indecopi.
- **Ocultar reseñas** falsas u ofensivas.

---

## ☁️ Publicación gratuita (Vercel + Supabase)

- **Base de datos:** Supabase (plan gratuito), proyecto en São Paulo. El backend entra con un usuario propio (`caleb_app`), no con el usuario maestro.
- **Hosting:** Vercel (plan gratuito). Los archivos de `frontend/` se sirven como estáticos y la API corre como función de Python (`api/index.py`, que reutiliza el mismo `backend/`). La configuración está en `vercel.json`.
- **Variables en Vercel** (Settings → Environment Variables): `DATABASE_URL` (Transaction pooler, puerto 6543), `DATABASE_SSLMODE=require`, `ADMIN_SALT`, `ADMIN_PASSWORD_HASH`, `SESSION_SECRET`, `TRUST_PROXY=true`, `ENABLE_HSTS=true`, `DATABASE_POOL_MIN_SIZE=0`, `DATABASE_POOL_MAX_SIZE=3`.
- `GET /api/health` responde `"database": "ok"` cuando la conexión funciona.
