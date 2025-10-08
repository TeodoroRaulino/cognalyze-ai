from typing import List, Optional, Literal, Any, Dict
from pydantic import BaseModel, Field, validator

class ExistingProfile(BaseModel):
    name: str = Field(..., description="Nome do perfil existente")
    description: Optional[str] = Field(None, description="Descrição do perfil existente (se houver)")

class ProfileSuggestRequest(BaseModel):
    description: str = Field(..., description="Descrição do usuário para classificar/sugerir perfil")
    existing_profiles: List[ExistingProfile] = Field(default_factory=list, description="Lista de perfis já existentes (opcional)")
    name: Optional[str] = Field(None, description="Nome proposto pelo cliente (opcional)")

class ProfileSuggestResponse(BaseModel):
    name: str = Field(..., description="Nome do perfil escolhido/sugerido")

class GenerateQuestionnaireRequest(BaseModel):
    profile_name: str = Field(..., description="Nome do perfil")
    profile_description: str = Field(..., description="Descrição do perfil")
    model: Optional[str] = Field(None, description="Modelo OpenAI opcional para override")

class UpdateQuestionnaireRequest(BaseModel):
    profile_description: str = Field(..., description="Descrição do perfil de acessibilidade")
    actual_questionnaire_md: str = Field(..., description="Questionário atual em Markdown")
    new_questionnaire_md: str = Field(..., description="Novo questionário em Markdown")
    model: Optional[str] = Field(None, description="Modelo OpenAI opcional para override")

class AnalyzeRequest(BaseModel):
    profile_key: Literal["tea","tdah","dislexia","acessibilidade_cognitiva","outro"]
    message: str
    model: Optional[str] = None

class LLMResponse(BaseModel):
    content: str
    used_prompt: str

class CreateProfileRequest(BaseModel):
    name: str = Field(..., description="Nome do perfil")
    description: str = Field(..., description="Descrição resumida do perfil")
    model: Optional[str] = Field(None, description="Modelo OpenAI (override opcional)")

class CreateProfileResponse(BaseModel):
    guidelines: str = Field(..., description="Diretrizes recomendadas (Markdown)")
    questionnaire: str = Field(..., description="Questionário (Markdown)")

class EvaluationRequest(BaseModel):
    questionnaire: str = Field(..., description="Questionnaire in Markdown format")
    imageBase64: str = Field(..., description="Image encoded in base64")

class EvaluationResponse(BaseModel):
    message: str

class ResultInput(BaseModel):
    message: str


class ExecutiveReportRequest(BaseModel):
    results: List[str] = Field(..., description="Lista de 1 a 10 resultados")

    @validator("results")
    def check_results_length(cls, v):
        if not (1 <= len(v) <= 10):
            raise ValueError("É necessário enviar entre 1 e 10 resultados.")
        return v


class ExecutiveReportResponse(BaseModel):
    report: str