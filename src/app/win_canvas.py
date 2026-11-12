"""Sesión 7 de Emiliano. API pública, tres gráficas y guardado en CSV."""

import csv
from datetime import datetime
import math
from pathlib import Path
from queue import Empty, Queue
from tempfile import NamedTemporaryFile
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib import dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import requests


API_URL = "https://api.open-meteo.com/v1/forecast"
PARAMETROS = {
    "latitude": 21.12,
    "longitude": -101.68,
    "hourly": "temperature_2m",
    "past_hours": 48,
    "forecast_hours": 0,
    "timezone": "America/Mexico_City",
    "temperature_unit": "celsius",
}
FONDO = "#fcf8f0"
CAFE = "#765130"
TINTA = "#2c241e"
DORADO = "#c29f6c"
BORDE = "#ded0bc"


def fetch_data():
    """Consulta las últimas 48 horas disponibles de temperatura de León."""
    respuesta = requests.get(API_URL, params=PARAMETROS, timeout=15)
    respuesta.raise_for_status()
    datos = respuesta.json()["hourly"]
    horas = datos["time"]
    temperaturas = datos["temperature_2m"]
    if not horas or len(horas) != len(temperaturas):
        raise ValueError("La API devolvió una serie de datos incompleta.")

    # Validar las fechas y temperaturas antes de mostrarlas o guardarlas.
    for hora, temperatura in zip(horas, temperaturas):
        datetime.fromisoformat(hora)
        if isinstance(temperatura, bool) or not isinstance(temperatura, (int, float)):
            raise ValueError("La API devolvió una temperatura inválida.")
        if not math.isfinite(temperatura):
            raise ValueError("La API devolvió una temperatura fuera de rango.")
    return horas, temperaturas


def guardar_csv(ruta, horas, temperaturas):
    """Guarda la consulta completa y reemplaza el archivo al terminar."""
    ruta = Path(ruta)
    temporal = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=ruta.parent,
            prefix=".temperaturas_", suffix=".tmp", delete=False,
        ) as archivo:
            temporal = Path(archivo.name)
            escritor = csv.writer(archivo, lineterminator="\n")
            escritor.writerow(["fecha_hora", "temperatura_c"])
            escritor.writerows(zip(horas, temperaturas))
        temporal.replace(ruta)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)


def crear_graficas(horas, temperaturas):
    """Dibuja línea, barras y dispersión sobre la misma consulta horaria."""
    fechas = [datetime.fromisoformat(hora) for hora in horas]
    figura = Figure(figsize=(10, 8), dpi=90, layout="constrained", facecolor=FONDO)
    ejes = figura.subplots(3, 1)
    ejes[0].plot(fechas, temperaturas, color=CAFE, marker="D", markersize=3,
                 linewidth=1.7, label="Temperatura horaria")
    ejes[1].bar(fechas, temperaturas, width=0.033, color=DORADO, edgecolor=CAFE,
                linewidth=0.4, label="Temperatura por hora")
    ejes[2].scatter(fechas, temperaturas, color=CAFE, edgecolors=DORADO,
                    marker="o", s=34, alpha=0.8, label="Lecturas horarias")

    titulos = ["1. Línea · Evolución de la temperatura",
               "2. Barras · Comparación por hora",
               "3. Dispersión · Distribución de las lecturas"]
    for eje, titulo in zip(ejes, titulos):
        eje.set_facecolor(FONDO)
        eje.set_title(titulo, loc="left", color=TINTA, fontsize=12, pad=10)
        eje.set_xlabel("Fecha y hora local de León", color=TINTA)
        eje.set_ylabel("Temperatura (°C)", color=TINTA)
        eje.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
        eje.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
        eje.tick_params(axis="both", labelsize=9, colors=TINTA)
        eje.grid(axis="y", linestyle="--", alpha=0.35, color=CAFE)
        eje.set_axisbelow(True)
        for borde in eje.spines.values():
            borde.set_color(BORDE)
    return figura


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
    resultados = Queue()
    datos_actuales = None
    grafica = None
    figura = None
    tarea_pendiente = None

    def cerrar():
        if tarea_pendiente is not None:
            win.after_cancel(tarea_pendiente)
        if figura is not None:
            figura.clear()
        win.destroy()

    def guardar():
        if datos_actuales is None:
            return
        ruta = filedialog.asksaveasfilename(
            parent=win, title="Guardar la consulta de Emiliano",
            initialfile="temperaturas_emiliano.csv", defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
        )
        if not ruta:
            return
        try:
            guardar_csv(ruta, *datos_actuales)
        except OSError as error:
            messagebox.showerror("Error al guardar", str(error), parent=win)
            return
        estado.set(f"CSV guardado · {len(datos_actuales[0])} registros.")
        messagebox.showinfo("Consulta guardada", "Se guardaron las fechas y temperaturas en CSV.", parent=win)

    def recibir_resultado():
        nonlocal datos_actuales, grafica, figura, tarea_pendiente
        tarea_pendiente = None
        try:
            datos, error = resultados.get_nowait()
        except Empty:
            tarea_pendiente = win.after(100, recibir_resultado)
            return
        boton_cargar.configure(state="normal")
        if error:
            estado.set("No se pudo actualizar la consulta. Puedes volver a intentarlo.")
            boton_guardar.configure(state="normal" if datos_actuales else "disabled")
            messagebox.showerror("Error de conexión", error, parent=win)
            return

        nueva_figura = crear_graficas(*datos)
        if grafica is not None:
            grafica.get_tk_widget().destroy()
            figura.clear()
        figura = nueva_figura
        grafica = FigureCanvasTkAgg(figura, master=panel_graficas)
        grafica.draw()
        grafica.get_tk_widget().pack(fill="both", expand=True)
        datos_actuales = datos
        inicio = datetime.fromisoformat(datos[0][0]).strftime("%d/%m/%Y %H:%M")
        fin = datetime.fromisoformat(datos[0][-1]).strftime("%d/%m/%Y %H:%M")
        periodo.set(f"Periodo consultado · {inicio} a {fin} · Hora local de León")
        estado.set(f"Consulta correcta · {len(datos[0])} registros · Desplázate para ver las tres gráficas.")
        boton_guardar.configure(state="normal")
        visor.yview_moveto(0)

    def cargar():
        nonlocal tarea_pendiente
        boton_cargar.configure(state="disabled")
        boton_guardar.configure(state="disabled")
        estado.set("Consultando Open-Meteo…")

        def consultar():
            # La consulta corre fuera de Tkinter para mantener la ventana activa.
            try:
                resultados.put((fetch_data(), None))
            except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                resultados.put((None, f"No se pudieron obtener los datos. Revisa tu conexión.\n{error}"))

        Thread(target=consultar, daemon=True).start()
        tarea_pendiente = win.after(100, recibir_resultado)

    boton_cargar = ttk.Button(controles, text="Cargar y mostrar gráficas", command=cargar,
                              style="Emiliano.TButton")
    boton_cargar.pack(side="left", padx=(0, 8))
    boton_guardar = ttk.Button(controles, text="Guardar CSV", command=guardar,
                               state="disabled", style="Emiliano.TButton")
    boton_guardar.pack(side="left")
    ttk.Button(controles, text="Volver al menú", command=cerrar,
               style="Emiliano.TButton").pack(side="right")
    tk.Label(frm, textvariable=periodo, bg=FONDO, fg=TINTA).pack(anchor="w", pady=(12, 4))
    tk.Label(frm, textvariable=estado, bg=FONDO, fg=TINTA, wraplength=940).pack(anchor="w", pady=(0, 10))

    area = tk.Frame(frm, bg=FONDO)
    area.pack(fill="both", expand=True)
    visor = tk.Canvas(area, bg=FONDO, highlightthickness=1, highlightbackground=BORDE)
    desplazamiento = ttk.Scrollbar(area, orient="vertical", command=visor.yview)
    visor.configure(yscrollcommand=desplazamiento.set)
    desplazamiento.pack(side="right", fill="y")
    visor.pack(side="left", fill="both", expand=True)
    panel_graficas = tk.Frame(visor, bg=FONDO)
    ventana_interior = visor.create_window((0, 0), window=panel_graficas, anchor="nw")
    panel_graficas.bind("<Configure>", lambda event: visor.configure(scrollregion=visor.bbox("all")))
    visor.bind("<Configure>", lambda event: visor.itemconfigure(ventana_interior, width=event.width))
    win.bind("<MouseWheel>", lambda event: visor.yview_scroll(-1 if event.delta > 0 else 1, "units"))
    win.bind("<Next>", lambda event: visor.yview_scroll(1, "pages"))
    win.bind("<Prior>", lambda event: visor.yview_scroll(-1, "pages"))
    win.protocol("WM_DELETE_WINDOW", cerrar)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_win_canvas(root)
    ventana = root.winfo_children()[0]
    ventana.bind("<Destroy>", lambda event: root.destroy() if event.widget is ventana else None)
    root.mainloop()
