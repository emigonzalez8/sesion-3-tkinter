import tkinter as tk
from tkinter import ttk, messagebox
import csv
from pathlib import Path

def open_win_table(parent: tk.Tk):
    win = tk.Toplevel(parent)
    win.title("Tabla (Treeview)")
    win.geometry("480x300")
    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    cols = ("nombre", "valor1", "valor2")
    tv = ttk.Treeview(frm, columns=cols, show="headings", height=10)
    for c in cols:
        tv.heading(c, text=c.capitalize())
        tv.column(c, width=120, anchor="center")
    tv.pack(fill="both", expand=True)

    ruta = Path(__file__).resolve().parents[2] / "data" / "sample.csv"  # <repo>/data/sample.csv
    try:
        with ruta.open(encoding="utf-8", newline="") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                tv.insert("", "end", values=(fila["nombre"], fila["valor1"], fila["valor2"]))
    except (OSError, UnicodeError, csv.Error, KeyError):
        messagebox.showwarning("Aviso", f"No se pudo leer el CSV. Revisa este archivo:\n{ruta}", parent=win)

    ttk.Button(frm, text="Cerrar", command=win.destroy).pack(pady=8, anchor="e")