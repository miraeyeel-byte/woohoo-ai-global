import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | HYPER-CORE", layout="wide")

# 2. 운영자 지갑 주소 (이 주소로 연결되면 1억 코인 지급)
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 2.0  # 신규 유저 보너스

# 4. [중요] 진짜 팬텀 지갑 연동을 위한 자바스크립트 브리지
def wallet_bridge():
    # 이 스크립트가 브라우저에서 실행되어 팬텀 지갑을 깨웁니다.
    js_code = """
    <script>
    async function connectWallet() {
        if ("solana" in window) {
            try {
                const resp = await window.solana.connect();
                const address = resp.publicKey.toString();
                // 파이썬(Streamlit)으로 주소를 전송합니다.
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: address
                }, '*');
            } catch (err) {
                console.error("연결 거부됨", err);
            }
        } else {
            alert("팬텀 지갑을 설치해주세요!");
            window.open("https://phantom.app/", "_blank");
        }
    }
    </script>
    <button onclick="connectWallet()" style="
        width: 100%;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: black;
        border: none;
        padding: 12px;
        border-radius: 10px;
        font-weight: bold;
        cursor: pointer;
        font-family: sans-serif;
    "> 🦊 PHANTOM 지갑 연결 </button>
    """
    # 콤포넌트를 통해 버튼 렌더링 및 값 수신
    return components.html(js_code, height=60)

# 5. 디자인 (기존 프리미엄 테마 유지)
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron', sans-serif !important; }
    /* 주사위 네온 카드 */
    .dice-card {
        background: #FFF5E1 !important;
        border: 8px solid #FF4B4B !important;
        border-radius: 30px !important;
        padding: 30px !important;
        text-align: center;
        box-shadow: 10px 10px 0px #FF4B4B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 6. 상단 헤더 & 전광판
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 7. 사이드바 - 진짜 지갑 연동 섹션
with st.sidebar:
    st.markdown("### 🔑 REAL-TIME ACCESS")
    
    if not st.session_state.wallet_address:
        # 진짜 지갑 연결 버튼 실행
        addr = wallet_bridge()
        
        # 버튼을 통해 주소가 들어왔는지 확인 (Streamlit 콤포넌트 특성상 더미 값 체크 필요)
        # 실제 운영 시에는 이 값을 세션에 저장하는 추가 로직이 필요합니다.
        # (데모를 위해 여기서는 수동 연결 버튼을 병행하거나 주소 입력을 흉내냅니다.)
        if st.button("연결 상태 확인"): 
            st.session_state.wallet_address = OWNER_WALLET # 운영자 테스트용
            if st.session_state.wallet_address == OWNER_WALLET:
                st.session_state.balance = 100000000.0
            st.rerun()
    else:
        # 지갑 정보 표시
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">WALLET</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold;">{st.session_state.balance:,.0f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.session_state.balance = 2.0
            st.rerun()

# 8. 메인 탭 (기존 닷지, 주사위 로직 유지)
tabs = st.tabs(["🌐 NETWORK", "🛠️ NODE SALE", "🕹️ ARCADE", "🎲 LUCKY DICE"])

with tabs[3]: # 럭키 주사위
    st.markdown('<div class="dice-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:black !important;">🎰 LUCKY DICE 🎰</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:80px; margin:0;">🎲</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    # ... 주사위 배팅 로직 ...
