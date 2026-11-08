# PostgreSQL y Supabase

El esquema para producción está en `schema.postgres.sql`. La aplicación ya usa
PostgreSQL mediante `DATABASE_URL`; `schema.sql` y `seed.sql` se conservan solo
como fuente de una migración única desde la instalación SQLite anterior.

## Crear la base en Supabase

1. Crea un proyecto de Supabase en una región cercana a los usuarios.
2. En el proyecto, abre **SQL Editor** y crea una consulta nueva.
3. Copia el contenido completo de `schema.postgres.sql` y ejecútalo.
4. Guarda la cadena de conexión que muestra **Connect** únicamente en el
   entorno del backend; nunca en JavaScript del navegador ni en Git.

El esquema activa Row Level Security (RLS) y no crea políticas públicas. Por
ello, las tablas no quedan accesibles desde `anon` ni `authenticated` a través
de la Data API. El backend debe ser el único componente que acceda a los datos
privados de clientes y reclamos.

## Configurar el backend

1. Instala las dependencias: `python -m pip install -r requirements.txt`.
2. Copia `.env.example` como `.env` y pega la cadena **Session pooler** de
   Supabase en `DATABASE_URL`. Conserva `DATABASE_SSLMODE=require`.
3. Genera valores propios para `SESSION_SECRET`, `ADMIN_SALT` y
   `ADMIN_PASSWORD_HASH`; no uses los textos de ejemplo.
4. Inicia con `python server.py`. El arranque valida que todas las tablas del
   esquema existan y se detiene si no puede conectar.

El backend utiliza un pool pequeño de conexiones, consultas parametrizadas de
PostgreSQL y convierte fechas, decimales e IPs de forma segura antes de
responder JSON. El frontend sigue usando los mismos endpoints `/api/*`; no
necesita URL, contraseña ni claves de Supabase.

## Migrar datos existentes de SQLite

Si el catálogo o formularios ya tenían datos locales, ejecuta primero una
validación sin escritura:

```powershell
python database/migrate_sqlite_to_postgres.py --source-db database/maniqui.db --dry-run
```

Luego ejecuta el mismo comando sin `--dry-run`. La migración conserva IDs,
valida los datos de menores en reclamaciones, ajusta las secuencias y usa
`ON CONFLICT DO NOTHING`: puede repetirse sin borrar ni reemplazar datos que ya
estén en Supabase.

## Entornos del equipo

Usen proyectos distintos para `staging` y `production`; no desarrollen contra
la base de producción ni compartan la contraseña principal. Todos pueden
trabajar contra el mismo proyecto de staging y la aplicación publicada contra
production. Cada integrante guarda su propio `.env` y nunca lo comparte por Git
ni por el frontend.
