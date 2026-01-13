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

# 1. DB 설정 및 성능 최적화
def get_db_conn():
    conn = sqlite3.connect('woohoo_v8_final.db', timeout=15, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')
db_lock = threading.Lock()

# 2. [Singleton] 하트비트 기반 봇 리커버리 로직
def try_start_bot():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS bot_lock (id INTEGER PRIMARY KEY CHECK(id=1), last_heartbeat REAL)")
        now = time.time()
        try:
            # 봇 권한 획득 시도
            c.execute("INSERT INTO bot_lock (id, last_heartbeat) VALUES (1, ?)", (now,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 이미 존재하면 하트비트 체크
            c.execute("SELECT last_heartbeat FROM bot_lock WHERE id=1")
            last_hb = c.fetchone()[0]
            if now - last_hb > 120: # 120초 경과 시 좀비 봇으로 판단
                c.execute("UPDATE bot_lock SET last_heartbeat = ? WHERE id=1", (now,))
                conn.commit()
                return True
            return False

def system_bot_thread():
    """배경 분위기 조성 및 하트비트 갱신"""
    msgs = ["🔥 잭팟의 주인공을 찾습니다!", "🚀 TGE 리스팅 임박!", "🐲 가디언 합성 성공 확률 업!", "🎲 하우스 배당 이벤트 진행 중!"]
    while True:
        try:
            with get_db_conn() as conn:
                # 하트비트 업데이트
                conn.execute("UPDATE bot_lock SET last_heartbeat = ? WHERE id=1", (time.time(),))
                # 랜덤 메시지 발송
                msg = random.choice(msgs)
                conn.execute("INSERT INTO chat (wallet, message, time) VALUES (?, ?, ?)", 
                             ("⚙ SYSTEM", msg, time.strftime('%H:%M:%S')))
                conn.execute("DELETE FROM chat WHERE id NOT IN (SELECT id FROM chat ORDER BY id DESC LIMIT 200)")
                conn.commit()
        except: pass
        time.sleep(random.randint(25, 55))

# 3. 데이터베이스 초기화
def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, nodes INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK (id=1), treasury REAL)''')
        c.execute("INSERT OR IGNORE INTO system_state (id, treasury) VALUES (1, 1000.0)")
        c.execute('''CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)''')
        # TX 로그 기록용 테이블 (EV 리포트용)
        c.execute('''CREATE TABLE IF NOT EXISTS tx_history (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, reason TEXT, user_delta REAL, house_delta REAL, time REAL)''')
        conn.commit()

init_db()
if try_start_bot():
    threading.Thread(target=system_bot_thread, daemon=True).start()

# 4. [확률 제어] 연속적 페널티 엔진
def weighted_roll(t):
    """중앙 금고 잔액에 따라 주사위 눈금 확률을 선형적으로 조절"""
    base = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    # 금고가 300 이하로 떨어지면 페널티 발생 (0~300 구간)
    penalty = max(0, 300 - t) / 300  # 0~1 사이 값
    # 5번(index 4), 6번(index 5) 눈금 확률 최대 60%까지 감소
    base[4] -= penalty * 0.6
    base[5] -= penalty * 0.6
    return random.choices(range(1, 7), weights=base)[0]

GAME_CONFIG = {
    "DODGE_FEE": 0.05, "DODGE_REWARD": 0.1, "DODGE_MIN_TIME": 10.0,
    "FUSE_SUCCESS": 0.75, "MAX_LEVEL": 6, "DICE_X6": 2.0, "DICE_X5": 1.2,
    "SESSION_BET_LIMIT": 50 # 세션당 베팅 제한
}

OWNER_WALLET = os.getenv("OWNER_WALLET", "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx")
APP_MODE = os.getenv("APP_MODE", "DEMO")

# 5. 세션 상태 초기화
if 'session_id' not in st.session_state: st.session_state.session_id = uuid.uuid4().hex[:8]
if 'bet_count' not in st.session_state: st.session_state.bet_count = 0
if 'treasury_loaded' not in st.session_state:
    with get_db_conn() as conn:
        st.session_state.global_treasury = conn.cursor().execute("SELECT treasury FROM system_state WHERE id=1").fetchone()[0]
    st.session_state.treasury_loaded = True

init_states = {'wallet_address': None, 'is_admin': False, 'balance': 10.0, 'heroes': {}, 'dice_status': "idle", 'chat_paused': False}
for k, v in init_states.items():
    if k not in st.session_state: st.session_state[k] = v

# --- [V8 원자적 트랜잭션 함수] ---
def process_transaction(user_delta, house_delta, reason, meta=None):
    if st.session_state.balance + user_delta < 0: return False
    with db_lock:
        try:
            with get_db_conn() as conn:
                # 원자성 확보를 위한 BEGIN IMMEDIATE
                conn.execute("BEGIN IMMEDIATE")
                c = conn.cursor()
                st.session_state.balance += user_delta
                c.execute("INSERT OR REPLACE INTO users (wallet, balance, nodes) VALUES (?, ?, ?)", 
                          (st.session_state.wallet_address, st.session_state.balance, 0))
                c.execute("UPDATE system_state SET treasury = treasury + ? WHERE id=1", (house_delta,))
                c.execute("INSERT INTO tx_history (wallet, reason, user_delta, house_delta, time) VALUES (?, ?, ?, ?, ?)",
                          (st.session_state.wallet_address, reason, user_delta, house_delta, time.time()))
                c.execute("SELECT treasury FROM system_state WHERE id=1")
                st.session_state.global_treasury = c.fetchone()[0]
                conn.commit()
            return True
        except Exception as e:
            logging.error(f"TX ERR: {e}")
            return False

def send_chat(wallet, msg, is_system=False):
    msg = html.escape(msg)
    if not is_system and (len(msg) > 100 or re.search(r"(http|www|\.com|\.net)", msg.lower())): return
    if not msg.strip(): return
    with db_lock:
        with get_db_conn() as conn:
            conn.execute("INSERT INTO chat (wallet, message, time) VALUES (?, ?, ?)", 
                         ("⚙ SYSTEM" if is_system else wallet, msg, time.strftime('%H:%M:%S')))
            conn.commit()

# 6. UI 디자인
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Noto+Sans+KR:wght@700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] { color: #FFFFFF !important; font-family: 'Noto Sans KR', sans-serif !important; text-shadow: 2px 2px 4px #000 !important; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'Orbitron' !important; }
    .premium-card { background: linear-gradient(145deg, #1e1e1e, #050505); border: 2px solid #FFD700; border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 20px; }
    .chat-box { background: #0a0a0a; border: 1px solid #333; height: 350px; overflow-y: auto; padding: 10px; font-size: 14px; }
</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE V8</h1>", unsafe_allow_html=True)

# 7. 메인 탭 레이아웃
tabs = st.tabs(["🌐 현황", "🕹️ 닷지", "🎲 주사위", "🐲 히어로", "💬 채팅", "👑 관리자" if st.session_state.is_admin else " "])

# --- 탭 2: 주사위 (연속 확률 엔진 및 세션 리밋) ---
@st.fragment
def dice_tab():
    if st.session_state.bet_count >= GAME_CONFIG['SESSION_BET_LIMIT']:
        st.warning("⚠️ 세션 베팅 한도 도달. 잠시 후 시도하세요.")
        return

    if st.session_state.dice_status == "rolling":
        p = st.empty()
        for _ in range(12): p.markdown(f"<h1 style='text-align:center;'>🎲 {random.choice(['⚀','⚁','⚂','⚃','⚄','⚅'])}</h1>", unsafe_allow_html=True); time.sleep(0.08)
        # 선형 페널티 확률 적용
        st.session_state.dice_res = weighted_roll(st.session_state.global_treasury)
        st.session_state.dice_status = "done"; st.rerun()
    
    elif st.session_state.dice_status == "done":
        res = st.session_state.dice_res
        win = st.session_state.cur_bet * (GAME_CONFIG['DICE_X6'] if res==6 else GAME_CONFIG['DICE_X5'] if res==5 else 0)
        if win > 0: process_transaction(win, -win, "DICE_WIN")
        else: process_transaction(0, st.session_state.cur_bet, "DICE_LOSE")
        st.write(f"결과: {res}"); st.button("RETRY", on_click=lambda: st.session_state.update({"dice_status":"idle"}))
    
    else:
        bet = st.selectbox("BET AMOUNT", [1, 10, 100])
        if st.button("ROLL!"):
            if process_transaction(-bet, 0, "DICE_BET_HOLD"):
                st.session_state.bet_count += 1
                st.session_state.update({"cur_bet": bet, "dice_status": "rolling"}); st.rerun()

with tabs[2]: dice_tab()

# --- 탭 5: 관리자 (EV 리포트 및 랭킹) ---
if st.session_state.is_admin and len(tabs) > 5:
    with tabs[5]:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("중앙 금고 순수익 (Treasury)", f"{st.session_state.global_treasury:,.2f} WH")
        with c2:
            with get_db_conn() as conn:
                # 하우스 수익률 분석 (EV 리포트)
                stats = conn.execute("SELECT SUM(CASE WHEN reason LIKE 'DICE_LOSE' THEN house_delta ELSE 0 END), SUM(CASE WHEN reason LIKE 'DICE_WIN' THEN -house_delta ELSE 0 END) FROM tx_history").fetchone()
                win_val, lose_val = (stats[0] or 0), (stats[1] or 0)
                st.metric("주사위 누적 하우스 수익", f"{win_val - lose_val:,.2f} WH")

        st.write("---")
        st.write("📊 **유저 랭킹 (Top 10)**")
        with get_db_conn() as conn:
            ranking_df = pd.read_sql("SELECT wallet, balance FROM users ORDER BY balance DESC LIMIT 10", conn)
            st.table(ranking_df)

# 사이드바 및 기타 탭 (기존 로직 유지)
with st.sidebar:
    if not st.session_state.wallet_address:
        if APP_MODE == "DEMO" and st.button("👑 운영자 연결"):
            st.session_state.wallet_address, st.session_state.is_admin = OWNER_WALLET, True
            st.session_state.balance = 1000000.0; st.rerun()
    else:
        st.markdown(f"<div class='premium-card'><b>BALANCE</b><h2>{st.session_state.balance:,.2f} WH</h2></div>", unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.clear(); st.rerun()

@st.fragment(run_every=5)
def chat_tab():
    with get_db_conn() as conn:
        chats = conn.cursor().execute("SELECT wallet, message, time FROM chat ORDER BY id DESC LIMIT 20").fetchall()[::-1]
    box = "<div class='chat-box'>"
    for w, m, t in chats:
        is_sys = "SYSTEM" in w
        box += f"<div style='margin-bottom:5px;'><b><span class='{'chat-system' if is_sys else ''}'>{w[:6]}..</span></b>: {m} <small style='float:right; color:#444;'>{t}</small></div>"
    st.markdown(box + "</div>", unsafe_allow_html=True)
    with st.form("c_f", clear_on_submit=True):
        msg = st.text_input("메시지", label_visibility="collapsed")
        if st.form_submit_button("전송") and st.session_state.wallet_address:
            send_chat(st.session_state.wallet_address, msg); st.rerun()
with tabs[4]: chat_tab()
