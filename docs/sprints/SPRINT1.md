# Sprint 1 — Configuración base y autenticación

**Proyecto:** Sistema de Gestión Operativa de Torneos de Tenis  
**Sprint:** 1  
**Estado:** Completado  
**Tipo:** Análisis, configuración técnica e implementación inicial  
**Fecha:** 2026  

---

## 1. Objetivo del Sprint

Establecer la base técnica del sistema y desarrollar el primer incremento funcional, correspondiente al mecanismo de autenticación de usuarios.

El Sprint 1 contempla la configuración inicial del backend y frontend, la conexión con la base de datos PostgreSQL, la configuración de Django REST Framework, la implementación de autenticación mediante JSON Web Token (JWT), la protección de rutas en Angular y la validación mediante pruebas automatizadas y manuales.

---

## 2. Alcance

Durante este sprint se trabajó en:

- Configuración del entorno backend.
- Configuración de Django.
- Configuración de Django REST Framework.
- Configuración de PostgreSQL.
- Configuración de variables de entorno.
- Creación del modelo de usuario personalizado.
- Configuración de CORS.
- Configuración de autenticación mediante JWT.
- Configuración inicial de Angular 20.
- Configuración de Bootstrap.
- Implementación del servicio de autenticación.
- Implementación del almacenamiento de tokens.
- Implementación del interceptor HTTP.
- Implementación del guard de autenticación.
- Implementación de la pantalla de inicio de sesión.
- Implementación del dashboard inicial.
- Implementación del cierre de sesión.
- Pruebas automatizadas de frontend.
- Pruebas automatizadas de backend.
- Pruebas manuales del flujo de autenticación.

---

# 3. Tecnologías utilizadas

## Backend

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL 18
- Simple JWT
- `python-decouple`
- `django-cors-headers`

## Frontend

- Angular 20
- TypeScript
- Bootstrap 5
- SCSS
- Node.js 22
- npm

## Herramientas

- Visual Studio Code
- Git
- GitHub
- Postman

---

# 4. Arquitectura implementada

Durante el Sprint 1 se estableció la comunicación entre las principales capas de la aplicación.

```text
┌──────────────────────────────┐
│          Angular 20          │
│                              │
│  Login                       │
│  AuthService                 │
│  TokenService                │
│  AuthGuard                   │
│  HTTP Interceptor             │
│  Dashboard                   │
└──────────────┬───────────────┘
               │
               │ HTTP / REST
               │ JWT
               ▼
┌──────────────────────────────┐
│    Django REST Framework     │
│                              │
│  Authentication              │
│  JWT / SimpleJWT             │
│  API                         │
└──────────────┬───────────────┘
               │
               │ Django ORM
               ▼
┌──────────────────────────────┐
│        PostgreSQL 18         │
└──────────────────────────────┘