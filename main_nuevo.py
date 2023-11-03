#%% Importar librerias
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

#%% Funciones básicas

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
    
#%% Subir datos cursos obligatorios

with open("cursos_obligatorios.json") as json_file:
    cursos = json.load(json_file)

pensum_courses = list(cursos.keys())

#%% Filtrar solo los estudiantes IBIO (primer programa)

desired_program = 'INGENIERIA BIOMEDICA'
    
xlsx = pd.read_excel("Data/Cursos IBIO 2018-2023.xlsx")
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

#%% Piecharts por materia

directory = "Results_new"

if not os.path.exists(directory):
    os.makedirs(directory)

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

        condition_anio = condition_anio.reset_index(drop=True)

        df_materia = solo_IBIO.loc[condition]

        df_materia = df_materia.reset_index(drop=True)

        df_materia_anio = df_materia.loc[condition_anio]

        # count the number of values in each group
        counts = df_materia_anio['Group'].value_counts()

        colors = [group_colors[group] for group in counts.index]

        explode = 0.05
        explode_list = [explode] * len(counts)

        fig, ax = plt.subplots()
        plt.style.use('ggplot')
        wedges, labels, _ = ax.pie(counts, colors =colors,autopct=lambda x: f'{int(round(x/100.0*sum(counts)))} ({x:.1f}%)', 
            textprops={'fontsize': 13}, explode = explode_list)
        ax.set_title(f'{cursos[pensum_courses[j]][1]}{" "}{todosPeriodos[i]}{0}', fontsize=16)
        handles = [mpatches.Patch(color=color, label=label) for label, color in group_colors.items()]
        ax.legend(handles=handles, loc='upper right')
        plt.savefig(f'{directory2}/piechart_{pensum_courses[j]}.png')
        plt.cla()
        plt.close()

#%% Crear dataframes para estadísticas de cohortes

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
n_sancionados=pd.DataFrame([0]*11)
n_sancionados.index=todosPeriodos

#%% Cohortes

for i in range(len(todosPeriodos)):

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

    #Stadisticas cohorte

    for periodo in cohortes_dict:
        if periodo in todosPeriodos:
            semestre_actual=i-list(todosPeriodos).index(periodo)
            mean=np.mean(list(cohortes_dict[periodo].values()))
            desv=np.std(list(cohortes_dict[periodo].values()))
            n=len(list(cohortes_dict[periodo].values()))
            mean_dataframe.loc[periodo,semestre_actual]=mean
            desv_dataframe.loc[periodo,semestre_actual]=desv

    for periodo in sancionados_dict:
        if periodo in todosPeriodos:
            semestre_actual=i-list(todosPeriodos).index(periodo)
            mean=np.mean(list(sancionados_dict[periodo].values()))
            desv=np.std(list(sancionados_dict[periodo].values()))
            n=len(list(sancionados_dict[periodo].values()))
            mean_sancionados.loc[periodo,semestre_actual]=mean
            desv_sancionados.loc[periodo,semestre_actual]=desv

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
        plt.style.use('ggplot')
        colors2 = [group_colors_2[group] for group in results[anio]]
        plt.pie(results[anio].values(), autopct=lambda x: f'{int(round(x/100.0*sum(results[anio].values())))}('+str(round(x,1))+"%)" ,colors=colors2,textprops={'fontsize':14}, explode=[0.05] * len(results[anio]))
        plt.title(f'Avance de los estudiantes ingresados en {anio} para el periodo {todosPeriodos[i]}', fontdict={'fontsize':14, 'weight': 'bold'})
        plt.legend(results[anio].keys())
        plt.savefig(f'Results_new/{todosPeriodos[i]}/piechart_{str(anio)}.png')
        plt.cla()
        plt.close()

    all_cohortes = {">3":0,"3-2":0,"2-1":0,"1-0":0,"0-1":0,"-1-2":0,"-2-3":0}
    for anio in results:
        for key in results[anio]:
            all_cohortes[key]+=results[anio][key]
    
    all_cohortes = {key: value for key, value in all_cohortes.items() if value != 0}
    plt.figure()
    plt.style.use('ggplot')
    colors2 = [group_colors_2[group] for group in all_cohortes]
    plt.pie(all_cohortes.values(), autopct=lambda x: f'{int(round(x/100.0*sum(all_cohortes.values())))}('+str(round(x,1))+"%)" ,colors=colors2,textprops={'fontsize':14}, explode=[0.05] * len(all_cohortes))
    plt.title(f'Avance de todos los estudiantes en el periodo {todosPeriodos[i]}', fontdict={'fontsize':14, 'weight': 'bold'})
    plt.legend(all_cohortes.keys())
    plt.savefig(f'Results_new/{todosPeriodos[i]}/piechart_all_cohortes.png')
    plt.cla()
    plt.close()

#%% Dataframe de todos los estudiantes IBIO 

mask = xlsx['Programa principal'] == 'INGENIERIA BIOMEDICA'
todos_IBIO = xlsx[mask]
todos_IBIO = todos_IBIO.reset_index()
todos_IBIO['Periodo'] = todos_IBIO['Periodo'].astype(str).str[:5].astype(int)
todos_IBIO = todos_IBIO.drop('index', axis=1)
todos_IBIO['Código est'] = todos_IBIO['Código est'].astype(int)
todos_IBIO['Año Ingreso'] = todos_IBIO['Código est'].astype(str).str[:5].astype(int)

#%% Número de estudiantes IBIO por semestre

for i in range(len(todosPeriodos)):
    condicion_periodo = todos_IBIO['Periodo']==todosPeriodos[i]
    df_periodo=todos_IBIO[condicion_periodo]
    estudiantes={}
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
        
#%% Estadísticas históricas por semestre 

mean_avance_hist=[]

for semestre in range(11):
    avance=[mean_dataframe[semestre][x] for x in todosPeriodos if not np.isnan(mean_dataframe[semestre][x])]
    n=[n_dataframe[semestre][x] for x in todosPeriodos if not np.isnan(n_dataframe[semestre][x])]
    mean_avance_hist.append(np.mean(avance))

#%% Path resultados de cohortes
directory = f"Results_new/Cohortes_Results"

if not os.path.exists(directory):
    os.makedirs(directory)

#%% Gráficas de avance por cohortes

for periodo in todosPeriodos:
    plt.figure(figsize=(10,7.5))
    lim=sum([not np.isnan(mean_dataframe.loc[periodo][x]) for x in range(11)])
    x_list=range(1,lim+1)
    y_list=mean_dataframe.loc[periodo][:lim]
    y_err=desv_dataframe.loc[periodo][:lim]
    plt.plot(x_list, mean_avance_hist[:lim], 'o--', linewidth=0.8, label="Avance promedio histórico")
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

#%% Grafica de avance para todas las cohortes juntas

plt.figure(figsize=(10,7.5))
colors_list=list(mcolors.TABLEAU_COLORS.values())
colors_list.append('#000000')

for i in range(len(todosPeriodos)):
    lim=sum([not np.isnan(mean_dataframe.loc[todosPeriodos[i]][x]) for x in range(11)])
    x_list=range(1,lim+1)
    y_list=mean_dataframe.loc[todosPeriodos[i]][:lim]
    plt.plot(x_list, y_list, 'o--', linewidth=0.8, label=todosPeriodos[i],color=colors_list[i])
    plt.axhline(y=0, color="black", linewidth=0.8, linestyle='--')
    plt.ylim((-1,5))
plt.xlabel('Semestre',fontsize=14)
plt.ylabel('Avance Promedio',fontsize=14)
plt.legend(fontsize=12, loc=2)
plt.xticks(range(1,12))
plt.title(f"Avance promedio por cohorte",fontsize=18)
plt.savefig(f'{directory}/cohortes_avance.png')
plt.cla()
plt.close()

#%% Gráficas de N por cohortes

xlsx_estudiantes = pd.read_excel("Data/Estudiantes IBIO 201810-202220.xlsx", sheet_name=None)
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

for semestre in range(11):
    n=[n_dataframe[semestre][x] for x in todosPeriodos if not np.isnan(n_dataframe[semestre][x])]
    mean_n_hist.append(np.mean(n))

for periodo in todosPeriodos:
    plt.figure(figsize=(10,7.5))
    lim=sum([not np.isnan(n_dataframe.loc[periodo][x]) for x in range(11)])
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

#%% Gráfica de N para todas las cohortes juntas

plt.figure(figsize=(10,7.5))
colors_list=["maroon","firebrick","red","orange","gold","yellow","greenyellow","limegreen","green","darkgreen","darkslategray"]

for i in range(len(todosPeriodos)):
    lim=sum([not np.isnan(n_dataframe.loc[todosPeriodos[i]][x]) for x in range(11)])
    x_list=range(1,lim+1)
    n_list=n_dataframe.loc[todosPeriodos[i]][:lim]
    plt.plot(x_list, n_list, 'o--', linewidth=0.8, label=todosPeriodos[i], color=colors_list[i])

plt.plot(range(1,12), mean_n_hist, 'o--', linewidth=0.8, label="N histórico",color="black")
plt.xticks(range(1,12))
plt.xlabel('Semestre',fontsize=14)
plt.ylabel('Número de estudiantes',fontsize=14)
plt.legend(fontsize=12, loc=1)
plt.title(f"N por cohorte",fontsize=18)
plt.savefig(f'{directory}/cohortes_n.png')
plt.cla()
plt.close()

#%% Sancionados

mean_sancionados_list=[]
desv_sancionados_list=[]
n_sancionados_list=[]
for i in range(9):
    mean_sancionados_list.append(mean_sancionados[i].mean())
    desv_sancionados_list.append(desv_sancionados[i].mean())
    n_sancionados_list.append(n_sancionados[i].sum())

#%% Gráfica de avance para sancionados

plt.figure(figsize=(10,7.5))
x_list=range(1,10)
plt.axhline(y=0, color="black", linewidth=0.8, linestyle='--')
plt.plot(x_list, mean_avance_hist[:9], 'o--', linewidth=0.8, label="Avance promedio histórico")
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

#%% Gráfica de N para sancionados

for sheet_name in xlsx_estudiantes:
    estudiantes = xlsx_estudiantes[sheet_name]
    IBIO = estudiantes['Programa principal'] == "INGENIERIA BIOMEDICA"
    estudiantes = estudiantes[IBIO].reset_index()
    for estudiante in estudiantes["Código est"]:
        if estudiante in sancionados:
            n_sancionados.loc[int(sheet_name)]+=1

plt.figure(figsize=(10,7.5))
x_list=range(1,12)
plt.plot(x_list, mean_n_hist, 'o--', linewidth=0.8, label="N histórico", color="black")
plt.plot(x_list, list(n_sancionados.T.loc[0]), 'o--', linewidth=0.8, label="Número de estudiantes", color="red")
plt.xlabel('Semestre',fontsize=14)
plt.ylabel('Número de estudiantes',fontsize=14)
plt.title(f"Estudiantes sancionados",fontsize=18)
plt.xticks(x_list,list(n_sancionados.T))
plt.legend(fontsize=12, loc=3)
plt.savefig(f'{directory}/sancionados_n.png')

plt.cla()
plt.close()

#%% Gráficas de estadísticas por materia

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

for i in range(len(pensum_courses)):

    directory = f'Results_new/Subject_Results/{pensum_courses[i]}'

    if not os.path.exists(directory):
        os.makedirs(directory)

    x = list(results_dict[pensum_courses[i]].keys())
    x_list = [str(i) for i in x]
    y = [results_dict[pensum_courses[i]][year]['mean'] for year in x]
    y_err = [results_dict[pensum_courses[i]][year]['std_dev'] for year in x]
    n = [results_dict[pensum_courses[i]][year]['n'] for year in x]

    fig, ax = plt.subplots()
    plt.errorbar(x_list, y, yerr=y_err, color='red', linewidth=0.8, fmt='o--', ecolor='black', capsize=7, elinewidth=1, markeredgewidth=1)
    plt.xticks(x_list)
    plt.xlabel('Semestre')
    plt.ylim(min_value-0.1, max_mean+max_desv+0.1)
    plt.ylabel('Avance Promedio')
    ax.axhline(y=0, linestyle='dotted', color='blue')
    #Poner el numero de estudiantes (n) en el cap
    #for y_n, y_val in enumerate(y):
    #    plt.text(x_list[y_n], y_val + y_err[y_n] + 0.1, f'{n[y_n]}', ha='center')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}')
    plt.show()
    ax.text(8.5,6,f'{" Avance promedio: "}{round(np.mean(y),3)}\n{" Desviación promedio: "}{round(np.mean(y_err),3)}', fontsize=10, ha='center', va='center',
        bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))
    plt.savefig(f'Results_new/Subject_Results/{pensum_courses[i]}/mean_desv_{pensum_courses[i]}.png')
    plt.cla()
    plt.close()

##

#Promedio por Niveles 



medias_niveles ={}
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

    fig, ax1 = plt.subplots()

    ax1.bar(x_list, n_est, color="skyblue")
    plt.xticks(x_list)
    plt.xlabel('Semestre')
    plt.ylabel('Número de estudiantes')
    ax1.set_ylim([0,max_n+5])
    ax1.text(1,86,f'{" Avance "}{pensum_courses[i]}{": "}{round(np.mean(y),3)}\n{" Avance Nivel "}{nivel_materia}{": "}{round(np.mean(y_nivel),3)}\n\n{" Estudiantes promedio: "}{round(np.mean(n_est),3)}', fontsize=10, ha='center', va='center',
        bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))
    ax2 = ax1.twinx()
    ax2.plot(x_list,y,'--o', label=f'{pensum_courses[i]}',linewidth=0.8, color='red')
    plt.plot(x_nivel, y_nivel, '--o', label = f'{"Promedio Nivel "}{nivel_materia}' , linewidth=0.8, color='black')
    ax2.grid(False)
    plt.ylabel('Avance promedio')
    ax2.set_ylim([media_min-0.1,media_max+0.15])
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}')
    plt.legend()
    plt.savefig(f'Results_new/Subject_Results/{pensum_courses[i]}/barplot_{pensum_courses[i]}.png')
    plt.cla()
    plt.close()



## RETIROS

excel_retiros = pd.read_excel("Data/Retiros 2018-10 a 202310.xlsx")


filtered_df = excel_retiros[excel_retiros['Materia'].isin(pensum_courses)]

retiros_count = {materia: {periodo[:5]: count for periodo, count in filtered_df[filtered_df['Materia'] == materia]['Periodo'].value_counts().items()} for materia in filtered_df['Materia'].unique()}


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
    
    retirosMateria = retiros_count[pensum_courses[i]]

    result_list_retiros = []
    for item in x_nivel:
        if item in retirosMateria:
            result_list_retiros.append(retirosMateria[item])
        else:
            result_list_retiros.append(0)

            
    fig, ax1 = plt.subplots(figsize=(8, 6))
    x_pos = [i for i, _ in enumerate(x_list)]

    result_total = []

    for p, q in zip(n_est, result_list_retiros):
        result_total.append(p+q)
    ax1.bar([i - 0.2  for i in x_pos], n_est, color="mediumaquamarine", width=0.38, label='Aprobados')
    ax1.bar([i + 0.2  for i in x_pos], result_total, color="cornflowerblue", width=0.38, label='Estudiantes totales')
    ax1.bar([i + 0.2 for i in x_pos], result_list_retiros, color="salmon", width=0.38, label='Retiros')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True, ncol=5)
    #plt.xticks(x_list)
    plt.xlabel('Semestre')
    plt.ylabel('Número de estudiantes')
    ax1.set_ylim([0,max_n+10])
    ax1.text(1,86,f'{" Avance "}{pensum_courses[i]}{": "}{round(np.mean(y),3)}\n{" Avance Nivel "}{nivel_materia}{": "}{round(np.mean(y_nivel),3)}\n\n{" Estudiantes promedio: "}{round(np.mean(n_est),3)}', fontsize=10, ha='center', va='center',
        bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))
    ax2 = ax1.twinx()
    ax2.plot(x_list,y,'--o', label=f'{pensum_courses[i]}',linewidth=0.8, color='red')
    plt.plot(x_nivel, y_nivel, '--o', label = f'{"Promedio Nivel "}{nivel_materia}' , linewidth=0.8, color='black')
    ax2.grid(False)
    plt.ylabel('Avance promedio')
    ax2.set_ylim([media_min-0.1,media_max+0.15])
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}')
    plt.legend()
    plt.savefig(f'Results_new/Subject_Results/{pensum_courses[i]}/retiros_barplot_{pensum_courses[i]}.png', bbox_inches='tight')
    plt.cla()
    plt.close()


list_dict_estudiantes = []
list_dict_retiros = []
list_dict_avance = []

for i in range(len(pensum_courses)):

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

    fig, ax1 = plt.subplots(figsize=(8, 6))
    x_pos = [i for i, _ in enumerate(x_list)]

    result_total = []

    for p, q in zip(n_est, result_list_retiros):
        result_total.append(p+q)
    ax1.bar(x_pos, result_total, color="cornflowerblue", width=0.38, label='Estudiantes totales')
    ax1.bar( x_pos, result_list_retiros, color="salmon", width=0.38, label='Retiros')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True, ncol=5)
    #plt.xticks(x_list)
    plt.xlabel('Semestre')
    plt.ylabel('Número de estudiantes')
    ax1.set_ylim([0,max_n+10])
    ax1.text(1,86,f'{" Avance "}{pensum_courses[i]}{": "}{round(np.mean(y),3)}\n{" Avance Nivel "}{nivel_materia}{": "}{round(np.mean(y_nivel),3)}\n\n{" Estudiantes promedio: "}{round(np.mean(n_est),3)}', fontsize=10, ha='center', va='center',
        bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))
    ax2 = ax1.twinx()
    ax2.plot(x_list,y,'--o', label=f'{pensum_courses[i]}',linewidth=0.8, color='red')
    plt.plot(x_nivel, y_nivel, '--o', label = f'{"Promedio Nivel "}{nivel_materia}' , linewidth=0.8, color='black')
    ax2.grid(False)
    plt.ylabel('Avance promedio')
    ax2.set_ylim([media_min-0.1,media_max+0.15])
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}')
    plt.legend()
    plt.savefig(f'Results_new/Subject_Results/{pensum_courses[i]}/retiros_barplot_{pensum_courses[i]}_uno.png', bbox_inches='tight')
    plt.cla()
    plt.close()


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



divisor = 13

result_list_retiros = []
result_list_estudiantes = []
result_list_avance = []

for i in range(len(retiros_totales)):

    result_list_retiros.append(retiros_totales[i]/divisor)

for i in range(len(estudiantes_totales)):
    result_list_estudiantes.append(estudiantes_totales[i]/divisor)
    result_list_avance.append(avance_general[i]/divisor)



semestreDani = [441,450,473,466,529,410,534,524,522,536,534]
o=[0,0,0,0,63, 89, 38, 92, 62, 49, 10]

sum_list = [semestreDani[i] + o[i] for i in range(len(semestreDani))]

fig, ax1 = plt.subplots(figsize=(8, 6))
ax1.bar(semestres, sum_list, color="cornflowerblue", width=0.5, label='Estudiantes totales')
ax1.bar(retiros_x, retiros_totales, color="salmon", width=0.5, label='Retiros')
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True, ncol=5)
#plt.xticks(x_list)
plt.xlabel('Semestre')
plt.ylabel('Número de estudiantes')
ax2 = ax1.twinx()
ax2.plot(semestres,result_list_avance,'--o', label='Avance general',linewidth=0.8, color='red')

ax2.grid(False)
plt.ylabel('Avance promedio')
ax2.axhline(y=0, linestyle='dotted', color='blue')
plt.title('GRAFICA GENERAL POR PERIODOS')
plt.legend()
plt.savefig(f'Results_new/Subject_Results/grafica_suma.png', bbox_inches='tight')
plt.cla()
plt.close()


fig, ax1 = plt.subplots(figsize=(8, 6))
ax1.bar(semestres, result_list_estudiantes, color="cornflowerblue", width=0.38, label='Estudiantes totales')
ax1.bar(retiros_x, result_list_retiros, color="salmon", width=0.38, label='Retiros')
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True, ncol=5)
#plt.xticks(x_list)
plt.xlabel('Semestre')
plt.ylabel('Número de estudiantes')
ax2 = ax1.twinx()
ax2.plot(semestres,result_list_avance,'--o', label='Avance general',linewidth=0.8, color='red')
ax2.grid(False)
plt.ylabel('Avance promedio')
ax2.axhline(y=0, linestyle='dotted', color='blue')
plt.title('Grafica general (Promedio)')
plt.legend()
plt.savefig(f'Results_new/Subject_Results/grafica_promedio.png', bbox_inches='tight')
plt.cla()
plt.close()

