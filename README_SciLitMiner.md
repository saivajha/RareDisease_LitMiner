# 🔬 Scientific Literature Miner

Explore the biomedical frontier with **Scientific Literature Miner** — a Streamlit-based web app that allows scientists, researchers, and students to search, visualize, and export PubMed literature using keyword-based queries.

> “Shoot for the stars. Even if you miss, you'll land among the moon.”  
> — Inspired by John F. Kennedy

---

## 🌍 Project Overview

This app leverages the **PubMed API** to fetch and display scientific articles relevant to biomedical and life sciences research. Originally built to explore rare diseases, this version is now optimized to handle broader **scientific literature mining** needs, including:

- 🧬 Genetic Disorders  
- 🧠 Neuroscience  
- 💊 Pharmacology  
- 🧪 Biomedical Innovation  

---

## 🧠 Features

- 🔎 **Real-time Search** on PubMed using any keyword
- 📄 **Abstracts, Titles, Journals, and Publication Dates** listed
- 🟨 **Keyword Highlighting** for easy reading
- 📊 **Data Visualizations**:
  - Articles per year
  - Top publishing journals
- 📥 **Download Results** as CSV
- 🔗 **Direct links** to each article on PubMed

---

## 🚀 How to Use

1. Open the app: [https://sci-lit-miner.streamlit.app](https://sci-lit-miner.streamlit.app)
2. Enter a biomedical keyword (e.g., *Fragile X Syndrome*)
3. Click **Search**
4. View, explore, and download the literature results instantly!

---

## 🛠 Tech Stack

- **Frontend/UI**: Streamlit  
- **Backend/Data Fetch**: NCBI Entrez Utilities (E-Utils)  
- **Visualization**: Streamlit Charts, Pandas  
- **Environment**: Python 3.12+, dotenv  

---

## 📦 Installation (Optional: Local Run)

```bash
# Clone the repo
git clone https://github.com/saivajha/RareDisease_LitMiner.git
cd RareDisease_LitMiner

# Create a .env file with your PubMed API Key
echo "PUBMED_API_KEY=your_key_here" > .env

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📄 Example Query

```txt
Keyword: "Cerebrotendinous Xanthomatosis"
Results: 10 articles
Charts: Distribution by publication year and journal
Export: Available as CSV
```

---

## 👤 Author

Created by **Sai Vajha** ([@saivajha](https://github.com/saivajha))  
📫 Email: saisvajha@gmail.com  
🌐 Project by: [qbitsai.com](https://qbitsai.com)

---

## ✅ License

MIT License – Use, learn, contribute, and improve freely!