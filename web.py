# ===============================
# WOOHOO V17.3 - Virtual Crime Hunter
# ===============================

# -------------------------------
# 1. IMPORTS
# -------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import sqlite3
import html
import threading
import requests
import os
import datetime

# -------------------------------
# 2. CONFIG / GLOBALS
# -------------------------------
st.set_page_config(page_title="WOOHOO V17.3 - Crime Hunter", layout="wide")
db_lock = threading.Lock()
FUSE_RATE = 0.7  # 강화 성공 확률 기본

# -------------------------------
# 3. DB INITIALIZATION
# -------------------------------
DB_PATH = "woohoo_master_v17.db"
# 폴더 자동 생성
db_dir = os.path.dirname(DB_PATH)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

def get_db_conn():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        # 유저, 범죄자, 시스템, 채팅
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, nodes INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS criminals (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, lvl INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS vault (wallet TEXT, criminal_id INTEGER, count INTEGER, PRIMARY KEY(wallet,criminal_id))")
        c.execute("CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK(id=1), treasury REAL)")
        c.execute("INSERT OR IGNORE INTO system_state VALUES (1,1000)")
        c.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS licenses (wallet TEXT PRIMARY KEY, expiry_time TEXT)")
        conn.commit()

init_db()

# -------------------------------
# 4. SESSION INIT
# -------------------------------
def init_session():
    defaults = {
        "wallet_address": None,
        "is_admin": False,
        "balance": 0.1,  # 초기 소량 SOL
        "owned_nodes": 0,
        "criminals": {i:0 for i in range(1,21)},  # 20레벨 범죄자
        "vault": {i:0 for i in range(1,21)},
        "op_lock": False,
        "current_capture": None,
        "capture_result": None,
        "capture_paid": False,
        "cur_bounty": 0.01
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# -------------------------------
# 5. TRANSACTION
# -------------------------------
def process_transaction(user_delta, house_delta):
    if not st.session_state.wallet_address:
        return False
    if st.session_state.balance + user_delta < 0:
        return False

    with db_lock:
        with get_db_conn() as conn:
            conn.execute("BEGIN IMMEDIATE")
            c = conn.cursor()
            new_balance = st.session_state.balance + user_delta
            c.execute(
                "INSERT OR REPLACE INTO users VALUES (?,?,?)",
                (st.session_state.wallet_address, new_balance, st.session_state.owned_nodes)
            )
            c.execute(
                "UPDATE system_state SET treasury = treasury + ? WHERE id=1",
                (house_delta,)
            )
            for lvl in range(1,21):
                c.execute(
                    "INSERT OR REPLACE INTO vault VALUES (?,?,?)",
                    (st.session_state.wallet_address, lvl, st.session_state.vault[lvl])
                )
            conn.commit()
            st.session_state.balance = new_balance
    return True

# -------------------------------
# 6. SECURITY ENGINE
# -------------------------------
FIREWALL_THRESHOLD = 80
def get_visitor_ip():
    try:
        ip = st.context.headers.get("X-Forwarded-For", "").split(",")[0]
        if not ip: ip = st.context.headers.get("X-Real-IP", "127.0.0.1")
        return ip
    except:
        return "127.0.0.1"

def check_firewall():
    if st.session_state.get("is_admin"):
        return True, 0, ""
    ip = get_visitor_ip()
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,countryCode,proxy,hosting}"
        res = requests.get(url, timeout=2).json()
        risk_score = 0
        reasons = []
        if res.get("proxy"): risk_score += 40; reasons.append("VPN/Proxy")
        if res.get("hosting"): risk_score += 30; reasons.append("Hosting/Server")
        if res.get("countryCode") != "KR": risk_score += 20; reasons.append("Foreign IP")
        if risk_score >= FIREWALL_THRESHOLD:
            st.error(f"⚠️ [보안 위협 감지] 접속 제한 (Risk: {risk_score})")
            st.info(f"사유: {', '.join(reasons)}")
            st.stop()
        return True, risk_score, ", ".join(reasons)
    except:
        return True, 0, "Security Engine Bypass (Error)"

can_proceed, current_risk, risk_desc = check_firewall()

# -------------------------------
# 7. TELEGRAM ALERT
# -------------------------------
def send_telegram_alert(message):
    token = "YOUR_BOT_TOKEN"
    chat_id = "@FuckHoneypot"
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": f"🚨 [Crime Hunter Alert]\n{message}"}
        requests.get(url, params=params, timeout=3)
    except:
        pass

# -------------------------------
# 8. CRIMINAL SCAN / CAPTURE
# -------------------------------
def scan_criminal_level(lvl):
    fail_rate = 0.2 + (lvl-1)*0.05  # 레벨별 기본 실패율
    return min(fail_rate, 0.95)

def capture_criminal(lvl, use_retrial=False, reinforcement=0):
    base_fail = scan_criminal_level(lvl)
    adjusted_fail = base_fail - 0.1*reinforcement
    if use_retrial:
        adjusted_fail -= 0.1  # 재판권 사용시 10% 감소
    return random.random() > adjusted_fail

# -------------------------------
# 9. UI STYLE
# -------------------------------
st.markdown("""
<style>
.stApp {background:#000;color:white;}
.glow {color:#FFD700;text-shadow:0 0 10px #000;}
.card {border:2px solid #FFD700;border-radius:15px;padding:15px;margin:10px;background:#111;}
.criminal {border:1px solid #FFD700;border-radius:12px;padding:10px;margin:5px;text-align:center;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 10. HEADER / LOGIN
# -------------------------------
st.markdown("<h1 class='glow' style='text-align:center'>⚡ WOOHOO Crime Hunter V17.3</h1>", unsafe_allow_html=True)

with st.sidebar:
    if not st.session_state.wallet_address:
        if st.button("👑 Admin Login"):
            st.session_state.wallet_address = "ADMIN"
            st.session_state.is_admin = True
            st.rerun()
    else:
        st.markdown(f"<div class='card'><h2 class='glow'>{st.session_state.balance:.3f} SOL</h2></div>", unsafe_allow_html=True)
        if st.button("Logout"):
            for k in st.session_state.keys():
                st.session_state[k] = None
            st.rerun()

# -------------------------------
# 11. TABS
# -------------------------------
tabs = st.tabs(["📊 Dashboard","🛡️ Crime Capture","🏛️ Vault","🏆 Leaderboard"])

# ---------- DASHBOARD ----------
with tabs[0]:
    st.markdown("<h2 class='glow'>Network Overview</h2>", unsafe_allow_html=True)
    st.line_chart(pd.DataFrame(np.random.randn(30,1), columns=["System Activity"]))

# ---------- CRIME CAPTURE ----------
with tabs[1]:
    st.markdown("<h3 class='glow'>Capture Criminals</h3>", unsafe_allow_html=True)
    
    lvl = st.selectbox("Select Criminal Level (1-20)", range(1,21))
    use_retrial = st.checkbox("Use Retrial (increase success 10%)")
    reinforcement = st.slider("Reinforcement (max 2 per level)", 0, 2, 0)
    count = st.number_input("Number to Capture (1-10)", min_value=1, max_value=10, value=1)
    price = 0.01 * count  # SOL 단위
    st.markdown(f"Total Cost: {price:.3f} SOL")
    
    if st.button("Capture!"):
        if st.session_state.balance < price:
            st.error("Insufficient balance!")
        else:
            st.session_state.cur_bounty = price
            success = capture_criminal(lvl, use_retrial, reinforcement)
            if success:
                st.session_state.criminals[lvl] += count
                st.success(f"🎉 Successfully captured {count} criminal(s) at level {lvl}!")
                send_telegram_alert(f"{st.session_state.wallet_address} captured {count} level {lvl} criminal(s)!")
                process_transaction(-price, price)
            else:
                st.warning("❌ Capture failed!")
                process_transaction(-price, 0)

# ---------- VAULT ----------
with tabs[2]:
    st.markdown("<h3 class='glow'>Vault Storage</h3>", unsafe_allow_html=True)
    for lvl, cnt in st.session_state.criminals.items():
        if cnt > 0:
            c1,c2,c3 = st.columns(3)
            st.markdown(f"<div class='criminal'>Level {lvl} Criminal x{cnt}</div>", unsafe_allow_html=True)
            if c1.button("Send to Vault", key=f"v{lvl}"):
                st.session_state.vault[lvl] += cnt
                st.session_state.criminals[lvl] = 0
                process_transaction(0,0)
                st.rerun()

# ---------- LEADERBOARD ----------
with tabs[3]:
    st.markdown("<h3 class='glow'>Top Hunters</h3>", unsafe_allow_html=True)
    with get_db_conn() as conn:
        rows = conn.execute("""
            SELECT wallet, IFNULL(SUM(balance),0.0) as total_sol
            FROM users
            GROUP BY wallet
            ORDER BY total_sol DESC
            LIMIT 10
        """).fetchall()
    for i,row in enumerate(rows):
        val = row[1] if row[1] is not None else 0.0
        st.markdown(f"{i+1}. {row[0]} - {val:.3f} SOL")
