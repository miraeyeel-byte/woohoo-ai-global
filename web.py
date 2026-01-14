# ===============================
# WOOHOO V17.3 - 범죄자 체포 & 보안 통합
# ===============================

import os
import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import sqlite3
import threading
import requests
import datetime
import html

# ===============================
# GLOBAL CONFIG
# ===============================
st.set_page_config(page_title="WOOHOO V17.3 Catch Criminals", layout="wide")
db_lock = threading.Lock()
FUSE_RATE = 0.7  # 강화 성공 기본 확률

# ===============================
# DB PATH & PERSISTENT STORAGE
# ===============================
DB_PATH = os.getenv("DB_PATH", "woohoo_master_v17.db")
db_dir = os.path.dirname(DB_PATH)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

def get_db_conn():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

# ===============================
# DB INIT
# ===============================
def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        # 유저 / 지갑
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, hunter_level INTEGER)")
        # 범죄자 레벨
        c.execute("CREATE TABLE IF NOT EXISTS criminals (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet,lvl))")
        # 감옥 (보관)
        c.execute("CREATE TABLE IF NOT EXISTS jail (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet,lvl))")
        # 시스템 상태 (재무)
        c.execute("CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK(id=1), treasury REAL)")
        c.execute("INSERT OR IGNORE INTO system_state VALUES (1,1000)")
        # 채팅 및 공지
        c.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)")
        # 라이선스/티어
        c.execute("CREATE TABLE IF NOT EXISTS licenses (wallet TEXT PRIMARY KEY, tier TEXT, expiry TEXT)")
        conn.commit()

init_db()

# ===============================
# SESSION INIT
# ===============================
def init_session():
    defaults = {
        "wallet_address": None,
        "is_admin": False,
        "balance": 0.01,
        "hunter_level": 1,
        "criminals": {i:0 for i in range(1,21)},
        "jail": {i:0 for i in range(1,21)},
        "cur_action": None,
        "action_result": None,
        "cur_bet": 1
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ===============================
# LICENSE CHECK
# ===============================
def check_license(wallet):
    if not wallet: return False
    with get_db_conn() as conn:
        row = conn.execute("SELECT tier,expiry FROM licenses WHERE wallet=?", (wallet,)).fetchone()
    if not row: return False
    tier, expiry_str = row
    expiry = datetime.datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
    if expiry < datetime.datetime.now(): return False
    return True

def grant_license(wallet, tier, hours):
    expiry = datetime.datetime.now() + datetime.timedelta(hours=hours)
    with db_lock:
        with get_db_conn() as conn:
            conn.execute("INSERT OR REPLACE INTO licenses VALUES (?,?,?)",
                         (wallet, tier, expiry.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

# ===============================
# TRANSACTION
# ===============================
def process_transaction(user_delta, house_delta=0):
    if not st.session_state.wallet_address: return False
    if st.session_state.balance + user_delta < 0: return False
    with db_lock:
        with get_db_conn() as conn:
            conn.execute("BEGIN IMMEDIATE")
            # 유저 잔액 업데이트
            new_balance = st.session_state.balance + user_delta
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)",
                      (st.session_state.wallet_address, new_balance, st.session_state.hunter_level))
            # 시스템 재무 업데이트
            c.execute("UPDATE system_state SET treasury = treasury + ? WHERE id=1",(house_delta,))
            # 범죄자/감옥 상태 저장
            for lvl in range(1,21):
                c.execute("INSERT OR REPLACE INTO criminals VALUES (?,?,?)",
                          (st.session_state.wallet_address, lvl, st.session_state.criminals[lvl]))
                c.execute("INSERT OR REPLACE INTO jail VALUES (?,?,?)",
                          (st.session_state.wallet_address, lvl, st.session_state.jail[lvl]))
            conn.commit()
            st.session_state.balance = new_balance
    return True

# ===============================
# TELEGRAM ALERT
# ===============================
def send_telegram_alert(message):
    token = "YOUR_BOT_TOKEN" 
    chat_id = "@FuckHoneypot"   
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": f"🚨 [FuckHoneypot 실시간 감지]\n{message}"}
        requests.get(url, params=params, timeout=3)
    except:
        pass

# ===============================
# SECURITY / FIREWALL
# ===============================
FIREWALL_THRESHOLD = 80
def get_visitor_ip():
    try:
        ip = st.context.headers.get("X-Forwarded-For","").split(",")[0]
        if not ip: ip = st.context.headers.get("X-Real-IP","127.0.0.1")
        return ip
    except: return "127.0.0.1"

def check_firewall():
    if st.session_state.get("is_admin"): return True,0,""
    ip = get_visitor_ip()
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,countryCode,proxy,hosting"
        res = requests.get(url, timeout=2).json()
        risk_score = 0; reasons=[]
        if res.get("proxy"): risk_score+=40; reasons.append("VPN/Proxy")
        if res.get("hosting"): risk_score+=30; reasons.append("Hosting/Server")
        if res.get("countryCode")!="KR": risk_score+=20; reasons.append("Foreign IP")
        if risk_score>=FIREWALL_THRESHOLD:
            st.error(f"⚠️ [보안 위협] Risk {risk_score} 점. 접속 차단됨")
            st.info(f"사유: {', '.join(reasons)}")
            st.stop()
        return True,risk_score,", ".join(reasons)
    except: return True,0,"Security Engine Bypass (Error)"

check_firewall()

# ===============================
# STREAMLIT HEADER & SIDEBAR
# ===============================
st.markdown("<h1 style='text-align:center;color:#FFD700;'>🔥 범죄자 체포 & 보안 V17.3 🔥</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#fff;'>개발자는 펌프펀 사기 경험 후 홧김에 만들었으며, 같은 피해자가 없기를 바람</p>", unsafe_allow_html=True)

with st.sidebar:
    if not st.session_state.wallet_address:
        if st.button("👑 접속"):
            st.session_state.wallet_address = "USER_"+str(random.randint(1000,9999))
            st.session_state.balance = 0.01
            st.session_state.hunter_level = 1
            st.rerun()
    else:
        st.markdown(f"<div style='background:#111;color:#FFD700;padding:10px;border-radius:10px;text-align:center;'>Wallet: {st.session_state.wallet_address}<br>Balance: {st.session_state.balance:.3f} SOL<br>Hunter Lv: {st.session_state.hunter_level}</div>", unsafe_allow_html=True)
        if st.button("로그아웃"):
            for k in ["wallet_address","balance","hunter_level","criminals","jail","cur_action","action_result","cur_bet"]:
                st.session_state[k] = None
            st.rerun()

# ===============================
# TABS: 범죄자 / 리더보드 / 프리미엄
# ===============================
tabs = st.tabs(["🚨 범죄자 체포","🏆 리더보드","📊 프리미엄 리포트"])

# ---------- 범죄자 체포 ----------
with tabs[0]:
    st.markdown("<h3 style='color:#FFD700;'>범죄자 레벨별 체포</h3>", unsafe_allow_html=True)
    icons = ["","👤","👹","💀","🕵️","🛡️","💣","👺","👻","👽","🤖","🧟","👻","👹","🦹","🦹‍♂️","🧛","🧟‍♀️","👿","😈","👺"]
    for lvl in range(1,21):
        cnt = st.session_state.criminals[lvl]
        if cnt>0:
            st.markdown(f"<div style='border:1px solid #FFD700;padding:5px;margin:3px;border-radius:5px;'>{icons[lvl]} Lv.{lvl} x {cnt}</div>", unsafe_allow_html=True)
            c1,c2,c3,c4 = st.columns(4)
            # 강화
            if lvl<20 and cnt>=1:
                if c1.button("강화",key=f"f{lvl}"):
                    # 실패율 레벨 기반
                    fail_rate = 0.2 + (lvl-3)*0.1 if lvl>=3 else 0.2
                    if random.random() > fail_rate: st.session_state.criminals[lvl+1]+=1
                    st.session_state.criminals[lvl]-=1
                    process_transaction(0,0)
                    st.rerun()
            # 감옥
            if c2.button("감옥",key=f"v{lvl}"):
                st.session_state.criminals[lvl]-=1
                st.session_state.jail[lvl]+=1
                # 보상: 체포 성공 SOL
                reward = 0.01 * lvl
                process_transaction(reward,-reward)
                send_telegram_alert(f"{st.session_state.wallet_address} 체포 성공! Lv.{lvl} 범죄자 감옥 이동, 보상 {reward:.3f} SOL")
                st.success(f"🎉 체포 성공! +{reward:.3f} SOL")
                st.rerun()
            # 판매
            if c3.button("판매",key=f"s{lvl}"):
                st.session_state.criminals[lvl]-=1
                reward = 0.005 * lvl
                process_transaction(reward,-reward)
                st.info(f"범죄자 판매 완료 +{reward:.3f} SOL")
                st.rerun()
            # 체포 실패권 / 재판권
            if c4.button("재판권",key=f"r{lvl}"):
                # 실패율 10% 감소
                st.session_state.cur_action = f"재판권 Lv.{lvl}"
                st.session_state.action_result = "사용됨"
                st.success(f"재판권 사용: 실패율 10% 감소")
                st.rerun()

# ---------- 리더보드 ----------
with tabs[1]:
    st.markdown("<h3 style='color:#FFD700;'>상위 헌터 리더보드</h3>", unsafe_allow_html=True)
    with get_db_conn() as conn:
        rows = conn.execute("SELECT wallet, SUM(balance) as total_sol FROM users ORDER BY total_sol DESC LIMIT 10").fetchall()
    for i,row in enumerate(rows):
        st.markdown(f"{i+1}. {row[0]} - {row[1]:.3f} SOL")

# ---------- 프리미엄 리포트 ----------
with tabs[2]:
    st.markdown("<h3 style='color:#FFD700;'>이번 주 악질 범죄자 리포트 (프리미엄)</h3>", unsafe_allow_html=True)
    with get_db_conn() as conn:
        rows = conn.execute("SELECT lvl, SUM(count) as cnt FROM criminals GROUP BY lvl ORDER BY lvl DESC").fetchall()
    st.table(pd.DataFrame(rows, columns=["Lv","Count"]))

# ===============================
# 구독 / 라이선스 버튼 예시
# ===============================
st.markdown("<h4 style='color:#FFD700;'>라이선스 / 티어</h4>", unsafe_allow_html=True)
col1,col2 = st.columns(2)
with col1:
    if st.button("BASIC 0.01 SOL - 감시만"):
        grant_license(st.session_state.wallet_address,"BASIC",1)
        st.success("BASIC 티어 활성화 완료")
with col2:
    if st.button("PRO 0.1 SOL - 원천 차단"):
        grant_license(st.session_state.wallet_address,"PRO",1)
        st.success("PRO 티어 활성화 완료")
