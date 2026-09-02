# Manual de usuario

## 1. Introducción

Este manual describe el uso del MVP del **Sistema Informático para la Gestión Operativa de Torneos de Tenis en el Club Estadio Español de Curicó**. Su contenido se limita a las pantallas, rutas, permisos y reglas implementadas actualmente.

La interfaz adapta las opciones visibles al rol autenticado. Las operaciones críticas vuelven a ser verificadas por el backend, por lo que conocer una dirección interna no permite omitir los permisos.

## 2. Objetivo del sistema

El sistema centraliza la gestión de jugadores, organizadores, competencias, categorías competitivas, inscripciones, partidos, resultados, cuadros de eliminación directa, escalerillas y posiciones. También ofrece al jugador una vista de su actividad deportiva y de las competencias disponibles.

## 3. Roles del sistema

### 3.1. Administrador

El Administrador dispone del alcance más amplio del MVP. Puede:

- crear, consultar, editar y eliminar jugadores;
- crear, consultar, editar y eliminar competencias;
- configurar las categorías asociadas a una competencia;
- consultar, crear, editar y eliminar inscripciones;
- asignar estados y cabezas de serie a las inscripciones;
- consultar, crear, editar y eliminar partidos manuales, con las restricciones del cuadro;
- programar partidos y registrar resultados;
- generar y, cuando las reglas lo permiten, eliminar cuadros y escalerillas;
- crear, editar, activar y desactivar usuarios organizadores;
- consultar el dashboard administrativo.

### 3.2. Organizador

El Organizador puede efectuar la gestión operativa, pero no posee todas las facultades del Administrador. Puede:

- consultar, crear y editar jugadores, pero no eliminarlos;
- consultar, crear y editar competencias, pero no eliminarlas;
- configurar categorías de competencia y eliminar una asociación de categoría cuando no tenga inscripciones activas;
- crear y editar inscripciones, pero no eliminarlas;
- generar cuadros de eliminación directa y escalerillas;
- programar partidos y registrar o corregir resultados;
- crear, editar y eliminar sets;
- acceder a la gestión contextual de partidos desde cada categoría de competencia.

La navegación principal no muestra al Organizador las listas globales de `Inscripciones`, `Partidos` ni `Organizadores`. Las operaciones de inscripciones y partidos se realizan desde el contexto de una competencia o categoría. Tampoco puede crear ni administrar organizadores.

### 3.3. Jugador

El Jugador tiene un acceso deportivo y de consulta. Puede:

- consultar competencias;
- ver categorías abiertas o categorías en las que tiene una inscripción vigente;
- inscribirse a sí mismo en una categoría habilitada;
- consultar sus propias inscripciones;
- consultar cuadros, escalerillas, participantes confirmados, partidos y posiciones de categorías en las que está confirmado;
- consultar su próximo partido, torneos, rendimiento y resultados recientes en el dashboard.

No puede crear o modificar competencias, jugadores, partidos, sets, posiciones u organizadores.

## 4. Inicio de sesión

**Rol habilitado:** Administrador, Organizador y Jugador.

**Objetivo:** Autenticar al usuario y cargar la interfaz correspondiente a su rol.

### Pasos

1. Abrir la dirección del frontend, normalmente `http://localhost:4200/`.
2. Ingresar el nombre de usuario.
3. Ingresar la contraseña.
4. Presionar el botón de inicio de sesión.

### Resultado esperado

El sistema obtiene tokens JWT, identifica el rol incluido en el token y redirige al dashboard. La barra superior presenta las opciones autorizadas.

### Validaciones o restricciones

- Las credenciales incorrectas producen un mensaje de acceso no autorizado.
- Un usuario inactivo no puede iniciar sesión.
- El token de acceso tiene una vigencia de 30 minutos.
- La interfaz cierra la sesión tras 20 minutos sin actividad.
- El botón `Cerrar sesión` elimina los tokens almacenados localmente y vuelve al formulario de acceso.

## 5. Funcionalidades del Administrador

### 5.1. Consultar el dashboard administrativo

**Rol habilitado:** Administrador.

**Objetivo:** Acceder a un resumen de competencias y a los accesos principales de administración.

### Pasos

1. Iniciar sesión.
2. Seleccionar `Dashboard`.
3. Revisar las secciones de próximas competencias y competencias en curso.
4. Utilizar los accesos a competencias, jugadores, inscripciones o partidos.

### Resultado esperado

Se muestran competencias con estado `PENDIENTE`, `ABIERTA` o `EN_CURSO`, ordenadas por fecha según su sección.

### Validaciones o restricciones

- El dashboard no reemplaza las listas completas de gestión.
- Solo se muestran datos disponibles en la API.

### 5.2. Gestionar organizadores

**Rol habilitado:** Administrador.

**Objetivo:** Crear y mantener las cuentas de los usuarios con rol Organizador.

### Pasos

1. Seleccionar `Organizadores` en la navegación.
2. Para crear uno, seleccionar `Nuevo organizador`.
3. Completar nombre, apellido, usuario, correo, contraseña y confirmación.
4. Guardar el formulario.
5. Para modificar datos, utilizar `Editar` en el listado.
6. Para controlar el acceso, utilizar la acción de activar o desactivar.

### Resultado esperado

El usuario se crea siempre con el rol `Organizador`. La contraseña se almacena mediante el mecanismo de hash de Django. La activación o desactivación cambia su posibilidad de autenticarse.

### Validaciones o restricciones

- Esta sección está protegida tanto por el guard de Administrador como por el permiso del backend.
- La contraseña y su confirmación deben coincidir y satisfacer los validadores de Django.
- En la edición no se ofrece cambio de contraseña.
- El MVP permite activar y desactivar organizadores; no expone eliminación de organizadores.
- No se puede forzar otro rol desde el formulario.

### 5.3. Gestionar jugadores

**Rol habilitado:** Administrador.

**Objetivo:** Crear, consultar, editar o eliminar perfiles de jugadores y sus cuentas asociadas.

### Pasos

1. Seleccionar `Jugadores`.
2. Utilizar la búsqueda cuando sea necesario.
3. Seleccionar `Nuevo jugador` para crear un registro.
4. Completar los datos personales, de contacto, categoría y credenciales requeridas.
5. Guardar.
6. Utilizar `Editar` o `Eliminar` desde el listado para mantener un registro existente.

### Resultado esperado

Al crear un jugador se crea también un usuario con rol `Jugador`, relacionado uno a uno con el perfil deportivo.

### Validaciones o restricciones

- El nombre de usuario, correo y RUT no pueden duplicarse.
- La fecha de nacimiento no puede ser futura y debe respetar las validaciones implementadas.
- La contraseña debe cumplir los validadores de Django y coincidir con su confirmación.
- La categoría seleccionada debe existir.
- La eliminación está reservada al Administrador.

### 5.4. Gestionar competencias y sus categorías

**Rol habilitado:** Administrador.

**Objetivo:** Crear o mantener una competencia y asociarle categorías con cupos mínimos y máximos.

### Pasos

1. Seleccionar `Competencias`.
2. Presionar `Nueva competencia` o `Editar` en una competencia existente.
3. Completar nombre, tipo, fechas, estado y fecha límite de inscripción.
4. Marcar las categorías que participarán.
5. Para cada categoría marcada, indicar mínimo y máximo de jugadores.
6. Guardar.
7. Desde la lista, utilizar `Categorías` para consultar cupos, inscritos y acciones deportivas.

### Resultado esperado

Se guarda la competencia y se crean o actualizan sus asociaciones `CompetitionCategory`. La pantalla de categorías muestra cupos usados, cupos disponibles, capacidad y jugadores inscritos.

### Validaciones o restricciones

- Los tipos disponibles son `ELIMINACION_DIRECTA` y `ESCALERILLA`.
- La fecha de término no puede ser anterior a la de inicio.
- La fecha límite de inscripción no puede ser posterior al inicio.
- Al crear, las fechas de inicio y cierre no pueden estar en el pasado.
- El mínimo de jugadores debe ser mayor que cero y no puede superar el máximo.
- Una misma categoría no puede repetirse dentro de una competencia.
- No se puede quitar una categoría de competencia que tenga inscripciones no canceladas.
- La eliminación completa de una competencia está reservada al Administrador.

### 5.5. Gestionar inscripciones y cabezas de serie

**Rol habilitado:** Administrador.

**Objetivo:** Inscribir jugadores, cambiar el estado de una inscripción y definir cabezas de serie.

### Pasos

1. Seleccionar `Inscripciones` o acceder a `Inscribir jugador` desde una categoría.
2. Seleccionar la competencia y su categoría.
3. Buscar y seleccionar al jugador.
4. Definir el estado: `PENDIENTE`, `CONFIRMADA` o `CANCELADA`.
5. Ingresar el número de cabeza de serie cuando corresponda.
6. Guardar.
7. Para mantener una inscripción, utilizar `Editar` o `Eliminar` desde el listado.

### Resultado esperado

La inscripción queda asociada al jugador y a la categoría efectiva de la competencia. Las inscripciones canceladas dejan de ocupar cupo.

### Validaciones o restricciones

- No se puede superar el máximo de jugadores de la categoría.
- Un jugador no puede mantener más de una inscripción vigente en la misma competencia, aunque sean categorías diferentes.
- Solo las inscripciones `CONFIRMADA` participan en cuadros y escalerillas.
- El Administrador puede inscribir después del cierre y en una competencia `EN_CURSO`; los demás roles no.
- No se puede inscribir en una competencia `FINALIZADA` o `CANCELADA`.
- Los números de seed deben ser positivos, no repetirse y no superar el número de participantes confirmados al generar el cuadro.
- La eliminación de inscripciones está reservada al Administrador.

### 5.6. Generar un cuadro de eliminación directa

**Rol habilitado:** Administrador.

**Objetivo:** Crear automáticamente todas las rondas de una categoría de eliminación directa.

### Pasos

1. Abrir `Competencias`.
2. Entrar a `Categorías` de una competencia de eliminación directa.
3. Abrir el detalle deportivo de la categoría.
4. Revisar los participantes confirmados y sus seeds.
5. Seleccionar `Generar cuadro`.
6. Confirmar la operación.

### Resultado esperado

El sistema calcula la siguiente potencia de dos, distribuye jugadores y crea los partidos de todas las rondas. Los BYE de primera ronda avanzan automáticamente al jugador correspondiente.

### Validaciones o restricciones

- La competencia debe ser de eliminación directa.
- Solo se consideran inscripciones `CONFIRMADA`.
- Debe cumplirse el mínimo configurado, no superarse el máximo y existir al menos dos participantes.
- No se genera un segundo cuadro si ya existen partidos en la categoría.
- Los seeds 1 y 2 quedan en mitades opuestas; los seeds superiores se distribuyen según el orden implementado.
- Sin seeds, la distribución es aleatoria.
- Los BYE se resuelven en la primera ronda y no deben confundirse con un Walk Over.
- El cuadro solo puede eliminarse mientras no tenga resultados deportivos o estados que lo bloqueen; los BYE automáticos no se consideran actividad manual.

### 5.7. Programar un partido y validar conflictos

**Rol habilitado:** Administrador.

**Objetivo:** Asignar fecha, hora y cancha a un partido generado o manual.

### Pasos

1. Abrir el cuadro o la gestión de partidos de una escalerilla.
2. Seleccionar la acción para programar o editar la programación del partido.
3. Ingresar fecha y hora.
4. Seleccionar una cancha presentada en el formulario.
5. Guardar.

### Resultado esperado

El partido queda asociado a la fecha, hora y cancha seleccionadas, y la programación se muestra en la vista deportiva.

### Validaciones o restricciones

- El backend utiliza una duración fija de 90 minutos para detectar superposiciones.
- Se rechaza la superposición con otro partido no cancelado en la misma cancha.
- Se rechaza la superposición de cualquiera de los jugadores con otro partido no cancelado.
- El partido que se está editando se excluye de su propia verificación.
- Los partidos `CANCELADO` no producen conflictos.
- La interfaz advierte cuando la fecha está fuera del período de la competencia o es anterior a la fecha actual, pero permite guardar si la corrección es intencional.
- Solo se puede modificar la programación mientras el partido esté `PROGRAMADO`.
- Las canchas con estado de mantención se identifican en el selector; el estado por sí solo no bloquea su selección en la implementación actual.
- La programación de una ronda futura depende de que sus participantes estén definidos.

### 5.8. Registrar un resultado normal

**Rol habilitado:** Administrador.

**Objetivo:** Registrar sets hasta determinar el ganador de un partido.

### Pasos

1. Abrir el partido desde el cuadro, la escalerilla o la lista de partidos.
2. Seleccionar `Ingresar resultado`.
3. Registrar el marcador del primer set.
4. Registrar el segundo set.
5. Si cada jugador ganó un set, registrar el tercer set como Super Tie-Break.
6. Guardar cada set.

### Resultado esperado

El partido pasa a `EN_JUEGO` mientras no exista ganador. Cuando un jugador gana dos sets completos, pasa a `FINALIZADO` y el ganador queda registrado automáticamente.

### Validaciones o restricciones

- El formato es al mejor de tres sets.
- Los sets normales válidos incluyen 6-0 a 6-4, 7-5 y 7-6.
- No se pueden registrar sets en un partido cancelado, con BYE, con jugadores por definir, con Walk Over o resuelto por retiro.
- Los sets deben registrarse en orden y no pueden repetirse.
- No puede existir un set posterior a un set marcado como incompleto.
- Si el partido pertenece a eliminación directa, no se permite alterar el resultado cuando el partido dependiente de la ronda siguiente ya comenzó o fue resuelto.

### 5.9. Registrar un Super Tie-Break

**Rol habilitado:** Administrador.

**Objetivo:** Resolver el tercer set cuando ambos jugadores han ganado un set.

### Pasos

1. Registrar los dos primeros sets con un ganador distinto en cada uno.
2. Crear el set número 3.
3. Marcarlo como Super Tie-Break.
4. Ingresar los puntos y guardar.

### Resultado esperado

El ganador del Super Tie-Break obtiene el segundo set ganado y el partido finaliza.

### Validaciones o restricciones

- Solo el tercer set puede ser Super Tie-Break y el tercer set debe registrarse de esa forma.
- Se juega a 10 puntos con diferencia mínima de dos.
- Si el perdedor tiene 8 puntos o menos, el ganador debe tener 10.
- Si el perdedor tiene 9 o más, el ganador debe tener exactamente dos puntos más.
- Ejemplos válidos: 10-8, 11-9 y 12-10.
- Un resultado como 12-2 es inválido.

### 5.10. Registrar Walk Over

**Rol habilitado:** Administrador.

**Objetivo:** Finalizar administrativamente un partido porque un jugador no se presentó.

### Pasos

1. Abrir el ingreso de resultado del partido.
2. Seleccionar la opción de Walk Over.
3. Indicar el ganador.
4. Confirmar.

### Resultado esperado

El partido queda `FINALIZADO`, con resolución `WALKOVER`, sin sets y con el ganador indicado.

### Validaciones o restricciones

- Deben estar definidos los dos jugadores.
- No pueden existir sets registrados.
- El ganador debe ser uno de los participantes.
- No se admite en un partido cancelado.
- Si ya hubo juego, debe utilizarse Retiro.
- En eliminación directa el ganador avanza; en escalerilla se recalculan las posiciones sin propagación de cuadro.

### 5.11. Registrar retiro

**Rol habilitado:** Administrador.

**Objetivo:** Finalizar un partido cuando un jugador se retira, conservando el marcador existente o parcial.

### Pasos

1. Abrir el ingreso de resultado.
2. Seleccionar la opción de Retiro.
3. Indicar el ganador.
4. Cuando corresponda, registrar el marcador parcial como set incompleto.
5. Confirmar.

### Resultado esperado

El partido queda `FINALIZADO`, con resolución `RETIREMENT`; los sets existentes se conservan y el ganador queda registrado.

### Validaciones o restricciones

- Deben estar definidos ambos jugadores.
- Puede registrarse sin sets cuando el retiro ocurre al inicio.
- Un set incompleto no cuenta como set ganado y debe ser el último registrado.
- Un marcador que ya constituye un set completo no puede marcarse como incompleto.
- Un parcial del tercer set debe seguir las reglas de Super Tie-Break.
- No se admite en un partido cancelado.
- En eliminación directa el ganador avanza automáticamente.

### 5.12. Corregir una resolución administrativa

**Rol habilitado:** Administrador.

**Objetivo:** Volver desde Walk Over o Retiro a una resolución normal.

### Pasos

1. Abrir el resultado de un partido resuelto por Walk Over o Retiro.
2. Seleccionar la acción para restablecer la resolución.
3. Confirmar.
4. Corregir o completar los sets cuando sea necesario.

### Resultado esperado

La resolución vuelve a `NORMAL`, se conservan los sets y el sistema recalcula el estado y el ganador. Si los sets no determinan ganador, el ganador administrativo se limpia.

### Validaciones o restricciones

- No se puede aplicar a un partido cancelado ni a uno que ya tenga resolución normal.
- No se permite cuando el partido siguiente del cuadro ya comenzó o fue resuelto.
- La propagación hacia la ronda siguiente se corrige cuando todavía es editable.

### 5.13. Generar y consultar una escalerilla

**Rol habilitado:** Administrador.

**Objetivo:** Crear los enfrentamientos todos contra todos y consultar la tabla de posiciones.

### Pasos

1. Abrir una competencia de tipo `ESCALERILLA`.
2. Entrar a su categoría.
3. Revisar los participantes confirmados.
4. Seleccionar `Generar escalerilla` y confirmar.
5. Abrir `Gestión de partidos` para programar o ingresar resultados.
6. Revisar la tabla de posiciones en la vista de la categoría.

### Resultado esperado

El sistema crea un partido para cada combinación de dos participantes y un registro de posición para cada jugador. La tabla se recalcula al cambiar resultados o inscripciones.

### Validaciones o restricciones

- La categoría debe pertenecer a una competencia de escalerilla.
- Se requieren al menos dos participantes confirmados.
- No puede existir una escalerilla previamente generada en esa categoría.
- La tabla muestra posición, partidos jugados, ganados y perdidos, sets, diferencia de sets, juegos, diferencia de juegos y puntos.
- En un resultado normal 2-1, el ganador recibe 3 puntos y el perdedor 2.
- En los demás resultados normales contabilizados, el ganador recibe 4 puntos y el perdedor 1.
- Walk Over asigna 4 puntos al ganador y 1 al perdedor, además de 2 sets y 12 juegos administrativos para el ganador.
- Retiro asigna 4 puntos al ganador y 1 al perdedor, conservando las estadísticas derivadas de los sets registrados.
- El Super Tie-Break no se suma como juegos en la diferencia de juegos.
- La escalerilla solo puede eliminarse si sus partidos siguen sin actividad deportiva que bloquee la operación.

## 6. Funcionalidades del Organizador

### 6.1. Gestión de jugadores y competencias

**Rol habilitado:** Organizador.

**Objetivo:** Mantener los datos operativos necesarios para organizar torneos.

### Pasos

1. Desde el dashboard o la navegación, abrir `Jugadores` o `Competencias`.
2. Crear o editar el registro requerido.
3. En competencias, seleccionar y configurar las categorías participantes.
4. Guardar los cambios.

### Resultado esperado

Los datos quedan actualizados conforme a las mismas validaciones descritas para el Administrador.

### Validaciones o restricciones

- El Organizador no puede eliminar jugadores ni competencias.
- Puede quitar una categoría de competencia únicamente si no existen inscripciones activas asociadas.
- No tiene acceso a la gestión de organizadores.

### 6.2. Gestionar inscripciones desde una categoría

**Rol habilitado:** Organizador.

**Objetivo:** Inscribir o actualizar participantes dentro del contexto de una competencia.

### Pasos

1. Abrir `Competencias`.
2. Seleccionar `Categorías`.
3. En la categoría deseada, seleccionar `Inscribir jugador`.
4. Completar jugador, estado y seed.
5. Guardar.

### Resultado esperado

La inscripción se crea y el usuario vuelve al contexto de la competencia.

### Validaciones o restricciones

- El Organizador puede crear y editar, pero no eliminar inscripciones.
- No puede inscribir después de la fecha límite ni en una competencia en curso; esas excepciones corresponden solo al Administrador.
- Se aplican las reglas de cupo y duplicidad descritas en la sección 5.5.

### 6.3. Gestionar cuadros, escalerillas y resultados

**Rol habilitado:** Organizador.

**Objetivo:** Ejecutar la operación deportiva de una categoría.

### Pasos

1. Abrir una competencia y su listado de categorías.
2. Entrar al detalle deportivo.
3. Generar el cuadro o la escalerilla, según el tipo.
4. Programar los partidos.
5. Ingresar resultados normales, Walk Over o Retiro.
6. Consultar el avance del cuadro o las posiciones.

### Resultado esperado

El Organizador puede completar el flujo operativo desde el contexto de la categoría, con las mismas reglas deportivas y protecciones históricas indicadas para el Administrador.

### Validaciones o restricciones

- La lista global `/matches` está protegida en el frontend para el Administrador; el Organizador utiliza la gestión contextual de la categoría.
- Puede crear, modificar y eliminar sets.
- No puede eliminar partidos manuales mediante el permiso general de backend; la eliminación general de partidos está reservada al Administrador.
- Las acciones de generación y eliminación completa de cuadro o escalerilla están disponibles cuando las reglas de actividad lo permiten.

## 7. Funcionalidades del Jugador

### 7.1. Consultar el dashboard del jugador

**Rol habilitado:** Jugador.

**Objetivo:** Consultar la actividad deportiva personal.

### Pasos

1. Iniciar sesión.
2. Abrir `Dashboard`.
3. Revisar `Próximo partido`, `Mis torneos`, `Rendimiento`, `Resultados recientes` y `Torneos disponibles`.
4. Seleccionar un torneo confirmado para abrir su detalle deportivo.

### Resultado esperado

El dashboard muestra:

- el próximo partido programado futuro, con rival, fecha, hora, competencia, categoría y cancha;
- inscripciones pendientes o confirmadas;
- victorias, derrotas, partidos jugados y porcentaje de victorias;
- resultados finalizados recientes y sus marcadores;
- competencias abiertas de la categoría actual que tengan plazo y cupos disponibles.

### Validaciones o restricciones

- El usuario debe poseer un perfil `Player` asociado.
- Solo se consideran como resultados personales los partidos finalizados con ambos jugadores y un ganador válido.
- Solo las inscripciones confirmadas permiten abrir el detalle deportivo desde `Mis torneos`.

### 7.2. Inscribirse en una competencia

**Rol habilitado:** Jugador.

**Objetivo:** Crear su propia inscripción en una categoría disponible.

### Pasos

1. Abrir el dashboard o `Competencias` y luego `Categorías`.
2. Identificar una competencia abierta correspondiente a la categoría actual.
3. Confirmar que existen cupos disponibles.
4. Seleccionar `Inscribirme`.

### Resultado esperado

La inscripción se crea para el jugador autenticado. En la implementación actual, la inscripción realizada por el propio Jugador queda con estado `CONFIRMADA` y sin seed.

### Validaciones o restricciones

- El jugador no puede seleccionar otra identidad, estado ni cabeza de serie.
- Solo puede inscribirse en su categoría actual.
- La competencia debe estar `PENDIENTE` o `ABIERTA`; la interfaz de descubrimiento muestra como disponibles las abiertas.
- La fecha límite no debe haber vencido.
- Deben existir cupos.
- No puede existir otra inscripción vigente del jugador en la misma competencia.
- No puede inscribirse en competencias finalizadas, canceladas o en curso.

### 7.3. Consultar un cuadro de eliminación directa

**Rol habilitado:** Jugador con inscripción confirmada en la categoría.

**Objetivo:** Revisar participantes, emparejamientos, programación, resultados y avance.

### Pasos

1. Abrir una competencia asociada a una inscripción confirmada.
2. Entrar a la categoría.
3. Seleccionar la acción para ver el cuadro.
4. Recorrer las rondas y revisar cada partido.

### Resultado esperado

Se muestran los participantes confirmados, rondas, BYE, marcadores, programación y ganador final cuando exista.

### Validaciones o restricciones

- El Jugador solo puede recuperar el detalle de categorías en las que su inscripción está confirmada.
- La vista es de consulta; no presenta acciones administrativas.
- Los jugadores todavía no determinados aparecen como pendientes de definición.

### 7.4. Consultar una escalerilla y posiciones

**Rol habilitado:** Jugador con inscripción confirmada en la categoría.

**Objetivo:** Consultar partidos personales, resultados y tabla de posiciones.

### Pasos

1. Abrir una competencia de escalerilla asociada a una inscripción confirmada.
2. Entrar al detalle de la categoría.
3. Revisar la tabla de posiciones.
4. Revisar las secciones de próximos partidos y resultados.

### Resultado esperado

Se presenta la clasificación calculada y la actividad del jugador dentro de la categoría.

### Validaciones o restricciones

- La vista no permite generar enfrentamientos, programar ni registrar resultados.
- Solo se exponen participantes confirmados al rol Jugador.
- Las posiciones se calculan automáticamente desde resultados finalizados.

## 8. Consulta general de resultados y estados

Los estados de partido utilizados por la interfaz son:

- `PROGRAMADO`: creado y pendiente de inicio, con o sin fecha asignada;
- `EN_JUEGO`: tiene actividad registrada sin ganador definitivo;
- `FINALIZADO`: posee un ganador por resultado normal, Walk Over o Retiro;
- `CANCELADO`: no admite nuevos sets ni resoluciones deportivas.

Las resoluciones son:

- `NORMAL`: determinada a partir de sets completos;
- `WALKOVER`: ausencia de un participante, sin sets;
- `RETIREMENT`: retiro con o sin marcador registrado.

En eliminación directa, el ganador de un partido finalizado se copia automáticamente al espacio correspondiente del partido siguiente. Esta propagación no se utiliza en la escalerilla.

## 9. Restricciones transversales del MVP

- Las operaciones se autorizan nuevamente en el backend, aunque la interfaz oculte los botones.
- El Jugador consulta solo los datos deportivos permitidos por sus inscripciones.
- Las inscripciones canceladas no ocupan cupo.
- Un jugador requiere inscripción confirmada para participar en un cuadro, escalerilla o partido de esa categoría.
- Los resultados anteriores quedan protegidos cuando un partido dependiente de la ronda siguiente ya comenzó o contiene una resolución.
- Los partidos generados por un cuadro no se eliminan individualmente; se utiliza la eliminación completa del cuadro cuando todavía está permitida.
- El MVP no incluye una pantalla frontend independiente para administrar el catálogo maestro de categorías ni las canchas. Las categorías existentes se seleccionan al configurar una competencia y las canchas existentes al programar partidos.
- La interfaz registra auditoría backend para operaciones de creación, modificación y eliminación de varios recursos, pero no presenta una pantalla de consulta de auditoría.
