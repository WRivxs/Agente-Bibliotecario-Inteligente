"""
Script: generar_dataset.py  (v2 - Google Books API + 50 categorias)
Proyecto: Agente Bibliotecario Inteligente
Descripcion: Descarga ~2.000 libros academicos universitarios usando la
             API de Google Books con API Key. 50 categorias x 40 libros.
             Lee la key desde el archivo .env del proyecto.

Uso:
    python scripts/generar_dataset.py
"""

import sys
import os
import time
import re
import requests
import pandas as pd
from dotenv import load_dotenv

# Cargar .env desde la raiz del proyecto
_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
load_dotenv(os.path.join(_ROOT, ".env"))

API_KEY          = os.getenv("GEMINI_API_KEY", "")   # reutilizamos la key de Google
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
MAX_POR_PETICION = 40
PAUSA_SEGUNDOS   = 1.2    # con API key el limite es mucho mayor
ARCHIVO_SALIDA   = os.path.join(_ROOT, "data", "catalogo_libros.csv")
META_POR_CAT     = 55     # 53 categorias x 55 = 2915 brutos -> ~2000+ unicos tras dedup

# ─────────────────────────────────────────────────────────────────────────────
# 50 CATEGORIAS ACADEMICAS
# ─────────────────────────────────────────────────────────────────────────────
CATEGORIAS = [
    # ── PROGRAMACION ─────────────────────────────────────────────────────────
    ("programming fundamentals algorithms beginner",          "Programacion General",          "Basico"),
    ("python programming data science beginner",              "Python",                        "Basico"),
    ("java programming object oriented university",           "Java",                          "Intermedio"),
    ("C programming language pointers memory",                "C y C++",                       "Intermedio"),
    ("javascript web programming frontend",                   "JavaScript",                    "Basico"),
    ("kotlin android swift ios mobile programming",           "Programacion Movil",            "Intermedio"),
    ("software engineering design patterns architecture",     "Ingenieria de Software",        "Avanzado"),
    ("web development HTML CSS frameworks",                   "Desarrollo Web",                "Basico"),
    ("git version control devops CI CD",                      "DevOps y Control de Versiones", "Intermedio"),
    ("compilers interpreters programming languages theory",   "Compiladores",                  "Avanzado"),

    # ── ESTRUCTURAS Y ALGORITMOS ─────────────────────────────────────────────
    ("data structures arrays linked lists stacks queues",     "Estructuras de Datos",          "Intermedio"),
    ("algorithms sorting searching complexity Big-O",         "Algoritmos",                    "Intermedio"),
    ("competitive programming problem solving",               "Programacion Competitiva",      "Avanzado"),
    ("graph theory algorithms networks",                      "Teoria de Grafos",              "Avanzado"),
    ("dynamic programming recursion backtracking",            "Programacion Dinamica",         "Avanzado"),

    # ── MATEMATICAS ───────────────────────────────────────────────────────────
    ("differential calculus limits derivatives university",   "Calculo Diferencial",           "Basico"),
    ("integral calculus techniques integration university",   "Calculo Integral",              "Basico"),
    ("multivariable calculus vector calculus partial",        "Calculo Multivariable",         "Intermedio"),
    ("linear algebra matrices vectors eigenvalues",           "Algebra Lineal",                "Intermedio"),
    ("discrete mathematics logic sets combinatorics",         "Matematicas Discretas",         "Intermedio"),
    ("probability theory random variables distributions",     "Probabilidad",                  "Intermedio"),
    ("statistics hypothesis testing regression university",   "Estadistica",                   "Basico"),
    ("numerical methods numerical analysis engineering",      "Metodos Numericos",             "Avanzado"),
    ("differential equations ODE PDE university",            "Ecuaciones Diferenciales",      "Intermedio"),
    ("abstract algebra group theory number theory",           "Algebra Abstracta",             "Avanzado"),

    # ── BASES DE DATOS ────────────────────────────────────────────────────────
    ("database systems SQL relational model university",      "Bases de Datos Relacionales",   "Intermedio"),
    ("NoSQL MongoDB Cassandra document database",             "Bases de Datos NoSQL",          "Intermedio"),
    ("data warehouse business intelligence ETL",              "Data Warehouse y BI",           "Avanzado"),
    ("database administration performance tuning",            "Administracion de BD",          "Avanzado"),

    # ── REDES Y SISTEMAS ─────────────────────────────────────────────────────
    ("computer networks protocols TCP IP university",         "Redes de Computadoras",         "Intermedio"),
    ("operating systems processes memory management",         "Sistemas Operativos",           "Intermedio"),
    ("cybersecurity network security cryptography",           "Ciberseguridad",                "Avanzado"),
    ("cloud computing AWS Azure distributed systems",         "Cloud Computing",               "Avanzado"),
    ("Linux administration shell scripting",                  "Administracion Linux",          "Intermedio"),
    ("embedded systems microcontrollers IoT programming",     "Sistemas Embebidos",            "Avanzado"),

    # ── INTELIGENCIA ARTIFICIAL ───────────────────────────────────────────────
    ("artificial intelligence agents planning university",    "Inteligencia Artificial",       "Avanzado"),
    ("machine learning supervised unsupervised scikit",      "Machine Learning",              "Intermedio"),
    ("deep learning neural networks TensorFlow PyTorch",     "Deep Learning",                 "Avanzado"),
    ("natural language processing NLP text mining",           "Procesamiento de Lenguaje",     "Avanzado"),
    ("computer vision image recognition CNN",                 "Vision por Computador",         "Avanzado"),
    ("reinforcement learning reward agent policy",            "Aprendizaje por Refuerzo",      "Avanzado"),
    ("data science pandas numpy visualization",               "Ciencia de Datos",              "Intermedio"),
    ("robotics autonomous systems sensors actuators",         "Robotica",                      "Avanzado"),

    # ── FISICA Y CIENCIAS ─────────────────────────────────────────────────────
    ("university physics mechanics kinematics dynamics",      "Fisica General",                "Basico"),
    ("electromagnetism Maxwell equations university",         "Electromagnetismo",             "Intermedio"),
    ("thermodynamics heat engines entropy university",        "Termodinamica",                 "Basico"),
    ("quantum mechanics Schrodinger wave function",           "Fisica Cuantica",               "Avanzado"),
    ("chemistry general university atoms molecules",          "Quimica General",               "Basico"),

    # ── OTRAS AREAS UNIVERSITARIAS ────────────────────────────────────────────
    ("economics microeconomics macroeconomics university",    "Economia",                      "Basico"),
    ("accounting financial statements university",            "Contabilidad",                  "Basico"),
    ("signals systems Fourier Laplace transform",             "Senales y Sistemas",            "Avanzado"),
    ("control systems feedback PID engineering",              "Control Automatico",            "Avanzado"),
    ("electronics circuits transistors operational amplifier","Electronica",                   "Intermedio"),
]


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────

def limpiar(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def asignar_nivel(titulo: str, desc: str, nivel_default: str) -> str:
    t = (titulo + " " + desc).lower()
    if any(w in t for w in ["introduction", "beginner", "basic", "introduccion",
                             "fundamentals", "primer", "101", "starting", "easy",
                             "getting started", "step by step"]):
        return "Basico"
    if any(w in t for w in ["advanced", "avanzado", "expert", "professional",
                             "mastery", "graduate", "research", "in depth"]):
        return "Avanzado"
    return nivel_default


def buscar_en_api(query: str, materia: str, nivel_default: str, meta: int) -> list[dict]:
    libros = []
    start  = 0
    vacios = 0

    while len(libros) < meta and vacios < 4:
        params = {
            "q":          query,
            "startIndex": start,
            "maxResults": MAX_POR_PETICION,
            "printType":  "books",
            "orderBy":    "relevance",
            "key":        API_KEY,
        }
        try:
            r = requests.get(GOOGLE_BOOKS_URL, params=params, timeout=15)
            r.raise_for_status()
            items = r.json().get("items", [])
        except Exception as e:
            print(f"  [!] Error ({materia} start={start}): {e}")
            time.sleep(3)
            vacios += 1
            continue

        if not items:
            vacios += 1
            start  += MAX_POR_PETICION
            time.sleep(PAUSA_SEGUNDOS)
            continue

        nuevos = 0
        for item in items:
            info = item.get("volumeInfo", {})
            desc = limpiar(info.get("description", ""))
            if len(desc) < 60:
                continue

            titulo = limpiar(info.get("title", "Sin titulo"))
            autores = info.get("authors", ["Desconocido"])
            autor   = ", ".join(autores[:3])
            portada = (info.get("imageLinks", {})
                           .get("thumbnail", "")
                           .replace("http://", "https://"))
            nivel   = asignar_nivel(titulo, desc, nivel_default)

            libros.append({
                "titulo":      titulo,
                "autor":       autor,
                "materia":     materia,
                "nivel":       nivel,
                "descripcion": desc,
                "portada_url": portada,
            })
            nuevos += 1
            if len(libros) >= meta:
                break

        vacios  = 0 if nuevos > 0 else vacios + 1
        start  += MAX_POR_PETICION
        time.sleep(PAUSA_SEGUNDOS)

    return libros[:meta]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print(f"[INFO] API Key: {'OK (' + API_KEY[:8] + '...)' if API_KEY else 'NO ENCONTRADA'}")
    print(f"[INFO] Categorias: {len(CATEGORIAS)}  |  Meta por categoria: {META_POR_CAT}")
    print(f"[INFO] Objetivo total: {len(CATEGORIAS) * META_POR_CAT} libros\n")

    todos = []

    for i, (query, materia, nivel_default) in enumerate(CATEGORIAS, 1):
        print(f"[{i:02d}/{len(CATEGORIAS)}] Buscando: {materia} ...", end=" ", flush=True)
        libros = buscar_en_api(query, materia, nivel_default, META_POR_CAT)
        todos.extend(libros)
        print(f"{len(libros)} libros obtenidos  (total acumulado: {len(todos)})")

    # ── DataFrame y limpieza ──────────────────────────────────────────────────
    df = pd.DataFrame(todos)
    antes = len(df)
    df = df.drop_duplicates(subset=["titulo"])
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    print(f"\n[INFO] Duplicados eliminados: {antes - len(df)}")

    # ── Guardar ───────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(ARCHIVO_SALIDA), exist_ok=True)
    df.to_csv(ARCHIVO_SALIDA, index=False, encoding="utf-8-sig")

    # ── Reporte final ─────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("[EXITO] Dataset generado")
    print(f"[ARCHIVO] {ARCHIVO_SALIDA}")
    print(f"[TOTAL] {len(df)} libros unicos")
    print("-" * 65)
    print("Distribucion por materia:")
    for mat, cnt in df.groupby("materia")["id"].count().items():
        print(f"  {mat:<40} {cnt:>4} libros")
    print("-" * 65)
    print("Distribucion por nivel:")
    for niv, cnt in df.groupby("nivel")["id"].count().items():
        print(f"  {niv:<40} {cnt:>4} libros")
    print("=" * 65)


if __name__ == "__main__":
    main()
