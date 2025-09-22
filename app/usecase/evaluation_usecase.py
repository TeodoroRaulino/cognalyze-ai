from app.openai_client import get_client, get_model
from app.prompts import PROMPTS

PROMPT_QUESTION = "avaliacao_questionario"
PROMPT_REPORT = "avaliacao_geral"

async def evaluate_image(questionnaire: str, image_base64: str):
    client = get_client()
    model = get_model()
    prompt = PROMPTS[PROMPT_QUESTION].format(message=questionnaire)

    response = await client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": prompt },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
    )

    return response.output_text

async def generate_executive_report(results: list[str]):
    client = get_client()
    model = get_model()

    results_text = "\n\n".join(results)

    prompt = PROMPTS[PROMPT_REPORT]

    response = await client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": results_text,
            },
        ],
    )

    return response.output_text