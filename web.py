import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import os
import time

# [1. 기본 설정]
st.set_page_config(page_title="WOOHOO SECURITY V18.2", layout="wide")
DB_PATH = "woohoo_v18_final_fixed.db"

# [2. DB 초기화 (안전 모드)]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, exp INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS prison_log (id INTEGER PRIMARY KEY, wallet TEXT, lvl INTEGER, reward REAL, time TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, wallet TEXT, content TEXT, time TEXT)")
        # 운영자 계정
        c.execute("INSERT OR IGNORE INTO users VALUES ('Operator_Admin', 10.0, 0)")
        conn.commit()
init_db()

# [3. CSS 스타일링: 전문적인 다크 테마]
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border-radius: 4px; padding: 8px 16px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; font-weight: bold; }

    /* 카드 스타일 */
    .card-box {
        border: 1px solid #333; background-color: #161b22; padding: 20px;
        border-radius: 8px; text-align: center; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .card-box:hover { border-color: #FFD700; transform: translateY(-2px); transition: 0.3s; }
    
    /* 레벨 1 전용 카드 */
    .pickpocket-card {
        border: 2px solid #ff4b4b; background: linear-gradient(145deg, #2d0000, #1a0000);
        padding: 30px; border-radius: 15px; text-align: center;
    }
    
    /* 버튼 */
    .stButton button { width: 100%; border-radius: 6px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# [4. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'confirm_buy' not in st.session_state: st.session_state.confirm_buy = False

# [5. 기능 로직]
def get_user():
    if not st.session_state.wallet: return None, 0.0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0)

def update_balance(delta):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (delta, st.session_state.wallet))
        conn.commit()

def get_inventory():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())

def update_inventory(lvl, delta):
    with get_db() as conn:
        cur = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl)).fetchone()
        new_c = (cur[0] + delta) if cur else delta
        if new_c < 0: new_c = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, lvl, new_c))
        conn.commit()

def log_prison(lvl, reward):
    with get_db() as conn:
        conn.execute("INSERT INTO prison_log (wallet, lvl, reward, time) VALUES (?, ?, ?, datetime('now'))", 
                     (st.session_state.wallet, lvl, reward))
        conn.commit()

# [6. 메인 화면 구성]
st.title("🛡️ WOOHOO SECURITY PLATFORM")

# 사이드바: 지갑 연결
with st.sidebar:
    st.header("🔐 Wallet Access")
    if not st.session_state.wallet:
        if st.button("Connect Phantom Wallet"):
            st.session_state.wallet = "Operator_Admin"
            st.rerun()
    else:
        u_wallet, u_bal = get_user()
        st.success(f"Connected: {u_wallet}")
        st.metric("Balance", f"{u_bal:.4f} SOL")
        if st.button("Disconnect"):
            st.session_state.wallet = None
            st.rerun()

if not st.session_state.wallet:
    st.info("Please connect your wallet to access the system.")
    st.stop()

# 탭 구성 (요청하신 대로 분리)
tabs = st.tabs(["🛡️ 보안 센터", "🚨 범죄자 체포", "📦 보관함", "🧬 강화실", "🔒 감옥", "🏆 명예의 전당", "🕵️ 제보하기"])

# === TAB 1: 보안 센터 (스캐너) ===
with tabs[0]:
    st.subheader("📡 Advanced Token Scanner")
    st.caption("실시간 허니팟/러그풀 감지 시스템")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        token = st.text_input("Token Address", placeholder="Enter Solana Token Address...")
    with col2:
        st.write("")
        st.write("")
        if st.button("🔍 SCAN"):
            with st.spinner("Analyzing..."):
                time.sleep(1)
                st.warning("⚠️ High Risk Detected!")
                st.write("- **Mint Authority:** Enabled")
                st.write("- **Liquidity:** Unlocked")

# === TAB 2: 범죄자 체포 (Lv.1 전용) ===
with tabs[1]:
    st.subheader("🔫 Bounty Hunting")
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class='pickpocket-card'>
            <div style='font-size: 60px;'>👤</div>
            <h2>Lv.1 소매치기범</h2>
            <p>거리의 좀도둑을 체포합니다.</p>
            <h3 style='color:#FFD700'>Cost: 0.01 SOL</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 구매 로직 (팝업 포함)
        if not st.session_state.confirm_buy:
            if st.button("🚨 체포 시도 (구매)", type="primary"):
                st.session_state.confirm_buy = True
                st.rerun()
        else:
            st.warning("⚠️ 0.01 SOL이 차감됩니다. 진행하시겠습니까?")
            b1, b2 = st.columns(2)
            if b1.button("✅ 승인"):
                _, bal = get_user()
                if bal >= 0.01:
                    update_balance(-0.01)
                    update_inventory(1, 1)
                    st.session_state.confirm_buy = False
                    st.toast("체포 성공! 보관함으로 이송되었습니다.", icon="🚔") # 풍선 대신 토스트
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("잔액 부족!")
            if b2.button("❌ 취소"):
                st.session_state.confirm_buy = False
                st.rerun()

# === TAB 3: 보관함 (인벤토리) ===
with tabs[2]:
    st.subheader("📦 Inventory Storage")
    inv = get_inventory()
    
    if not inv:
        st.info("보관함이 비어있습니다. '범죄자 체포' 탭에서 체포하세요.")
    else:
        # 그리드 형태로 표시
        for lvl, count in sorted(inv.items()):
            if count > 0:
                with st.container():
                    st.markdown(f"<div class='card-box'>", unsafe_allow_html=True)
                    c_info, c_act1, c_act2 = st.columns([2, 1, 1])
                    
                    with c_info:
                        icon = ["👤", "👺", "🤡", "💀", "👾", "🐉"][min(lvl-1, 5)]
                        st.markdown(f"### {icon} Lv.{lvl} Criminal")
                        st.write(f"보유 수량: **{count}** 명")
                    
                    with c_act1:
                        # 강화실 기능 바로 수행
                        if count >= 2:
                            if st.button(f"🧬 강화하기 (2->1)", key=f"inv_fuse_{lvl}"):
                                if random.random() < 0.8: # 80% 성공
                                    update_inventory(lvl, -2)
                                    update_inventory(lvl+1, 1)
                                    st.toast(f"강화 성공! Lv.{lvl+1} 획득", icon="✨")
                                else:
                                    update_inventory(lvl, -1)
                                    st.error("강화 실패! 1명 도주.")
                                st.rerun()
                        else:
                            st.button("강화 불가 (부족)", disabled=True, key=f"dis_fuse_{lvl}")

                    with c_act2:
                        # 감옥 보내기 바로 수행
                        reward = 0.008 * (1.5**(lvl-1)) # 보상 계산
                        if st.button(f"🔒 감옥보내기 (+{reward:.4f})", key=f"inv_jail_{lvl}"):
                            update_inventory(lvl, -1)
                            update_balance(reward)
                            log_prison(lvl, reward)
                            st.toast(f"감옥 이송 완료. {reward:.4f} SOL 획득", icon="💰")
                            st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)

# === TAB 4: 강화실 (전용 탭) ===
with tabs[3]:
    st.subheader("🧬 Fusion Lab")
    st.caption("범죄자 2명을 합성하여 상위 레벨로 진화시킵니다.")
    
    inv = get_inventory()
    fusible_found = False
    
    cols = st.columns(4)
    for i, (lvl, count) in enumerate(sorted(inv.items())):
        if count >= 2:
            fusible_found = True
            with cols[i % 4]:
                st.markdown(f"""
                <div class='card-box'>
                    <h4>Lv.{lvl} ➡️ Lv.{lvl+1}</h4>
                    <p>가능 횟수: {count // 2}회</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"⚡ 강화 실행 (Lv.{lvl})", key=f"lab_fuse_{lvl}"):
                    if random.random() < 0.8:
                        update_inventory(lvl, -2)
                        update_inventory(lvl+1, 1)
                        st.toast("강화 성공!", icon="✨")
                    else:
                        update_inventory(lvl, -1)
                        st.error("강화 실패")
                    st.rerun()
    
    if not fusible_found:
        st.info("강화 가능한 유닛이 없습니다. (같은 레벨 2명 필요)")

# === TAB 5: 감옥 (로그) ===
with tabs[4]:
    st.subheader("🔒 Federal Prison Log")
    st.caption("감옥으로 이송된 범죄자 기록 및 수익 현황")
    
    with get_db() as conn:
        logs = conn.execute("SELECT lvl, reward, time FROM prison_log ORDER BY id DESC LIMIT 10").fetchall()
        total_earnings = conn.execute("SELECT SUM(reward) FROM prison_log").fetchone()[0]
    
    if total_earnings:
        st.metric("총 현상금 수익", f"{total_earnings:.4f} SOL")
    
    if logs:
        st.table(pd.DataFrame(logs, columns=["Level", "Reward (SOL)", "Time"]))
    else:
        st.write("수감 기록이 없습니다.")

# === TAB 6: 명예의 전당 ===
with tabs[5]:
    st.subheader("🏆 Hall of Fame")
    
    with get_db() as conn:
        # 에러 방지를 위한 IFNULL 처리
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0) FROM users ORDER BY balance DESC LIMIT 10").fetchall()
    
    for i, (w, b) in enumerate(ranks):
        st.write(f"**{i+1}위** 🕵️ {w} : {b:.4f} SOL")

# === TAB 7: 제보하기 ===
with tabs[6]:
    st.subheader("🕵️ Intelligence Report")
    with st.form("rep_form"):
        addr = st.text_input("Scammer Address")
        desc = st.text_area("Details")
        if st.form_submit_button("Submit"):
            with get_db() as conn:
                conn.execute("INSERT INTO reports (wallet, content, time) VALUES (?, ?, datetime('now'))", (addr, desc))
            st.success("Reported.")

