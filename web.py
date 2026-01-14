import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import os
import time
import threading

# [1. 환경 설정]
st.set_page_config(page_title="WOOHOO RPG COMMANDER", layout="wide")

# [에러 수정 1 & 4] DB 경로를 가장 안전한 현재 위치로 설정
DB_PATH = "woohoo_v17_final.db"

# [2. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, content TEXT, time TEXT)")
        # 초기 운영자 계정 생성 (테스트용 자금 지급)
        c.execute("INSERT OR IGNORE INTO users VALUES ('Operator', 10.0)")
        conn.commit()
init_db()

# [3. 스타일링 (RPG 다크 테마 & 네온)]
st.markdown("""
<style>
    .stApp { background-color: #0b0c10; color: #c5c6c7; }
    
    /* 유닛 카드 스타일 */
    .unit-card {
        border: 2px solid #45a29e; border-radius: 10px; padding: 10px;
        background: #1f2833; text-align: center; cursor: pointer;
        transition: 0.3s; margin-bottom: 10px;
    }
    .unit-card:hover {
        border-color: #66fcf1; box-shadow: 0 0 15px #66fcf1; transform: scale(1.02);
    }
    .unit-selected {
        border: 3px solid #FFD700 !important; background: #2b3e50 !important;
        box-shadow: 0 0 20px #FFD700;
    }
    
    /* 하단 커맨드 패널 */
    .command-console {
        background-color: #111; border-top: 3px solid #66fcf1;
        padding: 20px; border-radius: 15px 15px 0 0;
        margin-top: 20px; box-shadow: 0 -5px 20px rgba(0,0,0,0.8);
    }
</style>
""", unsafe_allow_html=True)

# [4. 세션 상태]
if 'wallet' not in st.session_state: st.session_state.wallet = "Operator" 
if 'selected_lvl' not in st.session_state: st.session_state.selected_lvl = None
if 'confirm_buy' not in st.session_state: st.session_state.confirm_buy = False

# [5. 핵심 로직]
def get_balance():
    with get_db() as conn:
        res = conn.execute("SELECT balance FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return res[0] if res else 0.0

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
        new_cnt = (cur[0] + delta) if cur else delta
        if new_cnt < 0: new_cnt = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, lvl, new_cnt))
        conn.commit()

# [에러 수정 2] IP API URL 오타 수정 (중괄호 제거)
def check_ip_security():
    try:
        ip = "127.0.0.1"
        url = f"http://ip-api.com/json/{ip}?fields=status,countryCode,proxy,hosting"
        return requests.get(url, timeout=1).json()
    except:
        return {}

# [6. 메인 UI]
st.title("⚔️ WOOHOO RPG COMMANDER")

# 상단 상태바
bal = get_balance()
c1, c2, c3 = st.columns([2, 1, 1])
c1.metric("OPERATOR WALLET", st.session_state.wallet)
c2.metric("ASSETS (SOL)", f"{bal:.4f}")
c3.metric("DEFCON", "LEVEL 1")

# 탭 구성
tabs = st.tabs(["🎮 COMMAND CENTER", "🏆 HALL OF FAME", "🕵️ INTELLIGENCE"])

# --- TAB 1: COMMAND CENTER (RPG 메인) ---
with tabs[0]:
    st.subheader("🛑 UNIT CONTROLLER")
    inv = get_inventory()
    
    # 유닛 그리드
    cols = st.columns(6)
    for i in range(1, 19): # 1~18레벨
        count = inv.get(i, 0)
        with cols[(i-1)%6]:
            border_cls = "unit-selected" if st.session_state.selected_lvl == i else "unit-card"
            img_icon = ["👤", "👺", "🤡", "💀", "👾", "🐉", "👹", "👽"][min(i-1, 7)]
            
            st.markdown(f"""
            <div class='{border_cls}'>
                <div style='font-size:30px;'>{img_icon}</div>
                <div><b>Lv.{i} Criminal</b></div>
                <div style='color:#66fcf1'>x {count}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"SELECT Lv.{i}", key=f"sel_{i}", use_container_width=True):
                st.session_state.selected_lvl = i
                st.session_state.confirm_buy = False
                st.rerun()

    # 하단 커맨드 콘솔
    st.markdown("<div class='command-console'>", unsafe_allow_html=True)
    
    if st.session_state.selected_lvl:
        slvl = st.session_state.selected_lvl
        scount = inv.get(slvl, 0)
        
        col_l, col_m, col_r = st.columns([1, 2, 1])
        
        with col_l:
            st.markdown(f"### 🎯 TARGET: Lv.{slvl}")
            st.write(f"보유 수량: **{scount}** 명")
            
        with col_m:
            # [기능 A] 레벨 1 구매
            if slvl == 1:
                st.info("💡 Lv.1은 [0.01 SOL]로 즉시 구매(체포) 가능")
                if not st.session_state.confirm_buy:
                    if st.button("🚨 체포 작전 개시 (구매)", key="buy_init"):
                        st.session_state.confirm_buy = True
                        st.rerun()
                else:
                    st.warning("⚠️ 0.01 SOL이 소모됩니다. 승인하시겠습니까?")
                    b1, b2 = st.columns(2)
                    if b1.button("✅ 승인"):
                        if bal >= 0.01:
                            update_balance(-0.01)
                            update_inventory(1, 1)
                            st.session_state.confirm_buy = False
                            st.toast("체포 성공!", icon="🚔")
                            st.rerun()
                        else: st.error("자금 부족!")
                    if b2.button("❌ 취소"):
                        st.session_state.confirm_buy = False
                        st.rerun()
            else:
                st.info("🔒 상위 레벨은 구매 불가. 오직 [합성]으로만 획득 가능.")

            # [기능 B] 합성 (2 -> 1)
            st.markdown("---")
            if scount >= 2:
                st.write(f"🧬 **Lv.{slvl} (2명)** ➡️ **Lv.{slvl+1} (1명)** 합성")
                if st.button(f"⚡ 합성 실행 (Fusion)"):
                    if random.random() < 0.9: # 90% 성공률
                        update_inventory(slvl, -2)
                        update_inventory(slvl+1, 1)
                        st.balloons()
                        st.success("변이 성공! 레벨 업!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        update_inventory(slvl, -1)
                        st.error("합성 실패! 1명 소멸.")
                        st.rerun()
            else:
                st.caption(f"⚠️ 합성을 위해서는 2명이 필요합니다.")

        with col_r:
            # [기능 C] 판매 (감옥)
            sell_price = 0.008 * (1.5**(slvl-1))
            st.write("⚖️ **처분 (감옥 이송)**")
            st.write(f"보상금: {sell_price:.4f} SOL")
            if scount > 0:
                if st.button("🔒 이송 (판매)"):
                    update_inventory(slvl, -1)
                    update_balance(sell_price)
                    st.toast("이송 완료.", icon="💰")
                    st.rerun()
    else:
        st.info("👆 상단 목록에서 유닛을 선택하세요.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: 명예의 전당 (에러 수정됨) ---
with tabs[1]:
    st.subheader("🏆 HALL OF FAME")
    
    # [에러 수정 3] 데이터가 없을 때 TypeError 방지 (IFNULL 사용)
    with get_db() as conn:
        rows = conn.execute("""
            SELECT wallet, IFNULL(balance, 0.0) 
            FROM users 
            ORDER BY balance DESC 
            LIMIT 5
        """).fetchall()
    
    if rows:
        for i, row in enumerate(rows):
            val = row[1] if row[1] is not None else 0.0
            st.write(f"**{i+1}위** : {row[0]} — {val:.4f} SOL")
    else:
        st.write("아직 데이터가 없습니다.")

# --- TAB 3: 제보하기 ---
with tabs[2]:
    st.subheader("🕵️ INTELLIGENCE REPORT")
    with st.form("report_form"):
        target = st.text_input("사기꾼 지갑 주소")
        note = st.text_area("제보 내용")
        if st.form_submit_button("전송"):
            if target:
                with get_db() as conn:
                    conn.execute("INSERT INTO reports (wallet, content, time) VALUES (?, ?, datetime('now'))", (target, note))
                    conn.commit()
                st.success("접수 완료.")
            else: st.error("주소를 입력하세요.")
            
    st.markdown("---")
    st.write("📢 **최근 제보 목록**")
    with get_db() as conn:
        logs = conn.execute("SELECT wallet, content, time FROM reports ORDER BY id DESC LIMIT 5").fetchall()
    for log in logs:
        st.info(f"[{log[2]}] {log[0]} - {log[1]}")
