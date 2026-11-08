# 🏛️ Maniquí Studio & Boutique — Arquitectura Web Completa

Un esqueleto web profesional, moderno, seguro y 100% legal diseñado para **Maniquí Studio & Boutique** (o adaptable a cualquier tienda, catálogo y plataforma digital).

Incluye **Frontend interactivo** de alta gama, **Backend REST API** en Python nativo, **PostgreSQL alojado en Supabase**, **Módulo de Seguridad Integral**, **Libro de Reclamaciones Virtual** conforme a ley y **Centro de Políticas Legales** libres de derechos de autor.

---

## 📁 Estructura del Proyecto

```
PaginaWebManiqui/
├── backend/
│   ├── app.py              # Servidor HTTP multihilo, enrutador REST y despachador estático
│   ├── config.py           # Configuración central (variables de entorno, CORS, límites)
│   ├── database.py         # Pool PostgreSQL/Supabase y consultas parametrizadas
│   ├── security.py         # Cabeceras CSP, sanitización XSS, validadores y rate limiter
│   ├── models/             # Lógica de negocio y modelos de datos
│   │   ├── product.py      # CRUD de maniquíes y productos
│   │   ├── category.py     # Categorías de exhibición
│   │   ├── claim.py        # Libro de Reclamaciones (Quejas y Reclamos)
│   │   ├── message.py      # Mensajes de contacto
│   │   └── subscriber.py   # Suscriptores al boletín
│   └── routes/             # Controladores de endpoints REST
│       ├── products.py
│       ├── categories.py
│       ├── claims.py
│       ├── messages.py
│       ├── newsletter.py
│       ├── stats.py
│       └── legal.py
├── database/
│   ├── schema.postgres.sql # Esquema versionado para Supabase/PostgreSQL
│   ├── migrate_sqlite_to_postgres.py # Migración única e idempotente desde SQLite
│   └── README.postgres.md  # Configuración de Supabase, equipo y migración
├── frontend/
│   ├── index.html          # Inicio: escena por capas (fachada, vitrina, interior)
│   ├── nosotros.html       # Quiénes somos, materiales y contacto
│   ├── catalogo.html       # Vitrina de productos y listado con filtros
│   ├── resenas.html        # Reseñas de clientes (carrusel con flechas)
│   ├── reclamaciones.html  # Libro de Reclamaciones virtual (Indecopi)
│   ├── privacidad.html     # Términos, privacidad y uso de IA
│   ├── admin.html          # Panel del dueño (se abre en /admin)
│   ├── css/
│   │   └── site.css        # Todos los estilos del sitio y del panel
│   ├── js/
│   │   ├── site.js         # Catálogo, reseñas, formularios y reclamaciones
│   │   ├── escena.js       # Animación de la portada al hacer scroll
│   │   └── admin.js        # Panel: ingreso, inventario, mensajes y reclamos
│   └── assets/
│       ├── capas/          # Capas de la escena de Inicio
│       ├── productos/      # Fotos de los productos del catálogo
│       ├── img/            # Fotos de portada y fondos
│       └── logo/           # Logo y favicons
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Exclusiones de Git
├── LICENSE                 # Licencia de software libre MIT (100% legal)
├── README.md               # Documentación general
├── server.py               # Punto de entrada principal (`python3 server.py`)
└── start.sh                # Script de inicio rápido automatizado
```

---

## 🛡️ Seguridad Implementada

1. **Protección contra Inyecciones SQL (SQLi)**:
   - Todas las consultas a PostgreSQL están estrictamente parametrizadas mediante enlaces `%s` de psycopg.
2. **Prevención de Cross-Site Scripting (XSS)**:
   - Sanitización de entradas en el servidor (`backend/security.py`) y escape de caracteres HTML antes de renderizar en el cliente (`frontend/js/security.js`).
3. **Cabeceras HTTP de Seguridad (Security Headers)**:
   - `Content-Security-Policy (CSP)`: Control estricto de scripts y fuentes permitidas.
   - `X-Content-Type-Options: nosniff`: Prevención de ejecución MIME errónea.
   - `X-Frame-Options: SAMEORIGIN`: Prevención contra Clickjacking.
   - `X-XSS-Protection: 1; mode=block`.
   - `Referrer-Policy: strict-origin-when-cross-origin`.
4. **Protección de Rutas (Path Traversal)**:
   - El servidor estático restringe el acceso al directorio permitido impidiendo descargas arbitrarias del sistema de archivos.
5. **Rate Limiting**:
   - Limitador en memoria por dirección IP para mitigar ataques de fuerza bruta o saturación.

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

Completa `DATABASE_URL`, `SESSION_SECRET`, `ADMIN_SALT` y
`ADMIN_PASSWORD_HASH` en `.env`. Ejecuta primero `database/schema.postgres.sql`
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

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/health` | Estado del servidor y servicio |
| `GET` | `/api/products` | Listar maniquíes (soporta `?category_id=`, `?q=`, `?featured=true`) |
| `GET` | `/api/products/<id_or_slug>` | Detalle de un producto específico |
| `POST` | `/api/products` | Crear nuevo maniquí en la base de datos |
| `PUT` | `/api/products/<id>` | Actualizar producto existente |
| `DELETE` | `/api/products/<id>` | Eliminar producto del catálogo |
| `GET` | `/api/categories` | Listar categorías de maniquíes |
| `POST` | `/api/claims` | Registrar hoja de reclamación virtual |
| `GET` | `/api/claims/<codigo>` | Consultar estado de reclamación por código |
| `POST` | `/api/contact` | Enviar mensaje de cotización o consulta |
| `POST` | `/api/subscribe` | Suscribirse al boletín de vitrinismo |
| `GET` | `/api/stats` | Métricas para el panel de administración |
| `GET` | `/api/legal` | Información fiscal y políticas de la empresa |

---

## ⚙️ Panel de Administración
Abre **`/admin`** (por ejemplo `http://localhost:8000/admin`) o haz clic en el enlace **Administración** al final del pie de cualquier página. Con la contraseña maestra puedes:
- Ver el inventario y quitar productos del catálogo.
- Añadir maniquíes nuevos (aparecen al instante en el catálogo).
- Leer los mensajes de contacto de los clientes.
- Revisar las hojas del Libro de Reclamaciones.
