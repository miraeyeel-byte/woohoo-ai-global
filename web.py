import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import streamlit.components.v1 as components

# 1. 페이지 설정
st.set_page_config(page_title="WOOHOO AI | MASTER CONTROL", layout="wide")

# 2. 운영자 정보 (마스터 지갑)
OWNER_WALLET = "7kLoYeYu1nNRw7EhA7FWNew2f1KWpe6mL7zpcMvntxPx"

# 3. 세션 상태 관리 (초기화)
if 'wallet_address' not in st.session_state:
    st.session_state.wallet_address = None
if 'balance' not in st.session_state:
    st.session_state.balance = 2.0  # 첫 방문 보너스
if 'sol_balance' not in st.session_state:
    st.session_state.sol_balance = 5.0 # 기본 5 SOL 부여
if 'is_first_dice' not in st.session_state:
    st.session_state.is_first_dice = True # 첫 판 당첨용
if 'owned_nodes' not in st.session_state:
    st.session_state.owned_nodes = 0
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'treasury' not in st.session_state:
    st.session_state.treasury = 0.0
if 'heroes' not in st.session_state:
    st.session_state.heroes = {} # RPG 영웅 저장 {레벨: 개수}
if 'last_dice_roll' not in st.session_state:
    st.session_state.last_dice_roll = None # 주사위 애니메이션용

# 4. [디자인] 프리미엄 티타늄 & 골드 + 귀여운 주사위 테마
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Noto+Sans+KR:wght@300;700&display=swap');
    
    .stApp { background-color: #000000 !important; }
    html, body, [class*="st-"] {
        color: #F0F0F0 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 1) !important;
    }
    h1, h2, h3, h4 { color: #FFD700 !important; font-family: 'Orbitron' !important; font-weight: 900 !important; }

    /* 전광판 스타일 */
    .ticker { background: #111; border-top: 2px solid #FFD700; border-bottom: 2px solid #FFD700; padding: 8px 0; color: #FFD700; font-weight: bold; }

    /* 🎲 귀여운 주사위 카드 디자인 (복구 및 애니메이션 추가) */
    .dice-card {
        background: #FFF5E1 !important;
        border: 8px solid #FF4B4B !important;
        border-radius: 30px !important;
        padding: 40px !important;
        text-align: center !important;
        box-shadow: 10px 10px 0px #FF4B4B !important;
        color: #000 !important;
        margin-bottom: 20px;
    }
    .dice-num { font-size: 100px !important; color: #FF4B4B !important; margin: 0; font-weight: 900; }

    /* 주사위 애니메이션 */
    .dice-animation {
        font-size: 80px;
        animation: roll 0.5s infinite alternate; /* 주사위 굴러가는 애니메이션 */
    }
    @keyframes roll {
        0% { transform: rotateY(0deg); opacity: 0.5; }
        100% { transform: rotateY(360deg); opacity: 1; }
    }

    /* 영웅 카드 디자인 */
    .hero-card {
        background: #222;
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.4);
    }
    .hero-image {
        width: 100px;
        height: 100px;
        object-fit: contain;
        margin-bottom: 10px;
        filter: drop-shadow(0 0 5px #FFD700);
    }
    .fusion-effect {
        animation: fadeOutZoom 0.8s forwards;
    }
    @keyframes fadeOutZoom {
        0% { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(1.5); }
    }
    </style>
    """, unsafe_allow_html=True)

# 5. 상단 헤더 & 축하 전광판
st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡ WOOHOO AI HYPER-CORE</h1>", unsafe_allow_html=True)
st.markdown("""
    <div class="ticker">
        <marquee scrollamount="10">
            🎊 축하합니다! 0x...8f2 님이 주사위 6번으로 잭팟 당첨! &nbsp;&nbsp;&nbsp;&nbsp; 🚀 신규 노드 구매 트랜잭션 승인 완료: 0x...a3c &nbsp;&nbsp;&nbsp;&nbsp; 💎 WOOHOO AI 메인넷 채굴 파워가 1.4 EH/s를 돌파했습니다!
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# 6. 사이드바 - 지갑 센터
with st.sidebar:
    st.markdown("### 🔑 WALLET CENTER")
    if not st.session_state.wallet_address:
        # 실제 팬텀 지갑 연결 시도 (Streamlit 환경 제약으로 알림만)
        st.info("💡 Phantom 지갑이 설치되어 있다면 'PHANTOM 연결 시도'를 눌러보세요.")
        phantom_connect_script = """
        <script>
        async function connectWalletActual() {
            if (window.solana && window.solana.isPhantom) {
                try {
                    const resp = await window.solana.connect();
                    alert("Phantom 지갑 연결 성공: " + resp.publicKey.toString());
                    // 실제 Streamlit 세션으로 주소값을 가져오기 위해서는 추가적인 js/py 브릿지 필요
                } catch (err) {
                    console.error("Phantom 연결 실패:", err);
                    alert("Phantom 연결에 실패했습니다. 지갑이 잠금 해제되었는지 확인해주세요.");
                }
            } else {
                alert("Phantom 지갑이 설치되어 있지 않습니다. Phantom 홈페이지로 이동합니다.");
                window.open("https://phantom.app/", "_blank");
            }
        }
        </script>
        <button onclick="connectWalletActual()" style="
            width: 100%;
            background: #4B0082; /* Deep Purple */
            color: #FFD700;
            border: none;
            padding: 12px;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            font-family: 'Orbitron', sans-serif;
            box-shadow: 0 0 10px rgba(75, 0, 130, 0.7);
        "> 🦊 PHANTOM 연결 시도 </button>
        """
        components.html(phantom_connect_script, height=60)
        
        # [운영자님 전용 비상 버튼] - 지갑 없어도 1억개 즉시 충전
        if st.button("👑 운영자 전용 빠른 연결", use_container_width=True):
            st.session_state.wallet_address = OWNER_WALLET
            st.session_state.balance = 100000000.0 # 운영자 비밀 1억코인
            st.session_state.sol_balance = 1000.0 # 운영자 SOL도 넉넉하게
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background:#111; padding:15px; border-radius:12px; border:2px solid #FFD700;">
                <p style="margin:0; font-size:12px; color:#888;">ADDRESS</p>
                <p style="margin:0; font-size:13px; color:#FFD700; font-weight:bold;">{st.session_state.wallet_address[:14]}...</p>
                <hr style="border-color:#333;">
                <p style="margin:0; font-size:12px; color:#888;">SOL BALANCE</p>
                <p style="margin:0; font-size:20px; font-weight:bold; color:#FFF;">{st.session_state.sol_balance:.2f} SOL</p>
                <p style="margin:0; font-size:12px; color:#888; margin-top:10px;">WH BALANCE</p>
                <p style="margin:0; font-size:24px; font-weight:bold; color:#FFD700;">{st.session_state.balance:,.0f} WH</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("DISCONNECT"):
            st.session_state.wallet_address = None
            st.rerun()

# 7. 탭 메뉴 (ADMIN 탭 포함)
menu_tabs = ["🌐 NETWORK", "🛠️ NODE SALE", "🕹️ ARCADE", "🎲 LUCKY DICE", "🐲 RPG HERO"]
if st.session_state.wallet_address == OWNER_WALLET:
    menu_tabs.append("👑 ADMIN")
tabs = st.tabs(menu_tabs)

# --- TAB 1: NETWORK ---
with tabs[0]:
    st.markdown("### 🌐 GLOBAL COMPUTE NETWORK")
    st.line_chart(pd.DataFrame(np.random.randn(20, 1), columns=['Power']), color=["#FFD700"])

# --- TAB 2: NODE SALE (노드 판매 복구) ---
with tabs[1]:
    st.markdown("### 🛠️ HYPER-FUSE 노드 분양")
    if not st.session_state.wallet_address:
        st.error("지갑을 연결해야 노드 구매가 가능합니다.")
    else:
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            st.markdown("""<div style='background:#111; padding:20px; border:1px solid #333; border-radius:15px;'>
                <h4>GENESIS NODE (Tier 1)</h4>
                <p>가격: 2.0 SOL</p>
                <p>채굴 수익: 50 WH / 일</p>
            </div>""", unsafe_allow_html=True)
            if st.button("MINT NODE (2.0 SOL)", use_container_width=True):
                if st.session_state.sol_balance >= 2.0:
                    with st.spinner("트랜잭션 승인 대기 중..."):
                        time.sleep(2)
                        st.session_state.sol_balance -= 2.0
                        st.session_state.owned_nodes += 1
                        st.balloons()
                        st.success("노드 구매 성공! 채굴 목록에 추가되었습니다.")
                else: st.error("SOL 잔액이 부족합니다.")
        with col_n2:
            st.metric("내가 보유한 노드", f"{st.session_state.owned_nodes} 개")
            st.info(f"예상 일일 채굴량: {st.session_state.owned_nodes * 50} WH")

# --- TAB 3: ARCADE (닷지 게임 복구) ---
with tabs[2]:
    st.markdown("### 🕹️ DODGE SURVIVAL (P2E)")
    if not st.session_state.wallet_address:
        st.error("지갑 연결이 필요합니다.")
    else:
        st.warning("⚠️ 참가비: 0.05 WH (시작 시 자동 차감)")
        if not st.session_state.game_active:
            if st.button("🚀 미션 시작 (START)", use_container_width=True):
                if st.session_state.balance >= 0.05:
                    st.session_state.balance -= 0.05
                    st.session_state.treasury += 0.05
                    st.session_state.game_active = True
                    st.rerun()
                else: st.error("잔액이 부족합니다.")
        else:
            if st.button("⏹️ 게임 종료 (EXIT)"):
                st.session_state.game_active = False
                st.rerun()
            
            # 닷지 게임 엔진 (JS)
            game_js = """
            <div style="text-align:center;">
                <canvas id="c" width="500" height="350" style="border:3px solid #FFD700; background:#000; cursor:none;"></canvas>
                <h2 id="t" style="color:#FFD700;">생존 시간: 0.00초</h2>
            </div>
            <script>
                const cv=document.getElementById("c"), x=cv.getContext("2d");
                let s=Date.now(), p={x:250,y:175,r:6}, b=[], go=false, ft=0;
                cv.onmousemove=e=>{ const r=cv.getBoundingClientRect(); p.x=e.clientX-r.left; p.y=e.clientY-r.top; };
                cv.onmouseleave=()=>{ if(!go){go=true; ft=(Date.now()-s)/1000;} };
                function spawn(){
                    const side=Math.floor(Math.random()*4); let blt={r:3,x:0,y:0,vx:0,vy:0};
                    if(side==0){blt.x=0; blt.y=Math.random()*350; blt.vx=3+Math.random()*2; blt.vy=(Math.random()-0.5)*4;}
                    else if(side==1){blt.x=500; blt.y=Math.random()*350; blt.vx=-3-Math.random()*2; blt.vy=(Math.random()-0.5)*4;}
                    else if(side==2){blt.x=Math.random()*500; blt.y=0; blt.vx=(Math.random()-0.5)*4; blt.vy=3+Math.random()*2;}
                    else {blt.x=Math.random()*500; blt.y=350; blt.vx=(Math.random()-0.5)*4; blt.vy=-3-Math.random()*2;}
                    b.push(blt);
                }
                function loop(){
                    if(go) return;
                    let el=(Date.now()-s)/1000;
                    document.getElementById("t").innerText="생존 시간: "+el.toFixed(2)+"초";
                    if(b.length<30+el) spawn();
                    b.forEach((i,idx)=>{
                        i.x+=i.vx; i.y+=i.vy;
                        if(i.x<0||i.x>500||i.y<0||i.y>350) b.splice(idx,1);
                        if(Math.hypot(i.x-p.x,i.y-p.y)<i.r+p.r){go=true; ft=el;}
                    });
                    x.clearRect(0,0,500,350);
                    x.fillStyle="#FFD700"; x.beginPath(); x.arc(p.x,p.y,p.r,0,7); x.fill();
                    x.fillStyle="#F44"; b.forEach(i=>{x.beginPath(); x.arc(i.x,i.y,i.r,0,7); x.fill();});
                    if(go){ x.fillStyle="#F44"; x.font="30px sans-serif"; x.fillText("GAME OVER", 170, 160); x.fillText(ft.toFixed(2)+"s", 220, 200); }
                    requestAnimationFrame(loop);
                }
                loop();
            </script>
            """
            components.html(game_js, height=500)
            if st.button("🎁 보상 확인 (10초당 0.1 WH)"):
                st.session_state.balance += 0.1
                st.success("보상 지급 완료!")

# --- TAB 4: LUCKY DICE (주사위 애니메이션 복구) ---
with tabs[3]:
    if not st.session_state.wallet_address:
        st.error("지갑을 연결하세요.")
    else:
        st.markdown('<div class="dice-card">', unsafe_allow_html=True)
        st.markdown('<h3>🎰 LUCKY DICE 🎰</h3>', unsafe_allow_html=True)
        
        # 주사위 애니메이션 (굴러가는 모습)
        if st.session_state.last_dice_roll == 'rolling':
            st.markdown('<p class="dice-num dice-animation">🎲</p>', unsafe_allow_html=True)
        elif 'last_res' in st.session_state and st.session_state.last_res is not None:
            st.markdown(f'<p class="dice-num">{st.session_state.last_res}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="dice-num">🎲</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        bet = st.select_slider("배팅액 선택 (WH)", options=[1, 5, 10, 50, 100, 500])
        
        if st.button("ROLL THE DICE!!", use_container_width=True):
            if st.session_state.balance >= bet:
                st.session_state.balance -= bet
                st.session_state.treasury += bet
                
                # 애니메이션을 위해 먼저 'rolling' 상태를 표시
                st.session_state.last_dice_roll = 'rolling'
                st.rerun() # 화면을 다시 그려 애니메이션 시작
                
                # 실제 주사위 결과 계산 (애니메이션 후 보여줌)
                time.sleep(1.5) # 애니메이션 시간
                
                if st.session_state.is_first_dice:
                    res = 6
                    st.session_state.is_first_dice = False
                else:
                    res = random.randint(1, 6)
                
                st.session_state.last_res = res
                st.session_state.last_dice_roll = None # 애니메이션 종료
                if res >= 5:
                    win = bet * 1.9
                    st.session_state.balance += win
                    st.session_state.treasury -= win
                    st.balloons()
                st.rerun() # 최종 결과 표시
            else: st.error("잔액이 부족합니다.")

# --- TAB 5: RPG HERO (새로운 RPG 게임 추가) ---
with tabs[4]:
    st.markdown("### 🐲 HERO'S JOURNEY (RPG FUSION)")
    st.info("같은 레벨 영웅 2개를 합성하여 다음 레벨 영웅을 만드세요!")

    HERO_IMAGES = {
        1: "https://img.icons8.com/color/96/slime.png", # 슬라임
        2: "https://img.icons8.com/color/96/goblin.png", # 고블린
        3: "https://img.icons8.com/color/96/orc.png",    # 오크
        4: "https://img.icons8.com/color/96/centaur.png", # 켄타우로스
        5: "https://img.icons8.com/color/96/dragon.png", # 드래곤
        # ... 추가 레벨 이미지 (총 1000레벨까지 이미지 URL 정의)
        # 예시: 1000레벨 이미지는 운영자님이 추가해주세요.
        1000: "https://img.icons8.com/ultraviolet/80/crown.png" # 1000레벨 최종 영웅
    }
    
    HERO_NAMES = {
        1: "슬라임", 2: "고블린", 3: "오크", 4: "켄타우로스", 5: "드래곤",
        1000: "마스터 영웅"
    }

    if not st.session_state.wallet_address:
        st.error("지갑을 연결해야 영웅을 생성하고 관리할 수 있습니다.")
    else:
        st.markdown("---")
        st.subheader("나의 영웅 컬렉션")
        
        # 보유 영웅 표시
        if st.session_state.heroes:
            sorted_heroes = sorted(st.session_state.heroes.items())
            for level, count in sorted_heroes:
                if count > 0:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        st.markdown(f'<div class="hero-card"><img src="{HERO_IMAGES.get(level, HERO_IMAGES[1])}" class="hero-image"><p>Lv.{level} {HERO_NAMES.get(level, "미지의 존재")}</p></div>', unsafe_allow_html=True)
                    with col2:
                        st.write(f"보유 개수: **{count}개**")
                    with col3:
                        if level < 1000 and count >= 2: # 1000레벨 미만이고 2개 이상일 때 합성 버튼
                            if st.button(f"합성 (Lv.{level} ➡️ Lv.{level+1})", key=f"fuse_{level}", use_container_width=True):
                                # 합성 애니메이션 효과
                                st.markdown('<div class="fusion-effect" style="color:#FFD700; font-size:30px;">✨ FUSION! ✨</div>', unsafe_allow_html=True)
                                time.sleep(0.5) # 효과를 보여줄 시간
                                
                                st.session_state.heroes[level] -= 2
                                st.session_state.heroes[level+1] = st.session_state.heroes.get(level+1, 0) + 1
                                st.success(f"Lv.{level} 영웅 2개가 Lv.{level+1} {HERO_NAMES.get(level+1, '미지의 존재')}으로 합성되었습니다!")
                                st.rerun()
                        elif level == 1000 and count > 0:
                             st.success("최고 레벨 영웅을 보유중입니다!")
                        else:
                            st.write("") # 공간 맞춤용

        st.markdown("---")
        st.subheader("영웅 생성")
        cost_per_hero = 100 # 영웅 1개 생성 비용
        st.write(f"영웅 1개 생성 비용: **{cost_per_hero} WH**")
        
        if st.button(f"Lv.1 {HERO_NAMES[1]} 생성", use_container_width=True):
            if st.session_state.balance >= cost_per_hero:
                st.session_state.balance -= cost_per_hero
                st.session_state.heroes[1] = st.session_state.heroes.get(1, 0) + 1
                st.balloons()
                st.success(f"Lv.1 {HERO_NAMES[1]} 이 생성되었습니다!")
                st.rerun()
            else:
                st.error("WH 잔액이 부족합니다.")

# --- TAB 6: ADMIN (관리자 탭 복구) ---
if st.session_state.wallet_address == OWNER_WALLET:
    with tabs[5]: # 0부터 시작하므로 5번 인덱스
        st.subheader("👑 MASTER PANEL")
        st.metric("금고 누적 수익 (TREASURY)", f"{st.session_state.treasury:,.2f} WH")
        st.write("---")
        st.subheader("유저 자산 관리 (비밀)")
        st.json(st.session_state.heroes) # 모든 유저의 영웅 정보 (테스트용)

        if st.button("모든 영웅 초기화", help="이 버튼을 누르면 모든 유저의 영웅 정보가 초기화됩니다.", type="secondary"):
            st.session_state.heroes = {}
            st.success("모든 영웅 정보가 초기화되었습니다.")
            st.rerun()
