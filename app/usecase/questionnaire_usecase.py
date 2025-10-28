from app.openai_client import get_client, get_model

WCAG_INDEX = [
    {"id": "1.4.3", "title": "Contrast (Minimum)", "url": "https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum"},
    {"id": "1.4.11", "title": "Non-text Contrast", "url": "https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast"},
    {"id": "1.4.1", "title": "Use of Color", "url": "https://www.w3.org/WAI/WCAG22/Understanding/use-of-color"},
    {"id": "1.3.1", "title": "Info and Relationships", "url": "https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships"},
    {"id": "3.3.2", "title": "Labels or Instructions", "url": "https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions"},
]

COGA_INDEX = [
    {"id": "plain-language", "title": "Use plain, clear language", "url": "https://www.w3.org/TR/coga-usable/#plain-language"},
    {"id": "redundant-cues", "title": "Provide cues beyond color", "url": "https://www.w3.org/TR/coga-usable/#redundant-cues"},
    {"id": "familiar-icons", "title": "Use familiar icons", "url": "https://www.w3.org/TR/coga-usable/#familiar-icons"},
    {"id": "chunking", "title": "Chunk content and provide headings", "url": "https://www.w3.org/TR/coga-usable/#help-users-understand"},
]

_LIKERT_ANCHORS = (
    "Âncoras da Escala Likert (use exatamente estas definições por critério):\n"
    "- **1 (Crítico/Não Atende)**: Falhas graves que impedem a compreensão; viola a(s) referência(s) WCAG indicada(s) e contraria o COGA.\n"
    "- **3 (Parcialmente Atende)**: Há progresso visível, mas persistem obstáculos cognitivos relevantes; atende parcialmente a WCAG indicada; COGA aplicado de forma inconsistente.\n"
    "- **5 (Atende Bem/Ótimo)**: Critério cumprido com clareza; boas práticas do COGA evidentes; WCAG indicada atendida sem ressalvas.\n"
)

_WCAG_COGA_HELP = (
    "Mapeamentos úteis (exemplos para **imagens estáticas** — escolha os aplicáveis):\n"
    "- **Contraste de texto** → WCAG 1.4.3; COGA: \"Use contraste suficiente\".\n"
    "- **Contraste de ícones/controles** → WCAG 1.4.11; COGA: \"Controles fáceis de perceber\".\n"
    "- **Não depender apenas de cor** → WCAG 1.4.1; COGA: \"Sinais redundantes, não só cor\".\n"
    "- **Rótulos e instruções claros** → WCAG 3.3.2; COGA: \"Texto simples e direto\".\n"
    "- **Hierarquia e relações visuais** → WCAG 1.3.1; COGA: \"Quebre em blocos e títulos claros\".\n"
    "- **Ícones compreensíveis** → WCAG 3.2.4/1.3.3; COGA: \"Pictogramas familiares\".\n"
    "- **Legibilidade tipográfica** → WCAG 1.4.3/1.4.4* (em imagem estática, foque na legibilidade); COGA: \"Tipografia legível\".\n"
    "Observação: cite **apenas** referências pertinentes; não invente numerações.\n"
)

_CITATION_RULES = (
    "REGRAS DE CITAÇÃO (OBRIGATÓRIAS):\n"
    "- Para **cada critério**, selecione **no máximo 2** itens de **WCAG (CATÁLOGO)** e **1** de **COGA (CATÁLOGO)**.\n"
    "- **Proibido** citar referência fora do catálogo abaixo (não inventar).\n"
    "- Se nada do catálogo se aplicar, escreva: **WCAG: N/A; COGA: N/A**.\n"
)

def _render_reference_catalog() -> str:
    wcag_lines = "\n".join(f"  - {i['id']} — {i['title']} — {i['url']}" for i in WCAG_INDEX)
    coga_lines = "\n".join(f"  - {i['id']} — {i['title']} — {i['url']}" for i in COGA_INDEX)
    return (
        "CATÁLOGO DE REFERÊNCIAS (uso obrigatório):\n"
        "- **WCAG**:\n" + wcag_lines + "\n"
        "- **COGA**:\n" + coga_lines + "\n"
    )

# Regras duras com anti-deriva e foco em imagem estática
_STATIC_RULES_SYSTEM = (
    "Você é um assistente especialista em acessibilidade cognitiva para **imagens estáticas**.\n"
    "REGRAS DURAS:\n"
    "1) A entrada SEMPRE é **uma imagem estática**. Não há vídeo, animação, transições, parallax, GIF ou movimento.\n"
    "2) **Não crie critérios** sobre animação, movimento, microinterações, hover, foco, autoplay, tempo, loop ou áudio.\n"
    "3) Se o usuário mencionar reunião/processos/áudio/vídeo/motion, **reformule** o conceito para um **equivalente visual verificável** na imagem (p.ex., previsibilidade → hierarquia/títulos; ritmo → densidade/clutter; agenda → instruções/legendas visíveis). Se não houver equivalente, marque como **N/A**.\n"
    "4) Saída **exclusivamente em Markdown**, em **português**, **sem cercas de código**.\n"
    "5) **Cada critério** DEVE conter:\n"
    "   - Nome do critério e objetivo cognitivo.\n"
    "   - **Como avaliar (na imagem)**: passos observáveis e verificáveis.\n"
    "   - **Escala Likert 1–5** com âncoras 1/3/5 **específicas deste critério**.\n"
    "   - **Evidências a coletar** (bullets concisas do que observar/capturar).\n"
    "   - **Referências** (somente do CATÁLOGO): até 2 WCAG + 1 COGA, ou **N/A**.\n"
    "6) Inclua **Resumo Executivo**: Pontos Positivos; Principais Problemas; **Pontuação Geral (média 1–5)**; Prioridades de Correção (ordem sugerida).\n"
    "7) **Não liste referências irrelevantes** ao que é visível.\n"
    "\n"
    + _LIKERT_ANCHORS + "\n" + _WCAG_COGA_HELP + "\n" + _CITATION_RULES + "\n" + _render_reference_catalog()
)

# =========================
# Prompt builders
# =========================
def _build_generation_prompt(profile_name: str, profile_description: str) -> str:
    return f"""
Você é um especialista em acessibilidade cognitiva.

Perfil alvo:
- **Nome:** {profile_name}
- **Descrição:** \"\"\"{profile_description}\"\"\"

Tarefa:
Gere um **questionário de avaliação de acessibilidade cognitiva** em **Markdown**, para uso por um LLM ao **analisar imagens estáticas**. Produza **entre 6 e 10 critérios**.

Formato por critério (obrigatório):
- **Nome do critério**
- **Objetivo cognitivo**
- **Como avaliar (na imagem)** — passos de inspeção visual, objetivos e verificáveis
- **Escala Likert 1–5 (âncoras 1/3/5 específicas do critério)**
- **Evidências a coletar**
- **Referências** — escolha **somente do CATÁLOGO** (no máx. 2 WCAG + 1 COGA) ou **N/A**

Depois da lista de critérios, inclua **Resumo Executivo**:
- Pontos Positivos
- Principais Problemas
- **Pontuação Geral (média 1–5)**
- Prioridades de Correção (ordem sugerida)

{_STATIC_RULES_SYSTEM}

Entrada do usuário (imagem/descrição contextual): {{message}}
""".strip()

def _build_update_prompt(questionnaire_md: str, description_update: str) -> str:
    return f"""
Você é um especialista em acessibilidade cognitiva.

Questionário atual (Markdown):
{questionnaire_md}

Nova descrição/observação a considerar:
\"\"\"{description_update}\"\"\"

Atualize o questionário **mantendo formato e seções** e reforçando:
- **Imagem estática somente**; reformule itens de processo para equivalentes visuais verificáveis ou marque N/A.
- **Âncoras Likert 1/3/5 específicas por critério**.
- **Referências** apenas do **CATÁLOGO** (≤2 WCAG + 1 COGA); se não aplicável → **WCAG: N/A; COGA: N/A**.
- **Resumo Executivo** com média 1–5 atualizada.

{_STATIC_RULES_SYSTEM}

Entrada do usuário (imagem/descrição contextual): {{message}}
""".strip()

# =========================
# API público (assinaturas inalteradas)
# =========================
async def generate_from_profile(profile_name: str, profile_description: str, model_override: str | None):
    client = get_client()
    model = get_model(model_override)

    prompt = _build_generation_prompt(profile_name, profile_description)

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em acessibilidade cognitiva e deve seguir estritamente o formato solicitado."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        top_p=0.9,
        max_tokens=1800,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    content = (completion.choices[0].message.content or "").strip()
    # Nota: se quiser, aqui dá para adicionar sanitização leve (ex.: remover cercas ``` se vierem).
    return content, prompt

async def update_questionnaire(questionnaire_md: str, description_update: str, model_override: str | None):
    client = get_client()
    model = get_model(model_override)

    prompt = _build_update_prompt(questionnaire_md, description_update)

    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente especialista em acessibilidade cognitiva e deve seguir estritamente o formato solicitado."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        top_p=0.9,
        max_tokens=1800,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    content = (completion.choices[0].message.content or "").strip()
    return content, prompt
