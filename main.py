from psycopg2.extras import DictCursor
from conexion import conn
from datetime import datetime, timedelta, time
import psycopg2
import tkinter as tk
from tkinter import ttk

def subtract_hours(start_time, end_time):
    if isinstance(start_time, time) and isinstance(end_time, time):
        start_time = datetime.combine(datetime.today(), start_time)
        end_time = datetime.combine(datetime.today(), end_time)
        delta = end_time - start_time
        total_hours = delta.total_seconds() / 3600
        return total_hours
    else:
        raise ValueError("Las horas deben ser del tipo datetime.time")

def search_employee_data_mumtaz_milagro(start_date, end_date):
    conn = psycopg2.connect(
        host="192.168.1.20",
        port="5432",
        database="SVP_SUPRALIVE",
        user="postgres",
        password="admin"
    )
    
    query = """
    SELECT em.cedula, em.nombres, em.apellido_paterno as apellido, m.fecha,
        (SELECT hora FROM rrhh.rh_marcaciones rm 
         JOIN rrhh.rh_fichas_empleados em2 ON em2.id = rm.empleado_id 
         JOIN rrhh.rh_tipo_marcaciones tm2 ON rm.id_tipo_marcacion = tm2.id  
         WHERE em2.cedula = em.cedula AND rm.fecha = m.fecha AND tm2.id = 1  
         ORDER BY rm.id DESC LIMIT 1) AS entrada,
        (SELECT hora FROM rrhh.rh_marcaciones rm 
         JOIN rrhh.rh_fichas_empleados em2 ON em2.id = rm.empleado_id 
         JOIN rrhh.rh_tipo_marcaciones tm2 ON rm.id_tipo_marcacion = tm2.id  
         WHERE em2.cedula = em.cedula AND rm.fecha = m.fecha AND tm2.id = 2  
         ORDER BY rm.id DESC LIMIT 1) AS salida_almuerzo,
        (SELECT hora FROM rrhh.rh_marcaciones rm 
         JOIN rrhh.rh_fichas_empleados em2 ON em2.id = rm.empleado_id 
         JOIN rrhh.rh_tipo_marcaciones tm2 ON rm.id_tipo_marcacion = tm2.id  
         WHERE em2.cedula = em.cedula AND rm.fecha = m.fecha AND tm2.id = 3 
         ORDER BY rm.id DESC LIMIT 1) AS entrada_almuerzo,
        (SELECT hora FROM rrhh.rh_marcaciones rm 
         JOIN rrhh.rh_fichas_empleados em2 ON em2.id = rm.empleado_id 
         JOIN rrhh.rh_tipo_marcaciones tm2 ON rm.id_tipo_marcacion = tm2.id  
         WHERE em2.cedula = em.cedula AND rm.fecha = m.fecha AND tm2.id = 4  
         ORDER BY rm.id DESC LIMIT 1) AS salida
    FROM rrhh.rh_marcaciones m
    JOIN rrhh.rh_fichas_empleados em ON em.id = m.empleado_id 
    JOIN rrhh.rh_tipo_marcaciones tm ON m.id_tipo_marcacion = tm.id 
    WHERE m.fecha BETWEEN %s AND %s
    GROUP BY em.cedula, nombres, apellido_paterno, fecha
    ORDER BY fecha, nombres
    """
    
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (start_date, end_date))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    report_data = []
    for row in rows:
        entrada = row['entrada']
        salida_almuerzo = row['salida_almuerzo']
        entrada_almuerzo = row['entrada_almuerzo']
        salida = row['salida']

        horas_trabajadas = subtract_hours(entrada, salida) if entrada and salida else None
        horas_almuerzo = subtract_hours(salida_almuerzo, entrada_almuerzo) if salida_almuerzo and entrada_almuerzo else None

        report_data.append({
            'nombre': f"{row['nombres']} {row['apellido']}",
            'fecha': row['fecha'],
            'entrada': entrada,
            'salida_almuerzo': salida_almuerzo,
            'entrada_almuerzo': entrada_almuerzo,
            'salida': salida,
            'horas_trabajadas': horas_trabajadas,
            'horas_almuerzo': horas_almuerzo,
        })

    return report_data

def search_employee_data_mumtaz_guayaquil(start_date, end_date):
    conn = psycopg2.connect(
        host="192.168.1.49",
        port="5432",
        database="hikcentral",
        user="postgres",
        password="admin2"
    )

    query = """
    SELECT 
        person_name,
        DATE(fecha_hora) AS fecha,
        COALESCE(MIN(CASE WHEN hora < '12:00:00' THEN hora::TIME END), '00:00:00'::TIME) AS hora_entrada,
        COALESCE(MAX(CASE WHEN hora >= '12:00:00' THEN hora::TIME END), '00:00:00'::TIME) AS hora_salida,
        CASE 
            WHEN COALESCE(MIN(CASE WHEN hora < '12:00:00' THEN hora::TIME END), '00:00:00'::TIME) = '00:00:00'::TIME OR
                 COALESCE(MAX(CASE WHEN hora >= '12:00:00' THEN hora::TIME END), '00:00:00'::TIME) = '00:00:00'::TIME 
            THEN '00:00:00'::TIME
            ELSE 
                ( 
                    (DATE(fecha_hora)::DATE + COALESCE(MAX(CASE WHEN hora >= '12:00:00' THEN hora::TIME END), '00:00:00'::TIME))::TIMESTAMP 
                    - 
                    (DATE(fecha_hora)::DATE + COALESCE(MIN(CASE WHEN hora < '12:00:00' THEN hora::TIME END), '00:00:00'::TIME))::TIMESTAMP 
                )::TIME
        END AS horas_trabajadas
    FROM 
        supralive.registros r
    WHERE 
        device_serial = 'E94634941'
        AND DATE(fecha_hora) BETWEEN %s AND %s
    GROUP BY 
        person_name, DATE(fecha_hora);
    """

    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (start_date, end_date))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    report_data = []
    for row in rows:
        report_data.append({
            'nombre': row['person_name'],
            'fecha': row['fecha'],
            'hora_entrada': row['hora_entrada'],
            'hora_salida': row['hora_salida'],
            'horas_trabajadas': row['horas_trabajadas'],
        })

    return report_data
def search_employee_data_milagro_nuevo(start_date, end_date):
    conn = psycopg2.connect(
        host="192.168.1.49",
        port="5432",
        database="hikcentral",
        user="postgres",
        password="admin2"
    )

    query = """
    SELECT 
        person_name,
        DATE(fecha_hora) AS fecha,
        COALESCE(MIN(CASE WHEN hora < '12:00:00' THEN hora::TIME END), '00:00:00'::TIME) AS hora_entrada,
        COALESCE(MAX(CASE WHEN hora >= '12:00:00' THEN hora::TIME END), '00:00:00'::TIME) AS hora_salida,
        CASE 
            WHEN COALESCE(MIN(CASE WHEN hora < '12:00:00' THEN hora::TIME END), '00:00:00'::TIME) = '00:00:00'::TIME OR
                 COALESCE(MAX(CASE WHEN hora >= '12:00:00' THEN hora::TIME END), '00:00:00'::TIME) = '00:00:00'::TIME 
            THEN '00:00:00'::TIME
            ELSE 
                ( 
                    (DATE(fecha_hora)::DATE + COALESCE(MAX(CASE WHEN hora >= '12:00:00' THEN hora::TIME END), '00:00:00'::TIME))::TIMESTAMP 
                    - 
                    (DATE(fecha_hora)::DATE + COALESCE(MIN(CASE WHEN hora < '12:00:00' THEN hora::TIME END), '00:00:00'::TIME))::TIMESTAMP 
                )::TIME
        END AS horas_trabajadas
    FROM 
        supralive.registros r
    WHERE 
        device_serial = 'E94634932'
        AND DATE(fecha_hora) BETWEEN %s AND %s
    GROUP BY 
        person_name, DATE(fecha_hora);
    """

    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(query, (start_date, end_date))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    report_data = []
    for row in rows:
        report_data.append({
            'nombre': row['person_name'],
            'fecha': row['fecha'],
            'hora_entrada': row['hora_entrada'],
            'hora_salida': row['hora_salida'],
            'horas_trabajadas': row['horas_trabajadas'],
        })

    return report_data



