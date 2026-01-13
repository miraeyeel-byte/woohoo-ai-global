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

# 1. 시스템 설정 및 로깅 (app.log 기록)
# ---------------------------------------------------------
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
db_lock = threading.Lock()

# 2. 전역 설정 (모든 매직 넘버 통합 관리)
# ---------------------------------------------------------
GAME_CONFIG = {
    "DODGE_FEE": 0.05, "DODGE_REWARD": 0.1, "DODGE_MIN_TIME": 10.0,
    "SUMMON_10_COST": 90, "SUMMON_100_COST": 800,
    "FUSE_SUCCESS_RATE": 0.75, "MAX_LEVEL": 6, "WH_PRICE": 1.00,
    "DICE_X6": 2.0, "DICE_X5": 1.2,
    "CHAT_LIMIT": 200, "CHAT_DELAY": 2.0,
    "BLOCK_WORDS": ["출금", "돈", "수익", "벌었", "얼마", "원", "$", "솔", "토큰", "환전", "사기"]
}

APP_MODE = os.getenv("APP_MODE", "DEMO") 
OWNER_WALLET = os.getenv("OWNER_WALLET", "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx")

# 3. 데이터베이스 커넥션 헬퍼 (WAL 에러 방지 수정)
# ---------------------------------------------------------
def get_db_conn():
    # Streamlit Cloud 환경 호환성을 위해 WAL 모드 대신 표준 모드 사용
    conn = sqlite3.connect('woohoo_master_v8.db', timeout=20, check_same_thread=False)
    return conn

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, nodes INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK (id=1), treasury REAL)''')
        c.execute("INSERT OR IGNORE INTO system_state (id, treasury) VALUES (1, 1000.0)")
        c.execute('''CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tx_history (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, reason TEXT, user_delta REAL, house_delta REAL, time REAL)''')
        # 봇 싱글톤 락 테이블
        c.execute("CREATE TABLE IF NOT EXISTS bot_lock (id INTEGER PRIMARY KEY CHECK(id=1), last_heartbeat REAL)")
        conn.commit()

init_db()

# 4. [Singleton] 시스템 봇 리커버리 (120초 하트비트)
# ---------------------------------------------------------
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
    msgs = ["🔥 잭팟의 주인공을 찾습니다!", "🚀 TGE 리스팅 임박!", "🐲 가디언 합성 성공 확률 업!", "🎲 하우스 배당 이벤트 진행 중!"]
    while True:
        try:
            with get_db_conn() as conn:
                conn.execute("UPDATE bot_lock SET last_heartbeat = ? WHERE id=1", (time.time(),))
                msg = random.choice(msgs)
                conn.execute("INSERT INTO chat (wallet, message, time) VALUES (?, ?, ?)", ("⚙ SYSTEM", msg, time.strftime('%H:%M:%S')))
                conn.execute("DELETE FROM chat WHERE id NOT IN (SELECT id FROM chat ORDER BY id DESC LIMIT 200)")
                conn.commit()
        except: pass
        time.sleep(random.randint(30, 60))

if try_start_bot():
    threading.Thread(target=system_bot_thread, daemon=True).start()

# 5. 핵심 비즈니스 로직 (트랜잭션 및 확률 제어)
# ---------------------------------------------------------
def weighted_roll(t):
    """중앙 금고 잔액에 따른 선형 확률 페널티 엔진"""
    base = [1.0] * 6
    penalty = max(0, 300 - t) / 300
    base[4] -= penalty * 0.6 # 5번 확률 감소
    base[5] -= penalty * 0.6 # 6번 확률 감소
    return random.choices(range(1, 7), weights=base)[0]

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
                c.execute("INSERT INTO tx_history (wallet, reason, user_delta, house_delta, time) VALUES (?, ?, ?, ?, ?)", (st.session_state.wallet_address, reason, user_delta, house_delta, time.time()))
                c.execute("SELECT treasury FROM system_state WHERE id=1")
                st.session_state.global_treasury = c.fetchone()[0]
                conn.commit()
            return True
        except Exception as e:
            logging.error(f"TX FAIL: {e}")
            return False

def send_chat(wallet, msg, is_system=False):
    msg = html.escape(msg)
    if not is_system:
        if not wallet or len(msg) > 100 or re.search(r"(http|www|\.com)", msg.lower()): return
        if any(b in msg for b in GAME_CONFIG["BLOCK_WORDS"]): return
        if time.time() - st.session_state.get('last_chat', 0) < GAME_CONFIG["CHAT_DELAY"]: return
        st.session_state.last_chat = time.time()
    with db_lock:
        with get_db_conn() as conn:
            conn.execute("INSERT INTO chat (wallet, message, time) VALUES (?, ?, ?)", ("⚙ SYSTEM" if is_system else wallet, msg, time.strftime('%H:%M:%S')))
            conn.commit()

# 6. UI 및 디자인 (입체 음양 테마 고수)
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Noto+Sans+KR:wght@700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] {
        color: #FFFFFF !important; font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 4px #000, -2px -2px 4px #000, 2px -2px 4px #000 !important;
    }
    h1, h2, h3, h4 { color: #FFD700 !important; font-family: 'Orbitron' !important; text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.7); }
    .premium-card { background: linear-gradient(145deg, #1e1e1e, #050505); border: 2px solid #FFD700; border-radius: 20px; padding: 15px; box-shadow: 10px 10px 25px #000; text-align: center; margin-bottom: 20px; }
    /* 히어로 소환 콤팩트 카드 (180px) */
    .hero-card { background: #111; border: 1px solid #FFD700; border-radius: 15px; padding: 10px; width: 180px; margin: 0 auto 15px auto; text-align: center; }
    .char-img { font-size: 80px !important; filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.8)); margin: 5px 0; display: inline-block; }
    .chat-box { background: #0a0a0a; border: 1px solid #333; border-radius: 10px; padding: 10px; height: 350px; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

# 7. 레이아웃
# ---------------------------------------------------------
if 'session_id' not in st.session_state: st.session_state.session_id = uuid.uuid4().hex[:8]
if 'treasury_loaded' not in st.session_state:
    with get_db_conn() as conn: st.session_state.global_treasury = conn.cursor().execute("SELECT treasury FROM system_state WHERE id=1").fetchone()[0]
    st.session_state.treasury_loaded = True

st.markdown("<h1 style='text-align: center;'>⚡ WOOHOO AI HYPER-CORE V8.1</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 🔑 ACCESS [{st.session_state.session_id}]")
    if not st.session_state.get('wallet_address'):
        if APP_MODE == "DEMO" and st.button("👑 운영자 빠른 연결"):
            st.session_state.wallet_address, st.session_state.is_admin, st.session_state.balance = OWNER_WALLET, True, 1000000.0; st.rerun()
    else:
        st.markdown(f"<div class='premium-card'><b>BALANCE</b><h2>{st.session_state.balance:,.2f} WH</h2></div>", unsafe_allow_html=True)
        if st.button("DISCONNECT"): st.session_state.clear(); st.rerun()

tabs = st.tabs(["🌐 현황", "🛠️ 노드", "🕹️ 닷지", "🎲 주사위", "🐲 히어로", "💬 채팅", "👑 관리자" if st.session_state.get('is_admin') else " "])

# --- 탭 0: 현황 (사진 3 복구) ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL NETWORK STATUS")
    st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['Power']), color=["#FFD700"])

# --- 탭 2: 닷지 ---
with tabs[2]:
    if st.button("🚀 START GAME"):
        if process_transaction(-GAME_CONFIG['DODGE_FEE'], GAME_CONFIG['DODGE_FEE'], "DODGE_START"):
            st.session_state.update({"last_dodge_start": time.time(), "dodge_claimed": False, "dodge_run": True}); st.rerun()
    if st.session_state.get('dodge_run'):
        components.html("<html><body style='background:black;'><canvas id='dg' width='500' height='300'></canvas></body></html>", height=320)
        if not st.session_state.get('dodge_claimed') and st.button("🎁 CLAIM"):
            elapsed = time.time() - st.session_state.last_dodge_start
            if elapsed >= GAME_CONFIG['DODGE_MIN_TIME']:
                if process_transaction(GAME_CONFIG['DODGE_REWARD'], -GAME_CONFIG['DODGE_REWARD'], "DODGE_CLAIM"):
                    st.session_state.dodge_claimed = True; st.success("SUCCESS"); send_chat("SYSTEM", f"🕹️ {st.session_state.wallet_address[:6]}.. 생존 보상!", True)
            else: st.error(f"실패: {elapsed:.1f}s")

# --- 탭 3: 주사위 (사진 1 컬럼 에러 해결) ---
@st.fragment
def dice_section():
    if st.session_state.get('dice_status') == "rolling":
        p = st.empty()
        for _ in range(12): p.markdown(f"<h1 style='text-align:center;'>🎲 {random.choice(['⚀','⚁','⚂','⚃','⚄','⚅'])}</h1>", unsafe_allow_html=True); time.sleep(0.08)
        st.session_state.multi_dice_results = [weighted_roll(st.session_state.global_treasury) for _ in range(st.session_state.get('rc', 1))]
        st.session_state.dice_status = "done"; st.rerun()
    elif st.session_state.get('dice_status') == "done":
        # [수정] 결과 리스트가 있을 때만 컬럼 생성 (사진 1 해결)
        res_list = st.session_state.get('multi_dice_results', [])
        if res_list:
            cols = st.columns(len(res_list))
            total_win = 0
            for i, r in enumerate(res_list):
                cols[i].markdown(f"<h1 style='text-align:center;'>{r}</h1>", unsafe_allow_html=True)
                total_win += st.session_state.cur_bet * (GAME_CONFIG['DICE_X6'] if r==6 else GAME_CONFIG['DICE_X5'] if r==5 else 0)
            if total_win > 0: 
                process_transaction(total_win, -total_win, "DICE_WIN")
                send_chat("SYSTEM", f"🎲 {st.session_state.wallet_address[:6]}.. 당첨!", True)
            else: process_transaction(0, st.session_state.cur_bet, "DICE_LOSE")
        st.button("RETRY", on_click=lambda: st.session_state.update({"dice_status":"idle"}))
    else:
        bet = st.selectbox("BET", [1, 10, 100])
        c1, c2, c3 = st.columns(3)
        if c1.button("🎲 1회"):
            if process_transaction(-bet, 0, "DICE_BET"): st.session_state.update({"cur_bet":bet, "rc":1, "dice_status":"rolling"}); st.rerun()
        if c2.button("🎰 5회"):
            if process_transaction(-bet*5, 0, "DICE_BET_X5"): st.session_state.update({"cur_bet":bet, "rc":5, "dice_status":"rolling"}); st.rerun()
        if c3.button("🔥 10회"):
            if process_transaction(-bet*10, 0, "DICE_BET_X10"): st.session_state.update({"cur_bet":bet, "rc":10, "dice_status":"rolling"}); st.rerun()

with tabs[3]: dice_section()

# --- 탭 4: 히어로 (사진 2 콤팩트 UI 최적화) ---
with tabs[4]:
    st.markdown("### 🐲 HERO SUMMON & INVENTORY")
    h_icons = {1:"💧", 2:"👺", 3:"👹", 4:"🐎", 5:"🐉", 6:"👼"}
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("10회 소환 (90 WH)"):
            if process_transaction(-90, 90, "SUMMON"): st.session_state.heroes[1] = st.session_state.heroes.get(1,0)+10; st.rerun()
    with col2:
        for lvl, cnt in sorted(st.session_state.get('heroes', {}).items()):
            if cnt > 0:
                st.markdown(f"<div class='hero-card'><div class='char-img'>{h_icons.get(lvl)}</div> Lv.{lvl} ({cnt}개)</div>", unsafe_allow_html=True)
                if lvl < GAME_CONFIG['MAX_LEVEL'] and cnt >= 2 and st.button(f"합성", key=f"f_{lvl}"):
                    st.session_state.heroes[lvl] -= 2
                    if random.random() < GAME_CONFIG['FUSE_SUCCESS_RATE']:
                        st.session_state.heroes[lvl+1] = st.session_state.heroes.get(lvl+1,0)+1; st.success("성공")
                        send_chat("SYSTEM", f"🐲 {st.session_state.wallet_address[:6]}.. Lv.{lvl+1} 합성!", True)
                    st.rerun()

# --- 탭 5: 채팅 (가짜 트래픽 연출) ---
@st.fragment(run_every=5)
def chat_tab():
    if random.random() < 0.02: send_chat("SYSTEM", random.choice(["🔥 가즈아!", "🚀 떡상!", "🎲 대박 기원!"]), True)
    with db_lock:
        with get_db_conn() as conn: chats = conn.cursor().execute("SELECT wallet, message, time FROM chat ORDER BY id DESC LIMIT 15").fetchall()[::-1]
    box = "<div class='chat-box'>"
    for w, m, t in chats:
        is_sys = "SYSTEM" in w
        box += f"<div><b><span class='{'chat-system' if is_sys else ''}'>{w[:10]}</span></b>: {m} <small style='float:right; color:#444;'>{t}</small></div>"
    st.markdown(box + "</div>", unsafe_allow_html=True)
    if st.session_state.get('wallet_address'):
        with st.form("c_f", clear_on_submit=True):
            m = st.text_input("메시지", label_visibility="collapsed")
            if st.form_submit_button("전송"): send_chat(st.session_state.wallet_address, m); st.rerun()

with tabs[5]: chat_tab()

# --- 탭 6: 관리자 ---
if st.session_state.get('is_admin') and len(tabs) > 6:
    with tabs[6]:
        st.metric("중앙 금고 수익", f"{st.session_state.global_treasury:,.2f} WH")
        with get_db_conn() as conn:
            st.write("📊 TOP 고래")
            st.table(pd.read_sql("SELECT wallet, balance FROM users ORDER BY balance DESC LIMIT 5", conn))
