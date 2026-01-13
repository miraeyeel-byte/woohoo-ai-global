import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | HYPER-CORE", layout="wide")

# 2. 세션 상태 관리
if 'balance' not in st.session_state:
    st.session_state.balance = 1000
if 'free_spins' not in st.session_state:
    st.session_state.free_spins = 2

# 3. [디자인 수정] - 글자 깨짐 방지 및 가독성 최적화
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    
    .stApp { background-color: #000000 !important; }

    /* 기본 텍스트: 그림자를 1px로 줄여 깨짐 방지 */
    html, body, p, div, span {
        color: #FFFFFF !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    }

    /* 제목(H1, H2, H3): 여기만 강한 음영 효과 적용 */
    h1, h2, h3 {
        color: #FFD700 !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 1), 0 0 10px rgba(255, 215, 0, 0.3) !important;
        font-weight: 900 !important;
    }

    /* 코드 블록(깨짐 현상 주범): 그림자 완전히 제거 */
    code, pre {
        text-shadow: none !important;
        background-color: #1a1a1a !important;
        color: #00FF00 !important; /* 터미널 느낌의 초록색 */
    }

    /* 전광판 스타일 */
    .winner-board {
        background: #111;
        border-top: 2px solid #FFD700;
        border-bottom: 2px solid #FFD700;
        padding: 5px 0;
        margin: 10px 0;
    }

    /* 탭 메뉴 가시성 강화 */
    .stTabs [data-baseweb="tab"] {
        color: #888 !important;
        font-size: 16px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #FFD700 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 상단 헤더 & 전광판
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

st.markdown("""
    <div class="winner-board">
        <marquee scrollamount="8" style="color: #FFD700; font-weight: bold;">
            🎊 잭팟 소식: 0x...8a2님이 5,000 WH 당첨! &nbsp;&nbsp;&nbsp;&nbsp; 🚀 신규 방문자 무료 주사위 2회 제공 중! &nbsp;&nbsp;&nbsp;&nbsp; 💎 NODE SALE: TIER 1 진행 중 (74% 남음)
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# 5. 탭 브라우저
tab1, tab2, tab3 = st.tabs(["💎 NETWORK_CORE (네트워크)", "🎲 LUCKY GAME (게임)", "🛠️ TECH_SPEC (기술)"])

with tab1:
    st.markdown("### 🌐 제네시스 노드 에코시스템")
    c1, c2, c3 = st.columns(3)
    c1.metric("PRICE", "2.40 SOL")
    c2.metric("SOLD", "12,842 / 50K")
    c3.metric("APY", "142%")
    
    st.write("---")
    st.markdown("### 📊 실시간 연산량")
    st.line_chart(pd.DataFrame(np.random.randn(15, 2), columns=['AI', 'SEC']))

with tab2:
    st.markdown("<h2 style='text-align:center;'>🎲 로열 럭키 다이스</h2>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"#### 💰 잔액: `{st.session_state.balance} WH`")
    with col_b:
        st.markdown(f"#### 🎁 무료 기회: `{st.session_state.free_spins}회`")

    bet = st.selectbox("배팅액", [10, 100, 500, 1000])
    
    if st.button("주사위 굴리기 (SPIN)", use_container_width=True):
        if st.session_state.free_spins > 0 or st.session_state.balance >= bet:
            if st.session_state.free_spins > 0:
                st.session_state.free_spins -= 1
                st.toast("무료 기회 사용!")
            else:
                st.session_state.balance -= bet
            
            with st.spinner("운명 결정 중..."):
                time.sleep(0.5)
                res = random.randint(1, 100)
                if res <= 15:
                    win = bet * 10
                    st.session_state.balance += win
                    st.success(f"당첨! +{win} WH")
                else:
                    st.error("꽝! 다시 도전하세요.")
            st.rerun()
        else:
            st.error("잔액이 부족합니다.")

with tab3:
    st.markdown("### 🛠️ 하이퍼-퓨즈 아키텍처")
    st.code("""
// 핵심 프로토콜 명세 (Protocol Spec)
Node: Hyper-Fuse v2.4
Network: Solana Layer-3
Security: Atomic Compute Proof (ACP)
    """, language="javascript")
    st.write("깨짐 없는 깔끔한 폰트로 기술 문서를 확인하세요.")
