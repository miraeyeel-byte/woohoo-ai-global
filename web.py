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
if 'heroes' not in st.session_state: st.session_state.heroes = {} # 인벤토리 {레벨: 개수}
if 'vault' not in st.session_state: st.session_state.vault = {} # 보관소 {레벨: 개수}
if 'treasury' not in st.session_state: st.session_state.treasury = 0.0
if 'is_first_dice' not in st.session_state: st.session_state.is_first_dice = True
if 'game_active' not in st.session_state: st.session_state.game_active = False

# 4. RPG 밸런스 데이터 (판매가 및 보호비용)
# 레벨별 판매 가격 (기하급수적 상승)
SELL_PRICES = {
    1: 5, 2: 15, 3: 45, 4: 120, 5: 350, 
    6: 1000, 7: 3000, 8: 10000, 9: 50000, 10: 200000
}
# 1000레벨까지는 (레벨 * 레벨 * 10) 등으로 자동 계산되도록 하단 로직 처리

# 5. [디자인] 프리미엄 티타늄 & 골드 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] { color: #F0F0F0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3, .gold { color: #FFD700 !important; font-family: 'Orbitron' !important; font-weight: 900 !important; }
    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 8px 0; color: #FFD700; font-weight: bold; }
    .storage-box { background: rgba(255, 215, 0, 0.05); border: 1px solid #FFD700; border-radius: 15px; padding: 15px; }
    .dice-card { background: #FFF5E1 !important; border: 8px solid #FF4B4B !important; border-radius: 30px !important; padding: 40px !important; text-align: center !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 6. 헤더 & 전광판
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""<div class="ticker"><marquee scrollamount="10">🛡️ 고레벨 강화 시 파괴 방지 보호 기능을 반드시 확인하세요! &nbsp;&nbsp;&nbsp;&nbsp; 💰 Lv.10 달성 시 200,000 WH 즉시 판매 가능! &nbsp;&nbsp;&nbsp;&nbsp; 🚀 네트워크 파워 상향 안정화 진행 중...</marquee></div>""", unsafe_allow_html=True)

# 7. 사이드바 (운영자 히든 로직)
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 전용 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0
            st.rerun()
    else:
        st.markdown(f"""<div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;"><p style="margin:0; font-size:12px; color:#888;">CONNECTED WALLET</p><p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p><hr style="border-color:#333;"><p style="margin:0; font-size:12px; color:#888;">WH BALANCE</p><p style="margin:0; font-size:24px; font-weight:bold;">{st.session_state.balance:,.1f} WH</p></div>""", unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.wallet_address = None; st.rerun()

# 8. 탭 메뉴 (모든 기능 유지)
menu_tabs = ["🌐 NETWORK", "🕹️ ARCADE", "🎲 LUCKY DICE", "🐲 RPG HERO & VAULT"]
if st.session_state.wallet_address == OWNER_WALLET: menu_tabs.append("👑 ADMIN")
tabs = st.tabs(menu_tabs)

# --- 탭 1 & 2: 네트워크 & 아케이드 (기존 보존) ---
with tabs[0]: st.line_chart(np.random.randn(20, 1), color=["#FFD700"])
with tabs[1]: st.write("🕹️ 닷지 게임 참가비 0.05 WH (10초 생존 시 0.1 WH 보상)"); st.button("준비 중..")

# --- 탭 3: 주사위 (애니메이션 주사위 보존) ---
with tabs[2]:
    st.markdown('<div class="dice-card"><h3>🎰 LUCKY DICE 🎰</h3>', unsafe_allow_html=True)
    res = st.session_state.get('last_res', '🎲')
    st.markdown(f'<p style="font-size:100px; margin:0; font-weight:900; color:#FF4B4B;">{res}</p></div>', unsafe_allow_html=True)
    bet = st.selectbox("배팅액 (WH)", [1, 5, 10, 50, 100])
    if st.button("ROLL!", use_container_width=True):
        st.session_state.balance -= bet
        final_res = 6 if st.session_state.is_first_dice else random.randint(1, 6)
        st.session_state.is_first_dice = False
        st.session_state.last_res = final_res
        if final_res >= 5: st.session_state.balance += (bet * 1.9); st.balloons()
        st.rerun()

# --- 탭 4: RPG 영웅 & 보관소 (차등 물약값 및 고가 판매 적용) ---
with tabs[3]:
    st.markdown("### 🐲 HERO'S JOURNEY : EVOLUTION")
    
    col_play, col_inv, col_vlt = st.columns([1, 2, 2])
    
    with col_play:
        st.subheader("✨ 영웅 소환")
        if st.button("일반 소환 (10 WH)", use_container_width=True):
            if st.session_state.balance >= 10:
                st.session_state.balance -= 10
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 1
                st.rerun()
        st.info("Lv.5 부터는 강화 실패 시 영웅이 파괴될 수 있습니다.")

    with col_inv:
        st.subheader("🎒 인벤토리")
        for lvl in sorted(st.session_state.heroes.keys()):
            count = st.session_state.heroes[lvl]
            if count > 0:
                # 차등 판매 가격 계산
                s_price = SELL_PRICES.get(lvl, lvl * lvl * 100)
                st.markdown(f"**Lv.{lvl} 영웅** ({count}개) - 판매가: **{s_price} WH**")
                
                # 1. 판매 기능 (밸런스 조정됨)
                if st.button(f"💰 판매하기 (+{s_price} WH)", key=f"sell_{lvl}"):
                    st.session_state.heroes[lvl] -= 1
                    st.session_state.balance += s_price
                    st.toast(f"Lv.{lvl} 판매 완료!"); st.rerun()

                # 2. 강화/합성 기능 (차등 보호비용 적용)
                if count >= 2:
                    # 차등 보호 비용: 레벨이 높을수록 비싸짐
                    prot_cost = (lvl * lvl * 20) if lvl >= 5 else 0
                    success_prob = 100 if lvl < 5 else max(5, 85 - (lvl * 8))
                    
                    st.markdown(f"<small>성공률: {success_prob}%</small>", unsafe_allow_html=True)
                    use_prot = st.checkbox(f"🛡️ 파괴방지 ({prot_cost} WH)", key=f"prot_{lvl}")
                    
                    if st.button(f"🧬 합성 도전 (Lv.{lvl+1})", key=f"fuse_{lvl}"):
                        actual_cost = prot_cost if use_prot else 0
                        if st.session_state.balance >= actual_cost:
                            st.session_state.balance -= actual_cost
                            st.session_state.heroes[lvl] -= 2
                            
                            if random.randint(1, 100) <= success_prob:
                                st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1, 0) + 1
                                st.balloons(); st.success("강화 성공!")
                            else:
                                if use_prot:
                                    st.session_state.heroes[lvl] += 1
                                    st.warning("강화 실패! 하지만 보호 기능으로 영웅 1개를 지켰습니다.")
                                else:
                                    st.error("강화 실패! 영웅이 파괴되었습니다.")
                            st.rerun()
                        else: st.error("보호 비용이 부족합니다.")

                # 3. 보관소 이동
                if st.button("📦 보관함으로", key=f"to_v_{lvl}"):
                    st.session_state.heroes[lvl] -= 1
                    st.session_state.vault[lvl] = st.session_state.vault.get(lvl, 0) + 1
                    st.rerun()

    with col_vlt:
        st.subheader("🏛️ 보관소")
        st.markdown('<div class="storage-box">', unsafe_allow_html=True)
        if not st.session_state.vault or sum(st.session_state.vault.values()) == 0:
            st.write("보관 중인 영웅이 없습니다.")
        for lvl, v_count in st.session_state.vault.items():
            if v_count > 0:
                st.write(f"Lv.{lvl} 영웅 ({v_count}개)")
                if st.button("🎒 꺼내기", key=f"from_v_{lvl}"):
                    st.session_state.vault[lvl] -= 1
                    st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl, 0) + 1
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 탭 5: 관리자 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.subheader("👑 MASTER CONTROL")
        st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
