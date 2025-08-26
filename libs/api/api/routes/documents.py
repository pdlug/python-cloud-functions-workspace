from core.models import TextDocument
from core.text import get_word_count
from fastapi import APIRouter
from pydantic import BaseModel, Field

router: APIRouter = APIRouter()


class WordCountRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to count words in")


class WordCountResponse(BaseModel):
    word_count: int = Field(..., description="Number of words in the text")


@router.post("/documents/word_count", response_model=WordCountResponse)
async def count_words(request: WordCountRequest) -> WordCountResponse:
    """Count words in the provided text."""
    document = TextDocument(text=request.text)
    word_count = get_word_count(document)

    return WordCountResponse(word_count=word_count)
