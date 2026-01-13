import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | PRO MASTER", layout="wide")

# 2. 운영자 지갑 주소
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 100.0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False

# 4. [디자인] 강력한 가독성 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    .stApp { background-color: #050505 !important; color: #E0E0E0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3 { color: #FFD700 !important; font-weight: 900 !important; }
    .stTabs [aria-selected="true"] { background-color: #FFD700 !important; color: #000 !important; font-weight: bold; }
    .status-box { border: 2px solid #FFD700; padding: 15px; border-radius: 10px; background: rgba(255, 215, 0, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# 5. 상단 헤더
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 6. 사이드바 - 지갑 센터
with st.sidebar:
    st.markdown("### 🔑 지갑 센터")
    if not st.session_state.wallet_address:
        if st.button("내 지갑 연결 (Phantom)", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.rerun()
    else:
        is_owner = (st.session_state.wallet_address == OWNER_WALLET)
        st.markdown(f"""
            <div class="status-box">
                <p style="margin:0; font-size:12px; color:#888;">지갑 주소</p>
                <p style="margin:0; font-size:14px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:12]}...</p>
                <p style="margin:0; font-size:12px; color:#888; margin-top:10px;">보유 잔액</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFF;">{st.session_state.balance:,.2f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if is_owner: st.warning("⚠️ 운영자(MASTER) 권한 활성화")
        if st.button("연결 해제"):
            st.session_state.wallet_address = None
            st.session_state.game_active = False
            st.rerun()

# 7. 탭 메뉴 구성
menu = ["📊 네트워크", "🛠️ AI 노드 채굴", "🕹️ 닷지 게임", "🎲 럭키 주사위"]
if st.session_state.wallet_address == OWNER_WALLET:
    menu.append("👑 관리자")

tabs = st.tabs(menu)

# --- 탭 1 & 2 (네트워크 및 노드 정보) ---
with tabs[0]:
    st.markdown("### 🌐 WOOHOO AI란 무엇인가요?")
    st.info("**'인공지능을 돌리기 위한 거대한 분산 에너지'**입니다. 유저들이 제공하는 GPU 파워로 AI가 연산되고, 그 생태계의 화폐가 WH 코인입니다.")
    st.line_chart(np.random.randn(20, 1))

with tabs[1]:
    st.markdown("### 🛠️ 내 노드 채굴 현황")
    st.write("GPU 기여를 통해 실시간으로 WH 코인을 생산 중입니다.")
    st.progress(65, text="GPU 연산 가동률 65%")

# --- 탭 3: 미니게임 (난이도 및 참가비 시스템) ---
with tabs[2]:
    st.markdown("### 🕹️ 닷지 생존 미션 (P2E)")
    st.warning("⚠️ 게임 시작 시 **참가비 0.1 WH**가 지갑에서 차감됩니다.")
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        diff = st.radio("난이도 선택", ["하 (보통)", "중 (어려움)", "상 (매우 어려움)"], horizontal=True)
    with col_opt2:
        if diff == "하 (보통)": st.info("보상: 10초당 0.05 WH")
        elif diff == "중 (어려움)": st.info("보상: 10초당 0.1 WH")
        else: st.error("보상: 10초당 1.0 WH (강력 추천)")

    if not st.session_state.game_active:
        if st.button("🚀 게임 시작 (참가비 0.1 WH 차감)", use_container_width=True):
            if st.session_state.balance >= 0.1:
                st.session_state.balance -= 0.1
                st.session_state.game_active = True
                st.rerun()
            else:
                st.error("잔액이 부족합니다!")
    else:
        # 난이도 수치 설정
        speed_rate = 1.0
        if "중" in diff: speed_rate = 1.5
        if "상" in diff: speed_rate = 2.5

        if st.button("⏹️ 게임 종료 및 리셋"):
            st.session_state.game_active = False
            st.rerun()

        game_js = f"""
        <div style="text-align:center;">
            <canvas id="dodgeCanvas" width="500" height="350" style="border:3px solid #FFD700; background:#000; cursor:crosshair;"></canvas>
            <h2 id="timerDisplay" style="color:#FFD700;">생존 시간: 0.00초</h2>
            <p id="rewardHint" style="color:#888;">마우스가 화면을 나가면 즉시 종료됩니다!</p>
        </div>
        <script>
            const canvas = document.getElementById("dodgeCanvas");
            const ctx = canvas.getContext("2d");
            let startTime = Date.now();
            let player = {{ x: 250, y: 175, r: 6 }};
            let bullets = [];
            let gameOver = false;
            let finalTime = 0;
            const speedMult = {speed_rate};

            canvas.onmousemove = e => {{
                if(gameOver) return;
                const rect = canvas.getBoundingClientRect();
                player.x = e.clientX - rect.left;
                player.y = e.clientY - rect.top;
            }};

            canvas.onmouseleave = () => {{
                if(!gameOver) {{ gameOver = true; finalTime = (Date.now() - startTime)/1000; }}
            }};

            function spawnBullet() {{
                const side = Math.floor(Math.random() * 4);
                let b = {{ r: 3, x: 0, y: 0, vx: 0, vy: 0 }};
                if(side==0){{ b.x=0; b.y=Math.random()*350; b.vx=(2+Math.random()*2)*speedMult; b.vy=(Math.random()-0.5)*4; }}
                else if(side==1){{ b.x=500; b.y=Math.random()*350; b.vx=(-2-Math.random()*2)*speedMult; b.vy=(Math.random()-0.5)*4; }}
                else if(side==2){{ b.x=Math.random()*500; b.y=0; b.vx=(Math.random()-0.5)*4; b.vy=(2+Math.random()*2)*speedMult; }}
                else {{ b.x=Math.random()*500; b.y=350; b.vx=(Math.random()-0.5)*4; b.vy=(-2-Math.random()*2)*speedMult; }}
                bullets.push(b);
            }}

            function update() {{
                if(gameOver) return;
                let elapsed = (Date.now() - startTime) / 1000;
                document.getElementById("timerDisplay").innerText = "생존 시간: " + elapsed.toFixed(2) + "초";
                if(bullets.length < 30 + (elapsed*2)) spawnBullet();
                bullets.forEach((b, i) => {{
                    b.x += b.vx; b.y += b.vy;
                    if(b.x<-10||b.x>510||b.y<-10||b.y>360) bullets.splice(i, 1);
                    let dx = b.x - player.x; let dy = b.y - player.y;
                    if(Math.sqrt(dx*dx+dy*dy) < b.r + player.r) {{ gameOver = true; finalTime = elapsed; }}
                }});
            }}

            function draw() {{
                ctx.clearRect(0,0,500,350);
                if(!gameOver) {{
                    ctx.fillStyle = "#FFD700"; ctx.beginPath(); ctx.arc(player.x, player.y, player.r, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle = "#FF4B4B"; bullets.forEach(b => {{ ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); }});
                }} else {{
                    ctx.fillStyle = "#FF4B4B"; ctx.font = "bold 30px sans-serif"; ctx.fillText("GAME OVER", 160, 150);
                    ctx.fillStyle = "#FFF"; ctx.font = "20px sans-serif"; ctx.fillText(finalTime.toFixed(2) + "초 생존!", 190, 190);
                    ctx.fillStyle = "#FFD700"; ctx.font = "16px sans-serif"; ctx.fillText("난이도별 보상 조건 확인 후 수령하세요", 130, 230);
                }}
                requestAnimationFrame(() => {{ update(); draw(); }});
            }}
            draw();
        </script>
        """
        components.html(game_js, height=500)
        
        st.write("보상은 10초 단위로 계산됩니다.")
        if st.button("🎁 보상 수령하기"):
            # 실제로는 스코어를 연동해야 하지만 시뮬레이션으로 수령 버튼 구현
            st.session_state.balance += 0.1 # 예시 보상
            st.success("보상이 지급되었습니다!")
            st.session_state.game_active = False
            st.rerun()

# --- 탭 4: 럭키 주사위 (완벽 복구) ---
with tabs[3]:
    st.markdown("### 🎲 럭키 주사위 (LUCKY DICE)")
    st.write("주사위 눈이 4, 5, 6이 나오면 배팅액의 2배를 드립니다!")
    
    bet = st.selectbox("배팅액 (WH)", [10, 50, 100, 500])
    
    if st.button("주사위 던지기!", use_container_width=True):
        if st.session_state.balance >= bet:
            st.session_state.balance -= bet
            with st.spinner("던지는 중..."):
                time.sleep(0.5)
                res = random.randint(1, 6)
                st.title(f"🎲 {res}")
                if res >= 4:
                    st.session_state.balance += (bet * 2)
                    st.balloons()
                    st.success(f"축하합니다! {bet * 2} WH 당첨!")
                else:
                    st.error("아쉽네요. 다음 기회에!")
            st.rerun()
        else:
            st.error("잔액이 부족합니다.")

# --- 탭 5: 관리자 패널 (보안 유지) ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.subheader("👑 마스터 통제실")
        st.write("전체 유저 보상률과 시스템을 통제합니다.")
        st.metric("시스템 총 수익", "12,480 SOL")
        st.button("수익금 정산하기")
