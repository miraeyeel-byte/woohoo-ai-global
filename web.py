import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go  # 강제 컬러링을 위한 강력한 차트 도구

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO CORE", layout="wide")

# 2. [핵심] CSS로 폰트와 배경 강제 주입
st.markdown("""
    <style>
    /* 전체 배경 무조건 리얼 블랙 */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* 모든 폰트를 해커 스타일(타자기체)로 강제 변경 */
    html, body, p, h1, h2, h3, div, span, button {
        font-family: 'Courier New', Courier, monospace !important;
        color: #E8C35E !important;
    }
    
    /* 숫자 박스 디자인 */
    [data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #E8C35E !important;
        box-shadow: 0 0 10px rgba(232, 195, 94, 0.2);
    }
    
    /* 버튼 디자인 */
    .stButton>button {
        background-color: #E8C35E !important;
        color: #000000 !important;
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더
st.title("⚡ WOOHOO_AI_CORE")
st.write("Target: SOLANA_MAINNET | Status: MONITORING...")
st.write("---")

# 4. 대시보드
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("SCANNER", "ACTIVE", "0.001ms")
with c2:
    st.metric("NODES", "2,405", "+128")
with c3:
    st.metric("CONFIDENCE", "99.9
