# 📦 MANUAL DE ENTREGA Y GUÍA DEL PROPIETARIO
## Proyecto: Sitio Web Oficial — NOVEDADES CALEB
**Cliente:** ROMERO ENRIQUEZ PATRICK JUNIOR (RUC: 10727851971)  
**Establecimiento:** Calle 119 Tomás Tuyro Túpac, Galería Comercial La Exitosa, Stand N° 3, Cusco - Perú  
**Fecha de Entrega:** Agosto 2026  

---

## 1. 🌟 Resumen de lo que Incluye el Proyecto Entregado

El cliente recibe un sistema web **Full-Stack hecho a medida**, 100% libre de costos de licencias mensuales (no usa Shopify, ni plugins de pago de WordPress):

1. **Frontend Moderno & Responsive:** Optimizado para celulares, tablets y computadoras, con diseño de alta gama y modo claro / oscuro.
2. **Catálogo Interactivo en Soles (S/):** Con buscador por modelo, material, SKU y filtros por categoría (Femeninos, Masculinos, Bustos, Infantiles, Accesorios).
3. **Botón Directo de Ventas por WhatsApp:** Conexión directa al número oficial `+51 916 126 747` con mensajes pre-redactados para cotizaciones inmediatas.
4. **Reloj Inteligente de Horario Comercial:** Detecta automáticamente si el Stand N° 3 de Galería La Exitosa está Abierto, en Refrigerio (1 a 3 PM) o Cerrado.
5. **Libro de Reclamaciones Virtual Oficial Indecopi:** Cumple con la Ley N° 29571 y D.S. N° 011-2011-PCM, emitiendo constancias digitales imprimibles en PDF con código secuencial (`REC-2026-XXXX`) y plazo legal de 15 días hábiles.
6. **Centro de Políticas Legales Peruanas:** Términos de Contratación (Nuevo RUS), Política de Privacidad y Derechos ARCO (Ley N° 29733), Política de Envíos a Provincias y Banner de Cookies de 2 Capas.
7. **Panel de Administración Privado:** Para gestionar el inventario de maniquíes, ver cotizaciones recibidas y gestionar reclamos desde el navegador.
8. **Seguridad y Cero Vulnerabilidades:** Base de datos SQLite protegida contra Inyección SQL, scripts maliciosos (XSS) y contraseñas cifradas con algoritmo criptográfico PBKDF2.

---

## 2. 🔑 Credenciales de Acceso Administrativo

| Concepto | Detalle |
|---|---|
| **Acceso al Panel** | Abrir **`/admin`** o clic en **Administración** al final del pie de la página |
| **Contraseña Maestra Inicial** | `AdminManiqui2026!` *(Recomendable cambiar al subir a producción)* |
| **Ubicación de Base de Datos** | `database/maniqui.db` |

---

## 3. 📸 ¿Cómo Gestionar y Editar el Catálogo? (Guía para el Dueño)

El dueño no necesita saber programación para administrar su tienda:

### A. Para Entrar al Panel:
1. Abrir la dirección **`/admin`** de la página (ej. `https://su-dominio/admin`), o bajar al final de cualquier página y hacer clic en **Administración**.
2. Escribir la contraseña maestra y pulsar **Ingresar**.
3. Arriba se ven los totales: productos activos, categorías, mensajes y reclamos pendientes.

### B. Para Ver o Quitar Productos:
1. En la pestaña **Inventario** está la lista de productos con su foto, categoría, código y stock.
2. El botón **Eliminar** quita el producto del catálogo (pide confirmación antes).

### C. Para Añadir un Nuevo Maniquí:
1. Ir a la pestaña **Añadir maniquí** y completar:
   - **Nombre** y **Categoría**.
   - **Descripción:** para qué sirve y cómo es.
   - **Material, Color y Medidas** (opcionales; si se dejan vacíos, el catálogo muestra "Consultar").
   - **Stock:** unidades disponibles en el Stand 3.
   - **Foto:** la ruta del archivo, por ejemplo `/assets/productos/maniqui-dorado.webp` (se ve una vista previa).
2. Pulsar **Guardar en el catálogo**: aparece al instante en la página.

### D. Para Subir Fotos Reales:
1. Guardar la foto (de preferencia `.webp`, fondo transparente o claro) en la carpeta:
   👉 `frontend/assets/productos/`
2. Ponerle un nombre sin espacios ni tildes (ej. `maniqui-dorado.webp`).
3. En el formulario escribir: `/assets/productos/maniqui-dorado.webp`.

---

## 4. 📬 ¿Cómo Revisar Mensajes y Reclamaciones?

1. En el panel, la pestaña **Mensajes** muestra lo que escribieron los clientes desde la web, con su correo y un enlace directo a su WhatsApp.
2. La pestaña **Reclamaciones** muestra cada hoja del Libro de Reclamaciones (código, datos del cliente, detalle y pedido). La respuesta al cliente se envía por correo dentro de los 15 días hábiles que exige Indecopi.

---

## 5. 🚀 Cómo Poner la Web en Internet (Dominio y Hosting)

Cuando el cliente decida comprar el dominio (ej. `novedadescaleb.com` o `maniquiescaleb.pe`):

1. **Adquirir Dominio:** En proveedores como Namecheap, GoDaddy o Nic.pe (~S/ 40 a S/ 110 al año).
2. **Adquirir Hosting / Servidor:** Un hosting básico o VPS tipo Hostinger, DigitalOcean, Render o cPanel (~S/ 120 a S/ 250 al año).
3. **Subir los Archivos:** Subir toda la carpeta del proyecto.
4. **Ejecutar el Servidor:** Con el comando `python3 server.py` o configurándolo con Gunicorn/Nginx.

---

## 6. 📜 Certificado de Garantía y Propiedad del Software

Todo el código fuente y estructura de la base de datos se entregan bajo **Licencia MIT**, otorgando a **NOVEDADES CALEB (ROMERO ENRIQUEZ PATRICK JUNIOR)** la propiedad total, libre y perpetua del software sin cobros de comisiones ni regalías por uso comercial.
