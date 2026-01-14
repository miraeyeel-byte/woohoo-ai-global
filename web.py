import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import os
import time

# [1. 기본 설정]
st.set_page_config(page_title="WOOHOO DARK JUSTICE V18.3", layout="wide")
DB_PATH = "woohoo_v18_final_fixed.db"

# [2. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, exp INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS prison_log (id INTEGER PRIMARY KEY, wallet TEXT, lvl INTEGER, reward REAL, time TEXT)")
        # 운영자 계정
        c.execute("INSERT OR IGNORE INTO users VALUES ('Operator_Admin', 10.0, 0)")
        conn.commit()
init_db()

# [3. CSS 스타일링: 다크 테마 + 밝은 글씨]
st.markdown("""
<style>
    /* 전체 배경 어둡게, 글씨 밝게 */
    .stApp { background-color: #050505; color: #e0e0e0 !important; }
    h1, h2, h3, h4, h5, h6, p, div, span { color: #e0e0e0 !important; text-shadow: 1px 1px 2px #000; }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border-radius: 4px; padding: 8px 16px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; font-weight: bold; text-shadow: none; }

    /* 카드 스타일 (어두운 배경 + 밝은 테두리/글씨) */
    .card-box {
        border: 2px solid #FFD700; background: linear-gradient(145deg, #111, #1a1a1a);
        padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: 0.3s;
    }
    .card-box:hover { border-color: #66fcf1; transform: translateY(-3px); box-shadow: 0 0 15px #66fcf1; }
    
    /* 강조 텍스트 */
    .gold-text { color: #FFD700 !important; font-weight: bold; }
    .neon-text { color: #66fcf1 !important; font-weight: bold; }
    
    /* 버튼 */
    .stButton button { width: 100%; border-radius: 6px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# [4. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None

# [5. 범죄자 데이터 (20단계)]
CRIMINALS = {
    1: ("👤", "소매치기"), 2: ("👺", "스캠 링크 배포자"), 3: ("🤡", "러그풀 개발자"), 4: ("💀", "해킹 조직원"),
    5: ("👾", "악성 봇 제작자"), 6: ("🐉", "작전 세력 팀장"), 7: ("👹", "다단계 사기꾼"), 8: ("👽", "신원 도용범"),
    9: ("🤖", "AI 사기 설계자"), 10: ("☠️", "금융 테러리스트"), 11: ("🧛", "흡혈 고래"), 12: ("🧟", "좀비 지갑 관리자"),
    13: ("👻", "유령 회사 대표"), 14: ("👿", "악마의 계약자"), 15: ("🦄", "가짜 유니콘 CEO"), 16: ("🐲", "고대 폰지 설계자"),
    17: ("🧙‍♂️", "흑마법사"), 18: ("🦸‍♂️", "타락한 영웅"), 19: ("👑", "사기 공화국 왕"), 20: ("🪐", "우주적 사기꾼")
}

# [6. 기능 로직]
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

def gacha_pull(times):
    """범인 뽑기 (확률 가중치 적용)"""
    levels = list(range(1, 21))
    # 레벨이 높을수록 확률 급격히 감소 (예시 가중치)
    weights = [1000, 600, 300, 150, 80, 40, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.001, 0.0001]
    results = random.choices(levels, weights=weights, k=times)
    return results

# [7. 메인 화면 구성]
st.title("🚓 WOOHOO DARK JUSTICE")

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

# 탭 구성
tabs = st.tabs(["🛡️ 보안 센터", "🚓 범인 잡기 (뽑기)", "📦 보관소 (관리/합성)", "🏆 명예의 전당"])

# === TAB 1: 보안 센터 (유지) ===
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
                st.warning("⚠️ High Risk Detected! (Simulation)")

# === TAB 2: 범인 잡기 (미니게임 - 뽑기) ===
with tabs[1]:
    st.subheader("🚓 범죄자 소탕 작전 (Gacha)")
    st.write("비용을 지불하고 랜덤한 범죄자를 검거합니다. <span class='gold-text'>실패는 없습니다.</span>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    def pull_action(cost, times):
        _, bal = get_user()
        if bal >= cost:
            update_balance(-cost)
            results = gacha_pull(times)
            # 결과 집계 및 인벤토리 추가
            res_counts = {}
            for lvl in results:
                res_counts[lvl] = res_counts.get(lvl, 0) + 1
                update_inventory(lvl, 1)
            
            # 결과 메시지 표시
            msg = ""
            for lvl, cnt in res_counts.items():
                icon, name = CRIMINALS.get(lvl, ("❓", "Unknown"))
                msg += f"[{icon} Lv.{lvl} {name}] x {cnt}\n"
            st.toast(f"체포 성공!\n{msg}", icon="🚨")
            st.balloons()
            time.sleep(1)
            st.rerun()
        else:
            st.error("잔액 부족!")

    with c1:
        st.markdown("""
        <div class='card-box'>
            <h3>1회 잡기</h3>
            <p class='neon-text'>Cost: 0.01 SOL</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚨 1회 체포 시도", key="pull_1", type="primary"):
            pull_action(0.01, 1)
            
    with c2:
        st.markdown("""
        <div class='card-box'>
            <h3>5회 잡기 (연속)</h3>
            <p class='neon-text'>Cost: 0.05 SOL</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚨 5회 체포 시도", key="pull_5", type="primary"):
            pull_action(0.05, 5)

    with c3:
        st.markdown("""
        <div class='card-box'>
            <h3>10회 잡기 (대규모)</h3>
            <p class='neon-text'>Cost: 0.10 SOL</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚨 10회 체포 시도", key="pull_10", type="primary"):
            pull_action(0.10, 10)

# === TAB 3: 보관소 (관리/합성) ===
with tabs[2]:
    st.subheader("📦 Inventory & Management")
    st.write("보유한 범죄자를 관리합니다. <span class='neon-text'>[합성]</span>하거나 <span class='gold-text'>[감옥 이송(판매)]</span>하세요.", unsafe_allow_html=True)
    inv = get_inventory()
    
    if not inv:
        st.info("보관소가 비어있습니다. '범인 잡기' 탭에서 체포해오세요.")
    else:
        for lvl, count in sorted(inv.items()):
            if count > 0:
                icon, name = CRIMINALS.get(lvl, ("❓", "Unknown"))
                with st.container():
                    st.markdown(f"<div class='card-box'>", unsafe_allow_html=True)
                    c_info, c_act1, c_act2 = st.columns([2, 1, 1])
                    
                    with c_info:
                        st.markdown(f"### {icon} Lv.{lvl} {name}")
                        st.write(f"보유 수량: <span class='neon-text'>{count}</span> 명", unsafe_allow_html=True)
                    
                    with c_act1:
                        # [합성] 2 -> 1
                        if count >= 2 and lvl < 20:
                            if st.button(f"🧬 합성 (2명 -> Lv.{lvl+1})", key=f"fuse_{lvl}"):
                                update_inventory(lvl, -2)
                                update_inventory(lvl+1, 1)
                                st.toast(f"합성 성공! Lv.{lvl+1} 획득", icon="✨")
                                st.rerun()
                        else:
                            st.button("합성 불가 (부족/최대)", disabled=True, key=f"dis_fuse_{lvl}")

                    with c_act2:
                        # [감옥 이송 (판매)]
                        # 판매 가격: 뽑기 비용(0.01)보다 낮게 설정하여 운영자 수익 보장
                        # 예: Lv.1 = 0.005, 레벨 오를수록 조금씩 증가
                        reward = 0.005 * (1.2**(lvl-1)) 
                        if st.button(f"💰 감옥 이송 (+{reward:.4f})", key=f"sell_{lvl}"):
                            update_inventory(lvl, -1)
                            update_balance(reward)
                            st.toast(f"이송 완료. {reward:.4f} SOL 획득", icon="💰")
                            st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)

# === TAB 4: 명예의 전당 (유지) ===
with tabs[3]:
    st.subheader("🏆 Hall of Fame")
    with get_db() as conn:
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0) FROM users ORDER BY balance DESC LIMIT 10").fetchall()
    for i, (w, b) in enumerate(ranks):
        st.write(f"**{i+1}위** 🕵️ {w} : <span class='gold-text'>{b:.4f} SOL</span>", unsafe_allow_html=True)
