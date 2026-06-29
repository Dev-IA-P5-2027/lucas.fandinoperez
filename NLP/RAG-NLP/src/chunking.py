"""
Étape 2 du RAG : Découpage (chunking) adapté aux tableaux.

Plutôt que de découper bêtement le Markdown par titres (ce qui casse les tableaux),
on utilise le `HybridChunker` natif de Docling. Il a deux qualités essentielles
pour des factures / devis :

1. Il est conscient de la STRUCTURE : il garde un tableau cohérent et ne coupe pas
   une ligne en plein milieu.
2. Il est conscient des TOKENS : il regroupe / scinde le contenu pour rester sous
   la limite du modèle d'embedding (sinon le texte serait tronqué silencieusement).

En plus, la méthode `contextualize()` réinjecte dans chaque chunk son contexte
(titres de section, légende du tableau...). Concrètement, une ligne de tableau est
accompagnée des en-têtes de colonnes : c'est ce qui rend la recherche pertinente
sur des données tabulaires.

Chaque chunk est converti en `Document` LangChain pour s'intégrer avec ChromaDB.
"""

from docling.chunking import HybridChunker
from langchain_core.documents import Document

# Modèle d'embedding cible : le chunker s'en sert UNIQUEMENT pour compter les tokens
# et caler la taille des chunks. Doit être le même qu'à l'étape 3 (indexation), sinon
# les chunks risquent de dépasser la fenêtre du modèle d'embedding et d'être tronqués.
MODELE_TOKENIZER = "intfloat/multilingual-e5-base"


def decouper_document(document, source: str = "document") -> list[Document]:
    """
    Découpe un document Docling en chunks prêts pour l'embedding.

    - `document` : objet DoclingDocument issu de l'étape d'ingestion.
    - `source`   : nom du fichier d'origine, conservé en métadonnée.

    Renvoie une liste de `Document` LangChain (texte + métadonnées).
    """
    chunker = HybridChunker(tokenizer=MODELE_TOKENIZER)

    documents = []
    for i, chunk in enumerate(chunker.chunk(dl_doc=document)):
        # contextualize() = texte du chunk ENRICHI de son contexte (titres,
        # en-têtes de tableau...). C'est cette version qu'on embarque pour avoir
        # une recherche pertinente sur les lignes de tableaux.
        texte_enrichi = chunker.contextualize(chunk=chunk)

        # On récupère la / les page(s) d'origine si Docling l'expose, pour pouvoir
        # citer la source dans l'interface.
        pages = set()
        for item in getattr(chunk.meta, "doc_items", []) or []:
            for prov in getattr(item, "prov", []) or []:
                if getattr(prov, "page_no", None) is not None:
                    pages.add(prov.page_no)

        metadonnees = {
            "source": source,
            "chunk_id": i,
            "pages": ", ".join(str(p) for p in sorted(pages)) if pages else "",
        }

        documents.append(Document(page_content=texte_enrichi, metadata=metadonnees))

    return documents


if __name__ == "__main__":
    # Test manuel : on enchaîne ingestion + découpage.
    from ingestion import convertir_pdf

    doc, _ = convertir_pdf("data/pdf/FACTURE 1100481.pdf")
    chunks = decouper_document(doc, source="FACTURE 1100481.pdf")
    print(f"{len(chunks)} chunks générés.\n")
    for c in chunks[:3]:
        print("---", c.metadata, "---")
        print(c.page_content[:300], "\n")
