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
if 'heroes' not in st.session_state: st.session_state.heroes = {} 
if 'vault' not in st.session_state: st.session_state.vault = {}
if 'protection_potions' not in st.session_state: st.session_state.protection_potions = 0
if 'treasury' not in st.session_state: st.session_state.treasury = 0.0
if 'game_active' not in st.session_state: st.session_state.game_active = False

# 4. [디자인] 초고급 입체 음영 & 티타늄 골드 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700;900&display=swap');
    
    .stApp { background-color: #000000 !important; }
    
    /* 텍스트 가독성 강화: 강한 이중 그림자 */
    html, body, [class*="st-"] {
        color: #FFFFFF !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 4px #000, 0 0 10px rgba(255, 255, 255, 0.2) !important;
    }
    
    h1, h2, h3, h4 { 
        color: #FFD700 !important; 
        font-family: 'Orbitron' !important; 
        text-shadow: 3px 3px 8px rgba(255, 215, 0, 0.6) !important;
        font-weight: 900 !important;
    }

    /* 입체 카드 디자인 (음양 강화) */
    .premium-card {
        background: linear-gradient(145deg, #1a1a1a, #050505);
        border: 1px solid #444;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 10px 10px 25px #000, -5px -5px 15px #222; /* 깊은 입체감 */
        text-align: center;
        margin-bottom: 20px;
    }

    /* 할인 가격 표시용 취소선 */
    .discount-old { text-decoration: line-through; color: #ff4b4b; font-size: 0.8em; margin-right: 5px; }
    .discount-new { color: #00ff00; font-weight: bold; }

    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 10px 0; color: #FFD700; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 5. 헤더 & 전광판
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 6. 사이드바 (지갑 및 잔액)
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 전용 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0
            st.rerun()
    else:
        st.markdown(f"""<div class="premium-card"><p style="margin:0; font-size:12px; color:#888;">MY WALLET</p><p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p><hr style="border-color:#333;"><p style="margin:0; font-size:12px; color:#888;">BALANCE</p><p style="margin:0; font-size:24px; font-weight:900; color:#FFF;">{st.session_state.balance:,.1f} WH</p></div>""", unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.wallet_address = None; st.rerun()

# 7. 탭 메뉴 (에러 방지를 위해 미리 리스트 확정)
menu_list = ["🌐 현황", "🛠️ 노드", "🕹️ 게임", "🎲 주사위", "🐲 RPG & 보관소"]
if st.session_state.wallet_address == OWNER_WALLET: menu_list.append("👑 ADMIN")
tabs = st.tabs(menu_list)

# --- RPG 데이터 설정 ---
HERO_INFO = {
    1: {"icon": "💧", "name": "슬라임", "sell": 5},
    2: {"icon": "👺", "name": "고블린", "sell": 20},
    3: {"icon": "👹", "name": "오크", "sell": 80},
    4: {"icon": "🐎", "name": "켄타우로스", "sell": 500},
    5: {"icon": "🐉", "name": "드래곤", "sell": 3000},
    1000: {"icon": "👑", "name": "마스터", "sell": 1000000}
}

# --- 탭 4: RPG 영웅 (연속 뽑기 추가) ---
with tabs[4]:
    st.markdown("### 🐲 HERO'S JOURNEY : EVOLUTION")
    
    col_shop, col_inv, col_vlt = st.columns([1.5, 2.5, 2.2])
    
    with col_shop:
        st.subheader("🎰 영웅 소환 상점")
        
        # 1회 뽑기
        if st.button("✨ 1회 소환 (10 WH)", use_container_width=True):
            if st.session_state.balance >= 10:
                st.session_state.balance -= 10
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 1
                st.toast("슬라임 소환 완료!"); st.rerun()
        
        # 10회 연속 뽑기 (할인)
        st.markdown('<p><span class="discount-old">100 WH</span> <span class="discount-new">90 WH</span></p>', unsafe_allow_html=True)
        if st.button("🔥 10연속 소환 (10% 할인)", use_container_width=True):
            if st.session_state.balance >= 90:
                st.session_state.balance -= 90
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 10
                st.balloons(); st.rerun()

        # 100회 연속 뽑기 (파격 할인)
        st.markdown('<p><span class="discount-old">1,000 WH</span> <span class="discount-new">800 WH</span></p>', unsafe_allow_html=True)
        if st.button("⚡ 100연속 소환 (20% 할인)", use_container_width=True):
            if st.session_state.balance >= 800:
                st.session_state.balance -= 800
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 100
                st.balloons(); st.rerun()
        
        st.divider()
        st.subheader("🧪 아이템 상점")
        if st.button("파괴방지 물약 (50 WH)", use_container_width=True):
            if st.session_state.balance >= 50:
                st.session_state.balance -= 50
                st.session_state.protection_potions += 1
                st.success("물약 충전 완료!")

    with col_inv:
        st.subheader("🎒 인벤토리")
        for lvl in sorted(st.session_state.heroes.keys()):
            cnt = st.session_state.heroes[lvl]
            if cnt > 0:
                data = HERO_INFO.get(lvl, {"icon": "🛡️", "name": "용사", "sell": lvl*100})
                st.markdown(f"""
                    <div class="premium-card">
                        <span style="font-size:40px; filter: drop-shadow(0 0 5px #ffd700);">{data['icon']}</span>
                        <h4>Lv.{lvl} {data['name']}</h4>
                        <p style="color:#888;">보유: {cnt}개 / 판매가: {data['sell']} WH</p>
                    </div>
                """, unsafe_allow_html=True)
                
                b1, b2, b3 = st.columns(3)
                if cnt >= 2 and b1.button(f"🧬 합성", key=f"f_{lvl}"):
                    st.session_state.heroes[lvl] -= 2
                    prob = 100 if lvl < 5 else max(5, 80 - (lvl*5))
                    if random.randint(1, 100) <= prob:
                        st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1, 0) + 1
                        st.success("합성 성공!"); st.rerun()
                    else: st.error("파괴됨!"); st.rerun()
                
                if b2.button(f"💰 판매", key=f"s_{lvl}"):
                    st.session_state.balance += data['sell']
                    st.session_state.heroes[lvl] -= 1; st.rerun()
                
                if b3.button(f"📦 보관", key=f"v_{lvl}"):
                    st.session_state.heroes[lvl] -= 1
                    st.session_state.vault[lvl] = st.session_state.vault.get(lvl, 0) + 1; st.rerun()

    with col_vlt:
        st.subheader("🏛️ 보관소")
        for lvl, v_cnt in st.session_state.vault.items():
            if v_cnt > 0:
                st.write(f"Lv.{lvl} 영웅 ({v_cnt}개)")
                if st.button("🎒 꺼내기", key=f"out_{lvl}"):
                    st.session_state.vault[lvl] -= 1
                    st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl, 0) + 1; st.rerun()

# --- 탭 0, 1, 2, 3 (기능 보존) ---
with tabs[0]: st.line_chart(np.random.randn(20, 1), color=["#FFD700"])
with tabs[2]: st.markdown("### 🕹️ DODGE GAME"); st.button("미션 시작 (준비됨)")
with tabs[3]: st.markdown('<div class="premium-card"><h2>🎲 LUCKY DICE</h2><p style="font-size:60px;">🎲</p></div>', unsafe_allow_html=True)

# --- 탭 5: 관리자 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[5]:
        st.subheader("👑 MASTER CONTROL")
        st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
