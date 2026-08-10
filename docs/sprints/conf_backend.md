backend/
├── authentication/
├── core/
├── config/
├── manage.py
├── requirements.txt
├── .env
└── .env.example

5. Configuración del Backend
5.1 Django

Se configuró el proyecto Django como backend principal de la aplicación.

La estructura inicial considera:

backend/
├── authentication/
├── core/
├── config/
├── manage.py
├── requirements.txt
├── .env
└── .env.example
5.2 Usuario personalizado

Se implementó un modelo de usuario basado en AbstractUser.

class User(AbstractUser):
    pass

Django fue configurado para utilizar este modelo mediante:

AUTH_USER_MODEL = "authentication.User"

El modelo mantiene inicialmente las capacidades proporcionadas por Django y constituye la base para el mecanismo de autenticación del sistema.

5.3 PostgreSQL

Se configuró PostgreSQL como sistema gestor de base de datos.

La conexión se realiza mediante variables de entorno:

DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT

La aplicación utiliza Django ORM para realizar la interacción con la base de datos.

5.4 Variables de entorno

Se utilizó python-decouple para separar la configuración sensible del código fuente.

Se definieron archivos:

.env
.env.example

El archivo .env contiene los valores utilizados localmente, mientras que .env.example sirve como referencia para configurar el proyecto en otros entornos.

5.5 Django REST Framework

Se configuró Django REST Framework como plataforma para la construcción de la API REST.

La autenticación predeterminada utiliza:

JWTAuthentication

La configuración permite que las vistas puedan definir explícitamente cuáles requieren autenticación.

5.6 CORS

Se configuró CORS para permitir la comunicación entre el frontend Angular y el backend Django durante el desarrollo:

http://localhost:4200

Esto permite la comunicación:

Angular → Django REST Framework
6. Health Check

Se implementó un endpoint de comprobación del estado de la API:

GET /api/health/

Este endpoint permite comprobar que el backend se encuentra operativo.

Respuesta esperada:

{
    "status": "OK",
    "application": "Sistema de Gestión de Torneos de Tenis",
    "version": "1.0.0"
}

El endpoint no requiere autenticación debido a que su finalidad es comprobar la disponibilidad de la API.

7. Autenticación mediante JWT

Se implementó autenticación utilizando JSON Web Token mediante Simple JWT.

Se configuraron los siguientes endpoints:

POST /api/token/
POST /api/token/refresh/
POST /api/token/verify/
7.1 Obtención del token

El usuario envía sus credenciales:

username
password

al endpoint:

POST /api/token/

Si las credenciales son válidas, Django devuelve:

access token
refresh token
7.2 Refresh Token

El refresh token permite solicitar un nuevo access token sin volver a ingresar las credenciales.

Endpoint:

POST /api/token/refresh/
8. Implementación de Angular

Se configuró Angular 20 utilizando una estructura basada en componentes y funcionalidades.

La estructura relevante quedó organizada de la siguiente manera:

src/app/
├── core/
│   ├── guards/
│   │   └── auth-guard.ts
│   ├── interceptors/
│   │   └── auth-interceptor.ts
│   ├── models/
│   │   ├── login-request.ts
│   │   ├── token-response.ts
│   │   └── health-response.model.ts
│   └── services/
│       ├── auth.ts
│       ├── health.service.ts
│       └── token.ts
│
├── features/
│   ├── authentication/
│   │   └── pages/login/
│   ├── dashboard/
│   │   └── pages/home/
│   ├── matches/
│   ├── players/
│   ├── rankings/
│   └── tournaments/
│
├── layout/
└── shared/

Las funcionalidades correspondientes a players, matches, rankings y tournaments corresponden a etapas posteriores del desarrollo.

9. AuthService

Se implementó AuthService en:

core/services/auth.ts

Sus responsabilidades principales son:

Realizar el inicio de sesión.
Comunicarse con /api/token/.
Guardar los tokens obtenidos.
Cerrar la sesión.
Eliminar los tokens almacenados.

Flujo:

LoginComponent
      ↓
AuthService
      ↓
POST /api/token/
      ↓
Django
      ↓
Access + Refresh Token
      ↓
TokenService
10. TokenService

Se implementó:

core/services/token.ts

Sus responsabilidades son:

Guardar el access token.
Guardar el refresh token.
Recuperar el access token.
Recuperar el refresh token.
Eliminar los tokens.
Determinar si existe una sesión autenticada.

Los tokens son almacenados utilizando localStorage.

11. HTTP Interceptor

Se implementó:

core/interceptors/auth-interceptor.ts

Su función es agregar automáticamente el access token a las peticiones HTTP cuando existe una sesión autenticada.

El encabezado utilizado es:

Authorization: Bearer <access_token>

Flujo:

Petición HTTP
     ↓
AuthInterceptor
     ↓
¿Existe access token?
     ↓
Sí
     ↓
Authorization: Bearer <token>
     ↓
Django REST Framework

El interceptor fue registrado en app.config.ts.

12. Auth Guard

Se implementó:

core/guards/auth-guard.ts

Su función es proteger las rutas que requieren autenticación.

Actualmente el dashboard se encuentra protegido mediante:

authGuard

Flujo:

/dashboard
     ↓
authGuard
     ↓
¿Usuario autenticado?
   ↙        ↘
 Sí          No
 ↓            ↓
Dashboard    /login
13. Login

Se implementó el componente:

features/authentication/pages/login/

El formulario permite ingresar:

Usuario.
Contraseña.

El componente utiliza AuthService para realizar la autenticación.

Después de una autenticación exitosa:

Login
  ↓
JWT
  ↓
Guardar tokens
  ↓
/dashboard
14. Dashboard

Se implementó una vista inicial de dashboard como destino posterior al inicio de sesión.

La vista permite comprobar que:

La autenticación fue exitosa.
La ruta protegida puede ser accedida.
El usuario puede cerrar sesión.
15. Logout

Se implementó el cierre de sesión mediante AuthService.

El proceso elimina los tokens almacenados:

Logout
   ↓
TokenService
   ↓
Eliminar access token
   ↓
Eliminar refresh token
   ↓
/login
16. Pruebas automatizadas
16.1 Backend

Se implementaron pruebas utilizando el framework de pruebas de Django y Django REST Framework.

Las pruebas verifican:

Health Check
GET /api/health/

Debe responder:

200 OK
Login válido

Se crea un usuario temporal dentro de la base de datos de pruebas y se verifica que las credenciales correctas permitan obtener:

access
refresh
Login inválido

Se utilizan credenciales incorrectas y se verifica:

401 Unauthorized
Refresh Token

Se obtiene un refresh token y se verifica que permita generar un nuevo access token.

16.2 Base de datos utilizada en las pruebas

Las pruebas de Django utilizan una base de datos temporal creada automáticamente por el framework de pruebas.

Los usuarios utilizados durante las pruebas no corresponden a usuarios reales de la base de datos de desarrollo.

Esto permite ejecutar las pruebas de manera reproducible sin modificar los datos reales de la aplicación.

16.3 Frontend

Se implementaron pruebas mediante el sistema de testing de Angular.

Se verificaron los principales componentes de la autenticación:

App
AuthService
TokenService
AuthGuard
AuthInterceptor
LoginComponent
HomeComponent

Las pruebas fueron ejecutadas mediante:

ng test

El conjunto de pruebas configurado para el Sprint 1 fue ejecutado correctamente.

17. Pruebas manuales

Además de las pruebas automatizadas, se realizó una validación manual del flujo completo de autenticación.

Caso 1 — Login correcto
Usuario ingresa credenciales
        ↓
Login
        ↓
JWT
        ↓
Dashboard

Resultado: Correcto.

Caso 2 — Acceso al Dashboard sin autenticación

Se intentó acceder directamente a:

/dashboard

sin haber iniciado sesión.

Resultado esperado:

/dashboard
      ↓
AuthGuard
      ↓
/login

Resultado: Correcto.

Caso 3 — Logout

Se inició sesión y posteriormente se seleccionó la opción de cerrar sesión.

Resultado:

Dashboard
   ↓
Logout
   ↓
Tokens eliminados
   ↓
Login

Resultado: Correcto.

18. Resultado del Sprint

El Sprint 1 se considera completado.

Se logró establecer la infraestructura inicial del sistema y desarrollar el primer incremento funcional correspondiente al mecanismo de autenticación.

El incremento desarrollado permite:

Ejecutar el backend Django.
Conectarse con PostgreSQL.
Ejecutar la API REST.
Autenticar usuarios mediante JWT.
Mantener los tokens en el frontend.
Proteger rutas mediante AuthGuard.
Enviar automáticamente el JWT mediante HTTP Interceptor.
Acceder a un dashboard protegido.
Cerrar sesión.
Ejecutar pruebas automatizadas de frontend y backend.
Validar manualmente el flujo de autenticación.
19. Pendientes para Sprint 2

Con el Sprint 1 cerrado, el desarrollo continúa con el Sprint 2, orientado a la implementación de la gestión de jugadores e inscripciones.

El desarrollo comenzará por la entidad:

Player

y posteriormente se incorporarán las entidades relacionadas según las dependencias definidas en el modelo de datos:

Player
   ↓
Registration
   ↓
CompetitionCategory

Antes de implementar nuevas entidades se deberá respetar el modelo de datos y las relaciones establecidas en el diseño del sistema.

20. Evidencias recomendadas

Para documentar el Sprint 1 se deben conservar las siguientes evidencias:

Captura del backend Django ejecutándose.
Captura de PostgreSQL/conexión exitosa, si corresponde.
Captura de login exitoso.
Captura del dashboard.
Captura de acceso a /dashboard sin autenticación y redirección al login.
Captura del cierre de sesión.
Resultado de python manage.py test.
Resultado de ng test.
Commits correspondientes al desarrollo del Sprint 1.

Estas evidencias podrán utilizarse posteriormente en el capítulo de implementación, pruebas y resultados de la tesis.


### Una recomendación importante

Yo **no pondría en este MD el endpoint `/api/auth/me/`**, porque finalmente decidimos no crearlo. No forma parte del sistema y no necesitamos agregar una funcionalidad artificial solamente para demostrar JWT.

También dejaría este archivo como **registro técnico del sprint**, mientras que en la tesis usamos una versión más resumida y académica en el **4.1** y posteriormente las evidencias en el apartado de implementación/pruebas.

Y desde ahora, para cada sprint podemos mantener exactamente la misma estructura:

```text
docs/
└── sprints/
    ├── SPRINT_1.md
    ├── SPRINT_2.md
    ├── SPRINT_3.md
    └── SPRINT_4.md

Así, mientras programamos el Sprint 2, vamos actualizando SPRINT_2.md con cada modelo, endpoint, componente, prueba y decisión técnica. Eso nos va a facilitar muchísimo después escribir el capítulo 4 sin tener que recordar todo lo que hicimos.