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
