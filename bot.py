import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
historial = {}

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    mensaje = update.message.text
    if chat_id not in historial:
        historial[chat_id] = []
    historial[chat_id].append({"role": "user", "content": mensaje})
    respuesta = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        system="Eres un agente personal experto en nutricion y fitness. Respondes en espanol de forma cercana y practica.",
        messages=historial[chat_id]
    )
    texto = respuesta.content[0].text
    historial[chat_id].append({"role": "assistant", "content": texto})
    await update.message.reply_text(texto)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
