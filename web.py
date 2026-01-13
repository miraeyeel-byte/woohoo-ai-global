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

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state: st.session_state.wallet_address = None
if 'balance' not in st.session_state: st.session_state.balance = 2.0
if 'heroes' not in st.session_state: st.session_state.heroes = {} # 인벤토리
if 'vault' not in st.session_state: st.session_state.vault = {} # 보관소
if 'treasury' not in st.session_state: st.session_state.treasury = 0.0
if 'is_first_dice' not in st.session_state: st.session_state.is_first_dice = True
if 'game_active' not in st.session_state: st.session_state.game_active = False

# 4. [디자인] 프리미엄 입체 음양 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    
    /* 입체적 텍스트 음영 (가독성 강화) */
    html, body, [class*="st-"] {
        color: #FFFFFF !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 1), 0px 0px 10px rgba(0,0,0,0.8) !important;
    }
    
    h1, h2, h3, h4 { 
        color: #FFD700 !important; 
        font-family: 'Orbitron' !important; 
        text-shadow: 3px 3px 12px rgba(255, 215, 0, 0.5) !important;
        font-weight: 900 !important;
    }

    /* 프리미엄 카드 음양 디자인 */
    .premium-card {
        background: linear-gradient(145deg, #1a1a1a, #0d0d0d);
        border: 1px solid #FFD700;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 8px 8px 20px #000000, -2px -2px 10px #222;
        margin-bottom: 20px;
    }

    /* 연속 뽑기 버튼 스타일 */
    .pull-btn-discount { color: #00FF00; font-weight: bold; font-size: 12px; }
    .stButton>button { border-radius: 10px; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 5. 헤더 및 전광판
st.markdown("<h1 style='text-align: center; font-size: 55px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 6. 사이드바 (운영자 1억코인 히든 로직)
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 전용 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">MY WALLET</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">WH BALANCE</p>
                <p style="margin:0; font-size:26px; font-weight:900; color:#FFF;">{st.session_state.balance:,.1f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.wallet_address = None; st.rerun()

# 7. 탭 메뉴 (에러 수정: 리스트 미리 생성)
tabs_list = ["🌐 현황", "🕹️ 닷지", "🎲 주사위", "🐲 RPG 영웅"]
if st.session_state.wallet_address == OWNER_WALLET:
    tabs_list.append("👑 관리자")
tabs = st.tabs(tabs_list)

# --- 탭 1 & 2: 생략 (기존 기능 유지) ---
with tabs[0]: st.line_chart(np.random.randn(20, 1), color=["#FFD700"])
with tabs[1]:
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if st.button("🚀 게임 시작"): st.toast("닷지 게임 엔진 가동 중...")

# --- 탭 3: 주사위 (애니메이션 유지) ---
with tabs[2]:
    st.markdown('<center><div style="background:#FFF5E1; border:8px solid #FF4B4B; border-radius:30px; padding:40px; width:300px; box-shadow: 10px 10px 0px #FF4B4B;">', unsafe_allow_html=True)
    res = st.session_state.get('last_res', '🎲')
    st.markdown(f'<p style="font-size:100px; color:#FF4B4B; margin:0; font-weight:900;">{res}</p></div></center>', unsafe_allow_html=True)
    if st.button("ROLL!", use_container_width=True):
        final = 6 if st.session_state.is_first_dice else random.randint(1, 6)
        st.session_state.is_first_dice = False
        st.session_state.last_res = final; st.rerun()

# --- 탭 4: RPG 영웅 (연속 뽑기 & 음양 강화) ---
with tabs[3]:
    st.markdown("### 🐲 HERO'S JOURNEY : EVOLUTION")
    
    col_pull, col_inv, col_vlt = st.columns([1.5, 2, 2])
    
    with col_pull:
        st.subheader("✨ 영웅 소환")
        # 1회 뽑기
        if st.button("💎 1회 소환 (10 WH)", use_container_width=True):
            if st.session_state.balance >= 10:
                st.session_state.balance -= 10
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 1
                st.rerun()
        
        # 5회 연속
        if st.button("💎 5회 연속 소환 (50 WH)", use_container_width=True):
            if st.session_state.balance >= 50:
                st.session_state.balance -= 50
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 5
                st.rerun()

        # 10회 연속 (할인 적용)
        st.markdown('<p class="pull-btn-discount"><s>100 WH</s> → 90 WH (10% OFF)</p>', unsafe_allow_html=True)
        if st.button("🔥 10회 연속 소환 (90 WH)", use_container_width=True):
            if st.session_state.balance >= 90:
                st.session_state.balance -= 90
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 10
                st.rerun()

        # 100회 연속 (파격 할인)
        st.markdown('<p class="pull-btn-discount"><s>1,000 WH</s> → 800 WH (20% OFF)</p>', unsafe_allow_html=True)
        if st.button("👑 100회 연속 소환 (800 WH)", use_container_width=True):
            if st.session_state.balance >= 800:
                st.session_state.balance -= 800
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 100
                st.rerun()

    HERO_DATA = {1: "💧 슬라임", 2: "👺 고블린", 3: "👹 오크", 4: "🐎 켄타우로스", 5: "🐉 드래곤"}
    PRICES = {1: 5, 2: 20, 3: 100, 4: 500, 5: 2500}

    with col_inv:
        st.subheader("🎒 인벤토리")
        for lvl in sorted(st.session_state.heroes.keys()):
            cnt = st.session_state.heroes[lvl]
            if cnt > 0:
                st.markdown(f"""<div class="premium-card"><b>Lv.{lvl} {HERO_DATA.get(lvl,'용사')}</b><br>보유: {cnt}개 | 판매가: {PRICES.get(lvl,0)} WH</div>""", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                if cnt >= 2 and c1.button(f"🧬 합성", key=f"f_{lvl}"):
                    st.session_state.heroes[lvl] -= 2
                    prob = 100 if lvl < 5 else max(10, 80 - (lvl*5))
                    if random.randint(1, 100) <= prob: st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1, 0) + 1; st.balloons()
                    st.rerun()
                if c2.button(f"💰 판매", key=f"s_{lvl}"): st.session_state.balance += PRICES.get(lvl,0); st.session_state.heroes[lvl] -= 1; st.rerun()
                if c3.button(f"📦 보관", key=f"v_{lvl}"): st.session_state.heroes[lvl] -= 1; st.session_state.vault[lvl] = st.session_state.vault.get(lvl, 0) + 1; st.rerun()

    with col_vlt:
        st.subheader("🏛️ 보관소")
        for lvl, v_cnt in st.session_state.vault.items():
            if v_cnt > 0:
                st.write(f"Lv.{lvl} ({v_cnt}개 보관 중)")
                if st.button("🎒 꺼내기", key=f"out_{lvl}"):
                    st.session_state.vault[lvl] -= 1
                    st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl, 0) + 1
                    st.rerun()

# --- 탭 5: 관리자 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.subheader("👑 MASTER ADMIN")
        st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
