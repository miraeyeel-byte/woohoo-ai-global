import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | HYPER-CORE", layout="wide")

# 2. 운영자 지갑 주소 (이 주소가 감지되면 1억 코인)
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 2.0
if 'is_first_dice' not in st.session_state:
    st.session_state.is_first_dice = True
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

# 4. [디자인] 프리미엄 티타늄 & 골드 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] { color: #F0F0F0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron' !important; }
    
    /* 🎲 네온 주사위 카드 디자인 */
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
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""<div style='background:#111; border-top:2px solid #FFD700; border-bottom:2px solid #FFD700; padding:8px 0; color:#FFD700; font-weight:bold; text-align:center;'>
    <marquee scrollamount="10">🎊 축하합니다! 주사위 잭팟 당첨자 탄생 &nbsp;&nbsp;&nbsp;&nbsp; 🚀 WOOHOO AI 독자 노드 1단계 분양 마감 임박!</marquee>
</div>""", unsafe_allow_html=True)

# 6. 사이드바 - 진짜 지갑 연동 브릿지
with st.sidebar:
    st.markdown("### 🔑 WALLET CONNECT")
    
    # [진짜 팬텀 호출 버튼] 자바스크립트
    phantom_js = """
    <div id="wallet-btn-root"></div>
    <script>
    async function connectWallet() {
        if (window.solana && window.solana.isPhantom) {
            try {
                const resp = await window.solana.connect();
                alert("연결 성공: " + resp.publicKey.toString());
                // 실제 주소를 파이썬으로 넘기려면 추가 라이브러리가 필요하므로,
                // 여기서는 연결 성공 알림만 띄웁니다.
            } catch (err) { console.error(err); }
        } else {
            alert("팬텀 지갑이 없습니다! 설치 페이지로 이동합니다.");
            window.open("https://phantom.app/", "_blank");
        }
    }
    </script>
    <button onclick="connectWallet()" style="width:100%; background:#FFD700; color:black; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">
        🦊 PHANTOM 지갑 연결
    </button>
    """
    components.html(phantom_js, height=70)

    # 운영자님을 위한 '빠른 연결' 버튼 (실제 팬텀 없이도 1억개 확인용)
    if st.button("운영자 모드 활성화 (테스트용)"):
        st.session_state.wallet_address = OWNER_WALLET
        st.session_state.balance = 100000000.0
        st.rerun()

    if st.session_state.wallet_address:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700; margin-top:10px;">
                <p style="margin:0; font-size:12px; color:#888;">MY WALLET</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFF;">{st.session_state.balance:,.0f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.rerun()

# 7. 탭 메뉴
menu_tabs = ["🌐 NETWORK", "🛠️ AI NODE", "🕹️ ARCADE", "🎲 LUCKY DICE"]
if st.session_state.wallet_address == OWNER_WALLET:
    menu_tabs.append("👑 ADMIN")
tabs = st.tabs(menu_tabs)

# --- 각 탭의 기능들 ---
with tabs[0]: st.line_chart(np.random.randn(20, 1), color=["#FFD700"])

with tabs[2]: # 🕹️ 닷지 게임
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if not st.session_state.wallet_address: st.error("지갑을 연결하세요.")
    else:
        if not st.session_state.game_active:
            if st.button("🚀 미션 시작 (0.05 WH)", use_container_width=True):
                st.session_state.balance -= 0.05
                st.session_state.game_active = True
                st.rerun()
        else:
            if st.button("⏹️ 종료"): st.session_state.game_active = False; st.rerun()
            # 닷지 게임 엔진 (JS)
            game_js = """<div style="text-align:center;"><canvas id="c" width="500" height="300" style="border:2px solid #FFD700; background:#000;"></canvas><h2 id="t" style="color:#FFD700;">시간: 0.00초</h2></div>
            <script>const cv=document.getElementById("c"),x=cv.getContext("2d");let s=Date.now(),p={x:250,y:150,r:6},b=[],go=false;cv.onmousemove=e=>{const r=cv.getBoundingClientRect();p.x=e.clientX-r.left;p.y=e.clientY-r.top;};
            function loop(){if(go)return;let el=(Date.now()-s)/1000;document.getElementById("t").innerText="시간: "+el.toFixed(2)+"초";if(b.length<25+el)b.push({x:Math.random()*500,y:0,vx:(Math.random()-0.5)*4,vy:3+Math.random()*2,r:3});
            b.forEach((i,idx)=>{i.x+=i.vx;i.y+=i.vy;if(i.y>300)b.splice(idx,1);if(Math.hypot(i.x-p.x,i.y-p.y)<i.r+p.r)go=true;});
            x.clearRect(0,0,500,300);x.fillStyle="#FFD700";x.beginPath();x.arc(p.x,p.y,p.r,0,7);x.fill();x.fillStyle="#F44";b.forEach(i=>{x.beginPath();x.arc(i.x,i.y,i.r,0,7);x.fill();});if(go){x.fillStyle="#F44";x.font="30px sans-serif";x.fillText("GAME OVER",170,150);}requestAnimationFrame(loop);}loop();</script>"""
            components.html(game_js, height=450)

with tabs[3]: # 🎲 럭키 주사위
    if not st.session_state.wallet_address: st.error("지갑을 연결하세요.")
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
