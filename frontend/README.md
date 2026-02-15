# Streamlit Frontend for Alzheimer's Assistant

A user-friendly chat interface for the Alzheimer's Assistant RAG (Retrieval-Augmented Generation) agent.

## Features

- 🧠 **Production Mode**: Full integration with RAG backend for evidence-based responses
- 👤 **Patient Context**: Optional patient information for personalized responses
- 💬 **Chat History**: Maintains conversation context across queries
- 🔒 **Safety First**: Built-in disclaimers and error handling

## Quick Start (Demo Mode)

The fastest way to run the application without any backend setup:

```bash
# Install Streamlit
pip install streamlit

# Run the app
streamlit run frontend/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`.

**Demo Mode is enabled by default**, showing mock responses to demonstrate the UI functionality.

## Running with Backend Integration

To use the full RAG agent with real knowledge base:

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with:

```env
# Model Configuration
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
LLM_MODEL=gpt-4o-mini
TEMPERATURE=0.7

# FAISS Paths
FAISS_INDEX_PATH=backend/data/alzheimer_faiss_deepl_hybrid.index
FAISS_METADATA_PATH=backend/data/alzheimer_metadata_deepl_hybrid.json
```

### 3. Run Streamlit App

```bash
# From project root
streamlit run frontend/streamlit_app.py
```

## Usage Guide

### Patient Information (Optional)

When you first launch the app, you can:
- **Skip to Chat**: Jump directly to the chat interface without providing patient details
- **Enter Patient Info**: Provide optional context (name, age, weight, height, diagnosis timeframe) for personalized responses

All fields are optional and can be left empty.

### Chat Interface

1. **Ask Questions**: Type queries about Alzheimer's disease, symptoms, treatment, or caregiving strategies
2. **View History**: All messages persist during your session
3. **Clear Chat**: Use the sidebar button to start fresh
4. **Update Patient Info**: Modify patient details at any time via the sidebar

### Sidebar Controls

- **Mode Selection**: Toggle between Demo and Production modes
- **Patient Information**: View entered patient details
- **Session Statistics**: Track number of queries and session start time
- **Actions**:
  - Clear Chat: Reset conversation history
  - Update Patient Info: Modify patient details
  - Logout: Clear patient data and return to welcome screen

## Architecture

```
frontend/
├── streamlit_app.py          # Main Streamlit application
├── requirements_streamlit.txt # Frontend dependencies
└── README.md                  # This file

backend/
├── agent.py                   # RAG agent implementation
├── agent_tools.py             # Search tools
├── rag.py                     # RAG retriever
└── requirements.txt           # Backend dependencies
```

## Sample Queries

Try these example questions:

- "What are the early symptoms of Alzheimer's disease?"
- "What treatment options are available?"
- "How can I help manage behavioral changes?"
- "What dietary recommendations support brain health?"
- "What strategies help with daily caregiving tasks?"

## Troubleshooting

### Backend Connection Failed

If you see "Backend unavailable" in Production Mode:
1. Verify backend dependencies are installed: `pip install -r backend/requirements.txt`
2. Check `.env` file has correct API keys
3. Ensure vector store is initialized: `python backend/ingest.py`
4. Check console for detailed error messages
5. Fall back to Demo Mode for immediate testing

### Import Errors

If you get import errors when trying Production Mode:
1. Ensure you're running from the project root directory
2. Check that `backend/` directory contains all required files
3. Verify Python path is configured correctly

### Port Already in Use

If Streamlit can't start on port 8501:
```bash
streamlit run frontend/streamlit_app.py --server.port 8502
```

## Security & Disclaimers

⚠️ **Important**: This application is for informational purposes only and does not constitute medical advice. Always consult qualified healthcare professionals for medical decisions.

- Patient data is stored only in session state (not persisted)
- No data is transmitted outside the application
- API keys should be kept secure in `.env` file (never commit to git)

## Development

### Code Style

- Follows PEP 8 conventions
- Uses type hints for function parameters and returns
- Includes docstrings for all functions

### Session State Variables

- `chat_history`: List of chat messages
- `patient_data`: Dictionary with patient information
- `is_authenticated`: Boolean for auth status
- `show_patient_form`: Boolean to control view
- `demo_mode`: Boolean for mode selection
- `query_count`: Integer tracking number of queries
- `session_start`: Datetime of session start

## Support

For issues or questions:
1. Check this README for common solutions
2. Review console logs for error details
3. Try Demo Mode to isolate UI vs backend issues
4. Consult the backend documentation for RAG agent details

## License

Part of the OPITHackathon2026 project.
