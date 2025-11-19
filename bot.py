import os
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN no está definido como variable de entorno.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "🚀 TON_MINING_BOT está online y funcionando.")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"Has dicho: {message.text}")

if __name__ == "__main__":
    print("✅ Bot arrancando...")
    bot.infinity_polling()
