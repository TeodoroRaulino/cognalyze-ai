from fastapi import FastAPI, HTTPException
from app.schemas import (
    ProfileSuggestRequest, ProfileSuggestResponse,
    GenerateQuestionnaireRequest, UpdateQuestionnaireRequest,
    AnalyzeRequest, LLMResponse,
    CreateProfileRequest, CreateProfileResponse,
    EvaluationRequest, EvaluationResponse,
)
from app.usecase.profile_usecase import suggest_profile_name
from app.usecase.questionnaire_usecase import generate_from_profile, update_questionnaire
from app.usecase.analyze_usecase import analyze
from app.usecase.profile_create_usecase import create_profile_assets
from app.usecase.evaluation_usecase import evaluate_image

app = FastAPI(title="Cognalyze Simple LLM API", version="0.2.0")


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/profiles/create", response_model=CreateProfileResponse)
async def post_create_profile(body: CreateProfileRequest):
    try:
        result = await create_profile_assets(
            name=body.name,
            description=body.description,
            model_override=body.model
        )
        return CreateProfileResponse(**result)

    except ValueError as ve:
        # Erro conhecido (JSON inválido/campos ausentes) → 502 com detalhe útil
        raise HTTPException(status_code=502, detail=str(ve))

    except Exception as e:
        # Erro inesperado
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.post("/profile/suggest-name", response_model=ProfileSuggestResponse)
async def post_suggest_profile_name(body: ProfileSuggestRequest):
    try:
        name = await suggest_profile_name(
            description=body.description,
            existing_profiles=body.existing_profiles,
            proposed_name=body.name
        )
        return ProfileSuggestResponse(name=name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/questionnaires/from-profile", response_model=LLMResponse)
async def post_generate_questionnaire(body: GenerateQuestionnaireRequest):
    try:
        content, used_prompt = await generate_from_profile(
            profile_name=body.profile_name,
            profile_description=body.profile_description,
            model_override=body.model
        )
        return LLMResponse(content=content, used_prompt=used_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/questionnaires/update", response_model=LLMResponse)
async def post_update_questionnaire(body: UpdateQuestionnaireRequest):
    try:
        content, used_prompt = await update_questionnaire(
            questionnaire_md=body.questionnaire,
            description_update=body.description_update,
            model_override=body.model
        )
        return LLMResponse(content=content, used_prompt=used_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=LLMResponse)
async def post_analyze_message(body: AnalyzeRequest):
    try:
        content, used_prompt = await analyze(
            profile_key=body.profile_key,
            message=body.message,
            model_override=body.model
        )
        return LLMResponse(content=content, used_prompt=used_prompt)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluation", response_model=EvaluationResponse)
async def post_questionnaire_with_image(body: EvaluationRequest):
    try:
        response_message = await evaluate_image(body.questionnaire, body.imageBase64)

        return EvaluationResponse(
            message=response_message,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")