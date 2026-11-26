import os
import streamlit as st

def aplicar_identidad_acclaim():
    st.markdown("""
    <style>
        @import url('https://googleapis.com');
        html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background-color: transparent !important;}
        
        .banner-acclaim {
            background: linear-gradient(120deg, #BF0D3E 0%, #9E0932 100%);
            padding: 2rem 2.5rem;
            border-radius: 12px;
            color: #FFFFFF;
            margin-bottom: 1.5rem;
            box-shadow: 0 6px 20px rgba(191, 13, 62, 0.18);
            border-bottom: 4px solid #75787B;
        }
        .banner-acclaim h1 {
            color: #FFFFFF !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            margin: 0 0 0.35rem 0 !important;
        }
        .banner-acclaim p { color: #F3F4F6 !important; font-size: 1rem !important; margin: 0 !important; }
        .tagline-acclaim {
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 1px;
            color: rgba(255, 255, 255, 0.85);
            margin-top: 0.6rem;
        }
        .tarjeta-reporte {
            background-color: #FFFFFF;
            padding: 2rem 2.2rem;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            border-left: 5px solid #BF0D3E;
            box-shadow: 0 4px 12px rgba(117, 120, 123, 0.08);
            margin-top: 1rem;
            color: #33373B;
        }
        .tarjeta-reporte a { color: #BF0D3E !important; font-weight: 600; text-decoration: underline; }
        div.stButton > button[kind="primary"] {
            background-color: #BF0D3E;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 0.65rem 1.8rem;
            font-weight: 600;
        }
        div.stButton > button[kind="primary"]:hover { background-color: #9E0932; }
        div.stButton > button[kind="secondary"] {
            background-color: #FFFFFF;
            color: #33373B;
            border: 1px solid #75787B;
            border-radius: 8px;
        }
        div.stButton > button[kind="secondary"]:hover {
            border-color: #BF0D3E;
            color: #BF0D3E;
            background-color: #FFF5F7;
        }
    </style>
    """, unsafe_allow_html=True)

def mostrar_logo_sidebar():
    st.markdown('<div style="padding: 0.5rem 0.5rem 0.8rem 0.5rem; background-color: #FFFFFF; border-radius: 10px;">', unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
