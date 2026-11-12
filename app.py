"""
Aplicacion Web: app.py
Proyecto: Agente Bibliotecario Inteligente
Tecnologia: Streamlit + Google Gemini + Scikit-Learn TF-IDF
Diseno: Interfaz Abierta y Limpia estilo ChatGPT & Google Gemini (Mobile-First y Responsive)
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
# ESTILOS VISUALES (ESTILO CHATGPT / GEMINI - ABIERTO, SIN CAJAS)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Margen superior amplio para que el titulo NUNCA se corte */
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 6.5rem !important;
        max-width: 1300px !important;
    }
    
    /* Tipografia limpia estilo Google Gemini / ChatGPT */
    .gemini-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .gemini-subtitle {
        color: #6B7280;
        font-size: 0.96rem;
        margin-bottom: 1.8rem;
    }

    /* Fondo limpio de los mensajes: sin marcos ni recuadros grises */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding-top: 0.8rem !important;
        padding-bottom: 0.8rem !important;
    }
    
    /* Barra de entrada flotante fija en la parte inferior (estilo ChatGPT/Gemini) */
    [data-testid="stChatInput"] {
        border-radius: 28px !important;
        border: 1px solid #D1D5DB !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08) !important;
        padding: 4px 8px !important;
    }
    [data-testid="stChatInput"] textarea {
        font-size: 0.95rem !important;
    }

    /* Tarjetas de libros limpias (estilo cards de Gemini) */
    .gemini-book-card {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 12px 14px;
        margin-top: 8px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .gemini-book-thumb {
        width: 72px;
        min-width: 72px;
        height: 105px;
        object-fit: cover;
        border-radius: 6px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .gemini-book-content {
        flex: 1;
        min-width: 0;
    }
    .badge-basico { background-color: #ECFDF5; color: #065F46; padding: 2px 7px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }
    .badge-intermedio { background-color: #EFF6FF; color: #1E40AF; padding: 2px 7px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }
    .badge-avanzado { background-color: #FEF2F2; color: #991B1B; padding: 2px 7px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }
    .badge-score { background-color: #FFFBEB; color: #92400E; padding: 2px 7px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; }

    /* Panel lateral fijo y limpio para la vista previa */
    .preview-sidecar {
        position: -webkit-sticky;
        position: sticky;
        top: 4.5rem;
        max-height: calc(100vh - 6.5rem);
        overflow-y: auto;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }

    /* Reglas para Celular / Pantallas < 900px */
    @media (max-width: 900px) {
        .block-container {
            padding-top: 4rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        .gemini-title {
            font-size: 1.55rem !important;
        }
        .gemini-subtitle {
            font-size: 0.88rem !important;
        }
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        .gemini-book-thumb {
            width: 60px !important;
            min-width: 60px !important;
            height: 90px !important;
        }
        .preview-sidecar {
            position: relative !important;
            top: 0 !important;
            max-height: none !important;
            margin-top: 1.5rem !important;
        }
    }
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
# CABECERA PRINCIPAL (CON AMPLIO ESPACIO SUPERIOR)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="gemini-title">🤖 Agente Bibliotecario Inteligente</div>', unsafe_allow_html=True)
st.markdown('<div class="gemini-subtitle">Recomendador Académico Explicable con Machine Learning (TF-IDF) + Google Gemini IA</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DISTRIBUCION DE PANTALLA: CHAT ABIERTO Y PANEL DERECHO OPCIONAL
# ─────────────────────────────────────────────────────────────────────────────
hay_libro = st.session_state.libro_seleccionado is not None

if hay_libro:
    col_chat, col_preview = st.columns([1.25, 1.0], gap="large")
else:
    col_chat = st.container()
    col_preview = None

# ─────────────────────────────────────────────────────────────────────────────
# CHAT ABIERTO Y NATURAL (SIN CAJAS NI RECUADROS GRISES)
# ─────────────────────────────────────────────────────────────────────────────
with col_chat:
    for idx_msg, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🎓"):
            st.markdown(msg["content"])
            
            # Mostrar tarjetas limpias si el mensaje contiene libros recomendados
            if msg.get("libros"):
                st.markdown("##### 📚 Libros sugeridos de nuestro catálogo:")
                for idx_lib, lib in enumerate(msg["libros"]):
                    portada = lib.get("portada_url", "")
                    if not portada or "http" not in portada:
                        portada = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=120&q=80"
                    
                    nivel = str(lib.get("nivel", "Intermedio")).capitalize()
                    clase_badge = f"badge-{nivel.lower()}"
                    score = lib.get("score", 0.0)
                    
                    st.markdown(f"""
                    <div class="gemini-book-card">
                        <img src="{portada}" class="gemini-book-thumb" onerror="this.src='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=120&q=80'" />
                        <div class="gemini-book-content">
                            <div style="font-weight:700; color:#111827; font-size:0.97rem; margin-bottom:2px;">📖 {lib['titulo']}</div>
                            <div style="font-size:0.82rem; color:#4B5563; margin-bottom:5px;">✍️ {lib['autor']}</div>
                            <div style="margin-bottom:6px;">
                                <span class="{clase_badge}">{nivel}</span> &nbsp;
                                <span style="font-size:0.75rem; color:#4B5563;">📁 {lib['materia']}</span> &nbsp;
                                <span class="badge-score">🎯 Afinidad: {score}%</span>
                            </div>
                            <div style="font-size:0.8rem; color:#374151; line-height:1.35;">{lib['descripcion'][:150]}...</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_key = f"btn_leer_{idx_msg}_{idx_lib}_{lib['id']}"
                    if st.button(f"📖 Abrir lectura: {lib['titulo'][:32]}...", key=btn_key, type="primary", use_container_width=True):
                        st.session_state.libro_seleccionado = lib
                        st.rerun()
                    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL LATERAL DE LECTURA (CANVAS / SIDECAR)
# ─────────────────────────────────────────────────────────────────────────────
if hay_libro and col_preview:
    libro_sel = st.session_state.libro_seleccionado
    book_id, embed_url, direct_url = extraer_info_libro(libro_sel)
    
    with col_preview:
        st.markdown('<div class="preview-sidecar">', unsafe_allow_html=True)
        
        # Encabezado del lector
        head_c1, head_c2 = st.columns([0.78, 0.22])
        with head_c1:
            st.markdown("### 📖 Lector y Vista Previa")
        with head_c2:
            if st.button("✖ Cerrar", key="btn_cerrar_preview", help="Cerrar panel de lectura"):
                st.session_state.libro_seleccionado = None
                st.rerun()
        
        # Ficha del libro seleccionado
        st.markdown(f"#### **{libro_sel['titulo']}**")
        st.caption(f"👤 Autor(es): **{libro_sel['autor']}** | 📁 Materia: **{libro_sel['materia']}**")
        
        # Boton directo externo
        st.link_button("🔗 Abrir ficha en Google Books", direct_url, use_container_width=True)
        
        # Pestañas de Vista Previa y Sinopsis
        tab_lector, tab_sinopsis = st.tabs(["📄 Vista Previa en Vivo", "📝 Sinopsis y Temas"])
        
        with tab_lector:
            st.info("💡 Lector oficial de Google Books para navegar capítulos de muestra:")
            components.iframe(embed_url, height=480, scrolling=True)
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
                
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRADA DE TEXTO FLOTANTE FIJA AL FONDO (ESTILO CHATGPT / GEMINI)
# ─────────────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Escribe tu duda aquí (ej. 'Recomiéndame libros para circuitos eléctricos')..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "libros": []})
    
    with col_chat:
        with st.chat_message("user", avatar="🎓"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("El Agente Bibliotecario está consultando el catálogo y analizando la mejor recomendación..."):
                try:
                    if st.session_state.agente:
                        respuesta, libros = st.session_state.agente.enviar_mensaje(prompt)
                    else:
                        libros = recomendador.consultar_catalogo(tema=prompt, top_k=3)
                        respuesta = "He consultado nuestro catálogo con el algoritmo TF-IDF. Aquí tienes los libros más pertinentes:"
                    
                    if not libros and any(k in prompt.lower() for k in ["libro", "recomiend", "aprender", "estudiar", "circuito", "puntero", "calculo", "c", "java", "python", "base de datos", "cuantica"]):
                        libros = recomendador.consultar_catalogo(tema=prompt, top_k=3)
                    
                    if libros:
                        st.session_state.libro_seleccionado = libros[0]
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": respuesta,
                        "libros": libros
                    })
                    st.rerun()
                    
                except Exception as e:
                    libros = recomendador.consultar_catalogo(tema=prompt, top_k=3)
                    fallback_resp = "He consultado directamente nuestro catálogo de la biblioteca universitaria con **TF-IDF y Similitud del Coseno**. Aquí tienes las recomendaciones:"
                    if libros:
                        st.session_state.libro_seleccionado = libros[0]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": fallback_resp,
                        "libros": libros
                    })
                    st.rerun()
