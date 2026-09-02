from flask import Flask, request, render_template
from flask import session, redirect, url_for, flash

import mysql.connector
import bcrypt
import os
from datetime import datetime


app = Flask(__name__)


# ========================================
# 🔐 CONFIGURACIÓN DE SESIÓN
# ========================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "huellitas-clave-local-2026"
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

        usuario_encontrado = cursor.fetchone()

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
                hash_guardado.encode("utf-8")
            )

        password_bytes = password.encode(
            "utf-8"
        )

        contraseña_correcta = False

        try:

            if hash_guardado.startswith(b"$2"):

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
            usuario_encontrado["id_usuario"]
        )

        session["nombre"] = (
            usuario_encontrado["nombres"]
        )

        session["email"] = (
            usuario_encontrado["email"]
        )

        flash(
            "🐾 ¡Bienvenido/a a Huellitas En Acción! 💗",
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
            "🐾 Debes iniciar sesión primero.",
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

        usuario_id = session["usuario_id"]

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

        if not nombres or not apellidos or not email:

            return render_template(
                "actualizar_usuario.html",
                usuario={
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "email": email
                },
                error=(
                    "❌ Nombre, apellido y correo son obligatorios."
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

        correo_existente = cursor.fetchone()

        if correo_existente:

            return render_template(
                "actualizar_usuario.html",
                usuario={
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "email": email
                },
                error=(
                    "❌ Ese correo ya pertenece a otro usuario."
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
            "💗 ¡Usuario actualizado exitosamente! 🐾",
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
            "🐾 Debes iniciar sesión primero.",
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
                "❌ Debes confirmar que deseas eliminar tu cuenta."
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
            (session["usuario_id"],)
        )

        conexion.commit()

        session.clear()

        flash(
            "🐾 Tu cuenta fue eliminada correctamente.",
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
            "🐾 Debes iniciar sesión para agendar una cita.",
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
            INSERT INTO citas(
                id_usuario,
                fecha,
                hora,
                servicio,
                mascota,
                motivo
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                session["usuario_id"],
                fecha,
                hora,
                servicio,
                mascota,
                motivo
            )
        )

        conexion.commit()

        flash(
            "📅 ¡Tu cita fue agendada correctamente! 🐾💗",
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

@app.route("/politica-privacidad")
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
            "🐾 Debes iniciar sesión para dejar un comentario.",
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

    if calificacion < 1:
        calificacion = 1

    if calificacion > 5:
        calificacion = 5

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
            (session["usuario_id"],)
        )

        usuario = cursor.fetchone()

        if not usuario:

            flash(
                "❌ No se encontró tu usuario. 🐾",
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
            "💗 ¡Tu comentario fue publicado! 🐾",
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
            "❌ No se pudo guardar tu comentario. 🐾",
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
# 🚪 CERRAR SESIÓN
# ========================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "🐾 Has cerrado sesión correctamente. 💗",
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