#This function is to search Pubmed Central
# Rare Disease Literature Miner with Enhanced Features

# streamlit_app.py
# Rare Disease Literature Miner - Streamlit UI Version

import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import re
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("PUBMED_API_KEY")

# Constants
ENTREZ_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ENTREZ_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Utility functions
def search_pubmed(query: str, api_key: str, max_results: int = 10) -> List[str]:
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'retmode': 'json',
        'api_key': api_key
    }
    response = requests.get(ENTREZ_SEARCH_URL, params=params)
    response.raise_for_status()
    return response.json().get('esearchresult', {}).get('idlist', [])

def fetch_article_details_efetch(ids: List[str], api_key: str) -> List[Dict]:
    if not ids:
        return []

    id_string = ",".join(ids)
    params = {
        'db': 'pubmed',
        'id': id_string,
        'retmode': 'xml',
        'api_key': api_key
    }

    response = requests.get(ENTREZ_FETCH_URL, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        article_data = {}
        article_data['pmid'] = article.findtext(".//PMID")
        article_data['title'] = article.findtext(".//ArticleTitle")
        abstract_parts = [abst.text.strip() for abst in article.findall(".//AbstractText") if abst.text]
        article_data['abstract'] = " ".join(abstract_parts)
        article_data['journal'] = article.findtext(".//Journal/Title")
        article_data['pubdate'] = article.findtext(".//PubDate/Year") or "N/A"
        articles.append(article_data)

    return articles

# Streamlit UI
st.set_page_config(page_title="Rare Disease Literature Miner", layout="wide")
st.title("🔬 Rare Disease Literature Miner")
st.markdown("""Search PubMed for rare disease-related articles and view abstracts, journals, and publication years. 🧠""")

query = st.text_input("Enter a rare disease or biomedical keyword", "Fragile X Syndrome")
num_results = st.slider("Number of results to fetch", 1, 50, 10)

if st.button("Search"):
    with st.spinner("🔍 Searching PubMed..."):
        pmc_ids = search_pubmed(query, API_KEY, max_results=num_results)
        articles = fetch_article_details_efetch(pmc_ids, API_KEY)

    if articles:
        df = pd.DataFrame(articles)

        # Keyword highlighting
        def highlight(text):
            return re.sub(f"(?i)({query})", r"**\1**", text or "", flags=re.IGNORECASE)
        df['abstract'] = df['abstract'].apply(highlight)

        st.success(f"✅ Found {len(df)} articles.")
        st.dataframe(df[['title', 'journal', 'pubdate', 'abstract']])

        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "literature_results.csv", "text/csv")

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Articles by Year")
            st.bar_chart(df['pubdate'].value_counts().sort_index())
        with col2:
            st.subheader("📚 Top Journals")
            st.bar_chart(df['journal'].value_counts().head(10))

        # Citations
        st.subheader("🔗 Links")
        for i, row in df.iterrows():
            pmid = row['pmid']
            st.markdown(f"[{row['title']}]({'https://pubmed.ncbi.nlm.nih.gov/' + pmid})")
    else:
        st.warning("⚠️ No articles found for this query.")