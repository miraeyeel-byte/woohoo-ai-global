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

# 4. [디자인]
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    .stApp { background-color: #050505 !important; color: #E0E0E0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3 { color: #FFD700 !important; font-weight: 900 !important; }
    .stTabs [aria-selected="true"] { background-color: #FFD700 !important; color: #000 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 5. 헤더 및 사이드바
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔑 지갑 센터")
    if not st.session_state.wallet_address:
        if st.button("내 지갑 연결 (Phantom)", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.rerun()
    else:
        is_owner = (st.session_state.wallet_address == OWNER_WALLET)
        st.info(f"연결됨: {st.session_state.wallet_address[:12]}...")
        st.write(f"보유 잔액: **{st.session_state.balance:,.2f} WH**")
        if is_owner: st.warning("⚠️ MASTER ADMIN")
        if st.button("연결 해제"):
            st.session_state.wallet_address = None
            st.rerun()

# 6. 탭 구성 (주사위 게임 복구)
tabs_list = ["🌐 현황", "🛠️ AI 노드", "🕹️ 닷지 게임", "🎲 럭키 주사위"]
if st.session_state.wallet_address == OWNER_WALLET:
    tabs_list.append("👑 관리자")

tabs = st.tabs(tabs_list)

# --- 탭 1 & 2 (생략/유지) ---
with tabs[0]: st.subheader("네트워크 통계"); st.line_chart(np.random.randn(20, 1))
with tabs[1]: st.subheader("내 노드 채굴 현황"); st.write("가동 중...")

# --- 탭 3: 미니게임 (버그 수정판) ---
with tabs[2]:
    st.markdown("### 🕹️ 극한의 닷지 (60초 생존 미션)")
    st.write("마우스가 화면을 벗어나면 즉시 탈락입니다!")

    if not st.session_state.game_active:
        if st.button("🚀 게임 시작", use_container_width=True):
            st.session_state.game_active = True
            st.rerun()
    else:
        if st.button("⏹️ 게임 리셋"):
            st.session_state.game_active = False
            st.rerun()
        
        game_js = """
        <div style="text-align:center;">
            <canvas id="dodgeCanvas" width="500" height="400" style="border:3px solid #FFD700; background:#000; cursor:crosshair;"></canvas>
            <h2 id="timerDisplay" style="color:#FFD700;">생존 시간: 0.00초</h2>
        </div>
        <script>
            const canvas = document.getElementById("dodgeCanvas");
            const ctx = canvas.getContext("2d");
            let startTime = Date.now();
            let player = { x: 250, y: 200, r: 6 };
            let bullets = [];
            let gameOver = false;
            let statusMsg = "";

            // 마우스 이동 시 좌표 업데이트
            canvas.onmousemove = e => {
                if(gameOver) return;
                const rect = canvas.getBoundingClientRect();
                player.x = e.clientX - rect.left;
                player.y = e.clientY - rect.top;
            };

            // [버그 수정] 마우스가 캔버스를 나가면 즉시 종료
            canvas.onmouseleave = () => {
                if(!gameOver) {
                    gameOver = true;
                    statusMsg = "이탈로 인한 실격!";
                }
            };

            function spawnBullet(elapsed) {
                const side = Math.floor(Math.random() * 4);
                let speedMult = 1 + (elapsed / 20); // 시간 지날수록 빨라짐
                let b = { r: 3 + Math.random()*2, x: 0, y: 0, vx: 0, vy: 0 };
                if(side==0){ b.x=0; b.y=Math.random()*400; b.vx=(2+Math.random()*3)*speedMult; b.vy=(Math.random()-0.5)*4; }
                else if(side==1){ b.x=500; b.y=Math.random()*400; b.vx=(-2-Math.random()*3)*speedMult; b.vy=(Math.random()-0.5)*4; }
                else if(side==2){ b.x=Math.random()*500; b.y=0; b.vx=(Math.random()-0.5)*4; b.vy=(2+Math.random()*3)*speedMult; }
                else { b.x=Math.random()*500; b.y=400; b.vx=(Math.random()-0.5)*4; b.vy=(-2-Math.random()*3)*speedMult; }
                bullets.push(b);
            }

            function update() {
                if(gameOver) return;
                let elapsed = (Date.now() - startTime) / 1000;
                document.getElementById("timerDisplay").innerText = "생존 시간: " + elapsed.toFixed(2) + "초";
                
                if(bullets.length < (40 + elapsed)) spawnBullet(elapsed);

                bullets.forEach((b, i) => {
                    b.x += b.vx; b.y += b.vy;
                    if(b.x<-20||b.x>520||b.y<-20||b.y>420) bullets.splice(i, 1);
                    
                    let dx = b.x - player.x; let dy = b.y - player.y;
                    if(Math.sqrt(dx*dx+dy*dy) < b.r + player.r) {
                        gameOver = true;
                        statusMsg = elapsed.toFixed(2) + "초 생존 실패!";
                    }
                });
            }

            function draw() {
                ctx.clearRect(0,0,500,400);
                if(!gameOver) {
                    // 플레이어
                    ctx.shadowBlur = 10; ctx.shadowColor = "#FFD700";
                    ctx.fillStyle = "#FFD700"; ctx.beginPath(); ctx.arc(player.x, player.y, player.r, 0, Math.PI*2); ctx.fill();
                    // 총알
                    ctx.shadowBlur = 0; ctx.fillStyle = "#FF4B4B"; 
                    bullets.forEach(b => { ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); });
                } else {
                    ctx.shadowBlur = 0; ctx.fillStyle = "#FF4B4B"; ctx.font = "bold 35px sans-serif";
                    ctx.fillText("GAME OVER", 145, 160);
                    ctx.fillStyle = "#FFF"; ctx.font = "20px sans-serif";
                    ctx.fillText(statusMsg, 165, 200);
                    ctx.fillStyle = "#FFD700"; ctx.font = "16px sans-serif";
                    ctx.fillText("60초 생존 시 보너스 코인 지급", 145, 240);
                }
                requestAnimationFrame(() => { update(); draw(); });
            }
            draw();
        </script>
        """
        components.html(game_js, height=550)
        if st.button("🎁 60초 달성 보상 받기 (0.1 WH)"):
            st.session_state.balance += 0.1
            st.success("입금 완료!")

# --- 탭 4: 럭키 주사위 (복구) ---
with tabs[3]:
    st.markdown("### 🎲 럭키 주사위 (High Risk)")
    bet_amt = st.select_slider("배팅액 선택", options=[1, 5, 10, 50, 100])
    if st.button("주사위 굴리기", use_container_width=True):
        if st.session_state.balance >= bet_amt:
            st.session_state.balance -= bet_amt
            result = random.randint(1, 6)
            st.write(f"결과: **{result}**")
            if result >= 5:
                prize = bet_amt * 2
                st.session_state.balance += prize
                st.balloons(); st.success(f"당첨! {prize} WH 획득!")
            else:
                st.error("꽝! 다음 기회에...")
            st.rerun()
        else:
            st.error("잔액이 부족합니다.")

# --- 탭 5: 관리자 전용 ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[4]:
        st.subheader("👑 마스터 통제실")
        st.write("운영자님 전용 탭입니다.")
        st.button("전체 시스템 리셋")
