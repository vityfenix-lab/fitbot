import os
import base64
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

MI_CHAT_ID = 799200103
ELENA_CHAT_ID = 5571353487

usuarios_autorizados = {MI_CHAT_ID, ELENA_CHAT_ID}

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
historial = {}
entrenos = {}

SYSTEM_VITY = """Eres el asistente personal de Vity, hombre de 43 anos, cumple 44 el 15 de mayo de 2026, residente en Espana.

PERFIL FISICO:
Objetivo: recomposicion corporal a 69-70kg y 83-85cm de cintura al 12-13% de grasa corporal.
Ayuno intermitente: ventana de comida de 11:00 a 19:30.
Entrena 3 dias por semana combinando fuerza y cardio.

LESIONES:
- Epicondilitis bilateral en codos (muy superada pero vigilar cargas altas y agarre prolongado)
- Zona lumbar sensible con pesos altos: priorizar core, evitar carga axial excesiva

ENTRENAMIENTO Y ESPECIALIDADES:
Eres experto en entrenamiento funcional, core, gomas de resistencia, movilidad, cardio y fuerza.
Conoces toda la maquinaria de gimnasio y tambien entrenos en casa con recursos limitados.
Eres experto en correccion postural, higiene postural, trabajo de fascia y estiramientos terapeuticos.
Disenyas rutinas personalizadas, corriges tecnica, propones progresiones y periodizacion.
Tienes conocimiento de todos los metodos de entrenamiento contrastados cientificamente.
Siempre adaptas los ejercicios a sus lesiones. Priorizas core, movilidad y postura como base.
Para codos: evitar agarre prolongado o extension con mucha carga.
Para lumbar: sustituir carga axial por alternativas seguras cuando sea necesario.

NUTRICION:
Perfil lipidico elevado: limitar carne roja a 1 vez por semana, queso duro max 20g al dia.
Prioridades: pescado azul 4 veces por semana, avena diaria, legumbres 4 veces por semana, nueces 20-25g diarios, aguacate 3 veces por semana.
Usa proteina whey isolate Prozis post-entrenamiento.
Excluir: coliflor, brocoli, pure, caldos, patata cocida.

ANALISIS DE CONTENIDO:
Cuando analices fotos de comida valora si encaja con su plan.
Cuando analices fotos corporales comenta el progreso de forma positiva y constructiva.
Cuando analices PDFs o informes medicos extrae lo relevante y adaptalo a su plan.

TONO:
Habla como un amigo experto: cercano, coloquial, practico y motivador.
De vez en cuando incluye algun toque de humor ligero y natural, sin pasarte.
Responde siempre en espanol."""

SYSTEM_ELENA = """Eres el asistente personal de Elena, mujer de 45 anos, cumple 46 el 28 de julio de 2026, residente en Espana.

PERFIL FISICO:
Medidas actuales: 61kg, 1,65m altura, 80cm cintura.
Objetivos: afinar cintura, ganar fuerza y tonificar.
Actividad: 2-3 dias gimnasio mas baile. Media de 15000 pasos diarios en el trabajo.

LESIONES:
- Ligeras molestias en psoas. Perfil completo pendiente de actualizar.

ENTRENAMIENTO:
Experta en entrenamiento funcional, tonificacion, movilidad, correccion postural y fuerza para mujeres.
Tienes en cuenta su alto nivel de actividad diaria para no sobrecargarla.
Cuidas especialmente la zona del psoas en los ejercicios que propones.

NUTRICION:
No le gusta el queso.
Suplementos: magnesio y colageno.
Abierta a incorporar proteina si se considera optimo.

Cuando analices fotos de comida valora si encaja con sus objetivos.
Cuando analices PDFs o informes medicos extrae lo relevante y adapatalo a su plan.
Nunca menciones ni compartas informacion de otros usuarios.
Responde siempre en espanol de forma cercana, practica y motivadora."""

SYSTEM_GENERAL = """Eres un asistente experto en nutricion, fitness, entrenamiento personal y correccion postural.
Ayudas a las personas con consejos personalizados de alimentacion, entrenamiento y habitos saludables.
Responde siempre en espanol de forma cercana, practica y motivadora."""

def get_system(chat_id):
    if chat_id == MI_CHAT_ID:
        return SYSTEM_VITY
    elif chat_id == ELENA_CHAT_ID:
        return SYSTEM_ELENA
    else:
        return SYSTEM_GENERAL

async def check_acceso(update, context):
    chat_id = update.effective_chat.id
    if chat_id not in usuarios_autorizados:
        await update.message.reply_text("No tienes acceso a este bot. Contacta con el administrador.")
        nombre = update.effective_user.first_name or "Desconocido"
        username = update.effective_user.username or "sin username"
        await context.bot.send_message(
            chat_id=MI_CHAT_ID,
            text=f"Intento de acceso no autorizado:\nNombre: {nombre}\nUsername: @{username}\nID: {chat_id}"
        )
        return False
    return True

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

async def entreno(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_acceso(update, context):
        return
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Uso: /entreno pecho y triceps 45min")
        return
    registro = " ".join(context.args)
    if chat_id not in entrenos:
        entrenos[chat_id] = []
    entrenos[chat_id].append(registro)
    await update.message.reply_text(f"Entreno registrado: {registro}\nLlevas {len(entrenos[chat_id])} entrenos en esta sesion. Sigue asi!")

async def mis_entrenos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_acceso(update, context):
        return
    chat_id = update.effective_chat.id
    if chat_id not in entrenos or not entrenos[chat_id]:
        await update.message.reply_text("No tienes entrenos registrados todavia.")
        return
    lista = "\n".join([f"{i+1}. {e}" for i, e in enumerate(entrenos[chat_id])])
    await update.message.reply_text(f"Tus entrenos registrados:\n{lista}")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_acceso(update, context):
        return
    chat_id = update.effective_chat.id
    mensaje = update.message.text
    if chat_id not in historial:
        historial[chat_id] = []
    historial[chat_id].append({"role": "user", "content": mensaje})
    respuesta = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        system=get_system(chat_id),
        messages=historial[chat_id]
    )
    texto = respuesta.content[0].text
    historial[chat_id].append({"role": "assistant", "content": texto})
    await update.message.reply_text(texto)

async def responder_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_acceso(update, context):
        return
    chat_id = update.effective_chat.id
    await update.message.reply_text("Analizando la imagen, un momento...")
    foto = update.message.photo[-1]
    caption = update.message.caption or "Analiza esta imagen en el contexto de mi plan de nutricion y entrenamiento."
    foto_file = await context.bot.get_file(foto.file_id)
    foto_bytes = await foto_file.download_as_bytearray()
    foto_b64 = base64.standard_b64encode(foto_bytes).decode("utf-8")
    respuesta = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        system=get_system(chat_id),
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": foto_b64}},
                {"type": "text", "text": caption}
            ]
        }]
    )
    texto = respuesta.content[0].text
    await update.message.reply_text(texto)

async def responder_documento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_acceso(update, context):
        return
    chat_id = update.effective_chat.id
    doc = update.message.document
    caption = update.message.caption or "Analiza este documento en el contexto de mi plan de nutricion y entrenamiento."
    mime = doc.mime_type or ""
    await update.message.reply_text("Procesando el documento, un momento...")
    doc_file = await context.bot.get_file(doc.file_id)
    doc_bytes = await doc_file.download_as_bytearray()
    doc_b64 = base64.standard_b64encode(doc_bytes).decode("utf-8")
    if "pdf" in mime:
        content = [
            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": doc_b64}},
            {"type": "text", "text": caption}
        ]
    elif "image" in mime:
        content = [
            {"type": "image", "source": {"type": "base64", "media_type": mime, "data": doc_b64}},
            {"type": "text", "text": caption}
        ]
    else:
        await update.message.reply_text("Formato no soportado. Puedes enviarme PDFs o imagenes.")
        return
    respuesta = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        system=get_system(chat_id),
        messages=[{"role": "user", "content": content}]
    )
    texto = respuesta.content[0].text
    await update.message.reply_text(texto)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("autorizar", autorizar))
app.add_handler(CommandHandler("desautorizar", desautorizar))
app.add_handler(CommandHandler("entreno", entreno))
app.add_handler(CommandHandler("misentrenos", mis_entrenos))
app.add_handler(MessageHandler(filters.PHOTO, responder_foto))
app.add_handler(MessageHandler(filters.Document.ALL, responder_documento))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
