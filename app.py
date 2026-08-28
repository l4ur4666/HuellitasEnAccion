from flask import Flask, request, render_template
import mysql.connector
import bcrypt

app = Flask(__name__)


# ========================================
# 🐾 CONEXIÓN A MYSQL
# ========================================

conexion = mysql.connector.connect(
    host="::1",
    user="root",
    password="",
    database="huellitas_sirs",
    port=3306,
    use_pure=True
)


# ========================================
# 🏠 PÁGINA PRINCIPAL
# ========================================

@app.route("/")
def inicio():
    return render_template("bienvenida_tienda.html")


# ========================================
# 🛒 CARRITO
# ========================================

@app.route("/carrito")
def carrito():
    return render_template("carrito.html")


# ========================================
# 🛍️ TIENDA
# ========================================

@app.route("/tienda")
def tienda():
    return render_template("index.html")


# ========================================
# 🔐 INICIO DE SESIÓN
# ========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form["usuario"]
    password = request.form["password"]

    cursor = conexion.cursor(
        dictionary=True,
        buffered=True
    )

    sql = """
    SELECT nombres, email, hash_password
    FROM usuario
    WHERE email = %s
    """

    cursor.execute(sql, (email,))

    usuario_encontrado = cursor.fetchone()

    cursor.close()

    # ========================================
    # ✅ USUARIO CORRECTO
    # ========================================

    if usuario_encontrado:

        hash_guardado = usuario_encontrado["hash_password"]

        try:
            if isinstance(hash_guardado, str):
                hash_guardado = hash_guardado.encode("utf-8")

            if bcrypt.checkpw(
                password.encode("utf-8"),
                hash_guardado
            ):
                return render_template(
                    "bienvenida.html",
                    nombre=usuario_encontrado["nombres"]
                )

        except (ValueError, TypeError):
            pass

    # ========================================
    # ❌ DATOS INCORRECTOS
    # ========================================

    return render_template(
        "login.html",
        error="❌ Correo o contraseña incorrectos. 🐾"
    )


# ========================================
# 📝 REGISTRO
# ========================================

@app.route("/registro", methods=["GET", "POST"])
def registrar():

    if request.method == "GET":
        return render_template("registro.html")

    # Recibir datos del formulario
    nombres = request.form["nombre"]
    apellidos = request.form["apellidos"]
    email = request.form["correo"]
    password = request.form["password"]

    # Crear hash seguro de la contraseña
    hash_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    cursor = conexion.cursor()

    # Insertar usuario en MySQL
    sql = """
    INSERT INTO usuario(
        nombres,
        apellidos,
        email,
        hash_password
    )
    VALUES (%s, %s, %s, %s)
    """

    valores = (
        nombres,
        apellidos,
        email,
        hash_password
    )

    cursor.execute(sql, valores)

    conexion.commit()

    cursor.close()

    return """
    <!DOCTYPE html>

    <html lang="es">

    <head>
        <meta charset="UTF-8">
        <title>Registro exitoso</title>

        <style>

            body {
                background: #ffdff1;
                font-family: Arial, sans-serif;
                text-align: center;
                padding-top: 120px;
            }

            .mensaje {
                background: white;
                width: 70%;
                max-width: 600px;
                margin: auto;
                padding: 40px;
                border-radius: 25px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            }

            h1 {
                color: #7ec8f8;
                font-size: 40px;
            }

            p {
                font-size: 22px;
            }

            a {
                display: inline-block;
                margin-top: 20px;
                padding: 15px 30px;
                background: #7ec8f8;
                color: white;
                text-decoration: none;
                border-radius: 15px;
                font-size: 18px;
            }

        </style>
    </head>

    <body>

        <div class="mensaje">

            <h1>🐾 ¡Registro exitoso! 💖</h1>

            <p>Tu cuenta fue creada correctamente. ✨</p>

            <a href="/login">
                🔐 Iniciar sesión
            </a>

        </div>

    </body>

    </html>
    """


# ========================================
# 🐾 EJECUTAR FLASK
# ========================================

if __name__ == "__main__":
    app.run(debug=True)