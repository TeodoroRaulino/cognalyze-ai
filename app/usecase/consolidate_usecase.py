from __future__ import annotations

import math
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.schemas import AlertItem, CommonItem, CriterionStats, OverallStats


# -----------------------------
# Regex (tolerante ao seu payload)
# -----------------------------
def clean_criterion_label(label: str) -> str:
    """
    Remove ruídos comuns do label:
    - markdown headings ###, ##, #
    - numeração '1.' '1)' etc
    - bullets
    - espaços duplicados
    """
    s = label.strip()

    # remove heading markdown: ### Título
    s = re.sub(r"^\s*#{1,6}\s*", "", s)

    # remove prefixos numerados: "1." "1)" "1-" etc
    s = re.sub(r"^\s*\d+\s*[\.\)\-]\s*", "", s)

    # remove bullets
    s = re.sub(r"^\s*[-•*]\s*", "", s)

    # normaliza espaços
    s = re.sub(r"\s+", " ", s).strip()
    return s


SCORE_LINE_RE = re.compile(
    r"^\s*(?:\d+\.)?\s*(?P<label>[^:]+?)\s*:\s*(?P<score>\d+(?:[.,]\d+)?)\s*$",
    re.IGNORECASE,
)

# Headers de seção (aceita variações)
SECTION_RE = re.compile(
    r"^\s*(Resumo Executivo|✅\s*Pontos Positivos:?|❌\s*Principais Problemas:?|🔧\s*Prioridades de Correção:?|📊\s*Pontuação Geral:?)\s*$",
    re.IGNORECASE,
)

# Itens de lista: "- x" / "• x" / "* x" / "1. x"
LIST_ITEM_RE = re.compile(r"^\s*(?:[-•*]|\d+\.)\s+(?P<item>.+?)\s*$")


# -----------------------------
# Helpers numéricos
# -----------------------------
def normalize_score(value: str) -> float:
    return float(value.strip().replace(",", "."))

def mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else float("nan")

def stdev(values: List[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    m = mean(values)
    var = sum((x - m) ** 2 for x in values) / (n - 1)
    return math.sqrt(var)

def fmt_pt(value: Optional[float], decimals: int = 1) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:.{decimals}f}".replace(".", ",")


# -----------------------------
# Parsing
# -----------------------------
def is_overall_label(label: str) -> bool:
    l = label.lower()
    return "pontuação geral" in l or "pontuacao geral" in l

def parse_scores_from_message(message: str) -> Tuple[Dict[str, float], Optional[float]]:
    """
    Extrai linhas no formato "Label: score".
    - Retorna (criteria_scores, overall_score_if_present)
    - Suporta "1. Contraste: 5" e "Pontuação Geral: 4,3"
    """
    scores: Dict[str, float] = {}
    overall: Optional[float] = None

    for raw_line in message.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = SCORE_LINE_RE.match(line)
        if not m:
            continue
        
        label = clean_criterion_label(m.group("label"))
        score = normalize_score(m.group("score"))

        if is_overall_label(label):
            overall = score
        else:
            scores[label] = score

    return scores, overall


def parse_qualitative_sections(message: str) -> Dict[str, List[str]]:
    """
    Extrai itens das seções:
    - Pontos Positivos
    - Principais Problemas
    - Prioridades de Correção
    Aceita listas com '-' ou '1.' dentro das seções.
    """
    out = {"positives": [], "problems": [], "priorities": []}
    current: Optional[str] = None

    def set_section(header: str) -> Optional[str]:
        h = header.lower()
        if "pontos positivos" in h:
            return "positives"
        if "principais problemas" in h:
            return "problems"
        if "prioridades" in h:
            return "priorities"
        return None

    for raw_line in message.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if SECTION_RE.match(line):
            current = set_section(line)
            continue

        if current:
            lm = LIST_ITEM_RE.match(line)
            if lm:
                out[current].append(lm.group("item").strip())
            else:
                # se apareceu um novo score line/section header, encerra
                if SCORE_LINE_RE.match(line) or SECTION_RE.match(line):
                    current = None

    return out


def normalize_item_key(text: str) -> str:
    """
    Normalização simples para agrupar itens parecidos.
    (Sem fuzzy por dependência; se quiser, dá pra plugar rapidfuzz.)
    """
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[^\w\sáàâãéèêíìîóòôõúùûç]", "", t)
    return t


# -----------------------------
# Reporting model interno
# -----------------------------
@dataclass
class ConsolidatedReport:
    criteria: List[str]
    per_criterion_scores: Dict[str, List[float]]
    per_criterion_stats: Dict[str, Dict[str, float]]
    overall_score: float
    overall_score_from_messages: Optional[float] = None
    positives: List[str] = field(default_factory=list)
    problems: List[str] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)


def consolidate(messages: Iterable[str]) -> ConsolidatedReport:
    msgs = list(messages)  # ✅ garante reuso + total conhecido

    score_maps: List[Dict[str, float]] = []
    overall_list: List[float] = []

    for m in msgs:
        sm, overall = parse_scores_from_message(m)
        score_maps.append(sm)
        if overall is not None:
            overall_list.append(overall)

    all_criteria = sorted({k for sm in score_maps for k in sm.keys()})

    per_criterion_scores: Dict[str, List[float]] = {c: [] for c in all_criteria}
    for sm in score_maps:
        for c in all_criteria:
            if c in sm:
                per_criterion_scores[c].append(sm[c])

    per_criterion_stats: Dict[str, Dict[str, float]] = {}
    for c, vals in per_criterion_scores.items():
        if not vals:
            per_criterion_stats[c] = {"mean": float("nan"), "min": float("nan"), "max": float("nan"), "stdev": float("nan"), "n": 0}
        else:
            per_criterion_stats[c] = {"mean": mean(vals), "min": min(vals), "max": max(vals), "stdev": stdev(vals), "n": len(vals)}

    # ✅ overall determinístico: média das médias por critério (igual seu result.py)
    criterion_means = [v["mean"] for v in per_criterion_stats.values() if not math.isnan(v["mean"])]
    overall = mean(criterion_means) if criterion_means else float("nan")

    # se vier "Pontuação Geral" dentro das mensagens, também calculamos uma média separada (opcional)
    overall_from_msgs = mean(overall_list) if overall_list else None

    # Qualitativo: agrega e remove duplicatas simples
    pos, prob, pri = [], [], []
    seen_pos, seen_prob, seen_pri = set(), set(), set()

    for m in messages:
        q = parse_qualitative_sections(m)
        for item in q["positives"]:
            key = normalize_item_key(item)
            if key not in seen_pos:
                seen_pos.add(key)
                pos.append(item)
        for item in q["problems"]:
            key = normalize_item_key(item)
            if key not in seen_prob:
                seen_prob.add(key)
                prob.append(item)
        for item in q["priorities"]:
            key = normalize_item_key(item)
            if key not in seen_pri:
                seen_pri.add(key)
                pri.append(item)

    report = ConsolidatedReport(
      criteria=all_criteria,
      per_criterion_scores=per_criterion_scores,
      per_criterion_stats=per_criterion_stats,
      overall_score=overall,
      overall_score_from_messages=overall_from_msgs,
      positives=pos,
      problems=prob,
      priorities=pri,
    )
    report.total_messages = len(msgs)
    return report



def render_markdown(report: ConsolidatedReport, title: str = "Relatório Consolidado de Avaliação") -> str:
    lines: List[str] = []
    lines.append(f"# {title}\n")

    # Cabeçalho com contexto
    total_msgs = getattr(report, "n_messages", None)  # se não existir, tudo bem
    # (como você já tem len(messages) em aggregate_evaluations, vamos passar isso abaixo)

    lines.append("## 📊 Resultados Quantitativos\n")
    lines.append(
        "> **n (amostra)** = quantidade de avaliações que continham este critério após o parse.\n"
        "> Se algum critério não aparecer em todas as avaliações, o **n** dele será menor.\n"
    )

    lines.append("| Critério Avaliado | n (amostra) | Cobertura | Média | Mín | Máx | Desvio Padrão |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for c in report.criteria:
        st = report.per_criterion_stats[c]
        n = int(st["n"])
        total = report.total_messages if hasattr(report, "total_messages") else None
        coverage = f"{n}/{total}" if total else str(n)

        lines.append(
            f"| {c} | {n} | {coverage} | {fmt_pt(st['mean'])} | {fmt_pt(st['min'])} | {fmt_pt(st['max'])} | {fmt_pt(st['stdev'])} |"
        )

    lines.append("\n## ⭐ Pontuação Global\n")
    lines.append(f"- **Global (média das médias por critério):** {fmt_pt(report.overall_score)} / 5,0")
    if report.overall_score_from_messages is not None:
        lines.append(f"- **Global (média das 'Pontuações Gerais' reportadas):** {fmt_pt(report.overall_score_from_messages)} / 5,0")

    # Alertas: critérios com maior divergência
    divergences = sorted(
        [(c, report.per_criterion_stats[c]["stdev"]) for c in report.criteria if not math.isnan(report.per_criterion_stats[c]["stdev"])],
        key=lambda x: x[1],
        reverse=True,
    )
    top_div = [(c, s) for c, s in divergences if s >= 0.8][:3]  # threshold ajustável
    if top_div:
        lines.append("\n## ⚠️ Alertas (alta divergência entre avaliações)\n")
        for c, s in top_div:
            lines.append(f"- **{c}** — desvio padrão: {fmt_pt(s)}")

    if report.positives:
        lines.append("\n## ✅ Pontos Positivos (agregados)\n")
        for item in report.positives[:10]:
            lines.append(f"- {item}")

    if report.problems:
        lines.append("\n## ❌ Principais Problemas (agregados)\n")
        for item in report.problems[:10]:
            lines.append(f"- {item}")

    if report.priorities:
        lines.append("\n## 🔧 Prioridades de Correção (agregadas)\n")
        for i, item in enumerate(report.priorities[:10], start=1):
            clean = re.sub(r"^\s*\d+\.\s*", "", item).strip()
            lines.append(f"{i}. {clean}")

    return "\n".join(lines)

def aggregate_evaluations(messages: List[str]) -> Dict[str, Any]:
    report = consolidate(messages)

    # Contagem “recorrente” (agora por normalização)
    problem_count: Dict[str, Tuple[str, int]] = {}   # key -> (best_text, count)
    positive_count: Dict[str, Tuple[str, int]] = {}

    for m in messages:
        q = parse_qualitative_sections(m)

        for item in q["problems"]:
            k = normalize_item_key(item)
            if k not in problem_count:
                problem_count[k] = (item, 0)
            problem_count[k] = (problem_count[k][0], problem_count[k][1] + 1)

        for item in q["positives"]:
            k = normalize_item_key(item)
            if k not in positive_count:
                positive_count[k] = (item, 0)
            positive_count[k] = (positive_count[k][0], positive_count[k][1] + 1)

    common_problems = sorted(problem_count.values(), key=lambda x: x[1], reverse=True)
    common_positives = sorted(positive_count.values(), key=lambda x: x[1], reverse=True)

    # Alertas por divergência
    alerts: List[AlertItem] = []
    for c in report.criteria:
        sd = report.per_criterion_stats[c]["stdev"]
        if not math.isnan(sd) and sd >= 0.8:
            alerts.append(AlertItem(criterion=c, stdev=sd))
    alerts = sorted(alerts, key=lambda x: x.stdev, reverse=True)[:5]

    # criteria list
    criteria_out: List[CriterionStats] = []
    for c in report.criteria:
        st = report.per_criterion_stats[c]
        vals = report.per_criterion_scores[c]
        criteria_out.append(
            CriterionStats(
                name=c,
                n=int(st["n"]),
                mean=None if math.isnan(st["mean"]) else float(st["mean"]),
                min=None if math.isnan(st["min"]) else float(st["min"]),
                max=None if math.isnan(st["max"]) else float(st["max"]),
                stdev=None if math.isnan(st["stdev"]) else float(st["stdev"]),
                scores=[float(v) for v in vals],
            )
        )

    diagnosis_md = render_markdown(report)

    return {
        "overall": OverallStats(
            mean_by_criteria=None if math.isnan(report.overall_score) else float(report.overall_score),
            mean_reported_overall=report.overall_score_from_messages,
            n_messages=len(messages),
        ),
        "criteria": criteria_out,
        "common_problems": [CommonItem(text=t, count=c) for (t, c) in common_problems[:10]],
        "common_positives": [CommonItem(text=t, count=c) for (t, c) in common_positives[:10]],
        "alerts": alerts,
        "diagnosis_markdown": diagnosis_md,
    }