import streamlit as st
import time
import random

# --- 운영자 설정 ---
ADMIN_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"  # 이 주소를 본인의 지갑 주소로 바꾸세요

if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'win_rate' not in st.session_state:
    st.session_state.win_rate = 20  # 기본 당첨 확률 20%

# ... (디자인 CSS는 동일하므로 생략하거나 유지) ...

with st.sidebar:
    st.title("🛠️ WOOHOO CONTROL")
    if st.button("ADMIN LOGIN (TEST)"): # 실제로는 지갑 주소 체크 로직
        st.session_state.wallet_address = ADMIN_WALLET
        st.session_state.is_admin = True
        st.success("운영자 계정으로 접속되었습니다.")

# --- 탭 구성 ---
tabs = ["💎 CORE", "🎲 GAME", "🛠️ TERMINAL"]
if st.session_state.is_admin:
    tabs.append("🚀 ADMIN PANEL") # 운영자 전용 탭 추가

selected_tabs = st.tabs(tabs)

# --- (일반 탭 생략) ---

# --- 운영자 전용 탭 (여기가 핵심!) ---
if st.session_state.is_admin:
    with selected_tabs[3]:
        st.markdown("## 👑 OPERATOR MASTER DASHBOARD")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💰 수익 현황")
            st.metric("Total Fees Collected", "4,250 SOL", "+12%")
            if st.button("수익금 지갑으로 출금"):
                st.warning("출금을 진행합니다...")
        
        with col2:
            st.subheader("🎲 시스템 조작 (모드 변경)")
            new_rate = st.slider("게임 당첨 확률 설정 (%)", 0, 100, st.session_state.win_rate)
            if st.button("확률 즉시 적용"):
                st.session_state.win_rate = new_rate
                st.success(f"당첨 확률이 {new_rate}%로 조정되었습니다.")

        st.divider()
        st.subheader("🌐 노드 네트워크 관리")
        st.write("CESS 기반 AI 연산 노드 상태")
        st.table({
            "Node_ID": ["#001", "#002", "#003"],
            "Status": ["Running", "Running", "Offline"],
            "Reward_Pool": ["120 WH", "45 WH", "0 WH"]
        })
