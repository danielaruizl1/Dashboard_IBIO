import json
import tqdm as tqdm
from plots import retiros_plot, retiros_plot_resumido

def assign_group(value):
    if value > 3:
        return '> +3'
    elif value == 3:
        return '+3'
    elif value == 2:
        return '+2'
    elif value == 1:
        return '+1'
    elif value == 0:
        return '+0'
    elif value == -1:
        return '-1'
    elif value == -2:
        return '-2'
    elif value == -3:
        return '-3'
    else:
        return '< -3'
    

def assign_group2(value):
    if value >= 3:
        return '>= +3'
    elif 2 <= value < 3:
        return '[+2, +3)'
    elif 1 <= value < 2:
        return '[+1, +2)'
    elif 0 <= value < 1:
        return '[+0, +1)'
    elif -1 < value < 0:
        return '[-1, +0)'
    elif -2 < value <= -1:
        return '[-2, -1)'
    elif value <= -2:
        return '<= -2'

def Semestre(row):

    ingreso = row['Año Ingreso']
    periodo = row['Periodo']
    
    if ingreso == periodo:
        return 1
    
    anioIngreso = int(str(ingreso)[:4])
    anioActual = int(str(periodo)[:4])
    semestreIngreso = int(str(ingreso)[4:])
    semestreActual = int(str(periodo)[4:])

    if semestreIngreso>semestreActual:
        return 2*(anioActual-anioIngreso)
    
    elif semestreIngreso==semestreActual:

        return 2*(anioActual-anioIngreso)+1
        
    elif semestreIngreso<semestreActual:
        return 2*(anioActual-anioIngreso)+2
    

def Avance(row):

    #%% Subir datos cursos obligatorios
    with open("cursos_obligatorios.json") as json_file:
        cursos = json.load(json_file)

    semestreEstudiante = row['Semestre']
    materia = row['Materia']
    semestreMateriaActual = cursos[materia][0]
        
    if semestreEstudiante == semestreMateriaActual:
        return 0
        
    else:
        valor = semestreEstudiante - semestreMateriaActual
        return valor
    

def fill_results_dict(pensum_courses, solo_IBIO):
    
    results_dict = {}

    for i in range(len(pensum_courses)):

        materia_df = solo_IBIO[solo_IBIO['Materia'] == pensum_courses[i]]
        materia_df = materia_df.reset_index()
        unique_periods = materia_df['Periodo'].unique()

        pensum_course_dict = {}

        for j in range(len(unique_periods)):
    
            periodo_df = materia_df[materia_df['Periodo'] == unique_periods[j]]
            periodo_df = periodo_df.reset_index()

            n = len(periodo_df)
            mean = periodo_df['Avance'].mean()
            std_dev = periodo_df['Avance'].std()

            pensum_course_dict[unique_periods[j]] = {'mean': mean, 'std_dev': std_dev, 'n':n}

        results_dict[pensum_courses[i]] = pensum_course_dict

    return results_dict


def medianNivel (results_dict):

    medias_niveles={}
    for i in range(3):
        nivel = i+1
        materias_nivel = [key for key in results_dict.keys() if key.startswith(f'IBIO-{nivel}')]
        
        nivel = {}
        for materia in materias_nivel:
            valores = results_dict[materia]
            
            for anio in valores.keys():
                
                if anio not in nivel:
                    nivel[anio]=valores[anio]['mean']
                else: 
                    nivel[anio]+=valores[anio]['mean']

        for key in nivel:
            nivel[key] = nivel[key] / len(materias_nivel)

        medias_niveles[i+1]=nivel

    return medias_niveles

def get_year(key):

    return int(str(key)[:5])

def retirosPorMateria (pensum_courses, results_dict, medias_niveles, retiros_count, max_n, media_min, media_max, cursos, directory_name, todosPeriodos):
    
    list_dict_estudiantes = []
    list_dict_retiros = []
    list_dict_avance = []

    

    # Create an empty dictionary to store the sorted results
    sorted_results_dict = {}

    periodos = todosPeriodos.tolist()
    # Iterate through each key in results_dict

    for subject_code in results_dict:
        # Sort the sub-dictionary based on the order of years
        sorted_keys = sorted(results_dict[subject_code].keys(), key=lambda x: periodos.index(x))
        sorted_sub_dict = {sub_key: results_dict[subject_code][sub_key] for sub_key in sorted_keys}
        sorted_results_dict[subject_code] = sorted_sub_dict


    for i in range(len(pensum_courses)):

        x = list(sorted_results_dict[pensum_courses[i]].keys())
        x_list = [str(i) for i in x]
        y = [sorted_results_dict[pensum_courses[i]][year]['mean'] for year in x]
        n_est = [sorted_results_dict[pensum_courses[i]][year]['n'] for year in x]
        
        
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
    
        retiros_plot(y, x_list, n_est, result_list_retiros, max_n, pensum_courses, x_nivel, y_nivel, nivel_materia, media_min, media_max, cursos, i, directory_name)
        retiros_plot_resumido (y, x_list, n_est, result_list_retiros, max_n, pensum_courses, x_nivel, y_nivel, nivel_materia, media_min, media_max, cursos, i, directory_name)

    return list_dict_retiros, list_dict_estudiantes, list_dict_avance
