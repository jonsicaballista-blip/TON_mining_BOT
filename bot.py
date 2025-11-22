# bot.py
import os
import time
import json
import random
import threading
from functools import wraps
import telebot
from telebot import types

# ---------------------------
# CONFIG
# ---------------------------
# Si no hay variable de entorno BOT_TOKEN, usa este token (temporal).
# RECOMENDACIÓN: establecer BOT_TOKEN en Render (Environment -> Add Variable) y
# eliminar el token hardcodeado de este archivo.
FALLBACK_TOKEN = "8312805594:AAE6PK7kNko1TGAoTaDCz1AgT6wza1gOlQE"

BOT_TOKEN = os.getenv("BOT_TOKEN") or FALLBACK_TOKEN

# Tu admin ID (has indicado 7664138436)
ADMIN_ID = int(os.getenv("ADMIN_ID") or 7664138436)

DB_FILE = "data.json"

# Cooldowns en segundos
MINING_COOLDOWN = 60  # ejemplo: 60s entre minados
NOTCOIN_COOLDOWN = 10

# Valores iniciales
START_BALANCE = 100

# ---------------------------
# BOT INIT
# ---------------------------
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ---------------------------
# DB UTILITIES
# ---------------------------
db_lock = threading.Lock()

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with db_lock:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {"users": {}}

def save_db(db):
    with db_lock:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

def ensure_user(user_id, username=None, first_name=None, last_name=None):
    db = load_db()
    users = db.setdefault("users", {})
    sid = str(user_id)
    if sid not in users:
        users[sid] = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "balance": START_BALANCE,
            "last_mine": 0,
            "last_notcoin": 0
        }
        save_db(db)
    else:
        # update some meta if provided
        if username:
            users[sid]["username"] = username
        if first_name:
            users[sid]["first_name"] = first_name
        if last_name:
            users[sid]["last_name"] = last_name
        save_db(db)
    return users[sid]

def change_balance(user_id, amount):
    db = load_db()
    users = db.setdefault("users", {})
    sid = str(user_id)
    if sid not in users:
        ensure_user(user_id)
        db = load_db()
        users = db["users"]
    users[sid]["balance"] = max(0, users[sid].get("balance", 0) + amount)
    save_db(db)
    return users[sid]["balance"]

def get_balance(user_id):
    db = load_db()
    users = db.get("users", {})
    sid = str(user_id)
    return users.get(sid, {}).get("balance", 0)

def set_timestamp(user_id, key, ts=None):
    if ts is None:
        ts = int(time.time())
    db = load_db()
    users = db.setdefault("users", {})
    sid = str(user_id)
    if sid not in users:
        ensure_user(user_id)
        db = load_db()
        users = db["users"]
    users[sid][key] = ts
    save_db(db)

def get_timestamp(user_id, key):
    db = load_db()
    users = db.get("users", {})
    sid = str(user_id)
    return users.get(sid, {}).get(key, 0)

# ---------------------------
# HELPERS
# ---------------------------
def admin_only(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        uid = message.from_user.id if hasattr(message, "from_user") else None
        if uid != ADMIN_ID:
            bot.reply_to(message, "🔒 Acceso denegado. Solo el administrador puede usar esto.")
            return
        return func(message, *args, **kwargs)
    return wrapper

def format_balance_text(user_id):
    bal = get_balance(user_id)
    return f"💰 Tu balance: <b>{bal}</b> NotCoin"

# ---------------------------
# KEYBOARDS
# ---------------------------
def main_menu_keyboard(is_admin=False):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("⛏️ Minería", callback_data="mine"),
        types.InlineKeyboardButton("🎯 NotCoin", callback_data="notcoin"),
    )
    kb.add(
        types.InlineKeyboardButton("💰 Balance", callback_data="balance"),
        types.InlineKeyboardButton("📈 Mis estadísticas", callback_data="stats"),
    )
    if is_admin:
        kb.add(types.InlineKeyboardButton("⚙️ Panel Admin", callback_data="admin"))
    return kb

def admin_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("👥 Ver usuarios", callback_data="admin_users"),
        types.InlineKeyboardButton("➕ Añadir saldo a usuario", callback_data="admin_add"),
        types.InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("🔙 Volver al menú", callback_data="menu")
    )
    return kb

# ---------------------------
# HANDLERS
# ---------------------------

@bot.message_handler(commands=["start", "menu"])
def cmd_start(message):
    user = message.from_user
    ensure_user(user.id, username=user.username, first_name=user.first_name, last_name=user.last_name)
    is_admin = (user.id == ADMIN_ID)
    txt = (
        "🚀 <b>TON_Mining_Bot</b>\n\n"
        "Bienvenido. Aquí tienes las opciones principales. Pulsa un botón.\n\n"
        "👤 Usa /help para comandos."
    )
    bot.send_message(message.chat.id, txt, reply_markup=main_menu_keyboard(is_admin))

@bot.message_handler(commands=["help"])
def cmd_help(message):
    txt = (
        "Comandos disponibles:\n"
        "/start - Volver al menú\n"
        "/balance - Ver balance\n\n"
        "También usa los botones del menú.\n"
    )
    bot.send_message(message.chat.id, txt)

@bot.message_handler(commands=["balance"])
def cmd_balance(message):
    ensure_user(message.from_user.id, username=message.from_user.username)
    bot.reply_to(message, format_balance_text(message.from_user.id))

# Inline button callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    uid = call.from_user.id
    ensure_user(uid, username=call.from_user.username, first_name=call.from_user.first_name)
    data = call.data

    if data == "menu":
        bot.edit_message_text(
            "Menú principal:",
            chat_id=cid, message_id=call.message.message_id,
            reply_markup=main_menu_keyboard(is_admin=(uid==ADMIN_ID))
        )
        return

    if data == "balance":
        bot.answer_callback_query(call.id, "Mostrando balance...")
        bot.send_message(cid, format_balance_text(uid))
        return

    if data == "stats":
        bal = get_balance(uid)
        last_mine = get_timestamp(uid, "last_mine")
        last_not = get_timestamp(uid, "last_notcoin")
        txt = (
            f"📊 Estadísticas:\n\n"
            f"Balance: <b>{bal}</b>\n"
            f"Última minería: {time_ago(last_mine)}\n"
            f"Último NotCoin: {time_ago(last_not)}\n"
        )
        bot.send_message(cid, txt)
        return

    if data == "mine":
        now = int(time.time())
        last = get_timestamp(uid, "last_mine")
        if now - last < MINING_COOLDOWN:
            remaining = MINING_COOLDOWN - (now - last)
            bot.answer_callback_query(call.id, f"⏳ Cooldown: espera {remaining}s")
            return
        set_timestamp(uid, "last_mine")
        bot.answer_callback_query(call.id, "Iniciando minería...")
        threading.Thread(target=simulate_mining, args=(cid, uid)).start()
        return

    if data == "notcoin":
        now = int(time.time())
        last = get_timestamp(uid, "last_notcoin")
        if now - last < NOTCOIN_COOLDOWN:
            remaining = NOTCOIN_COOLDOWN - (now - last)
            bot.answer_callback_query(call.id, f"⏳ Cooldown NotCoin: espera {remaining}s")
            return
        set_timestamp(uid, "last_notcoin")
        # show play keyboard: bet choices
        kb = types.InlineKeyboardMarkup(row_width=3)
        for b in (1, 5, 10, 20):
            kb.add(types.InlineKeyboardButton(f"Apostar {b}", callback_data=f"bet_{b}"))
        kb.add(types.InlineKeyboardButton("🔙 Volver", callback_data="menu"))
        bot.send_message(cid, "🎯 Elige cuánto apostar (NotCoin):", reply_markup=kb)
        return

    if data.startswith("bet_"):
        amount = int(data.split("_",1)[1])
        bal = get_balance(uid)
        if amount > bal:
            bot.answer_callback_query(call.id, "No tienes suficiente balance.")
            return
        # resolve game
        bot.answer_callback_query(call.id, "Jugando NotCoin...")
        result, change = resolve_notcoin(amount)
        change_amount = change
        # apply change
        change_balance(uid, change_amount)
        txt = f"🎯 NotCoin result: {result}\n"
        if change_amount >= 0:
            txt += f"✅ Ganaste <b>{change_amount}</b> NotCoin\n"
        else:
            txt += f"❌ Perdiste <b>{-change_amount}</b> NotCoin\n"
        txt += f"Nuevo balance: <b>{get_balance(uid)}</b>"
        bot.send_message(cid, txt)
        return

    if data == "admin":
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🔒 Panel admin solo para el propietario.")
            return
        bot.edit_message_text("🔧 Panel Admin:", chat_id=cid, message_id=call.message.message_id, reply_markup=admin_keyboard())
        return

    # Admin sub-actions
    if data == "admin_users":
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🔒 Acceso denegado.")
            return
        db = load_db()
        users = db.get("users", {})
        txt = "👥 Usuarios registrados:\n\n"
        for u in users.values():
            txt += f"- {u.get('first_name') or ''} @{u.get('username') or ''} (id: {u.get('id')}) bal: {u.get('balance')}\n"
        bot.send_message(cid, txt)
        return

    if data == "admin_add":
        # ask admin for target id and amount via reply
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🔒 Acceso denegado.")
            return
        msg = bot.send_message(cid, "📥 Envíame: <code>id amount</code> (ej: <code>7664138436 50</code>)")
        bot.register_next_step_handler(msg, admin_add_balance_step)
        return

    if data == "admin_broadcast":
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🔒 Acceso denegado.")
            return
        msg = bot.send_message(cid, "📣 Envíame el mensaje para broadcast (se enviará a todos los usuarios).")
        bot.register_next_step_handler(msg, admin_broadcast_step)
        return

# ---------------------------
# ADMIN HANDLERS (steps)
# ---------------------------
def admin_add_balance_step(message):
    try:
        parts = message.text.strip().split()
        target = int(parts[0])
        amount = int(parts[1])
    except:
        bot.reply_to(message, "Formato inválido. Usa: id amount")
        return
    newbal = change_balance(target, amount)
    bot.reply_to(message, f"✅ Añadidos {amount} NotCoin al usuario {target}. Nuevo balance: {newbal}")

def admin_broadcast_step(message):
    text = message.text
    db = load_db()
    users = db.get("users", {})
    sent = 0
    for u in list(users.values()):
        try:
            bot.send_message(u["id"], f"📣 Broadcast del admin:\n\n{text}")
            sent += 1
        except Exception:
            pass
    bot.reply_to(message, f"✅ Enviado a {sent} usuarios.")

# ---------------------------
# MINING SIMULATION
# ---------------------------
def simulate_mining(chat_id, user_id):
    # send initial message
    msg = bot.send_message(chat_id, "⛏️ Iniciando minería... preparando equipo.")
    try:
        # simple progress simulation
        steps = [
            "Conectando al nodo...",
            "Asignando hilos virtuales...",
            "Escaneando bloques...",
            "Optimizando recompensas..."
        ]
        for s in steps:
            time.sleep(1.2)
            bot.send_message(chat_id, f"⛏️ {s}")
        time.sleep(1.2)
        # reward calculation
        reward = random.randint(1, 12)  # small random reward
        change_balance(user_id, reward)
        bot.send_message(chat_id, f"🎉 Minería completada. Has ganado <b>{reward}</b> NotCoin.\n{format_balance_text(user_id)}")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error en minería: {e}")

# ---------------------------
# NOTCOIN GAME LOGIC
# ---------------------------
def resolve_notcoin(bet):
    # simple probabilistic game:
    # 40% perder (pierdes bet)
    # 45% ganar x1.5
    # 15% jackpot x4
    r = random.random()
    if r < 0.40:
        # lose
        return "Perdiste", -bet
    elif r < 0.85:
        gain = int(bet * 1.5)
        return "Ganaste x1.5", gain
    else:
        gain = int(bet * 4)
        return "Jackpot x4", gain

# ---------------------------
# UTIL
# ---------------------------
def time_ago(ts):
    if not ts:
        return "Nunca"
    diff = int(time.time()) - ts
    if diff < 60:
        return f"hace {diff}s"
    if diff < 3600:
        return f"hace {diff//60}m"
    if diff < 86400:
        return f"hace {diff//3600}h"
    return f"hace {diff//86400}d"

# ---------------------------
# FALLBACK: text messages (for convenience)
# ---------------------------
@bot.message_handler(func=lambda m: True, content_types=['text'])
def all_texts(message):
    txt = message.text.strip().lower()
    uid = message.from_user.id
    ensure_user(uid, username=message.from_user.username, first_name=message.from_user.first_name)
    if txt == "menu":
        cmd_start(message)
        return
    if txt.startswith("/admin") and uid == ADMIN_ID:
        # show admin keyboard
        bot.send_message(message.chat.id, "🔧 Panel admin:", reply_markup=admin_keyboard())
        return
    # short commands
    if txt in ("miner","mineria","mine","⛏️ mineria"):
        callback = types.CallbackQuery.__new__(types.CallbackQuery)  # not used; just call simulate directly
        threading.Thread(target=simulate_mining, args=(message.chat.id, uid)).start()
        bot.reply_to(message, "🔥 He iniciado una minería (simulada).")
        return

    # default: friendly reply + menu
    bot.send_message(message.chat.id, "Usa el menú para interactuar con el bot.", reply_markup=main_menu_keyboard(is_admin=(uid==ADMIN_ID)))

# ---------------------------
# START BOT (polling)
# ---------------------------
if __name__ == "__main__":
    print("Bot arrancando...")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Detenido por teclado.")
    except Exception as e:
        print("Error:", e)
