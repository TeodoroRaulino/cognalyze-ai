# FastAPI Cognalyze Starter

Um microserviço **sem banco de dados** para:
- Classificar/normalizar perfis (nome + descrição);
- Gerar questionário com base no perfil;
- Atualizar um questionário conforme uma nova descrição;
- Analisar mensagens usando prompts por perfil (TEA, TDAH, Dislexia etc.).

## Como rodar

1) Crie e preencha um arquivo `.env` (use `.env.example` como base).
2) Instale dependências:
```bash
pip install -r requirements.txt
```
3) Rode o servidor:
```bash
uvicorn app.main:app --reload
```
4) Acesse a documentação:
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Endpoints

- `POST /profile/suggest-name` — Sugestão/normalização de nome de perfil a partir da descrição.
- `POST /questionnaires/from-profile` — Geração de questionário (Markdown) a partir de nome/descrição de perfil.
- `POST /questionnaires/update` — Atualização de questionário existente conforme nova descrição.
- `POST /analyze` — Análise de mensagem usando os prompts por perfil.

> Observação: O serviço é **stateless** (sem persistência). Qualquer dado de sessão/usuário deve ser trafegado pela API chamadora.
