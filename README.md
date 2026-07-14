# 📊 AI CSV Analyst

![AI CSV Analyst Banner](https://img.shields.io/badge/AI-CSV_Analyst-blue?style=for-the-badge&logo=python&logoColor=white)

An intelligent, agentic data analysis tool powered by LLMs. Just upload your CSV, and let the AI figure out how to analyze, chart, and summarize your data!

## 🚀 Features (Planned)

- **Upload & Explore**: Seamlessly load CSV data into Pandas DataFrames.
- **Agentic Routing**: Uses an LLM to decide which tool handles your specific query.
- **Natural Language Analysis**: Ask questions like *"Show me the first 5 rows"* or *"What's the dataset shape?"* and get instant answers.
- **Advanced Visualizations**: Automatically generate beautiful Matplotlib charts (Histograms, Bar, Pie, Scatter).
- **Data Quality Checks**: Automatically find missing values and duplicates.

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **LLM**: Gemini / Ollama
- **Agent Framework**: LangGraph
- **Data Processing**: Pandas
- **Visualizations**: Matplotlib
- **Validation**: Pydantic
- **Environment**: Python 3.11+

## 📂 Project Structure

```text
.
├── app.py                  # Streamlit frontend entry point
├── agent/                  # LangGraph agent definitions
│   ├── graph.py
│   ├── nodes.py
│   └── state.py
├── tools/                  # The tools our agent can use
│   ├── analyzer.py
│   ├── charts.py
│   ├── csv_loader.py
│   └── statistics.py
├── uploads/                # Local directory for uploaded files
└── requirements.txt        # Python dependencies
```

## 🎯 Getting Started

To run this project locally, you need to set up your Google Cloud Platform (GCP) API key.

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure Environment Variables**:
   Create a `.env` file in the root directory of the project and add your GCP API key:
   ```env
   GOOGLE_API_KEY="your-gcp-api-key-here"
   ```
   *(Note: The `.env` file is ignored by Git, so your secret will be kept safe locally.)*
4. **Run the App**: `streamlit run app.py`
