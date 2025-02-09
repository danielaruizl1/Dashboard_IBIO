import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import openpyxl
import os

def piecharts_por_materia (counts, cursos, pensum_courses, todosPeriodos, i, j,directory2, avance_promedio):

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

    colors = [group_colors[group] for group in counts.index]
    explode = 0.05
    explode_list = [explode] * len(counts)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(f'{cursos[pensum_courses[j]][1]}{" "}{todosPeriodos[i]}{0}', fontsize=24, fontweight='bold')
    wedges, labels, _ = ax.pie(counts, colors =colors,autopct=lambda x: f'{int(round(x/100.0*sum(counts)))} ({x:.1f}%)', textprops={'fontsize': 18}, explode = explode_list)
    #handles = [mpatches.Patch(color=color, label=label) for label, color in group_colors.items()]
    #legend = ax.legend(title=f"Avance promedio: {avance_promedio}", loc='upper right', prop={'size': 14})
    #for text in legend.get_texts():
        #text.set_fontsize(14) 
    ax.text(0.5, 0.98, f"Avance promedio: {avance_promedio:.2f}", 
        transform=ax.transAxes, fontsize=16, 
        verticalalignment='top', horizontalalignment='center')
    plt.savefig(f'{directory2}/piechart_{pensum_courses[j]}.png')
    plt.cla()
    plt.close()

def plot_avance_cohortes(period, results, directory_name, avance_promedio):

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
        #legend = plt.legend(results[anio].keys(), prop={'size': 14})
        plt.text(0.5, 0.95, f"Avance promedio: {np.mean(avance_promedio[anio]):.2f}", fontsize=16, ha='center', va='bottom', transform=plt.gca().transAxes)
        directory = f'{directory_name}/{period}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(f'{directory}/piechart_{str(anio)}.png')
        plt.cla()
        plt.close()

def plot_avance_all_cohortes(period, results, directory_name, avance_promedio):

    group_colors_2 = {
    '>3': '#d3554c',
    '3-2': '#fc6c64',
    '2-1': '#feb268',
    '1-0': '#f7e16a',
    '0-1': '#ffe9af',
    '-1-2': '#d3e1a2',
    '-2-3': '#a9e070',
    }

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
    #plt.legend(all_cohortes.keys())
    plt.text(0.5, 0.95, f"Avance promedio: {avance_promedio:.2f}", 
         fontsize=16, ha='center', va='bottom', transform=plt.gca().transAxes)
    directory = f'{directory_name}/{period}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(f'{directory}/piechart_all_cohortes.png')
    plt.cla()
    plt.close()

def std_dev_plot (results_dict, pensum_courses, min_value, max_mean, max_desv, cursos, i, directory_name):
    plt.style.use('ggplot')
    x = list(results_dict[pensum_courses[i]].keys())
    x_list = [str(i) for i in x]
    y = [results_dict[pensum_courses[i]][year]['mean'] for year in x]
    y_err = [results_dict[pensum_courses[i]][year]['std_dev'] for year in x]
    n = [results_dict[pensum_courses[i]][year]['n'] for year in x]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.errorbar(x_list, y, yerr=y_err, color='red', linewidth=0.8, fmt='o--', ecolor='black', capsize=7, elinewidth=1, markeredgewidth=1)
    plt.xticks(x_list)
    plt.xlabel('Semestre', fontsize=14)
    plt.ylim(min_value-0.1, max_mean+max_desv+0.1)
    plt.ylabel('Avance Promedio', fontsize=14)
    ax.axhline(y=0, linestyle='dotted', color='blue')
    #Poner el numero de estudiantes (n) en el cap
    #for y_n, y_val in enumerate(y):
    #    plt.text(x_list[y_n], y_val + y_err[y_n] + 0.1, f'{n[y_n]}', ha='center')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}', fontsize=20, fontdict={'fontweight': 'bold'})
    ax.text(8.5,6,f'{" Avance promedio: "}{round(np.mean(y),3)}\n{" Desviación promedio: "}{round(np.mean(y_err),3)}', fontsize=12, ha='center', va='center',
            bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))
    plt.savefig(f'{directory_name}/Materias/{pensum_courses[i]}/mean_desv_{pensum_courses[i]}.png')
    plt.cla()
    plt.close()


def comparacionNivelPlot (directory_name,y,x_list, n_est, max_n, pensum_courses,i,x_nivel,y_nivel, nivel_materia,media_min, media_max, cursos):
    plt.style.use('ggplot')
    fig, ax1 = plt.subplots(figsize=(12, 8))

    ax1.bar(x_list, n_est, color="skyblue")
    plt.xticks(x_list)
    plt.xlabel('Semestre', fontsize=14)
    plt.ylabel('Número de estudiantes', fontsize=14)
    ax1.set_ylim([0,max_n+5])
    ax1.text(1,157,f'{" Avance "}{pensum_courses[i]}{": "}{round(np.mean(y),3)}\n{" Avance Nivel "}{nivel_materia}{": "}{round(np.mean(y_nivel),3)}\n\n{" Estudiantes promedio: "}{round(np.mean(n_est),3)}', fontsize=12, ha='center', va='center',
            bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))
    ax2 = ax1.twinx()
    ax2.plot(x_list,y,'--o', label=f'{pensum_courses[i]}',linewidth=0.8, color='red')
    plt.plot(x_nivel, y_nivel, '--o', label = f'{"Promedio Nivel "}{nivel_materia}' , linewidth=0.8, color='black')
    ax2.grid(False)
    plt.ylabel('Avance promedio', fontsize=14)
    ax2.set_ylim([media_min-0.1,media_max+0.15])
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}', fontsize=20, fontdict={'fontweight': 'bold'})
    plt.legend(loc='upper right')
    plt.savefig(f'{directory_name}/Materias/{pensum_courses[i]}/barplot_{pensum_courses[i]}.png')
    plt.cla()
    plt.close()


def retiros_plot(y, x_list, n_est, result_list_retiros, max_n, pensum_courses, x_nivel, y_nivel, nivel_materia, media_min, media_max, cursos, i, directory_name):
    plt.style.use('ggplot')
    fig, ax1 = plt.subplots(figsize=(12, 8))
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
    plt.xlabel('Semestre', fontsize=14)
    plt.ylabel('Número de estudiantes', fontsize=14)
    ax1.set_ylim([0,max_n+10])
    ax1.text(1,93,f'{" Avance "}{pensum_courses[i]}{": "}{round(np.mean(y),3)}\n{" Avance Nivel "}{nivel_materia}{": "}{round(np.mean(y_nivel),3)}\n\n{" Estudiantes promedio: "}{round(np.mean(n_est),3)}', fontsize=10, ha='center', va='center',
            bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))
    ax2 = ax1.twinx()
    ax2.plot(x_list,y,'--o', label=f'{pensum_courses[i]}',linewidth=1.5, color='red')
    plt.plot(x_nivel, y_nivel, '--o', label = f'{"Promedio Nivel "}{nivel_materia}' , linewidth=1.5, color='black')
    ax2.grid(False)
    plt.ylabel('Avance promedio', fontsize=14)
    ax2.set_ylim([media_min-0.1,media_max+0.15])
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}', fontsize=20, fontdict={'fontweight': 'bold'})
    plt.legend(loc='upper right')
    plt.savefig(f'{directory_name}/Materias/{pensum_courses[i]}/retiros_barplot_{pensum_courses[i]}.png', bbox_inches='tight')
    plt.cla()
    plt.close()


def retiros_plot_resumido (y, x_list, n_est, result_list_retiros, max_n, pensum_courses, x_nivel, y_nivel, nivel_materia, media_min, media_max, cursos, i, directory_name):
    plt.style.use('ggplot')
    fig, ax1 = plt.subplots(figsize=(12, 8))
    x_pos = [i for i, _ in enumerate(x_list)]

    result_total = []

    for p, q in zip(n_est, result_list_retiros):
        result_total.append(p+q)
    ax1.bar(x_pos, result_total, color="cornflowerblue", width=0.38, label='Estudiantes totales')
    ax1.bar( x_pos, result_list_retiros, color="salmon", width=0.38, label='Retiros')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
            fancybox=True, shadow=True, ncol=5)
    #plt.xticks(x_list)
    plt.xlabel('Semestre', fontsize=14)
    plt.ylabel('Número de estudiantes', fontsize=14)
    ax1.set_ylim([0,max_n+10])
    ax1.text(1,85,f'{" Avance "}{pensum_courses[i]}{": "}{round(np.mean(y),3)}\n{" Avance Nivel "}{nivel_materia}{": "}{round(np.mean(y_nivel),3)}\n\n{" Estudiantes promedio: "}{round(np.mean(n_est),3)}', fontsize=10, ha='center', va='center',
            bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))
    ax2 = ax1.twinx()
    ax2.plot(x_list,y,'--o', label=f'{pensum_courses[i]}',linewidth=1.5, color='red')
    plt.plot(x_nivel, y_nivel, '--o', label = f'{"Promedio Nivel "}{nivel_materia}' , linewidth=1.5, color='black')
    ax2.grid(False)
    plt.ylabel('Avance promedio', fontsize=14)
    ax2.set_ylim([media_min-0.1,media_max+0.15])
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title(f'{pensum_courses[i]}{" "}{cursos[pensum_courses[i]][1]}', fontsize=20, fontdict={'fontweight': 'bold'})
    plt.legend(loc='upper right')
    plt.savefig(f'{directory_name}/Materias/{pensum_courses[i]}/retiros_barplot_{pensum_courses[i]}_resumida.png', bbox_inches='tight')
    plt.cla()
    plt.close()


def graficaSumaRetiros(semestres, sum_list, retiros_x, retiros_totales, result_list_avance, directory):
    plt.style.use('ggplot')
    fig, ax1 = plt.subplots(figsize=(12, 8))
    ax1.bar(semestres, sum_list, color="cornflowerblue", width=0.5, label='Registros totales')
    ax1.bar(retiros_x, retiros_totales, color="salmon", width=0.5, label='Retiros')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
            fancybox=True, shadow=True, ncol=5)
    #plt.xticks(x_list)
    plt.xlabel('Semestre', fontsize=14)
    plt.ylabel('Número de estudiantes', fontsize=14)
    ax2 = ax1.twinx()
    ax2.plot(semestres,result_list_avance,'--o', label='Avance general',linewidth=2, color='red')
    ax2.grid(False)
    plt.ylabel('Avance promedio', fontsize=14)
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title('GRÁFICA GENERAL POR PERIODOS', fontsize=20, fontdict={'fontweight': 'bold'})
    plt.legend()
    plt.savefig(f'{directory}/Materias/grafica_general_por_periodos.png', bbox_inches='tight')
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
    ax2.plot(n_semestres, mean_avance_hist,'--o', label='Avance general',linewidth=2, color='red')
    ax2.grid(False)
    plt.ylabel('Avance promedio')
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title('GRÁFICA GENERAL POR SEMESTRES', fontsize=18, fontweight='bold')
    plt.legend()
    plt.savefig(f'{directory_name}/grafica_general_semestre.png', bbox_inches='tight')
    plt.cla()   
    plt.close()