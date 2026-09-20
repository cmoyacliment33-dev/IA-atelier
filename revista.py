import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import json
import os
import datetime
import random
import base64
import shutil
import hashlib
from supabase import create_client, Client

ARCHIVO_REVISTA = "revista_actual.json"
DIR_DISPONIBLES = "imagenes_disponibles"
DIR_USADAS = "imagenes_usadas"
BUCKET_REVISTA = "galeria_fotos" 

os.makedirs(DIR_DISPONIBLES, exist_ok=True)
os.makedirs(DIR_USADAS, exist_ok=True)

@st.cache_resource
def init_supabase_revista() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

RUTA_FOTO_EDITOR = "assets/mi_foto.jpg"

TEXTO_DEL_EDITOR = """
Para la persona que lo puede todo y que su único límite debe ser su imaginación.<br><br>

Que este mes te traiga tanta inspiración como la que tú nos regalas a los demás.
"""

REGALO_DEL_MES = """
🎉 <b>Un libro a tu elección</b><br><br>
Elige la novela que más ganas tengas de leer y yo me encargo del resto. 📖✨<br><br>
<i>(Pídemelo cuando sepas cuál quieres 😉)</i>
"""

def limpiar_imagenes_duplicadas():
    hashes_usados = set()
    for f in os.listdir(DIR_USADAS):
        ruta = os.path.join(DIR_USADAS, f)
        if os.path.isfile(ruta):
            with open(ruta, "rb") as img:
                hashes_usados.add(hashlib.md5(img.read()).hexdigest())
                
    for f in os.listdir(DIR_DISPONIBLES):
        ruta = os.path.join(DIR_DISPONIBLES, f)
        if os.path.isfile(ruta):
            with open(ruta, "rb") as img:
                filehash = hashlib.md5(img.read()).hexdigest()
            if filehash in hashes_usados:
                os.remove(ruta)

def obtener_img_base64(ruta_o_nombre):
    if os.path.exists(ruta_o_nombre):
        ruta_final = ruta_o_nombre
    else:
        nombre_archivo = os.path.basename(ruta_o_nombre)
        ruta_usada = os.path.join(DIR_USADAS, nombre_archivo)
        ruta_disp = os.path.join(DIR_DISPONIBLES, nombre_archivo)
        
        if os.path.exists(ruta_usada):
            ruta_final = ruta_usada
        elif os.path.exists(ruta_disp):
            ruta_final = ruta_disp
        else:
            return "https://placehold.co/400x600/eae6df/a39f98?text=+"
            
    with open(ruta_final, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
        ext = ruta_final.split('.')[-1].lower()
        tipo = "png" if ext == "png" else ("webp" if ext == "webp" else "jpeg")
        return f"data:image/{tipo};base64,{encoded}"

def generar_doble_pagina_modular(index, articulo, fotos_mes, layout_asignado):
    tit = articulo.get("titular", "INSPIRACIÓN")
    txt_original = articulo.get("texto", "Explorando las profundidades del diseño...")
    cita = articulo.get("cita", "La moda es un lenguaje.")
    tag = articulo.get("tag", "Editorial")
    
    txt_limpio = txt_original.replace("<span class='hb-dropcap'>", "").replace("</span>", "").strip()
    if len(txt_limpio) > 0:
        txt = f"<span class='hb-dropcap'>{txt_limpio[0]}</span>{txt_limpio[1:]}"
    else:
        txt = "<span class='hb-dropcap'>E</span>l arte de la moda siempre encuentra un camino."

    if len(fotos_mes) == 0:
        fotos_mes = ["dummy.jpg"]

    img1 = obtener_img_base64(fotos_mes[(index * 3) % len(fotos_mes)])
    img2 = obtener_img_base64(fotos_mes[((index * 3) + 1) % len(fotos_mes)])
    img3 = obtener_img_base64(fotos_mes[((index * 3) + 2) % len(fotos_mes)])

    paleta = random.choice([
        {"bg": "#ffffff", "text": "#111111", "accent": "#888888"},
        {"bg": "#faf8f5", "text": "#222222", "accent": "#666666"},
        {"bg": "#111111", "text": "#eeeeee", "accent": "#aaaaaa"},
        {"bg": "#0a0a0a", "text": "#fdfcf9", "accent": "#777777"} 
    ])
    
    filtro_img = "filter: contrast(110%);"
    
    tamano_titulo = random.choice(["70px", "90px", "110px"])
    alineacion = random.choice(["left", "center"])
    columnas = random.choice(["1", "2"])
    
    es_espejo = random.choice([True, False])
    flex_dir = "row-reverse" if es_espejo else "row"

    html_base = f"""<div id="pag-{index}" class="pagina doble" style="display: none; background-color: {paleta["bg"]}; color: {paleta["text"]}; flex-direction: {flex_dir};">"""

    num_izq = (index*2) + 1 if es_espejo else (index*2)
    num_der = (index*2) if es_espejo else (index*2) + 1

    if layout_asignado == 1:
        html_base += f"""
        <div class="pagina-izq" style="padding: 80px; display: flex; flex-direction: column; justify-content: center; text-align: {alineacion}; border-right: 1px solid rgba(150,150,150,0.2);">
            <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: {tamano_titulo}; color:{paleta["text"]}; margin: 30px 0;">{tit}</div>
            <div class="hb-columnas" style="color: {paleta["text"]}; column-count: {columnas};">{txt}</div><span class="numero-pagina np-izq" style="color: {paleta["accent"]};">{num_izq}</span>
        </div>
        <div class="pagina-der" style="background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center; {filtro_img}"><span class="numero-pagina np-der" style="color:white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{num_der}</span></div>
        """
    elif layout_asignado == 2:
        html_base += f"""
        <div class="pagina-izq p1-izq" style="border-right: 1px solid rgba(150,150,150,0.2); display: flex; flex-direction: column;">
            <div class="hb-titulo-1" style="z-index: 100; color:{paleta["text"]};">The</div>
            <div class="hb-imagen" style="flex: 1; width: 80%; background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center; z-index: 1; {filtro_img}"></div>
            <span class="numero-pagina np-izq" style="color:{paleta["accent"]};">{num_izq}</span>
        </div>
        <div class="pagina-der p1-der" style="background: {paleta["bg"]}; padding: 80px; display: flex; flex-direction: column; justify-content: center;">
            <div class="hb-titulo-2" style="font-size: 70px; color:{paleta["text"]};">{tit}</div>
            <div class="seccion-tag" style="margin-top: 20px; color:{paleta["accent"]};">{tag}</div>
            <div class="hb-columnas" style="color:{paleta["text"]};">{txt}</div><div class="linea-fina" style="background:{paleta["text"]};"></div>
            <div style="font-style: italic; text-align: center; color: {paleta["accent"]};">"{cita}"</div><span class="numero-pagina np-der" style="color:{paleta["accent"]};">{num_der}</span>
        </div>
        """
    elif layout_asignado == 3:
        html_base += f"""
        <div class="pagina-izq" style="background-color: #eae6df; background-image: url('{img2}'); background-size: cover; background-position: center; {filtro_img}"><span class="numero-pagina np-izq" style="color:white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{num_izq}</span></div>
        <div class="pagina-der" style="padding: 100px; display: flex; flex-direction: column; justify-content: center; background: {paleta["bg"]};">
            <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 55px; font-style: italic; line-height: 1.2; margin: 40px 0; color: {paleta["text"]};">"{cita}"</div>
            <div style="font-family: 'Montserrat', sans-serif; font-size: 14px; line-height: 2; color: {paleta["accent"]}; border-left: 2px solid {paleta["text"]}; padding-left: 20px;">{txt.split('<br><br>')[0]}</div>
            <span class="numero-pagina np-der" style="color:{paleta["accent"]};">{num_der}</span>
        </div>
        """
    elif layout_asignado == 4:
        html_base += f"""
        <div class="pagina-izq" style="padding: 80px; background: {paleta["bg"]}; border-right: 1px solid rgba(150,150,150,0.2); display: flex; flex-direction: column;">
            <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: 70px; color:{paleta["text"]};">{tit}</div>
            <div class="collage-container" style="position:relative; flex: 1; margin-top: 40px; min-height: 400px;">
                <div style="position:absolute; width: 70%; height: 70%; top:20px; left:0; transform: rotate(-{random.randint(2,8)}deg); border: 15px solid {paleta["bg"]}; box-shadow: 0 10px 30px rgba(0,0,0,0.1); background-color: #eae6df; background-image: url('{img1}'); background-size:cover; background-position: center; {filtro_img}"></div>
                <div style="position:absolute; width: 60%; height: 60%; bottom:20px; right:0; transform: rotate({random.randint(2,8)}deg); border: 15px solid {paleta["bg"]}; box-shadow: 0 10px 30px rgba(0,0,0,0.1); background-color: #eae6df; background-image: url('{img2}'); background-size:cover; background-position: center; {filtro_img}"></div>
            </div><span class="numero-pagina np-izq" style="color:{paleta["accent"]};">{num_izq}</span>
        </div>
        <div class="pagina-der" style="padding: 80px; display: flex; flex-direction: column; background: {paleta["bg"]};">
            <div style="font-size: 18px; line-height: 1.8; color: {paleta["text"]}; font-style: italic;">{txt}</div>
            <div style="flex: 1; background-color: #eae6df; background-image: url('{img3}'); background-size: cover; background-position: center; margin-top: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); {filtro_img}"></div><span class="numero-pagina np-der" style="color:{paleta["accent"]};">{num_der}</span>
        </div>
        """
    elif layout_asignado == 5:
        html_base += f"""
        <div class="pagina-izq" style="padding: 80px; display: flex; flex-direction: column; border-right: 1px solid rgba(150,150,150,0.2); background: {paleta["bg"]};">
            <div style="flex: 1; background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center; margin-bottom: 40px; {filtro_img}"></div>
            <div class="hb-columnas" style="column-count: {columnas}; color:{paleta["text"]}; margin-top:0;">{txt}</div><span class="numero-pagina np-izq" style="color:{paleta["accent"]};">{num_izq}</span>
        </div>
        <div class="pagina-der" style="background-color: #eae6df; background-image: url('{img2}'); background-size: cover; background-position: center;">
            <div style="position: absolute; bottom: 80px; left: 80px; background: {paleta["bg"]}; padding: 40px; max-width: 70%; box-shadow: 0 20px 40px rgba(0,0,0,0.2);">
                <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: 45px; line-height: 1; color:{paleta["text"]};">{tit}</div>
            </div><span class="numero-pagina np-der" style="color:white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{num_der}</span>
        </div>
        """
    elif layout_asignado == 6:
        html_base += f"""
        <div class="pagina-izq" style="padding: 80px; display: flex; flex-direction: column; border-right: 1px solid rgba(150,150,150,0.2); background: {paleta["bg"]};">
            <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: 80px; color:{paleta["text"]};">{tit}</div>
            <div class="hb-columnas" style="column-count: 1; color:{paleta["text"]};">{txt}</div><span class="numero-pagina np-izq" style="color:{paleta["accent"]};">{num_izq}</span>
        </div>
        <div class="pagina-der" style="padding: 40px; display: flex; gap: 20px; background: {paleta["bg"]};">
            <div style="flex: 1; background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center; {filtro_img}"></div>
            <div style="flex: 1; background-color: #eae6df; background-image: url('{img2}'); background-size: cover; background-position: center; margin-top: 80px; margin-bottom: -80px; {filtro_img}"></div>
            <span class="numero-pagina np-der" style="color:{paleta["accent"]};">{num_der}</span>
        </div>
        """
    elif layout_asignado == 7:
        html_base += f"""
        <div class="pagina-izq" style="background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center; {filtro_img}"><span class="numero-pagina np-izq" style="color:white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{num_izq}</span></div>
        <div class="pagina-der" style="padding: 100px; display: flex; flex-direction: column; justify-content: center; align-items: center; background: {paleta["bg"]};">
            <div class="seccion-tag" style="text-align:center; color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: 60px; text-align:center; margin: 30px 0; color:{paleta["text"]};">{tit}</div>
            <div style="font-size: 20px; text-align:center; font-style: italic; color: {paleta["accent"]}; margin-bottom: 40px;">"{cita}"</div>
            <div class="hb-columnas" style="column-count: 1; font-size: 17px; line-height: 1.8; color:{paleta["text"]}; text-align: justify;">{txt}</div><span class="numero-pagina np-der" style="color:{paleta["accent"]};">{num_der}</span>
        </div>
        """
    elif layout_asignado == 8:
        html_base += f"""
        <div class="pagina-izq" style="background-color: #eae6df; background-image: url('{img2}'); background-size: cover; background-position: center; position: relative;">
             <div style="position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.5);"></div>
             <div style="position: absolute; top: 80px; left: 80px; color: white; padding-right: 80px;">
                 <div class="seccion-tag" style="color: #ddd;">{tag}</div><div class="hb-titulo-2" style="font-size: 80px; color: white;">{tit}</div>
             </div>
             <span class="numero-pagina np-izq" style="color:white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{num_izq}</span>
        </div>
        <div class="pagina-der" style="padding: 100px; display: flex; align-items: center; background: {paleta["bg"]};">
            <div class="hb-columnas" style="column-count: 1; color:{paleta["text"]};">{txt}</div><span class="numero-pagina np-der" style="color:{paleta["accent"]};">{num_der}</span>
        </div>
        """
    elif layout_asignado == 9:
        html_base += f"""
        <div class="pagina-izq" style="background-color: #eae6df; background-image: url('{img3}'); background-size: cover; background-position: center; {filtro_img}"><span class="numero-pagina np-izq" style="color:white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{num_izq}</span></div>
        <div class="pagina-der" style="background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center;">
             <div style="position:absolute; bottom: 80px; right: 80px; background: {paleta["bg"]}; padding: 40px; width: 350px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: 40px; color:{paleta["text"]};">{tit}</div><div style="font-size: 15px; line-height: 1.6; margin-top:20px; color:{paleta["text"]};">{txt.split('<br><br>')[0]}</div>
             </div><span class="numero-pagina np-der" style="color:white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{num_der}</span>
        </div>
        """
    elif layout_asignado == 10:
        html_base += f"""
        <div class="pagina-izq" style="padding: 60px; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 20px; background: {paleta["bg"]}; border-right: 1px solid rgba(150,150,150,0.2);">
            <div style="grid-column: 1 / -1; background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center; {filtro_img}"></div>
            <div style="background-color: #eae6df; background-image: url('{img2}'); background-size: cover; background-position: center; {filtro_img}"></div>
            <div style="background-color: #eae6df; background-image: url('{img3}'); background-size: cover; background-position: center; {filtro_img}"></div>
            <span class="numero-pagina np-izq" style="color:{paleta["accent"]};">{num_izq}</span>
        </div>
        <div class="pagina-der" style="padding: 100px; display: flex; flex-direction: column; justify-content: center; background: {paleta["bg"]};">
            <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: 65px; color:{paleta["text"]};">{tit}</div>
            <div class="hb-columnas" style="color:{paleta["text"]}; margin-top:30px;">{txt}</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 26px; font-style: italic; color: {paleta["accent"]}; margin-top: 60px; border-top: 1px solid rgba(150,150,150,0.3); padding-top: 40px; text-align: center;">"{cita}"</div>
            <span class="numero-pagina np-der" style="color:{paleta["accent"]};">{num_der}</span>
        </div>
        """
    elif layout_asignado == 11:
        html_base += f"""
        <div class="pagina-izq" style="display: flex; flex-direction: column; background: {paleta["bg"]};">
            <div style="flex: 1.5; background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center; {filtro_img}"></div>
            <div style="flex: 1; padding: 60px; display: flex; flex-direction: column; justify-content: center;">
                <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: 55px; color:{paleta["text"]}; margin-top: 10px;">{tit}</div>
            </div><span class="numero-pagina np-izq" style="color:{paleta["text"]};">{num_izq}</span>
        </div>
        <div class="pagina-der" style="padding: 80px; display: flex; flex-direction: column; justify-content: center; gap: 30px; background: {paleta["bg"]};">
            <div style="font-family: 'Playfair Display', serif; font-size: 22px; font-style: italic; color: {paleta["accent"]}; text-align: center;">"{cita}"</div>
            <div class="hb-columnas" style="color:{paleta["text"]}; margin-top:0;">{txt}</div>
            <div style="height: 40%; min-height: 300px; background-color: #eae6df; background-image: url('{img2}'); background-size: cover; background-position: center; {filtro_img}"></div>
            <span class="numero-pagina np-der" style="color:{paleta["accent"]};">{num_der}</span>
        </div>
        """
    else:
        html_base += f"""
        <div class="pagina-izq" style="padding: 80px; display: flex; flex-direction: column; justify-content: center; background: {paleta["bg"]};">
            <div class="seccion-tag" style="color:{paleta["accent"]};">{tag}</div><div class="hb-titulo-2" style="font-size: 85px; margin-bottom: 40px; color:{paleta["text"]};">{tit}</div>
            <div class="hb-columnas" style="column-count: 1; color:{paleta["text"]};">{txt}</div><span class="numero-pagina np-izq" style="color:{paleta["accent"]};">{num_izq}</span>
        </div>
        <div class="pagina-der" style="display: flex; flex-direction: column;">
            <div style="flex:1; background-color: #eae6df; background-image: url('{img1}'); background-size: cover; background-position: center; {filtro_img}"></div>
            <div style="flex:1; background-color: #eae6df; background-image: url('{img2}'); background-size: cover; background-position: center; {filtro_img}"></div>
            <span class="numero-pagina np-der" style="color:white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{num_der}</span>
        </div>
        """
        
    html_base += "</div>"
    return html_base

def mostrar_revista():
    limpiar_imagenes_duplicadas()

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    supabase = init_supabase_revista()
    
    fecha_actual = datetime.datetime.now()
    mes_actual = fecha_actual.strftime("%Y-%m")
    nombre_mes = fecha_actual.strftime("%B %Y").capitalize()
    mes_numero = fecha_actual.month
    
    datos_revista = None
    generar_nueva = True

    try:
        res = supabase.storage.from_(BUCKET_REVISTA).download(ARCHIVO_REVISTA)
        if res:
            datos_guardados = json.loads(res.decode("utf-8"))
            if datos_guardados.get("mes") == mes_actual and "secciones" in datos_guardados:
                datos_revista = datos_guardados
                generar_nueva = False
    except Exception:
        pass

    if generar_nueva:
        with st.spinner(f"✨ Vogue AI redactando la edición de {nombre_mes}... (Esto puede tardar un poco)"):
            
            calendario_temas = {
                1: "Futurismo, tejidos técnicos y siluetas del año 3000",
                2: "El impacto del Surrealismo y los sueños en el patronaje",
                3: "La deconstrucción: prendas inacabadas y simetría rota",
                4: "Inspiración floral oscura: la naturaleza salvaje en la alta costura",
                5: "El arte de la sastrería clásica hiper-femenina",
                6: "Fluidez extrema y tejidos translúcidos de inspiración marina",
                7: "Estilo retro-futurista de los años 70",
                8: "Arquitectura brutalista y la creación de prendas con volumen rígido",
                9: "El color rojo y la psicología emocional en el vestir",
                10: "Minimalismo extremo japonés y la belleza del vacío",
                11: "El renacer del movimiento Punk y la moda de protesta",
                12: "Decadencia elegante, terciopelo y lujo oscuro"
            }
            
            tema_mes = calendario_temas.get(mes_numero, "Innovación en el diseño de moda")

            prompt = f"""
            Eres el redactor jefe de una publicación de alta costura y ensayo visual.
            
            ATENCIÓN - REGLA ABSOLUTA Y ESTRICTA:
            Esta edición es un NÚMERO MONOTEMÁTICO. El ÚNICO tema de TODA la revista es: '{tema_mes}'.
            
            ESTÁ TERMINANTEMENTE PROHIBIDO hacer un pupurrí de temas. 
            Las 14 secciones que vas a generar DEBEN hablar EXCLUSIVAMENTE de '{tema_mes}'. 
            Cada artículo debe abordar este mismo tema desde un ángulo diferente (materiales, siluetas, filosofía, arte), pero NUNCA cambiar a temas genéricos como "eco-cultura", "historia", "identidad global" o "colaboraciones" si no están 100% justificados por el tema principal '{tema_mes}'.
            
            Genera el contenido en formato JSON.
            
            REGLAS MUY ESTRICTAS PARA LOS TEXTOS ('texto') Y TITULARES ('titular'):
            1. Son ensayos y crónicas reales, y CADA UNA DE ELLAS debe centrarse obsesivamente en el tema '{tema_mes}'.
            2. VARIEDAD DE LONGITUD DE TEXTO (MUY IMPORTANTE): 
               - Crea una mezcla equilibrada. Algunos artículos deben ser largos y profundos (2 o 3 párrafos, unas 150-200 palabras) llenos de datos técnicos.
               - Otros artículos deben ser reseñas muy cortas (1 solo párrafo de unas 30-40 palabras) para que la revista respire.
            3. OBLIGATORIO: Si tu texto tiene más de un párrafo, usa EXACTAMENTE la etiqueta "<br><br>" para separar los párrafos. NO uses ninguna otra etiqueta HTML.
            4. VARIEDAD EN LOS TITULARES: 
               - EXACTAMENTE la mitad de los artículos deben tener titulares compuestos usando dos puntos.
               - La otra mitad deben tener titulares muy cortos y directos (1 a 3 palabras máximo).
            
            Estructura JSON requerida (DEBES CREAR EXACTAMENTE 14 SECCIONES):
            {{
                "portada": {{
                    "titulo": "PALABRA",
                    "tema": "El tema central adaptado a '{tema_mes}'"
                }},
                "secciones": [
                    {{
                        "titular": "Titular conceptual",
                        "tag": "Categoría",
                        "texto": "Aquí tu ensayo, largo o corto según corresponda. Usa <br><br> para separar párrafos si es largo.",
                        "cita": "Una frase inspiradora relacionada"
                    }}
                ]
            }}
            """
            
            respuesta = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={ "type": "json_object" },
                messages=[{"role": "user", "content": prompt}]
            )
            
            datos_revista = json.loads(respuesta.choices[0].message.content)
            datos_revista["mes"] = mes_actual
            datos_revista["nombre_mes"] = nombre_mes
            
            archivos_disponibles = [f for f in os.listdir(DIR_DISPONIBLES) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.avif'))]
            random.shuffle(archivos_disponibles)
            
            fotos_mes = []
            fotos_necesarias = 43 
            
            for img in archivos_disponibles[:fotos_necesarias]:
                src = os.path.join(DIR_DISPONIBLES, img)
                dst = os.path.join(DIR_USADAS, img)
                try:
                    shutil.move(src, dst)
                    fotos_mes.append(img) 
                except Exception:
                    pass

            if len(fotos_mes) < fotos_necesarias:
                archivos_usados = [f for f in os.listdir(DIR_USADAS) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.avif'))]
                random.shuffle(archivos_usados)
                faltantes = fotos_necesarias - len(fotos_mes)
                
                fotos_extra = [f for f in archivos_usados if f not in fotos_mes]
                fotos_mes.extend(fotos_extra[:faltantes])
                
            datos_revista["fotos_mes"] = fotos_mes

            datos_revista["orden_layouts"] = [1, 8, 2, 5, 3, 10, 4, 9, 6, 11, 7, 12, 1, 8]

            try:
                json_str = json.dumps(datos_revista, ensure_ascii=False)
                supabase.storage.from_(BUCKET_REVISTA).upload(
                    path=ARCHIVO_REVISTA,
                    file=json_str.encode("utf-8"),
                    file_options={"content-type": "application/json", "upsert": "true"}
                )
            except Exception as e:
                pass 

    fotos_mes = datos_revista.get("fotos_mes", [])
    orden_layouts = datos_revista.get("orden_layouts", [1, 8, 2, 5, 3, 10, 4, 9, 6, 11, 7, 12, 1, 8])
    
    datos_portada = datos_revista.get("portada", {"titulo": "VOGUE", "tema": "The Design Issue"})
    titulo_portada = datos_portada.get("titulo", "VOGUE")
    tema_portada = datos_portada.get("tema", "Edición Especial")
    
    foto_portada = obtener_img_base64(fotos_mes[0]) if fotos_mes else ""
    
    palabras_titulo = titulo_portada.split()
    len_max_palabra = max([len(p) for p in palabras_titulo] + [1])
    font_size_px = min(140, int((700 / len_max_palabra) * 1.4))
    
    estilo_texto = f"font-size: {font_size_px}px; word-break: keep-all; overflow-wrap: break-word; hyphens: none; line-height: 1.1; width: 100%; max-width: 730px; margin: 0 auto;"
    
    html_portada = f"""
    <div id="pag-0" class="pagina simple" style="display: block; width: 850px; margin: 0 auto; background-color: #111; background-image: url('{foto_portada}'); background-size: cover; background-position: center; position: relative;">
        <div class="revista-overlay" style="position: absolute; top:0; left:0; right:0; bottom:0; background: linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.8) 100%); display: flex; flex-direction: column; justify-content: space-between; padding: 60px;">
            <div class="portada-header" style="display: flex; justify-content: space-between; color: white; font-family: 'Montserrat', sans-serif; font-size: 15px; letter-spacing: 5px; text-transform: uppercase;"><span>Edición de</span><span>{datos_revista.get("nombre_mes", "Este Mes")}</span></div>
            
            <h1 class="portada-titulo" style="text-align: center; font-family: 'Playfair Display', serif; {estilo_texto} font-weight: 700; color: white; letter-spacing: -3px; text-shadow: 2px 4px 20px rgba(0,0,0,0.5); text-transform: uppercase;">{titulo_portada}</h1>
            
            <div class="portada-footer" style="color: white; font-family: 'Playfair Display', serif; text-align: right;">
                <div class="portada-titular-principal" style="font-size: 55px; font-style: italic; margin-bottom: 10px; line-height: 1.1;">{tema_portada}</div>
                <div class="portada-subtitular" style="font-family: 'Montserrat', sans-serif; font-size: 16px; font-weight: 300; letter-spacing: 4px; text-transform: uppercase;">Moda · Patronaje · Inspiración</div>
            </div>
        </div>
    </div>
    """

    html_paginas_interiores = ""
    secciones = datos_revista.get("secciones", [])
    fotos_interiores = fotos_mes[1:] if len(fotos_mes) > 1 else fotos_mes

    for i, seccion in enumerate(secciones):
        layout_asignado = orden_layouts[i % len(orden_layouts)]
        html_paginas_interiores += generar_doble_pagina_modular(i+1, seccion, fotos_interiores, layout_asignado)

    index_final = len(secciones) + 1
    total_paginas = index_final + 1
    
    img_editor_b64 = obtener_img_base64(RUTA_FOTO_EDITOR)
    
    html_contraportada = f"""
    <div id="pag-{index_final}" class="pagina simple" style="display: none; width: 850px; flex-direction: row; margin: 0 auto; box-shadow: inset 0 0 100px rgba(0,0,0,0.05); overflow: hidden;">
        
        <div style="width: 40%; background-color: #111; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; position: relative; color: white;">
            <div style="position: absolute; top: 20px; left: 20px; right: 20px; bottom: 20px; border: 1px solid rgba(255,255,255,0.1); pointer-events: none;"></div>
            
            <div style="width: 180px; height: 240px; background-image: url('{img_editor_b64}'); background-size: cover; background-position: center; margin-bottom: 30px; border: 1px solid #fff; filter: grayscale(100%);"></div>
            
            <div style="font-family: 'Montserrat', sans-serif; font-size: 11px; letter-spacing: 6px; text-transform: uppercase; color: #aaa; text-align: center;">El<br><br>Editor</div>
        </div>

        <div style="width: 60%; background-color: #fcfbf9; display: flex; flex-direction: column; justify-content: center; padding: 60px;">
            <div style="font-family: 'Montserrat', sans-serif; font-size: 13px; letter-spacing: 5px; text-transform: uppercase; color: #111; margin-bottom: 30px; border-bottom: 2px solid #111; padding-bottom: 10px; display: inline-block; align-self: flex-start;">Nota del editor</div>
            
            <div style="font-family: 'Playfair Display', serif; font-size: 18px; line-height: 2; font-style: italic; color: #333; margin-bottom: 40px;">
                {TEXTO_DEL_EDITOR}
            </div>
            
            <div onclick="document.getElementById('modal-regalo').style.display='flex'" style="cursor:pointer; border: 2px solid #111; padding: 20px; text-align: center; transition: all 0.3s ease; background: #fff;" onmouseover="this.style.background='#111'; this.style.color='#fff'; this.querySelector('.barcode').style.color='#fff'; this.querySelector('.ticket-title').style.color='#fff'; this.querySelector('.ticket-subtitle').style.color='#aaa';" onmouseout="this.style.background='#fff'; this.style.color='#111'; this.querySelector('.barcode').style.color='#111'; this.querySelector('.ticket-title').style.color='#111'; this.querySelector('.ticket-subtitle').style.color='#666';">
                <div class="ticket-title" style="font-family: 'Montserrat', sans-serif; letter-spacing: 3px; font-size: 12px; font-weight: 600; color: #111; transition: color 0.3s;">TICKET DE REGALO</div>
                <div class="barcode" style="font-family: 'Libre Barcode 39', cursive, sans-serif; font-size: 60px; margin: 10px 0 -10px 0; color: #111; transition: color 0.3s;">*BELEN*</div>
                <div class="ticket-subtitle" style="font-size: 10px; color: #666; font-family: 'Montserrat', sans-serif; letter-spacing: 1px; transition: color 0.3s;">CANJEAR SORPRESA</div>
            </div>

            <div style="margin-top: 40px; font-family: 'Montserrat', sans-serif; font-size: 11px; letter-spacing: 4px; text-transform: uppercase; color: #999; text-align: right;">
                - Tu mayor fan
            </div>
        </div>

        <div id="modal-regalo" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center; font-family: 'Montserrat', sans-serif;">
           <div style="background: #fdfcf9; border: 1px solid #d4cbb8; padding: 60px 50px; max-width: 550px; text-align: center; position: relative; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
               <div style="position: absolute; top: 5px; left: 5px; right: 5px; bottom: 5px; border: 1px solid #e8e4db; pointer-events: none;"></div>
               <span onclick="document.getElementById('modal-regalo').style.display='none'" style="position: absolute; top: 15px; right: 25px; font-size: 35px; cursor: pointer; color: #aaa; transition: color 0.2s;" onmouseover="this.style.color='#111'" onmouseout="this.style.color='#aaa'">&times;</span>
               
               <div style="font-family: 'Montserrat', sans-serif; font-size: 11px; letter-spacing: 5px; color: #888; text-transform: uppercase; margin-bottom: 20px;">Sorpresa Desbloqueada</div>
               <h2 style="font-family: 'Playfair Display', serif; font-size: 35px; margin-top: 0; margin-bottom: 25px; color: #111; font-style: italic;">Tu Regalo de este Mes</h2>
               
               <div style="width: 40px; height: 1px; background-color: #111; margin: 0 auto 30px auto;"></div>
               
               <div style="font-size: 16px; line-height: 1.8; color: #444; font-family: 'Montserrat', sans-serif;">{REGALO_DEL_MES}</div>
           </div>
        </div>
    </div>
    """

    html_completo = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Montserrat:wght@300;400;600&family=Libre+Barcode+39&display=swap');
    body {{ margin: 0; padding: 0; background-color: #ffffff; display: flex; justify-content: center; overflow-x: hidden; }}
    
    .aviso-movil {{ display: none; }}
    .revista-container {{ position: relative; width: 100%; max-width: 1700px; height: 1100px; display: flex; justify-content: center; background: #fff; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.1);}}
    
    .nav-zona {{ position: absolute; top: 0; bottom: 0; width: 150px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: rgba(0,0,0,0); font-size: 50px; transition: color 0.4s ease, background 0.4s ease; z-index: 100; user-select: none; }}
    .nav-zona.izq {{ left: 0; }} .nav-zona.der {{ right: 0; }}
    .nav-zona:hover {{ color: rgba(0,0,0,0.6); background: linear-gradient(90deg, rgba(0,0,0,0.05) 0%, rgba(255,255,255,0) 100%); }}
    .nav-zona.der:hover {{ background: linear-gradient(-90deg, rgba(0,0,0,0.05) 0%, rgba(255,255,255,0) 100%); }}
    
    .pagina {{ height: 1100px; box-sizing: border-box; }}
    .pagina.doble {{ width: 100%; display: flex; }}
    .pagina.simple {{ display: flex; }}

    .pagina-izq, .pagina-der {{ flex: 1; flex-basis: 50%; max-width: 50%; position: relative; box-sizing: border-box; overflow: hidden; }}
    .numero-pagina {{ position: absolute; bottom: 40px; font-family: 'Montserrat', sans-serif; font-size: 12px; letter-spacing: 2px;}}
    .np-izq {{ left: 80px; }} .np-der {{ right: 80px; }}
    .seccion-tag {{ font-family: 'Montserrat', sans-serif; font-size: 12px; letter-spacing: 4px; text-transform: uppercase; font-weight: 600;}}
    .hb-titulo-1 {{ font-family: 'Playfair Display', serif; font-size: 160px; font-style: italic; line-height: 0.7; margin: 80px 0 -50px 80px; z-index: 10; position: relative; }}
    .hb-titulo-2 {{ font-family: 'Playfair Display', serif; font-weight: 700; text-transform: uppercase; line-height: 0.9; letter-spacing: -2px; margin-top: 0; word-break: keep-all; overflow-wrap: break-word; hyphens: none; }}
    .hb-columnas {{ column-gap: 50px; font-family: 'Playfair Display', serif; font-size: 17px; line-height: 1.8; margin-top: 50px; text-align: justify; }}
    .hb-dropcap {{ float: left; font-size: 90px; line-height: 65px; padding-top: 8px; padding-right: 10px; font-style: italic; font-weight: 700; }}
    .linea-fina {{ width: 100%; height: 1px; background: currentColor; margin: 50px 0; opacity: 0.3; }}
    
    /* EL NUEVO ESCUDO PARA MÓVILES SÚPER PREMIUM */
    @media (max-width: 1000px) {{
        .revista-container {{ display: none !important; }}
        body {{ background-color: #050505; margin: 0; padding: 0; }}
        .aviso-movil {{ 
            display: flex; 
            width: 100vw; 
            height: 100vh; 
            background: radial-gradient(circle at center, #1c1c1c 0%, #050505 100%); 
            color: #fff; 
            justify-content: center; 
            align-items: center; 
            padding: 20px; 
            box-sizing: border-box; 
        }}
        .aviso-inner {{
            border: 1px solid rgba(255,255,255,0.07);
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 40px;
            box-sizing: border-box;
            background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0) 100%);
        }}
    }}
    </style>
    </head>
    <body>
        
        <!-- PANTALLA DE AVISO PARA MÓVILES REDISEÑADA -->
        <div class="aviso-movil">
            <div class="aviso-inner">
                <div style="font-size: 20px; color: #555; margin-bottom: 25px;">✧</div>
                <h1 style="font-family: 'Playfair Display', serif; font-style: italic; font-size: 55px; margin-bottom: 5px; font-weight: 400; color: #fdfcf9; letter-spacing: 1px;">Belen's Studio</h1>
                <div style="font-family: 'Montserrat', sans-serif; font-size: 10px; letter-spacing: 8px; color: #666; text-transform: uppercase; margin-bottom: 40px;">Private Atelier</div>
                
                <div style="width: 1px; height: 60px; background-color: rgba(255,255,255,0.15); margin: 0 auto 40px auto;"></div>
                
                <p style="font-family: 'Montserrat', sans-serif; font-size: 10px; letter-spacing: 4px; text-transform: uppercase; color: #999; line-height: 2;">La experiencia editorial<br>requiere una pantalla más grande.</p>
                <p style="font-family: 'Playfair Display', serif; font-size: 18px; font-style: italic; color: #666; margin-top: 25px;">Por favor, abre tu Atelier<br>en tu iPad o en el ordenador.</p>
            </div>
        </div>

        <div class="revista-container">
            <div id="btn-izq" class="nav-zona izq" onclick="cambiarPagina(-1)">&#10094;</div>
            <div id="btn-der" class="nav-zona der" onclick="cambiarPagina(1)">&#10095;</div>

            {html_portada}
            {html_paginas_interiores}
            {html_contraportada}
            
        </div>

        <script>
            let paginaActual = 0; const totalPaginas = {total_paginas}; 
            document.getElementById('btn-izq').style.display = 'none';
            function cambiarPagina(direccion) {{
                let nuevaPagina = paginaActual + direccion;
                if (nuevaPagina >= 0 && nuevaPagina < totalPaginas) {{
                    let elemActual = document.getElementById('pag-' + paginaActual);
                    let elemNuevo = document.getElementById('pag-' + nuevaPagina);
                    if(elemActual && elemNuevo) {{
                        elemActual.style.display = 'none';
                        paginaActual = nuevaPagina;
                        elemNuevo.style.display = 'flex';
                        document.getElementById('btn-izq').style.display = (paginaActual === 0) ? 'none' : 'flex';
                        document.getElementById('btn-der').style.display = (paginaActual === totalPaginas - 1) ? 'none' : 'flex';
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """

    components.html(html_completo, height=1150, scrolling=False)
