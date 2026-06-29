"""
Test automatique de bout en bout du pipeline RAG (sans interface Gradio).

Ce script enchaîne les 5 étapes sur un PDF d'exemple :
    1. Ingestion Docling   (PDF -> document structuré)
    2. Chunking            (HybridChunker)
    3. + 4. Indexation     (embeddings HuggingFace + ChromaDB)
    5. Questions/Réponses  (retrieval + génération flan-t5)

Objectif : vérifier en UNE commande que tout fonctionne et observer la
qualité des réponses + les sources utilisées.

Lancement :
    python3 test_rag.py                       # PDF par défaut
    python3 test_rag.py "data/pdf/devis_jardin_garcia.pdf"   # autre PDF
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Charge HF_TOKEN avant les imports qui téléchargent les modèles.
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingestion import convertir_pdf
from chunking import decouper_document
from indexation import construire_index
from rag import repondre


# PDF testé par défaut (modifiable en argument de ligne de commande).
PDF_PAR_DEFAUT = "data/pdf/FACTURE 1100481.pdf"

# Questions posées automatiquement. Adapte-les à ton document si besoin.
QUESTIONS = [
    "Quel est le montant total TTC ?",
    "Quel est le taux de TVA appliqué ?",
    "Quels sont les articles ou prestations facturés ?",
    "Quelle est la date du document ?",
    # Question hors-sujet : le système doit dire qu'il ne sait pas (anti-hallucination).
    "Quelle est la capitale de l'Australie ?",
]


def titre(texte: str) -> None:
    """Affiche un séparateur lisible dans la console."""
    print("\n" + "=" * 70)
    print(texte)
    print("=" * 70)


def main() -> None:
    chemin = sys.argv[1] if len(sys.argv) > 1 else PDF_PAR_DEFAUT
    nom = Path(chemin).name

    if not Path(chemin).exists():
        print(f"❌ PDF introuvable : {chemin}")
        sys.exit(1)

    # --- Étape 1 : Ingestion ---
    titre(f"1) INGESTION (Docling) — {nom}")
    document, markdown = convertir_pdf(chemin)
    print("Aperçu du Markdown extrait (tableaux préservés) :\n")
    print(markdown[:1200])

    # --- Étape 2 : Chunking ---
    titre("2) CHUNKING (HybridChunker)")
    chunks = decouper_document(document, source=nom)
    print(f"{len(chunks)} chunks générés.")
    if not chunks:
        print("❌ Aucun chunk : impossible de continuer.")
        sys.exit(1)
    print("\nExemple de chunk #0 :")
    print(chunks[0].page_content[:300])

    # --- Étapes 3 + 4 : Indexation ---
    titre("3+4) INDEXATION (embeddings HuggingFace + ChromaDB)")
    dossier = f"data/index/_test_{Path(nom).stem}"
    base = construire_index(chunks, dossier=dossier)
    print(f"✅ Base vectorielle construite dans « {dossier} ».")

    # --- Étape 5 : Questions / Réponses ---
    titre("5) QUESTIONS / RÉPONSES (retrieval + flan-t5)")
    for question in QUESTIONS:
        reponse, sources = repondre(question, base)
        print(f"\n❓ {question}")
        print(f"💬 {reponse}")
        if sources:
            refs = ", ".join(
                f"{d.metadata.get('source', '?')} (p. {d.metadata.get('pages') or '?'})"
                for d in sources
            )
            print(f"   📎 Sources : {refs}")

    titre("✅ TEST TERMINÉ")
    print("Vérifie que les montants/chiffres correspondent bien au PDF,")
    print("et que la question hors-sujet n'a PAS inventé de réponse.")


if __name__ == "__main__":
    main()
