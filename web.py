import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 엔진 설정
st.set_page_config(page_title="WOOHOO AI | NODE SALE", layout="wide")

# 2. [디자인] 글씨를 하얗고 선명하게 + 델리시움 감성
st.markdown("""
    <style>
    /* 전체 배경: 깊은 블랙 */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* 기본 글씨: 무조건 순백색 (#FFFFFF) */
    html, body, p, div, span {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }

    /* 제목: 강렬한 네온 골드 */
    h1 {
        color: #FFD700 !important;
        text-align: center;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }

    /* 지표 박스: 하얀 글씨와 황금색 테두리 */
    [data-testid="stMetric"] {
        background: #0a0a0a !important;
        border: 1px solid #FFD700 !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important; /* 숫자는 하얗게 */
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #FFD700 !important; /* 라벨은 황금색 */
    }

    /* 버튼: 소닉 스타일 그라데이션 */
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #B8860B) !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 20px !important;
        border-radius: 10px;
        height: 60px;
        width: 100%;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 상단 헤더 (무엇을 파는지 명시)
st.markdown("<h1>⚡ WOOHOO AI GENESIS NODE SALE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:20px;'>수천조 규모의 AI 네트워크, 그 주인이 될 기회</p>", unsafe_allow_html=True)
st.write("---")

# 4. 실시간 노드 판매 현황 (핵심 정보)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("판매 가격", "2.40 SOL", "TIER 01")
with col2:
    st.metric("남은 수량", "12,842 / 50,000", "🔥 마감 임박")
with col3:
    st.metric("예상 수익률", "142.5% APY", "VIP 보상")

# 5. 시각적 신뢰감 (네트워크 상태)
st.write(" ")
st.markdown("### 📊 GLOBAL NETWORK LIVE FLOW")
# 차트 데이터 (간결하게)
df = pd.DataFrame(np.random.randn(20, 1), columns=['Network Power'])
st.area_chart(df, color="#FFD700")

# 6. 기술력 증명 (해커 스타일 로그)
st.write("---")
st.markdown("#### 📡 REAL-TIME SYSTEM LOG")
st.code("""
> [SYSTEM] SOLANA NODE V2.4 INITIALIZED
> [INFO] SECURE CHANNEL ESTABLISHED... OK
> [SCAN] 128 NEW NODES ACTIVATED IN LAST 1 HOUR
> [STATUS] READY FOR MINTING
""", language="bash")

# 7. 구매 버튼 (가장 크게)
st.write(" ")
if st.button("지금 바로 노드 구매하기 (MINT NODE)"):
    st.balloons()
    st.success("지갑 연결 중... 잠시만 기다려 주십시오.")

# 8. 푸터
st.write("---")
st.caption("© 2026 WOOHOO AI GLOBAL | 본 사이트는 투자 유치를 위한 공식 세일즈 페이지입니다.")
