# bot.py
import os
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# -----------------------------
#   CARGAR VARIABLES DEL .ENV
# -----------------------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
JWT_SECRET = os.getenv("JWT_SECRET")
STRIPE_KEY = os.getenv("STRIPE_KEY")

if not BOT_TOKEN or not ADMIN_ID or not JWT_SECRET or not STRIPE_KEY:
    raise ValueError("❌ Alguna variable del .env no está definida correctamente")

# -----------------------------
#   INICIALIZAR BOT Y DISPATCHER
# -----------------------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# -----------------------------
#   TECLADO PRINCIPAL
# -----------------------------
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                text="🌐 Abrir TONPayHub",
                web_app={"url": "https://tonpayhub.onrender.com"}
            )
        ],
        [
            InlineKeyboardButton(
                text="💳 Comprar vía Cryptomus",
                callback_data="pay_cryptomus"
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ Información",
                callback_data="info"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# -----------------------------
#   COMANDO /START
# -----------------------------
@dp.message(Command("start"))
async def start(message: Message):
    try:
        await message.answer(
            f"👋 Hola **{message.from_user.first_name}**\n\n"
            "Bienvenido a **TONMoneyBot**.\n\n"
            "Aquí puedes:\n"
            "💠 Comprar tu token TMB/FROG\n"
            "💠 Acceder al portal seguro TONPayHub\n"
            "💠 Ver información del proyecto\n\n"
            "Selecciona una opción abajo 👇",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error en /start: {e}")

# -----------------------------
#   BOTONES DE CALLBACK
# -----------------------------
@dp.callback_query(F.data == "info")
async def info(callback: types.CallbackQuery):
    try:
        await callback.message.edit_text(
            "📘 *Información del Proyecto*\n\n"
            "🔹 TONMoneyBot controla tu acceso al ecosistema\n"
            "🔹 TONPayHub gestiona los pagos\n"
            "🔹 TMB/FROG son los tokens oficiales del proyecto\n"
            "\nSi necesitas ayuda, contacta con soporte.",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    except Exception as e:
        print(f"Error en info callback: {e}")

@dp.callback_query(F.data == "pay_cryptomus")
async def pay_cryptomus(callback: types.CallbackQuery):
    try:
        await callback.message.edit_text(
            "💳 *Pago por Cryptomus (Próximamente)*\n\n"
            "🛠 Estamos configurando la pasarela.\n"
            "⏳ Estará disponible en cuanto completes la verificación.",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    except Exception as e:
        print(f"Error en pay_cryptomus callback: {e}")

# -----------------------------
#   MAIN LOOP
# -----------------------------
async def main():
    print("🤖 TONMoneyBot está corriendo...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Error en polling: {e}")

if __name__ == "__main__":
    asyncio.run(main())