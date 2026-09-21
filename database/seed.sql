-- ==============================================================================
-- DATOS INICIALES (SEED DATA): NOVEDADES CALEB - MANIQUÍES & EXHIBIDORES
-- 12 Productos de Alta Costura, Bustos y Exhibidores Colgantes
-- ==============================================================================

-- 1. Categorías Principales
INSERT OR IGNORE INTO categories (id, name, slug, description, icon, display_order) VALUES
(1, 'Maniquíes Femeninos', 'maniquies-femeninos', 'Modelos estilizados de alta costura, cuerpo completo y poses dinámicas.', 'user', 1),
(2, 'Maniquíes Masculinos', 'maniquies-masculinos', 'Líneas atléticas, elegantes y contemporáneas de alta presencia.', 'user-check', 2),
(3, 'Bustos y Sastrería', 'bustos-sastreria', 'Bustos para sastrería con base de madera y torso de lino ajustable.', 'scissors', 3),
(4, 'Colgantes & Exhibidores', 'exhibidores-colgantes', 'Colgantes de fierro, plástico y madera, torsos suspendidos y percheros.', 'hanger', 4),
(5, 'Maniquíes Infantiles', 'maniquies-infantiles', 'Modelos infantiles y juveniles en fibra de vidrio y polímero resistente.', 'smile', 5),
(6, 'Accesorios y Bases', 'accesorios-bases', 'Bases de acero inoxidable, brazos de madera articulados y cabezas estilizadas.', 'tool', 6);

-- 2. Catálogo Completo (12 Modelos Únicos Novedades Caleb)
INSERT OR REPLACE INTO products (id, category_id, name, slug, sku, description, material, color, dimensions, price, stock, image_url, is_featured, is_active) VALUES
(1, 1, 'Maniquí Femenino Haute Couture "Aura"', 'maniqui-femenino-aura', 'MNQ-FEM-001', 'Maniquí de cuerpo completo con acabado blanco mate sofisticado, cabeza abstracta y postura editorial. Ideal para boutiques de lujo.', 'Fibra de vidrio reforzada', 'Blanco Mate Premium', '180cm x 84cm x 62cm x 89cm', 280.00, 15, '/assets/images/mannequin-aura.png', 1, 1),

(2, 1, 'Maniquí Femenino "Velvet Noir"', 'maniqui-femenino-velvet-noir', 'MNQ-FEM-002', 'Elegante maniquí negro cuerpo completo de la colección oficial Novedades Caleb con base metálica de alta estabilidad.', 'Resina ecológica y fibra', 'Negro Satinado', '178cm x 86cm x 64cm x 91cm', 310.00, 10, '/assets/images/mannequin-black-real.jpg', 1, 1),

(3, 1, 'Maniquí Femenino "Golden Runway"', 'maniqui-femenino-golden-runway', 'MNQ-FEM-003', 'Espectacular maniquí de silueta pasarela en acabado cromado dorado brillante para vitrinas de alto impacto.', 'Polímero cromado oro espejo', 'Dorado Oro Brillante', '182cm x 85cm x 61cm x 90cm', 390.00, 8, '/assets/images/mannequin-gold.jpg', 1, 1),

(4, 2, 'Maniquí Masculino "Atelier Titan"', 'maniqui-masculino-atelier-titan', 'MNQ-MAS-001', 'Maniquí masculino titan esculpido atléticamente con facción abstracta y base de acero.', 'Fibra de vidrio de alta densidad', 'Gris Grafito Titan', '188cm x 98cm x 80cm x 96cm', 330.00, 8, '/assets/images/mannequin-titan.png', 1, 1),

(5, 2, 'Maniquí Masculino "Urban Minimal"', 'maniqui-masculino-urban-minimal', 'MNQ-MAS-002', 'Líneas ergonómicas y postura ejecutiva masculina con acabado mate carbón de alta durabilidad.', 'Fibra de vidrio', 'Negro Mate Carbón', '186cm x 96cm x 78cm x 94cm', 290.00, 12, '/assets/images/mannequin-noir.png', 0, 1),

(6, 2, 'Maniquí Masculino "Executive Tailor"', 'maniqui-masculino-executive-tailor', 'MNQ-MAS-003', 'Postura erguida sobria con estructura reforzada para vitrinismo comercial, incluye soporte metálico.', 'Fibra reforzada', 'Negro Mate Grafito', '187cm x 100cm x 82cm x 98cm', 340.00, 6, '/assets/images/mannequin-black-real.jpg', 0, 1),

(7, 3, 'Busto Sastre Profesional "Heritage"', 'busto-sastre-heritage', 'BST-SAS-001', 'Busto de sastrería profesional con base de madera maciza para modistería y escaparates.', 'Lino orgánico y estructura acolchada', 'Blanco Marfil / Madera', 'Altura regulable 140cm - 190cm', 180.00, 25, '/assets/images/mannequin-busto-real.jpg', 1, 1),

(8, 3, 'Busto Femenino Sastrería "Atelier Luxe"', 'busto-femenino-atelier-luxe', 'BST-SAS-002', 'Torso femenino de sastrería con acabados finos de lino y base pedestal de caoba torneada.', 'Lino importado y base pedestal', 'Lino Blanco / Caoba', 'Altura regulable 135cm - 185cm', 195.00, 14, '/assets/images/mannequin-busto.png', 0, 1),

(9, 4, 'Exhibidor Torso Colgante "Aero Frame"', 'exhibidor-torso-colgante-aero', 'EXH-CLG-001', 'Estructura silueta de fierro y alambre plastificado colgante con gancho giratorio 360°.', 'Fierro y alambre de acero plastificado', 'Negro Metalizado', '75cm x 50cm x 25cm', 160.00, 20, '/assets/images/mannequin-wire-real.jpg', 1, 1),

(10, 4, 'Busto Colgante Femenino "Minimal Hook"', 'busto-colgante-femenino-minimal', 'EXH-CLG-002', 'Busto silueta colgante de plástico reforzado ultraligero con gancho de fierro para escaparates flotantes.', 'Plástico reforzado termoformado', 'Cromo / Negro', '78cm x 85cm x 60cm', 75.00, 35, '/assets/images/mannequin-colgante.jpg', 0, 1),

(11, 5, 'Maniquí Infantil "Junior Star" (Gateador/Niño)', 'maniqui-infantil-junior-star', 'MNQ-INF-001', 'Maniquí infantil anatómico en polímero irrompible de alto impacto con base sólida.', 'Polímero irrompible de alto impacto', 'Blanco Semimate', '65cm x 40cm x 35cm', 140.00, 18, '/assets/images/mannequin-infantil-real.jpg', 0, 1),

(12, 6, 'Exhibidor Torso Anatómico "Anatomix"', 'brazos-madera-articulados', 'ACC-BRZ-001', 'Torsos y exhibidores anatómicos en madera y fibra moldeada para vitrinismo comercial.', 'Madera torneada y fibra moldeada', 'Acabado Natural', '70cm x 45cm', 110.00, 20, '/assets/images/mannequin-hip-real.jpg', 0, 1);

-- 3. Mensaje inicial
INSERT OR IGNORE INTO contact_messages (id, name, email, phone, subject, message, status) VALUES
(1, 'Valeria Morales', 'valeria.boutique@ejemplo.pe', '+51 987 654 321', 'Cotización de 6 maniquíes para tienda en Cusco', 'Hola Novedades Caleb, deseo cotizar 6 maniquíes con entrega en Galería La Exitosa.', 'unread');

-- 4. Suscriptores iniciales
INSERT OR IGNORE INTO subscribers (id, email, status) VALUES
(1, 'contacto@estudiomoda.pe', 'active'),
(2, 'vitrinismo.peru@tendencias.pe', 'active');
