import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import requests
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# ---------- Configuración ----------
CIUDADES = {
    "León, Gto": (21.12, -101.68),
    "Ciudad de México": (19.43, -99.13),
    "Guadalajara": (20.67, -103.35),
    "Monterrey": (25.67, -100.31),
    "Cancún": (21.16, -86.85),
}

# Paleta oscura
BG = "#1e1e2e"
PANEL = "#2a2a3d"
TEXTO = "#e6e6f0"
COLOR_TEMP = "#ff7a59"
COLOR_HUM = "#4fc3f7"
COLOR_VIENTO = "#81e6a1"


def fetch_data(ciudad, dias_pasados, dias_futuros):
    """
    Consulta Open-Meteo: temperatura, humedad relativa y viento horarios
    para un rango de días pasados + futuros.
    Devuelve (horas, temperaturas, humedad, viento) o listas vacías si falla.
    """
    try:
        lat, lon = CIUDADES[ciudad]
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
            f"&past_days={dias_pasados}&forecast_days={dias_futuros}"
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


# ---------- Gráficas ----------
def _estilo(fig, ax, titulo, ylabel):
    fig.patch.set_facecolor(PANEL)
    ax.set_facecolor(BG)
    ax.set_title(titulo, color=TEXTO, fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel, color=TEXTO)
    ax.tick_params(colors=TEXTO)
    for s in ax.spines.values():
        s.set_color("#555570")
    ax.grid(True, linestyle="--", alpha=.35, color="#888899")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))


def grafica_temperatura(horas, temps, ciudad):
    """Línea con área rellena, marcadores cuadrados y marca del máximo/mínimo."""
    fig = Figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    ax.plot(horas, temps, color=COLOR_TEMP, linewidth=2, marker="s",
            markersize=3, alpha=.95)
    ax.fill_between(horas, temps, min(temps), color=COLOR_TEMP, alpha=.18)

    i_max = temps.index(max(temps))
    i_min = temps.index(min(temps))
    ax.annotate(f"Máx {temps[i_max]:.1f}°", (horas[i_max], temps[i_max]),
                xytext=(0, 12), textcoords="offset points", ha="center",
                color=TEXTO, arrowprops=dict(arrowstyle="-", color=TEXTO))
    ax.annotate(f"Mín {temps[i_min]:.1f}°", (horas[i_min], temps[i_min]),
                xytext=(0, -20), textcoords="offset points", ha="center",
                color=TEXTO, arrowprops=dict(arrowstyle="-", color=TEXTO))
    ax.axvline(datetime.now(), color="#ffd54f", linestyle=":", linewidth=1.5)
    _estilo(fig, ax, f"Temperatura – {ciudad}", "°C")
    fig.tight_layout()
    return fig


def grafica_humedad(horas, hum, ciudad):
    """Barras con transparencia y línea de promedio."""
    fig = Figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    ax.bar(horas, hum, width=0.035, color=COLOR_HUM, alpha=.75)
    prom = sum(hum) / len(hum)
    ax.axhline(prom, color="#ffffff", linestyle="--", linewidth=1.2,
               label=f"Promedio {prom:.0f}%")
    ax.set_ylim(0, 100)
    ax.legend(facecolor=PANEL, labelcolor=TEXTO, edgecolor="#555570")
    _estilo(fig, ax, f"Humedad relativa – {ciudad}", "%")
    fig.tight_layout()
    return fig


def grafica_viento(horas, viento, ciudad):
    """Gráfica escalonada con puntos de color según intensidad."""
    fig = Figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    ax.step(horas, viento, where="mid", color=COLOR_VIENTO, linewidth=1.8, alpha=.9)
    sc = ax.scatter(horas, viento, c=viento, cmap="viridis", s=18, zorder=3)
    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.ax.tick_params(colors=TEXTO)
    cb.set_label("km/h", color=TEXTO)
    _estilo(fig, ax, f"Velocidad del viento – {ciudad}", "km/h")
    fig.tight_layout()
    return fig


# ---------- Ventana ----------
def open_win_canvas(parent: tk.Tk):
    """Ventana secundaria con pestañas, selector de ciudad y rango de días."""
    win = tk.Toplevel(parent)
    win.title("Clima con Open-Meteo – Panel de gráficas")
    win.geometry("980x640")
    win.configure(bg=BG)

    style = ttk.Style(win)
    style.theme_use("clam")
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXTO)
    style.configure("TButton", padding=6)
    style.configure("TNotebook", background=BG)
    style.configure("TNotebook.Tab", padding=(14, 6))

    # Barra de controles
    barra = ttk.Frame(win, padding=10)
    barra.pack(fill="x")

    ttk.Label(barra, text="Ciudad:").pack(side="left")
    ciudad_var = tk.StringVar(value="León, Gto")
    ttk.Combobox(barra, textvariable=ciudad_var, values=list(CIUDADES),
                 state="readonly", width=18).pack(side="left", padx=(4, 14))

    ttk.Label(barra, text="Días pasados:").pack(side="left")
    pasados_var = tk.IntVar(value=3)
    ttk.Spinbox(barra, from_=0, to=7, textvariable=pasados_var, width=4).pack(side="left", padx=(4, 14))

    ttk.Label(barra, text="Días futuros:").pack(side="left")
    futuros_var = tk.IntVar(value=3)
    ttk.Spinbox(barra, from_=1, to=7, textvariable=futuros_var, width=4).pack(side="left", padx=(4, 14))

    estado = ttk.Label(barra, text="")
    estado.pack(side="right")

    # Pestañas
    nb = ttk.Notebook(win)
    nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    tabs = {}
    for nombre in ("Temperatura", "Humedad", "Viento"):
        f = ttk.Frame(nb)
        nb.add(f, text=nombre)
        tabs[nombre] = f

    def limpiar(frame):
        for w in frame.winfo_children():
            w.destroy()

    def poner(frame, fig):
        limpiar(frame)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        NavigationToolbar2Tk(canvas, frame).update()

    def cargar():
        try:
            pasados, futuros = int(pasados_var.get()), int(futuros_var.get())
        except (tk.TclError, ValueError):
            messagebox.showwarning("Aviso", "Los días deben ser números enteros.")
            return
        ciudad = ciudad_var.get()
        horas, temps, hum, viento = fetch_data(ciudad, pasados, futuros)
        if not horas:
            return
        poner(tabs["Temperatura"], grafica_temperatura(horas, temps, ciudad))
        poner(tabs["Humedad"], grafica_humedad(horas, hum, ciudad))
        poner(tabs["Viento"], grafica_viento(horas, viento, ciudad))
        estado.config(text=f"Actualizado {datetime.now():%H:%M:%S}")

    ttk.Button(barra, text="Cargar gráficas", command=cargar).pack(side="left")

    return win


# Para pruebas independientes (opcional)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba win_canvas")
    ttk.Button(root, text="Abrir ventana Canvas",
               command=lambda: open_win_canvas(root)).pack(pady=20)
    root.mainloop()
