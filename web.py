import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | PRO MASTER", layout="wide")

# 2. 운영자 지갑 주소 (절대 보안)
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 100.0
if 'token_symbol' not in st.session_state:
    st.session_state.token_symbol = "WH"

# 4. [디자인] 더 선명한 한국어 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    .stApp { background-color: #050505 !important; color: #E0E0E0 !important; font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3 { color: #FFD700 !important; font-weight: 900 !important; }
    .stMetric { background: rgba(255, 215, 0, 0.05); border: 1px solid #333; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 5. 상단 헤더
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)

# 6. 사이드바 - 지갑 연결
with st.sidebar:
    st.markdown("### 🔑 지갑 센터")
    if not st.session_state.wallet_address:
        if st.button("내 지갑 연결 (Phantom)", use_container_width=True):
            # 시뮬레이션 (실제로는 여기서 팝업이 떠야함)
            st.session_state.wallet_address = OWNER_WALLET
            st.rerun()
    else:
        is_owner = (st.session_state.wallet_address == OWNER_WALLET)
        status_color = "#FFD700" if is_owner else "#FFF"
        st.markdown(f"""
            <div style="border:1px solid {status_color}; padding:10px; border-radius:5px;">
                <p style="margin:0; font-size:12px; color:#888;">지갑 주소</p>
                <p style="margin:0; font-size:14px; color:{status_color}; font-weight:bold;">{st.session_state.wallet_address[:12]}...</p>
                <p style="margin:0; font-size:12px; color:#888; margin-top:10px;">보유 잔액</p>
                <p style="margin:0; font-size:20px; font-weight:bold;">{st.session_state.balance:,.2f} {st.session_state.token_symbol}</p>
            </div>
        """, unsafe_allow_html=True)
        if is_owner:
            st.warning("⚠️ 운영자(MASTER) 권한 활성화")
        if st.button("연결 해제"):
            st.session_state.wallet_address = None
            st.rerun()

# 7. 탭 메뉴 (관리자 권한에 따라 탭 노출 제어)
tabs_to_show = ["🌐 현황", "🛠️ AI 노드 채굴", "🕹️ 미니게임"]
# 오직 운영자 지갑일 때만 [관리자] 탭 추가
if st.session_state.wallet_address == OWNER_WALLET:
    tabs_to_show.append("👑 관리자 전용")

tabs = st.tabs(tabs_to_show)

# --- 탭 1: 네트워크 현황 ---
with tabs[0]:
    st.subheader("📊 글로벌 네트워크 통계")
    col1, col2, col3 = st.columns(3)
    col1.metric("총 AI 연산력", "42.8 TFLOPS", "Normal")
    col2.metric("활성 노드", "1,042 Units", "+12")
    col3.metric("가스비", "0.00001 SOL", "Low")
    st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['연산 가치']))

# --- 탭 2: AI 노드 채굴 (내용 보강) ---
with tabs[1]:
    st.markdown("### 🛠️ 내 AI 노드 관리")
    if not st.session_state.wallet_address:
        st.error("지갑을 연결해야 채굴 현황을 볼 수 있습니다.")
    else:
        st.info("현재 운영자님의 GPU 자원이 WOOHOO AI 네트워크에 기여하고 있습니다.")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("""
            **현재 노드 상태**
            - 🟢 가동 중 (Active)
            - **기여도:** 상위 5%
            - **오늘의 보상:** +12.5 WH
            """)
            if st.button("보상 수령하기"):
                st.toast("채굴 보상이 지갑으로 전송되었습니다.")
        with c2:
            st.write("실시간 GPU 사용률 (AI 연산 작업)")
            st.bar_chart(np.random.rand(10))

# --- 탭 3: 미니게임 (닷지 게임 구현) ---
with tabs[2]:
    st.markdown("### 🕹️ 총알 피하기 (60초 생존 미션)")
    st.write("60초 동안 날아오는 총알을 피하세요! 성공 시 **0.1 WH** 지급.")

    game_js = """
    <div style="text-align:center;">
        <canvas id="dodgeCanvas" width="500" height="400" style="border:2px solid #FF4B4B; background:#000;"></canvas>
        <h2 id="timerDisplay" style="color:#FF4B4B;">시간: 0.00초</h2>
    </div>
    <script>
        const canvas = document.getElementById("dodgeCanvas");
        const ctx = canvas.getContext("2d");
        let startTime = Date.now();
        let player = { x: 250, y: 200, r: 5 };
        let bullets = [];
        let gameOver = false;

        window.onmousemove = e => {
            const rect = canvas.getBoundingClientRect();
            player.x = e.clientX - rect.left;
            player.y = e.clientY - rect.top;
        };

        function spawnBullet() {
            const side = Math.floor(Math.random() * 4);
            let b = { r: 3, x: 0, y: 0, vx: 0, vy: 0 };
            if(side==0){ b.x=0; b.y=Math.random()*400; b.vx=2+Math.random()*3; b.vy=(Math.random()-0.5)*4; }
            else if(side==1){ b.x=500; b.y=Math.random()*400; b.vx=-2-Math.random()*3; b.vy=(Math.random()-0.5)*4; }
            else if(side==2){ b.x=Math.random()*500; b.y=0; b.vx=(Math.random()-0.5)*4; b.vy=2+Math.random()*3; }
            else { b.x=Math.random()*500; b.y=400; b.vx=(Math.random()-0.5)*4; b.vy=-2-Math.random()*3; }
            bullets.push(b);
        }

        function update() {
            if(gameOver) return;
            let elapsed = (Date.now() - startTime) / 1000;
            document.getElementById("timerDisplay").innerText = "시간: " + elapsed.toFixed(2) + "초";
            
            if(bullets.length < 50) spawnBullet();

            bullets.forEach((b, i) => {
                b.x += b.vx; b.y += b.vy;
                if(b.x<0||b.x>500||b.y<0||b.y>400) bullets.splice(i, 1);
                let dx = b.x - player.x; let dy = b.y - player.y;
                if(Math.sqrt(dx*dx+dy*dy) < b.r + player.r) {
                    gameOver = true;
                    alert("게임 오버! " + elapsed.toFixed(2) + "초 생존");
                    location.reload();
                }
            });
        }

        function draw() {
            ctx.clearRect(0,0,500,400);
            ctx.fillStyle = "#FFD700"; ctx.beginPath(); ctx.arc(player.x, player.y, player.r, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#FF4B4B"; bullets.forEach(b => { ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill(); });
            if(!gameOver) requestAnimationFrame(() => { update(); draw(); });
        }
        draw();
    </script>
    """
    components.html(game_js, height=550)
    
    if st.button("🎁 60초 생존 보상 받기 (0.1 WH)"):
        st.session_state.balance += 0.1
        st.success("0.1 WH가 지갑으로 입금되었습니다!")
        st.rerun()

# --- 탭 4: 관리자 전용 (오직 운영자 지갑일 때만 렌더링) ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[3]:
        st.markdown("## 👑 마스터 운영 대시보드")
        st.write("유저들은 이 탭을 볼 수 없습니다. 오직 마스터 지갑만 접근 가능합니다.")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.subheader("⚙️ 보상 벨런스 조절")
            new_reward = st.slider("게임 보상 (WH)", 0.0, 1.0, 0.1)
            st.button("적용하기")
        with col_a2:
            st.subheader("💰 마스터 금고")
            st.title("8,520 SOL")
            st.button("내 주소로 수수료 출금")
