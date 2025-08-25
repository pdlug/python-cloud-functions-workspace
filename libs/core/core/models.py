"""Shared data models for business logic."""

from pydantic import BaseModel, Field


class TextDocument(BaseModel):
    """A text document for processing."""

    text: str = Field(..., description="The text content")
