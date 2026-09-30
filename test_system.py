#!/usr/bin/env python3
"""
Suite de pruebas de integración y validación del sistema Maniquí Studio.
"""

import json
import urllib.request

BASE = "http://localhost:8000"


def get(path, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.headers.get("Content-Type", ""), resp.read()


def post(path, data, token=None):
    body = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def put(path, data, token=None):
    body = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers=headers,
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def delete(path, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", headers=headers, method="DELETE")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def run_tests():
    print("=" * 60)
    print("🧪 1. Probando Archivos Estáticos, CSS, JS e Imágenes...")
    print("=" * 60)

    static_paths = [
        "/",
        "/nosotros.html",
        "/catalogo.html",
        "/resenas.html",
        "/reclamaciones.html",
        "/privacidad.html",
        "/admin",
        "/css/site.css",
        "/js/site.js",
        "/js/escena.js",
        "/js/admin.js",
        "/assets/capas/fachada.webp",
        "/assets/capas/interior.webp",
        "/assets/img/portada-cusco.jpg",
        "/assets/logo/logo-caleb.webp",
        "/assets/productos/maniqui-femenino-realista.webp",
    ]

    for path in static_paths:
        status, ctype, body = get(path)
        assert status == 200, f"Error en {path}: {status}"
        clean_type = ctype.split(";")[0]
        print(f"  [✔] {path:36} -> {status} ({clean_type}, {len(body)} bytes)")

    # /admin debe abrir el panel, no caer en la portada
    _, _, body = get("/admin")
    assert "Panel de administración".encode("utf-8") in body, "/admin no sirve el panel"
    print("  [✔] /admin abre el panel de administración")

    print("\n" + "=" * 60)
    print("🧪 2. Probando Endpoints REST API y Autenticación...")
    print("=" * 60)

    # Health
    status, _, health = get("/api/health")
    print(f"  [✔] GET /api/health -> {json.loads(health.decode('utf-8'))['status']}")

    # Categorías
    status, _, cats = get("/api/categories")
    cats_data = json.loads(cats.decode("utf-8"))["data"]
    print(f"  [✔] GET /api/categories -> {len(cats_data)} categorías disponibles.")

    # Listar Productos
    status, _, prods = get("/api/products")
    prods_data = json.loads(prods.decode("utf-8"))["data"]
    print(f"  [✔] GET /api/products -> {len(prods_data)} productos activos en el catálogo.")

    # Login Admin
    status, auth_res = post("/api/admin/login", {"password": "AdminManiqui2026!"})
    token = auth_res["data"]["token"]
    print(f"  [✔] POST /api/admin/login -> Sesión iniciada con éxito.")

    # Crear Producto (con token admin)
    status, new_prod = post("/api/products", {
        "name": "Maniquí Femenino Edición Platino",
        "category_id": 1,
        "price": 380.00,
        "stock": 7,
        "description": "Edición limitada platino con pedestal de acero inoxidable.",
        "material": "Fibra de vidrio y resina",
        "color": "Platino Satinado",
        "dimensions": "180cm x 86cm x 62cm",
        "image_url": "/assets/productos/maniqui-femenino-realista.webp",
        "is_featured": True
    }, token=token)
    prod_id = new_prod["data"]["id"]
    print(f"  [✔] POST /api/products -> Creado con ID #{prod_id} ('{new_prod['data']['name']}')")

    # Actualizar Producto
    status, upd_prod = put(f"/api/products/{prod_id}", {
        "price": 395.00,
        "stock": 15
    }, token=token)
    print(f"  [✔] PUT /api/products/{prod_id} -> Precio actualizado a ${upd_prod['data']['price']} y stock {upd_prod['data']['stock']}")

    # Eliminar Producto
    status, del_res = delete(f"/api/products/{prod_id}", token=token)
    print(f"  [✔] DELETE /api/products/{prod_id} -> {del_res['message']}")

    # Enviar Mensaje de Contacto
    status, msg_res = post("/api/contact", {
        "name": "Sofía Benavides",
        "email": "sofia.moda@boutique.pe",
        "phone": "+51 912345678",
        "subject": "Presupuesto para 12 unidades",
        "message": "Hola, solicitamos cotización formal con envío a San Isidro."
    })
    print(f"  [✔] POST /api/contact -> {msg_res['data']['message']}")

    # Suscribirse al Boletín
    status, sub_res = post("/api/subscribe", {
        "email": "vitrinismo.nacional@tendencias.com"
    })
    print(f"  [✔] POST /api/subscribe -> {sub_res['data']['message']}")

    # Libro de Reclamaciones (Queja / Reclamo)
    status, claim_res = post("/api/claims", {
        "claim_type": "Reclamo",
        "full_name": "Gabriel Thorne",
        "doc_type": "DNI",
        "doc_number": "71829304",
        "email": "gabriel.thorne@ejemplo.com",
        "phone": "+51 987654321",
        "address": "Av. Dos de Mayo 890, San Isidro",
        "contracted_good": "Producto",
        "amount_claimed": 319.50,
        "good_description": "Maniquí Velvet Noir",
        "claim_description": "La base presentó una ligera falta de estabilidad en el montaje.",
        "consumer_request": "Solicito cambio de la base de vidrio templado."
    })
    claim_code = claim_res["data"]["claim_code"]
    print(f"  [✔] POST /api/claims -> Hoja generada bajo código: {claim_code}")

    # Consulta pública por código: solo el estado, sin datos personales (Ley 29733)
    status, _, claim_get = get(f"/api/claims/{claim_code}")
    claim_item = json.loads(claim_get.decode("utf-8"))["data"]
    assert "full_name" not in claim_item and "doc_number" not in claim_item, "La consulta pública expone datos personales"
    print(f"  [✔] GET /api/claims/{claim_code} (público) -> Estado: {claim_item['status']}, sin datos personales")

    # Consulta como administrador: datos completos
    status, _, claim_get = get(f"/api/claims/{claim_code}", token=token)
    claim_item = json.loads(claim_get.decode("utf-8"))["data"]
    print(f"  [✔] GET /api/claims/{claim_code} (admin) -> Reclamante: {claim_item['full_name']}")

    # Estadísticas (con token)
    status, _, stats_raw = get("/api/stats", token=token)
    stats_data = json.loads(stats_raw.decode("utf-8"))["data"]
    print(f"  [✔] GET /api/stats -> {stats_data}")

    # Reseñas de Clientes (GET y POST)
    status, _, reviews_raw = get("/api/reviews")
    reviews_data = json.loads(reviews_raw.decode("utf-8"))
    print(f"  [✔] GET /api/reviews -> {reviews_data['total']} reseñas activas de boutiques.")

    status, new_rev_res = post("/api/reviews", {
        "name": "Mariana De la Cuba",
        "boutique": "Atelier De la Cuba",
        "city": "Cusco",
        "product_model": "Busto Sastre Profesional",
        "rating": 5,
        "comment": "Los bustos de sastre son una joya en durabilidad y estética para nuestro atelier."
    })
    print(f"  [✔] POST /api/reviews -> {new_rev_res['message']} (ID #{new_rev_res['review']['id']})")

    # Legal
    status, _, legal_raw = get("/api/legal")
    legal_data = json.loads(legal_raw.decode("utf-8"))["data"]
    print(f"  [✔] GET /api/legal -> Empresa: {legal_data['company']['commercial_name']} (Titular: {legal_data['company']['legal_name']} | {legal_data['company']['tax_id']})")

    print("\n" + "=" * 60)
    print("🎉 ¡TODAS LAS PRUEBAS AUTOMATIZADAS PASARON CON ÉXITO AL 100%!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
