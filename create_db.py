import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./data_db")
collection = client.create_collection("erwin_trading")

model = SentenceTransformer('all-MiniLM-L6-v2')

documents = [
    # Style & Accueil
    "Salut [Prénom] ! Bienvenue 🚀 Peux-tu me donner ton prénom pour que je sache à qui je parle ? 😊",
    "Enchanté [Prénom] ! Tu cherches à rejoindre notre VIP ? Voici toutes les options disponibles pour toi 👇",
    
    # Offres VIP
    "Dépôt de 500€ via broker partenaire : accès VIP gratuit.",
    "Dépôt de 1000€ via broker partenaire : accès VIP + Mentorat gratuit.",
    "VIP Diamond : 165 USDT/mois.",
    "VIP Crypto : 149€/mois.",
    "Mentorship seul : 175€/mois.",
    "Trading Room Live : 200€/mois.",
    
    # Instructions Agent
    "Demander les infos utilisateur (nom, expérience, objectifs). Présenter services adaptés. Donner liens affiliés. Valider inscription. Donner accès VIP et instructions.",
    
    # FAQ
    "PropFirm : Entreprises fournissant des capitaux aux traders sous certaines conditions.",
    "Copy trading : Copier les transactions d’un trader expérimenté.",
    "Mentorship : Programme d'accompagnement pour apprendre le trading avec un expert.",
    "Paiement : crypto, Revolut, carte bancaire.",
    "Lot : Taille d'une position sur un marché financier.",
    "Stop Loss (SL) : Niveau de fermeture automatique pour limiter les pertes.",
    "Symboles : XAUUSD (or), NAS100 (Nasdaq).",
    "Bots : systèmes automatisés gérant les inscriptions et paiements.",
    "Trading Room : espace d'analyse de marché en direct."
]

embeddings = model.encode(documents).tolist()

collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=[f"doc{i}" for i in range(len(documents))]
)

print("✅ Base vectorielle prête !")