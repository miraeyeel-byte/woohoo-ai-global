import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import os
import threading

# [1. 설정 및 보안]
st.set_page_config(page_title="WOOHOO SIU V17.13", layout="wide")
DB_PATH = "woohoo_master_v17.db" # 경로 단순화로 에러 방지

# [2. CSS: 카드 및 성공 효과]
st.markdown("""
<style>
    .stApp {background:#000; color:white;}
    .wanted-card {
        border: 2px solid #FFD700; border-radius: 15px; padding: 15px;
        background: #111; text-align: center; transition: 0.3s;
    }
    .wanted-card:hover { transform: translateY(-5px); box-shadow: 0 0 20px #FFD700; }
    .success-glow {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        box-shadow: inset 0 0 100px #FFD700; pointer-events: none;
        animation: fadeOut 2s forwards; z-index: 9999;
    }
    @keyframes fadeOut { from {opacity: 1;} to {opacity: 0;} }
</style>
""", unsafe_allow_html=True)

# [3. DB 초기화]
def get_db_conn():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        conn.commit()
init_db()

# [4. 핵심 기능 로직]
def check_firewall(ip):
    # 3번째 사진의 SyntaxError 수정: hosting} -> hosting
    url = f"http://ip-api.com/json/{ip}?fields=status,countryCode,proxy,hosting"
    try:
        res = requests.get(url, timeout=2).json()
        return res.get('proxy', False)
    except: return False

# [5. UI 구성]
st.title("🚔 WOOHOO Special Investigation Unit (V17.13)")
st.write("사기꾼 추적 및 자산 보호 보안 플랫폼")

# 세션 관리
if "inv" not in st.session_state: st.session_state.inv = {i:0 for i in range(1, 21)}

tabs = st.tabs(["🎯 Wanted List", "🧪 Evidence Lab", "🏆 Top Hunters"])

with tabs[0]: # [카드형 UI 부활]
    st.subheader("Wanted Level 1 - 20")
    cols = st.columns(4)
    for i in range(1, 13): # 예시로 12개 카드 출력
        with cols[(i-1)%4]:
            st.markdown(f"""
            <div class="wanted-card">
                <h2 style="font-size: 50px;">{'👤' if i < 5 else '👹'}</h2>
                <h3>Lv.{i} Criminal</h3>
                <p>Reward: {i*0.01} SOL</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Hunt Lv.{i}", key=f"h_{i}"):
                if random.random() > (0.1 + i*0.04):
                    st.session_state.inv[i] += 1
                    st.success(f"Lv.{i} 체포 성공!")
                    st.markdown("<div class='success-glow'></div>", unsafe_allow_html=True)
                else:
                    st.error("체포 실패!")

with tabs[1]: # [조합 기능 전문화]
    st.subheader("🧪 증거 분석 및 합성실")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"현재 보유한 Lv.1 증거: **{st.session_state.inv[1]}개**")
        if st.button("Lv.1 10개를 합성하여 Lv.2 추적권 생성"):
            if st.session_state.inv[1] >= 10:
                st.session_state.inv[1] -= 10
                st.session_state.inv[2] += 1
                st.toast("✨ 합성 성공! Lv.2 단서를 획득했습니다.")
            else:
                st.error("증거가 부족합니다.")

with tabs[2]: # [리더보드 TypeError 수정]
    st.subheader("🏆 Legendary Hunters")
    with get_db_conn() as conn:
        rows = conn.execute("SELECT wallet, IFNULL(balance, 0.0) FROM users ORDER BY balance DESC LIMIT 5").fetchall()
    if rows:
        for i, r in enumerate(rows):
            val = r[1] if r[1] is not None else 0.0 # TypeError 방지
            st.write(f"{i+1}. {r[0]} — {val:.3f} SOL")
    else:
        st.write("No data available.")
