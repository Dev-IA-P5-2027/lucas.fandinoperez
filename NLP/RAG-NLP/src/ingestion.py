"""
Étape 1 du RAG : Ingestion des PDF.

On utilise Docling (IBM, open source) car il est excellent pour les documents
qui contiennent des tableaux (factures, devis). Sa brique TableFormer reconnaît
la STRUCTURE des tableaux (lignes / colonnes / en-têtes) au lieu de tout aplatir
en texte brut. C'est le point clé pour un RAG spécialisé sur des données tabulaires.

On expose deux objets utiles pour la suite :
- le document Docling complet (`DoclingDocument`), nécessaire au chunker structuré ;
- le Markdown propre (pratique pour le debug et l'affichage).
"""

from pathlib import Path

from docling.document_converter import DocumentConverter


# On garde un seul convertisseur en mémoire : son initialisation charge des
# modèles (mise en page + TableFormer), c'est coûteux, inutile de le refaire.
_convertisseur = None


def _get_convertisseur() -> DocumentConverter:
    """Initialise le convertisseur Docling une seule fois (paresseux)."""
    global _convertisseur
    if _convertisseur is None:
        _convertisseur = DocumentConverter()
    return _convertisseur


def convertir_pdf(chemin_pdf: str):
    """
    Convertit un PDF en document Docling structuré.

    Renvoie un tuple (document_docling, texte_markdown) :
    - document_docling : sert d'entrée au chunker de l'étape 2 ;
    - texte_markdown   : version lisible (tableaux conservés en Markdown).
    """
    chemin = Path(chemin_pdf)
    if not chemin.exists():
        raise FileNotFoundError(f"PDF introuvable : {chemin}")

    convertisseur = _get_convertisseur()

    # Docling analyse toute la mise en page : titres, paragraphes, tableaux.
    resultat = convertisseur.convert(str(chemin))
    document = resultat.document

    # Export Markdown : les tableaux sont rendus avec la syntaxe '| col | col |'.
    texte_markdown = document.export_to_markdown()

    return document, texte_markdown


if __name__ == "__main__":
    # Petit test manuel sur une facture d'exemple.
    doc, markdown = convertir_pdf("data/pdf/FACTURE 1100481.pdf")
    print(markdown[:2000])
