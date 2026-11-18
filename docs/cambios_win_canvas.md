# Sesión 7 — API pública y gráficas

**Entrega individual:** German Ahgue Renteria

## Objetivo y archivos

Esta versión consulta temperaturas horarias de León, Guanajuato en Open-Meteo y las muestra en dos gráficas de Matplotlib (línea y barras) dentro de una ventana secundaria de tkinter. Se parte del código existente de `win_canvas.py` y se conserva su estructura modular: `fetch_data()`, `create_line_chart()`, `create_bar_chart()`, `mostrar_graficas()` y `open_win_canvas()`.

La implementación está en `win_canvas.py`. Los parámetros de la consulta (ciudad y variable) quedaron como constantes al inicio del archivo para poder cambiarlos desde un solo lugar sin tocar las funciones.

## Cambios individuales

* **Ciudad:** León, Gto; latitud `21.12`, longitud `-101.68`. Ahora son las constantes `LATITUD` y `LONGITUD`, y la URL las toma con un f-string. Para otra ciudad solo se modifican esos dos valores (ejemplo: CDMX con `19.43` y `-99.13`).
* **Rango:** últimas 24 horas, con `past_days=1`; zona horaria `timezone=auto`.
* **Variable:** se agregó la constante `PARAMETRO`, que por defecto es `temperature_2m` (°C). También se puede cambiar a `relativehumidity_2m` (humedad relativa, %) o `windspeed_10m` (viento, km/h). El diccionario `ETIQUETAS` ajusta automáticamente el título y la etiqueta del eje Y según la variable elegida.
* **Estilo de la línea:** marcadores cuadrados (`marker="s"`), grosor `linewidth=2` y transparencia `alpha=0.8`.
* **Estilo de las barras:** transparencia `alpha=0.8`.
* **Rejilla:** `ax.grid(True, linestyle="--", alpha=.5)` en ambas gráficas.
* **Etiquetas del eje X:** se muestra una hora de cada tres (`set_xticks(range(0, len(horas), 3))`) para que no se amontonen.
* **Títulos dinámicos:** incluyen la variable y la ciudad, por ejemplo "Temperatura (°C) en León, Gto (línea)".
