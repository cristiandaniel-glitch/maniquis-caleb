# 🏛️ Maniquí Studio & Boutique — Arquitectura Web Completa

Un esqueleto web profesional, moderno, seguro y 100% legal diseñado para **Maniquí Studio & Boutique** (o adaptable a cualquier tienda, catálogo y plataforma digital).

Incluye **Frontend interactivo** de alta gama, **Backend REST API** en Python nativo, **Base de Datos SQLite** con migraciones y semillas, **Módulo de Seguridad Integral**, **Libro de Reclamaciones Virtual** conforme a ley y **Centro de Políticas Legales** libres de derechos de autor.

---

## 📁 Estructura del Proyecto

```
PaginaWebManiqui/
├── backend/
│   ├── app.py              # Servidor HTTP multihilo, enrutador REST y despachador estático
│   ├── config.py           # Configuración central (variables de entorno, CORS, límites)
│   ├── database.py         # Conexión SQLite segura (consultas parametrizadas)
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
│   ├── schema.sql          # Tablas con claves foráneas, restricciones e índices
│   ├── seed.sql            # Datos iniciales realistas 100% libres de derechos
│   ├── init_db.py          # Script CLI de inicialización de base de datos
│   └── maniqui.db          # Base de datos SQLite generada
├── frontend/
│   ├── index.html          # Interfaz principal semántica y SEO optimizada
│   ├── css/
│   │   ├── variables.css   # Tokens de diseño, modo oscuro y claro
│   │   ├── reset.css       # Reseteo base CSS moderno
│   │   ├── main.css        # Layouts, header glassmorphism, hero, footer
│   │   ├── components.css  # Botones, tarjetas de maniquíes, modales, toasts
│   │   └── legal.css       # Estilos para Libro de Reclamaciones y constancia
│   ├── js/
│   │   ├── config.js       # Configuración y URLs del cliente
│   │   ├── security.js     # Sanitizador del cliente (prevención XSS)
│   │   ├── api.js          # Cliente fetch reutilizable con manejo de errores
│   │   ├── ui.js           # Notificaciones Toast, modales, alternador de tema
│   │   ├── catalog.js      # Catálogo interactivo con búsqueda en tiempo real
│   │   ├── claims.js       # Formulario y constancia del Libro de Reclamaciones
│   │   ├── admin.js        # Panel de administración interactivo (CRUD en vivo)
│   │   ├── contact.js      # Formulario de cotizaciones y newsletter
│   │   └── app.js          # Arranque y orquestación de la aplicación
│   └── assets/
│       └── images/         # Imágenes de alta resolución de maniquíes (sin copyright)
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
   - Todas las consultas a la base de datos están estrictamente parametrizadas mediante enlaces `?` en SQLite.
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

## ⚙️ Panel de Administración en Vivo
Dentro de la página web, haz clic en el botón **`⚙️ Panel Admin`** en la esquina superior derecha para:
- Añadir nuevos maniquíes directamente a la base de datos SQLite.
- Ver el inventario en tiempo real.
- Revisar mensajes de clientes y cotizaciones recibidas.
- Gestionar las hojas de reclamación registradas.
