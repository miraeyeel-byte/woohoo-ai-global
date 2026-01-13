import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER", layout="wide")

# 2. 운영자 정보 및 세션 관리
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 100.0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

# 3. [디자인] 귀여운 네온 스타일 UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&family=Jua&display=swap');
    
    .stApp { background-color: #0A0A0A !important; color: #E0E0E0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    
    /* 귀여운 제목 폰트 */
    h1, h2, h3 { font-family: 'Jua', sans-serif !important; color: #FFD700 !important; }

    /* 주사위 게임용 밝은 카드 디자인 */
    .dice-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        border: 5px solid #FF007A; /* 네온 핑크 */
        box-shadow: 0 0 20px #FF007A;
        margin: 20px 0;
    }
    .dice-text { color: #000 !important; font-size: 24px; font-weight: bold; }
    .dice-number { font-size: 80px !important; margin: 10px 0; color: #FF007A !important; }
    
    /* 탭 스타일 */
    .stTabs [aria-selected="true"] { background-color: #FFD700 !important; color: #000 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 4. 헤더 및 사이드바
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔑 지갑 센터")
    if not st.session_state.wallet_address:
        if st.button("내 지갑 연결 (Phantom)", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.rerun()
    else:
        is_owner = (st.session_state.wallet_address == OWNER_WALLET)
        st.markdown(f"""
            <div style="background:#222; padding:15px; border-radius:15px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">MY WALLET</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:12]}...</p>
                <hr>
                <p style="margin:0; font-size:12px; color:#888;">BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFF;">{st.session_state.balance:,.2f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if is_owner: st.warning("👑 운영자 모드")
        if st.button("연결 해제"):
            st.session_state.wallet_address = None
            st.rerun()

# 5. 탭 메뉴
menu = ["📊 네트워크", "🛠️ AI 노드 채굴", "🕹️ 닷지 게임", "🎲 럭키 주사위"]
if st.session_state.wallet_address == OWNER_WALLET:
    menu.append("👑 관리자 전용")
tabs = st.tabs(menu)

# --- 탭 1: 네트워크 (코인 정체성 설명) ---
with tabs[0]:
    st.markdown("### 🌐 WOOHOO AI 코인이란?")
    st.info("""
    **WOOHOO AI는 '인공지능 에너지'입니다.** 전 세계의 GPU 파워를 하나로 묶어 AI를 돌리고, 그 대가로 WH 코인을 주고받는 생태계입니다. 
    사용자는 코인으로 AI 서비스를 구매하고, 채굴자는 컴퓨터를 빌려주고 코인을 법니다.
    """)
    
    st.line_chart(np.random.randn(15, 1))

# --- 탭 2: 채굴 ---
with tabs[1]:
    st.subheader("🛠️ 내 채굴기 상태")
    st.progress(85, text="GPU 연산 중... (채굴 효율 85%)")
    st.metric("오늘의 예상 수익", "1.25 WH", "+0.05")

# --- 탭 3: 닷지 게임 (보상 체계 수정) ---
with tabs[2]:
    st.markdown("### 🕹️ 60초 생존 챌린지 (P2E)")
    st.write("참가비: **0.1 WH** (시작 시 자동 차감)")
    
    diff = st.selectbox("난이도 선택", ["하 (10초당 0.05 WH)", "중 (10초당 0.1 WH)", "상 (10초당 1.0 WH)"])

    if not st.session_state.game_active:
        if st.button("🚀 게임 시작", use_container_width=True):
            if st.session_state.balance >= 0.1:
                st.session_state.balance -= 0.1
                st.session_state.game_active = True
                st.rerun()
            else:
                st.error("잔액이 부족합니다!")
    else:
        st.button("⏹️ 리셋", on_click=lambda: setattr(st.session_state, 'game_active', False))
        
        # 난이도별 속도 설정
        spd = 1.0 if "하" in diff else 1.8 if "중" in diff else 3.0
        
        game_js = f"""
        <div style="text-align:center;">
            <canvas id="c" width="500" height="350" style="border:3px solid #FFD700; background:#000; cursor:none;"></canvas>
            <h2 id="t" style="color:#FFD700;">생존 시간: 0.00초</h2>
        </div>
        <script>
            const cv = document.getElementById("c"), x = cv.getContext("2d");
            let s = Date.now(), p = {{x:250, y:175, r:6}}, b = [], go = false, ft = 0;
            cv.onmousemove = e => {{ 
                const r = cv.getBoundingClientRect(); 
                p.x = e.clientX - r.left; p.y = e.clientY - r.top; 
            }};
            cv.onmouseleave = () => {{ if(!go) {{ go=true; ft=(Date.now()-s)/1000; }} }};
            function spawn() {{
                const side = Math.floor(Math.random()*4);
                let blt = {{r:3, x:0, y:0, vx:0, vy:0}};
                let v = (2+Math.random()*2)*{spd};
                if(side==0){{blt.x=0; blt.y=Math.random()*350; blt.vx=v; blt.vy=(Math.random()-0.5)*4;}}
                else if(side==1){{blt.x=500; blt.y=Math.random()*350; blt.vx=-v; blt.vy=(Math.random()-0.5)*4;}}
                else if(side==2){{blt.x=Math.random()*500; blt.y=0; blt.vx=(Math.random()-0.5)*4; blt.vy=v;}}
                else {{blt.x=Math.random()*500; blt.y=350; blt.vx=(Math.random()-0.5)*4; blt.vy=-v;}}
                b.push(blt);
            }}
            function loop() {{
                if(go) return;
                let el = (Date.now()-s)/1000;
                document.getElementById("t").innerText = "생존 시간: " + el.toFixed(2) + "초";
                if(b.length < 20 + el*2) spawn();
                b.forEach((i, idx) => {{
                    i.x+=i.vx; i.y+=i.vy;
                    if(i.x<0||i.x>500||i.y<0||i.y>350) b.splice(idx,1);
                    if(Math.hypot(i.x-p.x, i.y-p.y) < i.r+p.r) {{ go=true; ft=el; }}
                }});
                x.clearRect(0,0,500,350);
                x.fillStyle="#FFD700"; x.beginPath(); x.arc(p.x,p.y,p.r,0,7); x.fill();
                x.fillStyle="#F44"; b.forEach(i=>{{x.beginPath(); x.arc(i.x,i.y,i.r,0,7); x.fill();}});
                if(go) {{ x.fillStyle="#F44"; x.font="30px Jua"; x.fillText("GAME OVER", 170, 160); x.fillText(ft.toFixed(2)+"초 생존", 185, 200); }}
                requestAnimationFrame(loop);
            }}
            loop();
        </script>
        """
        components.html(game_js, height=500)
        if st.button("🎁 보상 받기"):
            st.session_state.balance += 0.1
            st.success("보상이 지급되었습니다!")
            st.session_state.game_active = False
            st.rerun()

# --- 탭 4: 럭키 주사위 (귀여운 카드 UI 적용) ---
with tabs[3]:
    st.markdown("### 🎲 럭키 주사위 (LUCKY DICE)")
    
    # [수정] 밝은 배경의 카드 섹션
    st.markdown("""
        <div class="dice-card">
            <p class="dice-text">🎰 오늘의 운을 시험해 보세요! 🎰</p>
            <p class="dice-text" style="font-size:16px; color:#666;">눈이 4, 5, 6이 나오면 배팅액의 2배!</p>
    """, unsafe_allow_html=True)
    
    # 주사위 결과가 있을 때만 숫자를 크게 보여줌
    if 'last_dice' in st.session_state:
        st.markdown(f'<p class="dice-number">{st.session_state.last_dice}</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="dice-number">🎲</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    bet_val = st.selectbox("배팅할 금액을 고르세요 (WH)", [10, 50, 100, 500])
    
    if st.button("🔴 주사위 던지기!!", use_container_width=True):
        if st.session_state.balance >= bet_val:
            st.session_state.balance -= bet_val
            res = random.randint(1, 6)
            st.session_state.last_dice = res
            if res >= 4:
                st.session_state.balance += (bet_val * 2)
                st.balloons()
            st.rerun()
        else:
            st.error("잔액이 부족해요! 😥")

# --- 탭 5: 관리자 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.subheader("👑 마스터 통제실")
        st.metric("시스템 누적 수익", "12,482 SOL")
        st.button("전체 시스템 초기화")
