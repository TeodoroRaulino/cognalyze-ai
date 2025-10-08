from app.openai_client import get_client, get_model
from app.prompts import PROMPTS

PROMPT_UPDATE_QUESTIONNAIRE = "atualizacao_questionario_v3"

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

async def update_questionnaire(profile_description: str, actual_questionnaire_md: str, new_questionnaire_md: str, model_override: str | None):
    client = get_client()
    model = get_model(model_override)

    prompt = PROMPTS[PROMPT_UPDATE_QUESTIONNAIRE]

    data = {
        "profile_description": profile_description,
        "actual_questionnaire_md": actual_questionnaire_md
    }

    prompt = prompt.format(**data)

    response = await client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": new_questionnaire_md,
            },
        ],
    )

    return response.output_text
