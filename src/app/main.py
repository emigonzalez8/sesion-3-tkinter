import tkinter as tk
from tkinter import ttk
from .win_home import open_win_home
from .win_form import open_win_form
from .win_list import open_win_list
from .win_table import open_win_table
from .win_canvas import open_win_canvas
from .win_canvas_fabio import open_win_canvas as open_win_canvas_fabio
from .win_canvas_miguel import open_win_canvas as open_win_canvas_miguel
from .win_canvas_marcelo import open_win_canvas as open_win_canvas_marcelo
from .win_canvas_german import open_win_canvas as open_win_canvas_german

def main():
    root = tk.Tk()
    root.title("Proyecto Integrador - MVP")
    root.geometry("460x500")

    themed_roots = []

    def open_themed_window(open_window):
        # Each Tk interpreter has its own ttk theme.
        window_root = tk.Tk()
        window_root.withdraw()
        try:
            window = open_window(window_root)
        except Exception:
            window_root.destroy()
            raise
        themed_roots.append(window_root)

        def close_window():
            themed_roots.remove(window_root)
            window_root.destroy()

        window.protocol("WM_DELETE_WINDOW", close_window)

    def close_menu():
        for window_root in themed_roots:
            window_root.destroy()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_menu)

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Aplicación Demo (tkinter)", font=("Segoe UI", 12, "bold")).pack(pady=(0, 12))
    ttk.Button(frame, text="1) Home / Bienvenida", command=lambda: open_win_home(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="2) Formulario", command=lambda: open_win_form(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="3) Lista (CRUD básico)", command=lambda: open_win_list(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="4) Tabla (Treeview)", command=lambda: open_win_table(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="5) API y gráficas (Emiliano)", command=lambda: open_win_canvas(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="6) API y gráficas (Fabio Andrade)", command=lambda: open_win_canvas_fabio(root)).pack(pady=4, fill="x")
    ttk.Button(frame, text="7) API y gráficas (Miguel)", command=lambda: open_themed_window(open_win_canvas_miguel)).pack(pady=4, fill="x")
    ttk.Button(frame, text="8) API y gráficas (Marcelo)", command=lambda: open_themed_window(open_win_canvas_marcelo)).pack(pady=4, fill="x")
    ttk.Button(frame, text="9) API y gráficas (Germán)", command=lambda: open_themed_window(open_win_canvas_german)).pack(pady=4, fill="x")
    ttk.Separator(frame).pack(pady=6, fill="x")
    ttk.Button(frame, text="Salir", command=close_menu).pack(pady=6)

    root.mainloop()

if __name__ == "__main__":
    main()