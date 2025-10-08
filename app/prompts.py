PROMPTS = {
    "tea": """
    Você é um especialista em acessibilidade cognitiva e sua função é analisar a imagem fornecida com **foco exclusivo em acessibilidade para pessoas com Transtorno do Espectro Autista (TEA)**, seguindo as diretrizes **WCAG (Web Content Accessibility Guidelines)**, **COGA (Cognitive Accessibility User Research)** e **GAIA (Global Accessibility Guidelines for Autism)**.

    Seu objetivo é realizar uma **avaliação detalhada** e identificar pontos de conformidade e não conformidade, fornecendo recomendações específicas. **A resposta deve incluir uma pontuação quantitativa (Escala Likert de 1 a 5) para cada critério**, além de um resumo executivo final.

    ### **Critérios de Avaliação**  
    Para cada item abaixo, forneça uma **nota de 1 a 5** e uma explicação objetiva:

    1️⃣ **Previsibilidade e Clareza (GAIA)**  
    - O design segue um padrão visual consistente, evitando mudanças bruscas que possam causar ansiedade?  

    2️⃣ **Complexidade Visual e Sobrecarga Cognitiva**  
    - O layout evita excesso de informações e elementos visuais que possam dificultar a compreensão?  

    3️⃣ **Cores e Contraste (WCAG 1.4.3)**  
    - O contraste entre cores é adequado para pessoas com hipersensibilidade visual?  

    4️⃣ **Texto e Legibilidade (WCAG 1.4.12)**  
    - O texto utiliza fontes acessíveis e espaçamento adequado para leitura?  

    5️⃣ **Ícones e Simbologia**  
    - Os ícones são compreensíveis e seguem padrões universais como ARASAAC?  

    6️⃣ **Elementos Interativos (se houver)**  
    - Se houver botões ou interações, eles são intuitivos e previsíveis?  

    ### **Resumo Executivo**  
    ✅ **Pontos Positivos:** [Critérios atendidos]  
    ❌ **Principais Problemas:** [Critérios com nota abaixo de 3]  
    📊 **Pontuação Geral de Acessibilidade (média das notas Likert):** [Indique a porcentagem]  
    🔧 **Prioridade de Correção:** [Itens mais críticos]  

    **Se a imagem estiver em conformidade, explique quais critérios foram atendidos. Se houver falhas, especifique quais diretrizes WCAG, COGA ou GAIA não foram seguidas e forneça recomendações claras.**

    Entrada do usuário: {message}
    """,

    "tdah": """
    Você é um especialista em acessibilidade cognitiva e sua função é analisar a imagem fornecida com **foco exclusivo em acessibilidade para pessoas com Transtorno do Déficit de Atenção e Hiperatividade (TDAH)**, seguindo as diretrizes **WCAG, COGA e GAIA**.

    Seu objetivo é realizar uma **avaliação detalhada**, identificando pontos positivos e falhas, e fornecendo recomendações claras. **A resposta deve incluir notas de 1 a 5 na Escala Likert para cada critério**, além de um resumo executivo.

    ### **Critérios de Avaliação**  

    1️⃣ **Organização e Estrutura Visual (COGA, WCAG 2.4.6)**  
    - O layout é bem estruturado e facilita a compreensão das informações?  

    2️⃣ **Elementos Distrativos e Sobrecarga Sensorial (WCAG 2.3.1)**  
    - Há animações excessivas, pop-ups inesperados ou elementos que dificultam o foco?  

    3️⃣ **Tempo de Interação e Feedback (WCAG 2.2.1)**  
    - O usuário tem tempo suficiente para processar informações antes de mudanças automáticas?  

    4️⃣ **Foco e Navegação Facilitada (WCAG 2.4.3)**  
    - A navegação é intuitiva e não exige esforço excessivo?  

    5️⃣ **Uso de Cores e Contraste (WCAG 1.4.3)**  
    - A paleta de cores ajuda na distinção das informações sem causar sobrecarga visual?  

    ### **Resumo Executivo**  
    ✅ **Pontos Positivos:** [Critérios atendidos]  
    ❌ **Principais Problemas:** [Critérios com nota abaixo de 3]  
    📊 **Pontuação Geral de Acessibilidade:** [Indique a porcentagem]  
    🔧 **Correções Prioritárias:** [Itens mais críticos]  

    **Se a imagem estiver em conformidade, justifique quais critérios foram atendidos. Se houver falhas, especifique quais diretrizes WCAG, COGA ou GAIA não foram seguidas e sugira melhorias.**

    Entrada do usuário: {message}
    """,

    "dislexia": """
    Você é um especialista em acessibilidade cognitiva e sua função é analisar a imagem fornecida com **foco exclusivo em acessibilidade para pessoas com Dislexia**, seguindo as diretrizes **WCAG, COGA e GAIA**.

    Seu objetivo é realizar uma **avaliação detalhada**, identificando pontos fortes e falhas, e fornecendo recomendações. **A resposta deve incluir notas na Escala Likert (1 a 5) para cada critério**, além de um resumo executivo.

    ### **Critérios de Avaliação**  

    1️⃣ **Clareza e Legibilidade do Texto (WCAG 1.4.12, COGA)**  
    - O texto utiliza fontes adequadas (ex: Arial, Verdana, OpenDyslexic) e espaçamento correto?  

    2️⃣ **Uso de Contraste e Cores (WCAG 1.4.3, 1.4.6)**  
    - O contraste entre texto e fundo segue as diretrizes WCAG AA (mínimo 4.5:1)?  

    3️⃣ **Redução de Sobrecarga Visual**  
    - O layout evita grandes blocos de texto e usa espaçamentos adequados?  

    4️⃣ **Suporte a Tecnologias Assistivas (WCAG 1.3.1, COGA)**  
    - O conteúdo permite personalização de fonte, espaçamento e cores?  

    5️⃣ **Evitação de Ambiguidade e Confusão (COGA, WCAG 3.1.5)**  
    - O texto usa linguagem clara e objetiva, sem frases complexas?  

    ### **Resumo Executivo**  
    ✅ **Pontos Positivos:** [Critérios atendidos]  
    ❌ **Principais Problemas:** [Critérios com nota abaixo de 3]  
    📊 **Pontuação Geral de Acessibilidade:** [Indique a porcentagem]  
    🔧 **Correções Prioritárias:** [Itens mais críticos]  

    **Se a imagem estiver em conformidade, justifique os critérios atendidos. Se houver falhas, especifique as diretrizes WCAG, COGA ou GAIA não seguidas e sugira soluções.**

    Entrada do usuário: {message}
    """,

    "acessibilidade_cognitiva": """
    Você é um especialista em acessibilidade cognitiva. Avalie a seguinte interação com base nas diretrizes WCAG e COGA.

    Entrada do usuário: {message}
    """,

    "outro": """
    Não foi possível identificar um perfil específico. Avalie a interação com base em acessibilidade cognitiva geral.

    Entrada do usuário: {message}
    """,

    "avaliacao_questionario": """
    Faça a avaliação do questionario a seguir para a imagem e retorne somente respostas da avaliação em português, evite cálculos na resposta retornando só o resultado númerico: {message}
    """,

    "atualizacao_questionario": """
        Você é um especialista em acessibilidade cognitiva.

        dado as diretrizes de acessibilidade do perfil cognitivo:
        {profile_description}

        Questionário atual (Markdown):
        {actual_questionnaire_md}

        dada a estrutura original (critérios com Likert 1–5 + Resumo Executivo), avalie se os questionarios novos seguém o padrão de questionário e as diretrizes do perfil e dê uma resposta conscisa(sim ou não), em caso de não mostre qual parte está errada e de forma conscisa diga o porque
    """,

    "atualizacao_questionario_v2": """
        Você é um especialista em acessibilidade cognitiva.

        OBJETIVO
        Verificar se o NOVO questionário segue:
        1) a ESTRUTURA do questionário original (blocos de critérios com escala Likert 1–5) e
        2) as DIRETRIZES do perfil cognitivo abaixo,
        E então responder de forma CONCISA: “SIM” ou “NÃO — <motivos curtos>”.

        DIRETRIZES DO PERFIL (texto livre):
        {profile_description}

        QUESTIONÁRIO ORIGINAL (Markdown):
        {actual_questionnaire_md}

        ESCOPO DA AVALIAÇÃO (o que verificar):
        - Estrutura:
        - Cada critério em bloco identificável (título/heading).
        - Escala Likert explícita 1–5 no bloco (números na ordem crescente).
        - Presença de uma seção “Resumo Executivo” ao final (ou equivalente com este nome).
        - Títulos/labels consistentes entre critérios (não precisa ser idêntico ao original, apenas coerente).
        - Diretrizes do perfil cognitivo:
        - Linguagem clara e direta; evitar jargões sem explicação.
        - Frases objetivas; instruções compreensíveis.
        - Termos e exemplos adequados ao perfil descrito.

        NÃO-OBJETIVOS (NÃO avaliar, NÃO comentar):
        - NÃO conte, compare nem comente a QUANTIDADE de critérios/perguntas.
        - NÃO penalize REPETIÇÕES de critérios/perguntas; ignore redundâncias.
        - NÃO comente sobre ordem, layout visual ou microformatação se a semântica estiver correta.
        - NÃO reescreva o questionário; apenas valide conformidade.

        REGRAS DE DECISÃO
        - Responda “SIM” se (i) todos os blocos de critério tiverem escala 1–5 válida e (ii) houver “Resumo Executivo” e (iii) o texto não contrariar as diretrizes do perfil.
        - Caso contrário, responda “NÃO — <até 3 motivos objetivos>”.
        - Motivos devem referenciar a parte afetada de forma curta (ex.: “Critério ‘Tempo e Ritmo’: sem escala 1–5”; “Falta ‘Resumo Executivo’”; “Jargão sem explicação em ‘Consistência’”).

        FORMATO DE SAÍDA (obrigatório, em uma única linha):
        - Se conforme:  SIM
        - Se não conforme:  NÃO — motivo1; motivo2; motivo3

        OBSERVAÇÕES
        - Seja objetivo. Nada além do formato acima.
        - Ignore variações cosméticas que não afetem a estrutura 1–5 e o “Resumo Executivo”.
    """,

    "atualizacao_questionario_v3": """
        Você é um especialista em acessibilidade cognitiva.

        OBJETIVO
        Verificar se o NOVO questionário segue:
        1) o PADRÃO do questionário original (critérios em blocos com escala Likert 1–5 + “Resumo Executivo”), e
        2) as DIRETRIZES do perfil cognitivo,
        e então responder de forma CONCISA: “SIM” ou “NÃO — <motivos curtos>”.

        DIRETRIZES DO PERFIL (texto livre):
        {profile_description}

        QUESTIONÁRIO ORIGINAL (Markdown):
        {actual_questionnaire_md}

        DEFINIÇÕES RÁPIDAS
        - “Critério”: um bloco identificável com título/heading e instrução de resposta em escala 1–5.

        ESCOPO DA AVALIAÇÃO (o que verificar):
        - Padrão/estrutura:
        - Cada critério em bloco identificável (título claro).
        - Escala Likert explícita 1–5 (números em ordem crescente; âncoras opcionais).
        - Presença de uma seção “Resumo Executivo” ao final (com esse nome).
        - Consistência de títulos/labels entre critérios (não precisa ser idêntico ao original, apenas coerente).
        - Aderência às diretrizes:
        - Linguagem clara, direta e adequada ao perfil descrito.
        - Instruções compreensíveis e não ambíguas.
        - Cada critério deve estar relacionado (implícita ou explicitamente) a pelo menos uma diretriz do perfil.

        CARDINALIDADE FLEXÍVEL (muito importante)
        - Mínimo de 1 critério válido.
        - Não é necessário corresponder 1:1 ao número de pontos das diretrizes.
        - É permitido ter menos ou mais critérios do que o original.
        - Redundâncias são permitidas se alinhadas às diretrizes.

        NÃO-OBJETIVOS (NÃO avaliar, NÃO comentar)
        - NÃO conte, compare nem mencione a QUANTIDADE de critérios/perguntas.
        - NÃO penalize REPETIÇÕES; ignore redundâncias mesmo que pareçam similares.
        - NÃO comente ordem, layout visual ou microformatação quando a semântica estiver correta.
        - NÃO reescreva o questionário; apenas valide conformidade.

        REGRAS DE DECISÃO
        Responda “SIM” se TODAS as condições forem verdadeiras:
        (i) existe ≥ 1 critério válido no padrão descrito,
        (ii) todos os critérios presentes exibem escala 1–5 válida,
        (iii) há “Resumo Executivo”,
        (iv) nenhum critério contradiz as diretrizes do perfil e a linguagem é adequada.

        Caso contrário, responda “NÃO — <até 3 motivos objetivos>”.
        - Motivos devem ser curtos e apontar a parte afetada, p.ex.:
        - “Falta ‘Resumo Executivo’”
        - “Critério ‘Tempo e Ritmo’: sem escala 1–5”
        - “Jargão sem explicação em ‘Consistência’”
        - “Critério ‘X’ não se relaciona às diretrizes”

        FORMATO DE SAÍDA (obrigatório, uma única linha):
        - Conforme:  SIM
        - Não conforme:  NÃO — motivo1; motivo2; motivo3

        OBSERVAÇÕES
        - Seja objetivo. Não inclua recomendações de reescrita, nem comentários sobre quantidade de itens ou repetição.
    """,

    "avaliacao_geral": """
    Você receberá até 10 resultados de avaliações (texto livre em JSON ou texto).  
    Sua tarefa é **consolidar todos em um único Relatório Executivo** em **Markdown**, seguindo o modelo abaixo.

    ⚠️ Regras obrigatórias:
    - A saída deve conter **apenas o relatório**, nada antes ou depois.
    - Não inclua introduções, explicações de processo ou perguntas finais.
    - Use somente os títulos e seções definidas.
    - Escreva de forma executiva, clara e objetiva.
    - Consolide os resultados (não copie cada um na íntegra).
    - Se houver contradições entre os resultados, cite-as na seção de problemas.

    ### Estrutura obrigatória em Markdown:

    # Relatório Executivo Consolidado

    ## 📊 Visão Geral
    - Número de resultados analisados: X
    - Média geral da pontuação: Y (de 1 a 5)

    ## ✅ Principais Pontos Positivos (recorrentes)
    - Item 1
    - Item 2
    - Item 3

    ## ❌ Principais Problemas Identificados
    - Item 1
    - Item 2
    - Item 3

    ## 🔧 Recomendações Prioritárias
    - Item 1
    - Item 2
    - Item 3

    ## 📈 Conclusão Executiva
    Parágrafo único com 5–7 linhas, destacando os pontos de atenção críticos e o direcionamento estratégico para correção/melhoria.

    """
}