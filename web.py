import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER", layout="wide")

# 2. 운영자 정보
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 2.0
if 'sol_balance' not in st.session_state:
    st.session_state.sol_balance = 5.0
if 'owned_nodes' not in st.session_state:
    st.session_state.owned_nodes = 0
if 'is_first_dice' not in st.session_state:
    st.session_state.is_first_dice = True
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'treasury' not in st.session_state:
    st.session_state.treasury = 0.0

# 4. [디자인] 프리미엄 티타늄 & 골드 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] { color: #F0F0F0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron' !important; font-weight: 900 !important; }
    
    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 8px 0; color: #FFD700; font-weight: bold; text-align: center; }
    
    /* 🎲 귀여운 네온 주사위 카드 */
    .dice-card {
        background: #FFF5E1 !important;
        border: 8px solid #FF4B4B !important;
        border-radius: 30px !important;
        padding: 40px !important;
        text-align: center !important;
        box-shadow: 10px 10px 0px #FF4B4B !important;
        color: #000 !important;
    }
    .dice-num { font-size: 100px !important; color: #FF4B4B !important; margin: 0; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 5. 헤더 & 전광판
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""<div class="ticker"><marquee scrollamount="10">🎊 잭팟! 0x...8f2 님이 500 WH 획득! &nbsp;&nbsp;&nbsp;&nbsp; 🛠️ 노드 분양 개시: SOL로 구매하고 매일 채굴하세요!</marquee></div>""", unsafe_allow_html=True)

# 6. 사이드바 - 지갑 센터 (진짜 연동 시도 + 비상 버튼)
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    
    if not st.session_state.wallet_address:
        # 진짜 지갑 호출 브릿지
        phantom_js = """
        <script>
        async function connect() {
            if (window.parent.solana) {
                try {
                    const resp = await window.parent.solana.connect();
                    alert("지갑 연결됨: " + resp.publicKey.toString());
                } catch (err) { console.error(err); }
            } else { alert("지갑을 찾을 수 없습니다. 테스트용 버튼을 이용하세요!"); }
        }
        </script>
        <button onclick="connect()" style="width:100%; background:#FFD700; color:black; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">
            🦊 PHANTOM 연결 시도
        </button>
        """
        components.html(phantom_js, height=60)
        
        # [운영자님 전용 비상 버튼] - 지갑 없어도 1억개 즉시 충전
        if st.button("👑 운영자 전용 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">ADDRESS</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">WH BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFF;">{st.session_state.balance:,.0f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.rerun()

# 7. 탭 메뉴 (순서대로 꽉 채움)
menu_tabs = ["🌐 NETWORK", "🛠️ NODE SALE", "🕹️ ARCADE", "🎲 LUCKY DICE"]
if st.session_state.wallet_address == OWNER_WALLET:
    menu_tabs.append("👑 ADMIN")
tabs = st.tabs(menu_tabs)

# --- 탭 1: 네트워크 ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL COMPUTE NETWORK")
    st.line_chart(np.random.randn(20, 1), color=["#FFD700"])

# --- 탭 2: 노드 판매 (복구 완료) ---
with tabs[1]:
    st.markdown("### 🛠️ HYPER-FUSE 노드 분양")
    if not st.session_state.wallet_address:
        st.error("지갑을 연결해야 노드를 구매할 수 있습니다.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""<div style='background:#111; padding:20px; border:1px solid #333; border-radius:15px;'>
                <h4>GENESIS NODE (Tier 1)</h4>
                <p>가격: 2.0 SOL / 채굴량: 50 WH/일</p>
            </div>""", unsafe_allow_html=True)
            if st.button("MINT NODE (2.0 SOL)", use_container_width=True):
                if st.session_state.sol_balance >= 2.0:
                    st.session_state.sol_balance -= 2.0
                    st.session_state.owned_nodes += 1
                    st.balloons(); st.success("노드 구매 성공!")
                else: st.error("SOL 부족!")
        with c2:
            st.metric("내 보유 노드", f"{st.session_state.owned_nodes} 개")
            st.info(f"일일 채굴 예상: {st.session_state.owned_nodes * 50} WH")

# --- 탭 3: 닷지 게임 (복구 완료) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        if not st.session_state.game_active:
            if st.button("🚀 미션 시작 (START)", use_container_width=True):
                st.session_state.balance -= 0.05
                st.session_state.game_active = True
                st.rerun()
        else:
            if st.button("⏹️ 종료"): st.session_state.game_active = False; st.rerun()
            game_js = """<div style="text-align:center;"><canvas id="c" width="500" height="300" style="border:2px solid #FFD700; background:#000; cursor:none;"></canvas><h2 id="t" style="color:#FFD700;">시간: 0.00s</h2></div>
            <script>const cv=document.getElementById("c"),x=cv.getContext("2d");let s=Date.now(),p={x:250,y:150,r:6},b=[],go=false;cv.onmousemove=e=>{const r=cv.getBoundingClientRect();p.x=e.clientX-r.left;p.y=e.clientY-r.top;};
            function loop(){if(go)return;let el=(Date.now()-s)/1000;document.getElementById("t").innerText="시간: "+el.toFixed(2)+"s";if(b.length<30+el)b.push({x:Math.random()*500,y:0,vx:(Math.random()-0.5)*4,vy:3+Math.random()*2,r:3});
            b.forEach((i,idx)=>{i.x+=i.vx;i.y+=i.vy;if(i.y>300)b.splice(idx,1);if(Math.hypot(i.x-p.x,i.y-p.y)<i.r+p.r)go=true;});
            x.clearRect(0,0,500,300);x.fillStyle="#FFD700";x.beginPath();x.arc(p.x,p.y,p.r,0,7);x.fill();x.fillStyle="#F44";b.forEach(i=>{x.beginPath();x.arc(i.x,i.y,i.r,0,7);x.fill();});if(go){x.fillStyle="#F44";x.font="30px Orbitron";x.fillText("GAME OVER",160,150);}requestAnimationFrame(loop);}loop();</script>"""
            components.html(game_js, height=400)

# --- 탭 4: 주사위 (디자인 복구) ---
with tabs[3]:
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        st.markdown('<div class="dice-card"><h3>🎰 LUCKY DICE 🎰</h3>', unsafe_allow_html=True)
        res = st.session_state.get('last_res', '🎲')
        st.markdown(f'<p class="dice-num">{res}</p></div>', unsafe_allow_html=True)
        bet = st.selectbox("배팅액 (WH)", [1, 5, 10, 100])
        if st.button("ROLL!", use_container_width=True):
            st.session_state.balance -= bet
            final_res = 6 if st.session_state.is_first_dice else random.randint(1, 6)
            st.session_state.is_first_dice = False
            st.session_state.last_res = final_res
            if final_res >= 5: st.session_state.balance += (bet * 1.9); st.balloons()
            st.rerun()

# --- 탭 5: 관리자 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.subheader("👑 MASTER CONTROL")
        st.metric("금고 누적 수익", f"{st.session_state.treasury:,.2f} WH")
