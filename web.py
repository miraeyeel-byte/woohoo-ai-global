import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 정보 및 세션 유지 (절대 삭제 금지)
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"
WH_PRICE = 1.00 # 1 WH = $1.00

if 'wallet_address' not in st.session_state: st.session_state.wallet_address = None
if 'balance' not in st.session_state: st.session_state.balance = 2.0
if 'heroes' not in st.session_state: st.session_state.heroes = {} 
if 'vault' not in st.session_state: st.session_state.vault = {}
if 'treasury' not in st.session_state: st.session_state.treasury = 0.0
if 'owned_nodes' not in st.session_state: st.session_state.owned_nodes = 0
if 'is_first_dice' not in st.session_state: st.session_state.is_first_dice = True
if 'dice_status' not in st.session_state: st.session_state.dice_status = "idle"

# 3. [디자인] 초강력 입체 음양 테마 (글자 시인성 극한 보강)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Noto+Sans+KR:wght@700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    
    /* 텍스트 가독성: 4중 레이어 음영 */
    html, body, [class*="st-"] {
        color: #FFFFFF !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 5px #000, -2px -2px 5px #000, 2px -2px 5px #000, -2px 2px 5px #000 !important;
    }
    
    h1, h2, h3 { 
        color: #FFD700 !important; 
        font-family: 'Orbitron' !important; 
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.7), 4px 4px 4px #000 !important; 
    }

    .premium-card {
        background: linear-gradient(145deg, #1e1e1e, #050505);
        border: 2px solid #FFD700;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 12px 12px 30px #000, inset 0 0 15px #333;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 헤더
st.markdown("<h1 style='text-align: center; font-size: 55px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 5. 사이드바 - 지갑 센터
with st.sidebar:
    st.markdown("### 🔑 WALLET ACCESS")
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0; st.rerun()
    else:
        st.markdown(f"""<div class='premium-card'><p style='color:#888;'>WALLET ADDRESS</p><p style='font-size:14px; color:#FFD700;'>{st.session_state.wallet_address[:14]}...</p><hr style='border-color:#333;'><p style='color:#888;'>잔액</p><h2>{st.session_state.balance:,.1f} WH</h2></div>""", unsafe_allow_html=True)
        if st.button("지갑 연결 해제"): st.session_state.wallet_address = None; st.rerun()

# 6. 탭 구성 (에러 방지를 위해 미리 리스트 확정)
t_list = ["🌐 현황", "🛠️ 노드 분양", "🕹️ 닷지 게임", "🎲 주사위 게임", "🐲 RPG & 보관소"]
if st.session_state.wallet_address == OWNER_WALLET:
    t_list.append("👑 관리자")
tabs = st.tabs(t_list)

# --- 탭 0: 현황 (데이터 시각화 복구) ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL NETWORK STATUS")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.write("실시간 연산 처리 그래프")
        st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['Computing Power']), color=["#FFD700"])
    with col_s2:
        st.markdown("<div class='premium-card'><h4>SYSTEM STATUS</h4><p style='color:#00FF00;'>● MAINNET ACTIVE</p><p>Nodes: 12,842 Active</p><p>Uptime: 99.99%</p></div>", unsafe_allow_html=True)

# --- 탭 1: 노드 분양 ---
with tabs[1]:
    st.markdown("### 🛠️ HYPER-FUSE NODE MINTING")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.markdown("<div class='premium-card'><h4>GENESIS MASTER NODE</h4><p>가격: 2.0 SOL<br>수익: 일일 50 WH</p></div>", unsafe_allow_html=True)
        if st.button("MINT NODE (2.0 SOL)", use_container_width=True):
            st.session_state.owned_nodes += 1; st.success("노드 민팅 성공!")
    with col_n2: st.metric("내 보유 노드 수", f"{st.session_state.owned_nodes} Units")

# --- 탭 2: 닷지 게임 (엔진 완전 복구) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if not st.session_state.wallet_address: st.error("지갑을 연결하세요.")
    else:
        st.write("붉은 탄환을 피하세요! (참가비: 0.05 WH / 10초 생존 시 0.1 WH 보상)")
        # 실제 자바스크립트 기반 게임 엔진
        game_js = """<div style='text-align:center;'><canvas id='dg' width='500' height='300' style='border:2px solid #FFD700; background:#000; cursor:none;'></canvas><h2 id='tm' style='color:#FFD700;'>0.00s</h2></div>
        <script>const c=document.getElementById('dg'),x=c.getContext('2d');let s=Date.now(),p={x:250,y:150,r:7},b=[],go=false;
        c.onmousemove=e=>{const r=c.getBoundingClientRect();p.x=e.clientX-r.left;p.y=e.clientY-r.top;};
        function loop(){if(go)return;let el=(Date.now()-s)/1000;document.getElementById('tm').innerText=el.toFixed(2)+'s';
        if(b.length<25+el*2)b.push({x:Math.random()*500,y:0,vx:(Math.random()-0.5)*6,vy:2+Math.random()*4,r:3});
        b.forEach((i,idx)=>{i.x+=i.vx;i.y+=i.vy;if(i.y>300)b.splice(idx,1);if(Math.hypot(i.x-p.x,i.y-p.y)<i.r+p.r)go=true;});
        x.clearRect(0,0,500,300);x.fillStyle='#FFD700';x.beginPath();x.arc(p.x,p.y,p.r,0,7);x.fill();
        x.fillStyle='#FF4B4B';b.forEach(i=>{x.beginPath();x.arc(i.x,i.y,i.r,0,7);x.fill();});
        if(go){x.fillStyle='red';x.font='40px Orbitron';x.fillText('GAME OVER',130,150);}requestAnimationFrame(loop);}loop();</script>"""
        components.html(game_js, height=450)
        if st.button("🎁 생존 보상 받기"):
            st.session_state.balance += 0.1; st.success("0.1 WH 입금 완료!")

# --- 탭 3: 주사위 게임 (크기 확대 & 시간 조절 & 멀티 롤) ---
with tabs[3]:
    st.markdown("### 🎲 LUCKY DICE : PREMIUM")
    if st.session_state.dice_status == "rolling":
        roll_box = st.empty()
        roll_box.markdown("<center><h1 style='font-size:150px; animation: spin 0.2s infinite;'>🎲</h1></center><style>@keyframes spin {to{transform:rotate(360deg);}}</style>", unsafe_allow_html=True)
        time.sleep(1.0) # 운영자님 요청: 1초 지연
        count = st.session_state.get('roll_count', 1)
        st.session_state.multi_dice_results = [(6 if st.session_state.is_first_dice else random.randint(1,6)) for _ in range(count)]
        st.session_state.is_first_dice = False; st.session_state.dice_status = "done"; st.rerun()

    elif st.session_state.dice_status == "done":
        st.markdown("<div class='premium-card' style='background:#FFF5E1;'>", unsafe_allow_html=True)
        res_list = st.session_state.multi_dice_results
        cols = st.columns(len(res_list))
        total_win = 0
        for i, r in enumerate(res_list):
            # 주사위 크기 대폭 확대 (1.5배)
            cols[i].markdown(f"<h1 style='color:#FF4B4B; font-size:120px; text-align:center; margin:0;'>{r}</h1>", unsafe_allow_html=True)
            if r >= 5: total_win += (st.session_state.current_bet * 1.9)
        st.markdown("</div>", unsafe_allow_html=True)
        st.session_state.balance += total_win
        if total_win > 0: st.success(f"🎊 당첨금 {total_win:,.1f} WH 획득!")
        if st.button("다시 하기"): st.session_state.dice_status = "idle"; st.rerun()
    else:
        bet = st.selectbox("베팅액 (WH)", [1, 5, 10, 50, 100])
        st.session_state.current_bet = bet
        c1, c2, c3 = st.columns(3)
        if c1.button("🎲 1회", use_container_width=True):
            st.session_state.roll_count=1; st.session_state.dice_status="rolling"; st.rerun()
        if c2.button("🎰 5회 연속", use_container_width=True):
            st.session_state.roll_count=5; st.session_state.dice_status="rolling"; st.rerun()
        if c3.button("🔥 10회 연속", use_container_width=True):
            st.session_state.roll_count=10; st.session_state.dice_status="rolling"; st.rerun()

# --- 탭 4: RPG 영웅 & 보관소 (100회 합성 추가) ---
with tabs[4]:
    st.markdown("### 🐲 HERO EVOLUTION : MULTI-FUSION")
    h_icons = {1:"💧", 2:"👺", 3:"👹", 4:"🐎", 5:"🐉", 6:"👼"}
    h_prices = {1:5, 2:15, 3:45, 4:150, 5:500, 6:2000}

    col_p, col_i, col_v = st.columns([1.5, 2.5, 2])
    with col_p:
        st.subheader("✨ 소환")
        if st.button("10회 소환 (90 WH)", use_container_width=True):
            st.session_state.balance -= 90
            st.session_state.heroes[1] = st.session_state.heroes.get(1,0)+10; st.rerun()
        if st.button("👑 100회 소환 (800 WH)", use_container_width=True):
            st.session_state.balance -= 800
            st.session_state.heroes[1] = st.session_state.heroes.get(1,0)+100; st.rerun()

    with col_i:
        st.subheader("🎒 가방")
        for lvl in sorted(st.session_state.heroes.keys()):
            cnt = st.session_state.heroes[lvl]
            if cnt > 0:
                price = h_prices.get(lvl, lvl*500)
                st.markdown(f"<div class='premium-card'>{h_icons.get(lvl,'🛡️')} Lv.{lvl} ({cnt}개)<br><span style='color:#00FF00;'>판매: {price} WH</span></div>", unsafe_allow_html=True)
                cc1, cc2, cc3 = st.columns(3)
                if cnt >= 2 and cc1.button(f"x1", key=f"f1_{lvl}"):
                    st.session_state.heroes[lvl] -= 2
                    if random.random() < 0.75: st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+1
                    st.rerun()
                if cnt >= 20 and cc2.button(f"x10", key=f"f10_{lvl}"):
                    st.session_state.heroes[lvl] -= 20
                    win = sum(1 for _ in range(10) if random.random() < 0.75)
                    st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+win; st.rerun()
                # 운영자님 요청: 100회 합성 추가
                if cnt >= 200 and cc3.button(f"x100", key=f"f100_{lvl}"):
                    st.session_state.heroes[lvl] -= 200
                    win = sum(1 for _ in range(100) if random.random() < 0.75)
                    st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+win; st.rerun()
                
                if st.button(f"💰 판매", key=f"s_{lvl}"): st.session_state.balance += price; st.session_state.heroes[lvl] -= 1; st.rerun()
                if st.button(f"📦 보관", key=f"v_{lvl}"): st.session_state.heroes[lvl] -= 1; st.session_state.vault[lvl] = st.session_state.vault.get(lvl,0)+1; st.rerun()

    with col_v:
        st.subheader("🏛️ 보관소")
        for lvl, vcnt in st.session_state.vault.items():
            if vcnt > 0:
                st.write(f"{h_icons.get(lvl)} Lv.{lvl} ({vcnt}개)")
                if st.button("🎒 꺼내기", key=f"vout_{lvl}"):
                    st.session_state.vault[lvl] -= 1; st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl,0)+1; st.rerun()

# --- 탭 5: 관리자 (운영자 전용 보안) ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[5]:
        st.subheader("👑 MASTER CONTROL")
        st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
