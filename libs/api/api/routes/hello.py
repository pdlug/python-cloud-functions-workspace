from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router: APIRouter = APIRouter()


class HelloRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name to greet")


class HelloResponse(BaseModel):
    hello: str = Field(..., description="Greeting response")


class HelloGetResponse(BaseModel):
    text: str = Field(..., description="Hello world message")


@router.get("/hello", response_model=HelloGetResponse)
async def get_hello() -> HelloGetResponse:
    """Return a simple hello world message."""
    return HelloGetResponse(text="Hello World!")


@router.post("/hello", response_model=HelloResponse)
async def post_hello(request: HelloRequest) -> HelloResponse:
    """Return a greeting with the provided name."""
    if not request.name.strip():
        raise HTTPException(
            status_code=400, detail="Name cannot be empty or whitespace"
        )
    return HelloResponse(hello=request.name)
