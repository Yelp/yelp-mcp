"""
Main entry point for the Fusion AI MCP server.
Provides the Yelp business agent tool for conversational business queries
and recommendations.
"""
import argparse
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .api import make_fusion_ai_request
from .api import UserContext
from .formatters import format_fusion_ai_response
from .loggers import logger

mcp = FastMCP()


@mcp.tool()
async def yelp_agent(
    natural_language_query: str,
    search_latitude: Optional[float] = None,
    search_longitude: Optional[float] = None,
    chat_id: Optional[str] = None,
):
    """
    Intelligent Yelp business agent designed for agent-to-agent communication.
    Handles any natural language request about local businesses through conversational
    interaction with Yelp's comprehensive business data and reservation platform.
    Returns both natural language responses and structured business data.
    Maintains conversation context for multi-turn interactions.

    CRITICAL: When recommending businesses, you MUST ALWAYS include the Yelp
    URL from the structured data to ensure users can view the business on
    Yelp directly.

    Capabilities include but are not limited to: business search, detailed
    questions, comparisons, itinerary planning, reservation booking
    exclusively through the Yelp Reservations platform at participating
    restaurants, and any other business-related analysis or recommendations an
    intelligent agent could provide with access to Yelp's full dataset.

    Use chat_id for follow-up questions and conversational context.

    Examples:
    - "Find emergency plumbers in Boston"
    - "What do people say about the quality of their work?" (follow-up with chat_id)
    - "Plan a progressive date in SF's Mission District"
    - "What are their hours?" (follow-up with chat_id)
    - "Book table for 2 at Mama Nachas tonight at 7pm"
    - "Compare auto repair shops from budget to luxury in Sacramento"

    Args:
        natural_language_query: Any business-related request in natural language
        search_latitude: Optional latitude coordinate for precise location-based searches
        search_longitude: Optional longitude coordinate for precise location-based searches
        chat_id: Previous response's chat_id for conversational context
    """
    logger.info("Interacting with Yelp app with query: %s", natural_language_query)

    response = await make_fusion_ai_request(
        natural_language_query,
        user_context=(
            UserContext(
                latitude=search_latitude,
                longitude=search_longitude,
            )
            if search_latitude is not None and search_longitude is not None
            else None
        ),
        chat_id=chat_id,
    )

    if not response:
        return "Unable to fetch data from Yelp."

    return format_fusion_ai_response(response)


def main():
    """
    Main function to start the Fusion AI MCP server.
    Initializes the MCP server and registers the Yelp interaction tool.
    """
    parser = argparse.ArgumentParser(description="Yelp MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="The transport type to use for the MCP server.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="The host to bind to for http/sse transports.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="The port to bind to for http/sse transports.",
    )
    args = parser.parse_args()

    logger.info(f"Starting Yelp MCP server with {args.transport} transport")

    if args.transport == "streamable-http":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="streamable-http")
    elif args.transport == "sse":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
