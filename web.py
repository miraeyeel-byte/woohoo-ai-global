import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"
WH_PRICE = 1.00 # 1 WH = $1.00

# 세션 상태 초기화 (절대 삭제 금지)
if 'wallet_address' not in st.session_state: st.session_state.wallet_address = None
if 'balance' not in st.session_state: st.session_state.balance = 2.0
if 'heroes' not in st.session_state: st.session_state.heroes = {}
if 'vault' not in st.session_state: st.session_state.vault = {}
if 'treasury' not in st.session_state: st.session_state.treasury = 0.0
if 'owned_nodes' not in st.session_state: st.session_state.owned_nodes = 0
if 'is_first_dice' not in st.session_state: st.session_state.is_first_dice = True
if 'dice_status' not in st.session_state: st.session_state.dice_status = "idle"
if 'multi_dice_results' not in st.session_state: st.session_state.multi_dice_results = []

# 2. [디자인] 초강력 입체 음양 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Noto+Sans+KR:wght@700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    
    /* 가독성 4중 음영 효과 */
    html, body, [class*="st-"] {
        color: #FFFFFF !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 0px #000, 4px 4px 8px #000, -1px -1px 0px #000, 1px -1px 0px #000 !important;
    }
    
    h1, h2, h3 { 
        color: #FFD700 !important; 
        font-family: 'Orbitron' !important; 
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.8), 3px 3px 5px #000 !important; 
    }

    .premium-card {
        background: linear-gradient(145deg, #222, #000);
        border: 2px solid #FFD700;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 15px 15px 35px #000, inset 2px 2px 5px #444;
        margin-bottom: 15px;
        text-align: center;
    }

    /* 주사위 애니메이션 속도 향상 */
    .dice-fast-roll {
        font-size: 80px;
        display: inline-block;
        animation: fast-spin 0.15s infinite linear;
    }
    @keyframes fast-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-weight: bold; color: #00FF00;'>LIVE TOKEN PRICE: ${WH_PRICE:.2f}</p>", unsafe_allow_html=True)

# 4. 사이드바
with st.sidebar:
    st.markdown("### 🔑 WALLET CONNECT")
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 모드 활성화", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0; st.rerun()
    else:
        st.markdown(f"<div class='premium-card'><b>MY BALANCE</b><br><h2 style='color:#FFD700;'>{st.session_state.balance:,.1f} WH</h2></div>", unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.wallet_address = None; st.rerun()

# 5. 탭 구성 (에러 방지 리스트)
t_list = ["🌐 현황", "🛠️ 노드 분양", "🕹️ 닷지 게임", "🎲 주사위 도박", "🐲 RPG & 보관소"]
if st.session_state.wallet_address == OWNER_WALLET: t_list.append("👑 관리자")
tabs = st.tabs(t_list)

# --- 탭 0 & 1: 현황 및 노드 (유지) ---
with tabs[0]: st.line_chart(np.random.randn(20, 1), color=["#FFD700"])
with tabs[1]:
    st.markdown("### 🛠️ NODE MINTING")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><h4>MASTER NODE</h4><p>2.0 SOL / 일일 50 WH</p></div>", unsafe_allow_html=True)
        if st.button("MINT"): st.session_state.owned_nodes += 1; st.balloons()
    with c2: st.metric("가동 노드", f"{st.session_state.owned_nodes} Units")

# --- 탭 2: 닷지 게임 (복구 버전) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if st.session_state.wallet_address:
        game_html = """<div style='text-align:center;'><canvas id='g' width='500' height='250' style='border:2px solid #FFD700; background:#000; cursor:none;'></canvas></div>
        <script>const c=document.getElementById('g'),x=c.getContext('2d');let p={x:250,y:125,r:7},b=[],go=false,s=Date.now();
        c.onmousemove=e=>{const r=c.getBoundingClientRect();p.x=e.clientX-r.left;p.y=e.clientY-r.top;};
        function loop(){if(go)return;let el=(Date.now()-s)/1000;if(b.length<20+el*2)b.push({x:Math.random()*500,y:0,vx:(Math.random()-0.5)*6,vy:3+Math.random()*3,r:3});
        b.forEach((i,idx)=>{i.x+=i.vx;i.y+=i.vy;if(i.y>250)b.splice(idx,1);if(Math.hypot(i.x-p.x,i.y-p.y)<i.r+p.r)go=true;});
        x.clearRect(0,0,500,250);x.fillStyle='#FFD700';x.beginPath();x.arc(p.x,p.y,p.r,0,7);x.fill();
        x.fillStyle='red';b.forEach(i=>{x.beginPath();x.arc(i.x,i.y,i.r,0,7);x.fill();});
        if(go){x.fillStyle='white';x.font='30px Orbitron';x.fillText('GAME OVER',160,125);}requestAnimationFrame(loop);}loop();</script>"""
        components.html(game_html, height=300)
        if st.button("보상 받기 (10 WH)"): st.session_state.balance += 10.0; st.success("보상 완료")

# --- 탭 3: 주사위 도박 (속도 개선 & 멀티 롤 추가) ---
with tabs[3]:
    st.markdown("### 🎲 LUCKY DICE : FAST MULTI-ROLL")
    
    if st.session_state.dice_status == "rolling":
        roll_box = st.empty()
        roll_box.markdown("<center><div class='dice-fast-roll'>🎲</div></center>", unsafe_allow_html=True)
        time.sleep(0.5) # 속도 3배 단축
        
        # 결과 처리
        count = st.session_state.get('roll_count', 1)
        results = []
        for i in range(count):
            res = 6 if st.session_state.is_first_dice else random.randint(1, 6)
            st.session_state.is_first_dice = False
            results.append(res)
        
        st.session_state.multi_dice_results = results
        st.session_state.dice_status = "done"; st.rerun()

    elif st.session_state.dice_status == "done":
        st.markdown("<div class='premium-card' style='background:#FFF5E1;'>", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.multi_dice_results))
        total_win = 0
        for i, r in enumerate(st.session_state.multi_dice_results):
            cols[i].markdown(f"<h1 style='color:#FF4B4B; text-align:center;'>{r}</h1>", unsafe_allow_html=True)
            if r >= 5: total_win += (st.session_state.current_bet * 1.9)
        
        st.session_state.balance += total_win
        st.session_state.treasury -= total_win
        st.markdown("</div>", unsafe_allow_html=True)
        
        if total_win > 0: st.balloons(); st.success(f"총 {total_win:,.1f} WH 획득!")
        if st.button("다시 던지기"): st.session_state.dice_status = "idle"; st.rerun()

    else:
        bet = st.selectbox("베팅액 (WH)", [1, 5, 10, 50, 100])
        st.session_state.current_bet = bet
        
        c1, c2, c3 = st.columns(3)
        if c1.button("🎲 1회 던지기", use_container_width=True):
            if st.session_state.balance >= bet:
                st.session_state.balance -= bet; st.session_state.treasury += bet
                st.session_state.roll_count = 1; st.session_state.dice_status = "rolling"; st.rerun()
        
        if c2.button("🎰 5회 연속", use_container_width=True):
            if st.session_state.balance >= bet * 5:
                st.session_state.balance -= (bet * 5); st.session_state.treasury += (bet * 5)
                st.session_state.roll_count = 5; st.session_state.dice_status = "rolling"; st.rerun()

        if c3.button("🔥 10회 연속", use_container_width=True):
            if st.session_state.balance >= bet * 10:
                st.session_state.balance -= (bet * 10); st.session_state.treasury += (bet * 10)
                st.session_state.roll_count = 10; st.session_state.dice_status = "rolling"; st.rerun()

# --- 탭 4: RPG 영웅 & 보관소 (유지 및 꺼내기 포함) ---
with tabs[4]:
    st.markdown("### 🐲 HERO FUSION & VAULT")
    h_icons = {1:"💧", 2:"👺", 3:"👹", 4:"🐎", 5:"🐉", 6:"👼"}
    h_prices = {1:5, 2:15, 3:45, 4:150, 5:500, 6:2000}

    cp, ci, cv = st.columns([1.5, 2.5, 2])
    with cp:
        st.subheader("✨ 뽑기")
        if st.button("10회 소환 (90 WH)"): 
            st.session_state.balance -= 90; st.session_state.heroes[1] = st.session_state.heroes.get(1,0)+10; st.rerun()

    with ci:
        st.subheader("🎒 가방")
        for lvl in sorted(st.session_state.heroes.keys()):
            cnt = st.session_state.heroes[lvl]
            if cnt > 0:
                price = h_prices.get(lvl, lvl*500)
                st.markdown(f"<div class='premium-card'>{h_icons.get(lvl,'🛡️')} Lv.{lvl} ({cnt}개)<br>판매: {price} WH</div>", unsafe_allow_html=True)
                if cnt >= 20 and st.button(f"합성 x10", key=f"x10_{lvl}"):
                    st.session_state.heroes[lvl] -= 20
                    win = sum(1 for _ in range(10) if random.random() < 0.7)
                    st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+win; st.rerun()
                if st.button(f"💰 판매", key=f"s_{lvl}"): st.session_state.balance += price; st.session_state.heroes[lvl] -= 1; st.rerun()
                if st.button(f"📦 보관", key=f"v_{lvl}"): st.session_state.heroes[lvl]-=1; st.session_state.vault[lvl]=st.session_state.vault.get(lvl,0)+1; st.rerun()

    with cv:
        st.subheader("🏛️ 보관소")
        for lvl, vcnt in st.session_state.vault.items():
            if vcnt > 0:
                st.write(f"{h_icons.get(lvl)} Lv.{lvl} ({vcnt}개)")
                if st.button("🎒 꺼내기", key=f"out_{lvl}"):
                    st.session_state.vault[lvl] -= 1; st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl,0)+1; st.rerun()

# --- 탭 5: 관리자 (유지) ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[5]: st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
