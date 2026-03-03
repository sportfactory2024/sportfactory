# 🏭 SportFactory — Guía de instalación y publicación

## ¿Qué incluye este proyecto?
- Página web completa para recibir pedidos de ropa deportiva
- Base de datos real que guarda todos los pedidos
- Emails automáticos al cliente cuando su pedido avanza de etapa
- Panel de administración con PIN para Saury, Paola y Angela
- Botones para avanzar las etapas: Recibido → En Proceso → Terminación → Despacho

---

## PASO 1 — Configurar el email de Gmail

Para que los emails funcionen necesitás una **Contraseña de Aplicación** de Google.
(No es tu contraseña normal, es una especial para apps.)

1. Andá a: https://myaccount.google.com
2. Click en **Seguridad**
3. Activá **Verificación en dos pasos** si no la tenés
4. Volvé a Seguridad → buscá **Contraseñas de aplicaciones**
5. En "Seleccionar aplicación" elegí **Correo**
6. En "Seleccionar dispositivo" escribí **SportFactory**
7. Click **Generar** → Google te da 16 caracteres (ej: `abcd efgh ijkl mnop`)
8. Guardá esos 16 caracteres, los vas a necesitar abajo

---

## PASO 2 — Configurar el archivo .env

1. Copiá el archivo `.env.example` y renombralo `.env`
2. Abrilo y completá:

```
SECRET_KEY=cualquier-texto-largo-aleatorio-aqui
ADMIN_PIN=2024
GMAIL_USER=tuemail@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
DATABASE_URL=sqlite:///sportfactory.db
```

> ⚠️ IMPORTANTE: El archivo `.env` nunca lo compartas ni lo subas a internet

---

## PASO 3 — Publicar en Railway (GRATIS)

Railway te da hosting gratuito y es el más fácil.

### 3a. Subir el código a GitHub
1. Creá una cuenta en https://github.com
2. Creá un repositorio nuevo llamado `sportfactory`
3. Subí todos estos archivos al repositorio

### 3b. Conectar con Railway
1. Andá a https://railway.app
2. Registrate con tu cuenta de GitHub
3. Click **New Project** → **Deploy from GitHub repo**
4. Seleccioná tu repositorio `sportfactory`
5. Railway detecta automáticamente que es Python/Flask

### 3c. Configurar las variables de entorno en Railway
1. En tu proyecto Railway, click en el servicio
2. Andá a la pestaña **Variables**
3. Agregá cada variable del `.env`:
   - `SECRET_KEY` = cualquier texto largo
   - `ADMIN_PIN` = 2024
   - `GMAIL_USER` = tuemail@gmail.com
   - `GMAIL_APP_PASSWORD` = los 16 caracteres de Google
4. Railway reinicia automáticamente

### 3d. Obtener tu URL
- Railway te da una URL pública tipo: `https://sportfactory-production.up.railway.app`
- ¡Esa es tu página web real! Cualquier persona puede acceder

---

## PASO 4 — Probar que todo funciona

1. Abrí tu URL de Railway
2. Hacé un pedido de prueba con tu propio email
3. Deberías recibir un email de confirmación
4. Entrá al panel Admin con el PIN `2024`
5. Avanzá la etapa del pedido
6. Verificá que llegue el email de actualización

---

## Comandos para correr localmente (opcional)

Si querés probarlo en tu computadora antes de publicar:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear el archivo .env con tus datos
cp .env.example .env
# (editá el .env con tus datos)

# Correr la app
python app.py

# Abrir en el navegador
http://localhost:5000
```

---

## Estructura del proyecto

```
sportfactory/
├── app.py              ← Servidor Python (Flask)
├── requirements.txt    ← Dependencias Python
├── Procfile           ← Para Railway/Render
├── railway.toml       ← Config de Railway
├── .env.example       ← Plantilla de variables
├── .env               ← Tus variables privadas (no subir)
└── templates/
    └── index.html     ← La página web completa
```

---

## ¿Dudas o problemas?

- **No llegan los emails**: Verificá que la Contraseña de Aplicación esté bien copiada (sin espacios extra)
- **Error 500**: Revisá las variables de entorno en Railway
- **PIN no funciona**: Verificá que `ADMIN_PIN` esté configurado en Railway

---

*SportFactory — Saury Perez Mercedes · Paola Maria Rodriguez · Angela Peña*
