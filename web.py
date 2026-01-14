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
st.set_page_config(page_title="WOOHOO SECURITY V19.4", layout="wide")
DB_PATH = "woohoo_v19_4_god.db"

# [2. 16개국어 번역 팩]
LANG = {
    "🇰🇷 한국어": {
        "title": "WOOHOO 보안 플랫폼",
        "tab_sec": "🛡️ 보안 센터", "tab_game": "🚨 범인 체포", "tab_inv": "📦 보관함", "tab_rank": "🏆 명예의 전당",
        "wallet_con": "지갑 연결", "wallet_dis": "연결 해제", "balance": "자산", "total_profit": "누적 수익", "max_lvl": "최고 레벨",
        "sec_btn": "💰 매수 시도", "sec_warn": "주소를 입력하세요.", "sec_safe": "✅ 안전 (점수: {score})", "sec_danger": "🚨 [경고] 위험 점수 {score}!", "sec_block": "🚫 차단됨!",
        "game_desc": "비용을 지불하고 체포합니다. (최대 Lv.100 출현 / Lv.1000은 합성으로만 가능)",
        "pull_1": "1회 체포", "pull_5": "5회 체포", "pull_10": "10회 체포",
        "inv_empty": "보관함이 비어있습니다.", "fuse_all": "🧬 일괄 합성", "jail_all": "🔒 일괄 감옥",
        "btn_yes": "✅ 승인", "btn_no": "❌ 취소",
        "toast_catch": "{n}명 체포 완료!", "err_bal": "잔액이 부족합니다.",
        "fuse_confirm": "총 {n}회 합성을 진행합니까?", "jail_confirm": "모두 감옥으로 보내고 보상을 받겠습니까?",
        "toast_fuse": "일괄 합성 완료!", "toast_jail": "이송 완료! +{r:.4f} SOL",
        "rank_title": "명예의 전당", "rank_desc": "최고 레벨 범죄자를 검거하고 수익을 낸 헌터들",
        "name_1": "소매치기", "name_10": "양아치", "name_50": "조직 간부", "name_100": "세계관 최강자",
        "name_500": "차원의 지배자", "name_900": "우주 파괴자", "name_1000": "THE GOD (신)"
    },
    "🇺🇸 English": {
        "title": "WOOHOO SECURITY PLATFORM",
        "tab_sec": "🛡️ Security", "tab_game": "🚨 Arrest", "tab_inv": "📦 Inventory", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Connect Wallet", "wallet_dis": "Disconnect", "balance": "Balance", "total_profit": "Total Profit", "max_lvl": "Max Lvl",
        "sec_btn": "💰 Buy (Sim)", "sec_warn": "Enter Address.", "sec_safe": "✅ Safe (Score: {score})", "sec_danger": "🚨 High Risk {score}!", "sec_block": "🚫 Blocked!",
        "game_desc": "Arrest criminals. Max draw Lv.100. Fuse to reach Lv.1000!",
        "pull_1": "Arrest x1", "pull_5": "Arrest x5", "pull_10": "Arrest x10",
        "inv_empty": "Inventory Empty.", "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "btn_yes": "✅ Yes", "btn_no": "❌ No",
        "toast_catch": "{n} Captured!", "err_bal": "Insufficient Balance.",
        "fuse_confirm": "Proceed with {n} fusions?", "jail_confirm": "Send all to prison?",
        "toast_fuse": "Fusion Complete!", "toast_jail": "Sent to Prison! +{r:.4f} SOL",
        "rank_title": "Hall of Fame", "rank_desc": "Top Hunters by Max Level & Profit",
        "name_1": "Pickpocket", "name_10": "Thug", "name_50": "Gang Boss", "name_100": "Overlord",
        "name_500": "Dimension Ruler", "name_900": "Universe Destroyer", "name_1000": "THE GOD"
    }
}

# [3. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, total_profit REAL DEFAULT 0.0, max_lvl INTEGER DEFAULT 0)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, total_profit, max_lvl) VALUES ('Operator_Admin', 1000.0, 0.0, 0)")
        conn.commit()
init_db()

# [4. 유틸리티 함수]
if 'lang' not in st.session_state: st.session_state.lang = "🇰🇷 한국어"

def T(key, **kwargs):
    lang_dict = LANG.get(st.session_state.lang, LANG.get("🇺🇸 English", {}))
    text = lang_dict.get(key, LANG["🇰🇷 한국어"].get(key, key))
    if kwargs: return text.format(**kwargs)
    return text

def get_criminal_name(lvl):
    prefix = f"Lv.{lvl} "
    if lvl == 1: name = T("name_1")
    elif lvl < 10: name = T("name_10")
    elif lvl < 50: name = T("name_50")
    elif lvl < 100: name = f"Terrorist Lv.{lvl}"
    elif lvl == 100: name = T("name_100")
    elif lvl < 500: name = T("name_500")
    elif lvl < 1000: name = T("name_900")
    else: name = T("name_1000")
    return f"{prefix}{name}"

def get_img_url(lvl):
    # 레벨 1000까지 고유한 시드 생성
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=CryptoEvil{lvl}&backgroundColor=1a1a1a"

# [5. 보안 및 게임 로직]
def process_security_action(token_address, user_tier):
    risk_score = random.randint(0, 100)
    if user_tier.startswith("BASIC"):
        if risk_score >= 70: st.warning(T("sec_danger", score=risk_score)); return
    elif user_tier.startswith("PRO"):
        if risk_score >= 70: st.error(T("sec_block", score=risk_score)); return
    st.success(T("sec_safe", score=risk_score))

def get_user():
    if not st.session_state.wallet: return None, 0.0, 0.0, 0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance, total_profit, max_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0, 0.0, 0)

def update_balance(d):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (d, st.session_state.wallet)); conn.commit()

def update_inventory(l, d):
    with get_db() as conn:
        c = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, l)).fetchone()
        n = (c[0] + d) if c else d
        if n < 0: n = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, l, n)); conn.commit()
    if d > 0:
        with get_db() as conn:
            curr = conn.execute("SELECT max_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()[0]
            if l > curr: conn.execute("UPDATE users SET max_lvl = ? WHERE wallet=?", (l, st.session_state.wallet)); conn.commit()

def record_profit(amount):
    with get_db() as conn:
        conn.execute("UPDATE users SET total_profit = total_profit + ? WHERE wallet=?", (amount, st.session_state.wallet)); conn.commit()

def get_inv():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())

def gacha_pull(n):
    # [중요] 뽑기는 오직 레벨 1 ~ 100까지만 나옴
    levels = list(range(1, 101))
    weights = [1000 / (1.05 ** i) for i in levels]
    return random.choices(levels, weights=weights, k=n)

def calculate_reward(lvl):
    # [밸런스] 레벨 1000까지 감안하여 판매 가격 조정
    # Lv.1 = 0.005
    # Lv.100 = 약 0.6 SOL
    # Lv.1000 = 기하급수적 증가 방지를 위해 100 이후로는 선형 증가로 변경
    if lvl <= 100:
        return 0.005 * (1.05**(lvl-1))
    else:
        # Lv 100 보상(약 0.6) + (레벨차이 * 0.05)
        base_100 = 0.005 * (1.05**99)
        return base_100 + ((lvl - 100) * 0.05)

# [6. 스타일링]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700&display=swap');
    .stApp { background-color: #050505; color: #fff; font-family: 'Noto Sans KR', sans-serif; }
    h1, h2, h3, h4, p, div, label, span { color: #fff !important; text-shadow: 2px 2px 4px #000 !important; }
    div[role="radiogroup"] label { color: #FFD700 !important; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #222; border: 1px solid #444; color: #aaa; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; font-weight: bold; border: none; text-shadow: none !important; }
    .card-box { border: 2px solid #FFD700; background: #111; padding: 10px; text-align: center; margin-bottom: 10px; box-shadow: 5px 5px 0px #333; }
    .neon { color: #66fcf1 !important; font-weight: bold; }
    .gold { color: #FFD700 !important; font-weight: bold; }
    .red { color: #ff4b4b !important; font-weight: bold; }
    .stButton button { width: 100%; border-radius: 0px; font-weight: bold; border: 2px solid #66fcf1; background: #000; color: #66fcf1; }
    .stButton button:hover { background: #66fcf1; color: #000; }
</style>
""", unsafe_allow_html=True)

# [7. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'user_tier' not in st.session_state: st.session_state.user_tier = "BASIC (0.01 SOL)"
if 'confirm_fuse_all' not in st.session_state: st.session_state.confirm_fuse_all = False
if 'confirm_jail_all' not in st.session_state: st.session_state.confirm_jail_all = False

# [8. 메인 UI]
with st.sidebar:
    st.title("🌐 Language")
    lang_list = list(LANG.keys())
    try: idx = lang_list.index(st.session_state.lang)
    except: idx = 0
    selected_lang = st.selectbox("Select", lang_list, index=idx)
    if selected_lang != st.session_state.lang: st.session_state.lang = selected_lang; st.rerun()
    
    st.divider()
    st.header(f"🔐 {T('wallet_con')}")
    if not st.session_state.wallet:
        if st.button(T("wallet_con"), key="con"): st.session_state.wallet = "Operator_Admin"; st.rerun()
    else:
        u_wallet, u_bal, u_prof, u_max = get_user()
        st.success(f"User: {u_wallet}")
        st.metric(T("balance"), f"{u_bal:.4f} SOL")
        st.metric(T("total_profit"), f"{u_prof:.4f} SOL")
        st.metric(T("max_lvl"), f"Lv.{u_max}")
        if st.button(T("wallet_dis"), key="dis"): st.session_state.wallet = None; st.rerun()

st.title(T("title"))

if not st.session_state.wallet:
    st.info("Wallet Connect Required.")
    st.stop()

tabs = st.tabs([T("tab_sec"), T("tab_game"), T("tab_inv"), T("tab_rank")])

# === 1. 보안 센터 ===
with tabs[0]:
    st.subheader(T("tab_sec"))
    tier = st.radio("Tier", ["BASIC (0.01 SOL)", "PRO (0.1 SOL)"], label_visibility="collapsed")
    st.session_state.user_tier = tier
    st.divider()
    token = st.text_input("Address", placeholder="Solana Address...")
    if st.button(T("sec_btn"), key="btn_scan"):
        if not token: st.warning(T("sec_warn"))
        else: process_security_action(token, st.session_state.user_tier)

# === 2. 범인 체포 ===
with tabs[1]:
    st.subheader(T("tab_game"))
    st.caption(T("game_desc"))
    
    def run_gacha(cost, n):
        _, bal, _, _ = get_user()
        if bal < cost: st.error(T("err_bal")); return
        update_balance(-cost)
        res = gacha_pull(n)
        for r in res: update_inventory(r, 1)
        st.toast(T("toast_catch", n=n), icon="🚨")
        cols = st.columns(min(n, 5))
        for i, lvl in enumerate(res[:5]):
            with cols[i]:
                st.markdown(f"<div class='card-box'><img src='{get_img_url(lvl)}' width='50'><div class='neon'>Lv.{lvl}</div></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button(f"{T('pull_1')} (0.01 SOL)", key="gp1"): run_gacha(0.01, 1)
    with c2: 
        if st.button(f"{T('pull_5')} (0.05 SOL)", key="gp5"): run_gacha(0.05, 5)
    with c3: 
        if st.button(f"{T('pull_10')} (0.10 SOL)", key="gp10"): run_gacha(0.10, 10)

# === 3. 보관함 ===
with tabs[2]:
    st.subheader(T("tab_inv"))
    inv = get_inv()
    if inv:
        bc1, bc2 = st.columns(2)
        total_fusions = sum([cnt // 2 for lvl, cnt in inv.items() if lvl < 1000]) # 1000 미만만 합성
        with bc1:
            if not st.session_state.confirm_fuse_all:
                if st.button(f"{T('fuse_all')} ({total_fusions})", type="primary", disabled=total_fusions==0, key="b_fa"):
                    st.session_state.confirm_fuse_all = True; st.rerun()
            else:
                st.warning(T("fuse_confirm", n=total_fusions))
                c1, c2 = st.columns(2)
                if c1.button(T("btn_yes"), key="bfy"):
                    for lvl in sorted(inv.keys()):
                        f_cnt = inv[lvl] // 2
                        if f_cnt > 0 and lvl < 1000:
                            update_inventory(lvl, -(f_cnt*2)); update_inventory(lvl+1, f_cnt)
                    st.toast(T("toast_fuse"), icon="🧬"); st.session_state.confirm_fuse_all = False; st.rerun()
                if c2.button(T("btn_no"), key="bfn"): st.session_state.confirm_fuse_all = False; st.rerun()
        with bc2:
            if not st.session_state.confirm_jail_all:
                if st.button(T("jail_all"), key="b_ja"): st.session_state.confirm_jail_all = True; st.rerun()
            else:
                st.warning(T("jail_confirm"))
                c1, c2 = st.columns(2)
                if c1.button(T("btn_yes"), key="bjy"):
                    tr = 0
                    for lvl, cnt in inv.items():
                        if cnt > 0:
                            r = cnt * calculate_reward(lvl)
                            update_inventory(lvl, -cnt); tr += r
                    update_balance(tr); record_profit(tr); st.toast(T("toast_jail", r=tr), icon="💰"); st.session_state.confirm_jail_all = False; st.rerun()
                if c2.button(T("btn_no"), key="bjn"): st.session_state.confirm_jail_all = False; st.rerun()

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
                        if count >= 2 and lvl < 1000:
                            if st.button(f"🧬 (2->1)", key=f"kf_{lvl}"): 
                                update_inventory(lvl, -2); update_inventory(lvl+1, 1); st.toast("Success!", icon="✨"); st.rerun()
                        r = calculate_reward(lvl)
                        if st.button(f"🔒 (+{r:.4f})", key=f"kj_{lvl}"): 
                            update_inventory(lvl, -1); update_balance(r); record_profit(r); st.rerun()
                st.markdown("---")

# === 4. 명예의 전당 ===
with tabs[3]:
    st.subheader(T("rank_title"))
    st.caption(T("rank_desc"))
    with get_db() as conn:
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0), IFNULL(total_profit, 0.0), IFNULL(max_lvl, 0) FROM users ORDER BY max_lvl DESC, total_profit DESC LIMIT 10").fetchall()
    for i, (w, b, p, m) in enumerate(ranks):
        medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        st.markdown(f"<div class='card-box' style='padding:15px; text-align:left; display:flex; justify-content:space-between;'><span style='font-size:1.2em'>{medal} <span class='neon'>{w}</span></span><span style='text-align:right'><span class='red'>Lv.{m}</span> <span class='gold'>+{p:.4f} SOL</span></span></div>", unsafe_allow_html=True)
