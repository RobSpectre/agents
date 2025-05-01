import os

from typing import Iterator

from agno.agent import Agent, RunResponse
from agno.knowledge.csv import CSVKnowledgeBase
from agno.vectordb.pgvector import PgVector
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.models.openrouter import OpenRouter
from agno.tools.mcp import MCPTools
from agno.playground import Playground, serve_playground_app


db_url = f"postgresql+psycopg://ai:{os.environ.get('AI_POSTGRES_PASSWORD')}@localhost:5432/ai"

knowledge_base = CSVKnowledgeBase(
    path="marvel_characters.csv",
    vector_db=PgVector(
        table_name="marvel_characters",
        db_url=db_url
    ),
)

storage = PostgresAgentStorage(table_name="marvel_characters_agent", db_url=db_url)

mcp_tools = MCPTools(urls=['http://0.0.0.0:8000/mcp'])

marvel_agent = Agent(
    model=OpenRouter(id="google/gemini-2.5-flash-preview"),
    knowledge=knowledge_base,
    storage=storage,
    read_chat_history=True,
    show_tool_calls=True,
    description="""You are a helpful assistant with knowledge of every
    character from the Marvel comic universe. Use your authorization tools to
    ensure that users can only see data to which they are allowed. 
    """
)

app = Playground(agents=[marvel_agent]).get_app()

if __name__ == "__main__":
    knowledge_base.load(upsert=True)
    
    serve_playground_app("marvel_agent:app", reload=True)
