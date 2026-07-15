import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# Decoupled component imports for production engineering framework
from src.retriever import initialize_advanced_retriever
from src.prompts import SYSTEM_PROMPT

# Load ecosystem secrets before initializing API clients
load_dotenv()

app = FastAPI(
    title="Snowflake Docs Assistant", 
    description="Production-Grade Modular Hybrid RAG search engine tailored for technical documentation extraction.",
    version="3.0.0"
)

# Initialize the 3-Layer compound retrieval engine (BM25 + Pinecone + FlashRank)
advanced_retriever = initialize_advanced_retriever()

# -----------------------------------------------------------------
# 1. GENERATION PIPELINE INITIALIZATION (STRICT GROUNDING LOGIC)
# -----------------------------------------------------------------
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

# temperature=0.0 completely eliminates creative stochastic randomness for precise facts
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
qa_chain = create_stuff_documents_chain(llm, prompt_template)
rag_chain = create_retrieval_chain(advanced_retriever, qa_chain)

# -----------------------------------------------------------------
# 2. DATA MODELS
# -----------------------------------------------------------------
class QueryRequest(BaseModel):
    question: str

# -----------------------------------------------------------------
# 3. FASTAPI ROUTE MANIFEST
# -----------------------------------------------------------------

@app.get("/")
def serve_web_interface():
    """Serves the decoupled static HTML file from the templates directory."""
    template_path = os.path.join(os.getcwd(), "templates", "index.html")
    if not os.path.exists(template_path):
        template_path = os.path.join(os.getcwd(), "src", "templates", "index.html")
        
    return FileResponse(template_path)

@app.get("/health")
def health_check():
    """Liveness probe confirming serving layers are functional."""
    return {"status": "healthy", "engine_version": "3.0.0"}

@app.post("/query")
async def process_user_query(payload: QueryRequest):
    """Processes search intents via RRF hybrid vector pipelines and returns strict answers."""
    response = rag_chain.invoke({"input": payload.question})
    
    # Isolate unique source metadata references from the compression array
    sources = list(set([
        doc.metadata.get("source") 
        for doc in response.get("context", []) 
        if doc.metadata.get("source")
    ]))
    
    return {
        "answer": response["answer"],
        "sources": sources
    }