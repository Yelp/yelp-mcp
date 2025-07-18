# **MCP Server for Yelp Fusion AI**

[Yelp Fusion AI](https://business.yelp.com/data/products/fusion-ai/) brings conversational intelligence to your applications, enabling users to ask natural language questions and receive real-time, contextually relevant answers powered by Yelp’s latest business data and reviews.

### Fusion AI Capabilities

* **Next generation search & discovery** – Search with natural language, discover, and connect with contextually relevant businesses. *("Find the best tacos in the Bay Area")*
* **Multi-turn conversations** – Support back-and-forth interactions and refine queries with follow-up questions. *("Which of the options have open air seating?")*
* **Direct business queries** – Ask targeted questions about businesses without needing to perform a prior search. *("Does Ricky’s Taco allow pets?")*
* **Conversational restaurant reservations** – Explore availability and book a table at restaurants through natural language interactions. (Please note that this is available on **request only**. To enable reservations, please [contact us](https://business.yelp.com/data/products/fusion-ai/?utm_source=GitHub&utm_medium=Readme#form).) *("Reserve a table for 4 tomorrow at 8PM at Ricky’s")*

### Tools:

This server exposes one primary tool:

* **yelp_agent**: Designed for agent-to-agent communication. This tool handles natural language requests about local businesses, providing both natural language responses and structured business data. It supports follow-up questions using a chat\_id. Capabilities include business search, detailed questions, comparisons, itinerary planning, and more, leveraging Yelp's dataset.
  Key Arguments:
  * **natural\_language\_query** (str): Your query (e.g. "find the best tacos in the Bay Area").
  * **search\_latitude** (float or null): Latitude for location-specific searches.
  * **search\_longitude** (float or null): Longitude for location-specific searches.
  * **chat\_id** (str or null): ID for continuing a previous conversation.

## **Prerequisites**

You either need a container manager (like [Docker](https://docker.com) or [Podman](https://podman.io)) or the following installed locally:

* **Python:** Version 3.10 or higher (as specified in pyproject.toml).
* **uv**: The Python package manager. You can find installation instructions at [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/).

You will also need an API key for Yelp Fusion AI. You can get a key by [creating an app here](https://www.yelp.com/developers/v3/manage_app?utm_source=GitHub&utm_medium=Readme), which will start your free trial. If you need more time to evaluate, email us at [fusion@yelp.com](mailto:fusion@yelp.com) to extend your trial.

Find more details and [comprehensive documentation about Yelp Fusion AI here.](https://docs.developer.yelp.com/reference/v2_ai_chat?utm_source=GitHub&utm_medium=Readme)

## **Setup and Installation**

1. Clone the repository:

```
git clone <repository_url>
cd yelp-mcp
```

2. Install dependencies: This command will create a virtual environment (if one doesn't exist), install all necessary dependencies as defined in pyproject.toml and uv.lock, and install the project into the uv environment.

```
make install
```

## **Building the Docker Image (Optional)**

If you prefer to run the server in a container, you can build a Docker image:

```
docker build -t mcp-yelp-agent .
```

This will create an image named mcp-yelp-agent:latest.

## **Running the Server**

This repository is designed to be run as a [Model Context Protocol server](https://modelcontextprotocol.io/docs/concepts/architecture). You will need an MCP client (like compatible versions of Claude, Cursor, or VS Code with MCP support) to interact with it.

### **Method 1: Running without Docker**

Ensure you have completed the "Setup and Installation" steps, especially installing the project so the mcp-yelp-agent script is available.

#### **Server Configuration**

The server supports multiple transport protocols and can be configured with command-line arguments. While `stdio` is the primary transport for most MCP clients, other options are available for different use cases.

*   `--transport`: Choose the communication protocol.
    *   `stdio` (default): Standard input/output, ideal for local tools.
    *   `streamable-http`: Streamable HTTP.
    *   `sse`: Server-Sent Events.
*   `--host`: The host address to bind to (e.g., `127.0.0.1` or `0.0.0.0`). Default is `127.0.0.1`.
*   `--port`: The port to listen on. Default is `8000`.

### **Method 1: Running without Docker**

Configure your MCP client with the following JSON settings to run the server with the default `stdio` transport.

```json
{
  "mcpServers": {
    "yelp_agent": {
      "command": "uv",
      "args": [
        "--directory",
        "<PATH_TO_YOUR_CLONED_PROJECT_DIRECTORY>",
        "run",
        "mcp-yelp-agent"
      ],
      "env": {
        "YELP_API_KEY": "<YOUR_YELP_FUSION_API_KEY>"
      }
    }
  }
}
```

Notes:

*   Replace `<PATH_TO_YOUR_CLONED_PROJECT_DIRECTORY>` with the absolute path to where you cloned this project.
*   Replace `<YOUR_YELP_FUSION_API_KEY>` with your actual Yelp Fusion API key.
*   If your MCP client has trouble invoking uv directly, you might need to provide the full path to the uv binary. You can find this by running `which uv` in your terminal.

### **Method 2: Running with Docker**

Ensure you have built the Docker image as described in "Building the Docker Image".

Configure your MCP client with the following JSON settings:

```json
{
  "mcpServers": {
    "yelp_agent": {
      "command": "docker",
      "args": [
        "run",
        "-i",          // Interactive mode
        "--rm",        // Automatically remove the container when it exits
        "--init",      // Run an init process as PID 1 in the container
        "-e", "YELP_API_KEY=<YOUR_YELP_FUSION_API_KEY>",
        "mcp-yelp-agent:latest" // The image name built earlier
      ]
    }
  }
}
```

Notes:

*   Replace `<YOUR_YELP_FUSION_API_KEY>` with your actual Yelp Fusion API key.
*   If your MCP client has trouble invoking docker from the system PATH, you might need to provide the full path to its binary (e.g., run which docker).
