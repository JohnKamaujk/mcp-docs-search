import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from bs4 import BeautifulSoup
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
    
async def fetch_url(url: str):
    """
    Given a URL, fetch their text content using BeautifulSoup.
    Returns text_content
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            return text
        except httpx.TimeoutException:
            return "Timeout error"

@mcp.tool()  
async def get_docs(query: str, library: str):
    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, and llama-index.

    Args:
        query: The query to search for (e.g. "Chroma DB")
        library: The library to search in (e.g. "langchain")

    Returns:
        Text from the docs
    """
    if library not in docs_urls:
        raise ValueError(f"Library {library} not supported by this tool")
  
    query = f"site:{docs_urls[library]} {query}"
    results = await search_web(query)
    if len(results["organic"]) == 0:
        return "No results found"
    
    text = ""
    for result in results["organic"]:
        text += await fetch_url(result["link"])
    return text


if __name__ == "__main__":
    mcp.run(transport="stdio")
