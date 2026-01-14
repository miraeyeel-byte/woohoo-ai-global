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
st.set_page_config(page_title="WOOHOO WORLDWIDE V18.9", layout="wide")
DB_PATH = "woohoo_v18_9_world.db"

# [2. 16개국어 번역 팩 (Global Language Pack)]
LANG = {
    # 1. 한국어
    "🇰🇷 한국어": {
        "tab_sec": "🛡️ 보안 센터", "tab_game": "🚨 범인 체포", "tab_inv": "📦 보관함", "tab_rank": "🏆 명예의 전당",
        "wallet_con": "지갑 연결", "wallet_dis": "연결 해제", "balance": "자산", "max_lvl": "최고 기록",
        "sec_btn": "💰 매수 시도", "sec_warn": "주소를 입력하세요.", "sec_safe": "✅ 안전 (점수: {score})", "sec_danger": "🚨 [경고] 위험 점수 {score}!", "sec_block": "🚫 차단됨!",
        "game_desc": "비용을 지불하고 체포합니다. 운이 좋으면 고레벨 등장!", "pull_1": "1회 체포", "pull_5": "5회 체포", "pull_10": "10회 체포",
        "inv_empty": "보관함이 비어있습니다.", "fuse_all": "🧬 일괄 합성", "jail_all": "🔒 일괄 감옥",
        "name_1": "소매치기", "name_10": "양아치", "name_50": "조직 간부", "name_90": "테러리스트", "name_100": "세계관 최강자"
    },
    # 2. 영어 (미국/호주/영국 등)
    "🇺🇸 English": {
        "tab_sec": "🛡️ Security", "tab_game": "🚨 Arrest", "tab_inv": "📦 Inventory", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Connect Wallet", "wallet_dis": "Disconnect", "balance": "Balance", "max_lvl": "Max Level",
        "sec_btn": "💰 Buy (Sim)", "sec_warn": "Enter Address.", "sec_safe": "✅ Safe (Score: {score})", "sec_danger": "🚨 High Risk {score}!", "sec_block": "🚫 Blocked!",
        "game_desc": "Pay bounty to arrest criminals. Lucky drops enabled.", "pull_1": "Arrest x1", "pull_5": "Arrest x5", "pull_10": "Arrest x10",
        "inv_empty": "Inventory Empty.", "fuse_all": "🧬 Fuse All", "jail_all": "🔒 Jail All",
        "name_1": "Pickpocket", "name_10": "Thug", "name_50": "Gang Boss", "name_90": "Terrorist", "name_100": "Overlord"
    },
    # 3. 일본어
    "🇯🇵 日本語": {
        "tab_sec": "🛡️ セキュリティ", "tab_game": "🚨 逮捕", "tab_inv": "📦 保管庫", "tab_rank": "🏆 殿堂入り",
        "wallet_con": "接続", "wallet_dis": "切断", "balance": "残高", "max_lvl": "最高記録",
        "sec_btn": "💰 購入試行", "sec_warn": "アドレスを入力。", "sec_safe": "✅ 安全 (点数: {score})", "sec_danger": "🚨 [警告] 危険度 {score}!", "sec_block": "🚫 遮断!",
        "game_desc": "費用を払って逮捕します。高レベル出現のチャンス。", "pull_1": "1回逮捕", "pull_5": "5回逮捕", "pull_10": "10回逮捕",
        "inv_empty": "保管庫は空です。", "fuse_all": "🧬 一括合成", "jail_all": "🔒 一括送獄",
        "name_1": "スリ", "name_10": "チンピラ", "name_50": "幹部", "name_90": "テロリスト", "name_100": "絶対悪"
    },
    # 4. 중국어
    "🇨🇳 中文": {
        "tab_sec": "🛡️ 安全中心", "tab_game": "🚨 逮捕", "tab_inv": "📦 仓库", "tab_rank": "🏆 名人堂",
        "wallet_con": "连接钱包", "wallet_dis": "断开", "balance": "余额", "max_lvl": "最高记录",
        "sec_btn": "💰 尝试购买", "sec_warn": "请输入地址。", "sec_safe": "✅ 安全 (分数: {score})", "sec_danger": "🚨 [警告] 风险 {score}!", "sec_block": "🚫 已拦截!",
        "game_desc": "支付费用逮捕罪犯。有机会获得高等级。", "pull_1": "逮捕 1次", "pull_5": "逮捕 5次", "pull_10": "逮捕 10次",
        "inv_empty": "仓库为空。", "fuse_all": "🧬 一键合成", "jail_all": "🔒 一键入狱",
        "name_1": "扒手", "name_10": "流氓", "name_50": "干部", "name_90": "恐怖分子", "name_100": "终极BOSS"
    },
    # 5. 러시아어
    "🇷🇺 Русский": {
        "tab_sec": "🛡️ Защита", "tab_game": "🚨 Арест", "tab_inv": "📦 Инвентарь", "tab_rank": "🏆 Рейтинг",
        "wallet_con": "Подключить", "wallet_dis": "Выйти", "balance": "Баланс", "max_lvl": "Макс. Ур.",
        "sec_btn": "💰 Купить", "sec_warn": "Введите адрес.", "sec_safe": "✅ Безопасно (Счет: {score})", "sec_danger": "🚨 [Опасно] Риск {score}!", "sec_block": "🚫 Блок!",
        "game_desc": "Платите награду за арест. Возможен редкий дроп.", "pull_1": "Арест x1", "pull_5": "Арест x5", "pull_10": "Арест x10",
        "inv_empty": "Инвентарь пуст.", "fuse_all": "🧬 Синтез", "jail_all": "🔒 В тюрьму",
        "name_1": "Карманник", "name_10": "Бандит", "name_50": "Босс", "name_90": "Террорист", "name_100": "Владыка"
    },
    # 6. 베트남어
    "🇻🇳 Tiếng Việt": {
        "tab_sec": "🛡️ Bảo mật", "tab_game": "🚨 Bắt giữ", "tab_inv": "📦 Kho", "tab_rank": "🏆 Xếp hạng",
        "wallet_con": "Kết nối ví", "wallet_dis": "Ngắt kết nối", "balance": "Số dư", "max_lvl": "Cấp cao nhất",
        "sec_btn": "💰 Mua", "sec_warn": "Nhập địa chỉ.", "sec_safe": "✅ An toàn (Điểm: {score})", "sec_danger": "🚨 [Cảnh báo] Rủi ro {score}!", "sec_block": "🚫 Đã chặn!",
        "game_desc": "Trả tiền thưởng để bắt tội phạm. Cơ hội nhận cấp cao.", "pull_1": "Bắt x1", "pull_5": "Bắt x5", "pull_10": "Bắt x10",
        "inv_empty": "Kho trống.", "fuse_all": "🧬 Hợp nhất", "jail_all": "🔒 Vào tù",
        "name_1": "Móc túi", "name_10": "Côn đồ", "name_50": "Trùm", "name_90": "Khủng bố", "name_100": "Chúa tể"
    },
    # 7. 태국어
    "🇹🇭 ภาษาไทย": {
        "tab_sec": "🛡️ ความปลอดภัย", "tab_game": "🚨 จับกุม", "tab_inv": "📦 คลัง", "tab_rank": "🏆 อันดับ",
        "wallet_con": "เชื่อมต่อกระเป๋า", "wallet_dis": "ตัดการเชื่อมต่อ", "balance": "ยอดคงเหลือ", "max_lvl": "ระดับสูงสุด",
        "sec_btn": "💰 ซื้อ", "sec_warn": "ป้อนที่อยู่", "sec_safe": "✅ ปลอดภัย (คะแนน: {score})", "sec_danger": "🚨 [เตือน] ความเสี่ยง {score}!", "sec_block": "🚫 บล็อค!",
        "game_desc": "จ่ายเงินรางวัลเพื่อจับกุมอาชญากร", "pull_1": "จับ x1", "pull_5": "จับ x5", "pull_10": "จับ x10",
        "inv_empty": "คลังว่างเปล่า", "fuse_all": "🧬 ผสมทั้งหมด", "jail_all": "🔒 เข้าคุกทั้งหมด",
        "name_1": "นักล้วงกระเป๋า", "name_10": "อันธพาล", "name_50": "หัวหน้าแก๊ง", "name_90": "ผู้ก่อการร้าย", "name_100": "จอมมาร"
    },
    # 8. 히브리어 (이스라엘)
    "🇮🇱 עברית": {
        "tab_sec": "🛡️ אבטחה", "tab_game": "🚨 מעצר", "tab_inv": "📦 מלאי", "tab_rank": "🏆 דירוג",
        "wallet_con": "חבר ארנק", "wallet_dis": "התנתק", "balance": "יתרה", "max_lvl": "רמה מקס",
        "sec_btn": "💰 קנה", "sec_warn": "הכנס כתובת", "sec_safe": "✅ בטוח (ניקוד: {score})", "sec_danger": "🚨 [אזהרה] סיכון {score}!", "sec_block": "🚫 נחסם!",
        "game_desc": "שלם פרס כדי לעצור פושעים.", "pull_1": "מעצר x1", "pull_5": "מעצר x5", "pull_10": "מעצר x10",
        "inv_empty": "המלאי ריק", "fuse_all": "🧬 למזג הכל", "jail_all": "🔒 לכלא הכל",
        "name_1": "כייס", "name_10": "בריון", "name_50": "בוס", "name_90": "טרוריסט", "name_100": "אדון"
    },
    # 9. 필리핀 (Tagalog)
    "🇵🇭 Tagalog": {
        "tab_sec": "🛡️ Seguridad", "tab_game": "🚨 Huliin", "tab_inv": "📦 Imbentaryo", "tab_rank": "🏆 Hall of Fame",
        "wallet_con": "Ikonekta", "wallet_dis": "Diskonekta", "balance": "Balanse", "max_lvl": "Max Level",
        "sec_btn": "💰 Bumili", "sec_warn": "Ilagay ang address.", "sec_safe": "✅ Ligtas (Score: {score})", "sec_danger": "🚨 [Babala] Panganib {score}!", "sec_block": "🚫 Hinarang!",
        "game_desc": "Magbayad para manghuli ng kriminal.", "pull_1": "Huli x1", "pull_5": "Huli x5", "pull_10": "Huli x10",
        "inv_empty": "Walang laman.", "fuse_all": "🧬 Pagsamahin", "jail_all": "🔒 I-kulong",
        "name_1": "Mandurukot", "name_10": "Siga", "name_50": "Boss", "name_90": "Terorista", "name_100": "Overlord"
    },
    # 10. 말레이시아 (Bahasa Melayu)
    "🇲🇾 Melayu": {
        "tab_sec": "🛡️ Keselamatan", "tab_game": "🚨 Tangkap", "tab_inv": "📦 Inventori", "tab_rank": "🏆 Dewan Kemasyhuran",
        "wallet_con": "Sambung Dompet", "wallet_dis": "Putuskan", "balance": "Baki", "max_lvl": "Tahap Maks",
        "sec_btn": "💰 Beli", "sec_warn": "Masukkan alamat.", "sec_safe": "✅ Selamat (Skor: {score})", "sec_danger": "🚨 [Amaran] Risiko {score}!", "sec_block": "🚫 Disekat!",
        "game_desc": "Bayar ganjaran untuk menangkap penjenayah.", "pull_1": "Tangkap x1", "pull_5": "Tangkap x5", "pull_10": "Tangkap x10",
        "inv_empty": "Inventori kosong.", "fuse_all": "🧬 Gabung Semua", "jail_all": "🔒 Penjara Semua",
        "name_1": "Pencopet", "name_10": "Samseng", "name_50": "Bos", "name_90": "Pengganas", "name_100": "Raja"
    },
    # 11. 인도네시아
    "🇮🇩 Indonesia": {
        "tab_sec": "🛡️ Keamanan", "tab_game": "🚨 Penangkapan", "tab_inv": "📦 Inventaris", "tab_rank": "🏆 Peringkat",
        "wallet_con": "Konek Dompet", "wallet_dis": "Putus", "balance": "Saldo", "max_lvl": "Level Maks",
        "sec_btn": "💰 Beli", "sec_warn": "Masukkan alamat.", "sec_safe": "✅ Aman (Skor: {score})", "sec_danger": "🚨 [Peringatan] Risiko {score}!", "sec_block": "🚫 Diblokir!",
        "game_desc": "Bayar bounty untuk menangkap kriminal.", "pull_1": "Tangkap x1", "pull_5": "Tangkap x5", "pull_10": "Tangkap x10",
        "inv_empty": "Kosong.", "fuse_all": "🧬 Gabung", "jail_all": "🔒 Penjara",
        "name_1": "Copet", "name_10": "Preman", "name_50": "Bos", "name_90": "Teroris", "name_100": "Raja Iblis"
    },
    # 12. 튀르키예
    "🇹🇷 Türkçe": {
        "tab_sec": "🛡️ Güvenlik", "tab_game": "🚨 Tutuklama", "tab_inv": "📦 Envanter", "tab_rank": "🏆 Şeref Listesi",
        "wallet_con": "Cüzdan Bağla", "wallet_dis": "Çıkış", "balance": "Bakiye", "max_lvl": "Maks Sv.",
        "sec_btn": "💰 Satın Al", "sec_warn": "Adres girin.", "sec_safe": "✅ Güvenli (Puan: {score})", "sec_danger": "🚨 [Uyarı] Risk {score}!", "sec_block": "🚫 Engellendi!",
        "game_desc": "Suçluları yakalamak için ödül ödeyin.", "pull_1": "Yakala x1", "pull_5": "Yakala x5", "pull_10": "Yakala x10",
        "inv_empty": "Boş.", "fuse_all": "🧬 Birleştir", "jail_all": "🔒 Hapse At",
        "name_1": "Yankesici", "name_10": "Haydut", "name_50": "Patron", "name_90": "Terörist", "name_100": "Lord"
    },
    # 13. 포르투갈 (브라질)
    "🇵🇹 Português": {
        "tab_sec": "🛡️ Segurança", "tab_game": "🚨 Prisão", "tab_inv": "📦 Inventário", "tab_rank": "🏆 Hall da Fama",
        "wallet_con": "Conectar", "wallet_dis": "Desconectar", "balance": "Saldo", "max_lvl": "Nível Máx",
        "sec_btn": "💰 Comprar", "sec_warn": "Insira o endereço.", "sec_safe": "✅ Seguro (Score: {score})", "sec_danger": "🚨 [Aviso] Risco {score}!", "sec_block": "🚫 Bloqueado!",
        "game_desc": "Pague recompensa para prender criminosos.", "pull_1": "Prender x1", "pull_5": "Prender x5", "pull_10": "Prender x10",
        "inv_empty": "Vazio.", "fuse_all": "🧬 Fundir", "jail_all": "🔒 Prender Todos",
        "name_1": "Batedor", "name_10": "Bandido", "name_50": "Chefe", "name_90": "Terrorista", "name_100": "Lorde"
    },
    # 14. 스페인
    "🇪🇸 Español": {
        "tab_sec": "🛡️ Seguridad", "tab_game": "🚨 Arresto", "tab_inv": "📦 Inventario", "tab_rank": "🏆 Salón de la Fama",
        "wallet_con": "Conectar", "wallet_dis": "Desconectar", "balance": "Saldo", "max_lvl": "Nivel Máx",
        "sec_btn": "💰 Comprar", "sec_warn": "Ingrese dirección.", "sec_safe": "✅ Seguro (Puntaje: {score})", "sec_danger": "🚨 [Alerta] Riesgo {score}!", "sec_block": "🚫 Bloqueado!",
        "game_desc": "Pagar recompensa para arrestar.", "pull_1": "Arrestar x1", "pull_5": "Arrestar x5", "pull_10": "Arrestar x10",
        "inv_empty": "Vacío.", "fuse_all": "🧬 Fusionar", "jail_all": "🔒 Encarcelar",
        "name_1": "Carterista", "name_10": "Matón", "name_50": "Jefe", "name_90": "Terrorista", "name_100": "Señor"
    },
    # 15. 독일어
    "🇩🇪 Deutsch": {
        "tab_sec": "🛡️ Sicherheit", "tab_game": "🚨 Festnahme", "tab_inv": "📦 Inventar", "tab_rank": "🏆 Ruhmeshalle",
        "wallet_con": "Verbinden", "wallet_dis": "Trennen", "balance": "Guthaben", "max_lvl": "Max Level",
        "sec_btn": "💰 Kaufen", "sec_warn": "Adresse eingeben.", "sec_safe": "✅ Sicher (Score: {score})", "sec_danger": "🚨 [Warnung] Risiko {score}!", "sec_block": "🚫 Blockiert!",
        "game_desc": "Zahlen Sie Kopfgeld, um Verbrecher zu fangen.", "pull_1": "Fangen x1", "pull_5": "Fangen x5", "pull_10": "Fangen x10",
        "inv_empty": "Leer.", "fuse_all": "🧬 Fusionieren", "jail_all": "🔒 Einsperren",
        "name_1": "Taschendieb", "name_10": "Schläger", "name_50": "Boss", "name_90": "Terrorist", "name_100": "Overlord"
    },
    # 16. 프랑스어
    "🇫🇷 Français": {
        "tab_sec": "🛡️ Sécurité", "tab_game": "🚨 Arrestation", "tab_inv": "📦 Inventaire", "tab_rank": "🏆 Panthéon",
        "wallet_con": "Connecter", "wallet_dis": "Déconnecter", "balance": "Solde", "max_lvl": "Niveau Max",
        "sec_btn": "💰 Acheter", "sec_warn": "Entrez l'adresse.", "sec_safe": "✅ Sûr (Score: {score})", "sec_danger": "🚨 [Attention] Risque {score}!", "sec_block": "🚫 Bloqué!",
        "game_desc": "Payez une prime pour arrêter les criminels.", "pull_1": "Arrêter x1", "pull_5": "Arrêter x5", "pull_10": "Arrêter x10",
        "inv_empty": "Vide.", "fuse_all": "🧬 Fusionner", "jail_all": "🔒 Emprisonner",
        "name_1": "Pickpocket", "name_10": "Voyou", "name_50": "Parrain", "name_90": "Terroriste", "name_100": "Seigneur"
    }
}

# [3. DB 초기화]
def get_db():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (wallet TEXT PRIMARY KEY, balance REAL, max_lvl INTEGER DEFAULT 0)")
        c.execute("CREATE TABLE IF NOT EXISTS inventory (wallet TEXT, lvl INTEGER, count INTEGER, PRIMARY KEY(wallet, lvl))")
        # 운영자 계정 초기화 (레벨 0 시작)
        c.execute("INSERT OR IGNORE INTO users (wallet, balance, max_lvl) VALUES ('Operator_Admin', 10.0, 0)")
        conn.commit()
init_db()

# [4. 번역 및 유틸리티 함수]
if 'lang' not in st.session_state: st.session_state.lang = "🇰🇷 한국어"

def T(key, **kwargs):
    # 선택된 언어의 텍스트 반환 (없으면 영어로 폴백)
    lang_dict = LANG.get(st.session_state.lang, LANG["🇺🇸 English"])
    text = lang_dict.get(key, LANG["🇺🇸 English"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
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
    return f"https://api.dicebear.com/7.x/bottts/svg?seed=CryptoCrime{lvl}&backgroundColor=1a1a1a"

# [5. 보안 및 게임 로직]
def process_security_action(token_address, user_tier):
    risk_score = random.randint(0, 100)
    if user_tier.startswith("BASIC"):
        if risk_score >= 70:
            st.warning(T("sec_danger", score=risk_score)); return
    elif user_tier.startswith("PRO"):
        if risk_score >= 70:
            st.error(T("sec_block", score=risk_score)); return
    st.success(T("sec_safe", score=risk_score))

def get_user():
    if not st.session_state.wallet: return None, 0.0, 0
    with get_db() as conn:
        u = conn.execute("SELECT wallet, balance, max_lvl FROM users WHERE wallet=?", (st.session_state.wallet,)).fetchone()
        return u if u else (st.session_state.wallet, 0.0, 0)
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
def get_inv():
    with get_db() as conn:
        return dict(conn.execute("SELECT lvl, count FROM inventory WHERE wallet=?", (st.session_state.wallet,)).fetchall())
def gacha_pull(n):
    levels = list(range(1, 101))
    weights = [1000 / (i * i) for i in levels]
    return random.choices(levels, weights=weights, k=n)

# [6. 스타일링]
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3, h4, p, div { color: #e0e0e0; text-shadow: 1px 1px 2px #000; }
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border: 1px solid #333; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FFD700; color: #000; font-weight: bold; border: none; }
    .card-box {
        border: 2px solid #FFD700; background: linear-gradient(145deg, #111, #1a1a1a);
        padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.6); transition: 0.3s;
    }
    .card-box:hover { border-color: #66fcf1; transform: translateY(-3px); }
    .neon { color: #66fcf1; font-weight: bold; }
    .gold { color: #FFD700; font-weight: bold; }
    .red { color: #ff4b4b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# [7. 세션 관리]
if 'wallet' not in st.session_state: st.session_state.wallet = None
if 'user_tier' not in st.session_state: st.session_state.user_tier = "BASIC (0.01 SOL)"
if 'confirm_fuse_all' not in st.session_state: st.session_state.confirm_fuse_all = False
if 'confirm_jail_all' not in st.session_state: st.session_state.confirm_jail_all = False

# [8. 메인 UI]
# 사이드바 (언어 및 지갑)
with st.sidebar:
    st.title("🌐 Language / 言語 / 언어")
    # 언어 선택 드롭다운
    lang_options = list(LANG.keys())
    selected_index = lang_options.index(st.session_state.lang)
    selected_lang = st.selectbox("Select", lang_options, index=selected_index)
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()
    
    st.divider()
    st.header(f"🔐 {T('wallet_con')}")
    if not st.session_state.wallet:
        if st.button(T("wallet_con")): st.session_state.wallet = "Operator_Admin"; st.rerun()
    else:
        u_wallet, u_bal, u_max = get_user()
        st.success(f"User: {u_wallet}")
        st.metric(T("balance"), f"{u_bal:.4f} SOL")
        st.metric(T("max_lvl"), f"Lv.{u_max}")
        if st.button(T("wallet_dis")): st.session_state.wallet = None; st.rerun()

st.title(T("tab_sec").replace("🛡️ ", "WOOHOO "))

if not st.session_state.wallet:
    st.info("Please Connect Wallet.")
    st.stop()

tabs = st.tabs([T("tab_sec"), T("tab_game"), T("tab_inv"), T("tab_rank")])

# === 1. 보안 센터 ===
with tabs[0]:
    st.subheader(T("sec_title")) # "토큰 보안 스캐너"
    st.markdown("**Tier:**")
    tier = st.radio("Level", ["BASIC (0.01 SOL)", "PRO (0.1 SOL)"])
    st.session_state.user_tier = tier
    st.divider()
    token_address = st.text_input(T("sec_warn")) # "주소를 입력하세요"
    if st.button(T("sec_btn")):
        if not token_address: st.warning(T("sec_warn"))
        else: process_security_action(token_address, st.session_state.user_tier)

# === 2. 범인 체포 ===
with tabs[1]:
    st.subheader(T("tab_game")) # "범인 체포"
    st.caption(T("game_desc"))
    
    def run_gacha(cost, n):
        _, bal, _ = get_user()
        if bal < cost: st.error("Low Balance"); return
        update_balance(-cost)
        res = gacha_pull(n)
        for r in res: update_inventory(r, 1)
        st.toast(f"{n} Captured!", icon="🚨")
        cols = st.columns(min(n, 5))
        for i, lvl in enumerate(res[:5]):
            with cols[i]:
                st.markdown(f"<div class='card-box'><img src='{get_img_url(lvl)}' width='50'><div class='neon'>Lv.{lvl}</div></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button(f"{T('pull_1')} (0.01 SOL)"): run_gacha(0.01, 1)
    with c2: 
        if st.button(f"{T('pull_5')} (0.05 SOL)"): run_gacha(0.05, 5)
    with c3: 
        if st.button(f"{T('pull_10')} (0.10 SOL)"): run_gacha(0.10, 10)

# === 3. 보관함 ===
with tabs[2]:
    st.subheader(T("tab_inv")) # "보관함"
    inv = get_inv()
    if inv:
        bc1, bc2 = st.columns(2)
        total_fusions = sum([cnt // 2 for lvl, cnt in inv.items() if lvl < 100])
        with bc1:
            if not st.session_state.confirm_fuse_all:
                if st.button(f"{T('fuse_all')} ({total_fusions})", type="primary", disabled=total_fusions==0):
                    st.session_state.confirm_fuse_all = True; st.rerun()
            else:
                st.warning("Confirm Fusion?")
                if st.button("✅ YES"):
                    for lvl in sorted(inv.keys()):
                        f_cnt = inv[lvl] // 2
                        if f_cnt > 0 and lvl < 100: update_inventory(lvl, -(f_cnt*2)); update_inventory(lvl+1, f_cnt)
                    st.toast("Fusion Success!", icon="🧬"); st.session_state.confirm_fuse_all = False; st.rerun()
        with bc2:
            if not st.session_state.confirm_jail_all:
                if st.button(T("jail_all")): st.session_state.confirm_jail_all = True; st.rerun()
            else:
                st.warning("Confirm Jail All?")
                if st.button("✅ YES"):
                    tr = 0
                    for lvl, cnt in inv.items():
                        if cnt > 0:
                            r = cnt * (0.005 * (1.1**(lvl-1)))
                            update_inventory(lvl, -cnt); tr += r
                    update_balance(tr); st.toast(f"Reward: +{tr:.4f} SOL", icon="💰"); st.session_state.confirm_jail_all = False; st.rerun()
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
                            if st.button(f"🧬 (2->1)", key=f"f_{lvl}"): update_inventory(lvl, -2); update_inventory(lvl+1, 1); st.toast("Success!", icon="✨"); st.rerun()
                        r = 0.005 * (1.1**(lvl-1))
                        if st.button(f"🔒 (+{r:.4f})", key=f"j_{lvl}"): update_inventory(lvl, -1); update_balance(r); st.rerun()
                st.markdown("---")

# === 4. 명예의 전당 ===
with tabs[3]:
    st.subheader(T("tab_rank")) # "명예의 전당"
    with get_db() as conn:
        ranks = conn.execute("SELECT wallet, balance, max_lvl FROM users ORDER BY max_lvl DESC, balance DESC LIMIT 10").fetchall()
    for i, (w, b, m) in enumerate(ranks):
        medal = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        st.markdown(f"<div class='card-box' style='padding:15px; text-align:left; display:flex; justify-content:space-between;'><span style='font-size:1.2em'>{medal} <span class='neon'>{w}</span></span><span style='text-align:right'><span class='red'>Lv.{m}</span> <span class='gold'>{b:.4f} SOL</span></span></div>", unsafe_allow_html=True)
