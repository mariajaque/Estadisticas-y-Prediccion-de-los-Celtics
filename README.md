# Estadisticas-y-Prediccion-de-los-Celtics
***
El código de este repositorio permite generar de manera automática
un reporte ejecutivo en pdf con las estadísticas el equipo de los
Boston Celtics tonto a nivel de equipo como a nivel de jugadores
en la temporada de 2022. Asimismo, tras la ejecución se devolverá por
pantalla la predicción para el próximo partido de los celtics basándose
en las predicciones de las casas de apuestas.

## Antes de ejecutar

Es de gran importancia hacer un pip install del requierements.txt

```
pip install -r requirements.txt
```

E introducir la clave de la api en el fichero config.txt de tal forma que
el fichero quede de la siguiente manera:

```
{'key':'clave'}
```

Para obtener la clave de la api es necesario acceder a https://sportsdata.io/
y suscribirse. Para poder leer la clave de la api es necesario acceder a
https://sportsdata.io/developers/api-documentation/nba y ahí podremos verla
en el apartado de API KEY de cualquiera de las categorías de las que se
puede hacer un request

Una vez hemos seguido estos dos pasos el código estará listo para ejecutarse


## Ficheros para la Ejecución:

- **requirements.txt**: contiene las librerías necesarias para la ejecución
- **config.txt**: fichero del que se leerá la clave necesaria para hacer un request a la API
- **celtics_stats_and_prediction.py**: fichero python ejecutable que generará el reporte
en pdf así como la búsqueda de la predicción para el siguiente partido. Este es el fichero
que debe de ejecutarse si se desea usar el programa pero para ello será necesario haber seguido
los pasos previos


### Otros ficheros:
- **celtics_stats.pdf**: reporte con las estadísticas de los Celtics en esta temporada.
Contiene estadísticas tanto por equipo como por jugador
- **doubles.jpg**: gráfica generada para el reporte con los dobles dobles y los triples
dobles marcados por el equipo.
- **free_trows.jpg**: gráfica generada para el reporte con el porcentaje de tiros libres
marcados por cadad jugador del equipo.
- **global_results.jpg**: pie chart con el porcentaje de partidos perdidos y ganados por el
equipo generado para el reporte.
- **leats_5_efficient.jpg**: gráfica con los 5 jugadores menos eficientes del equipo generada
para el reporte
- **least_5_scorers.jpg**: gráfica con los 5 jugadores menos anotadores del equipo generada
para el reporte
- **logo.svg**: enlace al logo del equipo usado para la portada del reporte
- **player_stats_table.jpg**: gráfica con las estadísticas generales de los jugadores del
equipo generada para el reporte
- **team_shooting_percentaje.jpg**: gráfica con porcentajes en función del tipo de tiro
- **team_stats_table.jpg**: tabla con las estadísticas generales del equipo
- **three_pointers.jpg**: gráfica con los porcentajes de triples anotados por cada jugador
- **top_5_efficient.jpg**: gráfica con los 5 jugadores considerados los más eficientes
- **top_5_scorers.jpg**: gráfica con los 5 máximos anotadores del equipo
- **two_pointers.jpg**: gráfica con los porcentajes de tiros dobles anotados por cada jugador
del equipo
