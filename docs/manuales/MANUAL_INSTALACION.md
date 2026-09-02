# Manual de instalación

## 1. Introducción

Este manual describe la instalación local del MVP del **Sistema Informático para la Gestión Operativa de Torneos de Tenis en el Club Estadio Español de Curicó**. El proyecto está compuesto por una API REST desarrollada con Django y un cliente web desarrollado con Angular. Ambos componentes utilizan PostgreSQL como sistema de persistencia a través del backend.

Las instrucciones corresponden al estado actual del repositorio. Los ejemplos de variables y credenciales son referenciales y deben reemplazarse por valores locales seguros.

## 2. Requisitos previos

Antes de comenzar se requiere:

- Git, para obtener el repositorio cuando corresponda.
- Python 3.12 o una versión compatible con las dependencias declaradas.
- PostgreSQL instalado, en ejecución y accesible desde el equipo del backend.
- Node.js y npm compatibles con Angular 20.
- Un navegador web moderno.

Angular CLI está declarado como dependencia de desarrollo del frontend, por lo que los comandos pueden ejecutarse mediante los scripts de npm sin instalarlo globalmente.

Para comprobar las herramientas disponibles:

```bash
python --version
pip --version
node --version
npm --version
psql --version
```

En algunos sistemas el ejecutable de Python se denomina `python3` en lugar de `python`.

## 3. Tecnologías utilizadas

### 3.1. Backend

- Python 3.12.
- Django 5.2.
- Django REST Framework 3.17.1.
- Simple JWT 5.5.1 para autenticación mediante tokens JWT.
- psycopg 3.3.4 para la conexión con PostgreSQL.
- django-cors-headers 4.9.0.
- drf-spectacular 0.30.0 para el esquema y la documentación de la API.
- python-decouple 3.8 para cargar variables locales.

### 3.2. Frontend

- Angular 20.3.
- Angular CLI 20.3.3.
- TypeScript 5.9.
- Bootstrap 5.3.8.
- RxJS 7.8.
- Karma y Jasmine para pruebas unitarias.

### 3.3. Persistencia

- PostgreSQL.

## 4. Estructura general del proyecto

```text
trabajo_tesis_proyecto_tenis/
├── backend/           API Django, aplicaciones, migraciones y pruebas
├── frontend/          Aplicación Angular
├── database/          Recursos relacionados con base de datos
├── docs/              Documentación del proyecto
└── postman/           Recursos para pruebas de API
```

Dentro del backend se encuentran las aplicaciones `authentication`, que contiene el usuario personalizado y los roles, y `core`, que contiene el dominio deportivo. El frontend se organiza en funcionalidades, servicios, modelos, guards e interceptores.

## 5. Configuración del backend

### 5.1. Ingreso al directorio

Desde la raíz del repositorio:

```bash
cd backend
```

### 5.2. Creación y activación del entorno virtual

Crear el entorno:

```bash
python -m venv .venv
```

Activación en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activación en Símbolo del sistema de Windows:

```bat
.venv\Scripts\activate.bat
```

Activación en Linux o macOS:

```bash
source .venv/bin/activate
```

### 5.3. Instalación de dependencias

Con el entorno virtual activo:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5.4. Configuración local

El backend requiere un archivo `backend/.env`. El repositorio dispone de `backend/.env.example`, que contiene únicamente valores de ejemplo.

En PowerShell o Símbolo del sistema:

```bat
copy .env.example .env
```

En Linux o macOS:

```bash
cp .env.example .env
```

Editar `.env` sin incorporar credenciales reales al control de versiones. La estructura requerida es:

```env
SECRET_KEY=clave_local_larga_y_aleatoria
DEBUG=True
DB_NAME=nombre_base_datos
DB_USER=usuario_postgresql
DB_PASSWORD=contrasena_local
DB_HOST=localhost
DB_PORT=5432
```

`SECRET_KEY` debe ser privada. `DEBUG=True` solo corresponde al entorno local. El archivo actual de configuración deja `ALLOWED_HOSTS` vacío y autoriza CORS desde `http://localhost:4200`, por lo que la configuración entregada está orientada a ejecución local.

### 5.5. Conexión con PostgreSQL

Crear una base de datos y un usuario de PostgreSQL con permisos sobre ella. Los nombres siguientes son ejemplos:

```bash
psql -U postgres
```

```sql
CREATE USER usuario_tenis WITH PASSWORD 'contrasena_local_segura';
CREATE DATABASE torneos_tenis OWNER usuario_tenis;
```

Salir de `psql`:

```text
\q
```

Luego se deben copiar esos datos en las variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT` del archivo `.env`.

### 5.6. Aplicación de migraciones

Desde `backend/`, con el entorno activo y PostgreSQL disponible:

```bash
python manage.py migrate
```

Este comando crea las tablas definidas por Django y por las migraciones de `authentication` y `core`.

### 5.7. Creación inicial de roles y administrador

El modelo de usuario exige un rol. Las migraciones actuales no crean automáticamente los registros `Administrador`, `Organizador` y `Jugador`; además, el comando `createsuperuser` estándar no solicita este campo personalizado. Por ello, la inicialización debe realizarse explícitamente desde el shell de Django.

Ejecutar:

```bash
python manage.py shell
```

En el shell:

```python
from getpass import getpass
from authentication.models import Role, User

admin_role, _ = Role.objects.get_or_create(name="Administrador")
Role.objects.get_or_create(name="Organizador")
Role.objects.get_or_create(name="Jugador")

username = input("Nombre de usuario administrador: ")
email = input("Correo electrónico: ")
password = getpass("Contraseña: ")

User.objects.create_superuser(
    username=username,
    email=email,
    password=password,
    role=admin_role,
)
```

Finalizar el shell:

```python
exit()
```

No se deben copiar usuarios ni contraseñas de archivos de datos de desarrollo a un ambiente real. El catálogo maestro `Category` está registrado en el administrador de Django; si la base comienza vacía, un administrador técnico puede crear allí las categorías deportivas necesarias antes de configurar competencias.

### 5.8. Ejecución del servidor Django

```bash
python manage.py runserver
```

Direcciones locales principales:

- Backend: `http://localhost:8000/`
- API: `http://localhost:8000/api/`
- Salud de la API: `http://localhost:8000/api/health/`
- Administración Django: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## 6. Configuración del frontend

### 6.1. Ingreso e instalación

Abrir una segunda terminal desde la raíz del repositorio:

```bash
cd frontend
npm install
```

Cuando se requiera una instalación reproducible basada estrictamente en `package-lock.json`, se puede utilizar:

```bash
npm ci
```

### 6.2. Configuración necesaria

Los archivos `src/environments/environment.ts` y `src/environments/environment.development.ts` definen actualmente:

```typescript
apiUrl: 'http://localhost:8000/api'
```

No es necesario modificarlos para la ejecución local estándar. Si el backend se publica en otra dirección, este valor debe adaptarse sin incluir secretos en el código del frontend.

### 6.3. Ejecución de Angular

```bash
npm start
```

El script ejecuta `ng serve` y publica la aplicación en:

```text
http://localhost:4200/
```

## 7. Puesta en marcha completa

El orden recomendado es:

1. Iniciar PostgreSQL.
2. Activar el entorno virtual del backend.
3. Verificar el archivo `backend/.env`.
4. Ejecutar las migraciones cuando existan cambios pendientes.
5. Iniciar Django con `python manage.py runserver`.
6. En otra terminal, ingresar a `frontend/`.
7. Ejecutar `npm start`.
8. Abrir `http://localhost:4200/`.
9. Iniciar sesión con un usuario creado localmente.

El navegador se comunica con Angular en el puerto 4200 y Angular consume la API Django en el puerto 8000.

## 8. Verificación del funcionamiento

### 8.1. Verificación del backend

Abrir:

```text
http://localhost:8000/api/health/
```

La respuesta esperada informa el estado saludable del servicio. También se puede abrir `http://localhost:8000/api/docs/` para comprobar que Django carga el esquema de la API.

### 8.2. Verificación del frontend

1. Abrir `http://localhost:4200/`.
2. Confirmar que aparece el formulario de inicio de sesión.
3. Ingresar un usuario local válido.
4. Verificar que el sistema redirige al dashboard correspondiente al rol.
5. Comprobar que la barra de navegación muestra solo las opciones autorizadas.

### 8.3. Verificación de compilación

Desde `frontend/`:

```bash
npm run build
```

La compilación debe finalizar sin errores y generar los artefactos bajo `frontend/dist/`.

## 9. Ejecución de pruebas automatizadas

### 9.1. Backend

Desde `backend/`, con PostgreSQL configurado:

```bash
python manage.py test
```

Para ejecutar grupos existentes por aplicación:

```bash
python manage.py test authentication
python manage.py test core
```

El proyecto también contiene pruebas específicas de escalerilla en `core/test_ladder.py`, incluidas al ejecutar la suite de la aplicación.

### 9.2. Frontend

Desde `frontend/`:

```bash
npm test
```

Para una ejecución única sin permanecer observando cambios:

```bash
npm test -- --watch=false
```

Las pruebas utilizan Karma, Jasmine y Chrome mediante `karma-chrome-launcher`.

## 10. Problemas frecuentes y consideraciones

### 10.1. Falta una variable de entorno

Si Django informa que `SECRET_KEY` o una variable `DB_*` no está definida, comprobar que `.env` se encuentra dentro de `backend/` y contiene todos los nombres esperados por `settings.py`.

### 10.2. PostgreSQL rechaza la conexión

Verificar que el servicio esté iniciado, que el puerto coincida con `DB_PORT`, que la base exista y que el usuario tenga permisos. No sustituir PostgreSQL por SQLite sin modificar deliberadamente la configuración del proyecto.

### 10.3. No existen roles

La creación de jugadores y organizadores depende de los nombres exactos `Jugador` y `Organizador`. La autorización utiliza además `Administrador`. Se debe ejecutar la inicialización descrita en la sección 5.7.

### 10.4. `createsuperuser` no completa la creación

El campo `role` del usuario personalizado es obligatorio y no forma parte de las preguntas del comando estándar. Utilizar el shell de Django según la sección 5.7.

### 10.5. Error CORS o conexión desde Angular

La configuración permite `http://localhost:4200`. Confirmar que Angular utiliza ese origen y que el backend escucha en `http://localhost:8000`. Revisar también `apiUrl` en los archivos de entorno.

### 10.6. La interfaz no muestra categorías o canchas

El repositorio no automatiza datos maestros en las migraciones. El catálogo `Category` puede inicializarse desde el administrador Django. No existe actualmente una pantalla frontend independiente para administrar canchas; la interfaz de programación consume las canchas que ya existan en la base.

### 10.7. Token vencido o cierre por inactividad

El token de acceso tiene una vigencia configurada de 30 minutos y el token de actualización de 7 días. La interfaz también cierra la sesión después de 20 minutos de inactividad. Si la sesión deja de ser válida, se debe volver a iniciar sesión.

### 10.8. Consideraciones de despliegue

La configuración actual corresponde al desarrollo local. Antes de un despliegue se deben revisar, al menos, `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, CORS, manejo de archivos estáticos, servidor de aplicación, TLS y credenciales de PostgreSQL. Estas tareas no están automatizadas en el MVP actual.
