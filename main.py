#%% Importar librerias
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker

#%% Subir datos cursos obligatorios
with open("cursos_obligatorios.json") as json_file:
    cursos = json.load(json_file)

xlsx = pd.read_excel("Data/Cursos IBIO 2018-2023.xlsx")
pensum_courses = list(cursos.keys())

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
       
directory = "Results_new"

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

#%%

#Todas las cohortes
mean_dataframe=pd.DataFrame()
desv_dataframe=pd.DataFrame()
n_dataframe=pd.DataFrame()

#Estudiantes sacionados
sancionados_xlsx=pd.read_excel("Data/Estudiantes Sancionados 2021-10.xlsx")
sancionados=list(sancionados_xlsx["CÓDIGO"])
sancionados_dict={}
mean_sancionados=pd.DataFrame()
desv_sancionados=pd.DataFrame()
n_sancionados=pd.DataFrame()

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
        #plt.savefig(f'{directory2}/piechart_{pensum_courses[j]}.png')
        plt.cla()
        plt.close()

    #cohortes
    df_cohorte=solo_IBIO[condition_anio]
    semesters_per_cohorte=np.unique(df_cohorte['Año Ingreso'])
    cohortes_dict=dict.fromkeys(semesters_per_cohorte)
    for cohorte in cohortes_dict:
        cohortes_dict[cohorte]={}
        sancionados_dict[cohorte]={}

    students_per_cohorte=np.unique(df_cohorte['Código est'])
    for student in students_per_cohorte:
        semestre_ingreso=int(np.unique(df_cohorte[df_cohorte['Código est']==student]['Año Ingreso']))
        cohortes_dict[semestre_ingreso][student]=np.mean(df_cohorte[df_cohorte['Código est']==student]["Avance"])
        if student in sancionados:
            sancionados_dict[semestre_ingreso][student]=np.mean(df_cohorte[df_cohorte['Código est']==student]["Avance"])
        
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

    #Stadisticas cohorte
    for periodo in cohortes_dict:
        if periodo in todosPeriodos:
            semestre_actual=i-list(todosPeriodos).index(periodo)
            mean=np.mean(list(cohortes_dict[periodo].values()))
            desv=np.std(list(cohortes_dict[periodo].values()))
            n=len(list(cohortes_dict[periodo].values()))
            mean_dataframe.loc[periodo,semestre_actual]=mean
            desv_dataframe.loc[periodo,semestre_actual]=desv
            n_dataframe.loc[periodo,semestre_actual]=n

    for periodo in sancionados_dict:
        if periodo in todosPeriodos:
            semestre_actual=i-list(todosPeriodos).index(periodo)
            mean=np.mean(list(sancionados_dict[periodo].values()))
            desv=np.std(list(sancionados_dict[periodo].values()))
            n=len(list(sancionados_dict[periodo].values()))
            mean_sancionados.loc[periodo,semestre_actual]=mean
            desv_sancionados.loc[periodo,semestre_actual]=desv
            n_sancionados.loc[periodo,semestre_actual]=n

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
        #plt.savefig(f'Results_new/{todosPeriodos[i]}/piechart_{str(anio)}.png')
        plt.cla()
        plt.close()

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
    #plt.savefig(f'Results_new/{todosPeriodos[i]}/piechart_all_cohortes.png')
    plt.cla()
    plt.close()

#%% Gráficas de media y desviación stándar para todas las cohortes

directory = f"Results_new/Cohortes_Results"

if not os.path.exists(directory):
    os.makedirs(directory)

mean_semestres=[]

#Promedio de avance por semestre
for semestre in range(11):
    datos=[mean_dataframe[semestre][x] for x in todosPeriodos if not np.isnan(mean_dataframe[semestre][x])]
    mean_semestres.append(np.mean(datos))

mean_semestres[0]=0

for periodo in todosPeriodos:
    plt.figure()
    plt.title(f"Cohorte {periodo}",fontsize=18)
    lim=sum([not np.isnan(n_dataframe.loc[periodo][x]) for x in range(11)])
    x_list=range(lim)
    y_list=mean_dataframe.loc[periodo][:lim]
    y_err=desv_dataframe.loc[periodo][:lim]
    n_list=n_dataframe.loc[periodo][:lim]
    plt.plot(x_list,mean_semestres[:lim],'o--', label="Avance promedio histórico")
    plt.errorbar(x_list, y_list, yerr=y_err, color='red', linewidth=0.8, fmt='o--', ecolor='black', capsize=7, elinewidth=1, markeredgewidth=1,label="Avance cohorte")
    plt.xticks(x_list)
    plt.xlabel('Semestre')
    plt.ylabel('Avance Promedio')
    plt.legend()
    for y_n, y_val in enumerate(y_list):
        plt.text(x_list[y_n], y_val + y_err[y_n]+0.01, f'{n_list[y_n]}', ha='center')
    plt.savefig(f'{directory}/{periodo}.png')

#%% Gráficas de media y desviación stándar para sancionados

directory = f"Results_new/Sancionados_Results"

if not os.path.exists(directory):
    os.makedirs(directory)

periodos_sancionados=[20191,20192,20201]

for periodo in periodos_sancionados:
    plt.figure()
    plt.title(f"Sancionados ingresados en {periodo}",fontsize=18)
    lim=sum([not np.isnan(n_sancionados.loc[periodo][x]) for x in range(11)])
    x_list=range(lim)
    y_list=mean_sancionados.loc[periodo][:lim]
    y_err=desv_sancionados.loc[periodo][:lim]
    n_list=n_sancionados.loc[periodo][:lim]
    plt.plot(x_list,mean_semestres[:lim],'o--', label="Avance promedio histórico")
    plt.errorbar(x_list, y_list, yerr=y_err, color='red', linewidth=0.8, fmt='o--', ecolor='black', capsize=7, elinewidth=1, markeredgewidth=1,label="Avance cohorte")
    plt.xticks(x_list)
    plt.xlabel('Semestre')
    plt.ylabel('Avance Promedio')
    plt.legend()
    for y_n, y_val in enumerate(y_list):
        plt.text(x_list[y_n], y_val + y_err[y_n]+0.01, f'{n_list[y_n]}', ha='center')
    plt.savefig(f'{directory}/{periodo}.png')

#%% Estadísticas por materia

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

directory = f"Results_new/Subject_Results"

if not os.path.exists(directory):
    os.makedirs(directory)

for i in range(len(pensum_courses)):

    x = list(results_dict[pensum_courses[i]].keys())
    x_list = [str(i) for i in x]
    y = [results_dict[pensum_courses[i]][year]['mean'] for year in x]
    y_err = [results_dict[pensum_courses[i]][year]['std_dev'] for year in x]
    n = [results_dict[pensum_courses[i]][year]['n'] for year in x]

    plt.errorbar(x_list, y, yerr=y_err, color='red', linewidth=0.8, fmt='o--', ecolor='black', capsize=7, elinewidth=1, markeredgewidth=1)
    plt.xticks(x_list)
    plt.xlabel('Semestre')
    plt.ylabel('Avance Promedio')
    
    for y_n, y_val in enumerate(y):
        plt.text(x_list[y_n], y_val + y_err[y_n] + 0.1, f'{n[y_n]}', ha='center')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}')
    plt.show()
    plt.savefig(f'Results_new/Subject_Results/{pensum_courses[i]}.png')
    plt.cla()
    plt.close()
