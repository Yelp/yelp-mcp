import os
from typing import Any
from typing import Optional
from typing import TypedDict

import httpx

from .loggers import logger


class UserContext(TypedDict):
    latitude: float
    longitude: float


async def make_fusion_ai_request(
    query: str,
    chat_id: Optional[str] = None,
    user_context: Optional[UserContext] = None,
):
    headers = {
        "Authorization": f"Bearer {os.getenv('YELP_API_KEY')}",
        "Content-Type": "application/json",
    }

    data: dict[str, Any] = {
        "query": query,
    }
    if chat_id:
        data["chat_id"] = chat_id
    if user_context:
        data["user_context"] = user_context

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url="https://api.yelp.com/ai/chat/v2",
                json=data,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error making Fusion AI request: {e}")
            return None
