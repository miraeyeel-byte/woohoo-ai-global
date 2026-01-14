# ===============================
# V17.10 WOOHOO / FuckHoneypot Security Dashboard
# ===============================

# ===============================
# IMPORTS
# ===============================
import os
import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import sqlite3
import html
import threading
import requests
import ipaddress
import datetime

# ===============================
# DB & PERSISTENT STORAGE 설정
# ===============================
DB_PATH = os.getenv("DB_PATH", "woohoo_master_v17.db")
db_dir = os.path.dirname(DB_PATH)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

db_lock = threading.Lock()

def get_db_conn():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        # 사용자, 인벤토리, 체포 히어로(범죄자), 감옥, 시스템 상태, 라이선스, 채팅, 프리미엄 리포트
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, nodes INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS criminals (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet,lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS jail (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet,lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS system_state (id INTEGER PRIMARY KEY CHECK(id=1), treasury REAL)")
        c.execute("INSERT OR IGNORE INTO system_state VALUES (1,1000)")
        c.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, message TEXT, time TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS licenses (wallet TEXT PRIMARY KEY, expiry_time TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS premium_reports (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, report TEXT, time TEXT)")
        conn.commit()

init_db()

# ===============================
# SESSION INIT
# ===============================
def init_session():
    defaults = {
        "wallet_address": None,
        "is_admin": False,
        "balance": 0.1,  # SOL 기본
        "owned_nodes": 0,
        "criminals": {i:0 for i in range(1,21)},  # 레벨1~20
        "jail": {i:0 for i in range(1,21)},
        "op_lock": False
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ===============================
# SECURITY / FIREWALL ENGINE
# ===============================
FIREWALL_THRESHOLD = 80  # 고위험 접속 차단 임계치

def get_visitor_ip():
    try:
        ip = st.context.headers.get("X-Forwarded-For", "").split(",")[0]
        if not ip: ip = st.context.headers.get("X-Real-IP", "127.0.0.1")
        return ip
    except:
        return "127.0.0.1"

def analyze_security_risk(ip, allowed_countries=["KR"]):
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback:
            return "내부망", 0, "비정상적인 접근"
    except:
        return "입력 오류", 0, "IP 형식 오류"

    res_data = None
    for _ in range(2):
        try:
            url = f"https://ip-api.com/json/{ip}?fields=status,countryCode,proxy,hosting"
            r = requests.get(url, timeout=3)
            if r.status_code==200: res_data=r.json(); break
        except: continue

    if not res_data or res_data.get('status')!="success":
        return "분석 실패", 0, "데이터 확인 불가"

    risk = 0; reasons=[]
    if res_data.get('proxy'): risk+=40; reasons.append("VPN/Proxy")
    if res_data.get('hosting'): risk+=30; reasons.append("Hosting/Server")
    if res_data.get('countryCode') not in allowed_countries: risk+=20; reasons.append("Foreign IP")
    risk = min(risk,100)
    return ("고위험" if risk>=FIREWALL_THRESHOLD else "일반"), risk, ", ".join(reasons)

def check_firewall():
    if st.session_state.get("is_admin"): return True,0,""
    ip = get_visitor_ip()
    status,risk,reason = analyze_security_risk(ip)
    if risk>=FIREWALL_THRESHOLD:
        st.error(f"⚠️ 고위험 접속 감지 (Risk: {risk})")
        st.info(f"사유: {reason}")
        st.stop()
    return True,risk,reason

can_proceed,current_risk,risk_desc = check_firewall()

# ===============================
# LICENSE ENGINE
# ===============================
def check_license(wallet):
    if not wallet: return False
    with get_db_conn() as conn:
        row = conn.execute("SELECT expiry_time FROM licenses WHERE wallet=?", (wallet,)).fetchone()
    if not row: return False
    expiry=datetime.datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S")
    return expiry>datetime.datetime.now()

def grant_license(wallet,hours):
    expiry=datetime.datetime.now()+datetime.timedelta(hours=hours)
    with db_lock:
        with get_db_conn() as conn:
            conn.execute("INSERT OR REPLACE INTO licenses VALUES (?,?)",
                         (wallet,expiry.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

# ===============================
# TELEGRAM ALERT
# ===============================
def send_telegram_alert(message):
    token="YOUR_BOT_TOKEN"
    chat_id="@FuckHoneypot"
    try:
        url=f"https://api.telegram.org/bot{token}/sendMessage"
        params={"chat_id":chat_id,"text":f"🚨 [FuckHoneypot Alert]\n{message}"}
        requests.get(url,params=params,timeout=3)
    except: pass

# ===============================
# CRIMINAL / CAPTURE SYSTEM
# ===============================
def process_capture(lvl, count, use_upgrade=False, use_retry=False):
    """
    lvl: 범죄자 레벨 1~20
    count: 몇 명 체포
    use_upgrade: 강화권 사용
    use_retry: 재판권 사용
    """
    base_fail = 10+(lvl-1)*5  # 레벨별 기본 실패율 1레벨10%, 2레벨15%, 3레벨20%, ...
    if use_upgrade: base_fail -= 10
    if use_retry: base_fail -= 10
    base_fail = max(5,min(base_fail,90))
    
    success = 0
    for _ in range(count):
        if random.randint(1,100)>base_fail:
            success+=1
            # Jail 이동
            st.session_state.jail[lvl]+=1
            st.session_state.criminals[lvl]-=1
            # 보상: 레벨 * 0.01 SOL
            st.session_state.balance+=0.01*lvl
            send_telegram_alert(f"{st.session_state.wallet_address}님이 레벨{lvl} 범죄자 체포 성공! 보상: {0.01*lvl:.3f} SOL")
    return success, count-success, base_fail

# ===============================
# STREAMLIT UI
# ===============================
st.set_page_config(page_title="🚨 FuckHoneypot V17.10", layout="wide")

st.markdown("""
<h1 style='color:red;text-align:center;'>🚨 FuckHoneypot Security Dashboard</h1>
<p style='text-align:center;color:#fff;'>Developed to fight scammers after being burned by pump/fun coins. Stay safe, protect your wallet!</p>
""",unsafe_allow_html=True)

# Sidebar: 로그인
with st.sidebar:
    if not st.session_state.wallet_address:
        if st.button("Connect Wallet"):
            st.session_state.wallet_address="USER_01"
            st.session_state.balance=0.1
            st.rerun()
    else:
        st.markdown(f"<div style='color:gold'>Wallet: {st.session_state.wallet_address}<br>Balance: {st.session_state.balance:.3f} SOL</div>",unsafe_allow_html=True)
        if st.button("Logout"):
            for k in st.session_state.keys(): st.session_state[k]=None
            st.rerun()

# Tabs
tabs=st.tabs(["⚡ Overview","🕵️ Criminal Capture","📊 Premium Reports"])

# ---------- Overview ----------
with tabs[0]:
    st.write("Welcome to FuckHoneypot! Protect your wallet, track suspicious tokens, and become a bounty hunter!")
    st.metric("Current Risk Level", current_risk)

# ---------- Criminal Capture ----------
with tabs[1]:
    st.markdown("## 🕵️ Capture Virtual Criminals")
    lvl = st.selectbox("범죄자 레벨 선택", list(range(1,21)))
    count = st.number_input("몇 명 체포?", min_value=1, max_value=20, value=1)
    upgrade = st.checkbox("Use Upgrade (강화권, 실패율 감소)")
    retry = st.checkbox("Use Retry (재판권, 실패율 추가 감소)")
    
    if st.button("Capture"):
        success, fail, fail_rate = process_capture(lvl,count,upgrade,retry)
        st.success(f"체포 성공: {success} / 실패: {fail} (Fail Rate: {fail_rate}%)")
        # 화려한 UI 연출
        st.balloons()
        st.toast(f"👏 {success} 범죄자 체포 성공! 보상 지급 완료!")

# ---------- Premium Reports ----------
with tabs[2]:
    st.markdown("## 📊 Premium Rugger Reports")
    with get_db_conn() as conn:
        rows=conn.execute("SELECT wallet,report,time FROM premium_reports ORDER BY id DESC LIMIT 10").fetchall()
    for w,r,t in rows:
        st.markdown(f"{t} | {w[:6]}: {r}")

# ===============================
# LICENSE / SUBSCRIPTION UI
# ===============================
with st.sidebar:
    st.markdown("## 🏷 License Options")
    if st.button("Activate 0.01 SOL Basic License (Observation)"):
        grant_license(st.session_state.wallet_address,1)
        st.success("✅ Basic license granted")
        st.rerun()
    if st.button("Activate 0.1 SOL Pro License (Full Block)"):
        grant_license(st.session_state.wallet_address,24)
        st.success("✅ Pro license granted")
        st.rerun()
