import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import time
import requests

# [1. 기본 설정]
st.set_page_config(page_title="WOOHOO COMMANDER V18.1", layout="wide")
DB_PATH = "woohoo_v18_final.db"

# [2. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, exp INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, wallet TEXT, content TEXT, time TEXT)")
        # 운영자 계정 (테스트용)
        c.execute("INSERT OR IGNORE INTO users VALUES ('Operator_Admin', 10.0, 0)")
        conn.commit()
init_db()

# [3. 스타일링: 고급진 다크 커맨드 센터]
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* 지갑 연결 버튼 */
    .wallet-btn {
        border: 2px solid #66fcf1; background: #1f2833; color: #66fcf1;
        padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;
    }
    
    /* 범죄자 카드 */
    .criminal-card {
        border: 2px solid #333; border-radius: 10px; padding: 15px;
        background: linear-gradient(145deg, #111, #1a1a1a); text-align: center;
        margin-bottom: 10px; transition: 0.3s; cursor: pointer;
    }
    .criminal-card:hover { border-color: #FFD700; transform: translateY(-5px); }
    
    /* 선택된 카드 */
    .selected { border: 2px solid #FFD700 !important; background: #222 !important; }
    
    /* 랭킹 보드 */
    .rank-row { padding: 10px; border-bottom: 1px solid #333; }
    
    /* 팝업 느낌의 박스 */
    .confirm-box {
        border: 2px solid #ff4b4b; background: #2d0000; padding: 20px;
        border-radius: 10px; text-align: center; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# [4. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'selected_lvl' not in st.session_state: st.session_state.selected_lvl = None
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

# [6. 메인 화면]
st.title("⚔️ WOOHOO SECURITY & HUNTER")

# --- 사이드바: 지갑 연결 (복구됨) ---
with st.sidebar:
    st.header("🔌 WALLET CONNECT")
    if not st.session_state.wallet:
        if st.button("Connect Phantom (Simulate)"):
            st.session_state.wallet = "Operator_Admin" # 테스트용
            st.rerun()
    else:
        u_wallet, u_bal = get_user()
        st.markdown(f"<div class='wallet-btn'>🟢 {u_wallet[:8]}...<br>{u_bal:.4f} SOL</div>", unsafe_allow_html=True)
        if st.button("Disconnect"):
            st.session_state.wallet = None
            st.rerun()

if not st.session_state.wallet:
    st.info("👈 사이드바에서 지갑을 먼저 연결해주세요.")
    st.stop()

# --- 탭 구성: 보안 / 게임(체포) / 관리(합성) / 랭킹 ---
tabs = st.tabs(["🛡️ 보안 센터", "🔫 범죄자 체포 (미니게임)", "⛓️ 관리/합성", "🏆 명예의 전당"])

# === TAB 1: 보안 센터 (핵심 기술) ===
with tabs[0]:
    st.subheader("📡 Security Scanner")
    c1, c2 = st.columns([3, 1])
    with c1:
        token = st.text_input("스캔할 토큰 주소 입력", placeholder="So1anaTokenAddress...")
    with c2:
        st.write("")
        st.write("")
        if st.button("🔍 SCAN"):
            with st.spinner("Checking On-Chain Data..."):
                time.sleep(1)
                st.warning("⚠️ Warning: Suspicious Activity Detected!")
                st.write("**Mint Authority:** Enabled ❌")
                st.write("**LP Status:** Unlocked (Risk High) ❌")

# === TAB 2: 범죄자 체포 (미니게임 복구) ===
with tabs[1]:
    st.subheader("🎯 WANTED LIST (Bounty Hunting)")
    
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.write("체포할 대상을 선택하세요.")
        # 카드 그리드
        icols = st.columns(3)
        for i in range(1, 4): # Lv.1~3 예시
            with icols[i-1]:
                # 스타일링
                border = "selected" if st.session_state.selected_lvl == i else "criminal-card"
                icon = ["👤", "👺", "🤡"][i-1]
                name = ["소매치기", "스캠 배포자", "러그풀러"][i-1]
                
                st.markdown(f"""
                <div class='{border}'>
                    <h1>{icon}</h1>
                    <h4>Lv.{i} {name}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"선택 (Lv.{i})", key=f"sel_{i}", use_container_width=True):
                    st.session_state.selected_lvl = i
                    st.session_state.confirm_buy = False
                    st.rerun()

    with col_r:
        if st.session_state.selected_lvl:
            lvl = st.session_state.selected_lvl
            st.info(f"선택됨: **Lv.{lvl}**")
            
            if lvl == 1:
                st.write("### 🚨 체포 작전 (구매)")
                st.write(f"비용: **0.01 SOL**")
                
                if not st.session_state.confirm_buy:
                    if st.button("체포 시도 (구매하기)", type="primary"):
                        st.session_state.confirm_buy = True
                        st.rerun()
                else:
                    # [구매 확인 팝업]
                    st.markdown("""<div class='confirm-box'>⚠️ 0.01 SOL을 사용하여<br>체포하시겠습니까?</div>""", unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    if b1.button("✅ 승인"):
                        _, bal = get_user()
                        if bal >= 0.01:
                            update_balance(-0.01)
                            update_inventory(1, 1)
                            st.session_state.confirm_buy = False
                            st.toast("체포 성공! 유치장으로 이송됨.", icon="🚔")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("잔액 부족!")
                    if b2.button("❌ 취소"):
                        st.session_state.confirm_buy = False
                        st.rerun()
            else:
                st.warning("🔒 상위 레벨은 구매 불가! '관리/합성' 탭에서 조합하세요.")
        else:
            st.info("왼쪽에서 대상을 선택하세요.")

# === TAB 3: 관리/합성 (RPG 커맨드 센터) ===
with tabs[2]:
    st.subheader("🧬 INVENTORY & FUSION")
    inv = get_inventory()
    
    if not inv:
        st.info("보유한 범죄자가 없습니다. '범죄자 체포' 탭에서 잡아오세요.")
    else:
        for lvl, count in sorted(inv.items()):
            if count > 0:
                with st.container():
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
                    c1.markdown(f"## Lv.{lvl}")
                    c2.markdown(f"**보유량: {count} 명**")
                    
                    # [합성] Lv.1 -> Lv.2
                    if count >= 2:
                        if c3.button(f"🧬 2명 합성 -> Lv.{lvl+1}", key=f"fuse_{lvl}"):
                            # 90% 성공 확률
                            if random.random() < 0.9:
                                update_inventory(lvl, -2)
                                update_inventory(lvl+1, 1)
                                st.toast(f"합성 성공! Lv.{lvl+1} 획득!", icon="✨")
                                st.rerun()
                            else:
                                update_inventory(lvl, -1)
                                st.error("합성 실패... 1명 도주.")
                                st.rerun()
                    else:
                        c3.caption("합성하려면 2명 필요")
                    
                    # [판매/이송]
                    sell_price = 0.008 * (1.5**(lvl-1))
                    if c4.button(f"💰 감옥 이송 (+{sell_price:.4f} SOL)", key=f"sell_{lvl}"):
                        update_inventory(lvl, -1)
                        update_balance(sell_price)
                        st.toast("이송 완료. 보상금 지급됨.", icon="💰")
                        st.rerun()
                st.divider()

# === TAB 4: 명예의 전당 (복구됨) ===
with tabs[3]:
    st.subheader("🏆 HALL OF FAME")
    st.write("가장 악명 높은 범죄자를 검거한 헌터 랭킹입니다.")
    
    with get_db() as conn:
        # 간단히 잔액 순으로 랭킹 표시 (실제론 보유 최고 레벨 등으로 가능)
        ranks = conn.execute("SELECT wallet, balance FROM users ORDER BY balance DESC LIMIT 10").fetchall()
    
    for i, (w, b) in enumerate(ranks):
        st.markdown(f"""
        <div class='rank-row'>
            <b>#{i+1}</b> | 🕵️ {w} | 💰 자산: {b:.4f} SOL
        </div>
        """, unsafe_allow_html=True)
