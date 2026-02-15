"""
Streamlit Application for Alzheimer's Assistant - Production Version

RAG-powered chat application for Alzheimer's caregiving information.
Fully integrated with ConversationAgent backend with conversation memory.

Setup:
    1. Install requirements: pip install -r requirements.txt
    2. Configure .env with API keys (HF_TOKEN)
    3. Run: streamlit run frontend/streamlit_app.py

Features:
- Conversation memory (multi-turn context)
- Safety checks (crisis/dangerous topic detection)
- RAG-powered knowledge retrieval
- Patient context personalization
"""

import sys
import os
import time
import logging
from typing import Dict, Optional, List
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="Alzheimer's Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .demo-banner {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-bottom: 1rem;
        border: 2px solid #ffc107;
    }
    .patient-info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .disclaimer {
        background-color: #f8d7da;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {
            'name': '',
            'gender': '',
            'age_years': None,
            'weight_kg': None,
            'height_cm': None,
            'diagnosis_months': 0
        }
    
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    
    if 'show_patient_form' not in st.session_state:
        st.session_state.show_patient_form = True
    
    
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
    
    if 'backend_available' not in st.session_state:
        st.session_state.backend_available = None
    
    if 'agent' not in st.session_state:
        st.session_state.agent = None

def initialize_agent() -> bool:
    """Initialize the conversation agent and check if it's available."""
    if st.session_state.agent is not None:
        return True
    
    try:
        from backend.agent import ConversationAgent
        st.session_state.agent = ConversationAgent()
        logger.info("Backend agent initialized successfully.")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing backend agent: {str(e)}")
        st.session_state.agent = None
        return False

def check_backend_availability() -> bool:
    """Check if backend agent is available."""
    if st.session_state.backend_available is not None:
        return st.session_state.backend_available
    
    try:
        # Try to import the agent module
        from backend.agent import ConversationAgent
        st.session_state.backend_available = True
        return True
    except Exception as e:
        logger.error(f"Backend is not available: {str(e)}")
        st.session_state.backend_available = False
        return False


def get_agent_response(query: str, patient_context: Optional[Dict] = None) -> str:
    """Get response from backend agent."""
    try:
        # Import agent functions
        if not initialize_agent():
            raise Exception("Backend agent is not available, please check configuration.")
        
        # Augment query with patient context if available
        if patient_context and any(patient_context.values()):
            context_str = "Patient context: "
            if patient_context.get('name'):
                context_str += f"Name: {patient_context['name']}, "
            if patient_context.get('gender'):
                context_str += f"Sex: {patient_context['gender']}, "
            if patient_context.get('age_years'):
                context_str += f"Age: {patient_context['age_years']} years, "
            if patient_context.get('diagnosis_months'):
                months = patient_context['diagnosis_months']
                years = months // 12
                remaining_months = months % 12
                if years > 0 and remaining_months > 0:
                    diagnosis_text = f"{years} years {remaining_months} months"
                elif years > 0:
                    diagnosis_text = f"{years} years"
                else:
                    diagnosis_text = f"{remaining_months} months"
                context_str += f"Time since diagnosis: {diagnosis_text}, "
            
            augmented_query = f"{context_str}\n\nQuestion: {query}"
        else:
            augmented_query = query
        
        response = st.session_state.agent.chat_agent(augmented_query)
        return response
    
    except Exception as e:
        # Log error and provide user-friendly message
        logger.error(f"Error calling backend agent: {str(e)}")
        raise Exception(f"Backend agent error: {str(e)}")


def render_patient_form() -> None:
    """Render patient information form."""
    st.markdown("<h2 style='text-align: center;'>Welcome to Alzheimer's Assistant 🧠</h2>", unsafe_allow_html=True)
    
    # Check backend availability with loading message
    with st.spinner("🔌 Connecting to backend..."):
        backend_ready = check_backend_availability()

    # Check backend availability
    if not check_backend_availability():
        st.markdown(
            '<div class="error-banner">❌ <strong>Backend Not Available</strong><br/>Please check your backend configuration and dependencies.</div>',
            unsafe_allow_html=True
        )
        st.error("**Setup Instructions:**\n1. Install backend requirements: `pip install -r backend/requirements.txt`\n2. Configure your `.env` file with API keys\n3. Restart the application")
        return
    
    st.markdown(
        '<div class="success-banner">✅ <strong>Backend Connected</strong> - Ready to chat!</div>',
        unsafe_allow_html=True
    )
    
    st.info("💡 Patient information is optional. You can skip directly to chat or provide details for personalized responses.")
    
    # Skip to Chat button at the top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⏭️ Skip to Chat", use_container_width=True, type="primary"):
            st.session_state.show_patient_form = False
            st.rerun()
    
    st.markdown("---")
    
    # Patient information form
    st.subheader("Patient Information (Optional)")
    
    with st.form("patient_form"):
        name = st.text_input("Patient Name", placeholder="e.g., John Doe")
        
        # Biological sex dropdown
        gender = st.selectbox(
            "Biological Sex",
            options=["", "Biological male", "Biological female"],
            index=0,
            help="Select biological sex for personalized medical information"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age (years)", min_value=0, max_value=120, value=None, step=1)
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=None, step=0.1)
        
        with col2:
            height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=None, step=0.1)
            # Diagnosis slider (0-30 years in 3-month steps = 0-360 months in steps of 3)
            diagnosis_months = st.slider(
                "Time Since Diagnosis",
                min_value=0,
                max_value=360,
                value=0,
                step=3,
                help="Slide to select time since Alzheimer's diagnosis (in 3-month increments)"
            )
            # Display formatted value
            years = diagnosis_months // 12
            months = diagnosis_months % 12
            if years > 0 and months > 0:
                diagnosis_display = f"{years} years {months} months"
            elif years > 0:
                diagnosis_display = f"{years} years"
            elif months > 0:
                diagnosis_display = f"{months} months"
            else:
                diagnosis_display = "Not diagnosed yet"
            st.caption(f"Selected: {diagnosis_display}")
        
        submitted = st.form_submit_button("Start Chat", use_container_width=True, type="primary")
        
        if submitted:
            # Store patient data in session state
            st.session_state.patient_data = {
                'name': name,
                'gender': gender,
                'age_years': age,
                'weight_kg': weight,
                'height_cm': height,
                'diagnosis_months': diagnosis_months
            }
            
            # Mark as authenticated if any patient info provided
            if any([name, gender, age, weight, height, diagnosis_months]):
                st.session_state.is_authenticated = True
            
            st.session_state.show_patient_form = False
            st.rerun()


def render_sidebar() -> None:
    """Render sidebar with patient info and controls."""
    with st.sidebar:
        st.header("Settings & Information")
        
        # Check backend availability
        if check_backend_availability():
            st.success("✅ Production Mode - Backend connected")
        else:
            st.error("⚠️ Backend unavailable")
            if st.button("🔄 Retry Connection", use_container_width=True):
                st.session_state.backend_available = None
                st.session_state.agent = None
                st.rerun()
        
        st.markdown("---")
        
        # Patient Information Display
        if st.session_state.is_authenticated and any(st.session_state.patient_data.values()):
            st.markdown("### Patient Information")
            st.markdown('<div class="patient-info-box">', unsafe_allow_html=True)
            
            patient = st.session_state.patient_data
            if patient.get('name'):
                st.write(f"**Name:** {patient['name']}")
            if patient.get('gender'):
                st.write(f"**Sex:** {patient['gender']}")
            if patient.get('age_years'):
                st.write(f"**Age:** {patient['age_years']} years")
            if patient.get('weight_kg'):
                st.write(f"**Weight:** {patient['weight_kg']} kg")
            if patient.get('height_cm'):
                st.write(f"**Height:** {patient['height_cm']} cm")
            if patient.get('diagnosis_months') is not None and patient.get('diagnosis_months') > 0:
                months = patient['diagnosis_months']
                years = months // 12
                remaining_months = months % 12
                if years > 0 and remaining_months > 0:
                    diagnosis_text = f"{years} years {remaining_months} months"
                elif years > 0:
                    diagnosis_text = f"{years} years"
                else:
                    diagnosis_text = f"{remaining_months} months"
                st.write(f"**Diagnosis:** {diagnosis_text}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        
        # Session Statistics
        st.markdown("### Session Statistics")
        st.write(f"**Queries:** {st.session_state.query_count}")
        st.write(f"**Session Start:** {st.session_state.session_start.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Control Buttons
        st.markdown("### Actions")
        
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.query_count = 0
            if st.session_state.agent is not None:
                st.session_state.agent.clear_history()  # Clear agent's conversation history if applicable
            st.success("Chat history cleared!")
            st.rerun()
        
        if st.button("✏️ Update Patient Info", use_container_width=True):
            st.session_state.show_patient_form = True
            st.rerun()
        
        if st.session_state.is_authenticated:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.is_authenticated = False
                st.session_state.patient_data = {
                    'name': '',
                    'gender': '',
                    'age_years': None,
                    'weight_kg': None,
                    'height_cm': None,
                    'diagnosis_months': 0
                }
                st.session_state.chat_history = []
                st.session_state.query_count = 0
                st.session_state.show_patient_form = True
                #Reset agent state if applicable
                st.session_state.agent = None
                st.success("Logged out successfully!")
                st.rerun()

        with st.expander("ℹ️ Help & Tips"):
            st.markdown("""
            **How to use:**
            - Ask questions about Alzheimer's disease
            - Get caregiving advice and support
            - Learn about symptoms and treatments
            
            **Features:**
            - Conversation memory (context-aware)
            - Safety checks (crisis detection)
            - Evidence-based responses
            
            **Note:** This is not medical advice. Always consult healthcare professionals.
            """)


def render_chat_interface() -> None:
    """Render main chat interface."""
    # Check backend availability
    if not check_backend_availability():
        st.markdown(
            '<div class="error-banner">❌ <strong>Backend Not Available</strong><br/>Cannot process queries without backend connection.</div>',
            unsafe_allow_html=True
        )
        st.error("Please configure the backend and restart the application.")
        
        if st.button("🔄 Retry Connection"):
            st.session_state.backend_available = None
            st.session_state.agent = None
            st.rerun()
        return
    
    st.markdown("<h1 class='main-header'>Alzheimer's Assistant Chat 💬</h1>", unsafe_allow_html=True)
    
    # Display disclaimer
    st.markdown(
        '<div class="disclaimer"><strong>⚠️ Disclaimer:</strong> This application is for informational purposes only and does not constitute medical advice. Always consult with qualified healthcare professionals for medical decisions.</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    else:
        st.info("👋 Welcome! Ask me anything about Alzheimer's disease, caregiving strategies, symptoms, or treatment options.")
        
        # Example questions
        st.markdown("**Example questions:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💭 What are early symptoms?"):
                st.session_state.example_query = "What are the early symptoms of Alzheimer's disease?"
                st.rerun()
            if st.button("🏥 Tell me about treatments"):
                st.session_state.example_query = "What treatments are available for Alzheimer's?"
                st.rerun()
        with col2:
            if st.button("❤️ Caregiving tips"):
                st.session_state.example_query = "What are effective caregiving strategies?"
                st.rerun()
            if st.button("🧠 How does it progress?"):
                st.session_state.example_query = "How does Alzheimer's disease progress over time?"
                st.rerun()
    
    # Chat input - ALWAYS show it ONCE
    user_query = st.chat_input("Ask a question about Alzheimer's...")
    
    # Handle example query - override user_query if button was clicked
    if hasattr(st.session_state, 'example_query'):
        user_query = st.session_state.example_query
        del st.session_state.example_query
    
    # Process query if we have one
    if user_query:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.query_count += 1
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = get_agent_response(user_query, st.session_state.patient_data)
                    st.write(response)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                except Exception as e:
                    error_message = f"❌ An error occurred: {str(e)}"
                    st.error(error_message)
                    logger.error(f"Chat error: {str(e)}")
                    
                    # Offer troubleshooting options
                    st.markdown("**Troubleshooting:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Retry Query"):
                            st.rerun()
                    with col2:
                        if st.button("🔌 Check Connection"):
                            st.session_state.backend_available = None
                            st.session_state.agent = None
                            st.rerun()

def main() -> None:
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Render appropriate view
    if st.session_state.show_patient_form:
        render_patient_form()
    else:
        # Render sidebar
        render_sidebar()
        
        # Render chat interface
        render_chat_interface()


if __name__ == "__main__":
    main()
