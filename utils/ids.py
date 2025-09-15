from __future__ import annotations

import uuid


# PUBLIC_INTERFACE
def generate_model_id() -> str:
    """Generate a new model identifier.

    Returns:
        str: A unique model id such as 'model-<uuid4>'.
    """
    return f"model-{uuid.uuid4().hex[:12]}"
