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
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 2.0  # 신규 유저 보너스
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'treasury' not in st.session_state:
    st.session_state.treasury = 0.0
if 'is_first_dice' not in st.session_state:
    st.session_state.is_first_dice = True

# 4. [디자인 복구] 프리미엄 티타늄 & 골드 + 귀여운 네온 주사위
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] {
        color: #F0F0F0 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 1) !important;
    }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron' !important; font-weight: 900 !important; }

    /* 전광판 스타일 */
    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 8px 0; color: #FFD700; font-weight: bold; }

    /* 🎲 귀여운 네온 주사위 카드 (복구됨) */
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
    .dice-num { font-size: 100px !important; color: #FF4B4B !important; margin: 0; font-weight: 900; font-family: 'Orbitron' !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. 상단 헤더 & 전광판
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""
    <div class="ticker">
        <marquee scrollamount="10">
            💎 WOOHOO AI 메인넷 가동! 전 세계 GPU 파워를 연결합니다. &nbsp;&nbsp;&nbsp;&nbsp; 🚀 신규 가입자 2.0 WH 즉시 지급 이벤트 중! &nbsp;&nbsp;&nbsp;&nbsp; 🕹️ 닷지 게임 오픈: 당신의 피지컬을 증명하세요!
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# 6. 사이드바 - 지갑 센터 (운영자 1억 코인 히든 로직)
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    if not st.session_state.wallet_address:
        if st.button("CONNECT PHANTOM", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            # 운영자 지갑이면 조용히 1억 개 세팅
            if st.session_state.wallet_address == OWNER_WALLET:
                st.session_state.balance = 100000000.0
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">ADDRESS</p>
                <p style="margin:0; font-size:13px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFF;">{st.session_state.balance:,.1f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.session_state.balance = 2.0
            st.rerun()

# 7. 탭 메뉴
tabs = st.tabs(["🌐 NETWORK", "🛠️ AI NODE", "🕹️ ARCADE", "🎲 LUCKY DICE"])

# --- TAB 1 & 2 (기본 정보) ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL COMPUTE NETWORK")
    st.write("WOOHOO AI는 전 세계 유휴 GPU 자원을 활용하는 탈중앙화 AI 연산 네트워크입니다.")
    st.line_chart(np.random.randn(20, 1), color=["#FFD700"])
with tabs[1]:
    st.markdown("### 🛠️ HYPER-FUSE NODE")
    st.info("지갑 연결 시 노드 채굴 현황이 표시됩니다.")
    st.progress(92)

# --- TAB 3: 닷지 게임 (복구됨) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL (P2E)")
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        st.warning("⚠️ 참가비: 0.05 WH (시작 시 자동 차감)")
        if not st.session_state.game_active:
            if st.button("🚀 미션 시작 (START)", use_container_width=True):
                if st.session_state.balance >= 0.05:
                    st.session_state.balance -= 0.05
                    st.session_state.treasury += 0.05
                    st.session_state.game_active = True
                    st.rerun()
                else: st.error("잔액이 부족합니다.")
        else:
            if st.button("⏹️ 게임 종료 (EXIT)"):
                st.session_state.game_active = False
                st.rerun()
            
            # 닷지 게임 엔진 (JS 복구)
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
            if st.button("🎁 보상 확인 (10초당 0.1 WH)"):
                st.session_state.balance += 0.1
                st.success("보상 지급 완료!")

# --- TAB 4: 주사위 (귀여운 디자인 & 첫 판 조작 복구) ---
with tabs[3]:
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        st.markdown('<div class="dice-card">', unsafe_allow_html=True)
        st.markdown('<h3>🎰 LUCKY DICE 🎰</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color:#333;">당첨 기준: 5, 6 (1.9배)</p>', unsafe_allow_html=True)
        
        if 'last_res' in st.session_state:
            st.markdown(f'<p class="dice-num">{st.session_state.last_res}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="dice-num">🎲</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        bet = st.select_slider("배팅액 (WH)", options=[1, 5, 10, 50, 100])
        if st.button("ROLL!", use_container_width=True):
            if st.session_state.balance >= bet:
                st.session_state.balance -= bet
                st.session_state.treasury += bet
                
                # [운영자 비밀] 첫 판은 무조건 6
                if st.session_state.is_first_dice:
                    res = 6
                    st.session_state.is_first_dice = False
                else:
                    res = random.randint(1, 6)
                    
                st.session_state.last_res = res
                if res >= 5:
                    win = bet * 1.9
                    st.session_state.balance += win
                    st.session_state.treasury -= win
                    st.balloons()
                st.rerun()
            else: st.error("잔액이 부족합니다.")

# --- TAB 5: ADMIN (운영자 전용) ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs.append("👑 ADMIN"): # 탭 추가 방식 변경
        st.markdown("### 👑 MASTER PANEL")
        st.metric("TREASURY (수익금)", f"{st.session_state.treasury:,.2f} WH")
