from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = "7693055035:AAGZBIDFAsRA0WfFpoBUiF3moCj5nuJlcBw"
AUDIO_FOLDER = "vocaux/"
AFFILIATE_LINK = "https://partners.raisefx.com/visit/?bta=163220&brand=raisefx"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_voice(chat_id=chat_id, voice=open(AUDIO_FOLDER + "intro.ogg", "rb"))
    keyboard = [["🔗 Je veux le lien"], ["🔓 Accéder au VIP"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Choisis une option :", reply_markup=reply_markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    chat_id = update.effective_chat.id

    if "lien" in text:
        await context.bot.send_voice(chat_id=chat_id, voice=open(AUDIO_FOLDER + "lien.ogg", "rb"))
        await update.message.reply_text(f"Voici ton lien : {AFFILIATE_LINK}")
    elif "vip" in text:
        await context.bot.send_voice(chat_id=chat_id, voice=open(AUDIO_FOLDER + "vip.ogg", "rb"))
        await update.message.reply_text("Envoie ta preuve ici pour débloquer l’accès selon ton dépôt.")
    else:
        await update.message.reply_text("Commande non reconnue. Utilise les boutons.")

def main():
    port = int(os.environ.get('PORT', 8000))  # <-- Render choisira automatiquement le port

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Webhook configuration spécifique pour Render
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

    print("Bot lancé ✅")

if __name__ == '__main__':
    main()