from typing import List, Optional
from app.schemas import ExistingProfile
from app.openai_client import get_client, get_model

def _build_profile_classification_prompt(description: str, existing: List[ExistingProfile]) -> str:
    prompt = (
        "Você é um assistente especializado em acessibilidade cognitiva. "
        "Sua tarefa é classificar descrições de usuários em perfis cognitivos existentes "
        "ou sugerir um novo perfil, caso necessário.\n\n"
        "Com base na descrição abaixo, identifique o perfil cognitivo correspondente. "
        "Se a descrição corresponder a mais de um perfil existente, você pode considerar uma combinação "
        "(ex: TEA + TDAH). Evite sugestões fora do escopo da acessibilidade.\n\n"
        f"Descrição recebida:\n{description}\n\n"
        "Perfis existentes:\n"
    )
    for p in existing:
        prompt += f"- Nome: {p.name}\n  Descrição: {p.description or 'Sem descrição'}\n"
    prompt += (
        "\nRetorne apenas o nome do perfil (sem explicações)."
    )
    return prompt

async def suggest_profile_name(description: str, existing_profiles: List[ExistingProfile], proposed_name: Optional[str] = None) -> str:
    """
    Retorna apenas um nome de perfil sugerido/normalizado a partir da descrição e dos perfis existentes.
    """
    client = get_client()
    model = get_model()
    prompt = _build_profile_classification_prompt(description, existing_profiles)

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em acessibilidade e perfis de usuários."},
            {"role": "user", "content": prompt},
        ],
    )
    decision = (completion.choices[0].message.content or "").strip()
    return decision or (proposed_name or "Perfil")
