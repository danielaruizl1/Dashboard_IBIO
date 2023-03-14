import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker

with open("cursos_obligatorios.json") as json_file:
    cursos = json.load(json_file)

xlsx = pd.read_excel("Data/Cursos IBIO 2018-2023.xlsx")
pensum_courses = cursos.keys()

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

def Avance(row):

    semestreEstudiante = row['Semestre']
    materia = row['Materia']
    semestreMateriaActual = cursos[materia][0]
        
    if semestreEstudiante == semestreMateriaActual:
        return 0
        
    else:
        valor = semestreEstudiante - semestreMateriaActual
        return valor
       
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
    
directory = "/media/SSD3/jpuentes/IBIO_Dashboard/Results_new"

if not os.path.exists(directory):
    os.makedirs(directory)

avances = []

desired_program = 'INGENIERIA BIOMEDICA'
    
#Keep only the students whose main programme is IBIO
mask = xlsx['Programa principal'] == desired_program

solo_IBIO = xlsx[mask]
solo_IBIO = solo_IBIO.reset_index()

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

group_colors = {
    '> +3': '#d3554c',
    '+3': '#fc6c64',
    '+2': '#feb268',
    '+1': '#f7e16a',
    '+0': '#ffe9af',
    '-1': '#d3e1a2',
    '-2': '#a9e070',
    '-3': '#06b050',
    '< -3': 'darkgreen'
}

pensum_courses = list(pensum_courses)

for i in range(len(todosPeriodos)):

    directory = f"Results_new/{todosPeriodos[i]}"

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for j in range(len(pensum_courses)):
        
        directory2 = f"Results_new/{todosPeriodos[i]}/{cursos[pensum_courses[j]][1]}"

        if not os.path.exists(directory2):
            os.makedirs(directory2)

        condition = solo_IBIO['Materia']== pensum_courses[j]

        condition_anio = solo_IBIO['Periodo']== todosPeriodos[i]

        df_materia = solo_IBIO[condition]

        df_materia_anio = df_materia[condition_anio]

        # count the number of values in each group
        counts = df_materia_anio['Group'].value_counts()

        colors = [group_colors[group] for group in counts.index]

        explode = 0.05
        explode_list = [explode] * len(counts)

        fig, ax = plt.subplots()
        plt.style.use('seaborn')
        wedges, labels, _ = ax.pie(counts, colors =colors,autopct=lambda x: f'{int(round(x/100.0*sum(counts)))} ({x:.1f}%)', 
            textprops={'fontsize': 13}, explode = explode_list)
        ax.set_title(f'{cursos[pensum_courses[j]][1]}{" "}{todosPeriodos[i]}{0}', fontsize=16)
        handles = [mpatches.Patch(color=color, label=label) for label, color in group_colors.items()]
        ax.legend(handles=handles, loc='upper right')
        plt.savefig(f'{directory2}/piechart_{pensum_courses[j]}.png')
        plt.cla()
        plt.close()

    #cohortes
    df_cohorte=solo_IBIO[condition_anio]
    semesters_per_cohorte=np.unique(df_cohorte['Año Ingreso'])
    cohortes_dict=dict.fromkeys(semesters_per_cohorte)
    for cohorte in cohortes_dict:
        cohortes_dict[cohorte]={}

    students_per_cohorte=np.unique(df_cohorte['Código est'])
    for student in students_per_cohorte:
        semestre_ingreso=int(np.unique(df_cohorte[df_cohorte['Código est']==student]['Año Ingreso']))
        cohortes_dict[semestre_ingreso][student]=np.mean(df_cohorte[df_cohorte['Código est']==student]["Avance"])

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
        plt.figure()
        plt.style.use('seaborn')
        colors2 = [group_colors_2[group] for group in results[anio]]
        plt.pie(results[anio].values(), autopct=lambda x: f'{int(round(x/100.0*sum(results[anio].values())))}('+str(round(x,1))+"%)" ,colors=colors2,textprops={'fontsize':14}, explode=[0.05] * len(results[anio]))
        plt.title(f'Avance de los estudiantes ingresados en {anio} para el periodo {todosPeriodos[i]}', fontdict={'fontsize':14, 'weight': 'bold'})
        plt.legend(results[anio].keys())
        plt.savefig(f'Results_new/{todosPeriodos[i]}/piechart_{str(anio)}.png')

    all_cohortes = {">3":0,"3-2":0,"2-1":0,"1-0":0,"0-1":0,"-1-2":0,"-2-3":0}
    for anio in results:
        for key in results[anio]:
            all_cohortes[key]+=results[anio][key]
    
    all_cohortes = {key: value for key, value in all_cohortes.items() if value != 0}
    plt.figure()
    plt.style.use('seaborn')
    colors2 = [group_colors_2[group] for group in all_cohortes]
    plt.pie(all_cohortes.values(), autopct=lambda x: f'{int(round(x/100.0*sum(all_cohortes.values())))}('+str(round(x,1))+"%)" ,colors=colors2,textprops={'fontsize':14}, explode=[0.05] * len(all_cohortes))
    plt.title(f'Avance de todos los estudiantes en el periodo {todosPeriodos[i]}', fontdict={'fontsize':14, 'weight': 'bold'})
    plt.legend(all_cohortes.keys())
    plt.savefig(f'Results_new/{todosPeriodos[i]}/piechart_all_cohortes.png')

