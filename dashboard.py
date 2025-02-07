# Importar librerias
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from utils import Avance, Semestre, assign_group, fill_results_dict, medianNivel, retirosPorMateria, assign_group2
from plots import piecharts_por_materia, std_dev_plot, comparacionNivelPlot, graficaSumaRetiros, retiros_plot_resumido
from tqdm import tqdm
import warnings
import openpyxl
import math

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

    solo_IBIO['Periodo'] = pd.to_numeric(solo_IBIO['Periodo'].astype(str).str[:5], errors='coerce').astype('Int64') #Si hay valores no convertibles a int, se convierten a NaN sin lanzar error
    periodo = solo_IBIO["Periodo"]
    todosPeriodos = np.unique(periodo.dropna()) # Eliminar NaN antes de obtener valores únicos

    solo_IBIO = solo_IBIO.drop('index', axis=1, errors='ignore') # Evita error si 'index' no existe
    solo_IBIO = solo_IBIO[solo_IBIO['Materia'].isin(pensum_courses)]
    solo_IBIO = solo_IBIO.reset_index(drop=True)

    #Convert code to int
    solo_IBIO['Código est'] = pd.to_numeric(solo_IBIO['Código est'], errors='coerce').astype('Int64')

    #Add new column for each student with the year they enter to college
    solo_IBIO['Año Ingreso'] = pd.to_numeric(solo_IBIO['Código est'].astype(str).str[:5], errors='coerce').astype('Int64')

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

    result_df = pd.DataFrame(index=pensum_courses, columns=todosPeriodos, dtype=int)


    for i in tqdm(range(len(todosPeriodos)), desc="Procesando periodos académicos"):

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

            num_rows = df_materia_anio.shape[0]

            # Save the number of rows in the result_df
            result_df.at[pensum_courses[j], todosPeriodos[i]] = num_rows

            # count the number of values in each group
            counts = df_materia_anio['Group'].value_counts()

            piecharts_por_materia (counts, cursos, pensum_courses, todosPeriodos, i, j,directory2)

  
    # Save the result_df to an Excel file
    excel_file_path = f"{directory_name}/students_counts.xlsx"
    result_df.to_excel(excel_file_path)

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

    for i in tqdm(range(len(pensum_courses)), desc="Creando gráficas"):

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
        materia_data.loc[:, 'Periodo'] = materia_data['Periodo'].astype(str)

        periodos_counts = materia_data['Periodo'].value_counts().items()
        
        for periodo, count in periodos_counts:
            retiros_count[materia][periodo[:5]] = count

    xlsx = pd.read_excel(original_path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    results_dict = fill_results_dict (pensum_courses, solo_IBIO)

    periodos = todosPeriodos.tolist()
    # Iterate through each key in results_dict
    sorted_results_dict = {}

    for subject_code in results_dict:
        # Sort the sub-dictionary based on the order of years
        sorted_keys = sorted(results_dict[subject_code].keys(), key=lambda x: periodos.index(x))
        sorted_sub_dict = {sub_key: results_dict[subject_code][sub_key] for sub_key in sorted_keys}
        sorted_results_dict[subject_code] = sorted_sub_dict

    medias_niveles = medianNivel(sorted_results_dict)

    max_n = 0
    max_value, min_value = 0, 10
    media_max , media_min = 0,10

    for course in sorted_results_dict.values():
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
    
    list_dict_retiros, list_dict_estudiantes, list_dict_avance = retirosPorMateria (pensum_courses, results_dict, medias_niveles, retiros_count, max_n, media_min, media_max, cursos, directory_name, todosPeriodos)

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

  
    semesters_ordered = sorted(accumulated_avance.keys(), key=lambda x: int(x))
 
    accumulated_avance = {key: accumulated_avance[key] for key in semesters_ordered if key in accumulated_avance}
    accumulated_retiros = {key: accumulated_retiros[key] for key in semesters_ordered if key in accumulated_retiros}
    accumulated_estudiantes = {key: accumulated_estudiantes[key] for key in semesters_ordered if key in accumulated_estudiantes}

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

    ##ESTO ES PROVISIONAL PARA EL INICIO DE 2024-10 PORQUE NO HAY INFO DE RETIROS AUN
    o.append(0)

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
    n_sancionados_dict={}
    
    for i in tqdm(range(len(todosPeriodos)), desc="Procesando periodos académicos"):

        condicion_periodo = solo_IBIO['Periodo']==todosPeriodos[i]
        df_periodo=solo_IBIO[condicion_periodo]
        cohortes_periodo=np.unique(df_periodo['Año Ingreso'])
        cohortes_dict=dict.fromkeys(cohortes_periodo)
        for cohorte in cohortes_dict:
            cohortes_dict[cohorte]={}

        estudiantes_periodo=np.unique(df_periodo['Código est'])
        for estudiante in estudiantes_periodo:
            semestre_ingreso=int(str(estudiante)[:5])
            cohortes_dict[semestre_ingreso][estudiante]=np.mean(df_periodo[df_periodo['Código est']==estudiante]["Avance"])
            if estudiante in sancionados:
                if semestre_ingreso not in sancionados_dict:
                    sancionados_dict[semestre_ingreso]={}
                if i not in sancionados_dict[semestre_ingreso]:
                    sancionados_dict[semestre_ingreso][i]=[]
                sancionados_dict[semestre_ingreso][i].append(np.mean(df_periodo[df_periodo['Código est']==estudiante]["Avance"]))
                if i not in n_sancionados_dict:
                    n_sancionados_dict[i]=1
                else:
                    n_sancionados_dict[i]+=1

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

    #Stadisticas sancionados
    for i in range(len(todosPeriodos)):
        for cohorte in sancionados_dict:
            if todosPeriodos[i] > cohorte:
                semestre_actual= i-list(todosPeriodos).index(cohorte)
                if i in sancionados_dict[cohorte]:
                    mean=np.mean(sancionados_dict[cohorte][i])
                    desv=np.std(sancionados_dict[cohorte][i])
                else:
                    mean=0
                    desv=0
                mean_sancionados.loc[cohorte,semestre_actual]=mean
                desv_sancionados.loc[cohorte,semestre_actual]=desv

    return mean_dataframe, desv_dataframe, results, mean_sancionados, desv_sancionados, n_sancionados_dict

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

    # plot a 2 chart with the counts
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
        plt.ylim((0,100))
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
    colors_list=list(mcolors.CSS4_COLORS.keys())
    dark_colors = [color for color in colors_list if "dark" in color]

    for i in range(len(todosPeriodos)):
        lim=sum([not np.isnan(n_dataframe.loc[todosPeriodos[i]][x]) for x in range(len(todosPeriodos))])
        x_list=range(1,lim+1)
        n_list=n_dataframe.loc[todosPeriodos[i]][:lim]
        plt.plot(x_list, n_list, 'o--', linewidth=0.8, label=todosPeriodos[i], color=dark_colors[i])

    plt.plot(range(1,len(todosPeriodos)+1), mean_n_hist, 'o--', linewidth=0.8, label="N histórico",color="black")
    plt.xticks(range(1,len(todosPeriodos)+1))
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
    
    max_avance=0
    for periodo in todosPeriodos:
        plt.figure(figsize=(10,7.5))
        plt.style.use('ggplot')
        lim=sum([not np.isnan(mean_dataframe.loc[periodo][x]) for x in range(len(todosPeriodos))])
        x_list=range(1,lim+1)
        y_list=mean_dataframe.loc[periodo][:lim]
        max_avance=max(max_avance,max(y_list))
        y_err=desv_dataframe.loc[periodo][:lim]
        plt.plot(x_list, mean_avance_hist[:lim], 'o--', color='black', linewidth=0.8, label="Avance promedio histórico")
        plt.axhline(y=0, color="black", linewidth=0.8, linestyle='--')
        plt.errorbar(x_list, y_list, yerr=y_err, color='red', linewidth=0.8, fmt='o--', ecolor='black', label="Avance cohorte")
        plt.ylim((-1,math.ceil(max_avance)))
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
    colors_list=list(mcolors.CSS4_COLORS.keys())
    dark_colors = [color for color in colors_list if "dark" in color]

    max_avance=0
    for i in range(len(todosPeriodos)):
        lim=sum([not np.isnan(mean_dataframe.loc[todosPeriodos[i]][x]) for x in range(len(todosPeriodos))])
        x_list=range(1,lim+1)
        y_list=mean_dataframe.loc[todosPeriodos[i]][:lim]
        plt.plot(x_list, y_list, 'o--', linewidth=0.8, label=todosPeriodos[i], color=dark_colors[i])
        plt.axhline(y=0, color="black", linewidth=0.8, linestyle='--')
        max_avance=max(max_avance, max(y_list))
     
    plt.ylim((-1,math.ceil(max_avance)))
    plt.xlabel('Semestre',fontsize=14)
    plt.ylabel('Avance Promedio',fontsize=14)
    plt.legend(fontsize=12, loc=2)
    plt.xticks(range(1,len(todosPeriodos)+1))
    plt.title(f"Avance promedio por cohorte",fontsize=18)
    plt.savefig(f'{directory}/cohortes_avance.png')
    plt.cla()
    plt.close()


def sancionados(xlsx_cursos, directory, desired_program, xlsx_sancionados):
    
    cursos = load_cursos_obligatorios()
    pensum_courses = list(cursos.keys())
    xlsx = pd.read_excel(xlsx_cursos)
    mask = xlsx['Programa principal'] == desired_program
    solo_IBIO = soloIBIO_df(xlsx, mask)
    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)
    todosPeriodos = list(todosPeriodos)

    _, _, _, mean_sancionados, desv_sancionados, n_sancionados_dict = avance_cohortes(xlsx_cursos, xlsx_sancionados, desired_program)
    mean_avance_hist = historico_cohortes(xlsx_cursos, xlsx_sancionados, desired_program)
    mean_sancionados_list=[]
    desv_sancionados_list=[]

    #Se usa el úlitmo periodo en el cual hubo estudiantes sancionados
    ultimo_periodo = len(mean_sancionados.columns)

    for i in range(1,ultimo_periodo+1):
        mean_sancionados_list.append(mean_sancionados[i].mean())
        desv_sancionados_list.append(desv_sancionados[i].mean())

    # Gráfica de avance para sancionados
    if not os.path.exists(directory):
        os.makedirs(directory)

    plt.figure(figsize=(10,7.5))
    plt.style.use('ggplot')
    x_list=mean_sancionados.columns
    plt.axhline(y=0, color="black", linewidth=0.8, linestyle='--')
    plt.plot(x_list, mean_avance_hist[1:ultimo_periodo+1], 'o--', linewidth=0.8, label="Avance promedio histórico", color="black")
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
    plt.figure(figsize=(10,7.5))
    plt.style.use('ggplot')
    x_list=[str(todosPeriodos[periodo]) for periodo in n_sancionados_dict]
    y_list = list(n_sancionados_dict.values())
    rango = list(range(len(y_list)))
    plt.bar(rango, y_list, color="red")
    plt.ylabel('Número de estudiantes',fontsize=14)
    plt.title(f"Estudiantes sancionados",fontsize=18)
    plt.xticks(rango, x_list, rotation=45)
    plt.savefig(f'{directory}/sancionados_n.png')

    plt.cla()
    plt.close() 

def general_plots(xlsx_estudiantes, mean_avance_hist, mean_n_hist, directory_name):

    estudiantes = openpyxl.load_workbook(xlsx_estudiantes)
    semestres = estudiantes.sheetnames
    n_semestres = list(range(len(semestres)))

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    plt.style.use('ggplot')
    fig, ax1 = plt.subplots(figsize=(10, 7))
    ax1.bar(n_semestres, mean_n_hist, color="cornflowerblue", width=0.38, label='Estudiantes totales')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
            fancybox=True, shadow=True, ncol=5)
    plt.xlabel('Semestre')
    plt.ylabel('Número de estudiantes')
    ax2 = ax1.twinx()
    ax2.plot(n_semestres, mean_avance_hist,'--o', label='Avance general',linewidth=0.8, color='red')
    ax2.grid(False)
    plt.ylabel('Avance promedio')
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title('GRÁFICA GENERAL POR SEMESTRES', fontsize=18, fontweight='bold')
    plt.legend()
    plt.savefig(f'{directory_name}/grafica_general_semestre.png', bbox_inches='tight')
    plt.cla()   
    plt.close()

def estudiantesUnicosConAvance (original_path, desired_program, directory_name):

    os.makedirs(directory_name, exist_ok=True)

    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    xlsx = pd.read_excel(original_path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    unique_df = solo_IBIO.groupby(['Código est', 'Periodo']).agg({'Avance': 'mean'}).reset_index()

    unique_df['Group'] = unique_df['Avance'].apply(assign_group2)

    period_counts = unique_df['Periodo'].value_counts().to_dict()

    sorted_periods = sorted(period_counts.keys())
    
    sorted_period_counts = {period: period_counts[period] for period in sorted_periods}
    
    group_counts = unique_df.groupby(['Periodo', 'Group']).size().unstack(fill_value=0)

    group_colors = {
    '>= +3': 'darkred',
    '[+2, +3)': 'orangered',
    '[+1, +2)': 'orange',
    '[+0, +1)': 'gold',
    '[-1, +0)': 'yellowgreen',
    '[-2, -1)': 'green',
    '<= -2': 'darkgreen',

}

    plt.style.use('ggplot')
    

    fig, ax1 = plt.subplots(figsize=(14, 8))


    x_pos = [i for i, _ in enumerate(todosPeriodos)]


    ax1.bar([i - 0.0 for i in x_pos], sorted_period_counts.values(), color="cornflowerblue", width=0.38)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(todosPeriodos)

    ax2 = ax1.twinx()


    for group in group_counts.columns:

        color = group_colors.get(group, 'black') 

        group_counts_list = group_counts[group].tolist()
 
        ax2.plot(x_pos,  group_counts_list, label=group, color=color, linewidth=2)

    max_y = max(ax1.get_ylim()[1], ax2.get_ylim()[1])

    average_line = np.mean(group_counts.values, axis=1)

    # Plot the average line
    ax2.plot(x_pos, average_line, label='Average', color='black', linestyle='--', linewidth=2)


    # Set the same y-axis limits for both axes
    ax1.set_ylim(0, max_y)
    ax2.set_ylim(0, max_y)

    ax2.grid(False)

    # Adding labels and title
    ax1.set_xlabel('Periodo')
    ax1.set_ylabel('Número de estudiantes')
    plt.title('Estudiantes Únicos con Avance por Periodo', fontsize=18, fontweight='bold')
    #plt.legend()
    
    plt.savefig(f'{directory_name}/estudiantes_unicos_con_avance_por_periodo.png')


def estudiantesUnicosPorPeriodo (original_path, desired_program, directory_name):

    os.makedirs(directory_name, exist_ok=True)

    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    xlsx = pd.read_excel(original_path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO, todosPeriodos = IBIO_columns(solo_IBIO, pensum_courses)

    unique_df = solo_IBIO.groupby(['Código est', 'Periodo']).agg({'Avance': 'mean'}).reset_index()

    unique_df['Group'] = unique_df['Avance'].apply(assign_group2)

    period_counts = unique_df['Periodo'].value_counts().to_dict()

    sorted_periods = sorted(period_counts.keys())
    
    sorted_period_counts = {period: period_counts[period] for period in sorted_periods}

    group_counts = unique_df.groupby(['Periodo', 'Group']).size().unstack(fill_value=0)

    group_colors = {
    '>= +3': 'darkred',
    '[+2, +3)': 'orangered',
    '[+1, +2)': 'orange',
    '[+0, +1)': 'gold',
    '[-1, +0)': 'yellowgreen',
    '[-2, -1)': 'green',
    '<= -2': 'darkgreen'}
    
    plt.style.use('ggplot')

    mean_avance_per_year = unique_df.groupby('Periodo')['Avance'].mean()

    fig, ax2 = plt.subplots(figsize=(14, 8))

    x_pos = [i for i, _ in enumerate(todosPeriodos)]

    ax2.bar([i - 0.0 for i in x_pos], sorted_period_counts.values(), color="cornflowerblue", width=0.38)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(todosPeriodos)

    bottom = np.zeros(len(sorted_periods))

    for period in sorted_periods:

        period_group_counts = group_counts.loc[period].sort_values(ascending=False)

        # Define the order of colors based on your specified order

        color_order = ['darkgreen', 'green', 'yellowgreen', 'gold', 'orange', 'orangered', 'darkred']

        # Iterate over colors in the specified order
        for color in color_order:

            for group, count in period_group_counts.items():

                if group_colors.get(group) == color:  # Check if the color matches the current one in the order
                    ax2.bar(x_pos[sorted_periods.index(period)], count, bottom=bottom[sorted_periods.index(period)], label=group, color=color, width=0.42)
                    bottom[sorted_periods.index(period)] += count
                    break  # Break once the bar is plotted with the correct color to avoid plotting duplicates

    ax2.grid(True)

    # Adding labels and title
    ax2.set_xlabel('Periodo')
    ax2.set_ylabel('Número de estudiantes')
    plt.title('Estudiantes Únicos por Periodo', fontsize=18, fontweight='bold')
    
    plt.savefig(f'{directory_name}/estudiantes_unicos_por_periodo.png')

    fig, ax2 = plt.subplots(figsize=(14, 8))

    x_pos = np.arange(len(todosPeriodos))

     # Define the order of colors based on your specified order
    color_order = ['darkgreen', 'green', 'yellowgreen', 'gold', 'orange', 'orangered', 'darkred']
    stacks = {color: np.zeros(len(todosPeriodos)) for color in color_order}

    # Procesar los datos para cada periodo
    for period_idx, period in enumerate(sorted_periods):
        period_group_counts = group_counts.loc[period].sort_values(ascending=False)

        total_height = sum(period_group_counts)
        previous_height = np.zeros(len(todosPeriodos))

        for color in color_order:
            for group, count in period_group_counts.items():
                if group_colors.get(group) == color:
                    normalized_height = (count / total_height) * 100

                    # Acumular las alturas para el área correspondiente al color actual
                    stacks[color][period_idx] = normalized_height + previous_height[period_idx]
                    previous_height[period_idx] += normalized_height
                    break

    keys_inverted = list(stacks.keys())[::-1]  # Obtiene las llaves en orden inverso
    colors_inverted = [stacks[key] for key in keys_inverted]  # Obtiene los valores en el mismo orden inverso

    # Traza cada área en el orden invertido
    for color, heights in zip(keys_inverted, colors_inverted):
        bottoms = np.zeros_like(x_pos, dtype=float)
        ax2.stackplot(x_pos, bottoms, heights, labels=[color], colors=[color])

    ax2.grid(True)

    # Plot the average as area
    ax3 = ax2.twinx()
    ax3.fill_between(x_pos, 0, mean_avance_per_year.tolist(), label='Average', color='grey', alpha=0.5)
    ax3.set_ylabel('Avance promedio')
    ax3.set_ylim(0,2.75)
    ax2.set_ylim(0,100*(1.1))
    ax3.grid(False)

    # Plot the average line
    ax3 = ax2.twinx()
    ax3.plot(x_pos, mean_avance_per_year.tolist(), label='Average', color='black', linestyle='--', marker='o' , linewidth=2)
    ax3.set_ylabel('Avance promedio')
    ax3.set_ylim(0,2.75)
    ax2.set_ylim(0,100*(1.1))
    ax3.grid(False)

    # Adding labels and title
    ax2.set_xlabel('Periodo')
    ax2.set_ylabel('Número de estudiantes')
    plt.title('Estudiantes Únicos con Avance por Periodo', fontsize=18, fontweight='bold')
    #plt.legend()
    
    plt.savefig(f'{directory_name}/estudiantes_unicos_con_avance_por_periodo.png')


def PoblacionEstudiantesUnicos(xlsx_cursos, desired_program, directory_name):

    cursos = load_cursos_obligatorios()
    pensum_courses = list(cursos.keys())     
    xlsx = pd.read_excel(xlsx_cursos)
    solo_IBIO, todosPeriodos = IBIO_columns(xlsx, pensum_courses)
    
    # Asegurar que no haya duplicados en "Código est" al contar estudiantes
    df_unique = solo_IBIO.drop_duplicates(subset=["Periodo", "Código est"])
    
    # Contar total de estudiantes por periodo
    total_estudiantes = df_unique.groupby("Periodo")["Código est"].count()
    
    # Filtrar por "Programa principal" == "INGENIERIA BIOMEDICA" y contar
    df_ibio = df_unique[df_unique["Programa principal"] == "INGENIERIA BIOMEDICA"]
    total_estudiantes_ibio = df_ibio.groupby("Periodo")["Código est"].count()
    
    # Contar estudiantes en cada materia específica por periodo
    ibio_1010 = solo_IBIO[solo_IBIO["Materia"] == "IBIO-1010"].groupby("Periodo")["Código est"].count()
    ibio_3870 = solo_IBIO[solo_IBIO["Materia"] == "IBIO-3870"].groupby("Periodo")["Código est"].count()

    # Unir todos los conteos en un solo DataFrame
    df = pd.DataFrame({
        "Total Estudiantes": total_estudiantes,
        "Total Estudiantes IBIO": total_estudiantes_ibio,
        "IBIO1010": ibio_1010,
        "IBIO3870": ibio_3870
    }).fillna(0).astype(int)  # Llenar NaN con 0 y convertir a enteros
    
    plt.style.use('ggplot')

    # Configuración inicial de la figura y los ejes
    plt.figure(figsize=(10, 6))
    # Número de periodos (eje x)
    n_periodos = len(df.index)
    # Ancho de las barras
    bar_width = 0.21
    # Índices del eje x para cada grupo de barras
    indices = np.arange(n_periodos)
    # Listas para almacenar las entradas y salidas de estudiantes
    entradas = []
    salidas = []

    # Bucle para iterar a través de cada fila (periodo) y plotear las barras basado en la condición
    for i in range(n_periodos):
        plt.bar(indices[i], df['Total Estudiantes IBIO'].iloc[i]-(df['IBIO1010'].iloc[i]+df['IBIO3870'].iloc[i]), width=bar_width, label='Total IBIO' if i == 0 else "", color='#6495ED')
        plt.bar(indices[i]+bar_width, df['IBIO1010'].iloc[i], width=bar_width, label='IBIO1010' if i == 0 else "", color='#92D050')
        plt.bar(indices[i]+(2*bar_width), df['IBIO3870'].iloc[i], width=bar_width, label='IBIO3870' if i == 0 else "", color='#FF0000')
        entradas.append(df['IBIO1010'].iloc[i])
        salidas.append(df['IBIO3870'].iloc[i])

    # Configuración de los ticks y labels del eje x
    plt.xticks(indices+bar_width, df.index.astype(str))
    # Sumar entradas y salidas cada 2 periodos
    entradas_anios = []
    salidas_anios = []

    for i in range(0, len(entradas), 2):
        if i != len(entradas)-1:
            entradas_anios.append(entradas[i]+entradas[i+1])
            salidas_anios.append(salidas[i]+salidas[i+1])
        else:
            entradas_anios.append(entradas[i]*2)
            salidas_anios.append(salidas[i]*2)
    
    # Calcular el flujo de estudiantes
    flujo_anios = [entradas_anios[i]-salidas_anios[i] for i in range(len(entradas_anios))]
    # Añadir lines de flujo de estudiantes
    puntos_x = list(indices[0::2] + (3*bar_width))
    plt.plot(puntos_x, entradas_anios, linestyle='--', color='#92D050', marker='o')
    plt.plot(puntos_x, salidas_anios, linestyle='--', color='#FF0000', marker='o')
    plt.plot(puntos_x, flujo_anios, linestyle='--', color='black', marker='o')

    # Añadir leyendas, títulos y etiquetas de ejes
    plt.xlabel('Periodo')
    plt.ylabel('Número de Estudiantes')
    plt.title('Estudiantes Unicos por Periodo', fontsize=18, fontweight='bold')
 
    # Ajustar layout y mostrar el plot
    plt.tight_layout()

    plt.savefig(f'{directory_name}/poblacionIBIO.png')

    # Estudiantes únicos totales por periodo
    plt.figure(figsize=(10, 6))
    plt.bar(indices, df['Total Estudiantes IBIO'], width=bar_width, label='Estudiantes IBIO', color='#6495ED')
    plt.bar(indices+bar_width, df['Total Estudiantes'], width=bar_width, label='Estudiantes totales', color='#92D050')
    plt.xticks(indices, df.index.astype(str))
    plt.xlabel('Periodo')
    plt.ylabel('Número de Estudiantes')

    plt.title('Estudiantes Unicos Totales por Periodo', fontsize=18, fontweight='bold')
    plt.legend()
    plt.tight_layout()

    plt.savefig(f'{directory_name}/EstudiantesTotales_EstudiantesIBIO.png')

if __name__ == '__main__':

    # Escriba el periodo actual o el periodo hasta el cual quiere calcular las estadísticas. Ej: "201810"
    periodo_actual = "202510"
    # Escriba el programa principal para el cual quiere calcular las estadísticas. Ej: "INGENIERIA BIOMEDICA"
    programa_principal = "INGENIERIA BIOMEDICA"
    # Ruta al archivo de datos de los cursos
    cursos_excelPath = f"Data/Cursos 201810-{periodo_actual}.xlsx"
    # Ruta al archivo de datos de los estudiantes
    estudiantes_excelPath = f"Data/Estudiantes IBIO 201810-{periodo_actual}.xlsx"
    # Ruta al archivo de datos de los sancionados
    sancionados_excelPath = "Data/Estudiantes Sancionados 2021-10.xlsx"
    # Ruta al archivo de datos de los estudiantes que se retiraron
    path_retiros = "Data/Retiros 201810-202420.xlsx"
    # Ruta al archivo de la población de estudiantes IBIO
    poblacion_IBIO = "Data/EstudiantesUnicosTotales.xlsx" 

    ## Piecharts por materia en cada periodo
    directory_name = f'RESULTS_{periodo_actual}/PieCharts_por_Materia' 
    mainMaterias(cursos_excelPath, programa_principal, directory_name)

    ## Piecharts por cohorte en cada periodo
    directory_name = f"RESULTS_{periodo_actual}/PieCharts_por_cohorte"
    mean_dataframe, desv_dataframe, results, mean_sancionados, desv_sancionados, sancionados_dict = avance_cohortes(cursos_excelPath, sancionados_excelPath, programa_principal, directory_name)

    ## Estadisticas historicas por semestre
    directory_name = f"RESULTS_{periodo_actual}/Historico_cohortes"
    mean_dataframe, desv_dataframe, results, mean_sancionados, desv_sancionados, sancionados_dict = avance_cohortes(cursos_excelPath, sancionados_excelPath, programa_principal)
    mean_avance_hist = historico_cohortes(cursos_excelPath, sancionados_excelPath, programa_principal)
    plot_historico_cohortes(cursos_excelPath, sancionados_excelPath, mean_dataframe, desv_dataframe, mean_avance_hist, directory_name, programa_principal)

    ## Graficas de N por cohortes
    directory_name = f"RESULTS_{periodo_actual}/N_cohortes"
    n_dataframe, mean_n_hist, n_sancionados = n_estudiantes(cursos_excelPath, sancionados_excelPath, estudiantes_excelPath, programa_principal)
    plot_n_cohortes(cursos_excelPath, n_dataframe, mean_n_hist, directory_name, programa_principal)

    ## Estadisticas de retiros & aprobados por materia IBIO. Piecharts por materia en cada periodo
    directory_name = f'RESULTS_{periodo_actual}/Resultados_por_Materia'
    avanceNivel(cursos_excelPath, programa_principal, directory_name)

    ## Estadísticas sancionados
    directory_name = f"RESULTS_{periodo_actual}/Sancionados"
    sancionados(cursos_excelPath, directory_name, programa_principal, sancionados_excelPath)

    ## Gráficas generales
    directory_name = f"RESULTS_{periodo_actual}/Graficas_Generales"
    mean_avance_hist = historico_cohortes(cursos_excelPath, sancionados_excelPath, programa_principal)
    n_dataframe, mean_n_hist, n_sancionados = n_estudiantes(cursos_excelPath, sancionados_excelPath, estudiantes_excelPath, programa_principal)
    general_plots(estudiantes_excelPath, mean_avance_hist, mean_n_hist, directory_name)
    estudiantesUnicosPorPeriodo(cursos_excelPath, programa_principal, directory_name)
    PoblacionEstudiantesUnicos(cursos_excelPath, programa_principal, directory_name)