"""
Aplicacion Web: app.py
Proyecto: Agente Bibliotecario Inteligente
Tecnologia: Streamlit + Google Gemini + Scikit-Learn TF-IDF
Caracteristicas:
  - Chat conversacional con Agente IA (Gemini 3.1)
  - Contenedor de chat con SCROLL INDEPENDIENTE (estilo ChatGPT/Claude Canvas)
  - Panel Lateral Derecho 100% FIJO para lectura y vista previa en vivo
"""

import os
import sys
import io
import re
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# Asegurar codificacion UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import recomendador
from agente import AgenteBibliotecario

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACION DE LA PAGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Biblioteca Inteligente - Agente Universitario",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS VISUALES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Evitar que la pagina principal haga scroll innecesario */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
    .main-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        color: #475569;
        font-size: 0.92rem;
        margin-bottom: 0.8rem;
    }
    .badge-basico { background-color: #DEF7EC; color: #03543F; padding: 2px 7px; border-radius: 5px; font-size: 0.72rem; font-weight: 700; }
    .badge-intermedio { background-color: #E1EFFE; color: #1E429F; padding: 2px 7px; border-radius: 5px; font-size: 0.72rem; font-weight: 700; }
    .badge-avanzado { background-color: #FDE8E8; color: #9B1C1C; padding: 2px 7px; border-radius: 5px; font-size: 0.72rem; font-weight: 700; }
    .score-badge { background-color: #FEF3C7; color: #92400E; padding: 2px 7px; border-radius: 5px; font-size: 0.72rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES: Extraccion de Google Books ID y Links
# ─────────────────────────────────────────────────────────────────────────────
def extraer_info_libro(libro: dict):
    portada = libro.get("portada_url", "")
    match = re.search(r"id=([^&]+)", str(portada))
    book_id = match.group(1) if match else ""
    
    titulo_q = urllib.parse.quote(libro.get("titulo", ""))
    autor_q = urllib.parse.quote(libro.get("autor", ""))
    
    if book_id:
        embed_url = f"https://books.google.com/books?id={book_id}&lpg=PP1&pg=PP1&output=embed"
        direct_url = f"https://books.google.com/books?id={book_id}"
    else:
        embed_url = f"https://www.google.com/search?tbm=bks&q={titulo_q}+{autor_q}"
        direct_url = f"https://www.google.com/search?tbm=bks&q={titulo_q}+{autor_q}"
        
    return book_id, embed_url, direct_url

# ─────────────────────────────────────────────────────────────────────────────
# GESTION DEL ESTADO DE LA SESION
# ─────────────────────────────────────────────────────────────────────────────
if "agente" not in st.session_state:
    try:
        st.session_state.agente = AgenteBibliotecario()
    except Exception as e:
        st.session_state.agente = None
        st.error(f"Error al inicializar el agente: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "¡Hola! 👋 Soy tu Agente Bibliotecario Universitario. ¿En qué asignatura o tema te estás preparando hoy? Cuéntame tu duda o qué tema buscas y te recomendaré los libros exactos de nuestro catálogo.",
            "libros": []
        }
    ]

if "libro_seleccionado" not in st.session_state:
    st.session_state.libro_seleccionado = None

# ─────────────────────────────────────────────────────────────────────────────
# BARRA LATERAL (SIDEBAR): Informacion del Catalogo
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3145/3145765.png", width=70)
    st.title("📚 Biblioteca Virtual")
    st.caption("Introducción a los Sistemas Inteligentes")
    
    st.divider()
    st.subheader("📊 Catálogo Indexado")
    st.metric("Libros Académicos", f"{len(recomendador._df):,}")
    st.metric("Materias / Áreas", f"{recomendador._df['materia'].nunique()}")
    st.metric("Términos TF-IDF", f"{len(recomendador._vectorizer.vocabulary_):,}")
    
    st.divider()
    with st.expander("🔍 Buscador Directo (TF-IDF)", expanded=False):
        q_directa = st.text_input("Tema:", placeholder="ej. punteros en C")
        m_directa = st.selectbox("Materia:", ["Todas"] + sorted(recomendador._df['materia'].unique().tolist()))
        if st.button("Buscar ahora", use_container_width=True):
            mat = "" if m_directa == "Todas" else m_directa
            res = recomendador.consultar_catalogo(tema=q_directa, materia=mat, top_k=3)
            for lib in res:
                st.markdown(f"**{lib['titulo']}** ({lib['score']}%)")
                if st.button(f"📖 Previsualizar", key=f"side_prev_{lib['id']}"):
                    st.session_state.libro_seleccionado = lib
                    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# CABECERA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🤖 Agente Bibliotecario Inteligente</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Recomendador Académico Explicable con Machine Learning (TF-IDF) + Google Gemini IA</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DISTRIBUCION DE PANTALLA: CHAT A LA IZQUIERDA Y PANEL FIJO A LA DERECHA
# ─────────────────────────────────────────────────────────────────────────────
hay_libro = st.session_state.libro_seleccionado is not None

if hay_libro:
    col_chat, col_preview = st.columns([1.22, 1.0], gap="large")
else:
    col_chat = st.container()
    col_preview = None

# ─────────────────────────────────────────────────────────────────────────────
# COLUMNA DEL CHAT (CON SCROLL INTERNO PROPIO)
# ─────────────────────────────────────────────────────────────────────────────
with col_chat:
    # Contenedor con altura fija y scroll propio: la pagina principal NO se mueve
    chat_box = st.container(height=650)
    
    with chat_box:
        for idx_msg, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🎓"):
                st.markdown(msg["content"])
                
                # Mostrar tarjetas si hay libros recomendados
                if msg.get("libros"):
                    st.markdown("##### 📚 Libros recomendados en nuestro catálogo:")
                    for idx_lib, lib in enumerate(msg["libros"]):
                        portada = lib.get("portada_url", "")
                        if not portada or "http" not in portada:
                            portada = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=120&q=80"
                        
                        nivel = str(lib.get("nivel", "Intermedio")).capitalize()
                        clase_badge = f"badge-{nivel.lower()}"
                        score = lib.get("score", 0.0)
                        
                        card_c1, card_c2 = st.columns([0.22, 0.78])
                        with card_c1:
                            st.image(portada, use_container_width=True)
                        with card_c2:
                            st.markdown(f"**{lib['titulo']}**")
                            st.caption(f"✍️ {lib['autor']}")
                            st.markdown(f"""
                            <span class="{clase_badge}">{nivel}</span> &nbsp;
                            <span style="font-size: 0.75rem; color: #475569;">📁 {lib['materia']}</span> &nbsp;
                            <span class="score-badge">🎯 Afinidad: {score}%</span>
                            """, unsafe_allow_html=True)
                            st.markdown(f"<div style='font-size:0.8rem; color:#475569; margin-top:3px;'>{lib['descripcion'][:140]}...</div>", unsafe_allow_html=True)
                            
                            btn_key = f"btn_leer_{idx_msg}_{idx_lib}_{lib['id']}"
                            if st.button("📖 Abrir vista previa y lectura", key=btn_key, type="primary"):
                                st.session_state.libro_seleccionado = lib
                                st.rerun()
                        st.divider()

    # Entrada de texto del chat (anclada debajo del contenedor de chat)
    if prompt := st.chat_input("Escribe tu duda aquí (ej. 'Recomiéndame libros para circuitos eléctricos')..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "libros": []})
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PROCESAMIENTO DEL MENSAJE DEL USUARIO
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    ultimo_prompt = st.session_state.messages[-1]["content"]
    
    with col_chat:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("El Agente Bibliotecario está consultando el catálogo y analizando la mejor recomendación..."):
                try:
                    if st.session_state.agente:
                        respuesta, libros = st.session_state.agente.enviar_mensaje(ultimo_prompt)
                    else:
                        libros = recomendador.consultar_catalogo(tema=ultimo_prompt, top_k=3)
                        respuesta = "He consultado nuestro catálogo con el algoritmo TF-IDF. Aquí tienes los libros más pertinentes:"
                    
                    if not libros and any(k in ultimo_prompt.lower() for k in ["libro", "recomiend", "aprender", "estudiar", "circuito", "puntero", "calculo", "c", "java", "python", "base de datos"]):
                        libros = recomendador.consultar_catalogo(tema=ultimo_prompt, top_k=3)
                    
                    if libros:
                        st.session_state.libro_seleccionado = libros[0]
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": respuesta,
                        "libros": libros
                    })
                    st.rerun()
                    
                except Exception as e:
                    libros = recomendador.consultar_catalogo(tema=ultimo_prompt, top_k=3)
                    fallback_resp = "He consultado directamente nuestro catálogo de la biblioteca universitaria con **TF-IDF y Similitud del Coseno**. Aquí tienes las recomendaciones:"
                    if libros:
                        st.session_state.libro_seleccionado = libros[0]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": fallback_resp,
                        "libros": libros
                    })
                    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# COLUMNA DERECHA: PANEL FIJO DE LECTURA Y VISTA PREVIA (CANVAS / SIDECAR)
# ─────────────────────────────────────────────────────────────────────────────
if hay_libro and col_preview:
    libro_sel = st.session_state.libro_seleccionado
    book_id, embed_url, direct_url = extraer_info_libro(libro_sel)
    
    with col_preview:
        preview_box = st.container(height=650)
        
        with preview_box:
            # Encabezado del lector
            head_c1, head_c2 = st.columns([0.75, 0.25])
            with head_c1:
                st.markdown("### 📖 Lector y Vista Previa")
            with head_c2:
                if st.button("✖ Cerrar", key="btn_cerrar_preview", help="Cerrar panel"):
                    st.session_state.libro_seleccionado = None
                    st.rerun()
            
            # Ficha del libro seleccionado
            st.markdown(f"#### **{libro_sel['titulo']}**")
            st.caption(f"👤 Autor(es): **{libro_sel['autor']}** | 📁 Materia: **{libro_sel['materia']}**")
            
            # Boton directo externo
            st.link_button("🔗 Abrir libro en Google Books", direct_url, use_container_width=True)
            
            # Pestañas de Vista Previa y Sinopsis
            tab_lector, tab_sinopsis = st.tabs(["📄 Vista Previa en Vivo", "📝 Sinopsis y Temas"])
            
            with tab_lector:
                st.info("💡 A continuación se carga el lector oficial de Google Books:")
                components.iframe(embed_url, height=450, scrolling=True)
                st.caption(f"ID del catálogo: `{book_id if book_id else 'Búsqueda directa'}`")
                
            with tab_sinopsis:
                st.markdown("**Descripción temática y resumen curricular:**")
                st.write(libro_sel.get("descripcion", "Sin sinopsis disponible."))
                st.metric("Afinidad calculada por TF-IDF", f"{libro_sel.get('score', 0.0)}%")
                
                if st.button("🤖 Pedirle al Agente que me resuma este libro", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"Por favor explícame en detalle qué temas trata el libro '{libro_sel['titulo']}' de {libro_sel['autor']} y cómo me ayudará a estudiar.",
                        "libros": []
                    })
                    st.rerun()
