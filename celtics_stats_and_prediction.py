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
        self.image('logo.svg', x=50, y=120, w=100)


def handler_signal(signal,frame):

    # Salida controlada del programa en caso de pulsar
    # control C

    print("Salida ordenada del sistema")

    sys.exit(1)


signal.signal(signal.SIGINT, handler_signal)


def extract_api(fichero):

    # Se extrae la información sobre las estadísticas de todos los equipos
    # de una API de deportes.

    # Para poder accerder hay que cambiar 'xxxxxxxxxxx' por la clave que
    # nos asigna la API al registrarnos

    with open(fichero, 'r') as f:
        texto = f.read()

    key = eval(texto)['key']

    headers = {
            'Ocp-Apim-Subscription-Key': key
            }

    # Recibimos las respuestas y estas se almacenan en una lista con diccionarios
    # donde cada diccionario contendrá las estadísticas de un equipo.

    response_stats = requests.get("https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/2022", headers=headers)
    stats_list = response_stats.json()

    # Además de las estadísticas del equipo se extraen también las
    # estadísticas individuales de cada uno de sus jugadores

    response_players = requests.get('https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2022/BOS', headers=headers)
    players_lista = response_players.json()

    # Obtenemos y almacenamos el logo del equipo
    logo = open('logo.svg', 'wb')
    a = requests.get('https://upload.wikimedia.org/wikipedia/en/8/8f/Boston_Celtics.svg')
    logo.write(a.content)
    logo.close()

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
    pdf.image('player_stats_table.jpg', x=10, y=pdf.get_y() + 5, w=190, h=250)
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

    fig, ax = plt.subplots(figsize=(10, 15))
    ax.axis('off')
    ax.table(
             cellText=df.values,
             colLabels=df.columns.values,
             rowLabels=df.index.tolist(),
             rowColours=['#c2e5d2']*len(df.index.tolist()),
             cellLoc='center',
             loc='center',
             colColours=['#91d1ae']*len(df.columns.values.tolist()),
             colWidths=[0.7, 0.5]
            )
    plt.savefig('team_stats_table.jpg', dpi=300)


    # PIE CHART CON LOS RESULTADOS GLOBALES DE LOS PARTIDOS:

    # Se crea un pie chart exclusivamente con la información del total
    # de partidos ganados y el total de partidos perdidos
    # A la gráfica se le añaden los porcentajes de ganados y
    # de perdidos

    plt.figure(figsize=(7,7))
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

    plt.figure(figsize=(12,10))
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

    plt.figure(figsize=(10,8))
    ax = sns.barplot(datos, x='Doubles', y='doubles stats', orient='v', palette=sns.light_palette('seagreen', reverse=True, n_colors=3))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('DOUBLES', fontsize=20, fontweight='bold')
    plt.savefig('doubles.jpg', dpi=300, bbox_inches='tight')

    # TABLA CON LAS ESTADÍSTICAS DE LOS JUGADORES:

    # Se crea una tabla con los valores de las estadísticas
    # más relevantes por jugador:

    fig, ax = plt.subplots(figsize=(40, 20))
    ax.axis('off')
    ax.table(
             cellText=df_reducido.transpose().values,
             colLabels=df_reducido.transpose().columns.values,
             rowLabels=df_reducido.transpose().index.tolist(),
             rowColours=['#c2e5d2']*len(df_reducido.transpose().index.tolist()),
             cellLoc='center',
             loc='center',
             colColours=['#91d1ae']*len(df_reducido.transpose().columns.values.tolist())
            )
    plt.savefig('player_stats_table.jpg', dpi=300)

    # TOP 5 ANOTADORES DEL EQUIPO

    # Barplot con los cinco máximos anotadores de los celtics
    max_anotadores = df_reducido.nlargest(5, ['Points'])
    plt.figure(figsize=(12,10))
    ax = sns.barplot(max_anotadores, y='Points', x='Name', orient='v', palette=sns.light_palette('seagreen', reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('TOP 5 SCORERS', fontsize=20, fontweight='bold')
    plt.savefig('top_5_scorers.jpg', dpi=300, bbox_inches='tight')

    # 5 JUGADORES QUE HAN MARCADO MENOS PUNTOS

    min_anotadores = df_reducido.nsmallest(5, ['Points'])
    plt.figure(figsize=(12,10))
    ax = sns.barplot(min_anotadores, y='Points', x='Name', orient='v', palette=sns.light_palette('seagreen'))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('LEAST 5 SCORERS', fontsize=20, fontweight='bold')
    plt.savefig('least_5_scorers.jpg', dpi=300, bbox_inches='tight')

    # 5 MOST EFFICIENT PLAYERS ON THE TEAM

    # Barplot basado en el porcentage de eficiencia que muestra los cinco
    # jugadores más eficientes del equipo

    ef_rating = df_reducido.nlargest(5, ['PlayerEfficiencyRating'])
    plt.figure(figsize=(12,10))
    ax = sns.barplot(ef_rating, y='PlayerEfficiencyRating', x='Name', orient='v', palette=sns.light_palette('seagreen', reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('MOST EFFICIENT PLAYERS', fontsize=20, fontweight='bold')
    plt.savefig('top_5_efficient.jpg', dpi=300, bbox_inches='tight')

    # 5 LEAST EFFICIENT PLAYERS ON THE TEAM

    # Barplot con los 5 jugadores con menor eficiencia del equipo

    ef_rating_min = df_reducido.nsmallest(5, ['PlayerEfficiencyRating'])
    plt.figure(figsize=(12,10))
    ax = sns.barplot(ef_rating_min, y='PlayerEfficiencyRating', x='Name', orient='v', palette=sns.light_palette('seagreen', reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('LEAST EFFICIENT PLAYERS', fontsize=20, fontweight='bold')
    plt.savefig('least_5_efficient.jpg', dpi=300, bbox_inches='tight')

    # TWO POINTERS PERCENTAGE

    # Barplot con el porcentage de tiros de 2 anotados por cada
    # jugador y ordenado de mayor a menor porcentage

    plt.figure(figsize=(12,10))
    ax = sns.barplot(df_reducido.sort_values('TwoPointersPercentage', ascending=False), x='TwoPointersPercentage', y='Name', orient='h', palette=sns.light_palette('seagreen', 24, reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('TWO POINTERS PERCENTAGE', fontsize=20, fontweight='bold')
    plt.savefig('two_pointers.jpg', dpi=300, bbox_inches='tight')

    # THREE POINTERS PERCENTAGE

    # Barplot con los jugadores ordenados en función de su porcentage
    # de tiros libres anotados esta temporada

    plt.figure(figsize=(12,10))
    ax = sns.barplot(df_reducido.sort_values('ThreePointersPercentage', ascending=False), x='ThreePointersPercentage', y='Name', orient='h', palette=sns.light_palette('seagreen', 24,reverse=True))
    ax.bar_label(ax.containers[0], padding=5)
    plt.title('THREE POINTERS PERCENTAGE', fontsize=20, fontweight='bold')
    plt.savefig('three_pointers.jpg', dpi=300, bbox_inches='tight')

    # FREE THROWS PERCENTAGE

    # Porcentage de tiros libres anotados por cada jugador representado
    # con un barplot ordenado de mayor a menor.

    plt.figure(figsize=(12,10))
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

    # En primer lugar extraemos todos los partidos ya que, tras
    # examinar la página detenidamente podemos ver que
    # siempre se encuentran dentro de una clase concreta

    partidos = soup.find_all(
                             'div',
                             {
                                'class': 'cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative'
                             }
                            )

    # Para cada uno de los partidos buscamos la palabra Celtics
    stats = []

    for partido in partidos:

        texto = partido.text
        encontrado = re.findall('Boston Celtics', texto)

        # En caso de que el partido sea de los Celtics
        # se buscaran las cuotas y se agregarán a la lista de stats
        # y se agregará el nombre del partido

        if encontrado:

            match = partido.find_all('a', {'class':''})[0].text
            cuotas = partido.find_all('span', {'class':'px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base'})

            for cuota in cuotas:
                stats.append(cuota.text)
            break

    if len(partidos) > 0:
        # Limpiamos para obtener el nombre de los equipos
        teams = match[1:-1].split(' - ')

        # El ganador será el de la cuota más baja:
        ind_winner = stats.index(min(stats))
        winner = teams[ind_winner]

        # Se devuelve el siguiente partido junto con el ganador
        return (match[1:-1], winner)

    else:
        return None


def load_prediction(prediction):

    if prediction:
        # Se muestra la predicción del siguiente partido por pantalla

        print(f'La predicción para el partido {prediction[0]} es que el ganador',
              f'será {prediction[1]}')

    else:
        print('No se ha encontrado el siguiente partido del equipo')


if __name__ == '__main__':

    # ETL para obtener los datos de la API y cargarlos
    # en un pdf

    config = 'config.txt'

    stats_list, player_lista = extract_api(config)
    pdf = transform_api(stats_list, player_lista)
    load_api(pdf)

    # ETL para obtener la predicción del siguiente
    # partido y mostrarla por pantalla.

    soup = extract_prediction()
    prediction = transform_prediction(soup)
    load_prediction(prediction)
