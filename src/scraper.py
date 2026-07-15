import asyncio
import json
import os
import re
import urllib.request
import nest_asyncio
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer, Html2TextTransformer

nest_asyncio.apply()

ESSENTIAL_URLS = [
    # ---- THE HIGH-LEVEL FOUNDATION LANDING PAGES (Added to fix "What is Snowflake") ----
    "https://docs.snowflake.com/en/user-guide/intro-key-concepts",
    "https://docs.snowflake.com/en/user-guide/intro-supported-features",
    "https://docs.snowflake.com/en/user-guide/intro-editions",
    
    # ---- COMPUTE & STORAGE ----
    "https://docs.snowflake.com/en/user-guide/warehouses-overview",
    "https://docs.snowflake.com/en/user-guide/warehouses-tasks",
    "https://docs.snowflake.com/en/user-guide/warehouses-considerations",
    "https://docs.snowflake.com/en/user-guide/databases",
    "https://docs.snowflake.com/en/user-guide/tables-storage",
    "https://docs.snowflake.com/en/user-guide/views",
    
    # ---- DATA LOADING PIPELINES ----
    "https://docs.snowflake.com/en/user-guide/data-load-overview",
    "https://docs.snowflake.com/en/user-guide/data-load-stages",
    "https://docs.snowflake.com/en/user-guide/data-load-local-file-system",
    "https://docs.snowflake.com/en/user-guide/data-load-copy-into",
    
    # ---- SECURITY & PRIVACY ----
    "https://docs.snowflake.com/en/user-guide/security-access-control-overview",
    "https://docs.snowflake.com/en/user-guide/security-access-control-privileges",
    "https://docs.snowflake.com/en/user-guide/access-history"
]
def get_snowflake_urls() -> list:
    sitemap_url = "https://docs.snowflake.com/sitemap.xml"
    print(f"🔍 Fetching sitemap list: {sitemap_url}...")
    try:
        req = urllib.request.Request(sitemap_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_content = response.read().decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"❌ Error downloading sitemap: {e}")
        
    urls = re.findall(r"<loc>(.*?)</loc>", raw_content)
    return [url.strip() for url in urls if "docs.snowflake.com/en/user-guide/" in url]

async def extract_and_clean_batch(urls_batch: list) -> list:
    loader = AsyncHtmlLoader(urls_batch, header_template={'User-Agent': 'Mozilla/5.0'})
    raw_docs = await loader.aload()
    
    bs_transformer = BeautifulSoupTransformer()
    trimmed_docs = bs_transformer.transform_documents(
        raw_docs, 
        tags_to_extract=["main", "article", "div[role='main']"]
    )
    
    html2text = Html2TextTransformer()
    return html2text.transform_documents(trimmed_docs)

async def run_scraper():
    print("🚦 Starting Scraper...")
    all_scoped_urls = get_snowflake_urls()
    
    filler_urls = [url for url in all_scoped_urls if url not in ESSENTIAL_URLS]
    target_urls = ESSENTIAL_URLS + filler_urls[:35] 
    
    print(f"📋 Target pages to scrape: {len(target_urls)}")
    
    all_extracted_docs = []
    batch_size = 5
    for i in range(0, len(target_urls), batch_size):
        batch = target_urls[i:i + batch_size]
        print(f"📦 Processing Batch {(i // batch_size) + 1}/{(len(target_urls) - 1)//batch_size + 1}...")
        cleaned_batch = await extract_and_clean_batch(batch)
        all_extracted_docs.extend(cleaned_batch)
        await asyncio.sleep(1)

    structured_data = []
    for doc in all_extracted_docs:
        raw_title = doc.metadata.get("title", "Snowflake Document")
        clean_title = raw_title.split("|")[0].split("—")[0].strip()
        clean_content = re.sub(r'\n{3,}', '\n\n', doc.page_content.strip())
        
        structured_data.append({
            "title": clean_title,
            "url": doc.metadata.get("source", ""),
            "markdown_content": clean_content
        })
        
    os.makedirs("data", exist_ok=True)
    with open("data/scraped_docs.json", "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    print("💾 Scraped documents saved successfully to data/scraped_docs.json!")

if __name__ == "__main__":
    asyncio.run(run_scraper())