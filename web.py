import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 정보 (마스터 지갑)
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리 (초기화)
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 2.0  # 첫 방문 보너스
if 'sol_balance' not in st.session_state:
    st.session_state.sol_balance = 5.0 # 기본 5 SOL 부여
if 'is_first_dice' not in st.session_state:
    st.session_state.is_first_dice = True
if 'owned_nodes' not in st.session_state:
    st.session_state.owned_nodes = 0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'treasury' not in st.session_state:
    st.session_state.treasury = 0.0

# 4. [디자인] 프리미엄 티타늄 & 골드 + 귀여운 주사위 테마
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

    /* 🎲 귀여운 주사위 카드 디자인 (복구) */
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

# 5. 상단 헤더 & 축하 전광판 (복구)
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""
    <div class="ticker">
        <marquee scrollamount="10">
            🎊 축하합니다! 0x...8f2 님이 주사위 6번으로 잭팟 당첨! &nbsp;&nbsp;&nbsp;&nbsp; 🚀 신규 노드 구매 트랜잭션 승인 완료: 0x...a3c &nbsp;&nbsp;&nbsp;&nbsp; 💎 WOOHOO AI 메인넷 채굴 파워가 1.4 EH/s를 돌파했습니다!
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# 6. 사이드바 - 지갑 센터
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    if not st.session_state.wallet_address:
        if st.button("CONNECT PHANTOM", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            if st.session_state.wallet_address == OWNER_WALLET:
                st.session_state.balance = 100000000.0 # 운영자 비밀 1억코인
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">ADDRESS</p>
                <p style="margin:0; font-size:13px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">SOL BALANCE</p>
                <p style="margin:0; font-size:20px; font-weight:bold; color:#FFF;">{st.session_state.sol_balance:.2f} SOL</p>
                <p style="margin:0; font-size:12px; color:#888; margin-top:10px;">WH BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFD700;">{st.session_state.balance:,.0f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.rerun()

# 7. 탭 메뉴
tabs = st.tabs(["🌐 NETWORK", "🛠️ NODE SALE", "🕹️ ARCADE", "🎲 LUCKY DICE"])

# --- TAB 1: NETWORK ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL COMPUTE NETWORK")
    st.line_chart(np.random.randn(20, 1), color=["#FFD700"])

# --- TAB 2: NODE SALE (실제 구매 시스템) ---
with tabs[1]:
    st.markdown("### 🛠️ HYPER-FUSE 노드 분양")
    if not st.session_state.wallet_address:
        st.error("지갑을 연결해야 노드 구매가 가능합니다.")
    else:
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            st.markdown("""<div style='background:#111; padding:20px; border:1px solid #333; border-radius:15px;'>
                <h4>GENESIS NODE (Tier 1)</h4>
                <p>가격: 2.0 SOL</p>
                <p>채굴 수익: 50 WH / 일</p>
            </div>""", unsafe_allow_html=True)
            if st.button("MINT NODE (2.0 SOL)", use_container_width=True):
                if st.session_state.sol_balance >= 2.0:
                    with st.spinner("트랜잭션 승인 대기 중..."):
                        time.sleep(2)
                        st.session_state.sol_balance -= 2.0
                        st.session_state.owned_nodes += 1
                        st.balloons()
                        st.success("노드 구매 성공! 채굴 목록에 추가되었습니다.")
                else: st.error("SOL 잔액이 부족합니다.")
        with col_n2:
            st.metric("내가 보유한 노드", f"{st.session_state.owned_nodes} 개")
            st.info(f"오늘의 채굴 예상액: {st.session_state.owned_nodes * 50} WH")

# --- TAB 3: ARCADE (닷지 게임 복구) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL (P2E)")
    if not st.session_state.wallet_address:
        st.error("지갑 연결이 필요합니다.")
    else:
        st.warning("⚠️ 참가비: 0.05 WH (시작 시 자동 차감)")
        if not st.session_state.game_active:
            if st.button("🚀 미션 시작 (START)", use_container_width=True):
                if st.session_state.balance >= 0.05:
                    st.session_state.balance -= 0.05
                    st.session_state.treasury += 0.05
                    st.session_state.game_active = True
                    st.rerun()
        else:
            if st.button("⏹️ 게임 종료 (EXIT)"):
                st.session_state.game_active = False
                st.rerun()
            
            # 닷지 게임 엔진 (JS)
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

# --- TAB 4: LUCKY DICE (귀여운 디자인 & 첫 판 6 고정) ---
with tabs[3]:
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        st.markdown('<div class="dice-card">', unsafe_allow_html=True)
        st.markdown('<h3>🎰 LUCKY DICE 🎰</h3>', unsafe_allow_html=True)
        if 'last_res' in st.session_state:
            st.markdown(f'<p class="dice-num">{st.session_state.last_res}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="dice-num">🎲</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 배팅액 1부터 가능하게 수정
        bet = st.select_slider("배팅액 선택 (WH)", options=[1, 5, 10, 50, 100, 500])
        
        if st.button("ROLL THE DICE!!", use_container_width=True):
            if st.session_state.balance >= bet:
                st.session_state.balance -= bet
                
                # [운영자 비밀 로직] 첫 판은 무조건 6!
                if st.session_state.is_first_dice:
                    res = 6
                    st.session_state.is_first_dice = False
                else:
                    res = random.randint(1, 6)
                
                st.session_state.last_res = res
                if res >= 5:
                    st.session_state.balance += (bet * 1.9)
                    st.balloons()
                st.rerun()
            else: st.error("잔액이 부족합니다.")
