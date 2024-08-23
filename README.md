# Dashboard IBIO

## ¿Qué es?

El Dashboard IBIO es una herramienta diseñada para los docentes del Departamento de Ingeniería Biomédica de la Universidad de los Andes. Esta plataforma facilita el análisis de la distribución de estudiantes en las diversas asignaturas a lo largo de los semestres. Al incorporar datos históricos desde el semestre 2018-1, el dashboard permite identificar tendencias y respaldar la toma de decisiones informadas.

## ¿Como funciona?

El Dashboard IBIO está diseñado para monitorear el progreso académico de cada estudiante en relación con su semestre de ingreso a la universidad y las materias que está cursando en el semestre actual. Para lograr esto,

**1.** Se determina el semestre que cada estudiante debería estar cursando en función del período académico actual.

<p align="center">
<img align="center" img width="500" alt="Screenshot 2024-08-22 at 20 37 43" src="https://github.com/user-attachments/assets/9d396af7-bbfe-4773-8c05-8227b5a9e0b9">
</p>

**2.** Teniendo en cuenta el plan de estudios del programa IBIO, es posible determinar el semestre en el que se espera que cada materia sea cursada por los estudiantes.

<p align="center">
<img align="center" img width="300" alt="Screenshot 2024-08-22 at 20 37 55" src="https://github.com/user-attachments/assets/8689ca94-34e8-429a-ae44-0cddded4387f">
</p>

**3.** Se calcula el progreso de cada estudiante del curso comparando el semestre en el que se encuentra actualmente con el semestre en el que debería haber cursado la materia según el plan de estudios.

<p align="center">
<img width="1200" alt="Screenshot 2024-08-22 at 20 43 31" src="https://github.com/user-attachments/assets/93af64f5-9b54-45f8-8389-b3796ea13eaf">
</p>

4. Finalmente, se genera una lista que muestra la distribución del avance de los estudiantes en el curso.
<p align="center">
<img width="500" alt="Screenshot 2024-08-22 at 20 44 50" src="https://github.com/user-attachments/assets/934bd9c7-b15a-4854-9f4e-18d32093a54d">
</p>


## Ejecución

### Instalaciones

Instalar [python](https://www.python.org/downloads/) (versión 3.11 funciona bien) 

Instalar [Visual Studio Code](https://code.visualstudio.com/download) (VsCode)

Crear cuenta en [Github](https://github.com/) 


### Repositorio
Primero, es necesario clonar este repositorio en tu máquina local:
```
git clone https://github.com/danielaruizl1/Dashboard_IBIO.git
```

### Entorno virtual
Para ejecutar el código del repositorio es necesario crear un entorno de python de la siguiente manera:
```
conda create -n dashboard
conda activate dashboard
conda install python
pip install pandas
pip install matplotlib
pip install tqdm
pip install openpyxl

```

### Datos 

En la carpeta _**Data**_ se encuentran diferentes archivos que permitirán construir las diferentes gráficas del Dashboard IBIO.

  - **Cursos Unicos 2018-202410.xlsx:** Contiene la información de todos los cursos desde 2018-10 hasta 2024-10.
  - **Estudiantes IBIO 201810-202410.xlsx:** Contiene la información de todos estudiantes desde 2018-10 hasta 2024-10.
  - **Estudiantes Sancionados 2021-10.xlsx:** Contiene la información de los estudiantes sancionados en 2021-10.
  - **Retiros 2018-10 a 202320.xlsx:** Contiene la información histórica de todos los retiros desde 2018-10 hasta 2024-10.


### Jupyter Notebook

El archivo [run.ipynb](https://github.com/danielaruizl1/Dashboard_IBIO/blob/main/run.ipynb) contiene varias celdas ejecutables, cada una diseñada para generar un conjunto distinto de gráficas. Es importante ejecutar las celdas en el **orden indicado**, haciendo clic en el botón con el símbolo _play_.
<p align="center">
<img width="400" alt="Screenshot 2024-08-22 at 20 58 09" src="https://github.com/user-attachments/assets/d09b9ed4-a1a5-44f8-80c6-04ae5c9c868f">
</p>


Una vez que cada celda se ejecute correctamente, al finalizar la ejecución, se observará el siguiente símbolo:
<p align="center">
<img width="300" alt="Screenshot 2024-08-22 at 21 16 40" src="https://github.com/user-attachments/assets/c5d44a34-9868-470b-85c0-69ab92ec5b02">
</p>


#### Celda 1: _Definición de Rutas y Variables Importantes_
Esta celda contiene las rutas de los archivos y algunas variables esenciales (como el período actual y el programa principal) necesarias para graficar los datos.

#### Celda 2: _PieCharts por Materia para cada Periodo_

Esta celda permite generar pie-charts por materia, mostrando el avance de cada estudiante en cada período. Es crucial especificar la ruta donde se desea guardar estos resultados antes de ejecutar la celda.
```
directory_name = f'RESULTS_{periodo_actual}/PieCharts_por_Materia'
```
En este caso particular, se creará una carpeta llamada PieCharts_por_Materia que contendrá subcarpetas para cada período. Dentro de cada subcarpeta, habrá carpetas correspondientes a todas las materias del plan de estudios de IBIO, y en su interior se encontrará la imagen del piechart correspondiente.

```
.
├── 20181
│   ├── Biomateriales
│   │   └── piechart_IBIO-2650.png
│   ├── Biomecánica
│   .
│   .
│   .
│   ├── Proc. Señales e Inst. Biomédica
│   ├── Proyecto de Diseño 1
│   └── Proyecto de Diseño 2
.
.
.
├── 20232
└── 20241
```

Los gráficos de pastel obtenidos se visualizarán de la siguiente manera. Es crucial tener en cuenta la escala de colores que indica el avance de los estudiantes: un mayor predominio de rojo representa un menor avance, mientras que el verde indica un mayor progreso.

<p align="center"><img width="825" alt="Screenshot 2024-08-22 at 21 25 47" src="https://github.com/user-attachments/assets/3caff559-d7e3-4386-adef-1f5c129cd04f">

</p>

#### Celda 3: _PieCharts por Cohorte_

Esta celda permite generar pie charts por cohorte, calculando el avance de cada generación de estudiantes que ingresaron al programa de Ingeniería Biomédica. Al igual que en otros casos, es fundamental especificar la ruta donde se desean guardar estos resultados antes de ejecutar la celda.

En este caso, se creará una carpeta para cada periodo (2018-10 hasta 2024-10) donde se encontrarán los piecharts para cada una de las cohortes.
<p align="center">
<img width="840" alt="Screenshot 2024-08-22 at 21 33 48" src="https://github.com/user-attachments/assets/2054b7db-ffd2-4b57-a9bf-ed666f174142">
</p>

#### Celda 4: _Estadísticas históricas por semestre_
Esta celda genera gráficos que muestran el avance de cada cohorte en comparación con el promedio histórico. Esto permite evaluar el progreso de los estudiantes que ingresaron en un semestre particular en relación con todos los estudiantes del programa IBIO. La celda produce gráficos para cada uno de los períodos (desde 2018-10 hasta 2024-10) y un gráfico general que incluye las líneas de todas las cohortes, facilitando un análisis comparativo más directo.

<p align="center">
<img width="1391" alt="Screenshot 2024-08-22 at 21 40 49" src="https://github.com/user-attachments/assets/d7938b54-dd67-41af-93f4-c515ab6e3273">
</p>

#### Celda 5: _Número de estudiantes por Cohorte_

Al igual que la celda 4, esta celda permite generar gráficos que muestran la evolución del número de estudiantes de cada cohorte a lo largo del tiempo. La celda produce gráficos específicos para cada cohorte (desde 2018-10 hasta 2024-10) y un gráfico general que incluye la evolución del número de estudiantes para todas las cohortes, proporcionando una visión integral del cambio en la matrícula a través del tiempo.
<p align="center">
<img width="1390" alt="Screenshot 2024-08-22 at 21 44 43" src="https://github.com/user-attachments/assets/e43a6543-f135-467b-b033-b93d024856ec">
</p>


#### Celda 6: _Avance conjunto con número de estudiantes_
Esta celda genera gráficos combinados que describen tanto el número de estudiantes (en azul claro) como el avance de cada materia (rojo), así como el avance promedio de las materias de ese mismo nivel (negro). Además, el gráfico de la derecha muestra el avance promedio junto con los valores de la desviación estándar.
<p align="center">
<img width="1227" alt="Screenshot 2024-08-22 at 21 51 54" src="https://github.com/user-attachments/assets/7079522b-2266-4a1a-8ed7-829ebdecbd7c">
</p>

#### Celda 7: _Retiros_
Esta celda permite generar gráficos similares a los obtenidos en la celda 6, pero que incorporan información sobre la cantidad de estudiantes que retiraron cada materia en cada semestre. Esto facilita un análisis temporal de los retiros mientras se examina el avance académico.
<p align="center">
<img width="1347" alt="Screenshot 2024-08-22 at 21 55 56" src="https://github.com/user-attachments/assets/f796307a-2263-479e-a312-c6669a055c72">
</p>


#### Celda 8: _Sancionados_

Esta celda permite obtener estadísticas sobre los estudiantes sancionados en 2021-1. Entre los gráficos generados se incluyen el avance de estos estudiantes a lo largo de los semestres y la evolución en su número.
<p align="center">
<img width="826" alt="Screenshot 2024-08-22 at 21 58 32" src="https://github.com/user-attachments/assets/f86a2375-9dd6-40f8-b8a0-a23eaf101b4d">
</p>

#### Celda 9: _Gráficas Generales_

Esta celda permite obtener graficas que resumen las principales estadisticas encontradas y evaluar tendencias a lo largo del tiempo para tomar decisiones informadas. 
