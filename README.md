# Tennis Tournament Management System

Sistema informático para la gestión operativa de torneos de tenis del Club Estadio Español de Curicó.

## Tecnologías

- Python 3.12
- Django 5.2
- Django REST Framework 3.17.1
- Django REST Framework Simple JWT
- PostgreSQL
- Angular 20.3
- Angular CLI 20.3.3
- Node.js y npm
- TypeScript 5.9
- Bootstrap 5.3.8

## Estructura

/backend
/frontend
/database
/docs
/postman

## Instalación

### Requisitos previos

Antes de ejecutar el proyecto, se deben instalar las siguientes tecnologías:

- Python 3.12 o superior
- PostgreSQL
- Node.js y npm
- Angular CLI
- Git

Para instalar Angular CLI de forma global:

```bash
npm install -g @angular/cli
```

### Backend

Entrar a la carpeta del backend:

```bash
cd backend
```

Crear un entorno virtual:

```bash
python -m venv venv
```

Activar el entorno virtual en Windows:

```bash
venv\Scripts\activate
```

Activar el entorno virtual en Linux o macOS:

```bash
source venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear el archivo de variables de entorno a partir del ejemplo:

```bash
cp .env.example .env
```

En Windows también se puede usar:

```bash
copy .env.example .env
```

Configurar en el archivo `.env` los datos de conexión a PostgreSQL:

```env
SECRET_KEY=tu_clave_secreta
DEBUG=True
DB_NAME=nombre_base_datos
DB_USER=usuario_postgresql
DB_PASSWORD=contrasena_postgresql
DB_HOST=localhost
DB_PORT=5432
```

Ejecutar migraciones:

```bash
python manage.py migrate
```

Levantar el servidor del backend:

```bash
python manage.py runserver
```

El backend quedará disponible en:

```text
http://localhost:8000
```

La API se consume desde:

```text
http://localhost:8000/api
```

### Frontend

Entrar a la carpeta del frontend:

```bash
cd frontend
```

Instalar dependencias:

```bash
npm install
```

Levantar el servidor de desarrollo:

```bash
npm start
```

También se puede ejecutar con Angular CLI:

```bash
ng serve
```

El frontend quedará disponible en:

```text
http://localhost:4200
```

Al ser este un trabajo de universidad, se dejan credenciales expuestas, pero serán eliminadas al momento de pasar el proyecto a producción.
