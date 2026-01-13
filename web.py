import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 운영자 지갑 주소
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 세션 상태 관리 (데이터 유실 방지)
if 'wallet_address' not in st.session_state: st.session_state.wallet_address = None
if 'balance' not in st.session_state: st.session_state.balance = 2.0
if 'heroes' not in st.session_state: st.session_state.heroes = {} # {레벨: 개수}
if 'vault' not in st.session_state: st.session_state.vault = {} # 보관소
if 'treasury' not in st.session_state: st.session_state.treasury = 0.0
if 'game_active' not in st.session_state: st.session_state.game_active = False

# 2. [디자인] 입체적 음양 및 프리미엄 테마 적용
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700;900&display=swap');
    
    .stApp { background-color: #000000 !important; }
    
    /* 입체적 텍스트 및 음영 효과 */
    html, body, [class*="st-"] {
        color: #E0E0E0 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    h1, h2, h3 { 
        color: #FFD700 !important; 
        font-family: 'Orbitron' !important; 
        text-shadow: 3px 3px 10px rgba(255, 215, 0, 0.3); /* 음양 추가 */
    }

    /* 카드 음양 및 입체감 디자인 */
    .premium-card {
        background: linear-gradient(145deg, #1a1a1a, #0d0d0d); /* 입체 그라데이션 */
        border: 1px solid #333;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 10px 10px 20px #050505, -5px -5px 15px #1f1f1f; /* 깊은 음영 효과 */
        text-align: center;
        margin-bottom: 20px;
    }

    /* 캐릭터 입체 광채 효과 */
    .char-sprite {
        font-size: 60px;
        filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.8)); /* 입체적 광채 */
        margin-bottom: 10px;
        display: inline-block;
    }

    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 10px 0; color: #FFD700; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 3. 사이드바 - 지갑 관리
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 전용 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0 # 1억 코인 지급
            st.rerun()
    else:
        st.markdown(f"""
            <div class="premium-card">
                <p style="margin:0; font-size:12px; color:#888;">MY WALLET</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:24px; font-weight:900;">{st.session_state.balance:,.1f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.rerun()

# 4. [수정] 탭 에러 해결 - 미리 리스트를 확정하여 생성
tab_list = ["🌐 현황", "🕹️ 게임", "🎲 주사위", "🐲 RPG & 보관소"]
if st.session_state.wallet_address == OWNER_WALLET:
    tab_list.append("👑 관리자")

tabs = st.tabs(tab_tabs := tab_list) # tabs.append 에러 원천 차단

# --- 탭 1, 2, 3은 기존과 동일하되 디자인 음영 강화 ---
with tabs[0]: 
    st.markdown("### 🌐 글로벌 네트워크 통계")
    st.line_chart(np.random.randn(20, 1), color=["#FFD700"])

with tabs[1]:
    st.markdown("### 🕹️ 닷지 서바이벌")
    st.write("지갑 연결 후 이용 가능합니다. (준비 중)")

# --- 탭 4: RPG HERO & VAULT (엑박 없는 캐릭터 시스템) ---
with tabs[3]:
    st.markdown("### 🐲 HERO'S JOURNEY : EVOLUTION")
    
    # 레벨별 아이콘 및 이름 (이모지는 엑박이 뜨지 않습니다)
    HERO_DATA = {
        1: {"icon": "💧", "name": "슬라임", "price": 5},
        2: {"icon": "👺", "name": "고블린", "price": 20},
        3: {"icon": "👹", "name": "오크", "price": 80},
        4: {"icon": "🐎", "name": "켄타우로스", "price": 300},
        5: {"icon": "🐲", "name": "드래곤", "price": 1500},
        6: {"icon": "👼", "name": "가디언", "price": 10000},
        1000: {"icon": "👑", "name": "마스터", "price": 1000000}
    }

    col_play, col_inv, col_vlt = st.columns([1.2, 2.5, 2.5])

    with col_play:
        st.subheader("✨ 영웅 소환")
        if st.button("신규 영웅 소환 (10 WH)", use_container_width=True):
            if st.session_state.balance >= 10:
                st.session_state.balance -= 10
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 1
                st.success("Lv.1 슬라임이 탄생했습니다!")
                st.rerun()
            else: st.error("잔액이 부족합니다.")

    with col_inv:
        st.subheader("🎒 인벤토리")
        for lvl in sorted(st.session_state.heroes.keys()):
            count = st.session_state.heroes[lvl]
            if count > 0:
                data = HERO_DATA.get(lvl, {"icon": "🛡️", "name": "용사", "price": lvl*100})
                st.markdown(f"""
                    <div class="premium-card">
                        <div class="char-sprite">{data['icon']}</div>
                        <h4>Lv.{lvl} {data['name']}</h4>
                        <p>보유수량: {count}개</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # 합성 및 판매 버튼
                c1, c2, c3 = st.columns(3)
                if count >= 2:
                    # 5레벨부터 강화비용 및 실패 확률 적용
                    prot_cost = (lvl * 50) if lvl >= 5 else 0
                    if c1.button(f"🧬 합성", key=f"f_{lvl}"):
                        st.session_state.heroes[lvl] -= 2
                        prob = 100 if lvl < 5 else max(10, 80 - (lvl*5))
                        if random.randint(1, 100) <= prob:
                            st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1, 0) + 1
                            st.balloons(); st.success("강화 성공!")
                        else: st.error("강화 실패! 영웅이 파괴되었습니다.")
                        st.rerun()
                
                if c2.button(f"💰 판매", key=f"s_{lvl}"):
                    st.session_state.heroes[lvl] -= 1
                    st.session_state.balance += data['price']
                    st.toast(f"{data['price']} WH 획득!"); st.rerun()
                
                if c3.button(f"📦 보관", key=f"v_{lvl}"):
                    st.session_state.heroes[lvl] -= 1
                    st.session_state.vault[lvl] = st.session_state.vault.get(lvl, 0) + 1
                    st.rerun()

    with col_vlt:
        st.subheader("🏛️ 영웅 보관소")
        for lvl, v_count in st.session_state.vault.items():
            if v_count > 0:
                data = HERO_DATA.get(lvl, {"icon": "🛡️", "name": "용사"})
                st.markdown(f"""
                    <div class="premium-card" style="border-color: #555;">
                        <div style="font-size:30px;">{data['icon']}</div>
                        <p>Lv.{lvl} {data['name']} ({v_count}개)</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🎒 꺼내기", key=f"out_{lvl}"):
                    st.session_state.vault[lvl] -= 1
                    st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl, 0) + 1
                    st.rerun()

# --- 탭 5: 관리자 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.subheader("👑 MASTER ADMIN PANEL")
        st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
