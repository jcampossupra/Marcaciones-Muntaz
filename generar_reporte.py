import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from fpdf import FPDF
from main import search_employee_data_mumtaz_milagro, search_employee_data_mumtaz_guayaquil, search_employee_data_milagro_nuevo
import webbrowser


def time_to_decimal(t):
    if t is None:
        return None
    return t.hour + t.minute / 60 + t.second / 3600


def mostrar_reporte():
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()
    selected_source = source_combobox.get()  # Obtener la fuente seleccionada

    # Limpiar la tabla antes de insertar nuevos datos
    for row in tree.get_children():
        tree.delete(row)

    if selected_source == "MUMTAZ MILAGRO":
        data = search_employee_data_mumtaz_milagro(start_date, end_date)
        for row in data:
            horas_trabajadas = round(row['horas_trabajadas'], 2) if row['horas_trabajadas'] is not None else None
            horas_almuerzo = round(row['horas_almuerzo'], 2) if row['horas_almuerzo'] is not None else None

            tree.insert("", "end", values=(
                row['nombre'], row['fecha'], row['entrada'],
                row['salida_almuerzo'], row['entrada_almuerzo'],
                row['salida'], horas_trabajadas, horas_almuerzo
            ))

    elif selected_source == "MUMTAZ GUAYAQUIL" or selected_source == "MILAGRO NUEVO":
        if selected_source == "MUMTAZ GUAYAQUIL":
            data = search_employee_data_mumtaz_guayaquil(start_date, end_date)
        else:
            data = search_employee_data_milagro_nuevo(start_date, end_date)

        for row in data:
            horas_trabajadas = round(time_to_decimal(row['horas_trabajadas']), 2) if row['horas_trabajadas'] is not None else None

            tree.insert("", "end", values=(
                row['nombre'],                       # Nombre correcto
                row['fecha'],                        # Fecha correcta
                row['hora_entrada'],                 # Entrada
                '',                                  # Salida Almuerzo vacío
                '',                                  # Entrada Almuerzo vacío
                row['hora_salida'],                  # Salida (colocar valor de Salida Almuerzo)
                horas_trabajadas,                    # Horas Trabajadas (conversión a decimal)
                ''                                   # Horas Almuerzo vacío
            ))


def exportar_pdf():
    pdf_file = "reporte_marcaciones.pdf"
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Agregar título
    pdf.cell(0, 10, txt="REPORTE DE MARCACIONES", ln=True, align='C', border=0)
    pdf.ln(5)

    # Obtener fechas seleccionadas
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()
    source = source_combobox.get()  # Obtener la fuente seleccionada

    # Agregar fechas y fuente al PDF
    pdf.cell(0, 10, txt=f"Fuente: {source}", ln=False, align='L', border=1)
    pdf.cell(0, 10, txt=f"Desde: {start_date}    Hasta: {end_date}", ln=True, align='R', border=1)
    pdf.ln(5)

    # Agregar encabezados de la tabla
    if source == "MUMTAZ MILAGRO":
        columns = ["Nombre", "Fecha", "Entrada", "Salida Almuerzo", "Entrada Almuerzo", "Salida", "Horas Trabajadas", "Horas Almuerzo"]
        widths = [50, 26, 35, 35, 35, 30, 40, 35]
    else:
        columns = ["Nombre", "Fecha", "Hora Entrada", "Hora Salida", "Horas Trabajadas"]
        widths = [70, 45, 55, 55, 52]

    pdf.set_fill_color(200, 220, 255)

    # Agregar encabezados con los anchos correspondientes
    for col, width in zip(columns, widths):
        pdf.cell(width, 10, col, 1, 0, 'C', fill=True)
    pdf.ln()

    # Obtener los datos de la tabla y agregarlos al PDF
    for row in tree.get_children():
        values = tree.item(row)["values"]

        if source in ["MUMTAZ GUAYAQUIL", "MILAGRO NUEVO"]:
            nombre = values[0]
            fecha = values[1]
            hora_entrada = values[2]
            hora_salida = values[5]
            horas_trabajadas = values[6]

            pdf.cell(widths[0], 10, str(nombre), 1, 0, 'C')
            pdf.cell(widths[1], 10, str(fecha), 1, 0, 'C')
            pdf.cell(widths[2], 10, str(hora_entrada), 1, 0, 'C')
            pdf.cell(widths[3], 10, str(hora_salida), 1, 0, 'C')
            pdf.cell(widths[4], 10, str(horas_trabajadas), 1, 0, 'C')
            pdf.ln()

        elif source == "MUMTAZ MILAGRO":
            for value, width in zip(values, widths):
                pdf.cell(width, 10, str(value), 1, 0, 'C')
            pdf.ln()

    pdf.output(pdf_file)
    webbrowser.open_new(pdf_file)

    messagebox.showinfo("Exportar PDF", "El reporte se ha exportado como 'reporte_marcaciones.pdf' y se ha abierto en el navegador.")


# Crear la ventana principal
root = tk.Tk()
root.title("Reporte de Marcaciones")
root.geometry("800x600")
root.resizable(True, True)

# Selector de fuente de datos
tk.Label(root, text="Seleccionar Fuente:").grid(row=0, column=0, padx=5, pady=10)
source_combobox = ttk.Combobox(root, values=["MUMTAZ MILAGRO", "MUMTAZ GUAYAQUIL", "MILAGRO NUEVO"], state="readonly")
source_combobox.grid(row=0, column=1, padx=5, pady=10)
source_combobox.current(0)

# Crear entradas para fechas con el selector de calendario
tk.Label(root, text="Fecha Inicio:").grid(row=1, column=0, padx=5, pady=10)
start_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
start_date_entry.grid(row=1, column=1, padx=5, pady=10)

tk.Label(root, text="Fecha Fin:").grid(row=2, column=0, padx=5, pady=10)
end_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
end_date_entry.grid(row=2, column=1, padx=5, pady=10)

# Botones para mostrar y exportar reporte
tk.Button(root, text="Mostrar Reporte", command=mostrar_reporte).grid(row=3, column=0, padx=5, pady=10)
tk.Button(root, text="Exportar a PDF", command=exportar_pdf).grid(row=3, column=1, padx=5, pady=10)

# Crear tabla para mostrar datos
tree = ttk.Treeview(root, columns=("Nombre", "Fecha", "Entrada", "Salida Almuerzo", "Entrada Almuerzo", "Salida", "Horas Trabajadas", "Horas Almuerzo"), show="headings")
tree.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

# Configuración de encabezados
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

root.mainloop()
