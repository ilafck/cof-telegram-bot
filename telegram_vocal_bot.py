import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Clés API via variables d'environnement
TOKEN = os.environ.get("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# Liens d'affiliation
AFFILIATE_LINK_1 = "https://partners.raisefx.com/visit/?bta=163220&brand=raisefx"
AFFILIATE_LINK_2 = "https://go.fxcess.com/visit/?bta=35772&brand=fxcess"
KUCOIN_LINK = "https://www.kucoin.com/r/af/rP6K1J3"

# Chemin des vocaux
AUDIO_FOLDER = os.path.join(os.getcwd(), "vocaux/")

# Configuration de la base de connaissances avec ChromaDB
client_db = chromadb.PersistentClient(path="./data_db")
from chromadb.utils import embedding_functions

collection_name = "erwin_trading"
try:
    collection = client_db.get_collection(collection_name)
except ValueError:
    collection = client_db.create_collection(
        name=collection_name,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    )

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_context(query):
    query_embedding = model.encode([query]).tolist()[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    return " ".join(results["documents"][0])

# Fonction IA DeepSeek avec gestion d'erreurs
async def deepseek_response(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
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

        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=8)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    except requests.exceptions.Timeout:
        return "⏳ Le serveur DeepSeek est un peu lent. Réessaie dans un instant."

    except requests.exceptions.RequestException:
        return "❌ L'assistant IA est momentanément indisponible. Pose une autre question ou réessaie plus tard."

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        audio = open(os.path.join(AUDIO_FOLDER, "intro.ogg"), "rb")
        await context.bot.send_voice(chat_id=chat_id, voice=audio)
    except FileNotFoundError:
        await update.message.reply_text("Erreur : intro.ogg non trouvé.")
        return

    keyboard = [
        ["🔗 Lien RaiseFX", "🔗 Lien FXCess"],
        ["💸 VIP Forex", "💰 VIP Crypto"],
        ["📤 J’ai fait mon dépôt"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text("Choisis une option ou pose-moi une question trading :", reply_markup=reply_markup)

# Handler principal
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    chat_id = update.effective_chat.id

    if "raisefx" in text:
        audio_file = "lien.ogg"
        reply_text = f"Voici ton lien RaiseFX : {AFFILIATE_LINK_1}"

    elif "fxcess" in text:
        audio_file = "lien.ogg"
        reply_text = f"Voici ton lien FXCess : {AFFILIATE_LINK_2}"

    elif "vip forex" in text:
        audio_file = "vip.ogg"
        reply_text = f"Félicitations pour ton accès VIP Forex ! Voici les liens :\n{AFFILIATE_LINK_1}\n{AFFILIATE_LINK_2}"

    elif "vip crypto" in text:
        audio_file = "vip.ogg"
        reply_text = f"Félicitations pour ton accès VIP Crypto ! Voici ton lien Kucoin :\n{KUCOIN_LINK}"

    elif "fait mon dépôt" in text or "j’ai fait mon dépôt" in text:
        await update.message.reply_text("Merci ! Envoie-moi une capture d’écran de ton dépôt. Une fois reçu, je valide manuellement ton accès VIP. 🔒")
        return

    else:
        response = await deepseek_response(text)
        await update.message.reply_text(response)
        return

    try:
        audio = open(os.path.join(AUDIO_FOLDER, audio_file), "rb")
        await context.bot.send_voice(chat_id=chat_id, voice=audio)
        await update.message.reply_text(reply_text)
    except FileNotFoundError:
        await update.message.reply_text(f"Erreur : {audio_file} non trouvé.")

# Lancement du bot
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

    print("Bot lancé avec DeepSeek, vocaux et fonctions VIP ✅")

if __name__ == '__main__':
    main()