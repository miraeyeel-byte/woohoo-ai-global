import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI GLOBAL", layout="wide")

# 2. 강제 블랙 & 골드 테마 디자인
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #E8C35E !important; }
    h1, h2, h3, p, span { color: #E8C35E !important; }
    
    /* 지표 박스 테두리 및 배경 */
    [data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 2px solid #E8C35E !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    
    /* 큰 버튼 디자인 */
    .stButton>button {
        background: linear-gradient(90deg, #E8C35E, #B8860B) !important;
        color: black !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 50px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_index=True)

# 3. 상단 제목
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_index=True)
st.write("---")

# 4. 델리시움 스타일 대시보드 (에러 수정된 부분!)
# 반드시 columns (복수형) 이어야 합니다.
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("SCANNER STATUS", "ACTIVE", "0.001ms")
with col2:
    st.metric("GLOBAL NODES", "2,405 EA", "+128")
with col3:
    st.metric("SECURITY LEVEL", "ELITE", "99.8%")

# 5. 분석 그래프
st.write("### 📊 Real-time Flow")
chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['AI', 'Network'])
st.line_chart(chart_data)

# 6. 기술력 과시 로그
st.code("""
[SYSTEM] SCANNING BLOCK #29481... DONE
[DETECT] $WOOHOO TOKEN VERIFIED: SAFE ✅
""", language='bash')

# 7. 버튼
if st.button("MINT FOUNDER NODE (2.0 SOL)"):
    st.balloons()
    st.success("SUCCESS!")

st.caption("© 2026 WOOHOO AI LABS")
