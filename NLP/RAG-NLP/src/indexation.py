"""
Étape 3 du RAG : Embeddings (HuggingFace) + stockage vectoriel (ChromaDB).

On transforme chaque chunk en vecteur grâce à un modèle d'embedding HuggingFace,
puis on stocke ces vecteurs dans ChromaDB (base vectorielle locale).

Choix du modèle : `intfloat/multilingual-e5-base`. Contrairement aux modèles de
similarité « symétrique » (ex. paraphrase-MiniLM, entraînés à rapprocher deux
phrases de même sens), E5 est entraîné pour la RECHERCHE « asymétrique » : une
question COURTE doit retrouver un passage LONG. C'est exactement notre cas (RAG),
et le gain de pertinence sur des documents français est net.

⚠️ Particularité d'E5 : il faut préfixer explicitement chaque texte selon son
rôle — « query: » pour une question, « passage: » pour un chunk indexé. Sans ces
préfixes, la qualité s'effondre. La sous-classe `E5Embeddings` ci-dessous s'en
charge automatiquement, de sorte que le reste du code ne s'en préoccupe pas.

On normalise les vecteurs pour que la similarité cosinus soit fiable à la recherche.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Doit rester identique au tokenizer utilisé dans chunking.py (cohérence des tokens).
MODELE_EMBEDDING = "intfloat/multilingual-e5-base"

# Dossier où ChromaDB persiste les vecteurs sur le disque.
DOSSIER_INDEX = "data/index"

# On garde l'objet embeddings en mémoire (le charger relit ~440 Mo de modèle).
_embeddings = None


class E5Embeddings(HuggingFaceEmbeddings):
    """
    Embeddings E5 avec préfixage automatique.

    E5 distingue le rôle du texte : on encode les chunks indexés avec « passage: »
    et les questions avec « query: ». LangChain appelle déjà deux méthodes
    distinctes (`embed_documents` pour l'index, `embed_query` pour la recherche) :
    il suffit donc d'ajouter le bon préfixe dans chacune.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return super().embed_documents([f"passage: {t}" for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return super().embed_query(f"query: {text}")


def get_embeddings() -> HuggingFaceEmbeddings:
    """Initialise le modèle d'embedding HuggingFace une seule fois."""
    global _embeddings
    if _embeddings is None:
        _embeddings = E5Embeddings(
            model_name=MODELE_EMBEDDING,
            model_kwargs={"device": "cpu"},          # 'cuda' si GPU Nvidia dispo
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def construire_index(documents, dossier: str = DOSSIER_INDEX) -> Chroma:
    """
    Construit (ou écrase) la base vectorielle à partir d'une liste de chunks.

    Renvoie l'objet Chroma prêt pour la recherche.
    """
    base = Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        persist_directory=dossier,
    )
    return base


def charger_index(dossier: str = DOSSIER_INDEX) -> Chroma:
    """Recharge une base vectorielle déjà construite et persistée sur disque."""
    return Chroma(
        persist_directory=dossier,
        embedding_function=get_embeddings(),
    )
