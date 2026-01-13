import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 지갑 주소
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state: st.session_state.wallet_address = None
if 'balance' not in st.session_state: st.session_state.balance = 2.0
if 'sol_balance' not in st.session_state: st.session_state.sol_balance = 5.0
if 'heroes' not in st.session_state: st.session_state.heroes = {} # 인벤토리
if 'vault' not in st.session_state: st.session_state.vault = {} # 보관소
if 'treasury' not in st.session_state: st.session_state.treasury = 0.0
if 'is_first_dice' not in st.session_state: st.session_state.is_first_dice = True
if 'game_active' not in st.session_state: st.session_state.game_active = False

# 4. [디자인] 프리미엄 입체 테마 (음양 및 그림자 강화)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] { color: #E0E0E0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron' !important; text-shadow: 2px 2px 10px rgba(255, 215, 0, 0.4); }
    
    /* 전광판 */
    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 10px 0; color: #FFD700; font-weight: 900; }

    /* 🎲 네온 주사위 카드 (복구) */
    .dice-card {
        background: #FFF5E1 !important;
        border: 8px solid #FF4B4B !important;
        border-radius: 30px !important;
        padding: 40px !important;
        text-align: center !important;
        box-shadow: 10px 10px 0px #FF4B4B !important;
        color: #000 !important;
        margin-bottom: 20px;
    }
    .dice-num { font-size: 100px !important; color: #FF4B4B !important; margin: 0; font-weight: 900; }

    /* 🐲 영웅 카드 입체 디자인 */
    .hero-card {
        background: linear-gradient(145deg, #1a1a1a, #0d0d0d);
        border: 1px solid #333;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 5px 5px 15px #050505;
        text-align: center;
        margin-bottom: 15px;
    }
    .price-tag { color: #00FF00; font-weight: bold; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# 5. 상단 헤더 & 전광판
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""<div class="ticker"><marquee scrollamount="10">💰 고레벨 영웅 판매 시 엄청난 보너스 지급! &nbsp;&nbsp;&nbsp;&nbsp; 🕹️ 닷지 서바이벌: 0.05 WH로 시작해 0.1 WH 보상을 쟁취하세요! &nbsp;&nbsp;&nbsp;&nbsp; 🎲 주사위 잭팟 1.9배 이벤트 중!</marquee></div>""", unsafe_allow_html=True)

# 6. 사이드바 (지갑 및 잔액)
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 전용 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0
            st.rerun()
    else:
        st.markdown(f"""<div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;"><p style="margin:0; font-size:12px; color:#888;">CONNECTED</p><p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p><hr style="border-color:#333;"><p style="margin:0; font-size:12px; color:#888;">BALANCE</p><p style="margin:0; font-size:24px; font-weight:900;">{st.session_state.balance:,.1f} WH</p></div>""", unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.wallet_address = None; st.rerun()

# 7. 탭 메뉴 (모든 기능 보존 및 순서 정렬)
menu_list = ["🌐 현황", "🛠️ 노드 분양", "🕹️ 아케이드", "🎲 주사위 게임", "🐲 영웅 & 보관소"]
if st.session_state.wallet_address == OWNER_WALLET: menu_list.append("👑 관리자")
tabs = st.tabs(menu_list)

# --- 탭 0 & 1: 현황 및 노드 ---
with tabs[0]: st.line_chart(np.random.randn(20, 1), color=["#FFD700"])
with tabs[1]: 
    st.markdown("### 🛠️ 노드 라이선스 민팅"); st.write("가동 중인 노드: 12,842 Units")
    if st.button("MINT NODE (2.0 SOL)"): st.toast("트랜잭션 승인 대기 중...")

# --- 탭 2: 아케이드 (닷지 게임 엔진 복구) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if not st.session_state.wallet_address: st.error("지갑을 연결하세요.")
    else:
        st.warning("⚠️ 참가비: 0.05 WH (10초당 0.1 WH 보상)")
        if not st.session_state.game_active:
            if st.button("🚀 미션 시작 (START)", use_container_width=True):
                if st.session_state.balance >= 0.05:
                    st.session_state.balance -= 0.05
                    st.session_state.treasury += 0.05
                    st.session_state.game_active = True
                    st.rerun()
        else:
            if st.button("⏹️ 종료"): st.session_state.game_active = False; st.rerun()
            game_js = """<div style="text-align:center;"><canvas id="c" width="500" height="350" style="border:3px solid #FFD700; background:#000; cursor:none;"></canvas><h2 id="t" style="color:#FFD700;">시간: 0.00s</h2></div>
            <script>const cv=document.getElementById("c"),x=cv.getContext("2d");let s=Date.now(),p={x:250,y:175,r:6},b=[],go=false,ft=0;cv.onmousemove=e=>{const r=cv.getBoundingClientRect();p.x=e.clientX-r.left;p.y=e.clientY-r.top;};
            function spawn(){const side=Math.floor(Math.random()*4);let blt={r:3,x:0,y:0,vx:0,vy:0};if(side==0){blt.x=0;blt.y=Math.random()*350;blt.vx=3+Math.random()*2;blt.vy=(Math.random()-0.5)*4;}
            else if(side==1){blt.x=500;blt.y=Math.random()*350;blt.vx=-3-Math.random()*2;blt.vy=(Math.random()-0.5)*4;}else if(side==2){blt.x=Math.random()*500;blt.y=0;blt.vx=(Math.random()-0.5)*4;blt.vy=3+Math.random()*2;}
            else{blt.x=Math.random()*500;blt.y=350;blt.vx=(Math.random()-0.5)*4;blt.vy=-3-Math.random()*2;}b.push(blt);}
            function loop(){if(go)return;let el=(Date.now()-s)/1000;document.getElementById("t").innerText="시간: "+el.toFixed(2)+"s";if(b.length<30+el)spawn();
            b.forEach((i,idx)=>{i.x+=i.vx;i.y+=i.vy;if(i.x<0||i.x>500||i.y<0||i.y>350)b.splice(idx,1);if(Math.hypot(i.x-p.x,i.y-p.y)<i.r+p.r){go=true;ft=el;}});
            x.clearRect(0,0,500,350);x.fillStyle="#FFD700";x.beginPath();x.arc(p.x,p.y,p.r,0,7);x.fill();x.fillStyle="#F44";b.forEach(i=>{x.beginPath();x.arc(i.x,i.y,i.r,0,7);x.fill();});
            if(go){x.fillStyle="#F44";x.font="30px Orbitron";x.fillText("GAME OVER",170,160);x.fillText(ft.toFixed(2)+"s",220,200);}requestAnimationFrame(loop);}loop();</script>"""
            components.html(game_js, height=500)
            if st.button("🎁 보상 받기"): st.session_state.balance += 0.1; st.success("보상 지급 완료!")

# --- 탭 3: 주사위 (UI 복구) ---
with tabs[3]:
    st.markdown('<div class="dice-card"><h3>🎰 LUCKY DICE 🎰</h3>', unsafe_allow_html=True)
    res = st.session_state.get('last_res', '🎲')
    st.markdown(f'<p class="dice-num">{res}</p></div>', unsafe_allow_html=True)
    bet = st.select_slider("배팅액 (WH)", options=[1, 5, 10, 50, 100])
    if st.button("ROLL!", use_container_width=True):
        if st.session_state.balance >= bet:
            st.session_state.balance -= bet
            st.session_state.treasury += bet
            final = 6 if st.session_state.is_first_dice else random.randint(1, 6)
            st.session_state.is_first_dice = False
            st.session_state.last_res = final
            if final >= 5: st.session_state.balance += (bet * 1.9); st.balloons()
            st.rerun()

# --- 탭 4: 영웅 & 보관소 (판매 가격 명시) ---
with tabs[4]:
    st.markdown("### 🐲 영웅 진화 및 보관")
    HERO_ICONS = {1: "💧", 2: "👺", 3: "👹", 4: "🐎", 5: "🐉", 1000: "👑"}
    HERO_PRICES = {1: 5, 2: 20, 3: 100, 4: 500, 5: 2500, 1000: 1000000}

    c_pull, c_inv, c_vlt = st.columns([1, 2, 2])
    with c_pull:
        st.subheader("✨ 뽑기")
        if st.button("영웅 생성 (10 WH)"):
            if st.session_state.balance >= 10: st.session_state.balance -= 10; st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 1; st.rerun()
    
    with c_inv:
        st.subheader("🎒 인벤토리")
        for lvl in sorted(st.session_state.heroes.keys()):
            count = st.session_state.heroes[lvl]
            if count > 0:
                price = HERO_PRICES.get(lvl, lvl*100)
                st.markdown(f"""<div class="hero-card"><div style="font-size:40px;">{HERO_ICONS.get(lvl,'🛡️')}</div>
                    <b>Lv.{lvl} 용사</b><br>보유: {count}개<br><span class="price-tag">판매가: {price} WH</span></div>""", unsafe_allow_html=True)
                b1, b2, b3 = st.columns(3)
                if count >= 2 and b1.button(f"🧬 합성", key=f"f_{lvl}"):
                    st.session_state.heroes[lvl] -= 2
                    # 5레벨부터 파괴 확률
                    prob = 100 if lvl < 5 else max(10, 80 - (lvl*5))
                    if random.randint(1, 100) <= prob: st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1, 0) + 1; st.balloons(); st.success("성공!")
                    else: st.error("파괴됨!")
                    st.rerun()
                if b2.button(f"💰 판매", key=f"s_{lvl}"): st.session_state.balance += price; st.session_state.heroes[lvl] -= 1; st.rerun()
                if b3.button(f"📦 보관", key=f"v_{lvl}"): st.session_state.heroes[lvl] -= 1; st.session_state.vault[lvl] = st.session_state.vault.get(lvl, 0) + 1; st.rerun()

    with c_vlt:
        st.subheader("🏛️ 보관소")
        for lvl, v_count in st.session_state.vault.items():
            if v_count > 0:
                st.markdown(f"Lv.{lvl} ({v_count}개 보관 중)")
                if st.button("🎒 꺼내기", key=f"out_{lvl}"): st.session_state.vault[lvl] -= 1; st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl, 0) + 1; st.rerun()

# --- 탭 5: 관리자 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[5]:
        st.subheader("👑 MASTER ADMIN")
        st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
