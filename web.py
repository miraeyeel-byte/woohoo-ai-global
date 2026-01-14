import streamlit as st
import pandas as pd
import numpy as np
import random
import sqlite3
import requests
import os
import time
from datetime import datetime, timedelta

# [1. 기본 설정]
st.set_page_config(page_title="WOOHOO GLOBAL SECURITY", layout="wide")
DB_PATH = "woohoo_v18_global.db"

# [2. 다국어 사전 (Translation Dictionary)]
LANG = {
    "KR": {
        "title": "WOOHOO 보안 플랫폼",
        "tab_security": "🛡️ 보안 센터", "tab_gacha": "🚨 범인 체포", "tab_inv": "📦 보관함 (관리)", "tab_fame": "🏆 명예의 전당",
        "connect_wallet": "🔌 지갑 연결", "disconnect": "연결 해제", "balance": "자산",
        "scan_title": "고급 토큰 스캐너", "scan_desc": "실시간 스캠/러그풀 감지 시스템",
        "scan_btn": "🔍 스캔 시작", "scan_warn": "⚠️ 위험 감지! (시뮬레이션)",
        "gacha_title": "범죄자 소탕 작전", "gacha_desc": "비용을 지불하고 범죄자를 체포합니다. 실패는 없습니다.",
        "pull_1": "1회 체포", "pull_5": "5회 체포", "pull_10": "10회 체포",
        "inv_title": "통합 보관 및 관리", "inv_desc": "범죄자를 합성하여 현상금을 높이거나, 감옥으로 이송하여 수익을 얻으세요.",
        "fuse_btn": "🧬 합성 (2개로 합성)", "jail_btn": "🔒 감옥 이송",
        "fuse_all": "🧬 일괄 합성 (모두)", "jail_all": "🔒 일괄 감옥 (모두)",
        "fuse_confirm": "⚠️ 총 {count}회의 합성을 진행하시겠습니까?",
        "jail_confirm": "⚠️ 총 {count}명을 감옥으로 보냅니다.\n예상 수익: {reward:.4f} SOL",
        "yes": "✅ 승인", "no": "❌ 취소",
        "fame_title": "명예의 전당", "fame_desc": "가장 많은 범죄자를 검거한 헌터 랭킹",
        "live_feed": "🔥 실시간 수감 현황", "just_now": "방금 전", "mins_ago": "분 전",
        "jail_msg": "이송 완료! +{reward:.4f} SOL", "fuse_msg": "합성 성공! 상위 레벨 획득",
        "buy_warn": "⚠️ {cost} SOL이 차감됩니다. 진행하시겠습니까?"
    },
    "EN": {
        "title": "WOOHOO SECURITY PLATFORM",
        "tab_security": "🛡️ Security", "tab_gacha": "🚨 Arrest", "tab_inv": "📦 Storage", "tab_fame": "🏆 Hall of Fame",
        "connect_wallet": "🔌 Connect Wallet", "disconnect": "Disconnect", "balance": "Balance",
        "scan_title": "Advanced Token Scanner", "scan_desc": "Real-time Scam/Rug-pull Detection",
        "scan_btn": "🔍 Scan", "scan_warn": "⚠️ High Risk Detected!",
        "gacha_title": "Criminal Takedown", "gacha_desc": "Pay bounty to arrest criminals. No failure.",
        "pull_1": "Arrest x1", "pull_5": "Arrest x5", "pull_10": "Arrest x10",
        "inv_title": "Inventory Management", "inv_desc": "Fuse criminals to upgrade or send them to prison for rewards.",
        "fuse_btn": "🧬 Fuse (Use 2)", "jail_btn": "🔒 To Prison",
        "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "fuse_confirm": "⚠️ Proceed with {count} fusions?",
        "jail_confirm": "⚠️ Sending {count} criminals to prison.\nEst. Reward: {reward:.4f} SOL",
        "yes": "✅ Confirm", "no": "❌ Cancel",
        "fame_title": "Hall of Fame", "fame_desc": "Top Hunters Ranking",
        "live_feed": "🔥 Live Prison Feed", "just_now": "Just now", "mins_ago": "m ago",
        "jail_msg": "Sent to Prison! +{reward:.4f} SOL", "fuse_msg": "Fusion Success!",
        "buy_warn": "⚠️ {cost} SOL will be deducted. Proceed?"
    },
    "JP": {
        "title": "WOOHOO セキュリティ",
        "tab_security": "🛡️ セキュリティ", "tab_gacha": "🚨 逮捕", "tab_inv": "📦 保管庫", "tab_fame": "🏆 殿堂入り",
        "connect_wallet": "🔌 ウォレット接続", "disconnect": "切断", "balance": "残高",
        "scan_title": "トークンスキャナー", "scan_desc": "リアルタイム詐欺検知システム",
        "scan_btn": "🔍 スキャン", "scan_warn": "⚠️ 危険を検知しました！",
        "gacha_title": "犯罪者掃討作戦", "gacha_desc": "費用を払って逮捕します。失敗はありません。",
        "pull_1": "1回逮捕", "pull_5": "5回逮捕", "pull_10": "10回逮捕",
        "inv_title": "保管と管理", "inv_desc": "合成して懸賞金を上げるか、刑務所に送って報酬を得ます。",
        "fuse_btn": "🧬 合成 (2体消費)", "jail_btn": "🔒 刑務所へ",
        "fuse_all": "🧬 一括合成", "jail_all": "🔒 一括送獄",
        "fuse_confirm": "⚠️ 合計 {count} 回の合成を行いますか？",
        "jail_confirm": "⚠️ 合計 {count} 名を刑務所に送ります。\n予想収益: {reward:.4f} SOL",
        "yes": "✅ 承認", "no": "❌ キャンセル",
        "fame_title": "名誉の殿堂", "fame_desc": "トップハンターランキング",
        "live_feed": "🔥 実況中継", "just_now": "たった今", "mins_ago": "分前",
        "jail_msg": "送獄完了！ +{reward:.4f} SOL", "fuse_msg": "合成成功！",
        "buy_warn": "⚠️ {cost} SOL 消費します。よろしいですか？"
    },
    "CN": {
        "title": "WOOHOO 安全平台",
        "tab_security": "🛡️ 安全中心", "tab_gacha": "🚨 逮捕行动", "tab_inv": "📦 仓库", "tab_fame": "🏆 名人堂",
        "connect_wallet": "🔌 连接钱包", "disconnect": "断开连接", "balance": "余额",
        "scan_title": "代币扫描器", "scan_desc": "实时诈骗检测系统",
        "scan_btn": "🔍 开始扫描", "scan_warn": "⚠️ 检测到高风险！",
        "gacha_title": "打击犯罪", "gacha_desc": "支付费用逮捕罪犯。必定成功。",
        "pull_1": "逮捕 1次", "pull_5": "逮捕 5次", "pull_10": "逮捕 10次",
        "inv_title": "库存管理", "inv_desc": "合成罪犯提升等级，或送入监狱获得奖励。",
        "fuse_btn": "🧬 合成 (消耗2个)", "jail_btn": "🔒 送入监狱",
        "fuse_all": "🧬 一键合成", "jail_all": "🔒 一键入狱",
        "fuse_confirm": "⚠️ 即将进行 {count} 次合成？",
        "jail_confirm": "⚠️ 将 {count} 名罪犯送入监狱。\n预计收益: {reward:.4f} SOL",
        "yes": "✅ 确认", "no": "❌ 取消",
        "fame_title": "名人堂", "fame_desc": "最强猎人排行榜",
        "live_feed": "🔥 实时动态", "just_now": "刚刚", "mins_ago": "分钟前",
        "jail_msg": "入狱完成！ +{reward:.4f} SOL", "fuse_msg": "合成成功！",
        "buy_warn": "⚠️ 将扣除 {cost} SOL。继续吗？"
    }
}

# [3. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("CREATE TABLE IF NOT EXISTS prison_log (id INTEGER PRIMARY KEY AUTOINCREMENT, wallet TEXT, lvl INTEGER, reward REAL, time_str TEXT)")
        c.execute("INSERT OR IGNORE INTO users VALUES ('Operator_Admin', 10.0)")
        conn.commit()
init_db()

# [4. 가라 데이터 (분위기 조성)]
def inject_fake_data():
    with get_db() as conn:
        cnt = conn.execute("SELECT COUNT(*) FROM prison_log").fetchone()[0]
        if cnt < 5:
            fake_wallets = ["Whale_0x", "SafeGuard", "AntiScam_Bot", "Sol_Hunter", "Justice_DAO"]
            for _ in range(10):
                fw = random.choice(fake_wallets)
                fl = random.randint(1, 10)
                fr = 0.005 * (1.2**(fl-1))
                ft = (datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("INSERT INTO prison_log (wallet, lvl, reward, time_str) VALUES (?, ?, ?, ?)", (fw, fl, fr, ft))
            conn.commit()
inject_fake_data()

# [5. 스타일링]
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3, h4, p, span, div { color: #e0e0e0; text-shadow: 1px 1px 2px #000; }
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border-radius: 4px; border: 1px solid #333; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; font-weight: bold; border: none; }
    .card-box {
        border: 2px solid #FFD700; background: linear-gradient(145deg, #111, #1a1a1a);
        padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.6);
    }
    .neon { color: #66fcf1; font-weight: bold; }
    .gold { color: #FFD700; font-weight: bold; }
    .stButton button { width: 100%; border-radius: 6px; font-weight: bold; }
    .live-ticker { background: #0f1115; border-left: 3px solid #FFD700; padding: 8px; font-size: 0.85em; margin-bottom: 5px; }
    .confirm-box { border: 2px solid #ff4b4b; background: #2d0000; padding: 15px; border-radius: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# [6. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'lang' not in st.session_state: st.session_state.lang = "KR"
# 일괄 처리용 세션 상태
if 'confirm_fuse_all' not in st.session_state: st.session_state.confirm_fuse_all = False
if 'confirm_jail_all' not in st.session_state: st.session_state.confirm_jail_all = False

# [7. 유틸리티 함수]
def T(key): return LANG[st.session_state.lang].get(key, key)
def get_user():
    if not st.session_state.wallet: return None, 0.0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0)
def update_balance(d):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (d, st.session_state.wallet)); conn.commit()
def get_inv():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())
def update_inv(l, d):
    with get_db() as conn:
        c = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, l)).fetchone()
        n = (c[0] + d) if c else d
        if n < 0: n = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, l, n)); conn.commit()

def gacha_pull(n):
    weights = [1000, 600, 300, 150, 80, 40, 20, 10, 5, 2] + [1]*10
    return random.choices(range(1, 21), weights=weights[:20], k=n)

def get_img(lvl):
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=SecurityRisk{lvl}&backgroundColor=1a1a1a"

# [8. 사이드바 & 언어 설정]
with st.sidebar:
    st.title("🌐 Language")
    st.session_state.lang = st.selectbox("Select Language", ["KR", "EN", "JP", "CN"])
    
    st.divider()
    st.header("🔐 Wallet")
    if not st.session_state.wallet:
        if st.button(T("connect_wallet")): st.session_state.wallet = "Operator_Admin"; st.rerun()
    else:
        u, b = get_user()
        st.success(f"User: {u}")
        st.metric(T("balance"), f"{b:.4f} SOL")
        if st.button(T("disconnect")): st.session_state.wallet = None; st.rerun()

# [9. 메인 UI]
st.title(T("title"))

# 실시간 티커
with get_db() as conn:
    logs = conn.execute("SELECT wallet, lvl, reward, time_str FROM prison_log ORDER BY id DESC LIMIT 3").fetchall()
if logs:
    for w, l, r, t in logs:
        st.markdown(f"<div class='live-ticker'><span class='gold'>[{w}]</span> jailed Lv.{l} -> <span class='neon'>+{r:.4f} SOL</span></div>", unsafe_allow_html=True)

if not st.session_state.wallet:
    st.warning("Please Connect Wallet First.")
    st.stop()

tabs = st.tabs([T("tab_security"), T("tab_gacha"), T("tab_inv"), T("tab_fame")])

# === 1. 보안 센터 ===
with tabs[0]:
    st.subheader(T("scan_title"))
    st.caption(T("scan_desc"))
    c1, c2 = st.columns([3, 1])
    c1.text_input("Token Address", placeholder="So1ana...")
    if c2.button(T("scan_btn")):
        with st.spinner("Scanning..."):
            time.sleep(1)
            st.warning(T("scan_warn"))

# === 2. 범인 체포 ===
with tabs[1]:
    st.subheader(T("gacha_title"))
    st.caption(T("gacha_desc"))
    
    def run_gacha(cost, n):
        _, bal = get_user()
        if bal < cost: st.error("Low Balance"); return
        
        # 확인 팝업 (세션 스테이트로 관리하면 복잡해지므로, 여기선 즉시 실행하되 토스트로 안내)
        # 운영자님이 확인 문구는 '감옥/합성'에 강조하셨으므로 여긴 속도감 있게 진행
        update_balance(-cost)
        res = gacha_pull(n)
        for r in res: update_inv(r, 1)
        st.toast(f"{n} Captured!", icon="🚨")
        
        # 결과 카드 (최대 5개)
        cols = st.columns(min(n, 5))
        for i, lvl in enumerate(res[:5]):
            with cols[i]:
                st.markdown(f"<div class='card-box'><img src='{get_img(lvl)}' width='50'><br><b>Lv.{lvl}</b></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(f"{T('pull_1')} (0.01 SOL)"): run_gacha(0.01, 1)
    with c2:
        if st.button(f"{T('pull_5')} (0.05 SOL)"): run_gacha(0.05, 5)
    with c3:
        if st.button(f"{T('pull_10')} (0.10 SOL)"): run_gacha(0.10, 10)

# === 3. 보관함 (일괄 처리 & 팝업) ===
with tabs[2]:
    st.subheader(T("inv_title"))
    st.caption(T("inv_desc"))
    
    inv = get_inv()
    
    # [일괄 기능 버튼]
    if inv:
        bc1, bc2 = st.columns(2)
        # 일괄 합성 로직
        total_fusions = sum([cnt // 2 for lvl, cnt in inv.items() if lvl < 20])
        
        with bc1:
            if not st.session_state.confirm_fuse_all:
                if st.button(T("fuse_all"), type="primary", disabled=total_fusions==0):
                    st.session_state.confirm_fuse_all = True
                    st.rerun()
            else:
                st.markdown(f"<div class='confirm-box'>{T('fuse_confirm').format(count=total_fusions)}</div>", unsafe_allow_html=True)
                y, n = st.columns(2)
                if y.button(T("yes"), key="y_f"):
                    for lvl in sorted(inv.keys()):
                        f_cnt = inv[lvl] // 2
                        if f_cnt > 0 and lvl < 20:
                            update_inv(lvl, -(f_cnt*2))
                            update_inv(lvl+1, f_cnt)
                    st.toast(T("fuse_msg"), icon="🧬")
                    st.session_state.confirm_fuse_all = False
                    st.rerun()
                if n.button(T("no"), key="n_f"):
                    st.session_state.confirm_fuse_all = False
                    st.rerun()

        # 일괄 감옥 로직
        total_jail_count = sum(inv.values())
        total_jail_reward = sum([cnt * (0.005 * (1.2**(lvl-1))) for lvl, cnt in inv.items()])
        
        with bc2:
            if not st.session_state.confirm_jail_all:
                if st.button(T("jail_all"), type="secondary", disabled=total_jail_count==0):
                    st.session_state.confirm_jail_all = True
                    st.rerun()
            else:
                st.markdown(f"<div class='confirm-box'>{T('jail_confirm').format(count=total_jail_count, reward=total_jail_reward)}</div>", unsafe_allow_html=True)
                y, n = st.columns(2)
                if y.button(T("yes"), key="y_j"):
                    for lvl, cnt in inv.items():
                        if cnt > 0:
                            r = cnt * (0.005 * (1.2**(lvl-1)))
                            update_inv(lvl, -cnt)
                            update_balance(r)
                            with get_db() as conn:
                                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                conn.execute("INSERT INTO prison_log (wallet, lvl, reward, time_str) VALUES (?, ?, ?, ?)", (st.session_state.wallet, 0, r, now))
                                conn.commit()
                    st.toast(T("jail_msg").format(reward=total_jail_reward), icon="💰")
                    st.session_state.confirm_jail_all = False
                    st.rerun()
                if n.button(T("no"), key="n_j"):
                    st.session_state.confirm_jail_all = False
                    st.rerun()

    st.divider()

    # 개별 목록 표시
    if not inv:
        st.info("Empty Inventory.")
    else:
        for lvl, count in sorted(inv.items()):
            if count > 0:
                with st.container():
                    c_img, c_info, c_act = st.columns([1, 2, 3])
                    with c_img:
                        st.image(get_img(lvl), width=60)
                    with c_info:
                        st.markdown(f"#### Lv.{lvl} Criminal")
                        st.markdown(f"Count: <span class='neon'>{count}</span>", unsafe_allow_html=True)
                    with c_act:
                        b1, b2 = st.columns(2)
                        # 개별 합성
                        if count >= 2:
                            if b1.button(f"{T('fuse_btn')}", key=f"f_{lvl}"):
                                update_inv(lvl, -2); update_inv(lvl+1, 1)
                                st.toast(T("fuse_msg"), icon="🧬"); st.rerun()
                        else:
                            b1.button(T("fuse_btn"), disabled=True, key=f"df_{lvl}")
                        
                        # 개별 감옥
                        r = 0.005 * (1.2**(lvl-1))
                        if b2.button(f"{T('jail_btn')} (+{r:.4f})", key=f"j_{lvl}"):
                            update_inv(lvl, -1); update_balance(r)
                            st.toast(T("jail_msg").format(reward=r), icon="💰"); st.rerun()
                st.markdown("---")

# === 4. 명예의 전당 ===
with tabs[3]:
    st.subheader(T("fame_title"))
    st.caption(T("fame_desc"))
    with get_db() as conn:
        ranks = conn.execute("SELECT wallet, balance FROM users ORDER BY balance DESC LIMIT 10").fetchall()
    for i, (w, b) in enumerate(ranks):
        st.markdown(f"<div class='card-box' style='padding:10px; text-align:left;'>#{i+1} {w} <span style='float:right;' class='gold'>{b:.4f} SOL</span></div>", unsafe_allow_html=True)
