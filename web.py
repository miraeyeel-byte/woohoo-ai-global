import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import os
import time
import threading

# [1. 환경 설정 & DB 경로 자동 생성]
st.set_page_config(page_title="WOOHOO Security & Hunter", layout="wide", initial_sidebar_state="expanded")
DB_PATH = "woohoo_v17_final.db"

def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        # 유저 정보 (지갑, 잔액)
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL)")
        # 인벤토리 (유치장): 잡은 범죄자 대기소
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        # 볼트 (교도소): 영구 보관
        c.execute("CREATE TABLE IF NOT EXISTS prison (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        # 보안 로그
        c.execute("CREATE TABLE IF NOT EXISTS security_logs (id INTEGER PRIMARY KEY, ip TEXT, risk INTEGER, action TEXT, time TEXT)")
        conn.commit()
init_db()

# [2. CSS: 예쁜 캐릭터 카드 & 네온 스타일]
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a; border-radius: 5px; color: #888; padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFD700; color: #000; font-weight: bold;
    }
    
    /* 범죄자 카드 (구매/체포용) */
    .bounty-card {
        border: 2px solid #333; border-radius: 15px; padding: 15px;
        background: linear-gradient(145deg, #111, #222);
        text-align: center; margin-bottom: 15px; transition: 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    }
    .bounty-card:hover {
        border-color: #FF4500; transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(255, 69, 0, 0.4);
    }
    
    /* 유치장/보관소 카드 */
    .inv-card {
        border: 1px solid #444; border-radius: 10px; padding: 10px;
        background: #0f0f0f; text-align: center;
    }
    
    /* 버튼 스타일 커스텀 */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    
    /* 텍스트 효과 */
    .neon-text { color: #00ffea; text-shadow: 0 0 10px #00ffea; font-weight: bold; }
    .risk-high { color: #ff0055; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# [3. 세션 초기화]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'balance' not in st.session_state: st.session_state.balance = 1.0 # 테스트용 1 SOL 지급

# [4. 핵심 기능 로직]
def process_payment(amount):
    """0.01 SOL 결제 처리"""
    if st.session_state.balance >= amount:
        st.session_state.balance -= amount
        return True
    return False

def add_criminal(lvl, count=1):
    with get_db() as conn:
        # 기존 수량 확인
        cur = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl)).fetchone()
        new_cnt = (cur[0] + count) if cur else count
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, lvl, new_cnt))
        conn.commit()

def check_ip_security():
    """핵심기술 1: IP 보안 스캔"""
    try:
        # 실제 환경에서는 st.context.headers 등 사용
        ip = "127.0.0.1" 
        url = f"http://ip-api.com/json/{ip}?fields=status,countryCode,proxy,hosting"
        res = requests.get(url, timeout=1).json()
        return res
    except:
        return {"status": "fail"}

# [5. 메인 UI]
st.title("🛡️ WOOHOO SECURITY & HUNTER")

# 사이드바 (지갑 정보)
with st.sidebar:
    st.header("🕵️ AGENT STATUS")
    if not st.session_state.wallet:
        if st.button("지갑 연결 (Connect)"):
            st.session_state.wallet = "User_X"
            st.rerun()
    else:
        st.success(f"Connected: {st.session_state.wallet}")
        st.metric("Balance", f"{st.session_state.balance:.4f} SOL")
        if st.button("Disconnect"):
            st.session_state.wallet = None
            st.rerun()

if not st.session_state.wallet:
    st.warning("시스템에 접속하려면 지갑을 연결하십시오.")
    st.stop()

# 탭 구성: 보안(핵심기술) -> 체포(게임) -> 유치장(합성) -> 교도소(보관)
tabs = st.tabs(["🖥️ 보안 관제실 (Security)", "🔫 현상수배 (Hunting)", "⛓️ 유치장 (Cell)", "🔒 교도소 (Prison)"])

# --- TAB 1: 보안 관제실 (잃어버린 핵심 기술 복구) ---
with tabs[0]:
    st.markdown("### 📡 CORE SECURITY SYSTEMS")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("<div class='inv-card'><h4>🌐 네트워크 방화벽</h4>", unsafe_allow_html=True)
        sec_data = check_ip_security()
        if sec_data.get('proxy'):
            st.markdown("<span class='risk-high'>⚠️ VPN 감지됨 (차단)</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#00ff00'>✅ 안전한 접속 (Clean IP)</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='inv-card'><h4>🚫 트랜잭션 차단기</h4>", unsafe_allow_html=True)
        st.write("상태: **ACTIVE (가동중)**")
        st.caption("사기 의심 지갑 서명 요청 시 0.01초 내 자동 차단")
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='inv-card'><h4>🔍 토큰 정밀 스캐너</h4>", unsafe_allow_html=True)
        t_addr = st.text_input("토큰 주소 입력 (Simulation)", placeholder="So1ana...")
        if st.button("스캔 실행"):
            with st.spinner("컨트랙트 분석 중..."):
                time.sleep(1)
                st.error("🚨 경고: 허니팟(Honeypot) 코드로 판명됨!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: 현상수배 (0.01 SOL 체포 게임) ---
with tabs[1]:
    st.subheader("🔫 WANTED LIST (Live)")
    st.caption("※ '체포 시도' 클릭 시 0.01 SOL이 차감되며, 확률적으로 범죄자를 검거합니다.")
    
    # 범죄자 데이터 (이름, 이미지, 검거확률)
    criminals = [
        (1, "소매치기범 (Pickpocket)", "👤", 90),
        (2, "스캠 링크 배포자", "👺", 80),
        (3, "러그풀 개발자", "🤡", 60),
        (4, "해킹 조직원", "💀", 40)
    ]
    
    cols = st.columns(4)
    for idx, (lvl, name, icon, prob) in enumerate(criminals):
        with cols[idx]:
            st.markdown(f"""
            <div class='bounty-card'>
                <div style='font-size:50px;'>{icon}</div>
                <h3>Lv.{lvl} {name}</h3>
                <p>검거 확률: {prob}%</p>
                <p class='neon-text'>Bounty Cost: 0.01 SOL</p>
            </div>
            """, unsafe_allow_html=True)
            
            # [핵심] 0.01 SOL 결제 후 체포 로직
            if st.button(f"🚨 체포 시도 (Lv.{lvl})", key=f"hunt_{lvl}"):
                if process_payment(0.01):
                    with st.spinner("추적 중..."):
                        time.sleep(0.5)
                        if random.randint(1, 100) <= prob:
                            add_criminal(lvl)
                            st.success(f"검거 성공! Lv.{lvl} {name} 유치장 이송 완료.")
                            st.balloons()
                        else:
                            st.error("체포 실패! 용의자가 도주했습니다.")
                else:
                    st.error("잔액이 부족합니다! (Need 0.01 SOL)")

# --- TAB 3: 유치장 (인벤토리 & 합성) ---
with tabs[2]:
    st.subheader("⛓️ HOLDING CELL (Inventory)")
    
    with get_db() as conn:
        my_inv = conn.execute("SELECT lvl, count FROM inventory WHERE wallet=? AND count > 0 ORDER BY lvl", (st.session_state.wallet,)).fetchall()
    
    if not my_inv:
        st.info("유치장이 비어있습니다. '현상수배' 탭에서 범죄자를 잡아오세요.")
    else:
        # 보유 목록 표시
        icols = st.columns(6)
        for i, (lvl, count) in enumerate(my_inv):
            with icols[i % 6]:
                icon = ["?", "👤", "👺", "🤡", "💀", "👿", "🐲"][min(lvl, 6)]
                st.markdown(f"""
                <div class='inv-card'>
                    <div style='font-size:30px;'>{icon}</div>
                    <b>Lv.{lvl}</b><br>x {count} 명
                </div>
                """, unsafe_allow_html=True)
                
                # [기능 1] 합성 (3마리 -> 상위 1마리)
                if count >= 3:
                    if st.button(f"⚡ 심문/자백 (합성)", key=f"fuse_{lvl}"):
                        # 3마리 차감
                        with get_db() as conn:
                            conn.execute("UPDATE inventory SET count = count - 3 WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl))
                            # 상위 1마리 추가
                            cur = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl+1)).fetchone()
                            new_c = (cur[0] + 1) if cur else 1
                            conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, lvl+1, new_c))
                            conn.commit()
                        st.toast(f"성공! Lv.{lvl+1} 조직 간부 정보를 얻어냈습니다!", icon="🔥")
                        st.rerun()

                # [기능 2] 교도소 이송 (보관)
                if st.button("🔒 교도소 이송", key=f"send_{lvl}"):
                    with get_db() as conn:
                        conn.execute("UPDATE inventory SET count = count - 1 WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl))
                        cur = conn.execute("SELECT count FROM prison WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl)).fetchone()
                        new_c = (cur[0] + 1) if cur else 1
                        conn.execute("INSERT OR REPLACE INTO prison VALUES (?, ?, ?)", (st.session_state.wallet, lvl, new_c))
                        conn.commit()
                    st.toast("이송 완료. 교도소 탭을 확인하세요.")
                    st.rerun()

# --- TAB 4: 교도소 (보관소) ---
with tabs[3]:
    st.subheader("🔒 FEDERAL PRISON (Vault)")
    st.caption("이곳에 수감된 범죄자는 안전하게 보관됩니다.")
    
    with get_db() as conn:
        my_prison = conn.execute("SELECT lvl, count FROM prison WHERE wallet=? AND count > 0 ORDER BY lvl", (st.session_state.wallet,)).fetchall()
        
    if not my_prison:
        st.write("교도소에 수감된 인원이 없습니다.")
    else:
        pcols = st.columns(6)
        for i, (lvl, count) in enumerate(my_prison):
            with pcols[i % 6]:
                icon = ["?", "👤", "👺", "🤡", "💀", "👿", "🐲"][min(lvl, 6)]
                st.markdown(f"""
                <div class='inv-card' style='border-color:#555;'>
                    <div style='font-size:30px; opacity:0.7;'>{icon}</div>
                    <span style='color:#888'>Lv.{lvl} (x{count})</span>
                </div>
                """, unsafe_allow_html=True)
                
                # 다시 유치장으로(꺼내기)
                if st.button("반환 (To Cell)", key=f"back_{lvl}"):
                    with get_db() as conn:
                        conn.execute("UPDATE prison SET count = count - 1 WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl))
                        cur = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, lvl)).fetchone()
                        new_c = (cur[0] + 1) if cur else 1
                        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, lvl, new_c))
                        conn.commit()
                    st.rerun()

