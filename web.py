import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# 1. 페이지 엔진 설정
st.set_page_config(page_title="WOOHOO AI | HYPER-CORE", layout="wide")

# 2. 세션 상태 관리 (잔액 및 무료 기회)
if 'balance' not in st.session_state:
    st.session_state.balance = 1000
if 'free_spins' not in st.session_state:
    st.session_state.free_spins = 2  # 첫 방문 시 2회 무료 기회

# 3. [디자인] - 엠보싱 음영 및 시인성 강화 CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    
    .stApp { background-color: #000000 !important; }

    /* 글자 가독성: 다중 그림자로 강력한 음영 효과 */
    html, body, [class*="st-"] {
        color: #FFFFFF !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 
            2px 2px 2px #000,
            -1px -1px 0 #000,  
            1px -1px 0 #000,
            -1px 1px 0 #000,
            1px 1px 0 #000 !important;
    }

    /* 제목 및 골드 포인트 */
    h1, h2, h3, .gold-text {
        color: #FFD700 !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.7) !important;
    }

    /* 메인 전광판 스타일 */
    .winner-board {
        background: linear-gradient(90deg, #1a1a1a, #333, #1a1a1a);
        color: #FFD700;
        padding: 10px;
        border-top: 2px solid #FFD700;
        border-bottom: 2px solid #FFD700;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #111 !important;
        border-radius: 5px;
        color: #bbb !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFD700 !important;
        color: #000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 상단 헤더 & 실시간 당첨자 전광판 (메인 화면 배치)
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

st.markdown("""
    <div class="winner-board">
        <marquee scrollamount="10">
            🎊 축하합니다! 0x...a3ef 님이 주사위 잭팟으로 5,000 WH 획득! &nbsp;&nbsp;&nbsp;&nbsp; 
            🔥 현재 노드 세일 1단계 마감 임박! &nbsp;&nbsp;&nbsp;&nbsp; 
            💎 0x...77bb 님이 10배 당첨에 성공했습니다! &nbsp;&nbsp;&nbsp;&nbsp;
            🚀 신규 방문자 무료 기회 2회 제공 중!
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# 5. 탭 브라우저 (한글/영어 병기)
tab1, tab2, tab3 = st.tabs(["💎 네트워크 코어 (NETWORK_CORE)", "🎲 엔터테인먼트 (GAME)", "🛠️ 기술 명세 (TECH_SPEC)"])

# --- TAB 1: 메인 정보 ---
with tab1:
    st.markdown("### 🌐 제네시스 노드 에코시스템")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("현재가 (PRICE)", "2.40 SOL")
    with col2: st.metric("판매량 (SOLD)", "12,842 / 50K")
    with col3: st.metric("보상률 (APY)", "142%")

    st.write("---")
    st.markdown("### 📊 실시간 글로벌 연산력")
    chart_data = pd.DataFrame(np.random.randn(15, 2), columns=['AI SCAN', 'SECURITY'])
    st.line_chart(chart_data)

# --- TAB 2: 게임 센터 (무료 기회 로직 포함) ---
with tab2:
    st.markdown("<h2 style='text-align:center;'>🎲 로열 럭키 다이스 (LUCKY DICE)</h2>", unsafe_allow_html=True)
    
    # 지갑 상태 표시
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"#### 💰 내 잔액: `{st.session_state.balance} WH`")
    with c2:
        if st.session_state.free_spins > 0:
            st.markdown(f"#### 🎁 무료 기회: <span style='color:#FF4B4B;'>{st.session_state.free_spins}회 남음</span>", unsafe_allow_html=True)
        else:
            st.markdown("#### 🎁 무료 기회: `소진됨`")

    bet_val = st.selectbox("배팅액 선택 (BET AMOUNT)", [10, 100, 500, 1000])

    if st.button("주사위 굴리기 (ROLL THE DICE)", use_container_width=True):
        # 기회 체크
        can_play = False
        is_free = False
        
        if st.session_state.free_spins > 0:
            can_play = True
            is_free = True
        elif st.session_state.balance >= bet_val:
            can_play = True
            is_free = False
        
        if can_play:
            if is_free:
                st.session_state.free_spins -= 1
                st.toast("무료 기회를 사용합니다!")
            else:
                st.session_state.balance -= bet_val
            
            # 주사위 로직
            with st.spinner("결과 대기 중..."):
                time.sleep(0.5)
                res = random.randint(1, 100)
                if res <= 10: # 잭팟
                    win = bet_val * 100
                    st.session_state.balance += win
                    st.balloons()
                    st.success(f"🎊 대박! 100배 당첨! +{win} WH")
                elif res <= 40: # 일반 당첨
                    win = bet_val * 2
                    st.session_state.balance += win
                    st.info(f"승리! 2배 당첨! +{win} WH")
                else:
                    st.error("REKT! 다음 기회를 노리세요.")
            st.rerun()
        else:
            st.error("잔액이 부족합니다.")

# --- TAB 3: 기술 문서 ---
with tab3:
    st.markdown("### 🛠️ 하이퍼-퓨즈 아키텍처 (TECHNICAL)")
    st.code("""
// 핵심 프로토콜 명세
Protocol: Solana L3 Hybrid Integration
Node Type: Hyper-Fuse v2.4
Security: ACP (Atomic Compute Proof)
    """, language="javascript")
    st.write("전 세계 분산형 GPU 자원을 하나로 통합하여 초거대 언어 모델(LLM)을 최적화합니다.")

