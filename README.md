# 📚 Agente Bibliotecario Inteligente
### Sistema Conversacional de Recomendación Explicable de Libros Académicos

> **Asignatura:** Introducción a los Sistemas Inteligentes  
> **Proyecto:** Proyecto de Aula - Entrega Final  
> **Equipo Investigador:**  
> * María Álvarez López  
> * Wadid Rivas Payares  
> * Andrés Acosta Royet  
> * Luis Arraut Turizo  

---

## 🌐 Enlaces Clave del Proyecto

| Recurso | Enlace Directo | Descripción |
| :--- | :--- | :--- |
| 🚀 **Aplicación en Vivo (Cloud)** | **[https://agente-bibliotecario-inteligente-wrivas.streamlit.app/](https://agente-bibliotecario-inteligente-wrivas.streamlit.app/)** | Despliegue 24/7 en la nube para probar el sistema sin instalar nada |
| 💻 **Repositorio GitHub** | **[https://github.com/WRivxs/Agente-Bibliotecario-Inteligente](https://github.com/WRivxs/Agente-Bibliotecario-Inteligente)** | Código fuente completo, historial de commits y control de versiones |
| 🎨 **Prototipo 3D Interactivo** | Archivo local: `arquitectura_3d.html` | Visualizador 3D por capas interactivo (Three.js) para sustentación |

---

## 🧠 ¿Cómo se aplica como Sistema Inteligente? (Fundamentación Teórica)

El proyecto integra de manera coherente **tres ramas fundamentales de la Inteligencia Artificial**:

### 1. Teoría de Agentes Inteligentes (Russell & Norvig)
El sistema no es un script rígido ni un árbol de decisiones fijo; implementa un **Agente Basado en Metas (*Goal-based Agent*)**:
* **Percepción:** El agente percibe y analiza el lenguaje natural del estudiante, deduciendo su necesidad, asignatura y nivel de abstracción requerido.
* **Razonamiento:** Posee memoria conversacional (*Multi-turn chat*) y un *System Prompt* pedagógico. Si la consulta del alumno es vaga o incompleta, indaga proactivamente antes de asumir.
* **Acción (*Tool Calling / Function Calling*):** Cuando el agente dispone de los criterios suficientes, decide **de forma autónoma** invocar la función `buscar_libros()`, pasando los términos clave técnicos correspondientes.

### 2. Machine Learning y Procesamiento de Lenguaje Natural (NLP Clásico)
El motor de recuperación de información opera bajo modelos matemáticos formales:
* **Modelo de Espacio Vectorial (*Vector Space Model - VSM*):** Representación de los textos como vectores en un espacio multidimensional.
* **Algoritmo TF-IDF (*Term Frequency - Inverse Document Frequency*):** Ponderación estadística entrenada sobre **25.000 n-gramas (1, 2)** con escalado sublineal `sublinear_tf=True` y diccionario de equivalencias bilingües (Español ⇄ Inglés).
* **Métrica de Similitud del Coseno:** Calcula el coseno del ángulo formado entre el vector de la consulta del estudiante ($\vec{q}$) y los vectores de las sinopsis de los libros ($\vec{d}$):
  $$\text{similitud}(\vec{q}, \vec{d}) = \frac{\vec{q} \cdot \vec{d}}{\|\vec{q}\| \|\vec{d}\|}$$
  Esto permite obtener un índice porcentual objetivo de pertinencia temática con tiempos de inferencia de apenas **15 milisegundos**.

### 3. Inteligencia Artificial Generativa y Explicable (*Explainable AI - XAI / RAG*)
* **Arquitectura RAG (*Retrieval-Augmented Generation*):** El modelo de lenguaje grande (**Google Gemini 3.1 Flash Lite**) no inventa libros (*alucinación*); se alimenta estrictamente de los libros recuperados del catálogo real por el motor TF-IDF.
* **Explicabilidad Pedagógica:** El agente traduce los datos numéricos en una justificación humana: explica por qué recomienda cada título, qué capítulos o diagramas le servirán al estudiante y utiliza analogías didácticas adaptadas a su nivel.

---

## 🏛️ Arquitectura del Sistema por Capas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAPA 1: PRESENTACIÓN Y UX                             │
│  • Interfaz Web Abierta y Responsiva (Streamlit 1.35+)                       │
│  • Panel Split-Screen / Canvas con Visor Oficial de Google Books Embed      │
│  • Tarjetas dinámicas con Insignia de Nivel y Afinidad TF-IDF               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Consulta en Lenguaje Natural
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CAPA 2: AGENTE AUTÓNOMO COGNITIVO                        │
│  • Cerebro: Google Gemini 3.1 Flash Lite (google-genai SDK)                 │
│  • Memoria Conversacional Multi-turn + System Prompt Pedagógico             │
│  • Mecanismo de Tool / Function Calling hacia 'buscar_libros()'             │
│  • Explicabilidad (XAI) y Re-ranqueo pedagógico de candidatos                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Invocación de Herramienta
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 CAPA 3: MOTOR DE MACHINE LEARNING & NLP                     │
│  • Modelo de Espacio Vectorial (scikit-learn TfidfVectorizer)               │
│  • Matriz de Vocabulario de 25.000 dimensiones                              │
│  • Similitud del Coseno angular (cosine_similarity)                         │
│  • Normalización y expansión léxica bilingüe (ES ⇄ EN)                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Cálculo matricial sobre el dataset
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  CAPA 4: DATOS & CATÁLOGO ACADÉMICO                         │
│  • 2.521 libros universitarios únicos y verificados                         │
│  • 53 áreas del conocimiento clasificadas                                   │
│  • Metadatos: Título, Autores, Materia, Nivel, Sinopsis, Portada, Book ID    │
│  • Archivo estructurado: 'data/catalogo_libros.csv'                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Contenido del Proyecto Comprimido

El archivo comprimido contiene la totalidad de los recursos necesarios para que el proyecto sea 100% funcional:

```
proyecto_sistemas_inteligente/
│
├── 📄 app.py                                   # Aplicación web principal en Streamlit (Frontend & UX)
├── 📄 agente.py                                # Agente de IA con Gemini 3.1 y Tool Calling
├── 📄 recomendador.py                          # Motor de Machine Learning (TF-IDF + Coseno)
├── 📄 requirements.txt                         # Dependencias y librerías de Python
├── 📄 .env                                     # Configuración de variables de entorno (API Key)
├── 📄 arquitectura_3d.html                     # Visualizador 3D interactivo en Three.js
│
├── 📁 data/
│   └── 📄 catalogo_libros.csv                  # Dataset oficial con los 2.521 libros académicos
│
├── 📁 scripts/
│   └── 📄 generar_dataset.py                   # Script de descarga y curaduría vía Google Books API
│
├── 📄 README.md                                # Ficha técnica y arquitectura del proyecto
├── 📄 ENTREGA_PROYECTO_LINKS_Y_ARQUITECTURA.md # Documento formal de entrega para el docente
├── 📄 PROPUESTA_PROYECTO.md                    # Documento académico formal de la propuesta
├── 📄 GUIA_TECNICA_Y_DESARROLLO.md             # Guía técnica de desarrollo y sustentación
└── 📄 Propuesta_Proyecto_de_Aula.docx          # Documento de texto original de la propuesta
```

---

## 💻 Instrucciones para Ejecución Local

Si el docente o evaluador desea ejecutar el proyecto en su máquina local:

1. **Clonar o descomprimir el archivo:**
   Asegúrese de estar ubicado en la carpeta raíz del proyecto.

2. **Instalar dependencias necesarias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación con Streamlit:**
   ```bash
   streamlit run app.py
   ```
   *(La aplicación se abrirá automáticamente en el navegador en `http://localhost:8501`).*

4. **Para ver la arquitectura en 3D:**
   Hacer doble clic sobre el archivo `arquitectura_3d.html` para abrirlo en cualquier navegador web moderno (Chrome, Edge, Firefox).
