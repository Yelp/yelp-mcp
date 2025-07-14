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
    yelp_api_key = os.getenv("YELP_API_KEY")

    if not yelp_api_key:
        logger.warning(
            "YELP_API_KEY is missing from the environment. Unable to make authorized requests."
        )
        return None

    headers = {
        "Authorization": f"Bearer {yelp_api_key}",
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
        except httpx.RequestError as e:
            logger.error(f"Request error while making Fusion AI request: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error while making Fusion AI request: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while making Fusion AI request: {e}")
