"""
Étapes 4 et 5 du RAG : Recherche (retrieval) + Génération (LLM).

Le principe du RAG (Retrieval-Augmented Generation) :
1. On transforme la question en vecteur et on récupère dans ChromaDB les chunks
   les plus proches (les passages pertinents des factures / devis).
2. On donne ces passages comme CONTEXTE à un LLM, qui rédige la réponse.

Objectif : éviter les hallucinations. Le modèle ne répond que d'après les
documents fournis, pas d'après ses connaissances générales.

Deux backends de génération sont disponibles (variable `LLM_BACKEND`) :

- "ollama"  (défaut) : `llama3` servi en local par Ollama. Llama 3 (8B, contexte
  8k tokens) lit beaucoup mieux les tableaux que flan-t5 et extrait correctement
  les montants, même depuis la sérialisation « en triplets » de Docling.

- "flan-t5"          : `google/flan-t5-large` (HuggingFace), cité dans les
  consignes. Léger et 100 % HuggingFace, mais limité à 512 tokens en entrée et
  faible en extraction sur tableaux. Conservé comme repli / point de comparaison.
"""

# Backend de génération : "ollama" ou "flan-t5".
LLM_BACKEND = "ollama"

# --- Config Ollama ---
MODELE_OLLAMA = "llama3"

# --- Config flan-t5 (HuggingFace) ---
MODELE_LLM = "google/flan-t5-large"
# flan-t5 n'accepte que 512 tokens EN ENTRÉE. Au-delà, le prompt est tronqué par
# la droite (= la question et « Réponse : » sautent), ce qui ruine la génération.
# On assemble donc le contexte sous ce budget. Llama 3 (8k) n'en a pas besoin.
MAX_INPUT_TOKENS = 512
MARGE_TOKENS = 12

# Nombre de chunks récupérés pour construire le contexte.
NB_CHUNKS = 4

_generateur = None
_tokenizer = None


def get_tokenizer():
    """Charge le tokenizer de flan-t5 une seule fois (sert à mesurer le prompt)."""
    global _tokenizer
    if _tokenizer is None:
        from transformers import AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(MODELE_LLM)
    return _tokenizer


def get_generateur():
    """Initialise le LLM choisi une seule fois et renvoie une fonction prompt -> texte."""
    global _generateur
    if _generateur is not None:
        return _generateur

    if LLM_BACKEND == "ollama":
        from langchain_ollama import ChatOllama

        # temperature=0 : réponses déterministes et factuelles (pas de créativité).
        llm = ChatOllama(model=MODELE_OLLAMA, temperature=0)
        _generateur = lambda prompt: llm.invoke(prompt).content
    else:  # flan-t5
        from transformers import pipeline

        pipe = pipeline(
            "text2text-generation",
            model=MODELE_LLM,
            tokenizer=get_tokenizer(),
            max_new_tokens=256,
            truncation=True,  # filet de sécurité ; en pratique le budget évite d'y arriver
        )
        _generateur = lambda prompt: pipe(prompt)[0]["generated_text"]

    return _generateur


def _formater_bloc(d) -> str:
    """Met en forme un chunk récupéré (en-tête de source + contenu)."""
    source = d.metadata.get("source", "document")
    pages = d.metadata.get("pages", "")
    entete = f"[Source : {source}" + (f", page(s) {pages}" if pages else "") + "]"
    return f"{entete}\n{d.page_content}"


def _formater_contexte(documents, question: str = "") -> str:
    """
    Concatène les chunks récupérés en un bloc de contexte.

    Avec flan-t5 (512 tokens max), on assemble sous un budget de tokens : on ajoute
    les blocs un par un tant que le prompt COMPLET reste sous `MAX_INPUT_TOKENS`, et
    on tronque le dernier bloc qui dépasse plutôt que de l'ignorer. Ainsi le LLM
    voit toujours la question et un maximum de contexte pertinent.

    Avec Ollama/Llama 3 (8k de contexte), aucun budget serré n'est nécessaire : on
    transmet tous les chunks.
    """
    if LLM_BACKEND != "flan-t5":
        return "\n\n".join(_formater_bloc(d) for d in documents)

    tok = get_tokenizer()
    budget = MAX_INPUT_TOKENS - MARGE_TOKENS

    # Coût du gabarit seul (prompt avec un contexte vide) : instruction + question.
    cout_gabarit = len(tok.encode(construire_prompt(question, ""), add_special_tokens=True))

    blocs = []
    total = cout_gabarit
    for d in documents:
        bloc = _formater_bloc(d)
        # +2 pour le séparateur « \n\n » entre les blocs.
        cout = len(tok.encode(bloc, add_special_tokens=False)) + (2 if blocs else 0)
        if total + cout <= budget:
            blocs.append(bloc)
            total += cout
            continue
        # Le bloc ne tient pas entier : on en garde le début si la place le justifie.
        reste = budget - total - (2 if blocs else 0)
        if reste > 20:
            ids = tok.encode(bloc, add_special_tokens=False)[:reste]
            blocs.append(tok.decode(ids, skip_special_tokens=True))
        break

    return "\n\n".join(blocs)


def construire_prompt(question: str, contexte: str) -> str:
    """Construit l'instruction envoyée au LLM (consignes anti-hallucination)."""
    return (
        "Tu es un assistant qui répond à des questions sur des documents "
        "(factures, devis). Réponds en français, de façon précise et concise, "
        "en t'appuyant UNIQUEMENT sur le contexte ci-dessous. Si la réponse ne "
        "figure pas dans le contexte, réponds : « Je ne trouve pas cette "
        "information dans le document. »\n\n"
        f"Contexte :\n{contexte}\n\n"
        f"Question : {question}\n"
        "Réponse :"
    )


def repondre(question: str, base, nb_chunks: int = NB_CHUNKS):
    """
    Exécute le pipeline RAG complet pour une question.

    Renvoie un tuple (reponse_texte, documents_sources) afin de pouvoir afficher
    les passages utilisés dans l'interface (transparence / vérifiabilité).
    """
    # 1. Recherche des chunks les plus proches dans la base vectorielle.
    documents = base.similarity_search(question, k=nb_chunks)

    if not documents:
        return "Aucun document indexé. Charge d'abord un PDF.", []

    # 2. Construction du contexte + du prompt.
    contexte = _formater_contexte(documents, question=question)
    prompt = construire_prompt(question, contexte)

    # 3. Génération de la réponse par le LLM.
    reponse = get_generateur()(prompt).strip()

    return reponse, documents
