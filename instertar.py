import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="techstore_sena"
)

cursor = conexion.cursor()

sql = """
INSERT INTO clientes(nombre, correo, ciudad)
VALUES (%s, %s, %s)
"""

datos = ("Pedro Sánchez", "pedro@gmail.com", "Bogotá")

cursor.execute(sql, datos)

conexion.commit()

print("Cliente insertado correctamente")

conexion.close()