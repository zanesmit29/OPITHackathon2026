# Alzheimer's Assistant - OPITHackathon2026

A comprehensive RAG-powered (Retrieval-Augmented Generation) chatbot and caregiving companion for Alzheimer's disease caregivers. This application provides evidence-based information, daily activity tracking, and reporting features to support family caregivers.

## 🌟 Features

### 💬 AI-Powered Chat Assistant
- **RAG Technology**: Retrieves information from a curated knowledge base using FAISS vector search
- **Conversation Memory**: Maintains context across multi-turn conversations
- **Safety-First Approach**: 
  - Built-in crisis detection (suicide, violence, emergency situations)
  - Dangerous topic filtering (medication advice, diagnoses)
  - Automatic logging of safety events
- **Patient Context**: Personalized responses based on patient information (age, weight, diagnosis timeframe)
- **Citation Support**: All responses include sources with URLs

### 📝 Daily Activity Logging
- Track daily observations including:
  - Nutrition (meals eaten, water intake)
  - Behavioral observations
  - Mood and cognitive status
  - Sleep patterns
  - Activities completed
- SQLite database for persistent storage

### 📊 Reports & Analytics
- Visualize trends over time
- Filter data by date range
- Export data to Excel for healthcare providers

### 🔒 Security & Privacy
- Patient data stored locally in session state (not persisted beyond session)
- No external data transmission except to configured AI APIs
- Comprehensive safety disclaimers

## 🏗️ Architecture

```
OPITHackathon2026/
├── backend/                      # AI Agent & RAG System
│   ├── agent.py                  # ConversationAgent with tool integration
│   ├── agent_tools.py            # Search tools for RAG
│   ├── rag.py                    # FAISS retriever with hybrid search
│   ├── prompts.py                # System prompts and safety rules
│   ├── ingest.py                 # Vector store ingestion
│   ├── data/                     # FAISS index and metadata
│   │   ├── alzheimer_faiss_deepl_hybrid.index
│   │   └── alzheimer_metadata_deepl_hybrid.json
│   └── requirements.txt
│
├── frontend/                     # Streamlit Web Application
│   ├── Home.py                   # Main chat interface
│   ├── pages/
│   │   ├── Daily_Log.py          # Daily activity tracking
│   │   └── Report.py             # Analytics and data export
│   ├── utils/
│   │   ├── database.py           # SQLite database operations
│   │   └── generate_sample_data.py
│   ├── README.md                 # Frontend-specific documentation
│   └── requirements_streamlit.txt
│
├── data/                         # Application data
│   └── daily_logs.db             # SQLite database for logs
│
├── strategy/                     # Business documentation
│   ├── ads.md
│   └── revenue_model.md
│
├── pitch/                        # Pitch materials
│   └── pitch_deck.pdf
│
├── .env.example                  # Environment configuration template
├── requirements.txt              # Backend dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- HuggingFace API token (for AI models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/zanesmit29/OPITHackathon2026.git
   cd OPITHackathon2026
   ```

2. **Install dependencies**
   ```bash
   # Backend dependencies
   pip install -r requirements.txt
   
   # Frontend dependencies
   pip install -r frontend/requirements_streamlit.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   # Model Configuration
   HF_TOKEN=your_huggingface_token_here
   LLM_MODEL=gpt-4o-mini
   TEMPERATURE=0.7
   
   # FAISS Paths
   FAISS_INDEX_PATH=backend/data/alzheimer_faiss_deepl_hybrid.index
   FAISS_METADATA_PATH=backend/data/alzheimer_metadata_deepl_hybrid.json
   ```

4. **Run the application**
   ```bash
   streamlit run frontend/Home.py
   ```
   
   The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Chat Assistant

1. **Enter Patient Information** (Optional)
   - Provide patient details for personalized responses
   - All fields are optional
   - Data is only stored in session state

2. **Ask Questions**
   - "What are early symptoms of Alzheimer's?"
   - "How can I manage behavioral changes?"
   - "What dietary recommendations support brain health?"
   - "How do I create a safe home environment?"

3. **View Sources**
   - All responses include citations
   - Click source URLs to verify information

### Daily Activity Log

1. Navigate to the "Daily Activity Log" page
2. Fill in observations for the day
3. Submit to save to local database
4. View previous entries

### Reports

1. Navigate to the "Reports & Analytics" page
2. Select date range
3. View visualizations of trends
4. Export data to Excel for sharing with healthcare providers

## 🛠️ Technology Stack

### AI & Machine Learning
- **LangChain**: RAG pipeline orchestration
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Text embeddings (`all-MiniLM-L6-v2`)
- **HuggingFace Inference API**: LLM integration

### Web Framework
- **Streamlit**: Interactive web interface
- **Plotly**: Data visualizations

### Data Processing
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **SQLite**: Local database storage

### Document Processing
- **pypdf**: PDF parsing
- **python-docx**: Word document processing
- **BeautifulSoup4**: HTML parsing

## ⚠️ Important Disclaimers

**This application is for informational purposes only and does not constitute medical advice.**

- Always consult qualified healthcare professionals for medical decisions
- Do not use this tool for emergency situations
- Crisis keywords trigger immediate referral to emergency services
- The system logs safety events for review

## 🔧 Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest test_safety.py
python -m pytest test_setup.py
```

### Environment Modes

The application supports two modes:

1. **Demo Mode**: Mock responses without backend (for UI testing)
2. **Production Mode**: Full RAG integration with knowledge base

Toggle between modes in the sidebar.

## 📝 Configuration

### Model Configuration
- Default LLM: `gpt-4o-mini`
- Default embedding model: `all-MiniLM-L6-v2`
- Adjustable temperature (0.0 - 1.0)

### Vector Store
- FAISS index for fast similarity search
- Hybrid search combining semantic and keyword matching
- Configurable chunk size and overlap

### Safety System
Two-layer safety detection:
1. **Keyword matching**: Fast detection of obvious crisis/dangerous terms
2. **LLM evaluation**: Catches subtle cases missed by keywords

## 🤝 Contributing

This project was created for the OPIT Hackathon 2026. Contributions, issues, and feature requests are welcome.

## 📄 License

This project is part of the OPITHackathon2026.

## 👥 Team

Created by the OPITHackathon2026 team for supporting Alzheimer's disease caregivers.
@danielinkudos - https://www.linkedin.com/in/daniel-p%C3%A9rez-vidal-energ%C3%ADa/
@stefanostelluti - https://www.linkedin.com/in/stefanostelluti/


## 📚 Additional Resources

- [Frontend Documentation](frontend/README.md) - Detailed Streamlit app documentation
- [Pitch Deck](pitch/pitch_deck.pdf) - Project presentation
- [Revenue Model](strategy/revenue_model.md) - Business strategy

## 🆘 Troubleshooting

### Backend Connection Failed
1. Verify all dependencies are installed: `pip install -r requirements.txt`
2. Check `.env` file has correct API tokens
3. Ensure FAISS index files exist in `backend/data/`
4. Check console for detailed error messages

### Import Errors
1. Run from project root directory
2. Ensure all `__init__.py` files are present
3. Verify Python version (3.8+)

### Port Already in Use
```bash
streamlit run frontend/Home.py --server.port 8502
```

### Vector Store Issues
If FAISS index is missing or corrupted:
1. Check that files exist: `backend/data/alzheimer_faiss_deepl_hybrid.index`
2. Verify metadata file: `backend/data/alzheimer_metadata_deepl_hybrid.json`
3. Re-run ingestion if needed: `python backend/ingest.py`

## 🔗 Links

- Repository: https://github.com/zanesmit29/OPITHackathon2026
- Streamlit: https://opithackathon2026-nm9ah9mhgvncnfgretpxao.streamlit.app/
