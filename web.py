import streamlit as st
import pandas as pd
import numpy as np
import random

# 1. 페이지 엔진 설정
st.set_page_config(page_title="WOOHOO AI | NODE & GAME", layout="wide")

# 2. [세션 상태] 게임을 위한 코인 잔액 초기화 (새로고침 전까지 유지)
if 'balance' not in st.session_state:
    st.session_state.balance = 1000  # 처음 들어오면 1000개 서비스

# 3. [디자인] 네온 글로우 + 게임 UI
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    
    /* 흰색 글씨 음영 효과 */
    html, body, p, div, span, label {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
    }
    h1 {
        color: #FFD700 !important;
        text-align: center;
        text-shadow: 0 0 25px rgba(255, 215, 0, 0.7);
    }
    
    /* 게임판 디자인 */
    .game-container {
        background: rgba(30, 30, 30, 0.5);
        border: 2px dashed #FFD700;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-top: 50px;
    }
    
    /* 지표 박스 */
    [data-testid="stMetric"] {
        background: rgba(20, 20, 20, 0.8) !important;
        border: 1px solid #FFD700 !important;
        border-radius: 15px !important;
    }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 900 !important; text-shadow: 0 0 15px rgba(255, 255, 255, 0.8); }

    /* 버튼 스타일 */
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #B8860B) !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 10px;
        height: 50px;
        width: 100%;
        border: none;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 상단 노드 세일즈 파트 (기존 유지) ---
st.markdown("<h1>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1: st.metric("판매 가격", "2.40 SOL", "TIER 01")
with col2: st.metric("남은 수량", "12,842 / 50,000", "🔥 마감")
with col3: st.metric("보유 코인", f"{st.session_state.balance} WH", "MY WALLET")

st.write("---")

# --- 하단 주사위 게임 파트 (사장님 요청 사항) ---
st.markdown("<h2 style='text-align:center; color:#FFD700;'>🎲 WOOHOO LUCKY DICE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>10배 잭팟에 도전하세요! (10개 걸면 100개 지급)</p>", unsafe_allow_html=True)

# 게임판 레이아웃
game_col1, game_col2 = st.columns([1, 1])

with game_col1:
    bet_amount = st.number_input("배팅할 코인 수량을 입력하세요", min_value=10, max_value=st.session_state.balance, value=10, step=10)
    
with game_col2:
    st.write(" ") # 줄맞춤
    if st.button("🎲 주사위 굴리기 (ROLL)"):
        if st.session_state.balance >= bet_amount:
            # 주사위 로직
            dice_result = random.randint(1, 6)
            st.session_state.balance -= bet_amount # 일단 배팅액 차감
            
            st.write(f"### 결과: {dice_result}이(가) 나왔습니다!")
            
            if dice_result == 6: # 잭팟 (10배)
                win_amt = bet_amount * 10
                st.session_state.balance += win_amt
                st.balloons()
                st.success(f"🎊 대박!! 잭팟 터졌습니다! {win_amt}개 획득!")
            elif dice_result >= 4: # 본전 (1배)
                st.session_state.balance += bet_amount
                st.info(f"운이 좋으시네요! 본전입니다. {bet_amount}개 복구!")
            else: # 반타작 (0.5배)
                loss_amt = bet_amount // 2
                st.session_state.balance += loss_amt
                st.warning(f"아쉽습니다! 반타작... {loss_amt}개만 돌아옵니다.")
        else:
            st.error("코인이 부족합니다!")

# 현재 잔액 실시간 업데이트를 위한 리런
st.write(f"### 💰 현재 보유 잔액: {st.session_state.balance} WH")

# --- 하단 터미널 로그 ---
st.write("---")
st.code("""
> [GAME_ENGINE] INITIALIZING RANDOM_SEED... OK
> [WALLET] BALANCE CHECKED: SUCCESS
> [STATUS] READY FOR NEXT BET
""", language="bash")
