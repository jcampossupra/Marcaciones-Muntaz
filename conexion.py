import psycopg2
from psycopg2 import sql

# Configuración de la conexión
conn = psycopg2.connect(
    host="192.168.1.49",
    port="5432",
    database="hikcentral",
    user="postgres",
    password="admin2"
)

cur = conn.cursor()
