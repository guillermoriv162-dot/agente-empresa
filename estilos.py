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
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        <svg width="64" height="64" viewBox="0 0 100 100" xmlns="http://w3.org">
            <path d="M50 10 C72 10 88 26 90 48 C80 30 64 22 45 24 C47 18 48 14 50 10 Z" fill="#75787B"/>
            <path d="M90 55 C85 77 67 90 45 90 C63 82 74 68 75 49 C80 51 85 53 90 55 Z" fill="#75787B"/>
            <path d="M40 88 C20 80 10 60 15 38 C20 57 32 70 50 74 C46 79 43 84 40 88 Z" fill="#75787B"/>
            <path d="M50 32 C62 42 66 56 60 66 C48 68 38 64 34 54 C38 42 44 35 50 32 Z" fill="#BF0D3E"/>
        </svg>
        <div style="font-size: 1.35rem; font-weight: 700; color: #BF0D3E; margin-top: 0.2rem;">acclaim</div>
        <div style="font-size: 0.65rem; font-weight: 600; color: #75787B; letter-spacing: 2px;">ENERGY ADVISORS</div>
    </div>
    """, unsafe_allow_html=True)
