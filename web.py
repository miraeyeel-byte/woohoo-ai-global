import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# 1. 페이지 엔진 설정
st.set_page_config(page_title="WOOHOO AI | HYPER-CORE", layout="wide")

# 2. 잔액 관리 (세션)
if 'balance' not in st.session_state:
    st.session_state.balance = 1000

# 3. [초프리미엄 디자인] - 티타늄 화이트 & 엠보싱 음영
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;700&display=swap');
    
    .stApp { background-color: #000000 !important; }

    /* [핵심] 티타늄 화이트 글씨 + 선명한 블랙 쉐도우 (가독성 끝판왕) */
    html, body, p, div, span, label {
        color: #F0F0F0 !important;
        font-family: 'Inter', sans-serif !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 1); /* 날카로운 음영으로 글씨를 띄움 */
    }

    /* 금색 제목 및 포인트 */
    h1, h2, .gold-text {
        color: #FFD700 !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
        font-weight: 900 !important;
    }

    /* 탭(Tab) 디자인 커스텀 - 소닉 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #111111 !important;
        border: 1px solid #333 !important;
        border-radius: 10px 10px 0 0;
        color: #888 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFD700 !important;
        color: #000 !important;
        font-weight: bold !important;
    }

    /* 메트릭 카드: 델리시움 글래스모피즘 */
    [data-testid="stMetric"] {
        background: rgba(20, 20, 20, 0.7) !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 상단 고정 헤더
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.write(" ")

# 5. [메인 시스템] 탭 브라우저 생성
tab1, tab2, tab3 = st.tabs(["💎 NETWORK_CORE", "🎲 ENTERTAINMENT", "🛠️ TECHNICAL_SPEC"])

# --- TAB 1: 프로젝트 정보 & 노드 세일 (신뢰도 중심) ---
with tab1:
    st.markdown("## 🌐 GENESIS NODE ECOSYSTEM")
    st.write("WOOHOO AI는 솔라나 기반의 분산형 지능 네트워크입니다. 하이퍼-퓨즈 노드는 이 거대한 신경망의 연산 장치입니다.")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("CURRENT PRICE", "2.40 SOL", "TIER 01")
    with col2: st.metric("SOLD COUNT", "12,842 / 50K", "74% REMAINING")
    with col3: st.metric("REWARD RATE", "142% APY", "ELITE")

    st.write("---")
    st.markdown("### 📊 GLOBAL COMPUTE POWER (LIVE)")
    df = pd.DataFrame(np.random.randn(20, 2), columns=['AI_SCAN', 'SECURITY'])
    st.line_chart(df, color=["#FFD700", "#FFFFFF"])

    if st.button(">>> INITIALIZE NODE MINT (2.0 SOL) <<<", use_container_width=True):
        st.success("WALLET CONNECTED: MINTING PROCESS STARTING...")

# --- TAB 2: 게임 센터 (사장님이 원하신 도박장 분리) ---
with tab2:
    st.markdown("<h2 style='text-align:center;'>🎲 ROYAL LUCKY DICE</h2>", unsafe_allow_html=True)
    
    # FOMO 보드 (게임 탭에만 노출)
    st.markdown("""<div style='background:#111; border:1px solid #FFD700; padding:10px; border-radius:10px; text-align:center; color:#FFD700;'>
        🔥 [RECENT] 0x8f...e2 님이 주사위 6번으로 100배 잭팟 (10,000 WH) 당첨!
    </div>""", unsafe_allow_html=True)
    
    st.write(" ")
    g_col1, g_col2 = st.columns([1, 1])
    with g_col1:
        st.markdown(f"### 💰 YOUR WALLET: **{st.session_state.balance} WH**")
        bet_val = st.radio("배팅액 선택", [10, 100, 500, 1000], horizontal=True)
    
    with g_col2:
        st.write(" ")
        if st.button("ROLL THE DICE (SPIN)"):
            if st.session_state.balance >= bet_val:
                st.session_state.balance -= bet_val
                # 확률 로직: 사장님 수익 70%
                res = random.randint(1, 100)
                if res <= 10: # 100배 잭팟
                    win = bet_val * 100
                    st.session_state.balance += win
                    st.success(f"🏆 100배 잭팟!! +{win} WH!")
                elif res <= 30: # 10배
                    win = bet_val * 10
                    st.session_state.balance += win
                    st.info(f"승리! 10배 당첨! +{win} WH")
                else: # 꽝
                    st.error("REKT! 다음 기회를 노리세요.")
                st.rerun()
            else:
                st.error("코인이 부족합니다! CORE 탭에서 노드를 구매하세요.")

# --- TAB 3: 기술 문서 (전문성 강화) ---
with tab3:
    st.markdown("## 🛠️ HYPER-FUSE ARCHITECTURE")
    st.code("""
> Solana SVM Layer-3 Integration
> Atomic Compute Proof (ACP) Protocol v2.4
> Real-time Neural Scanning Engine
> Decentralized GPU-Node Clustering
    """, language="bash")
    st.write("하이퍼-퓨즈 노드는 전 세계에 흩어진 GPU 자원을 하나로 묶어 초거대 AI 모델을 구동합니다.")
