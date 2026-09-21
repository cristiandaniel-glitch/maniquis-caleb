-- ==============================================================================
-- BASE DE DATOS: MANIQUÍ STUDIO & BOUTIQUE
-- Motor: SQLite3
-- Cumple con estándares de integridad referencial y marcas de tiempo UTC.
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. Tabla de Categorías de Maniquíes / Productos
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT DEFAULT 'tag',
    display_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Maniquíes y Productos
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    sku TEXT UNIQUE,
    description TEXT NOT NULL,
    material TEXT,
    color TEXT,
    dimensions TEXT,
    price REAL NOT NULL DEFAULT 0.00,
    stock INTEGER NOT NULL DEFAULT 0,
    image_url TEXT NOT NULL,
    is_featured INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- 3. Tabla del Libro de Reclamaciones Virtual (Cumplimiento Legal)
CREATE TABLE IF NOT EXISTS claims_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_code TEXT NOT NULL UNIQUE,          -- Código único, ej: REC-2026-0001
    claim_type TEXT NOT NULL CHECK(claim_type IN ('Reclamo', 'Queja')), -- Reclamo: disconformidad con producto/servicio. Queja: malestar en atención.
    
    -- Datos del Consumidor Reclamante
    full_name TEXT NOT NULL,
    doc_type TEXT NOT NULL,                  -- DNI, CE, Pasaporte, RUC
    doc_number TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    is_minor INTEGER DEFAULT 0,
    guardian_name TEXT,
    
    -- Detalle del Bien Contratado
    contracted_good TEXT NOT NULL CHECK(contracted_good IN ('Producto', 'Servicio')),
    amount_claimed REAL DEFAULT 0.00,
    good_description TEXT NOT NULL,
    
    -- Detalle de la Reclamación y Pedido
    claim_description TEXT NOT NULL,
    consumer_request TEXT NOT NULL,          -- Qué solicita el cliente para solucionar
    
    -- Estado de Gestión y Auditoría
    status TEXT DEFAULT 'Pendiente' CHECK(status IN ('Pendiente', 'En Proceso', 'Atendido', 'Cerrado')),
    admin_response TEXT,
    response_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla de Mensajes del Formulario de Contacto
CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'unread' CHECK(status IN ('unread', 'read', 'archived')),
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tabla de Suscriptores al Boletín (Newsletter)
CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'unsubscribed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabla de Auditoría / Logs de Seguridad del Sistema
CREATE TABLE IF NOT EXISTS security_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    detail TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- ÍNDICES PARA RENDIMIENTO ÓPTIMO
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_featured ON products(is_featured);
CREATE INDEX IF NOT EXISTS idx_claims_code ON claims_book(claim_code);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims_book(status);
CREATE INDEX IF NOT EXISTS idx_messages_status ON contact_messages(status);
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
