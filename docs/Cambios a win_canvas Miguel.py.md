# Cambios a `win_canvas.py`

Autor: Miguel González

## Resumen

Se creó una versión distinta de `win_canvas.py` con otro diseño, otro rango de consulta a la API de Open-Meteo y nuevos elementos visuales en las gráficas. La función `open_win_canvas(parent)` se conserva, por lo que se integra igual que la versión anterior.

## 1. Diseño de la ventana

| Antes | Ahora |
|---|---|
| Un solo botón "Cargar y mostrar gráficas" | Barra de controles con ciudad, días pasados, días futuros y botón de carga |
| Gráficas apiladas verticalmente (se duplicaban al pulsar de nuevo) | Pestañas (`ttk.Notebook`): Temperatura, Humedad y Viento |
| Ventana de 960x1000 con estilo por defecto | Ventana de 980x640 con tema oscuro (`clam`) |
| Sin herramientas de navegación | `NavigationToolbar2Tk` en cada gráfica (zoom, mover, guardar) |
| Sin indicador de estado | Etiqueta "Actualizado HH:MM:SS" |

Además, al recargar se limpian las pestañas antes de dibujar, así que ya no se acumulan gráficas.

## 2. Consulta a la API

- **Ciudad seleccionable** (modifica `latitude` y `longitude` en la URL): León, Ciudad de México, Guadalajara, Monterrey y Cancún, guardadas en el diccionario `CIUDADES`.
- **Rango de días configurable**:
  - Antes: `past_days=1`.
  - Ahora: `past_days` de 0 a 7 y `forecast_days` de 1 a 7 (valor inicial 3 y 3).
- **Más parámetros horarios**:
  - Antes: `temperature_2m`.
  - Ahora: `temperature_2m`, `relative_humidity_2m` y `wind_speed_10m`.
- Las horas se convierten a `datetime` para que el eje X muestre fecha y hora.

## 3. Elementos visuales de las gráficas

### Temperatura
- Línea con marcadores cuadrados (`marker="s"`), `linewidth=2` y `alpha=.95`.
- Área rellena bajo la línea con `fill_between` y `alpha=.18`.
- Anotaciones del valor máximo y mínimo.
- Línea punteada vertical en la hora actual.

### Humedad relativa
- Barras con transparencia (`alpha=.75`).
- Línea horizontal punteada con el promedio y leyenda.
- Eje Y fijo de 0 a 100 %.

### Viento
- Gráfica escalonada (`ax.step`).
- Puntos coloreados según la velocidad (`scatter` con mapa `viridis`) y barra de color en km/h.

### Comunes a todas
- Rejilla: `ax.grid(True, linestyle="--", alpha=.35)`.
- Fondo oscuro, títulos en negrita y ejes con colores claros.
- Formato de fecha `dd/mm` y hora en el eje X.
- Se usa `Figure` de matplotlib en lugar de `plt.subplots`, lo que es más adecuado dentro de tkinter.

## 4. Parámetros que se pueden seguir ajustando

- Otra ciudad: agregar una entrada a `CIUDADES` con su latitud y longitud.
- Otros marcadores: `marker="s"`, `"o"`, `"^"`, `"D"`.
- Grosor y transparencia: `linewidth` y `alpha`.
- Otros parámetros de la API: por ejemplo `precipitation` o `surface_pressure` en `hourly=`.
