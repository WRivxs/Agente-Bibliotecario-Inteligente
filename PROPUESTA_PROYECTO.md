# Agente Bibliotecario Inteligente: Sistema Conversacional de Recomendación Explicable de Libros Académicos

> **Propuesta Oficial de Proyecto de Aula**  
> **Asignatura:** Sistemas Inteligentes / Inteligencia Artificial  
> **Equipo Investigador:** María Álvarez López, Wadid Rivas Payares, Andrés Acosta Royet, Luis Arraut Turizo  

---

## 💡 Concepto General del Proyecto: ¿Qué es y cómo funciona?

El proyecto consiste en el desarrollo de un **Agente de Inteligencia Artificial Autónomo** que actúa como un bibliotecario universitario virtual. No es un chatbot simple que solo responde texto predefinido, sino un agente capaz de interactuar, indagar las necesidades del estudiante, ejecutar consultas matemáticas en un catálogo de libros y razonar sobre las recomendaciones.

### Capacidades Clave del Agente:
1. **Memoria de Conversación (*Multi-turn Chat*):** El agente recuerda el contexto completo del diálogo. Si el estudiante dice *"Tengo parcial la otra semana y no entiendo nada"*, el agente mantiene una charla guiada preguntando por la materia, el tema específico y el nivel de dificultad deseado.
2. **Uso Autónomo de Herramientas (*Tool Calling / Function Calling*):** La API de Google Gemini tiene el control sobre el catálogo. Cuando el agente recopila los datos del estudiante, ejecuta internamente una función en Python (`consultar_catalogo(tema, materia, nivel)`), la cual procesa la base de datos con algoritmos de Machine Learning (**TF-IDF y Similitud del Coseno**).
3. **Explicabilidad Pedagógica (*Explainable AI*):** El agente no solo entrega una lista fría de títulos; analiza los resultados recuperados y explica de forma personalizada y motivadora **por qué** cada libro recomendado se ajusta exactamente al nivel y dudas del estudiante.

---

### Ejemplo de Interacción Real

```text
Estudiante: Hola, necesito ayuda para estudiar.

Agente Bibliotecario: ¡Hola! Claro que sí, con mucho gusto. Cuéntame, ¿para qué asignatura te estás preparando y qué tema específico necesitas repasar?

Estudiante: Es para Programación 1, no logro entender punteros ni memoria dinámica en C.

Agente Bibliotecario: Los punteros suelen ser un dolor de cabeza al inicio, pero con el libro correcto se entienden fácil. ¿Sientes que necesitas empezar desde cero con ejemplos muy visuales, o buscas ejercicios más avanzados tipo examen?

Estudiante: Desde cero, algo con dibujitos y paso a paso.

[Sistema en segundo plano]: Gemini detecta la necesidad e invoca la función:
consultar_catalogo(materia='Programación', tema='punteros memoria dinámica', nivel='Básico')
El motor TF-IDF + Coseno recupera el libro más afín del catálogo local.

Agente Bibliotecario: Acabo de consultar nuestro catálogo y tengo el libro perfecto para ti:
📖 "Cómo programar en C/C++" (Deitel & Deitel)
👉 ¿Por qué te lo recomiendo?: En el capítulo 7 aborda los punteros utilizando diagramas de memoria gráfica (te dibuja las "cajitas" de memoria RAM), lo que hace que entiendas visualmente cómo apuntan las direcciones sin enredarte con teoría pesada. ¿Te gustaría que te indique qué capítulos específicos leer o prefieres ver otra opción?
```

---

## 🏛️ Propuesta Académica Formal

### 1. Tema
Sistemas conversacionales y recomendación inteligente de recursos bibliográficos basados en Machine Learning (TF-IDF y similitud del coseno) combinados con Modelos de Lenguaje (LLMs) y arquitectura de Agentes para la orientación académica personalizada de estudiantes universitarios.

### 2. Título
**Agente Bibliotecario Inteligente: Sistema Conversacional de Recomendación Explicable de Libros Académicos mediante Machine Learning y Modelos de Lenguaje.**

### 3. El Problema
Los estudiantes universitarios que inician el estudio de asignaturas complejas (como matemáticas, programación o ciencias básicas) enfrentan dificultades para seleccionar la bibliografía adecuada dentro de los extensos catálogos de las bibliotecas universitarias. Con frecuencia, los estudiantes eligen libros cuyo nivel de abstracción o enfoque pedagógico no se corresponde con su nivel real de dominio inicial (por ejemplo, textos excesivamente teóricos frente a libros con enfoque práctico y aplicado).

Los buscadores bibliográficos tradicionales funcionan únicamente por coincidencia exacta de palabras clave, careciendo de la capacidad de comprender el contexto del estudiante, indagar sobre sus dificultades específicas o explicar las razones pedagógicas por las cuales un libro en particular es adecuado para su caso. Esta falta de orientación oportuna incrementa la frustración, prolonga los tiempos de búsqueda y afecta negativamente el rendimiento académico y el aprendizaje autónomo.

**Pregunta de investigación:**  
*¿Cómo puede un agente conversacional inteligente, que integre algoritmos de filtrado por contenido (TF-IDF y similitud del coseno) con las capacidades de razonamiento y diálogo de un Modelo de Lenguaje (LLM), mejorar la pertinencia y la comprensión en la recomendación de libros de texto para estudiantes universitarios?*

### 4. Objetivos

#### Objetivo General:
Desarrollar un agente conversacional inteligente para bibliotecas universitarias que dialogue con los estudiantes, identifique sus necesidades académicas y recomiende libros de estudio pertinentes mediante algoritmos de Machine Learning y la API de Google Gemini, ofreciendo justificaciones pedagógicas del material sugerido.

#### Objetivos Específicos:
1. **Diseñar y estructurar un catálogo bibliográfico piloto** (entre 100 y 300 libros) enfocado en asignaturas universitarias clave, parametrizando metadatos como asignatura, temario, sinopsis, enfoque pedagógico y nivel de dificultad.
2. **Implementar un motor de recomendación basado en contenido** utilizando TF-IDF y similitud del coseno sobre las sinopsis y temarios del catálogo para recuperar los libros con mayor afinidad semántica.
3. **Construir el agente conversacional mediante la API de Google Gemini**, dotándolo de memoria de diálogo (*multi-turn*) y mecanismos de ejecución de funciones (*tool/function calling*) que le permitan consultar de forma autónoma el motor de recomendación y generar explicaciones contextualizadas sobre por qué se sugiere cada libro.
4. **Evaluar el sistema** tanto en la precisión de las recomendaciones generadas (mediante Precision@3 y Precision@5 sobre casos de prueba) como en la experiencia de usuario y satisfacción del estudiante a través de pruebas de interacción real.

### 5. Justificación
Este proyecto es altamente pertinente y viable por las siguientes razones:
* **Innovación aplicada a bajo costo:** Combina el rigor matemático del Machine Learning clásico para la búsqueda interna con la versatilidad de los modelos de lenguaje modernos (LLM) a través de la capa gratuita (*Free Tier*) de Google AI Studio (Gemini).
* **Explicabilidad (*Explainable AI*):** A diferencia de los recomendadores tipo "caja negra" que solo arrojan títulos, este agente explica pedagógicamente al estudiante por qué ese libro resolverá su duda específica.
* **Factibilidad técnica:** Utiliza tecnologías de código abierto maduras y ligeras (Python, Flask o Streamlit, scikit-learn, SQLite/JSON) que se pueden ejecutar y desplegar sin necesidad de infraestructura de cómputo costosa.

### 6. Marco Teórico (Resumen)
Los sistemas de recomendación en educación han evolucionado desde el filtrado colaborativo y el filtrado basado en contenido (*Content-Based Filtering*) hacia arquitecturas híbridas y explicables. Trabajos como el de Mediani (2022) y Yaguana Condoy & Chicaiza Espinosa (2022) demostraron la efectividad de la técnica TF-IDF (Frecuencia de Término – Frecuencia Inversa de Documento) y la similitud del coseno para indexar y relacionar recursos educativos según afinidad temática de manera liviana y transparente.

Recientemente, el surgimiento de los Modelos de Lenguaje Grande (LLMs) ha transformado la interacción humano-computador. En sistemas de recomendación, los LLMs no solo actúan como interfaces conversacionales con memoria de contexto, sino que permiten implementar arquitecturas tipo RAG (*Retrieval-Augmented Generation*) y agentes con *Tool Calling*, donde el modelo de lenguaje consulta herramientas determinísticas de búsqueda y enriquece la respuesta con argumentación en lenguaje natural (Lewis et al., 2020), cerrando la brecha entre la búsqueda de información y el acompañamiento tutorial.

### 7. Metodología
* **Tipo de investigación:** Aplicada y de desarrollo tecnológico (diseño e implementación de prototipo funcional).
* **Fases del proyecto:**
  1. **Fase 1: Curaduría de datos:** Recolección y estandarización del catálogo de libros en formato estructurado (JSON/SQLite/CSV).
  2. **Fase 2: Desarrollo del motor analítico:** Vectorización de textos (TF-IDF) y cálculo de similitud del coseno con Python y scikit-learn.
  3. **Fase 3: Integración del Agente:** Programación del agente conversacional usando la API de Google Gemini con persistencia de historial de chat y enlace a la función de búsqueda de libros (*Tool Calling*).
  4. **Fase 4: Interfaz web y despliegue:** Desarrollo de una interfaz de chat interactiva y moderna (Streamlit o Flask).
  5. **Fase 5: Pruebas y evaluación:** Sesiones de prueba con estudiantes universitarios evaluando pertinencia de la recomendación (Precision@K considerando relevante una calificación $\ge 4/5$) y usabilidad del diálogo.

### 8. Factibilidad de Recursos
* **Software y librerías:** Python 3.10+, scikit-learn, pandas, SDK oficial de Google GenAI (`google-genai`), Flask o Streamlit.
* **Costos:** Financieramente nulos, ya que el consumo de la API de Gemini se realiza bajo el nivel gratuito para desarrollo de Google AI Studio y el hosting puede gestionarse en plataformas como Render o Streamlit Cloud.
* **Talento Humano:** Equipo de estudiantes investigadores con asesoría docente en Machine Learning e Ingeniería de Software.

### 9. Investigadores
* María Álvarez López
* Wadid Rivas Payares
* Andrés Acosta Royet
* Luis Arraut Turizo

### 10. Bibliografía Recomendada
* Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems (NeurIPS)*, 33, 9459-9474.
* Mediani, C. (2022). Interactive hybrid recommendation of pedagogical resources. *Ingénierie des Systèmes d'Information*, 27(5), 695–704. https://doi.org/10.18280/isi.270502
* Niño Rojas, V. (2019). *Metodología de la investigación: diseño, ejecución e informe* (2.ª ed.). Ediciones de la U.
* Yaguana Condoy, J. M. (2022). *Recomendación de secuencias de aprendizaje basadas en Recursos Educativos Abiertos: Implementación de un servicio web semántico* [Tesis de grado, Universidad Técnica Particular de Loja]. Repositorio Institucional UTPL. https://dspace.utpl.edu.ec/handle/123456789/32695
