from app.openai_client import get_client, get_model
from app.prompts import PROMPTS

async def analyze(profile_key: str, message: str, model_override: str | None):
    if profile_key not in PROMPTS:
        raise ValueError("profile_key inválido")

    client = get_client()
    model = get_model(model_override)
    prompt = PROMPTS[profile_key].format(message=message)

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um especialista em acessibilidade cognitiva."},
            {"role": "user", "content": prompt},
        ],
    )
    content = (completion.choices[0].message.content or "").strip()
    return content, prompt
