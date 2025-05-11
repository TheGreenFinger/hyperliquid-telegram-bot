import asyncio
import os
from dotenv import load_dotenv
from hyperliquid.info import Info
from hyperliquid.utils import constants
from telegram import Bot

# 📦 Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# 🔧 Infos Telegram récupérées depuis .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
THREAD_ID = int(os.getenv("THREAD_ID"))

# 🔍 Adresse du trader Hyperliquid
TRADER_ADDRESS = os.getenv("TRADER_ADDRESS")

# 📦 Init Hyperliquid Info client
info = Info(constants.MAINNET_API_URL, skip_ws=True)
bot = Bot(token=BOT_TOKEN)

def format_state(state: dict) -> str:
    positions = state.get("assetPositions", [])
    open_positions = [p for p in positions if float(p["position"]["szi"]) != 0]

    if not open_positions:
        return "📭 Le trader n'a **aucune position ouverte** actuellement."

    msg = "📊 **Positions ouvertes du trader :**\n\n"
    for pos in open_positions:
        coin = pos["position"]["coin"]
        size = pos["position"]["szi"]
        entry = pos["position"]["entryPx"]
        msg += f"• {coin} → {size} @ {entry}\n"
    return msg

def get_open_positions(state: dict) -> list:
    positions = state.get("assetPositions", [])
    open_positions = [
        (p["position"]["coin"], f"{float(p['position']['szi']):.6f}", f"{float(p['position']['entryPx']):.6f}")
        for p in positions if float(p["position"]["szi"]) != 0
    ]
    return open_positions

async def send_message(text: str):
    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text=text,
        parse_mode="Markdown"
    )

async def main():
    last_state = info.user_state(TRADER_ADDRESS)
    last_open_positions = get_open_positions(last_state)
    
    await send_message(format_state(last_state))
    print("🔄 Surveillance du trader en cours...")

    while True:
        await asyncio.sleep(300)
        new_state = info.user_state(TRADER_ADDRESS)
        new_open_positions = get_open_positions(new_state)

        if new_open_positions != last_open_positions:
            print("📢 Changement détecté ! Envoi de l'alerte Telegram.")
            await send_message(format_state(new_state))
            last_state = new_state
            last_open_positions = new_open_positions

if __name__ == "__main__":
    asyncio.run(main())
