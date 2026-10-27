import pandas as pd

fact = pd.read_csv("data/processed/fact_rendimiento_academico.csv")
oferta = pd.read_csv("data/processed/dim_oferta.csv")
asignaturas = pd.read_csv("data/processed/dim_asignatura.csv")

df = fact.merge(oferta, on='oferta_id', how='left')
df = df.merge(asignaturas, on='asignatura_id', how='left')

evaluados = df[~df['es_retiro_o_anulado']]

print("=== 1. TASA DE APROBACION POR PERIODO ===")
aprob_periodo = evaluados.groupby('periodo_id').agg(
    total=('matricula_id', 'count'),
    aprobados=('es_aprobado', 'sum'),
    promedio_nota=('nota_final', 'mean')
)
aprob_periodo['tasa_aprobacion_%'] = (aprob_periodo['aprobados'] / aprob_periodo['total']) * 100
print(aprob_periodo[['total', 'tasa_aprobacion_%', 'promedio_nota']])

print("\n=== 2. TOP 5 ASIGNATURAS CON MAYOR REPROBACION ===")
dificultad = evaluados.groupby(['codigo', 'nombre']).agg(
    total=('matricula_id', 'count'),
    reprobados=('es_reprobado', 'sum'),
    promedio_nota=('nota_final', 'mean')
)
dificultad['tasa_reprobacion_%'] = (dificultad['reprobados'] / dificultad['total']) * 100
print(dificultad.sort_values(by='tasa_reprobacion_%', ascending=False).head(5))

print("\n=== 3. COMPARATIVA: PRIMER INTENTO VS REPETICION ===")
intento = evaluados.groupby('intento').agg(
    total=('matricula_id', 'count'),
    tasa_aprobacion=('es_aprobado', 'mean'),
    promedio_nota=('nota_final', 'mean')
)
intento['tasa_aprobacion'] *= 100
print(intento)

print("\n=== 4. CORRELACION ASISTENCIA VS RENDIMIENTO ===")
corr = evaluados[['asistencia_pct', 'nota_final']].corr()
print(corr)
