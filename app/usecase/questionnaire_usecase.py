from app.openai_client import get_client, get_model

async def generate_from_profile(profile_name: str, profile_description: str, model_override: str | None):
    client = get_client()
    model = get_model(model_override)

    prompt = f"""
Você é um especialista em acessibilidade cognitiva.

Com base no seguinte perfil:
Nome: {profile_name}
Descrição: \"\"\"{profile_description}\"\"\"

Gere um **questionário de avaliação de acessibilidade cognitiva** em Markdown para uso por um LLM ao analisar imagens.
Inclua critérios com **notas de 1 a 5 (Escala Likert)** e um **Resumo Executivo** com:
- Pontos Positivos
- Principais Problemas
- Pontuação Geral
- Prioridades de Correção

Entrada do usuário: {{message}}
""".strip()

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em acessibilidade cognitiva."},
            {"role": "user", "content": prompt},
        ],
    )
    content = (completion.choices[0].message.content or "").strip()
    return content, prompt

async def update_questionnaire(questionnaire_md: str, description_update: str, model_override: str | None):
    client = get_client()
    model = get_model(model_override)

    prompt = f"""
Você é um especialista em acessibilidade cognitiva.

Questionário atual (Markdown):
{questionnaire_md}

Atualize o questionário considerando a seguinte nova descrição/observação:
\"\"\"{description_update}\"\"\"

Mantenha a estrutura original (critérios com Likert 1–5 + Resumo Executivo) e adapte somente o necessário.
Entrada do usuário: {{message}}
""".strip()

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em acessibilidade cognitiva."},
            {"role": "user", "content": prompt},
        ],
    )
    content = (completion.choices[0].message.content or "").strip()
    return content, prompt
