ㅡimport streamlit as st
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
DB_PATH = "woohoo_v17_rpg.db"

# [2. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, wallet TEXT, content TEXT, time TEXT)")
        # 테스트용 초기 자금
        c.execute("INSERT OR IGNORE INTO users VALUES ('Operator', 10.0)")
        conn.commit()
init_db()

# [3. 스타일링 (RPG 다크 테마 & 카드)]
st.markdown("""
<style>
    .stApp { background-color: #0b0c10; color: #c5c6c7; }
    
    /* 유닛 카드 */
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
    
    /* 텍스트 스타일 */
    .level-badge {
        background: #45a29e; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# [4. 세션 상태]
if 'wallet' not in st.session_state: st.session_state.wallet = "Operator" # 테스트용 자동 로그인
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

# [6. 메인 UI]
st.title("⚔️ WOOHOO RPG COMMANDER")

# 상단 상태바
bal = get_balance()
c1, c2, c3 = st.columns([2, 1, 1])
c1.metric("OPERATOR WALLET", st.session_state.wallet)
c2.metric("ASSETS (SOL)", f"{bal:.4f}")
c3.metric("DEFCON", "LEVEL 1")

# 탭 구성: 게임(RPG) / 랭킹 / 제보
tabs = st.tabs(["🎮 COMMAND CENTER", "🏆 HALL OF FAME", "🕵️ INTELLIGENCE (제보)"])

# --- TAB 1: COMMAND CENTER (RPG 메인) ---
with tabs[0]:
    # 1. 유닛(범죄자) 인벤토리 그리드
    st.subheader("🛑 UNIT CONTROLLER")
    inv = get_inventory()
    
    # 20레벨까지 슬롯 생성
    cols = st.columns(6)
    for i in range(1, 21): # 1~20레벨
        count = inv.get(i, 0)
        with cols[(i-1)%6]:
            # 카드 스타일링 (선택 시 하이라이트)
            border_cls = "unit-selected" if st.session_state.selected_lvl == i else "unit-card"
            
            # 카드 내용
            img_icon = ["👤", "👺", "🤡", "💀", "👾", "🐉", "👹", "👽"][min(i-1, 7)]
            st.markdown(f"""
            <div class='{border_cls}'>
                <div style='font-size:40px;'>{img_icon}</div>
                <div><b>Lv.{i} Criminal</b></div>
                <div style='color:#66fcf1'>x {count}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # [선택] 버튼 (클릭 시 하단 콘솔 활성화)
            if st.button(f"SELECT Lv.{i}", key=f"sel_{i}", use_container_width=True):
                st.session_state.selected_lvl = i
                st.session_state.confirm_buy = False # 선택 변경 시 구매창 닫기
                st.rerun()

    # 2. 하단 커맨드 콘솔 (스타크래프트 느낌)
    st.markdown("<div class='command-console'>", unsafe_allow_html=True)
    
    if st.session_state.selected_lvl:
        slvl = st.session_state.selected_lvl
        scount = inv.get(slvl, 0)
        
        c_left, c_mid, c_right = st.columns([1, 2, 1])
        
        with c_left:
            st.markdown(f"### 🎯 TARGET: Lv.{slvl}")
            st.write(f"보유 수량: **{scount}** 명")
            
        with c_mid:
            # [기능 A] 레벨 1 구매 (소환)
            if slvl == 1:
                st.info("💡 Lv.1은 [0.01 SOL]로 즉시 체포(구매) 가능합니다.")
                if not st.session_state.confirm_buy:
                    if st.button("🚨 체포 작전 개시 (구매)", key="buy_btn"):
                        st.session_state.confirm_buy = True
                        st.rerun()
                else:
                    st.warning("⚠️ 작전 승인: 0.01 SOL이 소모됩니다. 진행하시겠습니까?")
                    b1, b2 = st.columns(2)
                    if b1.button("✅ 승인 (YES)"):
                        if bal >= 0.01:
                            update_balance(-0.01)
                            update_inventory(1, 1)
                            st.session_state.confirm_buy = False
                            st.toast("체포 성공! 인벤토리에 추가되었습니다.", icon="🚔")
                            st.rerun()
                        else:
                            st.error("자금 부족!")
                    if b2.button("❌ 취소 (NO)"):
                        st.session_state.confirm_buy = False
                        st.rerun()
            else:
                st.info(f"🔒 Lv.{slvl}은 구매할 수 없습니다. 오직 [합성]으로만 획득 가능합니다.")

            # [기능 B] 합성 (Fusion) - 비콘 전송 느낌
            st.markdown("---")
            if scount >= 2:
                st.write(f"🧬 **Lv.{slvl} (2명)** ➡️ **Lv.{slvl+1} (1명)** 합성 가능")
                if st.button(f"⚡ 합성 프로토콜 실행 (Lv.{slvl} -> Lv.{slvl+1})"):
                    # 확률 설정 (예: 90% 성공)
                    if random.random() < 0.9:
                        update_inventory(slvl, -2)
                        update_inventory(slvl+1, 1)
                        st.balloons()
                        st.success(f"변이 성공! 더 강력한 Lv.{slvl+1} 범죄자가 되었습니다.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        update_inventory(slvl, -1) # 실패 시 1마리 소멸 페널티
                        st.error("합성 실패! 실험체 1명이 소멸했습니다.")
                        st.rerun()
            else:
                st.caption(f"⚠️ 합성을 위해서는 Lv.{slvl} 범죄자 2명이 필요합니다.")

        with c_right:
            # [기능 C] 감옥 보내기 (판매)
            sell_price = 0.008 * (2**(slvl-1)) # Lv1=0.008, Lv2=0.016...
            st.write("⚖️ **처분 (감옥 이송)**")
            st.write(f"보상금: {sell_price:.4f} SOL")
            
            if scount > 0:
                if st.button("🔒 감옥으로 이송 (판매)"):
                    update_inventory(slvl, -1)
                    update_balance(sell_price)
                    st.toast(f"이송 완료. {sell_price:.4f} SOL 획득", icon="💰")
                    st.rerun()
            else:
                st.caption("이송할 대상이 없습니다.")

    else:
        st.info("👆 상단 목록에서 유닛(범죄자)을 선택하여 명령을 내리십시오.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: 명예의 전당 (복구됨) ---
with tabs[1]:
    st.subheader("🏆 HALL OF FAME")
    st.write("가장 높은 레벨의 범죄자를 보유한 전설적인 헌터들입니다.")
    
    # 랭킹 더미 데이터 (실제 DB 연동 가능)
    rank_data = [
        {"Rank": 1, "Hunter": "Operator", "Top Criminal": "Lv.19 Lucifer", "Score": 9999},
        {"Rank": 2, "Hunter": "SolanaKing", "Top Criminal": "Lv.15 Joker", "Score": 5000},
        {"Rank": 3, "Hunter": "DegenHunter", "Top Criminal": "Lv.12 Thief", "Score": 1200},
    ]
    st.dataframe(pd.DataFrame(rank_data), use_container_width=True)

# --- TAB 3: 제보하기 (복구됨) ---
with tabs[2]:
    st.subheader("🕵️ INTELLIGENCE REPORT")
    st.write("의심스러운 스캠 코인이나 사기꾼 지갑을 제보해주세요. 헌터들이 출동합니다.")
    
    with st.form("report_form"):
        r_wallet = st.text_input("사기꾼 지갑 주소 (Scammer Wallet)")
        r_desc = st.text_area("제보 내용 (증거 자료 등)")
        
        if st.form_submit_button("📩 제보 전송"):
            if r_wallet and r_desc:
                with get_db() as conn:
                    conn.execute("INSERT INTO reports (wallet, content, time) VALUES (?, ?, ?)", 
                                 (r_wallet, r_desc, time.strftime('%Y-%m-%d %H:%M:%S')))
                    conn.commit()
                st.success("접수되었습니다. 보안 팀이 분석을 시작합니다.")
            else:
                st.error("내용을 입력해주세요.")
    
    # 최근 제보 목록
    st.markdown("---")
    st.markdown("##### 📢 최근 접수된 제보")
    with get_db() as conn:
        logs = conn.execute("SELECT wallet, content, time FROM reports ORDER BY id DESC LIMIT 5").fetchall()
    for log in logs:
        st.info(f"[{log[2]}] **Target:** {log[0]} | **Note:** {log[1]}")

