# Sesión 7 — API pública, persistencia y gráficas

Entrega individual: Marcelo Anaya

## Objetivo y archivos

Esta versión consulta temperatura, humedad relativa y viento horarios en Open-Meteo, los muestra en gráficas de Matplotlib dentro de tkinter y permite elegir la ciudad, los días de pronóstico y la vista desde una barra lateral. Se parte del código original de `win_canvas.py` y se conserva su función de entrada `open_win_canvas(parent)`.

La implementación individual está en `win_canvas.py`. La ventana se abre igual que la original, desde un botón que llama a `open_win_canvas`. Cada gráfica está en su propia función (`dibujar_temp`, `dibujar_hum`, `dibujar_viento`) y `crear_figura` las combina, por lo que se pueden reutilizar por separado.

## Cambios individuales

* Ciudad: seleccionable entre Mérida, Puebla, Oaxaca, Guanajuato y Tijuana, guardadas en el diccionario `CIUDADES`. La ciudad inicial es Mérida, con latitud `20.97` y longitud `-89.62`; la original era León, Gto.
* Rango: solo pronóstico, con `forecast_days` de 1 a 14 elegido con un deslizador (inicial 7) y sin `past_days`; la original usaba `past_days=1`.
* Variables: `hourly=temperature_2m,relative_humidity_2m,wind_speed_10m`, en °C, % y km/h; zona horaria `timezone=auto`. Se usan los nombres actuales de Open-Meteo y no `relativehumidity_2m` ni `windspeed_10m`, que están obsoletos.
* Diseño: tema claro tipo papel con barra lateral a la izquierda y una sola área de gráfica a la derecha. La barra lateral incluye ciudad, días, vista, botón Consultar API y un resumen con temperatura mínima y máxima, humedad promedio y viento máximo.
* Vistas: Comparativa (tres paneles apilados con eje X compartido), Temperatura, Humedad y Viento. Los datos se guardan en memoria, así que cambiar de vista no vuelve a consultar la API.
* Temperatura: línea naranja con marcadores de diamante (`marker="D"`), `linewidth=1.6` y `alpha=.85`, más un promedio móvil de 6 horas en línea punteada morada.
* Humedad: gráfica escalonada azul con relleno translúcido, franja verde de zona de confort entre 40 % y 60 % y eje Y de 0 a 100 %.
* Viento: barras con degradado de color según la velocidad y anotación de la racha máxima.
* Todas las gráficas tienen título, ejes con unidades, fechas con el día de la semana y rejilla con `ax.grid(True, linestyle="--", alpha=.5)`.
* Se usa `Figure` de matplotlib en lugar de `plt.subplots`, lo que es más adecuado dentro de tkinter.
* Captura: `Graficas_Marcelo.png` muestra la vista Comparativa de Mérida para los próximos 7 días, con las tres gráficas de este documento (temperatura con promedio móvil, humedad con zona de confort y viento con racha máxima).
