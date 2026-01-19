import json
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional

from app.openai_client import get_client, get_model
from app.prompts import PROMPTS

PROMPT_QUESTION = "avaliacao_questionario"
PROMPT_REPORT = "avaliacao_geral"

async def evaluate_image(questionnaire: str, image_base64: str) -> str:
    """
    Recebe o questionário (markdown) + imagem base64 e pede para o LLM avaliar.
    """
    client = get_client()
    model = get_model()
    prompt = PROMPTS[PROMPT_QUESTION].format(message=questionnaire)

    response = await client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
    )

    return response.output_text


_CRITERION_RE = re.compile(r"^\s*\d+\.\s*(.+?):\s*(\d+)\s*$")
_SECTION_RE = re.compile(r"^(✅|❌|📊|🔧)\s*(.+?):", re.IGNORECASE)


def parse_evaluation_message(message: str) -> Dict[str, Any]:
    """
    Transforma o texto de UMA avaliação em algo estruturado.
    """
    lines = message.splitlines()
    criteria: List[Dict[str, Any]] = []
    positives: List[str] = []
    problems: List[str] = []
    priorities: List[str] = []
    score_overall: Optional[float] = None

    current_section = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        m = _CRITERION_RE.match(line)
        if m:
            name = m.group(1).strip()
            score = int(m.group(2))
            criteria.append({"name": name, "score": score})
            continue

        s = _SECTION_RE.match(line)
        if s:
            title = s.group(2).lower()
            if "pontos positivos" in title:
                current_section = "positives"
            elif "principais problemas" in title:
                current_section = "problems"
            elif "pontuação geral" in title:
                current_section = "score"
            elif "prioridades" in title:
                current_section = "priorities"
            else:
                current_section = None
            continue

        if current_section == "positives" and line.startswith("-"):
            positives.append(line.lstrip("-").strip())
            continue

        if current_section == "problems" and line.startswith("-"):
            problems.append(line.lstrip("-").strip())
            continue

        if current_section == "priorities" and (
            (line[0].isdigit() and "." in line[:3]) or line.startswith("-")
        ):
            priorities.append(line.lstrip("0123456789.- ").strip())
            continue

        if current_section == "score":
            num_match = re.search(r"(\d+(?:[.,]\d+)?)", line)
            if num_match:
                num_txt = num_match.group(1).replace(",", ".")
                try:
                    score_overall = float(num_txt)
                except ValueError:
                    pass
            continue

    return {
        "criteria": criteria,
        "positives": positives,
        "problems": problems,
        "priorities": priorities,
        "score_overall": score_overall,
        "raw": message,
    }


def aggregate_evaluations(messages: List[str]) -> Dict[str, Any]:
    parsed = [parse_evaluation_message(m) for m in messages]

    criteria_scores: Dict[str, List[int]] = defaultdict(list)
    for p in parsed:
        for c in p["criteria"]:
            criteria_scores[c["name"]].append(c["score"])

    criteria_avg: Dict[str, float] = {}
    for name, scores in criteria_scores.items():
        criteria_avg[name] = sum(scores) / len(scores)

    overall_scores = [p["score_overall"] for p in parsed if p["score_overall"] is not None]
    overall_avg = sum(overall_scores) / len(overall_scores) if overall_scores else None

    problem_count: Dict[str, int] = defaultdict(int)
    positive_count: Dict[str, int] = defaultdict(int)

    for p in parsed:
        for prob in p["problems"]:
            problem_count[prob] += 1
        for pos in p["positives"]:
            positive_count[pos] += 1

    common_problems = sorted(problem_count.items(), key=lambda x: x[1], reverse=True)
    common_positives = sorted(positive_count.items(), key=lambda x: x[1], reverse=True)

    lines = []
    lines.append("### Diagnóstico Consolidado das Imagens")
    if overall_avg is not None:
        lines.append(f"- **Pontuação geral média (todas):** {overall_avg:.1f}")
    lines.append("- **Critérios com pior média:**")
    for name, avg in sorted(criteria_avg.items(), key=lambda x: x[1])[:3]:
        lines.append(f"  - {name}: {avg:.1f}")
    lines.append("- **Problemas mais recorrentes:**")
    if common_problems:
        for prob, count in common_problems[:5]:
            lines.append(f"  - ({count}x) {prob}")
    else:
        lines.append("  - Nenhum problema recorrente.")
    lines.append("- **Pontos positivos mais recorrentes:**")
    if common_positives:
        for pos, count in common_positives[:5]:
            lines.append(f"  - ({count}x) {pos}")
    else:
        lines.append("  - Nenhum ponto positivo recorrente.")

    return {
        "criteria_avg": criteria_avg,
        "overall_avg": overall_avg,
        "common_problems": common_problems,
        "common_positives": common_positives,
        "diagnosis_markdown": "\n".join(lines),
        "raw_parsed": parsed,
    }


async def generate_executive_report(results: List[str]) -> str:
    """
    Recebe várias respostas de avaliação (strings) e gera um relatório bonito.
    """
    client = get_client()
    model = get_model()

    agg = aggregate_evaluations(results)

    base_prompt = PROMPTS[PROMPT_REPORT]

    structured_summary = {
        "overall_avg": agg["overall_avg"],
        "criteria_avg": agg["criteria_avg"],
        "top_problems": agg["common_problems"][:5],
        "top_positives": agg["common_positives"][:5],
    }

    response = await client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": base_prompt,
            },
            {
                "role": "user",
                "content": (
                    "Use o diagnóstico consolidado a seguir como verdade e apenas reescreva de forma coesa, curta e priorizada.\n\n"
                    f"{agg['diagnosis_markdown']}\n\n"
                    f"Dados estruturados (JSON): {json.dumps(structured_summary, ensure_ascii=False)}\n\n"
                    "Produza: (1) resumo executivo curto; (2) 3–5 problemas mais comuns; (3) 3 recomendações práticas."
                ),
            },
        ],
    )

    return response.output_text