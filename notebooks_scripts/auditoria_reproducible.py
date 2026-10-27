# ==============================================================================
# UNIVERSIDAD CENTRAL DEL ECUADOR - FICA - ISI
# CASO 3: INTELIGENCIA ACADÉMICA - AUDITORÍA REPRODUCIBLE (COLAB / JUPYTER)
# ==============================================================================

import pandas as pd
import numpy as np

# 1. CARGA DE TABLAS PROCESADAS
fact = pd.read_csv("data/processed/fact_rendimiento_academico.csv")
oferta = pd.read_csv("data/processed/dim_oferta.csv")
asig = pd.read_csv("data/processed/dim_asignatura.csv")

# 2. ENLACE ANALÍTICO
df = fact.merge(oferta, on="oferta_id", how="left").merge(asig, on="asignatura_id", how="left")
evaluados = df[~df["es_retiro_o_anulado"]]

# 3. VERIFICACIÓN DE REQUISITOS CLAVE
print("=== VERIFICACIÓN FORMAL DE MÉTRICAS ===")
print(f"Total Inscripciones: {len(df)}")
print(f"Total Retiros Excluidos: {df['es_retiro_o_anulado'].sum()}")
print(f"Tasa Global Aprobación: {(evaluados['es_aprobado'].mean()*100):.2f}%")
print(f"Correlación Asistencia vs Nota Final: {evaluados[['asistencia_pct', 'nota_final']].corr().iloc[0,1]:.4f}")
