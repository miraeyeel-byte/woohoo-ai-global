import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | NODE & CASINO", layout="wide")

# 2. 잔액 관리
if 'balance' not in st.session_state:
    st.session_state.balance = 1000

# 3. 디자인 (네온 글씨 + 팝업 스타일 커스텀)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="css"] { font-family: 'Orbitron', sans-serif !important; color: #FFFFFF !important; }
    
    /* 팝업창 내부 스타일 */
    div[data-testid="stDialog"] {
        background-color: #050505 !important;
        border: 2px solid #FFD700 !important;
        border-radius: 20px !important;
    }

    /* 버튼 디자인 */
    .stButton>button {
        background: #FFD700 !important;
        color: #000 !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        height: 60px;
        width: 100%;
        border-radius: 10px;
    }
    
    .warning-text {
        color: #FF4B4B !important;
        text-align: center;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 75, 75, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# 4. [중요] 게임 실행 로직 (팝업창 함수)
@st.dialog("⚠️ RISK WARNING")
def confirm_bet(amount):
    st.markdown(f"<h2 class='warning-text'>주의: {amount} WH를 배팅하시겠습니까?</h2>", unsafe_allow_html=True)
    st.write("본 게임은 확률형 시스템으로 운영됩니다. 배팅하신 코인을 모두 잃으실 수도 있습니다. 시스템은 결과에 대해 책임지지 않습니다.")
    st.write("---")
    
    if st.button("확인 (I ACCEPT THE RISK)"):
        st.session_state.balance -= amount
        
        # 긴장감 연출
        placeholder = st.empty()
        with placeholder.container():
            st.write("🎲 네트워크 스캐닝 중...")
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
        
        # 확률 로직 (사장님 수익 70%)
        res = random.randint(1, 100)
        
        if res <= 10: # 잭팟 (5배)
            win = amount * 5
            st.session_state.balance += win
            st.success(f"🏆 JACKPOT! +{win} WH 획득!")
            st.toast("YOU ARE THE WINNER!")
        elif res <= 30: # 소액 승리 (1.5배)
            win = int(amount * 1.5)
            st.session_state.balance += win
            st.info(f"WIN! +{win} WH 획득!")
        else: # 70% 꽝
            st.error(f"REKT! -{amount} WH 손실.")
            st.write("운영진이 코인을 흡수했습니다.")
        
        time.sleep(2)
        st.rerun()

# --- 메인 화면 구성 ---
st.markdown("<h1 style='color:#FFD700; text-align:center;'>⚡ WOOHOO AI CORE</h1>", unsafe_allow_html=
