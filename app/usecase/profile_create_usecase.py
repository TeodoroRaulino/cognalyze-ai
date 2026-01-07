from __future__ import annotations

import json
import logging
import os
import re
from app.openai_client import get_client, get_model

logger = logging.getLogger("profile_create")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

DEBUG = os.getenv("DEBUG", "0") in ("1", "true", "True")


def _snip(text: str, n: int = 400) -> str:
    return text[:n] + ("…[truncated]" if len(text) > n else "")


# =========================
# Catálogo e Regras
# =========================

WCAG_INDEX = [
    {
        "id": "1.4.3",
        "title": "Contrast (Minimum)",
        "url": "https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum",
    },
    {
        "id": "1.4.11",
        "title": "Non-text Contrast",
        "url": "https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast",
    },
    {
        "id": "1.4.1",
        "title": "Use of Color",
        "url": "https://www.w3.org/WAI/WCAG22/Understanding/use-of-color",
    },
    {
        "id": "1.3.1",
        "title": "Info and Relationships",
        "url": "https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships",
    },
    {
        "id": "3.3.2",
        "title": "Labels or Instructions",
        "url": "https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions",
    },
]

# ⚠️ Mantido como você pediu: links com "-pattern"
COGA_INDEX = [
    {
        "id": "4.4.1",
        "title": "Use Clear Words (Pattern)",
        "url": "https://www.w3.org/TR/coga-usable/#use-clear-words-pattern",
    },
    {
        "id": "4.2.5",
        "title": "Clearly Identify Controls and Their Use (Pattern)",
        "url": "https://www.w3.org/TR/coga-usable/#clearly-identify-controls-and-their-use-pattern",
    },
    {
        "id": "4.2.7",
        "title": "Use Icons that Help the User (Pattern)",
        "url": "https://www.w3.org/TR/coga-usable/#use-icons-that-help-the-user-pattern",
    },
    {
        "id": "4.3.5",
        "title": "Break Media into Chunks (Pattern)",
        "url": "https://www.w3.org/TR/coga-usable/#break-media-into-chunks-pattern",
    },
]


def _render_reference_catalog() -> str:
    wcag_lines = "\n".join(
        f"  - {i['id']} — {i['title']} — {i['url']}" for i in WCAG_INDEX
    )
    coga_lines = "\n".join(
        f"  - {i['id']} — {i['title']} — {i['url']}" for i in COGA_INDEX
    )
    return (
        "CATÁLOGO DE REFERÊNCIAS (uso obrigatório):\n"
        "- **WCAG**:\n" + wcag_lines + "\n"
        "- **COGA**:\n" + coga_lines + "\n"
    )


_LIKERT_ANCHORS = (
    "Âncoras da Escala Likert (usar exatamente estas definições por critério):\n"
    "- **1 (Crítico/Não Atende)**: Falhas graves que impedem a compreensão; viola a(s) referência(s) WCAG indicada(s) e contraria o COGA.\n"
    "- **2 (Atende Insuficientemente)**: indica que há tentativas pontuais de atender ao critério, porém de forma incipiente ou inadequada, aproximando-se mais de uma falha crítica do que de um atendimento parcial\n"
    "- **3 (Parcialmente Atende)**: Há progresso visível, mas persistem obstáculos cognitivos relevantes; atende parcialmente a WCAG indicada; COGA aplicado de forma inconsistente.\n"
    "- **4 (Atende Adequadamente)**: indica que o critério é majoritariamente atendido, restando apenas ajustes pontuais ou inconsistências menores que impedem sua classificação como atendimento pleno\n"
    "- **5 (Atende Bem/Ótimo)**: Critério cumprido com clareza; boas práticas do COGA evidentes; WCAG indicada atendida sem ressalvas.\n"
)

_WCAG_COGA_HELP = (
    "Mapeamentos úteis para **imagens estáticas** (escolha os aplicáveis):\n"
    "- **Contraste de texto** → WCAG: 1.4.3.\n"
    "  COGA (escolha 1): 4.4.1 (Use Clear Words) quando legibilidade/clareza textual for o foco.\n"
    "- **Contraste de ícones/controles** → WCAG: 1.4.11.\n"
    "  COGA (escolha 1): 4.2.5 (Clearly Identify Controls) para tornar controles perceptíveis/identificáveis.\n"
    "- **Não depender apenas de cor** → WCAG: 1.4.1.\n"
    "  COGA (escolha 1): 4.2.5 (Clearly Identify Controls) para reforçar identificação por forma/rótulo/posição.\n"
    "- **Rótulos e instruções claros** → WCAG: 3.3.2.\n"
    "  COGA (escolha 1): 4.4.1 (Use Clear Words).\n"
    "- **Hierarquia e relações visuais (agrupamentos/estrutura)** → WCAG: 1.3.1.\n"
    "  COGA (escolha 1): 4.3.5 (Break Media into Chunks) quando o problema for 'quebrar em blocos/seções'.\n"
    "- **Ícones compreensíveis** → WCAG: 1.3.1 (consistência/relação) + (se contraste for problema, 1.4.11).\n"
    "  COGA (escolha 1): 4.2.7 (Use Icons that Help the User).\n"
)

_CITATION_RULES = (
    "REGRAS DE CITAÇÃO (OBRIGATÓRIAS):\n"
    "- Em **cada critério**, selecione **no máximo 2** itens da **WCAG (CATÁLOGO)** e **1** do **COGA (CATÁLOGO)**.\n"
    "- **Proibido** citar referência fora do catálogo (não inventar numeração/títulos/âncoras).\n"
    "- Se nada do catálogo se aplicar, escreva: **WCAG: N/A; COGA: N/A**.\n"
)

_RESUMO_RULES = (
    "APÓS listar os critérios/notas, gere obrigatoriamente um **Resumo Executivo (template, não preenchido)** contendo exatamente:\n"
    "- **✅ Pontos Positivos:**\n"
    "  - (preencher após a avaliação da imagem)\n"
    "  - (preencher após a avaliação da imagem)\n"
    "  - (preencher após a avaliação da imagem)\n"
    "- **❌ Principais Problemas:**\n"
    "  - (preencher após a avaliação da imagem)\n"
    "  - (preencher após a avaliação da imagem)\n"
    "  - (preencher após a avaliação da imagem)\n"
    "- **📊 Pontuação Geral:** (calcular média 1–5 após preencher as notas)\n"
    "- **🔧 Prioridades de Correção:**\n"
    "  1. (preencher após a avaliação da imagem)\n"
    "  2. (preencher após a avaliação da imagem)\n"
    "  3. (preencher após a avaliação da imagem)\n"
    "REGRAS:\n"
    "- **NÃO** invente pontuação real (ex.: 3,7 ou 4,2).\n"
    "- **NÃO** descreva problemas específicos da imagem, porque a imagem ainda será enviada depois.\n"
    "- O objetivo é gerar um **molde** de questionário que será usado por outro processo (ex.: `evaluate_image`).\n"
)

# ✅ Mudança: padroniza critérios com headings ### e remove dependência de "Critério X:"
_STATIC_RULES_SYSTEM = (
    "Você é um assistente especialista em acessibilidade cognitiva para **imagens estáticas**.\n"
    "REGRAS DURAS:\n"
    "1) A entrada é SEMPRE **uma imagem estática**. Não há vídeo, animação, transições, parallax, GIF ou movimento.\n"
    "2) **Não crie critérios** sobre animação, movimento, microinterações, hover, foco, autoplay, tempo ou áudio.\n"
    "3) Se a entrada mencionar reunião/processos/áudio/vídeo/motion, **reformule** o conceito para um **equivalente visual verificável**.\n"
    "4) **Questionário** (6–10 critérios): cada critério deve começar com um heading Markdown no formato:\n"
    "   ### <Nome do Critério>\n"
    "   E, abaixo, conter exatamente estes campos (na ordem):\n"
    "   - Objetivo Cognitivo:\n"
    "   - Como Avaliar (na imagem):\n"
    "   - Escala Likert:\n"
    "     - 1: ...\n"
    "     - 2: ...\n"
    "     - 3: ...\n"
    "     - 4: ...\n"
    "     - 5: ...\n"
    "   - Evidências a coletar:\n"
    "   - Referências: WCAG <...>; COGA <...> (≤2 WCAG + 1 COGA do CATÁLOGO ou N/A).\n"
    "   **Não usar prefixos como 'Critério X:'**.\n"
    "5) Ao final, **SEM preencher com dados reais**, gere o Resumo Executivo conforme o template abaixo.\n"
    "6) **Não liste referências irrelevantes** ao que é visível.\n"
    "\n"
    + _LIKERT_ANCHORS
    + "\n"
    + _WCAG_COGA_HELP
    + "\n"
    + _CITATION_RULES
    + "\n"
    + _RESUMO_RULES
    + "\n"
    + _render_reference_catalog()
)


# =========================
# PROMPT JSON (com regras injetadas)
# =========================
PROMPT_JSON_SPEC = """
Você é um especialista em acessibilidade cognitiva.
Gere uma resposta ESTRITAMENTE em JSON (sem markdown, sem explicações) no formato:

{{
  "guidelines": "Markdown com diretrizes recomendadas (W3C/WCAG/COGA/GAIA) para o perfil informado",
  "questionnaire": "Markdown com questionário: critérios com notas Likert (1–5) e Resumo Executivo"
}}

Requisitos:
- "guidelines": sintetize recomendações práticas mapeadas às diretrizes W3C/WCAG/COGA (cite GAIA apenas se realmente pertinente). Entregue em Markdown com subtítulos e bullets.
- "questionnaire": **seguir estritamente as REGRAS DURAS abaixo** (imagem estática, formato por critério, referências do CATÁLOGO, âncoras 1/2/3/4/5, Resumo Executivo).
- NÃO inclua cercas de código (```), apenas JSON puro.
- NÃO envolva o JSON em Markdown.

Contexto do perfil:
Nome: {name}
Descrição: \"\"\"{description}\"\"\"

REGRAS DURAS E CATÁLOGO (uso obrigatório):
{STATIC_RULES}
""".strip()


# =========================
# Pós-processamento + validação do questionário
# =========================

# Fallback robusto: remove variantes de "Critério X:" / "Critério - " / etc.
_CRITERION_PREFIX_RE = re.compile(
    r"(?mi)^(\s*[-*]?\s*)(?:\d+[\)\.]?\s*)?crit[eé]rio\s*\d*\s*[:\-—]\s*"
)

def _strip_criterion_prefixes(q: str) -> str:
    return _CRITERION_PREFIX_RE.sub(r"\1", q)

def _sanitize_questionnaire_template(q: str) -> str:
    """
    Substitui TUDO a partir de 'Resumo Executivo' por um template fixo,
    garantindo que nunca venha preenchido.
    """
    if "Resumo Executivo" not in q:
        return q

    template = (
        "Resumo Executivo\n"
        "✅ Pontos Positivos:\n"
        "- (preencher após a avaliação da imagem)\n"
        "- (preencher após a avaliação da imagem)\n"
        "- (preencher após a avaliação da imagem)\n"
        "❌ Principais Problemas:\n"
        "- (preencher após a avaliação da imagem)\n"
        "- (preencher após a avaliação da imagem)\n"
        "- (preencher após a avaliação da imagem)\n"
        "📊 Pontuação Geral: (calcular média 1–5 após preencher as notas)\n"
        "🔧 Prioridades de Correção:\n"
        "1. (preencher após a avaliação da imagem)\n"
        "2. (preencher após a avaliação da imagem)\n"
        "3. (preencher após a avaliação da imagem)\n"
    )

    before, _, _ = q.partition("Resumo Executivo")
    return before.rstrip() + "\n\n" + template


def _validate_questionnaire_shape(q: str) -> None:
    """
    Validação mínima do shape:
    - Deve conter 'Resumo Executivo'
    - Deve conter headings ### para os critérios (mín. 6)
    - Deve conter campos esperados em algum lugar do texto
    """
    required_markers = [
        "Resumo Executivo",
        "Objetivo Cognitivo",
        "Como Avaliar",
        "Escala Likert",
        "Evidências a coletar",
        "Referências",
    ]
    missing = [m for m in required_markers if m not in q]
    if missing:
        raise ValueError(f"Questionário inválido: faltando seções: {', '.join(missing)}")

    criteria_count = len(re.findall(r"(?m)^###\s+.+$", q))
    if criteria_count < 6:
        raise ValueError(
            f"Questionário inválido: critérios insuficientes via headings ### ({criteria_count})."
        )


# =========================
# Função principal
# =========================
async def create_profile_assets(name: str, description: str, model_override: str | None = None) -> dict:
    """
    Retorna { "guidelines": str, "questionnaire": str } para o perfil informado.
    """
    logger.info("[create_profile_assets] start | name=%s", name)
    if DEBUG:
        print("[DEBUG] Montando prompt…")

    client = get_client()
    model = get_model(model_override)

    user_prompt = PROMPT_JSON_SPEC.format(
        name=name,
        description=description,
        STATIC_RULES=_STATIC_RULES_SYSTEM,
    )

    if DEBUG:
        print("[DEBUG] Modelo:", model)
        print("[DEBUG] Prompt (primeiros 400 chars):\n", _snip(user_prompt))

    try:
        if DEBUG:
            print("[DEBUG] Chamando OpenAI…")
        completion = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especialista em acessibilidade (WCAG/COGA) e geração de questionários.",
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        if DEBUG:
            print("[DEBUG] Resposta recebida da OpenAI")
    except Exception as e:
        logger.exception("[create_profile_assets] erro chamando OpenAI")
        raise RuntimeError(f"Falha na chamada do LLM: {e}")

    raw = (completion.choices[0].message.content or "").strip()
    logger.info("[create_profile_assets] raw length=%d", len(raw))
    if DEBUG:
        print("[DEBUG] Raw (primeiros 400 chars):\n", _snip(raw))

    try:
        data = json.loads(raw)
        guidelines = str(data.get("guidelines", "")).strip()
        questionnaire = str(data.get("questionnaire", "")).strip()

        # ✅ Fallback/defesa: remove "Critério X:" se o modelo insistir
        questionnaire = _strip_criterion_prefixes(questionnaire)

        # ✅ Força o Resumo Executivo a ser template fixo
        questionnaire = _sanitize_questionnaire_template(questionnaire)

        # ✅ Valida shape mínimo (evita questionários “tortos”)
        _validate_questionnaire_shape(questionnaire)

        if not guidelines or not questionnaire:
            msg = "JSON válido porém campos obrigatórios ausentes (guidelines/questionnaire vazios)."
            logger.error("[create_profile_assets] %s | raw_snip=%s", msg, _snip(raw))
            if DEBUG:
                print("[DEBUG][ERRO]", msg)
            raise ValueError(msg)

        logger.info("[create_profile_assets] sucesso")
        return {"guidelines": guidelines, "questionnaire": questionnaire}

    except json.JSONDecodeError as je:
        err_msg = (
            f"JSON inválido: {je.msg} (pos={je.pos}, ln={je.lineno}, col={je.colno}). "
            f"Possível causa: modelo devolveu markdown ao invés de JSON puro. "
            f"raw_snip={_snip(raw)}"
        )
        logger.error("[create_profile_assets] %s", err_msg)
        if DEBUG:
            print("[DEBUG][JSONDecodeError]", err_msg)
        raise ValueError(err_msg)

    except Exception as e:
        err_msg = f"Falha ao processar JSON do LLM: {e}. raw_snip={_snip(raw)}"
        logger.error("[create_profile_assets] %s", err_msg)
        if DEBUG:
            print("[DEBUG][Exception]", err_msg)
        raise ValueError(err_msg)


# =========================
# Failsafe opcional (quando você só tem as notas)
# =========================
def build_summary_from_scores(scores: dict[str, int]) -> str:
    """
    Recebe um dict { 'Critério': nota_int } e devolve um Resumo Executivo (Markdown).
    Formata a média com vírgula e 1 casa decimal. Use quando o modelo retornar só as notas.
    """
    if not scores:
        return (
            "## Resumo Executivo\n"
            "**✅ Pontos Positivos**\n- N/A\n\n"
            "**❌ Principais Problemas**\n- N/A\n\n"
            "**📊 Pontuação Geral:** N/A\n\n"
            "**🔧 Prioridades de Correção**\n- N/A\n"
        )

    total = sum(scores.values())
    media = total / len(scores)
    media_fmt = f"{media:.1f}".replace(".", ",")

    positivos, problemas, prioridades = [], [], []

    low = {k: v for k, v in scores.items() if v <= 3}
    high = {k: v for k, v in scores.items() if v >= 4}

    if any("contraste do texto" in k.lower() for k in high):
        positivos.append("Bom contraste em textos, leitura confortável.")
    if any(("ícones" in k.lower()) or ("elementos gráficos" in k.lower()) for k in high):
        positivos.append("Ícones/elementos gráficos perceptíveis no fundo.")
    if any(("organização" in k.lower()) or ("hierarquia" in k.lower()) for k in high):
        positivos.append("Estrutura visual organizada e hierarquia clara.")
    if any("rótulos" in k.lower() for k in high):
        positivos.append("Rótulos/instruções claros e diretos.")

    if any("cor" in k.lower() for k in low):
        problemas.append("Dependência parcial de cor sem sinais redundantes suficientes.")
        prioridades.append("Adicionar sinais redundantes (ícone/texto/padrão) onde hoje se usa apenas cor.")
    if any("ícones" in k.lower() for k in low):
        problemas.append("Alguns ícones pouco familiares/ambíguos.")
        prioridades.append("Trocar/rotular ícones pouco familiares por pictogramas reconhecíveis.")
    if any("contraste" in k.lower() for k in low):
        problemas.append("Áreas com contraste insuficiente prejudicam a percepção.")
        prioridades.append("Normalizar contraste mínimo em elementos textuais e não textuais.")
    if any(("organização" in k.lower()) or ("hierarquia" in k.lower()) for k in low):
        problemas.append("Hierarquia ou agrupamento visual inconsistentes em alguns pontos.")
        prioridades.append("Rever agrupamentos/títulos para reduzir carga cognitiva.")

    if not positivos:
        positivos.append("Legibilidade e organização gerais adequadas.")
    while len(problemas) < 3:
        problemas.append("Oportunidades de melhoria na consistência visual e clareza de rótulos.")
    while len(prioridades) < 3:
        prioridades.append("Revisar densidade/ruído visual em áreas mais carregadas.")

    md = [
        "## Resumo Executivo",
        "**✅ Pontos Positivos:**",
        *[f"- {p}" for p in positivos[:3]],
        "",
        "**❌ Principais Problemas:**",
        *[f"- {p}" for p in problemas[:3]],
        "",
        f"**📊 Pontuação Geral:** {media_fmt}",
        "",
        "**🔧 Prioridades de Correção:**",
        *[f"- {p}" for p in prioridades[:3]],
        "",
    ]
    return "\n".join(md)
