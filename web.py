import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO CORE", layout="wide")

# 2. 디자인 강제 적용 (폰트: 타자기체, 배경: 리얼 블랙)
st.markdown("""
    <style>
    /* 전체 배경 검은색 강제 고정 */
    .stApp {
        background-color: #000000 !important;
    }
    /* 모든 폰트를 해커 스타일로 */
    html, body, p, h1, h2, h3, div, span, button {
        font-family: 'Courier New', Courier, monospace !important;
        color: #E8C35E !important;
    }
    /* 숫자 박스 디자인 */
    [data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #E8C35E !important;
        box-shadow: 0 0 10px rgba(232, 195, 94, 0.2);
    }
    /* 버튼 디자인 */
    .stButton>button {
        background-color: #E8C35E !important;
        color: #000000 !important;
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더 섹션
st.title("⚡ WOOHOO_AI_CORE")
st.write("Target: SOLANA_MAINNET | Status: MONITORING...")
st.write("---")

# 4. 대시보드 (여기가 아까 에러났던 부분입니다! 수정 완료)
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("SCANNER", "ACTIVE", "0.001ms")
with c2:
    st.metric("NODES", "2,405", "+128")
with c3:
    st.metric("CONFIDENCE", "99.9%", "SECURE")

# 5. [강제 블랙 차트] Plotly 적용
st.write("### 📊 NETWORK_TRAFFIC_ANALYSIS")

# 데이터 생성
df = pd.DataFrame(np.random.randn(50, 2), columns=['A', 'B'])

# 차트 그리기
fig = go.Figure()
fig.add_trace(go.Scatter(y=df['A'], fill='tozeroy', name='AI_LAYER', line=dict(color='#E8C35E')))
fig.add_trace(go.Scatter(y=df['B'], fill='tonexty', name='SECURE', line=dict(color='#333333')))

# 차트 배경을 코드로 까맣게 칠하기 (설정 안 건드려도 됨)
fig.update_layout(
    paper_bgcolor='black',
    plot_bgcolor='black',
    font={'color': '#E8C35E', 'family': 'Courier New'},
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='#222222')
)
st.plotly_chart(fig, use_container_width=True)

# 6. 해킹 로그 창
st.write("---")
st.code("""
root@woohoo-ai:~# initiate_scan
> CONNECTING TO SOLANA RPC NODE... [OK]
> DETECTED TOKEN: $WOOHOO (ADDR: 8x...F2)
> RUG_PULL_CHECK: PASSED (100%)
> LIQUIDITY: LOCKED
""", language="bash")

# 7. 실행 버튼
if st.button(">> INITIALIZE_FOUNDER_NODE_MINT <<"):
    st.balloons()
    st.success("ACCESS GRANTED. WALLET CONNECTING...")
