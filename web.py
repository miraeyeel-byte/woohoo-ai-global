import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 정보 설정
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"
ADMIN_BALANCE = 100000000  # 운영자 코인 1억 개

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 2.0  # 일반 유저 첫 방문 보너스
if 'treasury' not in st.session_state:
    st.session_state.treasury = 0.0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

# 4. [디자인] 프리미엄 티타늄 블랙 & 골드 테마 (주사위 제외)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    
    .stApp { background-color: #000000 !important; }

    /* 전체 텍스트: 티타늄 화이트 & 선명한 음영 */
    html, body, [class*="st-"] {
        color: #F0F0F0 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 1) !important;
    }

    /* 금색 포인트 및 제목 */
    h1, h2, h3, .gold-text {
        color: #FFD700 !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.5) !important;
        font-weight: 900 !important;
    }

    /* 탭 디자인: 하이테크 블랙 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111111 !important;
        border: 1px solid #333 !important;
        color: #888 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFD700 !important;
        color: #000 !important;
    }

    /* 🎲 럭키 주사위 전용: 귀여운 네온 팝 아트 카드 (운영자님 요청) */
    .dice-card {
        background: #FFF5E1 !important;
        border: 8px solid #FF4B4B !important;
        border-radius: 30px !important;
        padding: 40px !important;
        text-align: center !important;
        box-shadow: 10px 10px 0px #FF4B4B !important;
        color: #000 !important;
    }
    .dice-num { font-size: 100px !important; color: #FF4B4B !important; margin: 0; font-family: 'Orbitron' !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. 상단 헤더
st.markdown("<h1 style='text-align: center; font-size: 55px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 6. 사이드바 - 지갑 센터 (운영자 1억 개 로직 포함)
with st.sidebar:
    st.markdown("### 🔑 ACCESS CONTROL")
    if not st.session_state.wallet_address:
        st.error("🔒 지갑을 연결해야 서비스가 활성화됩니다.")
        if st.button("CONNECT PHANTOM WALLET", use_container_width=True):
            # 연결 시점 지갑 주소 할당
            st.session_state.wallet_address = OWNER_WALLET # 실제 운영자 주소로 테스트
            
            # 운영자 주소일 경우 1억 개 코인 지급
            if st.session_state.wallet_address == OWNER_WALLET:
                st.session_state.balance = ADMIN_BALANCE
            st.rerun()
    else:
        is_owner = (st.session_state.wallet_address == OWNER_WALLET)
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">ADDRESS</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:12]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFF;">{st.session_state.balance:,.0f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if is_owner:
            st.warning("👑 MASTER ADMIN: 100M WH LOADED")
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.rerun()

# 7. 탭 메뉴 생성 (운영자면 관리자 탭 노출)
menu = ["📊 NETWORK", "🛠️ AI NODE", "🕹️ ARCADE", "🎲 LUCKY DICE"]
if st.session_state.wallet_address == OWNER_WALLET:
    menu.append("👑 ADMIN")

tabs = st.tabs(menu)

# --- TAB 1: NETWORK ---
with tabs[0]:
    if not st.session_state.wallet_address:
        st.warning("지갑을 연결하면 네트워크 데이터가 로드됩니다.")
    else:
        st.markdown("### 🌐 GLOBAL COMPUTE STATUS")
        st.write("WOOHOO AI는 전 세계 유휴 GPU 자원을 활용하는 탈중앙화 AI 연산 메인넷입니다.")
        c1, c2, c3 = st.columns(3)
        c1.metric("NETWORK POWER", "1.4 EH/s", "+12%")
        c2.metric("ACTIVE NODES", "12,842", "STABLE")
        c3.metric("REWARD RATE", "142% APY", "ELITE")
        st.line_chart(np.random.randn(20, 1), color=["#FFD700"])

# --- TAB 2: AI NODE ---
with tabs[1]:
    if not st.session_state.wallet_address:
        st.error("지갑 연결이 필요합니다.")
    else:
        st.markdown("### 🛠️ HYPER-FUSE NODE 관리")
        st.info("현재 마스터 장치가 연산 검증 노드로 작동 중입니다.")
        st.progress(95, text="GPU 연산 엔진 가동률 95%")
        st.write("- 연산 가동 시간: 1,420시간")
        st.write("- 누적 채굴 보상: 42,500 WH")

# --- TAB 3: ARCADE (닷지 게임 - 참가비 0.05 WH) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        st.warning("⚠️ 참가비: 0.05 WH (시작 시 지갑에서 자동 차감)")
        if not st.session_state.game_active:
            if st.button("🚀 MISSION START (0.05 WH)", use_container_width=True):
                if st.session_state.balance >= 0.05:
                    st.session_state.balance -= 0.05
                    st.session_state.treasury += 0.05
                    st.session_state.game_active = True
                    st.rerun()
                else: st.error("잔액이 부족합니다.")
        else:
            st.button("⏹️ RESET / EXIT", on_click=lambda: setattr(st.session_state, 'game_active', False))
            # 닷지 게임 로직 (생략 - 기존 유지)
            st.write("게임 화면 로딩 중... 마우스를 화면 중앙에 위치시키세요.")

# --- TAB 4: LUCKY DICE (운영자가 좋아한 귀여운 디자인) ---
with tabs[3]:
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        st.markdown("""
            <div class="dice-card">
                <h2 style="color:#000 !important;">🎰 럭키 주사위 🎰</h2>
                <p style="color:#333 !important; font-weight:bold;">당첨 기준: 5, 6 (1.9배 보상)</p>
        """, unsafe_allow_html=True)
        
        if 'last_res' in st.session_state:
            st.markdown(f'<p class="dice-num">{st.session_state.last_res}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="dice-num">🎲</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        bet = st.selectbox("배팅액 선택 (WH)", [1, 5, 10, 50, 100])
        if st.button("🔴 ROLL THE DICE!", use_container_width=True):
            if st.session_state.balance >= bet:
                st.session_state.balance -= bet
                st.session_state.treasury += bet
                res = random.randint(1, 6)
                st.session_state.last_res = res
                if res >= 5: # 밸런스 조정: 5, 6 당첨
                    win = bet * 1.9
                    st.session_state.balance += win
                    st.session_state.treasury -= win
                    st.balloons()
                st.rerun()
            else: st.error("코인이 부족해요! 😥")

# --- TAB 5: ADMIN ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.markdown("### 👑 MASTER TREASURY")
        col_ad1, col_ad2 = st.columns(2)
        with col_ad1:
            st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
            if st.button("수익금 지갑으로 회수"):
                st.session_state.balance += st.session_state.treasury
                st.session_state.treasury = 0
                st.success("수익금이 운영자 지갑으로 이동되었습니다.")
        with col_ad2:
            st.subheader("⚙️ 서버 설정")
            st.write("- 닷지 참가비: 0.05 WH")
            st.write("- 주사위 승률: 33.3%")
