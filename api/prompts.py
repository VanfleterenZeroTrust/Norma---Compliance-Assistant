from typing import List, Dict, Any

def build_messages(question: str, contexts: List[Dict[str, Any]]):
    parts = []
    for i, c in enumerate(contexts, 1):
        src = c.get("source") or "Document"
        parts.append(f"[DOC {i}] {src}\n{c['content']}")
    context_text = "\n\n---\n".join(parts)

    system = (
        "Tu es un assistant qui répond en français de façon claire et précise. "
        "Tu NE DOIS utiliser que les informations présentes dans le CONTEXTE fourni. "
        "Quand tu utilises une information provenant d’un extrait, cite la référence "
        "sous la forme [DOC X] (X étant le numéro de l'extrait). "
        "Si l'information n'est pas dans le contexte, dis-le explicitement."
    )

    user = (
        f"CONTEXTE:\n{context_text}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Consigne: Rédige une réponse utile et structurée. "
        "Quand tu t'appuies sur un extrait, ajoute la référence [DOC X] correspondante. "
        "Ne fabrique pas d'informations hors du contexte."
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
