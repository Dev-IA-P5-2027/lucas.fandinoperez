"""
Interface Gradio du RAG spécialisé sur documents tabulaires (factures, devis).

Parcours utilisateur :
1. L'utilisateur dépose un PDF puis clique sur « Indexer le document ».
   -> ingestion Docling, découpage HybridChunker, indexation ChromaDB.
2. Il pose ensuite ses questions dans le chat.
   -> recherche des passages pertinents + réponse générée par flan-t5 (HuggingFace).

Les passages utilisés pour répondre sont affichés sous la réponse (transparence).
"""

import sys
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

# Charge le .env (notamment HF_TOKEN) AVANT les imports qui déclenchent le
# téléchargement des modèles : les bibliothèques HuggingFace lisent
# automatiquement HF_TOKEN dans l'environnement.
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingestion import convertir_pdf
from chunking import decouper_document
from indexation import construire_index
from rag import repondre


def indexer_pdf(fichier, etat):
    """Convertit et indexe le PDF déposé. Stocke la base dans l'état de session."""
    if fichier is None:
        return etat, "⚠️ Dépose d'abord un fichier PDF."

    chemin = fichier.name if hasattr(fichier, "name") else fichier
    nom = Path(chemin).name

    try:
        document, _ = convertir_pdf(chemin)
        chunks = decouper_document(document, source=nom)
        if not chunks:
            return etat, f"❌ Aucun contenu exploitable extrait de « {nom} »."

        # Index dédié à ce document (dossier basé sur le nom du fichier).
        dossier = f"data/index/{Path(nom).stem}"
        base = construire_index(chunks, dossier=dossier)

        etat = {"base": base, "nom": nom}
        return etat, f"✅ « {nom} » indexé ({len(chunks)} chunks). Tu peux poser tes questions."
    except Exception as e:
        return etat, f"❌ Erreur pendant l'indexation : {e}"


def discuter(message, historique, etat):
    """Répond à une question en s'appuyant sur la base vectorielle de la session."""
    if not etat or "base" not in etat:
        historique = historique + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "⚠️ Indexe d'abord un PDF avant de poser une question."},
        ]
        return historique, ""

    reponse, sources = repondre(message, etat["base"])

    # On ajoute la liste des passages sources sous la réponse.
    if sources:
        details = "\n".join(
            f"- {d.metadata.get('source', '?')} "
            f"(page(s) {d.metadata.get('pages') or '?'})"
            for d in sources
        )
        reponse = f"{reponse}\n\n---\n*Sources utilisées :*\n{details}"

    historique = historique + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reponse},
    ]
    return historique, ""


with gr.Blocks(title="RAG Tabulaire — Factures & Devis") as demo:
    gr.Markdown(
        "# 📄 RAG spécialisé documents tabulaires\n"
        "Indexe tes **factures** et **devis** PDF. "
        "Extraction des tableaux avec **Docling**, recherche vectorielle **ChromaDB**, "
        "réponses générées par **llama3 (via Ollama)**."
    )

    etat = gr.State(value={})

    with gr.Row():
        with gr.Column(scale=1):
            fichier = gr.File(label="Document PDF", file_types=[".pdf"])
            bouton_index = gr.Button("Indexer le document", variant="primary")
            statut = gr.Markdown("")
        with gr.Column(scale=2):
            chat = gr.Chatbot(label="Conversation", height=420)
            question = gr.Textbox(
                label="Ta question",
                placeholder="Ex : Quel est le montant total TTC de la facture ?",
            )
            envoyer = gr.Button("Envoyer")

    bouton_index.click(indexer_pdf, inputs=[fichier, etat], outputs=[etat, statut])
    envoyer.click(discuter, inputs=[question, chat, etat], outputs=[chat, question])
    question.submit(discuter, inputs=[question, chat, etat], outputs=[chat, question])


if __name__ == "__main__":
    demo.launch()
