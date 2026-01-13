import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 정보
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리 (첫 방문 보너스 로직 포함)
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True
    st.session_state.balance = 2.0  # [업데이트] 첫 방문 시 2 WH 지급
else:
    if 'balance' not in st.session_state:
        st.session_state.balance = 0.0

if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'treasury' not in st.session_state:
    st.session_state.treasury = 0.0  # 유저들이 잃은 코인이 쌓이는 금고
if 'burn_mode' not in st.session_state:
    st.session_state.burn_mode = False

# 4. [디자인] 한국어 가독성 및 귀여운 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;900&display=swap');
    .stApp { background-color: #050505 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3 { font-family: 'Jua', sans-serif !important; color: #FFD700 !important; }
    
    /* 주사위 카드 디자인 */
    .dice-board {
        background: #FFF5E1;
        border: 8px solid #FF4B4B;
        border-radius: 30px;
        padding: 40px;
        text-align: center;
        box-shadow: 10px 10px 0px #FF4B4B;
        margin: 20px 0;
    }
    .dice-num { font-size: 100px !important; color: #FF4B4B !important; font-family: 'Jua' !important; margin: 0; }
    .dice-info { color: #333 !important; font-weight: bold; font-size: 18px; margin: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 5. 상단 헤더
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 6. 사이드바 - 지갑 센터
with st.sidebar:
    st.markdown("### 🔑 지갑 센터")
    if not st.session_state.wallet_address:
        if st.button("내 지갑 연결 (Phantom)", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.rerun()
    else:
        is_owner = (st.session_state.wallet_address == OWNER_WALLET)
        st.markdown(f"""
            <div style="background:#1a1a1a; padding:15px; border-radius:15px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">접속 중인 주소</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:12]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">내 보유 코인</p>
                <p style="margin:0; font-size:24px; font-weight:bold;">{st.session_state.balance:,.2f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if is_owner: st.warning("👑 마스터 권한 접속 중")
        if st.button("연결 해제"):
            st.session_state.wallet_address = None
            st.rerun()

# 7. 탭 메뉴
tabs_list = ["📊 네트워크 현황", "🛠️ AI 노드", "🕹️ 닷지 게임", "🎲 럭키 주사위"]
if st.session_state.wallet_address == OWNER_WALLET:
    tabs_list.append("👑 운영 제어")
tabs = st.tabs(tabs_list)

# --- 탭 1: 네트워크 현황 ---
with tabs[0]:
    st.subheader("🌐 프로젝트 비전")
    st.write("WOOHOO AI는 전 세계의 GPU 연산력을 하나로 묶어 거대 AI 모델을 구동하는 탈중앙화 에너지 토큰입니다.")
    st.line_chart(np.random.randn(20, 1))

# --- 탭 2: AI 노드 ---
with tabs[1]:
    st.subheader("🛠️ 연산 노드 채굴")
    st.info("컴퓨터 자원을 빌려주고 실시간으로 WH 코인을 보상받으세요.")
    st.progress(70, text="시스템 최적화 중 (70%)")

# --- 탭 3: 닷지 게임 (참가비 0.05 WH 수정) ---
with tabs[2]:
    st.markdown("### 🕹️ 닷지 생존 미션")
    st.warning("⚠️ 게임 시작 시 **참가비 0.05 WH**가 차감됩니다.")
    
    diff = st.radio("난이도 설정", ["초보 (10초당 0.05)", "중급 (10초당 0.1)", "상급 (10초당 1.0)"], horizontal=True)

    if st.button("🚀 게임 시작 (START)"):
        if st.session_state.balance >= 0.05:
            st.session_state.balance -= 0.05
            if st.session_state.burn_mode:
                # 소각 모드면 금고에 넣지 않고 그냥 소진 (공급량 감소 효과)
                pass
            else:
                # 수거 모드면 운영자 금고로 이동
                st.session_state.treasury += 0.05
            st.success("게임을 시작합니다! 마우스로 총알을 피하세요!")
            # 게임 실행 로직 생략(기존 유지)

# --- 탭 4: 럭키 주사위 (디자인 & 확률 밸런스) ---
with tabs[3]:
    st.markdown("### 🎲 럭키 주사위 (귀여운 카지노)")
    
    st.markdown("""
        <div class="dice-board">
            <p class="dice-info">🎰 주사위 눈 <b>5, 6</b>이 나오면 당첨! 🎰</p>
            <p class="dice-info" style="font-size:14px; color:#FF4B4B;">(보상: 배팅액의 1.9배 지급)</p>
    """, unsafe_allow_html=True)
    
    if 'last_res' in st.session_state:
        st.markdown(f'<p class="dice-num">{st.session_state.last_res}</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="dice-num">?</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    bet = st.selectbox("배팅액 선택", [1, 5, 10, 50, 100])
    
    if st.button("🎲 주사위 던지기!!", use_container_width=True):
        if st.session_state.balance >= bet:
            st.session_state.balance -= bet
            # 유저가 낸 돈은 일단 운영자 수익으로 처리
            if not st.session_state.burn_mode:
                st.session_state.treasury += bet
            
            res = random.randint(1, 6)
            st.session_state.last_res = res
            
            if res >= 5: # 5, 6만 당첨
                win_amt = bet * 1.9
                st.session_state.balance += win_amt
                if not st.session_state.burn_mode:
                    st.session_state.treasury -= win_amt
                st.balloons()
                st.success(f"🎊 당첨되었습니다! {win_amt} WH 획득!")
            else:
                st.error("아쉽네요! 꽝입니다.")
            st.rerun()
        else:
            st.error("코인이 부족합니다.")

# --- 탭 5: 운영 제어 (운영자 전용) ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.markdown("## 👑 마스터 운영 대시보드")
        
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            st.subheader("💰 하우스 누적 수익")
            st.title(f"{st.session_state.treasury:,.2f} WH")
            
            mode = st.toggle("🔥 코인 소각 모드 (Burn Mode)", value=st.session_state.burn_mode)
            st.session_state.burn_mode = mode
            if mode:
                st.info("현재 유저가 잃은 코인은 즉시 소각되어 가치가 상승합니다.")
            else:
                st.success("현재 유저가 잃은 코인은 운영자 금고로 수거됩니다.")
                
            if st.button("금고 수익금을 내 지갑으로 수령"):
                st.session_state.balance += st.session_state.treasury
                st.session_state.treasury = 0
                st.success("전액 수령 완료!")

        with col_adm2:
            st.subheader("⚙️ 밸런스 조정")
            st.write("- 닷지 참가비: **0.05 WH**")
            st.write("- 주사위 승률: **33.3% (5, 6 당첨)**")
            st.write("- 주사위 배당: **1.9배**")
