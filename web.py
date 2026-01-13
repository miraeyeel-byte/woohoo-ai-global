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
    "BLOCK_WORDS": ["출금", "돈", "수익", "벌었", "원", "솔", "토큰", "환전"]
}

OWNER_WALLET = os.getenv("OWNER_WALLET", "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx")
APP_MODE = os.getenv("APP_MODE", "DEMO")

# 3. DB 커넥션 및 무결성 초기화 (OperationalError 방지 표준 모드)
def get_db_conn():
    return sqlite3.connect('woohoo_master_v92.db', timeout=30, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, nodes INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))''')
        c.execute('''CREATE TABLE IF NOT EXISTS vault (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK (id=1), treasury REAL)''')
        c.execute("INSERT OR IGNORE INTO system_state (id, treasury) VALUES (1, 1000.0)")
        c.execute('''CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS bot_lock (id INTEGER PRIMARY KEY CHECK(id=1), last_heartbeat REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tx_history (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, reason TEXT, user_delta REAL, house_delta REAL, time REAL)''')
        conn.commit()

init_db()

# 4. [Singleton] 시스템 봇 (좀비 프로세스 방지 하트비트)
def try_start_bot():
    with get_db_conn() as conn:
        c = conn.cursor()
        now = time.time()
        try:
            c.execute("INSERT INTO bot_lock (id, last_heartbeat) VALUES (1, ?)", (now,))
            conn.commit(); return True
        except sqlite3.IntegrityError:
            c.execute("SELECT last_heartbeat FROM bot_lock WHERE id=1")
            last_hb = c.fetchone()[0]
            if now - last_hb > 120:
                c.execute("UPDATE bot_lock SET last_heartbeat = ? WHERE id=1", (now,))
                conn.commit(); return True
            return False

def system_bot_thread():
    msgs = ["🔥 대박 당첨의 기회!", "🚀 WOOHOO 코인 가즈아!", "🐲 가디언 합성 성공 확률 UP!", "🎲 주사위 6을 노려보세요!"]
    while True:
        try:
            with get_db_conn() as conn:
                conn.execute("UPDATE bot_lock SET last_heartbeat = ? WHERE id=1", (time.time(),))
                msg = random.choice(msgs)
                conn.execute("INSERT INTO chat (wallet, message, time) VALUES (?, ?, ?)", ("⚙ SYSTEM", msg, time.strftime('%H:%M:%S')))
                conn.commit()
        except: pass
        time.sleep(random.randint(40, 80))

if try_start_bot():
    threading.Thread(target=system_bot_thread, daemon=True).start()

# 5. 핵심 비즈니스 로직 (트랜잭션 & 데이터 로드)
def process_transaction(user_delta, house_delta, reason):
    if st.session_state.balance + user_delta < 0: return False
    with db_lock:
        try:
            with get_db_conn() as conn:
                conn.execute("BEGIN IMMEDIATE")
                c = conn.cursor()
                st.session_state.balance += user_delta
                c.execute("INSERT OR REPLACE INTO users (wallet, balance, nodes) VALUES (?, ?, ?)", (st.session_state.wallet_address, st.session_state.balance, st.session_state.owned_nodes))
                c.execute("UPDATE system_state SET treasury = treasury + ? WHERE id=1", (house_delta,))
                # 인벤토리 및 보관소 상태 전체 저장
                for lvl, count in st.session_state.heroes.items():
                    c.execute("INSERT OR REPLACE INTO inventory (wallet, lvl, count) VALUES (?, ?, ?)", (st.session_state.wallet_address, lvl, count))
                for lvl, count in st.session_state.vault.items():
                    c.execute("INSERT OR REPLACE INTO vault (wallet, lvl, count) VALUES (?, ?, ?)", (st.session_state.wallet_address, lvl, count))
                conn.commit()
            return True
        except Exception as e:
            logging.error(f"TX FAIL: {e}"); return False

def load_user_data(wallet):
    with db_lock:
        with get_db_conn() as conn:
            c = conn.cursor()
            u = c.execute("SELECT balance, nodes FROM users WHERE wallet=?", (wallet,)).fetchone()
            if u:
                st.session_state.balance, st.session_state.owned_nodes = u
                st.session_state.heroes = dict(c.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (wallet,)).fetchall())
                st.session_state.vault = dict(c.execute("SELECT lvl, count FROM vault WHERE wallet=?", (wallet,)).fetchall())
            else:
                st.session_state.balance, st.session_state.heroes, st.session_state.vault = 10.0, {1:0}, {1:0}

def send_chat(wallet, msg, is_system=False):
    msg = html.escape(msg)
    if not is_system:
        if not wallet or len(msg) > 100 or re.search(r"(http|www)", msg.lower()): return
        if any(b in msg for b in GAME_CONFIG["BLOCK_WORDS"]): return
    with db_lock:
        with get_db_conn() as conn:
            conn.execute("INSERT INTO chat (wallet, message, time) VALUES (?, ?, ?)", ("⚙ SYSTEM" if is_system else wallet, msg, time.strftime('%H:%M:%S')))
            conn.commit()

# 6. UI 및 디자인 (마우스 오버 툴팁 가독성 수정)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Noto+Sans+KR:wght@700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    /* 전역 텍스트 스타일: 툴팁 방해 요인 제거 */
    html, body {
        color: #FFFFFF !important; font-family: 'Noto Sans KR', sans-serif !important;
    }
    /* 특정 카드와 제목에만 그림자 효과 적용 (그래프 툴팁 보호) */
    h1, h2, h3, h4, .premium-card, .hero-card {
        text-shadow: 2px 2px 4px #000 !important;
    }
    h1, h2, h3, h4 { color: #FFD700 !important; font-family: 'Orbitron' !important; }
    .premium-card { background: linear-gradient(145deg, #1e1e1e, #050505); border: 2px solid #FFD700; border-radius: 20px; padding: 15px; box-shadow: 10px 10px 25px #000; text-align: center; margin-bottom: 20px; }
    .hero-card { background: #111; border: 1px solid #FFD700; border-radius: 15px; padding: 10px; width: 180px; margin: 0 auto 15px auto; text-align: center; }
    .char-img { font-size: 80px !important; filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.8)); margin: 5px 0; display: inline-block; }
    .chat-box { background: #0a0a0a; border: 1px solid #333; border-radius: 10px; padding: 10px; height: 350px; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

# 7. 레이아웃 (헤더/사이드바)
if 'session_id' not in st.session_state: st.session_state.session_id = uuid.uuid4().hex[:8]
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE V9.2</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 🔑 ACCESS CONTROL")
    if not st.session_state.get('wallet_address'):
        if APP_MODE == "DEMO" and st.button("👑 운영자 빠른 연결"):
            st.session_state.wallet_address, st.session_state.is_admin, st.session_state.balance = OWNER_WALLET, True, 1000000.0
            load_user_data(OWNER_WALLET); st.rerun()
    else:
        st.markdown(f"<div class='premium-card'><b>BALANCE</b><h2>{st.session_state.balance:,.2f} WH</h2></div>", unsafe_allow_html=True)
        if st.button("지갑 연결 해제"): st.session_state.clear(); st.rerun()

# 8. 탭 구성 (닷지만 제거하고 나머지는 원상복구)
tabs = st.tabs(["🌐 현황", "🛠️ 노드 분양", "🎲 주사위 게임", "🐲 히어로 소환 & 보관", "💬 채팅창", "👑 관리자" if st.session_state.get('is_admin') else " "])

# --- 탭 0: 현황 (마우스 오버 수치 확인 가능) ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL NETWORK STATUS")
    # 마우스 오버 시 수치가 보이도록 CSS 간섭을 최소화한 그래프
    st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['Network Power']), color=["#FFD700"])

# --- 탭 1: 노드 분양 ---
with tabs[1]:
    st.markdown("### 🛠️ MASTER NODE MINTING")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='premium-card'><h4>GENESIS NODE</h4><p>2.0 SOL / 일일 50 WH 수익</p></div>", unsafe_allow_html=True)
        if st.button("MINT MASTER NODE"):
            st.session_state.owned_nodes += 1; process_transaction(0, 0, "NODE_MINT"); st.success("분양 완료!")
    with c2: st.metric("보유 노드 수", f"{st.session_state.owned_nodes} EA")

# --- 탭 2: 주사위 게임 (에러 방지 적용) ---
@st.fragment
def dice_section():
    if st.session_state.get('dice_status') == "rolling":
        p = st.empty()
        for _ in range(12): p.markdown(f"<h1 style='text-align:center;'>🎲 {random.choice(['⚀','⚁','⚂','⚃','⚄','⚅'])}</h1>", unsafe_allow_html=True); time.sleep(0.08)
        st.session_state.dice_res = [random.randint(1,6)]
        st.session_state.dice_status = "done"; st.rerun()
    elif st.session_state.get('dice_status') == "done":
        res = st.session_state.get('dice_res', [])
        if res:
            win = st.session_state.cur_bet * (GAME_CONFIG['DICE_X6'] if res[0]==6 else GAME_CONFIG['DICE_X5'] if res[0]==5 else 0)
            if win > 0: process_transaction(win, -win, "DICE_WIN"); st.success("🎉 당첨!")
            else: process_transaction(0, st.session_state.cur_bet, "DICE_LOSE")
            st.markdown(f"<div class='premium-card'><h1>결과: {res[0]}</h1></div>", unsafe_allow_html=True)
        st.button("다시 하기", on_click=lambda: st.session_state.update({"dice_status":"idle"}))
    else:
        bet = st.selectbox("베팅액", [1, 10, 100])
        if st.button("ROLL!"):
            if process_transaction(-bet, 0, "DICE_BET"):
                st.session_state.update({"cur_bet": bet, "dice_status": "rolling"}); st.rerun()

with tabs[2]: dice_section()

# --- 탭 3: 히어로 소환 & 보관 (1회 소환, 합성 글자, 보관소 기능 완벽 복구) ---
with tabs[3]:
    st.markdown("### 🐲 HERO SUMMON & VAULT STATION")
    h_icons = {1:"💧", 2:"👺", 3:"👹", 4:"🐎", 5:"🐉", 6:"👼"}
    h_names = {1:"슬라임", 2:"고블린", 3:"오크", 4:"켄타우로스", 5:"드래곤", 6:"가디언"}
    
    col_p, col_i, col_v = st.columns([1.5, 2.5, 2])
    with col_p:
        st.subheader("✨ 히어로 소환")
        # 1회 소환 복구
        if st.button("1회 소환 (10 WH)", use_container_width=True):
            if process_transaction(-GAME_CONFIG['SUMMON_1_COST'], GAME_CONFIG['SUMMON_1_COST'], "SUMMON_X1"):
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 1; st.rerun()
        if st.button("10회 소환 (90 WH)", use_container_width=True):
            if process_transaction(-GAME_CONFIG['SUMMON_10_COST'], GAME_CONFIG['SUMMON_10_COST'], "SUMMON_X10"):
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 10; st.rerun()

    with col_i:
        st.subheader("🎒 내 가방")
        for lvl, cnt in sorted(st.session_state.heroes.items()):
            if cnt > 0:
                st.markdown(f"<div class='hero-card'><div class='char-img'>{h_icons.get(lvl)}</div><br><b>Lv.{lvl} {h_names.get(lvl)}</b> ({cnt})</div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                # "합성" 글자 복구
                if lvl < GAME_CONFIG['MAX_LEVEL'] and cnt >= 2 and c1.button("합성", key=f"f_{lvl}"):
                    st.session_state.heroes[lvl] -= 2
                    if random.random() < GAME_CONFIG['FUSE_SUCCESS_RATE']:
                        st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+1; st.success("성공!")
                    st.rerun()
                if c2.button("판매", key=f"s_{lvl}"):
                    if process_transaction(10, -10, "SELL"): st.session_state.heroes[lvl] -= 1; st.rerun()
                # "보관" 기능 복구
                if c3.button("보관", key=f"v_{lvl}"):
                    st.session_state.heroes[lvl] -= 1
                    st.session_state.vault[lvl] = st.session_state.vault.get(lvl, 0) + 1; st.rerun()

    with col_v:
        st.subheader("🏛️ 보관소")
        for lvl, cnt in sorted(st.session_state.vault.items()):
            if cnt > 0:
                st.markdown(f"<div class='hero-card' style='border-color:#555;'>{h_icons.get(lvl)} Lv.{lvl} ({cnt}개)</div>", unsafe_allow_html=True)
                # "가방으로" 기능 복구
                if st.button("가방으로", key=f"out_{lvl}", use_container_width=True):
                    st.session_state.vault[lvl] -= 1
                    st.session_state.heroes[lvl] = st.session_state.heroes.get(lvl, 0) + 1; st.rerun()

# --- 탭 4: 채팅창 (정상 가동) ---
@st.fragment(run_every=5)
def chat_tab():
    st.markdown("### 💬 GLOBAL TROLLBOX")
    with get_db_conn() as conn: chats = conn.cursor().execute("SELECT wallet, message, time FROM chat ORDER BY id DESC LIMIT 15").fetchall()[::-1]
    box = "<div class='chat-box'>"
    for w, m, t in chats:
        is_sys = "SYSTEM" in w
        box += f"<div><b><span style='color:{'#00FF00' if is_sys else '#FFD700'}'>{w[:8]}</span></b>: {m} <small style='float:right; color:#444;'>{t}</small></div>"
    st.markdown(box + "</div>", unsafe_allow_html=True)
    if st.session_state.get('wallet_address'):
        with st.form("chat_f", clear_on_submit=True):
            m = st.text_input("메시지 입력", label_visibility="collapsed")
            if st.form_submit_button("전송"): send_chat(st.session_state.wallet_address, m); st.rerun()

with tabs[4]: chat_tab()
