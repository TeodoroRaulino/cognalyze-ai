from __future__ import annotations
import json
import logging
import os
from app.openai_client import get_client, get_model
from string import Template

logger = logging.getLogger("profile_create")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

DEBUG = os.getenv("DEBUG", "0") in ("1", "true", "True")

def _snip(text: str, n: int = 400) -> str:
    return text[:n] + ("…[truncated]" if len(text) > n else "")

PROMPT_JSON_SPEC = """
Você é um especialista em acessibilidade cognitiva.
Gere uma resposta ESTRITAMENTE em JSON (sem markdown, sem explicações) no formato:

{{
  "guidelines": "Markdown com diretrizes recomendadas (W3C/WCAG/COGA/GAIA) para o perfil informado",
  "questionnaire": "Markdown com questionário: critérios com notas Likert (1–5) e Resumo Executivo"
}}

Requisitos:
- "guidelines": sintetize recomendações práticas mapeadas às diretrizes W3C/WCAG/COGA/GAIA (ex.: WCAG 1.4.3, 2.4.6 etc). Entregue em Markdown com subtítulos e bullets.
- "questionnaire": Markdown com ~5–8 critérios numerados (1️⃣, 2️⃣, …), cada um com breve justificativa e campo para nota (Likert 1–5).
  Inclua ao final “Resumo Executivo” com: ✅ Pontos Positivos, ❌ Principais Problemas, 📊 Pontuação Geral (instrução: média das notas), 🔧 Prioridades de Correção.
- NÃO inclua cercas de código (```), apenas JSON puro.
- NÃO envolva o JSON em Markdown.

Contexto do perfil:
Nome: {name}
Descrição: \"\"\"{description}\"\"\"
"""

async def create_profile_assets(name: str, description: str, model_override: str | None = None) -> dict:
    """
    Retorna { "guidelines": str, "questionnaire": str } para o perfil informado.
    Com logs/prints em cada etapa para depuração.
    """
    logger.info("[create_profile_assets] start | name=%s", name)
    if DEBUG: print("[DEBUG] Montando prompt…")
    client = get_client()
    model = get_model(model_override)
    user_prompt = PROMPT_JSON_SPEC.format(name=os.name, description=description)
    print("Using user_prompt:", user_prompt)

    if DEBUG:
        print("[DEBUG] Modelo:", model)
        print("[DEBUG] Prompt (primeiros 400 chars):\n", _snip(user_prompt))

    try:
        if DEBUG: print("[DEBUG] Chamando OpenAI…")
        completion = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente especialista em acessibilidade (WCAG/COGA/GAIA) e geração de questionários."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        if DEBUG: print("[DEBUG] Resposta recebida da OpenAI")
    except Exception as e:
        logger.exception("[create_profile_assets] erro chamando OpenAI")
        raise RuntimeError(f"Falha na chamada do LLM: {e}")

    raw = (completion.choices[0].message.content or "").strip()
    logger.info("[create_profile_assets] raw length=%d", len(raw))
    if DEBUG:
        print("[DEBUG] Raw (primeiros 400 chars):\n", _snip(raw))

    # Tentativa de parse estrito de JSON
    try:
        data = json.loads(raw)
        guidelines = str(data.get("guidelines", "")).strip()
        questionnaire = str(data.get("questionnaire", "")).strip()

        if not guidelines or not questionnaire:
            msg = "JSON válido porém campos obrigatórios ausentes (guidelines/questionnaire vazios)."
            logger.error("[create_profile_assets] %s | raw_snip=%s", msg, _snip(raw))
            if DEBUG:
                print("[DEBUG][ERRO]", msg)
            raise ValueError(msg)

        logger.info("[create_profile_assets] sucesso")
        return {"guidelines": guidelines, "questionnaire": questionnaire}

    except json.JSONDecodeError as je:
        # Erro de JSON → fornece posição/linha/coluna e snippet
        err_msg = (
            f"JSON inválido: {je.msg} (pos={je.pos}, ln={je.lineno}, col={je.colno}). "
            f"Possível causa: modelo devolveu markdown ao invés de JSON puro. "
            f"raw_snip={_snip(raw)}"
        )
        logger.error("[create_profile_assets] %s", err_msg)
        if DEBUG:
            print("[DEBUG][JSONDecodeError]", err_msg)
        # Propaga erro mais claro para o controller
        raise ValueError(err_msg)

    except Exception as e:
        # Qualquer outro erro de validação
        err_msg = f"Falha ao processar JSON do LLM: {e}. raw_snip={_snip(raw)}"
        logger.error("[create_profile_assets] %s", err_msg)
        if DEBUG:
            print("[DEBUG][Exception]", err_msg)
        raise ValueError(err_msg)
