import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 지갑 주소 설정
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 초기화
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'balance' not in st.session_state:
    st.session_state.balance = 0
if 'token_info' not in st.session_state:
    st.session_state.token_info = {"name": "WOOHOO", "symbol": "WH", "supply": "1,000,000,000"}

# 4. [디자인] 사이버펑크 & 운영자 골드 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Black+Han+Sans&display=swap');
    .stApp { background-color: #000; color: #eee; }
    h1, h2, h3 { font-family: 'Orbitron', 'Black Han Sans' !important; color: #FFD700 !important; }
    .admin-card { border: 2px solid #FFD700; padding: 20px; border-radius: 15px; background: rgba(255, 215, 0, 0.05); }
    .stTabs [aria-selected="true"] { background-color: #FFD700 !important; color: #000 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 5. 사이드바 - 지갑 연동 로직
with st.sidebar:
    st.markdown("### 🔑 ACCESS CONTROL")
    if not st.session_state.wallet_address:
        if st.button("CONNECT PHANTOM WALLET"):
            # 시뮬레이션: 유저가 지갑을 연결했을 때
            connected_addr = OWNER_WALLET # 실제로는 지갑 API에서 받아옴
            st.session_state.wallet_address = connected_addr
            if connected_addr == OWNER_WALLET:
                st.session_state.is_admin = True
                st.session_state.balance = 999999 # 운영자 무한 잔액
            st.rerun()
    else:
        st.success(f"Connected: {st.session_state.wallet_address[:6]}...{st.session_state.wallet_address[-4:]}")
        if st.session_state.is_admin:
            st.warning("⚠️ MASTER ADMIN MODE ACTIVE")
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.session_state.is_admin = False
            st.rerun()

# 6. 메인 화면
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE SYSTEM</h1>", unsafe_allow_html=True)

# 7. 탭 메뉴 (운영자면 추가 메뉴 오픈)
menu = ["🌐 ECOSYSTEM", "🎲 GAME", "🛠️ NODES"]
if st.session_state.is_admin:
    menu.append("🪙 TOKEN FORGE")
    menu.append("👑 ADMIN PANEL")

tabs = st.tabs(menu)

# --- TAB 1: ECOSYSTEM ---
with tabs[0]:
    st.subheader("Global Statistics")
    c1, c2, c3 = st.columns(3)
    c1.metric("TOKEN NAME", st.session_state.token_info['name'])
    c2.metric("SYMBOL", st.session_state.token_info['symbol'])
    c3.metric("TOTAL SUPPLY", st.session_state.token_info['supply'])
    
    st.write("---")
    st.markdown("### 📈 Live Token Value")
    st.line_chart(np.random.randn(20, 1))

# --- TAB 2: GAME ---
with tabs[1]:
    st.write("게임 시스템은 운영자 패널에서 확률 조정이 가능합니다.")
    # (이전 주사위 게임 코드 포함 가능)

# --- TAB 3: NODES (CESS 방식) ---
with tabs[2]:
    st.markdown("### 🛠️ CESS-BASED AI NODE SYSTEM")
    st.info("CESS의 분산 스토리지 기술을 AI 연산 노드에 결합했습니다.")
    
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.markdown("""
        **1. Storage & Compute Node**
        - 역할: AI 모델 데이터를 저장하고 연산을 처리합니다.
        - 필수: 32GB RAM / RTX 3060↑
        """)
        if st.button("Purchase Node License"):
            st.success("노드 라이선스 구매 완료! 스테이킹을 시작하세요.")
            
    with col_n2:
        st.markdown("""
        **2. Consensus Node (Validator)**
        - 역할: 연산의 무결성을 검증합니다 (PoDR2 증명).
        - 보상: 네트워크 수수료의 15% 배분.
        """)
        st.button("Apply for Validator", disabled=True)

# --- TAB 4: TOKEN FORGE (운영자 전용 코인 제작) ---
if st.session_state.is_admin:
    with tabs[3]:
        st.markdown("## 🪙 COIN FACTORY")
        st.write("새로운 코인을 블록체인에 배포하는 설정입니다.")
        
        with st.form("token_form"):
            t_name = st.text_input("Coin Name", value=st.session_state.token_info['name'])
            t_symbol = st.text_input("Coin Symbol", value=st.session_state.token_info['symbol'])
            t_supply = st.text_input("Total Supply", value=st.session_state.token_info['supply'])
            
            if st.form_submit_button("DEPLOY TOKEN TO MAINNET"):
                with st.spinner("Smart Contract Deploying..."):
                    time.sleep(3)
                    st.session_state.token_info = {"name": t_name, "symbol": t_symbol, "supply": t_supply}
                    st.balloons()
                    st.success(f"Successfully Deployed {t_name} ({t_symbol})!")

# --- TAB 5: ADMIN PANEL ---
if st.session_state.is_admin:
    with tabs[4]:
        st.markdown("## 👑 SYSTEM MASTER PANEL")
        st.write(f"Welcome, Master {OWNER_WALLET}")
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.subheader("시스템 수익금")
            st.metric("Total Vault", "12,504 SOL", "↑ 2.4%")
            st.button("Withdraw to Master Wallet")
            
        with col_a2:
            st.subheader("유저 활동량")
            st.write("- Active Users: 1,242명")
            st.write("- Running Nodes: 84 units")
            st.progress(84, text="Node Capacity (84/100)")
