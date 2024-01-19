# Importar librerias
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from utils2 import Avance, Semestre, assign_group, fill_results_dict, medianNivel, retirosPorMateria
from plots import piecharts_por_materia, std_dev_plot, comparacionNivelPlot, graficaSumaRetiros, retiros_plot_resumido
from tqdm import tqdm
import warnings

# Ignorar todos los RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)

def load_cursos_obligatorios():

    with open("cursos_obligatorios.json", "r", encoding='utf-8') as json_file:
        cursos = json.load(json_file)

    return cursos

def soloIBIO_df (xlsx, mask):

    solo_IBIO = xlsx[mask]
    solo_IBIO = solo_IBIO.reset_index()

    return solo_IBIO

def IBIO_columns (solo_IBIO, pensum_courses):

    solo_IBIO['Periodo'] = solo_IBIO['Periodo'].astype(str).str[:5].astype(int)
    periodo = solo_IBIO["Periodo"]
    todosPeriodos = np.unique(periodo)

    solo_IBIO = solo_IBIO.drop('index', axis=1)
    solo_IBIO = solo_IBIO[solo_IBIO['Materia'].isin(pensum_courses)]
    solo_IBIO = solo_IBIO.reset_index()
    solo_IBIO = solo_IBIO.drop('index', axis=1)

    #Convert code to int
    solo_IBIO['Código est'] = solo_IBIO['Código est'].astype(int)

    #Add new column for each student with the year they enter to college
    solo_IBIO['Año Ingreso'] = solo_IBIO['Código est'].astype(str).str[:5].astype(int)

    solo_IBIO['Semestre'] = solo_IBIO.apply(Semestre, axis=1)
    solo_IBIO['Avance'] = solo_IBIO.apply(Avance, axis=1)

    solo_IBIO['Group'] = solo_IBIO['Avance'].apply(assign_group)

    return solo_IBIO, todosPeriodos

def mainMaterias(path, desired_program, directory_name):

    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    # Filtrar solo los estudiantes IBIO (primer programa)
        
    xlsx = pd.read_excel(path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    for i in tqdm(range(len(todosPeriodos)), desc="Processing Periods"):

        directory = f"{directory_name}/{todosPeriodos[i]}"

        if not os.path.exists(directory):
            os.makedirs(directory)
        
        for j in range(len(pensum_courses)):

            directory2 = f"{directory_name}/{todosPeriodos[i]}/{cursos[pensum_courses[j]][1]}"

            if not os.path.exists(directory2):
                os.makedirs(directory2)

            condition_materia = solo_IBIO['Materia']== pensum_courses[j]

            condition_anio = solo_IBIO['Periodo']== todosPeriodos[i]

            df_materia_anio = solo_IBIO.loc[condition_materia & condition_anio]

            # count the number of values in each group
            counts = df_materia_anio['Group'].value_counts()

            piecharts_por_materia (counts, cursos, pensum_courses, todosPeriodos, i, j,directory2)


def avanceNivel(path, desired_program, directory_name):

    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    xlsx = pd.read_excel(path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    results_dict = fill_results_dict(pensum_courses, solo_IBIO)

    directory = f"{directory_name}/Materias"

    if not os.path.exists(directory):
        os.makedirs(directory)

    max_n = 0
    max_mean, min_mean = 0, 0
    max_value, min_value = 0, 10
    min_desv, max_desv = 0, 0
    media_max , media_min = 0,10
    for course in results_dict.values():
        for semester in course.values():
            if semester['n'] > max_n:
                max_n = semester['n']
            if semester['mean'] > media_max:
                media_max = semester['mean']
            if semester['mean'] < media_min:
                media_min = semester['mean']
            if semester['std_dev']+ semester['mean'] > max_value:
                max_mean = semester['mean']
                max_desv = semester['std_dev']
                max_value = semester['std_dev']+ semester['mean']

            if  semester['mean'] - semester['std_dev']< min_value:
                min_mean = semester['mean']
                min_desv = semester['std_dev']
                min_value = semester['mean'] - semester['std_dev']

    for i in tqdm(range(len(pensum_courses)), desc="Graphics Creating"):

        directory = f'{directory_name}/Materias/{pensum_courses[i]}'

        if not os.path.exists(directory):
            os.makedirs(directory)

        std_dev_plot(results_dict, pensum_courses, min_value, max_mean, max_desv, cursos, i, directory_name)


    comparacionNivel (results_dict, max_n, media_min, media_max, directory_name)


def comparacionNivel (results_dict, max_n, media_min, media_max, directory_name):

    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    medias_niveles = medianNivel(results_dict)


    for i in range(len(pensum_courses)):

        x = list(results_dict[pensum_courses[i]].keys())
        x_list = [str(i) for i in x]
        y = [results_dict[pensum_courses[i]][year]['mean'] for year in x]
        n_est = [results_dict[pensum_courses[i]][year]['n'] for year in x]
        
        nivel_materia= int(pensum_courses[i][5])
        y_nivel = list(medias_niveles[nivel_materia].values())
        x_2 = list(medias_niveles[nivel_materia].keys())
        x_nivel = [str(i) for i in x_2]

        if len(x_list) != len(x_nivel):
            del x_nivel[0]
            del y_nivel[0]

        comparacionNivelPlot(directory_name, y,x_list, n_est, max_n, pensum_courses,i,x_nivel,y_nivel, nivel_materia,media_min, media_max, cursos)


def Retiros (path, original_path, desired_program, directory_name):

    excel_retiros = pd.read_excel(path)

    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    filtered_df = excel_retiros[excel_retiros['Materia'].isin(pensum_courses)]

    #retiros_count = {materia: {periodo[:5]: count for periodo, count in filtered_df[filtered_df['Materia'] == materia]['Periodo'].value_counts().items()} for materia in filtered_df['Materia'].unique()}

    retiros_count = {}

    unique_materias = filtered_df['Materia'].unique()

    for materia in unique_materias:
        retiros_count[materia] = {}
        
        materia_data = filtered_df[filtered_df['Materia'] == materia]
        materia_data['Periodo'] = materia_data['Periodo'].astype(str)

        periodos_counts = materia_data['Periodo'].value_counts().items()
        
        for periodo, count in periodos_counts:
            retiros_count[materia][periodo[:5]] = count

    xlsx = pd.read_excel(original_path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    results_dict = fill_results_dict (pensum_courses, solo_IBIO)

    medias_niveles = medianNivel(results_dict)

    max_n = 0
    max_value, min_value = 0, 10
    media_max , media_min = 0,10

    for course in results_dict.values():
        for semester in course.values():
            if semester['n'] > max_n:
                max_n = semester['n']
            if semester['mean'] > media_max:
                media_max = semester['mean']
            if semester['mean'] < media_min:
                media_min = semester['mean']
            if semester['std_dev']+ semester['mean'] > max_value:
                max_value = semester['std_dev']+ semester['mean']
            if  semester['mean'] - semester['std_dev']< min_value:
                min_value = semester['mean'] - semester['std_dev']
                        
    list_dict_retiros, list_dict_estudiantes, list_dict_avance = retirosPorMateria (pensum_courses, results_dict, medias_niveles, retiros_count, max_n, media_min, media_max, cursos, directory_name)

    ## Retiros promedio

    accumulated_retiros = {}
    accumulated_estudiantes = {}
    accumulated_avance = {}

    
    # loop over each iteration's dictionary
    for d in list_dict_retiros:
        # iterate over each key-value pair in the dictionary
        for key, value in d.items():
            # add the value to the running total for this key
            accumulated_retiros[key] = accumulated_retiros.get(key, 0) + value

    # loop over each iteration's dictionary
    for d in list_dict_estudiantes:
        # iterate over each key-value pair in the dictionary
        for key, value in d.items():
            # add the value to the running total for this key
            accumulated_estudiantes[key] = accumulated_estudiantes.get(key, 0) + value


    for d in list_dict_avance:
        # iterate over each key-value pair in the dictionary
        for key, value in d.items():
            # add the value to the running total for this key
            accumulated_avance[key] = accumulated_avance.get(key, 0) + value


    estudiantes_totales = list(accumulated_estudiantes.values())
    retiros_totales = list(accumulated_retiros.values())
    retiros_x = list(accumulated_retiros.keys())
    avance_general = list(accumulated_avance.values())
    semestres = list(accumulated_avance.keys())

    divisor = len(pensum_courses)

    result_list_retiros = []
    result_list_estudiantes = []
    result_list_avance = []

    for i in range(len(retiros_totales)):

        result_list_retiros.append(retiros_totales[i]/divisor)

    for i in range(len(estudiantes_totales)):
        result_list_estudiantes.append(estudiantes_totales[i]/divisor)
        result_list_avance.append(avance_general[i]/divisor)

    missing_values = [0, 0, 0, 0]
    o = missing_values + retiros_totales

    sum_list = [estudiantes_totales[i] + o[i] for i in range(len(estudiantes_totales))]

    graficaSumaRetiros(semestres, sum_list, retiros_x, retiros_totales, result_list_avance, directory_name)

def avance_cohortes(xlsx_cursos, xlsx_sancionados, desired_program, directory_name=None):
   
    cursos = load_cursos_obligatorios()
    pensum_courses = list(cursos.keys())     
    xlsx = pd.read_excel(xlsx_cursos)
    mask = xlsx['Programa principal'] == desired_program
    solo_IBIO = soloIBIO_df(xlsx, mask)
    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    #Todas las cohortes
    mean_dataframe=pd.DataFrame()
    desv_dataframe=pd.DataFrame()

    #Estudiantes sacionados
    sancionados_xlsx=pd.read_excel(xlsx_sancionados)
    sancionados=list(sancionados_xlsx["CÓDIGO"])
    sancionados_dict={}
    mean_sancionados=pd.DataFrame()
    desv_sancionados=pd.DataFrame()
    
    for i in tqdm(range(len(todosPeriodos)), desc="Processing Periods"):

        condicion_periodo = solo_IBIO['Periodo']==todosPeriodos[i]
        df_periodo=solo_IBIO[condicion_periodo]
        cohortes_periodo=np.unique(df_periodo['Año Ingreso'])
        cohortes_dict=dict.fromkeys(cohortes_periodo)
        for cohorte in cohortes_dict:
            cohortes_dict[cohorte]={}
            sancionados_dict[cohorte]={}

        estudiantes_periodo=np.unique(df_periodo['Código est'])
        for estudiante in estudiantes_periodo:
            semestre_ingreso=int(str(estudiante)[:5])
            cohortes_dict[semestre_ingreso][estudiante]=np.mean(df_periodo[df_periodo['Código est']==estudiante]["Avance"])
            if estudiante in sancionados:
                sancionados_dict[semestre_ingreso][estudiante]=np.mean(df_periodo[df_periodo['Código est']==estudiante]["Avance"])
            
        results={}

        for cohorte in cohortes_dict:

            results[cohorte]={">3":0,"3-2":0,"2-1":0,"1-0":0,"0-1":0,"-1-2":0,"-2-3":0}
            zero_values=[]

            for estudiante in cohortes_dict[cohorte]:
                if cohortes_dict[cohorte][estudiante]>=3:
                    results[cohorte][">3"]+=1
                elif 3>cohortes_dict[cohorte][estudiante]>=2:
                    results[cohorte]["3-2"]+=1
                elif 2>cohortes_dict[cohorte][estudiante]>=1:
                    results[cohorte]["2-1"]+=1
                elif 1>cohortes_dict[cohorte][estudiante]>=0:
                    results[cohorte]["1-0"]+=1
                elif 0>cohortes_dict[cohorte][estudiante]>=-1:
                    results[cohorte]["0-1"]+=1
                elif -1>cohortes_dict[cohorte][estudiante]>=-2:
                    results[cohorte]["-1-2"]+=1
                elif -2>cohortes_dict[cohorte][estudiante]>=-3:
                    results[cohorte]["-2-3"]+=1

            for key in results[cohorte]:
                if results[cohorte][key]==0:
                    zero_values.append(key)
            
            for zero_key in zero_values:
                del results[cohorte][zero_key]

            if directory_name != None:
                plot_avance_cohortes(todosPeriodos[i], results, directory_name)

        #Stadisticas cohorte

        for periodo in cohortes_dict:
            if periodo in todosPeriodos:
                semestre_actual=i-list(todosPeriodos).index(periodo)
                mean=np.mean(list(cohortes_dict[periodo].values()))
                desv=np.std(list(cohortes_dict[periodo].values()))
                mean_dataframe.loc[periodo,semestre_actual]=mean
                desv_dataframe.loc[periodo,semestre_actual]=desv

        for periodo in sancionados_dict:
            if periodo in todosPeriodos:
                semestre_actual=i-list(todosPeriodos).index(periodo)
                mean=np.mean(list(sancionados_dict[periodo].values()))
                desv=np.std(list(sancionados_dict[periodo].values()))
                mean_sancionados.loc[periodo,semestre_actual]=mean
                desv_sancionados.loc[periodo,semestre_actual]=desv

    return mean_dataframe, desv_dataframe, results, mean_sancionados, desv_sancionados, sancionados_dict

def plot_avance_cohortes(period, results, directory_name):

    group_colors_2 = {
    '>3': '#d3554c',
    '3-2': '#fc6c64',
    '2-1': '#feb268',
    '1-0': '#f7e16a',
    '0-1': '#ffe9af',
    '-1-2': '#d3e1a2',
    '-2-3': '#a9e070',
    }

    # plot a pie chart with the counts
    for anio in results:

        plt.figure(figsize=(10, 10))
        plt.style.use('ggplot')
        colors2 = [group_colors_2[group] for group in results[anio]]
        plt.pie(results[anio].values(), autopct=lambda x: f'{int(round(x/100.0*sum(results[anio].values())))}('+str(round(x,1))+"%)" ,colors=colors2,textprops={'fontsize':18}, explode=[0.05] * len(results[anio]))
        plt.title(f'Avance de los estudiantes ingresados en {anio}\n para el periodo {period}', fontdict={'fontsize':22, 'weight': 'bold'})
        legend = plt.legend(results[anio].keys(), prop={'size': 14})
        directory = f'{directory_name}/{period}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(f'{directory}/piechart_{str(anio)}.png')
        plt.cla()
        plt.close()

    all_cohortes = {">3":0,"3-2":0,"2-1":0,"1-0":0,"0-1":0,"-1-2":0,"-2-3":0}
    for anio in results:
        for key in results[anio]:
            all_cohortes[key]+=results[anio][key]
    
    all_cohortes = {key: value for key, value in all_cohortes.items() if value != 0}
    plt.figure(figsize=(10, 10))
    plt.style.use('ggplot')
    colors2 = [group_colors_2[group] for group in all_cohortes]
    plt.pie(all_cohortes.values(), autopct=lambda x: f'{int(round(x/100.0*sum(all_cohortes.values())))}('+str(round(x,1))+"%)" ,colors=colors2,textprops={'fontsize':14}, explode=[0.05] * len(all_cohortes))
    plt.title(f'Avance de todos los estudiantes en el periodo {period}', fontdict={'fontsize':22, 'weight': 'bold'})
    plt.legend(all_cohortes.keys())
    plt.savefig(f'{directory}/piechart_all_cohortes.png')
    plt.cla()
    plt.close()
    

def todosIBIO(xlsx):
        
    mask = xlsx['Programa principal'] == 'INGENIERIA BIOMEDICA'
    todos_IBIO = xlsx[mask]
    todos_IBIO = todos_IBIO.reset_index()
    todos_IBIO['Periodo'] = todos_IBIO['Periodo'].astype(str).str[:5].astype(int)
    todos_IBIO = todos_IBIO.drop('index', axis=1)
    todos_IBIO['Código est'] = todos_IBIO['Código est'].astype(int)
    todos_IBIO['Año Ingreso'] = todos_IBIO['Código est'].astype(str).str[:5].astype(int)

    return todos_IBIO

def n_estudiantes(xlsx_cursos, sancionados_xlsx, estudiantes_xlsx, desired_program):

    n_dataframe=pd.DataFrame()
    sancionados_xlsx=pd.read_excel(sancionados_xlsx)
    sancionados=list(sancionados_xlsx["CÓDIGO"])
    
    cursos = load_cursos_obligatorios()
    pensum_courses = list(cursos.keys())     
    xlsx = pd.read_excel(xlsx_cursos)
    mask = xlsx['Programa principal'] == desired_program
    solo_IBIO = soloIBIO_df(xlsx, mask)
    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)
    n_sancionados=pd.DataFrame([0]*len(todosPeriodos))
    n_sancionados.index = todosPeriodos
    todos_IBIO = todosIBIO(xlsx)

    for i in range(len(todosPeriodos)):
        condicion_periodo = todos_IBIO['Periodo']==todosPeriodos[i]
        df_periodo = todos_IBIO[condicion_periodo]
        for j in range(len(df_periodo)): 
            if df_periodo.iloc[j]['Año Ingreso'] in todosPeriodos:
                periodo = df_periodo.iloc[j]['Año Ingreso']
                condicion_semestre=df_periodo['Año Ingreso']==periodo
                df_estudiantes=df_periodo[condicion_semestre]
                estudiantes_unicos=np.unique(df_estudiantes['Código est'])
                n_estudiantes=len(estudiantes_unicos)
                semestre_actual=i-list(todosPeriodos).index(periodo)
                n_dataframe.loc[periodo,semestre_actual]=n_estudiantes
                contador_sancionados=0
                for codigo in estudiantes_unicos:
                    if codigo in sancionados:
                        contador_sancionados+=1
                n_sancionados.loc[periodo,semestre_actual]=contador_sancionados
    
    xlsx_estudiantes = pd.read_excel(estudiantes_xlsx, sheet_name=None)
    todosPeriodos = list(xlsx_estudiantes.keys())
    todosPeriodos = list(map(int, todosPeriodos))

    for sheet_name in xlsx_estudiantes:
        estudiantes = xlsx_estudiantes[sheet_name]
        IBIO = estudiantes['Programa principal'] == "INGENIERIA BIOMEDICA"
        estudiantes = estudiantes[IBIO].reset_index()
        periodos = np.unique(estudiantes["SemestreInicio"])
        for i in periodos:
            if i in todosPeriodos:
                semestre_actual=todosPeriodos.index(int(sheet_name))-todosPeriodos.index(i)
                conteo = estudiantes['SemestreInicio'].value_counts()[i]
                n_dataframe.loc[i,semestre_actual]=conteo

    mean_n_hist=[]

    for semestre in range(len(todosPeriodos)):
        n=[n_dataframe[semestre][x] for x in todosPeriodos if not np.isnan(n_dataframe[semestre][x])]
        mean_n_hist.append(np.mean(n))

    return n_dataframe, mean_n_hist, n_sancionados

def plot_n_cohortes(xlsx_cursos, n_dataframe, mean_n_hist, directory, desired_program):

    cursos = load_cursos_obligatorios()
    pensum_courses = list(cursos.keys())     
    xlsx = pd.read_excel(xlsx_cursos)
    mask = xlsx['Programa principal'] == desired_program
    solo_IBIO = soloIBIO_df(xlsx, mask)
    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    if not os.path.exists(directory):
        os.makedirs(directory)

    for periodo in todosPeriodos:
        plt.figure(figsize=(10,7.5))
        plt.style.use('ggplot')
        lim=sum([not np.isnan(n_dataframe.loc[periodo][x]) for x in range(len(todosPeriodos))])
        x_list=range(1,lim+1)
        n_list=n_dataframe.loc[periodo][:lim]
        plt.plot(x_list, mean_n_hist[:lim], 'o--', linewidth=0.8, label="N histórico", color="black")
        plt.plot(x_list, n_list, 'o--', linewidth=0.8, label="N cohorte", color='red')
        plt.xticks(x_list)
        plt.ylim((0,90))
        plt.xlabel('Semestre',fontsize=14)
        plt.ylabel('Número de estudiantes',fontsize=14)
        plt.legend(fontsize=12, loc=3)
        plt.title(f"Número de estudiantes cohorte {periodo}",fontsize=18)
        plt.savefig(f'{directory}/{periodo}_n.png')
        plt.cla()
        plt.close()

    # Gráfica de N para todas las cohortes juntas

    plt.figure(figsize=(10,7.5))
    plt.style.use('ggplot')
    colors_list=["maroon","firebrick","red","orange","gold","yellow","greenyellow","limegreen","green","darkgreen","darkslategray","darkcyan"]

    for i in range(len(todosPeriodos)):
        lim=sum([not np.isnan(n_dataframe.loc[todosPeriodos[i]][x]) for x in range(len(todosPeriodos))])
        x_list=range(1,lim+1)
        n_list=n_dataframe.loc[todosPeriodos[i]][:lim]
        plt.plot(x_list, n_list, 'o--', linewidth=0.8, label=todosPeriodos[i], color=colors_list[i])

    plt.plot(range(1,13), mean_n_hist, 'o--', linewidth=0.8, label="N histórico",color="black")
    plt.xticks(range(1,13))
    plt.xlabel('Semestre',fontsize=14)
    plt.ylabel('Número de estudiantes',fontsize=14)
    plt.legend(fontsize=12, loc=1)
    plt.title(f"N por cohorte",fontsize=18)
    plt.savefig(f'{directory}/cohortes_n.png')
    plt.cla()
    plt.close()

def historico_cohortes(xlsx_cursos, xlsx_sancionados, desired_program):

    cursos = load_cursos_obligatorios()
    pensum_courses = list(cursos.keys())
    xlsx = pd.read_excel(xlsx_cursos)
    mask = xlsx['Programa principal'] == desired_program
    solo_IBIO = soloIBIO_df(xlsx, mask)
    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    mean_dataframe, desv_dataframe, _, _, _, _ = avance_cohortes(xlsx_cursos, xlsx_sancionados, desired_program)
    mean_avance_hist=[]

    for semestre in range(len(todosPeriodos)):
        avance=[mean_dataframe[semestre][x] for x in todosPeriodos if not np.isnan(mean_dataframe[semestre][x])]
        mean_avance_hist.append(np.mean(avance))

    return mean_avance_hist

def plot_historico_cohortes(xlsx_cursos, xlsx_sancionados, mean_dataframe, desv_dataframe, mean_avance_hist, directory, desired_program):

    cursos = load_cursos_obligatorios()
    pensum_courses = list(cursos.keys())
    xlsx = pd.read_excel(xlsx_cursos)
    mask = xlsx['Programa principal'] == desired_program
    solo_IBIO = soloIBIO_df(xlsx, mask)
    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    mean_dataframe, desv_dataframe, _, _, _, _ = avance_cohortes(xlsx_cursos, xlsx_sancionados, desired_program)

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for periodo in todosPeriodos:
        plt.figure(figsize=(10,7.5))
        plt.style.use('ggplot')
        lim=sum([not np.isnan(mean_dataframe.loc[periodo][x]) for x in range(len(todosPeriodos))])
        x_list=range(1,lim+1)
        y_list=mean_dataframe.loc[periodo][:lim]
        y_err=desv_dataframe.loc[periodo][:lim]
        plt.plot(x_list, mean_avance_hist[:lim], 'o--', color='black', linewidth=0.8, label="Avance promedio histórico")
        plt.axhline(y=0, color="black", linewidth=0.8, linestyle='--')
        plt.errorbar(x_list, y_list, yerr=y_err, color='red', linewidth=0.8, fmt='o--', ecolor='black', label="Avance cohorte")
        plt.ylim((-1,5))
        plt.xticks(x_list)
        plt.xlabel('Semestre',fontsize=14)
        plt.ylabel('Avance Promedio',fontsize=14)
        plt.legend(fontsize=12, loc=2)
        avance_prom=np.round(np.mean(y_list),2)
        plt.title(f"Cohorte {periodo} (AP={avance_prom})",fontsize=18)
        plt.savefig(f'{directory}/{periodo}_avance.png')
        plt.cla()
        plt.close()

    # Grafica de avance para todas las cohortes juntas

    plt.figure(figsize=(10,7.5))
    plt.style.use('ggplot')
    tableau_colors=list(mcolors.TABLEAU_COLORS.values())
    additional_colors = ['cyan', 'magenta', 'yellow', 'black']
    colors_list = tableau_colors + additional_colors[:12 - len(tableau_colors)]

    for i in range(len(todosPeriodos)):
        lim=sum([not np.isnan(mean_dataframe.loc[todosPeriodos[i]][x]) for x in range(len(todosPeriodos))])
        x_list=range(1,lim+1)
        y_list=mean_dataframe.loc[todosPeriodos[i]][:lim]
        plt.plot(x_list, y_list, 'o--', linewidth=0.8, label=todosPeriodos[i], color=colors_list[i])
        plt.axhline(y=0, color="black", linewidth=0.8, linestyle='--')
        plt.ylim((-1,5))

    plt.xlabel('Semestre',fontsize=14)
    plt.ylabel('Avance Promedio',fontsize=14)
    plt.legend(fontsize=12, loc=2)
    plt.xticks(range(1,13))
    plt.title(f"Avance promedio por cohorte",fontsize=18)
    plt.savefig(f'{directory}/cohortes_avance.png')
    plt.cla()
    plt.close()


def sancionados(xlsx_cursos, directory, desired_program, xlsx_sancionados, xlsx_estudiantes):
    
    _, _, _, mean_sancionados, desv_sancionados, sancionados_dict = avance_cohortes(xlsx_cursos, xlsx_sancionados, desired_program)
    n_dataframe, mean_n_hist, n_sancionados = n_estudiantes(xlsx_cursos, xlsx_sancionados, xlsx_estudiantes, desired_program)
    mean_avance_hist = historico_cohortes(xlsx_cursos, xlsx_sancionados, desired_program)
    
    sancionados_xlsx=pd.read_excel(xlsx_sancionados)
    sancionados=list(sancionados_xlsx["CÓDIGO"])

    mean_sancionados_list=[]
    desv_sancionados_list=[]
    n_sancionados_list=[]
    for i in range(9):
        mean_sancionados_list.append(mean_sancionados[i].mean())
        desv_sancionados_list.append(desv_sancionados[i].mean())
        n_sancionados_list.append(n_sancionados[i].sum())

    # Gráfica de avance para sancionados
    if not os.path.exists(directory):
        os.makedirs(directory)

    plt.figure(figsize=(10,7.5))
    plt.style.use('ggplot')
    x_list=range(1,10)
    plt.axhline(y=0, color="black", linewidth=0.8, linestyle='--')
    plt.plot(x_list, mean_avance_hist[:9], 'o--', linewidth=0.8, label="Avance promedio histórico", color="black")
    plt.errorbar(x_list, mean_sancionados_list, yerr=desv_sancionados_list, color='red', linewidth=0.8, fmt='o--', ecolor='black', label="Avance promedio sancionados")
    plt.ylim((-1,5))
    plt.xticks(x_list)
    plt.xlabel('Semestre',fontsize=14)
    plt.ylabel('Avance Promedio',fontsize=14)
    plt.legend(fontsize=12, loc=2)
    avance_prom=np.round(np.mean(mean_sancionados_list),2)
    plt.title(f"Sancionados (AP={avance_prom})",fontsize=18)
    plt.savefig(f'{directory}/sancionados_avance.png')
    plt.cla()
    plt.close()

    # Gráfica de N para sancionados

    xlsx_estudiantes = pd.read_excel(xlsx_estudiantes, sheet_name=None)

    for sheet_name in xlsx_estudiantes:
        estudiantes = xlsx_estudiantes[sheet_name]
        IBIO = estudiantes['Programa principal'] == "INGENIERIA BIOMEDICA"
        estudiantes = estudiantes[IBIO].reset_index()
        for estudiante in estudiantes["Código est"]:
            if estudiante in sancionados:
                n_sancionados.loc[int(sheet_name)]+=1

    plt.figure(figsize=(10,7.5))
    plt.style.use('ggplot')
    x_list=range(1,13)
    plt.plot(x_list, mean_n_hist, 'o--', linewidth=0.8, label="N histórico", color="black")
    plt.plot(x_list, list(n_sancionados.T.loc[0]), 'o--', linewidth=0.8, label="N sancionados", color="red")
    plt.xlabel('Semestre',fontsize=14)
    plt.ylabel('Número de estudiantes',fontsize=14)
    plt.title(f"Estudiantes sancionados",fontsize=18)
    plt.xticks(x_list,list(n_sancionados.T))
    plt.legend(fontsize=12, loc=3)
    plt.savefig(f'{directory}/sancionados_n.png')

    plt.cla()
    plt.close() 