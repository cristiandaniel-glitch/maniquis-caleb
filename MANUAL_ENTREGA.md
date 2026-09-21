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
| **Acceso al Panel** | Clic en el botón superior **`⚙️ Panel Admin`** en la web |
| **Contraseña Maestra Inicial** | `AdminManiqui2026!` *(Recomendable cambiar al subir a producción)* |
| **Ubicación de Base de Datos** | `database/maniqui.db` |

---

## 3. 📸 ¿Cómo Gestionar y Editar el Catálogo? (Guía para el Dueño)

El dueño no necesita saber programación para administrar su tienda:

### A. Para Cambiar Precios o Stock:
1. Entrar a la página web y hacer clic en **`⚙️ Panel Admin`**.
2. Ingresar la contraseña maestra.
3. En la pestaña **`📦 Inventario`**, podrá ver toda la lista de maniquíes con su ID, precio y stock disponible.

### B. Para Añadir un Nuevo Modelo de Maniquí:
1. En el Panel Admin, hacer clic en la pestaña **`➕ Añadir Maniquí`**.
2. Completar los datos:
   - **Nombre del Maniquí:** Ej. *Maniquí Femenino Silueta Dorada*.
   - **Categoría:** Seleccionar entre Femeninos, Masculinos, Bustos, Infantiles o Accesorios.
   - **Precio en Soles (S/):** Ej. *290.00*.
   - **Stock:** Número de unidades disponibles en el Stand 3.
   - **Descripción y Medidas:** Altura, pecho, cintura, cadera y tipo de base.
   - **Foto del Maniquí:** Colocar la ruta de la foto (ej. `/assets/images/foto-maniqui.png`) o una URL directa.
3. Hacer clic en **`💾 Guardar Maniquí en la Base de Datos`** y aparecerá al instante en el catálogo público.

### C. Para Cambiar o Colocar Fotos Reales:
1. Guardar las fotografías tomadas en el stand dentro de la carpeta:
   👉 `frontend/assets/images/`
2. Ponerle un nombre descriptivo sin espacios (ej. `maniqui-dorado-stand3.jpg`).
3. En el formulario de producto colocar: `/assets/images/maniqui-dorado-stand3.jpg`.

---

## 4. 📬 ¿Cómo Revisar Mensajes y Reclamaciones?

1. En el Panel Admin, ir a la pestaña **`📬 Mensajes`** para ver los clientes que enviaron solicitudes de cotización desde la web.
2. En la pestaña **`⚖️ Libro de Reclamaciones`**, podrá revisar todas las hojas de quejas o reclamos registradas, responderles formalmente y cambiar su estado de *Pendiente* a *Atendido*.

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
