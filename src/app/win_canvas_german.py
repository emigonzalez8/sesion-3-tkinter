import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import requests
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------------------------------------------
# Configuración: ciudad y rango de consulta (distintos a la v1)
# ---------------------------------------------------------------
CIUDAD = "Ciudad de México"
LATITUD = 19.43
LONGITUD = -99.13
DIAS_PASADOS = 3      # v1 usaba 1 día
DIAS_FUTUROS = 2      # v1 no incluía pronóstico

# Paleta oscura para el nuevo diseño
BG = "#1e1f2b"
PANEL = "#2a2c3d"
FG = "#e8e8f0"
ACCENT = "#ff7a59"


def fetch_data():
    """
    Consulta Open-Meteo: temperatura, humedad relativa y viento (horario)
    para los últimos DIAS_PASADOS y los próximos DIAS_FUTUROS.
    Devuelve (horas, temperaturas, humedad, viento) o listas vacías si falla.
    """
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={LATITUD}&longitude={LONGITUD}"
            "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
            f"&past_days={DIAS_PASADOS}&forecast_days={DIAS_FUTUROS}"
            "&timezone=auto"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        h = r.json()["hourly"]
        horas = [datetime.fromisoformat(t) for t in h["time"]]
        return horas, h["temperature_2m"], h["relative_humidity_2m"], h["wind_speed_10m"]
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron obtener los datos:\n{e}")
        return [], [], [], []


def _estilo(fig, ax, titulo, ylabel):
    """Aplica el estilo oscuro común a todas las gráficas."""
    fig.patch.set_facecolor(PANEL)
    ax.set_facecolor(BG)
    ax.set_title(titulo, color=FG, fontsize=12, fontweight="bold")
    ax.set_xlabel("Fecha y hora", color=FG)
    ax.set_ylabel(ylabel, color=FG)
    ax.tick_params(colors=FG)
    for borde in ax.spines.values():
        borde.set_color("#555770")
    ax.grid(True, linestyle="--", alpha=0.35, color="#8a8da8")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    fig.tight_layout()


def grafica_temperatura(horas, temps):
    """Línea gruesa con marcadores cuadrados, área sombreada y máx/mín."""
    fig = Figure(figsize=(8, 4.2))
    ax = fig.add_subplot(111)
    ax.plot(horas, temps, color=ACCENT, linewidth=2.2, marker="s",
            markersize=3, alpha=0.95)
    ax.fill_between(horas, temps, min(temps), color=ACCENT, alpha=0.18)
    i_max, i_min = temps.index(max(temps)), temps.index(min(temps))
    ax.scatter([horas[i_max]], [temps[i_max]], color="#ffd166", s=70, zorder=5,
               label=f"Máx {temps[i_max]} °C")
    ax.scatter([horas[i_min]], [temps[i_min]], color="#4cc9f0", s=70, zorder=5,
               label=f"Mín {temps[i_min]} °C")
    ax.axhline(sum(temps) / len(temps), color="#ffffff", linestyle=":",
               linewidth=1, alpha=0.6, label="Promedio")
    ax.legend(facecolor=PANEL, labelcolor=FG, edgecolor="#555770")
    _estilo(fig, ax, f"Temperatura en {CIUDAD}", "°C")
    return fig


def grafica_humedad(horas, hum):
    """Barras semitransparentes coloreadas según el nivel de humedad."""
    fig = Figure(figsize=(8, 4.2))
    ax = fig.add_subplot(111)
    colores = ["#4cc9f0" if v >= 60 else "#ffd166" for v in hum]
    ax.bar(horas, hum, width=0.03, color=colores, alpha=0.8)
    ax.axhline(60, color="#ffffff", linestyle="--", linewidth=1, alpha=0.6)
    ax.set_ylim(0, 100)
    _estilo(fig, ax, f"Humedad relativa en {CIUDAD} (azul ≥ 60 %)", "%")
    return fig


def grafica_viento(horas, viento):
    """Dispersión con tamaño proporcional a la velocidad + línea tenue."""
    fig = Figure(figsize=(8, 4.2))
    ax = fig.add_subplot(111)
    ax.plot(horas, viento, color="#9b5de5", linewidth=1, alpha=0.5)
    sc = ax.scatter(horas, viento, c=viento, cmap="plasma", marker="D",
                    s=[20 + v * 4 for v in viento], alpha=0.85)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("km/h", color=FG)
    cb.ax.tick_params(colors=FG)
    _estilo(fig, ax, f"Velocidad del viento en {CIUDAD}", "km/h")
    return fig


def open_win_canvas(parent: tk.Tk):
    """Ventana secundaria con pestañas (una gráfica por pestaña)."""
    win = tk.Toplevel(parent)
    win.title(f"Clima en {CIUDAD} · Open-Meteo")
    win.geometry("960x640")
    win.configure(bg=BG)

    style = ttk.Style(win)
    style.theme_use("clam")
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("TNotebook", background=BG)
    style.configure("TNotebook.Tab", background=PANEL, foreground=FG, padding=(14, 6))
    style.map("TNotebook.Tab", background=[("selected", ACCENT)])
    style.configure("Accent.TButton", background=ACCENT, foreground="white",
                    font=("Segoe UI", 10, "bold"))

    # Barra superior
    top = ttk.Frame(win, padding=10)
    top.pack(fill="x")
    ttk.Label(
        top,
        text=f"{CIUDAD}: {DIAS_PASADOS} días pasados + {DIAS_FUTUROS} de pronóstico",
        font=("Segoe UI", 12, "bold"),
    ).pack(side="left")
    estado = ttk.Label(top, text="Sin datos")
    estado.pack(side="right")

    # Pestañas
    nb = ttk.Notebook(win)
    nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    pestanas = {}
    for nombre in ("Temperatura", "Humedad", "Viento"):
        f = ttk.Frame(nb)
        nb.add(f, text=nombre)
        pestanas[nombre] = f

    def cargar():
        horas, temps, hum, viento = fetch_data()
        if not horas:
            return
        figuras = {
            "Temperatura": grafica_temperatura(horas, temps),
            "Humedad": grafica_humedad(horas, hum),
            "Viento": grafica_viento(horas, viento),
        }
        for nombre, fig in figuras.items():
            for w in pestanas[nombre].winfo_children():  # evita duplicar al recargar
                w.destroy()
            canvas = FigureCanvasTkAgg(fig, master=pestanas[nombre])
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        estado.config(text=f"Actualizado {datetime.now():%H:%M:%S} · {len(horas)} registros")

    ttk.Button(top, text="Cargar datos", style="Accent.TButton",
               command=cargar).pack(side="right", padx=10)

    return win


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba win_canvas v2")
    ttk.Button(root, text="Abrir ventana Canvas",
               command=lambda: open_win_canvas(root)).pack(padx=40, pady=20)
    root.mainloop()
