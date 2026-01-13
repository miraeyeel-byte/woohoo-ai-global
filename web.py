import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# 1. Page Configuration
st.set_page_config(page_title="WOOHOO AI | GLOBAL", layout="wide")

# 2. Session State for Coin Balance
if 'balance' not in st.session_state:
    st.session_state.balance = 1000

# 3. High-End Cyberpunk Design (White Glow & Gold Neon)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    .stApp { background-color: #000000 !important; }

    /* All White Text with Strong Glow */
    html, body, [class*="css"], p, div, span, label {
        color: #FFFFFF !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 12px rgba(255, 255, 255, 0.7);
    }

    /* Golden Titles with Neon Effect */
    h1, h2, .gold-text {
        color: #FFD700 !important;
        text-align: center;
        text-shadow: 0 0 25px rgba(255, 215, 0, 0.8) !important;
        letter-spacing: 3px;
    }

    /* FOMO Board Animation */
    .fomo-container {
        border: 1px solid #FFD700;
        background: rgba(255, 215, 0, 0.05);
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 20px;
    }
    .fomo-flash {
        color: #FFD700 !important;
        font-size: 14px;
        animation: blink 1.5s infinite;
    }
    @keyframes blink { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }

    /* Metric Cards (Delysium Style) */
    [data-testid="stMetric"] {
        background: rgba(15, 15, 15, 0.9) !important;
        border: 1px solid #FFD700 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
    }

    /* Pro Button Style */
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #B8860B) !important;
        color: #000 !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        height: 60px;
        width: 100%;
        border-radius: 8px;
        border: none;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# 4. FOMO Live Win Logs (Simulated)
fake_logs = [
    "🔥 USER 0x8a...f2 JUST WON 5,000 WH (100x JACKPOT)",
    "💎 ANONYMOUS PLAYER CLAIMED 1,000 WH REWARD",
    "⚡ NODE HOLDER 0x4d...e1 MINTED 500 WH FROM DICE",
    "🔥 HUGE WIN! 0x2c...b9 HIT THE GOLDEN 6!"
]
st.markdown(f"<div class='fomo-container'><div class='fomo-flash'>{random.choice(fake_logs)}</div></div>", unsafe_allow_html=True)

# 5. Header & Stats
st.markdown("<h1>⚡ WOOHOO AI : HYPER-CORE</h1>", unsafe_allow_html=True)
st.write(" ")

m1, m2, m3 = st.columns(3)
with m1: st.metric("NODE PRICE", "2.40 SOL", "TIER 01")
with m2: st.metric("NODES SOLD", "12,842 / 50K", "ACTIVE")
with m3: st.metric("MY BALANCE", f"{st.session_state.balance} WH", "WALLET")

st.write("---")

# 6. ENTERTAINMENT ZONE (The Dice Game)
st.markdown("<h2>🎰 WOOHOO LUCKY DICE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Bet your WH Coins and aim for the 100x Jackpot!</p>", unsafe_allow_html=True)

# Betting UI
game_c1, game_c2 = st.columns([1, 1])

with game_c1:
    bet_amount = st.radio("SELECT WAGER AMOUNT (WH)", [10, 100, 500, 1000], horizontal=True)

with game_c2:
    st.write(" ")
    if st.button("🎲 ROLL THE DICE"):
        if st.session_state.balance >= bet_amount:
            # Risk Warning Dialog
            @st.dialog("⚠️ RISK ACKNOWLEDGMENT")
            def gamble(amt):
                st.write(f"You are about to wager **{amt} WH**.")
                st.error("WARNING: You may lose all your wagered coins.")
                if st.button("I UNDERSTAND, ROLL NOW"):
                    st.session_state.balance -= amt
                    with st.spinner("SCANNING NETWORK..."):
                        time.sleep(1.2)
                        res = random.randint(1, 100)
                        
                        if res <= 10: # 10% Jackpot (100x)
                            win = amt * 100
                            st.session_state.balance += win
                            st.balloons()
                            st.success(f"🎊 100x JACKPOT! +{win} WH RECEIVED!")
                        elif res <= 30: # 20% Small Win (10x)
                            win = amt * 10
                            st.session_state.balance += win
                            st.info(f"⚡ BIG WIN! +{win} WH RECEIVED!")
                        else: # 70% House Wins
                            st.error(f"REKT! -{amt} WH ABSORBED BY CORE.")
                    time.sleep(1)
                    st.rerun()
            
            gamble(bet_amount)
        else:
            st.error("Insufficient WH Coins! Purchase Nodes to earn more.")

# 7. System Logs
st.write("---")
st.code(f"""
> [SYSTEM] CORE_ENGINE: ONLINE
> [GAME] HOUSE_EDGE: 70% | STATUS: READY
> [WALLET] BALANCE: {st.session_state.balance} WH
> [INFO] CONNECTED TO SOLANA MAINNET
""", language="bash")

st.caption("© 2026 WOOHOO AI GLOBAL | Powered by Solana SVM")
