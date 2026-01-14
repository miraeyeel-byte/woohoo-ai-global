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
st.set_page_config(page_title="WOOHOO GLOBAL V19.2", layout="wide")
DB_PATH = "woohoo_v19_2_final.db"

# [2. 16개국어 풀 데이터 (생략 없음)]
LANG = {
    "🇰🇷 한국어": {
        "title": "WOOHOO 보안 플랫폼",
        "tab_sec": "🛡️ 보안 센터", "tab_game": "🚨 범인 체포", "tab_inv": "📦 보관함", "tab_rank": "🏆 명예의 전당",
        "wallet_con": "지갑 연결", "wallet_dis": "연결 해제", "balance": "자산", "total_profit": "누적 수익",
        "sec_btn": "💰 매수 시도", "sec_warn": "주소를 입력하세요.", "sec_safe": "✅ 안전 (점수: {score})", "sec_danger": "🚨 [경고] 위험 점수 {score}!", "sec_block": "🚫 차단됨!",
        "game_desc": "비용을 지불하고 체포합니다. 운이 좋으면 고레벨 등장!", "pull_1": "1회 체포", "pull_5": "5회 체포", "pull_10": "10회 체포",
        "inv_empty": "보관함이 비어있습니다.", "fuse_all": "🧬 일괄 합성", "jail_all": "🔒 일괄 감옥",
        "btn_yes": "✅ 승인", "btn_no": "❌ 취소",
        "toast_catch": "{n}명 체포 완료!", "err_bal": "잔액이 부족합니다.",
        "fuse_confirm": "총 {n}회 합성을 진행합니까?", "jail_confirm": "모두 감옥으로 보내고 보상을 받겠습니까?",
        "toast_fuse": "일괄 합성 완료!", "toast_jail": "이송 완료! +{r:.4f} SOL",
        "rank_title": "명예의 전당", "rank_desc": "범죄자를 감옥에 보내 가장 많은 수익을 낸 헌터",
        "name_1": "소매치기", "name_10": "양아치", "name_50": "조직 간부", "name_90": "테러리스트", "name_100": "세계관 최강자"
    },
    "🇺🇸 English": {
        "title": "WOOHOO SECURITY PLATFORM",
        "tab_sec": "🛡️ Security", "tab_game": "🚨 Arrest", "tab_inv": "📦 Inventory", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Connect Wallet", "wallet_dis": "Disconnect", "balance": "Balance", "total_profit": "Total Profit",
        "sec_btn": "💰 Buy (Sim)", "sec_warn": "Enter Address.", "sec_safe": "✅ Safe (Score: {score})", "sec_danger": "🚨 High Risk {score}!", "sec_block": "🚫 Blocked!",
        "game_desc": "Pay bounty to arrest criminals. Lucky drops enabled.", "pull_1": "Arrest x1", "pull_5": "Arrest x5", "pull_10": "Arrest x10",
        "inv_empty": "Inventory Empty.", "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "btn_yes": "✅ Yes", "btn_no": "❌ No",
        "toast_catch": "{n} Captured!", "err_bal": "Insufficient Balance.",
        "fuse_confirm": "Proceed with {n} fusions?", "jail_confirm": "Send all to prison?",
        "toast_fuse": "Fusion Complete!", "toast_jail": "Sent to Prison! +{r:.4f} SOL",
        "rank_title": "Hall of Fame", "rank_desc": "Top Hunters by Realized Profit",
        "name_1": "Pickpocket", "name_10": "Thug", "name_50": "Gang Boss", "name_90": "Terrorist", "name_100": "Overlord"
    },
    "🇯🇵 日本語": {
        "title": "WOOHOO セキュリティ",
        "tab_sec": "🛡️ セキュリティ", "tab_game": "🚨 逮捕", "tab_inv": "📦 保管庫", "tab_rank": "🏆 殿堂入り",
        "wallet_con": "接続", "wallet_dis": "切断", "balance": "残高", "total_profit": "累積収益",
        "sec_btn": "💰 購入試行", "sec_warn": "アドレスを入力。", "sec_safe": "✅ 安全 (点数: {score})", "sec_danger": "🚨 [警告] 危険度 {score}!", "sec_block": "🚫 遮断!",
        "game_desc": "費用を払って逮捕します。高レベル出現のチャンス。", "pull_1": "1回逮捕", "pull_5": "5回逮捕", "pull_10": "10回逮捕",
        "inv_empty": "保管庫は空です。", "fuse_all": "🧬 一括合成", "jail_all": "🔒 一括送獄",
        "btn_yes": "✅ 承認", "btn_no": "❌ キャンセル",
        "toast_catch": "{n}名 逮捕完了!", "err_bal": "残高不足です。",
        "fuse_confirm": "合計 {n} 回の合成を行いますか？", "jail_confirm": "全員を刑務所に送りますか？",
        "toast_fuse": "合成完了!", "toast_jail": "送獄完了! +{r:.4f} SOL",
        "rank_title": "名誉の殿堂", "rank_desc": "最も多くの収益を上げたハンター",
        "name_1": "スリ", "name_10": "チンピラ", "name_50": "幹部", "name_90": "テロリスト", "name_100": "絶対悪"
    },
    "🇨🇳 中文": {
        "title": "WOOHOO 安全平台",
        "tab_sec": "🛡️ 安全中心", "tab_game": "🚨 逮捕", "tab_inv": "📦 仓库", "tab_rank": "🏆 名人堂",
        "wallet_con": "连接钱包", "wallet_dis": "断开", "balance": "余额", "total_profit": "累计收益",
        "sec_btn": "💰 尝试购买", "sec_warn": "请输入地址。", "sec_safe": "✅ 安全 (分数: {score})", "sec_danger": "🚨 [警告] 风险 {score}!", "sec_block": "🚫 已拦截!",
        "game_desc": "支付费用逮捕罪犯。有机会获得高等级。", "pull_1": "逮捕 1次", "pull_5": "逮捕 5次", "pull_10": "逮捕 10次",
        "inv_empty": "仓库为空。", "fuse_all": "🧬 一键合成", "jail_all": "🔒 一键入狱",
        "btn_yes": "✅ 确认", "btn_no": "❌ 取消",
        "toast_catch": "成功逮捕 {n}名!", "err_bal": "余额不足。",
        "fuse_confirm": "确认进行 {n} 次合成？", "jail_confirm": "全部送入监狱？",
        "toast_fuse": "合成完成!", "toast_jail": "入狱完成! +{r:.4f} SOL",
        "rank_title": "名人堂", "rank_desc": "收益最高的猎人",
        "name_1": "扒手", "name_10": "流氓", "name_50": "干部", "name_90": "恐怖分子", "name_100": "终极BOSS"
    },
    "🇷🇺 Русский": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Защита", "tab_game": "🚨 Арест", "tab_inv": "📦 Инвентарь", "tab_rank": "🏆 Рейтинг",
        "wallet_con": "Подключить", "wallet_dis": "Выйти", "balance": "Баланс", "total_profit": "Прибыль",
        "sec_btn": "💰 Купить", "sec_warn": "Введите адрес.", "sec_safe": "✅ Безопасно ({score})", "sec_danger": "🚨 Опасно {score}!", "sec_block": "🚫 Блок!",
        "game_desc": "Платите за арест.", "pull_1": "Арест x1", "pull_5": "Арест x5", "pull_10": "Арест x10",
        "inv_empty": "Пусто.", "fuse_all": "🧬 Синтез", "jail_all": "🔒 В тюрьму", "btn_yes": "✅ Да", "btn_no": "❌ Нет",
        "name_1": "Карманник", "name_100": "Владыка"
    },
    "🇻🇳 Tiếng Việt": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Bảo mật", "tab_game": "🚨 Bắt giữ", "tab_inv": "📦 Kho", "tab_rank": "🏆 Xếp hạng",
        "wallet_con": "Kết nối", "wallet_dis": "Ngắt", "balance": "Số dư", "total_profit": "Lợi nhuận",
        "sec_btn": "💰 Mua", "sec_warn": "Nhập địa chỉ.", "sec_safe": "✅ An toàn ({score})", "sec_danger": "🚨 Rủi ro {score}!", "sec_block": "🚫 Chặn!",
        "game_desc": "Trả tiền để bắt.", "pull_1": "Bắt x1", "pull_5": "Bắt x5", "pull_10": "Bắt x10",
        "inv_empty": "Trống.", "fuse_all": "🧬 Hợp nhất", "jail_all": "🔒 Vào tù", "btn_yes": "✅ Có", "btn_no": "❌ Không",
        "name_1": "Móc túi", "name_100": "Chúa tể"
    },
    "🇹🇭 ภาษาไทย": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ ความปลอดภัย", "tab_game": "🚨 จับกุม", "tab_inv": "📦 คลัง", "tab_rank": "🏆 อันดับ",
        "wallet_con": "เชื่อมต่อ", "wallet_dis": "ตัด", "balance": "ยอดคงเหลือ", "total_profit": "กำไร",
        "sec_btn": "💰 ซื้อ", "sec_warn": "ป้อนที่อยู่", "sec_safe": "✅ ปลอดภัย ({score})", "sec_danger": "🚨 อันตราย {score}!", "sec_block": "🚫 บล็อค!",
        "game_desc": "จับกุมอาชญากร", "pull_1": "จับ x1", "pull_5": "จับ x5", "pull_10": "จับ x10",
        "inv_empty": "ว่างเปล่า", "fuse_all": "🧬 ผสม", "jail_all": "🔒 เข้าคุก", "btn_yes": "✅ ใช่", "btn_no": "❌ ไม่",
        "name_1": "นักล้วงกระเป๋า", "name_100": "จอมมาร"
    },
    "🇮🇱 עברית": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ אבטחה", "tab_game": "🚨 מעצר", "tab_inv": "📦 מלאי", "tab_rank": "🏆 דירוג",
        "wallet_con": "חבר", "wallet_dis": "התנתק", "balance": "יתרה", "total_profit": "רווח",
        "sec_btn": "💰 קנה", "sec_warn": "כתובת", "sec_safe": "✅ בטוח ({score})", "sec_danger": "🚨 סכנה {score}!", "sec_block": "🚫 נחסם!",
        "game_desc": "עצור פושעים.", "pull_1": "מעצר x1", "pull_5": "מעצר x5", "pull_10": "מעצר x10",
        "inv_empty": "ריק", "fuse_all": "🧬 למזג", "jail_all": "🔒 לכלא", "btn_yes": "✅ כן", "btn_no": "❌ לא",
        "name_1": "כייס", "name_100": "אדון"
    },
    "🇵🇭 Tagalog": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Seguridad", "tab_game": "🚨 Huliin", "tab_inv": "📦 Imbentaryo", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Ikonekta", "wallet_dis": "Diskonekta", "balance": "Balanse", "total_profit": "Kita",
        "sec_btn": "💰 Bumili", "sec_warn": "Address", "sec_safe": "✅ Ligtas ({score})", "sec_danger": "🚨 Panganib {score}!", "sec_block": "🚫 Hinarang!",
        "inv_empty": "Walang laman", "fuse_all": "🧬 Pagsamahin", "jail_all": "🔒 I-kulong", "btn_yes": "✅ Oo", "btn_no": "❌ Hindi",
        "name_1": "Mandurukot", "name_100": "Overlord"
    },
    "🇲🇾 Melayu": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Keselamatan", "tab_game": "🚨 Tangkap", "tab_inv": "📦 Inventori", "tab_rank": "🏆 Kedudukan",
        "wallet_con": "Sambung", "wallet_dis": "Putus", "balance": "Baki", "total_profit": "Keuntungan",
        "sec_btn": "💰 Beli", "sec_warn": "Alamat", "sec_safe": "✅ Selamat ({score})", "sec_danger": "🚨 Bahaya {score}!", "sec_block": "🚫 Sekat!",
        "inv_empty": "Kosong", "fuse_all": "🧬 Gabung", "jail_all": "🔒 Penjara", "btn_yes": "✅ Ya", "btn_no": "❌ Tidak",
        "name_1": "Pencopet", "name_100": "Raja"
    },
    "🇮🇩 Indonesia": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Keamanan", "tab_game": "🚨 Tangkap", "tab_inv": "📦 Inventaris", "tab_rank": "🏆 Peringkat",
        "wallet_con": "Konek", "wallet_dis": "Putus", "balance": "Saldo", "total_profit": "Profit",
        "sec_btn": "💰 Beli", "sec_warn": "Alamat", "sec_safe": "✅ Aman ({score})", "sec_danger": "🚨 Bahaya {score}!", "sec_block": "🚫 Blokir!",
        "inv_empty": "Kosong", "fuse_all": "🧬 Gabung", "jail_all": "🔒 Penjara", "btn_yes": "✅ Ya", "btn_no": "❌ Tidak",
        "name_1": "Copet", "name_100": "Raja Iblis"
    },
    "🇹🇷 Türkçe": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Güvenlik", "tab_game": "🚨 Tutukla", "tab_inv": "📦 Envanter", "tab_rank": "🏆 Liste",
        "wallet_con": "Bağla", "wallet_dis": "Çıkış", "balance": "Bakiye", "total_profit": "Kazanç",
        "sec_btn": "💰 Satın Al", "sec_warn": "Adres", "sec_safe": "✅ Güvenli ({score})", "sec_danger": "🚨 Risk {score}!", "sec_block": "🚫 Engel!",
        "inv_empty": "Boş", "fuse_all": "🧬 Birleştir", "jail_all": "🔒 Hapis", "btn_yes": "✅ Evet", "btn_no": "❌ Hayır",
        "name_1": "Yankesici", "name_100": "Lord"
    },
    "🇵🇹 Português": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Segurança", "tab_game": "🚨 Prisão", "tab_inv": "📦 Inventário", "tab_rank": "🏆 Hall",
        "wallet_con": "Conectar", "wallet_dis": "Sair", "balance": "Saldo", "total_profit": "Lucro",
        "sec_btn": "💰 Comprar", "sec_warn": "Endereço", "sec_safe": "✅ Seguro ({score})", "sec_danger": "🚨 Risco {score}!", "sec_block": "🚫 Bloqueado!",
        "inv_empty": "Vazio", "fuse_all": "🧬 Fundir", "jail_all": "🔒 Prender", "btn_yes": "✅ Sim", "btn_no": "❌ Não",
        "name_1": "Batedor", "name_100": "Lorde"
    },
    "🇪🇸 Español": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Seguridad", "tab_game": "🚨 Arresto", "tab_inv": "📦 Inventario", "tab_rank": "🏆 Fama",
        "wallet_con": "Conectar", "wallet_dis": "Salir", "balance": "Saldo", "total_profit": "Ganancia",
        "sec_btn": "💰 Comprar", "sec_warn": "Dirección", "sec_safe": "✅ Seguro ({score})", "sec_danger": "🚨 Riesgo {score}!", "sec_block": "🚫 Bloqueado!",
        "inv_empty": "Vacío", "fuse_all": "🧬 Fusionar", "jail_all": "🔒 Encarcelar", "btn_yes": "✅ Sí", "btn_no": "❌ No",
        "name_1": "Carterista", "name_100": "Señor"
    },
    "🇩🇪 Deutsch": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Sicherheit", "tab_game": "🚨 Festnahme", "tab_inv": "📦 Inventar", "tab_rank": "🏆 Ruhm",
        "wallet_con": "Verbinden", "wallet_dis": "Trennen", "balance": "Guthaben", "total_profit": "Gewinn",
        "sec_btn": "💰 Kaufen", "sec_warn": "Adresse", "sec_safe": "✅ Sicher ({score})", "sec_danger": "🚨 Risiko {score}!", "sec_block": "🚫 Blockiert!",
        "inv_empty": "Leer", "fuse_all": "🧬 Fusion", "jail_all": "🔒 Einsperren", "btn_yes": "✅ Ja", "btn_no": "❌ Nein",
        "name_1": "Dieb", "name_100": "Overlord"
    },
    "🇫🇷 Français": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Sécurité", "tab_game": "🚨 Arrêt", "tab_inv": "📦 Inventaire", "tab_rank": "🏆 Panthéon",
        "wallet_con": "Connecter", "wallet_dis": "Déconnecter", "balance": "Solde", "total_profit": "Profit",
        "sec_btn": "💰 Acheter", "sec_warn": "Adresse", "sec_safe": "✅ Sûr ({score})", "sec_danger": "🚨 Risque {score}!", "sec_block": "🚫 Bloqué!",
        "inv_empty": "Vide", "fuse_all": "🧬 Fusion", "jail_all": "🔒 Prison", "btn_yes": "✅ Oui", "btn_no": "❌ Non",
        "name_1": "Pickpocket", "name_100": "Seigneur"
    }
}

# [3. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, total_profit REAL DEFAULT 0.0)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, total_profit) VALUES ('Operator_Admin', 10.0, 0.0)")
        conn.commit()
init_db()

# [4. 유틸리티 함수 (안전 번역)]
if 'lang' not in st.session_state: st.session_state.lang = "🇰🇷 한국어"

def T(key, **kwargs):
    # 1. 선택된 언어에서 찾기
    lang_data = LANG.get(st.session_state.lang, {})
    text = lang_data.get(key)
    
    # 2. 없으면 영어에서 찾기 (Fallback)
    if not text:
        text = LANG["🇺🇸 English"].get(key)
        
    # 3. 그래도 없으면 키값 그대로 반환
    if not text:
        text = key
        
    if kwargs: return text.format(**kwargs)
    return text

def get_criminal_name(lvl):
    prefix = f"Lv.{lvl} "
    if lvl == 1: name = T("name_1")
    elif lvl <= 10: name = T("name_10")
    elif lvl <= 50: name = T("name_50")
    elif lvl <= 90: name = T("name_90")
    else: name = T("name_100")
    return f"{prefix}{name}"

def get_img_url(lvl):
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=Crime{lvl}&backgroundColor=1a1a1a"

# [5. 보안 및 게임 로직]
def process_security_action(token_address, user_tier):
    risk_score = random.randint(0, 100)
    if user_tier.startswith("BASIC"):
        if risk_score >= 70: st.warning(T("sec_danger", score=risk_score)); return
    elif user_tier.startswith("PRO"):
        if risk_score >= 70: st.error(T("sec_block", score=risk_score)); return
    st.success(T("sec_safe", score=risk_score))

def get_user():
    if not st.session_state.wallet: return None, 0.0, 0.0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance, total_profit FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0, 0.0)

def update_balance(d):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (d, st.session_state.wallet)); conn.commit()

def update_inventory(l, d):
    with get_db() as conn:
        c = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, l)).fetchone()
        n = (c[0] + d) if c else d
        if n < 0: n = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, l, n)); conn.commit()

def record_profit(amount):
    with get_db() as conn:
        conn.execute("UPDATE users SET total_profit = total_profit + ? WHERE wallet=?", (amount, st.session_state.wallet)); conn.commit()

def get_inv():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())

def gacha_pull(n):
    levels = list(range(1, 101))
    weights = [1000 / (1.05 ** i) for i in levels]
    return random.choices(levels, weights=weights, k=n)

# [6. 스타일링]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700&display=swap');
    .stApp { background-color: #050505; color: #fff; font-family: 'Noto Sans KR', sans-serif; }
    h1, h2, h3, h4, p, div, label, span { color: #fff !important; text-shadow: 2px 2px 4px #000 !important; }
    
    /* Tier 선택 라디오 버튼 가독성 패치 */
    div[role="radiogroup"] label {
        color: #FFD700 !important; font-size: 1.2rem !important;
        background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 5px; margin-bottom: 5px;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #222; border: 1px solid #444; color: #aaa; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; font-weight: bold; border: none; text-shadow: none !important; }
    .card-box { border: 2px solid #FFD700; background: #111; padding: 10px; text-align: center; margin-bottom: 10px; box-shadow: 5px 5px 0px #333; }
    .neon { color: #66fcf1 !important; font-weight: bold; }
    .gold { color: #FFD700 !important; font-weight: bold; }
    .red { color: #ff4b4b !important; font-weight: bold; }
    .stButton button { width: 100%; border-radius: 0px; font-weight: bold; border: 2px solid #66fcf1; background: #000; color: #66fcf1; }
    .stButton button:hover { background: #66fcf1; color: #000; }
</style>
""", unsafe_allow_html=True)

# [7. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'user_tier' not in st.session_state: st.session_state.user_tier = "BASIC (0.01 SOL)"
if 'confirm_fuse_all' not in st.session_state: st.session_state.confirm_fuse_all = False
if 'confirm_jail_all' not in st.session_state: st.session_state.confirm_jail_all = False

# [8. 메인 UI]
with st.sidebar:
    st.title("🌐 Language")
    lang_list = list(LANG.keys())
    # 현재 선택된 언어의 인덱스 찾기 (없으면 0번)
    try: idx = lang_list.index(st.session_state.lang)
    except: idx = 0
    selected_lang = st.selectbox("Select", lang_list, index=idx)
    if selected_lang != st.session_state.lang: st.session_state.lang = selected_lang; st.rerun()
    
    st.divider()
    st.header(f"🔐 {T('wallet_con')}")
    if not st.session_state.wallet:
        if st.button(T("wallet_con"), key="con"): st.session_state.wallet = "Operator_Admin"; st.rerun()
    else:
        u_wallet, u_bal, u_prof = get_user()
        st.success(f"User: {u_wallet}")
        st.metric(T("balance"), f"{u_bal:.4f} SOL")
        st.metric(T("total_profit"), f"{u_prof:.4f} SOL")
        if st.button(T("wallet_dis"), key="dis"): st.session_state.wallet = None; st.rerun()

st.title(T("title"))

if not st.session_state.wallet:
    st.info("Wallet Connect Required.")
    st.stop()

tabs = st.tabs([T("tab_sec"), T("tab_game"), T("tab_inv"), T("tab_rank")])

# === 1. 보안 센터 ===
with tabs[0]:
    st.subheader(T("tab_sec"))
    st.markdown(f"**Tier:**")
    tier = st.radio("Select", ["BASIC (0.01 SOL)", "PRO (0.1 SOL)"], label_visibility="collapsed")
    st.session_state.user_tier = tier
    st.divider()
    token = st.text_input("Address", placeholder="Solana Address...")
    if st.button(T("sec_btn"), key="btn_scan"):
        if not token: st.warning(T("sec_warn"))
        else: process_security_action(token, st.session_state.user_tier)

# === 2. 범인 체포 ===
with tabs[1]:
    st.subheader(T("tab_game"))
    st.caption(T("game_desc"))
    
    def run_gacha(cost, n):
        _, bal, _ = get_user()
        if bal < cost: st.error(T("err_bal")); return
        update_balance(-cost)
        res = gacha_pull(n)
        for r in res: update_inventory(r, 1)
        st.toast(T("toast_catch", n=n), icon="🚨")
        cols = st.columns(min(n, 5))
        for i, lvl in enumerate(res[:5]):
            with cols[i]:
                st.markdown(f"<div class='card-box'><img src='{get_img_url(lvl)}' width='50'><div class='neon'>Lv.{lvl}</div></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button(f"{T('pull_1')} (0.01 SOL)", key="gp1"): run_gacha(0.01, 1)
    with c2: 
        if st.button(f"{T('pull_5')} (0.05 SOL)", key="gp5"): run_gacha(0.05, 5)
    with c3: 
        if st.button(f"{T('pull_10')} (0.10 SOL)", key="gp10"): run_gacha(0.10, 10)

# === 3. 보관함 ===
with tabs[2]:
    st.subheader(T("tab_inv"))
    inv = get_inv()
    if inv:
        bc1, bc2 = st.columns(2)
        total_fusions = sum([cnt // 2 for lvl, cnt in inv.items() if lvl < 100])
        with bc1:
            if not st.session_state.confirm_fuse_all:
                if st.button(f"{T('fuse_all')} ({total_fusions})", type="primary", disabled=total_fusions==0, key="b_fa"):
                    st.session_state.confirm_fuse_all = True; st.rerun()
            else:
                st.warning(T("fuse_confirm", n=total_fusions))
                c1, c2 = st.columns(2)
                if c1.button(T("btn_yes"), key="bfy"):
                    for lvl in sorted(inv.keys()):
                        f_cnt = inv[lvl] // 2
                        if f_cnt > 0 and lvl < 100: update_inventory(lvl, -(f_cnt*2)); update_inventory(lvl+1, f_cnt)
                    st.toast(T("toast_fuse"), icon="🧬"); st.session_state.confirm_fuse_all = False; st.rerun()
                if c2.button(T("btn_no"), key="bfn"): st.session_state.confirm_fuse_all = False; st.rerun()
        with bc2:
            if not st.session_state.confirm_jail_all:
                if st.button(T("jail_all"), key="b_ja"): st.session_state.confirm_jail_all = True; st.rerun()
            else:
                st.warning(T("jail_confirm"))
                c1, c2 = st.columns(2)
                if c1.button(T("btn_yes"), key="bjy"):
                    tr = 0
                    for lvl, cnt in inv.items():
                        if cnt > 0:
                            # 밸런스 패치: 1.05배율
                            r = cnt * (0.005 * (1.05**(lvl-1)))
                            update_inventory(lvl, -cnt); tr += r
                    update_balance(tr); record_profit(tr); st.toast(T("toast_jail", r=tr), icon="💰"); st.session_state.confirm_jail_all = False; st.rerun()
                if c2.button(T("btn_no"), key="bjn"): st.session_state.confirm_jail_all = False; st.rerun()

    st.divider()
    if not inv: st.info(T("inv_empty"))
    else:
        for lvl, count in sorted(inv.items(), reverse=True):
            if count > 0:
                with st.container():
                    c1, c2, c3 = st.columns([1, 2, 2])
                    with c1: st.image(get_img_url(lvl), width=60)
                    with c2: st.markdown(f"#### {get_criminal_name(lvl)}"); st.markdown(f"Count: <span class='neon'>{count}</span>", unsafe_allow_html=True)
                    with c3:
                        if count >= 2 and lvl < 100:
                            if st.button(f"🧬 (2->1)", key=f"kf_{lvl}"): 
                                update_inventory(lvl, -2); update_inventory(lvl+1, 1); st.toast("Success!", icon="✨"); st.rerun()
                        r = 0.005 * (1.05**(lvl-1))
                        if st.button(f"🔒 (+{r:.4f})", key=f"kj_{lvl}"): 
                            update_inventory(lvl, -1); update_balance(r); record_profit(r); st.rerun()
                st.markdown("---")

# === 4. 명예의 전당 ===
with tabs[3]:
    st.subheader(T("rank_title"))
    st.caption(T("rank_desc"))
    with get_db() as conn:
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0), IFNULL(total_profit, 0.0) FROM users ORDER BY total_profit DESC LIMIT 10").fetchall()
    for i, (w, b, p) in enumerate(ranks):
        medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        st.markdown(f"<div class='card-box' style='padding:15px; text-align:left; display:flex; justify-content:space-between;'><span style='font-size:1.2em'>{medal} <span class='neon'>{w}</span></span><span style='text-align:right'><span class='gold'>+{p:.4f} SOL</span> (Bal: {b:.4f})</span></div>", unsafe_allow_html=True)
