import os
import json
import sys
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

def run_indexing():
    print("🚦 Starting Indexing Pipeline...")
    file_path = "data/scraped_docs.json"
    
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"❌ Error: Context file '{file_path}' is missing or empty!")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        scraped_data = json.load(f)

    documents = [
        Document(
            page_content=item["markdown_content"],
            metadata={"title": item["title"], "source": item["url"]}
        ) for item in scraped_data
    ]
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("PINECONE_API_KEY"):
         print("❌ Missing API Keys inside .env config!")
         sys.exit(1)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    print(f"🧠 Uploading {len(chunks)} chunks to Pinecone...")
    PineconeVectorStore.from_documents(chunks, embeddings, index_name=index_name)
    print("✅ Vector Indexing Complete!")

if __name__ == "__main__":
    run_indexing()