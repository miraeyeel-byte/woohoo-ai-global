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
st.set_page_config(page_title="WOOHOO DARK JUSTICE V18.4", layout="wide")
DB_PATH = "woohoo_v18_final_real.db"

# [2. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        # 감옥 로그 (누가, 언제, 누구를, 얼마에)
        c.execute("CREATE TABLE IF NOT EXISTS prison_log (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, lvl INTEGER, reward REAL, time_str TEXT)")
        # 운영자 계정
        c.execute("INSERT OR IGNORE INTO users VALUES ('Operator_Admin', 10.0)")
        conn.commit()

# [3. 가라 데이터(Social Proof) 주작 엔진]
def inject_fake_data():
    """사이트가 활발해 보이도록 가짜 로그를 심습니다."""
    with get_db() as conn:
        # 이미 데이터가 많으면 패스
        cnt = conn.execute("SELECT COUNT(*) FROM prison_log").fetchone()[0]
        if cnt < 5:
            fake_wallets = ["DeGod_Sol", "PhantomUser_99", "Whale_Hunter", "Solana_Sniper", "Degen_King", "Rich_Cat", "Elon_Musk_Sol"]
            
            for _ in range(15): # 15개 정도 주작 데이터 생성
                f_wallet = random.choice(fake_wallets)
                f_lvl = random.choices(range(1, 15), weights=[50,30,20,10,5,3,2,1,0.5,0.3,0.2,0.1,0.05,0.01])[0]
                f_reward = 0.005 * (1.2**(f_lvl-1))
                # 시간: 현재로부터 1분~60분 전 랜덤
                m_ago = random.randint(1, 60)
                f_time = (datetime.now() - timedelta(minutes=m_ago)).strftime("%Y-%m-%d %H:%M:%S")
                
                conn.execute("INSERT INTO prison_log (wallet, lvl, reward, time_str) VALUES (?, ?, ?, ?)", 
                             (f_wallet, f_lvl, f_reward, f_time))
            conn.commit()

init_db()
inject_fake_data() # 실행 시 가짜 데이터 주입

# [4. CSS 스타일링: NFT 스타일 & 네온]
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #111; border: 1px solid #333; color: #888; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; border: none; font-weight: bold; }

    /* 카드 스타일 (NFT 느낌) */
    .nft-card {
        background: #111; border: 1px solid #333; border-radius: 12px;
        padding: 15px; text-align: center; margin-bottom: 10px;
        transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .nft-card:hover { border-color: #66fcf1; transform: scale(1.02); box-shadow: 0 0 15px rgba(102, 252, 241, 0.3); }
    
    /* 라이브 티커 (최근 활동) */
    .live-ticker {
        background: #0f1115; border-left: 3px solid #FFD700;
        padding: 10px; margin-bottom: 5px; font-size: 0.9em;
    }
    
    /* 텍스트 강조 */
    .gold { color: #FFD700; font-weight: bold; }
    .neon { color: #66fcf1; font-weight: bold; }
    .red { color: #ff4b4b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# [5. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None

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

def log_prison_event(lvl, reward):
    """감옥 기록 저장 (유저용)"""
    with get_db() as conn:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO prison_log (wallet, lvl, reward, time_str) VALUES (?, ?, ?, ?)", 
                     (st.session_state.wallet, lvl, reward, now_str))
        conn.commit()

# [범죄자 이름 및 NFT 이미지 시드]
# DiceBear API를 사용하여 매번 고퀄리티 로봇/에일리언 이미지를 가져옴
CRIMINALS_META = {
    1: "좀도둑", 2: "스캠 링크 배포자", 3: "러그풀러", 4: "해커", 5: "봇 마스터",
    6: "작전 세력", 7: "다단계 왕", 8: "신원 도용범", 9: "AI 사기꾼", 10: "금융 테러리스트",
    11: "흡혈 고래", 12: "좀비 지갑", 13: "유령 CEO", 14: "악마 계약자", 15: "가짜 유니콘",
    16: "폰지 설계자", 17: "흑마법사", 18: "타락 영웅", 19: "사기 공화국 왕", 20: "우주적 존재"
}

def get_img_url(lvl):
    # 레벨별로 다른 시드(Seed)를 써서 이미지가 고정되지만 유니크하게 나옴
    # bottts (로봇) 스타일 사용 -> 크립토 느낌 물씬
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=CrimeLevel{lvl}&backgroundColor=b6e3f4,c0aede,d1d4f9"

def gacha(times):
    # 레벨 9가 4번만에 나온건 기적. 확률 조정 (고레벨 극악)
    weights = [5000, 3000, 1500, 800, 400, 200, 100, 50, 25, 10, 5, 3, 2, 1, 0.5, 0.3, 0.2, 0.1, 0.05, 0.01]
    levels = list(range(1, 21))
    return random.choices(levels, weights=weights, k=times)

# [7. 메인 화면]
st.title("🚓 WOOHOO DARK JUSTICE")

# [실시간 활동 로그 (주작된 데이터 포함)]
with get_db() as conn:
    # 최신 5개만 가져옴
    recent_logs = conn.execute("SELECT wallet, lvl, reward, time_str FROM prison_log ORDER BY id DESC LIMIT 5").fetchall()

if recent_logs:
    st.markdown("##### 🔥 LIVE PRISON FEED")
    # 전광판처럼 흐르게 하거나 리스트로 표시
    for w, l, r, t in recent_logs:
        # 시간 계산 (몇 분 전)
        try:
            log_time = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            diff = datetime.now() - log_time
            mins = int(diff.total_seconds() / 60)
            if mins == 0: time_txt = "방금 전"
            else: time_txt = f"{mins}분 전"
        except: time_txt = "방금 전"
        
        st.markdown(f"""
        <div class='live-ticker'>
            <span class='neon'>[{time_txt}]</span> 
            <b>{w[:10]}...</b> 님이 
            <span class='red'>Lv.{l}</span> 범죄자를 감옥에 처넣고 
            <span class='gold'>+{r:.4f} SOL</span> 획득!
        </div>
        """, unsafe_allow_html=True)

st.divider()

# 사이드바
with st.sidebar:
    if not st.session_state.wallet:
        if st.button("🔌 지갑 연결"):
            st.session_state.wallet = "Operator_Admin"
            st.rerun()
    else:
        u_wallet, u_bal = get_user()
        st.info(f"Connected: {u_wallet}")
        st.metric("My Balance", f"{u_bal:.4f} SOL")
        if st.button("Logout"):
            st.session_state.wallet = None
            st.rerun()

if not st.session_state.wallet:
    st.warning("지갑을 연결해야 접속 가능합니다.")
    st.stop()

# 탭
tabs = st.tabs(["🛡️ 보안 센터", "🎰 범인 뽑기 (Gacha)", "📦 보관함 (관리/합성)", "🏆 명예의 전당"])

# --- 1. 보안 센터 ---
with tabs[0]:
    st.subheader("📡 Security Scanner")
    c1, c2 = st.columns([3, 1])
    token = c1.text_input("토큰 주소 입력", placeholder="So1ana...")
    if c2.button("🔍 스캔"):
        with st.spinner("분석 중..."):
            time.sleep(1)
            st.error("⚠️ 위험 감지! (Simulation)")

# --- 2. 범인 뽑기 (이미지 개선) ---
with tabs[1]:
    st.subheader("🎰 CRIMINAL GACHA")
    st.caption("비용을 지불하고 범죄자를 체포(소환)합니다. **실패는 없습니다.**")
    
    col1, col2, col3 = st.columns(3)
    
    def run_gacha(cost, n):
        _, bal = get_user()
        if bal >= cost:
            update_balance(-cost)
            res = gacha(n)
            
            # 인벤토리 추가
            for r in res: update_inventory(r, 1)
            
            # 결과 보여주기 (토스트 + 이미지)
            st.toast(f"{n}명 체포 완료!", icon="🚨")
            
            # 결과 카드 표시
            st.write("### 🚨 체포 결과")
            r_cols = st.columns(min(n, 5)) # 최대 5열
            for idx, lvl in enumerate(res):
                # 5개 넘어가면 줄바꿈 처리는 복잡하니 일단 상위 5개만 크게 보여줌
                if idx < 5:
                    with r_cols[idx]:
                        img = get_img_url(lvl)
                        name = CRIMINALS_META.get(lvl, "Unknown")
                        st.markdown(f"""
                        <div class='nft-card'>
                            <img src='{img}' width='100%'>
                            <div style='margin-top:5px; font-weight:bold;'>Lv.{lvl} {name}</div>
                        </div>
                        """, unsafe_allow_html=True)
            if n > 5: st.write(f"...외 {n-5}명 추가 체포됨")
            
        else:
            st.error("잔액 부족!")

    with col1:
        st.markdown("<h4 class='neon'>1회 체포</h4><h5 class='gold'>0.01 SOL</h5>", unsafe_allow_html=True)
        if st.button("🚨 1회 뽑기"): run_gacha(0.01, 1)
        
    with col2:
        st.markdown("<h4 class='neon'>5회 체포</h4><h5 class='gold'>0.05 SOL</h5>", unsafe_allow_html=True)
        if st.button("🚨 5회 뽑기"): run_gacha(0.05, 5)

    with col3:
        st.markdown("<h4 class='neon'>10회 체포</h4><h5 class='gold'>0.10 SOL</h5>", unsafe_allow_html=True)
        if st.button("🚨 10회 뽑기"): run_gacha(0.10, 10)

# --- 3. 보관함 (합성/감옥) ---
with tabs[2]:
    st.subheader("📦 Inventory")
    inv = get_inventory()
    
    if not inv:
        st.info("보관함이 비어있습니다.")
    else:
        # 그리드 표시
        keys = sorted([k for k, v in inv.items() if v > 0])
        for lvl in keys:
            count = inv[lvl]
            name = CRIMINALS_META.get(lvl, "Unknown")
            img = get_img_url(lvl)
            
            with st.container():
                c_img, c_info, c_act = st.columns([1, 2, 3])
                
                with c_img:
                    st.markdown(f"<img src='{img}' style='border-radius:10px; width:80px;'>", unsafe_allow_html=True)
                
                with c_info:
                    st.markdown(f"#### Lv.{lvl} {name}")
                    st.markdown(f"수량: <span class='neon'>{count}</span> 명", unsafe_allow_html=True)
                
                with c_act:
                    c_a1, c_a2 = st.columns(2)
                    # 합성
                    if count >= 2 and lvl < 20:
                        if c_a1.button(f"🧬 합성 (2->1)", key=f"fuse_{lvl}"):
                            # 90% 성공
                            if random.random() < 0.9:
                                update_inventory(lvl, -2)
                                update_inventory(lvl+1, 1)
                                st.toast(f"합성 성공! Lv.{lvl+1} 획득", icon="✨")
                            else:
                                update_inventory(lvl, -1)
                                st.error("합성 실패... 1명 도주")
                            st.rerun()
                    else:
                        c_a1.button("합성 불가", disabled=True, key=f"d_f_{lvl}")
                    
                    # 감옥 (판매)
                    # 1레벨 판매가 0.005 (구매가의 절반) -> 운영자 이득 구조
                    sell_price = 0.005 * (1.3**(lvl-1))
                    if c_a2.button(f"🔒 감옥 (+{sell_price:.4f})", key=f"jail_{lvl}"):
                        update_inventory(lvl, -1)
                        update_balance(sell_price)
                        log_prison_event(lvl, sell_price) # 로그 저장
                        st.toast(f"감옥 이송 완료! +{sell_price:.4f} SOL", icon="💰")
                        st.rerun()
                st.markdown("---")

# --- 4. 명예의 전당 (수정됨: 많이 잡은 순) ---
with tabs[3]:
    st.subheader("🏆 Hall of Fame")
    st.caption("누가 가장 많은 범죄자를 감옥에 처넣었는가? (수익금 및 횟수 기준)")
    
    with get_db() as conn:
        # prison_log 테이블에서 집계 (지갑별 총 수익, 총 횟수)
        ranks = conn.execute("""
            SELECT wallet, SUM(reward) as total_earned, COUNT(*) as jailed_count
            FROM prison_log
            GROUP BY wallet
            ORDER BY total_earned DESC
            LIMIT 10
        """).fetchall()
    
    if ranks:
        for i, (w, earned, cnt) in enumerate(ranks):
            # 1,2,3등은 이모지 다르게
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            st.markdown(f"""
            <div class='card-box' style='padding:10px; text-align:left; display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span style='font-size:1.2em; margin-right:10px;'>{medal}</span>
                    <span class='neon'>{w}</span>
                </div>
                <div style='text-align:right;'>
                    <div class='gold'>{earned:.4f} SOL</div>
                    <div style='font-size:0.8em; color:#888;'>총 {cnt}명 수감</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("아직 데이터가 없습니다.")

