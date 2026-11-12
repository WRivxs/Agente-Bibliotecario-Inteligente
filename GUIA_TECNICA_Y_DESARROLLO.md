# Guía Técnica y Plan de Desarrollo: Agente Bibliotecario Inteligente

> **Documento de Fundamentación Técnica e Implementación**  
> **Asignatura:** Introducción a los Sistemas Inteligentes  
> **Proyecto:** Agente Bibliotecario Inteligente (Recomendador Explicable de Libros con ML y LLM)  
> **Equipo Investigador:** María Álvarez López, Wadid Rivas Payares, Andrés Acosta Royet, Luis Arraut Turizo  

---

## 1. ¿Qué tipo de Sistema Inteligente se está aplicando?

Para sustentar formalmente el proyecto ante el docente de la asignatura **Introducción a los Sistemas Inteligentes**, el sistema se apoya en **tres pilares fundamentales de la Inteligencia Artificial**:

### A. Teoría de Agentes Inteligentes (Enfoque Russell & Norvig)
El sistema no es un script lineal ni un chatbot rígido; implementa un **Agente Basado en Metas (*Goal-based Agent*)**.
* **Ciclo de Operación del Agente:**
  * **Percepción:** Captura los mensajes, intenciones y contexto del estudiante a través del diálogo.
  * **Razonamiento:** Evalúa si la información recopilada es suficiente para recomendar un recurso o si necesita indagar (repreguntar sobre la materia, tema o nivel).
  * **Acción:** Cuando dispone de los criterios necesarios, toma la decisión autónoma de invocar una herramienta externa (*Tool / Function Calling*) para consultar la base de datos de la biblioteca.

### B. Machine Learning y Procesamiento de Lenguaje Natural (NLP Clásico)
* **Modelo de Espacio Vectorial (*Vector Space Model - VSM*):** Representación matemática de documentos y consultas como vectores en un espacio de características multidimensional.
* **Algoritmo TF-IDF (*Term Frequency - Inverse Document Frequency*):** Ponderación estadística que mide la relevancia de los términos en las sinopsis y temarios de los libros, reduciendo el ruido de palabras vacías (*stopwords*).
* **Métrica de Distancia / Similitud del Coseno:** Cálculo angular del coseno entre el vector de consulta del estudiante y los vectores de los libros del catálogo para determinar los ítems de mayor afinidad semántica.

### C. Inteligencia Artificial Generativa y Explicabilidad (*Explainable AI - XAI*)
* **Arquitectura RAG (*Retrieval-Augmented Generation*):** Fusión entre la recuperación de información determinística/matemática (filtro TF-IDF) y la generación en lenguaje natural.
* **Modelo de Lenguaje Grande (LLM - Google Gemini):** Transforma la salida numérica del modelo de recomendación en una explicación pedagógica personalizada, argumentando con claridad el porqué cada libro es el adecuado para el estudiante.

---

## 2. Lenguaje y Stack Tecnológico

El desarrollo se realiza en **Python 3.10+**, el estándar indiscutible en la industria de la Inteligencia Artificial y la Ciencia de Datos.

| Componente | Tecnología | Justificación Técnica |
| :--- | :--- | :--- |
| **Lenguaje Principal** | **Python 3.10+** | Soporte integral para librerías matemáticas, procesamiento de datos y SDKs de IA. |
| **Manipulación de Datos** | **pandas** | Carga, filtrado, limpieza y estructuración del catálogo (`libros.csv`). |
| **Motor de Machine Learning** | **scikit-learn** | Implementaciones optimizadas de `TfidfVectorizer` y `cosine_similarity` de alta velocidad. |
| **Cerebro del Agente** | **Google Gemini API** (`google-genai`) | Gestión de memoria conversacional (*Multi-turn chat*) y soporte nativo de *Function Calling*. |
| **Interfaz de Usuario (Frontend)** | **Streamlit** | Creación rápida de interfaces web de chat modernas con avatares y tarjetas interactivas en Python puro. |

---

## 3. Estrategia para el Dataset de 1.000 Libros

Para estructurar un catálogo sólido de 1.000 libros académicos sin captura manual, se plantean dos alternativas viables:

### Opción A (Inmediata): Dataset público de Kaggle
Descargar un dataset abierto de libros (Google Books / Amazon Books / O'Reilly) y filtrar mediante un script de Python los 1.000 títulos correspondientes a carreras técnicas y ciencias básicas (*Computer Science, Mathematics, Physics, Programming, Engineering*).

### Opción B (Automatizada): Extracción vía Google Books API
Crear un script en Python que consulte la API pública de Google Books (gratuita y sin tarjeta) para recopilar automáticamente:
* 250 libros de **Programación y Algoritmos**.
* 250 libros de **Matemáticas y Cálculo**.
* 250 libros de **Bases de Datos y Sistemas**.
* 250 libros de **Física y Ciencias Básicas**.

### Esquema de Columnas del Catálogo (`catalogo_libros.csv`)
| Columna | Tipo | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `id` | Entero | Identificador único del registro | `101` |
| `titulo` | Texto | Título formal del libro | *C How to Program* |
| `autor` | Texto | Autor(es) de la obra | *Paul Deitel, Harvey Deitel* |
| `materia` | Texto | Asignatura o área de conocimiento | *Programación* |
| `nivel` | Categórico | Nivel pedagógico de la obra | *Básico*, *Intermedio*, *Avanzado* |
| `descripcion` | Texto | Sinopsis o temario clave (insumo TF-IDF) | *Introducción al control de flujo, punteros, memoria dinámica y estructuras en C...* |
| `portada_url` | URL | Enlace a la imagen de la carátula | `https://books.google.com/.../frontcover.jpg` |

---

## 4. Diseño de la Interfaz de Usuario (Streamlit)

La interfaz se diseña bajo un patrón de chat conversacional moderno:
* **Área central de interacción:** Componentes `st.chat_message` para visualizar el flujo continuo entre el estudiante y el agente bibliotecario.
* **Entrada de usuario:** Componente `st.chat_input` anclado al inferior para escribir consultas en lenguaje natural.
* **Tarjetas visuales de recomendación:** Cuando el agente recomienda un libro, la interfaz despliega:
  * Carátula oficial del libro.
  * Título, autor y etiqueta de dificultad (*Badge*: Básico / Intermedio / Avanzado).
  * Explicación pedagógica generada por el agente destacando los capítulos o enfoques pertinentes.

---

## 5. Plan de Ejecución por Fases

```
[Fase 1: Datos] ──► [Fase 2: Motor ML] ──► [Fase 3: Agente Gemini] ──► [Fase 4: Interfaz Web]
  libros.csv          TF-IDF + Coseno         Tool Calling + Chat        Streamlit App
```

1. **Fase 1: Curaduría del Dataset (`libros.csv`)**  
   Generar o descargar el archivo estructurado con los 1.000 libros académicos y sus metadatos limpios.
2. **Fase 2: Motor de Recomendación Matemático (`recomendador.py`)**  
   Construir la función de Python que recibe los criterios (`tema`, `materia`, `nivel`), calcula las matrices TF-IDF y la similitud del coseno, y retorna los 3 libros más pertinentes.
3. **Fase 3: Agente Autónomo (`agente.py`)**  
   Configurar el cliente de Google Gemini con el *System Prompt* de bibliotecario universitario, historial de conversación y registro de la función de recomendación como herramienta (*Tool*).
4. **Fase 4: Aplicación Web (`app.py`)**  
   Ensamblar el motor y el agente en la interfaz interactiva de Streamlit, lista para demostración y evaluación con usuarios reales.
