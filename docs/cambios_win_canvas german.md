# Sesión 7 — API pública y gráficas

**Entrega individual:** German Ahgue Renteria

**Objetivo y archivos**

Esta versión consulta temperatura, humedad relativa y viento por hora de la Ciudad de México en Open-Meteo y los muestra en tres gráficas de Matplotlib (línea, barras y dispersión) dentro de una ventana secundaria de tkinter con pestañas. Se parte del código existente de win_canvas.py y se conserva su estructura modular: fetch_data(), una función por gráfica (grafica_temperatura(), grafica_humedad(), grafica_viento()) y open_win_canvas(). Se agregó _estilo() para aplicar el mismo formato a todas las gráficas, y mostrar_graficas() se integró dentro de la función interna cargar().

La implementación está en win_canvas_v2.py. Los parámetros de la consulta (ciudad y rango) quedaron como constantes al inicio del archivo para poder cambiarlos desde un solo lugar sin tocar las funciones.

**Cambios individuales**
**Ciudad:** Ciudad de México; latitud 19.43, longitud -99.13. Ahora son las constantes LATITUD y LONGITUD (junto con CIUDAD para los títulos), y la URL las toma con un f-string. Para otra ciudad solo se modifican esos valores (ejemplo: León, Gto con 21.12 y -101.68).
**Rango:** 3 días pasados y 2 de pronóstico, con past_days=3 y forecast_days=2 (constantes DIAS_PASADOS y DIAS_FUTUROS); zona horaria timezone=auto. La v1 solo traía las últimas 24 horas.
**Variables:** se consultan en una sola petición temperature_2m (°C), relative_humidity_2m (humedad relativa, %) y wind_speed_10m (viento, km/h), y cada una se muestra en su propia pestaña. Se usan los nombres actuales de Open-Meteo con guion bajo.
**Estilo de la línea (temperatura)**: marcadores cuadrados (marker="s"), grosor linewidth=2.2 y transparencia alpha=0.95. Además lleva área sombreada, puntos de máxima y mínima, y una línea punteada con el promedio.
**Estilo de las barras (humedad):** transparencia alpha=0.8, color azul si la humedad es de 60 % o más y amarillo si es menor, con una línea guía en 60 %.
**Estilo de la dispersión (viento)**: marcadores de rombo (marker="D") con tamaño y color según la velocidad (mapa plasma y barra de color), unidos por una línea tenue.
**Rejilla:** ax.grid(True, linestyle="--", alpha=.35) en todas las gráficas.
**Etiquetas del eje X:** las horas son objetos datetime y se muestran con formato dd/mm y HH:MM cada 12 horas (HourLocator(byhour=(0, 12))) para que no se amontonen.
**Títulos dinámicos:** incluyen la variable y la ciudad, por ejemplo "Temperatura en Ciudad de México".
**Diseño de la ventana:** tema oscuro con paleta en constantes (BG, PANEL, FG, ACCENT), pestañas con ttk.Notebook, barra superior con el rango consultado y la hora de la última actualización.
**Recarga:** al presionar de nuevo "Cargar datos" se reemplazan las gráficas anteriores en lugar de duplicarlas. También se corrigió el \\n del mensaje de error por \n.
