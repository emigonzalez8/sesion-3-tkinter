import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import requests
import matplotlib.dates as mdates
from matplotlib import cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------- Configuración ----------
CIUDADES = {
    "Mérida": (20.97, -89.62),
    "Puebla": (19.04, -98.20),
    "Oaxaca": (17.06, -96.73),
    "Guanajuato": (21.02, -101.26),
    "Tijuana": (32.51, -117.04),
}

# Tema claro tipo "papel"
BG = "#f7f3ea"
SIDEBAR = "#e9e2d0"
TEXTO = "#2b2b2b"
VERDE = "#2d6a4f"
NARANJA = "#e76f51"
AZUL = "#277da1"
MORADO = "#7b2cbf"


def fetch_data(ciudad, dias):
    """
    Consulta Open-Meteo para los próximos `dias` días (sin días pasados):
    temperatura, humedad relativa y viento a 10 m.
    """
    try:
        lat, lon = CIUDADES[ciudad]
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
            f"&forecast_days={dias}&timezone=auto"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        h = r.json()["hourly"]
        return {
            "horas": [datetime.fromisoformat(t) for t in h["time"]],
            "temp": h["temperature_2m"],
            "hum": h["relative_humidity_2m"],
            "viento": h["wind_speed_10m"],
        }
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron obtener los datos:\n{e}")
        return None


def media_movil(vals, n):
    """Promedio móvil simple de ventana n."""
    out = []
    for i in range(len(vals)):
        ventana = vals[max(0, i - n + 1): i + 1]
        out.append(sum(ventana) / len(ventana))
    return out


# ---------- Estilo común ----------
def estilo(fig, ax, titulo, ylabel, mostrar_x=True):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor("#fffdf7")
    ax.set_title(titulo, color=TEXTO, fontsize=11, fontweight="bold", loc="left")
    ax.set_ylabel(ylabel, color=TEXTO)
    ax.tick_params(colors=TEXTO, labelbottom=mostrar_x)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(True, linestyle="--", alpha=.5)
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 6)))


# ---------- Gráficas (reciben un eje para poder combinarlas) ----------
def dibujar_temp(fig, ax, d, mostrar_x=True):
    ax.plot(d["horas"], d["temp"], color=NARANJA, linewidth=1.6, marker="D",
            markersize=3.5, alpha=.85, label="Hora a hora")
    ax.plot(d["horas"], media_movil(d["temp"], 6), color=MORADO, linewidth=2.6,
            linestyle="--", alpha=.9, label="Promedio móvil 6 h")
    ax.legend(frameon=False, loc="upper right")
    estilo(fig, ax, "Temperatura", "°C", mostrar_x)


def dibujar_hum(fig, ax, d, mostrar_x=True):
    ax.axhspan(40, 60, color="#95d5b2", alpha=.35, label="Zona de confort (40–60 %)")
    ax.fill_between(d["horas"], d["hum"], step="mid", color=AZUL, alpha=.30)
    ax.step(d["horas"], d["hum"], where="mid", color=AZUL, linewidth=2)
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, loc="upper right")
    estilo(fig, ax, "Humedad relativa", "%", mostrar_x)


def dibujar_viento(fig, ax, d, mostrar_x=True):
    v = d["viento"]
    vmax = max(v) or 1
    colores = [cm.YlGn(0.3 + 0.7 * x / vmax) for x in v]
    ax.bar(d["horas"], v, width=0.035, color=colores, edgecolor=VERDE,
           linewidth=0.4, alpha=.9)
    i = v.index(max(v))
    ax.annotate(f"Racha {v[i]:.1f} km/h", (d["horas"][i], v[i]),
                xytext=(0, 8), textcoords="offset points", ha="center",
                color=TEXTO, fontsize=9)
    estilo(fig, ax, "Viento a 10 m", "km/h", mostrar_x)


def crear_figura(modo, d, ciudad):
    """Una figura individual o una comparativa de tres paneles."""
    fig = Figure(figsize=(8, 5.5))
    if modo == "Comparativa":
        ax1, ax2, ax3 = fig.subplots(3, 1, sharex=True)
        dibujar_temp(fig, ax1, d, mostrar_x=False)
        dibujar_hum(fig, ax2, d, mostrar_x=False)
        dibujar_viento(fig, ax3, d)
    else:
        ax = fig.add_subplot(111)
        {"Temperatura": dibujar_temp,
         "Humedad": dibujar_hum,
         "Viento": dibujar_viento}[modo](fig, ax, d)
    fig.suptitle(f"{ciudad} – próximos {len(d['horas']) // 24} días",
                 color=TEXTO, fontsize=13, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return fig


# ---------- Ventana ----------
def open_win_canvas(parent: tk.Tk):
    """Ventana con barra lateral de controles y área de gráfica a la derecha."""
    win = tk.Toplevel(parent)
    win.title("Pronóstico Open-Meteo – Tablero")
    win.geometry("1040x620")
    win.configure(bg=BG)

    estilo_ttk = ttk.Style(win)
    estilo_ttk.theme_use("clam")
    estilo_ttk.configure("Side.TFrame", background=SIDEBAR)
    estilo_ttk.configure("Side.TLabel", background=SIDEBAR, foreground=TEXTO)
    estilo_ttk.configure("Side.TRadiobutton", background=SIDEBAR, foreground=TEXTO)
    estilo_ttk.configure("Main.TFrame", background=BG)
    estilo_ttk.configure("Main.TLabel", background=BG, foreground=TEXTO)

    datos = {"d": None, "ciudad": None}

    # --- Barra lateral ---
    side = ttk.Frame(win, style="Side.TFrame", padding=14)
    side.pack(side="left", fill="y")

    ttk.Label(side, text="Ciudad", style="Side.TLabel",
              font=("Segoe UI", 10, "bold")).pack(anchor="w")
    ciudad_var = tk.StringVar(value="Mérida")
    ttk.Combobox(side, textvariable=ciudad_var, values=list(CIUDADES),
                 state="readonly", width=18).pack(anchor="w", pady=(2, 12))

    ttk.Label(side, text="Días de pronóstico", style="Side.TLabel",
              font=("Segoe UI", 10, "bold")).pack(anchor="w")
    dias_var = tk.IntVar(value=7)
    dias_lbl = ttk.Label(side, text="7 días", style="Side.TLabel")
    dias_lbl.pack(anchor="w")
    ttk.Scale(side, from_=1, to=14, orient="horizontal", length=160,
              command=lambda v: (dias_var.set(round(float(v))),
                                 dias_lbl.config(text=f"{dias_var.get()} días"))
              ).pack(anchor="w", pady=(0, 12))

    ttk.Label(side, text="Vista", style="Side.TLabel",
              font=("Segoe UI", 10, "bold")).pack(anchor="w")
    modo_var = tk.StringVar(value="Comparativa")
    for m in ("Comparativa", "Temperatura", "Humedad", "Viento"):
        ttk.Radiobutton(side, text=m, value=m, variable=modo_var,
                        style="Side.TRadiobutton",
                        command=lambda: redibujar()).pack(anchor="w")

    ttk.Button(side, text="Consultar API", command=lambda: consultar()
               ).pack(anchor="w", pady=14)

    resumen = ttk.Label(side, text="", style="Side.TLabel", justify="left")
    resumen.pack(anchor="w", pady=(6, 0))

    # --- Área de gráfica ---
    main = ttk.Frame(win, style="Main.TFrame", padding=8)
    main.pack(side="left", fill="both", expand=True)

    def redibujar():
        if not datos["d"]:
            return
        for w in main.winfo_children():
            w.destroy()
        fig = crear_figura(modo_var.get(), datos["d"], datos["ciudad"])
        canvas = FigureCanvasTkAgg(fig, master=main)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def consultar():
        ciudad = ciudad_var.get()
        d = fetch_data(ciudad, dias_var.get())
        if not d:
            return
        datos["d"], datos["ciudad"] = d, ciudad
        t, h, v = d["temp"], d["hum"], d["viento"]
        resumen.config(text=(
            f"Resumen\n"
            f"Temp: {min(t):.1f} – {max(t):.1f} °C\n"
            f"Hum. prom: {sum(h) / len(h):.0f} %\n"
            f"Viento máx: {max(v):.1f} km/h"
        ))
        redibujar()

    return win


# Para pruebas independientes (opcional)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba win_canvas")
    ttk.Button(root, text="Abrir ventana Canvas",
               command=lambda: open_win_canvas(root)).pack(pady=20)
    root.mainloop()
