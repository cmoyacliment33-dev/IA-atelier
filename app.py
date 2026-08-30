import streamlit as st
from revista import mostrar_revista
from inspiracion import mostrar_buscador
from galeria import mostrar_galeria
from openai import OpenAI
import base64
import json
import os
from supabase import create_client, Client

st.set_page_config(page_title="IA Studio", page_icon="🪡", layout="wide")

# ==========================================
# 💅 ESTÉTICA EDITORIAL Y MENÚ DINÁMICO
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Montserrat:wght@300;400;500;600&display=swap');

/* Tipografía de encabezados global */
h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: #111111 !important; }
p, span, div, label { font-family: 'Montserrat', sans-serif; }

/* Estilo de la barra lateral (Solo visible en Taller) */
[data-testid="stSidebar"] { background-color: #f4f1eb !important; border-right: 1px solid #e6e2d8 !important; }

/* Transformar el Radio Button de navegación superior en Pestañas Elegantes */
div[role="radiogroup"] {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-bottom: 30px;
    border-bottom: 1px solid #eae6df;
    padding-bottom: 10px;
}
div[role="radiogroup"] label {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    cursor: pointer;
}
div[role="radiogroup"] label > div:first-child {
    display: none !important; /* Oculta el círculo de selección */
}
div[role="radiogroup"] label p {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 13px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
    color: #999 !important;
    margin: 0 !important;
    transition: color 0.3s;
}
div[role="radiogroup"] label[data-checked="true"] p {
    color: #111 !important;
    border-bottom: 2px solid #111;
    padding-bottom: 5px;
}

/* Botones Primary y Secondary (Barra lateral) */
button[kind="primary"] {
    background-color: #111111 !important;
    color: white !important;
    font-family: 'Montserrat', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 12px !important;
    border-radius: 0px !important;
    border: none !important;
    transition: all 0.3s ease;
}
button[kind="primary"]:hover { background-color: #333333 !important; }

button[kind="secondary"] {
    background-color: transparent !important;
    color: #111111 !important;
    border: 1px solid #111111 !important;
    font-family: 'Montserrat', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 12px !important;
    border-radius: 0px !important;
    transition: all 0.3s ease;
}
button[kind="secondary"]:hover { background-color: #111111 !important; color: white !important; }

/* Cajas de mensajes del chat (Burbujas) */
[data-testid="stChatMessage"] { background-color: transparent !important; border-bottom: 1px solid #f0eee9; padding: 2rem 0 !important; }
.stFileUploader small { display: none; }
hr { border-top: 1px solid #111 !important; opacity: 0.1; }
</style>
""", unsafe_allow_html=True)
# ==========================================

if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("⚠️ Falta configurar la OPENAI_API_KEY en los Secrets de Streamlit Cloud.")

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def guardar_chat(nombre, mensajes):
    try:
        supabase.table("proyectos_chats").upsert({
            "nombre_proyecto": nombre,
            "mensajes": mensajes
        }, on_conflict="nombre_proyecto").execute()
    except Exception as e:
        st.error(f"Error al guardar en la base de datos: {e}")

def cargar_chat(nombre):
    try:
        respuesta = supabase.table("proyectos_chats").select("mensajes").eq("nombre_proyecto", nombre).execute()
        if respuesta.data and len(respuesta.data) > 0:
            data = respuesta.data[0]["mensajes"]
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return [{"role": "assistant", "content": "¡Hola! ¿Qué prenda te gustaría crear hoy?"}]

def obtener_lista_proyectos():
    try:
        respuesta = supabase.table("proyectos_chats").select("nombre_proyecto, created_at").order("created_at", desc=True).execute()
        if respuesta.data:
            return [item["nombre_proyecto"] for item in respuesta.data]
    except Exception:
        pass
    return []

def comprobar_proyecto_existe(nombre):
    try:
        respuesta = supabase.table("proyectos_chats").select("nombre_proyecto").eq("nombre_proyecto", nombre).execute()
        return len(respuesta.data) > 0
    except Exception:
        return False

if "proyecto_actual" not in st.session_state:
    st.session_state.proyecto_actual = "Sin Proyecto"
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! ¿Qué prenda te gustaría crear hoy?"}]
if "widget_key" not in st.session_state:
    st.session_state.widget_key = 0
if "mensaje_pendiente" not in st.session_state:
    st.session_state.mensaje_pendiente = None
if "texto_usuario_pendiente" not in st.session_state:
    st.session_state.texto_usuario_pendiente = None

# ==========================================
# SISTEMA DE NAVEGACIÓN Y FONDOS DINÁMICOS
# ==========================================
opcion_nav = st.radio(
    "Navegación",
    ["🧵 Taller Virtual", "✨ Revista de Inspiración", "💡 Moodboard", "📸 Galería y Recompensas"],
    horizontal=True,
    label_visibility="collapsed"
)

if opcion_nav == "✨ Revista de Inspiración":
    st.markdown("<style>.stApp { background-color: #fdfcf9; }</style>", unsafe_allow_html=True)
    mostrar_revista()

elif opcion_nav == "💡 Moodboard":
    st.markdown("""
    <style>
    /* Fondo estilo Papel de Patronaje */
    .stApp { 
        background-color: #fdfcf9; 
        background-image: 
            linear-gradient(#e1dcd0 1px, transparent 1px), 
            linear-gradient(90deg, #e1dcd0 1px, transparent 1px); 
        background-size: 40px 40px; 
    }
    
    /* Caja de búsqueda con efecto relieve sobre la cuadrícula */
    div[data-testid="stForm"] {
        background: rgba(253, 252, 249, 0.95) !important;
        padding: 40px !important;
        border-radius: 8px;
        border: 1px solid #e1dcd0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)
    mostrar_buscador()

elif opcion_nav == "📸 Galería y Recompensas":
    # Fondo con patrón sutil de puntos
    st.markdown("<style>.stApp { background-color: #fdfcf9; background-image: radial-gradient(#d4cbb8 1px, transparent 1px); background-size: 25px 25px; }</style>", unsafe_allow_html=True)
    mostrar_galeria()

else:
    # 🧵 TALLER VIRTUAL (Fondo limpio para leer bien)
    st.markdown("<style>.stApp { background-color: #fdfcf9; }</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        if st.button("➕ NUEVA CONVERSACIÓN", use_container_width=True, type="primary"):
            st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! ¿Qué prenda te gustaría crear hoy?"}]
            st.session_state.proyecto_actual = "Sin Proyecto"
            st.session_state.widget_key += 1
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Playfair Display,serif; font-size:22px; font-style:italic; color:#111; margin-bottom:10px;'>Mis Proyectos</div>", unsafe_allow_html=True)
        
        proyectos_guardados = obtener_lista_proyectos()
        if proyectos_guardados:
            for proyecto in proyectos_guardados:
                tipo_boton = "primary" if proyecto == st.session_state.proyecto_actual else "secondary"
                if st.button(f"🧵 {proyecto}", key=f"btn_{proyecto}", use_container_width=True, type=tipo_boton):
                    st.session_state.mensajes = cargar_chat(proyecto)
                    st.session_state.proyecto_actual = proyecto
                    st.session_state.widget_key += 1
                    st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Playfair Display,serif; font-size:22px; font-style:italic; color:#111; margin-bottom:10px;'>Archivos Adjuntos</div>", unsafe_allow_html=True)
        
        fotos_subidas = st.file_uploader(
            "Sube fotos de tu tela o ideas (Máx. 3-5)", 
            type=['png', 'jpg', 'jpeg'], 
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.widget_key}" 
        )
        
        st.markdown("<div style='font-family:Montserrat,sans-serif; font-size:12px; letter-spacing:2px; text-transform:uppercase; color:#666; margin-top:20px; margin-bottom:5px;'>O graba una nota de voz</div>", unsafe_allow_html=True)
        audio_usuario = st.audio_input("Grabar mensaje", label_visibility="collapsed", key=f"audio_{st.session_state.widget_key}")

    st.markdown("""
        <div style="text-align: center; padding: 40px 0 20px 0;">
            <div style="font-family: 'Montserrat', sans-serif; font-size: 11px; letter-spacing: 5px; color: #888; text-transform: uppercase; margin-bottom: 10px;">Atelier Privado</div>
            <h1 style="font-size: 45px; margin: 0; line-height: 1.2;">El Taller de Belén</h1>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.proyecto_actual != "Sin Proyecto":
        st.markdown(f"<div style='text-align: center; font-family: Montserrat, sans-serif; font-size: 13px; font-weight: 600; letter-spacing: 2px; color: #111; text-transform: uppercase; border-bottom: 1px solid #ddd; padding-bottom: 20px; margin-bottom: 30px; display: inline-block; width: 100%;'>PROYECTO ACTUAL: {st.session_state.proyecto_actual}</div>", unsafe_allow_html=True)

    for mensaje in st.session_state.mensajes:
        if isinstance(mensaje, dict) and "role" in mensaje and "content" in mensaje:
            with st.chat_message(mensaje["role"]):
                contenido = mensaje["content"]
                if isinstance(contenido, list):
                    texto_mostrable = ""
                    for item in contenido:
                        if isinstance(item, dict) and item.get("type") == "text":
                            texto_mostrable += item.get("text", "")
                    st.markdown(texto_mostrable if texto_mostrable else "*(Imagen adjunta)*")
                else:
                    st.markdown(str(contenido))

    texto_usuario = st.chat_input("Escribe a tu mentora aquí...")

    if texto_usuario or audio_usuario:
        prompt_texto = None
        
        if audio_usuario:
            with st.spinner("Transcribiendo audio... 🎧"):
                transcripcion = client.audio.transcriptions.create(
                    model="whisper-1", file=("audio.wav", audio_usuario)
                )
                prompt_texto = transcripcion.text
        else:
            prompt_texto = texto_usuario

        contenido_usuario = [{"type": "text", "text": prompt_texto}]
        if fotos_subidas:
            for foto in fotos_subidas:
                img_bytes = foto.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                contenido_usuario.append({"type": "image_url", "image_url": {"url": f"data:{foto.type};base64,{img_base64}"}})
                
        st.session_state.mensaje_pendiente = contenido_usuario
        st.session_state.texto_usuario_pendiente = prompt_texto
        st.session_state.widget_key += 1
        st.rerun()

    if st.session_state.mensaje_pendiente:
        st.session_state.mensajes.append({"role": "user", "content": st.session_state.mensaje_pendiente})
        with st.chat_message("user"):
            st.write(st.session_state.texto_usuario_pendiente)

        with st.chat_message("assistant"):
            with st.spinner("Cosiendo la respuesta... 🪡"):
                if st.session_state.proyecto_actual == "Sin Proyecto":
                    resp_titulo = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": f"Resume este texto en 2 a 4 palabras para el título de un proyecto de costura. Responde SOLO con el título, sin comillas ni puntos: '{st.session_state.texto_usuario_pendiente}'"}]
                    )
                    nuevo_titulo = resp_titulo.choices[0].message.content.strip()
                    titulo_final = nuevo_titulo
                    contador = 1
                    while comprobar_proyecto_existe(titulo_final):
                        titulo_final = f"{nuevo_titulo} {contador}"
                        contador += 1
                    st.session_state.proyecto_actual = titulo_final

                mensajes_api = [
                    {"role": "system", "content": """Eres una MAESTRA PATRONISTA. La usuaria NO SABE NADA de costura.
                    REGLAS ESTRICTAS E INQUEBRANTABLES:
                    1. INSPIRACIÓN: Si pide inspiración, genera SIEMPRE este botón exacto: [📌 Ver ideas en Pinterest](https://www.pinterest.es/search/pins/?q=tu+busqueda+aqui).
                    2. VÍDEOS EN CADA PASO (OBLIGATORIO): Tienes TOTALMENTE PROHIBIDO agrupar los vídeos al final de tu respuesta. Debes poner el enlace de YouTube JUSTO DEBAJO del texto de CADA paso numerado. (Ejemplo: Paso 1, explicación, enlace. Paso 2, explicación, enlace). ¡Un paso, un vídeo!
                    3. FORMATO DEL VÍDEO: Usa exactamente: [🎥 Ver vídeo de este paso](https://www.youtube.com/results?search_query=palabras+clave+separadas+por+signo+mas).
                    4. BÚSQUEDAS DE YOUTUBE BLINDADAS: La URL debe ser una fórmula exacta. DEBE contener la ACCIÓN DEL PASO + la PRENDA ACTUAL + "costura". TIENES PROHIBIDO mezclar prendas o hacer búsquedas genéricas. Ejemplos correctos: "como+hacer+patron+top+costura", "como+coser+tirantes+top+costura".
                    5. DETALLE EXTREMO: Explica de qué lado mirar la tela, centímetros de margen, etc.
                    6. MEMORIA VISUAL: Si te pregunta por una foto que subió antes, mírala en tu historial.
                    """}
                ]
                
                for msg in st.session_state.mensajes[:-1]: 
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        mensajes_api.append({"role": msg["role"], "content": msg["content"]})
                    
                mensajes_api.append({"role": "user", "content": st.session_state.mensaje_pendiente})

                respuesta = client.chat.completions.create(model="gpt-4o-mini", messages=mensajes_api)
                texto_ia = respuesta.choices[0].message.content
                st.markdown(texto_ia)
                
                st.session_state.mensajes.append({"role": "assistant", "content": texto_ia})
                guardar_chat(st.session_state.proyecto_actual, st.session_state.mensajes)
                
                st.session_state.mensaje_pendiente = None
                st.session_state.texto_usuario_pendiente = None
                st.rerun()
