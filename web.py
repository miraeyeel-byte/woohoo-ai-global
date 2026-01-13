import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 정보 및 세션 상태 초기화
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 필수 변수들 (삭제 금지)
if 'wallet_address' not in st.session_state: st.session_state.wallet_address = None
if 'balance' not in st.session_state: st.session_state.balance = 2.0
if 'sol_balance' not in st.session_state: st.session_state.sol_balance = 5.0
if 'heroes' not in st.session_state: st.session_state.heroes = {} 
if 'vault' not in st.session_state: st.session_state.vault = {}
if 'treasury' not in st.session_state: st.session_state.treasury = 0.0
if 'owned_nodes' not in st.session_state: st.session_state.owned_nodes = 0
if 'is_first_dice' not in st.session_state: st.session_state.is_first_dice = True
if 'dice_status' not in st.session_state: st.session_state.dice_status = "idle" # idle, rolling, done

# 3. [디자인] 프리미엄 티타늄 음양 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    
    /* 가독성 강화 음영 */
    html, body, [class*="st-"] {
        color: #FFFFFF !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,1);
    }
    
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron' !important; font-weight: 900 !important; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }

    /* 입체 카드 디자인 */
    .premium-card {
        background: linear-gradient(145deg, #1a1a1a, #0d0d0d);
        border: 1px solid #FFD700;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 8px 8px 20px #000, -2px -2px 10px #222;
        margin-bottom: 20px;
        text-align: center;
    }
    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 10px 0; color: #FFD700; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 4. 상단 전광판
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""<div class="ticker"><marquee scrollamount="10">🚀 RPG 영웅 대규모 업데이트: 10회/100회 연속 합성 기능 오픈! &nbsp;&nbsp;&nbsp;&nbsp; 🛠️ 노드 분양 중: SOL로 구매하고 WH 코인을 채굴하세요!</marquee></div>""", unsafe_allow_html=True)

# 5. 사이드바 - 지갑 센터
with st.sidebar:
    st.markdown("### 🔑 ACCESS CONTROL")
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 전용 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0 # 조용히 1억개 세팅
            st.rerun()
    else:
        st.markdown(f"""<div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;"><p style="margin:0; font-size:12px; color:#888;">CONNECTED</p><p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p><hr style="border-color:#333;"><p style="margin:0; font-size:12px; color:#888;">BALANCE</p><p style="margin:0; font-size:24px; font-weight:900; color:#FFF;">{st.session_state.balance:,.1f} WH</p></div>""", unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.wallet_address = None; st.rerun()

# 6. [중요] 탭 리스트 미리 확정 (에러 방지)
tabs_list = ["🌐 네트워크", "🛠️ 노드 분양", "🕹️ 아케이드", "🎲 주사위 게임", "🐲 RPG & 보관소"]
if st.session_state.wallet_address == OWNER_WALLET: tabs_list.append("👑 관리자")
tabs = st.tabs(tabs_list)

# --- 탭 0: 네트워크 ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL NETWORK STATUS")
    st.line_chart(np.random.randn(20, 1), color=["#FFD700"])

# --- 탭 1: 노드 분양 (복구 완료) ---
with tabs[1]:
    st.markdown("### 🛠️ HYPER-FUSE NODE SALE")
    if not st.session_state.wallet_address: st.error("지갑 연결이 필요합니다.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""<div class="premium-card"><h4>GENESIS NODE</h4><p>2.0 SOL / 일일 50 WH 채굴</p></div>""", unsafe_allow_html=True)
            if st.button("MINT (2.0 SOL)"):
                if st.session_state.sol_balance >= 2.0:
                    st.session_state.sol_balance -= 2.0
                    st.session_state.owned_nodes += 1
                    st.balloons(); st.success("노드 구매 성공!")
                else: st.error("SOL 부족!")
        with c2: st.metric("보유 노드", f"{st.session_state.owned_nodes} 개")

# --- 탭 2: 아케이드 (닷지 게임 복구) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if not st.session_state.wallet_address: st.error("지갑을 연결하세요.")
    else:
        st.write("참가비 0.05 WH / 10초 생존 시 0.1 WH 보상")
        if st.button("🚀 게임 시작 (START)"):
            if st.session_state.balance >= 0.05:
                st.session_state.balance -= 0.05
                st.toast("게임 로딩 중...")
            else: st.error("잔액 부족")

# --- 탭 3: 주사위 게임 (애니메이션 강화) ---
with tabs[3]:
    st.markdown("### 🎲 LUCKY DICE (MODOO VERSION)")
    if not st.session_state.wallet_address: st.error("지갑 연결 필요")
    else:
        dice_container = st.empty()
        
        if st.session_state.dice_status == "rolling":
            # 주사위가 굴러가는 JS 애니메이션
            roll_js = """<div style='text-align:center;'><h1 style='font-size:100px; animation: spin 0.2s linear infinite;'>🎲</h1></div>
                         <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>"""
            components.html(roll_js, height=150)
            time.sleep(1.5) # 1.5초간 굴리기
            
            # 결과 계산
            final_res = 6 if st.session_state.is_first_dice else random.randint(1, 6)
            st.session_state.is_first_dice = False
            st.session_state.last_res = final_res
            st.session_state.dice_status = "done"
            st.rerun()

        elif st.session_state.dice_status == "done":
            st.markdown(f"""<center><div style='background:#FFF5E1; border:8px solid #FF4B4B; border-radius:30px; padding:40px; width:200px; box-shadow:10px 10px 0px #FF4B4B;'>
                            <h1 style='color:#FF4B4B; margin:0; font-size:100px;'>{st.session_state.last_res}</h1></div></center>""", unsafe_allow_html=True)
            if st.session_state.last_res >= 5: st.balloons(); st.success("WIN!")
            if st.button("CLEAR"): st.session_state.dice_status = "idle"; st.rerun()
        
        else:
            st.markdown("<center><h1 style='font-size:100px; opacity:0.3;'>🎲</h1></center>", unsafe_allow_html=True)
            bet_amt = st.selectbox("BETTING", [1, 5, 10, 50, 100])
            if st.button("ROLL!", use_container_width=True):
                if st.session_state.balance >= bet_amt:
                    st.session_state.balance -= bet_amt
                    st.session_state.treasury += bet_amt
                    st.session_state.dice_status = "rolling"
                    st.rerun()

# --- 탭 4: RPG & 보관소 (연속 합성 추가) ---
with tabs[4]:
    st.markdown("### 🐲 HERO EVOLUTION : MULTI-FUSION")
    HERO_ICONS = {1: "💧", 2: "👺", 3: "👹", 4: "🐎", 5: "🐉"}
    HERO_PRICES = {1: 5, 2: 25, 3: 120, 4: 600, 5: 3500}

    col_pull, col_inv, col_vlt = st.columns([1.5, 2, 2])
    
    with col_pull:
        st.subheader("✨ 소환")
        c1, c2 = st.columns(2)
        if c1.button("1회 (10 WH)"): 
            if st.session_state.balance >= 10: st.session_state.balance -= 10; st.session_state.heroes[1] = st.session_state.heroes.get(1,0)+1; st.rerun()
        if c2.button("10회 (90 WH)"):
            if st.session_state.balance >= 90: st.session_state.balance -= 90; st.session_state.heroes[1] = st.session_state.heroes.get(1,0)+10; st.rerun()
        if st.button("🔥 100회 연속 소환 (800 WH)", use_container_width=True):
            if st.session_state.balance >= 800: st.session_state.balance -= 800; st.session_state.heroes[1] = st.session_state.heroes.get(1,0)+100; st.rerun()

    with col_inv:
        st.subheader("🎒 가방")
        for lvl in sorted(st.session_state.heroes.keys()):
            cnt = st.session_state.heroes[lvl]
            if cnt > 0:
                st.markdown(f"""<div class="premium-card">{HERO_ICONS.get(lvl,'🛡️')} <b>Lv.{lvl} 용사</b> ({cnt}개)<br>판매가: {HERO_PRICES.get(lvl,0)} WH</div>""", unsafe_allow_html=True)
                
                # 합성 버튼 (x1, x10, x100)
                cc1, cc2, cc3 = st.columns(3)
                if cnt >= 2 and cc1.button(f"합성x1", key=f"f1_{lvl}"):
                    st.session_state.heroes[lvl] -= 2
                    if random.random() < 0.8: st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+1; st.success("성공!")
                    else: st.error("파괴됨")
                    st.rerun()
                
                if cnt >= 20 and cc2.button(f"합성x10", key=f"f10_{lvl}"):
                    success = sum(1 for _ in range(10) if random.random() < 0.8)
                    st.session_state.heroes[lvl] -= 20
                    st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0) + success
                    st.info(f"결과: {success}개 성공 / {10-success}개 파괴"); st.rerun()

                if cnt >= 200 and cc3.button(f"합성x100", key=f"f100_{lvl}"):
                    success = sum(1 for _ in range(100) if random.random() < 0.8)
                    st.session_state.heroes[lvl] -= 200
                    st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0) + success
                    st.info(f"결과: {success}개 성공 / {100-success}개 파괴"); st.rerun()

                if st.button(f"💰 {HERO_PRICES.get(lvl,0)} WH에 판매", key=f"s_{lvl}", use_container_width=True):
                    st.session_state.balance += HERO_PRICES.get(lvl,0); st.session_state.heroes[lvl] -= 1; st.rerun()

    with col_vlt:
        st.subheader("🏛️ 보관소")
        for lvl, vcnt in st.session_state.vault.items():
            if vcnt > 0:
                st.write(f"Lv.{lvl} ({vcnt}개)")
                if st.button("🎒 꺼내기", key=f"vout_{lvl}"):
                    st.session_state.vault[lvl] -= 1
                    st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl,0)+1
                    st.rerun()

# --- 탭 5: 관리자 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[5]:
        st.subheader("👑 MASTER CONTROL")
        st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
