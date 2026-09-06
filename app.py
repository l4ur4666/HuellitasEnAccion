from flask import Flask, request, render_template
from flask import session, redirect, url_for, flash

import mysql.connector
import bcrypt
import os
import random
import smtplib
import ssl
import certifi

from email.message import EmailMessage
from datetime import datetime, timedelta


app = Flask(__name__)


# ========================================
# 🔐 CONFIGURACIÓN DE SESIÓN
# ========================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "huellitas-clave-local-2026"
)


# ========================================
# 📧 CONFIGURACIÓN PARA RECUPERAR CONTRASEÑA
# ========================================

CORREO_REMITENTE = os.environ.get(
    "CORREO_REMITENTE",
    ""
)

CLAVE_CORREO = os.environ.get(
    "CLAVE_CORREO",
    ""
)

SMTP_SERVIDOR = "smtp.gmail.com"
SMTP_PUERTO = 465


# ========================================
# 📧 ENVIAR CÓDIGO DE RECUPERACIÓN
# ========================================

def enviar_codigo_recuperacion(
    correo_destino,
    codigo
):

    mensaje = EmailMessage()

    mensaje["Subject"] = (
        "🐾 Código para recuperar tu contraseña"
    )

    mensaje["From"] = CORREO_REMITENTE
    mensaje["To"] = correo_destino

    mensaje.set_content(
        f"""
Hola 🐾

Recibimos una solicitud para recuperar la contraseña
de tu cuenta de Huellitas En Acción.

Tu código de verificación es:

{codigo}

Este código tiene una duración de 10 minutos.

No compartas este código con nadie.

Si tú no solicitaste este cambio, puedes ignorar este mensaje.

💗 Huellitas En Acción
        """
    )

    contexto = ssl._create_unverified_context()

    with smtplib.SMTP_SSL(
        SMTP_SERVIDOR,
        SMTP_PUERTO,
        context=contexto
    ) as servidor:

        servidor.login(
            CORREO_REMITENTE,
            CLAVE_CORREO
        )

        servidor.send_message(
            mensaje
        )


# ========================================
# 🐾 CONEXIÓN A MYSQL
# ========================================

def obtener_conexion():

    return mysql.connector.connect(
        host=os.environ.get(
            "MYSQLHOST",
            "::1"
        ),

        user=os.environ.get(
            "MYSQLUSER",
            "root"
        ),

        password=os.environ.get(
            "MYSQLPASSWORD",
            ""
        ),

        database=os.environ.get(
            "MYSQLDATABASE",
            "huellitas_sirs"
        ),

        port=int(
            os.environ.get(
                "MYSQLPORT",
                3306
            )
        ),

        use_pure=True
    )


# ========================================
# 🏠 PÁGINA DE BIENVENIDA
# ========================================

@app.route("/")
def inicio():

    return render_template(
        "bienvenida_tienda.html"
    )


# ========================================
# 🛍️ TIENDA
# ========================================

@app.route("/tienda")
def tienda():

    conexion = None
    cursor = None

    comentarios = []

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            """
            SELECT
                id_comentario,
                id_usuario,
                nombre,
                comentario,
                calificacion,
                creado_en
            FROM comentarios
            ORDER BY creado_en DESC
            """
        )

        comentarios = cursor.fetchall()

    except mysql.connector.Error as error:

        print(
            "ERROR AL CARGAR COMENTARIOS:",
            error
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()

    return render_template(
        "index.html",
        comentarios=comentarios
    )


# ========================================
# 🛒 CARRITO
# ========================================

@app.route("/carrito")
def carrito():

    return render_template(
        "carrito.html"
    )


# ========================================
# 🔐 INICIO DE SESIÓN
# ========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )

    email = request.form.get(
        "usuario",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    no_robot = request.form.get(
        "no_robot"
    )

    if not no_robot:

        return render_template(
            "login.html",
            error=(
                "❌ Debes confirmar que no eres un robot."
            )
        )

    if not email or not password:

        return render_template(
            "login.html",
            error=(
                "❌ Debes escribir tu correo y contraseña. 🐾"
            )
        )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            """
            SELECT
                id_usuario,
                nombres,
                apellidos,
                email,
                hash_password,
                activo
            FROM usuario
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        usuario_encontrado = (
            cursor.fetchone()
        )

        if not usuario_encontrado:

            return render_template(
                "login.html",
                error=(
                    "❌ Correo o contraseña incorrectos. 🐾"
                )
            )

        if usuario_encontrado["activo"] == 0:

            return render_template(
                "login.html",
                error=(
                    "❌ Esta cuenta está desactivada. 🐾"
                )
            )

        hash_guardado = (
            usuario_encontrado["hash_password"]
        )

        if isinstance(
            hash_guardado,
            memoryview
        ):

            hash_guardado = (
                hash_guardado.tobytes()
            )

        elif isinstance(
            hash_guardado,
            bytearray
        ):

            hash_guardado = bytes(
                hash_guardado
            )

        elif isinstance(
            hash_guardado,
            str
        ):

            hash_guardado = (
                hash_guardado.encode(
                    "utf-8"
                )
            )

        password_bytes = password.encode(
            "utf-8"
        )

        contraseña_correcta = False

        try:

            if hash_guardado.startswith(
                b"$2"
            ):

                contraseña_correcta = (
                    bcrypt.checkpw(
                        password_bytes,
                        hash_guardado
                    )
                )

            else:

                contraseña_correcta = (
                    hash_guardado.decode(
                        "utf-8"
                    ) == password
                )

        except (
            ValueError,
            TypeError,
            UnicodeDecodeError
        ):

            contraseña_correcta = False

        if not contraseña_correcta:

            return render_template(
                "login.html",
                error=(
                    "❌ Correo o contraseña incorrectos. 🐾"
                )
            )

        session["usuario_id"] = (
            usuario_encontrado[
                "id_usuario"
            ]
        )

        session["nombre"] = (
            usuario_encontrado[
                "nombres"
            ]
        )

        session["email"] = (
            usuario_encontrado[
                "email"
            ]
        )

        flash(
            " ¡Bienvenido/a a Huellitas En Acción! 💗",
            "exito"
        )

        return redirect(
            url_for("tienda")
        )

    except mysql.connector.Error as error:

        print(
            "ERROR DE MYSQL EN LOGIN:",
            error
        )

        return render_template(
            "login.html",
            error=(
                "❌ No se pudo conectar con la base de datos. 🐾"
            )
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()


# ========================================
# 📝 REGISTRO
# ========================================

@app.route(
    "/registro",
    methods=["GET", "POST"]
)
def registrar():

    if request.method == "GET":

        return render_template(
            "registro.html"
        )

    nombres = request.form.get(
        "nombre",
        ""
    ).strip()

    apellidos = request.form.get(
        "apellidos",
        ""
    ).strip()

    email = request.form.get(
        "correo",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    no_robot = request.form.get(
        "no_robot"
    )

    if not no_robot:

        return render_template(
            "registro.html",
            error=(
                "❌ Debes confirmar que no eres un robot."
            )
        )

    if (
        not nombres
        or not apellidos
        or not email
        or not password
    ):

        return render_template(
            "registro.html",
            error=(
                "❌ Todos los campos son obligatorios. 🐾"
            )
        )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuario
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        usuario_existente = (
            cursor.fetchone()
        )

        if usuario_existente:

            return render_template(
                "registro.html",
                error=(
                    "❌ Ese correo ya está registrado. 🐾"
                )
            )

        hash_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor.execute(
            """
            INSERT INTO usuario(
                nombres,
                apellidos,
                email,
                hash_password
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                nombres,
                apellidos,
                email,
                hash_password
            )
        )

        conexion.commit()

        return render_template(
            "login.html",
            mensaje=(
                "🐾 ¡Registro exitoso! "
                "Ya puedes iniciar sesión. 💖"
            )
        )

    except mysql.connector.IntegrityError:

        if conexion is not None:
            conexion.rollback()

        return render_template(
            "registro.html",
            error=(
                "❌ Ese correo ya está registrado. 🐾"
            )
        )

    except mysql.connector.Error as error:

        if conexion is not None:
            conexion.rollback()

        print(
            "ERROR DE MYSQL EN REGISTRO:",
            error
        )

        return render_template(
            "registro.html",
            error=(
                "❌ Ocurrió un error al guardar tu cuenta. 🐾"
            )
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()


# ========================================
# ✏️ ACTUALIZAR USUARIO
# ========================================

@app.route(
    "/actualizar-usuario",
    methods=["GET", "POST"]
)
def actualizar_usuario():

    if "usuario_id" not in session:

        flash(
            " Debes iniciar sesión primero.",
            "salida"
        )

        return redirect(
            url_for("login")
        )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor(
            dictionary=True,
            buffered=True
        )

        usuario_id = session[
            "usuario_id"
        ]

        if request.method == "GET":

            cursor.execute(
                """
                SELECT
                    id_usuario,
                    nombres,
                    apellidos,
                    email
                FROM usuario
                WHERE id_usuario = %s
                """,
                (usuario_id,)
            )

            usuario = cursor.fetchone()

            return render_template(
                "actualizar_usuario.html",
                usuario=usuario
            )

        nombres = request.form.get(
            "nombre",
            ""
        ).strip()

        apellidos = request.form.get(
            "apellidos",
            ""
        ).strip()

        email = request.form.get(
            "correo",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        no_robot = request.form.get(
            "no_robot"
        )

        if not no_robot:

            return render_template(
                "actualizar_usuario.html",
                usuario={
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "email": email
                },
                error=(
                    "❌ Debes confirmar que no eres un robot."
                )
            )

        if (
            not nombres
            or not apellidos
            or not email
        ):

            return render_template(
                "actualizar_usuario.html",
                usuario={
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "email": email
                },
                error=(
                    "❌ Nombre, apellido y correo "
                    "son obligatorios."
                )
            )

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuario
            WHERE email = %s
            AND id_usuario != %s
            LIMIT 1
            """,
            (
                email,
                usuario_id
            )
        )

        correo_existente = (
            cursor.fetchone()
        )

        if correo_existente:

            return render_template(
                "actualizar_usuario.html",
                usuario={
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "email": email
                },
                error=(
                    "❌ Ese correo ya pertenece "
                    "a otro usuario."
                )
            )

        if password:

            hash_password = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            )

            cursor.execute(
                """
                UPDATE usuario
                SET
                    nombres = %s,
                    apellidos = %s,
                    email = %s,
                    hash_password = %s
                WHERE id_usuario = %s
                """,
                (
                    nombres,
                    apellidos,
                    email,
                    hash_password,
                    usuario_id
                )
            )

        else:

            cursor.execute(
                """
                UPDATE usuario
                SET
                    nombres = %s,
                    apellidos = %s,
                    email = %s
                WHERE id_usuario = %s
                """,
                (
                    nombres,
                    apellidos,
                    email,
                    usuario_id
                )
            )

        conexion.commit()

        session["nombre"] = nombres
        session["email"] = email

        flash(
            "💗 ¡Usuario actualizado exitosamente! ",
            "exito"
        )

        return redirect(
            url_for("tienda")
        )

    except mysql.connector.Error as error:

        print(
            "ERROR AL ACTUALIZAR USUARIO:",
            error
        )

        flash(
            "❌ No se pudo actualizar el usuario.",
            "salida"
        )

        return redirect(
            url_for("tienda")
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()


# ========================================
# 🗑️ ELIMINAR USUARIO
# ========================================

@app.route(
    "/eliminar-usuario",
    methods=["GET", "POST"]
)
def eliminar_usuario():

    if "usuario_id" not in session:

        flash(
            " Debes iniciar sesión primero.",
            "salida"
        )

        return redirect(
            url_for("login")
        )

    if request.method == "GET":

        return render_template(
            "eliminar_usuario.html"
        )

    confirmar = request.form.get(
        "confirmar"
    )

    no_robot = request.form.get(
        "no_robot"
    )

    if not confirmar:

        return render_template(
            "eliminar_usuario.html",
            error=(
                "❌ Debes confirmar que deseas "
                "eliminar tu cuenta."
            )
        )

    if not no_robot:

        return render_template(
            "eliminar_usuario.html",
            error=(
                "❌ Debes confirmar que no eres un robot."
            )
        )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE usuario
            SET activo = 0
            WHERE id_usuario = %s
            """,
            (
                session["usuario_id"],
            )
        )

        conexion.commit()

        session.clear()

        flash(
            " Tu cuenta fue eliminada correctamente.",
            "salida"
        )

        return redirect(
            url_for("inicio")
        )

    except mysql.connector.Error as error:

        if conexion is not None:
            conexion.rollback()

        print(
            "ERROR AL ELIMINAR USUARIO:",
            error
        )

        return render_template(
            "eliminar_usuario.html",
            error=(
                "❌ No se pudo eliminar la cuenta."
            )
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()


# ========================================
# 📅 AGENDAMIENTO DE CITAS
# ========================================

@app.route(
    "/agendamiento",
    methods=["GET", "POST"]
)
def agendamiento():

    if "usuario_id" not in session:

        flash(
            " Debes iniciar sesión para agendar una cita.",
            "salida"
        )

        return redirect(
            url_for("login")
        )

    if request.method == "GET":

        return render_template(
            "agendamiento.html"
        )

    fecha = request.form.get(
        "fecha",
        ""
    )

    hora = request.form.get(
        "hora",
        ""
    )

    servicio = request.form.get(
        "servicio",
        ""
    ).strip()

    mascota = request.form.get(
        "mascota",
        ""
    ).strip()

    motivo = request.form.get(
        "motivo",
        ""
    ).strip()

    no_robot = request.form.get(
        "no_robot"
    )

    if not no_robot:

        return render_template(
            "agendamiento.html",
            error=(
                "❌ Debes confirmar que no eres un robot."
            )
        )

    if (
        not fecha
        or not hora
        or not servicio
        or not mascota
    ):

        return render_template(
            "agendamiento.html",
            error=(
                "❌ Debes completar los campos obligatorios."
            )
        )

    try:

        hora_seleccionada = datetime.strptime(
            hora,
            "%H:%M"
        ).time()

        if (
            hora_seleccionada.hour < 6
            or hora_seleccionada.hour >= 20
        ):

            return render_template(
                "agendamiento.html",
                error=(
                    "❌ El horario de atención "
                    "es de 6:00 AM hasta las 8:00 PM."
                )
            )

    except ValueError:

        return render_template(
            "agendamiento.html",
            error=(
                "❌ La hora seleccionada no es válida."
            )
        )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id_mascota
            FROM mascota
            WHERE id_usuario = %s
              AND nombre = %s
            LIMIT 1
            """,
            (
                session["usuario_id"],
                mascota
            )
        )

        mascota_encontrada = (
            cursor.fetchone()
        )

        if not mascota_encontrada:

            return render_template(
                "agendamiento.html",
                error=(
                    "❌ No se encontró una mascota "
                    "con ese nombre en tu cuenta. 🐾"
                )
            )

        id_mascota = (
            mascota_encontrada[0]
        )

        fecha_cita = (
            f"{fecha} {hora}:00"
        )

        cursor.execute(
            """
            INSERT INTO cita(
                id_usuario,
                id_mascota,
                motivo,
                fecha_cita,
                estado
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                session["usuario_id"],
                id_mascota,
                (
                    f"{servicio} - {motivo}"
                    if motivo
                    else servicio
                ),
                fecha_cita,
                "PROGRAMADA"
            )
        )

        conexion.commit()

        flash(
            "📅 ¡Tu cita fue agendada correctamente! 💗",
            "exito"
        )

        return redirect(
            url_for("agendamiento")
        )

    except mysql.connector.Error as error:

        if conexion is not None:
            conexion.rollback()

        print(
            "ERROR AL AGENDAR CITA:",
            error
        )

        return render_template(
            "agendamiento.html",
            error=(
                "❌ No se pudo guardar la cita."
            )
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()


# ========================================
# 📄 POLÍTICA Y PRIVACIDAD
# ========================================

@app.route(
    "/politica-privacidad"
)
def politica_privacidad():

    return render_template(
        "politica_privacidad.html"
    )


# ========================================
# 💬 AGREGAR COMENTARIO
# ========================================

@app.route(
    "/comentarios",
    methods=["POST"]
)
def agregar_comentario():

    if "usuario_id" not in session:

        flash(
            " Debes iniciar sesión para dejar un comentario.",
            "salida"
        )

        return redirect(
            url_for("login")
        )

    comentario = request.form.get(
        "comentario",
        ""
    ).strip()

    calificacion = request.form.get(
        "calificacion",
        "5"
    )

    if not comentario:

        flash(
            "❌ No puedes publicar un comentario vacío. 🐾",
            "salida"
        )

        return redirect(
            url_for("tienda")
        )

    try:

        calificacion = int(
            calificacion
        )

    except (
        ValueError,
        TypeError
    ):

        calificacion = 5

    calificacion = max(
        1,
        min(
            5,
            calificacion
        )
    )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT nombres
            FROM usuario
            WHERE id_usuario = %s
            LIMIT 1
            """,
            (
                session["usuario_id"],
            )
        )

        usuario = cursor.fetchone()

        if not usuario:

            flash(
                "❌ No se encontró tu usuario.",
                "salida"
            )

            return redirect(
                url_for("tienda")
            )

        nombre = usuario[0]

        cursor.execute(
            """
            INSERT INTO comentarios(
                id_usuario,
                nombre,
                comentario,
                calificacion
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                session["usuario_id"],
                nombre,
                comentario,
                calificacion
            )
        )

        conexion.commit()

        flash(
            "💗 ¡Tu comentario fue publicado!",
            "exito"
        )

    except mysql.connector.Error as error:

        if conexion is not None:
            conexion.rollback()

        print(
            "ERROR AL GUARDAR COMENTARIO:",
            error
        )

        flash(
            "❌ No se pudo guardar tu comentario.",
            "salida"
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()

    return redirect(
        url_for("tienda")
    )


# ========================================
# ✏️ EDITAR COMENTARIO
# ========================================

@app.route(
    "/editar-comentario/<int:id_comentario>",
    methods=["POST"]
)
def editar_comentario(
    id_comentario
):

    if "usuario_id" not in session:

        flash(
            "🐾 Debes iniciar sesión para editar un comentario.",
            "salida"
        )

        return redirect(
            url_for("login")
        )

    comentario = request.form.get(
        "comentario",
        ""
    ).strip()

    calificacion = request.form.get(
        "calificacion",
        "5"
    )

    if not comentario:

        flash(
            "❌ El comentario no puede estar vacío. 🐾",
            "salida"
        )

        return redirect(
            url_for("tienda")
        )

    try:

        calificacion = int(
            calificacion
        )

    except (
        ValueError,
        TypeError
    ):

        calificacion = 5

    calificacion = max(
        1,
        min(
            5,
            calificacion
        )
    )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE comentarios
            SET
                comentario = %s,
                calificacion = %s
            WHERE id_comentario = %s
              AND id_usuario = %s
            """,
            (
                comentario,
                calificacion,
                id_comentario,
                session["usuario_id"]
            )
        )

        conexion.commit()

        flash(
            "💗 ¡Tu comentario fue actualizado! 🐾",
            "exito"
        )

    except mysql.connector.Error as error:

        if conexion is not None:
            conexion.rollback()

        print(
            "ERROR AL EDITAR COMENTARIO:",
            error
        )

        flash(
            "❌ No se pudo actualizar el comentario.",
            "salida"
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()

    return redirect(
        url_for("tienda")
    )


# ========================================
# 🗑️ ELIMINAR COMENTARIO
# ========================================

@app.route(
    "/eliminar-comentario/<int:id_comentario>",
    methods=["POST"]
)
def eliminar_comentario(
    id_comentario
):

    if "usuario_id" not in session:

        flash(
            "🐾 Debes iniciar sesión para eliminar un comentario.",
            "salida"
        )

        return redirect(
            url_for("login")
        )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute(
            """
            DELETE FROM comentarios
            WHERE id_comentario = %s
              AND id_usuario = %s
            """,
            (
                id_comentario,
                session["usuario_id"]
            )
        )

        conexion.commit()

        flash(
            "🗑️ ¡Tu comentario fue eliminado! 🐾",
            "exito"
        )

    except mysql.connector.Error as error:

        if conexion is not None:
            conexion.rollback()

        print(
            "ERROR AL ELIMINAR COMENTARIO:",
            error
        )

        flash(
            "❌ No se pudo eliminar el comentario.",
            "salida"
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()

    return redirect(
        url_for("tienda")
    )


# ========================================
# 🔑 RECUPERAR CONTRASEÑA
# ========================================

@app.route(
    "/recuperar-contrasena",
    methods=["GET", "POST"]
)
def recuperar_contrasena():

    if request.method == "GET":

        return render_template(
            "recuperar_contrasena.html"
        )

    email = request.form.get(
        "correo",
        ""
    ).strip().lower()

    if not email:

        return render_template(
            "recuperar_contrasena.html",
            error=(
                "❌ Escribe tu correo electrónico. 🐾"
            )
        )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            """
            SELECT
                id_usuario,
                email,
                activo
            FROM usuario
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        usuario = cursor.fetchone()

        if not usuario:

            return render_template(
                "recuperar_contrasena.html",
                error=(
                    "❌ No encontramos una cuenta "
                    "con ese correo. 🐾"
                )
            )

        if usuario["activo"] == 0:

            return render_template(
                "recuperar_contrasena.html",
                error=(
                    "❌ Esta cuenta está desactivada. 🐾"
                )
            )

        codigo = str(
            random.randint(
                100000,
                999999
            )
        )

        session["recuperacion_usuario_id"] = (
            usuario["id_usuario"]
        )

        session["recuperacion_correo"] = (
            email
        )

        session["codigo_recuperacion"] = (
            codigo
        )

        session["codigo_recuperacion_expira"] = (
            (
                datetime.now()
                + timedelta(minutes=10)
            ).timestamp()
        )

        enviar_codigo_recuperacion(
            email,
            codigo
        )

        return render_template(
            "verificar_codigo.html",
            correo=email
        )

    except mysql.connector.Error as error:

        print(
            "ERROR DE MYSQL EN RECUPERACIÓN:",
            error
        )

        return render_template(
            "recuperar_contrasena.html",
            error=(
                "❌ No se pudo consultar la cuenta. 🐾"
            )
        )

    except Exception as error:

        print(
            "ERROR AL ENVIAR CÓDIGO:",
            error
        )

        return render_template(
            "recuperar_contrasena.html",
            error=(
                "❌ No se pudo enviar el código "
                "al correo. Revisa la configuración "
                "del correo. 🐾"
            )
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()


# ========================================
# ✅ VERIFICAR CÓDIGO
# ========================================

@app.route(
    "/verificar-codigo",
    methods=["GET", "POST"]
)
def verificar_codigo():

    if "codigo_recuperacion" not in session:

        return redirect(
            url_for("recuperar_contrasena")
        )

    if request.method == "GET":

        return render_template(
            "verificar_codigo.html",
            correo=session.get(
                "recuperacion_correo"
            )
        )

    codigo_ingresado = request.form.get(
        "codigo",
        ""
    ).strip()

    codigo_guardado = session.get(
        "codigo_recuperacion"
    )

    tiempo_expiracion = session.get(
        "codigo_recuperacion_expira"
    )

    if not codigo_ingresado:

        return render_template(
            "verificar_codigo.html",
            correo=session.get(
                "recuperacion_correo"
            ),
            error=(
                "❌ Escribe el código "
                "que recibiste. 🐾"
            )
        )

    if (
        not tiempo_expiracion
        or datetime.now().timestamp()
        > tiempo_expiracion
    ):

        session.pop(
            "codigo_recuperacion",
            None
        )

        session.pop(
            "codigo_recuperacion_expira",
            None
        )

        return render_template(
            "recuperar_contrasena.html",
            error=(
                "❌ El código expiró. "
                "Solicita uno nuevo. 🐾"
            )
        )

    if codigo_ingresado != codigo_guardado:

        return render_template(
            "verificar_codigo.html",
            correo=session.get(
                "recuperacion_correo"
            ),
            error=(
                "❌ El código es incorrecto. 🐾"
            )
        )

    session["codigo_verificado"] = True

    session.pop(
        "codigo_recuperacion",
        None
    )

    session.pop(
        "codigo_recuperacion_expira",
        None
    )

    return render_template(
        "nueva_contrasena.html"
    )


# ========================================
# 🔒 NUEVA CONTRASEÑA
# ========================================

@app.route(
    "/nueva-contrasena",
    methods=["GET", "POST"]
)
def nueva_contrasena():

    if not session.get(
        "codigo_verificado"
    ):

        return redirect(
            url_for("recuperar_contrasena")
        )

    if request.method == "GET":

        return render_template(
            "nueva_contrasena.html"
        )

    password = request.form.get(
        "password",
        ""
    )

    confirmar_password = request.form.get(
        "confirmar_password",
        ""
    )

    if not password or not confirmar_password:

        return render_template(
            "nueva_contrasena.html",
            error=(
                "❌ Debes completar los dos campos."
            )
        )

    if password != confirmar_password:

        return render_template(
            "nueva_contrasena.html",
            error=(
                "❌ Las contraseñas no coinciden."
            )
        )

    if len(password) < 6:

        return render_template(
            "nueva_contrasena.html",
            error=(
                "❌ La contraseña debe tener "
                "al menos 6 caracteres."
            )
        )

    usuario_id = session.get(
        "recuperacion_usuario_id"
    )

    if not usuario_id:

        session.clear()

        return redirect(
            url_for("login")
        )

    hash_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()

        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE usuario
            SET hash_password = %s
            WHERE id_usuario = %s
            """,
            (
                hash_password,
                usuario_id
            )
        )

        conexion.commit()

        session.clear()

        return render_template(
            "login.html",
            mensaje=(
                "🐾 ¡Contraseña cambiada correctamente! "
                "Ya puedes iniciar sesión. 💗"
            )
        )

    except mysql.connector.Error as error:

        if conexion is not None:
            conexion.rollback()

        print(
            "ERROR AL CAMBIAR CONTRASEÑA:",
            error
        )

        return render_template(
            "nueva_contrasena.html",
            error=(
                "❌ No se pudo cambiar la contraseña."
            )
        )

    finally:

        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):

            conexion.close()


# ========================================
# 🚪 CERRAR SESIÓN
# ========================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Has cerrado sesión correctamente. 💗",
        "salida"
    )

    return redirect(
        url_for("inicio")
    )


# ========================================
# 🐾 EJECUTAR FLASK
# ========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )