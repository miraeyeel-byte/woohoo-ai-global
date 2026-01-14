import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import os
import time
from datetime import datetime, timedelta

# [1. 기본 설정]
st.set_page_config(page_title="WOOHOO SECURITY V18.6", layout="wide")
DB_PATH = "woohoo_v18_6_lvl100.db"

# [2. DB 초기화 (최고 레벨 컬럼 추가)]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        # users: 지갑, 잔액, 최고레벨(max_lvl)
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, max_lvl INTEGER DEFAULT 0)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS prison_log (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, lvl INTEGER, reward REAL, time_str TEXT)")
        # 운영자 계정
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, max_lvl) VALUES ('Operator_Admin', 10.0, 100)")
        conn.commit()
init_db()

# [3. 운영자님이 주신 보안 코드 (MOCK SCAN & SECURITY LAYER)]
def scan_token(token_address):
    """0.01초 정적 분석 예시"""
    risk_score = random.randint(0, 100)
    issues = []
    if risk_score > 70:
        issues.append("Honeypot detected")
        issues.append("Dev wallet holds >20%")
    return risk_score, issues

def process_security_action(token_address, user_tier):
    """BASIC -> 경고, PRO -> 차단"""
    risk_score, issues = scan_token(token_address)

    if user_tier.startswith("BASIC"):
        if risk_score >= 70:
            st.warning(f"🚨 [경고] 위험 점수 {risk_score}! 매수 시 자산 손실 위험이 큽니다.")
            for issue in issues: st.write(f"- {issue}")
            return "WARNING_DISPLAYED"
    elif user_tier.startswith("PRO"):
        if risk_score >= 70:
            st.error(f"🚫 원천 차단됨! 위험 점수: {risk_score}")
            for issue in issues: st.write(f"- {issue}")
            st.info("허니팟(Honeypot) 또는 위험 토큰. 지갑 호출이 차단되었습니다.")
            return "TRANSACTION_KILLED"
    
    # 안전할 경우
    st.success(f"✅ 안전 (Risk: {risk_score}). 지갑 호출 가능.")
    return "SAFE_PROCEED"

# [4. 스타일링 (다크 테마 + 가독성)]
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3, h4, p, div { color: #e0e0e0; text-shadow: 1px 1px 2px #000; }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border: 1px solid #333; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; font-weight: bold; border: none; }

    /* 카드 스타일 */
    .card-box {
        border: 2px solid #FFD700; background: linear-gradient(145deg, #111, #1a1a1a);
        padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.6); transition: 0.3s;
    }
    .card-box:hover { border-color: #66fcf1; transform: translateY(-3px); }
    
    .neon { color: #66fcf1; font-weight: bold; }
    .gold { color: #FFD700; font-weight: bold; }
    .red { color: #ff4b4b; font-weight: bold; }
    
    /* 티어 라디오 버튼 스타일 */
    div[role="radiogroup"] { color: white; }
</style>
""", unsafe_allow_html=True)

# [5. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'user_tier' not in st.session_state: st.session_state.user_tier = "BASIC (0.01 SOL)"
if 'confirm_fuse_all' not in st.session_state: st.session_state.confirm_fuse_all = False
if 'confirm_jail_all' not in st.session_state: st.session_state.confirm_jail_all = False

# [6. 기능 로직]
def get_user():
    if not st.session_state.wallet: return None, 0.0, 0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance, max_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0, 0)

def update_balance(delta):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (delta, st.session_state.wallet))
        conn.commit()

def update_max_lvl(lvl):
    """최고 레벨 갱신 로직"""
    with get_db() as conn:
        curr = conn.execute("SELECT max_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()[0]
        if lvl > curr:
            conn.execute("UPDATE users SET max_lvl = ? WHERE wallet=?", (lvl, st.session_state.wallet))
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
    # 인벤토리 추가 시 최고레벨 체크
    if delta > 0:
        update_max_lvl(lvl)

# [레벨 100까지 이름 생성]
def get_criminal_name(lvl):
    if lvl == 1: return "소매치기"
    if lvl <= 10: return f"동네 양아치 Lv.{lvl}"
    if lvl <= 30: return f"전문 사기꾼 Lv.{lvl}"
    if lvl <= 50: return f"조직 간부 Lv.{lvl}"
    if lvl <= 70: return f"국제 범죄자 Lv.{lvl}"
    if lvl <= 90: return f"블록체인 테러리스트 Lv.{lvl}"
    if lvl < 100: return f"세계관 최강자 Lv.{lvl}"
    return "👿 절대악 (THE END) 👿"

def get_img_url(lvl):
    # 레벨별로 다른 시드 생성 (DiceBear)
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=Level{lvl}Criminal&backgroundColor=1a1a1a"

def gacha_pull(n):
    # 레벨 100까지 확장된 확률 (저레벨 위주)
    levels = list(range(1, 101))
    weights = []
    for i in range(1, 101):
        # 레벨이 높을수록 확률이 지수적으로 감소
        weights.append(1000 / (i * i)) 
    return random.choices(levels, weights=weights, k=n)

# [7. 메인 화면]
st.title("🛡️ WOOHOO INFINITE JUSTICE (Lv.100)")

# 사이드바
with st.sidebar:
    st.header("🔐 Wallet Access")
    if not st.session_state.wallet:
        if st.button("Connect Wallet"):
            st.session_state.wallet = "Operator_Admin"
            st.rerun()
    else:
        u_wallet, u_bal, u_max = get_user()
        st.success(f"User: {u_wallet}")
        st.metric("Balance", f"{u_bal:.4f} SOL")
        st.metric("Max Level", f"Lv.{u_max}")
        if st.button("Disconnect"):
            st.session_state.wallet = None; st.rerun()

if not st.session_state.wallet:
    st.info("지갑을 연결해주세요.")
    st.stop()

# 탭 구성 (보안 센터 + 게임 기능)
tabs = st.tabs(["🛡️ 보안 센터 (Scanner)", "🚨 범인 체포 (Game)", "📦 보관함 (Inventory)", "🏆 명예의 전당 (Ranking)"])

# === TAB 1: 보안 센터 (운영자님 요청 코드 복구) ===
with tabs[0]:
    st.subheader("💎 WOOHOO Security Dashboard")
    
    # 티어 선택 (운영자님 코드)
    st.markdown("**구독 티어 선택:**")
    tier = st.radio("Security Level", ["BASIC (0.01 SOL)", "PRO (0.1 SOL)"])
    st.session_state.user_tier = tier
    
    st.divider()
    
    # 토큰 스캔 UI
    token_address = st.text_input("분석할 토큰 주소 입력", "")
    buy_button = st.button("💰 BUY TOKEN (Simulation)")

    if buy_button:
        if not token_address:
            st.warning("토큰 주소를 입력해주세요.")
        else:
            # 운영자님이 주신 보안 함수 호출
            status = process_security_action(token_address, st.session_state.user_tier)
            
            if status == "SAFE_PROCEED":
                st.balloons() # 안전하면 축하
            elif status == "WARNING_DISPLAYED":
                # 경고는 함수 내에서 이미 출력됨
                pass
            elif status == "TRANSACTION_KILLED":
                # 차단 메시지도 함수 내에서 출력됨
                pass

# === TAB 2: 범인 체포 (미니게임 유지) ===
with tabs[1]:
    st.subheader("🚓 범죄자 체포 (Lv.1 ~ Lv.100)")
    st.caption("비용을 지불하고 범죄자를 체포합니다. 운이 좋으면 고레벨 범죄자가 바로 나옵니다.")
    
    def run_gacha(cost, n):
        _, bal, _ = get_user()
        if bal < cost: st.error("잔액 부족!"); return
        
        update_balance(-cost)
        res = gacha_pull(n)
        for r in res: update_inventory(r, 1) # 인벤토리 추가 및 최고레벨 갱신
        
        st.toast(f"{n}명 체포 완료!", icon="🚨")
        
        # 결과 표시 (상위 5개)
        cols = st.columns(min(n, 5))
        for i, lvl in enumerate(res[:5]):
            with cols[i]:
                st.markdown(f"""
                <div class='card-box'>
                    <img src='{get_img_url(lvl)}' width='50'>
                    <div class='neon'>Lv.{lvl}</div>
                </div>
                """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("1회 체포 (0.01 SOL)"): run_gacha(0.01, 1)
    with c2:
        if st.button("5회 체포 (0.05 SOL)"): run_gacha(0.05, 5)
    with c3:
        if st.button("10회 체포 (0.10 SOL)"): run_gacha(0.10, 10)

# === TAB 3: 보관함 (Lv 100 대응) ===
with tabs[2]:
    st.subheader("📦 Inventory Management")
    inv = get_inventory()
    
    # [일괄 처리 버튼]
    if inv:
        bc1, bc2 = st.columns(2)
        total_fusions = sum([cnt // 2 for lvl, cnt in inv.items() if lvl < 100])
        
        with bc1:
            if not st.session_state.confirm_fuse_all:
                if st.button(f"🧬 일괄 합성 (가능: {total_fusions}회)", type="primary", disabled=total_fusions==0):
                    st.session_state.confirm_fuse_all = True
                    st.rerun()
            else:
                st.warning(f"총 {total_fusions}회 합성을 진행하시겠습니까?")
                if st.button("✅ 합성 승인"):
                    for lvl in sorted(inv.keys()):
                        f_cnt = inv[lvl] // 2
                        if f_cnt > 0 and lvl < 100:
                            update_inventory(lvl, -(f_cnt*2))
                            update_inventory(lvl+1, f_cnt) # 레벨업 시 최고레벨 자동 갱신
                    st.toast("일괄 합성 완료!", icon="🧬")
                    st.session_state.confirm_fuse_all = False
                    st.rerun()

        with bc2:
            if not st.session_state.confirm_jail_all:
                if st.button("🔒 일괄 감옥 (모두 판매)"):
                    st.session_state.confirm_jail_all = True
                    st.rerun()
            else:
                st.warning("정말 모든 범죄자를 감옥으로 보내고 보상을 받겠습니까?")
                if st.button("✅ 감옥 승인"):
                    total_r = 0
                    for lvl, cnt in inv.items():
                        if cnt > 0:
                            r = cnt * (0.005 * (1.1**(lvl-1))) # 보상 공식
                            update_inventory(lvl, -cnt)
                            total_r += r
                    update_balance(total_r)
                    st.toast(f"일괄 이송 완료! +{total_r:.4f} SOL", icon="💰")
                    st.session_state.confirm_jail_all = False
                    st.rerun()
    
    st.divider()

    # 개별 목록 (Lv 100까지 대응)
    if not inv:
        st.info("보관함이 비어있습니다.")
    else:
        for lvl, count in sorted(inv.items(), reverse=True): # 높은 레벨부터 표시
            if count > 0:
                with st.container():
                    c1, c2, c3 = st.columns([1, 2, 2])
                    with c1:
                        st.image(get_img_url(lvl), width=60)
                    with c2:
                        st.markdown(f"#### {get_criminal_name(lvl)}")
                        st.markdown(f"수량: <span class='neon'>{count}</span>", unsafe_allow_html=True)
                    with c3:
                        # 합성
                        if count >= 2 and lvl < 100:
                            if st.button(f"🧬 합성 (2->1)", key=f"f_{lvl}"):
                                update_inventory(lvl, -2)
                                update_inventory(lvl+1, 1)
                                st.toast("합성 성공!", icon="✨")
                                st.rerun()
                        
                        # 감옥
                        r = 0.005 * (1.1**(lvl-1))
                        if st.button(f"🔒 감옥 (+{r:.4f})", key=f"j_{lvl}"):
                            update_inventory(lvl, -1)
                            update_balance(r)
                            st.rerun()
                st.markdown("---")

# === TAB 4: 명예의 전당 (최고 레벨 추가) ===
with tabs[3]:
    st.subheader("🏆 Hall of Fame")
    st.caption("가장 강력한 범죄자(최고 레벨)를 잡은 헌터 순위")
    
    with get_db() as conn:
        # 최고 레벨(max_lvl) 우선, 그 다음 잔액(balance) 순으로 정렬
        ranks = conn.execute("SELECT wallet, balance, max_lvl FROM users ORDER BY max_lvl DESC, balance DESC LIMIT 10").fetchall()
    
    for i, (w, b, m) in enumerate(ranks):
        medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        st.markdown(f"""
        <div class='card-box' style='padding:15px; text-align:left; display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <span style='font-size:1.5em; margin-right:10px;'>{medal}</span>
                <span class='neon' style='font-size:1.1em;'>{w}</span>
            </div>
            <div style='text-align:right;'>
                <div class='red' style='font-size:1.2em;'>MAX: Lv.{m}</div>
                <div class='gold'>{b:.4f} SOL</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
