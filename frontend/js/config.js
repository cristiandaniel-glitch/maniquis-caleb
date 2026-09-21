/**
 * Configuración centralizada del cliente frontend para NOVEDADES CALEB.
 * Datos verificados ante SUNAT (Perú).
 */

const CONFIG = {
    APP_NAME: "Novedades Caleb — Maniquíes & Exhibidores",
    BRAND_NAME: "MANIQUÍES CALEB",
    API_BASE_URL: window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
        ? `${window.location.origin}/api`
        : "/api",
    CURRENCY: "PEN",
    CURRENCY_SYMBOL: "S/ ",
    LEGAL: {
        LEGAL_NAME: "ROMERO ENRIQUEZ PATRICK JUNIOR",
        COMMERCIAL_NAME: "NOVEDADES CALEB",
        TAX_ID: "RUC: 10727851971",
        DNI: "DNI: 72785197",
        ADDRESS: "Calle 119 Tomás Tuyro Túpac (4to Paradero San Sebastián, Frente a Tottus), Galería Comercial La Exitosa, Stand N° 3",
        LOCATION: "San Sebastián, Cusco - Perú",
        PHONE_CATALOG: "916 126 747",
        PHONE_ADMIN: "924 044 084",
        WHATSAPP_CATALOG_URL: "https://wa.me/51916126747?text=Hola%20Novedades%20Caleb,%20deseo%20solicitar%20el%20cat%C3%A1logo%20de%20maniqu%C3%ADes%20y%20precios.",
        EMAIL_CONTACT: "maniquicaleb.pe@gmail.com",
        EMAIL_LEGAL: "legal.exhicaleb.pe@gmail.com",
        HOURS_WEEKDAYS: "Lun a Vie: 8:00 AM - 6:00 PM",
        HOURS_LUNCH: "Refrigerio: 1:00 PM - 3:00 PM",
        HOURS_SATURDAYS: "Sáb: 8:00 AM - 12:00 PM",
        HOURS_SUNDAYS: "Dom: Cerrado",
        CLAIM_RESPONSE_DAYS: 15,
        WARRANTY_TIME: "1 Año de Garantía de Estructura"
    }
};

window.CONFIG = CONFIG;
