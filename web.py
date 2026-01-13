import streamlit as st
import pandas as pd
import numpy as np
import time

# 1. 페이지 엔진 설정
st.set_page_config(page_title="WOOHOO AI | NODE SALE", layout="wide", initial_sidebar_state="collapsed")

# 2. [초고성능 디자인] 델리시움 & 소닉 하이브리드 스타일
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');

    /* 전체 배경: 칠흑 같은 블랙 & 유리 질감 */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a00, #000000 50%) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* 타이틀: 소닉 스타일의 네온 골드 글래스 */
    .main-header {
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        font-size: 4rem;
        text-align: center;
        background: linear-gradient(to right, #FFD700, #FFFACD, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(255, 215, 0, 0.5));
        margin-bottom: 0px;
    }

    /* 델리시움 스타일의 프리미엄 카드 */
    [data-testid="stMetric"] {
        background: rgba(15, 15, 15, 0.8) !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.4s ease;
    }
    [data-testid="stMetric"]:hover {
        border: 1px solid #FFD700 !important;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
        transform: translateY(-10px);
    }

    /* 노드 구매 버튼: 압도적인 광채 */
    .stButton>button {
        background: linear-gradient(90deg, #000, #FFD700, #000);
        background-size: 200% auto;
        color: white !important;
        border: 1px solid #FFD700;
        border-radius: 50px;
        padding: 20px;
        font-size: 1.8rem !important;
        font-family: 'Syncopate', sans-serif;
        transition: 0.5s;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    .stButton>button:hover {
        background-position: right center;
        box-shadow: 0 0 50px rgba(255, 215, 0, 0.8);
        color: #000 !important;
        font-weight: bold;
    }

    /* 진행 바 스타일 (노드 판매 현황) */
    .stProgress > div > div > div > div {
        background-color: #FFD700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. [상단 비주얼]
st.markdown("<h1 class='main-header'>HYPER-FUSE NODE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888; letter-spacing:5px;'>SOLANA SVM GENESIS EDITION</p>", unsafe_allow_html=True)

st.write(" ")
st.write("---")

# 4. [노드 상태 정보] - 델리시움 레이아웃
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("CURRENT PRICE", "2.40 SOL", "TIER 03")
with c2:
    st.metric("TOTAL SOLD", "12,842 / 50,000", "ACTIVE")
with c3:
    st.metric("EST. REWARDS", "142% APY", "BOOSTED")

# 5. [실시간 판매 현황] - 소닉 노드 사이트 감성
st.write(" ")
st.markdown("### ⚡ NODE SALE PROGRESS")
progress = 12842 / 50000
st.progress(progress)
st.markdown(f"<p style='text-align:right; color:#FFD700;'>{progress*100:.1f}% ALLOCATED</p>", unsafe_allow_html=True)

# 6. [중앙 영역] - 실시간 그래프와 터미널
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("#### 📊 GLOBAL NETWORK LATENCY")
    chart_data = pd.DataFrame(np.random.randn(40, 1), columns=['ms'])
    st.area_chart(chart_data, color="#FFD700")

with col_right:
    st.markdown("#### 📡 LIVE SCANNER")
    # 터미널 느낌의 로그박스
    st.code("""
> Connecting to RPC...
> Block #2918 verified.
> Node #8821 minted.
> Security: 100%
> Target: Global
    """, language="bash")

# 7. [핵심] 노드 민팅 버튼
st.write(" ")
st.write(" ")
if st.button("MINT YOUR FOUNDER NODE"):
    st.balloons()
    st.toast("Initializing Wallet Connection...")
    time.sleep(1)
    st.success("SUCCESS: YOUR SEAT IN THE FUTURE IS RESERVED.")

# 8. [하단 혜택 설명]
st.write("---")
cols = st.columns(4)
benefits = ["Airdrop Access", "Governance Power", "Revenue Share", "Early Beta"]
for i, col in enumerate(cols):
    col.markdown(f"<div style='text-align:center; padding:10px; border:1px solid #333; border-radius:10px;'>{benefits[i]}</div>", unsafe_allow_html=True)

st.write(" ")
st.caption("© 2026 WOOHOO AI GLOBAL | POWERED BY SOLANA ATOMIC SVM")
