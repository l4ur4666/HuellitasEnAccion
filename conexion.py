import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="techstore_sena"
)

cursor = conexion.cursor()

consulta = "SELECT * FROM productos"

cursor.execute(consulta)

resultados = cursor.fetchall()

for fila in resultados:
    print(fila)

conexion.close()