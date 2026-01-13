import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# 1. 시스템 설정
st.set_page_config(page_title="WOOHOO AI | HYPER-CORE", layout="wide")

# 2. 잔액 관리
if 'balance' not in st.session_state:
    st.session_state.balance = 1000

# 3. [초프리미엄 디자인] 폰트 글로우 & 전광판 효과
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, p, div, span, label {
        color: #FFFFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
    }
    h1 { color: #FFD700 !important; text-align: center; text-shadow: 0 0 30px rgba(255, 215, 0, 0.8); letter-spacing: 5px; }
    
    /* 전광판 (FOMO Board) 디자인 */
    .fomo-board {
        background: rgba(255, 215, 0, 0.05);
        border: 1px solid #FFD700;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
    }
    .fomo-text {
        color: #FFD700 !important;
        font-size: 14px;
        text-align: center;
        animation: blink 2s infinite;
    }
    @keyframes blink { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

    /* 버튼 스타일 */
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #B8860B) !important;
        color: #000 !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        height: 70px;
        border-radius: 5px;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# 4. [조작된 전광판 데이터]
fake_wins = [
    "🔥 0x8f...e2 님이 100배 잭팟 (10,000 WH) 당첨!",
    "💎 0x1a...f9 님이 10배 중박 (1,000 WH) 당첨!",
    "⚡ 방금 전 익명의 홀더가 5,000 WH 보상을 수령했습니다.",
    "🔥 0x4d...2a 님이 주사위 6번으로 잭팟을 터뜨렸습니다!"
]

# 5. [게임 로직] 고배당 카지노
@st.dialog("⚠️ CONFIRM HIGH-STAKES BET")
def start_game(amount):
    st.markdown("<h3 style='color:#FF4B4B; text-align:center;'>ALL-IN 또는 대박?</h3>", unsafe_allow_html=True)
    st.write(f"배팅 수량: **{amount} WH** | 예상 최대 당첨금: **{amount * 100} WH**")
    st.write("---")
    
    if st.button("내 운명을 믿고 굴리기 (ROLL)"):
        st.session_state.balance -= amount
        with st.spinner("🎲 네트워크 스캐닝 중... 잭팟 확률 계산..."):
            time.sleep(1.2)
            res = random.randint(1, 100)
            
            if res <= 10: # 잭팟 100배 (사람들 미치게 만드는 구간)
                win = amount * 100
                st.session_state.balance += win
                st.markdown(f"<div style='border:3px solid #FFD700; padding:20px; text-align:center;'><h1>🎊 100배 잭팟! 🎊</h1><h2>+{win} WH</h2></div>", unsafe_allow_html=True)
            elif res <= 30: # 10배 (자주 터지는 느낌 주는 구간)
                win = amount * 10
                st.session_state.balance += win
                st.success(f"⚡ 대박! 10배 당첨! +{win} WH")
            else: # 70% 꽝
                st.error("REKT! 다음 기회를 노리세요.")
                st.write("운영 서버로 코인이 흡수되었습니다.")
        time.sleep(1.5)
        st.rerun()

# --- 화면 구성 ---
st.markdown("<h1>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 전광판 (포모 유도)
st.markdown(f"""<div class='fomo-board'><div class='fomo-text'>{random.choice(fake_wins)}</div></div>""", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1: st.metric("PRICE", "2.40 SOL")
with m2: st.metric("남은 노드", "12,842 / 50,000")
with m3: st.metric("내 코인", f"{st.session_state.balance} WH")

st.write("---")

# 카지노 구역
st.markdown("<h2 style='text-align:center;'>🎰 GENESIS ROYAL CASINO</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#FFD700;'>단 1%의 확률도 당신의 것이 될 수 있습니다.</p>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    bet = st.radio("배팅액", [10, 100, 500, 1000], horizontal=True)
with c2:
    st.write(" ")
    if st.button("SPIN & MINT"):
        if st.session_state.balance >= bet: start_game(bet)
        else: st.error("코인이 부족합니다!")

# 하단 정보
st.write("---")
st.code("> SYSTEM: FOMO_MODE_ACTIVATED\n> RECENT_WINS: UPDATING...\n> STATUS: 100x JACKPOT AVAILABLE", language="bash")
