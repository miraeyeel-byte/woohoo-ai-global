import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | HYPER-CORE", layout="wide")

# 2. 운영자 지갑 주소 (절대 보안)
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
if 'treasury' not in st.session_state:
    st.session_state.treasury = 0.0

# 4. [디자인] 프리미엄 티타늄 & 골드 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] { color: #F0F0F0 !important; font-family: 'Noto Sans KR', sans-serif !important; text-shadow: 2px 2px 4px rgba(0, 0, 0, 1) !important; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron' !important; font-weight: 900 !important; }
    
    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 8px 0; color: #FFD700; font-weight: bold; }
    
    /* 🎲 네온 주사위 카드 */
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
    </style>
    """, unsafe_allow_html=True)

# 5. [브릿지] 실제 팬텀 지갑 호출 자바스크립트
def phantom_connect_script():
    js_code = f"""
    <script>
    async function connect() {{
        try {{
            if ("solana" in window) {{
                const resp = await window.solana.connect();
                const addr = resp.publicKey.toString();
                // Streamlit에 주소 전달
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: addr
                }}, '*');
            }} else {{
                alert("팬텀 지갑이 감지되지 않습니다. 설치 후 다시 시도해주세요!");
                window.open("https://phantom.app/", "_blank");
            }}
        }} catch (err) {{
            console.error(err);
        }}
    }}
    </script>
    <button onclick="connect()" style="
        width: 100%; background: linear-gradient(90deg, #FFD700, #FFA500);
        color: black; border: none; padding: 12px; border-radius: 10px;
        font-weight: bold; cursor: pointer; font-family: sans-serif;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    "> 🦊 PHANTOM 지갑 연결 (진짜) </button>
    """
    return components.html(js_code, height=60)

# 6. 메인 헤더 & 전광판
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""<div class="ticker"><marquee scrollamount="10">🎊 잭팟 당첨! 0x...8f2 님이 1,000 WH를 획득했습니다! &nbsp;&nbsp;&nbsp;&nbsp; 🚀 WOOHOO AI 독자 노드 분양 시작!</marquee></div>""", unsafe_allow_html=True)

# 7. 사이드바 - 지갑 센터
with st.sidebar:
    st.markdown("### 🔑 ACCESS CONTROL")
    if not st.session_state.wallet_address:
        st.write("서비스 이용을 위해 지갑을 연결하세요.")
        # 실제 지갑 호출 버튼
        addr_result = phantom_connect_script()
        
        # 운영자 테스트용 (팝업 없이 바로 연결하고 싶을 때 대비)
        if st.button("운영자 빠른 연결 (테스트용)"):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">CONNECTED WALLET</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">WH BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFF;">{st.session_state.balance:,.0f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.rerun()

# 8. 탭 구성
menu_tabs = ["🌐 NETWORK", "🛠️ NODE SALE", "🕹️ ARCADE", "🎲 LUCKY DICE"]
if st.session_state.wallet_address == OWNER_WALLET:
    menu_tabs.append("👑 ADMIN")
tabs = st.tabs(menu_tabs)

with tabs[0]:
    st.markdown("### 🌐 GLOBAL STATUS")
    st.line_chart(np.random.randn(20, 1), color=["#FFD700"])

with tabs[2]: # 🕹️ 닷지 게임 (복구 버전)
    st.markdown("### 🕹️ DODGE SURVIVAL")
    if not st.session_state.wallet_address:
        st.error("지갑을 먼저 연결하세요.")
    else:
        if not st.session_state.game_active:
            if st.button("🚀 미션 시작 (START)", use_container_width=True):
                if st.session_state.balance >= 0.05:
                    st.session_state.balance -= 0.05
                    st.session_state.game_active = True
                    st.rerun()
        else:
            if st.button("⏹️ 종료"): st.session_state.game_active = False; st.rerun()
            game_js = """
            <div style="text-align:center;">
                <canvas id="c" width="500" height="350" style="border:3px solid #FFD700; background:#000; cursor:none;"></canvas>
                <h2 id="t" style="color:#FFD700;">생존 시간: 0.00초</h2>
            </div>
            <script>
                const cv=document.getElementById("c"), x=cv.getContext("2d");
                let s=Date.now(), p={x:250,y:175,r:6}, b=[], go=false, ft=0;
                cv.onmousemove=e=>{ const r=cv.getBoundingClientRect(); p.x=e.clientX-r.left; p.y=e.clientY-r.top; };
                cv.onmouseleave=()=>{ if(!go){go=true; ft=(Date.now()-s)/1000;} };
                function spawn(){
                    const side=Math.floor(Math.random()*4); let blt={r:3,x:0,y:0,vx:0,vy:0};
                    if(side==0){blt.x=0; blt.y=Math.random()*350; blt.vx=3+Math.random()*2; blt.vy=(Math.random()-0.5)*4;}
                    else if(side==1){blt.x=500; blt.y=Math.random()*350; blt.vx=-3-Math.random()*2; blt.vy=(Math.random()-0.5)*4;}
                    else if(side==2){blt.x=Math.random()*500; blt.y=0; blt.vx=(Math.random()-0.5)*4; blt.vy=3+Math.random()*2;}
                    else {blt.x=Math.random()*500; blt.y=350; blt.vx=(Math.random()-0.5)*4; blt.vy=-3-Math.random()*2;}
                    b.push(blt);
                }
                function loop(){
                    if(go) return;
                    let el=(Date.now()-s)/1000;
                    document.getElementById("t").innerText="생존 시간: "+el.toFixed(2)+"초";
                    if(b.length<30+el) spawn();
                    b.forEach((i,idx)=>{
                        i.x+=i.vx; i.y+=i.vy;
                        if(i.x<0||i.x>500||i.y<0||i.y>350) b.splice(idx,1);
                        if(Math.hypot(i.x-p.x,i.y-p.y)<i.r+p.r){go=true; ft=el;}
                    });
                    x.clearRect(0,0,500,350);
                    x.fillStyle="#FFD700"; x.beginPath(); x.arc(p.x,p.y,p.r,0,7); x.fill();
                    x.fillStyle="#F44"; b.forEach(i=>{x.beginPath(); x.arc(i.x,i.y,i.r,0,7); x.fill();});
                    if(go){ x.fillStyle="#F44"; x.font="30px sans-serif"; x.fillText("GAME OVER", 170, 160); x.fillText(ft.toFixed(2)+"s", 220, 200); }
                    requestAnimationFrame(loop);
                }
                loop();
            </script>
            """
            components.html(game_js, height=500)

with tabs[3]: # 🎲 주사위 (디자인 복구)
    if st.session_state.wallet_address:
        st.markdown('<div class="dice-card"><h3>🎰 LUCKY DICE 🎰</h3>', unsafe_allow_html=True)
        if 'last_res' in st.session_state:
            st.markdown(f'<p class="dice-num">{st.session_state.last_res}</p>', unsafe_allow_html=True)
        else: st.markdown('<p class="dice-num">🎲</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        bet = st.select_slider("배팅액 (WH)", options=[1, 5, 10, 50, 100])
        if st.button("ROLL!", use_container_width=True):
            if st.session_state.balance >= bet:
                st.session_state.balance -= bet
                res = 6 if st.session_state.is_first_dice else random.randint(1, 6)
                st.session_state.is_first_dice = False
                st.session_state.last_res = res
                if res >= 5: st.session_state.balance += (bet * 1.9); st.balloons()
                st.rerun()
