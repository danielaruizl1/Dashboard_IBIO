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

Primero, es necesario clonar este repositorio en tu máquina local:
```
git clone https://github.com/danielaruizl1/Dashboard_IBIO.git
```
### Datos 

En la carpeta _**Data**_ se encuentran diferentes archivos que permitirán construir las diferentes gráficas del Dashboard IBIO.

  - **Cursos Unicos 2018-202410.xlsx:** Contiene la información de todos los estudiantes inscritos a cada uno de los cursos desde 2018-10 hasta 2024-10.
  - **Estudiantes IBIO 201810-202410.xlsx:**
  - **Estudiantes Sancionados 2021-10.xlsx:**
  - **Retiros 2018-10 a 202320.xlsx:**


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
