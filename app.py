import streamlit as st
from revista import mostrar_revista
from inspiracion import mostrar_buscador
from galeria import mostrar_galeria
from openai import OpenAI
import base64
import json
import os

st.set_page_config(page_title="IA Studio", page_icon="🪡", layout="wide")

if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("⚠️ Falta configurar la OPENAI_API_KEY en los Secrets de Streamlit Cloud.")

CARPETA = "proyectos"
if not os.path.exists(CARPETA):
    os.makedirs(CARPETA)

def guardar_chat(nombre, mensajes):
    with open(f"{CARPETA}/{nombre}.json", "w", encoding="utf-8") as f:
        json.dump(mensajes, f, ensure_ascii=False)

def cargar_chat(nombre):
    ruta = f"{CARPETA}/{nombre}.json"
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return [{"role": "assistant", "content": "¡Hola! ¿Qué prenda te gustaría crear hoy?"}]

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

pestana_taller, pestana_revista, pestana_inspiracion, pestana_galeria = st.tabs([
    "🧵 Taller Virtual", 
    "✨ Revista de Inspiración", 
    "💡 Cazadora de Ideas", 
    "📸 Galería y Recompensas"
])

with pestana_revista:
    mostrar_revista()

with pestana_inspiracion:
    mostrar_buscador()

with pestana_galeria:
    mostrar_galeria()

with pestana_taller:
    with st.sidebar:
        if st.button("➕ Nueva Conversación", use_container_width=True, type="primary"):
            st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! ¿Qué prenda te gustaría crear hoy?"}]
            st.session_state.proyecto_actual = "Sin Proyecto"
            st.session_state.widget_key += 1
            st.rerun()

        st.markdown("---")
        st.title("📁 Mis Proyectos")
        
        if os.path.exists(CARPETA):
            # Filtramos para que NUNCA intente leer archivos de la revista como si fueran chats
            archivos = [f for f in os.listdir(CARPETA) if f.endswith(".json") and "revista" not in f.lower()]
            archivos_ordenados = sorted(archivos, key=lambda x: os.path.getmtime(os.path.join(CARPETA, x)), reverse=True)
            
            for archivo in archivos_ordenados:
                nombre_limpio = archivo.replace(".json", "")
                tipo_boton = "primary" if nombre_limpio == st.session_state.proyecto_actual else "secondary"
                if st.button(f"🧵 {nombre_limpio}", key=f"btn_{nombre_limpio}", use_container_width=True, type=tipo_boton):
                    st.session_state.mensajes = cargar_chat(nombre_limpio)
                    st.session_state.proyecto_actual = nombre_limpio
                    st.session_state.widget_key += 1
                    st.rerun()

        st.markdown("---")
        st.title("📎 Envíos Extra")
        
        fotos_subidas = st.file_uploader(
            "Sube fotos de tu tela o ideas (Máx. 3-5)", 
            type=['png', 'jpg', 'jpeg'], 
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.widget_key}" 
        )
        
        audio_usuario = st.audio_input("Grabar mensaje", label_visibility="collapsed", key=f"audio_{st.session_state.widget_key}")

    st.title("✨ El Taller Virtual de Belén")
    if st.session_state.proyecto_actual != "Sin Proyecto":
        st.subheader(f"🧵 {st.session_state.proyecto_actual}")

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
                    while os.path.exists(f"{CARPETA}/{titulo_final}.json"):
                        titulo_final = f"{nuevo_titulo} {contador}"
                        contador += 1
                    st.session_state.proyecto_actual = titulo_final

                mensajes_api = [
                    {"role": "system", "content": """Eres una MAESTRA PATRONISTA. La usuaria NO SABE NADA de costura.
                    REGLAS ESTRICTAS E INQUEBRANTABLES:
                    1. INSPIRACIÓN: Si pide inspiración, genera SIEMPRE este botón exacto: [📌 Ver ideas en Pinterest](https://www.pinterest.es/search/pins/?q=tu+busqueda+aqui).
                    2. VÍDEOS EN CADA PASO: Obligatorio poner un enlace de YouTube JUSTO AL FINAL DE CADA PASO. 
                    3. FORMATO DEL VÍDEO: Usa exactamente: [🎥 Ver vídeo de este paso](https://www.youtube.com/results?search_query=palabras+clave+separadas+por+signo+mas).
                    4. BÚSQUEDAS ESPECÍFICAS: Deben ser muy precisas (ej: "como+coser+tirantes+top+tela").
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
