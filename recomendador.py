"""
Modulo: recomendador.py
Proyecto: Agente Bibliotecario Inteligente
Descripcion: Motor de recomendacion de libros usando TF-IDF y
             Similitud del Coseno. Es el "cerebro matematico" del
             sistema que el Agente Gemini llama como herramienta.

Como funciona:
  1. Carga el catalogo de libros desde data/catalogo_libros.csv
  2. Vectoriza las descripciones con TF-IDF (una sola vez al arrancar)
  3. Cuando el agente llama a consultar_catalogo():
     - Filtra por materia y nivel (filtro duro de metadatos)
     - Calcula la similitud del coseno entre la consulta y los libros filtrados
     - Retorna los top-K libros mas relevantes como lista de diccionarios
"""

import os
import sys
import io
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Asegurar codificacion UTF-8 para consola de Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ─────────────────────────────────────────────────────────────────────────────
# CARGA Y VECTORIZACION DEL CATALOGO (se ejecuta una sola vez al importar)
# ─────────────────────────────────────────────────────────────────────────────

_BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
_CSV_PATH    = os.path.join(_BASE_DIR, "data", "catalogo_libros.csv")

# Cargar catalogo
_df = pd.read_csv(_CSV_PATH, encoding="utf-8-sig")

# Columna de texto unificada para TF-IDF:
# Combinamos titulo + materia + nivel + descripcion para mayor precision semantica
_df["_texto_tfidf"] = (
    _df["titulo"].fillna("") + " " +
    _df["materia"].fillna("") + " " +
    _df["nivel"].fillna("") + " " +
    _df["descripcion"].fillna("")
)

# Diccionario basico de traduccion/expansion para consultas en espanol
_TERMINOS_ES_EN = {
    "puntero": "pointer", "punteros": "pointers", "memoria dinamica": "dynamic memory",
    "arreglos": "arrays", "vectores": "vectors", "matrices": "matrices",
    "derivada": "derivative", "derivadas": "derivatives", "integral": "integral",
    "integrales": "integrals", "calculo": "calculus", "limites": "limits",
    "redes neuronales": "neural networks", "aprendizaje": "learning",
    "bases de datos": "databases", "arboles": "trees", "grafos": "graphs",
    "pilas": "stacks", "colas": "queues", "listas enlazadas": "linked lists",
    "algoritmos": "algorithms", "ordenamiento": "sorting", "busqueda": "searching"
}

def _expandir_consulta(texto: str) -> str:
    """Expande terminos comunes en espanol con sus equivalentes tecnicos en ingles."""
    texto_exp = texto.lower()
    for es, en in _TERMINOS_ES_EN.items():
        if es in texto_exp:
            texto_exp += f" {en}"
    return texto_exp

# Vectorizador TF-IDF global (entrenado sobre todo el catalogo)
# token_pattern permite capturar 'c', 'c++', 'c#', etc.
_vectorizer = TfidfVectorizer(
    token_pattern=r"(?u)\b[a-zA-Z0-9_+#]{1,}\b",
    stop_words="english",
    ngram_range=(1, 2),
    max_features=25000,
    sublinear_tf=True,
)
_matriz_tfidf = _vectorizer.fit_transform(_df["_texto_tfidf"])

print(f"[Recomendador] Catalogo cargado: {len(_df)} libros | "
      f"Vocabulario TF-IDF: {len(_vectorizer.vocabulary_)} terminos")


# ─────────────────────────────────────────────────────────────────────────────
# FUNCION PRINCIPAL: consultar_catalogo()
# Esta es la herramienta (Tool) que el Agente Gemini va a invocar
# ─────────────────────────────────────────────────────────────────────────────

def consultar_catalogo(
    tema: str,
    materia: str = "",
    nivel: str = "",
    top_k: int = 3
) -> list[dict]:
    """
    Busca los libros mas relevantes del catalogo para una consulta dada.

    Parametros:
        tema    : Descripcion de lo que necesita el estudiante.
                  Ej: "punteros y memoria dinamica en C con ejemplos graficos"
        materia : (Opcional) Filtro de asignatura.
                  Valores validos: "Programacion", "Matematicas",
                  "Estructuras de Datos", "Bases de Datos",
                  "Algebra y Estadistica", "Redes y Sistemas Operativos",
                  "Inteligencia Artificial", "Fisica"
        nivel   : (Opcional) Filtro de dificultad.
                  Valores validos: "Basico", "Intermedio", "Avanzado"
        top_k   : Numero de libros a retornar (por defecto 3)

    Retorna:
        Lista de diccionarios con los campos:
        id, titulo, autor, materia, nivel, descripcion, portada_url, score
        Ordenados de mayor a menor similitud.
    """

    # ── Paso 1: Filtro duro por metadatos ─────────────────────────────────────
    df_filtrado = _df.copy()

    if materia.strip():
        # Busqueda flexible: si la materia del catalogo CONTIENE el termino buscado
        mask = df_filtrado["materia"].str.contains(materia.strip(), case=False, na=False)
        if mask.any():
            df_filtrado = df_filtrado[mask]

    if nivel.strip():
        mask_nivel = df_filtrado["nivel"].str.contains(nivel.strip(), case=False, na=False)
        if mask_nivel.any():
            df_filtrado = df_filtrado[mask_nivel]

    # Si no queda nada despues del filtro, buscar en todo el catalogo
    if df_filtrado.empty:
        df_filtrado = _df.copy()

    # ── Paso 2: Vectorizar la consulta del estudiante ─────────────────────────
    tema_expandido = _expandir_consulta(tema)
    vector_consulta = _vectorizer.transform([tema_expandido])

    # ── Paso 3: Calcular Similitud del Coseno ─────────────────────────────────
    indices_filtrados = df_filtrado.index.tolist()
    matriz_filtrada   = _matriz_tfidf[indices_filtrados]

    similitudes = cosine_similarity(vector_consulta, matriz_filtrada).flatten()

    # Si la similitud maxima en el filtro es muy baja (< 0.05), buscar en todo el catalogo como respaldo
    if len(similitudes) == 0 or similitudes.max() < 0.05:
        indices_filtrados = _df.index.tolist()
        similitudes = cosine_similarity(vector_consulta, _matriz_tfidf).flatten()

    # ── Paso 4: Ordenar y seleccionar top-K ───────────────────────────────────
    top_indices_locales = similitudes.argsort()[::-1][:top_k]
    top_indices_globales = [indices_filtrados[i] for i in top_indices_locales]

    # ── Paso 5: Construir resultado ───────────────────────────────────────────
    resultados = []
    for idx_global, idx_local in zip(top_indices_globales, top_indices_locales):
        fila  = _df.loc[idx_global]
        score = round(float(similitudes[idx_local]) * 100, 2)  # porcentaje 0-100
        resultados.append({
            "id":          int(fila["id"]),
            "titulo":      str(fila["titulo"]),
            "autor":       str(fila["autor"]),
            "materia":     str(fila["materia"]),
            "nivel":       str(fila["nivel"]),
            "descripcion": str(fila["descripcion"]),
            "portada_url": str(fila["portada_url"]),
            "score":       score,
        })

    return resultados


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA RAPIDA (ejecutar directamente: python recomendador.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("PRUEBA DEL MOTOR DE RECOMENDACION TF-IDF + COSENO")
    print("=" * 65)

    casos_prueba = [
        {
            "descripcion": "Caso 1: Punteros en C para principiante",
            "tema":    "punteros memoria dinamica arreglos en C paso a paso",
            "materia": "Programacion",
            "nivel":   "Basico",
        },
        {
            "descripcion": "Caso 2: Redes neuronales avanzado",
            "tema":    "deep learning redes neuronales convolucionales clasificacion imagenes",
            "materia": "Inteligencia Artificial",
            "nivel":   "Avanzado",
        },
        {
            "descripcion": "Caso 3: SQL sin especificar nivel",
            "tema":    "consultas SQL joins tablas relacionales bases de datos",
            "materia": "Bases de Datos",
            "nivel":   "",
        },
        {
            "descripcion": "Caso 4: Calculo integral intermedio",
            "tema":    "integrales definidas tecnicas de integracion calculo",
            "materia": "Matematicas",
            "nivel":   "Intermedio",
        },
    ]

    for caso in casos_prueba:
        print(f"\n--- {caso['descripcion']} ---")
        print(f"    Tema: '{caso['tema']}'")
        print(f"    Filtros: materia='{caso['materia']}' | nivel='{caso['nivel']}'")
        print("    Recomendaciones:")
        resultados = consultar_catalogo(
            tema    = caso["tema"],
            materia = caso["materia"],
            nivel   = caso["nivel"],
            top_k   = 3
        )
        for i, libro in enumerate(resultados, 1):
            print(f"      {i}. [{libro['score']}%] {libro['titulo']} — {libro['autor']}")
            print(f"         Nivel: {libro['nivel']} | Materia: {libro['materia']}")

    print("\n" + "=" * 65)
    print("Motor funcionando correctamente.")
    print("=" * 65)
