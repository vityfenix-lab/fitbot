import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

MI_CHAT_ID = 799200103
ELENA_CHAT_ID = 5571353487

usuarios_autorizados = {MI_CHAT_ID, ELENA_CHAT_ID}

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
historial = {}

SYSTEM_VITY = """Eres el asistente personal de Vity, hombre de 43 anos, cumple 44 el 15 de mayo de 2026, residente en Espana.
Objetivo: recomposicion corporal a 69-70kg y 83-85cm de cintura al 12-13% de grasa corporal.
Entrena 3 dias por semana combinando fuerza y cardio.
Ayuno intermitente: ventana de comida de 11:00 a 19:30.
Perfil lipidico elevado: limitar carne roja a 1 vez por semana, queso duro max 20g al dia.
Prioridades nutricionales: pescado azul 4 veces por semana, avena diaria, legumbres 4 veces por semana, nueces 20-25g diarios, aguacate 3 veces por semana.
Usa proteina whey isolate Prozis post-entrenamiento.
Excluir: coliflor, brocoli, pure, caldos, patata cocida.
Responde siempre en espanol de forma cercana, practica y motivadora."""

SYSTEM_GENERAL = """Eres un asistente experto en nutricion y fitness.
Ayudas a las personas con consejos personalizados de alimentacion, entrenamiento y habitos saludables.
Responde siempre en espanol de forma cercana, practica y motivadora."""

async def autorizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != MI_CHAT_ID:
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /autorizar 123456789")
        return
    nuevo_id = int(context.args[0])
    usuarios_autorizados.add(nuevo_id)
    await update.message.reply_text(f"Usuario {nuevo_id} autorizado.")

async def desautorizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != MI_CHAT_ID:
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /desautorizar 123456789")
        return
    nuevo_id = int(context.args[0])
    usuarios_autorizados.discard(nuevo_id)
    await update.message.reply_text(f"Usuario {nuevo_id} eliminado.")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "sin username"
    nombre = update.effective_user.first_name or "Desconocido"
    if chat_id not in usuarios_autorizados:
        await update.message.reply_text("No tienes acceso a este bot. Contacta con el administrador.")
        await context.bot.send_message(
            chat_id=MI_CHAT_ID,
            text=f"Intento de acceso no autorizado:\nNombre: {nombre}\nUsername: @{username}\nID: {chat_id}"
        )
        return
    mensaje = update.message.text
    if chat_id not in historial:
        historial[chat_id] = []
    historial[chat_id].append({"role": "user", "content": mensaje})
    system = SYSTEM_VITY if chat_id == MI_CHAT_ID else SYSTEM_GENERAL
    respuesta = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        system=system,
        messages=historial[chat_id]
    )
    texto = respuesta.content[0].text
    historial[chat_id].append({"role": "assistant", "content": texto})
    await update.message.reply_text(texto)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("autorizar", autorizar))
app.add_handler(CommandHandler("desautorizar", desautorizar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
