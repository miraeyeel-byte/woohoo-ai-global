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
st.set_page_config(page_title="WOOHOO SECURITY V21.6", layout="wide")
DB_PATH = "woohoo_v21_6_final.db"

# [2. 함수 정의]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, revenue REAL DEFAULT 0.0, total_profit REAL DEFAULT 0.0, max_lvl INTEGER DEFAULT 0, max_sold_lvl INTEGER DEFAULT 0, is_bot INTEGER DEFAULT 0)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        # 운영자 계정 (초기 자금 0, 유저들이 돈 쓰면 revenue 쌓임)
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, revenue, total_profit, max_lvl, max_sold_lvl, is_bot) VALUES ('Operator_Admin', 0.0, 0.0, 0.0, 0, 0, 0)")
        # 가짜 랭커
        fake_users = [('HQ7a...k9L', 50.0, 524.12, 0, 55, 1), ('Ab2x...1zP', 12.0, 120.50, 0, 30, 1), ('9xKq...m4R', 5.5, 45.20, 0, 22, 1)]
        for user in fake_users:
            c.execute("INSERT OR IGNORE INTO users (wallet, balance, revenue, total_profit, max_lvl, max_sold_lvl, is_bot) VALUES (?, ?, 0.0, ?, ?, ?, ?)", user)
        conn.commit()

def get_user():
    if not st.session_state.wallet: return None, 0.0, 0.0, 0.0, 0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance, revenue, total_profit, max_sold_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0, 0.0, 0.0, 0)

def update_balance(d):
    with get_db() as conn:
        # 유저 지갑 차감/지급
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (d, st.session_state.wallet))
        # 유저가 돈을 썼을 때(음수) -> 운영자 매출(Revenue)로 적립
        if d < 0:
            conn.execute("UPDATE users SET revenue = revenue + ? WHERE wallet='Operator_Admin'", (abs(d),))
        conn.commit()

def update_inventory(l, d):
    with get_db() as conn:
        c = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, l)).fetchone()
        n = (c[0] + d) if c else d
        if n < 0: n = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, l, n)); conn.commit()

def get_inv():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())

def record_profit_and_rank(amount, sold_lvl):
    with get_db() as conn:
        conn.execute("UPDATE users SET total_profit = total_profit + ? WHERE wallet=?", (amount, st.session_state.wallet))
        curr = conn.execute("SELECT max_sold_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()[0]
        if sold_lvl > curr: conn.execute("UPDATE users SET max_sold_lvl = ? WHERE wallet=?", (sold_lvl, st.session_state.wallet))
        conn.commit()

def gacha_pull(n):
    levels = list(range(1, 101))
    weights = [100000 / (i**2.2) for i in levels] 
    return random.choices(levels, weights=weights, k=n)

def calculate_reward(lvl):
    return (0.003 * (1.05**(lvl-1))) if lvl <= 100 else (0.003 * (1.05**99) + (lvl-100)*0.2)

def run_security_scan(addr, mode):
    risk = random.randint(10, 99)
    with st.status("Analyzing...", expanded=True) as status:
        time.sleep(0.5); st.write("Scanning...")
        time.sleep(0.5); st.write("Checking...")
        status.update(label="Done", state="complete", expanded=False)
    
    if risk < 30:
        st.success(f"✅ Safe (Risk: {risk}%)")
    else:
        if mode == "basic":
            st.warning(f"⚠️ Warning! Risk: {risk}% (Reports found)")
        else:
            st.error(f"🚫 BLOCKED! Risk: {risk}% (Proxy Detected)")

def get_criminal_name(lvl):
    return f"Lv.{lvl} Scammer"

def get_img_url(lvl):
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=Scam{lvl}&backgroundColor=1a1a1a"

# [3. 초기화]
init_db()

# [4. 16개국어 데이터]
LANG = {
    "🇰🇷 한국어": {
        "title": "WOOHOO 보안 플랫폼", 
        "tab_sec": "🛡️ 보안 센터", "tab_game": "🚨 범인 체포", "tab_inv": "📦 보관함", "tab_rank": "🏆 명예의 전당",
        "wallet_con": "지갑 연결", "wallet_dis": "연결 해제", 
        "balance": "내 지갑", # 심플하게 변경
        "mode_basic": "BASIC (0.01 SOL)", "mode_basic_desc": "단순 경고 (구매 가능)",
        "mode_pro": "PRO (0.1 SOL)", "mode_pro_desc": "스캠 코인 매수 원천 차단",
        "sec_input": "검사할 주소 입력", "btn_scan": "검사 시작",
        "game_desc": "스캠범 체포 (확률 상향)",
        "pull_1": "1회", "pull_5": "5회", "pull_10": "10회", "pull_100": "🔥 100회",
        "inv_empty": "보관함이 비어있습니다.", "fuse_all": "🧬 일괄 합성", "jail_all": "🔒 일괄 감옥",
        "btn_yes": "✅ 승인", "btn_no": "❌ 취소", "toast_catch": "{n}명 체포!", "err_bal": "잔액 부족",
        "fuse_confirm": "{n}회 합성합니까?", "jail_confirm": "모두 보냅니까?",
        "buy_confirm": "⚠️ {cost} SOL 결제",
        "toast_fuse": "합성 완료!", "toast_jail": "이송 완료! +{r:.4f} SOL",
        "rank_title": "명예의 전당", "rank_desc": "최고의 헌터들", "rank_empty": "데이터 없음",
        "story_short": "허니팟 없는 세상을 위해 만들었습니다.", "tele_info": "제보: @FUCKHONEYPOT"
    },
    "🇺🇸 English": {
        "title": "WOOHOO SECURITY", 
        "tab_sec": "🛡️ Security", "tab_game": "🚨 Arrest", "tab_inv": "📦 Inventory", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Connect", "wallet_dis": "Disconnect", 
        "balance": "Balance",
        "mode_basic": "BASIC (0.01 SOL)", "mode_basic_desc": "Warn Only",
        "mode_pro": "PRO (0.1 SOL)", "mode_pro_desc": "Block Scam Purchase",
        "sec_input": "Enter Address", "btn_scan": "Scan",
        "game_desc": "Arrest Scammers",
        "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "🔥 x100",
        "inv_empty": "Empty.", "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "btn_yes": "✅ Yes", "btn_no": "❌ No", "toast_catch": "{n} Captured!", "err_bal": "Low Balance.",
        "fuse_confirm": "Fuse {n}?", "jail_confirm": "Jail All?", "buy_confirm": "⚠️ Confirm {cost} SOL?",
        "toast_fuse": "Fused!", "toast_jail": "Jailed! +{r:.4f} SOL",
        "rank_title": "Hall of Fame", "rank_desc": "Top Hunters", "rank_empty": "No Data",
        "story_short": "Stop Honey Pots.", "tele_info": "Report: @FUCKHONEYPOT"
    },
    # 나머지 언어 (공간상 유지)
    "🇯🇵 日本語": {"title": "WOOHOO", "balance": "残高", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "1回", "pull_5": "5回", "pull_10": "10回", "pull_100": "100回", "btn_yes": "✅", "btn_no": "❌"},
    "🇨🇳 中文": {"title": "WOOHOO", "balance": "余额", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "1次", "pull_5": "5次", "pull_10": "10次", "pull_100": "100次", "btn_yes": "✅", "btn_no": "❌"},
    "🇷🇺 Русский": {"title": "WOOHOO", "balance": "Баланс", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇻🇳 Tiếng Việt": {"title": "WOOHOO", "balance": "Số dư", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇹🇭 ภาษาไทย": {"title": "WOOHOO", "balance": "ยอดเงิน", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇮🇱 עברית": {"title": "WOOHOO", "balance": "יתרה", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇵🇭 Tagalog": {"title": "WOOHOO", "balance": "Balanse", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇲🇾 Melayu": {"title": "WOOHOO", "balance": "Baki", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇮🇩 Indonesia": {"title": "WOOHOO", "balance": "Saldo", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇹🇷 Türkçe": {"title": "WOOHOO", "balance": "Bakiye", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇵🇹 Português": {"title": "WOOHOO", "balance": "Saldo", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇪🇸 Español": {"title": "WOOHOO", "balance": "Saldo", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇩🇪 Deutsch": {"title": "WOOHOO", "balance": "Guthaben", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"},
    "🇫🇷 Français": {"title": "WOOHOO", "balance": "Solde", "mode_basic": "BASIC", "mode_pro": "PRO", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "pull_100": "x100", "btn_yes": "✅", "btn_no": "❌"}
}

# [5. 스타일링 - 흰색 강제 적용으로 시인성 확보]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700&display=swap');
    /* 배경은 블랙, 모든 텍스트는 화이트 강제 */
    .stApp { background-color: #000000; color: #ffffff !important; font-family: 'Noto Sans KR', sans-serif; }
    
    /* 텍스트 가시성 최우선 */
    h1, h2, h3, h4, h5, h6, p, div, span, label { color: #ffffff !important; }
    
    /* 입력창 내부 텍스트 및 배경 */
    .stTextInput > div > div > input { 
        color: #ffffff !important; 
        background-color: #222222 !important; 
        border: 1px solid #66fcf1 !important;
    }
    
    /* 박스 스타일 */
    .card-box { 
        border: 1px solid #66fcf1; 
        background: #111111; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 10px; 
    }
    
    /* 강조 색상 */
    .neon { color: #66fcf1 !important; font-weight: bold; }
    .gold { color: #FFD700 !important; font-weight: bold; }
    .red { color: #FF4B4B !important; font-weight: bold; }
    
    /* 버튼 */
    .stButton button { 
        border: 1px solid #66fcf1; 
        background: #000000; 
        color: #66fcf1 !important; 
        font-weight: bold; 
    }
    .stButton button:hover { 
        background: #66fcf1; 
        color: #000000 !important; 
    }
    
    /* 경고창 */
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
        u_w, u_b, u_rev, u_p, u_m = get_user()
        st.success(f"{u_w}")
        # [수정] 운영자 전용 매출/충전 버튼 전부 삭제 -> 깔끔하게 자산만 표시
        st.metric(T("balance"), f"{u_b:.4f} SOL")
        
        if st.button(T("wallet_dis")): st.session_state.wallet = None; st.rerun()

st.title(T("title"))

if not st.session_state.wallet:
    st.warning("Please Connect Wallet First.")
    st.stop()

tabs = st.tabs([T("tab_sec"), T("tab_game"), T("tab_inv"), T("tab_rank")])

# === 탭 1: 보안 센터 ===
with tabs[0]:
    st.subheader(T("tab_sec"))
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='card-box'><h4 class='gold'>{T('mode_basic')}</h4><p>{T('mode_basic_desc')}</p></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='card-box'><h4 class='red'>{T('mode_pro')}</h4><p>{T('mode_pro_desc')}</p></div>", unsafe_allow_html=True)
    
    mode = st.radio("Mode", ["basic", "pro"], label_visibility="collapsed")
    target_addr = st.text_input(T("sec_input"), placeholder="0x...")
    cost = 0.01 if mode == "basic" else 0.1
    
    if st.button(f"{T('btn_scan')} ({cost} SOL)"):
        _, bal, _, _, _ = get_user()
        if bal < cost: st.error(T("err_bal"))
        else:
            if not target_addr: st.warning("Address Required.")
            else:
                update_balance(-cost)
                run_security_scan(target_addr, mode)

# === 탭 2: 범인 체포 ===
with tabs[1]:
    st.subheader(T("tab_game"))
    st.caption(T("game_desc"))
    
    def execute_pull(cost, n):
        _, bal, _, _, _ = get_user()
        if bal < cost: st.error(T("err_bal"))
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

# === 탭 3: 보관함 ===
with tabs[2]:
    st.subheader(T("tab_inv"))
    inv = get_inv()
    if inv:
        bc1, bc2 = st.columns(2)
        total_fusions = sum([cnt // 2 for lvl, cnt in inv.items() if lvl < 1000])
        
        with bc1:
            if st.session_state.confirm_target == "fuse_all":
                st.markdown(f"<div class='tiny-warn'>{T('fuse_confirm', n=total_fusions)}</div>", unsafe_allow_html=True)
                if st.button(T("btn_yes"), key="fy"):
                    for lvl in sorted(inv.keys()):
                        f_cnt = inv[lvl] // 2
                        if f_cnt > 0 and lvl < 1000: update_inventory(lvl, -(f_cnt*2)); update_inventory(lvl+1, f_cnt)
                    st.toast(T("toast_fuse"), icon="🧬"); st.session_state.confirm_target = None; st.rerun()
                if st.button(T("btn_no"), key="fn"): st.session_state.confirm_target = None; st.rerun()
            else:
                if st.button(f"{T('fuse_all')} ({total_fusions})", type="primary", disabled=total_fusions==0, key="bf"): st.session_state.confirm_target = "fuse_all"; st.rerun()
        
        with bc2:
            if st.session_state.confirm_target == "jail_all":
                st.markdown(f"<div class='tiny-warn'>{T('jail_confirm')}</div>", unsafe_allow_html=True)
                if st.button(T("btn_yes"), key="jy"):
                    tr = 0
                    for lvl, cnt in inv.items():
                        if cnt > 0:
                            r = cnt * calculate_reward(lvl)
                            update_inventory(lvl, -cnt); tr += r
                            record_profit_and_rank(0, lvl)
                    with get_db() as conn:
                        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (tr, st.session_state.wallet)); conn.commit()
                    record_profit_and_rank(tr, 0); st.toast(T("toast_jail", r=tr), icon="💰"); st.session_state.confirm_target = None; st.rerun()
                if st.button(T("btn_no"), key="jn"): st.session_state.confirm_target = None; st.rerun()
            else:
                if st.button(T("jail_all"), key="bj"): st.session_state.confirm_target = "jail_all"; st.rerun()

    st.divider()
    if not inv: st.info(T("inv_empty"))
    else:
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
                            with get_db() as conn:
                                conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (r, st.session_state.wallet)); conn.commit()
                            record_profit_and_rank(r, lvl); st.rerun()
                st.markdown("---")

# === 4. 명예의 전당 ===
with tabs[3]:
    st.subheader(T("rank_title"))
    st.caption(T("rank_desc"))
    with get_db() as conn:
        # [수정] 운영자('Operator_Admin')는 랭킹에서 제외 (WHERE wallet != ...)
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0), IFNULL(total_profit, 0.0), IFNULL(max_sold_lvl, 0) FROM users WHERE total_profit > 0 AND wallet != 'Operator_Admin' ORDER BY max_sold_lvl DESC, total_profit DESC LIMIT 10").fetchall()
    
    if not ranks: st.info(T("rank_empty"))
    else:
        for i, (w, b, p, m) in enumerate(ranks):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            st.markdown(f"<div class='card-box' style='display:flex; justify-content:space-between;'><span>{medal} <span class='neon'>{w}</span></span><span><span class='red'>Lv.{m}</span> / <span class='gold'>+{p:.2f} SOL</span></span></div>", unsafe_allow_html=True)
