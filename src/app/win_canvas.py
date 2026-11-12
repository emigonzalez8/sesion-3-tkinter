import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import requests
from matplotlib import dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

FONDO = "#fcf8f0"
CAFE = "#765130"
TINTA = "#2c241e"
DORADO = "#c29f6c"
BORDE = "#ded0bc"


# 1. Pedir a la API las temperaturas de las últimas 48 horas de León.
def fetch_data():
    url = "https://api.open-meteo.com/v1/forecast"
    parametros = {
        "latitude": 21.12,
        "longitude": -101.68,
        "hourly": "temperature_2m",
        "past_hours": 48,
        "forecast_hours": 0,
        "timezone": "America/Mexico_City",
        "temperature_unit": "celsius",
    }
    respuesta = requests.get(url, params=parametros, timeout=15)
    respuesta.raise_for_status()
    datos = respuesta.json()["hourly"]
    horas = datos["time"]
    temperaturas = []
    for valor in datos["temperature_2m"]:
        temperaturas.append(float(valor))
    if not horas or len(horas) != len(temperaturas):
        raise ValueError("La API devolvió datos incompletos.")
    for hora in horas:
        datetime.fromisoformat(hora)
    return horas, temperaturas


# 2. Guardar las fechas y temperaturas en un archivo CSV.
def guardar_csv(ruta, horas, temperaturas):
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(["fecha_hora", "temperatura_c"])
        for i in range(len(horas)):
            escritor.writerow([horas[i], temperaturas[i]])


# 3. Dibujar tres gráficas con los mismos datos.
def crear_graficas(figura, horas, temperaturas):
    fechas = []
    for hora in horas:
        fechas.append(datetime.fromisoformat(hora))
    figura.clear()
    ejes = figura.subplots(3, 1)
    ejes[0].plot(fechas, temperaturas, color=CAFE, marker="D", markersize=3, linewidth=1.7)
    ejes[1].bar(fechas, temperaturas, width=0.033, color=DORADO, edgecolor=CAFE, linewidth=0.4)
    ejes[2].scatter(fechas, temperaturas, color=CAFE, edgecolors=DORADO, s=34, alpha=0.8)
    titulos = ["1. Línea · Evolución de la temperatura",
               "2. Barras · Comparación por hora",
               "3. Dispersión · Distribución de las lecturas"]
    for i in range(3):
        eje = ejes[i]
        eje.set_facecolor(FONDO)
        eje.set_title(titulos[i], loc="left", color=TINTA, fontsize=12, pad=10)
        eje.set_xlabel("Fecha y hora local de León", color=TINTA)
        eje.set_ylabel("Temperatura (°C)", color=TINTA)
        eje.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
        eje.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
        eje.tick_params(axis="both", labelsize=9, colors=TINTA)
        eje.grid(axis="y", linestyle="--", alpha=0.35, color=CAFE)
        eje.set_axisbelow(True)
        for borde in eje.spines.values():
            borde.set_color(BORDE)


# 4. Crear la subventana, igual que en el programa base del profesor.
def open_win_canvas(parent: tk.Tk):
    win = tk.Toplevel(parent)
    win.title("Tkinter · API y gráficas · Emiliano Gonzalez")
    win.geometry("1040x820")
    win.minsize(820, 620)
    win.configure(bg=FONDO)
    estilo = ttk.Style(win)
    estilo.configure("Emiliano.TButton", padding=(10, 0))
    frm = tk.Frame(win, padx=18, pady=18, bg=FONDO)
    frm.pack(fill="both", expand=True)
    tk.Label(frm, text="API pública y gráficas", bg=FONDO, fg=TINTA,
             font=("Arial", 21, "bold")).pack(anchor="w")
    tk.Label(frm, text="Sesión 7 · Emiliano Gonzalez · León, Guanajuato",
             bg=FONDO, fg=TINTA, font=("Arial", 11)).pack(anchor="w", pady=(4, 8))
    tk.Label(frm, text="Open-Meteo · Temperatura horaria · Consulta de 48 horas",
             bg=FONDO, fg=TINTA).pack(anchor="w", pady=(0, 12))
    controles = tk.Frame(frm, bg=FONDO)
    controles.pack(fill="x")
    estado = tk.StringVar(value="Presiona Cargar y mostrar gráficas para consultar la API.")
    periodo = tk.StringVar(value="Los datos se mostrarán con la hora local de León.")
    horas = []
    temperaturas = []

    def cargar():
        estado.set("Consultando Open-Meteo…")
        win.update_idletasks()
        try:
            nuevas_horas, nuevas_temperaturas = fetch_data()
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            estado.set("No se pudo actualizar la consulta. Puedes volver a intentarlo.")
            messagebox.showerror("Error de conexión", str(error), parent=win)
            return
        horas.clear()
        horas.extend(nuevas_horas)
        temperaturas.clear()
        temperaturas.extend(nuevas_temperaturas)
        crear_graficas(figura, horas, temperaturas)
        grafica.draw()
        inicio = datetime.fromisoformat(horas[0]).strftime("%d/%m/%Y %H:%M")
        fin = datetime.fromisoformat(horas[-1]).strftime("%d/%m/%Y %H:%M")
        periodo.set(f"Periodo consultado · {inicio} a {fin} · Hora local de León")
        estado.set(f"Consulta correcta · {len(horas)} registros · Desplázate para ver las tres gráficas.")
        boton_guardar.configure(state="normal")
        visor.yview_moveto(0)

    def guardar():
        ruta = filedialog.asksaveasfilename(
            parent=win, title="Guardar la consulta de Emiliano",
            initialfile="temperaturas_emiliano.csv", defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")])
        if ruta:
            try:
                guardar_csv(ruta, horas, temperaturas)
            except OSError as error:
                messagebox.showerror("Error al guardar", str(error), parent=win)
                return
            estado.set(f"CSV guardado · {len(horas)} registros.")
            messagebox.showinfo("Consulta guardada", "Se guardaron las fechas y temperaturas en CSV.", parent=win)

    def cerrar():
        figura.clear()
        win.destroy()

    ttk.Button(controles, text="Cargar y mostrar gráficas", command=cargar,
               style="Emiliano.TButton").pack(side="left", padx=(0, 8))
    boton_guardar = ttk.Button(controles, text="Guardar CSV", command=guardar,
                               state="disabled", style="Emiliano.TButton")
    boton_guardar.pack(side="left")
    ttk.Button(controles, text="Volver al menú", command=cerrar,
               style="Emiliano.TButton").pack(side="right")
    tk.Label(frm, textvariable=periodo, bg=FONDO, fg=TINTA).pack(anchor="w", pady=(12, 4))
    tk.Label(frm, textvariable=estado, bg=FONDO, fg=TINTA, wraplength=940).pack(anchor="w", pady=(0, 10))

    # El Canvas permite desplazar las gráficas hacia abajo y hacia arriba.
    area = tk.Frame(frm, bg=FONDO)
    area.pack(fill="both", expand=True)
    visor = tk.Canvas(area, bg=FONDO, highlightthickness=1, highlightbackground=BORDE)
    desplazamiento = ttk.Scrollbar(area, orient="vertical", command=visor.yview)
    visor.configure(yscrollcommand=desplazamiento.set)
    desplazamiento.pack(side="right", fill="y")
    visor.pack(side="left", fill="both", expand=True)
    panel = tk.Frame(visor, bg=FONDO)
    ventana_interior = visor.create_window((0, 0), window=panel, anchor="nw")
    panel.bind("<Configure>", lambda event: visor.configure(scrollregion=visor.bbox("all")))
    visor.bind("<Configure>", lambda event: visor.itemconfigure(ventana_interior, width=event.width))
    win.bind("<MouseWheel>", lambda event: visor.yview_scroll(-1 if event.delta > 0 else 1, "units"))
    win.bind("<Next>", lambda event: visor.yview_scroll(1, "pages"))
    win.bind("<Prior>", lambda event: visor.yview_scroll(-1, "pages"))

    figura = Figure(figsize=(10, 8), dpi=90, layout="constrained", facecolor=FONDO)
    grafica = FigureCanvasTkAgg(figura, master=panel)
    grafica.get_tk_widget().pack(fill="both", expand=True)
    win.protocol("WM_DELETE_WINDOW", cerrar)
