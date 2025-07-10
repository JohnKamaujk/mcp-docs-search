import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

mcp = FastMCP("docs")

USER_AGENT = "docs-app/1.0"
SERPER_URL="https://google.serper.dev/search"

docs_urls = {
    "langchain": "python.langchain.com/docs",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
}

async def search_web(query: str) -> dict:
    """
    Searches the web using Serper API. On failure or timeout, returns an empty result.
    """
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }
    payload = {
        "q": query,
        "gl": "us",
        "hl": "en",
        "num":2,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(SERPER_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
    except (httpx.TimeoutException, httpx.RequestError) as e:
        print(f"⚠️ SERPER API request failed: {e}")
        return {"organic": []}

def main():
    print("Hello from mcp-docs-search!")


if __name__ == "__main__":
    main()
