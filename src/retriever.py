import os
import json
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.document_compressors import FlashrankRerank

def initialize_advanced_retriever() -> ContextualCompressionRetriever:
    json_path = "data/scraped_docs.json"
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Missing base data layer context file: {json_path}")
        
    with open(json_path, "r", encoding="utf-8") as f:
        scraped_data = json.load(f)
        
    documents = [
        Document(
            page_content=item["markdown_content"],
            metadata={"title": item["title"], "source": item["url"]}
        ) for item in scraped_data
    ]
    
    # Layer A: Sparse Term Matcher (Exact Keywords)
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = 10 
    
    # Layer B: Dense Vector Matcher (Semantic Meanings)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = PineconeVectorStore(index_name=os.getenv("PINECONE_INDEX_NAME"), embedding=embeddings)
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 10})
    
    # Layer C: Hybrid Fusion Layer (Reciprocal Rank Fusion - RRF)
    hybrid_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever], 
        weights=[0.5, 0.5]
    )
    
    # Layer D: Cross-Encoder Document Recalibration Model (FlashRank)
    compressor = FlashrankRerank(top_n=5)
    
    return ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=hybrid_retriever
    )