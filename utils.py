import json
import tqdm as tqdm

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