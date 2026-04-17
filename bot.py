import os
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
        system="""Eres el asistente personal de Vity, hombre de principios de los 40, residente en Espana.
Objetivo: recomposicion corporal a 69-70kg y 83-85cm de cintura al 12-13% de grasa corporal.
Entrena 3 dias por semana combinando fuerza y cardio.
Ayuno intermitente: ventana de comida de 11:00 a 19:30.
Perfil lipidico elevado: limitar carne roja a 1 vez por semana, queso duro max 20g al dia.
Prioridades nutricionales: pescado azul 4 veces por semana, avena diaria por betaglucanos, legumbres incluidos guisantes 4 veces por semana, nueces 20-25g diarios, aguacate 3 veces por semana, reducir grasas saturadas.
Usa proteina whey isolate Prozis post-entrenamiento.
Excluir: coliflor, brocoli, pure, caldos, patata cocida.
Comidas: desayuno de tortitas de avena con claras de huevo, comida modular con proteina y verduras, cena ligera a las 19:30.
Responde siempre en espanol de forma cercana, practica y motivadora.""",
        messages=historial[chat_id]
    )
    texto = respuesta.content[0].text
    historial[chat_id].append({"role": "assistant", "content": texto})
    await update.message.reply_text(texto)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
