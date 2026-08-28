import os
import mysql.connector

conexion = mysql.connector.connect(
    host=os.environ.get("MYSQLHOST", "localhost"),
    port=int(os.environ.get("MYSQLPORT", 3306)),
    user=os.environ.get("MYSQLUSER", "root"),
    password=os.environ.get("MYSQLPASSWORD", ""),
    database=os.environ.get("MYSQLDATABASE", "techstore_sena")
)

cursor = conexion.cursor()

consulta = "SELECT * FROM productos"

cursor.execute(consulta)

resultados = cursor.fetchall()

for fila in resultados:
    print(fila)

conexion.close()