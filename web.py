import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components
import os
import sqlite3
import uuid
import logging
import threading
import html
import re

# 1. 시스템 설정 및 로깅
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
db_lock = threading.Lock()

# 2. 전역 설정 (중앙 관리)
GAME_CONFIG = {
    "SUMMON_1_COST": 10,
    "SUMMON_10_COST": 90,
    "FUSE_SUCCESS_RATE": 0.75,
    "MAX_LEVEL": 6,
    "DICE_X6": 2.0, "DICE_X5": 1.2,
    "CHAT_LIMIT": 200, "CHAT_DELAY": 1.5,
    "BLOCK_WORDS": ["출금", "돈", "수익", "원", "솔", "토큰", "환전"]
}

OWNER_WALLET = os.getenv("OWNER_WALLET", "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx")
APP_MODE = os.getenv("APP_MODE", "DEMO")

# 3. DB 커넥션 (호환성 극대화 표준 모드)
def get_db_conn():
    # timeout을 늘려 서버 환경의 지연 시간에 대비함
    return sqlite3.connect('woohoo_final_v93.db', timeout=30, check_same_thread=False)

def init_db():
    try:
        with get_db_conn() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, nodes INTEGER)''')
            c.execute('''CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))''')
            c.execute('''CREATE TABLE IF NOT EXISTS vault (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))''')
            c.execute('''CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK (id=1), treasury REAL)''')
            c.execute("INSERT OR IGNORE INTO system_state (id, treasury) VALUES (1, 1000.0)")
            c.execute('''CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS bot_lock (id INTEGER PRIMARY KEY CHECK(id=1), last_heartbeat REAL)''')
            conn.commit()
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {e}")

init_db()

# 4. 세션 상태 초기화 (AttributeError 방지)
if 'session_id' not in st.session_state: st.session_id = uuid.uuid4().hex[:8]
if 'treasury_loaded' not in st.session_state:
    try:
        with get_db_conn() as conn:
            st.session_state.global_treasury = conn.execute("SELECT treasury FROM system_state WHERE id=1").fetchone()[0]
        st.session_state.treasury_loaded = True
    except: st.session_state.global_treasury = 1000.0

for key, val in {
    'wallet_address': None, 'is_admin': False, 'balance': 10.0,
    'heroes': {}, 'vault': {}, 'owned_nodes': 0, 'dice_status': "idle"
}.items():
    if key not in st.session_state: st.session_state[key] = val

# 5. 핵심 비즈니스 로직
def process_transaction(u_delta, h_delta, reason):
    if st.session_state.balance + u_delta < 0: return False
    with db_lock:
        try:
            with get_db_conn() as conn:
                c = conn.cursor()
                st.session_state.balance += u_delta
                c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", (st.session_state.wallet_address, st.session_state.balance, st.session_state.owned_nodes))
                c.execute("UPDATE system_state SET treasury = treasury + ? WHERE id=1", (h_delta,))
                # 인벤토리 및 보관소 동시 저장
                for lvl, cnt in st.session_state.heroes.items():
                    c.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet_address, lvl, cnt))
                for lvl, cnt in st.session_state.vault.items():
                    c.execute("INSERT OR REPLACE INTO vault VALUES (?, ?, ?)", (st.session_state.wallet_address, lvl, cnt))
                conn.commit()
                st.session_state.global_treasury = conn.execute("SELECT treasury FROM system_state WHERE id=1").fetchone()[0]
            return True
        except: return False

def load_user_data(wallet):
    with db_lock:
        with get_db_conn() as conn:
            c = conn.cursor()
            u = c.execute("SELECT balance, nodes FROM users WHERE wallet=?", (wallet,)).fetchone()
            if u:
                st.session_state.balance, st.session_state.owned_nodes = u
                st.session_state.heroes = dict(c.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (wallet,)).fetchall())
                st.session_state.vault = dict(c.execute("SELECT lvl, count FROM vault WHERE wallet=?", (wallet,)).fetchall())

# 6. UI 및 디자인 (그래프 툴팁 시인성 확보 버전)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Noto+Sans+KR:wght@700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body { color: #FFFFFF !important; font-family: 'Noto Sans KR', sans-serif !important; }
    
    /* 카드와 제목에만 입체 효과 적용 (그래프 툴팁 간섭 방지) */
    h1, h2, h3, h4, .premium-card, .hero-card {
        text-shadow: 2px 2px 5px #000 !important;
    }
    h1, h2, h3, h4 { color: #FFD700 !important; font-family: 'Orbitron' !important; }
    
    .premium-card {
        background: linear-gradient(145deg, #1e1e1e, #050505);
        border: 2px solid #FFD700; border-radius: 20px; padding: 15px;
        box-shadow: 10px 10px 25px #000; text-align: center; margin-bottom: 20px;
    }
    .hero-card {
        background: #111; border: 1px solid #FFD700; border-radius: 15px;
        padding: 10px; width: 180px; margin: 0 auto 10px auto; text-align: center;
    }
    .char-img { font-size: 70px !important; filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.8)); margin: 5px 0; }
    .chat-box { background: #0a0a0a; border: 1px solid #333; border-radius: 10px; padding: 10px; height: 350px; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

# 7. 레이아웃
st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO V9.3 MASTER</h1>", unsafe_allow_html=True)

with st.sidebar:
    if not st.session_state.wallet_address:
        if APP_MODE == "DEMO" and st.button("👑 운영자 연결"):
            st.session_state.wallet_address, st.session_state.is_admin = OWNER_WALLET, True
            load_user_data(OWNER_WALLET); st.rerun()
    else:
        st.markdown(f"<div class='premium-card'><b>{st.session_state.balance:,.2f} WH</b></div>", unsafe_allow_html=True)
        if st.button("지갑 연결 해제"): st.session_state.clear(); st.rerun()

# 8. 탭 구성 (가장 안정적인 리스트 방식)
tabs = st.tabs(["🌐 현황", "🛠️ 노드 분양", "🎲 주사위 게임", "🐲 히어로 소환 & 보관", "💬 채팅창"])

# --- 탭 0: 현황 (마우스 오버 정상화) ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL NETWORK STATUS")
    # CSS 간섭을 줄여 마우스 오버 시 수치가 정확히 보임
    st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['Power']), color=["#FFD700"])

# --- 탭 1: 노드 분양 ---
with tabs[1]:
    st.markdown("### 🛠️ MASTER NODE MINTING")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><h4>MASTER NODE</h4><p>일일 50 WH 수익 창출</p></div>", unsafe_allow_html=True)
        if st.button("노드 민팅 시작"):
            st.session_state.owned_nodes += 1; process_transaction(0, 0, "NODE_MINT"); st.success("분양 완료!")
    with c2: st.metric("내 보유 노드", f"{st.session_state.owned_nodes} 개")

# --- 탭 2: 주사위 게임 (에러 방지 강화) ---
@st.fragment
def dice_section():
    if st.session_state.dice_status == "rolling":
        p = st.empty()
        for _ in range(12): p.markdown(f"<h1 style='text-align:center;'>🎲 {random.choice(['⚀','⚁','⚂','⚃','⚄','⚅'])}</h1>", unsafe_allow_html=True); time.sleep(0.08)
        st.session_state.dice_res = [random.randint(1,6)]
        st.session_state.dice_status = "done"; st.rerun()
    elif st.session_state.dice_status == "done":
        res = st.session_state.get('dice_res', [])
        if res:
            win = st.session_state.cur_bet * (GAME_CONFIG['DICE_X6'] if res[0]==6 else GAME_CONFIG['DICE_X5'] if res[0]==5 else 0)
            if win > 0: process_transaction(win, -win, "DICE_WIN"); st.balloons()
            else: process_transaction(0, st.session_state.cur_bet, "DICE_LOSE")
            st.markdown(f"<div class='premium-card'><h1>결과: {res[0]}</h1></div>", unsafe_allow_html=True)
        st.button("다시 하기", on_click=lambda: st.session_state.update({"dice_status":"idle"}))
    else:
        bet = st.selectbox("베팅액", [1, 10, 100])
        if st.button("ROLL!", use_container_width=True):
            if process_transaction(-bet, 0, "DICE_BET"):
                st.session_state.update({"cur_bet": bet, "dice_status": "rolling"}); st.rerun()

with tabs[2]: dice_section()

# --- 탭 3: 히어로 소환 & 보관 (1회 소환, 합성 글자, 보관소 복구) ---
with tabs[3]:
    st.markdown("### 🐲 HERO SUMMON & VAULT")
    h_icons = {1:"💧", 2:"👺", 3:"👹", 4:"🐎", 5:"🐉", 6:"👼"}
    
    col_p, col_i, col_v = st.columns([1.5, 2.5, 2])
    with col_p:
        st.subheader("✨ 소환")
        if st.button("1회 소환 (10 WH)", use_container_width=True): # 1회 소환 복구
            if process_transaction(-10, 10, "SUMMON_X1"):
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 1; st.rerun()
        if st.button("10회 소환 (90 WH)", use_container_width=True):
            if process_transaction(-90, 90, "SUMMON_X10"):
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 10; st.rerun()

    with col_i:
        st.subheader("🎒 가방")
        for lvl, cnt in sorted(st.session_state.heroes.items()):
            if cnt > 0:
                st.markdown(f"<div class='hero-card'><div class='char-img'>{h_icons.get(lvl)}</div> Lv.{lvl} ({cnt}개)</div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                if lvl < 6 and cnt >= 2 and c1.button("합성", key=f"f_{lvl}"): # 합성 글자 복구
                    st.session_state.heroes[lvl] -= 2
                    if random.random() < 0.75:
                        st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+1; st.success("성공")
                    st.rerun()
                if c2.button("판매", key=f"s_{lvl}"):
                    if process_transaction(10, -10, "SELL"): st.session_state.heroes[lvl] -= 1; st.rerun()
                if c3.button("보관", key=f"v_{lvl}"): # 보관소 이동 복구
                    st.session_state.heroes[lvl] -= 1
                    st.session_state.vault[lvl] = st.session_state.vault.get(lvl, 0) + 1; st.rerun()

    with col_v:
        st.subheader("🏛️ 보관소")
        for lvl, cnt in sorted(st.session_state.vault.items()):
            if cnt > 0:
                st.markdown(f"<div class='hero-card' style='border-color:#555;'>{h_icons.get(lvl)} Lv.{lvl} ({cnt})</div>", unsafe_allow_html=True)
                if st.button("가방으로", key=f"out_{lvl}", use_container_width=True): # 꺼내기 복구
                    st.session_state.vault[lvl] -= 1
                    st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl, 0) + 1; st.rerun()

# --- 탭 4: 채팅창 (안정화) ---
@st.fragment(run_every=5)
def chat_tab():
    try:
        with get_db_conn() as conn:
            chats = conn.cursor().execute("SELECT wallet, message, time FROM chat ORDER BY id DESC LIMIT 15").fetchall()[::-1]
        box = "<div class='chat-box'>"
        for w, m, t in chats:
            box += f"<div><b><span style='color:#FFD700;'>{w[:8]}</span></b>: {m} <small style='float:right; color:#444;'>{t}</small></div>"
        st.markdown(box + "</div>", unsafe_allow_html=True)
    except: st.write("채팅 불러오는 중...")
    
    if st.session_state.wallet_address:
        with st.form("chat_f", clear_on_submit=True):
            m = st.text_input("메시지", label_visibility="collapsed")
            if st.form_submit_button("전송"):
                msg = html.escape(m)
                with db_lock:
                    with get_db_conn() as conn:
                        conn.execute("INSERT INTO chat (wallet, message, time) VALUES (?, ?, ?)", (st.session_state.wallet_address, msg, time.strftime('%H:%M:%S')))
                st.rerun()
with tabs[4]: chat_tab()
