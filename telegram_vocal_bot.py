import os
from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Utilisation de variables d'environnement pour sécuriser les clés API
TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

AUDIO_FOLDER = os.path.join(os.getcwd(), "vocaux/")
AFFILIATE_LINK_1 = "https://partners.raisefx.com/visit/?bta=163220&brand=raisefx"
AFFILIATE_LINK_2 = "https://go.fxcess.com/visit/?bta=35772&brand=fxcess"

client = OpenAI(api_key=OPENAI_API_KEY)

# Fonction mise à jour pour OpenAI >= 1.0.0
async def chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es un assistant expert en trading, spécialisé en brokers, création de comptes, utilisation de MetaTrader 4 et 5, et explications des bases du trading."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

# Commande /start
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
    await update.message.reply_text("Choisis une option ou pose-moi une question trading :", reply_markup=reply_markup)

# Gestion des messages et réponses ChatGPT
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
        # ChatGPT prend le relais pour les questions non reconnues
        response = await chatgpt_response(text)
        await update.message.reply_text(response)
        return

    try:
        audio = open(AUDIO_FOLDER + audio_file, "rb")
        await context.bot.send_voice(chat_id=chat_id, voice=audio)
        await update.message.reply_text(reply_text)
    except FileNotFoundError:
        await update.message.reply_text(f"Erreur : {audio_file} non trouvé.")

# Fonction principale pour Render (webhook)
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

    print("Bot lancé avec ChatGPT-3.5 ✅")

if __name__ == '__main__':
    main()