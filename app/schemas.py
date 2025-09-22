from typing import List, Optional, Literal, Any, Dict
from pydantic import BaseModel, Field

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
    questionnaire: str = Field(..., description="Questionário em Markdown para ser atualizado")
    description_update: str = Field(..., description="Nova descrição/observações para atualizar o questionário")
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
