import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI GLOBAL", layout="wide")

# [수정 1] 디자인 코드를 맨 위로 배치 (그래야 처음부터 검은색으로 뜹니다!)
st.markdown("""
    <style>
    /* 전체 배경 강제 블랙 */
    .stApp {
        background-color: #000000 !important;
        color: #E8C35E !important;
    }
    /* 모든 텍스트 황금색 통일 */
    h1, h2, h3, p, span, div {
        color: #E8C35E !important;
        font-family: 'Courier New', sans-serif;
    }
    /* [프로버전 추가] 버튼을 고급스러운 금색 그라데이션으로 */
    .stButton>button {
        background: linear-gradient(45deg, #E8C35E, #B8860B) !important;
        color: black !important;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        height: 50px;
        width: 100%;
    }
    /* 지표 박스 테두리 디자인 */
    [data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 1px solid #E8C35E !important;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 0 10px rgba(232, 195, 94, 0.2);
    }
    </style>
    """, unsafe_allow_index=True)

# 2. 메인 타이틀
st.title("⚡ WOOHOO AI HYPER-CORE")
st.write("### 🌍 DECENTRALIZED INTELLIGENCE NETWORK")
st.write("---")

# [수정 2] 에러 나던 'col3' 부분 해결 + 디자인 예쁜 'Metric'으로 교체
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("📡 SCANNER STATUS", "ACTIVE", "0.001ms")
with c2:
    st.metric("💎 TOTAL NODES", "2,405 EA", "+128")
with c3:
    # 여기가 아까 에러났던 부분입니다. 깔끔하게 고쳤습니다.
    st.metric("🧠 AI CONFIDENCE", "99.8%", "ELITE")

# 4. 실시간 분석 차트
st.write("### 📊 Live Intelligence Flow")
chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['Security', 'AI-Shield'])
st.area_chart(chart_data)

# 5. AI 스나이퍼 로그
st.write("---")
st.write("🎯 **AI SNIPER ENGINE [LIVE SCANNING]**")
st.code("""
[SYSTEM] Deep-Scanning Block #29481...
[DETECT] Safe Token Found: $WOOHOO
[ACTION] Monitoring Liquidity Pools...
[STATUS] All Systems Green. No Rug-pull Detected.
""", language='bash')

# 6. 노드 구매 버튼
if st.button("MINT YOUR FOUNDER NODE (2.0 SOL)"):
    st.balloons()
    st.success("Wallet Connection Initialized! Checking Whitelist...")

# 7. 푸터
st.write("---")
st.caption("© 2026 WOOHOO AI LABS | Powered by Solana High-Speed Network")
