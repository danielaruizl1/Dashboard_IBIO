#%% Importar librerias
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from utils import Avance, Semestre, assign_group, fill_results_dict, medianNivel
from plots import piecharts_por_materia, std_dev_plot, comparacionNivelPlot, retiros_plot, retiros_plot_resumido
from tqdm import tqdm

def load_cursos_obligatorios():

    with open("cursos_obligatorios.json") as json_file:
        cursos = json.load(json_file)

    return cursos

def soloIBIO_df (xlsx, mask):

    solo_IBIO = xlsx[mask]
    solo_IBIO = solo_IBIO.reset_index()

    return solo_IBIO

def IBIO_columns (solo_IBIO, pensum_courses):

    solo_IBIO['Periodo'] = solo_IBIO['Periodo'].astype(str).str[:5].astype(int)

    solo_IBIO = solo_IBIO.drop('index', axis=1)

    solo_IBIO = solo_IBIO[solo_IBIO['Materia'].isin(pensum_courses)]
    solo_IBIO = solo_IBIO.reset_index()
    solo_IBIO = solo_IBIO.drop('index', axis=1)

    periodo = solo_IBIO["Periodo"]

    todosPeriodos = np.unique(periodo)
    #Convert code to int
    solo_IBIO['Código est'] = solo_IBIO['Código est'].astype(int)

    #Add new column for each student with the year they enter to college
    solo_IBIO['Año Ingreso'] = solo_IBIO['Código est'].astype(str).str[:5].astype(int)

    solo_IBIO['Semestre'] = solo_IBIO.apply(Semestre, axis=1)
    solo_IBIO['Avance'] = solo_IBIO.apply(Avance, axis=1)

    solo_IBIO['Group'] = solo_IBIO['Avance'].apply(assign_group)

    return solo_IBIO

def mainMaterias(path, desired_program, directory_name):

    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    # Filtrar solo los estudiantes IBIO (primer programa)
        
    xlsx = pd.read_excel(path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO = IBIO_columns(solo_IBIO, pensum_courses)

    periodo = solo_IBIO["Periodo"]

    todosPeriodos = np.unique(periodo)

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

            condition = solo_IBIO['Materia']== pensum_courses[j]

            condition_anio = solo_IBIO['Periodo']== todosPeriodos[i]

            condition_anio = condition_anio.reset_index(drop=True)

            df_materia = solo_IBIO.loc[condition]

            df_materia = df_materia.reset_index(drop=True)

            df_materia_anio = df_materia.loc[condition_anio]

            # count the number of values in each group
            counts = df_materia_anio['Group'].value_counts()

            piecharts_por_materia (counts, cursos, pensum_courses, todosPeriodos, i, j,directory2)


def avanceNivel(path, desired_program, directory_name):


    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    xlsx = pd.read_excel(path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO = IBIO_columns(solo_IBIO, pensum_courses)

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

        std_dev_plot (results_dict, pensum_courses, min_value, max_mean, max_desv, cursos, i, directory_name)


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

        comparacionNivelPlot (directory_name, y,x_list, n_est, max_n, pensum_courses,i,x_nivel,y_nivel, nivel_materia,media_min, media_max, cursos)


def Retiros (path, original_path, desired_program, directory_name):

    excel_retiros = pd.read_excel(path)

    cursos = load_cursos_obligatorios()

    pensum_courses = list(cursos.keys())

    filtered_df = excel_retiros[excel_retiros['Materia'].isin(pensum_courses)]

    retiros_count = {materia: {periodo[:5]: count for periodo, count in filtered_df[filtered_df['Materia'] == materia]['Periodo'].value_counts().items()} for materia in filtered_df['Materia'].unique()}

    xlsx = pd.read_excel(original_path)

    mask = xlsx['Programa principal'] == desired_program

    solo_IBIO = soloIBIO_df(xlsx, mask)

    solo_IBIO = IBIO_columns(solo_IBIO, pensum_courses)

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


    for i in tqdm(range(len(pensum_courses)), desc="Graficas Retiros"):

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
        
        retirosMateria = retiros_count[pensum_courses[i]]

        result_list_retiros = []
        for item in x_nivel:
            if item in retirosMateria:
                result_list_retiros.append(retirosMateria[item])
            else:
                result_list_retiros.append(0)

                
        retiros_plot(y, x_list, n_est, result_list_retiros, max_n, pensum_courses, x_nivel, y_nivel, nivel_materia, media_min, media_max, cursos, i, directory_name)



    list_dict_estudiantes = []
    list_dict_retiros = []
    list_dict_avance = []

    for i in tqdm(range(len(pensum_courses)), desc="Graficas Retiros Resumidas"):

        x = list(results_dict[pensum_courses[i]].keys())
        x_list = [str(i) for i in x]
        y = [results_dict[pensum_courses[i]][year]['mean'] for year in x]
        n_est = [results_dict[pensum_courses[i]][year]['n'] for year in x]
        
        
        my_dict_avance = dict(zip(x_list, y))
        list_dict_avance.append(my_dict_avance)

        nivel_materia= int(pensum_courses[i][5])
        y_nivel = list(medias_niveles[nivel_materia].values())
        x_2 = list(medias_niveles[nivel_materia].keys())
        x_nivel = [str(i) for i in x_2]

        if len(x_list) != len(x_nivel):
            del x_nivel[0]
            del y_nivel[0]
        
        retirosMateria = retiros_count[pensum_courses[i]]

        my_dict_estudiantes = dict(zip(x_list, n_est))

        result_list_retiros = []
        for item in x_nivel:
            if item in retirosMateria:
                result_list_retiros.append(retirosMateria[item])
            else:
                result_list_retiros.append(0)

        list_dict_retiros.append(retirosMateria)
        list_dict_estudiantes.append(my_dict_estudiantes)

        retiros_plot_resumido (y, x_list, n_est, result_list_retiros, max_n, pensum_courses, x_nivel, y_nivel, nivel_materia, media_min, media_max, cursos, i, directory_name)
