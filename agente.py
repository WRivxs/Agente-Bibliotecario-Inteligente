"""
Modulo: agente.py
Proyecto: Agente Bibliotecario Inteligente
Descripcion: Implementa el Agente Autonomo utilizando la API oficial
             de Google Gemini (google-genai) con soporte nativo de
             Tool Calling (Function Calling) y memoria conversacional.
"""

import os
import sys
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types
import recomendador

# Asegurar codificacion UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Cargar variables de entorno
_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_ROOT, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY", "")

# Soporte para despliegue en Streamlit Community Cloud (st.secrets)
try:
    import streamlit as st
    if not API_KEY and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Variable para almacenar los ultimos libros encontrados por la herramienta
# para que la interfaz web (app.py) pueda renderizar las tarjetas visuales
ultimos_libros_encontrados = []

# ─────────────────────────────────────────────────────────────────────────────
# DEFINICION DE LA HERRAMIENTA (TOOL) PARA GEMINI
# ─────────────────────────────────────────────────────────────────────────────

def buscar_libros(tema: str, materia: str = "", nivel: str = "") -> str:
    """
    Consulta el catalogo de la biblioteca universitaria para encontrar los mejores libros.
    
    Args:
        tema: Descripcion del tema o concepto con terminos tecnicos (preferiblemente en ingles o bilingue para maxima precision del catalogo, ej: 'pointers in C dynamic memory', 'calculus derivatives', 'neural networks deep learning').
        materia: Asignatura o area (ej: 'C y C++', 'Programacion General', 'Calculo Diferencial', 'Calculo Integral', 'Inteligencia Artificial', 'Bases de Datos Relacionales', 'Fisica General', etc.).
        nivel: Nivel educativo requerido ('Basico', 'Intermedio', 'Avanzado').
    """
    global ultimos_libros_encontrados
    libros = recomendador.consultar_catalogo(tema=tema, materia=materia, nivel=nivel, top_k=3)
    ultimos_libros_encontrados = libros
    
    if not libros:
        return "No se encontraron libros especificos para esa consulta."
    
    resultado = "LIBROS ENCONTRADOS EN NUESTRO CATALOGO (MENCIONA ESTOS LIBROS EXACTOS EN TU RESPUESTA):\n"
    for i, lib in enumerate(libros, 1):
        resultado += (
            f"\n{i}. Titulo: {lib['titulo']}\n"
            f"   Autor(es): {lib['autor']}\n"
            f"   Materia: {lib['materia']} | Nivel: {lib['nivel']}\n"
            f"   Afinidad calculada por TF-IDF: {lib['score']}%\n"
            f"   Sinopsis: {lib['descripcion']}\n"
        )
    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT DEL SISTEMA: Personalidad y Reglas del Agente Bibliotecario
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_INSTRUCTION = """
Eres el Agente Bibliotecario Inteligente oficial de la Universidad. Tu mision es orientar academicamente a los estudiantes y recomendarles los libros exactos de nuestra biblioteca.

REGLAS OBLIGATORIAS:
1. Sé cálido, pedagógico y motivador, como un excelente tutor universitario.
2. Si el estudiante te hace una consulta sobre una materia o tema, SIEMPRE utiliza tu herramienta `buscar_libros` para consultar el catálogo.
   - IMPORTANTE: En el parámetro `tema` de la herramienta `buscar_libros`, usa palabras clave técnicas precisas (ej. si piden 'punteros en C', busca 'pointers in C dynamic memory'; si piden 'derivadas', busca 'calculus derivatives limits').
3. CUANDO LA HERRAMIENTA TE DEVUELVA LIBROS DEL CATÁLOGO:
   - DEBES presentar y recomendar ESOS libros específicos encontrados en el catálogo.
   - Menciona el Título exacto y el Autor(es).
   - Explica de forma clara y pedagógica POR QUÉ ese libro le servirá para su necesidad y nivel.
   - Da un consejo de estudio o analogía sencilla para el tema que está aprendiendo.
4. Responde siempre en español con excelente formato markdown (negritas, viñetas).
"""

# ─────────────────────────────────────────────────────────────────────────────
# GESTOR DEL AGENTE (CLASE)
# ─────────────────────────────────────────────────────────────────────────────

class AgenteBibliotecario:
    def __init__(self):
        if not API_KEY:
            raise ValueError("No se encontro GEMINI_API_KEY en el archivo .env")
        
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = "gemini-3.1-flash-lite"
        
        # Inicializar sesion de chat con memoria y herramientas
        self.chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.6,
                tools=[buscar_libros],
            )
        )

    def enviar_mensaje(self, mensaje_usuario: str) -> tuple[str, list[dict]]:
        """
        Envia un mensaje al agente.
        Retorna una tupla: (texto_respuesta, lista_de_libros_recomendados)
        """
        global ultimos_libros_encontrados
        ultimos_libros_encontrados = []  # reset antes de la consulta
        
        response = self.chat.send_message(mensaje_usuario)
        libros = list(ultimos_libros_encontrados)
        return response.text, libros
