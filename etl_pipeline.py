import pandas as pd
import numpy as np
import os

RAW_PATH = "data/raw"
OUTPUT_PATH = "data/processed"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def ejecutar_etl():
    print("=== 1. CARGA DE FUENTES BRUTAS ===")
    periodos = pd.read_csv(f"{RAW_PATH}/periodos.csv")
    asignaturas = pd.read_csv(f"{RAW_PATH}/asignaturas.csv")
    docentes = pd.read_csv(f"{RAW_PATH}/docentes.csv")
    estudiantes = pd.read_csv(f"{RAW_PATH}/estudiantes.csv")
    oferta = pd.read_csv(f"{RAW_PATH}/oferta.csv")
    matriculas = pd.read_csv(f"{RAW_PATH}/matriculas.csv")
    calificaciones = pd.read_csv(f"{RAW_PATH}/calificaciones.csv")
    asistencia = pd.read_csv(f"{RAW_PATH}/asistencia.csv")

    print(f"Total registros cargados -> Matriculas: {len(matriculas)}, Calificaciones: {len(calificaciones)}, Asistencia: {len(asistencia)}")

    print("\n=== 2. CONTROLES DE CALIDAD Y CONCILIACION ===")
    calif_huerfanas = calificaciones[~calificaciones['matricula_id'].isin(matriculas['matricula_id'])]
    asist_huerfanas = asistencia[~asistencia['matricula_id'].isin(matriculas['matricula_id'])]
    print(f"[Control 1] Calificaciones huerfanas: {len(calif_huerfanas)} | Asistencias huerfanas: {len(asist_huerfanas)}")

    conteo_mat = matriculas.groupby('oferta_id').size().reset_index(name='alumnos_inscritos')
    oferta_audit = oferta.merge(conteo_mat, on='oferta_id', how='left').fillna({'alumnos_inscritos': 0})
    sobrecupos = oferta_audit[oferta_audit['alumnos_inscritos'] > oferta_audit['cupo']]
    print(f"[Control 2] Secciones con sobrecupo detectadas: {len(sobrecupos)}")

    calif_inconsistentes = calificaciones[
        (calificaciones['estado_academico'].astype(str).str.upper() == 'APROBADO') & (calificaciones['nota_final'] < 14.0)
    ]
    print(f"[Control 3] Aprobados inconsistentes con nota < 14.0: {len(calif_inconsistentes)}")

    print("\n=== 3. APLICACION DE REGLAS DE NEGOCIO Y MODELADO DIMENSIONAL ===")
    fact = matriculas.merge(calificaciones, on='matricula_id', how='left')
    fact = fact.merge(asistencia, on='matricula_id', how='left')

    fact['es_retiro_o_anulado'] = fact['estado_matricula'].astype(str).str.upper().isin(['RETIRADO', 'ANULADO']) | \
                                  fact['estado_academico'].astype(str).str.upper().isin(['RETIRADO', 'ANULADO'])

    fact['asistencia_imputada'] = fact['asistencia_pct'].isna()
    fact['asistencia_pct_calc'] = fact['asistencia_pct'].fillna(-1)

    fact['es_aprobado'] = np.where(fact['estado_academico'].astype(str).str.upper() == 'APROBADO', 1, 0)
    fact['es_reprobado'] = np.where(fact['estado_academico'].astype(str).str.upper() == 'REPROBADO', 1, 0)
    fact['es_repitencia'] = np.where(fact['intento'] > 1, 1, 0)

    fact['alerta_vulnerabilidad'] = np.where(
        (fact['asistencia_pct'] < 75.0) | (fact['nota_primer_parcial'] < 7.0), 
        1, 0
    )

    print("\n=== 4. EXPORTACION DEL MODELO ANALITICO ===")
    fact.to_csv(f"{OUTPUT_PATH}/fact_rendimiento_academico.csv", index=False)
    estudiantes.to_csv(f"{OUTPUT_PATH}/dim_estudiante.csv", index=False)
    docentes.to_csv(f"{OUTPUT_PATH}/dim_docente.csv", index=False)
    asignaturas.to_csv(f"{OUTPUT_PATH}/dim_asignatura.csv", index=False)
    periodos.to_csv(f"{OUTPUT_PATH}/dim_periodo.csv", index=False)
    oferta.to_csv(f"{OUTPUT_PATH}/dim_oferta.csv", index=False)
    
    print(f"Modelo dimensional exportado exitosamente a '{OUTPUT_PATH}/'")

if __name__ == "__main__":
    ejecutar_etl()
