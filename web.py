import os
import streamlit as st
import random
import sqlite3
import datetime
import requests
import threading

# [1. DB 및 환경 설정] - 에러 방지용 자동 경로 생성 포함
DB_PATH = os.getenv("DB_PATH", "woohoo_master_v17.db")
if not os.path.exists(os.path.dirname(DB_PATH)) and os.path.dirname(DB_PATH):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) #

def get_db_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# [2. 고급 UI 스타일 정의]
st.markdown("""
<style>
    .criminal-card {
        border: 2px solid #FFD700; border-radius: 12px; padding: 15px;
        background: #111; text-align: center; margin-bottom: 10px;
    }
    .success-glow {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        box-shadow: inset 0 0 100px #FFD700; pointer-events: none;
        animation: fadeOut 2s forwards; z-index: 9999;
    }
    @keyframes fadeOut { from {opacity: 1;} to {opacity: 0;} }
</style>
""", unsafe_allow_html=True)

# [3. 핵심 보안 및 수사 로직]
def process_capture_logic(lvl, hunter_tier):
    # PRO 티어 원천 차단 시뮬레이션
    risk = random.randint(10, 95)
    if hunter_tier == "PRO" and risk > 70:
        st.error("🚫 보안 엔진: 위험 감지로 인한 트랜잭션 원천 차단!")
        return "BLOCKED"

    # 체포 확률 계산
    fail_rate = 10 + (lvl-1)*4 
    if random.randint(1, 100) > fail_rate:
        st.toast(f"🎯 Lv.{lvl} 체포 성공!", icon="🚔")
        st.markdown("<div class='success-glow'></div>", unsafe_allow_html=True) # 풍선 대체
        return "SUCCESS"
    return "FAIL"

# [4. 메인 UI 구성]
st.title("🚨 FuckHoneypot SIU (Special Investigation Unit)")

# 사이드바: 헌터 정보 및 라이선스
with st.sidebar:
    st.header("🕵️ Hunter Profile")
    wallet = st.text_input("Wallet Connect", value="USER_01")
    tier = st.selectbox("License Tier", ["BASIC", "PRO"])
    st.info(f"Current Tier: {tier}")

tabs = st.tabs(["🎯 Wanted List", "🧪 Evidence Lab", "🏆 Leaderboard"])

with tabs[0]: # 범죄자 카드 UI
    st.subheader("현상 수배 명단 (Lv.1 - Lv.20)")
    cols = st.columns(4)
    for i in range(1, 21):
        with cols[(i-1)%4]:
            st.markdown(f"""
            <div class="criminal-card">
                <img src="https://via.placeholder.com/100?text=Lv.{i}" width="100%">
                <h4>범죄자 #{i}</h4>
                <small>Reward: {i*0.01} SOL</small>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"체포 Lv.{i}", key=f"hunt_{i}"):
                result = process_capture_logic(i, tier)
                if result == "SUCCESS": st.success("증거 확보 및 수감 완료!")

with tabs[1]: # 조합 기능
    st.subheader("🧪 증거 합성 시스템")
    st.write("하위 범죄자 체포 기록을 합성하여 상위 레벨의 결정적 단서를 생성합니다.")
    if st.button("Lv.1 증거 10개 합성하기"):
        st.info("합성 진행 중... (0.01 SOL 소모)")
        st.success("✨ Lv.2 수사 단서 생성 완료!")
