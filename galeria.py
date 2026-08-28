import streamlit as st
import os
import base64
from openai import OpenAI
from datetime import datetime, timedelta

DIR_GALERIA = "galeria_fotos"
os.makedirs(DIR_GALERIA, exist_ok=True)

def mostrar_galeria():
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    if "mostrar_globos_galeria" not in st.session_state:
        st.session_state.mostrar_globos_galeria = False

    st.markdown("""
        <style>
        .galeria-header { text-align: center; margin-bottom: 30px; margin-top: 20px; }
        .galeria-titulo { font-family: 'Playfair Display', serif; font-size: 45px; color: #111; font-style: italic; }
        .galeria-subtitulo { font-family: 'Montserrat', sans-serif; font-size: 13px; letter-spacing: 4px; color: #666; text-transform: uppercase; }
        .barra-bg { background-color: #eae6df; border-radius: 50px; height: 12px; width: 100%; margin: 15px 0; overflow: hidden; }
        .barra-fill { background-color: #111; height: 100%; border-radius: 50px; transition: width 0.5s ease-in-out; }
        .recompensa-box { background: linear-gradient(135deg, #fdfbf7 0%, #f4f1eb 100%); padding: 30px; border-radius: 10px; text-align: center; border: 1px dashed #111; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
        .vogue-review { font-family: 'Montserrat', sans-serif; font-size: 15px; color: #333; text-align: center; margin-top: -15px; padding: 15px; background: #faf9f6; border: 1px solid #eee; border-top: none; line-height: 1.6; }
        .tiempo-limite { text-align: center; font-family: 'Montserrat', sans-serif; font-size: 12px; color: #d9534f; font-weight: 600; margin-top: 5px; }
        .badge-ciclo { text-align: center; font-family: 'Montserrat', sans-serif; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: #666; margin-bottom: 5px; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='galeria-header'><div class='galeria-titulo'>El Muro del Orgullo</div><div class='galeria-subtitulo'>Reto: 10 prendas en 6 meses</div></div>", unsafe_allow_html=True)

    archivos_img = [f for f in os.listdir(DIR_GALERIA) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    archivos_img.sort(key=lambda x: os.path.getmtime(os.path.join(DIR_GALERIA, x)))
    
    total_fotos = len(archivos_img)
    
    ciclo_actual = (total_fotos // 10) + 1
    progreso_ciclo = total_fotos % 10
    if progreso_ciclo == 0 and total_fotos > 0:
        progreso_ciclo = 10

    texto_tiempo = "⏳ El tiempo (6 meses) empezará a contar cuando subas tu primera prenda"
    if total_fotos > 0:
        indice_primera_foto_ciclo = (ciclo_actual - 1) * 10
        if indice_primera_foto_ciclo < total_fotos:
            ruta_primera_foto = os.path.join(DIR_GALERIA, archivos_img[indice_primera_foto_ciclo])
            fecha_inicio = datetime.fromtimestamp(os.path.getmtime(ruta_primera_foto))
            fecha_limite = fecha_inicio + timedelta(days=180)
            dias_restantes = (fecha_limite - datetime.now()).days
            
            if dias_restantes >= 0:
                texto_tiempo = f"⏳ Fecha límite: {fecha_limite.strftime('%d/%m/%Y')} (Te quedan {dias_restantes} días)"
            else:
                texto_tiempo = "⏳ ¡Tiempo agotado! (Pero la jefa te deja terminar el ciclo 😉)"
        
    porcentaje = (progreso_ciclo / 10) * 100

    st.markdown(f"""
        <div style="max-width: 600px; margin: 0 auto 30px auto;">
            <div class="badge-ciclo">Temporada / Ciclo {ciclo_actual}</div>
            <div style="font-family: 'Montserrat', sans-serif; font-size: 14px; color: #111; text-align: right; letter-spacing: 1px; margin-bottom: 5px;">
                <b>{progreso_ciclo} / 10 PROYECTOS</b>
            </div>
            <div class="barra-bg"><div class="barra-fill" style="width: {porcentaje}%;"></div></div>
            <div class="tiempo-limite">{texto_tiempo}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.mostrar_globos_galeria:
        st.balloons()
        st.markdown(f"""
            <div class="recompensa-box">
                <h2 style="font-family: 'Playfair Display', serif; color: #111; margin-top:0;">¡RETO SUPERADO! 🎉</h2>
                <p style="font-family: 'Montserrat', sans-serif; color: #444; font-size: 15px;">
                    ¡Has completado 10 proyectos increíbles!<br>
                    <b>🎁 Has ganado una Tarjeta Regalo de 50€</b>.<br>
                    Mándame captura para canjear tu premio. ¡A por el siguiente ciclo!
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.mostrar_globos_galeria = False

    with st.expander("➕ Subir nuevo proyecto terminado"):
        with st.form("form_subida_galeria", clear_on_submit=True):
            foto_nueva = st.file_uploader("Sube la foto de tu prenda finalizada", type=['png', 'jpg', 'jpeg'])
            boton_subir = st.form_submit_button("Añadir al portfolio ✨")

            if boton_subir and foto_nueva is not None:
                ruta_img = os.path.join(DIR_GALERIA, foto_nueva.name)
                with open(ruta_img, "wb") as f:
                    f.write(foto_nueva.getbuffer())

                nuevo_total = total_fotos + 1
                if nuevo_total > 0 and nuevo_total % 10 == 0:
                    st.session_state.mostrar_globos_galeria = True

                with st.spinner("Generando reseña del diseño... 🧐"):
                    img_b64 = base64.b64encode(foto_nueva.getvalue()).decode("utf-8")
                    try:
                        respuesta = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Eres una compañera experta en costura. Hablas de forma natural y cercana. Tienes PROHIBIDO usar lenguaje empalagoso como 'audacia', 'evoca' o 'abraza'."},
                                {"role": "user", "content": [
                                    {"type": "text", "text": "Escribe un comentario natural de 20 palabras exactas destacando un detalle real de esta prenda (el estampado o las costuras). Sé motivadora."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                                ]}
                            ]
                        )
                        critica = respuesta.choices[0].message.content
                    except Exception:
                        critica = "¡Te ha quedado genial! El acabado se ve súper limpio y el tejido encaja perfectamente con el patrón."

                    ruta_txt = os.path.join(DIR_GALERIA, foto_nueva.name + ".txt")
                    with open(ruta_txt, "w", encoding="utf-8") as f:
                        f.write(critica)
                st.rerun()

    st.markdown("<hr style='opacity: 0.2; margin: 40px 0;'>", unsafe_allow_html=True)

    if archivos_img:
        cols = st.columns(3)
        for i, archivo in enumerate(reversed(archivos_img)):
            ruta_img = os.path.join(DIR_GALERIA, archivo)
            ruta_txt = ruta_img + ".txt"
            
            critica_ia = "Un proyecto fantástico con muy buenos acabados."
            if os.path.exists(ruta_txt):
                with open(ruta_txt, "r", encoding="utf-8") as f:
                    critica_ia = f.read()

            with cols[i % 3]:
                st.image(ruta_img, use_container_width=True)
                st.markdown(f"<div class='vogue-review'>«{critica_ia}»</div><br>", unsafe_allow_html=True)
    else:
        st.info("Aún no has subido ningún proyecto terminado. ¡Tu muro te está esperando!")