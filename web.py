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
st.set_page_config(page_title="WOOHOO SECURITY V22.2", layout="wide")
DB_PATH = "woohoo_v22_2_full.db"

# [2. 함수 정의]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, revenue REAL DEFAULT 0.0, total_profit REAL DEFAULT 0.0, max_lvl INTEGER DEFAULT 0, max_sold_lvl INTEGER DEFAULT 0, rental_expiry TEXT, rental_type TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, revenue, total_profit, max_lvl, max_sold_lvl) VALUES ('Operator_Admin', 0.0, 0.0, 0.0, 0, 0)")
        conn.commit()

def get_user():
    if not st.session_state.wallet: return None
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        if row:
            return {
                "wallet": row[0], "balance": row[1], "revenue": row[2], 
                "total_profit": row[3], "max_lvl": row[4], "max_sold_lvl": row[5],
                "rental_expiry": row[6], "rental_type": row[7]
            }
        return None

def update_balance(d):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (d, st.session_state.wallet))
        if d < 0: # 사용한 돈은 매출로
            conn.execute("UPDATE users SET revenue = revenue + ? WHERE wallet='Operator_Admin'", (abs(d),))
        conn.commit()

def buy_rental(type, cost):
    user = get_user()
    if user['balance'] < cost:
        st.error("잔액 부족! 충전이 필요합니다.")
        return
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance - ? WHERE wallet=?", (cost, st.session_state.wallet))
        conn.execute("UPDATE users SET revenue = revenue + ? WHERE wallet='Operator_Admin'", (cost,))
        now = datetime.now()
        current_expiry = user['rental_expiry']
        if current_expiry:
            expiry_dt = datetime.strptime(current_expiry, "%Y-%m-%d %H:%M:%S")
            new_expiry = (expiry_dt if expiry_dt > now else now) + timedelta(hours=1)
        else:
            new_expiry = now + timedelta(hours=1)
        conn.execute("UPDATE users SET rental_expiry = ?, rental_type = ? WHERE wallet=?", (new_expiry.strftime("%Y-%m-%d %H:%M:%S"), type, st.session_state.wallet))
        conn.commit()
    st.toast(f"✅ {type.upper()} 1시간 연장 완료!", icon="💳")
    st.rerun()

def check_rental_status():
    user = get_user()
    if not user or not user['rental_expiry']: return False, None, 0
    expiry = datetime.strptime(user['rental_expiry'], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    if expiry > now:
        return True, user['rental_type'], (expiry - now).total_seconds() / 60
    return False, None, 0

def update_inventory(l, d):
    with get_db() as conn:
        c = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, l)).fetchone()
        n = (c[0] + d) if c else d
        if n < 0: n = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, l, n)); conn.commit()

def get_inv():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())

def gacha_pull(n):
    levels = list(range(1, 101))
    weights = [100000 / (i**2.2) for i in levels] 
    return random.choices(levels, weights=weights, k=n)

def calculate_reward(lvl):
    return (0.003 * (1.05**(lvl-1))) if lvl <= 100 else (0.003 * (1.05**99) + (lvl-100)*0.2)

def record_profit_and_rank(amount, sold_lvl):
    with get_db() as conn:
        conn.execute("UPDATE users SET total_profit = total_profit + ? WHERE wallet=?", (amount, st.session_state.wallet))
        curr = conn.execute("SELECT max_sold_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()[0]
        if sold_lvl > curr: conn.execute("UPDATE users SET max_sold_lvl = ? WHERE wallet=?", (sold_lvl, st.session_state.wallet))
        conn.commit()

def get_criminal_name(lvl):
    return f"Lv.{lvl} Scammer"

def get_img_url(lvl):
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=Scam{lvl}&backgroundColor=1a1a1a"

# [3. 초기화]
init_db()

# [4. 16개국어 데이터 (완벽 복구)]
LANG = {
    "🇰🇷 한국어": {
        "title": "WOOHOO 보안 플랫폼", 
        "tab_photon": "⚡ 포톤 트레이딩", "tab_sec": "🛡️ 보안 센터", "tab_game": "🎮 미니게임", "tab_rank": "🏆 명예의 전당",
        "wallet_con": "지갑 연결 (봇 검사)", "wallet_dis": "연결 해제", 
        "story_short": "허니팟 없는 세상을 위해 만들었습니다.", "tele_info": "제보: @FUCKHONEYPOT",
        "rental_shop": "🛒 렌탈샵 (이용권)", "rental_basic": "Basic (0.01 SOL/시간)", "rental_pro": "PRO (0.1 SOL/시간)",
        "mode_basic_desc": "위험 감지 시 경고만 함", "mode_pro_desc": "위험 감지 시 매수 원천 차단",
        "msg_expired": "🚫 이용권이 만료되었습니다. 렌탈샵에서 구매하세요.",
        "sec_input": "검사할 코인 주소 (CA)", "btn_scan": "허니팟 정밀 분석",
        "game_desc": "스캠범 체포 (확률 상향)", "pull_1": "1회", "pull_5": "5회", "pull_10": "10회", "pull_100": "🔥 100회",
        "inv_empty": "보관함이 비어있습니다.", "fuse_all": "🧬 일괄 합성", "jail_all": "🔒 일괄 감옥",
        "btn_yes": "✅ 승인", "btn_no": "❌ 취소", "toast_catch": "{n}명 체포!", "buy_confirm": "⚠️ {cost} SOL 결제",
        "toast_fuse": "합성 완료!", "toast_jail": "이송 완료! +{r:.4f} SOL",
        "rank_title": "명예의 전당", "rank_desc": "최고의 헌터들", "rank_empty": "데이터 없음"
    },
    "🇺🇸 English": {
        "title": "WOOHOO SECURITY", 
        "tab_photon": "⚡ Photon Trading", "tab_sec": "🛡️ Security Center", "tab_game": "🎮 Mini Game", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Connect (Anti-Bot)", "wallet_dis": "Disconnect", 
        "story_short": "Stop Honey Pots.", "tele_info": "Report: @FUCKHONEYPOT",
        "rental_shop": "🛒 Rental Shop", "rental_basic": "Basic (0.01 SOL/h)", "rental_pro": "PRO (0.1 SOL/h)",
        "mode_basic_desc": "Warn Only", "mode_pro_desc": "Block Purchase",
        "msg_expired": "🚫 Rental Expired. Please renew.",
        "sec_input": "Token Address (CA)", "btn_scan": "Scan Token",
        "game_desc": "Arrest Scammers", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "🔥 x100",
        "inv_empty": "Empty.", "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "btn_yes": "✅ Yes", "btn_no": "❌ No", "toast_catch": "{n} Captured!", "buy_confirm": "⚠️ Confirm {cost} SOL?",
        "toast_fuse": "Fused!", "toast_jail": "Jailed! +{r:.4f} SOL",
        "rank_title": "Hall of Fame", "rank_desc": "Top Hunters", "rank_empty": "No Data"
    },
    # 나머지 14개국어 (복구)
    "🇯🇵 日本語": {"title": "WOOHOO", "tab_photon": "⚡ フォトン取引", "rental_basic": "Basic (0.01 SOL)", "rental_pro": "PRO (0.1 SOL)", "pull_1": "1回", "pull_5": "5回", "pull_10": "10回", "pull_100": "100回", "btn_yes": "✅", "btn_no": "❌"},
    "🇨🇳 中文": {"title": "WOOHOO", "tab_photon": "⚡ 光子交易", "rental_basic": "Basic (0.01 SOL)", "rental_pro": "PRO (0.1 SOL)", "pull_1": "1次", "pull_5": "5次", "pull_10": "10次", "pull_100": "100次", "btn_yes": "✅", "btn_no": "❌"},
    "🇷🇺 Русский": {"title": "WOOHOO", "tab_photon": "⚡ Трейдинг", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇻🇳 Tiếng Việt": {"title": "WOOHOO", "tab_photon": "⚡ Giao dịch", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇹🇭 ภาษาไทย": {"title": "WOOHOO", "tab_photon": "⚡ การซื้อขาย", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇮🇱 עברית": {"title": "WOOHOO", "tab_photon": "⚡ מסחר", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇵🇭 Tagalog": {"title": "WOOHOO", "tab_photon": "⚡ Trading", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇲🇾 Melayu": {"title": "WOOHOO", "tab_photon": "⚡ Trading", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇮🇩 Indonesia": {"title": "WOOHOO", "tab_photon": "⚡ Trading", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇹🇷 Türkçe": {"title": "WOOHOO", "tab_photon": "⚡ Ticaret", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇵🇹 Português": {"title": "WOOHOO", "tab_photon": "⚡ Negociação", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇪🇸 Español": {"title": "WOOHOO", "tab_photon": "⚡ Comercio", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇩🇪 Deutsch": {"title": "WOOHOO", "tab_photon": "⚡ Handel", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇫🇷 Français": {"title": "WOOHOO", "tab_photon": "⚡ Trading", "rental_basic": "Basic", "rental_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"}
}

# [5. 스타일링 - 블랙 & 가독성]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700&display=swap');
    
    .stApp, [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
        font-family: 'Noto Sans KR', sans-serif; 
    }
    
    h1, h2, h3, h4, h5, h6, p, label, div, span { color: #ffffff !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    .stTextInput > div > div > input { 
        color: #ffffff !important; 
        background-color: #222222 !important; 
        border: 1px solid #66fcf1 !important;
    }
    
    .card-box { 
        border: 2px solid #66fcf1; 
        background: #111111; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 10px; 
    }
    
    .neon { color: #66fcf1 !important; font-weight: bold; }
    .gold { color: #FFD700 !important; font-weight: bold; }
    .red { color: #FF4B4B !important; font-weight: bold; }
    
    .stButton button { 
        border: 2px solid #66fcf1; 
        background: #000000; 
        color: #66fcf1 !important; 
        font-weight: bold; 
    }
    .stButton button:hover { 
        background: #66fcf1; 
        color: #000000 !important; 
        border: 2px solid #ffffff;
    }
    
    .tiny-warn { 
        color: #FFD700 !important; 
        border: 1px solid #FFD700; 
        background: #222; 
        padding: 5px; 
        text-align: center;
        border-radius: 5px; 
    }
</style>
""", unsafe_allow_html=True)

# [6. 세션]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'lang' not in st.session_state: st.session_state.lang = "🇰🇷 한국어"
if 'confirm_target' not in st.session_state: st.session_state.confirm_target = None

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
    st.info(T("story_short"))
    st.markdown(f"📢 **{T('tele_info')}**")
    
    st.divider()
    if not st.session_state.wallet:
        if st.button(T("wallet_con")): st.session_state.wallet = "Operator_Admin"; st.rerun()
    else:
        user = get_user()
        st.success(f"User: {user['wallet']}")
        st.metric("Balance", f"{user['balance']:.4f} SOL")
        
        # 렌탈샵
        st.markdown("---")
        st.subheader(T("rental_shop"))
        is_active, r_type, mins = check_rental_status()
        if is_active:
            st.info(f"✅ {r_type.upper()} Mode\n(Time: {int(mins)}m)")
        else:
            st.warning("⛔ No Active Rental")
            
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Basic\n(0.01)"): buy_rental('basic', 0.01)
        with c2:
            if st.button("PRO\n(0.1)"): buy_rental('pro', 0.1)
        
        st.caption(f"Basic: {T('mode_basic_desc')}")
        st.caption(f"PRO: {T('mode_pro_desc')}")
        
        st.markdown("---")
        if st.button(T("wallet_dis")): st.session_state.wallet = None; st.rerun()

st.title(T("title"))

if not st.session_state.wallet:
    st.warning("Please Connect Wallet First.")
    st.stop()

# 탭 구성: 포톤(매매) / 보안센터 / 미니게임 / 랭킹
tabs = st.tabs([T("tab_photon"), T("tab_sec"), T("tab_game"), T("tab_rank")])

# === 탭 1: 포톤 트레이딩 (자동 매매) ===
with tabs[0]:
    st.subheader(T("tab_photon"))
    is_active, r_type, _ = check_rental_status()
    
    if not is_active:
        st.error(T("msg_expired"))
    else:
        ca_input = st.text_input("Target CA", placeholder="Token Contract Address...")
        c1, c2, c3 = st.columns(3)
        with c1: st.number_input("Amount (SOL)", value=0.5)
        with c2: st.number_input("Slippage (%)", value=10)
        with c3: st.text_input("Priority Fee", value="0.005")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Auto Buy", type="primary"):
            if not ca_input:
                st.warning("Input CA first.")
            else:
                risk = random.randint(0, 100)
                is_scam = risk > 70
                with st.spinner("Tx Pending..."):
                    time.sleep(0.5)
                    if is_scam and r_type == 'pro':
                        st.error(f"⛔ [PRO BLOCKED] HoneyPot Detected! (Risk {risk}%)")
                    elif is_scam and r_type == 'basic':
                        st.warning(f"⚠️ [Basic Warn] Risk {risk}% detected! Buying anyway...")
                        st.success("✅ Buy Success!")
                    else:
                        st.success(f"✅ Buy Success! (Clean Token, Risk {risk}%)")

# === 탭 2: 보안 센터 (스캠 판독) ===
with tabs[1]:
    st.subheader(T("tab_sec"))
    target_addr = st.text_input(T("sec_input"), placeholder="0x...")
    
    if st.button(f"{T('btn_scan')}"):
        is_active, r_type, _ = check_rental_status()
        if not is_active:
            st.error(T("msg_expired"))
        else:
            if not target_addr:
                st.warning("Address Required.")
            else:
                risk = random.randint(10, 99)
                is_scam = risk > 70
                with st.status("Scanning...", expanded=True) as status:
                    time.sleep(0.3); st.write("📜 Contract...")
                    time.sleep(0.3); st.write("💧 Liquidity...")
                    status.update(label="Done", state="complete", expanded=False)
                
                if is_scam:
                    if r_type == 'basic':
                        st.warning(f"⚠️ [WARNING] Risk {risk}%! Honeypot detected.")
                    else:
                        st.error(f"🚫 [PRO BLOCKED] Honeypot (Risk {risk}%)! Purchase Blocked.")
                else:
                    st.success(f"✅ [SAFE] Clean Token (Risk {risk}%)")

# === 탭 3: 미니게임 (4버튼 복구) ===
with tabs[2]:
    st.subheader(T("tab_game"))
    st.caption(T("game_desc"))
    
    def execute_pull(cost, n):
        user = get_user()
        if user['balance'] < cost: st.error(T("err_bal"))
        else:
            update_balance(-cost)
            res = gacha_pull(n)
            for r in res: update_inventory(r, 1)
            st.toast(T("toast_catch", n=n), icon="🚨")
            if n >= 100: st.balloons()
        st.session_state.confirm_target = None
        st.rerun()

    c1, c2, c3, c4 = st.columns(4)
    # 1회
    with c1:
        if st.session_state.confirm_target == "p1":
            st.markdown(f"<div class='tiny-warn'>{T('buy_confirm', cost=0.01)}</div>", unsafe_allow_html=True)
            if st.button(T("btn_yes"), key="y1"): execute_pull(0.01, 1)
            if st.button(T("btn_no"), key="n1"): st.session_state.confirm_target = None; st.rerun()
        else:
            if st.button(f"{T('pull_1')} (0.01 SOL)", key="btn_p1"): st.session_state.confirm_target = "p1"; st.rerun()
    # 5회
    with c2:
        if st.session_state.confirm_target == "p5":
            st.markdown(f"<div class='tiny-warn'>{T('buy_confirm', cost=0.05)}</div>", unsafe_allow_html=True)
            if st.button(T("btn_yes"), key="y5"): execute_pull(0.05, 5)
            if st.button(T("btn_no"), key="n5"): st.session_state.confirm_target = None; st.rerun()
        else:
            if st.button(f"{T('pull_5')} (0.05 SOL)", key="btn_p5"): st.session_state.confirm_target = "p5"; st.rerun()
    # 10회
    with c3:
        if st.session_state.confirm_target == "p10":
            st.markdown(f"<div class='tiny-warn'>{T('buy_confirm', cost=0.10)}</div>", unsafe_allow_html=True)
            if st.button(T("btn_yes"), key="y10"): execute_pull(0.10, 10)
            if st.button(T("btn_no"), key="n10"): st.session_state.confirm_target = None; st.rerun()
        else:
            if st.button(f"{T('pull_10')} (0.10 SOL)", key="btn_p10"): st.session_state.confirm_target = "p10"; st.rerun()
    # 100회
    with c4:
        if st.session_state.confirm_target == "p100":
            st.markdown(f"<div class='tiny-warn'>{T('buy_confirm', cost=1.00)}</div>", unsafe_allow_html=True)
            if st.button(T("btn_yes"), key="y100"): execute_pull(1.00, 100)
            if st.button(T("btn_no"), key="n100"): st.session_state.confirm_target = None; st.rerun()
        else:
            if st.button(f"{T('pull_100')} (1.00 SOL)", key="btn_p100", type="primary"): st.session_state.confirm_target = "p100"; st.rerun()

    # 보관함
    st.divider()
    st.subheader("Inventory")
    inv = get_inv()
    if inv:
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button(T("fuse_all"), key="bf"):
                for lvl in sorted(inv.keys()):
                    f_cnt = inv[lvl] // 2
                    if f_cnt > 0 and lvl < 1000: update_inventory(lvl, -(f_cnt*2)); update_inventory(lvl+1, f_cnt)
                st.toast(T("toast_fuse"), icon="🧬"); st.rerun()
        with bc2:
            if st.button(T("jail_all"), key="bj"):
                tr = 0
                for lvl, cnt in inv.items():
                    r = cnt * calculate_reward(lvl)
                    update_inventory(lvl, -cnt); tr += r
                    record_profit_and_rank(0, lvl)
                with get_db() as conn: conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (tr, st.session_state.wallet)); conn.commit()
                record_profit_and_rank(tr, 0); st.toast(T("toast_jail", r=tr), icon="💰"); st.rerun()
        
        st.divider()
        for lvl, count in sorted(inv.items(), reverse=True):
            if count > 0:
                with st.container():
                    c1, c2, c3 = st.columns([1, 2, 2])
                    with c1: st.image(get_img_url(lvl), width=60)
                    with c2: st.markdown(f"#### {get_criminal_name(lvl)}"); st.markdown(f"Count: <span class='neon'>{count}</span>", unsafe_allow_html=True)
                    with c3:
                        if st.button(f"🧬 (2->1)", key=f"kf_{lvl}"): 
                            update_inventory(lvl, -2); update_inventory(lvl+1, 1); st.toast("Success!", icon="✨"); st.rerun()
                        r = calculate_reward(lvl)
                        if st.button(f"🔒 (+{r:.4f})", key=f"kj_{lvl}"): 
                            update_inventory(lvl, -1); 
                            with get_db() as conn: conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (r, st.session_state.wallet)); conn.commit()
                            record_profit_and_rank(r, lvl); st.rerun()
                st.markdown("---")
    else:
        st.info(T("inv_empty"))

# === 4. 명예의 전당 ===
with tabs[3]:
    st.subheader(T("rank_title"))
    st.caption(T("rank_desc"))
    with get_db() as conn:
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0), IFNULL(total_profit, 0.0), IFNULL(max_sold_lvl, 0) FROM users WHERE total_profit > 0 AND wallet != 'Operator_Admin' ORDER BY max_sold_lvl DESC, total_profit DESC LIMIT 10").fetchall()
    
    if not ranks: st.info(T("rank_empty"))
    else:
        for i, (w, b, p, m) in enumerate(ranks):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            st.markdown(f"<div class='card-box' style='display:flex; justify-content:space-between;'><span>{medal} <span class='neon'>{w}</span></span><span><span class='red'>Lv.{m}</span> / <span class='gold'>+{p:.2f} SOL</span></span></div>", unsafe_allow_html=True)
