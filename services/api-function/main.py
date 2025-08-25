import json
from typing import Any

import functions_framework
from fastapi.testclient import TestClient

from api.main import app

# Create TestClient once at module level for better performance
client = TestClient(app)


@functions_framework.http
def api_function(request: Any) -> tuple[bytes, int, dict[str, str]]:
    """HTTP Cloud Function entry point using optimized TestClient."""
    try:
        response = client.request(
            method=request.method,
            # Remove trailing ? if no query params
            url=request.full_path.rstrip("?"),
            headers=dict(request.headers),
            content=request.get_data() if hasattr(request, "get_data") else None,
        )

        # Return in Cloud Functions format
        return response.content, response.status_code, dict(response.headers)

    except Exception:
        # Return a proper HTTP error response
        error_body = json.dumps({"detail": "Internal server error"}).encode()
        return error_body, 500, {"content-type": "application/json"}
