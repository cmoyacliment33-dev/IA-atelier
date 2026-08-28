import streamlit as st
import datetime
import random

def mostrar_buscador():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Montserrat:wght@300;400;600&display=swap');
        
        .inspiracion-container {
            background: linear-gradient(135deg, #fcfbf9 0%, #edeae3 100%);
            padding: 80px 40px;
            border-radius: 10px;
            box-shadow: inset 0 0 50px rgba(0,0,0,0.03), 0 20px 40px rgba(0,0,0,0.05);
            text-align: center;
            border: 1px solid #e0dcd3;
            margin-bottom: 50px;
        }

        .titulo-inspiracion {
            font-family: 'Playfair Display', serif;
            font-size: 55px;
            font-style: italic;
            font-weight: 700;
            color: #111;
            margin-bottom: 15px;
            letter-spacing: -1px;
        }
        
        .subtitulo-inspiracion {
            font-family: 'Montserrat', sans-serif;
            font-size: 13px;
            letter-spacing: 5px;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 50px;
        }
        
        .search-box {
            display: flex;
            gap: 15px;
            max-width: 700px;
            margin: 0 auto;
        }
        
        .search-input {
            flex: 1;
            padding: 20px 30px;
            border-radius: 3px;
            border: 1px solid #d4cbb8;
            font-family: 'Montserrat', sans-serif;
            font-size: 15px;
            background: #fff;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .search-input:focus {
            border: 1px solid #111;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        }
        
        .search-btn {
            padding: 20px 40px;
            background-color: #111;
            color: white;
            border: none;
            border-radius: 3px;
            font-weight: 600;
            cursor: pointer;
            font-family: 'Montserrat', sans-serif;
            font-size: 13px;
            letter-spacing: 3px;
            text-transform: uppercase;
            transition: all 0.3s ease;
        }
        
        .search-btn:hover {
            background-color: #333;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # HTML comprimido sin saltos de línea para que Streamlit no se rompa
    html_content = """<div class="inspiracion-container"><div class="titulo-inspiracion">Cazadora de Ideas</div><div class="subtitulo-inspiracion">Tu moodboard de alta costura a un clic</div><form class="search-box" action="https://www.pinterest.com/search/pins/" method="get" target="_blank"><input class="search-input" type="text" name="q" placeholder="Ej: Patronaje mangas globo, bordados vintage..."><button class="search-btn" type="submit">Inspirarme</button></form></div>"""
    
    st.markdown(html_content, unsafe_allow_html=True)

    # SUGERENCIAS DIARIAS
    st.markdown("<h3 style='font-family: \"Playfair Display\", serif; font-style: italic; color: #222; text-align: center; margin-bottom: 40px; font-size: 32px;'>Tendencias de Hoy</h3>", unsafe_allow_html=True)
    
    temas_totales = [
        "Patronaje Japonés", "Corsets modernos", "Vestidos fluidos", "Upcycling denim", 
        "Mangas abullonadas", "Moda victoriana estética", "Alta costura deconstruida", 
        "Lino minimalista", "Bordados botánicos", "Pantalones palazzo patronaje", 
        "Estética Cottagecore", "Diseño de lencería vintage", "Blazers oversize mujer", 
        "Técnica moulage costura", "Faldas asimétricas", "Chaquetas tweed", 
        "Patchwork creativo prendas", "Moda andrógina", "Siluetas años 50", 
        "Vestidos lenceros de seda", "Cuellos babero", "Transparencias y tul"
    ]

    hoy = datetime.date.today().toordinal()
    random.seed(hoy)
    sugerencias_hoy = random.sample(temas_totales, 5)
    random.seed() 

    cols = st.columns(5)
    for i, tema in enumerate(sugerencias_hoy):
        with cols[i]:
            url_pinterest = f"https://www.pinterest.com/search/pins/?q={tema.replace(' ', '%20')}"
            st.link_button(f"✨ {tema}", url_pinterest, use_container_width=True)

if __name__ == "__main__":
    mostrar_buscador()