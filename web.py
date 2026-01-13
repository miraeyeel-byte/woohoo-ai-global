import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 정보 및 세션 관리
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'balance' not in st.session_state:
    st.session_state.balance = 1000 # 테스트용 기본금
if 'token_symbol' not in st.session_state:
    st.session_state.token_symbol = "WH"

# 3. [디자인] 사이버펑크 스타일
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    .stApp { background-color: #050505 !important; color: #E0E0E0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3 { color: #FFD700 !important; font-weight: 900 !important; }
    .game-container { border: 2px solid #FFD700; border-radius: 10px; padding: 10px; background: #000; }
    </style>
    """, unsafe_allow_html=True)

# 4. 상단 헤더
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI 하이퍼-코어</h1>", unsafe_allow_html=True)

# 5. 사이드바 - 지갑 관리
with st.sidebar:
    st.markdown("### 🔑 지갑 센터")
    if not st.session_state.wallet_address:
        if st.button("내 지갑 연결 (Phantom)", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.is_admin = True
            st.rerun()
    else:
        st.success(f"연결됨: {st.session_state.wallet_address[:8]}...")
        st.write(f"현재 잔액: **{st.session_state.balance:,.2f} {st.session_state.token_symbol}**")
        if st.button("연결 해제"):
            st.session_state.wallet_address = None
            st.session_state.is_admin = False
            st.rerun()

# 6. 메인 탭 메뉴
tabs = st.tabs(["📊 네트워크", "🛠️ AI 노드", "🕹️ 아케이드 (게임)", "👑 관리자"])

# --- 탭 1 & 2는 기존 내용 유지 (생략 가능, 여기서는 게임 탭에 집중) ---

with tabs[2]:
    st.markdown("### 🕹️ 우주 방어 미니게임 (WOOHOO Defender)")
    st.write("적 기체를 10대 이상 격추하면 **1 WH 코인**을 보상으로 드립니다! (키보드 화살표와 스페이스바 사용)")

    # 자바스크립트 게임 엔진 (HTML5 Canvas)
    game_html = """
    <div style="text-align:center;">
        <canvas id="gameCanvas" width="600" height="400" style="border:1px solid #FFD700; background:#000;"></canvas>
        <h2 id="scoreDisplay" style="color:#FFD700; font-family:sans-serif;">점수: 0</h2>
    </div>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        let score = 0;
        let player = { x: 280, y: 350, w: 40, h: 40, speed: 7 };
        let bullets = [];
        let enemies = [];
        let keys = {};

        window.addEventListener("keydown", e => keys[e.code] = true);
        window.addEventListener("keyup", e => keys[e.code] = false);

        function update() {
            if (keys["ArrowLeft"] && player.x > 0) player.x -= player.speed;
            if (keys["ArrowRight"] && player.x < canvas.width - player.w) player.x += player.speed;
            if (keys["Space"]) {
                if (bullets.length < 5) bullets.push({ x: player.x + 18, y: player.y, w: 4, h: 10 });
                keys["Space"] = false; // 단발 사격
            }

            bullets.forEach((b, i) => {
                b.y -= 10;
                if (b.y < 0) bullets.splice(i, 1);
            });

            if (Math.random() < 0.03) enemies.push({ x: Math.random() * 560, y: 0, w: 30, h: 30 });

            enemies.forEach((e, ei) => {
                e.y += 3;
                bullets.forEach((b, bi) => {
                    if (b.x < e.x + e.w && b.x + b.w > e.x && b.y < e.y + e.h && b.y + b.h > e.y) {
                        enemies.splice(ei, 1);
                        bullets.splice(bi, 1);
                        score++;
                        document.getElementById("scoreDisplay").innerText = "점수: " + score;
                    }
                });
                if (e.y > canvas.height) enemies.splice(ei, 1);
            });
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#FFD700"; // 플레이어 색상 (금색)
            ctx.fillRect(player.x, player.y, player.w, player.h);
            ctx.fillStyle = "#FFF"; // 미사일
            bullets.forEach(b => ctx.fillRect(b.x, b.y, b.w, b.h));
            ctx.fillStyle = "#F00"; // 적군
            enemies.forEach(e => ctx.fillRect(e.x, e.y, e.w, e.h));
            requestAnimationFrame(() => { update(); draw(); });
        }
        draw();
    </script>
    """
    
    components.html(game_html, height=500)

    # 보상 수령 섹션
    st.write("---")
    reward_col1, reward_col2 = st.columns([2, 1])
    with reward_col1:
        st.write("💡 **보상 조건**: 게임에서 적 기체 10대 이상 격추")
    with reward_col2:
        if st.button("🎁 보상 받기 (1 WH)"):
            # 실제로는 게임 스코어를 JS에서 파이썬으로 넘겨받아야 하지만, 
            # 여기서는 간단히 클릭 시 지급으로 구현했습니다.
            st.session_state.balance += 1
            st.balloons()
            st.success("1 WH 코인이 지급되었습니다!")
            time.sleep(1)
            st.rerun()

# --- 탭 3: 마스터 컨트롤 (관리자) ---
if st.session_state.is_admin:
    with tabs[3]:
        st.markdown("## 👑 운영자 마스터 패널")
        st.write(f"접속 지갑: `{st.session_state.wallet_address}`")
        
        st.divider()
        col_admin1, col_admin2 = st.columns(2)
        with col_admin1:
            st.subheader("🪙 토큰 발행 관리")
            st.session_state.token_name = st.text_input("코인 이름", value="WOOHOO AI")
            st.session_state.token_symbol = st.text_input("코인 심볼", value="WH")
            st.button("정보 업데이트")

        with col_admin2:
            st.subheader("📈 게임 보상 설정")
            game_reward = st.number_input("판당 보상액 (WH)", value=1)
            st.write(f"현재 설정된 보상: {game_reward} WH")
            st.button("보상 설정 저장")
