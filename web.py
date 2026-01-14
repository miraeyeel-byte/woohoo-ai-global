import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# ---------------------------------------------------------
# 1. 페이지 설정 (다크 모드 및 레이아웃)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Photon Trading Clone",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (포톤 스타일의 네온/다크 테마 적용)
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 색상 */
    .stApp {
        background-color: #0e0e10;
        color: #ffffff;
    }
    
    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1c;
    }
    
    /* 헤드라인 그라데이션 효과 (포톤 스타일) */
    .neon-text {
        background: linear-gradient(to right, #00f2ea, #ff0050);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 3em;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 사이드바 메뉴 (이미지 1 참고)
# ---------------------------------------------------------
with st.sidebar:
    st.title("🚀 포톤 트레이딩")
    st.caption("SOL의 광자")
    
    menu = st.radio(
        "메뉴 선택",
        [
            "설정",
            "스마트 MEV 보호",
            "살아있는 쌍 먹이 (New Pairs)",
            "인기 페이지 (Trending)",
            "내 보유 자산",
            "멀티월렛",
            "지정가 주문",
            "DCA 주문",
            "밈스코프"
        ]
    )
    
    st.divider()
    st.info("현재 상태: 접속 중...")

# ---------------------------------------------------------
# 3. 메인 화면 로직 (이미지 2 참고)
# ---------------------------------------------------------

# 세션 상태 초기화 (지갑 연결 상태 관리)
if 'wallet_connected' not in st.session_state:
    st.session_state.wallet_connected = False
if 'balance' not in st.session_state:
    st.session_state.balance = 0.0

def connect_wallet():
    # 실제 블록체인 연결 대신 시뮬레이션
    with st.spinner('Phantom 지갑에 연결 중...'):
        time.sleep(1.5)
    st.session_state.wallet_connected = True
    st.session_state.balance = round(random.uniform(0.5, 10.0), 2)
    st.success("지갑 연결 성공!")

# 메인 UI 구성
if not st.session_state.wallet_connected:
    # 3-1. 랜딩 페이지 (연결 전)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="neon-text">스나이핑 후 토큰을<br>판매하세요</p>', unsafe_allow_html=True)
        st.markdown("### 번개처럼 빠른 속도 ⚡")
        st.write("지금 바로 연결하여 SOL 거래를 시작하세요.")
        
        if st.button("👻 지갑 연결"):
            connect_wallet()
            st.rerun() # 화면 새로고침
            
        st.caption("☑ 접속함으로서 본인은 다음 사항에 동의합니다. 자귀 & 은둔")

    with col2:
        # 차트 미리보기 느낌의 더미 데이터
        st.image("https://cryptologos.cc/logos/solana-sol-logo.png", width=100)
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
        st.line_chart(chart_data)

else:
    # 3-2. 트레이딩 대시보드 (연결 후)
    st.markdown(f"### 👋 환영합니다! 보유 SOL: **{st.session_state.balance} SOL**")
    
    # 실시간 토큰 스캐닝 시뮬레이션
    st.subheader("🔥 실시간 핫 토큰 (Live)")
    
    col_live1, col_live2, col_live3 = st.columns(3)
    
    # 더미 데이터 생성기
    def generate_token_data():
        return {
            "name": f"MEME-{random.randint(100,999)}",
            "price": round(random.uniform(0.0001, 0.05), 6),
            "change": random.choice(["+15%", "+230%", "-5%", "+1200%"])
        }
    
    tokens = [generate_token_data() for _ in range(3)]
    
    with col_live1:
        st.metric(label=tokens[0]["name"], value=f"{tokens[0]['price']} SOL", delta=tokens[0]["change"])
        if st.button(f"매수 {tokens[0]['name']}"):
            st.toast(f"{tokens[0]['name']} 매수 주문 전송 완료!")
            
    with col_live2:
        st.metric(label=tokens[1]["name"], value=f"{tokens[1]['price']} SOL", delta=tokens[1]["change"])
        if st.button(f"매수 {tokens[1]['name']}"):
            st.toast(f"{tokens[1]['name']} 매수 주문 전송 완료!")
            
    with col_live3:
        st.metric(label=tokens[2]["name"], value=f"{tokens[2]['price']} SOL", delta=tokens[2]["change"])
        if st.button(f"매수 {tokens[2]['name']}"):
            st.toast(f"{tokens[2]['name']} 매수 주문 전송 완료!")

    # 차트 영역
    st.divider()
    st.subheader("📊 차트 (BTC/SOL)")
    
    # 실시간처럼 움직이는 차트 데이터 생성
    last_rows = np.random.randn(1, 1)
    chart = st.line_chart(last_rows)

    if st.button("실시간 데이터 수신 (데모)"):
        for i in range(10):
            new_rows = last_rows + np.random.randn(1, 1)
            chart.add_rows(new_rows)
            last_rows = new_rows
            time.sleep(0.1)

# ---------------------------------------------------------
# 4. 하단 정보
# ---------------------------------------------------------
st.markdown("---")
st.caption("Powered by Python Streamlit | Photon Clone Project")
