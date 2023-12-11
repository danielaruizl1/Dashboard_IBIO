import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def piecharts_por_materia (counts, cursos, pensum_courses, todosPeriodos, i, j,directory2):

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
    wedges, labels, _ = ax.pie(counts, colors =colors,autopct=lambda x: f'{int(round(x/100.0*sum(counts)))} ({x:.1f}%)', 
                    textprops={'fontsize': 18}, explode = explode_list)
    ax.set_title(f'{cursos[pensum_courses[j]][1]}{" "}{todosPeriodos[i]}{0}', fontsize=24, fontweight='bold')
    handles = [mpatches.Patch(color=color, label=label) for label, color in group_colors.items()]
    legend = ax.legend(handles=handles, loc='upper right', prop={'size': 14})
    for text in legend.get_texts():
        text.set_fontsize(14)  
    plt.savefig(f'{directory2}/piechart_{pensum_courses[j]}.png')
    plt.cla()
    plt.close()


def std_dev_plot (results_dict, pensum_courses, min_value, max_mean, max_desv, cursos, i, directory_name):

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
    ax1.text(1,167,f'{" Avance "}{pensum_courses[i]}{": "}{round(np.mean(y),3)}\n{" Avance Nivel "}{nivel_materia}{": "}{round(np.mean(y_nivel),3)}\n\n{" Estudiantes promedio: "}{round(np.mean(n_est),3)}', fontsize=10, ha='center', va='center',
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
    plt.savefig(f'{directory_name}/Materias/{pensum_courses[i]}/retiros_barplot_{pensum_courses[i]}.png', bbox_inches='tight')
    plt.cla()
    plt.close()


def retiros_plot_resumido (y, x_list, n_est, result_list_retiros, max_n, pensum_courses, x_nivel, y_nivel, nivel_materia, media_min, media_max, cursos, i, directory_name):

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
    ax1.text(1,167,f'{" Avance "}{pensum_courses[i]}{": "}{round(np.mean(y),3)}\n{" Avance Nivel "}{nivel_materia}{": "}{round(np.mean(y_nivel),3)}\n\n{" Estudiantes promedio: "}{round(np.mean(n_est),3)}', fontsize=10, ha='center', va='center',
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
    plt.savefig(f'{directory_name}/Materias/{pensum_courses[i]}/retiros_barplot_{pensum_courses[i]}_resumida.png', bbox_inches='tight')
    plt.cla()
    plt.close()


def graficaSumaRetiros(semestres, sum_list, retiros_x, retiros_totales, result_list_avance, directory):

    fig, ax1 = plt.subplots(figsize=(12, 8))
    ax1.bar(semestres, sum_list, color="cornflowerblue", width=0.5, label='Estudiantes totales')
    ax1.bar(retiros_x, retiros_totales, color="salmon", width=0.5, label='Retiros')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
            fancybox=True, shadow=True, ncol=5)
    #plt.xticks(x_list)
    plt.xlabel('Semestre', fontsize=14)
    plt.ylabel('Número de estudiantes', fontsize=14)
    ax2 = ax1.twinx()
    ax2.plot(semestres,result_list_avance,'--o', label='Avance general',linewidth=0.8, color='red')
    ax2.grid(False)
    plt.ylabel('Avance promedio', fontsize=14)
    ax2.axhline(y=0, linestyle='dotted', color='blue')
    plt.title('GRAFICA GENERAL POR PERIODOS', fontsize=20, fontdict={'fontweight': 'bold'})
    plt.legend()
    plt.savefig(f'{directory}/Materias/grafica_general_por_periodos.png', bbox_inches='tight')
    plt.cla()
    plt.close()
