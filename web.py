import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI GLOBAL", layout="wide")

# 2. 디자인 적용 (여기서 에러 나던 'index' 단어를 'html'로 고쳤습니다!)
st.markdown("""
    <style>
    /* 전체 배경을 리얼 블랙으로 */
    .stApp {
        background-color: #000000 !important;
        color: #E8C35E !important;
    }
    /* 글자색 전부 황금색으로 통일 */
    h1, h2, h3, p, span, div {
        color: #E8C35E !important;
        font-family: 'Courier New', sans-serif;
    }
    /* 버튼을 고급진 그라데이션 골드로 */
    .stButton>button {
        background: linear-gradient(45deg, #E8C35E, #B8860B) !important;
        color: black !important;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        height: 50px;
        width: 100%;
    }
    /* 숫자 박스 테두리 디자인 */
    [data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 1px solid #E8C35E !important;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 0 10px rgba(232, 195, 94, 0.2);
    }
    </style>
    """, unsafe_allow_html=True) 

# 3. 메인 타이틀
st.title("⚡ WOOHOO AI HYPER-CORE")
st.write("### 🌍 DECENTRALIZED INTELLIGENCE NETWORK")
st.write("---")

# 4. 대시보드 (오타 없이 깔끔하게 정리)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("📡 SCANNER STATUS", "ACTIVE", "0.001ms")
with c2:
    st.metric("💎 TOTAL NODES", "2,405 EA", "+128")
with c3:
    st.metric("🧠 AI CONFIDENCE", "99.8%", "ELITE")

# 5. 차트
st.write("### 📊 Live Intelligence Flow")
chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['Security', 'AI-Shield'])
st.area_chart(chart_data)

# 6. 시스템 로그
st.write("---")
st.write("🎯 **AI SNIPER ENGINE [LIVE SCANNING]**")
st.code("""
[SYSTEM] Deep-Scanning Block #29481...
[DETECT] Safe Token Found: $WOOHOO
[ACTION] Monitoring Liquidity Pools...
[STATUS] All Systems Green. No Rug-pull Detected.
""", language='bash')

# 7. 버튼
if st.button("MINT YOUR FOUNDER NODE (2.0 SOL)"):
    st.balloons()
    st.success("Wallet Connection Initialized! Checking Whitelist...")

# 8. 바닥글
st.write("---")
st.caption("© 2026 WOOHOO AI LABS | Powered by Solana High-Speed Network")
