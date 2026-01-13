import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components
import os
import sqlite3
import uuid
import html
import re

# 1. 시스템 설정 (가장 먼저 호출)
# ---------------------------------------------------------
st.set_page_config(page_title="WOOHOO V13 PRO", layout="wide")

def get_db_conn():
    return sqlite3.connect('woohoo_final_v13.db', timeout=30, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, nodes INTEGER)')
        c.execute('CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))')
        c.execute('CREATE TABLE IF NOT EXISTS vault (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))')
        c.execute('CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK (id=1), treasury REAL)')
        c.execute('INSERT OR IGNORE INTO system_state (id, treasury) VALUES (1, 1000.0)')
        c.execute('CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)')
        conn.commit()

init_db()

# 2. 세션 상태 관리 (안전한 초기화 및 리셋)
# ---------------------------------------------------------
def init_session():
    if 'session_id' not in st.session_state: st.session_state.session_id = uuid.uuid4().hex[:8]
    # [필수 5줄] 중복 클릭 방지용 락
    if 'op_lock' not in st.session_state: st.session_state.op_lock = False
    
    keys = {
        'wallet_address': None, 'is_admin': False, 'balance': 10.0, 
        'heroes': {i:0 for i in range(1,7)}, 'vault': {i:0 for i in range(1,7)}, 
        'owned_nodes': 0, 'dice_status': "idle", 'dice_res': None, 
        'cur_bet': 1, 'global_treasury': 1000.0
    }
    for k, v in keys.items():
        if k not in st.session_state: st.session_state[k] = v

def reset_session():
    for k in list(st.session_state.keys()): del st.session_state[k]
    init_session()

init_session()

# 3. 핵심 로직 (트랜잭션 및 데이터 로드)
# ---------------------------------------------------------
def process_transaction(user_delta, house_delta, reason):
    """BEGIN IMMEDIATE를 적용한 원자적 트랜잭션"""
    if not st.session_state.wallet_address or st.session_state.balance + user_delta < 0: return False
    st.session_state.op_lock = True # 락 획득
    try:
        with get_db_conn() as conn:
            conn.execute("BEGIN IMMEDIATE") # 운영자급 안정성
            c = conn.cursor()
            st.session_state.balance += user_delta
            c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", (st.session_state.wallet_address, st.session_state.balance, st.session_state.owned_nodes))
            c.execute("UPDATE system_state SET treasury = treasury + ? WHERE id=1", (house_delta,))
            for lvl, cnt in st.session_state.heroes.items():
                c.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet_address, lvl, cnt))
            for lvl, cnt in st.session_state.vault.items():
                c.execute("INSERT OR REPLACE INTO vault VALUES (?, ?, ?)", (st.session_state.wallet_address, lvl, cnt))
            conn.commit()
            st.session_state.global_treasury = conn.execute("SELECT treasury FROM system_state WHERE id=1").fetchone()[0]
        return True
    except Exception as e:
        st.error(f"데이터 처리 실패: {e}")
        return False
    finally:
        st.session_state.op_lock = False # 락 해제

def load_user_data(wallet):
    """이전 세션 찌꺼기 제거 후 로딩"""
    st.session_state.heroes = {i:0 for i in range(1,7)}
    st.session_state.vault = {i:0 for i in range(1,7)}
    with get_db_conn() as conn:
        c = conn.cursor()
        u = c.execute("SELECT balance, nodes FROM users WHERE wallet=?", (wallet,)).fetchone()
        if u:
            st.session_state.balance, st.session_state.owned_nodes = u
            st.session_state.heroes.update(dict(c.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (wallet,)).fetchall()))
            st.session_state.vault.update(dict(c.execute("SELECT lvl, count FROM vault WHERE wallet=?", (wallet,)).fetchall()))

# 4. 디자인 (현황 탭 음영 제거 & 나머지 유지)
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Noto+Sans+KR:wght@700;900&display=swap');
    .stApp { background-color: #000000 !important; }
    html, body { color: #FFFFFF !important; font-family: 'Noto Sans KR', sans-serif !important; }
    .no-shadow { text-shadow: none !important; color: #FFD700 !important; }
    .glow-text { text-shadow: 2px 2px 8px #000 !important; color: #FFD700 !important; font-family: 'Orbitron' !important; }
    .premium-card { background: linear-gradient(145deg, #1e1e1e, #050505); border: 2px solid #FFD700; border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 20px; box-shadow: 10px 10px 25px #000; }
    .hero-card { background: #111; border: 1px solid #FFD700; border-radius: 15px; padding: 10px; width: 180px; margin: 0 auto 15px auto; text-align: center; }
    .char-img { font-size: 70px !important; filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.8)); }
    .chat-box { background: #0a0a0a; border: 1px solid #333; border-radius: 10px; padding: 10px; height: 350px; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

# 5. 메인 레이아웃 및 락 체크
# ---------------------------------------------------------
if st.session_state.op_lock: st.stop() # 중복 요청 차단

st.markdown("<h1 class='glow-text' style='text-align: center;'>⚡ WOOHOO V13 PRO-CORE</h1>", unsafe_allow_html=True)

with st.sidebar:
    if not st.session_state.wallet_address:
        if st.button("👑 운영자 연결"):
            st.session_state.wallet_address, st.session_state.is_admin = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx", True
            load_user_data(st.session_state.wallet_address); st.rerun()
    else:
        st.markdown(f"<div class='premium-card'><b class='glow-text'>{st.session_state.balance:,.2f} WH</b></div>", unsafe_allow_html=True)
        if st.button("지갑 연결 해제"):
            reset_session(); st.rerun()

tabs = st.tabs(["🌐 현황", "🛠️ 노드 분양", "🎲 주사위 게임", "🐲 히어로 소환 & 보관", "💬 채팅창"])

# --- 탭 0: 현황 ---
with tabs[0]:
    st.markdown("<h3 class='no-shadow'>🌐 NETWORK POWER STATUS</h3>", unsafe_allow_html=True)
    st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['Power']), color=["#FFD700"])

# --- 탭 1: 노드 분양 ---
with tabs[1]:
    st.markdown("<h3 class='glow-text'>🛠️ MINT MASTER NODE</h3>", unsafe_allow_html=True)
    if st.button("민팅 시작 (2.0 SOL)"):
        if not process_transaction(0, 0, "NODE_MINT"): 
            st.error("처리 실패"); st.stop() # UX 개선
        st.session_state.owned_nodes += 1; st.success("성공!")

# --- 탭 2: 주사위 게임 ---
with tabs[2]:
    st.markdown("<h3 class='glow-text'>🎲 LUCKY DICE</h3>", unsafe_allow_html=True)
    if st.session_state.dice_status == "rolling":
        p = st.empty()
        for _ in range(10): p.markdown(f"<h1 style='text-align:center;'>🎲 {random.choice(['⚀','⚁','⚂','⚃','⚄','⚅'])}</h1>", unsafe_allow_html=True); time.sleep(0.08)
        st.session_state.dice_res = random.randint(1,6)
        st.session_state.dice_status = "done"; st.rerun()
    elif st.session_state.dice_status == "done":
        res = st.session_state.dice_res
        win = st.session_state.cur_bet * (2.0 if res==6 else 1.2 if res==5 else 0)
        # 결과 정산 트랜잭션 검증
        if win > 0:
            if not process_transaction(win, -win, "DICE_WIN"): st.error("지급 실패"); st.stop()
            st.balloons()
        else:
            if not process_transaction(0, st.session_state.cur_bet, "DICE_LOSE"): st.error("정산 실패"); st.stop()
        st.markdown(f"<div class='premium-card'><h1>결과: {res}</h1></div>", unsafe_allow_html=True)
        if st.button("다시 하기"): st.session_state.dice_status = "idle"; st.rerun()
    else:
        if st.session_state.dice_status != "idle": st.stop() #
        bet = st.selectbox("베팅액", [1, 10, 100])
        if st.button("ROLL!"):
            if not process_transaction(-bet, 0, "DICE_BET"):
                st.error("잔액 부족 또는 시스템 오류"); st.stop()
            st.session_state.update({"cur_bet": bet, "dice_status": "rolling"}); st.rerun()

# --- 탭 3: 히어로 소환 & 보관 ---
with tabs[3]:
    st.markdown("<h3 class='glow-text'>🐲 SUMMON & VAULT</h3>", unsafe_allow_html=True)
    h_icons = {1:"💧", 2:"👺", 3:"👹", 4:"🐎", 5:"🐉", 6:"👼"}
    h_names = {1:"슬라임", 2:"고블린", 3:"오크", 4:"켄타우로스", 5:"드래곤", 6:"가디언"}
    col_p, col_i, col_v = st.columns([1.5, 2.5, 2])
    
    with col_p:
        st.subheader("✨ 소환")
        if st.button("1회 소환 (10 WH)", use_container_width=True):
            if process_transaction(-10, 10, "SUMMON_1"): st.session_state.heroes[1] += 1; st.rerun()
            else: st.error("실패"); st.stop()
        if st.button("10회 소환 (90 WH)", use_container_width=True):
            if process_transaction(-90, 90, "SUMMON_10"): st.session_state.heroes[1] += 10; st.rerun()
            else: st.error("실패"); st.stop()

    with col_i:
        st.subheader("🎒 내 가방")
        for lvl in range(1, 7):
            cnt = st.session_state.heroes.get(lvl, 0)
            if cnt > 0:
                st.markdown(f"<div class='hero-card'><div class='char-img'>{h_icons[lvl]}</div><br><b>Lv.{lvl} {h_names[lvl]}</b> ({cnt})</div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                if lvl < 6 and cnt >= 2 and c1.button("합성", key=f"f_{lvl}"):
                    st.session_state.heroes[lvl] -= 2
                    if random.random() < 0.75: st.session_state.heroes[lvl+1] += 1; st.success("성공")
                    process_transaction(0, 0, "FUSE"); st.rerun()
                if c2.button("💰", key=f"s_{lvl}"):
                    if process_transaction(10, -10, "SELL"): st.session_state.heroes[lvl] -= 1; st.rerun()
                if c3.button("📦", key=f"v_{lvl}"):
                    st.session_state.heroes[lvl] -= 1
                    st.session_state.vault[lvl] += 1; process_transaction(0,0,"VAULT_IN"); st.rerun()

    with col_v:
        st.subheader("🏛️ 보관소")
        for lvl, cnt in st.session_state.vault.items():
            if cnt > 0:
                st.markdown(f"<div class='hero-card' style='border-color:#555;'>{h_icons[lvl]} Lv.{lvl} ({cnt})</div>", unsafe_allow_html=True)
                if st.button("가방으로", key=f"out_{lvl}", use_container_width=True):
                    st.session_state.vault[lvl] -= 1
                    st.session_state.heroes[lvl] += 1; process_transaction(0,0,"VAULT_OUT"); st.rerun()

# --- 탭 4: 채팅창 ---
with tabs[4]:
    st.markdown("<h3 class='glow-text'>💬 GLOBAL TROLLBOX</h3>", unsafe_allow_html=True)
    with get_db_conn() as conn:
        chats = conn.execute("SELECT wallet, message, time FROM chat ORDER BY id DESC LIMIT 15").fetchall()[::-1]
    box_html = "<div class='chat-box'>"
    for w, m, t in chats:
        box_html += f"<div><b><span style='color:#FFD700;'>{w[:8]}</span></b>: {m} <small style='float:right; color:#444;'>{t}</small></div>"
    st.markdown(box_html + "</div>", unsafe_allow_html=True)
    
    if st.session_state.wallet_address:
        with st.form("chat_form", clear_on_submit=True):
            m = st.text_input("메시지 입력", label_visibility="collapsed")
            if st.form_submit_button("전송"):
                # [안전 검증] 빈 문자열 및 길이 제한
                if not m or len(m) > 200:
                    st.warning("메시지를 입력하세요 (200자 이내)"); st.stop()
                with get_db_conn() as conn:
                    conn.execute("BEGIN IMMEDIATE") # 채팅 트랜잭션 보호
                    conn.execute("INSERT INTO chat (wallet, message, time) VALUES (?, ?, ?)", (st.session_state.wallet_address, html.escape(m), time.strftime('%H:%M:%S')))
                    conn.commit()
                st.rerun()
