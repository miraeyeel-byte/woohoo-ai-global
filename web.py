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
st.set_page_config(page_title="WOOHOO GLOBAL V19.5", layout="wide")
DB_PATH = "woohoo_v19_5_final.db"

# [2. 16개국어 풀 데이터 (절대 삭제 안 함)]
LANG = {
    "🇰🇷 한국어": {
        "title": "WOOHOO 보안 플랫폼", "tab_sec": "🛡️ 보안 센터", "tab_game": "🚨 범인 체포", "tab_inv": "📦 보관함", "tab_rank": "🏆 명예의 전당",
        "wallet_con": "지갑 연결", "wallet_dis": "연결 해제", "balance": "자산", "total_profit": "누적 수익", "max_lvl": "최고 레벨",
        "sec_btn": "💰 매수 시도", "sec_warn": "주소를 입력하세요.", "sec_safe": "✅ 안전 (점수: {score})", "sec_danger": "🚨 [경고] 위험 점수 {score}!", "sec_block": "🚫 차단됨!",
        "game_desc": "비용을 지불하고 체포합니다. (최대 Lv.100 출현 / Lv.1000은 합성)",
        "pull_1": "1회 체포", "pull_5": "5회 체포", "pull_10": "10회 체포",
        "inv_empty": "보관함이 비어있습니다.", "fuse_all": "🧬 일괄 합성", "jail_all": "🔒 일괄 감옥",
        "btn_yes": "✅ 승인", "btn_no": "❌ 취소", "toast_catch": "{n}명 체포 완료!", "err_bal": "잔액 부족.",
        "fuse_confirm": "총 {n}회 합성합니까?", "jail_confirm": "모두 감옥으로 보내시겠습니까?",
        "toast_fuse": "일괄 합성 완료!", "toast_jail": "이송 완료! +{r:.4f} SOL",
        "rank_title": "명예의 전당", "rank_desc": "수익을 실현한(판매한) 헌터만 기록됩니다.",
        "rank_empty": "아직 수익을 낸 헌터가 없습니다. 범인을 잡아 감옥으로 보내세요!",
        "name_1": "소매치기", "name_10": "양아치", "name_50": "조직 간부", "name_100": "세계관 최강자", "name_500": "차원의 지배자", "name_1000": "THE GOD"
    },
    "🇺🇸 English": {
        "title": "WOOHOO SECURITY", "tab_sec": "🛡️ Security", "tab_game": "🚨 Arrest", "tab_inv": "📦 Inventory", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Connect", "wallet_dis": "Disconnect", "balance": "Balance", "total_profit": "Profit", "max_lvl": "Max Lvl",
        "sec_btn": "💰 Buy", "sec_warn": "Enter Address.", "sec_safe": "✅ Safe ({score})", "sec_danger": "🚨 Risk {score}!", "sec_block": "🚫 Blocked!",
        "game_desc": "Arrest criminals. Max draw Lv.100.", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10",
        "inv_empty": "Empty.", "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "btn_yes": "✅ Yes", "btn_no": "❌ No", "toast_catch": "{n} Captured!", "err_bal": "Low Balance.",
        "fuse_confirm": "Fuse {n} times?", "jail_confirm": "Jail all?",
        "toast_fuse": "Fused!", "toast_jail": "Jailed! +{r:.4f} SOL",
        "rank_title": "Hall of Fame", "rank_desc": "Hunters with REALIZED profits only.",
        "rank_empty": "No hunters have sold criminals yet.",
        "name_1": "Pickpocket", "name_10": "Thug", "name_50": "Boss", "name_100": "Overlord", "name_500": "Ruler", "name_1000": "GOD"
    },
    "🇯🇵 日本語": {
        "title": "WOOHOO セキュリティ", "tab_sec": "🛡️ セキュリティ", "tab_game": "🚨 逮捕", "tab_inv": "📦 保管庫", "tab_rank": "🏆 殿堂入り",
        "wallet_con": "接続", "wallet_dis": "切断", "balance": "残高", "total_profit": "収益", "max_lvl": "最高Lv",
        "sec_btn": "💰 購入", "sec_warn": "アドレス入力", "sec_safe": "✅ 安全 ({score})", "sec_danger": "🚨 危険 {score}!", "sec_block": "🚫 遮断!",
        "game_desc": "費用を払って逮捕。最大Lv.100。", "pull_1": "1回", "pull_5": "5回", "pull_10": "10回",
        "inv_empty": "空です。", "fuse_all": "🧬 一括合成", "jail_all": "🔒 一括送獄",
        "btn_yes": "✅ はい", "btn_no": "❌ いいえ", "toast_catch": "{n}名 逮捕!", "err_bal": "残高不足",
        "fuse_confirm": "{n}回 合成しますか？", "jail_confirm": "全員送獄しますか？",
        "toast_fuse": "合成完了!", "toast_jail": "送獄完了! +{r:.4f} SOL",
        "rank_title": "名誉の殿堂", "rank_desc": "収益を確定させたハンターのみ表示",
        "rank_empty": "まだ収益を上げたハンターがいません。",
        "name_1": "スリ", "name_10": "チンピラ", "name_50": "幹部", "name_100": "絶対悪", "name_500": "支配者", "name_1000": "神"
    },
    "🇨🇳 中文": {
        "title": "WOOHOO 安全平台", "tab_sec": "🛡️ 安全中心", "tab_game": "🚨 逮捕", "tab_inv": "📦 仓库", "tab_rank": "🏆 名人堂",
        "wallet_con": "连接", "wallet_dis": "断开", "balance": "余额", "total_profit": "收益", "max_lvl": "最高等级",
        "sec_btn": "💰 购买", "sec_warn": "输入地址", "sec_safe": "✅ 安全 ({score})", "sec_danger": "🚨 风险 {score}!", "sec_block": "🚫 拦截!",
        "game_desc": "付费逮捕。最高Lv.100。", "pull_1": "1次", "pull_5": "5次", "pull_10": "10次",
        "inv_empty": "空。", "fuse_all": "🧬 一键合成", "jail_all": "🔒 一键入狱",
        "btn_yes": "✅ 是", "btn_no": "❌ 否", "toast_catch": "逮捕 {n}名!", "err_bal": "余额不足",
        "fuse_confirm": "合成 {n} 次？", "jail_confirm": "全部入狱？",
        "toast_fuse": "合成完成!", "toast_jail": "入狱完成! +{r:.4f} SOL",
        "rank_title": "名人堂", "rank_desc": "仅显示已获利的猎人",
        "rank_empty": "暂无猎人获利。",
        "name_1": "扒手", "name_10": "流氓", "name_50": "干部", "name_100": "魔王", "name_500": "主宰", "name_1000": "神"
    },
    "🇷🇺 Русский": {"title": "WOOHOO", "tab_sec": "Защита", "tab_game": "Арест", "tab_inv": "Инвентарь", "tab_rank": "Рейтинг", "wallet_con": "Вход", "wallet_dis": "Выход", "balance": "Баланс", "total_profit": "Доход", "max_lvl": "Макс.Ур", "sec_btn": "Купить", "game_desc": "Арест", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Пусто", "fuse_all": "Синтез", "jail_all": "Тюрьма", "btn_yes": "Да", "btn_no": "Нет", "rank_title": "Рейтинг", "rank_desc": "Только с прибылью", "rank_empty": "Нет данных", "name_1": "Вор", "name_1000": "БОГ"},
    "🇻🇳 Tiếng Việt": {"title": "WOOHOO", "tab_sec": "Bảo mật", "tab_game": "Bắt giữ", "tab_inv": "Kho", "tab_rank": "Xếp hạng", "wallet_con": "Kết nối", "wallet_dis": "Ngắt", "balance": "Số dư", "total_profit": "Lợi nhuận", "max_lvl": "Cấp cao", "sec_btn": "Mua", "game_desc": "Bắt giữ", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Trống", "fuse_all": "Hợp nhất", "jail_all": "Vào tù", "btn_yes": "Có", "btn_no": "Không", "rank_title": "Xếp hạng", "rank_desc": "Chỉ người có lợi nhuận", "rank_empty": "Chưa có dữ liệu", "name_1": "Móc túi", "name_1000": "THẦN"},
    "🇹🇭 ภาษาไทย": {"title": "WOOHOO", "tab_sec": "ความปลอดภัย", "tab_game": "จับกุม", "tab_inv": "คลัง", "tab_rank": "อันดับ", "wallet_con": "เชื่อมต่อ", "wallet_dis": "ออก", "balance": "ยอดเงิน", "total_profit": "กำไร", "max_lvl": "เวลสูงสุด", "sec_btn": "ซื้อ", "game_desc": "จับกุม", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "ว่าง", "fuse_all": "ผสม", "jail_all": "เข้าคุก", "btn_yes": "ใช่", "btn_no": "ไม่", "rank_title": "อันดับ", "rank_desc": "เฉพาะผู้ที่มีกำไร", "rank_empty": "ไม่มีข้อมูล", "name_1": "โจร", "name_1000": "พระเจ้า"},
    "🇮🇱 עברית": {"title": "WOOHOO", "tab_sec": "אבטחה", "tab_game": "מעצר", "tab_inv": "מלאי", "tab_rank": "דירוג", "wallet_con": "חבר", "wallet_dis": "נתק", "balance": "יתרה", "total_profit": "רווח", "max_lvl": "רמה", "sec_btn": "קנה", "game_desc": "מעצר", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "ריק", "fuse_all": "מזג", "jail_all": "כלא", "btn_yes": "כן", "btn_no": "לא", "rank_title": "דירוג", "rank_desc": "רווחים בלבד", "rank_empty": "אין נתונים", "name_1": "גנב", "name_1000": "אלוהים"},
    "🇵🇭 Tagalog": {"title": "WOOHOO", "tab_sec": "Seguridad", "tab_game": "Huliin", "tab_inv": "Imbentaryo", "tab_rank": "Ranggo", "wallet_con": "Ikonekta", "wallet_dis": "Alis", "balance": "Balanse", "total_profit": "Kita", "max_lvl": "Max Lvl", "sec_btn": "Bumili", "game_desc": "Huliin", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Wala", "fuse_all": "Pagsamahin", "jail_all": "Kulong", "btn_yes": "Oo", "btn_no": "Hindi", "rank_title": "Ranggo", "rank_desc": "May kita lang", "rank_empty": "Wala pang data", "name_1": "Mandurukot", "name_1000": "DIYOS"},
    "🇲🇾 Melayu": {"title": "WOOHOO", "tab_sec": "Keselamatan", "tab_game": "Tangkap", "tab_inv": "Inventori", "tab_rank": "Kedudukan", "wallet_con": "Sambung", "wallet_dis": "Putus", "balance": "Baki", "total_profit": "Untung", "max_lvl": "Tahap Maks", "sec_btn": "Beli", "game_desc": "Tangkap", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Kosong", "fuse_all": "Gabung", "jail_all": "Penjara", "btn_yes": "Ya", "btn_no": "Tidak", "rank_title": "Kedudukan", "rank_desc": "Hanya yang untung", "rank_empty": "Tiada data", "name_1": "Pencopet", "name_1000": "DEWA"},
    "🇮🇩 Indonesia": {"title": "WOOHOO", "tab_sec": "Keamanan", "tab_game": "Tangkap", "tab_inv": "Inventaris", "tab_rank": "Peringkat", "wallet_con": "Konek", "wallet_dis": "Putus", "balance": "Saldo", "total_profit": "Profit", "max_lvl": "Level Maks", "sec_btn": "Beli", "game_desc": "Tangkap", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Kosong", "fuse_all": "Gabung", "jail_all": "Penjara", "btn_yes": "Ya", "btn_no": "Tidak", "rank_title": "Peringkat", "rank_desc": "Hanya yang profit", "rank_empty": "Tidak ada data", "name_1": "Copet", "name_1000": "DEWA"},
    "🇹🇷 Türkçe": {"title": "WOOHOO", "tab_sec": "Güvenlik", "tab_game": "Tutukla", "tab_inv": "Envanter", "tab_rank": "Liste", "wallet_con": "Bağla", "wallet_dis": "Çık", "balance": "Bakiye", "total_profit": "Kazanç", "max_lvl": "Maks Sv", "sec_btn": "Satın Al", "game_desc": "Tutukla", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Boş", "fuse_all": "Birleştir", "jail_all": "Hapis", "btn_yes": "Evet", "btn_no": "Hayır", "rank_title": "Liste", "rank_desc": "Sadece kazananlar", "rank_empty": "Veri yok", "name_1": "Hırsız", "name_1000": "TANRI"},
    "🇵🇹 Português": {"title": "WOOHOO", "tab_sec": "Segurança", "tab_game": "Prisão", "tab_inv": "Inventário", "tab_rank": "Hall", "wallet_con": "Conectar", "wallet_dis": "Sair", "balance": "Saldo", "total_profit": "Lucro", "max_lvl": "Nível Máx", "sec_btn": "Comprar", "game_desc": "Prender", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Vazio", "fuse_all": "Fundir", "jail_all": "Prender", "btn_yes": "Sim", "btn_no": "Não", "rank_title": "Hall", "rank_desc": "Apenas com lucro", "rank_empty": "Sem dados", "name_1": "Ladrão", "name_1000": "DEUS"},
    "🇪🇸 Español": {"title": "WOOHOO", "tab_sec": "Seguridad", "tab_game": "Arresto", "tab_inv": "Inventario", "tab_rank": "Fama", "wallet_con": "Conectar", "wallet_dis": "Salir", "balance": "Saldo", "total_profit": "Ganancia", "max_lvl": "Nivel Máx", "sec_btn": "Comprar", "game_desc": "Arrestar", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Vacío", "fuse_all": "Fusionar", "jail_all": "Encarcelar", "btn_yes": "Sí", "btn_no": "No", "rank_title": "Fama", "rank_desc": "Solo con ganancias", "rank_empty": "Sin datos", "name_1": "Ladrón", "name_1000": "DIOS"},
    "🇩🇪 Deutsch": {"title": "WOOHOO", "tab_sec": "Sicherheit", "tab_game": "Festnahme", "tab_inv": "Inventar", "tab_rank": "Ruhm", "wallet_con": "Verbinden", "wallet_dis": "Trennen", "balance": "Guthaben", "total_profit": "Gewinn", "max_lvl": "Max Lvl", "sec_btn": "Kaufen", "game_desc": "Fangen", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Leer", "fuse_all": "Fusion", "jail_all": "Einsperren", "btn_yes": "Ja", "btn_no": "Nein", "rank_title": "Ruhm", "rank_desc": "Nur mit Gewinn", "rank_empty": "Keine Daten", "name_1": "Dieb", "name_1000": "GOTT"},
    "🇫🇷 Français": {"title": "WOOHOO", "tab_sec": "Sécurité", "tab_game": "Arrêt", "tab_inv": "Inventaire", "tab_rank": "Panthéon", "wallet_con": "Connecter", "wallet_dis": "Déconnecter", "balance": "Solde", "total_profit": "Profit", "max_lvl": "Niveau Max", "sec_btn": "Acheter", "game_desc": "Arrêter", "pull_1": "x1", "pull_5": "x5", "pull_10": "x10", "inv_empty": "Vide", "fuse_all": "Fusion", "jail_all": "Prison", "btn_yes": "Oui", "btn_no": "Non", "rank_title": "Panthéon", "rank_desc": "Seulement avec profit", "rank_empty": "Pas de données", "name_1": "Voleur", "name_1000": "DIEU"}
}

# [3. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, total_profit REAL DEFAULT 0.0, max_lvl INTEGER DEFAULT 0)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, total_profit, max_lvl) VALUES ('Operator_Admin', 1000.0, 0.0, 0)")
        conn.commit()
init_db()

# [4. 유틸리티]
if 'lang' not in st.session_state: st.session_state.lang = "🇰🇷 한국어"

def T(key, **kwargs):
    lang_dict = LANG.get(st.session_state.lang, LANG.get("🇺🇸 English", {}))
    text = lang_dict.get(key, LANG["🇺🇸 English"].get(key, key))
    if kwargs: return text.format(**kwargs)
    return text

def get_criminal_name(lvl):
    prefix = f"Lv.{lvl} "
    if lvl == 1: name = T("name_1")
    elif lvl < 10: name = T("name_10")
    elif lvl < 50: name = T("name_50")
    elif lvl < 100: name = f"Terrorist Lv.{lvl}"
    elif lvl == 100: name = T("name_100")
    elif lvl < 500: name = T("name_500")
    elif lvl < 1000: name = f"Chaos Lv.{lvl}"
    else: name = T("name_1000")
    return f"{prefix}{name}"

def get_img_url(lvl):
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=WoohooCrime{lvl}&backgroundColor=1a1a1a"

# [5. 게임 로직]
def process_security_action(token_address, user_tier):
    risk_score = random.randint(0, 100)
    if user_tier.startswith("BASIC"):
        if risk_score >= 70: st.warning(T("sec_danger", score=risk_score)); return
    elif user_tier.startswith("PRO"):
        if risk_score >= 70: st.error(T("sec_block", score=risk_score)); return
    st.success(T("sec_safe", score=risk_score))

def get_user():
    if not st.session_state.wallet: return None, 0.0, 0.0, 0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance, total_profit, max_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0, 0.0, 0)

def update_balance(d):
    with get_db() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE wallet=?", (d, st.session_state.wallet)); conn.commit()

def update_inventory(l, d):
    with get_db() as conn:
        c = conn.execute("SELECT count FROM inventory WHERE wallet=? AND lvl=?", (st.session_state.wallet, l)).fetchone()
        n = (c[0] + d) if c else d
        if n < 0: n = 0
        conn.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (st.session_state.wallet, l, n)); conn.commit()
    if d > 0:
        with get_db() as conn:
            curr = conn.execute("SELECT max_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()[0]
            if l > curr: conn.execute("UPDATE users SET max_lvl = ? WHERE wallet=?", (l, st.session_state.wallet)); conn.commit()

def record_profit(amount):
    with get_db() as conn:
        conn.execute("UPDATE users SET total_profit = total_profit + ? WHERE wallet=?", (amount, st.session_state.wallet)); conn.commit()

def get_inv():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())

def gacha_pull(n):
    levels = list(range(1, 101)) # 100까지만 나옴
    weights = [1000 / (1.05 ** i) for i in levels]
    return random.choices(levels, weights=weights, k=n)

def calculate_reward(lvl):
    if lvl <= 100: return 0.005 * (1.05**(lvl-1))
    else:
        base_100 = 0.005 * (1.05**99)
        return base_100 + ((lvl - 100) * 0.05)

# [6. 스타일링]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700&display=swap');
    .stApp { background-color: #050505; color: #fff; font-family: 'Noto Sans KR', sans-serif; }
    h1, h2, h3, h4, p, div, label, span { color: #fff !important; text-shadow: 2px 2px 4px #000 !important; }
    div[role="radiogroup"] label { color: #FFD700 !important; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px; }
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

# [7. 세션]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'user_tier' not in st.session_state: st.session_state.user_tier = "BASIC (0.01 SOL)"
if 'confirm_fuse_all' not in st.session_state: st.session_state.confirm_fuse_all = False
if 'confirm_jail_all' not in st.session_state: st.session_state.confirm_jail_all = False

# [8. 메인 UI]
with st.sidebar:
    st.title("🌐 Language")
    lang_list = list(LANG.keys())
    try: idx = lang_list.index(st.session_state.lang)
    except: idx = 0
    selected_lang = st.selectbox("Select", lang_list, index=idx)
    if selected_lang != st.session_state.lang: st.session_state.lang = selected_lang; st.rerun()
    
    st.divider()
    st.header(f"🔐 {T('wallet_con')}")
    if not st.session_state.wallet:
        if st.button(T("wallet_con"), key="con"): st.session_state.wallet = "Operator_Admin"; st.rerun()
    else:
        u_wallet, u_bal, u_prof, u_max = get_user()
        st.success(f"User: {u_wallet}")
        st.metric(T("balance"), f"{u_bal:.4f} SOL")
        st.metric(T("total_profit"), f"{u_prof:.4f} SOL")
        st.metric(T("max_lvl"), f"Lv.{u_max}")
        if st.button(T("wallet_dis"), key="dis"): st.session_state.wallet = None; st.rerun()

st.title(T("title"))

if not st.session_state.wallet:
    st.info("Wallet Connect Required.")
    st.stop()

tabs = st.tabs([T("tab_sec"), T("tab_game"), T("tab_inv"), T("tab_rank")])

# === 1. 보안 센터 ===
with tabs[0]:
    st.subheader(T("tab_sec"))
    tier = st.radio("Tier", ["BASIC (0.01 SOL)", "PRO (0.1 SOL)"], label_visibility="collapsed")
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
        _, bal, _, _ = get_user()
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
        total_fusions = sum([cnt // 2 for lvl, cnt in inv.items() if lvl < 1000])
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
                        if f_cnt > 0 and lvl < 1000:
                            update_inventory(lvl, -(f_cnt*2)); update_inventory(lvl+1, f_cnt)
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
                            r = cnt * calculate_reward(lvl)
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
                        if count >= 2 and lvl < 1000:
                            if st.button(f"🧬 (2->1)", key=f"kf_{lvl}"): 
                                update_inventory(lvl, -2); update_inventory(lvl+1, 1); st.toast("Success!", icon="✨"); st.rerun()
                        r = calculate_reward(lvl)
                        if st.button(f"🔒 (+{r:.4f})", key=f"kj_{lvl}"): 
                            update_inventory(lvl, -1); update_balance(r); record_profit(r); st.rerun()
                st.markdown("---")

# === 4. 명예의 전당 (수정됨: 수익 0 초과만 표시) ===
with tabs[3]:
    st.subheader(T("rank_title"))
    st.caption(T("rank_desc"))
    with get_db() as conn:
        # [핵심 수정] WHERE total_profit > 0 추가 -> 수익 낸 사람만 표시
        ranks = conn.execute("SELECT wallet, IFNULL(balance, 0.0), IFNULL(total_profit, 0.0), IFNULL(max_lvl, 0) FROM users WHERE total_profit > 0 ORDER BY total_profit DESC, max_lvl DESC LIMIT 10").fetchall()
    
    if not ranks:
        st.info(T("rank_empty"))
    else:
        for i, (w, b, p, m) in enumerate(ranks):
            medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
            st.markdown(f"""
            <div class='card-box' style='padding:15px; text-align:left; display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span style='font-size:1.5em; margin-right:10px;'>{medal}</span>
                    <span class='neon'>{w}</span>
                </div>
                <div style='text-align:right;'>
                    <div class='gold' style='font-size:1.3em;'>+{p:.4f} SOL</div>
                    <div class='red'>MAX: Lv.{m}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
