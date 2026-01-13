import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | HYPER-CORE", layout="wide")

# 2. 운영자 지갑 주소
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 2.0
if 'sol_balance' not in st.session_state:
    st.session_state.sol_balance = 5.0 # 테스트용 기본 5 SOL 부여
if 'is_first_dice' not in st.session_state:
    st.session_state.is_first_dice = True # 첫 판 당첨용
if 'owned_nodes' not in st.session_state:
    st.session_state.owned_nodes = 0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

# 4. [디자인] 프리미엄 티타늄 & 골드 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] { color: #F0F0F0 !important; font-family: 'Noto Sans KR', sans-serif !important; text-shadow: 2px 2px 4px rgba(0, 0, 0, 1) !important; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron' !important; font-weight: 900 !important; }
    
    .dice-card {
        background: #FFF5E1 !important;
        border: 8px solid #FF4B4B !important;
        border-radius: 30px !important;
        padding: 40px !important;
        text-align: center;
        box-shadow: 10px 10px 0px #FF4B4B !important;
        color: #000 !important;
    }
    .dice-num { font-size: 100px !important; color: #FF4B4B !important; margin: 0; font-family: 'Orbitron' !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. 사이드바 - 지갑 & 잔액
with st.sidebar:
    st.markdown("### 🔑 WALLET CONNECT")
    if not st.session_state.wallet_address:
        if st.button("CONNECT PHANTOM", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            if st.session_state.wallet_address == OWNER_WALLET:
                st.session_state.balance = 100000000.0
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">ADDRESS</p>
                <p style="margin:0; font-size:13px; color:#FFD700;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">SOL BALANCE</p>
                <p style="margin:0; font-size:18px; font-weight:bold;">{st.session_state.sol_balance:.2f} SOL</p>
                <p style="margin:0; font-size:12px; color:#888; margin-top:10px;">WH BALANCE</p>
                <p style="margin:0; font-size:22px; font-weight:bold; color:#FFF;">{st.session_state.balance:,.0f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.rerun()

# 6. 메인 탭
tabs = st.tabs(["🌐 NETWORK", "🛠️ NODE SALE", "🕹️ ARCADE", "🎲 LUCKY DICE"])

# --- TAB 1: NETWORK ---
with tabs[0]:
    st.markdown("### 🌐 WOOHOO AI 가상 네트워크")
    st.line_chart(np.random.randn(20, 1), color=["#FFD700"])

# --- TAB 2: NODE SALE (실제 구매 로직) ---
with tabs[1]:
    st.markdown("### 🛠️ HYPER-FUSE 노드 라이선스 구매")
    st.write("노드를 소유하면 매일 WH 코인이 자동 채굴됩니다.")
    
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.image("https://img.icons8.com/neon/96/server.png")
        st.markdown("#### GENESIS NODE (Tier 1)")
        st.write("- 가격: **2.0 SOL**")
        st.write("- 채굴량: **50 WH / 일**")
        
        if st.button("MINT NODE (2.0 SOL)", use_container_width=True):
            if st.session_state.wallet_address:
                if st.session_state.sol_balance >= 2.0:
                    with st.spinner("솔라나 네트워크에서 트랜잭션 승인 중..."):
                        time.sleep(2)
                        st.session_state.sol_balance -= 2.0
                        st.session_state.owned_nodes += 1
                        st.balloons()
                        st.success("노드 구매 성공! 채굴을 시작합니다.")
                else: st.error("SOL 잔액이 부족합니다.")
            else: st.error("지갑을 먼저 연결하세요.")

    with col_n2:
        st.markdown("#### 📦 내 보유 자산")
        st.metric("보유 노드 수", f"{st.session_state.owned_nodes} 개")
        st.write(f"예상 일일 채굴량: {st.session_state.owned_nodes * 50} WH")

# --- TAB 3: ARCADE (생략) ---
with tabs[2]: st.write("닷지 게임 준비 중...")

# --- TAB 4: LUCKY DICE (첫 판 조작 로직 포함) ---
with tabs[3]:
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        st.markdown('<div class="dice-card">', unsafe_allow_html=True)
        st.markdown('<h3>🎰 LUCKY DICE 🎰</h3>', unsafe_allow_html=True)
        
        if 'last_res' in st.session_state:
            st.markdown(f'<p class="dice-num">{st.session_state.last_res}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="dice-num">🎲</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 최저가 1 WH 설정
        bet = st.select_slider("배팅액 선택 (WH)", options=[1, 5, 10, 50, 100, 500])
        
        if st.button("ROLL!", use_container_width=True):
            if st.session_state.balance >= bet:
                st.session_state.balance -= bet
                
                # [운영자 비밀 로직] 첫 판은 무조건 6!
                if st.session_state.is_first_dice:
                    res = 6
                    st.session_state.is_first_dice = False
                else:
                    res = random.randint(1, 6)
                
                st.session_state.last_res = res
                if res >= 5:
                    st.session_state.balance += (bet * 1.9)
                    st.balloons()
                st.rerun()
            else: st.error("잔액 부족!")
