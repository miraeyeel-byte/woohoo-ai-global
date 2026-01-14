import streamlit as st
import random
import sqlite3
import os
import time

# [1. 설정 & DB]
st.set_page_config(page_title="WOOHOO Command Center", layout="wide", initial_sidebar_state="collapsed")
DB_PATH = "woohoo_v17_hero.db"

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        # 유닛(범죄자) 인벤토리: lvl(레벨), count(수량)
        c.execute("CREATE TABLE IF NOT EXISTS units (lvl INTEGER PRIMARY KEY, count INTEGER)")
        # 감옥
        c.execute("CREATE TABLE IF NOT EXISTS jail (lvl INTEGER PRIMARY KEY, count INTEGER)")
        # 유저 자산
        c.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, balance REAL)")
        c.execute("INSERT OR IGNORE INTO user VALUES (1, 0.1)")
        # 초기 유닛 지급 (테스트용)
        for i in range(1, 6):
            c.execute("INSERT OR IGNORE INTO units VALUES (?, ?)", (i, 0))
        conn.commit()
init_db()

# [2. 스타크래프트 스타일 CSS - 음영 & 깊이감]
st.markdown("""
<style>
    /* 전체 배경: 우주 느낌의 다크 그레이 */
    .stApp { background-color: #0e0e10; color: #c0c0c0; }
    
    /* 유닛 카드 스타일 */
    .unit-card {
        background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
        border: 1px solid #444;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 5px 5px 10px #080808, -5px -5px 10px #333; /* 3D 음영 */
        transition: all 0.2s ease;
        cursor: pointer;
        margin-bottom: 15px;
    }
    .unit-card:hover {
        border-color: #00ff00; /* 선택 시 네온 그린 */
        box-shadow: 0 0 15px #00ff00;
        transform: translateY(-2px);
    }
    
    /* 커맨드 패널 (하단 고정 느낌) */
    .command-panel {
        background-color: #111;
        border-top: 2px solid #333;
        padding: 20px;
        border-radius: 15px;
        box-shadow: inset 0 0 20px #000;
        margin-top: 20px;
    }
    
    /* 버튼 스타일 */
    div.stButton > button {
        background-color: #222;
        color: #00ff00;
        border: 1px solid #00ff00;
        border-radius: 5px;
        font-weight: bold;
        box-shadow: 0 0 5px #00ff0040;
    }
    div.stButton > button:hover {
        background-color: #00ff00;
        color: #000;
        box-shadow: 0 0 15px #00ff00;
    }
    
    /* 텍스트 글로우 */
    .glow-text {
        color: #fff;
        text-shadow: 0 0 10px #00aaff;
    }
</style>
""", unsafe_allow_html=True)

# [3. 세션 상태 관리]
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None # 현재 선택된 유닛 레벨

# [4. 로직 함수]
def update_unit(lvl, delta):
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO units VALUES (?, 0)", (lvl,))
        conn.execute("UPDATE units SET count = count + ? WHERE lvl = ?", (delta, lvl))
        conn.commit()

def move_to_jail(lvl):
    with get_db() as conn:
        # 유닛 감소
        conn.execute("UPDATE units SET count = count - 1 WHERE lvl = ?", (lvl,))
        # 감옥 증가
        conn.execute("INSERT OR IGNORE INTO jail VALUES (?, 0)", (lvl,))
        conn.execute("UPDATE jail SET count = count + 1 WHERE lvl = ?", (lvl,))
        # 현상금 지급
        reward = lvl * 0.01
        conn.execute("UPDATE user SET balance = balance + ? WHERE id=1", (reward,))
        conn.commit()
    return reward

def synthesize_units(lvl):
    # 3마리를 합쳐서 상위 1마리로 (StarCraft Archon 소환 느낌)
    with get_db() as conn:
        cur = conn.execute("SELECT count FROM units WHERE lvl=?", (lvl,)).fetchone()
        if cur and cur[0] >= 3:
            conn.execute("UPDATE units SET count = count - 3 WHERE lvl=?", (lvl,))
            conn.execute("INSERT OR IGNORE INTO units VALUES (?, 0)", (lvl+1,))
            conn.execute("UPDATE units SET count = count + 1 WHERE lvl=?", (lvl+1,))
            conn.commit()
            return True
    return False

# [5. UI 구성]
st.markdown("<h1 class='glow-text'>⚔️ WOOHOO COMMAND CENTER</h1>", unsafe_allow_html=True)

# 상단 정보창 (미네랄/가스 대신 SOL/유닛)
with get_db() as conn:
    balance = conn.execute("SELECT balance FROM user").fetchone()[0]
    total_units = conn.execute("SELECT SUM(count) FROM units").fetchone()[0]
    if total_units is None: total_units = 0

col_inf1, col_inf2, col_inf3 = st.columns(3)
col_inf1.metric("OPERATIONAL FUNDS", f"{balance:.3f} SOL")
col_inf2.metric("ACTIVE UNITS", f"{total_units} ea")
col_inf3.metric("DEFCON LEVEL", "3 (Ready)")

# 탭 메뉴 (스타크래프트 건물 선택 느낌)
tab_field, tab_lab, tab_prison = st.tabs(["🚀 작전 필드 (Field)", "🧬 융합실 (Synthesis)", "🔒 감옥 (Jail)"])

# --- TAB 1: 작전 필드 (유닛 선택 및 명령) ---
with tab_field:
    st.caption("※ 유닛을 클릭(선택)하여 하단 패널에서 명령을 내리십시오.")
    
    # 유닛 그리드 표시
    with get_db() as conn:
        units = conn.execute("SELECT lvl, count FROM units WHERE count > 0 ORDER BY lvl ASC").fetchall()
    
    if not units:
        st.info("배치된 유닛이 없습니다. '탐색'을 통해 범죄자를 포착하십시오.")
        if st.button("📡 레이더 가동 (범죄자 탐색)"):
            found_lvl = random.randint(1, 3)
            update_unit(found_lvl, 1)
            st.success(f"경보! Lv.{found_lvl} 범죄자 포착!")
            time.sleep(1)
            st.rerun()
    else:
        # 유닛 카드 렌더링
        cols = st.columns(6)
        for idx, (lvl, count) in enumerate(units):
            with cols[idx % 6]:
                # 카드 UI
                emoji = ["👤", "👺", "🧟", "🧛", "🤖", "👿", "☠️"][min(lvl-1, 6)]
                name = f"CodeName: {emoji} Lv.{lvl}"
                
                # 선택 버튼 (스타크래프트 유닛 클릭)
                if st.button(f"{name}\n(x{count})", key=f"sel_{lvl}", help="클릭하여 선택"):
                    st.session_state.selected_unit = lvl

    # --- COMMAND PANEL (하단 명령창) ---
    st.markdown("---")
    st.markdown("<div class='command-panel'>", unsafe_allow_html=True)
    
    if st.session_state.selected_unit:
        sel_lvl = st.session_state.selected_unit
        st.markdown(f"### 🟢 TARGET SELECTED: **Lv.{sel_lvl} Criminal**")
        
        c1, c2, c3, c4 = st.columns(4)
        
        # [명령 1] 보관 (선택 해제)
        with c1:
            if st.button("🛡️ 대기 (Hold)"):
                st.session_state.selected_unit = None
                st.rerun()
                
        # [명령 2] 감옥 보내기
        with c2:
            if st.button("⚖️ 체포/수감 (Jail)"):
                r = move_to_jail(sel_lvl)
                st.toast(f"수감 완료! 현상금 {r:.2f} SOL 획득", icon="💰")
                st.rerun()
                
        # [명령 3] 융합 (조합실로 이동 안내)
        with c3:
            if st.button("🧬 융합 프로토콜"):
                st.info("상단 '융합실' 탭으로 이동하여 실행하십시오.")
                
        # [명령 4] 정보 보기
        with c4:
            st.caption(f"Status: Dangerous\nBounty: {sel_lvl*0.01} SOL")
            
    else:
        st.markdown("### ⚪ SYSTEM IDLE: Select a unit to execute orders.")
        st.caption("작전 필드의 유닛을 선택하면 명령 패널이 활성화됩니다.")
        
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: 융합실 (Synthesis) ---
with tab_lab:
    st.subheader("🧬 BIO-LAB: Criminal Synthesis")
    st.write("하위 범죄자 3명을 융합하여 더 강력한(나쁜) 상위 범죄자 1명으로 재조합합니다.")
    
    with get_db() as conn:
        # 조합 가능한 유닛(3마리 이상)만 표시
        fusible = conn.execute("SELECT lvl, count FROM units WHERE count >= 3 ORDER BY lvl ASC").fetchall()
        
    if not fusible:
        st.warning("융합 가능한 유닛이 없습니다. (최소 3명 필요)")
    else:
        f_cols = st.columns(4)
        for idx, (lvl, count) in enumerate(fusible):
            with f_cols[idx % 4]:
                st.info(f"**Lv.{lvl}** (보유: {count})")
                if st.button(f"⚡ 융합 시도 (3 -> 1)", key=f"fuse_{lvl}"):
                    if synthesize_units(lvl):
                        st.balloons() # 여기선 '변이 성공' 느낌
                        st.success(f"⚠️ 경고! **Lv.{lvl+1}** 변종이 탄생했습니다!")
                        time.sleep(1.5)
                        st.rerun()

# --- TAB 3: 감옥 (Vault/Jail) ---
with tab_prison:
    st.subheader("🔒 Maximum Security Prison")
    with get_db() as conn:
        prisoners = conn.execute("SELECT lvl, count FROM jail WHERE count > 0").fetchall()
    
    if not prisoners:
        st.write("감옥이 비어있습니다.")
    else:
        for p_lvl, p_cnt in prisoners:
            st.write(f"⛓️ **Lv.{p_lvl} 죄수**: {p_cnt}명 수감 중")

