import os
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN no está definido como variable de entorno.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "🚀 TON_MINING_BOT está online y funcionando.")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
bot.reply_to(message, f"Has dicho:{message.text}")

if __name__ == "__main__":
print("✅ Bot arrancando...")
bot.infinity_polling()
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
import random

# ===========================
#  CONFIGURACIÓN DEL BOT
# ===========================
BOT_TOKEN = "8312805594:AAE6PK7kNko1TGAoTaDCz1AgT6wza1gOlQE"
ADMIN_ID = 7664138436

bot = telebot.TeleBot(BOT_TOKEN)

# ===========================
#  MENÚ PRINCIPAL
# ===========================
def menu_principal():
markup = ReplyKeyboardMarkup(resize_keyboard=True)
markup.row(
KeyboardButton("📟 Minería"),
KeyboardButton("🟡 Notcoin Game")
)
markup.row(
KeyboardButton("👑 Panel Admin")
)
return markup

# ===========================
#  MINERÍA SIMULADA
# ===========================
mineria_usuarios = {}

def minar(user_id):
if user_id not in mineria_usuarios:
mineria_usuarios[user_id] = 0
recompensa = random.randint(1, 8)
mineria_usuarios[user_id] += recompensa
return recompensa, mineria_usuarios[user_id]

# ===========================
#  JUEGO NOTCOIN
# ===========================
notcoin_balance = {}

def jugar_notcoin(user_id):
if user_id not in notcoin_balance:
notcoin_balance[user_id] = 0
ganancia = random.randint(5, 20)
notcoin_balance[user_id] += ganancia
return ganancia, notcoin_balance[user_id]

# ===========================
#  PANEL ADMIN
# ===========================
def es_admin(user_id):
return user_id == ADMIN_ID

# ===========================
#  COMANDOS
# ===========================
@bot.message_handler(commands=['start'])
def start(message):
bot.send_message(
message.chat.id,
"🚀 *TON_MINING_BOT está online y listo para trabajar!*\n\n"
"Selecciona una opción del menú:",
parse_mode="Markdown",
reply_markup=menu_principal()
)
@bot.message_handler(func=lambda message: True)
def mensajes(message):
user_id = message.from_user.id
texto = message.text

# 📟 MINERÍA
if texto == "📟 Minería":
recompensa, total = minar(user_id)
bot.send_message(
user_id,
f"⛏️ *Minando...*\nHas generado **{recompensa} TONCoins** ⚡\n"
f"Total acumulado: **{total} TONCoins**",
parse_mode="Markdown"
)# 🟡 NOTCOIN GAME
elif texto == "🟡 Notcoin Game":
ganancia, total = jugar_notcoin(user_id)
bot.send_message(
user_id,
f"🟡 *Notcoin Tap!*\nHas ganado **{ganancia} NOT** 🤏✨\n"
f"Total acumulado: **{total} NOT**",
parse_mode="Markdown"
)
# 👑 PANEL ADMIN
elif texto == "👑 Panel Admin":
if es_admin(user_id):
bot.send_message(
user_id,
"👑 *Panel Admin*\n"
"➤ Usuarios minando: " + str(len(mineria_usuarios)) + "\n"
"➤ Usuarios Notcoin: " + str(len(notcoin_balance)),
parse_mode="Markdown"
)
else:
bot.send_message(user_id, "❌ No tienes acceso al panel admin.")
else:
bot.send_message(user_id, "Selecciona una opción del menú.")
# ===========================
#  ARRANQUE DEL BOT
# ===========================
print("✅ Bot arrancando en Render...")
bot.infinity_polling()
