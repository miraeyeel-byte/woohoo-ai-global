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
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')
db_lock = threading.Lock()

# 2. DB 커넥션 (호환성 극대화 버전)
@st.cache_resource
def get_db_conn():
    # WAL 모드 제거하여 서버 환경 호환성 확보
    conn = sqlite3.connect('woohoo_final_v82.db', check_same_thread=False)
    return conn

def init_db():
    try:
        conn = get_db_conn()
        with db_lock:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, nodes INTEGER)''')
            c.execute('''CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))''')
            c.execute('''CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK (id=1), treasury REAL)''')
            c.execute("INSERT OR IGNORE INTO system_state (id, treasury) VALUES (1, 1000.0)")
            c.execute('''CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS bot_lock (id INTEGER PRIMARY KEY CHECK(id=1), last_heartbeat REAL)''')
            conn.commit()
    except Exception as e:
        st.error(f"DB 초기화 실패: {e}")

init_db()

# 3. 전역 설정
GAME_CONFIG = {
    "DODGE_FEE": 0.05, "DODGE_REWARD": 0.1, "DODGE_MIN_TIME": 10.0,
    "FUSE_SUCCESS": 0.75, "MAX_LEVEL": 6, "WH_PRICE": 1.00,
    "DICE_X6": 2.0, "DICE_X5": 1.2, "CHAT_LIMIT": 200
}
OWNER_WALLET = os.getenv("OWNER_WALLET", "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx")
APP_MODE = os.getenv("APP_MODE", "DEMO")

# 4. 세션 상태 초기화 (삭제 금지)
if 'session_id' not in st.session_state: st.session_state.session_id = uuid.uuid4().hex[:8]
for key, val in {
    'wallet_address': None, 'is_admin': False, 'balance': 10.0, 'heroes': {},
    'global_treasury': 1000.0, 'dice_status': "idle", 'dodge_run': False, 'chat_paused': False
}.items():
    if key not in st.session_state: st.session_state[key] = val

# 5. 핵심 비즈니스 로직 (트랜잭션)
def process_tx(u_delta, h_delta, reason):
    if st.session_state.balance + u_delta < 0: return False
    try:
        conn = get_db_conn()
        with db_lock:
            st.session_state.balance += u_delta
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", (st.session_state.wallet_address, st.session_state.balance, 0))
            c.execute("UPDATE system_state SET treasury = treasury + ? WHERE id=1", (h_delta,))
            c.execute("SELECT treasury FROM system_state WHERE id=1")
            st.session_state.global_treasury = c.fetchone()[0]
            conn.commit()
        return True
    except: return False

# 6. UI 및 디자인 (입체 음양 테마)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Noto+Sans+KR:wght@700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] {
        color: #FFFFFF !important; font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 4px #000, -2px -2px 4px #000 !important;
    }
    h1, h2, h3, h4 { color: #FFD700 !important; font-family: 'Orbitron' !important; text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.7); }
    .premium-card { background: linear-gradient(145deg, #1e1e1e, #050505); border: 2px solid #FFD700; border-radius: 20px; padding: 15px; box-shadow: 10px 10px 25px #000; text-align: center; margin-bottom: 20px; }
    .hero-card { background: #111; border: 1px solid #FFD700; border-radius: 15px; padding: 10px; width: 180px; margin: 0 auto 10px auto; text-align: center; }
    .char-img { font-size: 80px !important; filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.8)); margin: 5px 0; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 7. 레이아웃 (헤더/사이드바)
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO V8.2 PRO</h1>", unsafe_allow_html=True)

with st.sidebar:
    if not st.session_state.wallet_address:
        if APP_MODE == "DEMO" and st.button("👑 운영자 연결"):
            st.session_state.wallet_address, st.session_state.is_admin, st.session_state.balance = OWNER_WALLET, True, 1000000.0; st.rerun()
    else:
        st.markdown(f"<div class='premium-card'><b>BALANCE</b><h2>{st.session_state.balance:,.2f} WH</h2></div>", unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.clear(); st.rerun()

# 8. 탭 구성 (가장 안정적인 방식)
tabs = st.tabs(["🌐 현황", "🛠️ 노드", "🕹️ 닷지", "🎲 주사위", "🐲 히어로", "💬 채팅"])

# --- 탭 0: 현황 (사진 3 복구) ---
with tabs[0]:
    st.markdown("### 🌐 NETWORK STATUS")
    st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['Power']), color=["#FFD700"])

# --- 탭 2: 닷지 ---
with tabs[2]:
    if st.button("🚀 START"):
        if process_tx(-GAME_CONFIG['DODGE_FEE'], GAME_CONFIG['DODGE_FEE'], "DODGE_START"):
            st.session_state.update({"last_dodge_start": time.time(), "dodge_claimed": False, "dodge_run": True}); st.rerun()
    if st.session_state.dodge_run:
        components.html("<html><body style='background:black;'><canvas id='dg' width='500' height='300'></canvas></body></html>", height=320)
        if not st.session_state.get('dodge_claimed') and st.button("🎁 CLAIM"):
            elapsed = time.time() - st.session_state.last_dodge_start
            if elapsed >= GAME_CONFIG['DODGE_MIN_TIME']:
                if process_tx(GAME_CONFIG['DODGE_REWARD'], -GAME_CONFIG['DODGE_REWARD'], "DODGE_CLAIM"):
                    st.session_state.dodge_claimed = True; st.success("SUCCESS")
            else: st.error(f"실패: {elapsed:.1f}s")

# --- 탭 3: 주사위 (사진 1 컬럼 에러 완벽 해결) ---
@st.fragment
def dice_section():
    if st.session_state.dice_status == "rolling":
        p = st.empty()
        for _ in range(12): p.markdown(f"<h1 style='text-align:center;'>🎲 {random.choice(['⚀','⚁','⚂','⚃','⚄','⚅'])}</h1>", unsafe_allow_html=True); time.sleep(0.08)
        st.session_state.dice_res = [random.randint(1,6) for _ in range(st.session_state.get('rc', 1))]
        st.session_state.dice_status = "done"; st.rerun()
    elif st.session_state.dice_status == "done":
        results = st.session_state.get('dice_res', [])
        if results: # [수정] 결과가 있을 때만 렌더링 (사진 1 에러 방지)
            cols = st.columns(len(results))
            for i, r in enumerate(results):
                cols[i].markdown(f"<h1 style='text-align:center;'>{r}</h1>", unsafe_allow_html=True)
        st.button("RETRY", on_click=lambda: st.session_state.update({"dice_status":"idle"}))
    else:
        bet = st.selectbox("BET", [1, 10, 100])
        if st.button("ROLL!"):
            if process_tx(-bet, 0, "DICE_BET"):
                st.session_state.update({"cur_bet": bet, "rc": 1, "dice_status": "rolling"}); st.rerun()

with tabs[3]: dice_section()

# --- 탭 4: 히어로 (사진 2 UI 최적화) ---
with tabs[4]:
    h_icons = {1:"💧", 2:"👺", 3:"👹", 4:"🐎", 5:"🐉", 6:"👼"}
    if st.button("소환 (90 WH / 10회)"):
        if process_tx(-90, 90, "SUMMON"): st.session_state.heroes[1] = st.session_state.heroes.get(1,0)+10; st.rerun()
    for lvl, cnt in sorted(st.session_state.heroes.items()):
        if cnt > 0:
            st.markdown(f"<div class='hero-card'><div class='char-img'>{h_icons.get(lvl)}</div> Lv.{lvl} ({cnt}개)</div>", unsafe_allow_html=True)
            if lvl < GAME_CONFIG['MAX_LEVEL'] and cnt >= 2 and st.button(f"합성", key=f"f_{lvl}"):
                st.session_state.heroes[lvl] -= 2
                if random.random() < GAME_CONFIG['FUSE_SUCCESS']:
                    st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+1; st.success("성공")
                st.rerun()

# --- 탭 5: 채팅 ---
@st.fragment(run_every=5)
def chat_tab():
    try:
        conn = get_db_conn()
        chats = conn.cursor().execute("SELECT wallet, message, time FROM chat ORDER BY id DESC LIMIT 15").fetchall()[::-1]
        box = "<div style='background:#0a0a0a; border:1px solid #333; height:300px; overflow-y:auto; padding:10px; font-size:14px;'>"
        for w, m, t in chats:
            box += f"<div><b>{w[:6]}..</b>: {m} <small style='float:right; color:#444;'>{t}</small></div>"
        st.markdown(box + "</div>", unsafe_allow_html=True)
    except: st.write("채팅 로딩 중...")

with tabs[5]: chat_tab()
