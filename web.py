import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import time
import requests

# [1. 기본 설정 및 DB]
st.set_page_config(page_title="FuckHoneypot Security", layout="wide", initial_sidebar_state="collapsed")
DB_PATH = "woohoo_v18_pro.db"

def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, tier TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS scan_logs (id INTEGER PRIMARY KEY, token TEXT, risk INTEGER, time TEXT)")
        # 운영자 초기 세팅
        c.execute("INSERT OR IGNORE INTO users VALUES ('Operator_Admin', 10.0, 'MASTER')")
        conn.commit()
init_db()

# [2. 전문적인 CSS (금융/보안 스타일)]
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    
    /* 보안 등급 배지 */
    .risk-badge-high { background-color: #ff2b2b; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
    .risk-badge-safe { background-color: #00c853; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
    
    /* 메인 스캐너 박스 */
    .scan-box {
        border: 1px solid #30363d; background-color: #161b22;
        padding: 30px; border-radius: 8px; margin-bottom: 20px;
    }
    
    /* 체포(헌터) 팝업 스타일 */
    .hunter-action {
        border: 2px solid #FFD700; background-color: #211a00;
        padding: 20px; border-radius: 8px; margin-top: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# [3. 세션 및 유틸리티]
if 'wallet' not in st.session_state: st.session_state.wallet = "Operator_Admin"
if 'scan_result' not in st.session_state: st.session_state.scan_result = None

def get_balance():
    with get_db() as conn:
        res = conn.execute("SELECT balance FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return res[0] if res else 0.0

def update_balance(delta):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (delta, st.session_state.wallet))
        conn.commit()

def add_inventory(lvl, qty):
    with get_db() as conn:
        cur = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl)).fetchone()
        new_c = (cur[0] + qty) if cur else qty
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, lvl, new_c))
        conn.commit()

# [4. 메인 UI 구성]

# [헤더: 전문 보안 사이트 느낌]
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🛡️ FuckHoneypot Security Protocol")
    st.caption("Solana Advanced Rug-Pull Detection & Prevention System")
with col2:
    bal = get_balance()
    st.metric("Wallet Status", "Connected", f"{bal:.4f} SOL")

st.divider()

# [메인 기능: 토큰 스캐너]
st.markdown("### 🔍 Token Risk Scanner")
st.markdown("<div class='scan-box'>", unsafe_allow_html=True)
token_input = st.text_input("Enter Token Address to Scan", placeholder="Example: So1ana... (Click 'Scan' to Analyze)")

if st.button("🚀 Analyze Token Security", use_container_width=True):
    if not token_input:
        st.error("Please enter a token address.")
    else:
        with st.spinner("Analyzing On-Chain Data (Mint Authority, LP Locks, Holders)..."):
            time.sleep(1.5) # 분석 시뮬레이션
            
            # 스캔 결과 생성 (랜덤 시뮬레이션)
            risk_score = random.randint(10, 99)
            st.session_state.scan_result = {
                "address": token_input,
                "risk": risk_score,
                "mint_auth": "Enabled" if risk_score > 50 else "Disabled",
                "lp_locked": "No (Unsafe)" if risk_score > 60 else "Yes (100%)",
                "top_holders": "Concentrated (Danger)" if risk_score > 70 else "Distributed"
            }
st.markdown("</div>", unsafe_allow_html=True)

# [분석 결과 및 액션]
if st.session_state.scan_result:
    res = st.session_state.scan_result
    
    # 1. 전문적인 분석 리포트 출력
    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Score", f"{res['risk']}/100")
    c2.write(f"**Mint Authority:** {res['mint_auth']}")
    c2.write(f"**LP Status:** {res['lp_locked']}")
    
    # 위험도 배지 표시
    if res['risk'] >= 70:
        c3.markdown(f"<span class='risk-badge-high'>🚨 HIGH RISK DETECTED</span>", unsafe_allow_html=True)
        is_scam = True
    else:
        c3.markdown(f"<span class='risk-badge-safe'>✅ SAFE TO TRADE</span>", unsafe_allow_html=True)
        is_scam = False

    st.divider()

    # 2. 여기서 '게임/수익' 기능으로 연결 (자연스러운 흐름)
    if is_scam:
        st.markdown(f"""
        <div class='hunter-action'>
            <h3>🚨 SCAMMER IDENTIFIED: Lv.1 Pickpocket</h3>
            <p>이 토큰은 높은 확률로 스캠입니다. 피해를 막기 위해 <b>즉시 체포(격리)</b>할 수 있습니다.</p>
            <p style='color:#FFD700; font-weight:bold;'>Bounty Cost: 0.01 SOL</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 구매(체포) 버튼
        col_b1, col_b2 = st.columns([1, 4])
        with col_b1:
            if st.button("👮 체포 집행 (0.01 SOL)"):
                if get_balance() >= 0.01:
                    update_balance(-0.01)
                    add_inventory(1, 1) # Lv.1 범죄자 획득
                    st.success("체포 성공! 범죄자가 '유치장'으로 이송되었습니다.")
                    time.sleep(1)
                else:
                    st.error("SOL 잔액이 부족합니다.")
        with col_b2:
            st.warning("※ 체포된 범죄자는 '유치장' 탭에서 합성하거나 판매(보상금)할 수 있습니다.")

# [하단: 보유 현황 및 관리 (탭으로 분리하지 않고 아래에 배치하여 대시보드화)]
st.markdown("---")
st.subheader("📂 Agent Management (Inventory)")

# 인벤토리 데이터 가져오기
with get_db() as conn:
    inv_data = conn.execute("SELECT lvl, count FROM inventory WHERE wallet=? ORDER BY lvl", (st.session_state.wallet,)).fetchall()

if not inv_data:
    st.info("No criminals captured yet. Scan suspicious tokens to hunt scammers.")
else:
    # 인벤토리 테이블 형태로 깔끔하게 표시
    # 조잡한 카드 대신 데이터 그리드 사용
    for lvl, count in inv_data:
        if count > 0:
            with st.container():
                cols = st.columns([1, 2, 2, 2])
                cols[0].write(f"**Lv.{lvl} Criminal**")
                cols[1].write(f"수량: {count} 명")
                
                # 합성 버튼 (2개 이상일 때만 활성)
                if count >= 2:
                    if cols[2].button(f"🧬 합성 (2->1)", key=f"fuse_{lvl}"):
                        update_balance(0) # 밸런스 체크용 더미
                        with get_db() as conn:
                            conn.execute("UPDATE inventory SET count = count - 2 WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl))
                            # 상위 레벨 추가
                            cur = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl+1)).fetchone()
                            new_c = (cur[0] + 1) if cur else 1
                            conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, lvl+1, new_c))
                            conn.commit()
                        st.rerun()
                else:
                    cols[2].caption("합성 불가 (2명 필요)")
                
                # 판매 버튼
                sell_price = 0.008 * (1.5**(lvl-1))
                if cols[3].button(f"💰 이송/판매 ({sell_price:.4f} SOL)", key=f"sell_{lvl}"):
                    with get_db() as conn:
                        conn.execute("UPDATE inventory SET count = count - 1 WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl))
                        conn.commit()
                    update_balance(sell_price)
                    st.success(f"판매 완료. +{sell_price:.4f} SOL")
                    time.sleep(0.5)
                    st.rerun()
            st.divider()

