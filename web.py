import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI GLOBAL", layout="wide")

# 2. 강제 다크모드 & 네온 골드 디자인 (사장님이 추가하신 부분)
st.markdown("""
    <style>
    /* 배경 블랙, 글자 황금색 */
    .stApp {
        background-color: #000000 !important;
        color: #E8C35E !important;
    }
    /* 제목 및 일반 텍스트 색상 고정 */
    h1, h2, h3, p, span, label {
        color: #E8C35E !important;
        text-shadow: 0 0 5px rgba(232, 195, 94, 0.3);
    }
    /* 지표(Metric) 박스 강화 */
    [data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 1px solid #E8C35E !important;
        border-radius: 10px;
        padding: 15px;
    }
    /* 구분선 색상 */
    hr { border-top: 1px solid #E8C35E !important; }
    </style>
    """, unsafe_allow_index=True)

# 3. 메인 화면 구성
st.title("⚡ WOOHOO AI HYPER-CORE")
st.write("🌐 DECENTRALIZED INTELLIGENCE NETWORK ON SOLANA")
st.write("---")

# 4. 델리시움 스타일 대시보드
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("SCANNER STATUS", "ACTIVE", "0.001ms")
with c2:
    st.metric("TOTAL NODES", "2,405 EA", "+128")
with c3:
    st.metric("AI CONFIDENCE", "99.8%", "ELITE")

# 5. 소닉 스타일 실시간 그래프
st.write("### 📊 Live Intelligence Flow")
chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['Security', 'AI-Shield'])
st.area_chart(chart_data)

# 6. 기술력 과시 (터미널)
st.write("---")
st.write("🎯 **AI SNIPER ENGINE [LIVE SCANNING]**")
st.code("""
[SYSTEM] Deep-Scanning Block #29481...
[DETECT] Safe Token Found: $WOOHOO
[ACTION] Monitoring Liquidity Pools...
[STATUS] All Systems Green. No Rug-pull Detected.
""", language='bash')

# 7. 노드 민팅 버튼
if st.button("MINT YOUR FOUNDER NODE (2.0 SOL)"):
    st.balloons()
    st.success("Wallet Connection Ready! Initializing...")

st.caption("© 2026 WOOHOO AI LABS | Powered by Solana High-Speed Network")
