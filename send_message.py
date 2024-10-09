import asyncio
from telegram import Bot

# Telegram configuration
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID_HERE'

async def send_notification(message):
    bot = Bot(TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    print(f"Notification sent: {message}")

async def main():
    test_message = "🔔 This is a test message from your Door Monitor bot!"
    await send_notification(test_message)

if __name__ == "__main__":
    asyncio.run(main())