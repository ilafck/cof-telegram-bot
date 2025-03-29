from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = "7693055035:AAGZBIDFAsRA0WfFpoBUiF3moCj5nuJlcBw"
AUDIO_FOLDER = os.path.join(os.getcwd(), "vocaux/")
AFFILIATE_LINK_1 = "https://partners.raisefx.com/visit/?bta=163220&brand=raisefx"
AFFILIATE_LINK_2 = "https://go.fxcess.com/visit/?bta=35772&brand=fxcess"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        audio = open(AUDIO_FOLDER + "intro.ogg", "rb")
        await context.bot.send_voice(chat_id=chat_id, voice=audio)
    except FileNotFoundError:
        await update.message.reply_text("Erreur : intro.ogg non trouvé.")
        return
    keyboard = [["🔗 Lien RaiseFX", "🔗 Lien FXCess"], ["🔓 Accéder au VIP"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Choisis une option :", reply_markup=reply_markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    chat_id = update.effective_chat.id

    if "raisefx" in text:
        audio_file = "lien.ogg"
        reply_text = f"Voici ton lien RaiseFX : {AFFILIATE_LINK_1}"

    elif "fxcess" in text:
        audio_file = "lien.ogg"
        reply_text = f"Voici ton lien FXCess : {AFFILIATE_LINK_2}"

    elif "vip" in text:
        audio_file = "vip.ogg"
        reply_text = "Envoie ta preuve ici pour débloquer l’accès selon ton dépôt."

    else:
        await update.message.reply_text("Commande non reconnue. Utilise les boutons.")
        return

    try:
        audio = open(AUDIO_FOLDER + audio_file, "rb")
        await context.bot.send_voice(chat_id=chat_id, voice=audio)
        await update.message.reply_text(reply_text)
    except FileNotFoundError:
        await update.message.reply_text(f"Erreur : {audio_file} non trouvé.")

def main():
    port = int(os.environ.get('PORT', 8000))

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

    print("Bot lancé ✅")

if __name__ == '__main__':
    main()