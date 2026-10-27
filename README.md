# Plataforma de Inteligencia Académica para el Seguimiento de la Trayectoria, Rendimiento Estudiantil y Planificación de Capacidad

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![Architecture](https://img.shields.io/badge/Data_Architecture-Star_Schema-green.svg)](#modelo-dimensional)
[![License: Academic](https://img.shields.io/badge/License-Academic_UCE-darkblue.svg)](#licencia)

> **Trabajo de Titulación - Examen Complexivo (Componente Práctico - Caso 3)**  
> **Institución:** Universidad Central del Ecuador (UCE)  
> **Facultad:** Facultad de Ingeniería y Ciencias Aplicadas (FICA)  
> **Carrera:** Ingeniería en Sistemas de Información  
> **Autor:** Fernando Wladimir Martínez Figueroa  
> **Fecha:** Octubre, 2026

---

## 📋 Descripción del Proyecto

El presente proyecto constituye una **Plataforma de Inteligencia de Negocios (BI) Institucional** diseñada para consolidar, auditar y analizar la trayectoria académica, retención y balance de infraestructura en la Carrera de Ingeniería en Sistemas de Información de la Universidad Central del Ecuador.

Integrando más de **15.538 hechos transaccionales** distribuidos en cinco ciclos lectivos continuos (2024-1 a 2026-1), la solución resuelve la fragmentación entre registros de matrícula, planillas de calificaciones y controles de asistencia mediante un pipeline ETL automatizado y reproducible, un almacén analítico multidimensional con granularidad atómica y un dashboard interactivo de nivel directivo.

---

## 🏛️ Arquitectura de la Solución (4 Capas Desacopladas)

La plataforma opera bajo una arquitectura modular desacoplada que garantiza trazabilidad total desde el indicador gerencial hasta la fuente original:

[CAPA 1: FUENTES OPERACIONALES (RAW)]
├── periodos.csv       (Calendarios académicos y términos)
├── asignaturas.csv    (Malla curricular, códigos y áreas)
├── docentes.csv       (Claustro, categoría y dedicación)
├── estudiantes.csv    (Perfiles y modalidad de ingreso)
├── oferta.csv         (Planificación de secciones y cupos)
├── matriculas.csv     (Eventos de inscripción e intentos)
├── calificaciones.csv (Evaluaciones sumativas: P1, P2, Examen, Final)
└── asistencia.csv     (Control de porcentaje de presencia y faltas)
│
▼
[CAPA 2: INGESTA, STAGING Y PIPELINE ETL (etl_pipeline.py)]
├── Tipado fuerte y normalización léxica
├── Ejecución de 3 Controles de Calidad y Conciliación
├── Aplicación de Reglas de Negocio (exclusión de retiros, centinelas)
└── Derivación analítica de banderas vectorizadas
│
▼
[CAPA 3: ALMACÉN ANALÍTICO MULTIDIMENSIONAL (DATA MART)]
├── Tabla de Hechos: Fact_Rendimiento_Academico (Grano: matricula_id)
└── Dimensiones Conformadas: Dim_Estudiante, Dim_Docente, Dim_Asignatura, Dim_Periodo, Dim_Oferta
│
▼
[CAPA 4: PRESENTACIÓN Y CONSUMO ANALÍTICO]
├── Cuadro de Mando Ejecutivo (KPIs y macrotendencias temporales)
├── Diagnóstico Académico (Dispersión bivariada y alertas tempranas)
├── Auditoría de Capacidad de Aulas (Control de secciones en sobrecupo)
└── Gobernanza de Datos (Control de acceso basado en roles - RBAC)

---

## 📐 Modelo Dimensional (Esquema en Estrella / Constelación)

* **Nivel de Granularidad:** Atómica, definida como **una fila por cada inscripción individual de un estudiante en un paralelo y período lectivo específico (`matricula_id`)**.
* **Justificación:** Preserva el historial íntegro de intentos de repitencia (1er intento vs. 2da y 3ra matrícula), notas parciales y control de asistencia sin la pérdida de resolución que provocan las agregaciones prematuras.

---

## ⚙️ Reglas de Negocio Formalizadas

1. **Tratamiento de Retiros y Anulaciones:** Todo registro con estado `RETIRADO` o `ANULADO` se excluye estrictamente del denominador para la *Tasa Neta de Aprobación*, evitando castigar la efectividad docente con deserciones administrativas. Se audita de forma independiente en la *Tasa de Retiro*.
2. **Registros sin Calificación Asentada:** Se aíslan mediante la bandera `nota_valida = False` en lugar de imputar ceros (0.00) arbitrarios que sesguen la media de rendimiento.
3. **Tratamiento de Repeticiones:** Se preserva el número secuencial de intento (`1`, `2`, `3`) y se genera la bandera `es_repitencia`, permitiendo contrastar de forma independiente a la cohorte regular frente a quienes recursan.
4. **Imputación de Asistencias Faltantes:** Se asigna el valor centinela `-1.00` y la bandera `asistencia_imputada = True`, excluyéndolos de los cálculos de correlación y dispersión para evitar sesgos de covarianza.

---

## 🛡️ Controles de Calidad y Auditoría (Conciliaciones)

El script `etl_pipeline.py` ejecuta automáticamente tres controles de consistencia sobre los **15.538 hechos**[cite: 17]:

| Control | Prueba Realizada | Condición Validada | Resultado Numérico | Estado |
| :---: | :--- | :--- | :---: | :---: |
| **Control 1** | **Integridad Referencial** | $\text{Count}(\text{calif})_{\text{huérfanas}} = 0 \land \text{Count}(\text{asist})_{\text{huérfanas}} = 0$ | **0 huérfanas** | Conforme (100% trazable) |
| **Control 2** | **Auditoría de Aulas** | $\text{Inscritos Reales} \le \text{Cupo Planificado}$ | **145 sobrecupos** | 🚨 Alerta Operativa Crítica |
| **Control 3** | **Consistencia Lógica** | $\text{Si Aprobado} \implies \text{Nota Final} \ge 14.00$ | **0 inconsistencias** | Conforme (Reglamento UCE) |

---

## 📊 Hallazgos Analíticos Clave

1. **Evolución Temporal Ascendente:** La tasa de aprobación neta institucional creció de **52,74% en 2024-1 a 57,55% en 2026-1** (+4,81 puntos porcentuales), con un promedio general estable de **14,21 / 20**[cite: 17].
2. **Concentración Crítica de Reprobación:** Cinco asignaturas concentran tasas de reprobación superiores al 68%, conformando el cuello de botella curricular[cite: 17]:
   * `ISI101` Análisis Matemático I: **82,89%**[cite: 17]
   * `ISI207` Programación I: **77,22%**[cite: 17]
   * `ISI102` Fundamentos de Programación: **72,94%**[cite: 17]
   * `ISI206` Análisis Matemático II: **72,85%**[cite: 17]
   * `ISI311` Programación II: **68,26%**[cite: 17]
3. **Curva Favorable de Repitencia:** La tasa de éxito asciende progresivamente según el intento: **Intento 1 (52,89%)**, **Intento 2 (61,74%)** e **Intento 3 (74,79%)**, demostrando consolidación de competencias tras recursar[cite: 17].
4. **Asistencia vs. Calificación (Criterio Metodológico):** Coeficiente de correlación lineal de Pearson de **$r = 0,206$** (asociación positiva moderada/baja)[cite: 17]. **Fundamento:** Correlación no implica causalidad; asistir a clase acompaña el proceso pero no garantiza por sí solo el dominio de competencias abstractas[cite: 17].
5. **Saturación Física:** **145 secciones (33,6% de la oferta)** operan por encima del cupo planificado, afectando principalmente laboratorios de software[cite: 17].

---

## 📂 Estructura del Repositorio

```text
plataforma-bi-academica-uce/
│
├── data/
│   ├── raw/                  # Fuentes operacionales originales (8 CSVs)
│   └── processed/            # Data Mart analítico normalizado (Tablas de Hechos y Dimensiones)
│       ├── fact_rendimiento_academico.csv
│       ├── dim_estudiante.csv
│       ├── dim_docente.csv
│       ├── dim_asignatura.csv
│       ├── dim_periodo.csv
│       └── dim_oferta.csv
│
├── docs/                     # Documentación formal de titulación
│   ├── Informe_Ejecutivo_3_Paginas_Fernando_Martinez.docx
│   ├── Informe_Completo_Complexivo_UCE_Fernando_Martinez.docx
│   └── modelo_estrella_diagrama.png
│
├── etl_pipeline.py           # Pipeline ETL automatizado, controles de calidad y exportación
├── exploratory_eda.py        # Script analítico de cálculo de KPIs institucionales
├── dashboard_pro.py          # Plataforma visual interactiva (Streamlit)
├── requirements.txt          # Dependencias y librerías del proyecto
├── .gitignore                # Reglas de exclusión para control de versiones
└── README.md                 # Documentación técnica del proyecto

🚀 Instalación y Guía de Uso
1. Clonar el repositorio
git clone [https://github.com/Wmartinez1203/plataforma-bi-academica-uce.git](https://github.com/Wmartinez1203/plataforma-bi-academica-uce.git)
cd plataforma-bi-academica-uce
2. Crear y activar entorno virtual
python -m venv venv
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux/Mac:
source venv/bin/activate
3. Instalar dependencias
pip install -r requirements.txt
4. Ejecutar el Pipeline ETL y Auditoría de Calidad
python etl_pipeline.py
Valida automáticamente los 3 controles de calidad y genera el Data Mart en data/processed/[cite: 17].

5. Iniciar la Plataforma Visual (Dashboard)
streamlit run dashboard_pro.py
Se abrirá automáticamente en tu navegador web en http://localhost:8501 con vistas Ejecutiva, Diagnóstico y Auditoría de Capacidad[cite: 17].

🔒 Gobierno de Datos y Seguridad (RBAC)
Perfil Directivo (Decanato / Dirección): Acceso a métricas macro agregadas, tendencias y auditoría de sobrecupos con identificadores disociados mediante hash unidireccional SHA-256[cite: 17].

Perfil Operativo (Bienestar Estudiantil / Tutores): Acceso a la vista de diagnóstico y matriz de alerta temprana (P1 < 7.00 o Asistencia < 75%) para asignación de tutorías bajo acuerdos de confidencialidad y registro en logs de auditoría[cite: 17].

Perfil Docente: Delimitado estrictamente al seguimiento de notas y asistencia de los paralelos bajo su responsabilidad directa[cite: 17].

🔄 Protocolo de Actualización Incremental
Para incorporar futuros semestres (ej. 2026-2) sin reconstrucción manual[cite: 17]:

Depositar los archivos CSV actualizados en data/raw/[cite: 17].

Ejecutar python etl_pipeline.py[cite: 17].

El pipeline detecta el nuevo ciclo lectivo, ejecuta los controles de consistencia y regenera el Data Mart[cite: 17].

El Dashboard en Streamlit o Power BI actualiza sus selectores y gráficos en memoria mediante @st.cache_data sin requerir modificaciones en el código fuente[cite: 17].

👨‍💻 Autor
Fernando Wladimir Martínez Figueroa

Estudiante / Egresado en Ingeniería en Sistemas de Información

Facultad de Ingeniería y Ciencias Aplicadas (FICA)

Universidad Central del Ecuador

📧 Contacto: wladimirmartinez1203@gmail.com

🐙 GitHub: @Wmartinez1203
