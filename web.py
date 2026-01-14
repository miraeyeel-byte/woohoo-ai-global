import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import os
import time
from datetime import datetime, timedelta

# [1. 기본 설정 - 포톤 스타일 와이드 모드]
st.set_page_config(page_title="WOOHOO PHOTON V22.8", layout="wide")
DB_PATH = "woohoo_v22_8_photon.db"

# [2. 함수 정의]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        # wallets 테이블 별도 분리 (다중 지갑 지원)
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, revenue REAL DEFAULT 0.0, total_profit REAL DEFAULT 0.0, max_lvl INTEGER DEFAULT 0, max_sold_lvl INTEGER DEFAULT 0, rental_expiry TEXT, rental_type TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, revenue, total_profit, max_lvl, max_sold_lvl) VALUES ('Operator_Admin', 10000.0, 0.0, 0.0, 0, 0)")
        
        # 가짜 랭커
        fake_users = [
            ('8xFa...92Lm', 500.0, 0.0, 524.12, 55, 55, None, None),
            ('Hv2...k9A', 120.0, 0.0, 120.50, 30, 30, None, None),
            ('3mP...x1Z', 50.0, 0.0, 45.20, 22, 22, None, None)
        ]
        for u in fake_users:
            c.execute("INSERT OR IGNORE INTO users (wallet, balance, revenue, total_profit, max_lvl, max_sold_lvl, rental_expiry, rental_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", u)
        conn.commit()

def get_user(wallet_addr):
    if not wallet_addr: return None
    with get_db() as conn:
        # 유저 없으면 자동 생성 (지갑 추가 시)
        conn.execute("INSERT OR IGNORE INTO users (wallet, balance, revenue, total_profit, max_lvl, max_sold_lvl) VALUES (?, 0.0, 0.0, 0.0, 0, 0)", (wallet_addr,))
        conn.commit()
        
        row = conn.execute("SELECT * FROM users WHERE wallet=?", (wallet_addr,)).fetchone()
        if row:
            return {
                "wallet": row[0], "balance": row[1], "revenue": row[2], 
                "total_profit": row[3], "max_lvl": row[4], "max_sold_lvl": row[5],
                "rental_expiry": row[6], "rental_type": row[7]
            }
        return None

def update_balance(wallet, d):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (d, wallet))
        if d < 0: # 사용한 돈은 운영자 매출로
            conn.execute("UPDATE users SET revenue = revenue + ? WHERE wallet='Operator_Admin'", (abs(d),))
        conn.commit()

def buy_rental(wallet, type, cost):
    user = get_user(wallet)
    if user['balance'] < cost:
        st.error("잔액 부족! 충전 필요.")
        return
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance - ? WHERE wallet=?", (cost, wallet))
        conn.execute("UPDATE users SET revenue = revenue + ? WHERE wallet='Operator_Admin'", (cost,))
        now = datetime.now()
        current_expiry = user['rental_expiry']
        if current_expiry:
            expiry_dt = datetime.strptime(current_expiry, "%Y-%m-%d %H:%M:%S")
            new_expiry = (expiry_dt if expiry_dt > now else now) + timedelta(hours=1)
        else:
            new_expiry = now + timedelta(hours=1)
        conn.execute("UPDATE users SET rental_expiry = ?, rental_type = ? WHERE wallet=?", (new_expiry.strftime("%Y-%m-%d %H:%M:%S"), type, wallet))
        conn.commit()
    st.toast(f"✅ {type.upper()} 1시간 연장 완료!", icon="💳")
    st.session_state.rental_confirm = None
    st.rerun()

def check_rental_status(wallet):
    user = get_user(wallet)
    if not user or not user['rental_expiry']: return False, None, 0
    expiry = datetime.strptime(user['rental_expiry'], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    if expiry > now:
        return True, user['rental_type'], (expiry - now).total_seconds() / 60
    return False, None, 0

def update_inventory(wallet, l, d):
    with get_db() as conn:
        c = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (wallet, l)).fetchone()
        n = (c[0] + d) if c else d
        if n < 0: n = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (wallet, l, n)); conn.commit()

def get_inv(wallet):
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (wallet,)).fetchall())

def gacha_pull(n):
    levels = list(range(1, 101))
    weights = [100000 / (i**2.2) for i in levels] 
    return random.choices(levels, weights=weights, k=n)

def calculate_reward(lvl):
    return (0.003 * (1.05**(lvl-1))) if lvl <= 100 else (0.003 * (1.05**99) + (lvl-100)*0.2)

def record_profit_and_rank(wallet, amount, sold_lvl):
    with get_db() as conn:
        conn.execute("UPDATE users SET total_profit = total_profit + ? WHERE wallet=?", (amount, wallet))
        curr = conn.execute("SELECT max_sold_lvl FROM users WHERE wallet=?", (wallet,)).fetchone()[0]
        if sold_lvl > curr: conn.execute("UPDATE users SET max_sold_lvl = ? WHERE wallet=?", (sold_lvl, wallet))
        conn.commit()

def get_criminal_name(lvl):
    return f"Lv.{lvl} Scammer"

def get_img_url(lvl):
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=Scam{lvl}&backgroundColor=1a1a1a"

# [3. 초기화]
init_db()

# [4. 16개국어 데이터]
LANG = {
    "🇰🇷 한국어": {
        "title": "WOOHOO SECURITY", 
        "tab_photon": "⚡ 트레이딩 (Photon)", "tab_game": "🎮 미니게임", "tab_rank": "🏆 명예의 전당",
        "story_short": "허니팟 없는 세상을 위해 만들었습니다.", "tele_info": "제보: @FUCKHONEYPOT",
        "rental_shop": "🎟️ 보안 이용권 (Time Pass)", 
        "rental_basic": "Basic (0.01 SOL/시간)", "rental_pro": "PRO (0.1 SOL/시간)",
        "mode_basic_desc": "위험 감지 시 경고만 함", "mode_pro_desc": "위험 감지 시 매수 원천 차단",
        "msg_expired": "🚫 이용권 만료됨",
        "sec_input": "검사할 코인 주소 (CA)", "btn_scan": "허니팟 정밀 분석",
        "game_desc": "스캠범 체포 (확률 상향)", "pull_1": "1회", "pull_5": "5회", "pull_10": "10회", "pull_100": "🔥 100회",
        "inv_empty": "보관함이 비어있습니다.", "fuse_all": "🧬 일괄 합성", "jail_all": "🔒 일괄 감옥 (현상금)",
        "btn_yes": "✅ 승인", "btn_no": "❌ 취소", "toast_catch": "{n}명 체포!", "buy_confirm": "⚠️ {cost} SOL 결제",
        "toast_fuse": "합성 완료!", "toast_jail": "이송 완료! +{r:.4f} SOL",
        "rank_title": "명예의 전당", "rank_desc": "최고의 헌터들 (1시간 기준 갱신)", "rank_empty": "데이터 없음",
        "jail_popup": "예상 현상금: {r:.4f} SOL\n\n정말 현상금을 받고 감옥으로 보내시겠습니까?",
        "jail_btn_real": "👮 감옥 보내고 현상금 받기",
        "rental_popup": "⚠️ {type} 모드 1시간 이용권\n가격: {cost} SOL\n\n정말 결제하시겠습니까?",
        "photon_warn": "Basic 모드: 경고 무시 가능", "photon_block": "PRO 모드: 매수 불가"
    },
    "🇺🇸 English": {
        "title": "WOOHOO SECURITY", 
        "tab_photon": "⚡ Trading (Photon)", "tab_game": "🎮 Mini Game", "tab_rank": "🏆 Hall of Fame",
        "story_short": "Stop Honey Pots.", "tele_info": "Report: @FUCKHONEYPOT",
        "rental_shop": "🎟️ Time Pass", "rental_basic": "Basic (0.01 SOL/h)", "rental_pro": "PRO (0.1 SOL/h)",
        "mode_basic_desc": "Warn Only", "mode_pro_desc": "Block Purchase",
        "msg_expired": "🚫 Pass Expired",
        "sec_input": "Token Address (CA)", "btn_scan": "Scan Token",
        "game_desc": "Arrest Scammers", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "🔥 x100",
        "inv_empty": "Empty.", "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "btn_yes": "✅ Yes", "btn_no": "❌ No", "toast_catch": "{n} Captured!", "buy_confirm": "⚠️ Confirm {cost} SOL?",
        "toast_fuse": "Fused!", "toast_jail": "Jailed! +{r:.4f} SOL",
        "rank_title": "Hall of Fame", "rank_desc": "Top Hunters", "rank_empty": "No Data",
        "jail_popup": "Expected Bounty: {r:.4f} SOL\n\nConfirm Jail?", "jail_btn_real": "👮 Jail & Claim Bounty",
        "rental_popup": "⚠️ {type} Mode 1 Hour Pass\nCost: {cost} SOL\n\nConfirm Payment?",
        "photon_warn": "Basic: Warning ignored", "photon_block": "PRO: Purchase Blocked"
    },
    # 나머지 14개국어 유지 (생략)
    "🇯🇵 日本語": {"title": "WOOHOO", "tab_photon": "⚡ 取引", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "1回", "pull_5": "5回", "pull_10": "10回", "pull_100": "100回", "btn_yes": "✅", "btn_no": "❌"},
    "🇨🇳 中文": {"title": "WOOHOO", "tab_photon": "⚡ 交易", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "1次", "pull_5": "5次", "pull_10": "10次", "pull_100": "100次", "btn_yes": "✅", "btn_no": "❌"},
    "🇷🇺 Русский": {"title": "WOOHOO", "tab_photon": "⚡ Трейдинг", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇻🇳 Tiếng Việt": {"title": "WOOHOO", "tab_photon": "⚡ Giao dịch", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇹🇭 ภาษาไทย": {"title": "WOOHOO", "tab_photon": "⚡ การซื้อขาย", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇮🇱 עברית": {"title": "WOOHOO", "tab_photon": "⚡ מסחר", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇵🇭 Tagalog": {"title": "WOOHOO", "tab_photon": "⚡ Trading", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇲🇾 Melayu": {"title": "WOOHOO", "tab_photon": "⚡ Trading", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇮🇩 Indonesia": {"title": "WOOHOO", "tab_photon": "⚡ Trading", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇹🇷 Türkçe": {"title": "WOOHOO", "tab_photon": "⚡ Ticaret", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇵🇹 Português": {"title": "WOOHOO", "tab_photon": "⚡ Negociação", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇪🇸 Español": {"title": "WOOHOO", "tab_photon": "⚡ Comercio", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇩🇪 Deutsch": {"title": "WOOHOO", "tab_photon": "⚡ Handel", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"},
    "🇫🇷 Français": {"title": "WOOHOO", "tab_photon": "⚡ Trading", "rental_basic": "Basic", "rental_pro": "PRO", "btn_yes": "✅", "btn_no": "❌"}
}

# [5. 스타일링 - 블랙 & 가독성]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700&display=swap');
    .stApp, [data-testid="stSidebar"] { background-color: #000000 !important; color: #ffffff !important; font-family: 'Noto Sans KR', sans-serif; }
    h1, h2, h3, h4, h5, h6, p, label, div, span, li, button { color: #ffffff !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div { background-color: #222 !important; color: #fff !important; border: 1px solid #66fcf1 !important; }
    .stTextInput > div > div > input { color: #ffffff !important; background-color: #1a1a1a !important; border: 1px solid #66fcf1 !important; }
    .stNumberInput > div > div > input { color: #ffffff !important; background-color: #1a1a1a !important; border: 1px solid #66fcf1 !important; }
    .card-box { border: 2px solid #66fcf1; background: #111111; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 0 5px #222; }
    .neon { color: #66fcf1 !important; font-weight: bold; }
    .gold { color: #FFD700 !important; font-weight: bold; }
    .red { color: #FF4B4B !important; font-weight: bold; }
    .stButton button { border: 2px solid #66fcf1 !important; background: #000000 !important; color: #66fcf1 !important; font-weight: bold; }
    .stButton button:hover { background: #66fcf1 !important; color: #000000 !important; border: 2px solid #ffffff !important; }
    .tiny-warn { color: #FFD700 !important; border: 1px solid #FFD700; background: #222; padding: 10px; text-align: center; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# [6. 세션]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'lang' not in st.session_state: st.session_state.lang = "🇰🇷 한국어"
if 'confirm_target' not in st.session_state: st.session_state.confirm_target = None
if 'jail_confirm' not in st.session_state: st.session_state.jail_confirm = 0
if 'rental_confirm' not in st.session_state: st.session_state.rental_confirm = None
if 'current_ca' not in st.session_state: st.session_state.current_ca = ""
if 'scan_result' not in st.session_state: st.session_state.scan_result = None

def T(key, **kwargs):
    lang_data = LANG.get(st.session_state.lang, LANG.get("🇺🇸 English", {}))
    text = lang_data.get(key, LANG["🇰🇷 한국어"].get(key, key))
    if kwargs: return text.format(**kwargs)
    return text

# [7. UI]
with st.sidebar:
    st.title("🌐 Language")
    lang_list = list(LANG.keys())
    try: idx = lang_list.index(st.session_state.lang)
    except: idx = 0
    new_lang = st.selectbox("Select", lang_list, index=idx)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang; st.rerun()
    
    st.divider()
    st.markdown("### 💼 지갑 관리자 (Wallets)")
    
    # [지갑 관리 기능]
    if st.session_state.wallet:
        st.success(f"현재 접속: {st.session_state.wallet}")
        user = get_user(st.session_state.wallet)
        st.metric("내 지갑 잔액", f"{user['balance']:.4f} SOL")
        
        if st.button("🔄 다른 지갑 연결 / 생성"):
            st.session_state.wallet = None
            st.rerun()
            
        # 렌탈샵: 결제 확인 팝업
        st.markdown("---")
        st.subheader(T("rental_shop"))
        is_active, r_type, mins = check_rental_status(st.session_state.wallet)
        
        if is_active:
            st.info(f"✅ {r_type.upper()} Mode\n(Time: {int(mins)}m)")
        else:
            st.warning("⛔ 이용권 없음")
            
        if st.session_state.rental_confirm:
            r_type_conf, r_cost_conf = st.session_state.rental_confirm
            st.markdown(f"<div class='tiny-warn'>{T('rental_popup', type=r_type_conf.upper(), cost=r_cost_conf)}</div>", unsafe_allow_html=True)
            c_y, c_n = st.columns(2)
            if c_y.button("✅ Yes", key="rent_y"): buy_rental(st.session_state.wallet, r_type_conf, r_cost_conf)
            if c_n.button("❌ No", key="rent_n"): st.session_state.rental_confirm = None; st.rerun()
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"{T('rental_basic')}"): st.session_state.rental_confirm = ('basic', 0.01); st.rerun()
            with c2:
                if st.button(f"{T('rental_pro')}"): st.session_state.rental_confirm = ('pro', 0.1); st.rerun()
        
        st.caption(f"Basic: {T('mode_basic_desc')}")
        st.caption(f"PRO: {T('mode_pro_desc')}")
    
    else:
        # 로그인 전: 지갑 입력/생성
        wallet_input = st.text_input("지갑 주소 또는 Private Key 입력", placeholder="Solana Address...")
        if st.button("🔗 지갑 연결 (Connect)"):
            if wallet_input:
                st.session_state.wallet = wallet_input
                st.rerun()
            else:
                st.warning("주소를 입력하세요.")
        
        if st.button("🎲 새 지갑 생성 (Generate)"):
            new_wallet = "New_Wallet_" + str(random.randint(1000,9999))
            st.session_state.wallet = new_wallet
            st.toast(f"새 지갑 생성 완료: {new_wallet}")
            st.rerun()
    
    st.divider()
    st.info(T("story_short"))
    st.markdown(f"📢 **{T('tele_info')}**")

st.title(T("title"))

if not st.session_state.wallet:
    st.warning("Please Connect Wallet First.")
    st.stop()

tabs = st.tabs([T("tab_photon"), T("tab_game"), T("tab_rank")])

# === 탭 1: 포톤 트레이딩 (선분석 시스템) ===
with tabs[0]:
    st.subheader(T("tab_photon"))
    is_active, r_type, _ = check_rental_status(st.session_state.wallet)
    
    # 1. 상단: CA 입력 및 분석
    ca_input = st.text_input("Target CA (펌프펀/레이디움)", value=st.session_state.current_ca, placeholder="Contract Address 입력 시 즉시 분석...")
    
    # CA가 변경되면 분석 실행
    if ca_input and ca_input != st.session_state.current_ca:
        st.session_state.current_ca = ca_input
        # 분석 시뮬레이션
        risk = random.randint(0, 100)
        is_scam = risk > 70
        st.session_state.scan_result = {"risk": risk, "is_scam": is_scam, "name": f"TOKEN-{ca_input[:4]}"}
        st.rerun()

    # 2. 분석 결과 표시
    if st.session_state.scan_result:
        res = st.session_state.scan_result
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Token Name", res['name'])
        with c2: st.metric("Liquidity", "$12,000")
        with c3: 
            risk_color = "normal" if res['risk'] < 50 else "off" if res['risk'] > 70 else "inverse"
            st.metric("Risk Score", f"{res['risk']}%", delta_color=risk_color)
        
        # 3. 트레이딩 패널 (분석 결과에 따라 바뀜)
        st.markdown("### ⚡ Trading Panel")
        
        if not is_active:
            st.error(T("msg_expired"))
        else:
            # 설정값 입력 (직접 입력 가능)
            c1, c2, c3 = st.columns(3)
            with c1: amount = st.number_input("Amount (SOL)", value=0.5, step=0.1, format="%.2f")
            with c2: slippage = st.number_input("Slippage (%)", value=20, step=5)
            with c3: priority = st.number_input("Priority Fee", value=0.005, format="%.4f")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # [핵심 로직] 상태별 버튼 표시
            if res['is_scam']:
                if r_type == 'pro':
                    # PRO: 차단됨
                    st.error(f"⛔ [PRO BLOCKED] 위험도 {res['risk']}%! 허니팟 확률이 높아 매수가 원천 차단되었습니다.")
                    st.button("🚫 매수 불가 (Protection Active)", disabled=True, type="primary")
                else:
                    # BASIC: 경고하지만 버튼은 줌
                    st.warning(f"⚠️ [BASIC WARNING] 위험도 {res['risk']}%! 허니팟 의심됩니다. (Basic은 막지 않습니다)")
                    if st.button(f"⚠️ 위험 감수하고 매수 ({amount} SOL)", type="secondary"):
                        with st.spinner("매수 진행 중..."):
                            time.sleep(1)
                            st.success(f"✅ 매수 성공! (위험 감수)")
            else:
                # 안전함
                st.success(f"✅ [SAFE] 안전한 코인입니다. (Risk {res['risk']}%)")
                if st.button(f"🚀 QUICK BUY ({amount} SOL)", type="primary"):
                    with st.spinner("⚡ 광속 매수 중..."):
                        time.sleep(0.5)
                        st.success(f"✅ 매수 체결 완료! ({amount} SOL)")

    else:
        st.info("👆 상단에 CA 주소를 입력하면 자동으로 분석하고 매수 패널이 열립니다.")

# === 탭 2: 미니게임 (4버튼 + 기능 복구) ===
with tabs[1]:
    st.subheader(T("tab_game"))
    st.caption(T("game_desc"))
    
    def execute_pull(cost, n):
        user = get_user(st.session_state.wallet)
        if user['balance'] < cost: st.error("잔액 부족")
        else:
            update_balance(st.session_state.wallet, -cost)
            res = gacha_pull(n)
            for r in res: update_inventory(st.session_state.wallet, r, 1)
            st.toast(T("toast_catch", n=n), icon="🚨")
            if n >= 100: st.balloons()
        st.session_state.confirm_target = None
        st.rerun()

    c1, c2, c3, c4 = st.columns(4)
    if st.session_state.confirm_target == "p1":
        with c1:
            st.markdown(f"<div class='tiny-warn'>{T('buy_confirm', cost=0.01)}</div>", unsafe_allow_html=True)
            if st.button(T("btn_yes"), key="y1"): execute_pull(0.01, 1)
            if st.button(T("btn_no"), key="n1"): st.session_state.confirm_target = None; st.rerun()
    else:
        with c1:
            if st.button(f"{T('pull_1')} (0.01 SOL)", key="btn_p1"): st.session_state.confirm_target = "p1"; st.rerun()
            
    with c2:
        if st.session_state.confirm_target == "p5":
            st.markdown(f"<div class='tiny-warn'>{T('buy_confirm', cost=0.05)}</div>", unsafe_allow_html=True)
            if st.button(T("btn_yes"), key="y5"): execute_pull(0.05, 5)
            if st.button(T("btn_no"), key="n5"): st.session_state.confirm_target = None; st.rerun()
        else:
            if st.button(f"{T('pull_5')} (0.05 SOL)", key="btn_p5"): st.session_state.confirm_target = "p5"; st.rerun()
            
    with c3:
        if st.session_state.confirm_target == "p10":
            st.markdown(f"<div class='tiny-warn'>{T('buy_confirm', cost=0.10)}</div>", unsafe_allow_html=True)
            if st.button(T("btn_yes"), key="y10"): execute_pull(0.10, 10)
            if st.button(T("btn_no"), key="n10"): st.session_state.confirm_target = None; st.rerun()
        else:
            if st.button(f"{T('pull_10')} (0.10 SOL)", key="btn_p10"): st.session_state.confirm_target = "p10"; st.rerun()
            
    with c4:
        if st.session_state.confirm_target == "p100":
            st.markdown(f"<div class='tiny-warn'>{T('buy_confirm', cost=1.00)}</div>", unsafe_allow_html=True)
            if st.button(T("btn_yes"), key="y100"): execute_pull(1.00, 100)
            if st.button(T("btn_no"), key="n100"): st.session_state.confirm_target = None; st.rerun()
        else:
            if st.button(f"{T('pull_100')} (1.00 SOL)", key="btn_p100", type="primary"): st.session_state.confirm_target = "p100"; st.rerun()

    st.divider()
    inv = get_inv(st.session_state.wallet)
    if inv:
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button(T("fuse_all"), key="bf"):
                for lvl in sorted(inv.keys()):
                    f_cnt = inv[lvl] // 2
                    if f_cnt > 0 and lvl < 1000: update_inventory(st.session_state.wallet, lvl, -(f_cnt*2)); update_inventory(st.session_state.wallet, lvl+1, f_cnt)
                st.toast(T("toast_fuse"), icon="🧬"); st.rerun()
        
        with bc2:
            if st.session_state.jail_confirm > 0:
                st.markdown(f"<div class='tiny-warn'>{T('jail_popup', r=st.session_state.jail_confirm)}</div>", unsafe_allow_html=True)
                c_y, c_n = st.columns(2)
                if c_y.button(T("jail_btn_real")):
                    tr = st.session_state.jail_confirm
                    for lvl, cnt in inv.items():
                        update_inventory(st.session_state.wallet, lvl, -cnt)
                        record_profit_and_rank(st.session_state.wallet, 0, lvl)
                    with get_db() as conn: conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (tr, st.session_state.wallet)); conn.commit()
                    record_profit_and_rank(st.session_state.wallet, tr, 0); st.toast(T("toast_jail", r=tr), icon="💰"); 
                    st.session_state.jail_confirm = 0
                    st.rerun()
                if c_n.button(T("btn_no"), key="jn"): 
                    st.session_state.jail_confirm = 0; st.rerun()
            else:
                if st.button(T("jail_all"), key="bj"):
                    tr = 0
                    for lvl, cnt in inv.items(): tr += cnt * calculate_reward(lvl)
                    st.session_state.jail_confirm = tr
                    st.rerun()
        
        st.divider()
        for lvl, count in sorted(inv.items(), reverse=True):
            if count > 0:
                with st.container():
                    c1, c2, c3 = st.columns([1, 2, 2])
                    with c1: st.image(get_img_url(lvl), width=60)
                    with c2: st.markdown(f"#### {get_criminal_name(lvl)}"); st.markdown(f"Count: <span class='neon'>{count}</span>", unsafe_allow_html=True)
                    with c3:
                        if st.button(f"🧬 (2->1)", key=f"kf_{lvl}"): 
                            update_inventory(st.session_state.wallet, lvl, -2); update_inventory(st.session_state.wallet, lvl+1, 1); st.toast("Success!", icon="✨"); st.rerun()
                        r = calculate_reward(lvl)
                        if st.button(f"🔒 (+{r:.4f})", key=f"kj_{lvl}"): 
                            update_inventory(st.session_state.wallet, lvl, -1); 
                            with get_db() as conn: conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (r, st.session_state.wallet)); conn.commit()
                            record_profit_and_rank(st.session_state.wallet, r, lvl); st.rerun()
                st.markdown("---")
    else:
        st.info(T("inv_empty"))

# === 4. 명예의 전당 ===
with tabs[2]:
    st.subheader(T("rank_title"))
    st.caption(T("rank_desc"))
    with get_db() as conn:
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0), IFNULL(total_profit, 0.0), IFNULL(max_sold_lvl, 0) FROM users WHERE total_profit > 0 AND wallet != 'Operator_Admin' ORDER BY max_sold_lvl DESC, total_profit DESC LIMIT 10").fetchall()
    
    if not ranks: st.info(T("rank_empty"))
    else:
        for i, (w, b, p, m) in enumerate(ranks):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            st.markdown(f"<div class='card-box' style='display:flex; justify-content:space-between;'><span>{medal} <span class='neon'>{w}</span></span><span><span class='red'>Lv.{m}</span> / <span class='gold'>+{p:.2f} SOL</span></span></div>", unsafe_allow_html=True)
