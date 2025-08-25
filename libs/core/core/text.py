"""Text processing functions."""

from .models import TextDocument


def get_word_count(document: TextDocument) -> int:
    """Get the word count for a text document."""
    if not document.text.strip():
        return 0
    return len(document.text.split())
