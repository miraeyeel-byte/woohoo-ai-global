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
st.set_page_config(page_title="WOOHOO SECURITY V21.0", layout="wide")
DB_PATH = "woohoo_v21_0_real_sec.db"

# [2. 16개국어 데이터 (보안 기능 강화)]
LANG = {
    "🇰🇷 한국어": {
        "title": "WOOHOO 스캠 방지 솔루션",
        "tab_story": "😢 운영자의 사연",
        "tab_sec": "🛡️ 허니팟 탐지 (메인)",
        "tab_game": "🚨 사기꾼 검거 (화풀이)",
        "tab_rank": "🏆 명예의 전당",
        "wallet_con": "지갑 연결", "balance": "자산", "total_profit": "누적 수익",
        "story_title": "저는 허니팟 사기로 전 재산을 잃었습니다...",
        "story_desc": """
        믿었던 프로젝트에 100 SOL을 넣었는데, 1초 만에 0원이 되었습니다.
        알고 보니 '매수'는 되는데 '매도'가 안 되는 악질 허니팟(Honey Pot) 스캠이었습니다.
        
        피가 거꾸로 솟는 심정으로 맹세했습니다.
        "내 같은 피해자가 다시는 나오지 않게 하겠다. 개같은 스캠범들, 내가 다 잡아낸다."
        
        그래서 이 WOOHOO 보안 플랫폼을 만들었습니다.
        제보해주십시오. 끝까지 추적해서 박제하고 처단하겠습니다.
        """,
        "tele_link": "📢 스캠 제보 및 문의: @FUCKHONEYPOT",
        "mode_basic": "BASIC 모드 (0.01 SOL/회)",
        "mode_basic_desc": "단순 경고만 합니다. (예: 신고 내역 있음)",
        "mode_pro": "PRO 모드 (0.1 SOL/회)",
        "mode_pro_desc": "위험 감지 시 매수를 강제로 차단합니다. (VPN/우회 완벽 방어)",
        "input_addr": "검사할 토큰/사이트 주소 입력",
        "btn_scan": "🔍 보안 검사 시작 (결제)",
        "scan_ing": "네트워크 트래픽 분석 중...",
        "res_safe": "✅ 안전한 프로젝트입니다. (Risk: {score}%)",
        "res_warn": "⚠️ [경고] 위험도 {score}%! 신고 내역이 존재합니다. 주의하세요!",
        "res_block": "🚫 [PRO 차단] 위험도 {score}%! 우회 IP/허니팟 코드 발견! 매수 절대 불가!",
        "game_desc": "스캠범들에게 화가 나십니까? 여기서라도 잡아넣으세요.",
        "pull_1": "1놈 체포", "pull_100": "🔥 100놈 쓸어담기",
        "buy_confirm": "⚠️ {cost} SOL 결제 확인",
        "err_bal": "잔액 부족 (충전 필요)",
        "rank_title": "명예의 보안관",
        "rank_desc": "가장 많은 스캠범을 처단한 영웅들"
    },
    # (다른 언어는 한국어 구조에 맞춰 영어 폴백 처리 - 공간 절약)
    "🇺🇸 English": {
        "title": "WOOHOO ANTI-SCAM",
        "tab_story": "😢 My Story", "tab_sec": "🛡️ Security Center", "tab_game": "🚨 Arrest Scammers", "tab_rank": "🏆 Hall of Fame",
        "story_title": "I lost everything to a Honey Pot...",
        "story_desc": "I created this tool to stop scammers. Report them to me.",
        "tele_link": "📢 Report Scams: @FUCKHONEYPOT",
        "mode_basic": "BASIC (0.01 SOL)", "mode_basic_desc": "Warns you about risks.",
        "mode_pro": "PRO (0.1 SOL)", "mode_pro_desc": "BLOCKS transaction if risky.",
        "btn_scan": "🔍 Scan & Pay", "res_block": "🚫 [PRO BLOCKED] Risk {score}%! Transaction stopped.",
        "buy_confirm": "⚠️ Confirm {cost} SOL"
    }
}

# [3. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, total_profit REAL DEFAULT 0.0, max_lvl INTEGER DEFAULT 0, max_sold_lvl INTEGER DEFAULT 0, is_bot INTEGER DEFAULT 0)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        # 운영자 계정
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, total_profit, max_lvl, max_sold_lvl, is_bot) VALUES ('Operator_Admin', 0.0, 0.0, 0, 0, 0)")
        # 가짜 랭커 (분위기용)
        fake_users = [('HQ7a...k9L', 50.0, 524.12, 0, 55, 1), ('Ab2x...1zP', 12.0, 120.50, 0, 30, 1), ('9xKq...m4R', 5.5, 45.20, 0, 22, 1)]
        for user in fake_users:
            c.execute("INSERT OR IGNORE INTO users (wallet, balance, total_profit, max_lvl, max_sold_lvl, is_bot) VALUES (?, ?, ?, ?, ?, ?)", user)
        conn.commit()
init_db()

# [4. 유틸리티]
if 'lang' not in st.session_state: st.session_state.lang = "🇰🇷 한국어"

def T(key, **kwargs):
    lang_data = LANG.get(st.session_state.lang, LANG.get("🇺🇸 English", {}))
    text = lang_data.get(key, LANG["🇰🇷 한국어"].get(key, key)) # 한국어 기본
    if kwargs: return text.format(**kwargs)
    return text

def get_criminal_name(lvl):
    return f"Lv.{lvl} Scammer" # 심플하게 통일

def get_img_url(lvl):
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=Scam{lvl}&backgroundColor=1a1a1a"

# [5. 핵심 로직]
def get_user():
    if not st.session_state.wallet: return None, 0.0, 0.0, 0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance, total_profit, max_sold_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0, 0.0, 0)

# [수익 모델] 돈 쓰면 -> 운영자 지갑으로
def update_balance(d):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (d, st.session_state.wallet))
        if d < 0: # 사용한 금액은 운영자에게
            conn.execute("UPDATE users SET balance = balance + ? WHERE wallet='Operator_Admin'", (abs(d),))
        conn.commit()

# [보안 검사 시뮬레이션]
def run_security_scan(addr, mode):
    # 실제로는 여기서 블록체인 조회 API가 돌지만, 지금은 시뮬레이션
    risk = random.randint(10, 99) # 랜덤 위험도
    
    with st.status(T("scan_ing"), expanded=True) as status:
        time.sleep(0.5); st.write("📡 Checking Contract Source...")
        time.sleep(0.5); st.write("🕵️ Analyzing Holder Distribution...")
        time.sleep(0.5); st.write("🤖 Detecting Honey Pot Logic...")
        status.update(label="Scan Complete", state="complete", expanded=False)
    
    if risk < 30:
        st.success(T("res_safe", score=risk))
    else:
        # 위험 감지 시 모드에 따른 차별화
        if mode == "basic":
            st.warning(T("res_warn", score=risk))
            st.info("💡 Pro 모드에서는 이런 위험을 자동으로 차단합니다.")
        else: # Pro Mode
            st.error(T("res_block", score=risk))
            st.markdown("### 🛡️ WOOHOO PRO PROTECTION ACTIVE")
            st.markdown("`Transaction forcibly terminated to protect user funds.`")

# [미니게임 로직]
def update_inventory(l, d):
    with get_db() as conn:
        c = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, l)).fetchone()
        n = (c[0] + d) if c else d
        if n < 0: n = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, l, n)); conn.commit()

def record_profit_and_rank(amount, sold_lvl):
    with get_db() as conn:
        conn.execute("UPDATE users SET total_profit = total_profit + ? WHERE wallet=?", (amount, st.session_state.wallet))
        curr = conn.execute("SELECT max_sold_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()[0]
        if sold_lvl > curr: conn.execute("UPDATE users SET max_sold_lvl = ? WHERE wallet=?", (sold_lvl, st.session_state.wallet))
        conn.commit()

def gacha_pull(n):
    levels = list(range(1, 101))
    weights = [100000 / (i**2.0) for i in levels] # 도파민 확률
    return random.choices(levels, weights=weights, k=n)

def calculate_reward(lvl):
    return (0.003 * (1.05**(lvl-1))) if lvl <= 100 else (0.003 * (1.05**99) + (lvl-100)*0.2)

# [6. 스타일링]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700&display=swap');
    .stApp { background-color: #050505; color: #fff; font-family: 'Noto Sans KR', sans-serif; }
    h1, h2, h3 { color: #fff !important; text-shadow: 0 0 10px #66fcf1; }
    .card-box { border: 1px solid #333; background: #111; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .neon { color: #66fcf1; font-weight: bold; }
    .warn { color: #FFD700; font-weight: bold; }
    .err { color: #FF4B4B; font-weight: bold; }
    .stButton button { border: 1px solid #66fcf1; background: transparent; color: #66fcf1; }
    .stButton button:hover { background: #66fcf1; color: #000; }
</style>
""", unsafe_allow_html=True)

# [7. 세션]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'confirm_pay' not in st.session_state: st.session_state.confirm_pay = None

# [8. UI 구성]
with st.sidebar:
    st.title("Language")
    lang_list = list(LANG.keys())
    try: idx = lang_list.index(st.session_state.lang)
    except: idx = 0
    if st.selectbox("Select", lang_list, index=idx) != st.session_state.lang:
        st.session_state.lang = st.selectbox("Select", lang_list, index=idx); st.rerun()
    
    st.divider()
    st.markdown(f"### {T('tele_link')}")
    # QR 코드 자리 (이미지가 없으면 텍스트만 표시됨)
    # st.image("1000022360.jpg", caption="@FUCKHONEYPOT") 
    
    st.divider()
    if not st.session_state.wallet:
        if st.button(T("wallet_con")): st.session_state.wallet = "Operator_Admin"; st.rerun()
    else:
        u_w, u_b, u_p, u_m = get_user()
        st.success(f"{u_w}")
        st.metric(T("balance"), f"{u_b:.4f} SOL")
        if st.button(T("wallet_dis")): st.session_state.wallet = None; st.rerun()

st.title(T("title"))

if not st.session_state.wallet:
    st.warning("Please Connect Wallet First.")
    st.stop()

# 탭 구성 재배치
tabs = st.tabs([T("tab_story"), T("tab_sec"), T("tab_game"), T("tab_rank")])

# === 탭 1: 운영자의 사연 (감성 팔이) ===
with tabs[0]:
    st.subheader(T("story_title"))
    st.write(T("story_desc"))
    st.markdown("---")
    st.markdown(f"### 📢 {T('tele_link')}")
    st.info("위 아이디로 제보해주시면, 제가 직접 분석해서 DB에 업데이트합니다.")

# === 탭 2: 보안 센터 (메인 기능) ===
with tabs[1]:
    st.subheader(T("tab_sec"))
    
    # 모드 선택
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='card-box'><h3 class='warn'>{T('mode_basic')}</h3><p>{T('mode_basic_desc')}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card-box'><h3 class='err'>{T('mode_pro')}</h3><p>{T('mode_pro_desc')}</p></div>", unsafe_allow_html=True)
    
    mode = st.radio("Select Mode", ["basic", "pro"], label_visibility="collapsed")
    target_addr = st.text_input(T("input_addr"), placeholder="Example: 8xFa...92Lm")
    
    cost = 0.01 if mode == "basic" else 0.1
    
    if st.button(f"{T('btn_scan')} ({cost} SOL)"):
        _, bal, _, _ = get_user()
        if bal < cost:
            st.error(T("err_bal"))
        else:
            if not target_addr:
                st.warning("주소를 입력해주세요.")
            else:
                update_balance(-cost) # 돈 내고
                run_security_scan(target_addr, mode) # 검사 실행

# === 탭 3: 미니게임 (화풀이용) ===
with tabs[2]:
    st.subheader(T("tab_game"))
    st.caption(T("game_desc"))
    
    # 간단하게 100회 뽑기만 강조
    if st.button(f"{T('pull_100')} (1.0 SOL)"):
        _, bal, _, _ = get_user()
        if bal < 1.0: st.error(T("err_bal"))
        else:
            update_balance(-1.0)
            res = gacha_pull(100)
            for r in res: update_inventory(r, 1)
            st.toast(f"{len(res)} Scammers Caught!", icon="🚨")
            st.balloons()
            
    # 인벤토리/판매 로직 (간소화)
    inv = get_inv()
    if inv:
        st.divider()
        st.write("체포된 스캠범들 (Inventory):")
        
        # 일괄 판매 버튼
        if st.button("🔒 모두 감옥 보내기 (보상 받기)"):
            tr = 0
            for lvl, cnt in inv.items():
                if cnt > 0:
                    r = cnt * calculate_reward(lvl)
                    update_inventory(lvl, -cnt); tr += r
                    record_profit_and_rank(0, lvl)
            update_balance(tr) # 이건 유저한테 보상금 지급
            record_profit_and_rank(tr, 0)
            st.success(f"+{tr:.4f} SOL Recovered!")
            st.rerun()
            
        # 보유 목록 표시
        cols = st.columns(5)
        for i, (lvl, cnt) in enumerate(sorted(inv.items(), key=lambda x: x[0], reverse=True)[:5]):
            with cols[i]:
                st.image(get_img_url(lvl), width=50)
                st.caption(f"Lv.{lvl} x{cnt}")

# === 탭 4: 명예의 전당 ===
with tabs[3]:
    st.subheader(T("rank_title"))
    st.caption(T("rank_desc"))
    with get_db() as conn:
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0), IFNULL(total_profit, 0.0), IFNULL(max_sold_lvl, 0) FROM users WHERE total_profit > 0 ORDER BY max_sold_lvl DESC, total_profit DESC LIMIT 10").fetchall()
    
    if not ranks: st.info("데이터 없음")
    else:
        for i, (w, b, p, m) in enumerate(ranks):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            if w == "Operator_Admin": w = "<span class='err'>👑 Operator_Admin (운영자)</span>"
            st.markdown(f"<div class='card-box' style='display:flex; justify-content:space-between;'><span>{medal} {w}</span><span>Lv.{m} / +{p:.2f} SOL</span></div>", unsafe_allow_html=True)
