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
st.set_page_config(page_title="WOOHOO SECURITY V19.0", layout="wide")
DB_PATH = "woohoo_v19_stable.db"

# [2. 16개국어 번역 팩]
LANG = {
    "🇰🇷 한국어": {
        "title": "WOOHOO 보안 플랫폼",
        "tab_sec": "🛡️ 보안 센터", "tab_game": "🚨 범인 체포", "tab_inv": "📦 보관함", "tab_rank": "🏆 명예의 전당",
        "wallet_con": "지갑 연결", "wallet_dis": "연결 해제", "balance": "자산", "max_lvl": "최고 기록",
        "sec_btn": "💰 매수 시도", "sec_warn": "주소를 입력하세요.", "sec_safe": "✅ 안전 (점수: {score})", "sec_danger": "🚨 [경고] 위험 점수 {score}!", "sec_block": "🚫 차단됨!",
        "game_desc": "비용을 지불하고 체포합니다. 운이 좋으면 고레벨 등장!", "pull_1": "1회 체포", "pull_5": "5회 체포", "pull_10": "10회 체포",
        "inv_empty": "보관함이 비어있습니다.", "fuse_all": "🧬 일괄 합성", "jail_all": "🔒 일괄 감옥",
        "btn_yes": "✅ 승인", "btn_no": "❌ 취소",
        "toast_catch": "{n}명 체포 완료!", "err_bal": "잔액이 부족합니다.",
        "fuse_confirm": "총 {n}회 합성을 진행합니까?", "jail_confirm": "모두 감옥으로 보내고 보상을 받겠습니까?",
        "toast_fuse": "일괄 합성 완료!", "toast_jail": "이송 완료! +{r:.4f} SOL",
        "rank_title": "명예의 전당", "rank_desc": "최고 레벨 범죄자를 검거한 헌터 순위",
        "name_1": "소매치기", "name_10": "양아치", "name_50": "조직 간부", "name_90": "테러리스트", "name_100": "세계관 최강자"
    },
    "🇺🇸 English": {
        "title": "WOOHOO SECURITY PLATFORM",
        "tab_sec": "🛡️ Security", "tab_game": "🚨 Arrest", "tab_inv": "📦 Inventory", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Connect Wallet", "wallet_dis": "Disconnect", "balance": "Balance", "max_lvl": "Max Level",
        "sec_btn": "💰 Buy (Sim)", "sec_warn": "Enter Address.", "sec_safe": "✅ Safe (Score: {score})", "sec_danger": "🚨 High Risk {score}!", "sec_block": "🚫 Blocked!",
        "game_desc": "Pay bounty to arrest criminals. Lucky drops enabled.", "pull_1": "Arrest x1", "pull_5": "Arrest x5", "pull_10": "Arrest x10",
        "inv_empty": "Inventory Empty.", "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "btn_yes": "✅ Yes", "btn_no": "❌ No",
        "toast_catch": "{n} Captured!", "err_bal": "Insufficient Balance.",
        "fuse_confirm": "Proceed with {n} fusions?", "jail_confirm": "Send all to prison?",
        "toast_fuse": "Fusion Complete!", "toast_jail": "Sent to Prison! +{r:.4f} SOL",
        "rank_title": "Hall of Fame", "rank_desc": "Top Hunters Ranking",
        "name_1": "Pickpocket", "name_10": "Thug", "name_50": "Gang Boss", "name_90": "Terrorist", "name_100": "Overlord"
    },
    # 나머지 언어는 공간상 영어로 폴백되거나 필요시 추가 가능 (코드 안정성을 위해 생략하나 기능은 작동)
}

# [3. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, max_lvl INTEGER DEFAULT 0)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, max_lvl) VALUES ('Operator_Admin', 10.0, 0)")
        conn.commit()
init_db()

# [4. 유틸리티 함수]
if 'lang' not in st.session_state: st.session_state.lang = "🇰🇷 한국어"

def T(key, **kwargs):
    # 언어가 없으면 영어로, 영어도 없으면 키값 그대로
    lang_dict = LANG.get(st.session_state.lang, LANG.get("🇺🇸 English", {}))
    text = lang_dict.get(key, LANG["🇰🇷 한국어"].get(key, key)) # 기본 한국어 폴백
    if kwargs:
        return text.format(**kwargs)
    return text

def get_criminal_name(lvl):
    prefix = f"Lv.{lvl} "
    if lvl == 1: name = T("name_1")
    elif lvl <= 10: name = T("name_10")
    elif lvl <= 50: name = T("name_50")
    elif lvl <= 90: name = T("name_90")
    else: name = T("name_100")
    return f"{prefix}{name}"

def get_img_url(lvl):
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=Crime{lvl}&backgroundColor=1a1a1a"

# [5. 보안 및 게임 로직]
def process_security_action(token_address, user_tier):
    risk_score = random.randint(0, 100)
    if user_tier.startswith("BASIC"):
        if risk_score >= 70:
            st.warning(T("sec_danger", score=risk_score)); return
    elif user_tier.startswith("PRO"):
        if risk_score >= 70:
            st.error(T("sec_block", score=risk_score)); return
    st.success(T("sec_safe", score=risk_score))

def get_user():
    if not st.session_state.wallet: return None, 0.0, 0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance, max_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0, 0)

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

def get_inv():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())

def gacha_pull(n):
    levels = list(range(1, 101))
    weights = [1000 / (i * i) for i in levels]
    return random.choices(levels, weights=weights, k=n)

# [6. 스타일링: 모범택시 레트로 감성]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Courier New', monospace; }
    h1, h2, h3 { color: #FFD700; text-shadow: 2px 2px 0px #000; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #222; border: 1px solid #444; color: #aaa; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; font-weight: bold; border: none; }
    
    .card-box {
        border: 2px solid #FFD700; background: #111;
        padding: 10px; border-radius: 0px; text-align: center; margin-bottom: 10px;
        box-shadow: 5px 5px 0px #333;
    }
    .neon { color: #66fcf1; font-weight: bold; }
    .gold { color: #FFD700; font-weight: bold; }
    .red { color: #ff4b4b; font-weight: bold; }
    
    /* 버튼 스타일: 레트로 게임 버튼 */
    .stButton button { 
        width: 100%; border-radius: 0px; font-weight: bold; 
        border: 2px solid #66fcf1; background: #000; color: #66fcf1;
    }
    .stButton button:hover {
        background: #66fcf1; color: #000;
    }
</style>
""", unsafe_allow_html=True)

# [7. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'user_tier' not in st.session_state: st.session_state.user_tier = "BASIC (0.01 SOL)"
if 'confirm_fuse_all' not in st.session_state: st.session_state.confirm_fuse_all = False
if 'confirm_jail_all' not in st.session_state: st.session_state.confirm_jail_all = False

# [8. 메인 UI]
# 사이드바
with st.sidebar:
    st.title("🌐 Language")
    # 전체 16개국어 리스트 (코드 길이상 핵심만 넣었으나 여기 선택지는 유지)
    lang_list = ["🇰🇷 한국어", "🇺🇸 English", "🇯🇵 日本語", "🇨🇳 中文", "🇷🇺 Русский", "🇻🇳 Tiếng Việt", "🇹🇭 ภาษาไทย", "🇮🇱 עברית", "🇵🇭 Tagalog", "🇲🇾 Melayu", "🇮🇩 Indonesia", "🇹🇷 Türkçe", "🇵🇹 Português", "🇪🇸 Español", "🇩🇪 Deutsch", "🇫🇷 Français"]
    
    # 선택된 인덱스 찾기 (안전장치 추가)
    try:
        idx = lang_list.index(st.session_state.lang)
    except:
        idx = 0
        
    selected_lang = st.selectbox("Select", lang_list, index=idx)
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()
    
    st.divider()
    st.header(f"🔐 {T('wallet_con')}")
    if not st.session_state.wallet:
        if st.button(T("wallet_con"), key="btn_connect"): 
            st.session_state.wallet = "Operator_Admin"; st.rerun()
    else:
        u_wallet, u_bal, u_max = get_user()
        st.success(f"User: {u_wallet}")
        st.metric(T("balance"), f"{u_bal:.4f} SOL")
        st.metric(T("max_lvl"), f"Lv.{u_max}")
        if st.button(T("wallet_dis"), key="btn_disconnect"): 
            st.session_state.wallet = None; st.rerun()

st.title(T("title"))

if not st.session_state.wallet:
    st.info("Wallet Connect Required.")
    st.stop()

tabs = st.tabs([T("tab_sec"), T("tab_game"), T("tab_inv"), T("tab_rank")])

# === 1. 보안 센터 ===
with tabs[0]:
    st.subheader(T("tab_sec"))
    st.markdown("**Tier:**")
    tier = st.radio("Level", ["BASIC (0.01 SOL)", "PRO (0.1 SOL)"])
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
        _, bal, _ = get_user()
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
        if st.button(f"{T('pull_1')} (0.01 SOL)", key="btn_pull_1"): run_gacha(0.01, 1)
    with c2: 
        if st.button(f"{T('pull_5')} (0.05 SOL)", key="btn_pull_5"): run_gacha(0.05, 5)
    with c3: 
        if st.button(f"{T('pull_10')} (0.10 SOL)", key="btn_pull_10"): run_gacha(0.10, 10)

# === 3. 보관함 ===
with tabs[2]:
    st.subheader(T("tab_inv"))
    inv = get_inv()
    if inv:
        bc1, bc2 = st.columns(2)
        total_fusions = sum([cnt // 2 for lvl, cnt in inv.items() if lvl < 100])
        
        with bc1:
            if not st.session_state.confirm_fuse_all:
                if st.button(f"{T('fuse_all')} ({total_fusions})", type="primary", disabled=total_fusions==0, key="btn_fuse_main"):
                    st.session_state.confirm_fuse_all = True; st.rerun()
            else:
                st.warning(T("fuse_confirm", n=total_fusions))
                c_y, c_n = st.columns(2)
                if c_y.button(T("btn_yes"), key="btn_fuse_yes"):
                    for lvl in sorted(inv.keys()):
                        f_cnt = inv[lvl] // 2
                        if f_cnt > 0 and lvl < 100: update_inventory(lvl, -(f_cnt*2)); update_inventory(lvl+1, f_cnt)
                    st.toast(T("toast_fuse"), icon="🧬"); st.session_state.confirm_fuse_all = False; st.rerun()
                if c_n.button(T("btn_no"), key="btn_fuse_no"):
                    st.session_state.confirm_fuse_all = False; st.rerun()
                    
        with bc2:
            if not st.session_state.confirm_jail_all:
                if st.button(T("jail_all"), key="btn_jail_main"): st.session_state.confirm_jail_all = True; st.rerun()
            else:
                st.warning(T("jail_confirm"))
                c_y, c_n = st.columns(2)
                if c_y.button(T("btn_yes"), key="btn_jail_yes"):
                    tr = 0
                    for lvl, cnt in inv.items():
                        if cnt > 0:
                            r = cnt * (0.005 * (1.1**(lvl-1)))
                            update_inventory(lvl, -cnt); tr += r
                    update_balance(tr); st.toast(T("toast_jail", r=tr), icon="💰"); st.session_state.confirm_jail_all = False; st.rerun()
                if c_n.button(T("btn_no"), key="btn_jail_no"):
                    st.session_state.confirm_jail_all = False; st.rerun()

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
                        if count >= 2 and lvl < 100:
                            if st.button(f"🧬 (2->1)", key=f"f_{lvl}"): update_inventory(lvl, -2); update_inventory(lvl+1, 1); st.toast("Success!", icon="✨"); st.rerun()
                        r = 0.005 * (1.1**(lvl-1))
                        # [중요] Duplicate Element ID 에러 해결: 키값에 'j_' + 레벨을 붙여 고유하게 만듦
                        if st.button(f"🔒 (+{r:.4f})", key=f"j_{lvl}"): update_inventory(lvl, -1); update_balance(r); st.rerun()
                st.markdown("---")

# === 4. 명예의 전당 ===
with tabs[3]:
    st.subheader(T("tab_rank"))
    with get_db() as conn:
        # [중요] IFNULL 처리로 TypeError 방지
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0), IFNULL(max_lvl, 0) FROM users ORDER BY max_lvl DESC, balance DESC LIMIT 10").fetchall()
    for i, (w, b, m) in enumerate(ranks):
        medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        st.markdown(f"<div class='card-box' style='padding:15px; text-align:left; display:flex; justify-content:space-between;'><span style='font-size:1.2em'>{medal} <span class='neon'>{w}</span></span><span style='text-align:right'><span class='red'>Lv.{m}</span> <span class='gold'>{b:.4f} SOL</span></span></div>", unsafe_allow_html=True)
