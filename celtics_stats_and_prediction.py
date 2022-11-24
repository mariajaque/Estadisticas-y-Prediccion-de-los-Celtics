import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fpdf import FPDF
import warnings
import signal
import sys


warnings.filterwarnings("ignore")


class PDF(FPDF):

    def footer(self):

        # Establecemos como vamos a querer que sea el pie de página de nuestro documento
        # Primero le pasamos la posición en la que queremos que comience el pie
        # de página. En nuestro caso queremos que comience a 10 mm del final de la página

        self.set_y(-20)
        self.set_font('helvetica', '', 8)

        # Añadimos el número de línea

        self.cell(0, 10, f'Página {str(self.page_no())}', align='C')

    def portada(self):

        # Creamos la portada en la que venga el título del reporte, el año y
        # una fotografía del logo del equipo
        # Alineamos ambos textos en el centro

        self.set_font('times', 'b', 40)
        self.set_y(50)
        self.cell(0, 40, 'Boston Celtics Statistics', ln=True, align='C')
        self.set_font('times', '', 25)
        self.cell(0, 25, '2022', ln=True, align='C')
        self.image('celtics_logo.jpg', x = 50, y = 120, w = 100)


def handler_signal(signal,frame):

    # Salida controlada del programa en caso de pulsar
    # control C

    print("\n\n [!] out .......\ n")

    sys.exit(1)

signal.signal(signal.SIGINT,handler_signal)


def extract_api():

    # Se extrae la información sobre las estadísticas de todos los equipos
    # de una API de deportes.

    # Para poder accerder hay que cambiar 'xxxxxxxxxxx' por la clave que
    # nos asigna la API al registrarnos

    headers = {
            'Ocp-Apim-Subscription-Key': 'e7da973922a641f79d7b9e34feec85c1'
            }

    # Recibimos las respuestas y estas se almacenan en una lista con diccionarios
    # donde cada diccionario contendrá las estadísticas de un equipo.

    response_stats = requests.get("https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/2022", headers=headers)
    stats_list = response_stats.json()

    # Además de las estadísticas del equipo se extraen también las
    # estadísticas individuales de cada uno de sus jugadores

    response_players = requests.get('https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2022/BOS', headers=headers)
    players_lista = response_players.json()

    return stats_list, players_lista


def transform_api(stats_list, player_lista):

    team_chosen = 'Boston Celtics'

    # Extraemos los datos del equipo en concreto
    # en este caso los Boston Celtics

    for s in stats_list:

        # Nos quedamos exclusivamente con el diccionario
        # que contiene las estadísticas de los Celtics

        if s['Name'] == team_chosen:
            dict_team_stats = s

    # Se extrae un dataframe reducido con las estadísticas de
    # los jugadores.

    df_players = pd.DataFrame(player_lista)
    df_reducido = df_players[['Name', 'Position', 'Games', 'FantasyPoints', 
                                'Minutes', 'Seconds', 'EffectiveFieldGoalsPercentage',
                                'TwoPointersPercentage', 'ThreePointersPercentage',
                                'FreeThrowsPercentage', 'OffensiveReboundsPercentage',
                                'DefensiveReboundsPercentage', 'PersonalFouls', 'Points',
                                'TrueShootingPercentage', 'PlayerEfficiencyRating',
                                'AssistsPercentage', 'StealsPercentage', 'BlocksPercentage',
                                'TurnOversPercentage', 'UsageRatePercentage',
                                'DoubleDoubles', 'TripleDoubles']]

    # Se crea un pdf que contendrá las gráficas de las
    # estadísticas del equipo

    pdf = create_pdf(dict_team_stats, df_reducido)

    return pdf


def create_pdf(dict_team_stats, df_reducido):

    # Se crean tanto el pdf como los gráficos que se añadirán

    pdf = PDF('P', 'mm')
    create_graphs_team(dict_team_stats, df_reducido)

    # Establecemos que cambie de página automáticamente
    # Establecemos que cambie de página cuando esté a 12mm del final de la
    # página

    pdf.set_auto_page_break(auto=True, margin=100)

    # Añadimos una página y la portada del reporte
    pdf.add_page()
    pdf.portada()
    pdf.add_page()

    # En la segunda página del reporte se añade una tabla con las
    # estadísticas del equipo

    pdf.set_font('times', 'b', 20)
    pdf.cell(0, 25, 'Team Stats Table:', ln=True)
    pdf.image('team_stats_table.jpg', x=30, y=40, w=150)
    pdf.add_page()

    # En la tercera página se añaden el pie chart con las victorias
    # y derrotas del equipo en la temporada y se añade también
    # una gráfica con los porcentages de tiro del equipo

    pdf.cell(0, 25, 'Result of Matches:', ln=True)
    pdf.image('global_results.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.set_y(140)
    pdf.cell(0, 25, 'Shooting Percentages:', ln=True)
    pdf.image('team_shooting_percentages.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.add_page()

    # En la cuarta cara se añade un barplot con los porcentages
    # de dobles dobles y de triples triples

    pdf.cell(0, 25, 'Doubles Percentage:', ln=True)
    pdf.image('doubles.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.add_page()

    # En la quinta cara añadimos la tabla de las estadísticas
    # de cada jugador

    pdf.cell(0, 25, 'Player Stats Table:', ln=True)
    pdf.image('player_stats_table.jpg', x=10, y=pdf.get_y() + 5, w=190, h=80)
    pdf.add_page()

    # En la siguiente página se añaden las gráficas de los 5
    # máximos anotadores y de los 5 que menos puntos han marcado

    pdf.cell(0, 25, 'Top 5 Scorers:', ln=True)
    pdf.image('top_5_scorers.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.set_y(140)
    pdf.cell(0, 25, 'Least 5 Scorers', ln=True)
    pdf.image('least_5_scorers.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.add_page()

    # Posteriormente en una nueva página se añaden las gráficas
    # de los jugadores con mayor y menor eficiencia

    pdf.cell(0, 25, 'Most Efficient Players:', ln=True)
    pdf.image('top_5_efficient.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.set_y(140)
    pdf.cell(0, 25, 'Least Efficient Players', ln=True)
    pdf.image('least_5_efficient.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.add_page()

    # Durante las siguientes 2 caras se añaden las gráficas de
    # el porcentage de tiros de 2 puntos anotados, de tiros
    # triples y de tiros libres

    pdf.cell(0, 25, 'Two Pointers Percentage of Each Player:', ln=True)
    pdf.image('two_pointers.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.set_y(140)
    pdf.cell(0, 25, 'Three Pointers Percentage of Each Player', ln=True)
    pdf.image('three_pointers.jpg', x=50, y=pdf.get_y() + 5, w=100)
    pdf.add_page()

    pdf.cell(0, 25, 'Free Throws Percentage of Each Player:', ln=True)
    pdf.image('free_throws.jpg', x=50, y=pdf.get_y() + 5, w=100)

    return pdf


def create_graphs_team(dict_team_stats, df_reducido):

    sns.set_style('darkgrid')

    # TABLA CON LAS ESTADÍSTICAS DE EQUIPO:

    # Primero se crea un diccionario con aquellas estadísticas
    # relevantes que se van a almacenar en la tabla

    dict_tabla = {}
    for i in dict_team_stats:
        if dict_team_stats[i] != None and i!= 'OpponentStat':
            dict_tabla[i] = [dict_team_stats[i]]

    # Posteriormente se crea un dataframe con esas estadísticas
    # y se traspone para que quede con la forma de la tabla deseada

    df = pd.DataFrame(dict_tabla)
    df = df.transpose()
    df = df.rename(columns={0: 'Boston Celtics'})

    # Finalmente se crea y guarda el gráfico table con la información
    # contenida en el dataset

    fig = plt.figure(figsize=(10,10))
    ax = plt.subplot(48, 2, 1, frameon=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    pd.plotting.table(ax, data = df, loc = 'center')
    plt.savefig('team_stats_table.jpg', dpi=300, bbox_inches='tight')

    # PIE CHART CON LOS RESULTADOS GLOBALES DE LOS PARTIDOS:

    # Se crea un pie chart exclusivamente con la información del total
    # de partidos ganados y el total de partidos perdidos
    # A la gráfica se le añaden los porcentajes de ganados y
    # de perdidos

    fig = plt.figure(figsize=(7,7))
    plt.pie([dict_team_stats['Wins'], dict_team_stats['Losses']], labels=['Wins', 'Losses'], colors=['seagreen', 'darkseagreen'], autopct='%1.1f%%')
    plt.title('GLOBAL RESULTS OF MATCHES', fontsize = 20, fontweight = 'bold')
    plt.savefig('global_results.jpg', dpi=300, bbox_inches='tight')

    # BARPLOT CON LOS PORCENTAJES:

    # Primero se crea una lista con las categorías de los porcentajes
    # posteriormente se crea otra lista con los valores de dichos
    # porcentajes

    cat = ['TwoPointersPercentage', 'ThreePointersPercentage', 'FreeThrowsPercentage', 'TrueShootingPercentage']
    vals = []

    for c in cat:
        vals.append(dict_team_stats[c])

    # Se almacenan tanto los nombres como los valores en un dataframe
    # y se ordenan de mayor a menor

    datos=pd.DataFrame({'Percentages': cat,'Throws Percentage Stats': vals})
    datos = datos.sort_values('Throws Percentage Stats', ascending=False)

    # Se crea el barplot con la información contenida en el dataframe

    fig = plt.figure(figsize=(12,10))
    ax = sns.barplot(datos, y='Percentages', x='Throws Percentage Stats', orient='h', palette=sns.light_palette('seagreen', reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('SHOOTING PERCENTAGES', fontsize=20, fontweight='bold')
    plt.savefig('team_shooting_percentages.jpg', dpi=300, bbox_inches='tight')

    # BARPLOT CON LOS DOUBLES:

    # Primero se crea una lista con las categorías de los porcentajes
    # posteriormente se crea otra lista con los valores de dichos
    # porcentajes

    cat = ['DoubleDoubles', 'TripleDoubles']
    vals = []

    for c in cat:
        vals.append(dict_team_stats[c])

    # Se almacenan tanto los nombres como los valores en un dataframe
    # y se ordenan de mayor a menor

    datos = pd.DataFrame({'Doubles': cat,'doubles stats': vals})
    datos = datos.sort_values('doubles stats', ascending=False)

    # Se crea el barplot con la información contenida en el dataframe

    fig = plt.figure(figsize=(10,8))
    ax = sns.barplot(datos, x='Doubles', y='doubles stats', orient='v', palette=sns.light_palette('seagreen', reverse=True, n_colors=3))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('DOUBLES', fontsize=20, fontweight='bold')
    plt.savefig('doubles.jpg', dpi=300, bbox_inches='tight')

    # TABLA CON LAS ESTADÍSTICAS DE LOS JUGADORES:

    # Se crea una tabla con los valores de las estadísticas
    # más relevantes por jugador:

    fig = plt.figure(figsize=(40,5))
    ax = plt.subplot(1, 1, 1, frameon=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    pd.plotting.table(ax, data = df_reducido.transpose(), loc = 'center')
    plt.savefig('player_stats_table.jpg', dpi=300, bbox_inches='tight')

    # TOP 5 ANOTADORES DEL EQUIPO

    # Barplot con los cinco máximos anotadores de los celtics
    max_anotadores = df_reducido.nlargest(5, ['Points'])
    fig = plt.figure(figsize=(12,10))
    ax = sns.barplot(max_anotadores, y='Points', x='Name', orient='v', palette=sns.light_palette('seagreen', reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('TOP 5 SCORERS', fontsize=20, fontweight='bold')
    plt.savefig('top_5_scorers.jpg', dpi=300, bbox_inches='tight')

    # 5 JUGADORES QUE HAN MARCADO MENOS PUNTOS

    min_anotadores = df_reducido.nsmallest(5, ['Points'])
    fig = plt.figure(figsize=(12,10))
    ax = sns.barplot(min_anotadores, y='Points', x='Name', orient='v', palette=sns.light_palette('seagreen'))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('LEAST 5 SCORERS', fontsize=20, fontweight='bold')
    plt.savefig('least_5_scorers.jpg', dpi=300, bbox_inches='tight')

    # 5 MOST EFFICIENT PLAYERS ON THE TEAM

    # Barplot basado en el porcentage de eficiencia que muestra los cinco
    # jugadores más eficientes del equipo

    ef_rating = df_reducido.nlargest(5, ['PlayerEfficiencyRating'])
    fig = plt.figure(figsize=(12,10))
    ax = sns.barplot(ef_rating, y='PlayerEfficiencyRating', x='Name', orient='v', palette=sns.light_palette('seagreen', reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('MOST EFFICIENT PLAYERS', fontsize=20, fontweight='bold')
    plt.savefig('top_5_efficient.jpg', dpi=300, bbox_inches='tight')

    # 5 LEAST EFFICIENT PLAYERS ON THE TEAM

    # Barplot con los 5 jugadores con menor eficiencia del equipo

    ef_rating_min = df_reducido.nsmallest(5, ['PlayerEfficiencyRating'])
    fig = plt.figure(figsize=(12,10))
    ax = sns.barplot(ef_rating_min, y='PlayerEfficiencyRating', x='Name', orient='v', palette=sns.light_palette('seagreen', reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('LEAST EFFICIENT PLAYERS', fontsize=20, fontweight='bold')
    plt.savefig('least_5_efficient.jpg', dpi=300, bbox_inches='tight')

    # TWO POINTERS PERCENTAGE

    # Barplot con el porcentage de tiros de 2 anotados por cada
    # jugador y ordenado de mayor a menor porcentage

    fig = plt.figure(figsize=(12,10))
    ax = sns.barplot(df_reducido.sort_values('TwoPointersPercentage', ascending=False), x='TwoPointersPercentage', y='Name', orient='h', palette=sns.light_palette('seagreen', 24, reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('TWO POINTERS PERCENTAGE', fontsize=20, fontweight='bold')
    plt.savefig('two_pointers.jpg', dpi=300, bbox_inches='tight')

    # THREE POINTERS PERCENTAGE

    # Barplot con los jugadores ordenados en función de su porcentage
    # de tiros libres anotados esta temporada

    fig = plt.figure(figsize=(12,10))
    ax = sns.barplot(df_reducido.sort_values('ThreePointersPercentage', ascending=False), x='ThreePointersPercentage', y='Name', orient='h', palette=sns.light_palette('seagreen', 24,reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('THREE POINTERS PERCENTAGE', fontsize=20, fontweight='bold')
    plt.savefig('three_pointers.jpg', dpi=300, bbox_inches='tight')

    # FREE THROWS PERCENTAGE

    # Porcentage de tiros libres anotados por cada jugador representado
    # con un barplot ordenado de mayor a menor.

    fig = plt.figure(figsize=(12,10))
    ax = sns.barplot(df_reducido.sort_values('FreeThrowsPercentage', ascending=False), x='FreeThrowsPercentage', y='Name', orient='h', palette=sns.light_palette('seagreen', 24, reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('FREE THROWS', fontsize=20, fontweight='bold')
    plt.savefig('free_throws.jpg', dpi=300, bbox_inches='tight')


def load_api(pdf):

    # Se almacenan las estadísticas en el pdf

    pdf.output('celtics_stats.pdf')


def extract_prediction():

    # Se extrae el código html de la página web de una casa de apuestas

    r = requests.get('https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/')
    soup = BeautifulSoup(r.text,'lxml')

    return soup


def transform_prediction(soup):

    # Tras examinar detenidamente el código de la casa de apuestas
    # podemos apreciar que tanto el nombre del partido como las cuotas
    # se encuentran precedidas por la etiqueta "a".
    # También debemos de tener en cuenta que los partidos aparecen en el
    # código ordenados por orden cronológico y que las cuotas relacionadas
    # a un partido concreto se encuentran en líneas inferiores a la que
    # contiene el nombre del partido.

    # Vamos a buscar la primera vez que aparezca el nombre del equipo
    # ya que será en el nombre del próximo partido que vaya a disputar.
    # Una vez que se tiene el siguiente partido se buscan en las líneas
    # siguientes las cuotas de cada equipo, sabiendo que la primera
    # cuota que aparezca hará referencia al primer nombre que salga
    # en el título del partido y la segunda hará referencia al
    # segundo nombre. Por tanto, una vez tengamos el siguiente partido
    # los dos números que encontremos serán los de las cuotas.

    div_class = soup.find_all('a')
    match = []
    stats = []

    for a in div_class:

        # Buscamos el siguiente partido en el que uno de los equipos
        # que jueguen sean los Boston Celtics.

        encontrado = re.findall('Celtics',str(a.text), re.I)

        # Solo agregaremos el primero que encontremos ya que van en
        # órden cronológico.

        if encontrado != [] and len(match) < 1:
            match.append(str(a.text))

        # En caso de que ya hayamos encontrado el siguiente partido
        # buscamos los 2 siguientes números ya que serán las cuotas.

        if match != [] and len(stats) < 2:

            encontrado = re.findall('\d\.\d*',str(a.text), re.I)

            if encontrado != []:
                stats.append(float(encontrado[0]))

    # Sacamos los nombres de los 2 equipos.
    # Uno de ellos será los celtics y el otro su adversario.

    teams = match[0][1:-1].split(' - ')

    # El ganador será el de la cuota más baja:

    ind_winner = stats.index(min(stats))
    winner = teams[ind_winner]

    # Se devuelve el siguiente partido junto con el ganador
    return (match[0][1:-1], winner)


def load_prediction(prediction):

    # Se muestra la predicción del siguiente partido por pantalla

    print(f'La predicción para el partido {prediction[0]} es que el ganador',
            f'será {prediction[1]}')


if __name__ == '__main__':

    # ETL para obtener los datos de la API y cargarlos
    # en un pdf

    stats_list, player_lista = extract_api()
    pdf = transform_api(stats_list, player_lista)
    load_api(pdf)

    # ETL para obtener la predicción del siguiente
    # partido y mostrarla por pantalla.

    soup = extract_prediction()
    prediction = transform_prediction(soup)
    load_prediction(prediction)
