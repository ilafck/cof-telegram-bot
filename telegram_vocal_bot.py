import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

AUDIO_FOLDER = os.path.join(os.getcwd(), "vocaux/")
AFFILIATE_LINK_1 = "https://partners.raisefx.com/visit/?bta=163220&brand=raisefx"
AFFILIATE_LINK_2 = "https://go.fxcess.com/visit/?bta=35772&brand=fxcess"

# Configuration ChromaDB
client_db = chromadb.PersistentClient(path="./data_db")
collection = client_db.get_collection("erwin_trading")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Fonction pour récupérer le contexte pertinent
def get_context(query):
    query_embedding = model.encode([query]).tolist()[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    return " ".join(results["documents"][0])

# Fonction DeepSeek intégrée
async def deepseek_response(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    contexte_erwin = get_context(prompt)

    system_prompt = f"""
    Tu es un assistant trading institutionnel pour Erwin COF. Utilise ce contexte précis pour répondre clairement avec un ton convivial, engageant et direct :
    {contexte_erwin}
    """

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

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

# Gestion des messages
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
        # DeepSeek avec datas personnalisées
        response = await deepseek_response(text)
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

    print("Bot lancé avec DeepSeek et datas personnalisées ✅")

if __name__ == '__main__':
    main()