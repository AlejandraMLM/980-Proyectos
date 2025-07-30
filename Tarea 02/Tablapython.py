import psycopg2

conn = psycopg2.connect("dbname=postgres user=postgres password=koala host=localhost port=5432")
cursor = conn.cursor()

cursor.execute("INSERT INTO redes VALUES ('Daniela', 201554650);")
conn.commit()

cursor.execute("SELECT * FROM redes;")
for nombre, carnet in cursor.fetchall():
    print(f"Nombre: {nombre}, Carnet: {carnet}")

cursor.close()
conn.close()
